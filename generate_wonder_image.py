#!/usr/bin/env python3
"""
Generate Towards Victory wonder image assets through Packy gpt-image-2.

Usage:
  1. Edit data/wonder_image_prompts.yaml for generic prompts and data/unique_wonders.yaml for unique prompts.
  2. Set PACKY_API_KEY, or put api.api_key in generate_wonder_image.local.json.
  3. Use generate_wonder_image_config.json only for selection, task_overrides, and runtime defaults; then run: python generate_wonder_image.py

The script reads a batch of image tasks from the JSON config, skips tasks whose
output already exists when overwrite is false, and writes generated PNGs as
single-level DXT1 DDS files without requiring ImageMagick, texconv, Pillow, or
other third-party packages.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import concurrent.futures
import json
import os
import re
import struct
import sys
import time
import urllib.error
import urllib.request
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
CONFIG_PATH = REPO_ROOT / "generate_wonder_image_config.json"
LOCAL_CONFIG_PATH = REPO_ROOT / "generate_wonder_image.local.json"
DEFAULT_ENDPOINT = "https://www.packyapi.com/v1/images/generations"
DEFAULT_WONDERS_DIR = (
    REPO_ROOT
    / "src"
    / "main_menu"
    / "gfx"
    / "interface"
    / "icons"
    / "towards_victory"
    / "wonders"
)
DEFAULT_PNG_DIR = REPO_ROOT / "data" / "generated_wonders"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

from wonder_mechanics.io import load_wonder_image_tasks
from dds_image_lib import RgbaImage, write_dds  # noqa: E402
from wonder_image_crop_lib import (  # noqa: E402
    cropped_wonder_dds_path,
    empty_crop_data,
    load_crop_data,
    write_wonder_dds_from_image,
    write_wonder_dds_from_source,
)


@dataclass(frozen=True)
class DecodedPng:
    width: int
    height: int
    rgb: bytes


@dataclass(frozen=True)
class RetrySettings:
    max_attempts: int
    initial_delay_seconds: float
    max_delay_seconds: float
    backoff_multiplier: float


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


def resolve_repo_path(value: str | None, default_path: Path) -> Path:
    if not value:
        return default_path
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def pretty_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def require_object(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be a JSON object")
    return value


def require_list(config: dict[str, Any], key: str) -> list[Any]:
    value = config.get(key, [])
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a JSON array")
    return value


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or rebuild Towards Victory wonder image DDS assets.")
    parser.add_argument(
        "--convert-existing-assets",
        action="store_true",
        help="Rebuild selected DDS files from existing PNGs, falling back to existing DDS files, without calling the API.",
    )
    return parser.parse_args(argv)


def normalize_task_key(value: str) -> str:
    token = str(value).strip().lower()
    token = token.replace("\\", "/").rsplit("/", 1)[-1]
    token = re.sub(r"\.dds$", "", token, flags=re.IGNORECASE)
    if token.startswith("tv_wonder_"):
        token = token[len("tv_wonder_") :]
    return token


def parse_size(size: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", str(size).strip())
    if not match:
        raise ValueError(f"Invalid image size {size!r}; expected WIDTHxHEIGHT")
    width, height = int(match.group(1)), int(match.group(2))
    if width <= 0 or height <= 0:
        raise ValueError("Image size must be positive")
    if width % 16 or height % 16:
        raise ValueError("Packy gpt-image-2 sizes must be multiples of 16")
    if max(width, height) > 3840:
        raise ValueError("Packy gpt-image-2 maximum side length is 3840")
    if max(width, height) / min(width, height) > 3:
        raise ValueError("Packy gpt-image-2 aspect ratio cannot exceed 3:1")
    pixels = width * height
    if pixels < 655_360 or pixels > 8_294_400:
        raise ValueError("Packy gpt-image-2 total pixels must be 655360..8294400")
    return width, height


def resolve_api_key(api_config: dict[str, Any]) -> str:
    configured = str(api_config.get("api_key") or "").strip()
    env_names = api_config.get("api_key_env", "PACKY_API_KEY")
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
        "Missing Packy API token. Set one of these environment variables "
        f"({env_hint}) or put api.api_key in {LOCAL_CONFIG_PATH.name}."
    )


def build_payload(image_config: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "model": image_config.get("model", "gpt-image-2"),
        "prompt": image_config.get("prompt", ""),
        "size": image_config.get("size", "1536x1024"),
        "quality": image_config.get("quality", "high"),
        "output_format": image_config.get("output_format", "png"),
        "response_format": image_config.get("response_format", "b64_json"),
        "n": image_config.get("n", 1),
    }

    optional_keys = ("background", "moderation", "user", "output_compression")
    for key in optional_keys:
        if key in image_config and image_config[key] not in (None, ""):
            payload[key] = image_config[key]

    if payload["model"] != "gpt-image-2":
        raise ValueError("image.model must be gpt-image-2")
    if not isinstance(payload["prompt"], str) or not payload["prompt"].strip():
        raise ValueError("image.prompt must be a non-empty string")
    if payload["n"] != 1:
        raise ValueError("Packy gpt-image-2 only supports image.n = 1")
    if payload["output_format"] != "png":
        raise ValueError("This helper expects image.output_format = png")
    if payload["response_format"] not in {"b64_json", "url"}:
        raise ValueError("image.response_format must be b64_json or url")
    if payload["quality"] not in {"low", "medium", "high", "auto"}:
        raise ValueError("image.quality must be low, medium, high, or auto")

    parse_size(str(payload["size"]))
    return payload


def load_task_config(config: dict[str, Any]) -> list[dict[str, Any]]:
    defaults = require_object(config, "defaults") if "defaults" in config else {}
    if "images" in config or "image" in config or "output" in config:
        raise ValueError(
            "generate_wonder_image_config.json no longer owns image prompts; "
            "put prompts in data/wonder_image_prompts.yaml and use selection/task_overrides instead"
        )

    selection = require_object(config, "selection") if "selection" in config else {}
    task_overrides = require_object(config, "task_overrides") if "task_overrides" in config else {}
    include_unique = bool(selection.get("include_unique", True))
    include_generic = bool(selection.get("include_generic", True))
    only_keys = {
        normalize_task_key(item)
        for item in require_list(selection, "only_keys")
    } if "only_keys" in selection else set()
    exclude_keys = {
        normalize_task_key(item)
        for item in require_list(selection, "exclude_keys")
    } if "exclude_keys" in selection else set()
    default_enabled = bool(selection.get("enabled", True))
    default_overwrite = bool(selection.get("overwrite", False))

    tasks: list[dict[str, Any]] = []
    for task in load_wonder_image_tasks(include_unique=include_unique):
        is_stage = bool(task.get("is_stage", False))
        if not is_stage:
            if task["is_unique"] and not include_unique:
                continue
            if not task["is_unique"] and not include_generic:
                continue

        normalized_key = normalize_task_key(task["key"])
        normalized_name = normalize_task_key(task["name"])
        if only_keys and normalized_key not in only_keys and normalized_name not in only_keys:
            continue
        if normalized_key in exclude_keys or normalized_name in exclude_keys:
            continue

        merged_task = deep_merge(
            defaults,
            {
                "name": task["name"],
                "prompt": task["prompt"],
                "enabled": default_enabled,
                "overwrite": default_overwrite,
            },
        )
        override = task_overrides.get(task["key"]) or task_overrides.get(normalized_key) or task_overrides.get(task["name"])
        if override is not None:
            if not isinstance(override, dict):
                raise ValueError(f"task_overrides[{task['key']}] must be a JSON object")
            merged_task = deep_merge(merged_task, override)
        merged_task["key"] = task["key"]
        merged_task["is_unique"] = task["is_unique"]
        merged_task["is_stage"] = is_stage
        tasks.append(merged_task)

    if not tasks:
        raise ValueError("selection produced no image tasks")
    return tasks


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
        urllib.request.ProxyHandler(
            {
                "http": proxy_url,
                "https": proxy_url,
            }
        )
    )


def sleep_before_retry(label: str, attempt: int, error: Exception, retry_settings: RetrySettings) -> None:
    delay = min(
        retry_settings.initial_delay_seconds
        * (retry_settings.backoff_multiplier ** max(attempt - 1, 0)),
        retry_settings.max_delay_seconds,
    )
    print(
        f"[retry] {label} failed on attempt {attempt}/{retry_settings.max_attempts}: "
        f"{error}. Retrying in {delay:.1f}s..."
    )
    if delay > 0:
        time.sleep(delay)


def api_post_json(
    endpoint: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> dict[str, Any]:
    request_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    for attempt in range(1, retry_settings.max_attempts + 1):
        request = urllib.request.Request(
            endpoint,
            data=request_body,
            headers={
                "Accept": "*/*",
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "TowardsVictoryWonderImageHelper/1.0",
            },
            method="POST",
        )

        try:
            with opener.open(request, timeout=timeout) as response:
                response_body = response.read()
            break
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                raise RuntimeError(f"Packy API request failed: HTTP {exc.code}: {error_body}") from exc
            if attempt >= retry_settings.max_attempts:
                raise RuntimeError(f"Packy API request failed after {attempt} attempts: HTTP {exc.code}: {error_body}") from exc
            sleep_before_retry("Packy API request", attempt, exc, retry_settings)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt >= retry_settings.max_attempts:
                raise RuntimeError(f"Packy API request failed after {attempt} attempts: {exc}") from exc
            sleep_before_retry("Packy API request", attempt, exc, retry_settings)
    else:
        raise RuntimeError("Packy API request failed without a response")

    try:
        decoded = json.loads(response_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        snippet = response_body[:500].decode("utf-8", errors="replace")
        raise RuntimeError(f"Packy API returned non-JSON response: {snippet}") from exc

    if not isinstance(decoded, dict):
        raise RuntimeError("Packy API returned a non-object JSON response")
    return decoded


def download_bytes(
    url: str,
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> bytes:
    for attempt in range(1, retry_settings.max_attempts + 1):
        request = urllib.request.Request(url, headers={"User-Agent": "TowardsVictoryWonderImageHelper/1.0"})
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            if exc.code not in {408, 409, 425, 429, 500, 502, 503, 504}:
                raise RuntimeError(f"Image download failed: HTTP {exc.code}: {error_body}") from exc
            if attempt >= retry_settings.max_attempts:
                raise RuntimeError(f"Image download failed after {attempt} attempts: HTTP {exc.code}: {error_body}") from exc
            sleep_before_retry("image download", attempt, exc, retry_settings)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt >= retry_settings.max_attempts:
                raise RuntimeError(f"Image download failed after {attempt} attempts: {exc}") from exc
            sleep_before_retry("image download", attempt, exc, retry_settings)
    raise RuntimeError("Image download failed without a response")


def extract_png_bytes(
    response: dict[str, Any],
    timeout: float,
    retry_settings: RetrySettings,
    opener: urllib.request.OpenerDirector,
) -> tuple[bytes, str]:
    data = response.get("data")
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise RuntimeError("Packy API response did not contain data[0]")

    item = data[0]
    revised_prompt = str(item.get("revised_prompt") or "")

    if isinstance(item.get("b64_json"), str):
        encoded = item["b64_json"]
        if encoded.startswith("data:image/") and "," in encoded:
            encoded = encoded.split(",", 1)[1]
        try:
            return base64.b64decode(encoded, validate=False), revised_prompt
        except binascii.Error as exc:
            raise RuntimeError("Packy API returned invalid b64_json image data") from exc

    if isinstance(item.get("url"), str):
        return download_bytes(item["url"], timeout, retry_settings, opener), revised_prompt

    raise RuntimeError("Packy API response did not contain b64_json or url image data")


def paeth_predictor(left: int, up: int, upper_left: int) -> int:
    p = left + up - upper_left
    pa = abs(p - left)
    pb = abs(p - up)
    pc = abs(p - upper_left)
    if pa <= pb and pa <= pc:
        return left
    if pb <= pc:
        return up
    return upper_left


def blend_channel(source: int, alpha: int, background: int) -> int:
    return (source * alpha + background * (255 - alpha) + 127) // 255


def blend_rgb(red: int, green: int, blue: int, alpha: int, background: tuple[int, int, int]) -> tuple[int, int, int]:
    if alpha >= 255:
        return red, green, blue
    if alpha <= 0:
        return background
    return (
        blend_channel(red, alpha, background[0]),
        blend_channel(green, alpha, background[1]),
        blend_channel(blue, alpha, background[2]),
    )


def decode_png_rgb(png_bytes: bytes, background: tuple[int, int, int]) -> DecodedPng:
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise ValueError("Generated image is not a PNG file")

    width = height = bit_depth = color_type = compression = filter_method = interlace = None
    palette: list[tuple[int, int, int]] = []
    transparency: bytes | None = None
    idat_chunks: list[bytes] = []
    pos = len(PNG_SIGNATURE)

    while pos + 8 <= len(png_bytes):
        length = int.from_bytes(png_bytes[pos : pos + 4], "big")
        chunk_type = png_bytes[pos + 4 : pos + 8]
        chunk_start = pos + 8
        chunk_end = chunk_start + length
        if chunk_end + 4 > len(png_bytes):
            raise ValueError("PNG chunk extends beyond end of file")
        chunk_data = png_bytes[chunk_start:chunk_end]
        pos = chunk_end + 4

        if chunk_type == b"IHDR":
            if length != 13:
                raise ValueError("Invalid PNG IHDR length")
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB", chunk_data
            )
        elif chunk_type == b"PLTE":
            if length % 3:
                raise ValueError("Invalid PNG palette length")
            palette = [
                (chunk_data[i], chunk_data[i + 1], chunk_data[i + 2])
                for i in range(0, length, 3)
            ]
        elif chunk_type == b"tRNS":
            transparency = chunk_data
        elif chunk_type == b"IDAT":
            idat_chunks.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width is None or height is None or color_type is None or bit_depth is None:
        raise ValueError("PNG is missing IHDR")
    if compression != 0 or filter_method != 0:
        raise ValueError("Unsupported PNG compression or filter method")
    if interlace != 0:
        raise ValueError("Interlaced PNGs are not supported by this helper")
    if bit_depth != 8:
        raise ValueError("Only 8-bit PNGs are supported by this helper")
    if color_type not in {0, 2, 3, 4, 6}:
        raise ValueError(f"Unsupported PNG color type: {color_type}")
    if not idat_chunks:
        raise ValueError("PNG is missing IDAT data")

    channels_by_type = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
    channels = channels_by_type[color_type]
    stride = width * channels
    bytes_per_pixel = channels

    raw = zlib.decompress(b"".join(idat_chunks))
    expected_min = (stride + 1) * height
    if len(raw) < expected_min:
        raise ValueError("PNG decompressed data is shorter than expected")

    rows: list[bytes] = []
    previous = bytearray(stride)
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        scanline = bytearray(raw[offset : offset + stride])
        offset += stride

        for x in range(stride):
            left = scanline[x - bytes_per_pixel] if x >= bytes_per_pixel else 0
            up = previous[x]
            upper_left = previous[x - bytes_per_pixel] if x >= bytes_per_pixel else 0

            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = paeth_predictor(left, up, upper_left)
            else:
                raise ValueError(f"Unsupported PNG row filter: {filter_type}")
            scanline[x] = (scanline[x] + predictor) & 0xFF

        rows.append(bytes(scanline))
        previous = scanline

    rgb = bytearray(width * height * 3)
    out = 0
    truecolor_transparent: tuple[int, int, int] | None = None
    grayscale_transparent: int | None = None
    if transparency:
        if color_type == 0 and len(transparency) >= 2:
            grayscale_transparent = int.from_bytes(transparency[:2], "big") & 0xFF
        elif color_type == 2 and len(transparency) >= 6:
            truecolor_transparent = (
                int.from_bytes(transparency[0:2], "big") & 0xFF,
                int.from_bytes(transparency[2:4], "big") & 0xFF,
                int.from_bytes(transparency[4:6], "big") & 0xFF,
            )

    for row in rows:
        for x in range(width):
            src = x * channels
            if color_type == 0:
                value = row[src]
                alpha = 0 if grayscale_transparent == value else 255
                red, green, blue = blend_rgb(value, value, value, alpha, background)
            elif color_type == 2:
                red, green, blue = row[src], row[src + 1], row[src + 2]
                if truecolor_transparent == (red, green, blue):
                    red, green, blue = background
            elif color_type == 3:
                index = row[src]
                if index >= len(palette):
                    raise ValueError("PNG palette index out of range")
                red, green, blue = palette[index]
                alpha = transparency[index] if transparency and index < len(transparency) else 255
                red, green, blue = blend_rgb(red, green, blue, alpha, background)
            elif color_type == 4:
                value, alpha = row[src], row[src + 1]
                red, green, blue = blend_rgb(value, value, value, alpha, background)
            else:
                red, green, blue, alpha = row[src], row[src + 1], row[src + 2], row[src + 3]
                red, green, blue = blend_rgb(red, green, blue, alpha, background)

            rgb[out] = red
            rgb[out + 1] = green
            rgb[out + 2] = blue
            out += 3

    return DecodedPng(width=width, height=height, rgb=bytes(rgb))


def decoded_png_to_rgba(image: DecodedPng) -> RgbaImage:
    rgba = bytearray(image.width * image.height * 4)
    out = 0
    for pos in range(0, len(image.rgb), 3):
        rgba[out] = image.rgb[pos]
        rgba[out + 1] = image.rgb[pos + 1]
        rgba[out + 2] = image.rgb[pos + 2]
        rgba[out + 3] = 255
        out += 4
    return RgbaImage(width=image.width, height=image.height, rgba=bytes(rgba))


def write_dxt1_dds(image: DecodedPng, path: Path, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing DDS: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_dds(decoded_png_to_rgba(image), path, dds_format="DXT1", overwrite=True)


def convert_existing_dds(
    source_path: Path,
    dds_path: Path,
    background: tuple[int, int, int],
    label: str,
    crop_data: dict[str, Any] | None = None,
    stem: str | None = None,
) -> None:
    for message in convert_existing_dds_messages(source_path, dds_path, background, label, crop_data, stem):
        print(message)


def convert_existing_dds_messages(
    source_path: Path,
    dds_path: Path,
    background: tuple[int, int, int],
    label: str,
    crop_data: dict[str, Any] | None = None,
    stem: str | None = None,
) -> list[str]:
    crop_data = load_crop_data() if crop_data is None else crop_data
    full_result = write_wonder_dds_from_source(
        source_path,
        dds_path,
        stem or dds_path.stem,
        empty_crop_data(),
        background,
        dds_format="DXT1",
        overwrite=True,
        allow_crop=False,
    )
    file_size = dds_path.stat().st_size
    messages = [
        f"{label}: source={pretty_repo_path(source_path)}, "
        f"full={pretty_repo_path(dds_path)}, output={full_result.output_width}x{full_result.output_height}, "
        f"levels={full_result.levels}, size={file_size:,} bytes"
    ]
    if source_path.suffix.lower() != ".png":
        messages.append(f"{label}: skipped cropped variant because the source is not a PNG")
        return messages

    cropped_path = cropped_wonder_dds_path(dds_path)
    cropped_result = write_wonder_dds_from_source(
        source_path,
        cropped_path,
        stem or dds_path.stem,
        crop_data,
        background,
        dds_format="DXT1",
        overwrite=True,
        allow_crop=True,
    )
    cropped_size = cropped_path.stat().st_size
    crop_note = ""
    if cropped_result.crop_rect is not None:
        left, top, width, height = cropped_result.crop_rect
        crop_note = f", crop={left:.1f},{top:.1f},{width:.1f}x{height:.1f}"
    messages.append(
        f"{label}: cropped={pretty_repo_path(cropped_path)}, "
        f"output={cropped_result.output_width}x{cropped_result.output_height}, "
        f"levels={cropped_result.levels}, size={cropped_size:,} bytes{crop_note}"
    )
    return messages


def convert_existing_dds_worker(args: tuple[Path, Path, tuple[int, int, int], str, dict[str, Any], str]) -> list[str]:
    source_path, dds_path, background, label, crop_data, stem = args
    return convert_existing_dds_messages(source_path, dds_path, background, label, crop_data, stem)


def run_parallel_existing_dds_jobs(
    jobs: list[tuple[Path, Path, tuple[int, int, int], str, dict[str, Any], str]],
) -> int:
    if not jobs:
        return 0
    worker_count = min(len(jobs), max(1, min(os.cpu_count() or 1, 8)))
    print(f"[parallel] converting {len(jobs)} PNG-backed DDS jobs with {worker_count} workers")
    completed = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(convert_existing_dds_worker, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            for message in future.result():
                print(message)
            completed += 1
            if completed % 10 == 0 or completed == len(jobs):
                print(f"[parallel] completed {completed}/{len(jobs)}")
    return completed


def write_dds_pair_from_image(
    image: RgbaImage,
    dds_path: Path,
    stem: str,
    crop_data: dict[str, Any],
    background: tuple[int, int, int],
    *,
    dds_format: str,
    overwrite: bool,
) -> tuple[Any, Any]:
    full_result = write_wonder_dds_from_image(
        image,
        dds_path,
        stem,
        empty_crop_data(),
        background,
        dds_format=dds_format,
        overwrite=overwrite,
    )
    cropped_result = write_wonder_dds_from_image(
        image,
        cropped_wonder_dds_path(dds_path),
        stem,
        crop_data,
        background,
        dds_format=dds_format,
        overwrite=overwrite,
    )
    return full_result, cropped_result


def complete_missing_dds_pair_from_png(
    png_path: Path,
    dds_path: Path,
    stem: str,
    crop_data: dict[str, Any],
    background: tuple[int, int, int],
) -> None:
    cropped_path = cropped_wonder_dds_path(dds_path)
    if not dds_path.exists():
        full_result = write_wonder_dds_from_source(
            png_path,
            dds_path,
            stem,
            empty_crop_data(),
            background,
            dds_format="DXT1",
            overwrite=False,
            allow_crop=False,
        )
        print(f"[dds] {pretty_repo_path(dds_path)}, output={full_result.output_width}x{full_result.output_height}")
    if not cropped_path.exists():
        cropped_result = write_wonder_dds_from_source(
            png_path,
            cropped_path,
            stem,
            crop_data,
            background,
            dds_format="DXT1",
            overwrite=False,
            allow_crop=True,
        )
        dds_note = f", output={cropped_result.output_width}x{cropped_result.output_height}"
        if cropped_result.crop_rect is not None:
            left, top, width, height = cropped_result.crop_rect
            dds_note += f", crop={left:.1f},{top:.1f},{width:.1f}x{height:.1f}"
        print(f"[dds] {pretty_repo_path(cropped_path)}{dds_note}")


def convert_existing_assets(
    tasks: list[dict[str, Any]],
    background: tuple[int, int, int],
) -> int:
    crop_data = load_crop_data()
    converted = 0
    skipped = 0
    seen_dds_paths: set[Path] = set()
    seen_png_paths: set[Path] = set()
    dds_dirs: set[Path] = set()
    png_dds_dirs: dict[Path, Path] = {}
    parallel_jobs: list[tuple[Path, Path, tuple[int, int, int], str, dict[str, Any], str]] = []
    task_total = len(tasks)
    for index, task in enumerate(tasks, start=1):
        name = str(task.get("name") or "").strip()
        enabled = bool(task.get("enabled", True))
        stem = wonder_file_stem({"name": name})
        png_dir = resolve_repo_path(task.get("png_dir"), DEFAULT_PNG_DIR)
        dds_dir = resolve_repo_path(task.get("dds_dir"), DEFAULT_WONDERS_DIR)
        png_path = png_dir / f"{stem}.png"
        dds_path = dds_dir / f"{stem}.dds"
        cropped_path = cropped_wonder_dds_path(dds_path)
        seen_dds_paths.add(dds_path.resolve())
        seen_dds_paths.add(cropped_path.resolve())
        seen_png_paths.add(png_path.resolve())
        dds_dirs.add(dds_dir)
        png_dds_dirs.setdefault(png_dir, dds_dir)

        if not enabled:
            print(f"[skip {index}/{task_total}] {stem}: disabled")
            skipped += 1
            continue
        if png_path.exists():
            source_path = png_path
        elif dds_path.exists():
            source_path = dds_path
        else:
            print(f"[skip {index}/{task_total}] {stem}: no existing PNG or DDS")
            skipped += 1
            continue

        label = f"[convert {index}/{task_total}] {stem}"
        if source_path.suffix.lower() == ".png":
            parallel_jobs.append((source_path, dds_path, background, label, crop_data, stem))
        else:
            convert_existing_dds(
                source_path,
                dds_path,
                background,
                label,
                crop_data,
                stem,
            )
        converted += 1

    extra_png_total = 0
    for png_dir, dds_dir in sorted(png_dds_dirs.items(), key=lambda item: str(item[0])):
        if not png_dir.exists():
            continue
        for png_path in sorted(png_dir.glob("*.png")):
            if png_path.resolve() in seen_png_paths:
                continue
            stem = png_path.stem
            dds_path = dds_dir / f"{stem}.dds"
            seen_dds_paths.add(dds_path.resolve())
            extra_png_total += 1
            parallel_jobs.append((png_path, dds_path, background, f"[convert extra png] {stem}", crop_data, stem))
            converted += 1

    run_parallel_existing_dds_jobs(parallel_jobs)

    extra_total = 0
    for dds_dir in sorted(dds_dirs):
        for dds_path in sorted(dds_dir.glob("*.dds")):
            if dds_path.resolve() in seen_dds_paths:
                continue
            if dds_path.stem.endswith("_cropped"):
                continue
            extra_total += 1
            convert_existing_dds(
                dds_path,
                dds_path,
                background,
                f"[convert extra] {dds_path.stem}",
                crop_data,
                dds_path.stem,
            )
            converted += 1

    if extra_png_total:
        print(f"[summary] converted extra PNG files not listed in image tasks: {extra_png_total}")
    if extra_total:
        print(f"[summary] converted extra DDS files not listed in image tasks: {extra_total}")
    print(f"[summary] converted={converted}, skipped={skipped}")
    return 0


def parse_background(value: Any) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("dds.opaque_background must be a three-item RGB list")
    result = tuple(int(item) for item in value)
    if any(item < 0 or item > 255 for item in result):
        raise ValueError("dds.opaque_background values must be between 0 and 255")
    return result  # type: ignore[return-value]


def wonder_file_stem(output_config: dict[str, Any]) -> str:
    raw_name = str(output_config.get("name") or "").strip()
    if not raw_name:
        raise ValueError("output.name must be set")

    raw_name = raw_name.replace("\\", "/").rsplit("/", 1)[-1]
    raw_name = re.sub(r"\.dds$", "", raw_name, flags=re.IGNORECASE)
    raw_name = raw_name.lower()
    if raw_name.startswith("tv_wonder_"):
        raw_name = raw_name[len("tv_wonder_") :]

    slug = re.sub(r"[^a-z0-9]+", "_", raw_name).strip("_")
    if not slug:
        raise ValueError("output.name must contain ASCII letters or numbers")
    return f"tv_wonder_{slug}"


def write_metadata(path: Path, payload: dict[str, Any], response: dict[str, Any], revised_prompt: str) -> None:
    metadata = {
        "payload": payload,
        "created": response.get("created"),
        "revised_prompt": revised_prompt,
    }
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    config = load_config()
    api_config = require_object(config, "api")
    dds_config = require_object(config, "dds")
    tasks = load_task_config(config)

    endpoint = str(api_config.get("endpoint") or DEFAULT_ENDPOINT)
    timeout = float(api_config.get("timeout_seconds", 180))
    retry_settings = load_retry_settings(api_config)
    proxy_url = load_proxy_url(api_config)
    opener = build_url_opener(proxy_url)
    dds_format = str(dds_config.get("format", "DXT1")).upper()
    if dds_format != "DXT1":
        raise ValueError("dds.format currently supports only DXT1")
    background = parse_background(dds_config.get("opaque_background", [0, 0, 0]))

    if args.convert_existing_assets:
        return convert_existing_assets(tasks, background)

    crop_data = load_crop_data()
    api_key = resolve_api_key(api_config)
    if proxy_url:
        print(f"[network] proxy={proxy_url}")

    task_total = len(tasks)
    for index, task in enumerate(tasks, start=1):
        name = str(task.get("name") or "").strip()
        overwrite = bool(task.get("overwrite", False))
        enabled = bool(task.get("enabled", True))
        stem = wonder_file_stem({"name": name})

        png_dir = resolve_repo_path(task.get("png_dir"), DEFAULT_PNG_DIR)
        dds_dir = resolve_repo_path(task.get("dds_dir"), DEFAULT_WONDERS_DIR)
        png_path = png_dir / f"{stem}.png"
        dds_path = dds_dir / f"{stem}.dds"
        cropped_path = cropped_wonder_dds_path(dds_path)
        metadata_path = png_dir / f"{stem}.json"
        existing_paths = [path for path in (dds_path, cropped_path, png_path, metadata_path) if path.exists()]
        full_dds_exists = dds_path.exists()
        cropped_dds_exists = cropped_path.exists()

        if not enabled:
            print(f"[skip {index}/{task_total}] {stem}: disabled")
            continue
        if full_dds_exists and cropped_dds_exists and not overwrite:
            rel_paths = ", ".join(pretty_repo_path(path) for path in existing_paths)
            print(f"[skip {index}/{task_total}] {stem}: existing output found ({rel_paths}); overwrite=false")
            continue
        if not overwrite and (full_dds_exists or cropped_dds_exists):
            if png_path.exists():
                print(f"[repair {index}/{task_total}] {stem}: completing missing DDS variant from existing PNG")
                complete_missing_dds_pair_from_png(png_path, dds_path, stem, crop_data, background)
            else:
                rel_paths = ", ".join(pretty_repo_path(path) for path in existing_paths)
                print(
                    f"[skip {index}/{task_total}] {stem}: partial DDS output exists ({rel_paths}) "
                    "but no PNG source is available; overwrite=false"
                )
            continue

        payload = build_payload(task)
        expected_width, expected_height = parse_size(str(payload["size"]))
        keep_png = bool(task.get("keep_png", True))
        write_metadata_enabled = bool(task.get("write_metadata", True))

        if existing_paths:
            rel_paths = ", ".join(pretty_repo_path(path) for path in existing_paths)
            print(f"[overwrite {index}/{task_total}] {stem}: {rel_paths}")

        print(f"[request {index}/{task_total}] {stem} -> POST {endpoint}")
        print(
            f"[request {index}/{task_total}] model={payload['model']} "
            f"size={payload['size']} quality={payload['quality']}"
        )
        response = api_post_json(endpoint, api_key, payload, timeout, retry_settings, opener)
        png_bytes, revised_prompt = extract_png_bytes(response, timeout, retry_settings, opener)
        if not png_bytes.startswith(PNG_SIGNATURE):
            raise RuntimeError("Generated image payload is not a PNG")

        png_path.parent.mkdir(parents=True, exist_ok=True)
        png_path.write_bytes(png_bytes)
        print(f"[png] {pretty_repo_path(png_path)}")

        decoded = decode_png_rgb(png_bytes, background)
        if (decoded.width, decoded.height) != (expected_width, expected_height):
            raise RuntimeError(
                "Generated PNG size does not match requested size: "
                f"{decoded.width}x{decoded.height} != {expected_width}x{expected_height}"
            )

        full_result, cropped_result = write_dds_pair_from_image(
            decoded_png_to_rgba(decoded),
            dds_path,
            stem,
            crop_data,
            background,
            dds_format="DXT1",
            overwrite=overwrite,
        )
        dds_note = f", output={full_result.output_width}x{full_result.output_height}"
        print(f"[dds] {pretty_repo_path(dds_path)}{dds_note}")
        cropped_note = f", output={cropped_result.output_width}x{cropped_result.output_height}"
        if cropped_result.crop_rect is not None:
            left, top, width, height = cropped_result.crop_rect
            cropped_note += f", crop={left:.1f},{top:.1f},{width:.1f}x{height:.1f}"
        print(f"[dds] {pretty_repo_path(cropped_path)}{cropped_note}")

        if write_metadata_enabled:
            write_metadata(metadata_path, payload, response, revised_prompt)
            print(f"[metadata] {pretty_repo_path(metadata_path)}")

        if revised_prompt:
            print(f"[revised_prompt] {revised_prompt}")

        if not keep_png:
            png_path.unlink(missing_ok=True)
            print("[png] removed because output.keep_png is false")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - command-line helper should fail tersely.
        print(f"[error] {exc}", file=sys.stderr)
        if os.environ.get("TV_WONDER_IMAGE_DEBUG"):
            raise
        raise SystemExit(1) from None
