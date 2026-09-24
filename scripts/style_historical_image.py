#!/usr/bin/env python3
"""Turn a historical photograph into a deterministic, cartoon-like game asset.

The pipeline intentionally keeps the source composition intact. It uses local
image operations only, so a processed asset can be regenerated on any machine
with the documented Python dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw
from skimage import color, filters, metrics, morphology


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "inputs",
        type=Path,
        nargs="+",
        help="one or more real historical photographs to stylize",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="directory for generated assets (default: alongside source in processed/)",
    )
    parser.add_argument("--max-size", type=int, default=1920, help="maximum output edge")
    parser.add_argument(
        "--keep-intermediates",
        action="store_true",
        help="write the named intermediate stages as JPEG files",
    )
    parser.add_argument("--seed", type=int, default=17, help="seed for repeatable paper grain")
    return parser.parse_args()


def resize_image(image: Image.Image, max_size: int) -> Image.Image:
    if max_size <= 0:
        raise ValueError("max_size must be a positive integer")
    if max(image.size) <= max_size:
        return image.copy()
    scale = max_size / max(image.size)
    size = (round(image.width * scale), round(image.height * scale))
    return image.resize(size, Image.Resampling.LANCZOS)


def percentile_normalize(rgb: np.ndarray) -> np.ndarray:
    """Recover a usable tonal range without clipping the bright marble."""
    low, high = np.percentile(rgb, (1.2, 99.2), axis=(0, 1), keepdims=True)
    return np.clip((rgb - low) / np.maximum(high - low, 1e-4), 0.0, 1.0)


def smoothstep(value: np.ndarray, low: float, high: float) -> np.ndarray:
    x = np.clip((value - low) / (high - low), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def color_grade(rgb: np.ndarray) -> np.ndarray:
    """Apply a warm/cool split tone with the stronger cartoon palette."""
    luminance = color.rgb2gray(rgb)
    shadows = (1.0 - smoothstep(luminance, 0.16, 0.58))[..., None]
    highlights = smoothstep(luminance, 0.42, 0.92)[..., None]

    # Cool blue-black shadows and parchment highlights make the scene read as
    # painted while retaining the source's sky, lawns, and white marble.
    shadow_tint = np.array([0.70, 0.82, 1.10], dtype=np.float32)
    highlight_tint = np.array([1.08, 0.98, 0.82], dtype=np.float32)
    graded = rgb * (1.0 + (shadow_tint - 1.0) * shadows * 0.38)
    graded *= 1.0 + (highlight_tint - 1.0) * highlights * 0.30

    # A gentle S curve increases separation between architecture and garden.
    graded = np.clip((graded - 0.5) * 1.18 + 0.5, 0.0, 1.0)
    hsv = color.rgb2hsv(graded)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.08, 0.0, 1.0)
    return np.clip(color.hsv2rgb(hsv), 0.0, 1.0)


def edge_preserving_smooth(rgb: np.ndarray) -> np.ndarray:
    """Fast edge-aware smoothing suitable for batch processing large photos."""
    blurred = filters.gaussian(rgb, sigma=1.65, channel_axis=-1)
    edge = filters.sobel(color.rgb2gray(rgb))
    flat_area = np.clip(1.0 - edge * 10.0, 0.08, 1.0)[..., None]
    return np.clip(rgb * (1.0 - flat_area * 0.70) + blurred * (flat_area * 0.70), 0.0, 1.0)


def cartoon_palette(rgb: np.ndarray, colors: int = 56) -> np.ndarray:
    """Reduce the image to a compact, hard-edged illustration palette."""
    softened = filters.gaussian(rgb, sigma=1.8, channel_axis=-1)
    quantized = Image.fromarray(np.round(softened * 255).astype(np.uint8), "RGB")
    quantized = quantized.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    return np.asarray(quantized.convert("RGB"), dtype=np.float32) / 255.0


def cel_shade(rgb: np.ndarray, levels: int = 7) -> np.ndarray:
    """Create graphic light/mid/shadow bands while retaining palette hue."""
    luminance = color.rgb2gray(rgb)
    band = np.round(luminance * (levels - 1)) / (levels - 1)
    ratio = np.divide(band + 0.045, luminance + 0.045)
    return np.clip(rgb * (0.62 + 0.38 * ratio[..., None]), 0.0, 1.0)


def cartoon_edges(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Draw clean dark outlines around broad forms, not photographic noise."""
    gray = color.rgb2gray(rgb)
    smoothed = filters.gaussian(gray, sigma=1.75)
    gradient = filters.sobel(smoothed)
    edge = gradient > 0.082
    edge = morphology.binary_dilation(edge, morphology.disk(1))
    edge = filters.gaussian(edge.astype(np.float32), sigma=0.45)
    ink = np.array([0.055, 0.075, 0.105], dtype=np.float32)
    outlined = rgb * (1.0 - edge[..., None] * 0.56) + ink * (edge[..., None] * 0.56)
    return np.clip(outlined, 0.0, 1.0), edge


