#!/usr/bin/env python3
"""Generate the small Eureka condition icons used by the Advance cards."""

from __future__ import annotations

import math
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from dds_image_lib import RgbaImage, encode_png_rgba, resize_rgba, write_dds  # noqa: E402


SIZE = 128
SUPERSAMPLE = 4
GOLD = (224, 194, 122)
BLUE = (42, 121, 229)


def _smooth_edge(distance: float, radius: float, width: float) -> float:
    edge = (radius + width * 0.5 - distance) / max(width, 0.001)
    return max(0.0, min(1.0, edge))


def _ring_alpha(distance: float, radius: float, width: float) -> float:
    return _smooth_edge(abs(distance - radius), 0.0, width)


def _put_pixel(pixel: bytearray, x: int, y: int, color: tuple[int, int, int], alpha: float) -> None:
    if alpha <= 0.0:
        return
    pos = (y * SIZE * SUPERSAMPLE + x) * 4
    existing_alpha = pixel[pos + 3] / 255.0
    combined = alpha + existing_alpha * (1.0 - alpha)
    if combined <= 0.0:
        return
    for channel, value in enumerate(color):
        old = pixel[pos + channel]
        pixel[pos + channel] = int(round((value * alpha + old * existing_alpha * (1.0 - alpha)) / combined))
    pixel[pos + 3] = int(round(combined * 255.0))


def _draw_icon(active: bool) -> RgbaImage:
    width = height = SIZE * SUPERSAMPLE
    pixels = bytearray(width * height * 4)
    cx = cy = (width - 1) / 2.0
    scale = float(SUPERSAMPLE)

    for y in range(height):
        for x in range(width):
            dx = (x - cx) / scale
            dy = (y - cy) / scale
            distance = math.hypot(dx, dy)

            # Civilization-style ornamental seal: a crisp double outline and a
            # blue enamel interior only in the active state.
            outer = _ring_alpha(distance, 50.0, 4.0)
            inner = _ring_alpha(distance, 42.0, 2.0)
            if outer:
                _put_pixel(pixels, x, y, GOLD, outer * 0.95)
            if inner:
                _put_pixel(pixels, x, y, GOLD, inner * 0.72)
            if active and distance < 40.0:
                fill_alpha = _smooth_edge(distance, 40.0, 2.0) * 0.92
                blue_mix = max(0.0, min(1.0, 1.0 - distance / 52.0))
                fill = tuple(int(BLUE[i] + (92 - BLUE[i]) * blue_mix) for i in range(3))
                _put_pixel(pixels, x, y, fill, fill_alpha)

            # Four-point knowledge spark in the centre.
            spark = max(abs(dx), abs(dy) * 0.45) + max(abs(dy), abs(dx) * 0.45)
            spark_alpha = _smooth_edge(spark, 8.0 if active else 7.0, 2.0)
            if spark_alpha:
                _put_pixel(pixels, x, y, GOLD if not active else (242, 226, 171), spark_alpha * 0.95)

    # Eight tiny cardinal/diagonal ticks reinforce the hand-crafted UI seal.
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        tx = cx + math.cos(radians) * 46.0 * scale
        ty = cy + math.sin(radians) * 46.0 * scale
        for oy in range(-2 * SUPERSAMPLE, 2 * SUPERSAMPLE + 1):
            for ox in range(-2 * SUPERSAMPLE, 2 * SUPERSAMPLE + 1):
                px = int(round(tx + ox))
                py = int(round(ty + oy))
                if 0 <= px < width and 0 <= py < height:
                    radius = math.hypot(ox / scale, oy / scale)
                    _put_pixel(pixels, px, py, GOLD, _smooth_edge(radius, 1.6, 1.5) * 0.8)

    supersampled = RgbaImage(width=width, height=height, rgba=bytes(pixels))
    return resize_rgba(supersampled, SIZE, SIZE, "stretch")


def main() -> None:
    output_dir = REPO_ROOT / "src_eureka" / "main_menu" / "gfx" / "interface" / "icons" / "eureka"
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = {
        "tv_eureka_condition.dds": _draw_icon(active=False),
        "tv_eureka_condition_active.dds": _draw_icon(active=True),
    }
    for filename, image in targets.items():
        path = output_dir / filename
        write_dds(image, path, dds_format="DXT5", overwrite=True, mipmaps=True, mipmap_min_dimension=4)
        print(f"OK {path.relative_to(REPO_ROOT)}")
        preview_path = path.with_suffix(".png")
        preview_path.write_bytes(encode_png_rgba(image))
        print(f"OK {preview_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
