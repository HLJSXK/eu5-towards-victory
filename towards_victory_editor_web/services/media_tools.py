from __future__ import annotations

import importlib.util
from contextlib import contextmanager
import sys
from pathlib import Path
from typing import Any, Callable, Iterator

from .tooling import (
    ToolContext,
    ToolOption,
    ToolRegistry,
    ToolResult,
    ToolPlan,
    read_plan_inputs,
    ToolSpec,
    capture_script_output,
    normalize_declared_options,
)
from .cropper import WonderCropTool, cropper
from .media_plans import dds_icon_plan, wonder_image_plan, historical_api_plan

REPO_ROOT = Path(__file__).resolve().parents[2]
_MODULES: dict[str, Any] = {}


def _load(name: str, path: Path, extra_paths: tuple[Path, ...] = ()) -> Any:
    if name in _MODULES:
        return _MODULES[name]
    for extra in extra_paths:
        value = str(extra)
        if value not in sys.path:
            sys.path.insert(0, value)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load tool module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    _MODULES[name] = module
    return module


class ModuleRunTool:
    """Adapter from the shared job contract to a generator's domain API.

    A required plan builder resolves configuration and tasks once. CLI and Web
    then call the same generator functions with those resolved tasks.
    """

    def __init__(
        self, spec: ToolSpec, script: str,
        options_builder: Callable[[dict[str, Any]], dict[str, Any]],
        plan_builder: Callable[[Any, dict[str, Any]], ToolPlan],
        extra_paths: tuple[str, ...] = (),
    ) -> None:
        self.spec = spec
        self.script_path = REPO_ROOT / script
        self.options_builder = options_builder
        self.plan_builder = plan_builder
        self.extra_paths = tuple(REPO_ROOT / path for path in extra_paths)

    def validate(self, options: dict[str, Any]) -> dict[str, Any]:
        normalized = normalize_declared_options(self.spec, options)
        self.options_builder(normalized)
        return normalized

    @contextmanager
    def prepare(self, options: dict[str, Any]) -> Iterator[ToolPlan]:
        module = _load(self.spec.id.replace(".", "_"), self.script_path, self.extra_paths)
        yield self.plan_builder(module, self.options_builder(options))


class HistoricalStyleTool:
    spec = ToolSpec(
        id="media.historical_style",
        label="Historical image styling",
        description="Run the deterministic local historical-image styling pipeline.",
        group="media",
        options=(
            ToolOption("inputs", "Input images", "paths", required=True),
            ToolOption("output_dir", "Output directory", "directory", "assets/historical/processed"),
            ToolOption("max_size", "Maximum edge", "integer", 1920),
            ToolOption("seed", "Seed", "integer", 17),
            ToolOption("keep_intermediates", "Keep intermediate stages", "boolean", False),
        ),
        artifact_formats=("png", "jpg", "json"),
    )

    def validate(self, options: dict[str, Any]) -> dict[str, Any]:
        normalized = normalize_declared_options(self.spec, options)
        inputs = normalized.get("inputs")
        if not isinstance(inputs, list) or not inputs:
            raise ValueError("inputs must contain at least one image")
        input_paths = []
        for value in inputs:
            path = _repo_file(value)
            if not path.is_file():
                raise ValueError(f"Input image does not exist: {value}")
            input_paths.append(path)
        output_dir = _repo_dir(normalized.get("output_dir", "assets/historical/processed"))
        max_size = int(normalized.get("max_size", 1920))
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        return {**normalized, "inputs": [str(path) for path in input_paths], "output_dir": str(output_dir), "max_size": max_size, "seed": int(normalized.get("seed", 17))}

    @contextmanager
    def prepare(self, options: dict[str, Any]) -> Iterator[ToolPlan]:
        _, snapshots = read_plan_inputs(
            tuple(Path(value) for value in options["inputs"]), lambda: None, repo_root=REPO_ROOT,
        )
        outputs = self.outputs(options)
        if len(set(outputs)) != len(outputs):
            raise ValueError("Input images must have distinct filenames without extensions")
        yield ToolPlan(snapshots, outputs, lambda context: self.run(options, context))

    def outputs(self, options: dict[str, Any]) -> tuple[Path, ...]:
        output_dir = Path(options["output_dir"])
        paths: list[Path] = []
        for value in options["inputs"]:
            stem = Path(value).stem
            paths.extend((
                output_dir / f"{stem}_cartoon.png",
                output_dir / f"{stem}_cartoon_comparison.jpg",
                output_dir / f"{stem}_cartoon_evaluation.json",
            ))
            if options.get("keep_intermediates"):
                paths.extend(
                    output_dir / f"{stem}_{name}.jpg"
                    for name in (
                        "01_normalized",
                        "02_smoothed",
                        "03_color_grade",
                        "04_cartoon_palette",
                        "05_cel_shade",
                        "06_ink_edges",
                    )
                )
        return tuple(paths)

    def run(self, options: dict[str, Any], context: ToolContext) -> ToolResult:
        try:
            module = _load("tv_style_historical_image", REPO_ROOT / "scripts/style_historical_image.py")
        except ModuleNotFoundError as exc:
            if exc.name in {"numpy", "PIL", "skimage"}:
                raise RuntimeError(
                    "Historical image styling requires requirements-image.txt "
                    f"(missing {exc.name})"
                ) from exc
            raise
        with capture_script_output(context):
            for value in options["inputs"]:
                context.check_cancelled()
                module.run(Path(value), Path(options["output_dir"]), options["max_size"], bool(options.get("keep_intermediates", False)), options["seed"])
        return ToolResult(message="Historical image styling completed")


