import hashlib
import shutil
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from towards_victory_editor_web.services import localization_editor as localization
from towards_victory_editor_web.services import platform

EN = "src/main_menu/localization/english/demo_l_english.yml"
ZH = "src/main_menu/localization/simp_chinese/demo_l_simp_chinese.yml"
URL = "/api/resources/editor.localization"
REAL_ROOT = Path(__file__).resolve().parents[1]


def write_loc(root, relative, rows, *, bom=True, newline="\r\n", comments=False):
    language = Path(relative).stem.rsplit("_l_", 1)[1]
    lines = ["# retained header", "", f"l_{language}:"]
    if comments:
        lines.append(" # body section comment")
    lines.extend(f' {key}:0 "{value}"' for key, value in rows)
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((newline.join(lines) + newline).encode("utf-8-sig" if bom else "utf-8"))
    return path


def registry(root, entries=()):
    path = root / localization.REGISTRY
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"generated": list(entries)}), encoding="utf-8")


def request_body(service, edits=None):
    loaded = service.load_resource()
    return {
        "edits": edits or {},
        "base": {item["path"]: item["sha256"] for item in loaded["change_set"]["base"]},
    }


def files_by_path(payload):
    return {file["path"]: file for root in payload["draft"]["roots"] for file in root["files"]}


def contents(service):
    return {path: (service.repo_root / path).read_bytes() for path in files_by_path(service.load_resource())}


@pytest.fixture
def service(tmp_path):
    registry(tmp_path)
    write_loc(tmp_path, EN, [("a", "A"), ("b", "B"), ("empty", "")], comments=True)
    write_loc(tmp_path, ZH, [("a", "甲"), ("b", "乙"), ("empty", "")], newline="\n", comments=True)
    return localization.LocalizationEditorService(repo_root=tmp_path)


@pytest.fixture
def client(service, monkeypatch, without_wonder_service):
    from towards_victory_editor_web import server

    monkeypatch.setattr(server, "LocalizationEditorService", lambda store: service)
    with TestClient(server.create_app(), raise_server_exceptions=False) as test_client:
        yield test_client


def test_load_discovery_ownership_and_root_isolation(service):
    generated = EN.replace("demo", "managed")
    generated_zh = ZH.replace("demo", "managed")
    write_loc(service.repo_root, generated, [("managed", "Generated")])
    write_loc(service.repo_root, generated_zh, [("managed", "生成")])
    registry(service.repo_root, [{"output": generated, "data": "data/owner.yaml + data/other.yaml"}])
    foreign = EN.replace("english", "french")
    write_loc(service.repo_root, foreign, [("a", "A fr")])
    other_en, other_zh = EN.replace("src/", "src_sample/"), ZH.replace("src/", "src_sample/")
    write_loc(service.repo_root, other_en, [("a", "Independent")])
    write_loc(service.repo_root, other_zh, [("a", "独立")])
    payload = service.load_resource()
    files = files_by_path(payload)
    assert list(files) == sorted(files)
    assert set(files) == {EN, ZH, generated, generated_zh, foreign, other_en, other_zh}
    assert payload["resource"]["discovery"]["glob"] == "src*/**/localization/**/*.yml"
    assert payload["resource"]["discovery"]["generated_registry"] == localization.REGISTRY
    assert files[EN]["languages"] == files[ZH]["languages"]
    assert [entry["key"] for entry in files[EN]["languages"]["english"]] == ["a", "b", "empty"]
    for path in (generated, generated_zh):
        assert files[path]["read_only"] is True
        assert files[path]["source_data"] == ["data/other.yaml", "data/owner.yaml"]
    assert files[foreign]["read_only"] is True
    assert files[foreign]["languages"]["french"] == [{"key": "a", "value": "A fr"}]
    assert service.validate_edits({})["valid"] is True
    assert set(payload["change_set"]["files"]) == set(files) | {localization.REGISTRY}
    for snapshot in payload["change_set"]["base"]:
        raw = (service.repo_root / snapshot["path"]).read_bytes()
        assert snapshot["sha256"] == hashlib.sha256(raw).hexdigest()
        assert snapshot["size"] == len(raw)


