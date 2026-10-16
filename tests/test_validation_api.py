from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from towards_victory_editor_web import server
from towards_victory_editor_web.services import validation


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    for name in ("data", "src", "src_engineering_department", "scripts", "scripts_engineering_department"):
        (root / name).mkdir(parents=True)
    monkeypatch.setattr(validation, "REPO_ROOT", root)
    return root


@pytest.fixture
def client(repo, without_wonder_service, monkeypatch):
    monkeypatch.setattr(server, "CostRewardEditorService", lambda _store: SimpleNamespace())
    monkeypatch.setattr(server, "VictoryTreePlannerService", lambda _store: SimpleNamespace())
    with TestClient(server.create_app(), client=("127.0.0.1", 50000)) as http:
        yield http


@pytest.fixture
def cli(client, monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(
            command, 0,
            json.dumps({"pass": True, "errors": [], "warnings": [], "files_checked": 3}), "",
        )

    monkeypatch.setattr(validation.subprocess, "run", run)
    return calls


def test_default_contract_and_safe_subprocess(client, cli, repo):
    response = client.post("/api/validate", json={})
    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"pass", "errors", "warnings", "files_checked", "command", "duration_ms", "fixed"}
    assert payload["pass"] is True
    assert payload["files_checked"] == 3
    assert payload["errors"] == payload["warnings"] == payload["fixed"] == []
    assert type(payload["duration_ms"]) is int and payload["duration_ms"] >= 0
    command, options = cli[0]
    assert command == [sys.executable, str(repo / "scripts" / "validate.py"), "--ai-report", "--changed"]
    assert payload["command"] == command
    assert options == {
        "cwd": repo, "capture_output": True, "text": True, "encoding": "utf-8",
        "errors": "replace", "check": False, "shell": False, "timeout": 180,
    }


@pytest.mark.parametrize("body,changed", [
    ({"changed": True}, True), ({"changed": False}, False),
    ({"files": []}, True), ({"files": ["data/x.yaml"]}, False),
    ({"files": ["data/x.yaml"], "changed": True}, True),
    ({"files": ["data/x.yaml"], "changed": False}, False),
])
def test_changed_selection_matches_cli(client, cli, body, changed):
    assert client.post("/api/validate", json=body).status_code == 200
    command = cli[0][0]
    assert ("--changed" in command) is changed
    assert "--fix" not in command
    if body.get("files"):
        assert "data/x.yaml" in command


@pytest.mark.parametrize("target", [
    "data/unique_wonders.yaml", "src/main_menu/test.txt", "src_engineering_department/test.yml",
    "src_court_positions/test.txt", "src_eureka/test.txt", "scripts/validate.py",
    "scripts_engineering_department/test.py", "data", "src", "scripts",
    "data\\unique_wonders.yaml", "scripts/a file.py",
])
def test_whitelisted_paths(client, cli, target):
    response = client.post("/api/validate", json={"files": [target], "changed": False})
    assert response.status_code == 200
    assert target.replace("\\", "/") in cli[0][0]


@pytest.mark.parametrize("target", [
    "../data/x.yaml", "data/../scripts/validate.py", "src\\..\\..\\outside.txt",
    "/tmp/src/x.txt", "C:/src/x.txt", "C:src/x.txt", "\\\\host\\share\\src\\x.txt",
    "\\src\\x.txt", "docs/x.md", "towards_victory_editor_web/server.py", "datafile.yaml",
    ".git/config", "--fix", "", "data/a\x00.yaml", "data/file.yaml:stream",
])
def test_bad_paths_return_400_without_execution(client, cli, target):
    response = client.post("/api/validate", json={"files": [target], "changed": True})
    assert response.status_code == 400
    assert cli == []


@pytest.mark.parametrize("directory_target", [False, True])
@pytest.mark.parametrize("outside_repo", [False, True])
def test_resolved_path_and_nested_link_rejection(client, cli, repo, monkeypatch, directory_target, outside_repo):
    link = repo / "data" / "escape.yaml"
    link.write_text("test", encoding="utf-8")
    destination = repo.parent / "outside.yaml" if outside_repo else repo / "docs" / "secret.yaml"
    original_resolve = Path.resolve

    def resolve(path, *args, **kwargs):
        return destination if path == link else original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    target = "data" if directory_target else "data/escape.yaml"
    assert client.post("/api/validate", json={"files": [target]}).status_code == 400
    assert cli == []


