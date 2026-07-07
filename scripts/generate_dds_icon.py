#!/usr/bin/env python3
"""
Generate EU5 DDS assets through Packyapi Images API from a
natural-language prompt and target-specific style DDS/PNG references.

Usage:
  1. Edit generate_dds_icon_config.json.
  2. Set PACKY_API_KEY (or PACKY_SORA_TOKEN), or put api.api_key in
     generate_dds_icon.local.json.
  3. Run: conda run --no-capture-output -n eu5 python scripts/generate_dds_icon.py

The script expands a short asset idea into a production prompt for one selected
target, uploads that target's style-reference images, writes the generated PNG,
and converts it into one DDS target with enforced dimensions and byte limits.
It can also run the victory path icon batch, the victory reward icon batch,
and a wonder building icon batch for every generated final wonder building.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dds_image_lib import (
    PNG_SIGNATURE,
    RgbaImage,
    decode_png_rgba,
    encode_png_rgba,
    read_image_rgba,
    resize_rgba,
    write_dds,
)
from wonder_mechanics._core import (
    load_all_wonder_mechanics_data,
    load_generic_wonder_image_prompts,
    load_yaml as load_wonder_yaml,
    wonder_image_prompt,
)


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "generate_dds_icon_config.json"
LOCAL_CONFIG_PATH = REPO_ROOT / "generate_dds_icon.local.json"
DEFAULT_GENERATIONS_ENDPOINT = "https://www.right.codes/draw/v1/images/generations"
DEFAULT_EDITS_ENDPOINT = "https://www.right.codes/draw/v1/images/edits"
DEFAULT_PNG_DIR = REPO_ROOT / "data" / "generated_icons"
DEFAULT_REF_DIR = DEFAULT_PNG_DIR / "_style_refs"
WONDER_LOCALIZATION_PATH = REPO_ROOT / "data" / "wonder_localization.yaml"
DEFAULT_STYLE_UPLOAD_FIELD = "image"
VICTORY_REWARD_BATCH = "victory_reward_icons"
VICTORY_PATH_BATCH = "victory_path_icons"
WONDER_BUILDING_BATCH = "wonder_building_icons"

TARGET_PRESETS: dict[str, dict[str, Any]] = {
    "trade_good_icon": {
        "label": "trade goods Icon",
        "path": "src/main_menu/gfx/interface/icons/trade_goods/{name}.dds",
        "width": 128,
        "height": 128,
        "resize": "cover",
        "dds_format": "DXT5",
        "circle_crop": True,
        "circle_crop_feather_px": 8,
        "max_file_size_bytes": 100_000,
        "image_size": "1024x1024",
        "prompt_requirements": (
            "This is a compact trade-goods inventory icon. Make the silhouette bold, centered, "
            "and readable at 128x128; avoid landscape scenery and fine narrative detail."
        ),
    },
    "trade_good_illustration": {
        "label": "trade goods Icon illustration",
        "path": "src/main_menu/gfx/interface/icons/trade_goods/illustrations/{name}.dds",
        "width": 1080,
        "height": 440,
        "resize": "cover",
        "dds_format": "DXT5",
        "circle_crop": False,
        "circle_crop_feather_px": 0,
        "max_file_size_bytes": 1_000_000,
        "image_size": "2160x880",
        "prompt_requirements": (
            "This is a wide trade-goods illustration. Compose for a 1080x440 banner crop with "
            "a clear focal subject, supporting environment, and no tiny UI-icon-style object pile."
        ),
    },
    "building_icon": {
        "label": "building Icon",
        "path": "src/main_menu/gfx/interface/icons/buildings/{name}.dds",
        "width": 128,
        "height": 128,
        "resize": "cover",
        "dds_format": "DXT5",
        "mipmaps": True,
        "mipmap_min_dimension": 2,
        "circle_crop": True,
        "circle_crop_feather_px": 8,
        "max_file_size_bytes": 100_000,
        "image_size": "1024x1024",
        "prompt_requirements": (
            "This is a compact building icon. Treat the uploaded reference as the style "
            "authority: match its simple painterly brushwork, compact crop, low object count, "
            "and readable 128px silhouette. Communicate a wonder construction worksite with "
            "exactly 2-3 simple shapes: a small worksite structure, one crane or hoist, and a "
            "stone foundation. Avoid extra props, busy scenery, crowds, complex scaffolding, "
            "ornate architecture, or a finished monument."
        ),
    },
    "victory_reward_icon": {
        "label": "victory reward Icon",
        "path": "src/main_menu/gfx/interface/icons/towards_victory/victory_rewards/{name}.dds",
        "width": 128,
        "height": 128,
        "resize": "cover",
        "dds_format": "DXT5",
        "mipmaps": True,
        "mipmap_min_dimension": 2,
        "circle_crop": True,
        "circle_crop_feather_px": 8,
        "max_file_size_bytes": 100_000,
        "image_size": "1024x1024",
        "prompt_requirements": (
            "This is a compact victory reward icon. Use an extreme minimalist icon design: "
            "one centered symbolic subject, at most 1-2 small supporting shapes, a simple "
            "readable silhouette at 128px, restrained EU5-style painterly texture, no text, "
            "no letters, no logo, no UI frame, and no complex scene."
        ),
    },
    "victory_situation_icon": {
        "label": "victory situation Icon",
        "path": "src/main_menu/gfx/interface/icons/situations/{name}.dds",
        "width": 128,
        "height": 128,
        "resize": "cover",
        "dds_format": "DXT5",
        "mipmaps": True,
        "mipmap_min_dimension": 2,
        "circle_crop": True,
        "circle_crop_feather_px": 8,
        "max_file_size_bytes": 100_000,
        "image_size": "1024x1024",
        "prompt_requirements": (
            "This is the main Towards Victory situation icon. Use an extreme minimalist "
            "emblem design: one centered victory-road symbol, up to six tiny route accents, "
            "a strong readable silhouette at 128px, restrained EU5-style painterly texture, "
            "no text, no letters, no logo, no UI frame, and no complex scene."
        ),
    },
    "victory_path_icon": {
        "label": "victory path Icon",
        "path": "src/main_menu/gfx/interface/icons/towards_victory/victory_paths/{name}.dds",
        "width": 128,
        "height": 128,
        "resize": "cover",
        "dds_format": "DXT5",
        "mipmaps": True,
        "mipmap_min_dimension": 2,
        "circle_crop": True,
        "circle_crop_feather_px": 8,
        "max_file_size_bytes": 100_000,
        "image_size": "1024x1024",
        "prompt_requirements": (
            "This is a compact victory path icon. Use an extreme minimalist icon design: "
            "one centered symbolic subject, one small route accent at most, a distinct "
            "silhouette for this path, readable at 128px, restrained EU5-style painterly "
            "texture, no text, no letters, no logo, no UI frame, and no complex scene."
        ),
    },
}

TARGET_ALIASES = {
    "building": "building_icon",
    "buildings": "building_icon",
    "building_icons": "building_icon",
    "icon": "trade_good_icon",
    "trade_goods_icon": "trade_good_icon",
    "trade_good_icons": "trade_good_icon",
    "illustration": "trade_good_illustration",
    "trade_goods_illustration": "trade_good_illustration",
    "trade_goods_icon_illustration": "trade_good_illustration",
    "trade_good_icon_illustration": "trade_good_illustration",
    "reward_icon": "victory_reward_icon",
    "victory_reward": "victory_reward_icon",
    "victory_rewards_icon": "victory_reward_icon",
    "victory_rewards_icons": VICTORY_REWARD_BATCH,
    "victory_reward_icons": VICTORY_REWARD_BATCH,
    "victory_reward_batch": VICTORY_REWARD_BATCH,
    "victory_rewards": VICTORY_REWARD_BATCH,
    "victory_situation": "victory_situation_icon",
    "victory_situation_icons": "victory_situation_icon",
    "victory_route_icon": "victory_path_icon",
    "victory_route_icons": VICTORY_PATH_BATCH,
    "victory_path_icons": VICTORY_PATH_BATCH,
    "victory_paths": VICTORY_PATH_BATCH,
    "wonder_building_icons": WONDER_BUILDING_BATCH,
    "wonder_buildings": WONDER_BUILDING_BATCH,
    "wonder_final_building_icons": WONDER_BUILDING_BATCH,
    "wonder_final_buildings": WONDER_BUILDING_BATCH,
    "wonder_icons": WONDER_BUILDING_BATCH,
}

BATCH_TARGETS = {VICTORY_REWARD_BATCH, VICTORY_PATH_BATCH, WONDER_BUILDING_BATCH}


@dataclass(frozen=True)
class RetrySettings:
    max_attempts: int
    initial_delay_seconds: float
    max_delay_seconds: float
    backoff_multiplier: float


@dataclass(frozen=True)
class UploadFile:
    field_name: str
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class TargetSpec:
    name: str
    label: str
    path: Path
    width: int
    height: int
    resize: str
    dds_format: str
    mipmaps: bool
    mipmap_min_dimension: int
    opaque_background: tuple[int, int, int]
    max_file_size_bytes: int
    image_size: str
    prompt_requirements: str
    style_reference_paths: tuple[str, ...]
    asset_name: str
    image_overrides: dict[str, Any]
    local_template: dict[str, Any]
    circle_crop: bool
    circle_crop_feather_px: int


@dataclass(frozen=True)
class BatchIconTask:
    kind: str
    path_id: str
    path_label: str
    milestone: int | None
    choice: int | None
    target: TargetSpec
    image_config: dict[str, Any]
    prompt_config: dict[str, Any]
    output_config: dict[str, Any]
    allow_missing_style_reference_dry_run: bool = False


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config file: {CONFIG_PATH}")
    config = load_json_object(CONFIG_PATH)
    if LOCAL_CONFIG_PATH.exists():
        config = deep_merge(config, load_json_object(LOCAL_CONFIG_PATH))
    return config


def require_object(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a JSON object")
    return value


def resolve_repo_path(value: str | None, default_path: Path | None = None) -> Path:
    if not value:
        if default_path is None:
            raise ValueError("missing path")
        return default_path
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def safe_slug(value: str, default: str = "generated_icon") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()
    return slug or default


def parse_size(size: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", str(size).strip())
    if not match:
        raise ValueError(f"Invalid image size {size!r}; expected WIDTHxHEIGHT")
    width, height = int(match.group(1)), int(match.group(2))
    if width <= 0 or height <= 0:
        raise ValueError("Image size must be positive")
    if width % 16 or height % 16:
        raise ValueError("gpt-image-2 request sizes must use edges that are multiples of 16")
    if max(width, height) > 3840:
        raise ValueError("gpt-image-2 maximum edge length is 3840")
    if max(width, height) / min(width, height) > 3:
        raise ValueError("gpt-image-2 aspect ratio cannot exceed 3:1")
    pixels = width * height
    if pixels < 655_360 or pixels > 8_294_400:
        raise ValueError("gpt-image-2 total pixels must be 655360..8294400")
    return width, height


def parse_rgb(value: Any, key: str = "opaque_background") -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{key} must be a three-item RGB list")
    result = tuple(int(item) for item in value)
    if any(item < 0 or item > 255 for item in result):
        raise ValueError(f"{key} values must be between 0 and 255")
    return result  # type: ignore[return-value]


def parse_args(argv: list[str]) -> argparse.Namespace:
    supported = sorted([*TARGET_PRESETS, *BATCH_TARGETS])
    parser = argparse.ArgumentParser(description="Generate configured EU5 DDS icon assets.")
    parser.add_argument(
        "--target",
        help=(
            "Generation target to write. Supported values: "
            f"{', '.join(supported)}. Aliases like icon and illustration are accepted."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config, references, prompt, and payload without calling the API or writing output art.",
    )
    parser.add_argument(
        "--convert-existing-png",
        metavar="PATH",
        help="Convert an existing PNG into the selected DDS target without calling the image API.",
    )
    parser.add_argument(
        "--list-targets",
        action="store_true",
        help="Print supported generation targets and batch modes, then exit.",
    )
    parser.add_argument(
        "--force-api",
        action="store_true",
        help="Ignore output.targets.<target>.local_template and call the image API for this target.",
    )
    return parser.parse_args(argv)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def format_bytes(value: int) -> str:
    return f"{value:,} bytes"


def expand_template(value: str, asset_name: str, target_name: str) -> str:
    return value.replace("{name}", asset_name).replace("{target}", target_name)


def normalize_target_name(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    key = safe_slug(raw)
    return TARGET_ALIASES.get(key, key)


def is_batch_target_name(value: str) -> bool:
    return value in BATCH_TARGETS


def parse_path_list(value: Any, key: str) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a string or list of strings")
    return value


def configured_target_names(output_config: dict[str, Any]) -> list[str]:
    targets = output_config.get("targets", {})
    names: list[str] = []
    if isinstance(targets, dict):
        names = [normalize_target_name(key) for key in targets]
    elif isinstance(targets, list):
        for index, target in enumerate(targets, start=1):
            if not isinstance(target, dict):
                raise ValueError(f"output.targets[{index}] must be a JSON object")
            names.append(normalize_target_name(target.get("name") or f"target_{index}"))
    elif targets not in ({}, [], None):
        raise ValueError("output.targets must be an object keyed by target name or a legacy target list")
    return [name for name in names if name]


def select_target_name(config: dict[str, Any], output_config: dict[str, Any], cli_target: str | None) -> str:
    raw_target = cli_target or config.get("generation_target") or output_config.get("target")
    if raw_target:
        target_name = normalize_target_name(raw_target)
    else:
        names = sorted(set(configured_target_names(output_config)))
        if len(names) == 1:
            target_name = names[0]
        else:
            valid = ", ".join(sorted([*TARGET_PRESETS, *BATCH_TARGETS]))
            raise ValueError(
                "Set generation_target (or pass --target) so the helper writes exactly one DDS target. "
                f"Supported targets: {valid}"
            )

    if target_name not in TARGET_PRESETS and not is_batch_target_name(target_name):
        valid = ", ".join(sorted([*TARGET_PRESETS, *BATCH_TARGETS]))
        raise ValueError(f"Unsupported generation target {raw_target!r}. Supported targets: {valid}")
    return target_name


def target_override(output_config: dict[str, Any], target_name: str) -> dict[str, Any]:
    targets = output_config.get("targets", {})
    if not targets:
        return {}
    if isinstance(targets, dict):
        for key, value in targets.items():
            if normalize_target_name(key) == target_name:
                if not isinstance(value, dict):
                    raise ValueError(f"output.targets.{key} must be a JSON object")
                return value
        return {}
    if isinstance(targets, list):
        for index, value in enumerate(targets, start=1):
            if not isinstance(value, dict):
                raise ValueError(f"output.targets[{index}] must be a JSON object")
            if normalize_target_name(value.get("name") or f"target_{index}") == target_name:
                return value
        return {}
    raise ValueError("output.targets must be an object keyed by target name or a legacy target list")


def parse_max_file_size_bytes(target_config: dict[str, Any]) -> int:
    if "max_file_size_bytes" in target_config:
        return int(target_config["max_file_size_bytes"])
    if "max_bytes" in target_config:
        return int(target_config["max_bytes"])
    if "max_file_size_kb" in target_config:
        return int(float(target_config["max_file_size_kb"]) * 1000)
    if "max_file_size_mb" in target_config:
        return int(float(target_config["max_file_size_mb"]) * 1_000_000)
    return 0


def target_style_reference_paths(
    target_config: dict[str, Any],
    style_config: dict[str, Any],
    target_name: str,
    asset_name: str,
) -> tuple[str, ...]:
    raw_paths: Any = target_config.get("style_reference_paths")
    if raw_paths is None and isinstance(target_config.get("style_reference"), dict):
        raw_paths = target_config["style_reference"].get("paths")

    if raw_paths is None and isinstance(style_config.get("paths_by_target"), dict):
        for key, value in style_config["paths_by_target"].items():
            if normalize_target_name(key) == target_name:
                raw_paths = value
                break

    if raw_paths is None and isinstance(style_config.get("targets"), dict):
        for key, value in style_config["targets"].items():
            if normalize_target_name(key) == target_name:
                if not isinstance(value, dict):
                    raise ValueError(f"style_reference.targets.{key} must be a JSON object")
                raw_paths = value.get("paths")
                break

    if raw_paths is None:
        raw_paths = style_config.get("paths", [])

    paths = parse_path_list(raw_paths, f"style reference paths for target {target_name}")
    return tuple(expand_template(path, asset_name, target_name) for path in paths)


def load_target_spec(
    config: dict[str, Any],
    output_config: dict[str, Any],
    style_config: dict[str, Any],
    cli_target: str | None,
) -> TargetSpec:
    target_name = select_target_name(config, output_config, cli_target)
    if is_batch_target_name(target_name):
        raise ValueError(f"{target_name} is a batch mode, not a single DDS target")
    preset = TARGET_PRESETS[target_name]
    target_config = deep_merge(preset, target_override(output_config, target_name))
    return build_target_spec(target_name, target_config, output_config, style_config)


def build_target_spec(
    target_name: str,
    target_config: dict[str, Any],
    output_config: dict[str, Any],
    style_config: dict[str, Any],
) -> TargetSpec:
    if target_name not in TARGET_PRESETS:
        valid = ", ".join(sorted(TARGET_PRESETS))
        raise ValueError(f"Unsupported single DDS target {target_name!r}. Supported targets: {valid}")
    preset = TARGET_PRESETS[target_name]
    target_config = deep_merge(preset, target_config)
    asset_name = safe_slug(
        str(
            target_config.get("asset_name")
            or target_config.get("output_name")
            or output_config.get("name")
            or "generated_icon"
        )
    )

    width = int(target_config.get("width") or preset["width"])
    height = int(target_config.get("height") or preset["height"])
    expected_size = (int(preset["width"]), int(preset["height"]))
    if (width, height) != expected_size:
        raise ValueError(
            f"{target_name} must be {expected_size[0]}x{expected_size[1]}, "
            f"but config requested {width}x{height}"
        )

    max_file_size_bytes = parse_max_file_size_bytes(target_config)
    expected_max = int(preset["max_file_size_bytes"])
    if max_file_size_bytes <= 0:
        raise ValueError(f"{target_name} must set max_file_size_bytes")
    if max_file_size_bytes > expected_max:
        raise ValueError(
            f"{target_name} max_file_size_bytes cannot exceed {format_bytes(expected_max)}; "
            f"config requested {format_bytes(max_file_size_bytes)}"
        )

    dds_format = str(target_config.get("dds_format") or preset["dds_format"]).upper()
    if dds_format not in {"DXT1", "DXT5"}:
        raise ValueError("dds_format must be DXT1 or DXT5")
    resize = str(target_config.get("resize") or preset["resize"]).lower().strip()
    if resize not in {"cover", "contain", "stretch"}:
        raise ValueError("resize mode must be cover, contain, or stretch")
    mipmaps = bool(target_config.get("mipmaps", False))
    mipmap_min_dimension = int(target_config.get("mipmap_min_dimension", 1))
    if mipmap_min_dimension < 1:
        raise ValueError("mipmap_min_dimension must be at least 1")

    image_size = str(target_config.get("image_size") or preset["image_size"])
    if image_size != "auto":
        parse_size(image_size)

    path_template = str(target_config.get("path") or preset["path"])
    path = resolve_repo_path(expand_template(path_template, asset_name, target_name))
    style_reference_paths = target_style_reference_paths(target_config, style_config, target_name, asset_name)
    image_overrides = target_config.get("image", {})
    if not isinstance(image_overrides, dict):
        raise ValueError(f"output.targets.{target_name}.image must be a JSON object")
    local_template = target_config.get("local_template", {})
    if not isinstance(local_template, dict):
        raise ValueError(f"output.targets.{target_name}.local_template must be a JSON object")

    return TargetSpec(
        name=target_name,
        label=str(target_config.get("label") or preset["label"]),
        path=path,
        width=width,
        height=height,
        resize=resize,
        dds_format=dds_format,
        mipmaps=mipmaps,
        mipmap_min_dimension=mipmap_min_dimension,
        opaque_background=parse_rgb(
            target_config.get("opaque_background", output_config.get("opaque_background", [0, 0, 0]))
        ),
        max_file_size_bytes=max_file_size_bytes,
        image_size=image_size,
        prompt_requirements=str(target_config.get("prompt_requirements") or preset["prompt_requirements"]),
        style_reference_paths=style_reference_paths,
        asset_name=asset_name,
        image_overrides=image_overrides,
        local_template=local_template,
        circle_crop=bool(target_config.get("circle_crop", False)),
        circle_crop_feather_px=int(target_config.get("circle_crop_feather_px", 0)),
    )


def apply_target_image_settings(image_config: dict[str, Any], target: TargetSpec) -> dict[str, Any]:
    configured = deep_merge(image_config, target.image_overrides)
    configured["size"] = target.image_size
    return configured


def clamp_float(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge0 == edge1:
        return 1.0 if value >= edge1 else 0.0
    t = clamp_float((value - edge0) / (edge1 - edge0))
    return t * t * (3.0 - 2.0 * t)


def apply_circle_icon_crop(image: RgbaImage, feather_px: int) -> RgbaImage:
    feather = max(0.0, float(feather_px))
    if feather <= 0:
        feather = 0.0
    radius = min(image.width, image.height) / 2.0
    center_x = image.width / 2.0
    center_y = image.height / 2.0
    rgba = bytearray(image.rgba)
    for y in range(image.height):
        dy = (y + 0.5) - center_y
        for x in range(image.width):
            dx = (x + 0.5) - center_x
            dist = math.hypot(dx, dy)
            pos = (y * image.width + x) * 4
            if dist >= radius:
                rgba[pos + 3] = 0
                continue
            if feather > 0 and dist > radius - feather:
                falloff = smoothstep(radius, radius - feather, dist)
                rgba[pos + 3] = int(round(rgba[pos + 3] * falloff))
    return RgbaImage(image.width, image.height, bytes(rgba))


def prepare_target_image(source_image: RgbaImage, target: TargetSpec) -> RgbaImage:
    image = resize_rgba(source_image, target.width, target.height, target.resize)
    if target.circle_crop:
        image = apply_circle_icon_crop(image, target.circle_crop_feather_px)
    return image


def default_victory_reward_paths() -> list[dict[str, str]]:
    return [
        {
            "id": "conquest",
            "label": "Conquest Victory",
            "template_prompt": "a single crowned sword silhouette over a tiny laurel mark",
            "reward_motif": "a crowned sword, shield, or banner symbol for conquest rewards",
            "style_reference_paths": ["data/generated_icons/_style_refs/construction_center.dds"],
        },
        {
            "id": "prosperity",
            "label": "Prosperity Victory",
            "template_prompt": "a single sprouting coin or granary mark",
            "reward_motif": "a sprouting coin, granary, or civic growth symbol for prosperity rewards",
            "style_reference_paths": ["data/generated_icons/_style_refs/construction_center.dds"],
        },
        {
            "id": "trade",
            "label": "Trade Victory",
            "template_prompt": "a single balanced scale with a small merchant sail accent",
            "reward_motif": "a scale, merchant sail, coin, or trade route symbol for trade rewards",
            "style_reference_paths": ["data/generated_icons/_style_refs/icon_goods_marble.dds"],
        },
        {
            "id": "diplomatic",
            "label": "Diplomatic Victory",
            "template_prompt": "a single sealed treaty scroll with two small clasped rings",
            "reward_motif": "a treaty scroll, seal, clasped rings, or envoy symbol for diplomatic rewards",
            "style_reference_paths": ["data/generated_icons/_style_refs/construction_center.dds"],
        },
        {
            "id": "cultural",
            "label": "Cultural Victory",
            "template_prompt": "a single theater mask with a small star accent",
            "reward_motif": "a theater mask, lyre, manuscript, or star symbol for cultural rewards",
            "style_reference_paths": ["data/generated_icons/_style_refs/icon_goods_marble.dds"],
        },
        {
            "id": "science",
            "label": "Scientific Victory",
            "template_prompt": "a single astrolabe disk with one small spark",
            "reward_motif": "an astrolabe, compass, lens, or spark symbol for scientific rewards",
            "style_reference_paths": ["data/generated_icons/_style_refs/construction_center.dds"],
        },
    ]


def default_victory_path_icon_paths() -> list[dict[str, Any]]:
    return [
        {
            "id": "conquest",
            "label": "Conquest Victory",
            "theme_color": "crimson red",
            "icon_prompt": "a crowned sword crossing a compact fortress banner",
            "style_reference_paths": [
                "src/main_menu/gfx/interface/icons/towards_victory/victory_rewards/tv_victory_conquest_template.dds"
            ],
        },
        {
            "id": "prosperity",
            "label": "Prosperity Victory",
            "theme_color": "leaf green",
            "icon_prompt": "a golden granary arch with a sprouting coin at its base",
            "style_reference_paths": [
                "src/main_menu/gfx/interface/icons/towards_victory/victory_rewards/tv_victory_prosperity_template.dds"
            ],
        },
        {
            "id": "trade",
            "label": "Trade Victory",
            "theme_color": "gold yellow",
            "icon_prompt": "a merchant sail forming a balanced scale over a small coin trail",
            "style_reference_paths": [
                "src/main_menu/gfx/interface/icons/towards_victory/victory_rewards/tv_victory_trade_template.dds"
            ],
        },
        {
            "id": "diplomatic",
            "label": "Diplomatic Victory",
            "theme_color": "ivory white",
            "icon_prompt": "a sealed treaty scroll clasped by two small interlocking rings",
            "style_reference_paths": [
                "src/main_menu/gfx/interface/icons/towards_victory/victory_rewards/tv_victory_diplomatic_template.dds"
            ],
        },
        {
            "id": "cultural",
            "label": "Cultural Victory",
            "theme_color": "royal purple",
            "icon_prompt": "a theatre mask beside a tiny lyre and single star",
            "style_reference_paths": [
                "src/main_menu/gfx/interface/icons/towards_victory/victory_rewards/tv_victory_cultural_template.dds"
            ],
        },
        {
            "id": "science",
            "label": "Scientific Victory",
            "theme_color": "azure blue",
            "icon_prompt": "an astrolabe ring with a lens spark and small compass point",
            "style_reference_paths": [
                "src/main_menu/gfx/interface/icons/towards_victory/victory_rewards/tv_victory_science_template.dds"
            ],
        },
    ]


def format_task_template(template: str, values: dict[str, Any]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{" + key + "}", str(value))
    return result


def output_stem_path(output_config: dict[str, Any], target: TargetSpec, suffix: str) -> Path:
    return resolve_repo_path(output_config.get(f"{suffix}_dir"), DEFAULT_PNG_DIR) / (
        f"{output_artifact_stem(output_config, target)}.{suffix}"
    )


def existing_template_reference(output_config: dict[str, Any], target: TargetSpec) -> str:
    png_path = output_stem_path(output_config, target, "png")
    if png_path.exists():
        return display_path(png_path).replace("\\", "/")
    return display_path(target.path).replace("\\", "/")


def compact_prompt_text(value: Any, *, max_chars: int = 280) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.split(r"\b(?:historical fantasy|historically grounded)\b", text, maxsplit=1, flags=re.IGNORECASE)[0]
    text = text.strip().rstrip(",.;")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip(" ,.;") + "..."


def load_english_wonder_localization(path: Path = WONDER_LOCALIZATION_PATH) -> dict[str, str]:
    if not path.exists():
        return {}
    data = load_wonder_yaml(path) or {}
    root = data.get("wonder_localization", {})
    if not isinstance(root, dict):
        raise ValueError("data/wonder_localization.yaml wonder_localization must be a mapping")
    english = root.get("english", {})
    if not isinstance(english, dict):
        raise ValueError("data/wonder_localization.yaml wonder_localization.english must be a mapping")
    return {str(key): str(value) for key, value in english.items()}


def label_from_key(localization: dict[str, str], key: str) -> str:
    value = compact_prompt_text(localization.get(key, ""), max_chars=120)
    if value:
        return value
    for prefix in ("tv_wonder_unique_", "tv_wonder_"):
        if key.startswith(prefix):
            key = key[len(prefix):]
            break
    return key.replace("_", " ").title()


def wonder_building_batch_config(config: dict[str, Any]) -> dict[str, Any]:
    value = config.get(WONDER_BUILDING_BATCH, {})
    if not isinstance(value, dict):
        raise ValueError(f"{WONDER_BUILDING_BATCH} must be a JSON object")
    return value


def victory_batch_config(config: dict[str, Any]) -> dict[str, Any]:
    value = config.get(VICTORY_REWARD_BATCH, {})
    if not isinstance(value, dict):
        raise ValueError(f"{VICTORY_REWARD_BATCH} must be a JSON object")
    return value


def victory_path_batch_config(config: dict[str, Any]) -> dict[str, Any]:
    value = config.get(VICTORY_PATH_BATCH, {})
    if not isinstance(value, dict):
        raise ValueError(f"{VICTORY_PATH_BATCH} must be a JSON object")
    return value


def load_victory_path_configs(batch_config: dict[str, Any]) -> list[dict[str, Any]]:
    raw_paths = batch_config.get("paths", default_victory_reward_paths())
    if not isinstance(raw_paths, list) or not raw_paths:
        raise ValueError(f"{VICTORY_REWARD_BATCH}.paths must be a non-empty list")
    paths: list[dict[str, Any]] = []
    for index, raw_path in enumerate(raw_paths, start=1):
        if not isinstance(raw_path, dict):
            raise ValueError(f"{VICTORY_REWARD_BATCH}.paths[{index}] must be a JSON object")
        path_id = safe_slug(str(raw_path.get("id") or ""))
        if not path_id:
            raise ValueError(f"{VICTORY_REWARD_BATCH}.paths[{index}].id must be set")
        path_config = dict(raw_path)
        path_config["id"] = path_id
        path_config["label"] = str(path_config.get("label") or path_id.replace("_", " ").title())
        paths.append(path_config)
    return paths


def load_victory_path_icon_configs(batch_config: dict[str, Any]) -> list[dict[str, Any]]:
    raw_paths = batch_config.get("paths", default_victory_path_icon_paths())
    if not isinstance(raw_paths, list) or not raw_paths:
        raise ValueError(f"{VICTORY_PATH_BATCH}.paths must be a non-empty list")
    paths: list[dict[str, Any]] = []
    for index, raw_path in enumerate(raw_paths, start=1):
        if not isinstance(raw_path, dict):
            raise ValueError(f"{VICTORY_PATH_BATCH}.paths[{index}] must be a JSON object")
        path_id = safe_slug(str(raw_path.get("id") or ""))
        if not path_id:
            raise ValueError(f"{VICTORY_PATH_BATCH}.paths[{index}].id must be set")
        path_config = dict(raw_path)
        path_config["id"] = path_id
        path_config["label"] = str(path_config.get("label") or path_id.replace("_", " ").title())
        paths.append(path_config)
    return paths


def build_wonder_building_icon_batch_tasks(
    config: dict[str, Any],
    output_config: dict[str, Any],
    style_config: dict[str, Any],
    image_config: dict[str, Any],
    prompt_config: dict[str, Any],
) -> list[BatchIconTask]:
    batch_config = wonder_building_batch_config(config)
    target_name = "building_icon"
    base_target_config = deep_merge(
        TARGET_PRESETS[target_name],
        require_object(batch_config, "target"),
    )

    include_generic = bool(batch_config.get("include_generic", True))
    include_unique = bool(batch_config.get("include_unique", True))
    if not include_generic and not include_unique:
        raise ValueError(f"{WONDER_BUILDING_BATCH} must include generic wonders, unique wonders, or both")

    output_dir = str(
        batch_config.get("output_dir")
        or base_target_config.get("path", TARGET_PRESETS[target_name]["path"]).rsplit("/", 1)[0]
    )
    artifact_stem_template = str(batch_config.get("artifact_stem") or "{name}")
    default_refs = parse_path_list(
        batch_config.get(
            "style_reference_paths",
            base_target_config.get(
                "style_reference_paths",
                ["data/generated_icons/_style_refs/construction_center.dds"],
            ),
        ),
        f"{WONDER_BUILDING_BATCH}.style_reference_paths",
    )
    icon_rules = str(
        batch_config.get("icon_rules")
        or (
            "Vanilla EU5 building icon style: compact centered 128px silhouette, simple painterly "
            "brushwork, limited palette of 3-4 colors, one main architectural form with at most "
            "1-2 tiny supporting shapes, readable at small size, no text, no letters, no logo, "
            "no UI frame, no full landscape, no crowded scene, no intricate panorama."
        )
    )
    prompt_prefix = str(
        batch_config.get("prompt_prefix")
        or "Create a compact vanilla-style Europa Universalis V wonder building icon for"
    )
    overrides = batch_config.get("overrides", {})
    if not isinstance(overrides, dict):
        raise ValueError(f"{WONDER_BUILDING_BATCH}.overrides must be a JSON object")

    wonders, _ = load_all_wonder_mechanics_data(include_unique=include_unique)
    if not include_generic:
        wonders = [wonder for wonder in wonders if bool(wonder.get("is_unique"))]
    localization = load_english_wonder_localization()
    generic_prompts = load_generic_wonder_image_prompts()

    batch_output_config = dict(output_config)
    batch_output_config["artifact_stem"] = artifact_stem_template
    tasks: list[BatchIconTask] = []
    seen_buildings: set[str] = set()
    for wonder in sorted(wonders, key=lambda item: int(item["id"])):
        wonder_key = str(wonder["key"])
        wonder_label = label_from_key(localization, str(wonder.get("concept") or f"tv_wonder_{wonder_key}"))
        wonder_context = compact_prompt_text(wonder_image_prompt(wonder, generic_prompts))
        final_buildings = wonder.get("final_buildings", {})
        for style, building in sorted(final_buildings.items(), key=lambda item: int(item[0])):
            building_name = safe_slug(str(building))
            if building_name in seen_buildings:
                continue
            seen_buildings.add(building_name)

            raw_override = overrides.get(building_name, {})
            if not isinstance(raw_override, dict):
                raise ValueError(f"{WONDER_BUILDING_BATCH}.overrides.{building_name} must be a JSON object")
            override = dict(raw_override)
            building_label = str(
                override.get("label") or label_from_key(localization, building_name)
            )
            branch_note = compact_prompt_text(localization.get(f"{building_name}_desc", ""), max_chars=180)
            icon_subject = str(
                override.get("icon_prompt")
                or override.get("subject")
                or (
                    f"{building_label}, reduced to one simple architectural silhouette or emblem "
                    f"from the {wonder_label}"
                )
            )
            refs = parse_path_list(
                override.get("style_reference_paths", default_refs),
                f"{WONDER_BUILDING_BATCH}.overrides.{building_name}.style_reference_paths",
            )
            note_sentence = f" Branch note: {branch_note}." if branch_note else ""
            target_config = deep_merge(
                base_target_config,
                {
                    "asset_name": building_name,
                    "path": f"{output_dir}/{{name}}.dds",
                    "style_reference_paths": refs,
                    "prompt_requirements": icon_rules,
                    "local_template": {"enabled": False},
                    "image": {
                        "natural_prompt": (
                            f"{prompt_prefix} {building_label}, the style {style} final building "
                            f"of {wonder_label}. Subject: {icon_subject}. Wonder motif for identity "
                            f"only: {wonder_context}.{note_sentence} {icon_rules}"
                        ),
                        "negative_prompt": (
                            "busy scene, landscape, full panorama, many objects, extra props, crowds, "
                            "workers, complex scaffolding, detailed narrative scene, ornate palace scene, "
                            "realistic photo, text, letters, numbers, logo, watermark, UI frame"
                        ),
                    },
                },
            )
            override_target_config = {
                key: value
                for key, value in override.items()
                if key not in {"icon_prompt", "label", "subject"}
            }
            target_config = deep_merge(target_config, override_target_config)
            target = build_target_spec(target_name, target_config, batch_output_config, style_config)
            tasks.append(
                BatchIconTask(
                    kind="unique_wonder_building" if bool(wonder.get("is_unique")) else "generic_wonder_building",
                    path_id=building_name,
                    path_label=f"{wonder_label}: {building_label}",
                    milestone=None,
                    choice=None,
                    target=target,
                    image_config=apply_target_image_settings(image_config, target),
                    prompt_config=prompt_config,
                    output_config=batch_output_config,
                )
            )

    if not tasks:
        raise ValueError(f"{WONDER_BUILDING_BATCH} did not find any final wonder buildings")
    return tasks


def build_victory_batch_tasks(
    config: dict[str, Any],
    output_config: dict[str, Any],
    style_config: dict[str, Any],
    image_config: dict[str, Any],
    prompt_config: dict[str, Any],
) -> list[BatchIconTask]:
    batch_config = victory_batch_config(config)
    target_name = "victory_reward_icon"
    target_defaults = target_override(output_config, target_name)
    base_target_config = deep_merge(TARGET_PRESETS[target_name], target_defaults)
    base_target_config = deep_merge(base_target_config, require_object(batch_config, "target"))

    paths = load_victory_path_configs(batch_config)
    milestones_raw = batch_config.get("milestones", [1, 2, 3, 4, 5])
    choices_raw = batch_config.get("choices", [1, 2, 3])
    if not isinstance(milestones_raw, list) or not all(isinstance(item, int) for item in milestones_raw):
        raise ValueError(f"{VICTORY_REWARD_BATCH}.milestones must be a list of integers")
    if not isinstance(choices_raw, list) or not all(isinstance(item, int) for item in choices_raw):
        raise ValueError(f"{VICTORY_REWARD_BATCH}.choices must be a list of integers")

    output_dir = str(
        batch_config.get("output_dir")
        or base_target_config.get("path", TARGET_PRESETS[target_name]["path"]).rsplit("/", 1)[0]
    )
    template_name_template = str(batch_config.get("template_name_template") or "tv_victory_{path}_template")
    reward_name_template = str(
        batch_config.get("reward_name_template") or "tv_victory_{path}_m{milestone}_reward_{choice}"
    )
    artifact_stem_template = str(batch_config.get("artifact_stem") or "{name}")
    minimalist_rules = str(
        batch_config.get("minimalist_rules")
        or (
            "Extreme minimalist EU5 reward icon: one central symbolic subject, at most 1-2 tiny supporting shapes, "
            "strong silhouette, readable at 128px, no text, no letters, no logo, no UI frame, no complex scene."
        )
    )
    template_prompt_prefix = str(
        batch_config.get("template_prompt_prefix")
        or "Route style template. Create the canonical visual language for this victory path:"
    )
    reward_prompt_prefix = str(
        batch_config.get("reward_prompt_prefix")
        or "Create a slightly different reward option icon in the same route style:"
    )
    choice_variants = batch_config.get(
        "choice_variants",
        {
            "1": "variant 1: use the cleanest frontal silhouette and the calmest accent color.",
            "2": "variant 2: shift the symbol angle slightly and add one small secondary accent.",
            "3": "variant 3: use a compact diagonal composition and a subtly brighter highlight.",
        },
    )
    if not isinstance(choice_variants, dict):
        raise ValueError(f"{VICTORY_REWARD_BATCH}.choice_variants must be a JSON object")

    batch_output_config = dict(output_config)
    batch_output_config["artifact_stem"] = artifact_stem_template
    tasks: list[BatchIconTask] = []
    for path_config in paths:
        path_id = str(path_config["id"])
        path_label = str(path_config["label"])
        values = {"path": path_id}
        template_name = safe_slug(format_task_template(template_name_template, values))
        template_refs = parse_path_list(
            path_config.get("template_style_reference_paths", path_config.get("style_reference_paths", [])),
            f"{VICTORY_REWARD_BATCH}.paths.{path_id}.style_reference_paths",
        )
        template_subject = str(path_config.get("template_prompt") or path_config.get("motif") or path_label)
        template_target_config = deep_merge(
            base_target_config,
            {
                "asset_name": template_name,
                "path": f"{output_dir}/{{name}}.dds",
                "style_reference_paths": template_refs,
                "prompt_requirements": minimalist_rules,
                "image": {
                    "natural_prompt": (
                        f"{template_prompt_prefix} {path_label}. Subject: {template_subject}. "
                        f"{minimalist_rules}"
                    ),
                    "negative_prompt": (
                        "busy scene, landscape, many objects, detailed narrative, ornate frame, UI frame, "
                        "text, letters, numbers, logo, watermark, realistic photo"
                    ),
                },
            },
        )
        template_target = build_target_spec(target_name, template_target_config, batch_output_config, style_config)
        template_image_config = apply_target_image_settings(image_config, template_target)
        tasks.append(
            BatchIconTask(
                kind="template",
                path_id=path_id,
                path_label=path_label,
                milestone=None,
                choice=None,
                target=template_target,
                image_config=template_image_config,
                prompt_config=prompt_config,
                output_config=batch_output_config,
            )
        )

        motif = str(path_config.get("reward_motif") or path_config.get("motif") or template_subject)
        template_ref = existing_template_reference(batch_output_config, template_target)
        for milestone in milestones_raw:
            for choice in choices_raw:
                task_values = {"path": path_id, "milestone": milestone, "choice": choice}
                asset_name = safe_slug(format_task_template(reward_name_template, task_values))
                variant = str(choice_variants.get(str(choice)) or choice_variants.get(choice) or "")
                reward_target_config = deep_merge(
                    base_target_config,
                    {
                        "asset_name": asset_name,
                        "path": f"{output_dir}/{{name}}.dds",
                        "style_reference_paths": [template_ref],
                        "prompt_requirements": minimalist_rules,
                        "image": {
                            "natural_prompt": (
                                f"{reward_prompt_prefix} {path_label}, milestone {milestone}, option {choice}. "
                                f"Use {motif}. {variant} Keep it only slightly different from the route template. "
                                f"{minimalist_rules}"
                            ),
                            "negative_prompt": (
                                "busy scene, landscape, many objects, detailed narrative, ornate frame, UI frame, "
                                "text, letters, numbers, logo, watermark, realistic photo"
                            ),
                        },
                    },
                )
                reward_target = build_target_spec(target_name, reward_target_config, batch_output_config, style_config)
                reward_image_config = apply_target_image_settings(image_config, reward_target)
                tasks.append(
                    BatchIconTask(
                        kind="reward",
                        path_id=path_id,
                        path_label=path_label,
                        milestone=milestone,
                        choice=choice,
                        target=reward_target,
                        image_config=reward_image_config,
                        prompt_config=prompt_config,
                        output_config=batch_output_config,
                        allow_missing_style_reference_dry_run=True,
                    )
                )
    return tasks


def build_victory_path_icon_batch_tasks(
    config: dict[str, Any],
    output_config: dict[str, Any],
    style_config: dict[str, Any],
    image_config: dict[str, Any],
    prompt_config: dict[str, Any],
) -> list[BatchIconTask]:
    batch_config = victory_path_batch_config(config)
    situation_target_name = "victory_situation_icon"
    path_target_name = "victory_path_icon"
    situation_defaults = target_override(output_config, situation_target_name)
    path_defaults = target_override(output_config, path_target_name)
    situation_base_config = deep_merge(TARGET_PRESETS[situation_target_name], situation_defaults)
    situation_base_config = deep_merge(situation_base_config, require_object(batch_config, "situation_target"))
    path_base_config = deep_merge(TARGET_PRESETS[path_target_name], path_defaults)
    path_base_config = deep_merge(path_base_config, require_object(batch_config, "path_target"))

    paths = load_victory_path_icon_configs(batch_config)
    situation_config = require_object(batch_config, "situation")
    situation_output_dir = str(
        batch_config.get("situation_output_dir")
        or situation_base_config.get("path", TARGET_PRESETS[situation_target_name]["path"]).rsplit("/", 1)[0]
    )
    path_output_dir = str(
        batch_config.get("path_output_dir")
        or path_base_config.get("path", TARGET_PRESETS[path_target_name]["path"]).rsplit("/", 1)[0]
    )
    situation_name_template = str(batch_config.get("situation_name_template") or "tv_victory_situation")
    path_name_template = str(batch_config.get("path_name_template") or "tv_victory_{path}")
    artifact_stem_template = str(batch_config.get("artifact_stem") or "{name}")
    icon_rules = str(
        batch_config.get("icon_rules")
        or (
            "Extreme minimalist EU5 icon: one central symbolic subject, at most 1-2 tiny supporting shapes, "
            "strong silhouette, readable at 128px, no text, no letters, no logo, no UI frame, no complex scene."
        )
    )
    situation_prompt_prefix = str(
        batch_config.get("situation_prompt_prefix")
        or "Create the main situation icon for the Towards Victory system:"
    )
    path_prompt_prefix = str(batch_config.get("path_prompt_prefix") or "Create a route identity icon for:")
    default_theme_colors = [
        "crimson red",
        "leaf green",
        "gold yellow",
        "ivory white",
        "royal purple",
        "azure blue",
    ]
    theme_colors = [
        str(path_config.get("theme_color") or path_config.get("accent_color") or default_theme_colors[index % len(default_theme_colors)])
        for index, path_config in enumerate(paths)
    ]

    batch_output_config = dict(output_config)
    batch_output_config["artifact_stem"] = artifact_stem_template
    tasks: list[BatchIconTask] = []

    situation_name = safe_slug(
        str(situation_config.get("asset_name") or situation_config.get("name") or situation_name_template)
    )
    situation_subject = str(
        situation_config.get("icon_prompt")
        or situation_config.get("prompt")
        or "a six-road victory emblem with a small laurel crown and six tiny route marks"
    )
    situation_refs = parse_path_list(
        situation_config.get(
            "style_reference_paths",
            ["data/generated_icons/_style_refs/construction_center.dds"],
        ),
        f"{VICTORY_PATH_BATCH}.situation.style_reference_paths",
    )
    situation_target_config = deep_merge(
        situation_base_config,
        {
            "asset_name": situation_name,
            "path": f"{situation_output_dir}/{{name}}.dds",
            "style_reference_paths": situation_refs,
            "prompt_requirements": icon_rules,
            "image": {
                "natural_prompt": (
                    f"{situation_prompt_prefix} {situation_subject}. "
                    f"Use six small route accents in the path theme colors: {', '.join(theme_colors)}. "
                    f"{icon_rules}"
                ),
                "negative_prompt": (
                    "busy scene, landscape, many objects, detailed narrative, ornate frame, UI frame, "
                    "text, letters, numbers, logo, watermark, realistic photo"
                ),
            },
        },
    )
    situation_target = build_target_spec(
        situation_target_name,
        situation_target_config,
        batch_output_config,
        style_config,
    )
    tasks.append(
        BatchIconTask(
            kind="situation",
            path_id="situation",
            path_label="Towards Victory",
            milestone=None,
            choice=None,
            target=situation_target,
            image_config=apply_target_image_settings(image_config, situation_target),
            prompt_config=prompt_config,
            output_config=batch_output_config,
        )
    )

    for path_config in paths:
        path_id = str(path_config["id"])
        path_label = str(path_config["label"])
        values = {"path": path_id}
        asset_name = safe_slug(format_task_template(path_name_template, values))
        icon_subject = str(
            path_config.get("icon_prompt")
            or path_config.get("prompt")
            or path_config.get("template_prompt")
            or path_label
        )
        theme_color = str(path_config.get("theme_color") or path_config.get("accent_color") or "distinct route color")
        path_refs = parse_path_list(
            path_config.get("icon_style_reference_paths", path_config.get("style_reference_paths", [])),
            f"{VICTORY_PATH_BATCH}.paths.{path_id}.style_reference_paths",
        )
        path_target_config = deep_merge(
            path_base_config,
            {
                "asset_name": asset_name,
                "path": f"{path_output_dir}/{{name}}.dds",
                "style_reference_paths": path_refs,
                "prompt_requirements": icon_rules,
                "image": {
                    "natural_prompt": (
                        f"{path_prompt_prefix} {path_label}: {icon_subject}. "
                        f"Theme color: {theme_color}. "
                        f"Use that color as the dominant accent, with marble and bronze as support. "
                        f"Make the silhouette unmistakably different from the other victory route icons. {icon_rules}"
                    ),
                    "negative_prompt": (
                        "busy scene, landscape, many objects, detailed narrative, ornate frame, UI frame, "
                        "text, letters, numbers, logo, watermark, realistic photo"
                    ),
                },
            },
        )
        path_target = build_target_spec(path_target_name, path_target_config, batch_output_config, style_config)
        tasks.append(
            BatchIconTask(
                kind="path",
                path_id=path_id,
                path_label=path_label,
                milestone=None,
                choice=None,
                target=path_target,
                image_config=apply_target_image_settings(image_config, path_target),
                prompt_config=prompt_config,
                output_config=batch_output_config,
            )
        )
    return tasks


def resolve_api_key(api_config: dict[str, Any]) -> str:
    configured = str(api_config.get("api_key") or "").strip()
    env_names = api_config.get("api_key_env", ["PACKY_API_KEY", "PACKY_SORA_TOKEN"])
    if isinstance(env_names, str):
        env_names = [env_names]
    if not isinstance(env_names, list) or not all(isinstance(item, str) for item in env_names):
        raise ValueError("api.api_key_env must be a string or a list of strings")

    for name in env_names:
        token = os.environ.get(name, "").strip()
        if token:
            return token
    if configured:
        return configured

    env_hint = ", ".join(env_names)
    raise RuntimeError(
        "Missing API token. Set one of these environment variables "
        f"({env_hint}) or put api.api_key in {LOCAL_CONFIG_PATH.name}."
    )


def load_retry_settings(api_config: dict[str, Any]) -> RetrySettings:
    max_attempts = int(api_config.get("max_attempts", 4))
    initial_delay = float(api_config.get("retry_initial_delay_seconds", 3))
    max_delay = float(api_config.get("retry_max_delay_seconds", 30))
    backoff = float(api_config.get("retry_backoff_multiplier", 2))
    if max_attempts < 1:
        raise ValueError("api.max_attempts must be at least 1")
    if initial_delay < 0:
        raise ValueError("api.retry_initial_delay_seconds cannot be negative")
    if max_delay < initial_delay:
        raise ValueError("api.retry_max_delay_seconds must be >= api.retry_initial_delay_seconds")
    if backoff < 1:
        raise ValueError("api.retry_backoff_multiplier must be >= 1")
    return RetrySettings(
        max_attempts=max_attempts,
        initial_delay_seconds=initial_delay,
        max_delay_seconds=max_delay,
        backoff_multiplier=backoff,
    )


def load_proxy_url(api_config: dict[str, Any]) -> str:
    proxy_url = str(api_config.get("proxy_url") or "").strip()
    if not proxy_url:
        return ""
    if "://" not in proxy_url:
        proxy_url = f"http://{proxy_url}"
    return proxy_url


def build_url_opener(proxy_url: str) -> urllib.request.OpenerDirector:
    if not proxy_url:
        return urllib.request.build_opener()
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
    )


def validate_images_endpoint(endpoint: str, expected_tail: str) -> None:
    normalized = endpoint.strip().rstrip("/")
    if not normalized:
        raise ValueError("api image endpoint must be non-empty")
    unsupported_markers = ("/responses", "/chat/completions", "/completions")
    if any(marker in normalized for marker in unsupported_markers):
        raise ValueError(
            "Packy gpt-image-2 image generation must use the Images API, "
            "not Responses API or Chat Completions API"
        )
    if not normalized.endswith(expected_tail):
        print(f"[warning] endpoint does not end with {expected_tail}: {endpoint}")


def sleep_before_retry(label: str, attempt: int, error: Exception, retry_settings: RetrySettings) -> None:
    delay = min(
        retry_settings.initial_delay_seconds * (retry_settings.backoff_multiplier ** max(attempt - 1, 0)),
        retry_settings.max_delay_seconds,
    )
    print(
        f"[retry] {label} failed on attempt {attempt}/{retry_settings.max_attempts}: "
        f"{error}. Retrying in {delay:.1f}s..."
    )
    if delay > 0:
        time.sleep(delay)


def api_request(
    label: str,
    request: urllib.request.Request,
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> bytes:
    for attempt in range(1, retry_settings.max_attempts + 1):
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                raise RuntimeError(f"{label} failed: HTTP {exc.code}: {error_body}") from exc
            if attempt >= retry_settings.max_attempts:
                raise RuntimeError(f"{label} failed after {attempt} attempts: HTTP {exc.code}: {error_body}") from exc
            sleep_before_retry(label, attempt, exc, retry_settings)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt >= retry_settings.max_attempts:
                raise RuntimeError(f"{label} failed after {attempt} attempts: {exc}") from exc
            sleep_before_retry(label, attempt, exc, retry_settings)
    raise RuntimeError(f"{label} failed without a response")


def api_post_json(
    endpoint: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Accept": "*/*",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TowardsVictoryDDSIconHelper/1.0",
        },
        method="POST",
    )
    response_body = api_request("API JSON request", request, timeout, retry_settings, opener)
    return decode_json_response(response_body, "API JSON request")


def build_multipart_body(fields: dict[str, Any], files: list[UploadFile]) -> tuple[bytes, str]:
    boundary = f"----TowardsVictoryIcon{uuid.uuid4().hex}"
    body = bytearray()

    for key, value in fields.items():
        if value in (None, ""):
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        body.extend(f"--{boundary}\r\n".encode("ascii"))
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        body.extend(str(value).encode("utf-8"))
        body.extend(b"\r\n")

    for upload in files:
        body.extend(f"--{boundary}\r\n".encode("ascii"))
        disposition = (
            f'Content-Disposition: form-data; name="{upload.field_name}"; '
            f'filename="{upload.filename}"\r\n'
        )
        body.extend(disposition.encode("utf-8"))
        body.extend(f"Content-Type: {upload.content_type}\r\n\r\n".encode("ascii"))
        body.extend(upload.data)
        body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode("ascii"))
    return bytes(body), boundary


def api_post_multipart(
    endpoint: str,
    api_key: str,
    fields: dict[str, Any],
    files: list[UploadFile],
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> dict[str, Any]:
    body, boundary = build_multipart_body(fields, files)
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Accept": "*/*",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "TowardsVictoryDDSIconHelper/1.0",
        },
        method="POST",
    )
    response_body = api_request("API multipart request", request, timeout, retry_settings, opener)
    return decode_json_response(response_body, "API multipart request")


def decode_json_response(response_body: bytes, label: str) -> dict[str, Any]:
    try:
        decoded = json.loads(response_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        snippet = response_body[:500].decode("utf-8", errors="replace")
        raise RuntimeError(f"{label} returned non-JSON response: {snippet}") from exc
    if not isinstance(decoded, dict):
        raise RuntimeError(f"{label} returned a non-object JSON response")
    return decoded


def download_bytes(
    url: str,
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "TowardsVictoryDDSIconHelper/1.0"})
    return api_request("image download", request, timeout, retry_settings, opener)


def extract_image_bytes(
    response: dict[str, Any],
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> tuple[bytes, str]:
    data = response.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise RuntimeError("Image API response did not contain data[0]")
    item = data[0]
    revised_prompt = str(item.get("revised_prompt") or "")

    if isinstance(item.get("b64_json"), str):
        encoded = item["b64_json"]
        if encoded.startswith("data:image/") and "," in encoded:
            encoded = encoded.split(",", 1)[1]
        try:
            return base64.b64decode(encoded, validate=False), revised_prompt
        except binascii.Error as exc:
            raise RuntimeError("Image API returned invalid b64_json image data") from exc

    if isinstance(item.get("url"), str):
        return download_bytes(item["url"], timeout, retry_settings, opener), revised_prompt

    raise RuntimeError("Image API response did not contain b64_json or url image data")


def refine_prompt(
    prompt_config: dict[str, Any],
    image_config: dict[str, Any],
    target: TargetSpec,
) -> str:
    prompt = str(image_config.get("prompt") or image_config.get("natural_prompt") or "").strip()
    if not prompt:
        raise ValueError("image.prompt or image.natural_prompt must be set")

    if not bool(prompt_config.get("enabled", False)):
        return prompt

    style_rules = str(prompt_config.get("style_rules") or "").strip()
    composition_rules = str(prompt_config.get("composition_rules") or "").strip()
    negative_prompt = str(image_config.get("negative_prompt") or "").strip()

    parts = [
        f"Create a Europa Universalis V {target.label} DDS asset.",
        f"Subject: {prompt}",
        "Reference image: use the uploaded target-specific reference image only as style guidance for palette, brushwork, lighting, surface treatment, and framing discipline. Do not copy its subject, exact composition, silhouette, ornament placement, or any text.",
        "Distinctiveness: keep the result in the same visual family as the reference, but make it visibly different at a glance through changed shape language, object arrangement, cropping, or decorative accents.",
        "Composition: keep the main subject centered, readable, and high-contrast, with no watermark, no letters, no logo, and no UI chrome baked into the art.",
        f"Target format: final DDS target is exactly {target.width}x{target.height} and must stay under {format_bytes(target.max_file_size_bytes)}.",
        f"Target-specific requirement: {target.prompt_requirements}",
    ]
    if style_rules:
        parts.extend(["Style rules:", style_rules])
    if composition_rules:
        parts.extend(["Extra composition rules:", composition_rules])
    if negative_prompt:
        parts.extend(["Avoid:", negative_prompt])
    return "\n".join(parts)


def build_generation_payload(image_config: dict[str, Any], final_prompt: str) -> dict[str, Any]:
    payload = {
        "model": image_config.get("model", "gpt-image-2"),
        "prompt": final_prompt,
        "size": image_config.get("size", "1024x1024"),
        "quality": image_config.get("quality", "high"),
        "output_format": image_config.get("output_format", "png"),
        "n": image_config.get("n", 1),
        "response_format": image_config.get("response_format", "url"),
    }
    optional_keys = ("background", "moderation", "user", "output_compression", "response_format")
    for key in optional_keys:
        if key in image_config and image_config[key] not in (None, ""):
            payload[key] = image_config[key]

    if not isinstance(payload["prompt"], str) or not payload["prompt"].strip():
        raise ValueError("image prompt must be non-empty")
    if payload["model"] != "gpt-image-2":
        raise ValueError("image.model must be gpt-image-2 for Packyapi")
    if payload["n"] != 1:
        raise ValueError("Packy gpt-image-2 only supports image.n = 1")
    if payload["output_format"] != "png":
        raise ValueError("This helper expects image.output_format = png")
    if payload["response_format"] not in {"url", "b64_json"}:
        raise ValueError("image.response_format must be url or b64_json")
    if payload["quality"] not in {"low", "medium", "high", "auto"}:
        raise ValueError("image.quality must be low, medium, high, or auto")
    if payload.get("background") == "transparent":
        raise ValueError("Packy gpt-image-2 does not support transparent background")
    if image_config.get("stream"):
        raise ValueError("Packy gpt-image-2 does not support image.stream")
    if "partial_images" in image_config:
        raise ValueError("Packy gpt-image-2 does not support image.partial_images")
    if "style" in image_config:
        raise ValueError("Packy gpt-image-2 does not need the legacy image.style parameter")
    if "output_compression" in payload:
        compression = int(payload["output_compression"])
        if compression < 0 or compression > 100:
            raise ValueError("image.output_compression must be between 0 and 100")
        payload["output_compression"] = compression
    if str(payload["size"]) != "auto":
        parse_size(str(payload["size"]))
    return payload


def collect_style_references(
    style_config: dict[str, Any],
    target: TargetSpec,
    dry_run: bool,
    allow_missing_dry_run: bool = False,
) -> list[UploadFile]:
    paths = list(target.style_reference_paths)
    if not paths:
        raise ValueError(
            f"{target.name} requires at least one target-specific DDS/PNG style reference. "
            "Set output.targets.<target>.style_reference_paths or style_reference.paths_by_target."
        )

    ref_dir = resolve_repo_path(style_config.get("temporary_png_dir"), DEFAULT_REF_DIR)
    upload_field = str(style_config.get("upload_field_name") or DEFAULT_STYLE_UPLOAD_FIELD)
    if upload_field != DEFAULT_STYLE_UPLOAD_FIELD:
        raise ValueError('Packy image edits require style_reference.upload_field_name = "image"')
    if bool(style_config.get("write_converted_pngs", True)) and not dry_run:
        ref_dir.mkdir(parents=True, exist_ok=True)
    uploads: list[UploadFile] = []
    for index, raw_path in enumerate(paths, start=1):
        path = resolve_repo_path(raw_path)
        if not path.exists():
            if dry_run and allow_missing_dry_run:
                print(f"[style] planned future reference: {display_path(path)}")
                continue
            raise FileNotFoundError(f"Missing style reference: {path}")
        image = read_image_rgba(path)
        png_bytes = encode_png_rgba(image)
        png_name = f"{index:02d}_{target.name}_{safe_slug(path.stem)}.png"
        if bool(style_config.get("write_converted_pngs", True)) and not dry_run:
            (ref_dir / png_name).write_bytes(png_bytes)
            print(f"[style] converted {display_path(path)} -> {display_path(ref_dir / png_name)}")
        else:
            print(f"[style] converted {display_path(path)} for upload")
        uploads.append(
            UploadFile(
                field_name=upload_field,
                filename=png_name,
                content_type="image/png",
                data=png_bytes,
            )
        )
    return uploads


def call_image_api(
    api_config: dict[str, Any],
    style_config: dict[str, Any],
    payload: dict[str, Any],
    style_uploads: list[UploadFile],
    api_key: str,
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> dict[str, Any]:
    if style_uploads:
        image_payload = dict(payload)
        image_payload["input_fidelity"] = str(style_config.get("input_fidelity") or "high")
        endpoint = str(api_config.get("edits_endpoint") or api_config.get("endpoint") or DEFAULT_EDITS_ENDPOINT)
        validate_images_endpoint(endpoint, "/v1/images/edits")
        print(f"[request] POST {endpoint}")
        print(f"[request] model={image_payload['model']} size={image_payload['size']} quality={image_payload['quality']} references={len(style_uploads)}")
        return api_post_multipart(endpoint, api_key, image_payload, style_uploads, timeout, retry_settings, opener)

    endpoint = str(api_config.get("generations_endpoint") or api_config.get("endpoint") or DEFAULT_GENERATIONS_ENDPOINT)
    validate_images_endpoint(endpoint, "/v1/images/generations")
    print(f"[request] POST {endpoint}")
    print(f"[request] model={payload['model']} size={payload['size']} quality={payload['quality']} references=0")
    return api_post_json(endpoint, api_key, payload, timeout, retry_settings, opener)


def output_asset_name(output_config: dict[str, Any], target: TargetSpec | None = None) -> str:
    if target is not None:
        return target.asset_name
    return safe_slug(str(output_config.get("name") or "generated_icon"))


def output_artifact_stem(output_config: dict[str, Any], target: TargetSpec) -> str:
    asset_name = output_asset_name(output_config, target)
    template = str(output_config.get("artifact_stem") or "{name}_{target}")
    return safe_slug(expand_template(template, asset_name, target.name), default=asset_name)


def clamp_channel(value: float) -> int:
    return max(0, min(255, int(round(value))))


def blend_pixel(
    rgba: bytearray,
    width: int,
    height: int,
    x: int,
    y: int,
    color: tuple[int, int, int, int],
) -> None:
    if x < 0 or y < 0 or x >= width or y >= height:
        return
    src_a = color[3] / 255.0
    if src_a <= 0:
        return
    pos = (y * width + x) * 4
    dst_a = rgba[pos + 3] / 255.0
    out_a = src_a + dst_a * (1.0 - src_a)
    if out_a <= 0:
        return
    for channel in range(3):
        src = color[channel] / 255.0
        dst = rgba[pos + channel] / 255.0
        out = (src * src_a + dst * dst_a * (1.0 - src_a)) / out_a
        rgba[pos + channel] = clamp_channel(out * 255.0)
    rgba[pos + 3] = clamp_channel(out_a * 255.0)


def draw_rect(
    rgba: bytearray,
    width: int,
    height: int,
    left: int,
    top: int,
    right: int,
    bottom: int,
    color: tuple[int, int, int, int],
) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            blend_pixel(rgba, width, height, x, y, color)


def draw_line(
    rgba: bytearray,
    width: int,
    height: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int, int],
    thickness: int = 1,
) -> None:
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    radius = max(0, thickness // 2)
    for step in range(steps + 1):
        t = step / steps
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        for oy in range(-radius, radius + 1):
            for ox in range(-radius, radius + 1):
                if ox * ox + oy * oy <= radius * radius + 1:
                    blend_pixel(rgba, width, height, x + ox, y + oy, color)


def draw_circle_outline(
    rgba: bytearray,
    width: int,
    height: int,
    cx: int,
    cy: int,
    radius: int,
    color: tuple[int, int, int, int],
    thickness: int = 1,
) -> None:
    inner = max(0, radius - thickness)
    outer_sq = radius * radius
    inner_sq = inner * inner
    for y in range(cy - radius - 1, cy + radius + 2):
        for x in range(cx - radius - 1, cx + radius + 2):
            dist_sq = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if inner_sq <= dist_sq <= outer_sq:
                blend_pixel(rgba, width, height, x, y, color)


def draw_polyline(
    rgba: bytearray,
    width: int,
    height: int,
    points: list[tuple[int, int]],
    color: tuple[int, int, int, int],
    thickness: int = 1,
) -> None:
    for start, end in zip(points, points[1:]):
        draw_line(rgba, width, height, start[0], start[1], end[0], end[1], color, thickness)


def color_grade_wonder_worksite(image: RgbaImage) -> RgbaImage:
    rgba = bytearray(image.rgba)
    for pos in range(0, len(rgba), 4):
        alpha = rgba[pos + 3]
        if alpha == 0:
            continue
        x = (pos // 4) % image.width
        y = (pos // 4) // image.width
        red, green, blue = rgba[pos], rgba[pos + 1], rgba[pos + 2]
        brightness = (red + green + blue) / 3.0

        red = (red - 128) * 1.08 + 128
        green = (green - 128) * 1.06 + 128
        blue = (blue - 128) * 1.08 + 128

        if abs(red - green) < 20 and abs(green - blue) < 20:
            red = red * 0.96 + 18
            green = green * 0.98 + 16
            blue = blue * 1.04 + 24
        elif red > green + 8 and green > blue + 6:
            red = red * 1.15 + 16
            green = green * 1.08 + 12
            blue = blue * 0.72 + 6

        if y > image.height * 0.46 and red > blue + 12:
            red = red * 1.18 + 18
            green = green * 1.12 + 16
            blue = blue * 0.70 + 4

        if brightness > 160:
            red += 8
            green += 7
            blue += 5

        if 22 <= x <= 100 and 30 <= y <= 102:
            red += 4
            green += 3

        rgba[pos] = clamp_channel(red)
        rgba[pos + 1] = clamp_channel(green)
        rgba[pos + 2] = clamp_channel(blue)
    return RgbaImage(image.width, image.height, bytes(rgba))


def render_wonder_worksite_icon(source: RgbaImage) -> RgbaImage:
    image = color_grade_wonder_worksite(source)
    rgba = bytearray(image.rgba)
    width, height = image.width, image.height

    marble = (218, 210, 191, 215)
    marble_shadow = (124, 116, 104, 165)
    marble_highlight = (247, 239, 218, 190)
    bronze = (197, 132, 52, 210)
    gold = (235, 185, 78, 215)
    dark_gold = (99, 65, 30, 205)

    draw_rect(rgba, width, height, 21, 108, 107, 119, marble)
    draw_line(rgba, width, height, 21, 108, 107, 108, marble_highlight, 1)
    draw_line(rgba, width, height, 21, 119, 107, 119, marble_shadow, 1)
    draw_line(rgba, width, height, 31, 113, 92, 113, gold, 1)
    draw_line(rgba, width, height, 44, 109, 39, 118, (152, 146, 134, 105), 1)

    draw_line(rgba, width, height, 12, 47, 54, 28, gold, 1)
    draw_line(rgba, width, height, 54, 28, 96, 48, gold, 1)
    draw_line(rgba, width, height, 27, 70, 88, 70, (220, 158, 69, 150), 1)

    draw_line(rgba, width, height, 75, 103, 107, 60, bronze, 2)
    draw_line(rgba, width, height, 75, 103, 108, 103, bronze, 1)
    draw_circle_outline(rgba, width, height, 100, 85, 17, gold, 2)
    for angle in range(0, 360, 90):
        radians = math.radians(angle)
        x = 100 + int(round(math.cos(radians) * 15))
        y = 85 + int(round(math.sin(radians) * 15))
        draw_line(rgba, width, height, 100, 85, x, y, bronze, 1)
    draw_circle_outline(rgba, width, height, 100, 85, 4, dark_gold, 1)

    return RgbaImage(width, height, bytes(rgba))


def render_local_template_image(target: TargetSpec) -> tuple[RgbaImage, Path, str]:
    config = target.local_template
    source_path = resolve_repo_path(
        config.get("source_path") or (target.style_reference_paths[0] if target.style_reference_paths else None)
    )
    if not source_path.exists():
        raise FileNotFoundError(f"Missing local template source: {source_path}")

    source = resize_rgba(read_image_rgba(source_path), target.width, target.height, target.resize)
    mode = str(config.get("mode") or "wonder_worksite").strip().lower()
    if mode != "wonder_worksite":
        raise ValueError(f"Unsupported local_template.mode {mode!r}; expected wonder_worksite")
    return render_wonder_worksite_icon(source), source_path, mode


def write_rgba_png(output_config: dict[str, Any], image: RgbaImage, target: TargetSpec) -> Path:
    png_dir = resolve_repo_path(output_config.get("png_dir"), DEFAULT_PNG_DIR)
    png_path = png_dir / f"{output_artifact_stem(output_config, target)}.png"
    if png_path.exists() and not bool(output_config.get("overwrite", False)):
        print(f"[png] refreshing intermediate {display_path(png_path)} because DDS target is missing")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.write_bytes(encode_png_rgba(image))
    print(f"[png] {display_path(png_path)}")
    return png_path


def write_local_template_png(output_config: dict[str, Any], image: RgbaImage, target: TargetSpec) -> Path:
    return write_rgba_png(output_config, prepare_target_image(image, target), target)


def write_local_template_metadata(
    output_config: dict[str, Any],
    target: TargetSpec,
    source_path: Path,
    mode: str,
    written_target: dict[str, Any],
) -> None:
    if not bool(output_config.get("write_metadata", True)):
        return
    metadata_dir = resolve_repo_path(output_config.get("metadata_dir"), DEFAULT_PNG_DIR)
    metadata_path = metadata_dir / f"{output_artifact_stem(output_config, target)}.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "generation_target": target.name,
        "generator": "local_template",
        "local_template": {
            "mode": mode,
            "source_path": display_path(source_path).replace("\\", "/"),
        },
        "final_prompt": target.image_overrides.get("natural_prompt") or target.image_overrides.get("prompt") or "",
        "targets": [written_target],
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[metadata] {display_path(metadata_path)}")


def write_generated_png(png_bytes: bytes, output_config: dict[str, Any], target: TargetSpec) -> Path:
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise RuntimeError("Generated image payload is not a PNG")
    if target.circle_crop:
        source_image = decode_png_rgba(png_bytes)
        return write_rgba_png(output_config, prepare_target_image(source_image, target), target)
    png_dir = resolve_repo_path(output_config.get("png_dir"), DEFAULT_PNG_DIR)
    png_path = png_dir / f"{output_artifact_stem(output_config, target)}.png"
    if png_path.exists() and not bool(output_config.get("overwrite", False)):
        print(f"[png] refreshing intermediate {display_path(png_path)} because DDS target is missing")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.write_bytes(png_bytes)
    print(f"[png] {display_path(png_path)}")
    return png_path


def write_target(
    output_config: dict[str, Any],
    source_png_path: Path,
    target: TargetSpec,
    *,
    source_is_prepared: bool = False,
) -> dict[str, Any]:
    overwrite = bool(output_config.get("overwrite", False))
    if target.path.exists() and not overwrite:
        file_size = target.path.stat().st_size
        print(f"[skip] {display_path(target.path)} exists; output.overwrite is false")
        return {
            "name": target.name,
            "label": target.label,
            "path": display_path(target.path).replace("\\", "/"),
            "width": target.width,
            "height": target.height,
            "resize": target.resize,
            "dds_format": target.dds_format,
            "dds_levels": None,
            "circle_crop": target.circle_crop,
            "circle_crop_feather_px": target.circle_crop_feather_px,
            "file_size_bytes": file_size,
            "max_file_size_bytes": target.max_file_size_bytes,
            "skipped": True,
        }
    source_image = read_image_rgba(source_png_path)
    if source_is_prepared and (source_image.width, source_image.height) == (target.width, target.height):
        target_image = source_image
    else:
        target_image = prepare_target_image(source_image, target)
    dds_levels = write_dds(
        target_image,
        target.path,
        dds_format=target.dds_format,
        overwrite=overwrite,
        opaque_background=target.opaque_background,
        mipmaps=target.mipmaps,
        mipmap_min_dimension=target.mipmap_min_dimension,
    )
    file_size = target.path.stat().st_size
    if file_size > target.max_file_size_bytes:
        raise RuntimeError(
            f"{target.name} output is {format_bytes(file_size)}, above the "
            f"{format_bytes(target.max_file_size_bytes)} limit: {target.path}"
        )
    print(
        f"[dds] {display_path(target.path)} "
        f"({target.width}x{target.height} {target.dds_format}, resize={target.resize}, "
        f"levels={dds_levels}, {format_bytes(file_size)} <= {format_bytes(target.max_file_size_bytes)})"
    )
    return {
        "name": target.name,
        "label": target.label,
        "path": display_path(target.path).replace("\\", "/"),
        "width": target.width,
        "height": target.height,
        "resize": target.resize,
        "dds_format": target.dds_format,
        "dds_levels": dds_levels,
        "circle_crop": target.circle_crop,
        "circle_crop_feather_px": target.circle_crop_feather_px,
        "file_size_bytes": file_size,
        "max_file_size_bytes": target.max_file_size_bytes,
    }


def update_existing_metadata_target(
    output_config: dict[str, Any],
    target: TargetSpec,
    written_target: dict[str, Any],
) -> None:
    if not bool(output_config.get("write_metadata", True)):
        return
    metadata_dir = resolve_repo_path(output_config.get("metadata_dir"), DEFAULT_PNG_DIR)
    metadata_path = metadata_dir / f"{output_artifact_stem(output_config, target)}.json"
    if not metadata_path.exists():
        return
    metadata = load_json_object(metadata_path)
    targets = metadata.get("targets")
    if not isinstance(targets, list):
        metadata["targets"] = [written_target]
    else:
        for index, existing in enumerate(targets):
            if isinstance(existing, dict) and existing.get("name") == target.name:
                targets[index] = written_target
                break
        else:
            targets.append(written_target)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[metadata] updated {display_path(metadata_path)}")


def write_metadata(
    output_config: dict[str, Any],
    target: TargetSpec,
    image_payload: dict[str, Any],
    image_response: dict[str, Any],
    final_prompt: str,
    revised_prompt: str,
    written_targets: list[dict[str, Any]],
) -> None:
    if not bool(output_config.get("write_metadata", True)):
        return
    metadata_dir = resolve_repo_path(output_config.get("metadata_dir"), DEFAULT_PNG_DIR)
    metadata_path = metadata_dir / f"{output_artifact_stem(output_config, target)}.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "generation_target": target.name,
        "payload": image_payload,
        "created": image_response.get("created"),
        "final_prompt": final_prompt,
        "revised_prompt": revised_prompt,
        "targets": written_targets,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[metadata] {display_path(metadata_path)}")


def should_skip_existing(output_config: dict[str, Any], target: TargetSpec) -> bool:
    return target.path.exists() and not bool(output_config.get("overwrite", False))


def print_target_summary(target: TargetSpec) -> None:
    print(
        f"[target] {target.name}: {target.width}x{target.height}, "
        f"request_size={target.image_size}, max={format_bytes(target.max_file_size_bytes)}"
    )
    print(f"[target] output={display_path(target.path)}")


def run_target_generation(
    args: argparse.Namespace,
    api_config: dict[str, Any],
    prompt_config: dict[str, Any],
    image_config: dict[str, Any],
    style_config: dict[str, Any],
    output_config: dict[str, Any],
    target: TargetSpec,
    *,
    allow_missing_style_reference_dry_run: bool = False,
) -> dict[str, Any] | None:
    print_target_summary(target)

    if should_skip_existing(output_config, target):
        print(f"[skip] {display_path(target.path)} exists; output.overwrite is false")
        return {
            "name": target.name,
            "label": target.label,
            "path": display_path(target.path).replace("\\", "/"),
            "width": target.width,
            "height": target.height,
            "resize": target.resize,
            "dds_format": target.dds_format,
            "dds_levels": None,
            "circle_crop": target.circle_crop,
            "circle_crop_feather_px": target.circle_crop_feather_px,
            "file_size_bytes": target.path.stat().st_size,
            "max_file_size_bytes": target.max_file_size_bytes,
            "skipped": True,
        }

    if args.convert_existing_png:
        source_png_path = resolve_repo_path(args.convert_existing_png)
        if not source_png_path.exists():
            raise FileNotFoundError(f"Missing source PNG: {source_png_path}")
        print(f"[png] source={display_path(source_png_path)}")
        written_target = write_target(output_config, source_png_path, target)
        update_existing_metadata_target(output_config, target, written_target)
        return written_target

    if bool(target.local_template.get("enabled", False)) and not bool(args.force_api):
        local_image, source_path, mode = render_local_template_image(target)
        print(f"[local-template] mode={mode} source={display_path(source_path)}")
        png_path = write_local_template_png(output_config, local_image, target)
        written_target = write_target(output_config, png_path, target, source_is_prepared=True)
        write_local_template_metadata(output_config, target, source_path, mode, written_target)
        return written_target

    timeout = float(api_config.get("timeout_seconds", 180))
    retry_settings = load_retry_settings(api_config)
    proxy_url = load_proxy_url(api_config)
    opener = build_url_opener(proxy_url)
    if proxy_url:
        print(f"[network] proxy={proxy_url}")
    style_uploads = collect_style_references(
        style_config,
        target,
        dry_run=bool(args.dry_run),
        allow_missing_dry_run=allow_missing_style_reference_dry_run,
    )

    final_prompt = refine_prompt(prompt_config, image_config, target)
    print("[prompt] final prompt:")
    print(final_prompt)

    image_payload = build_generation_payload(image_config, final_prompt)
    if args.dry_run:
        print("[dry-run] payload:")
        print(json.dumps(image_payload, ensure_ascii=False, indent=2))
        print("[dry-run] skipped API request and output writes")
        return None

    api_key = resolve_api_key(api_config)
    image_response = call_image_api(
        api_config,
        style_config,
        image_payload,
        style_uploads,
        api_key,
        timeout,
        retry_settings,
        opener,
    )
    png_bytes, revised_prompt = extract_image_bytes(image_response, timeout, retry_settings, opener)
    png_path = write_generated_png(png_bytes, output_config, target)
    written_target = write_target(output_config, png_path, target, source_is_prepared=True)
    write_metadata(output_config, target, image_payload, image_response, final_prompt, revised_prompt, [written_target])
    if not bool(output_config.get("keep_png", True)):
        png_path.unlink(missing_ok=True)
        print("[png] removed because output.keep_png is false")

    if revised_prompt:
        print(f"[revised_prompt] {revised_prompt}")
    return written_target


def run_victory_reward_batch(
    args: argparse.Namespace,
    config: dict[str, Any],
    api_config: dict[str, Any],
    prompt_config: dict[str, Any],
    image_config: dict[str, Any],
    style_config: dict[str, Any],
    output_config: dict[str, Any],
) -> int:
    if args.convert_existing_png:
        raise ValueError("--convert-existing-png is only supported for a single selected target")
    tasks = build_victory_batch_tasks(config, output_config, style_config, image_config, prompt_config)
    template_count = sum(1 for task in tasks if task.kind == "template")
    reward_count = sum(1 for task in tasks if task.kind == "reward")
    print(f"[batch] {VICTORY_REWARD_BATCH}: templates={template_count}, rewards={reward_count}, total={len(tasks)}")
    for index, task in enumerate(tasks, start=1):
        if task.kind == "template":
            print(f"[batch] {index}/{len(tasks)} template path={task.path_id}")
        else:
            print(
                f"[batch] {index}/{len(tasks)} reward path={task.path_id} "
                f"m{task.milestone} option={task.choice}"
            )
        run_target_generation(
            args,
            api_config,
            task.prompt_config,
            task.image_config,
            style_config,
            task.output_config,
            task.target,
            allow_missing_style_reference_dry_run=task.allow_missing_style_reference_dry_run,
        )
    return 0


def run_victory_path_icon_batch(
    args: argparse.Namespace,
    config: dict[str, Any],
    api_config: dict[str, Any],
    prompt_config: dict[str, Any],
    image_config: dict[str, Any],
    style_config: dict[str, Any],
    output_config: dict[str, Any],
) -> int:
    if args.convert_existing_png:
        raise ValueError("--convert-existing-png is only supported for a single selected target")
    tasks = build_victory_path_icon_batch_tasks(config, output_config, style_config, image_config, prompt_config)
    situation_count = sum(1 for task in tasks if task.kind == "situation")
    path_count = sum(1 for task in tasks if task.kind == "path")
    print(f"[batch] {VICTORY_PATH_BATCH}: situation={situation_count}, paths={path_count}, total={len(tasks)}")
    for index, task in enumerate(tasks, start=1):
        if task.kind == "situation":
            print(f"[batch] {index}/{len(tasks)} situation icon")
        else:
            print(f"[batch] {index}/{len(tasks)} path icon path={task.path_id}")
        run_target_generation(
            args,
            api_config,
            task.prompt_config,
            task.image_config,
            style_config,
            task.output_config,
            task.target,
            allow_missing_style_reference_dry_run=task.allow_missing_style_reference_dry_run,
        )
    return 0


def run_wonder_building_icon_batch(
    args: argparse.Namespace,
    config: dict[str, Any],
    api_config: dict[str, Any],
    prompt_config: dict[str, Any],
    image_config: dict[str, Any],
    style_config: dict[str, Any],
    output_config: dict[str, Any],
) -> int:
    if args.convert_existing_png:
        raise ValueError("--convert-existing-png is only supported for a single selected target")
    tasks = build_wonder_building_icon_batch_tasks(
        config,
        output_config,
        style_config,
        image_config,
        prompt_config,
    )
    generic_count = sum(1 for task in tasks if task.kind == "generic_wonder_building")
    unique_count = sum(1 for task in tasks if task.kind == "unique_wonder_building")
    print(
        f"[batch] {WONDER_BUILDING_BATCH}: generic={generic_count}, "
        f"unique={unique_count}, total={len(tasks)}"
    )
    for index, task in enumerate(tasks, start=1):
        print(f"[batch] {index}/{len(tasks)} wonder building icon {task.path_id} ({task.path_label})")
        run_target_generation(
            args,
            api_config,
            task.prompt_config,
            task.image_config,
            style_config,
            task.output_config,
            task.target,
            allow_missing_style_reference_dry_run=task.allow_missing_style_reference_dry_run,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.list_targets:
        for name, preset in TARGET_PRESETS.items():
            print(
                f"{name}: {preset['label']} "
                f"({preset['width']}x{preset['height']}, <= {format_bytes(int(preset['max_file_size_bytes']))})"
            )
        for name in sorted(BATCH_TARGETS):
            print(f"{name}: batch mode")
        return 0

    config = load_config()
    api_config = require_object(config, "api")
    prompt_config = require_object(config, "prompt_refinement")
    image_config = require_object(config, "image")
    style_config = require_object(config, "style_reference")
    output_config = require_object(config, "output")
    selected_target = select_target_name(config, output_config, args.target)
    if selected_target == VICTORY_PATH_BATCH:
        return run_victory_path_icon_batch(
            args,
            config,
            api_config,
            prompt_config,
            image_config,
            style_config,
            output_config,
        )
    if selected_target == VICTORY_REWARD_BATCH:
        return run_victory_reward_batch(
            args,
            config,
            api_config,
            prompt_config,
            image_config,
            style_config,
            output_config,
        )
    if selected_target == WONDER_BUILDING_BATCH:
        return run_wonder_building_icon_batch(
            args,
            config,
            api_config,
            prompt_config,
            image_config,
            style_config,
            output_config,
        )
    target = load_target_spec(config, output_config, style_config, args.target)
    image_config = apply_target_image_settings(image_config, target)
    run_target_generation(
        args,
        api_config,
        prompt_config,
        image_config,
        style_config,
        output_config,
        target,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - command-line helper should fail tersely.
        print(f"[error] {exc}", file=sys.stderr)
        if os.environ.get("TV_ICON_IMAGE_DEBUG"):
            raise
        raise SystemExit(1) from None
