#!/usr/bin/env python3
"""Shared crop settings for Engineering Department wonder image assets."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
# dds_image_lib.py is a generic, non-wonder-specific DDS utility that stayed
# in the main mod's scripts/ tree.
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from dds_image_lib import RgbaImage, crop_resize_rgba, read_image_rgba, write_dds  # noqa: E402
CROP_DATA_PATH = REPO_ROOT / "data" / "wonder_image_crops.json"
TARGET_ASPECT = (27, 11)
DEFAULT_OUTPUT_SIZE = (2160, 880)
CROPPED_SUFFIX = "_cropped"


@dataclass(frozen=True)
class WonderDdsWriteResult:
    crop_applied: bool
    source_width: int
    source_height: int
    output_width: int
    output_height: int
    levels: int
    crop_rect: tuple[float, float, float, float] | None


def empty_crop_data() -> dict[str, Any]:
    return {
        "version": 1,
        "target_aspect": {"width": TARGET_ASPECT[0], "height": TARGET_ASPECT[1]},
        "output_size": {"width": DEFAULT_OUTPUT_SIZE[0], "height": DEFAULT_OUTPUT_SIZE[1]},
        "crops": {},
    }


def normalize_crop_key(value: str) -> str:
    token = str(value).strip().replace("\\", "/").rsplit("/", 1)[-1].lower()
    for suffix in (".png", ".dds", ".json"):
        if token.endswith(suffix):
            token = token[: -len(suffix)]
            break
    return token


def cropped_wonder_dds_path(dds_path: Path) -> Path:
    return dds_path.with_name(f"{dds_path.stem}{CROPPED_SUFFIX}{dds_path.suffix}")


def cropped_wonder_image_name(stem: str) -> str:
    return f"{stem}{CROPPED_SUFFIX}"


def load_crop_data(path: Path = CROP_DATA_PATH) -> dict[str, Any]:
    if not path.exists():
        return empty_crop_data()
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")

    default_data = empty_crop_data()
    merged = dict(default_data)
    merged.update(data)
    if not isinstance(merged.get("crops"), dict):
        raise ValueError(f"{path}.crops must be a JSON object")
    merged["crops"] = {
        normalize_crop_key(key): value
        for key, value in merged["crops"].items()
        if isinstance(value, dict)
    }
    aspect_from_data(merged)
    output_size_from_data(merged)
    return merged


def save_crop_data(data: dict[str, Any], path: Path = CROP_DATA_PATH) -> None:
    payload = dict(empty_crop_data())
    payload.update(data)
    payload["crops"] = {
        normalize_crop_key(key): value
        for key, value in dict(payload.get("crops", {})).items()
        if isinstance(value, dict)
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def aspect_from_data(data: dict[str, Any]) -> tuple[int, int]:
    aspect = data.get("target_aspect", {})
    if not isinstance(aspect, dict):
        raise ValueError("target_aspect must be an object")
    width = int(aspect.get("width", TARGET_ASPECT[0]))
    height = int(aspect.get("height", TARGET_ASPECT[1]))
    if width <= 0 or height <= 0:
        raise ValueError("target_aspect dimensions must be positive")
    return width, height


def output_size_from_data(data: dict[str, Any]) -> tuple[int, int]:
    output_size = data.get("output_size")
    if output_size is None:
        return DEFAULT_OUTPUT_SIZE
    if not isinstance(output_size, dict):
        raise ValueError("output_size must be an object")
    width = int(output_size.get("width", DEFAULT_OUTPUT_SIZE[0]))
    height = int(output_size.get("height", DEFAULT_OUTPUT_SIZE[1]))
    if width <= 0 or height <= 0:
        raise ValueError("output_size dimensions must be positive")
    aspect_width, aspect_height = aspect_from_data(data)
    if width * aspect_height != height * aspect_width:
        raise ValueError("output_size must match target_aspect exactly")
    return width, height


def repo_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def aspect_ratio(aspect: tuple[int, int]) -> float:
    return aspect[0] / aspect[1]


def largest_center_crop_rect(
    image_width: int,
    image_height: int,
    aspect: tuple[int, int] = TARGET_ASPECT,
) -> tuple[float, float, float, float]:
    ratio = aspect_ratio(aspect)
    source_ratio = image_width / image_height
    if source_ratio >= ratio:
        crop_height = float(image_height)
        crop_width = crop_height * ratio
    else:
        crop_width = float(image_width)
        crop_height = crop_width / ratio
    left = (image_width - crop_width) / 2.0
    top = (image_height - crop_height) / 2.0
    return left, top, crop_width, crop_height


def clamp_rect_to_aspect(
    rect: tuple[float, float, float, float],
    image_width: int,
    image_height: int,
    aspect: tuple[int, int] = TARGET_ASPECT,
) -> tuple[float, float, float, float]:
    if image_width <= 0 or image_height <= 0:
        raise ValueError("image dimensions must be positive")

    ratio = aspect_ratio(aspect)
    _, _, max_width, max_height = largest_center_crop_rect(image_width, image_height, aspect)
    left, top, width, height = rect
    width = abs(float(width))
    height = abs(float(height))

    if width <= 0.001 or height <= 0.001:
        return largest_center_crop_rect(image_width, image_height, aspect)
    if width / height > ratio:
        width = height * ratio
    else:
        height = width / ratio

    if width > max_width:
        width = max_width
        height = width / ratio
    if height > max_height:
        height = max_height
        width = height * ratio

    width = max(1.0, min(width, float(image_width)))
    height = width / ratio
    if height > image_height:
        height = float(image_height)
        width = height * ratio

    left = min(max(float(left), 0.0), max(0.0, image_width - width))
    top = min(max(float(top), 0.0), max(0.0, image_height - height))
    return left, top, width, height


def rect_from_center(
    center_x: float,
    center_y: float,
    width: float,
    image_width: int,
    image_height: int,
    aspect: tuple[int, int] = TARGET_ASPECT,
) -> tuple[float, float, float, float]:
    height = float(width) / aspect_ratio(aspect)
    return clamp_rect_to_aspect(
        (center_x - width / 2.0, center_y - height / 2.0, width, height),
        image_width,
        image_height,
        aspect,
    )


def rect_from_points(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    image_width: int,
    image_height: int,
    aspect: tuple[int, int] = TARGET_ASPECT,
) -> tuple[float, float, float, float]:
    dx = end_x - start_x
    dy = end_y - start_y
    abs_dx = abs(dx)
    abs_dy = abs(dy)
    ratio = aspect_ratio(aspect)
    if abs_dx < 1.0 and abs_dy < 1.0:
        return largest_center_crop_rect(image_width, image_height, aspect)

    if abs_dy <= 0.001 or (abs_dx > 0.001 and abs_dx / ratio <= abs_dy):
        width = max(abs_dx, 1.0)
        height = width / ratio
    else:
        height = max(abs_dy, 1.0)
        width = height * ratio

    left = start_x if dx >= 0 else start_x - width
    top = start_y if dy >= 0 else start_y - height
    return clamp_rect_to_aspect((left, top, width, height), image_width, image_height, aspect)


def _number_from_mapping(mapping: dict[str, Any], key: str) -> float | None:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def get_crop_rect_for_image(
    crop_data: dict[str, Any],
    stem: str,
    image_width: int,
    image_height: int,
) -> tuple[float, float, float, float] | None:
    crops = crop_data.get("crops", {})
    if not isinstance(crops, dict):
        return None
    record = crops.get(normalize_crop_key(stem))
    if not isinstance(record, dict):
        return None

    aspect = aspect_from_data(crop_data)
    normalized = record.get("normalized")
    if isinstance(normalized, dict):
        x = _number_from_mapping(normalized, "x")
        y = _number_from_mapping(normalized, "y")
        width = _number_from_mapping(normalized, "width")
        height = _number_from_mapping(normalized, "height")
        if None not in (x, y, width, height):
            return clamp_rect_to_aspect(
                (
                    x * image_width,
                    y * image_height,
                    width * image_width,
                    height * image_height,
                ),
                image_width,
                image_height,
                aspect,
            )

    rect = record.get("rect")
    if not isinstance(rect, dict):
        return None
    x = _number_from_mapping(rect, "x")
    y = _number_from_mapping(rect, "y")
    width = _number_from_mapping(rect, "width")
    height = _number_from_mapping(rect, "height")
    if None in (x, y, width, height):
        return None

    source_width = record.get("source_width")
    source_height = record.get("source_height")
    if isinstance(source_width, (int, float)) and isinstance(source_height, (int, float)):
        if source_width > 0 and source_height > 0:
            x *= image_width / float(source_width)
            y *= image_height / float(source_height)
            width *= image_width / float(source_width)
            height *= image_height / float(source_height)

    return clamp_rect_to_aspect((x, y, width, height), image_width, image_height, aspect)


def set_crop_record(
    crop_data: dict[str, Any],
    stem: str,
    source_path: Path,
    image_width: int,
    image_height: int,
    rect: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    aspect = aspect_from_data(crop_data)
    left, top, width, height = clamp_rect_to_aspect(rect, image_width, image_height, aspect)
    crop_data.setdefault("crops", {})
    crop_data["crops"][normalize_crop_key(stem)] = {
        "source": repo_relative_path(source_path),
        "source_width": int(image_width),
        "source_height": int(image_height),
        "rect": {
            "x": round(left, 4),
            "y": round(top, 4),
            "width": round(width, 4),
            "height": round(height, 4),
        },
        "normalized": {
            "x": round(left / image_width, 8),
            "y": round(top / image_height, 8),
            "width": round(width / image_width, 8),
            "height": round(height / image_height, 8),
        },
    }
    return left, top, width, height


def remove_crop_record(crop_data: dict[str, Any], stem: str) -> bool:
    crops = crop_data.setdefault("crops", {})
    if not isinstance(crops, dict):
        crop_data["crops"] = {}
        return False
    return crops.pop(normalize_crop_key(stem), None) is not None


def crop_image_if_configured(
    image: RgbaImage,
    stem: str,
    crop_data: dict[str, Any],
) -> tuple[RgbaImage, tuple[float, float, float, float] | None]:
    rect = get_crop_rect_for_image(crop_data, stem, image.width, image.height)
    if rect is None:
        return image, None
    output_width, output_height = output_size_from_data(crop_data)
    return crop_resize_rgba(image, rect, output_width, output_height), rect


def write_wonder_dds_from_image(
    image: RgbaImage,
    dds_path: Path,
    stem: str,
    crop_data: dict[str, Any],
    background: tuple[int, int, int],
    *,
    dds_format: str = "DXT1",
    overwrite: bool = True,
) -> WonderDdsWriteResult:
    output_image, rect = crop_image_if_configured(image, stem, crop_data)
    levels = write_dds(
        output_image,
        dds_path,
        dds_format=dds_format,
        overwrite=overwrite,
        opaque_background=background,
    )
    return WonderDdsWriteResult(
        crop_applied=rect is not None,
        source_width=image.width,
        source_height=image.height,
        output_width=output_image.width,
        output_height=output_image.height,
        levels=levels,
        crop_rect=rect,
    )


def write_wonder_dds_from_source(
    source_path: Path,
    dds_path: Path,
    stem: str,
    crop_data: dict[str, Any],
    background: tuple[int, int, int],
    *,
    dds_format: str = "DXT1",
    overwrite: bool = True,
    allow_crop: bool = True,
) -> WonderDdsWriteResult:
    image = read_image_rgba(source_path)
    effective_crop_data = crop_data if allow_crop else empty_crop_data()
    return write_wonder_dds_from_image(
        image,
        dds_path,
        stem,
        effective_crop_data,
        background,
        dds_format=dds_format,
        overwrite=overwrite,
    )
