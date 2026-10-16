from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from fastapi.testclient import TestClient

from towards_victory_editor_web import server
from towards_victory_editor_web.services import generator_runs, platform
from towards_victory_editor_web.services.media_tools import build_registry
from towards_victory_editor_web.services.operation_store import OperationStore

SOURCE_ROOT = Path(__file__).resolve().parents[1]


def write(root, relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
    return path


def register(root, entries):
    write(root, generator_runs.REGISTRY_PATH, yaml.safe_dump({"generated": entries}))


def entry(script="scripts/gen_a.py", output="data/a.json", data="data/input.yaml"):
    return {"script": script, "output": output, "data": data}


def tree(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    write(root, "data/input.yaml", "value: 1\n")
    write(root, "data/a.json", '{"old": true}\n')
    write(root, "scripts/gen_a.py", "from pathlib import Path\nPath('data/a.json').write_text('{\"new\": true}', encoding='utf-8')\nprint('generated')\n")
    register(root, [entry()])
    monkeypatch.setattr(generator_runs, "REPO_ROOT", root)
    return root


@pytest.fixture
def client(repo, without_wonder_service, monkeypatch):
    for name in ("CostRewardEditorService", "VictoryTreePlannerService", "LocalizationEditorService"):
        monkeypatch.setattr(server, name, lambda _store: SimpleNamespace())
    with TestClient(server.create_app(), client=("127.0.0.1", 50000)) as http:
        yield http


def test_registry_merges_inputs_outputs_and_groups(repo, client):
    write(repo, "scripts_engineering_department/in_game/gen_b.py", "pass\n")
    register(repo, [entry(data="data/input.yaml + data/*.yaml (notes)"), entry(output="data/b.json"),
                    entry("scripts_engineering_department/in_game/gen_b.py", "data/c.json"), entry()])
    response = client.get("/api/generators")
    assert response.status_code == 200
    assert response.json() == {"generators": [
        {"script": "scripts/gen_a.py", "root": "src", "domain": "a", "data_inputs": ["data/*.yaml", "data/input.yaml"], "outputs": ["data/a.json", "data/b.json"]},
        {"script": "scripts_engineering_department/in_game/gen_b.py", "root": "src_engineering_department", "domain": "in_game", "data_inputs": ["data/input.yaml"], "outputs": ["data/c.json"]},
    ]}


def test_real_registry_and_index_outputs_are_complete():
    service = generator_runs.GeneratorRunService(repo_root=SOURCE_ROOT)
    generators = service.generators()
    registry = yaml.safe_load((SOURCE_ROOT / generator_runs.REGISTRY_PATH).read_text(encoding="utf-8"))["generated"]
    assert {item["script"] for item in generators} == {row["script"] for row in registry}
    index = next(item for item in generators if item["script"] == "scripts/gen_index.py")
    assert set(index["outputs"]) == {"data/index/" + name for name in (
        "icons.txt", "scripted_triggers.txt", "scripted_effects.txt", "static_modifiers.txt",
        "modifier_localization.json", "trigger_localization.json", "loc_keys_en.txt",
    )}
    assert len(index["outputs"]) == 7
    assert index["root"] == "src" and index["domain"] == "index"
    report = generator_runs.build_check_report()
    assert report[0] == f"[PASS] runnable generators: {len(generators)}"
    assert sum(int(line.rsplit(": ", 1)[1]) for line in report[1:]) == len(generators)


@pytest.mark.parametrize("scripts", [[], ["scripts/unknown.py"], ["../scripts/gen_a.py"], ["scripts/gen_a.py", "scripts/gen_a.py"]])
def test_invalid_selection_rejected_without_writes(repo, client, scripts, monkeypatch):
    before = tree(repo)
    monkeypatch.setattr(generator_runs.shutil, "copytree", lambda *args, **kwargs: pytest.fail("staging created before preflight rejection"))
    response = client.post("/api/generators/run", json={"scripts": scripts})
    assert response.status_code == 400
    assert set(response.json()) == {"detail"}
    assert tree(repo) == before
    assert client.get("/api/operations").json()["operations"] == []


@pytest.mark.parametrize("output", ["data/a.json", "data", "data/a.json/child.json", "data/A.json"])
def test_intersecting_outputs_rejected_without_writes(repo, client, output, monkeypatch):
    if output == "data/A.json" and os.name != "nt":
        pytest.skip("case-insensitive Windows path contract")
    write(repo, "scripts/gen_b.py", "raise AssertionError('must not execute')\n")
    register(repo, [entry(), entry("scripts/gen_b.py", output)])
    before = tree(repo)
    def reject_staging(*args, **kwargs):
        raise AssertionError("staging created before overlap rejection")
    monkeypatch.setattr(generator_runs.shutil, "copytree", reject_staging)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py", "scripts/gen_b.py"]})
    assert response.status_code == 400, response.text
    assert "Intersecting outputs" in response.json()["detail"]
    assert output.casefold() in response.json()["detail"].casefold()
    assert tree(repo) == before
    assert client.get("/api/operations").json()["operations"] == []


@pytest.mark.parametrize("bad", ["../outside.json", "C:/outside.json", ".git/objects/object"])
def test_registry_output_escape_rejected_without_writes(repo, client, bad):
    register(repo, [entry(output=bad)])
    before = tree(repo)
    assert client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]}).status_code == 400
    assert tree(repo) == before


