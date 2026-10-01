from __future__ import annotations

import json
from contextlib import contextmanager

import pytest

from towards_victory_editor_web.services import cropper as cropper_module
from towards_victory_editor_web.services.cropper import CropperService, WonderCropTool
from towards_victory_editor_web.services import media_plans
from towards_victory_editor_web.services.media_plans import dds_icon_plan, historical_api_plan, wonder_image_plan
from towards_victory_editor_web.services.media_tools import build_registry
from towards_victory_editor_web.services.tooling import JobManager, ToolContext, ToolRegistry, ToolSpec

from dds_image_lib import RgbaImage, encode_png_rgba, write_dds
import generate_wonder_image as wonder
from scripts import generate_dds_icon as icons
from scripts import generate_historical_images as historical


def write_png(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_png_rgba(RgbaImage(16, 16, bytes([120, 80, 40, 255]) * 256)))


def run_tool(root, tool):
    registry = ToolRegistry()
    registry.register(tool)
    manager = JobManager(registry, root)
    try:
        job = manager.submit(tool.spec.id, {})
    finally:
        manager.shutdown()
    return manager.get(job.id).payload()


class PlannedTool:
    spec = ToolSpec("test.plan", "Plan", "test", "test", artifact_formats=("dds", "png", "json"))

    def __init__(self, builder):
        self.builder = builder

    def validate(self, options):
        return options

    @contextmanager
    def prepare(self, options):
        yield self.builder()


