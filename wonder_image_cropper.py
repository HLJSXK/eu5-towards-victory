#!/usr/bin/env python3
"""Web tool for choosing 27:11 wonder image crops."""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import threading
import webbrowser
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from generate_wonder_image import (  # noqa: E402
    DEFAULT_PNG_DIR,
    DEFAULT_WONDERS_DIR,
    convert_existing_assets,
    load_config,
    load_task_config,
    parse_background,
    require_object,
    resolve_repo_path,
    wonder_file_stem,
)
from wonder_image_crop_lib import (  # noqa: E402
    CROP_DATA_PATH,
    TARGET_ASPECT,
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


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the browser-based wonder image 27:11 crop tool.")
    parser.add_argument("--host", default="127.0.0.1", help="host to bind; default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8789, help="port to bind; default: 8789")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the current crop data to existing wonder assets without starting the web server.",
    )
    return parser.parse_args(argv)


def repo_relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def build_image_tasks() -> list[ImageTask]:
    config = load_config()
    tasks = load_task_config(config)
    image_tasks: list[ImageTask] = []
    seen_pngs: set[Path] = set()
    png_dirs: set[Path] = set()

    for task in tasks:
        name = str(task.get("name") or "").strip()
        stem = wonder_file_stem({"name": name})
        png_dir = resolve_repo_path(task.get("png_dir"), DEFAULT_PNG_DIR)
        dds_dir = resolve_repo_path(task.get("dds_dir"), DEFAULT_WONDERS_DIR)
        png_dirs.add(png_dir)
        png_path = png_dir / f"{stem}.png"
        dds_path = dds_dir / f"{stem}.dds"
        if not png_path.exists():
            continue
        image_tasks.append(
            ImageTask(
                key=str(task.get("key") or stem),
                name=name or stem,
                stem=stem,
                png_path=png_path,
                dds_path=dds_path,
                source="configured",
            )
        )
        seen_pngs.add(png_path.resolve())

    for png_dir in sorted(png_dirs or {DEFAULT_PNG_DIR}, key=str):
        if not png_dir.exists():
            continue
        for png_path in sorted(png_dir.glob("*.png")):
            resolved = png_path.resolve()
            if resolved in seen_pngs:
                continue
            stem = normalize_crop_key(png_path.name)
            image_tasks.append(
                ImageTask(
                    key=stem,
                    name=stem,
                    stem=stem,
                    png_path=png_path,
                    dds_path=DEFAULT_WONDERS_DIR / f"{stem}.dds",
                    source="extra_png",
                )
            )
            seen_pngs.add(resolved)

    return image_tasks


def apply_current_crop_data() -> int:
    config = load_config()
    tasks = load_task_config(config)
    dds_config = require_object(config, "dds")
    dds_format = str(dds_config.get("format", "DXT1")).upper()
    if dds_format != "DXT1":
        raise ValueError("dds.format currently supports only DXT1")
    background = parse_background(dds_config.get("opaque_background", [0, 0, 0]))
    return convert_existing_assets(tasks, background)


def task_summary(task: ImageTask, index: int, crop_data: dict[str, Any]) -> dict[str, Any]:
    image_width, image_height = read_png_size(task.png_path)
    saved_rect = get_crop_rect_for_image(crop_data, task.stem, image_width, image_height)
    default_rect = largest_center_crop_rect(image_width, image_height, TARGET_ASPECT)
    rect = saved_rect or default_rect
    return {
        "index": index,
        "key": task.key,
        "name": task.name,
        "stem": task.stem,
        "source": task.source,
        "pngPath": repo_relative_path(task.png_path),
        "ddsPath": repo_relative_path(task.dds_path),
        "width": image_width,
        "height": image_height,
        "saved": saved_rect is not None,
        "rect": rect_to_payload(rect),
        "defaultRect": rect_to_payload(default_rect),
    }


def rect_to_payload(rect: tuple[float, float, float, float]) -> dict[str, float]:
    left, top, width, height = rect
    return {
        "x": left,
        "y": top,
        "width": width,
        "height": height,
    }


def read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or not header.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"{path} is not a PNG file")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def parse_rect_payload(payload: dict[str, Any]) -> tuple[float, float, float, float]:
    rect = payload.get("rect")
    if not isinstance(rect, dict):
        raise ValueError("payload.rect must be an object")
    try:
        left = float(rect["x"])
        top = float(rect["y"])
        width = float(rect["width"])
        height = float(rect["height"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("payload.rect must contain numeric x, y, width, and height") from exc
    return left, top, width, height


class CropperState:
    def __init__(self, tasks: list[ImageTask]) -> None:
        self.tasks = tasks
        self.lock = threading.Lock()
        self.crop_data = load_crop_data()
        self.logs: list[str] = []

    def reload_crops(self) -> None:
        self.crop_data = load_crop_data()

    def api_tasks(self) -> dict[str, Any]:
        with self.lock:
            self.reload_crops()
            return {
                "aspect": {"width": TARGET_ASPECT[0], "height": TARGET_ASPECT[1]},
                "dataPath": repo_relative_path(CROP_DATA_PATH),
                "tasks": [
                    task_summary(task, index, self.crop_data)
                    for index, task in enumerate(self.tasks)
                ],
                "logs": list(self.logs[-80:]),
            }

    def api_task(self, index: int) -> dict[str, Any]:
        with self.lock:
            self.reload_crops()
            return task_summary(self.tasks[index], index, self.crop_data)

    def save_crop(self, index: int, rect: tuple[float, float, float, float]) -> dict[str, Any]:
        task = self.tasks[index]
        with self.lock:
            self.reload_crops()
            image_width, image_height = read_png_size(task.png_path)
            saved_rect = set_crop_record(
                self.crop_data,
                task.stem,
                task.png_path,
                image_width,
                image_height,
                rect,
            )
            save_crop_data(self.crop_data)
            message = (
                f"saved {task.stem}: "
                f"{saved_rect[0]:.1f},{saved_rect[1]:.1f},{saved_rect[2]:.1f}x{saved_rect[3]:.1f}"
            )
            self.logs.append(message)
            return {"ok": True, "message": message, "task": task_summary(task, index, self.crop_data)}

    def remove_crop(self, index: int) -> dict[str, Any]:
        task = self.tasks[index]
        with self.lock:
            self.reload_crops()
            removed = remove_crop_record(self.crop_data, task.stem)
            save_crop_data(self.crop_data)
            message = f"removed crop for {task.stem}" if removed else f"no saved crop for {task.stem}"
            self.logs.append(message)
            return {"ok": True, "message": message, "removed": removed, "task": task_summary(task, index, self.crop_data)}

    def apply_crops(self) -> dict[str, Any]:
        with self.lock:
            self.logs.append("rebuild started")
        exit_code = apply_current_crop_data()
        with self.lock:
            self.reload_crops()
            message = "DDS rebuild finished" if exit_code == 0 else f"DDS rebuild exited with code {exit_code}"
            self.logs.append(message)
            return {"ok": exit_code == 0, "message": message, "logs": list(self.logs[-80:])}


def build_handler(state: CropperState) -> type[BaseHTTPRequestHandler]:
    class CropperRequestHandler(BaseHTTPRequestHandler):
        server_version = "WonderImageCropper/1.0"

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API.
            parsed = urlparse(self.path)
            try:
                if parsed.path in {"/", "/index.html"}:
                    self.send_html(INDEX_HTML)
                elif parsed.path == "/app.css":
                    self.send_text(APP_CSS, "text/css; charset=utf-8")
                elif parsed.path == "/app.js":
                    self.send_text(APP_JS, "application/javascript; charset=utf-8")
                elif parsed.path == "/api/tasks":
                    self.send_json(state.api_tasks())
                elif parsed.path.startswith("/api/task/"):
                    index = self.path_index(parsed.path, "/api/task/")
                    self.send_json(state.api_task(index))
                elif parsed.path.startswith("/api/image/"):
                    index = self.path_index(parsed.path, "/api/image/")
                    self.send_file(state.tasks[index].png_path)
                else:
                    self.send_error_json(HTTPStatus.NOT_FOUND, "not found")
            except Exception as exc:  # noqa: BLE001 - API should return a compact JSON error.
                self.send_error_json(HTTPStatus.BAD_REQUEST, str(exc))

        def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API.
            parsed = urlparse(self.path)
            try:
                payload = self.read_json_body()
                if parsed.path.startswith("/api/save/"):
                    index = self.path_index(parsed.path, "/api/save/")
                    self.send_json(state.save_crop(index, parse_rect_payload(payload)))
                elif parsed.path.startswith("/api/remove/"):
                    index = self.path_index(parsed.path, "/api/remove/")
                    self.send_json(state.remove_crop(index))
                elif parsed.path == "/api/apply":
                    self.send_json(state.apply_crops())
                else:
                    self.send_error_json(HTTPStatus.NOT_FOUND, "not found")
            except Exception as exc:  # noqa: BLE001 - API should return a compact JSON error.
                self.send_error_json(HTTPStatus.BAD_REQUEST, str(exc))

        def read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            value = json.loads(raw.decode("utf-8"))
            if not isinstance(value, dict):
                raise ValueError("request body must be a JSON object")
            return value

        def path_index(self, path: str, prefix: str) -> int:
            raw_index = path.removeprefix(prefix).split("/", 1)[0]
            index = int(raw_index)
            if index < 0 or index >= len(state.tasks):
                raise IndexError("image index out of range")
            return index

        def send_html(self, text: str) -> None:
            self.send_bytes(text.encode("utf-8"), "text/html; charset=utf-8")

        def send_text(self, text: str, content_type: str) -> None:
            self.send_bytes(text.encode("utf-8"), content_type)

        def send_json(self, payload: dict[str, Any]) -> None:
            self.send_bytes(
                json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                "application/json; charset=utf-8",
            )

        def send_file(self, path: Path) -> None:
            content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            self.send_bytes(path.read_bytes(), content_type)

        def send_bytes(self, data: bytes, content_type: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def send_error_json(self, status: HTTPStatus, message: str) -> None:
            payload = json.dumps({"ok": False, "error": message}, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            print(f"[web] {self.address_string()} - {format % args}")

    return CropperRequestHandler


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Wonder Image Cropper</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body>
  <header class="topbar">
    <div>
      <h1>Wonder Image Cropper</h1>
      <p id="dataPath"></p>
    </div>
    <div class="top-actions">
      <button id="prevBtn" type="button">Previous</button>
      <button id="nextBtn" type="button">Next</button>
      <button id="saveBtn" class="primary" type="button">Save and Next</button>
      <button id="removeBtn" type="button">Remove Crop</button>
      <button id="applyBtn" type="button">Apply Data Crops to DDS</button>
    </div>
  </header>
  <main class="layout">
    <aside class="sidebar">
      <div class="sidebar-title">Images</div>
      <div id="taskList" class="task-list"></div>
    </aside>
    <section class="stage">
      <canvas id="canvas"></canvas>
    </section>
    <aside class="inspector">
      <h2 id="title">No image</h2>
      <dl>
        <dt>Source</dt><dd id="sourcePath"></dd>
        <dt>Output</dt><dd id="outputPath"></dd>
        <dt>Image</dt><dd id="imageMeta"></dd>
        <dt>Crop</dt><dd id="cropMeta"></dd>
      </dl>
      <div id="status" class="status"></div>
      <div class="log-title">Log</div>
      <div id="log" class="log"></div>
    </aside>
  </main>
  <script src="/app.js"></script>
</body>
</html>
"""


APP_CSS = r"""
:root {
  color-scheme: dark;
  --bg: #15171a;
  --panel: #20242a;
  --panel-2: #272c34;
  --line: #3a414d;
  --text: #eef2f6;
  --muted: #9ba7b7;
  --accent: #71c7ec;
  --saved: #f6c453;
  --danger: #ff7c7c;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 980px;
  height: 100vh;
  overflow: hidden;
  background: var(--bg);
  color: var(--text);
  font: 14px/1.45 "Segoe UI", Arial, sans-serif;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 74px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
  background: #191c21;
}

h1, h2, p {
  margin: 0;
}

h1 {
  font-size: 20px;
}

#dataPath {
  margin-top: 3px;
  color: var(--muted);
  font-size: 12px;
}

button {
  min-height: 32px;
  border: 1px solid #4a5360;
  border-radius: 6px;
  padding: 0 12px;
  background: #2d333c;
  color: var(--text);
  cursor: pointer;
}

button:hover {
  background: #38414d;
}

button:disabled {
  opacity: 0.45;
  cursor: default;
}

button.primary {
  border-color: #2f8fbd;
  background: #146b92;
}

.top-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.layout {
  display: grid;
  grid-template-columns: 260px minmax(420px, 1fr) 330px;
  height: calc(100vh - 74px);
}

.sidebar,
.inspector {
  overflow: hidden;
  border-right: 1px solid var(--line);
  background: var(--panel);
}

.inspector {
  border-right: 0;
  border-left: 1px solid var(--line);
  padding: 14px;
}

.sidebar-title,
.log-title {
  padding: 12px 14px;
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.task-list {
  height: calc(100% - 42px);
  overflow: auto;
}

.task-item {
  width: 100%;
  display: block;
  border: 0;
  border-radius: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  padding: 10px 12px;
  background: transparent;
  text-align: left;
}

.task-item.active {
  background: #304151;
}

.task-item.saved .stem::after {
  content: " saved";
  margin-left: 6px;
  color: var(--saved);
  font-size: 11px;
}

.stem {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.path {
  display: block;
  overflow: hidden;
  color: var(--muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stage {
  min-width: 0;
  min-height: 0;
  padding: 16px;
  background: #111316;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #0f1115;
}

.inspector h2 {
  margin-bottom: 12px;
  overflow-wrap: anywhere;
  font-size: 18px;
}

dl {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 8px 10px;
  margin: 0 0 14px;
}

dt {
  color: var(--muted);
}

dd {
  margin: 0;
  min-width: 0;
  overflow-wrap: anywhere;
}

.status {
  min-height: 44px;
  margin: 10px 0 16px;
  padding: 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--panel-2);
}

.status.error {
  color: var(--danger);
}

.log {
  height: 280px;
  overflow: auto;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 8px;
  background: #181b20;
  color: var(--muted);
  font-family: Consolas, "Courier New", monospace;
  font-size: 12px;
  white-space: pre-wrap;
}
"""


APP_JS = r"""
const state = {
  tasks: [],
  index: 0,
  image: null,
  rect: null,
  saved: false,
  view: { scale: 1, left: 0, top: 0, width: 1, height: 1 },
  drag: null,
};

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const els = {
  dataPath: document.getElementById("dataPath"),
  taskList: document.getElementById("taskList"),
  title: document.getElementById("title"),
  sourcePath: document.getElementById("sourcePath"),
  outputPath: document.getElementById("outputPath"),
  imageMeta: document.getElementById("imageMeta"),
  cropMeta: document.getElementById("cropMeta"),
  status: document.getElementById("status"),
  log: document.getElementById("log"),
  prevBtn: document.getElementById("prevBtn"),
  nextBtn: document.getElementById("nextBtn"),
  saveBtn: document.getElementById("saveBtn"),
  removeBtn: document.getElementById("removeBtn"),
  applyBtn: document.getElementById("applyBtn"),
};

function setStatus(text, isError = false) {
  els.status.textContent = text;
  els.status.classList.toggle("error", isError);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok || payload.ok === false) {
    throw new Error(payload.error || payload.message || response.statusText);
  }
  return payload;
}

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function aspect() {
  return 27 / 11;
}

function largestCenterRect(width, height) {
  const ratio = aspect();
  let cropWidth;
  let cropHeight;
  if (width / height >= ratio) {
    cropHeight = height;
    cropWidth = cropHeight * ratio;
  } else {
    cropWidth = width;
    cropHeight = cropWidth / ratio;
  }
  return {
    x: (width - cropWidth) / 2,
    y: (height - cropHeight) / 2,
    width: cropWidth,
    height: cropHeight,
  };
}

function clampRect(rect, imageWidth, imageHeight) {
  const ratio = aspect();
  const maxRect = largestCenterRect(imageWidth, imageHeight);
  let width = Math.abs(rect.width);
  let height = Math.abs(rect.height);
  if (width <= 0.001 || height <= 0.001) {
    return maxRect;
  }
  if (width / height > ratio) {
    width = height * ratio;
  } else {
    height = width / ratio;
  }
  if (width > maxRect.width) {
    width = maxRect.width;
    height = width / ratio;
  }
  if (height > maxRect.height) {
    height = maxRect.height;
    width = height * ratio;
  }
  width = clamp(width, 1, imageWidth);
  height = width / ratio;
  if (height > imageHeight) {
    height = imageHeight;
    width = height * ratio;
  }
  return {
    x: clamp(rect.x, 0, Math.max(0, imageWidth - width)),
    y: clamp(rect.y, 0, Math.max(0, imageHeight - height)),
    width,
    height,
  };
}

function rectFromPoints(start, end, imageWidth, imageHeight) {
  const ratio = aspect();
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const absDx = Math.abs(dx);
  const absDy = Math.abs(dy);
  if (absDx < 1 && absDy < 1) {
    return largestCenterRect(imageWidth, imageHeight);
  }
  let width;
  let height;
  if (absDy <= 0.001 || (absDx > 0.001 && absDx / ratio <= absDy)) {
    width = Math.max(absDx, 1);
    height = width / ratio;
  } else {
    height = Math.max(absDy, 1);
    width = height * ratio;
  }
  return clampRect({
    x: dx >= 0 ? start.x : start.x - width,
    y: dy >= 0 ? start.y : start.y - height,
    width,
    height,
  }, imageWidth, imageHeight);
}

function resizeFromCenter(factor) {
  if (!state.image || !state.rect) return;
  const centerX = state.rect.x + state.rect.width / 2;
  const centerY = state.rect.y + state.rect.height / 2;
  const width = state.rect.width * factor;
  const height = width / aspect();
  state.rect = clampRect({
    x: centerX - width / 2,
    y: centerY - height / 2,
    width,
    height,
  }, state.image.naturalWidth, state.image.naturalHeight);
  state.saved = false;
  updateInspector();
  draw();
}

function resizeCanvasToDisplay() {
  const rect = canvas.getBoundingClientRect();
  const deviceRatio = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.floor(rect.width * deviceRatio));
  const height = Math.max(1, Math.floor(rect.height * deviceRatio));
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }
}

function imageToCanvas(point) {
  return {
    x: state.view.left + point.x * state.view.scale,
    y: state.view.top + point.y * state.view.scale,
  };
}

function canvasToImage(event) {
  const bounds = canvas.getBoundingClientRect();
  const ratio = canvas.width / bounds.width;
  const x = (event.clientX - bounds.left) * ratio;
  const y = (event.clientY - bounds.top) * ratio;
  return {
    x: clamp((x - state.view.left) / state.view.scale, 0, state.image.naturalWidth),
    y: clamp((y - state.view.top) / state.view.scale, 0, state.image.naturalHeight),
    canvasX: x,
    canvasY: y,
  };
}

function rectCanvasBounds() {
  const topLeft = imageToCanvas({ x: state.rect.x, y: state.rect.y });
  const bottomRight = imageToCanvas({
    x: state.rect.x + state.rect.width,
    y: state.rect.y + state.rect.height,
  });
  return { x1: topLeft.x, y1: topLeft.y, x2: bottomRight.x, y2: bottomRight.y };
}

function hitTest(point) {
  const b = rectCanvasBounds();
  const handles = [
    ["resize_nw", b.x1, b.y1],
    ["resize_ne", b.x2, b.y1],
    ["resize_sw", b.x1, b.y2],
    ["resize_se", b.x2, b.y2],
  ];
  for (const [mode, x, y] of handles) {
    if (Math.abs(point.canvasX - x) <= 12 && Math.abs(point.canvasY - y) <= 12) {
      return mode;
    }
  }
  if (point.canvasX >= b.x1 && point.canvasX <= b.x2 && point.canvasY >= b.y1 && point.canvasY <= b.y2) {
    return "move";
  }
  return "create";
}

function draw() {
  resizeCanvasToDisplay();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#0f1115";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (!state.image) return;

  const padding = 24 * (window.devicePixelRatio || 1);
  const scale = Math.min(
    (canvas.width - padding * 2) / state.image.naturalWidth,
    (canvas.height - padding * 2) / state.image.naturalHeight,
    1
  );
  state.view.scale = Math.max(scale, 0.05);
  state.view.width = state.image.naturalWidth * state.view.scale;
  state.view.height = state.image.naturalHeight * state.view.scale;
  state.view.left = (canvas.width - state.view.width) / 2;
  state.view.top = (canvas.height - state.view.height) / 2;

  ctx.drawImage(state.image, state.view.left, state.view.top, state.view.width, state.view.height);
  const b = rectCanvasBounds();
  const left = state.view.left;
  const top = state.view.top;
  const right = state.view.left + state.view.width;
  const bottom = state.view.top + state.view.height;

  ctx.save();
  ctx.fillStyle = "rgba(0, 0, 0, 0.58)";
  ctx.fillRect(left, top, right - left, b.y1 - top);
  ctx.fillRect(left, b.y2, right - left, bottom - b.y2);
  ctx.fillRect(left, b.y1, b.x1 - left, b.y2 - b.y1);
  ctx.fillRect(b.x2, b.y1, right - b.x2, b.y2 - b.y1);

  const color = state.saved ? "#f6c453" : "#71c7ec";
  ctx.strokeStyle = color;
  ctx.lineWidth = 3;
  ctx.strokeRect(b.x1, b.y1, b.x2 - b.x1, b.y2 - b.y1);
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(b.x1 + (b.x2 - b.x1) / 3, b.y1);
  ctx.lineTo(b.x1 + (b.x2 - b.x1) / 3, b.y2);
  ctx.moveTo(b.x1 + (b.x2 - b.x1) * 2 / 3, b.y1);
  ctx.lineTo(b.x1 + (b.x2 - b.x1) * 2 / 3, b.y2);
  ctx.moveTo(b.x1, b.y1 + (b.y2 - b.y1) / 3);
  ctx.lineTo(b.x2, b.y1 + (b.y2 - b.y1) / 3);
  ctx.moveTo(b.x1, b.y1 + (b.y2 - b.y1) * 2 / 3);
  ctx.lineTo(b.x2, b.y1 + (b.y2 - b.y1) * 2 / 3);
  ctx.stroke();
  for (const [x, y] of [[b.x1, b.y1], [b.x2, b.y1], [b.x1, b.y2], [b.x2, b.y2]]) {
    ctx.fillStyle = color;
    ctx.fillRect(x - 5, y - 5, 10, 10);
    ctx.strokeStyle = "#111";
    ctx.strokeRect(x - 5, y - 5, 10, 10);
  }
  ctx.restore();
}

function updateList() {
  els.taskList.innerHTML = "";
  state.tasks.forEach((task, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `task-item${index === state.index ? " active" : ""}${task.saved ? " saved" : ""}`;
    button.innerHTML = `<span class="stem">${task.stem}</span><span class="path">${task.width}x${task.height}</span>`;
    button.addEventListener("click", () => loadTask(index));
    els.taskList.appendChild(button);
  });
}

function updateInspector() {
  const task = state.tasks[state.index];
  if (!task || !state.rect) return;
  els.title.textContent = `${state.index + 1}/${state.tasks.length} ${task.stem}`;
  els.sourcePath.textContent = task.pngPath;
  els.outputPath.textContent = task.ddsPath;
  els.imageMeta.textContent = `${task.width}x${task.height} (${state.saved ? "saved crop" : "not saved"})`;
  els.cropMeta.textContent = `${state.rect.x.toFixed(1)}, ${state.rect.y.toFixed(1)}, ${state.rect.width.toFixed(1)} x ${state.rect.height.toFixed(1)}`;
  els.prevBtn.disabled = state.index <= 0;
  els.nextBtn.disabled = state.index >= state.tasks.length - 1;
}

async function loadInitial() {
  const payload = await api("/api/tasks");
  els.dataPath.textContent = `Data: ${payload.dataPath}`;
  state.tasks = payload.tasks;
  els.log.textContent = (payload.logs || []).join("\n");
  if (!state.tasks.length) {
    setStatus("No generated wonder PNG files were found.", true);
    draw();
    return;
  }
  updateList();
  await loadTask(0);
}

async function refreshTask(index) {
  const payload = await api(`/api/task/${index}`);
  state.tasks[index] = payload;
  if (index === state.index) {
    state.rect = { ...payload.rect };
    state.saved = payload.saved;
    updateInspector();
    draw();
  }
  updateList();
}

async function loadTask(index) {
  state.index = clamp(index, 0, state.tasks.length - 1);
  const task = await api(`/api/task/${state.index}`);
  state.tasks[state.index] = task;
  state.rect = { ...task.rect };
  state.saved = task.saved;
  const image = new Image();
  image.onload = () => {
    state.image = image;
    updateList();
    updateInspector();
    setStatus("Drag the frame, drag a corner to resize, use mouse wheel to zoom, or press Enter to save and advance.");
    draw();
  };
  image.onerror = () => setStatus(`Could not load ${task.pngPath}`, true);
  image.src = `/api/image/${state.index}?v=${Date.now()}`;
}

async function saveAndMaybeNext(advance) {
  if (!state.rect || !state.tasks.length) return;
  const payload = await api(`/api/save/${state.index}`, {
    method: "POST",
    body: JSON.stringify({ rect: state.rect }),
  });
  state.tasks[state.index] = payload.task;
  setStatus(payload.message);
  updateList();
  if (advance && state.index + 1 < state.tasks.length) {
    await loadTask(state.index + 1);
  } else {
    await refreshTask(state.index);
  }
}

async function removeCrop() {
  if (!state.tasks.length) return;
  const payload = await api(`/api/remove/${state.index}`, { method: "POST", body: "{}" });
  state.tasks[state.index] = payload.task;
  state.rect = { ...payload.task.rect };
  state.saved = false;
  setStatus(payload.message);
  updateList();
  updateInspector();
  draw();
}

async function applyCrops() {
  els.applyBtn.disabled = true;
  setStatus("Rebuilding DDS files...");
  try {
    const payload = await api("/api/apply", { method: "POST", body: "{}" });
    els.log.textContent = (payload.logs || []).join("\n");
    setStatus(payload.message);
  } finally {
    els.applyBtn.disabled = false;
  }
}

canvas.addEventListener("pointerdown", (event) => {
  if (!state.image || !state.rect) return;
  canvas.setPointerCapture(event.pointerId);
  const point = canvasToImage(event);
  state.drag = {
    mode: hitTest(point),
    start: point,
    startRect: { ...state.rect },
  };
});

canvas.addEventListener("pointermove", (event) => {
  if (!state.drag || !state.image) return;
  const point = canvasToImage(event);
  const start = state.drag.start;
  const rect = state.drag.startRect;
  if (state.drag.mode === "move") {
    state.rect = clampRect({
      x: rect.x + point.x - start.x,
      y: rect.y + point.y - start.y,
      width: rect.width,
      height: rect.height,
    }, state.image.naturalWidth, state.image.naturalHeight);
  } else if (state.drag.mode.startsWith("resize")) {
    const anchors = {
      resize_nw: { x: rect.x + rect.width, y: rect.y + rect.height },
      resize_ne: { x: rect.x, y: rect.y + rect.height },
      resize_sw: { x: rect.x + rect.width, y: rect.y },
      resize_se: { x: rect.x, y: rect.y },
    };
    state.rect = rectFromPoints(anchors[state.drag.mode], point, state.image.naturalWidth, state.image.naturalHeight);
  } else {
    state.rect = rectFromPoints(start, point, state.image.naturalWidth, state.image.naturalHeight);
  }
  state.saved = false;
  updateInspector();
  draw();
});

canvas.addEventListener("pointerup", () => {
  state.drag = null;
});

canvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  resizeFromCenter(event.deltaY < 0 ? 1.08 : 0.92);
}, { passive: false });

window.addEventListener("resize", draw);
document.addEventListener("keydown", async (event) => {
  try {
    if (event.key === "Enter") {
      event.preventDefault();
      await saveAndMaybeNext(true);
    } else if (event.key === "ArrowLeft") {
      await loadTask(state.index - 1);
    } else if (event.key === "ArrowRight") {
      await loadTask(state.index + 1);
    }
  } catch (error) {
    setStatus(error.message, true);
  }
});

els.prevBtn.addEventListener("click", () => loadTask(state.index - 1).catch(error => setStatus(error.message, true)));
els.nextBtn.addEventListener("click", () => loadTask(state.index + 1).catch(error => setStatus(error.message, true)));
els.saveBtn.addEventListener("click", () => saveAndMaybeNext(true).catch(error => setStatus(error.message, true)));
els.removeBtn.addEventListener("click", () => removeCrop().catch(error => setStatus(error.message, true)));
els.applyBtn.addEventListener("click", () => applyCrops().catch(error => setStatus(error.message, true)));

loadInitial().catch(error => setStatus(error.message, true));
"""


def run_server(host: str, port: int, open_browser: bool) -> int:
    tasks = build_image_tasks()
    if not tasks:
        print("No generated wonder PNG files were found. Generate PNGs first, then rerun this tool.", file=sys.stderr)
        return 1

    state = CropperState(tasks)
    handler_class = build_handler(state)
    server = ThreadingHTTPServer((host, port), handler_class)
    url = f"http://{host}:{server.server_port}/"
    print(f"Wonder Image Cropper Web running at {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Wonder Image Cropper Web.")
    finally:
        server.server_close()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.apply:
        return apply_current_crop_data()
    return run_server(args.host, args.port, not args.no_browser)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - command-line helper should fail tersely.
        print(f"[error] {exc}", file=sys.stderr)
        raise SystemExit(1) from None