def test_dry_run_never_stages_or_starts_process(repo, client, monkeypatch):
    before = tree(repo)
    monkeypatch.setattr(generator_runs.shutil, "copytree", lambda *args, **kwargs: pytest.fail("dry run staged files"))
    monkeypatch.setattr(generator_runs.subprocess, "run", lambda *args, **kwargs: pytest.fail("dry run started process"))
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"], "dry_run": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["operation"]["kind"] == "generator_run"
    assert payload["operation"]["status"] == "succeeded"
    assert payload["results"] == [{"script": "scripts/gen_a.py", "status": "skipped", "exit_code": None, "duration_ms": 0, "output_tail": ""}]
    assert payload["artifacts"] == [] and payload["rollback"] == {"status": "not_needed", "errors": []}
    assert tree(repo) == before
    for value in ("false", 1, None):
        assert client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"], "dry_run": value}).status_code == 422


def test_success_uses_staging_and_persists_report(repo, client, monkeypatch):
    original = subprocess.run
    calls = []
    def observe(command, **kwargs):
        calls.append((command, kwargs))
        assert Path(kwargs["cwd"]) != repo
        assert not Path(kwargs["cwd"]).is_relative_to(repo)
        assert command[0] == sys.executable and command[-1] == str(Path(kwargs["cwd"]) / "scripts/gen_a.py")
        assert kwargs["timeout"] == 120 and kwargs["check"] is False
        return original(command, **kwargs)
    monkeypatch.setattr(generator_runs.subprocess, "run", observe)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 200, response.text
    payload = response.json()
    result = payload["results"][0]
    assert result["status"] == "succeeded" and result["exit_code"] == 0
    assert result["duration_ms"] >= 0 and result["output_tail"] == "generated\n"
    data = (repo / "data/a.json").read_bytes()
    assert data == b'{"new": true}'
    assert payload["artifacts"] == [{"path": "data/a.json", "size": len(data), "sha256": hashlib.sha256(data).hexdigest(), "changed": True}]
    operation = client.get("/api/operations/" + payload["operation_id"]).json()
    assert operation == payload["operation"] and operation["resource_ids"] == []
    stored_operation, details = client.app.state.operation_store.get_with_details(payload["operation_id"])
    assert stored_operation == operation and details["results"] == payload["results"]
    assert details["artifacts"] == payload["artifacts"] and details["rollback"] == payload["rollback"]
    assert all(not Path(kwargs["cwd"]).exists() for _, kwargs in calls)
    second = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]}).json()
    assert second["artifacts"][0]["changed"] is False


def test_registered_output_deletion_is_published_with_contract_fields(repo, client):
    write(repo, "scripts/gen_a.py", "from pathlib import Path\nPath('data/a.json').unlink()\n")
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 200
    assert not (repo / "data/a.json").exists()
    assert response.json()["artifacts"] == [{"path": "data/a.json", "size": 0, "sha256": "missing", "changed": True}]


@pytest.mark.parametrize("action", ["Path('data/extra.json').write_text('{}')", "Path('data/input.yaml').write_text('changed')", "Path('data/input.yaml').unlink()"])
def test_unregistered_artifacts_rejected_without_publication(repo, client, action):
    write(repo, "scripts/gen_a.py", "from pathlib import Path\nPath('data/a.json').write_text('{}')\n" + action + "\n")
    before = tree(repo)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 400
    payload = response.json()
    assert "Unregistered artifacts" in payload["detail"]
    assert payload["operation"]["status"] == "failed" and payload["results"][0]["exit_code"] == 0
    assert payload["results"][0]["status"] == "failed"
    assert payload["rollback"] == {"status": "not_needed", "errors": []}
    assert tree(repo) == before


