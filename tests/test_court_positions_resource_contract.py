from pathlib import Path
import copy
import json
import shutil
import subprocess
import sys
import time

import pytest
from fastapi.testclient import TestClient

from scripts_engineering_department.wonder_mechanics.io import load_yaml
from towards_victory_editor_web import server
from towards_victory_editor_web.services import court_positions
from towards_victory_editor_web.services.generator_runs import GeneratorRunError, GeneratorRunService
from towards_victory_editor_web.services.operation_store import OperationStore
from towards_victory_editor_web.services.platform import ConflictError, atomic_write_files, yaml_bytes


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCES = {"data/court_positions.yaml"}
RESOURCE_URL = "/api/resources/editor.court_positions"
MODIFIER_SCHEMA = "reference_game_files/game/main_menu/common/modifier_type_definitions/00_modifier_types.txt"
TEST_OUTPUTS = ["src_court_positions/changed.txt", "src_court_positions/unchanged.txt", "src_court_positions/new.txt"]


def _body(resource, document=None):
    return {"document": resource["document"] if document is None else document, "base": {"sources": resource["sources"]}}


def _service_in_repo(root, monkeypatch):
    monkeypatch.setattr(court_positions, "REPO_ROOT", root)
    monkeypatch.setattr(court_positions, "SOURCE_FILE", root / court_positions.SOURCE_REL)
    return court_positions.CourtPositionsEditorService()


def _tracked_bytes(root, paths):
    return {relative: (root / relative).read_bytes() if (root / relative).exists() else None for relative in paths}


def _copy_file(root, relative):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / relative, target)