@pytest.fixture
def wonder_env(tmp_path, monkeypatch):
    config = tmp_path / "generate_wonder_image_config.json"
    local = tmp_path / "generate_wonder_image.local.json"
    tasks = tmp_path / "wonder_image_prompts.json"
    crops = tmp_path / "crops.json"
    config.write_text(json.dumps({
        "dds": {"opaque_background": [0, 0, 0]},
        "defaults": {"png_dir": "png", "dds_dir": "dds"},
        "task_overrides": {"disabled": {"enabled": False}},
    }))
    tasks.write_text(json.dumps([
        {"name": name, "key": name, "is_unique": False, "prompt": name}
        for name in ("selected", "dds_only", "disabled", "missing")
    ]))
    crops.write_text(json.dumps({"output_size": {"width": 54, "height": 22}, "crops": {}}))
    for module in (wonder, cropper_module):
        monkeypatch.setattr(module, "CONFIG_PATH", config)
        monkeypatch.setattr(module, "LOCAL_CONFIG_PATH", local)
    monkeypatch.setattr(wonder, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(wonder, "load_wonder_image_tasks", lambda **kwargs: json.loads(tasks.read_text()))
    monkeypatch.setattr(cropper_module, "WONDER_TASK_INPUTS", (tasks,))
    # Exercise the real converter without process creation in a unit test.
    monkeypatch.setattr(wonder, "run_parallel_existing_dds_jobs", lambda jobs: [wonder.convert_existing_dds_worker(job) for job in jobs])
    for name in ("selected", "extra", "disabled"):
        write_png(tmp_path / "png" / f"tv_wonder_{name}.png")
    for name in ("dds_only", "orphan", "ignored_cropped"):
        write_dds(RgbaImage(16, 16, bytes([80, 30, 10, 255]) * 256), tmp_path / "dds" / f"tv_wonder_{name}.dds", dds_format="DXT1")
    # A stale UI task cache must not determine the generator's file declarations.
    service = CropperService(tasks=[], data_path=crops, repo_root=tmp_path)
    return service, WonderCropTool(service), config, tasks


def test_wonder_rebuild_declares_and_writes_full_and_cropped_dds(wonder_env):
    service, tool, config, tasks = wonder_env
    with tool.prepare({}) as plan:
        inputs = {item.path for item in plan.inputs}
        assert inputs == {
            config.name, tasks.name, "generate_wonder_image.local.json", "crops.json",
            "png/tv_wonder_selected.png", "png/tv_wonder_extra.png", "dds/tv_wonder_dds_only.dds", "dds/tv_wonder_orphan.dds",
        }
        expected = {f"dds/tv_wonder_{name}.dds" for name in (
            "selected", "selected_cropped", "extra", "extra_cropped", "dds_only", "orphan",
        )}
        assert {path.relative_to(service.repo_root).as_posix() for path in plan.outputs} == expected
    job = run_tool(service.repo_root, tool)
    assert job["status"] == "succeeded", job["error"]
    assert {item["path"] for item in job["artifacts"]} == expected
    assert all(item["valid"] for item in job["metadata"]["output_validation"])
    assert not (service.repo_root / "dds/tv_wonder_disabled.dds").exists()


def test_prepared_wonder_rebuild_executes_resolved_tasks_without_reloading(wonder_env, monkeypatch):
    service, tool, config, tasks = wonder_env
    with tool.prepare({}) as plan:
        config.write_text('{}')
        tasks.write_text('[]')
        monkeypatch.setattr(cropper_module, "load_task_config", lambda _: pytest.fail("execution reloaded tasks"))
        plan.run(ToolContext("fixed-plan", service.repo_root, lambda line: None))
        assert all(path.is_file() for path in plan.outputs)


def test_live_wonder_crop_plan_tracks_repository_task_sources():
    # Read-only check against the real repository loader and current image directories.
    tool = WonderCropTool(cropper_module.cropper)
    with tool.prepare({}) as plan:
        inputs = {item.path for item in plan.inputs}
        assert cropper_module.CONFIG_PATH.relative_to(tool.workspace.repo_root).as_posix() in inputs
        assert "data/wonder_image_prompts.yaml" in inputs
        assert "data/wonder_image_crops.json" in inputs
        assert set(cropper_module.WONDER_TASK_INPUTS) <= {tool.workspace.repo_root / item.path for item in plan.inputs}
        outputs = set(plan.outputs)
        assert outputs
        for path in outputs:
            if path.stem.endswith("_cropped"):
                assert path.with_name(path.name.replace("_cropped.dds", ".dds")) in outputs


def test_wonder_generation_skips_partial_dds_without_png(wonder_env, monkeypatch):
    service, _, _, tasks = wonder_env
    monkeypatch.setattr(media_plans, "WONDER_TASK_INPUTS", (tasks,))
    monkeypatch.setattr(cropper_module.cropper, "data_path", service.data_path)
    monkeypatch.setattr(wonder, "resolve_api_key", lambda _config: "fixture-key")

    def unexpected_request(*_args):
        raise AssertionError("skipped task reached the API")

    monkeypatch.setattr(wonder, "api_post_json", unexpected_request)
    tasks.write_text(json.dumps([{"name": "dds_only", "key": "dds_only", "is_unique": False, "prompt": "x"}]))
    before = (service.repo_root / "dds/tv_wonder_dds_only.dds").read_bytes()
    # The generator skips a partial pair when no PNG can repair it, so only the existing file is declared.
    plan = wonder_image_plan(wonder, {})
    assert [path.relative_to(service.repo_root).as_posix() for path in plan.outputs] == ["dds/tv_wonder_dds_only.dds"]
    job = run_tool(service.repo_root, PlannedTool(lambda: plan))
    assert job["status"] == "succeeded", job["error"]
    assert job["missing_outputs"] == []
    assert [item["changed"] for item in job["artifacts"]] == [False]
    assert (service.repo_root / "dds/tv_wonder_dds_only.dds").read_bytes() == before


@pytest.fixture
def icon_env(tmp_path, monkeypatch):
    config = tmp_path / "icons.json"
    config.write_text(json.dumps({
        "output": {"name": "sample", "target": "building_icon", "overwrite": True,
                   "png_dir": "png", "metadata_dir": "data/generated_icons", "artifact_stem": "{name}",
                   "targets": {"building_icon": {"path": "icons/{name}.dds"}}},
    }))
    monkeypatch.setattr(icons, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(icons, "CONFIG_PATH", config)
    monkeypatch.setattr(icons, "LOCAL_CONFIG_PATH", tmp_path / "icons.local.json")
    source = tmp_path / "source.png"
    write_png(source)
    metadata = tmp_path / "data/generated_icons/sample.json"
    metadata.parent.mkdir(parents=True)
    metadata.write_text('{}')
    options = {"target": "building_icon", "convert_existing_png": str(source), "dry_run": False, "force_api": False, "list_targets": False}
    return tmp_path, metadata, options


def test_dds_conversion_tracks_json_outside_image_directory(icon_env):
    root, metadata, options = icon_env
    plan = dds_icon_plan(icons, options)
    assert {path.relative_to(root).as_posix() for path in plan.outputs} == {"icons/sample.dds", "data/generated_icons/sample.json"}
    assert metadata.relative_to(root).as_posix() in {item.path for item in plan.inputs}
    job = run_tool(root, PlannedTool(lambda: dds_icon_plan(icons, options)))
    assert job["status"] == "succeeded", job["error"]
    assert {item["path"] for item in job["metadata"]["output_validation"]} == {"icons/sample.dds", "data/generated_icons/sample.json"}
    assert json.loads(metadata.read_text())["targets"][0]["name"] == "building_icon"


def test_dds_dry_run_does_not_write_conversion_or_metadata(icon_env):
    root, metadata, options = icon_env
    options["dry_run"] = True
    job = run_tool(root, PlannedTool(lambda: dds_icon_plan(icons, options)))
    assert job["status"] == "succeeded", job["error"]
    assert job["declared_outputs"] == []
    assert job["artifacts"] == []
    assert metadata.read_text() == '{}'
    assert not (root / "icons/sample.dds").exists()


def test_historical_api_plan_keeps_config_and_outputs(tmp_path, monkeypatch):
    config = tmp_path / "historical.json"
    write_png(tmp_path / "source.png")
    config.write_text(json.dumps({"historical_images": {
        "endpoint": "https://example.invalid/images/edits", "model": "fixture", "overwrite": True,
        "api_key": "fixture", "images": [{"source": "source.png", "output": "out.png"}],
    }}))
    monkeypatch.setattr(historical, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(historical, "CONFIG_PATH", config)
    monkeypatch.setattr(historical, "OUTPUT_DIR", tmp_path / "processed")
    monkeypatch.setattr(historical, "edit_image", lambda cfg, src, key: src.read_bytes())
    plan = historical_api_plan(historical, {"dry_run": False})
    assert {item.path for item in plan.inputs} == {"historical.json", "source.png"}
    config.write_text('{}')
    plan.run(ToolContext("fixed-plan", tmp_path, lambda line: None))
    assert (tmp_path / "processed/out.png").read_bytes() == (tmp_path / "source.png").read_bytes()


def test_web_catalog_has_one_wonder_rebuild_entry():
    registry = build_registry()
    generator = registry.get("media.wonder_image")
    assert generator.spec.options == ()
    expected_resources = ("editor.wonder", "editor.wonder_crop", "editor.cost_reward")
    assert generator.spec.resource_ids == expected_resources
    with pytest.raises(ValueError, match="Unknown option"):
        generator.validate({"convert_existing_assets": True})
    assert registry.get("media.wonder_crop").spec.resource_ids == expected_resources
