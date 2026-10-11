from __future__ import annotations

import json
from argparse import Namespace
from contextlib import contextmanager
from pathlib import Path

import pytest

from towards_victory_editor_web.services import cropper as cropper_module
from towards_victory_editor_web.services.cropper import CropperService, WonderCropTool
from towards_victory_editor_web.services import media_plans
from towards_victory_editor_web.services.media_plans import dds_icon_plan, historical_api_plan, wonder_image_plan
from towards_victory_editor_web.services.media_tools import HistoricalStyleTool, build_registry
from towards_victory_editor_web.services.platform import OperationLog
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
        manager._futures[job.id].result(timeout=30)
    finally:
        manager.shutdown()
    return manager.get(job.id)


def run_tool_options(root, tool, options):
    registry = ToolRegistry()
    registry.register(tool)
    manager = JobManager(registry, root)
    try:
        job = manager.submit(tool.spec.id, options)
        manager._futures[job.id].result(timeout=30)
    finally:
        manager.shutdown()
    return manager.get(job.id)


def baseline_bytes(outputs, run):
    before = {path: path.read_bytes() if path.exists() else None for path in outputs}
    run()
    expected = {path: path.read_bytes() if path.exists() else None for path in outputs}
    for path, data in before.items():
        if data is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(data)
    return expected


def assert_output_bytes(expected):
    assert {path: path.read_bytes() if path.exists() else None for path in expected} == expected


def staged_context(root, outputs):
    context = ToolContext("fixed-plan", root, lambda line: None, OperationLog("media_job"))
    context.set_staging(root / ".editor_state" / "test-staging", outputs)
    return context


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
    monkeypatch.setattr(wonder, "run_parallel_existing_dds_jobs", lambda jobs, **_: [wonder.convert_existing_dds_worker(job) for job in jobs])
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
        config_data = wonder.load_config()
        expected_bytes = baseline_bytes(plan.outputs, lambda: wonder.run_existing_assets(
            wonder.plan_existing_assets(wonder.load_task_config(config_data)),
            (0, 0, 0), wonder.load_crop_data(service.data_path),
        ))
    job = run_tool(service.repo_root, tool)
    assert job["status"] == "succeeded", job["error"]
    assert {item["path"] for item in job["artifacts"]} == expected
    assert all(item["valid"] for item in job["metadata"]["output_validation"])
    assert not (service.repo_root / "dds/tv_wonder_disabled.dds").exists()
    assert_output_bytes(expected_bytes)


def test_wonder_crop_failure_restores_formal_outputs(wonder_env, monkeypatch):
    service, tool, _, _ = wonder_env
    target = service.repo_root / "dds/tv_wonder_dds_only.dds"
    before = target.read_bytes()

    def fail(jobs, *_args, **_controls):
        jobs[0][1].write_bytes(b"partial")
        raise RuntimeError("crop failed")

    monkeypatch.setattr(cropper_module, "run_existing_assets", fail)
    job = run_tool(service.repo_root, tool)
    assert job["status"] == "failed"
    assert target.read_bytes() == before


def test_wonder_image_failure_restores_formal_outputs(wonder_env, monkeypatch):
    service, _, config, tasks = wonder_env
    monkeypatch.setattr(media_plans, "WONDER_TASK_INPUTS", (tasks,))
    monkeypatch.setattr(cropper_module.cropper, "data_path", service.data_path)
    plan = wonder_image_plan(wonder, {})

    def fail(_config, planned, _crops):
        path = Path(planned[0]["dds_dir"]) / "tv_wonder_selected.dds"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"partial")
        raise RuntimeError("image failed")

    monkeypatch.setattr(wonder, "run_generation", fail)
    target = service.repo_root / "dds/tv_wonder_selected.dds"
    target.write_bytes(b"original")
    before = target.read_bytes()
    job = run_tool(service.repo_root, PlannedTool(lambda: plan))
    assert job["status"] == "failed"
    assert target.read_bytes() == before


def test_dds_icon_failure_restores_formal_outputs(icon_env, monkeypatch):
    root, _, options = icon_env
    plan = dds_icon_plan(icons, options)
    target = root / "icons/sample.dds"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"original")

    def fail(_config, _args, tasks):
        tasks[0].target.path.write_bytes(b"partial")
        raise RuntimeError("icon failed")

    monkeypatch.setattr(icons, "run_generation_tasks", fail)
    before = target.read_bytes()
    job = run_tool(root, PlannedTool(lambda: plan))
    assert job["status"] == "failed"
    assert target.read_bytes() == before