def _repo_file(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A repository-relative file path is required")
    path = (REPO_ROOT / value).resolve()
    _inside(path)
    return path


def _repo_dir(value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("A repository-relative directory is required")
    path = (REPO_ROOT / value).resolve()
    _inside(path)
    return path


def _inside(path: Path) -> None:
    try:
        path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError("Paths must stay inside the repository") from exc


def _dds_options(options: dict[str, Any]) -> dict[str, Any]:
    args: dict[str, Any] = {
        "target": None,
        "convert_existing_png": None,
        "dry_run": False,
        "force_api": False,
        "list_targets": False,
    }
    if options.get("target"):
        args["target"] = str(options["target"])
    if options.get("dry_run"):
        args["dry_run"] = True
    if options.get("convert_existing_png"):
        path = _repo_file(options["convert_existing_png"])
        args["convert_existing_png"] = str(path)
    if options.get("force_api"):
        args["force_api"] = True
    if options.get("list_targets"):
        args["list_targets"] = True
    return args


def _wonder_options(options: dict[str, Any]) -> dict[str, Any]:
    return {}


def _historical_api_options(options: dict[str, Any]) -> dict[str, Any]:
    return {"dry_run": bool(options.get("dry_run"))}


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ModuleRunTool(
        ToolSpec("media.dds_icon", "DDS icon generator", "Generate or convert configured icon and victory-tree DDS assets.", "media", (
            ToolOption("target", "Target", "text"), ToolOption("convert_existing_png", "Convert existing PNG", "file"), ToolOption("dry_run", "Dry run", "boolean", False), ToolOption("force_api", "Force API", "boolean", False), ToolOption("list_targets", "List targets", "boolean", False),
        ), artifact_formats=("dds", "png", "json")), "scripts/generate_dds_icon.py", _dds_options, dds_icon_plan, ("scripts", "scripts_engineering_department")))
    registry.register(ModuleRunTool(
        ToolSpec("media.wonder_image", "Wonder image generator", "Generate configured wonder PNG/DDS pairs.", "media", resource_ids=("editor.wonder", "editor.wonder_crop", "editor.cost_reward"), artifact_formats=("png", "dds", "json")),
        "scripts_engineering_department/generate_wonder_image.py", _wonder_options, wonder_image_plan, ("scripts", "scripts_engineering_department")))
    registry.register(HistoricalStyleTool())
    registry.register(ModuleRunTool(
        ToolSpec("media.historical_api", "Historical image API batch", "Run the configured historical image edit batch.", "media", (ToolOption("dry_run", "Dry run", "boolean", False),), artifact_formats=("png",)),
        "scripts/generate_historical_images.py", _historical_api_options, historical_api_plan, ("scripts",)))
    registry.register(WonderCropTool(cropper))
    return registry


registry = build_registry()
