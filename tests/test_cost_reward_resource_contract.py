from pathlib import Path

import pytest

from towards_victory_editor_web.services import cost_reward
from towards_victory_editor_web.services.cost_reward import ConflictError, CostRewardEditorService


@pytest.fixture
def service(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_file = data_dir / "cost_reward_units.yaml"
    task_file = data_dir / "task_pool.yaml"
    data_file.write_bytes(cost_reward.DATA_FILE.read_bytes())
    task_file.write_bytes(cost_reward.TASK_POOL_FILE.read_bytes())
    monkeypatch.setattr(cost_reward, "DATA_FILE", data_file)
    monkeypatch.setattr(cost_reward, "TASK_POOL_FILE", task_file)
    monkeypatch.setattr(cost_reward, "DATA_REL", "data/cost_reward_units.yaml")
    monkeypatch.setattr(cost_reward, "TASK_POOL_REL", "data/task_pool.yaml")
    monkeypatch.setattr(cost_reward, "REPO_ROOT", tmp_path)
    return CostRewardEditorService()


def test_validation_does_not_mutate_cached_draft(service):
    initial = service.load_resource()
    token = next(group["tokens"][0] for group in initial["draft"]["groups"] if group["key"] == "country_reward")
    response = service.validate_edits({"country_reward": {token["id"]: {"value": 777}}})
    assert response["valid"]
    current = service.load_resource()
    current_token = next(group["tokens"][0] for group in current["draft"]["groups"] if group["key"] == "country_reward")
    assert current_token["value"] == token["value"]


def test_unknown_category_and_preview_diff(service):
    response = service.validate_edits({"typo_category": {}})
    assert response["valid"] is False
    assert "Unknown category" in response["errors"][0]

    initial = service.load_resource()
    token = next(group["tokens"][0] for group in initial["draft"]["groups"] if group["key"] == "country_reward")
    response = service.preview_edits({"country_reward": {token["id"]: {"value": 777}}})
    assert response["diff"]
    assert response["diff"][0]["id"] == token["id"]
    assert response["diff"][0]["field"] == "value"


def test_commit_preserves_header_and_encoding_and_detects_conflict(service):
    initial = service.load_resource()
    token = next(group["tokens"][0] for group in initial["draft"]["groups"] if group["key"] == "country_reward")
    edits = {"country_reward": {token["id"]: {"value": token["value"] + 1}}}
    base = {item["path"]: item["sha256"] for item in initial["change_set"]["base"]}
    result = service.save_tokens(edits, base)
    assert result["draft"]
    raw = cost_reward.DATA_FILE.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert raw.startswith(b"# Foundational cost/reward unit catalog")
    with pytest.raises(ConflictError):
        service.save_tokens(edits, base)