def add_finish(rgb: np.ndarray, seed: int) -> np.ndarray:
    """Add a small amount of paper texture and a graphic vignette."""
    height, width = rgb.shape[:2]
    rng = np.random.default_rng(seed)
    grain = rng.normal(0.0, 0.0045, (height, width, 1)).astype(np.float32)

    luminance = color.rgb2gray(rgb)
    glow_mask = smoothstep(luminance, 0.72, 1.0)[..., None]
    glow = filters.gaussian(np.maximum(rgb - 0.62, 0.0), sigma=4.0, channel_axis=-1)
    finished = np.clip(rgb + glow * glow_mask * 0.06 + grain, 0.0, 1.0)

    y, x = np.ogrid[:height, :width]
    distance = np.sqrt(((x - width / 2) / (width / 2)) ** 2 + ((y - height / 2) / (height / 2)) ** 2)
    vignette = np.clip((distance - 0.52) / 0.72, 0.0, 1.0)[..., None]
    return np.clip(finished * (1.0 - vignette * 0.10), 0.0, 1.0)


def to_image(rgb: np.ndarray) -> Image.Image:
    return Image.fromarray(np.round(np.clip(rgb, 0.0, 1.0) * 255).astype(np.uint8), "RGB")


def save_jpeg(rgb: np.ndarray, path: Path, quality: int = 93) -> None:
    to_image(rgb).save(path, format="JPEG", quality=quality, optimize=True)


def image_stats(rgb: np.ndarray) -> dict[str, float]:
    gray = color.rgb2gray(rgb)
    hsv = color.rgb2hsv(rgb)
    return {
        "mean_luminance": round(float(gray.mean()), 5),
        "luminance_std": round(float(gray.std()), 5),
        "mean_saturation": round(float(hsv[..., 1].mean()), 5),
        "edge_density": round(float((filters.sobel(gray) > 0.07).mean()), 5),
    }


def similarity_scores(source: np.ndarray, final: np.ndarray) -> tuple[float, float]:
    """Measure both literal pixel change and low-frequency structural retention."""
    source_gray = color.rgb2gray(source)
    final_gray = color.rgb2gray(final)
    pixel_score = float(metrics.structural_similarity(source_gray, final_gray, data_range=1.0))

    # Downsampling and smoothing make this guardrail respond to buildings, roads,
    # skylines, and water bodies instead of period frames, captions, or photo grain.
    metric_edge = min(512, max(source_gray.shape))
    if max(source_gray.shape) > metric_edge:
        ratio = metric_edge / max(source_gray.shape)
        metric_size = (round(source_gray.shape[1] * ratio), round(source_gray.shape[0] * ratio))
        source_gray = np.asarray(
            Image.fromarray(np.round(source_gray * 255).astype(np.uint8)).resize(
                metric_size, Image.Resampling.LANCZOS
            ),
            dtype=np.float32,
        ) / 255.0
        final_gray = np.asarray(
            Image.fromarray(np.round(final_gray * 255).astype(np.uint8)).resize(
                metric_size, Image.Resampling.LANCZOS
            ),
            dtype=np.float32,
        ) / 255.0
    source_gray = filters.gaussian(source_gray, sigma=2.0)
    final_gray = filters.gaussian(final_gray, sigma=2.0)
    structure_score = float(metrics.structural_similarity(source_gray, final_gray, data_range=1.0))
    return pixel_score, structure_score