def test_preview_is_presence_aware_and_does_not_write_or_mutate(service, client):
    before = contents(service)
    edits = {ZH: {"a": {"english": "Changed", "simp_chinese": "变更"},
                  "new": {"english": "", "simp_chinese": "新"}}}
    response = client.post(URL + "/preview", json=request_body(service, edits))
    assert response.status_code == 200
    report = response.json()
    assert set(report) >= {"resource", "draft", "change_set", "valid", "errors", "diff", "missing_translations"}
    assert report["valid"] and not report["missing_translations"]
    rows = {(row["path"], row["key"]): row for row in report["diff"]}
    assert len(rows) == 4
    assert rows[EN, "a"] == {
        "path": EN, "key": "a", "language": "english", "field": "value",
        "before": "A", "after": "Changed", "before_present": True, "after_present": True,
    }
    assert rows[EN, "new"]["before"] is None
    assert rows[EN, "new"]["after"] == ""
    assert rows[EN, "new"]["before_present"] is False
    assert contents(service) == before
    loaded = client.get(URL).json()
    assert loaded["draft"] != report["draft"]
    assert client.post(URL + "/validate", json={"edits": edits}).json()["valid"] is True


@pytest.mark.parametrize("endpoint", ["validate", "preview", "commit"])
@pytest.mark.parametrize("language", ["english", "simp_chinese"])
def test_new_key_requires_both_languages_http_400(service, client, endpoint, language):
    before = contents(service)
    body = request_body(service, {EN: {"new": {language: "Only one"}}})
    response = client.post(URL + "/" + endpoint, json=body)
    assert response.status_code == 400
    assert "requires both english and simp_chinese" in response.json()["detail"]
    assert contents(service) == before


def test_missing_zh_is_previewed_rejected_and_repairable(service, client):
    write_loc(service.repo_root, ZH, [("a", "甲"), ("empty", "")])
    body = request_body(service)
    before = contents(service)
    expected = [{"path": ZH, "keys": ["b"]}]
    preview = client.post(URL + "/preview", json=body)
    assert preview.status_code == 200
    assert preview.json()["missing_translations"] == expected
    assert preview.json()["draft"]["missing_translations"] == expected
    assert preview.json()["valid"] is False
    validation = client.post(URL + "/validate", json=body)
    assert validation.status_code == 200
    assert validation.json()["valid"] is False
    response = client.post(URL + "/commit", json=body)
    assert response.status_code == 400
    assert response.json()["operation"]["status"] == "failed"
    assert contents(service) == before
    repair = request_body(service, {EN: {"b": {"simp_chinese": "修复"}}})
    result = client.post(URL + "/commit", json=repair)
    assert result.status_code == 200
    assert result.json()["written_paths"] == [ZH]
    assert not result.json()["draft"]["missing_translations"]


def test_missing_keys_are_bidirectional_and_do_not_cross_mod_roots(service):
    write_loc(service.repo_root, EN, [("a", "A"), ("empty", "")])
    write_loc(service.repo_root, EN.replace("src/", "src_sample/"), [("b", "Other")])
    write_loc(service.repo_root, ZH.replace("src/", "src_sample/"), [("b", "其他")])
    assert service.load_resource()["draft"]["missing_translations"] == [{"path": EN, "keys": ["b"]}]


def test_add_delete_pair_noop_and_persisted_operation(service, client):
    body = request_body(service, {EN: {"new": {"english": "N", "simp_chinese": "新"}}})
    response = client.post(URL + "/commit", json=body)
    assert response.status_code == 200
    result = response.json()
    assert result["operation_id"] == result["operation"]["id"]
    assert result["operation"]["status"] == "succeeded"
    assert set(result["written_paths"]) == {EN, ZH}
    assert client.get("/api/operations/" + result["operation_id"]).json()["status"] == "succeeded"
    refreshed_base = {item["path"]: item["sha256"] for item in result["change_set"]["base"]}
    assert set(refreshed_base) == set(body["base"])
    assert {path for path in refreshed_base if refreshed_base[path] != body["base"][path]} == {EN, ZH}
    assert refreshed_base == request_body(service)["base"]
    body = request_body(service, {ZH: {"new": None, "empty": None}})
    report = service.preview_edits(body["edits"], body["base"])
    assert len(report["diff"]) == 4
    empty = next(row for row in report["diff"] if row["key"] == "empty" and row["language"] == "english")
    assert empty["before"] == "" and empty["before_present"] and not empty["after_present"]
    assert empty["after"] is None
    result = service.commit_edits(body["edits"], body["base"])
    for item in files_by_path(result).values():
        for rows in item["languages"].values():
            assert {entry["key"] for entry in rows} == {"a", "b"}
    before = contents(service)
    body = request_body(service, {EN: {"a": {"english": "A"}}})
    assert service.preview_edits(body["edits"], body["base"])["diff"] == []
    assert service.commit_edits(body["edits"], body["base"])["written_paths"] == []
    assert contents(service) == before


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("bom", [True, False])
def test_commit_preserves_bom_newlines_header_and_literal_quotes(service, newline, bom):
    write_loc(service.repo_root, EN, [("a", "A"), ("b", "B"), ("empty", "")],
              bom=bom, newline=newline, comments=True)
    zh_before = (service.repo_root / ZH).read_bytes()
    value = 'Literal "quotes", escaped \\"quotes\\", and \\n text'
    body = request_body(service, {EN: {"a": {"english": value}}})
    result = service.commit_edits(body["edits"], body["base"])
    raw = (service.repo_root / EN).read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf") is bom
    text = raw.decode("utf-8-sig")
    assert text.startswith("# retained header" + newline)
    assert "body section comment" not in text
    assert newline in text and "\n" not in text.replace(newline, "") and "\r" not in text.replace(newline, "")
    assert f' a: "{value}"' in text
    assert files_by_path(result)[EN]["languages"]["english"][0]["value"] == value
    assert (service.repo_root / ZH).read_bytes() == zh_before


