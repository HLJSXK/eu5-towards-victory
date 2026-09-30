"""Resolve media invocations into explicit files and a fixed execution closure."""

from argparse import Namespace
from typing import Any, Callable

from .cropper import WONDER_TASK_INPUTS
from .tooling import ToolContext, ToolPlan, ToolResult, capture_script_output, read_plan_inputs


def _runner(callback: Callable[[], int], message: str) -> Callable[[ToolContext], ToolResult]:
    def run(context: ToolContext) -> ToolResult:
        context.check_cancelled()
        with capture_script_output(context):
            code = callback()
        if code != 0:
            raise RuntimeError(f"{message}: exited with code {code}")
        return ToolResult(message=message)
    return run


def dds_icon_plan(module: Any, options: dict[str, Any]) -> ToolPlan:
    args = Namespace(**options)
    if args.list_targets:
        return ToolPlan((), (), _runner(lambda: module.run(args), "Targets listed"))
    config, snapshots = read_plan_inputs(
        (module.CONFIG_PATH, module.LOCAL_CONFIG_PATH), module.load_config,
        repo_root=module.REPO_ROOT, optional=(module.LOCAL_CONFIG_PATH,),
    )
    output = module.require_object(config, "output")
    selected = module.select_target_name(config, output, args.target)
    task_sources = ()
    if selected == module.WONDER_BUILDING_BATCH:
        task_sources = (*WONDER_TASK_INPUTS, module.WONDER_LOCALIZATION_PATH)
    tasks, task_snapshots = read_plan_inputs(
        task_sources, lambda: module.build_generation_tasks(config, args),
        repo_root=module.REPO_ROOT, optional=(module.WONDER_LOCALIZATION_PATH,),
    )
    style = module.require_object(config, "style_reference")
    inputs, optional_inputs, outputs, optional_outputs = set(), set(), set(), set()
    for task in tasks:
        target, output = task.target, task.output_config
        previous_outputs = outputs | optional_outputs
        local = target.local_template.get("enabled", False) and not args.force_api
        if module.should_skip_existing(output, target):
            outputs.add(target.path)
            continue
        if args.dry_run:
            if not args.convert_existing_png and not local:
                for value in target.style_reference_paths:
                    path = module.resolve_repo_path(value)
                    inputs.add(path)
                    if task.allow_missing_style_reference_dry_run:
                        optional_inputs.add(path)
            continue
        outputs.add(target.path)
        metadata = module.resolve_repo_path(output.get("metadata_dir"), module.DEFAULT_METADATA_DIR) / f"{module.output_artifact_stem(output, target)}.json"
        if args.convert_existing_png:
            inputs.add(module.resolve_repo_path(args.convert_existing_png))
            if output.get("write_metadata", True) and metadata.exists():
                inputs.add(metadata)
                outputs.add(metadata)
            continue
        png = module.output_stem_path(output, target, "png")
        (outputs if local or output.get("keep_png", True) else optional_outputs).add(png)
        if output.get("write_metadata", True):
            outputs.add(metadata)
        if local:
            path = module.resolve_repo_path(
                target.local_template.get("source_path") or
                (target.style_reference_paths[0] if target.style_reference_paths else None)
            )
            if path not in previous_outputs:
                inputs.add(path)
        else:
            for index, value in enumerate(target.style_reference_paths, start=1):
                path = module.resolve_repo_path(value)
                if path not in previous_outputs:
                    inputs.add(path)
                if style.get("write_converted_pngs", True):
                    ref_dir = module.resolve_repo_path(style.get("temporary_png_dir"), module.DEFAULT_REF_DIR)
                    outputs.add(ref_dir / f"{index:02d}_{target.name}_{module.safe_slug(path.stem)}.png")
    # Only references produced by an earlier batch task can omit a source file.
    _, image_snapshots = read_plan_inputs(
        sorted(inputs), lambda: None, repo_root=module.REPO_ROOT, optional=optional_inputs,
    )
    return ToolPlan(
        snapshots + task_snapshots + image_snapshots,
        () if args.dry_run else tuple(sorted(outputs)),
        _runner(lambda: module.run_generation_tasks(config, args, tasks), "DDS icon generation completed"),
        tuple(sorted(optional_outputs)),
    )


def wonder_image_plan(module: Any, options: dict[str, Any]) -> ToolPlan:
    from .cropper import cropper

    def load():
        config = module.load_config()
        return config, module.load_task_config(config), module.load_crop_data(cropper.data_path)

    (config, tasks, crops), snapshots = read_plan_inputs(
        (module.CONFIG_PATH, module.LOCAL_CONFIG_PATH, *WONDER_TASK_INPUTS, cropper.data_path),
        load, repo_root=module.REPO_ROOT, optional=(module.LOCAL_CONFIG_PATH, cropper.data_path),
    )
    inputs, outputs, optional_outputs = set(), set(), set()
    for task in tasks:
        if not task.get("enabled", True):
            continue
        stem = module.wonder_file_stem(task)
        png = module.resolve_repo_path(task.get("png_dir"), module.DEFAULT_PNG_DIR) / f"{stem}.png"
        dds = module.resolve_repo_path(task.get("dds_dir"), module.DEFAULT_WONDERS_DIR) / f"{stem}.dds"
        cropped = module.cropped_wonder_dds_path(dds)
        pair = (dds, cropped)
        if not task.get("overwrite", False) and any(path.exists() for path in pair):
            # Mirrors run_generation: a partial pair is repaired from the PNG
            # when one exists; otherwise the generator skips the task.
            if png.exists():
                inputs.add(png)
                outputs.update(pair)
            else:
                outputs.update(path for path in pair if path.exists())
            continue
        outputs.update(pair)
        (outputs if task.get("keep_png", True) else optional_outputs).add(png)
        if task.get("write_metadata", True):
            metadata_dir = module.resolve_repo_path(task.get("metadata_dir"), module.DEFAULT_METADATA_DIR)
            outputs.add(metadata_dir / f"{stem}.json")
    _, image_snapshots = read_plan_inputs(sorted(inputs), lambda: None, repo_root=module.REPO_ROOT)
    return ToolPlan(
        snapshots + image_snapshots, tuple(sorted(outputs)),
        _runner(lambda: module.run_generation(config, tasks, crops), "Wonder image generation completed"),
        tuple(sorted(optional_outputs)),
    )


def historical_api_plan(module: Any, options: dict[str, Any]) -> ToolPlan:
    (config, tasks), snapshots = read_plan_inputs(
        (module.CONFIG_PATH,), module.load_tasks, repo_root=module.REPO_ROOT,
    )
    _, sources = read_plan_inputs(tuple(source for source, _ in tasks), lambda: None, repo_root=module.REPO_ROOT)
    outputs = () if options["dry_run"] else tuple(output for _, output in tasks)
    return ToolPlan(
        snapshots + sources, outputs,
        _runner(lambda: module.run_tasks(config, tasks, dry_run=options["dry_run"]), "Historical image batch completed"),
    )
