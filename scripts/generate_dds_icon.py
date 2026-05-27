#!/usr/bin/env python3
"""
Generate EU5 DDS icons through Packyapi Images API from a natural-language
prompt and an optional style DDS/PNG.

Usage:
  1. Edit generate_dds_icon_config.json.
  2. Set PACKY_API_KEY (or PACKY_SORA_TOKEN), or put api.api_key in
     generate_dds_icon.local.json.
  3. Run: conda run --no-capture-output -n eu5 python scripts/generate_dds_icon.py

The script expands a short asset idea into a production prompt, uploads one
style-reference image when configured, writes the generated PNG, and converts
it into one or more DDS targets with the requested dimensions.
"""

from __future__ import annotations

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
    output_config: dict[str, Any],
) -> str:
    prompt = str(image_config.get("prompt") or image_config.get("natural_prompt") or "").strip()
    if not prompt:
        raise ValueError("image.prompt or image.natural_prompt must be set")

    if not bool(prompt_config.get("enabled", False)):
        return prompt

    style_rules = str(prompt_config.get("style_rules") or "").strip()
    composition_rules = str(prompt_config.get("composition_rules") or "").strip()
    negative_prompt = str(image_config.get("negative_prompt") or "").strip()

    targets = output_config.get("targets", [])
    target_summary: list[str] = []
    if isinstance(targets, list):
        for target in targets:
            if isinstance(target, dict):
                name = str(target.get("name") or target.get("path") or "unnamed target")
                width = target.get("width")
                height = target.get("height")
                target_summary.append(f"- {name}: {width}x{height}")
    target_text = "\n".join(target_summary) if target_summary else "- single DDS target"

    parts = [
        "Create a Europa Universalis V DDS icon asset.",
        f"Subject: {prompt}",
        "Reference image: use the uploaded DDS only as style guidance for palette, brushwork, lighting, surface treatment, and framing discipline. Do not copy its subject or any text.",
        "Composition: keep the main subject centered, readable, and high-contrast, with no watermark, no letters, no logo, and no UI chrome baked into the art.",
        "Output targets:",
        target_text,
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


def collect_style_references(style_config: dict[str, Any]) -> list[UploadFile]:
    paths = style_config.get("paths", [])
    if isinstance(paths, str):
        paths = [paths]
    if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
        raise ValueError("style_reference.paths must be a string or list of strings")
    if bool(style_config.get("required", False)) and not paths:
        raise ValueError("style_reference.paths must include at least one vanilla DDS/PNG when required is true")

    ref_dir = resolve_repo_path(style_config.get("temporary_png_dir"), DEFAULT_REF_DIR)
    upload_field = str(style_config.get("upload_field_name") or DEFAULT_STYLE_UPLOAD_FIELD)
    if upload_field != DEFAULT_STYLE_UPLOAD_FIELD:
        raise ValueError('Packy image edits require style_reference.upload_field_name = "image"')
    ref_dir.mkdir(parents=True, exist_ok=True)
    uploads: list[UploadFile] = []
    for index, raw_path in enumerate(paths, start=1):
        path = resolve_repo_path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"Missing style reference: {path}")
        image = read_image_rgba(path)
        png_bytes = encode_png_rgba(image)
        png_name = f"{index:02d}_{safe_slug(path.stem)}.png"
        if bool(style_config.get("write_converted_pngs", True)):
            (ref_dir / png_name).write_bytes(png_bytes)
            print(f"[style] converted {path.relative_to(REPO_ROOT)} -> {(ref_dir / png_name).relative_to(REPO_ROOT)}")
        else:
            print(f"[style] converted {path.relative_to(REPO_ROOT)} for upload")
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


def target_name(target: dict[str, Any], index: int) -> str:
    raw = str(target.get("name") or target.get("path") or f"target_{index}").replace("\\", "/")
    return safe_slug(raw.rsplit("/", 1)[-1].removesuffix(".dds"), default=f"target_{index}")