def test_absolute_write_outside_staging_is_blocked_before_write(repo, client):
    write(repo, "scripts/gen_a.py", f"from pathlib import Path\nPath({str(repo / 'data/input.yaml')!r}).write_text('unsafe')\n")
    before = tree(repo)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 400
    assert "Unregistered write outside staging" in response.json()["detail"]
    assert tree(repo) == before


@pytest.mark.parametrize("output,content", [("data/a.json", "not json"), ("data/a.png", "not png"), ("data/a.dds", "not dds"), ("data/a.jpeg", "not jpeg"), ("data/a.txt", "unclosed = {"), ("src/in_game/common/a.txt", "value = {}"), ("src/main_menu/localization/english/a_l_english.yml", 'l_english:\n key:0 "text"')])
def test_file_level_validation_failure_does_not_publish(repo, client, output, content):
    register(repo, [entry(output=output)])
    write(repo, "scripts/gen_a.py", f"from pathlib import Path\npath = Path({output!r})\npath.parent.mkdir(parents=True, exist_ok=True)\npath.write_text({content!r}, encoding='utf-8')\n")
    before = tree(repo)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 400
    assert "File-level artifact validation failed" in response.json()["detail"]
    assert tree(repo) == before


def test_missing_output_is_rejected(repo, client):
    (repo / "data/a.json").unlink()
    write(repo, "scripts/gen_a.py", "print('nothing generated')\n")
    before = tree(repo)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 400 and "Missing registered outputs" in response.json()["detail"]
    assert tree(repo) == before


def test_nonzero_exit_stops_sequence_and_preserves_captured_output(repo, client):
    write(repo, "scripts/gen_b.py", "import sys\nfrom pathlib import Path\nPath('data/b.json').write_text('{}')\nprint('x' * 5000)\nprint('stderr diagnostic', file=sys.stderr, flush=True)\nsys.exit(7)\n")
    write(repo, "scripts/gen_c.py", "raise AssertionError('must not run')\n")
    register(repo, [entry(), entry("scripts/gen_b.py", "data/b.json"), entry("scripts/gen_c.py", "data/c.json")])
    before = tree(repo)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py", "scripts/gen_b.py", "scripts/gen_c.py"]})
    assert response.status_code == 500
    payload = response.json()
    assert [result["status"] for result in payload["results"]] == ["succeeded", "failed", "skipped"]
    assert payload["results"][1]["exit_code"] == 7
    assert len(payload["results"][1]["output_tail"]) == 4096
    assert "stderr diagnostic" in payload["results"][1]["output_tail"]
    assert payload["operation"]["status"] == "failed" and tree(repo) == before
    _, details = client.app.state.operation_store.get_with_details(payload["operation_id"])
    assert details["results"] == payload["results"]


def test_timeout_kills_writer_and_keeps_output(repo, client, monkeypatch):
    write(repo, "scripts/gen_a.py", "from pathlib import Path\nimport time\nprint('captured before timeout', flush=True)\ntime.sleep(2)\nPath('data/a.json').write_text('{}')\n")
    monkeypatch.setattr(generator_runs, "STEP_TIMEOUT_SECONDS", 0.5)
    before = tree(repo)
    started = time.monotonic()
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 504
    result = response.json()["results"][0]
    assert result["status"] == "timed_out" and result["exit_code"] is None
    assert "captured before timeout" in result["output_tail"]
    assert result["duration_ms"] >= 450
    assert time.monotonic() - started < 2
    assert tree(repo) == before


def test_resource_lock_busy_prevents_execution(repo, client, monkeypatch):
    register(repo, [entry(output="data/victory.json")])
    before = tree(repo)
    monkeypatch.setattr(generator_runs.shutil, "copytree", lambda *args, **kwargs: pytest.fail("locked resource executed"))
    with platform.resource_operation(("editor.victory_tree",)):
        response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 409
    assert "editor.victory_tree" in response.json()["operation"]["resource_ids"]
    assert response.json()["operation"]["status"] == "failed" and tree(repo) == before