def test_historical_api_failure_restores_formal_outputs(tmp_path, monkeypatch):
    config = tmp_path / "historical.json"
    write_png(tmp_path / "source.png")
    config.write_text(json.dumps({"historical_images": {
        "endpoint": "https://example.invalid/images/edits", "model": "fixture", "overwrite": True,
        "api_key": "fixture", "images": [{"source": "source.png", "output": "out.png"}],
    }}))
    monkeypatch.setattr(historical, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(historical, "CONFIG_PATH", config)
    monkeypatch.setattr(historical, "OUTPUT_DIR", tmp_path / "processed")
    plan = historical_api_plan(historical, {"dry_run": False})
    target = tmp_path / "processed/out.png"
    target.parent.mkdir()
    target.write_bytes(b"original")

    def fail(_config, planned, **_kwargs):
        planned[0][1].write_bytes(b"partial")
        raise RuntimeError("historical failed")

    monkeypatch.setattr(historical, "run_tasks", fail)
    before = target.read_bytes()
    job = run_tool(tmp_path, PlannedTool(lambda: plan))
    assert job["status"] == "failed"
    assert target.read_bytes() == before


def test_historical_style_failure_restores_formal_outputs(tmp_path, monkeypatch):
    source = tmp_path / "source.png"
    write_png(source)
    output_dir = tmp_path / "processed"
    target = output_dir / "source_cartoon.png"
    target.parent.mkdir()
    target.write_bytes(b"original")

    class FailingStyle:
        @staticmethod
        def run(_input, output, *_args):
            (Path(output) / "source_cartoon.png").write_bytes(b"partial")
            raise RuntimeError("style failed")

    monkeypatch.setattr("towards_victory_editor_web.services.media_tools._load", lambda *_args: FailingStyle)
    monkeypatch.setattr("towards_victory_editor_web.services.media_tools.REPO_ROOT", tmp_path)
    tool = HistoricalStyleTool()
    before = target.read_bytes()
    job = run_tool_options(tmp_path, tool, {"inputs": ["source.png"], "output_dir": "processed"})
    assert job["status"] == "failed"
    assert target.read_bytes() == before


def test_prepared_wonder_rebuild_executes_resolved_tasks_without_reloading(wonder_env, monkeypatch):
    service, tool, config, tasks = wonder_env
    with tool.prepare({}) as plan:
        config.write_text('{}')
        tasks.write_text('[]')
        monkeypatch.setattr(cropper_module, "load_task_config", lambda _: pytest.fail("execution reloaded tasks"))
        context = staged_context(service.repo_root, plan.outputs)
        plan.run(context)
        assert all(context.stage_path(path).is_file() for path in plan.outputs)


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


@pytest.mark.parametrize("keep_png", [True, False])
def test_wonder_repair_and_generation_match_direct_outputs(wonder_env, monkeypatch, keep_png):
    service, _, config, tasks = wonder_env
    root = service.repo_root
    monkeypatch.setattr(media_plans, "WONDER_TASK_INPUTS", (tasks,))
    monkeypatch.setattr(cropper_module.cropper, "data_path", service.data_path)
    monkeypatch.setattr(wonder, "resolve_api_key", lambda _: "fixture")
    write_png(root / "png/tv_wonder_dds_only.png")
    config.write_text(json.dumps({
        "defaults": {"png_dir": "png", "dds_dir": "dds", "metadata_dir": "metadata",
                     "size": "1024x640", "keep_png": keep_png},
    }))
    (root / "metadata").mkdir()
    tasks.write_text(json.dumps([
        {"name": name, "key": name, "is_unique": False, "prompt": name}
        for name in ("dds_only", "new")
    ]))
    image = encode_png_rgba(RgbaImage(1024, 640, bytes([120, 80, 40, 255]) * (1024 * 640)))
    monkeypatch.setattr(wonder, "api_post_json", lambda *_, **__: {"created": 42})
    monkeypatch.setattr(wonder, "extract_png_bytes", lambda *_, **__: (image, "fixture"))
    plan = wonder_image_plan(wonder, {})
    png = root / "png/tv_wonder_dds_only.png"
    png_before = png.read_bytes()
    assert png not in plan.outputs
    loaded_config = wonder.load_config()
    expected = baseline_bytes((*plan.outputs, *plan.optional_outputs), lambda: wonder.run_generation(
        loaded_config, wonder.load_task_config(loaded_config), wonder.load_crop_data(service.data_path),
    ))
    job = run_tool(root, PlannedTool(lambda: plan))
    assert job["status"] == "succeeded", job["error"]
    assert_output_bytes(expected)
    assert png.read_bytes() == png_before
    assert job["missing_outputs"] == []


@pytest.mark.parametrize("keep_intermediates", [True, False])
def test_historical_style_matches_direct_output_bytes(tmp_path, monkeypatch, keep_intermediates):
    pytest.importorskip("skimage.color")
    from scripts import style_historical_image as style
    from towards_victory_editor_web.services import media_tools

    source = tmp_path / "source.png"
    # Nonuniform input exercises image statistics, palette and deterministic noise.
    pixels = bytes(channel for y in range(32) for x in range(32)
                   for channel in (x * 8, y * 8, (x + y) * 4, 255))
    source.write_bytes(encode_png_rgba(RgbaImage(32, 32, pixels)))
    monkeypatch.setattr(media_tools, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(media_tools, "_load", lambda *_: style)
    tool = HistoricalStyleTool()
    options = {"inputs": ["source.png"], "output_dir": "processed", "max_size": 32,
               "seed": 17, "keep_intermediates": keep_intermediates}
    normalized = tool.validate(options)
    outputs = tool.outputs(normalized)
    expected = baseline_bytes(outputs, lambda: style.run(source, tmp_path / "processed", 32, keep_intermediates, 17))
    job = run_tool_options(tmp_path, tool, options)
    assert job["status"] == "succeeded", job["error"]
    assert_output_bytes(expected)
    report = json.loads((tmp_path / "processed/source_cartoon_evaluation.json").read_bytes())
    assert report["output"] == str(tmp_path / "processed/source_cartoon.png")
    assert Path(report["output"]).is_file()


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
    expected_bytes = baseline_bytes(plan.outputs, lambda: icons.run(Namespace(**options)))
    job = run_tool(root, PlannedTool(lambda: dds_icon_plan(icons, options)))
    assert job["status"] == "succeeded", job["error"]
    assert {item["path"] for item in job["metadata"]["output_validation"]} == {"icons/sample.dds", "data/generated_icons/sample.json"}
    metadata_payload = json.loads(metadata.read_text())
    assert metadata_payload["targets"][0]["name"] == "building_icon"
    assert metadata_payload["targets"][0]["path"] == "icons/sample.dds"
    assert_output_bytes(expected_bytes)


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
    monkeypatch.setattr(historical, "edit_image", lambda cfg, src, key, **_: src.read_bytes())
    plan = historical_api_plan(historical, {"dry_run": False})
    assert {item.path for item in plan.inputs} == {"historical.json", "source.png"}
    loaded_config, tasks = historical.load_tasks()
    expected_bytes = baseline_bytes(plan.outputs, lambda: historical.run_tasks(loaded_config, tasks, dry_run=False))
    job = run_tool(tmp_path, PlannedTool(lambda: plan))
    assert job["status"] == "succeeded", job["error"]
    assert_output_bytes(expected_bytes)
    config.write_text('{}')
    context = staged_context(tmp_path, plan.outputs)
    plan.run(context)
    assert context.stage_path(tmp_path / "processed/out.png").read_bytes() == (tmp_path / "source.png").read_bytes()


def test_web_catalog_has_one_wonder_rebuild_entry():
    registry = build_registry()
    generator = registry.get("media.wonder_image")
    assert generator.spec.options == ()
    expected_resources = ("editor.wonder", "editor.wonder_crop", "editor.cost_reward")
    assert generator.spec.resource_ids == expected_resources
    with pytest.raises(ValueError, match="Unknown option"):
        generator.validate({"convert_existing_assets": True})
    assert registry.get("media.wonder_crop").spec.resource_ids == expected_resources


def test_wonder_batch_icon_job_locks_every_editor_resource_it_reads():
    from towards_victory_editor_web.services import cost_reward
    from towards_victory_editor_web.services.cropper import WONDER_TASK_INPUTS
    from towards_victory_editor_web.services.wonder_localization import _wonder_source_rels

    owners = {"editor.wonder": set(_wonder_source_rels()),
              "editor.cost_reward": {cost_reward.DATA_REL, cost_reward.TASK_POOL_REL, cost_reward.UNIQUE_WONDERS_REL}}
    read = {f"data/{path.name}" for path in WONDER_TASK_INPUTS} | {"data/wonder_localization.yaml"}
    required = {resource for resource, paths in owners.items() if paths & read}
    assert required <= set(build_registry().get("media.dds_icon").spec.resource_ids)