@pytest.mark.parametrize("endpoint", ["validate", "preview", "commit"])
def test_generated_pair_rejects_both_entry_paths_with_data_hint(service, client, endpoint):
    registry(service.repo_root, [{"output": EN, "data": "data/owner.yaml + data/secondary.yaml"}])
    loaded = client.get(URL).json()
    assert all(item["read_only"] for item in files_by_path(loaded).values())
    for path in (EN, ZH):
        response = client.post(URL + "/" + endpoint, json=request_body(service, {path: {}}))
        assert response.status_code == 400
        assert "read_only" in response.json()["detail"]
        assert "data/owner.yaml" in response.json()["detail"]
        assert "data/secondary.yaml" in response.json()["detail"]


def test_internal_quotes_followed_by_formatting_are_not_truncated(service):
    value = 'Quoted "#bold emphasis#!", plus "more"'
    write_loc(service.repo_root, EN, [("a", value), ("b", "B"), ("empty", "")])
    assert files_by_path(service.load_resource())[EN]["languages"]["english"][0]["value"] == value
    updated = value + " updated"
    body = request_body(service, {EN: {"a": {"english": updated}}})
    result = service.commit_edits(body["edits"], body["base"])
    assert files_by_path(result)[EN]["languages"]["english"][0]["value"] == updated
    assert f' a: "{updated}"' in (service.repo_root / EN).read_text(encoding="utf-8-sig")


def test_generated_missing_keys_do_not_block_manual_coverage(service):
    managed = EN.replace("demo", "managed")
    write_loc(service.repo_root, managed, [("generated_missing", "Only EN")])
    registry(service.repo_root, [{"output": managed, "data": "data/owner.yaml"}])
    assert service.validate_edits({})["valid"] is True
    assert service.load_resource()["draft"]["missing_translations"] == []


@pytest.mark.parametrize("where", ["same_file", "another_file"])
def test_duplicate_keys_rejected_http_400(service, client, where):
    if where == "same_file":
        path = service.repo_root / EN
        path.write_bytes(path.read_bytes() + b' a: "Duplicate"\r\n')
    else:
        write_loc(service.repo_root, EN.replace("demo", "other"), [("a", "Duplicate")])
    response = client.post(URL + "/validate", json={"edits": {}})
    assert response.status_code == 400
    assert "Duplicate localization key" in response.json()["detail"]


def test_duplicate_edit_aliases_rejected_but_disjoint_languages_allowed(service):
    body = request_body(service, {EN: {"a": {"english": "First"}}, ZH: {"a": {"english": "Second"}}})
    with pytest.raises(ValueError, match="Duplicate localization edit"):
        service.preview_edits(body["edits"], body["base"])
    body["edits"][ZH]["a"] = {"simp_chinese": "第二"}
    assert len(service.preview_edits(body["edits"], body["base"])["diff"]) == 2


@pytest.mark.parametrize("changes", [
    {"bad key": {"english": "A"}}, {"a": {"english": None}}, {"a": {"english": 5}},
    {"a": {"english": "real\nnewline"}}, {"a": {"english": "carriage\rreturn"}},
    {"a": {"english": "nul\x00byte"}}, {"a": {"french": "Non"}}, {"a": []},
    {"a": {}}, {"unknown": None},
])
def test_invalid_rows_are_rejected(service, changes):
    with pytest.raises(ValueError):
        service.validate_edits({EN: changes})


