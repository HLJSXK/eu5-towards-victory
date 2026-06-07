#!/usr/bin/env python3
"""
Generate EU5 trade-good DDS assets through Packyapi Images API from a
natural-language prompt and target-specific style DDS/PNG references.

Usage:
  1. Edit generate_dds_icon_config.json.
  2. Set PACKY_API_KEY (or PACKY_SORA_TOKEN), or put api.api_key in
     generate_dds_icon.local.json.
  3. Run: conda run --no-capture-output -n eu5 python scripts/generate_dds_icon.py

The script expands a short asset idea into a production prompt for one selected
target, uploads that target's style-reference images, writes the generated PNG,
and converts it into one DDS target with enforced dimensions and byte limits.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
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

from dds_image_lib import PNG_SIGNATURE, encode_png_rgba, read_image_rgba, resize_rgba, write_dds


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "generate_dds_icon_config.json"
LOCAL_CONFIG_PATH = REPO_ROOT / "generate_dds_icon.local.json"
DEFAULT_GENERATIONS_ENDPOINT = "https://www.packyapi.com/v1/images/generations"
DEFAULT_EDITS_ENDPOINT = "https://www.packyapi.com/v1/images/edits"
DEFAULT_PNG_DIR = REPO_ROOT / "data" / "generated_icons"
DEFAULT_REF_DIR = DEFAULT_PNG_DIR / "_style_refs"
DEFAULT_STYLE_UPLOAD_FIELD = "image"

TARGET_PRESETS: dict[str, dict[str, Any]] = {
    "trade_good_icon": {
        "label": "trade goods Icon",
        "path": "src/main_menu/gfx/interface/icons/trade_goods/{name}.dds",
        "width": 128,
        "height": 128,
        "resize": "cover",
        "dds_format": "DXT5",
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
        "max_file_size_bytes": 1_000_000,
        "image_size": "2160x880",
        "prompt_requirements": (
            "This is a wide trade-goods illustration. Compose for a 1080x440 banner crop with "
            "a clear focal subject, supporting environment, and no tiny UI-icon-style object pile."
        ),
    },
}

TARGET_ALIASES = {
    "icon": "trade_good_icon",
    "trade_goods_icon": "trade_good_icon",
    "trade_good_icons": "trade_good_icon",
    "illustration": "trade_good_illustration",
    "trade_goods_illustration": "trade_good_illustration",
    "trade_goods_icon_illustration": "trade_good_illustration",
    "trade_good_icon_illustration": "trade_good_illustration",
}


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
    opaque_background: tuple[int, int, int]
    max_file_size_bytes: int
    image_size: str
    prompt_requirements: str
    style_reference_paths: tuple[str, ...]


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
    parser = argparse.ArgumentParser(description="Generate one configured EU5 trade-good DDS asset.")
    parser.add_argument(
        "--target",
        help=(
            "Generation target to write. Supported values: "
            f"{', '.join(sorted(TARGET_PRESETS))}. Aliases like icon and illustration are accepted."
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
        help="Print supported generation targets and exit.",
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
            valid = ", ".join(sorted(TARGET_PRESETS))
            raise ValueError(
                "Set generation_target (or pass --target) so the helper writes exactly one DDS target. "
                f"Supported targets: {valid}"
            )

    if target_name not in TARGET_PRESETS:
        valid = ", ".join(sorted(TARGET_PRESETS))
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
    asset_name = safe_slug(str(output_config.get("name") or "generated_icon"))
    preset = TARGET_PRESETS[target_name]
    target_config = deep_merge(preset, target_override(output_config, target_name))

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

    image_size = str(target_config.get("image_size") or preset["image_size"])
    if image_size != "auto":
        parse_size(image_size)

    path_template = str(target_config.get("path") or preset["path"])
    path = resolve_repo_path(expand_template(path_template, asset_name, target_name))
    style_reference_paths = target_style_reference_paths(target_config, style_config, target_name, asset_name)

    return TargetSpec(
        name=target_name,
        label=str(target_config.get("label") or preset["label"]),
        path=path,
        width=width,
        height=height,
        resize=resize,
        dds_format=dds_format,
        opaque_background=parse_rgb(
            target_config.get("opaque_background", output_config.get("opaque_background", [0, 0, 0]))
        ),
        max_file_size_bytes=max_file_size_bytes,
        image_size=image_size,
        prompt_requirements=str(target_config.get("prompt_requirements") or preset["prompt_requirements"]),
        style_reference_paths=style_reference_paths,
    )


def apply_target_image_settings(image_config: dict[str, Any], target: TargetSpec) -> dict[str, Any]:
    configured = dict(image_config)
    configured["size"] = target.image_size
    return configured


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


def output_asset_name(output_config: dict[str, Any]) -> str:
    return safe_slug(str(output_config.get("name") or "generated_icon"))


def output_artifact_stem(output_config: dict[str, Any], target: TargetSpec) -> str:
    asset_name = output_asset_name(output_config)
    template = str(output_config.get("artifact_stem") or "{name}_{target}")
    return safe_slug(expand_template(template, asset_name, target.name), default=asset_name)


def write_generated_png(png_bytes: bytes, output_config: dict[str, Any], target: TargetSpec) -> Path:
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise RuntimeError("Generated image payload is not a PNG")
    png_dir = resolve_repo_path(output_config.get("png_dir"), DEFAULT_PNG_DIR)
    png_path = png_dir / f"{output_artifact_stem(output_config, target)}.png"
    if png_path.exists() and not bool(output_config.get("overwrite", False)):
        raise FileExistsError(f"refusing to overwrite existing PNG: {png_path}")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.write_bytes(png_bytes)
    print(f"[png] {display_path(png_path)}")
    return png_path


def write_target(output_config: dict[str, Any], source_png_path: Path, target: TargetSpec) -> dict[str, Any]:
    overwrite = bool(output_config.get("overwrite", False))
    source_image = read_image_rgba(source_png_path)
    target_image = resize_rgba(source_image, target.width, target.height, target.resize)
    write_dds(
        target_image,
        target.path,
        dds_format=target.dds_format,
        overwrite=overwrite,
        opaque_background=target.opaque_background,
    )
    file_size = target.path.stat().st_size
    mipmap_count = read_dds_mipmap_count(target.path)
    if file_size > target.max_file_size_bytes:
        raise RuntimeError(
            f"{target.name} output is {format_bytes(file_size)}, above the "
            f"{format_bytes(target.max_file_size_bytes)} limit: {target.path}"
        )
    print(
        f"[dds] {display_path(target.path)} "
        f"({target.width}x{target.height} {target.dds_format}, resize={target.resize}, "
        f"mips={mipmap_count}, {format_bytes(file_size)} <= {format_bytes(target.max_file_size_bytes)})"
    )
    return {
        "name": target.name,
        "label": target.label,
        "path": display_path(target.path).replace("\\", "/"),
        "width": target.width,
        "height": target.height,
        "resize": target.resize,
        "dds_format": target.dds_format,
        "mipmap_count": mipmap_count,
        "file_size_bytes": file_size,
        "max_file_size_bytes": target.max_file_size_bytes,
    }


def read_dds_mipmap_count(path: Path) -> int:
    data = path.read_bytes()
    if len(data) < 32 or not data.startswith(b"DDS "):
        raise ValueError(f"{path} is not a DDS file")
    return int.from_bytes(data[28:32], "little")


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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.list_targets:
        for name, preset in TARGET_PRESETS.items():
            print(
                f"{name}: {preset['label']} "
                f"({preset['width']}x{preset['height']}, <= {format_bytes(int(preset['max_file_size_bytes']))})"
            )
        return 0

    config = load_config()
    api_config = require_object(config, "api")
    prompt_config = require_object(config, "prompt_refinement")
    image_config = require_object(config, "image")
    style_config = require_object(config, "style_reference")
    output_config = require_object(config, "output")
    target = load_target_spec(config, output_config, style_config, args.target)
    image_config = apply_target_image_settings(image_config, target)

    print(
        f"[target] {target.name}: {target.width}x{target.height}, "
        f"request_size={target.image_size}, max={format_bytes(target.max_file_size_bytes)}"
    )
    print(f"[target] output={display_path(target.path)}")

    if args.convert_existing_png:
        source_png_path = resolve_repo_path(args.convert_existing_png)
        if not source_png_path.exists():
            raise FileNotFoundError(f"Missing source PNG: {source_png_path}")
        print(f"[png] source={display_path(source_png_path)}")
        written_target = write_target(output_config, source_png_path, target)
        update_existing_metadata_target(output_config, target, written_target)
        return 0

    timeout = float(api_config.get("timeout_seconds", 180))
    retry_settings = load_retry_settings(api_config)
    proxy_url = load_proxy_url(api_config)
    opener = build_url_opener(proxy_url)
    if proxy_url:
        print(f"[network] proxy={proxy_url}")
    style_uploads = collect_style_references(style_config, target, dry_run=bool(args.dry_run))

    final_prompt = refine_prompt(prompt_config, image_config, target)
    print("[prompt] final prompt:")
    print(final_prompt)

    image_payload = build_generation_payload(image_config, final_prompt)
    if args.dry_run:
        print("[dry-run] payload:")
        print(json.dumps(image_payload, ensure_ascii=False, indent=2))
        print("[dry-run] skipped API request and output writes")
        return 0

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
    written_target = write_target(output_config, png_path, target)
    write_metadata(output_config, target, image_payload, image_response, final_prompt, revised_prompt, [written_target])
    if not bool(output_config.get("keep_png", True)):
        png_path.unlink(missing_ok=True)
        print("[png] removed because output.keep_png is false")

    if revised_prompt:
        print(f"[revised_prompt] {revised_prompt}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - command-line helper should fail tersely.
        print(f"[error] {exc}", file=sys.stderr)
        if os.environ.get("TV_ICON_IMAGE_DEBUG"):
            raise
        raise SystemExit(1) from None
