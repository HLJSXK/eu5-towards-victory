"""Resolve media invocations into explicit files and a fixed execution closure."""

from argparse import Namespace
import copy
from dataclasses import replace
from typing import Any, Callable

from .cropper import WONDER_TASK_INPUTS
from .tooling import ToolContext, ToolPlan, ToolResult, capture_script_output, read_plan_inputs


def _runner(callback: Callable[[ToolContext], int], message: str) -> Callable[[ToolContext], ToolResult]:
    def run(context: ToolContext) -> ToolResult:
        context.check_cancelled()
        with capture_script_output(context):
            code = callback(context)
        if code != 0:
            raise RuntimeError(f"{message}: exited with code {code}")
        return ToolResult(message=message)
    return run


def dds_icon_plan(module: Any, options: dict[str, Any]) -> ToolPlan:
    args = Namespace(**options)
    if args.list_targets:
        return ToolPlan((), (), _runner(lambda _context: module.run(args), "Targets listed"))
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
    preceding_outputs = []
    for task in tasks:
        target, output = task.target, task.output_config
        previous_outputs = outputs | optional_outputs
        preceding_outputs.append(previous_outputs)
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
    def run(context: ToolContext) -> int:
        if args.dry_run:
            return module.run_generation_tasks(config, args, tasks)
        staged_config = copy.deepcopy(config)
        staged_tasks = []
        for task, previous_outputs in zip(tasks, preceding_outputs):
            staged_target = replace(task.target, path=context.stage_path(task.target.path))
            staged_references = tuple(
                str(context.stage_path(module.resolve_repo_path(value)))
                if module.resolve_repo_path(value) in previous_outputs else value
                for value in task.target.style_reference_paths
            )
            local_template = copy.deepcopy(task.target.local_template)
            local_source = local_template.get("source_path")
            if local_source:
                source_path = module.resolve_repo_path(local_source)
                if source_path in previous_outputs:
                    local_template["source_path"] = str(context.stage_path(source_path))
            staged_target = replace(
                staged_target,
                style_reference_paths=staged_references,
                local_template=local_template,
            )
            output_config = copy.deepcopy(task.output_config)
            for key, default in (("png_dir", module.DEFAULT_PNG_DIR), ("metadata_dir", module.DEFAULT_METADATA_DIR)):
                directory = module.resolve_repo_path(output_config.get(key), default)
                suffix = 'png' if key == 'png_dir' else 'json'
                output_path = directory / f"{module.output_artifact_stem(output_config, task.target)}.{suffix}"
                if output_path in outputs | optional_outputs:
                    output_config[key] = str(context.stage_path(output_path).parent)
            staged_tasks.append(replace(task, target=staged_target, output_config=output_config))
        style_config = staged_config.get("style_reference")
        if isinstance(style_config, dict) and style_config.get("write_converted_pngs", True):
            directory = module.resolve_repo_path(style_config.get("temporary_png_dir"), module.DEFAULT_REF_DIR)
            references = [path for path in outputs if path.parent == directory]
            if references:
                style_config["temporary_png_dir"] = str(context.stage_path(references[0]).parent)
        code = module.run_generation_tasks(staged_config, args, staged_tasks)
        if code == 0:
            context.formalize_json_paths(outputs)
        return code

    return ToolPlan(
        snapshots + task_snapshots + image_snapshots,
        () if args.dry_run else tuple(sorted(outputs)),
        _runner(run, "DDS icon generation completed"),
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
    def run(context: ToolContext) -> int:
        staged_tasks = []
        for task in tasks:
            staged = dict(task)
            stem = module.wonder_file_stem(task)
            for key, default in (("png_dir", module.DEFAULT_PNG_DIR), ("dds_dir", module.DEFAULT_WONDERS_DIR), ("metadata_dir", module.DEFAULT_METADATA_DIR)):
                directory = module.resolve_repo_path(staged.get(key), default)
                suffix = {"png_dir": "png", "dds_dir": "dds", "metadata_dir": "json"}[key]
                output_path = directory / f"{stem}.{suffix}"
                candidates = (output_path, module.cropped_wonder_dds_path(output_path)) if key == "dds_dir" else (output_path,)
                destination = next((path for path in candidates if path in outputs | optional_outputs), None)
                if destination is not None:
                    staged[key] = str(context.stage_path(destination).parent)
            staged_tasks.append(staged)
        return module.run_generation(config, staged_tasks, crops)

    return ToolPlan(
        snapshots + image_snapshots, tuple(sorted(outputs)),
        _runner(run, "Wonder image generation completed"),
        tuple(sorted(optional_outputs)),
    )


def historical_api_plan(module: Any, options: dict[str, Any]) -> ToolPlan:
    (config, tasks), snapshots = read_plan_inputs(
        (module.CONFIG_PATH,), module.load_tasks, repo_root=module.REPO_ROOT,
    )
    _, sources = read_plan_inputs(tuple(source for source, _ in tasks), lambda: None, repo_root=module.REPO_ROOT)
    outputs = () if options["dry_run"] else tuple(output for _, output in tasks)
    def run(context: ToolContext) -> int:
        if options["dry_run"]:
            return module.run_tasks(config, tasks, dry_run=True)
        staged_tasks = [(source, context.stage_path(output)) for source, output in tasks]
        return module.run_tasks(config, staged_tasks, dry_run=options["dry_run"])

    return ToolPlan(
        snapshots + sources, outputs,
        _runner(run, "Historical image batch completed"),
    )