@pytest.mark.parametrize("path", ["../outside.yml", "data/source.yaml", "/absolute.yml", EN.upper()])
def test_unknown_paths_rejected_http_400(service, client, path):
    response = client.post(URL + "/commit", json=request_body(service, {path: {}}))
    assert response.status_code == 400
    assert "Unknown localization file" in response.json()["detail"]


def test_missing_partner_is_reported_and_cannot_create_files(service):
    (service.repo_root / ZH).unlink()
    loaded = service.load_resource()
    assert loaded["draft"]["missing_translations"] == [{"path": ZH, "keys": ["a", "b", "empty"]}]
    with pytest.raises(ValueError, match="Missing paired localization file"):
        service.validate_edits({EN: {"a": {"english": "New"}}})
    assert not (service.repo_root / ZH).exists()


@pytest.mark.parametrize("endpoint", ["preview", "commit"])
def test_stale_base_conflict_409_even_after_another_client_reload(service, client, endpoint):
    body = request_body(service, {EN: {"a": {"english": "Client"}}})
    write_loc(service.repo_root, EN, [("a", "External"), ("b", "B"), ("empty", "")])
    assert client.get(URL).status_code == 200
    response = client.post(URL + "/" + endpoint, json=body)
    assert response.status_code == 409
    assert response.json()["code"] == "resource_changed"
    assert ' a:0 "External"' in (service.repo_root / EN).read_text(encoding="utf-8-sig")
    body = request_body(service, {EN: {"a": {"english": "Refreshed"}}})
    assert client.post(URL + "/" + endpoint, json=body).status_code == 200


def test_ownership_registry_change_conflicts_then_becomes_read_only(service, client):
    body = request_body(service, {EN: {"a": {"english": "No"}}})
    registry(service.repo_root, [{"output": EN, "data": "data/now_owned.yaml"}])
    response = client.post(URL + "/commit", json=body)
    assert response.status_code == 409
    body = request_body(service, body["edits"])
    assert client.post(URL + "/commit", json=body).status_code == 400


@pytest.mark.parametrize("kind", ["missing", "extra"])
def test_base_requires_full_resource(service, client, kind):
    body = request_body(service)
    if kind == "missing":
        body["base"].pop(localization.REGISTRY)
    else:
        body["base"]["outside.yml"] = "fake"
    assert client.post(URL + "/preview", json=body).status_code == 400


def test_write_failure_recovers_both_files_cache_operation_and_retry(service, client, monkeypatch):
    before = contents(service)
    body = request_body(service, {EN: {"a": {"english": "Changed", "simp_chinese": "修改"}}})
    original = localization.atomic_write_files

    def partial_write(files):
        first, content = next(iter(files.items()))
        first.write_bytes(content)
        raise OSError("injected second-file replacement failure")

    monkeypatch.setattr(localization, "atomic_write_files", partial_write)
    response = client.post(URL + "/commit", json=body)
    assert response.status_code == 500
    assert response.json()["operation"]["status"] == "failed"
    assert "injected second-file" in response.json()["detail"]
    assert contents(service) == before
    assert {path: document.raw for path, document in service._documents.items()} == before
    operation_id = response.json()["operation_id"]
    assert client.get("/api/operations/" + operation_id).json()["status"] == "failed"
    monkeypatch.setattr(localization, "atomic_write_files", original)
    assert client.post(URL + "/commit", json=body).status_code == 200


def test_post_write_reload_failure_restores_files_and_cache(service, monkeypatch):
    before = contents(service)
    body = request_body(service, {EN: {"a": {"english": "Changed"}}})
    original_reload = service.reload_from_disk
    calls = []

    def fail_once():
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError("injected post-write reload failure")
        original_reload()

    monkeypatch.setattr(service, "reload_from_disk", fail_once)
    with pytest.raises(RuntimeError, match="post-write reload") as error:
        service.commit_edits(body["edits"], body["base"])
    assert error.value.operation["status"] == "failed"
    assert len(calls) == 3
    assert contents(service) == before


def test_failed_rollback_is_visible_and_other_files_still_recover(service, monkeypatch):
    before = contents(service)
    body = request_body(service, {EN: {"a": {"english": "Changed", "simp_chinese": "修改"}}})
    original_restore_write = platform.atomic_write_files

    def write_then_fail(files):
        for path, content in files.items():
            path.write_bytes(content)
        raise OSError("injected write failure")

    def fail_one_restore(files):
        if service.repo_root / EN in files:
            raise PermissionError("injected locked EN recovery")
        original_restore_write(files)

    monkeypatch.setattr(localization, "atomic_write_files", write_then_fail)
    monkeypatch.setattr(platform, "atomic_write_files", fail_one_restore)
    with pytest.raises(platform.RollbackError, match="Rollback incomplete") as error:
        service.commit_edits(body["edits"], body["base"])
    assert "locked EN recovery" in str(error.value)
    assert error.value.operation["status"] == "failed"
    assert (service.repo_root / ZH).read_bytes() == before[ZH]
    assert (service.repo_root / EN).read_bytes() != before[EN]