def test_concurrent_input_change_aborts_publication(repo, client, monkeypatch):
    original = subprocess.run
    def change_input(command, **kwargs):
        result = original(command, **kwargs)
        write(repo, "data/input.yaml", "concurrent: true\n")
        return result
    monkeypatch.setattr(generator_runs.subprocess, "run", change_input)
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 409
    assert (repo / "data/a.json").read_bytes() == b'{"old": true}\n'
    assert (repo / "data/input.yaml").read_text(encoding="utf-8") == "concurrent: true\n"


@pytest.mark.parametrize("incomplete", [False, True])
def test_publication_failure_reports_rollback(repo, client, monkeypatch, incomplete):
    before = tree(repo)
    def fail(files):
        for path, content in files.items():
            path.write_bytes(content)
            raise OSError("publication denied")
    monkeypatch.setattr(generator_runs, "atomic_write_files", fail)
    if incomplete:
        monkeypatch.setattr(platform, "restore_file_contents", lambda snapshots: ["restore denied"])
    response = client.post("/api/generators/run", json={"scripts": ["scripts/gen_a.py"]})
    assert response.status_code == 500
    payload = response.json()
    assert payload["operation"]["status"] == "failed"
    assert payload["rollback"] == {"status": "failed" if incomplete else "completed", "errors": ["restore denied"] if incomplete else []}
    if not incomplete:
        assert tree(repo) == before
    _, details = client.app.state.operation_store.get_with_details(payload["operation_id"])
    assert details["rollback"] == payload["rollback"]


def test_media_handlers_declare_actual_shared_dependencies():
    registry = build_registry()
    assert registry.get("media.historical_style").spec.resource_ids == ("media.historical",)
    assert registry.get("media.historical_api").spec.resource_ids == ("media.historical",)
    assert set(registry.get("media.dds_icon").spec.resource_ids) == {"editor.wonder", "editor.cost_reward", "editor.victory_tree", "editor.wonder_crop"}
    assert generator_runs._resource_ids(["src/main_menu/localization/english/test_l_english.yml"]) == ("editor.localization",)
    assert set(generator_runs._resource_ids(["src_engineering_department/main_menu/gfx/wonders/test.dds"])) == {"editor.wonder", "editor.cost_reward", "editor.wonder_crop"}


@pytest.mark.slow
def test_real_generator_bytes_and_generated_header_in_temporary_copies(tmp_path):
    script = "scripts/in_game/common/static_modifiers/gen_tv_victory_tree_modifiers.py"
    rows = yaml.safe_load((SOURCE_ROOT / generator_runs.REGISTRY_PATH).read_text(encoding="utf-8"))["generated"]
    rows = [row for row in rows if row["script"] == script]
    assert rows
    root = tmp_path / "real-repo"
    for relative in (script, "scripts/victory_tree_node_codegen.py", "data/victory_path_tree_variant.yaml", *(row["output"] for row in rows)):
        write(root, relative, (SOURCE_ROOT / relative).read_bytes())
    register(root, rows)
    expected = tmp_path / "cli-repo"
    shutil.copytree(root, expected)
    completed = subprocess.run([sys.executable, "-B", script], cwd=expected, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    with_store = OperationStore(":memory:")
    try:
        payload = generator_runs.GeneratorRunService(with_store, repo_root=root).run([script])
        assert payload["operation"]["status"] == "succeeded"
        assert len(payload["artifacts"]) == len(rows)
        for row in rows:
            actual = (root / row["output"]).read_bytes()
            assert actual == (expected / row["output"]).read_bytes()
            assert actual == (SOURCE_ROOT / row["output"]).read_bytes()
            assert b"# @Generated by" in b"\n".join(actual.splitlines()[:5])
    finally:
        with_store.close()
    for relative in ("scripts/validate.py", "scripts_engineering_department/wonder_unique_ritual_harness.py",
                     "scripts_engineering_department/wonder_mechanics/__init__.py", "scripts_engineering_department/wonder_mechanics/io.py",
                     "scripts_engineering_department/wonder_mechanics/_core.py", ".eu5-base/reference_game_files/game/main_menu/gui/shared/font_icons.gui"):
        write(root, relative, (SOURCE_ROOT / relative).read_bytes())
    validated = subprocess.run([sys.executable, "scripts/validate.py", rows[0]["output"], "--ai-report"],
                               cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert validated.returncode == 0, validated.stdout + validated.stderr
    report = json.loads(validated.stdout)
    assert report["pass"] is True
    assert not any(issue["rule"] == "autogen_header" for issue in report["warnings"])