@pytest.fixture
def temporary_service(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    for relative in EXPECTED_SOURCES | {MODIFIER_SCHEMA}:
        _copy_file(root, relative)
    service = _service_in_repo(root, monkeypatch)
    monkeypatch.setattr(service.generator_service, "generators", lambda: [{
        "script": "scripts/gen_test.py", "data_inputs": sorted(EXPECTED_SOURCES), "outputs": TEST_OUTPUTS,
    }])
    atomic_write_files({court_positions.SOURCE_FILE: yaml_bytes(court_positions.SOURCE_FILE, service.data)})
    service.reload_from_disk()
    (root / "src_court_positions").mkdir()
    (root / TEST_OUTPUTS[0]).write_bytes(b"before")
    (root / TEST_OUTPUTS[1]).write_bytes(b"unchanged")
    return service


def test_load_contract_and_registry_derived_plan(without_wonder_service):
    with TestClient(server.create_app()) as client:
        response = client.get(RESOURCE_URL)
        assert response.status_code == 200
        resource = response.json()
    assert resource["resource_id"] == "editor.court_positions"
    assert resource["schema_version"] == 1
    assert {source["path"] for source in resource["sources"]} == EXPECTED_SOURCES
    assert resource["document"] == load_yaml(REPO_ROOT / court_positions.SOURCE_REL)
    assert len(resource["document"]["positions"]) == 6
    assert resource["read_only_outputs"] is True
    assert "src_eureka" not in json.dumps(resource)
    assert all(reference["resolved"] and not reference["editable_here"] and not reference["editable"]
               for reference in resource["references"]["rewards"])
    assert resource["references"]["tasks"] == []
    selected = [item for item in GeneratorRunService().generators() if EXPECTED_SOURCES.intersection(item["data_inputs"])]
    outputs = {output for item in selected for output in item["outputs"]}
    assert len(selected) == 10
    assert len(outputs) == 10
    assert resource["generation"]["registry_complete"] is True
    assert resource["generation"]["required"] is False
    assert resource["generation"]["generators"] == [item["script"] for item in selected]
    assert set(resource["generation"]["outputs"]) == outputs


def test_validate_and_preview_are_read_only(temporary_service, monkeypatch, without_wonder_service):
    service = temporary_service
    monkeypatch.setattr(server, "CourtPositionsEditorService", lambda *args, **kwargs: service)
    monkeypatch.setattr(service.generator_service, "run", lambda *args: pytest.fail("Preview/validate must not generate"))
    root = service.generator_service.repo_root
    before = _tracked_bytes(root, EXPECTED_SOURCES | set(TEST_OUTPUTS))
    with TestClient(server.create_app()) as client:
        resource = client.get(RESOURCE_URL).json()
        valid = client.post(RESOURCE_URL + "/validate", json=_body(resource))
        assert valid.status_code == 200
        assert valid.json()["valid"] is True
        document = copy.deepcopy(resource["document"])
        document["positions"][0]["effect_at_100"] += 0.01
        preview = client.post(RESOURCE_URL + "/preview", json=_body(resource, document))
        assert preview.status_code == 200
        payload = preview.json()
        assert payload["ready"] is True
        assert payload["generation"]["required"] is True
        assert payload["written_paths"] == [court_positions.SOURCE_REL]
        assert payload["diff"]["fields"] == [{
            "path": court_positions.SOURCE_REL, "field": "positions[0].effect_at_100", "before": 0.05,
            "after": document["positions"][0]["effect_at_100"],
        }]
        assert payload["diff"]["sources"][0]["before_sha256"] == resource["sources"][0]["sha256"]
        assert client.get(RESOURCE_URL).json()["sources"] == resource["sources"]
    assert _tracked_bytes(root, before) == before


@pytest.mark.parametrize("field,value,code", [
    ("id", "../unsafe", "invalid_position_id"),
    ("id", "tutor", "duplicate_position_id"),
    ("name_zh", None, "bilingual_required"),
    ("ability_en", "", "bilingual_required"),
    ("effect_zh", 12, "bilingual_required"),
    ("ability", "unknown", "invalid_ability"),
    ("ability", [], "invalid_ability"),
    ("artist_only", 1, "invalid_boolean"),
    ("ability", "artist_skill", "invalid_artist_position"),
    ("effect_at_100", True, "invalid_number"),
    ("effect_at_100", float("inf"), "invalid_number"),
    ("effect_at_100", float("nan"), "invalid_number"),
    ("modifier", "unknown_court_modifier", "invalid_reward_reference"),
    ("modifier", "../unsafe", "invalid_modifier"),
    ("runtime_slot", 1, "invalid_position_fields"),
])
def test_validation_rejects_invalid_fields(temporary_service, field, value, code):
    resource = temporary_service.load_resource()
    resource["document"]["positions"][0][field] = value
    validation = temporary_service.validate_document(resource["document"])
    assert validation["valid"] is False
    assert code in {item["code"] for item in validation["errors"]}


@pytest.mark.parametrize("document,code", [
    ({}, "invalid_document"), ({"positions": {}, "other": []}, "invalid_document"),
    ({"positions": {}}, "invalid_positions"), ({"positions": []}, "invalid_positions"),
    ({"positions": [None] * 6}, "invalid_position"),
])
def test_validation_rejects_invalid_structure(temporary_service, document, code):
    validation = temporary_service.validate_document(document)
    assert validation["valid"] is False
    assert code in {item["code"] for item in validation["errors"]}


def test_missing_reference_blocks_all_write_routes(temporary_service, monkeypatch, without_wonder_service):
    service = temporary_service
    monkeypatch.setattr(server, "CourtPositionsEditorService", lambda *args, **kwargs: service)
    root = service.generator_service.repo_root
    before = _tracked_bytes(root, EXPECTED_SOURCES | set(TEST_OUTPUTS))
    with TestClient(server.create_app()) as client:
        resource = client.get(RESOURCE_URL).json()
        resource["document"]["positions"][0]["modifier"] = "unknown_court_modifier"
        valid = client.post(RESOURCE_URL + "/validate", json=_body(resource))
        assert valid.status_code == 200
        assert "invalid_reward_reference" in {item["code"] for item in valid.json()["errors"]}
        assert any(not reference["resolved"] for reference in valid.json()["references"]["rewards"])
        preview = client.post(RESOURCE_URL + "/preview", json=_body(resource))
        assert preview.status_code == 200
        assert preview.json()["ready"] is False
        commit = client.post(RESOURCE_URL + "/commit", json=_body(resource))
        assert commit.status_code == 400
        assert "operation_id" not in commit.json()
    assert _tracked_bytes(root, before) == before


def test_reference_removed_after_load_is_not_grandfathered(temporary_service):
    resource = temporary_service.load_resource()
    root = temporary_service.generator_service.repo_root
    (root / MODIFIER_SCHEMA).unlink()
    validation = temporary_service.validate_document(resource["document"])
    assert validation["valid"] is False
    assert {item["code"] for item in validation["errors"]} == {"invalid_reward_reference"}


def test_cost_reward_reference_is_read_only_and_refreshed(temporary_service):
    root = temporary_service.generator_service.repo_root
    catalog_path = root / "data/cost_reward_units.yaml"
    catalog_path.write_bytes(yaml_bytes(catalog_path, {"units": [{"id": "court_catalog_modifier"}]}))
    document = temporary_service.load_resource()["document"]
    document["positions"][0]["modifier"] = "court_catalog_modifier"
    validation = temporary_service.validate_document(document)
    assert validation["valid"] is True
    reference = next(item for item in validation["references"]["rewards"] if item["key"] == "court_catalog_modifier")
    assert reference == {"key": "court_catalog_modifier", "resolved": True, "source_resource": "editor.cost_reward",
                         "editable": False, "editable_here": False}
    catalog_path.write_bytes(yaml_bytes(catalog_path, {"units": []}))
    assert temporary_service.validate_document(document)["valid"] is False
    assert {item["path"] for item in temporary_service.load_resource()["sources"]} == EXPECTED_SOURCES


def test_base_conflict_and_bounds(temporary_service, monkeypatch, without_wonder_service):
    monkeypatch.setattr(server, "CourtPositionsEditorService", lambda *args, **kwargs: temporary_service)
    with TestClient(server.create_app()) as client:
        resource = client.get(RESOURCE_URL).json()
        stale = _body(resource)
        stale["base"]["sources"][0]["sha256"] = "0" * 64
        for action in ("preview", "commit"):
            response = client.post(RESOURCE_URL + "/" + action, json=stale)
            assert response.status_code == 409
            assert "operation_id" not in response.json()
        for sources in ([], resource["sources"] * 2, [{"path": "../outside.yaml", "sha256": "0" * 64}]):
            response = client.post(RESOURCE_URL + "/commit", json={"document": resource["document"], "base": {"sources": sources}})
            assert response.status_code == 400


def test_external_source_change_blocks_commit(temporary_service):
    resource = temporary_service.load_resource()
    court_positions.SOURCE_FILE.write_bytes(court_positions.SOURCE_FILE.read_bytes() + b"\n# external\n")
    with pytest.raises(ConflictError):
        temporary_service.commit_document(resource["document"], {"sources": resource["sources"]})


@pytest.mark.parametrize("failure", ["missing", "empty_outputs", "conflict", "registry_error"])
def test_registry_failures_block_commit(temporary_service, monkeypatch, failure):
    resource = temporary_service.load_resource()
    document = resource["document"]
    document["positions"][0]["effect_at_100"] += 0.01
    selected = [{"script": "scripts/gen_test.py", "data_inputs": [court_positions.SOURCE_REL], "outputs": TEST_OUTPUTS}]
    if failure == "missing":
        selected = []
    elif failure == "empty_outputs":
        selected[0]["outputs"] = []
    elif failure == "conflict":
        selected.append({**selected[0], "script": "scripts/gen_other.py"})
    def generators():
        if failure == "registry_error":
            raise ValueError("path_out_of_bounds")
        return selected
    monkeypatch.setattr(temporary_service.generator_service, "generators", generators)
    before = court_positions.SOURCE_FILE.read_bytes()
    assert temporary_service.validate_document(document)["valid"] is False
    assert temporary_service.preview_document(document, {"sources": resource["sources"]})["ready"] is False
    with pytest.raises(ValueError, match="validation failed"):
        temporary_service.commit_document(document, {"sources": resource["sources"]})
    assert court_positions.SOURCE_FILE.read_bytes() == before


def test_generation_roots_follow_registry_changes(temporary_service, monkeypatch):
    monkeypatch.setattr(temporary_service.generator_service, "generators", lambda: [
        {"script": "scripts/new_generator.py", "data_inputs": [court_positions.SOURCE_REL], "outputs": ["src_court_positions/new.txt"]},
        {"script": "scripts/unrelated.py", "data_inputs": ["data/unrelated.yaml"], "outputs": ["src/unrelated.txt"]},
    ])
    plan = temporary_service.load_resource()["generation"]
    assert plan["generators"] == ["scripts/new_generator.py"]
    assert plan["outputs"] == ["src_court_positions/new.txt"]


def _fake_generate(service, document):
    root = service.generator_service.repo_root
    def generate(scripts):
        assert scripts == ["scripts/gen_test.py"]
        assert load_yaml(root / court_positions.SOURCE_REL) == document
        atomic_write_files({root / TEST_OUTPUTS[0]: b"after", root / TEST_OUTPUTS[2]: b"new"})
        return {"artifacts": [
            {"path": TEST_OUTPUTS[0], "changed": True}, {"path": TEST_OUTPUTS[1], "changed": False},
            {"path": TEST_OUTPUTS[2], "changed": True}, {"path": TEST_OUTPUTS[0], "changed": True},
        ]}
    return generate


def test_commit_source_first_and_written_paths_filter(temporary_service, monkeypatch, without_wonder_service):
    service = temporary_service
    monkeypatch.setattr(server, "CourtPositionsEditorService", lambda *args, **kwargs: service)
    root = service.generator_service.repo_root
    before = _tracked_bytes(root, EXPECTED_SOURCES | set(TEST_OUTPUTS))
    with TestClient(server.create_app()) as client:
        resource = client.get(RESOURCE_URL).json()
        document = resource["document"]
        document["positions"][0]["effect_at_100"] += 0.01
        monkeypatch.setattr(service.generator_service, "run", _fake_generate(service, document))
        response = client.post(RESOURCE_URL + "/commit", json={**_body(resource, document), "message": "court update"})
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "succeeded"
        assert result["message"] == "court update"
        assert result["base"]["sources"] == result["sources"]
        operation = client.get("/api/operations/" + result["operation_id"]).json()
        assert operation["status"] == "succeeded"
        assert "editor.court_positions" in operation["resource_ids"]
    changed = {relative for relative in before if before[relative] != (root / relative).read_bytes()}
    assert changed == EXPECTED_SOURCES | {TEST_OUTPUTS[0], TEST_OUTPUTS[2]}
    assert set(result["written_paths"]) == changed
    assert len(result["written_paths"]) == len(changed)


def test_noop_commit_has_no_written_paths(temporary_service, monkeypatch):
    resource = temporary_service.load_resource()
    monkeypatch.setattr(temporary_service.generator_service, "run", lambda *args: pytest.fail("No-op must not generate"))
    result = temporary_service.commit_document(resource["document"], {"sources": resource["sources"]})
    assert result["written_paths"] == []
    assert result["generation"]["status"] == "not_required"


@pytest.mark.parametrize("failure,expected_error", [
    ("artifact", "artifact validation failed"), ("exit", "exited with 1"),
    ("extra", "Unregistered artifacts"), ("path", "Invalid repository path"),
])
def test_generator_contract_failure_rolls_back_source(temporary_service, monkeypatch, failure, expected_error):
    service = temporary_service
    root = service.generator_service.repo_root
    script = root / "scripts/gen_test.py"
    script.parent.mkdir()
    body = "from pathlib import Path\nimport sys\n"
    body += f"Path({TEST_OUTPUTS[0]!r}).write_bytes(b'}}')\n" if failure == "artifact" else f"Path({TEST_OUTPUTS[0]!r}).write_bytes(b'after')\n"
    if failure == "exit":
        body += "sys.exit(1)\n"
    elif failure == "extra":
        body += "Path('undeclared.txt').write_bytes(b'extra')\n"
    script.write_text(body, encoding="utf-8")
    registry = {"generated": [{"script": "scripts/gen_test.py", "data": court_positions.SOURCE_REL,
                               "output": "../outside.txt" if failure == "path" else TEST_OUTPUTS[0]}]}
    registry_path = root / "data/generated_files.yaml"
    registry_path.write_bytes(yaml_bytes(registry_path, registry))
    monkeypatch.setattr(service, "generator_service", GeneratorRunService(repo_root=root))
    resource = service.load_resource()
    document = resource["document"]
    document["positions"][0]["effect_at_100"] += 0.01
    before = _tracked_bytes(root, EXPECTED_SOURCES | set(TEST_OUTPUTS))
    with pytest.raises((GeneratorRunError, ValueError), match=expected_error):
        service.commit_document(document, {"sources": resource["sources"]})
    assert _tracked_bytes(root, before) == before
    assert not (root / "undeclared.txt").exists()


@pytest.mark.parametrize("failure_stage", ["source", "generator", "reload"])
def test_commit_failure_rolls_back_sources_and_outputs(temporary_service, monkeypatch, failure_stage):
    service = temporary_service
    resource = service.load_resource()
    document = resource["document"]
    document["positions"][0]["effect_at_100"] += 0.01
    root = service.generator_service.repo_root
    before = _tracked_bytes(root, EXPECTED_SOURCES | set(TEST_OUTPUTS))
    generate = _fake_generate(service, document)
    def fail_generate(scripts):
        result = generate(scripts)
        if failure_stage == "generator":
            raise RuntimeError("injected failure")
        return result
    monkeypatch.setattr(service.generator_service, "run", fail_generate)
    if failure_stage == "source":
        def fail_write(files):
            atomic_write_files(files)
            raise RuntimeError("injected failure")
        monkeypatch.setattr(court_positions, "atomic_write_files", fail_write)
    elif failure_stage == "reload":
        reload_from_disk = service.reload_from_disk
        def fail_reload():
            if court_positions.SOURCE_FILE.read_bytes() != before[court_positions.SOURCE_REL]:
                raise RuntimeError("injected failure")
            reload_from_disk()
        monkeypatch.setattr(service, "reload_from_disk", fail_reload)
    store = OperationStore(":memory:")
    try:
        service.operation_store = store
        with pytest.raises(RuntimeError, match="injected failure") as caught:
            service.commit_document(document, {"sources": resource["sources"]})
        assert caught.value.operation["status"] == "failed"
        operation, details = store.get_with_details(caught.value.operation["id"])
        assert operation["status"] == "failed"
        assert details["rollback"]["status"] == "completed"
        assert details["written_paths"] == []
    finally:
        store.close()
    assert _tracked_bytes(root, before) == before
    assert service.load_resource()["sources"] == resource["sources"]


@pytest.mark.parametrize("bom,newline", [(False, "\n"), (True, "\r\n")])
def test_yaml_write_boundary(temporary_service, monkeypatch, bom, newline):
    source = court_positions.SOURCE_FILE
    text = source.read_text(encoding="utf-8-sig").replace("positions:\n", "positions:\n  # body section\n", 1)
    source.write_bytes(text.replace("\n", newline).encode("utf-8-sig" if bom else "utf-8"))
    resource = temporary_service.load_resource()
    document = resource["document"]
    document["positions"][0]["name_en"] += " Updated"
    monkeypatch.setattr(temporary_service.generator_service, "run", _fake_generate(temporary_service, document))
    temporary_service.commit_document(document, {"sources": resource["sources"]})
    after = source.read_bytes()
    assert after.startswith(bytes((239, 187, 191))) is bom
    assert b"# Canonical data for the standalone Court Positions mod." in after
    assert b"# Ability values are normalized" in after
    assert b"# body section" not in after
    assert (b"\r\n" in after) is (newline == "\r\n")
    assert load_yaml(source) == document


def _copy_generator_repo(tmp_path):
    selected = [item for item in GeneratorRunService().generators() if EXPECTED_SOURCES.intersection(item["data_inputs"])]
    scripts = {item["script"] for item in selected}
    outputs = {output for item in selected for output in item["outputs"]}
    inputs = {path for item in selected for path in item["data_inputs"]}
    root = tmp_path / "repo"
    for relative in inputs | scripts | outputs | {MODIFIER_SCHEMA, "scripts_court_positions/court_positions_codegen.py"}:
        _copy_file(root, relative)
    registry = load_yaml(REPO_ROOT / "data/generated_files.yaml")
    registry["generated"] = [entry for entry in registry["generated"] if entry["script"] in scripts]
    (root / "data/generated_files.yaml").write_bytes(yaml_bytes(REPO_ROOT / "data/generated_files.yaml", registry))
    return root, selected, outputs


@pytest.mark.slow
def test_real_generators_byte_compare_in_temporary_repo(tmp_path):
    root, selected, outputs = _copy_generator_repo(tmp_path)
    expected = tmp_path / "expected"
    shutil.copytree(root, expected)
    started = time.perf_counter()
    for generator in selected:
        result = subprocess.run([sys.executable, generator["script"]], cwd=expected, capture_output=True, encoding="utf-8", timeout=120)
        assert result.returncode == 0, result.stdout + result.stderr
    result = GeneratorRunService(repo_root=root).run([item["script"] for item in selected])
    assert result["operation"]["status"] == "succeeded"
    assert {artifact["path"] for artifact in result["artifacts"]} == outputs
    for output in outputs:
        assert (root / output).read_bytes() == (expected / output).read_bytes()
        assert (REPO_ROOT / output).read_bytes().replace(b"\r\n", b"\n") == (expected / output).read_bytes().replace(b"\r\n", b"\n")
    print(f"court_positions byte comparison: {time.perf_counter() - started:.3f}s; generators={len(selected)} outputs={len(outputs)}")


@pytest.mark.slow
def test_commit_real_generators_use_new_source_and_report_changed_paths(tmp_path, monkeypatch):
    root, selected, outputs = _copy_generator_repo(tmp_path)
    service = _service_in_repo(root, monkeypatch)
    resource = service.load_resource()
    document = resource["document"]
    document["positions"][0]["effect_at_100"] = 0.07
    document["positions"][0]["name_en"] = "Updated Court Physician"
    before = _tracked_bytes(root, EXPECTED_SOURCES | outputs)
    expected = tmp_path / "expected"
    shutil.copytree(root, expected)
    (expected / court_positions.SOURCE_REL).write_bytes(yaml_bytes(root / court_positions.SOURCE_REL, document))
    for generator in selected:
        process = subprocess.run([sys.executable, generator["script"]], cwd=expected, capture_output=True, encoding="utf-8", timeout=120)
        assert process.returncode == 0, process.stdout + process.stderr
    result = service.commit_document(document, {"sources": resource["sources"]})
    assert result["status"] == "succeeded"
    assert result["generation"]["status"] == "succeeded"
    assert len(result["generation"]["generators"]) == len(selected)
    assert load_yaml(root / court_positions.SOURCE_REL) == document
    for output in outputs:
        assert (root / output).read_bytes() == (expected / output).read_bytes()
    changed = {relative for relative in before if before[relative] != (root / relative).read_bytes()}
    assert set(result["written_paths"]) == changed
    assert len(result["written_paths"]) == len(changed)
    assert outputs - changed
    assert not (outputs - changed).intersection(result["written_paths"])
    assert {artifact["path"] for artifact in result["generation"]["artifacts"] if artifact["changed"]} == changed - EXPECTED_SOURCES
