from __future__ import annotations

import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .tooling import ToolContext, ToolOption, ToolResult, ToolSpec, capture_script_output, normalize_declared_options

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from generate_wonder_image import (  # noqa: E402
    DEFAULT_PNG_DIR,
    DEFAULT_WONDERS_DIR,
    load_config,
    load_task_config,
    parse_background,
    require_object,
    resolve_repo_path,
    wonder_file_stem,
    convert_existing_assets,
)
from wonder_image_crop_lib import (  # noqa: E402
    CROP_DATA_PATH,
    TARGET_ASPECT,
    cropped_wonder_dds_path,
    get_crop_rect_for_image,
    largest_center_crop_rect,
    load_crop_data,
    normalize_crop_key,
    remove_crop_record,
    save_crop_data,
    set_crop_record,
)


@dataclass(frozen=True)
class ImageTask:
    key: str
    name: str
    stem: str
    png_path: Path
    dds_path: Path
    source: str


def _png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) < 24 or not header.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"{path} is not a PNG file")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def _repo_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def build_tasks() -> list[ImageTask]:
    config = load_config()
    configured = load_task_config(config)
    result: list[ImageTask] = []
    seen: set[Path] = set()
    png_dirs: set[Path] = set()
    for task in configured:
        name = str(task.get("name") or "").strip()
        stem = wonder_file_stem({"name": name})
        png_dir = resolve_repo_path(task.get("png_dir"), DEFAULT_PNG_DIR)
        dds_dir = resolve_repo_path(task.get("dds_dir"), DEFAULT_WONDERS_DIR)
        png_dirs.add(png_dir)
        png_path = png_dir / f"{stem}.png"
        if png_path.exists():
            result.append(ImageTask(str(task.get("key") or stem), name or stem, stem, png_path, dds_dir / f"{stem}.dds", "configured"))
            seen.add(png_path.resolve())
    for png_dir in sorted(png_dirs or {DEFAULT_PNG_DIR}, key=str):
        if not png_dir.exists():
            continue
        for png_path in sorted(png_dir.glob("*.png")):
            if png_path.resolve() in seen:
                continue
            stem = normalize_crop_key(png_path.name)
            result.append(ImageTask(stem, stem, stem, png_path, DEFAULT_WONDERS_DIR / f"{stem}.dds", "extra_png"))
            seen.add(png_path.resolve())
    return result


def _rect_payload(rect: tuple[float, float, float, float]) -> dict[str, float]:
    return {"x": rect[0], "y": rect[1], "width": rect[2], "height": rect[3]}


class CropperService:
    def __init__(self) -> None:
        self.tasks = build_tasks()
        self.lock = threading.RLock()
        self.logs: list[str] = []

    def _summary(self, task: ImageTask, index: int, data: dict[str, Any]) -> dict[str, Any]:
        width, height = _png_size(task.png_path)
        saved = get_crop_rect_for_image(data, task.stem, width, height)
        default = largest_center_crop_rect(width, height, TARGET_ASPECT)
        return {
            "index": index,
            "key": task.key,
            "name": task.name,
            "stem": task.stem,
            "source": task.source,
            "pngPath": _repo_path(task.png_path),
            "ddsPath": _repo_path(cropped_wonder_dds_path(task.dds_path)),
            "width": width,
            "height": height,
            "saved": saved is not None,
            "rect": _rect_payload(saved or default),
            "defaultRect": _rect_payload(default),
        }

    def bootstrap(self) -> dict[str, Any]:
        with self.lock:
            data = load_crop_data()
            return {
                "aspect": {"width": TARGET_ASPECT[0], "height": TARGET_ASPECT[1]},
                "dataPath": _repo_path(CROP_DATA_PATH),
                "tasks": [self._summary(task, i, data) for i, task in enumerate(self.tasks)],
                "logs": self.logs[-80:],
            }

    def _task(self, index: int) -> ImageTask:
        try:
            return self.tasks[index]
        except IndexError as exc:
            raise KeyError(f"Unknown crop image index: {index}") from exc

    def save(self, index: int, rect: dict[str, Any]) -> dict[str, Any]:
        task = self._task(index)
        try:
            values = tuple(float(rect[key]) for key in ("x", "y", "width", "height"))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("rect must contain numeric x, y, width, and height") from exc
        with self.lock:
            data = load_crop_data()
            width, height = _png_size(task.png_path)
            saved = set_crop_record(data, task.stem, task.png_path, width, height, values)  # type: ignore[arg-type]
            save_crop_data(data)
            message = f"saved {task.stem}: {saved[0]:.1f},{saved[1]:.1f},{saved[2]:.1f}x{saved[3]:.1f}"
            self.logs.append(message)
            return {"ok": True, "message": message, "task": self._summary(task, index, data)}

    def remove(self, index: int) -> dict[str, Any]:
        task = self._task(index)
        with self.lock:
            data = load_crop_data()
            removed = remove_crop_record(data, task.stem)
            save_crop_data(data)
            message = f"removed crop for {task.stem}" if removed else f"no saved crop for {task.stem}"
            self.logs.append(message)
            return {"ok": True, "message": message, "removed": removed, "task": self._summary(task, index, data)}

class WonderCropTool:
    spec = ToolSpec(
        id="media.wonder_crop",
        label="Wonder image cropper",
        description="Apply saved 27:11 wonder image crops and rebuild DDS assets.",
        group="media",
        options=(),
    )

    def __init__(self, workspace: CropperService) -> None:
        self.workspace = workspace

    def validate(self, options: dict[str, Any]) -> dict[str, Any]:
        return normalize_declared_options(self.spec, options)

    def roots(self, options: dict[str, Any]) -> tuple[Path, ...]:
        config = load_config()
        tasks = load_task_config(config)
        roots = {CROP_DATA_PATH}
        roots.update(resolve_repo_path(task.get("dds_dir"), DEFAULT_WONDERS_DIR) for task in tasks)
        return tuple(roots)

    def run(self, options: dict[str, Any], context: ToolContext) -> ToolResult:
        context.log("rebuild started")
        with self.workspace.lock:
            self.workspace.logs.append("rebuild started")
        config = load_config()
        tasks = load_task_config(config)
        background = parse_background(require_object(config, "dds").get("opaque_background", [0, 0, 0]))
        with capture_script_output(context):
            code = convert_existing_assets(tasks, background)
        if code != 0:
            raise RuntimeError(f"Wonder DDS rebuild exited with code {code}")
        context.log("DDS rebuild finished")
        with self.workspace.lock:
            self.workspace.logs.append("DDS rebuild finished")
        return ToolResult(message="Wonder DDS rebuild completed")


cropper = CropperService()