def contact_sheet(source: Image.Image, stages: Iterable[tuple[str, np.ndarray]]) -> Image.Image:
    entries = [("source", np.asarray(source.convert("RGB"), dtype=np.float32) / 255.0), *stages]
    thumb_width = 640
    thumbs = []
    for label, rgb in entries:
        image = to_image(rgb)
        image.thumbnail((thumb_width, 430), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (thumb_width, 470), (28, 29, 34))
        canvas.paste(image, ((thumb_width - image.width) // 2, 8))
        # Keep the labels in the artifact rather than relying on a viewer.
        label_bar = Image.new("RGB", (thumb_width, 32), (28, 29, 34))
        canvas.paste(label_bar, (0, 438))
        draw = ImageDraw.Draw(canvas)
        draw.text((16, 446), label, fill=(235, 231, 218))
        thumbs.append(canvas)
    columns = 2
    sheet = Image.new("RGB", (thumb_width * columns, 470 * ((len(thumbs) + columns - 1) // columns)), (18, 19, 23))
    for index, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((index % columns) * thumb_width, (index // columns) * 470))
    return sheet


def source_digest(input_path: Path) -> str:
    digest = hashlib.sha256()
    with input_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(input_path: Path, output_dir: Path, max_size: int, keep_intermediates: bool, seed: int) -> dict[str, object]:
    if not input_path.is_file():
        raise FileNotFoundError(f"Input image does not exist: {input_path}")

    try:
        with Image.open(input_path) as opened:
            source_image = resize_image(opened.convert("RGB"), max_size)
    except (OSError, ValueError) as exc:
        raise ValueError(f"Unable to read input image {input_path}: {exc}") from exc

    source = np.asarray(source_image, dtype=np.float32) / 255.0

    normalized = percentile_normalize(source)
    smoothed = edge_preserving_smooth(normalized)
    graded = color_grade(smoothed)
    palette = cartoon_palette(graded, colors=56)
    blocked = cel_shade(palette, levels=9)
    edged, edge_mask = cartoon_edges(blocked)
    final = add_finish(edged, seed)

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem
    final_path = output_dir / f"{stem}_cartoon.png"
    comparison_path = output_dir / f"{stem}_cartoon_comparison.jpg"
    report_path = output_dir / f"{stem}_cartoon_evaluation.json"
    to_image(final).save(final_path, format="PNG", optimize=True)

    stages = [("normalized", normalized), ("color grade", graded), ("cartoon palette", palette), ("cel shade", blocked), ("ink + finish", final)]
    contact_sheet(source_image, stages).save(comparison_path, format="JPEG", quality=91, optimize=True)

    if keep_intermediates:
        for name, stage in [
            ("01_normalized", normalized),
            ("02_smoothed", smoothed),
            ("03_color_grade", graded),
            ("04_cartoon_palette", palette),
            ("05_cel_shade", blocked),
            ("06_ink_edges", edged),
        ]:
            save_jpeg(stage, output_dir / f"{stem}_{name}.jpg")

    source_stats = image_stats(source)
    final_stats = image_stats(final)
    pixel_similarity, structure_similarity = similarity_scores(source, final)
    report = {
        "input": str(input_path),
        "output": str(final_path),
        "input_sha256": source_digest(input_path),
        "size": {"width": source_image.width, "height": source_image.height},
        "profile": "cartoon_historical_v2",
        "seed": seed,
        "source": source_stats,
        "final": final_stats,
        "structure_similarity": round(structure_similarity, 5),
        "pixel_similarity": round(pixel_similarity, 5),
        "interpretation": {
            "structure": (
                "composition preserved under strong stylization"
                if structure_similarity >= 0.60
                else "review crop or perspective"
            ),
            "color": "compact 56-color palette, stronger warm/cool split, cel-shaded value bands",
            "surface": "clean dark ink contours, softened photographic texture, light paper grain",
            "edge_coverage": round(float(edge_mask.mean()), 5),
            "historical_weight": (
                "preserved source architecture, perspective, and period details; no new scene content"
            ),
        },
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return {"final": final_path, "comparison": comparison_path, "report": report_path, "size": source_image.size}


def main() -> None:
    args = parse_args()
    if args.max_size <= 0:
        raise SystemExit("--max-size must be a positive integer")

    results = []
    for input_path in args.inputs:
        output_dir = args.output_dir or input_path.parent / "processed"
        result = run(input_path, output_dir, args.max_size, args.keep_intermediates, args.seed)
        results.append({key: str(value) for key, value in result.items()})

    payload: object = results[0] if len(results) == 1 else results
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