def write_generated_png(png_bytes: bytes, output_config: dict[str, Any]) -> Path:
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise RuntimeError("Generated image payload is not a PNG")
    png_dir = resolve_repo_path(output_config.get("png_dir"), DEFAULT_PNG_DIR)
    name = safe_slug(str(output_config.get("name") or "generated_icon"))
    png_path = png_dir / f"{name}.png"
    if png_path.exists() and not bool(output_config.get("overwrite", False)):
        raise FileExistsError(f"refusing to overwrite existing PNG: {png_path}")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.write_bytes(png_bytes)
    print(f"[png] {png_path.relative_to(REPO_ROOT)}")
    return png_path


def write_targets(output_config: dict[str, Any], source_png_path: Path) -> list[dict[str, Any]]:
    targets = output_config.get("targets", [])
    if not isinstance(targets, list) or not targets:
        raise ValueError("output.targets must be a non-empty list")

    overwrite = bool(output_config.get("overwrite", False))
    source_image = read_image_rgba(source_png_path)
    written: list[dict[str, Any]] = []
    for index, target in enumerate(targets, start=1):
        if not isinstance(target, dict):
            raise ValueError("each output target must be a JSON object")
        dds_path = resolve_repo_path(str(target.get("path") or ""))
        width = int(target.get("width") or source_image.width)
        height = int(target.get("height") or source_image.height)
        resize_mode = str(target.get("resize") or "cover")
        dds_format = str(target.get("dds_format") or output_config.get("dds_format") or "DXT5").upper()
        background = parse_rgb(target.get("opaque_background", output_config.get("opaque_background", [0, 0, 0])))
        target_image = resize_rgba(source_image, width, height, resize_mode)
        write_dds(target_image, dds_path, dds_format=dds_format, overwrite=overwrite, opaque_background=background)
        rel_path = dds_path.relative_to(REPO_ROOT)
        print(f"[dds] {rel_path} ({width}x{height} {dds_format}, resize={resize_mode})")
        written.append(
            {
                "name": target_name(target, index),
                "path": str(rel_path).replace("\\", "/"),
                "width": width,
                "height": height,
                "resize": resize_mode,
                "dds_format": dds_format,
            }
        )
    return written


def write_metadata(
    output_config: dict[str, Any],
    image_payload: dict[str, Any],
    image_response: dict[str, Any],
    final_prompt: str,
    revised_prompt: str,
    written_targets: list[dict[str, Any]],
) -> None:
    if not bool(output_config.get("write_metadata", True)):
        return
    metadata_dir = resolve_repo_path(output_config.get("metadata_dir"), DEFAULT_PNG_DIR)
    name = safe_slug(str(output_config.get("name") or "generated_icon"))
    metadata_path = metadata_dir / f"{name}.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "payload": image_payload,
        "created": image_response.get("created"),
        "final_prompt": final_prompt,
        "revised_prompt": revised_prompt,
        "targets": written_targets,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[metadata] {metadata_path.relative_to(REPO_ROOT)}")


def main() -> int:
    config = load_config()
    api_config = require_object(config, "api")
    prompt_config = require_object(config, "prompt_refinement")
    image_config = require_object(config, "image")
    style_config = require_object(config, "style_reference")
    output_config = require_object(config, "output")

    timeout = float(api_config.get("timeout_seconds", 180))
    retry_settings = load_retry_settings(api_config)
    proxy_url = load_proxy_url(api_config)
    opener = build_url_opener(proxy_url)
    if proxy_url:
        print(f"[network] proxy={proxy_url}")
    style_uploads = collect_style_references(style_config)
    api_key = resolve_api_key(api_config)

    final_prompt = refine_prompt(prompt_config, image_config, output_config)
    print("[prompt] final prompt:")
    print(final_prompt)

    image_payload = build_generation_payload(image_config, final_prompt)
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
    png_path = write_generated_png(png_bytes, output_config)
    written_targets = write_targets(output_config, png_path)
    write_metadata(output_config, image_payload, image_response, final_prompt, revised_prompt, written_targets)
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
