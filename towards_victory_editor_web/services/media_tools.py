from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from .tooling import (
    ToolContext,
    ToolOption,
    ToolRegistry,
    ToolResult,
    ToolSpec,
    capture_script_output,
    normalize_declared_options,
)
from .cropper import WonderCropTool, cropper

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


def _json_options(spec: ToolSpec, options: dict[str, Any]) -> dict[str, Any]:
    return normalize_declared_options(spec, options)


class ModuleRunTool:
    """Adapter from the shared job contract to a generator's domain API.

    Generators expose ``run(options)``; their CLI ``main`` functions only
    parse command-line arguments and delegate here.  This keeps Web execution
    independent of ``sys.argv`` and makes the boundary explicit.
    """

    def __init__(self, spec: ToolSpec, script: str, options_builder, roots_builder, extra_paths=()) -> None:
        self.spec = spec
        self.script_path = REPO_ROOT / script
        self.options_builder = options_builder
        self.roots_builder = roots_builder
        self.extra_paths = tuple(REPO_ROOT / path for path in extra_paths)

    def validate(self, options: dict[str, Any]) -> dict[str, Any]:
        normalized = _json_options(self.spec, options)
        self.options_builder(normalized, validate_only=True)
        return normalized

    def roots(self, options: dict[str, Any]) -> tuple[Path, ...]:
        return self.roots_builder(options)

    def run(self, options: dict[str, Any], context: ToolContext) -> ToolResult:
        module = _load(self.spec.id.replace(".", "_"), self.script_path, self.extra_paths)
        run_options = self.options_builder(options, validate_only=False)
        with capture_script_output(context):
            result = module.run(run_options)
        if result not in (None, 0):
            raise RuntimeError(f"{self.spec.label} exited with code {result}")
        return ToolResult(message=f"{self.spec.label} completed")


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
    )

    def validate(self, options: dict[str, Any]) -> dict[str, Any]:
        normalized = _json_options(self.spec, options)
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

    def roots(self, options: dict[str, Any]) -> tuple[Path, ...]:
        return (_repo_dir(options["output_dir"]),)

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
        outputs: list[Path] = []
        with capture_script_output(context):
            for value in options["inputs"]:
                context.check_cancelled()
                result = module.run(Path(value), Path(options["output_dir"]), options["max_size"], bool(options.get("keep_intermediates", False)), options["seed"])
                outputs.extend(Path(item) for item in (result["final"], result["comparison"], result["report"]))
        return ToolResult(message="Historical image styling completed", output_paths=tuple(outputs))


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


def _dds_options(options: dict[str, Any], *, validate_only: bool) -> dict[str, Any]:
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


def _wonder_options(options: dict[str, Any], *, validate_only: bool) -> dict[str, Any]:
    return {"convert_existing_assets": bool(options.get("convert_existing_assets"))}


def _historical_api_options(options: dict[str, Any], *, validate_only: bool) -> dict[str, Any]:
    return {"dry_run": bool(options.get("dry_run"))}


def _roots(*relative: str):
    return lambda options: tuple(REPO_ROOT / path for path in relative)


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(ModuleRunTool(
        ToolSpec("media.dds_icon", "DDS icon generator", "Generate or convert configured icon and victory-tree DDS assets.", "media", (
            ToolOption("target", "Target", "text"), ToolOption("convert_existing_png", "Convert existing PNG", "file"), ToolOption("dry_run", "Dry run", "boolean", False), ToolOption("force_api", "Force API", "boolean", False), ToolOption("list_targets", "List targets", "boolean", False),
        )), "scripts/generate_dds_icon.py", _dds_options, _roots("data/generated_icons", "src/main_menu/gfx/interface/icons", "src_engineering_department/main_menu/gfx/interface/icons"), ("scripts", "scripts_engineering_department")))
    registry.register(ModuleRunTool(
        ToolSpec("media.wonder_image", "Wonder image generator", "Generate wonder PNG/DDS pairs or rebuild DDS files from existing PNGs.", "media", (ToolOption("convert_existing_assets", "Rebuild from existing assets", "boolean", False),)),
        "scripts_engineering_department/generate_wonder_image.py", _wonder_options, _roots("data/generated_wonders", "src_engineering_department/main_menu/gfx/interface/icons/towards_victory/wonders"), ("scripts", "scripts_engineering_department")))
    registry.register(HistoricalStyleTool())
    registry.register(ModuleRunTool(
        ToolSpec("media.historical_api", "Historical image API batch", "Run the configured historical image edit batch.", "media", (ToolOption("dry_run", "Dry run", "boolean", False),)),
        "scripts/generate_historical_images.py", _historical_api_options, _roots("assets/historical/processed"), ("scripts",)))
    registry.register(WonderCropTool(cropper))
    return registry


registry = build_registry()
