import pytest
from fastapi.testclient import TestClient

from towards_victory_editor_web.services import cost_reward
from towards_victory_editor_web.services.cost_reward import CostRewardEditorService
from towards_victory_editor_web.services.platform import ConflictError, resource_operation
from scripts_engineering_department.wonder_mechanics.io import dump_yaml_document, load_yaml


COST_SAMPLE = """# Foundational cost/reward unit catalog
country_reward:
  - id: sample_one
    value: 0.2
  - id: sample_two
    value: 0.3
"""
TASK_SAMPLE = """on_action_task:
  - id: sample_action
    wired: false
    completion_note: sample
trigger_task:
  - id: sample_trigger
    comparison: gte
    representative_threshold: 1
"""
UNIQUE_SAMPLE = """unique_wonders:
- id: 101
  ceremony:
    stages:
""" + "".join(
    f"    - title_en: stage_{index}\n      cost:\n        - catalog: country_reward\n          type: sample_one\n          value: {-0.2 if index % 2 else -0.4}{' # authored' if index == 1 else ''}\n"
    for index in range(1, 9)
)


@pytest.fixture
def service(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_file = data_dir / "cost_reward_units.yaml"
    task_file = data_dir / "task_pool.yaml"
    unique_file = data_dir / "unique_wonders.yaml"
    data_file.write_text(COST_SAMPLE, encoding="utf-8")
    task_file.write_text(TASK_SAMPLE, encoding="utf-8")
    unique_file.write_text("unique_wonders: []\n", encoding="utf-8")
    monkeypatch.setattr(cost_reward, "DATA_FILE", data_file)
    monkeypatch.setattr(cost_reward, "TASK_POOL_FILE", task_file)
    monkeypatch.setattr(cost_reward, "UNIQUE_WONDERS_FILE", unique_file)
    monkeypatch.setattr(cost_reward, "DATA_REL", "data/cost_reward_units.yaml")
    monkeypatch.setattr(cost_reward, "TASK_POOL_REL", "data/task_pool.yaml")
    monkeypatch.setattr(cost_reward, "REPO_ROOT", tmp_path)
    from towards_victory_editor_web.services.generation import GenerationPlan
    monkeypatch.setattr(cost_reward, "wonder_generation_plan", lambda changed, **kwargs: GenerationPlan(tmp_path, ()))
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
    base = {item["path"]: item["sha256"] for item in initial["change_set"]["base"]}
    token = next(group["tokens"][0] for group in initial["draft"]["groups"] if group["key"] == "country_reward")
    response = service.preview_edits({"country_reward": {token["id"]: {"value": 777}}}, base)
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


def test_reload_uses_external_changes_and_old_base_cannot_commit(service):
    initial = service.load_resource()
    old_base = {item["path"]: item["sha256"] for item in initial["change_set"]["base"]}
    data = load_yaml(cost_reward.DATA_FILE)
    data["country_reward"][1]["value"] = 777
    cost_reward.DATA_FILE.write_text(dump_yaml_document(data), encoding="utf-8")

    with pytest.raises(ConflictError):
        service.preview_edits({"country_reward": {"sample_one": {"value": 42}}}, old_base)
    with pytest.raises(ConflictError):
        service.save_tokens({"country_reward": {"sample_one": {"value": 42}}}, old_base)

    refreshed = service.load_resource()
    tokens = next(group["tokens"] for group in refreshed["draft"]["groups"] if group["key"] == "country_reward")
    assert tokens[1]["value"] == 777
    new_base = {item["path"]: item["sha256"] for item in refreshed["change_set"]["base"]}
    # Another client reloaded the cache; a tab still holding the old base must not get a fresh one from preview.
    with pytest.raises(ConflictError):
        service.preview_edits({"country_reward": {"sample_one": {"value": 42}}}, old_base)
    with pytest.raises(ConflictError):
        service.save_tokens({"country_reward": {"sample_one": {"value": 42}}}, old_base)
    preview = service.preview_edits({"country_reward": {"sample_one": {"value": 42}}}, new_base)
    assert preview["change_set"]["base"] == refreshed["change_set"]["base"]
    service.save_tokens({"country_reward": {"sample_one": {"value": 42}}}, new_base)
    assert load_yaml(cost_reward.DATA_FILE)["country_reward"][1]["value"] == 777


def test_commit_preserves_existing_bom(service):
    data_file = cost_reward.DATA_FILE
    data_file.write_bytes(b"\xef\xbb\xbf" + data_file.read_bytes())
    loaded = service.load_resource()
    base = {item["path"]: item["sha256"] for item in loaded["change_set"]["base"]}
    service.save_tokens({"country_reward": {"sample_one": {"value": 42}}}, base)
    assert data_file.read_bytes().startswith(b"\xef\xbb\xbf")


def test_cost_change_rewrites_derived_unique_ceremony_values(service, monkeypatch):
    cost_reward.UNIQUE_WONDERS_FILE.write_text(UNIQUE_SAMPLE, encoding="utf-8")
    service.reload_from_disk()
    from towards_victory_editor_web.services.generation import GenerationPlan

    captured = {}
    refreshed = []
    monkeypatch.setattr(cost_reward, "wonder_generation_plan", lambda changed, **kwargs: (
        captured.setdefault("changed", changed), GenerationPlan(kwargs["repo_root"], ())
    )[1])
    service.set_reload_callback(lambda: refreshed.append(load_yaml(cost_reward.UNIQUE_WONDERS_FILE)))
    initial = service.load_resource()
    base = {item["path"]: item["sha256"] for item in initial["change_set"]["base"]}
    service.save_tokens({"country_reward": {"sample_one": {"value": 0.3}}}, base)
    assert captured["changed"] == {"unique": True, "cost_reward": True}
    assert refreshed and refreshed[0]["unique_wonders"][0]["ceremony"]["stages"][0]["cost"][0]["value"] == -0.3
    updated_unique = cost_reward.UNIQUE_WONDERS_FILE.read_text(encoding="utf-8")
    assert "value: -0.3 # authored" in updated_unique
    assert "value: -0.2" not in updated_unique


def test_derived_unique_change_blocks_only_cost_saves(service):
    initial = service.load_resource()
    base = {item["path"]: item["sha256"] for item in initial["change_set"]["base"]}
    unique_before = "unique_wonders: []\n# edited by the Wonder editor\n"
    cost_reward.UNIQUE_WONDERS_FILE.write_text(unique_before, encoding="utf-8")
    cost_before = cost_reward.DATA_FILE.read_bytes()
    with pytest.raises(ConflictError, match="data/unique_wonders.yaml"):
        service.save_tokens({"country_reward": {"sample_one": {"value": 0.3}}}, base)
    assert cost_reward.DATA_FILE.read_bytes() == cost_before
    service.save_tokens({"on_action_task": {"sample_action": {"wired": True}}}, base)
    assert load_yaml(cost_reward.TASK_POOL_FILE)["on_action_task"][0]["wired"] is True
    assert cost_reward.UNIQUE_WONDERS_FILE.read_text(encoding="utf-8") == unique_before


def test_unrecognized_unique_layout_fails_before_writing(service):
    # The stage title is not the first key, so the line rewrite cannot count stages.
    cost_reward.UNIQUE_WONDERS_FILE.write_text(
        UNIQUE_SAMPLE.replace("    - title_en: stage_2\n", "    - desc_en: moved\n      title_en: stage_2\n"),
        encoding="utf-8",
    )
    service.reload_from_disk()
    initial = service.load_resource()
    base = {item["path"]: item["sha256"] for item in initial["change_set"]["base"]}
    before = {path: path.read_bytes() for path in (cost_reward.DATA_FILE, cost_reward.UNIQUE_WONDERS_FILE)}
    with pytest.raises(ValueError, match="check the file layout"):
        service.preview_edits({"country_reward": {"sample_one": {"value": 0.3}}}, base)
    with pytest.raises(ValueError, match="check the file layout"):
        service.save_tokens({"country_reward": {"sample_one": {"value": 0.3}}}, base)
    assert {path: path.read_bytes() for path in before} == before
    assert "[error] Ceremony cost rewrite left" in service.log_text


def test_commit_conflicts_while_cost_reward_resource_is_busy(service):
    loaded = service.load_resource()
    base = {item["path"]: item["sha256"] for item in loaded["change_set"]["base"]}
    before = cost_reward.DATA_FILE.read_bytes()
    with resource_operation(("editor.cost_reward",)):
        with pytest.raises(ConflictError, match="Resource busy: editor.cost_reward"):
            service.save_tokens({}, base)
    assert cost_reward.DATA_FILE.read_bytes() == before
    assert "[error] Resource busy: editor.cost_reward" in service.log_text


def test_http_bad_id_missing_base_and_conflict(service, monkeypatch):
    from towards_victory_editor_web import server

    monkeypatch.setattr(server, "CostRewardEditorService", lambda: service)
    with TestClient(server.create_app()) as client:
        loaded = client.get("/api/resources/editor.cost_reward").json()
        base = {item["path"]: item["sha256"] for item in loaded["change_set"]["base"]}
        endpoint = "/api/resources/editor.cost_reward/commit"
        assert client.post(endpoint, json={"edits": {}, "base": {}}).status_code == 400
        bad = client.post(endpoint, json={"edits": {"country_reward": {"nope": {"value": 1}}}, "base": base})
        assert bad.status_code == 400
        assert bad.json()["detail"] == "Unknown unit id in country_reward: nope"
        preview = "/api/resources/editor.cost_reward/preview"
        assert client.post(preview, json={"edits": {}}).status_code == 400
        cost_reward.DATA_FILE.write_bytes(cost_reward.DATA_FILE.read_bytes() + b"\n# external\n")
        assert client.post(endpoint, json={"edits": {}, "base": base}).status_code == 409
        assert client.post(preview, json={"edits": {}, "base": base}).status_code == 409