def test_serialization_failure_writes_nothing(service, monkeypatch):
    before = contents(service)
    body = request_body(service, {EN: {"a": {"english": "Changed"}}})

    def fail_serialization(*args):
        raise RuntimeError("injected serialization failure")

    monkeypatch.setattr(localization, "source_text_bytes", fail_serialization)
    with pytest.raises(RuntimeError, match="serialization failure") as error:
        service.commit_edits(body["edits"], body["base"])
    assert error.value.operation["status"] == "failed"
    assert contents(service) == before


def test_conflict_after_serialization_does_not_overwrite_external_changes(service, monkeypatch):
    body = request_body(service, {EN: {"a": {"english": "Changed"}}})
    en_before = (service.repo_root / EN).read_bytes()
    original = localization.source_text_bytes

    def concurrent_change(path, text):
        content = original(path, text)
        write_loc(service.repo_root, ZH, [("a", "外部"), ("b", "乙"), ("empty", "")])
        return content

    monkeypatch.setattr(localization, "source_text_bytes", concurrent_change)
    with pytest.raises(platform.ConflictError):
        service.commit_edits(body["edits"], body["base"])
    assert (service.repo_root / EN).read_bytes() == en_before
    assert "外部" in (service.repo_root / ZH).read_text(encoding="utf-8-sig")


def test_existing_platform_resource_lock_is_used(service, client):
    body = request_body(service)
    with platform.resource_operation(("editor.localization",)):
        response = client.post(URL + "/commit", json=body)
    assert response.status_code == 409
    assert response.json()["code"] == "resource_busy"
    assert response.json()["operation"]["status"] == "failed"


def test_check_counts_are_per_mod_root_and_missing_keys_fail(service, monkeypatch):
    write_loc(service.repo_root, EN.replace("src/", "src_sample/"), [("other", "Other")])
    write_loc(service.repo_root, ZH.replace("src/", "src_sample/"), [("other", "其他")])
    monkeypatch.setattr(localization, "REPO_ROOT", service.repo_root)
    lines = localization.build_check_report()
    assert "hand-authored files=2" in lines[0] and "bilingual groups=1" in lines[0]
    assert "EN keys=3, ZH keys=3, missing keys=0" in lines[0]
    assert "src_sample" in lines[1] and "EN keys=1, ZH keys=1" in lines[1]
    write_loc(service.repo_root, ZH, [("a", "甲"), ("empty", "")])
    lines = localization.build_check_report()
    assert lines[0].startswith("[FAIL]") and "missing keys=1" in lines[0]


def test_real_repository_copy_discovery_commit_without_live_writes(tmp_path):
    expected = {}
    for root in REAL_ROOT.glob("src*"):
        if not root.is_dir():
            continue
        for path in root.glob("**/localization/**/*.yml"):
            relative = path.relative_to(REAL_ROOT).as_posix()
            expected[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
            target = tmp_path / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    (tmp_path / "data").mkdir()
    shutil.copy2(REAL_ROOT / localization.REGISTRY, tmp_path / localization.REGISTRY)
    service = localization.LocalizationEditorService(repo_root=tmp_path)
    loaded = service.load_resource()
    files = files_by_path(loaded)
    assert set(files) == set(expected)
    registered = {entry["output"] for entry in yaml.safe_load((tmp_path / localization.REGISTRY).read_bytes())["generated"]}
    assert all(files[path]["read_only"] for path in registered & set(files))
    writable = [path for path, item in files.items() if not item["read_only"]]
    assert writable
    path = writable[0]
    row = files[path]["languages"]["english"][0]
    edits = {path: {row["key"]: {"english": row["value"] + " WP-06 temporary-copy test"}}}
    body = request_body(service, edits)
    assert service.validate_edits(edits)["valid"] is True
    assert service.preview_edits(edits, body["base"])["diff"]
    result = service.commit_edits(edits, body["base"])
    assert result["operation"]["status"] == "succeeded"
    assert len(result["written_paths"]) == 1
    for relative, digest in expected.items():
        assert hashlib.sha256((REAL_ROOT / relative).read_bytes()).hexdigest() == digest
