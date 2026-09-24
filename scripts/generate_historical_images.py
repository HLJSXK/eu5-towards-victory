#!/usr/bin/env python3
"""Edit every configured historical source image into a stylized PNG."""

import base64
import binascii
import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "generate_dds_icon_config.json"
OUTPUT_DIR = REPO_ROOT / "assets/historical/processed"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PROMPT = (
    "Edit the supplied historical image into a richly painted, stylized cartoon illustration "
    "for a historical strategy game. The input image is the authority for the scene: preserve "
    "its composition, perspective, recognizable buildings and objects, period details, and "
    "major light and shadow shapes. Use broad painterly color planes, restrained ink contours, "
    "aged material texture, and a dignified historical mood. Keep the original aspect ratio. "
    "Do not replace the scene, invent architecture, add modern objects, text, or a UI frame."
)


def load_tasks() -> tuple[dict, list[tuple[Path, Path]]]:
    root_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    config = root_config["historical_images"]
    api_config = root_config.get("api", {})
    config.setdefault("api_key", api_config.get("api_key", ""))
    config.setdefault("api_key_env", api_config.get("api_key_env", "IMAGE_API_KEY"))
    endpoint = config["endpoint"]
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not parsed.path.rstrip("/").endswith("/images/edits"):
        raise ValueError("historical_images.endpoint must be an absolute Images edits URL")
    if not isinstance(config.get("overwrite"), bool):
        raise ValueError("historical_images.overwrite must be true or false")
    if not isinstance(config.get("model"), str) or not config["model"].strip():
        raise ValueError("historical_images.model must be set")
    images = config.get("images")
    if not isinstance(images, list) or not images:
        raise ValueError("historical_images.images must contain source/output mappings")

    tasks = []
    seen_outputs = set()
    for image in images:
        source = (REPO_ROOT / image["source"]).resolve()
        output_name = image["output"]
        if Path(output_name).name != output_name or not output_name.endswith(".png"):
            raise ValueError(f"Output must be a PNG filename: {output_name}")
        if output_name in seen_outputs:
            raise ValueError(f"Duplicate historical output: {output_name}")
        if not source.is_file() or source.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise FileNotFoundError(f"Missing or unsupported historical source: {source}")
        seen_outputs.add(output_name)
        tasks.append((source, OUTPUT_DIR / output_name))
    return config, tasks


def resolve_api_key(config: dict) -> str:
    configured = str(config.get("api_key") or "").strip()
    env_names = config.get("api_key_env", "IMAGE_API_KEY")
    if isinstance(env_names, str):
        env_names = [env_names]
    if not isinstance(env_names, list) or not all(isinstance(name, str) for name in env_names):
        raise ValueError("historical_images.api_key_env must be a string or list of strings")
    key = configured or next((os.environ[name].strip() for name in env_names if os.environ.get(name, "").strip()), "")
    if not key:
        raise RuntimeError(f"Set one of {', '.join(env_names)} or api.api_key in {CONFIG_PATH.name}")
    return key


def multipart_body(source: Path, model: str) -> tuple[bytes, str]:
    boundary = f"----TowardsVictoryHistorical{uuid.uuid4().hex}"
    body = bytearray()
    for name, value in {
        "model": model,
        "prompt": PROMPT,
        "n": "1",
        "output_format": "png",
        "response_format": "url",
    }.items():
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode("utf-8"))
    content_type = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}[source.suffix.lower()]
    body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{source.name}"\r\nContent-Type: {content_type}\r\n\r\n'.encode("utf-8"))
    body.extend(source.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode("ascii"))
    return bytes(body), boundary


def edit_image(config: dict, source: Path, api_key: str) -> bytes:
    body, boundary = multipart_body(source, config["model"])
    request = urllib.request.Request(
        config["endpoint"],
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)
        item = result["data"][0]
        if isinstance(item.get("b64_json"), str):
            encoded = item["b64_json"].split(",", 1)[-1]
            image = base64.b64decode(encoded, validate=True)
        elif isinstance(item.get("url"), str):
            with urllib.request.urlopen(item["url"], timeout=180) as response:
                image = response.read()
        else:
            raise RuntimeError("Edit response has neither data[0].url nor data[0].b64_json")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Image edit failed: HTTP {exc.code}: {details}") from exc
    except (KeyError, IndexError, TypeError, ValueError, binascii.Error) as exc:
        raise RuntimeError(f"Invalid image edit response: {exc}") from exc
    if not image.startswith(PNG_SIGNATURE):
        raise RuntimeError("Image edit response is not a PNG")
    return image


def main() -> int:
    parser = argparse.ArgumentParser(description="Edit the configured historical images into styled PNGs.")
    parser.add_argument("--dry-run", action="store_true", help="List pending edits without calling the API")
    args = parser.parse_args()
    config, tasks = load_tasks()
    print(f"[config] {CONFIG_PATH.relative_to(REPO_ROOT)}")
    pending = [(source, output) for source, output in tasks if config["overwrite"] or not output.exists()]
    for source, output in tasks:
        if (source, output) not in pending:
            print(f"[skip] {output.relative_to(REPO_ROOT)} exists; overwrite=false")
    if not pending:
        return 0
    if args.dry_run:
        print(f"[dry-run] POST {config['endpoint']}")
        for source, output in pending:
            print(f"[dry-run] {source.relative_to(REPO_ROOT)} -> {output.relative_to(REPO_ROOT)}")
        return 0
    api_key = resolve_api_key(config)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for source, output in pending:
        print(f"[edit] {source.relative_to(REPO_ROOT)} -> {output.relative_to(REPO_ROOT)}")
        image = edit_image(config, source, api_key)
        temporary = output.with_suffix(output.suffix + ".tmp")
        try:
            temporary.write_bytes(image)
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"[write] {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError, KeyError) as error:
        raise SystemExit(f"[error] {error}") from error
