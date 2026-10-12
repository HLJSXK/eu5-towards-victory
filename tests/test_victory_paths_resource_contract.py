from pathlib import Path
import json
import shutil
import subprocess
import time

import pytest
from fastapi.testclient import TestClient

from scripts_engineering_department.wonder_mechanics.io import load_yaml
from towards_victory_editor_web.server import create_app
from towards_victory_editor_web.services import victory_paths
from towards_victory_editor_web.services.generator_runs import GeneratorRunService
from towards_victory_editor_web.services.platform import ConflictError


EXPECTED_SOURCES = {"data/victory_paths.yaml", "data/victory_path_tasks.yaml"}
EXPECTED_PATHS = {"conquest", "prosperity", "trade", "diplomatic", "cultural", "science"}


def _resource(client):
    response = client.get("/api/resources/editor.victory_paths")
    assert response.status_code == 200
    return response.json()


def _body(resource, document=None):
    return {
        "document": document if document is not None else resource["document"],
        "base": {"sources": resource["sources"]},
    }


def test_load_contract_and_registry_derived_plan():
    with TestClient(create_app()) as client:
        resource = _resource(client)
    assert resource["resource_id"] == "editor.victory_paths"
    assert {source["path"] for source in resource["sources"]} == EXPECTED_SOURCES
    encoded = json.dumps(resource)
    assert "victory_path_tree_variant.yaml" not in encoded
    assert "task_pool.yaml" not in encoded
    assert {path["id"] for path in resource["document"]["paths"]} == EXPECTED_PATHS
    assert all(len(path["milestones"]) == 5 for path in resource["document"]["paths"])
    assert all(len(milestone["reward_options"]) == 3 for path in resource["document"]["paths"] for milestone in path["milestones"])
    assert all({item["source"]["path_id"] for item in path["tasks"]["items"]} == {path["id"]} for path in resource["document"]["paths"])
    assert resource["document"]["national_special"] == {"tasks": []}

    generators = GeneratorRunService().generators()
    selected = [item for item in generators if EXPECTED_SOURCES.intersection(item["data_inputs"])]
    outputs = {output for item in selected for output in item["outputs"]}
    assert len(selected) == 17
    assert len(outputs) == 32
    assert resource["generation"]["registry_complete"] is True
    assert set(resource["generation"]["generators"]) == {item["script"] for item in selected}
    assert set(resource["generation"]["outputs"]) == outputs


def test_validate_and_preview_are_read_only_and_show_generation_plan():
    with TestClient(create_app()) as client:
        resource = _resource(client)
        before = {source["path"]: source["sha256"] for source in resource["sources"]}
        valid = client.post("/api/resources/editor.victory_paths/validate", json=_body(resource))
        assert valid.status_code == 200
        assert valid.json()["valid"] is True
        assert valid.json()["errors"] == []
        changed = json.loads(json.dumps(resource["document"]))
        changed["paths"][0]["milestones"][0]["threshold"] += 1
        preview = client.post("/api/resources/editor.victory_paths/preview", json=_body(resource, changed))
        assert preview.status_code == 200
        payload = preview.json()
        assert payload["ready"] is True
        assert any(item["field"].endswith("threshold") for item in payload["diff"]["fields"])
        assert len(payload["generation"]["generators"]) == 17
        assert len(payload["generation"]["outputs"]) == 32
        after = _resource(client)
        assert {source["path"]: source["sha256"] for source in after["sources"]} == before


def test_validation_rejects_structure_bilingual_slots_and_reference():
    with TestClient(create_app()) as client:
        resource = _resource(client)
        bad = json.loads(json.dumps(resource["document"]))
        bad["paths"][0]["milestones"] = bad["paths"][0]["milestones"][:4]
        bad["paths"][0]["milestones"][0]["reward_options"] = bad["paths"][0]["milestones"][0]["reward_options"][:2]
        bad["paths"][0]["tasks"]["items"][0]["fields"]["loc"].pop("zh")
        bad["paths"][0]["milestones"][0]["reward_options"][0]["modifier"] = {"definitely_unknown_reward": 1}
        response = client.post("/api/resources/editor.victory_paths/validate", json=_body(resource, bad))
        assert response.status_code == 200
        errors = response.json()["errors"]
        codes = {error["code"] for error in errors}
        assert {"invalid_milestones", "invalid_reward_options", "bilingual_required", "invalid_reward_reference"}.issubset(codes)


def test_base_conflict_is_409_without_operation():
    with TestClient(create_app()) as client:
        resource = _resource(client)
        stale = json.loads(json.dumps(resource["sources"]))
        stale[0]["sha256"] = "0" * 64
        response = client.post("/api/resources/editor.victory_paths/preview", json={"document": resource["document"], "base": {"sources": stale}})
        assert response.status_code == 409
        assert "operation_id" not in response.json()


def test_reward_reference_is_read_only_and_does_not_include_cost_reward_base():
    with TestClient(create_app()) as client:
        resource = _resource(client)
        assert all(item["editable_here"] is False for item in resource["references"]["rewards"])
        assert all(source["path"] in EXPECTED_SOURCES for source in resource["sources"])
        assert all("cost_reward" not in path for path in resource["generation"]["outputs"])


@pytest.mark.slow
def test_real_generators_byte_compare_in_temporary_repo(tmp_path):
    source_root = Path(__file__).resolve().parents[1]
    plan = [item for item in GeneratorRunService().generators() if EXPECTED_SOURCES.intersection(item["data_inputs"])]
    outputs = {output for item in plan for output in item["outputs"]}
    root = tmp_path / "repo"
    for relative in EXPECTED_SOURCES | {item["script"] for item in plan} | outputs:
        source = source_root / relative
        if source.exists():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    registry = source_root / "data/generated_files.yaml"
    target_registry = root / "data/generated_files.yaml"
    target_registry.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(registry, target_registry)
    required_inputs = set(EXPECTED_SOURCES)
    required_inputs.add("scripts/victory_task_codegen.py")
    required_inputs.add("scripts/victory_tree_node_codegen.py")
    required_inputs.add("scripts/victory_tree_point_badge_layout.py")
    required_inputs.add("reference_game_files/game/in_game/common/institution")
    required_inputs.add("reference_game_files/game/main_menu/gui/shared/font_icons.gui")
    required_inputs.add("reference_game_files/game/in_game/events/economy/prices.txt")
    required_inputs.add("reference_game_files/game/in_game/common/scripted_effects/international_organization_effects.txt")
    required_inputs.add("data/court_positions.yaml")
    for generator in plan:
        required_inputs.update(input_path for input_path in generator["data_inputs"] if not any(char in input_path for char in "*?[]"))
    for relative in required_inputs:
        source = source_root / relative
        if source.is_file():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        elif source.is_dir():
            shutil.copytree(source, root / relative, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest-*"))
    expected = tmp_path / "expected"
    shutil.copytree(root, expected, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest-*"))
    started = time.perf_counter()
    for generator in plan:
        command = [str(Path(r"C:\Users\Hades\anaconda3\envs\eu5\python.exe")), generator["script"]]
        result = subprocess.run(command, cwd=expected, capture_output=True, text=True, encoding="utf-8", timeout=120)
        assert result.returncode == 0, result.stdout + result.stderr
    elapsed = time.perf_counter() - started
    assert elapsed >= 0
    for output in outputs:
        assert (root / output).read_bytes().replace(bytes((13, 10)), bytes((10,))) == (expected / output).read_bytes().replace(bytes((13, 10)), bytes((10,)))
    print(f"victory_paths slow byte comparison: {elapsed:.3f}s; generators={len(plan)} outputs={len(outputs)}")
