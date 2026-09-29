import copy

import pytest
from fastapi.testclient import TestClient

from scripts_engineering_department.wonder_mechanics.io import dump_yaml_document, load_yaml
from towards_victory_editor_web.services import victory_tree
from towards_victory_editor_web.services.platform import ConflictError


VARIANT_SAMPLE = """paths:
  - id: sample
    trunk:
      - id: trunk_a
        effect: first
        value: 1
      - id: trunk_b
        effect: second
        value: 2
    branches:
      - id: branch
        attach_after: trunk_a
        nodes:
          - id: branch_a
            effect: third
            value: 3
"""
POSITIONS_SAMPLE = """sample:
  trunk_a: {x: 0.2, y: 0.3}
  trunk_b: {x: 0.4, y: 0.5}
  branch_a: {x: 0.6, y: 0.7}
"""


@pytest.fixture
def service(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    variant_file = data_dir / "victory_path_tree_variant.yaml"
    positions_file = data_dir / "victory_tree_node_positions.yaml"
    variant_file.write_text(VARIANT_SAMPLE, encoding="utf-8")
    positions_file.write_text(POSITIONS_SAMPLE, encoding="utf-8")
    monkeypatch.setattr(victory_tree, "TREE_VARIANT_FILE", variant_file)
    monkeypatch.setattr(victory_tree, "POSITIONS_FILE", positions_file)
    monkeypatch.setattr(victory_tree, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(victory_tree, "TREES_DIR", tmp_path / "trees")
    monkeypatch.setattr(victory_tree, "GENERATED_PREVIEWS_DIR", tmp_path / "previews")
    return victory_tree.VictoryTreePlannerService()


def _edits_for_first_path(resource):
    path = resource["draft"]["paths"][0]
    return {path["id"]: {node["id"]: {"x": node["x"], "y": node["y"]} for node in path["nodes"]}}


def _base(resource):
    return {item["path"]: item["sha256"] for item in resource["change_set"]["base"]}


def test_load_and_preview_match_tree_draft_without_mutation(service):
    initial = service.load_resource()
    assert initial["resource"]["id"] == "editor.victory_tree"
    assert initial["draft"]["paths"] == service.bootstrap_payload()["paths"]
    assert set(_base(initial)) == {victory_tree.TREE_VARIANT_REL, victory_tree.POSITIONS_REL}

    edits = _edits_for_first_path(initial)
    path_id = next(iter(edits))
    node_id = next(iter(edits[path_id]))
    old_x = edits[path_id][node_id]["x"]
    edits[path_id][node_id]["x"] = 0.9 if old_x < 0.5 else 0.1

    assert service.validate_edits(edits)["valid"]
    preview = service.preview_edits(edits, _base(initial))
    assert preview["diff"] == [
        {
            "path": victory_tree.POSITIONS_REL,
            "id": f"{path_id}.{node_id}",
            "field": "x",
            "before": old_x,
            "after": edits[path_id][node_id]["x"],
        }
    ]
    assert service.load_resource()["draft"] == initial["draft"]


def test_validation_rejects_bad_nodes_and_coordinates(service):
    initial = service.load_resource()
    edits = _edits_for_first_path(initial)
    path_id = next(iter(edits))
    node_id = next(iter(edits[path_id]))

    missing = copy.deepcopy(edits)
    del missing[path_id][node_id]
    assert "node id mismatch" in service.validate_edits(missing)["errors"][0]

    for invalid in (-0.01, 1.01, "nan", "not a number", True):
        bad = copy.deepcopy(edits)
        bad[path_id][node_id]["x"] = invalid
        assert service.validate_edits(bad)["valid"] is False

    assert service.validate_edits({"unknown_path": {}})["valid"] is False


def test_commit_preserves_encoding_and_detects_external_changes(service):
    initial = service.load_resource()
    edits = _edits_for_first_path(initial)
    path_id = next(iter(edits))
    node_id = next(iter(edits[path_id]))
    edits[path_id][node_id]["x"] += 0.01
    positions_file = victory_tree.POSITIONS_FILE
    variant_file = victory_tree.TREE_VARIANT_FILE
    original_variant = variant_file.read_bytes()

    result = service.save_positions(edits, _base(initial))
    assert result["draft"]["paths"][0]["nodes"][0]["x"] == round(edits[path_id][node_id]["x"], 4)
    assert not positions_file.read_bytes().startswith(b"\xef\xbb\xbf")
    assert variant_file.read_bytes() == original_variant
    with pytest.raises(ConflictError):
        service.save_positions(edits, _base(initial))

    current = service.load_resource()
    saved_positions = positions_file.read_bytes()
    variant_file.write_bytes(original_variant + b"\n# external change\n")
    with pytest.raises(ConflictError):
        service.save_positions(edits, _base(current))
    assert positions_file.read_bytes() == saved_positions


def test_failed_write_keeps_disk_and_cached_draft(service, monkeypatch):
    initial = service.load_resource()
    edits = _edits_for_first_path(initial)
    path_id = next(iter(edits))
    node_id = next(iter(edits[path_id]))
    edits[path_id][node_id]["x"] += 0.01
    before = victory_tree.POSITIONS_FILE.read_bytes()

    def fail_write(_files):
        raise OSError("simulated write failure")

    monkeypatch.setattr(victory_tree, "atomic_write_files", fail_write)
    with pytest.raises(OSError, match="simulated write failure"):
        service.save_positions(edits, _base(initial))
    assert victory_tree.POSITIONS_FILE.read_bytes() == before
    assert service.load_resource()["draft"] == initial["draft"]


def test_missing_positions_file_uses_defaults_until_first_edit(service):
    victory_tree.POSITIONS_FILE.unlink()
    initial = service.load_resource()
    assert _base(initial)[victory_tree.POSITIONS_REL] == "missing"
    result = service.save_positions({}, _base(initial))
    assert victory_tree.POSITIONS_FILE.exists()
    assert result["draft"]["paths"] == initial["draft"]["paths"]


def test_reload_preserves_matching_nodes_when_variant_changes(service):
    initial = service.load_resource()
    variant = load_yaml(victory_tree.TREE_VARIANT_FILE)
    variant["paths"][0]["branches"][0]["nodes"] = [
        {"id": "branch_new", "effect": "new", "value": 4}
    ]
    victory_tree.TREE_VARIANT_FILE.write_text(dump_yaml_document(variant), encoding="utf-8")
    with pytest.raises(ConflictError):
        service.preview_edits(_edits_for_first_path(initial), _base(initial))
    refreshed = service.load_resource()
    nodes = {node["id"]: node for node in refreshed["draft"]["paths"][0]["nodes"]}
    assert set(nodes) == {"trunk_a", "trunk_b", "branch_new"}
    assert (nodes["trunk_a"]["x"], nodes["trunk_a"]["y"]) == (0.2, 0.3)
    assert (nodes["trunk_b"]["x"], nodes["trunk_b"]["y"]) == (0.4, 0.5)
    assert nodes["branch_new"]["x"] == nodes["branch_new"]["default_x"]
    service.save_positions({}, _base(refreshed))
    saved = load_yaml(victory_tree.POSITIONS_FILE)["sample"]
    assert set(saved) == set(nodes)
    assert saved["trunk_a"] == {"x": 0.2, "y": 0.3}


def test_deleted_positions_conflict_until_reload(service):
    loaded = service.load_resource()
    victory_tree.POSITIONS_FILE.unlink()
    with pytest.raises(ConflictError):
        service.save_positions({}, _base(loaded))
    refreshed = service.load_resource()
    assert _base(refreshed)[victory_tree.POSITIONS_REL] == "missing"
    assert service.save_positions({}, _base(refreshed))["draft"]


def test_stale_tab_cannot_refresh_base_through_preview(service):
    stale_tab = service.load_resource()
    stale_base = _base(stale_tab)
    edits = _edits_for_first_path(stale_tab)
    positions = load_yaml(victory_tree.POSITIONS_FILE)
    positions["sample"]["trunk_b"]["x"] = 0.55
    victory_tree.POSITIONS_FILE.write_text(dump_yaml_document(positions), encoding="utf-8")

    fresh_tab = service.load_resource()
    with pytest.raises(ConflictError):
        service.preview_edits(edits, stale_base)
    with pytest.raises(ConflictError):
        service.save_positions(edits, stale_base)
    assert load_yaml(victory_tree.POSITIONS_FILE)["sample"]["trunk_b"]["x"] == 0.55
    assert service.preview_edits(_edits_for_first_path(fresh_tab), _base(fresh_tab))["diff"] == []


def test_malformed_stored_coordinate_reports_source(service):
    victory_tree.POSITIONS_FILE.write_text(
        POSITIONS_SAMPLE.replace("trunk_b: {x: 0.4, y: 0.5}", "trunk_b: {x: 0.4}"), encoding="utf-8"
    )
    with pytest.raises(RuntimeError, match=r"sample\.trunk_b must have numeric x/y"):
        service.load_resource()


def test_http_bad_id_missing_base_and_conflict(service, monkeypatch):
    from towards_victory_editor_web import server

    monkeypatch.setattr(server, "VictoryTreePlannerService", lambda: service)
    with TestClient(server.create_app()) as client:
        loaded = client.get("/api/resources/editor.victory_tree").json()
        base = _base(loaded)
        endpoint = "/api/resources/editor.victory_tree/commit"
        assert client.post(endpoint, json={"edits": {}, "base": {}}).status_code == 400
        bad = client.post(endpoint, json={"edits": {"nope": {}}, "base": base})
        assert bad.status_code == 400
        assert bad.json()["detail"] == "Unknown victory path id: nope"
        preview = "/api/resources/editor.victory_tree/preview"
        assert client.post(preview, json={"edits": {}}).status_code == 400
        victory_tree.POSITIONS_FILE.write_bytes(victory_tree.POSITIONS_FILE.read_bytes() + b"\n# external\n")
        assert client.post(endpoint, json={"edits": {}, "base": base}).status_code == 409
        assert client.post(preview, json={"edits": {}, "base": base}).status_code == 409