@pytest.mark.parametrize("rule", ["loc", "localization"])
@pytest.mark.parametrize("prefix", ["", "[LOC] "])
def test_failed_checks_are_200_and_diagnostics_have_messages(client, monkeypatch, rule, prefix):
    report = {
        "pass": False, "files_checked": 1,
        "errors": [
            {"rule": rule, "message": f"{prefix}Duplicate localization key 'test'"},
            {"rule": "pattern", "file": "src\\test.txt", "line": 12, "bad": "old", "fix": "new"},
        ],
        "warnings": [{"raw": "A CLI warning"}],
    }
    monkeypatch.setattr(validation.subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 1, json.dumps(report), ""))
    response = client.post("/api/validate", json={"changed": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["pass"] is False
    assert payload["errors"][0]["rule"] == rule
    assert payload["errors"][0]["message"] == "[LOC] Duplicate localization key 'test'"
    assert payload["errors"][1]["message"] == "Bad: old -> new"
    assert payload["errors"][1]["file"] == "src/test.txt"
    assert payload["errors"][1]["line"] == 12
    assert payload["warnings"][0]["message"] == "A CLI warning"
    assert payload["fixed"] == []


@pytest.mark.parametrize("as_bytes", [False, True])
def test_timeout_is_504_and_contains_bounded_captured_output(client, monkeypatch, as_bytes):
    stdout = "x" * 5000 + "captured stdout"
    stderr = "captured stderr"
    if as_bytes:
        stdout, stderr = stdout.encode(), stderr.encode()

    def timeout(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"], output=stdout, stderr=stderr)

    monkeypatch.setattr(validation.subprocess, "run", timeout)
    response = client.post("/api/validate", json={})
    assert response.status_code == 504
    assert "180" in response.json()["detail"]
    assert len(response.json()["output_tail"]) == 4096
    assert response.json()["output_tail"].endswith("captured stdout\ncaptured stderr")


@pytest.mark.parametrize("stdout,returncode", [
    ("not JSON", 1), ("[]", 0), ("{}", 0),
    (json.dumps({"pass": True, "files_checked": 0, "errors": [], "warnings": []}), 2),
    (json.dumps({"pass": True, "files_checked": 0, "errors": ["bad"], "warnings": []}), 0),
])
def test_invalid_cli_report_is_500_with_output_tail(client, monkeypatch, stdout, returncode):
    monkeypatch.setattr(validation.subprocess, "run", lambda *args, **kwargs: subprocess.CompletedProcess(args[0], returncode, stdout, "CLI stderr"))
    response = client.post("/api/validate", json={})
    assert response.status_code == 500
    assert response.json()["output_tail"] == stdout + "\nCLI stderr"


def test_subprocess_start_failure_is_500(client, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("Cannot start Python")

    monkeypatch.setattr(validation.subprocess, "run", fail)
    response = client.post("/api/validate", json={})
    assert response.status_code == 500
    assert "Cannot start Python" in response.json()["detail"]


@pytest.mark.parametrize("value", ["true", 1, "false", None])
def test_fix_requires_explicit_boolean_true(client, cli, value):
    assert client.post("/api/validate", json={"fix": value}).status_code == 422
    assert cli == []


@pytest.mark.parametrize("host", ["192.0.2.1", "testclient"])
def test_remote_fix_rejected_even_with_forwarded_loopback(client, cli, host):
    with TestClient(client.app, client=(host, 50000)) as remote:
        response = remote.post("/api/validate", json={"fix": True}, headers={"X-Forwarded-For": "127.0.0.1"})
        assert response.status_code == 400
        assert remote.post("/api/validate", json={"fix": False}).status_code == 200
    assert all("--fix" not in command for command, _ in cli)


@pytest.mark.parametrize("headers", [
    {"Origin": "https://attacker.invalid"}, {"Origin": "null"},
    {"Sec-Fetch-Site": "cross-site"}, {"Sec-Fetch-Site": "same-site"},
])
def test_cross_origin_fix_rejected(client, cli, headers):
    assert client.post("/api/validate", json={"fix": True}, headers=headers).status_code == 400
    assert cli == []


@pytest.mark.parametrize("host", ["127.0.0.1", "::1", "::ffff:127.0.0.1"])
def test_loopback_fix_allowed(client, cli, host):
    with TestClient(client.app, client=(host, 50000)) as local:
        response = local.post("/api/validate", json={"fix": True}, headers={"Origin": "http://testserver", "Sec-Fetch-Site": "same-origin"})
    assert response.status_code == 200
    assert "--fix" in cli[0][0]


def test_fix_reports_only_actual_bom_additions(client, repo, monkeypatch):
    target = repo / "src" / "test.txt"
    unchanged = repo / "src" / "unchanged.txt"
    already_bom = repo / "src" / "already.txt"
    target.write_bytes(b"test = {}\n")
    unchanged.write_bytes(b"unchanged = {}\n")
    already_bom.write_bytes(validation.UTF8_BOM + b"already = {}\n")

    def fix(command, **kwargs):
        assert "--fix" in command
        target.write_bytes(validation.UTF8_BOM + target.read_bytes())
        return subprocess.CompletedProcess(command, 0, json.dumps({"pass": True, "errors": [], "warnings": [], "files_checked": 3}), "")

    monkeypatch.setattr(validation.subprocess, "run", fix)
    response = client.post("/api/validate", json={"files": ["src"], "changed": False, "fix": True})
    assert response.status_code == 200
    assert response.json()["fixed"] == ["src/test.txt"]
    assert unchanged.read_bytes() == b"unchanged = {}\n"


def _copy_validator(root):
    source = Path(server.__file__).resolve().parent.parent
    shutil.copy2(source / "scripts" / "validate.py", root / "scripts" / "validate.py")
    shutil.copy2(source / "scripts_engineering_department" / "wonder_unique_ritual_harness.py", root / "scripts_engineering_department" / "wonder_unique_ritual_harness.py")
    package = root / "scripts_engineering_department" / "wonder_mechanics"
    package.mkdir()
    for name in ("__init__.py", "io.py", "_core.py"):
        shutil.copy2(source / "scripts_engineering_department" / "wonder_mechanics" / name, package / name)
    icons = Path(".eu5-base/reference_game_files/game/main_menu/gui/shared/font_icons.gui")
    (root / icons).parent.mkdir(parents=True)
    shutil.copy2(source / icons, root / icons)


def test_duplicate_localization_in_temporary_repo_is_real_failure(client, repo):
    _copy_validator(repo)
    english = repo / "src" / "main_menu" / "localization" / "english" / "test_l_english.yml"
    chinese = repo / "src" / "main_menu" / "localization" / "simp_chinese" / "test_l_simp_chinese.yml"
    for path in (english, chinese):
        path.parent.mkdir(parents=True)
    english.write_text('l_english:\n test_duplicate:0 "First"\n test_duplicate:0 "Second"\n', encoding="utf-8-sig")
    chinese.write_text('l_simp_chinese:\n test_duplicate:0 "Test"\n', encoding="utf-8-sig")
    response = client.post("/api/validate", json={"files": ["src/main_menu/localization"], "changed": False})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["pass"] is False
    duplicates = [issue for issue in payload["errors"] if "Duplicate localization key 'test_duplicate'" in issue["message"]]
    assert len(duplicates) == 1
    assert "[LOC]" in duplicates[0]["message"]
    assert "test_l_english.yml:2" in duplicates[0]["message"]
    assert "test_l_english.yml:3" in duplicates[0]["message"]
    assert payload["files_checked"] == 2
    assert payload["fixed"] == []
    assert 'test_duplicate:0 "Second"' in english.read_text(encoding="utf-8-sig")
    english.write_text('l_english:\n test_duplicate:0 "First"\n', encoding="utf-8-sig")
    corrected = client.post("/api/validate", json={"files": ["src/main_menu/localization"], "changed": False})
    assert corrected.status_code == 200
    assert not any("Duplicate localization key" in issue["message"] for issue in corrected.json()["errors"])


@pytest.mark.parametrize("missing_file", [True, False], ids=["missing_zh_file", "missing_translation"])
def test_missing_chinese_localization_in_temporary_repo_has_loc_prefix(client, repo, missing_file):
    _copy_validator(repo)
    english = repo / "src" / "main_menu" / "localization" / "english" / "test_l_english.yml"
    chinese = repo / "src" / "main_menu" / "localization" / "simp_chinese" / "test_l_simp_chinese.yml"
    english.parent.mkdir(parents=True)
    english.write_text('l_english:\n test_present:0 "Present"\n test_missing:0 "Missing"\n', encoding="utf-8-sig")
    if not missing_file:
        chinese.parent.mkdir(parents=True)
        chinese.write_text('l_simp_chinese:\n test_present:0 "Present"\n', encoding="utf-8-sig")
    response = client.post("/api/validate", json={"files": ["src/main_menu/localization"], "changed": False})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["pass"] is False
    issues = [issue for issue in payload["errors"] if issue["rule"] == "loc"]
    assert len(issues) == 1
    expected = "Missing simp_chinese file:" if missing_file else "1 key(s) missing from simp_chinese: test_missing"
    assert expected in issues[0]["message"]
    assert issues[0]["message"].startswith("[LOC]")
    assert issues[0]["message"].count("[LOC]") == 1
    assert payload["files_checked"] == (1 if missing_file else 2)
    assert payload["fixed"] == []


@pytest.mark.parametrize("filename", ["test.txt", "test.custom"])
def test_real_cli_fix_and_read_only_default(client, repo, filename):
    _copy_validator(repo)
    relative = f"src/{filename}"
    target = repo / relative
    original = b"test = {}\n"
    target.write_bytes(original)
    read_only = client.post("/api/validate", json={"files": [relative], "changed": False})
    assert read_only.status_code == 200, read_only.text
    assert read_only.json()["pass"] is False
    assert target.read_bytes() == original
    assert read_only.json()["fixed"] == []
    fixed = client.post("/api/validate", json={"files": [relative], "changed": False, "fix": True})
    assert fixed.status_code == 200, fixed.text
    assert fixed.json()["fixed"] == [relative]
    assert target.read_bytes() == validation.UTF8_BOM + original
    repeated = client.post("/api/validate", json={"files": [relative], "changed": False, "fix": True})
    assert repeated.status_code == 200
    assert repeated.json()["fixed"] == []
