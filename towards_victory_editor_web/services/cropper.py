from __future__ import annotations

import copy
import json
import math
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .tooling import ToolContext, ToolOption, ToolResult, ToolSpec, capture_script_output, normalize_declared_options
from .platform import ChangeSet, ConflictError, FileSnapshot, ResourceDescriptor, assert_resource_base, atomic_write_files, file_transaction, repo_relative_path, snapshot_files

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
    def __init__(self, *, tasks: list[ImageTask] | None = None, data_path: Path = CROP_DATA_PATH, repo_root: Path = REPO_ROOT) -> None:
        self.tasks = build_tasks() if tasks is None else tasks
        self.data_path = data_path
        self.repo_root = repo_root
        self.lock = threading.RLock()
        self.logs: list[str] = []
        self._base = snapshot_files((self.data_path,), repo_root=self.repo_root)

    def resource_descriptor(self) -> ResourceDescriptor:
        return ResourceDescriptor(
            "editor.wonder_crop", "editor", "Wonder image crops",
            (repo_relative_path(self.data_path, self.repo_root),),
            ("media.wonder_crop",),
        )

    def _read_data(self) -> tuple[dict[str, Any], tuple[FileSnapshot, ...]]:
        before = snapshot_files((self.data_path,), repo_root=self.repo_root)
        data = load_crop_data(self.data_path)
        after = snapshot_files((self.data_path,), repo_root=self.repo_root)
        if before != after:
            raise ConflictError("Crop configuration changed during load")
        return data, after

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

    def load_resource(self) -> dict[str, Any]:
        with self.lock:
            data, base = self._read_data()
            descriptor = self.resource_descriptor()
            payload = {
                "resource": descriptor.payload(),
                "draft": {
                    "aspect": {"width": TARGET_ASPECT[0], "height": TARGET_ASPECT[1]},
                    "tasks": [self._summary(task, i, data) for i, task in enumerate(self.tasks)],
                    "logs": self.logs[-80:],
                },
                "change_set": ChangeSet(descriptor.id, (), base).payload(),
            }
            self._base = base
            return payload

    def _task(self, index: int) -> ImageTask:
        if index < 0:
            raise ValueError(f"Unknown crop image index: {index}")
        try:
            return self.tasks[index]
        except IndexError as exc:
            raise ValueError(f"Unknown crop image index: {index}") from exc

    def _candidate(self, data: dict[str, Any], edits: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        candidate = copy.deepcopy(data)
        diff: list[dict[str, Any]] = []
        for index_text, rect in edits.items():
            try:
                index = int(index_text)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid crop image index: {index_text}") from exc
            if str(index) != index_text:
                raise ValueError(f"Invalid crop image index: {index_text}")
            task = self._task(index)
            width, height = _png_size(task.png_path)
            key = normalize_crop_key(task.stem)
            before = copy.deepcopy(candidate.get("crops", {}).get(key))
            if rect is None:
                remove_crop_record(candidate, task.stem)
            else:
                if not isinstance(rect, dict):
                    raise ValueError("rect must be an object or null")
                try:
                    values = tuple(float(rect[field]) for field in ("x", "y", "width", "height"))
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError("rect must contain numeric x, y, width, and height") from exc
                if not all(math.isfinite(value) for value in values):
                    raise ValueError("rect coordinates must be finite")
                set_crop_record(candidate, task.stem, task.png_path, width, height, values)  # type: ignore[arg-type]
                candidate["crops"][key]["source"] = repo_relative_path(task.png_path, self.repo_root)
            after = candidate.get("crops", {}).get(key)
            if before != after:
                diff.append({"index": index, "key": task.key, "before": before, "after": copy.deepcopy(after)})
        return candidate, diff

    def validate_edits(self, edits: dict[str, Any]) -> dict[str, Any]:
        with self.lock:
            try:
                data, _ = self._read_data()
                _, diff = self._candidate(data, edits)
            except (KeyError, ValueError) as exc:
                return {"valid": False, "errors": [str(exc)], "diff": []}
            return {"valid": True, "errors": [], "diff": diff}

    def _prepare(self, edits: dict[str, Any], base: dict[str, str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        data, current = self._read_data()
        assert_resource_base(base, self._base, current)
        return self._candidate(data, edits)

    def preview_edits(self, edits: dict[str, Any], base: dict[str, str]) -> dict[str, Any]:
        with self.lock:
            _, diff = self._prepare(edits, base)
            descriptor = self.resource_descriptor()
            return {
                "resource": descriptor.payload(), "valid": True, "errors": [], "diff": diff,
                "change_set": ChangeSet(descriptor.id, descriptor.source_paths if diff else (), self._base).payload(),
            }

    def commit_edits(self, edits: dict[str, Any], base: dict[str, str]) -> dict[str, Any]:
        with self.lock:
            candidate, diff = self._prepare(edits, base)
            if diff:
                payload = json.dumps(candidate, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
                with file_transaction((self.data_path,), reload=lambda: None):
                    atomic_write_files({self.data_path: payload})
                    result = self.load_resource()
                self.logs.extend(f"{'removed' if item['after'] is None else 'saved'} {item['key']}" for item in diff)
                result["draft"]["logs"] = self.logs[-80:]
                return result
            return self.load_resource()

class WonderCropTool:
    spec = ToolSpec(
        id="media.wonder_crop",
        label="Wonder DDS rebuild",
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
        roots = {self.workspace.data_path}
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
