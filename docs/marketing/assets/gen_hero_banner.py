"""One-off generator for the Great Project Steam Workshop page banners
(hero + per-section header graphics), EN + ZH.

This page is for the standalone Engineering Department mod ("Great Project"),
not the main Towards Victory mod, so none of these banners should carry the
Towards Victory wordmark.

Not a mod-content generator (no `src/`/`data/` involvement), so it does not
follow the project's `scripts/` 1:1 generator convention or the `eu5` conda
env policy. Run with a Python that has Pillow with a working FreeType build,
e.g. the `Research` conda env (base anaconda3's Pillow lacks `_imagingft`,
and `eu5` has no Pillow at all):

    C:\\Users\\Hades\\anaconda3\\envs\\Research\\python.exe docs\\marketing\\assets\\gen_hero_banner.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT_DIR = Path(__file__).resolve().parent

HERO_SIZE = (1920, 420)
SECTION_SIZE = (1200, 170)

FONT_DIR = Path("C:/Windows/Fonts")
FONT_EN = FONT_DIR / "georgiab.ttf"
FONT_ZH = FONT_DIR / "msyhbd.ttc"

BG_TOP = (16, 21, 30)
BG_BOTTOM = (6, 8, 12)
FRAME_GOLD = (176, 138, 66)
TITLE_COLOR = (238, 228, 206)
SHADOW_COLOR = (0, 0, 0)


def vertical_gradient(width: int, height: int, top: tuple, bottom: tuple) -> Image.Image:
    img = Image.new("RGB", (width, height), top)
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / max(height - 1, 1)
        r = round(top[0] + (bottom[0] - top[0]) * t)
        g = round(top[1] + (bottom[1] - top[1]) * t)
        b = round(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img


def add_vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    w, h = img.size
    vignette = Image.new("L", (w, h), 0)
    vdraw = ImageDraw.Draw(vignette)
    max_dim = (w**2 + h**2) ** 0.5 / 2
    cx, cy = w / 2, h / 2
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            val = max(0, 255 - int(255 * strength * (dist / max_dim) ** 2))
            vdraw.rectangle([x, y, x + 1, y + 1], fill=val)
    vignette = vignette.filter(ImageFilter.GaussianBlur(40))
    dark = Image.new("RGB", img.size, (0, 0, 0))
    return Image.composite(img, dark, vignette)


def draw_diamond(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill) -> None:
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=fill)


def draw_frame(draw: ImageDraw.ImageDraw, w: int, h: int, outer: int = 36, inner: int = 44) -> None:
    draw.rectangle([outer, outer, w - outer, h - outer], outline=FRAME_GOLD, width=2)
    draw.rectangle([inner, inner, w - inner, h - inner], outline=FRAME_GOLD, width=1)
    for cx, cy in [(outer, outer), (w - outer, outer), (outer, h - outer), (w - outer, h - outer)]:
        draw_diamond(draw, cx, cy, 7, FRAME_GOLD)
    draw_diamond(draw, w // 2, outer, 6, FRAME_GOLD)
    draw_diamond(draw, w // 2, h - outer, 6, FRAME_GOLD)


def tracked_text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, tracking: int) -> float:
    if not text:
        return 0
    total = 0
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        total += (bbox[2] - bbox[0]) + tracking
    return total - tracking


def draw_tracked_text(
    draw: ImageDraw.ImageDraw,
    center_x: float,
    y: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill,
    tracking: int = 0,
    shadow_offset: int = 3,
) -> float:
    total_w = tracked_text_width(draw, text, font, tracking)
    x = center_x - total_w / 2
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        ch_w = bbox[2] - bbox[0]
        draw.text((x + shadow_offset, y + shadow_offset), ch, font=font, fill=SHADOW_COLOR)
        draw.text((x, y), ch, font=font, fill=fill)
        x += ch_w + tracking
    return total_w


def centered_text(
    draw: ImageDraw.ImageDraw,
    center_x: float,
    y: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill,
    shadow_offset: int = 2,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = center_x - w / 2 - bbox[0]
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=SHADOW_COLOR)
    draw.text((x, y), text, font=font, fill=fill)


def title_dims(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, is_zh: bool, tracking: int) -> tuple:
    if is_zh:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    w = tracked_text_width(draw, text, font, tracking)
    bbox = draw.textbbox((0, 0), text, font=font)
    return w, bbox[3] - bbox[1]


def draw_title(
    draw: ImageDraw.ImageDraw,
    cx: float,
    y: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill,
    is_zh: bool,
    tracking: int,
) -> None:
    if is_zh:
        centered_text(draw, cx, y, text, font, fill)
    else:
        draw_tracked_text(draw, cx, y, text, font, fill, tracking=tracking)


def build_hero(text: str, is_zh: bool, out_name: str) -> None:
    w, h = HERO_SIZE
    img = vertical_gradient(w, h, BG_TOP, BG_BOTTOM)
    img = add_vignette(img, strength=0.45)
    draw = ImageDraw.Draw(img)
    draw_frame(draw, w, h)

    font_path = FONT_ZH if is_zh else FONT_EN
    size = 150 if is_zh else 128
    font = ImageFont.truetype(str(font_path), size)
    tracking = 0 if is_zh else 8

    _, text_h = title_dims(draw, text, font, is_zh, tracking)
    title_y = h / 2 - text_h / 2 - (10 if is_zh else 0)
    draw_title(draw, w / 2, title_y, text, font, TITLE_COLOR, is_zh, tracking)

    out_path = OUT_DIR / out_name
    img.convert("RGB").save(out_path, "PNG")
    print(f"Wrote {out_path}")


def build_section(text: str, is_zh: bool, out_name: str) -> None:
    w, h = SECTION_SIZE
    img = vertical_gradient(w, h, BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)

    font_path = FONT_ZH if is_zh else FONT_EN
    size = 58 if is_zh else 50
    font = ImageFont.truetype(str(font_path), size)
    tracking = 0 if is_zh else 5

    cx = w / 2
    text_w, text_h = title_dims(draw, text, font, is_zh, tracking)
    title_y = h / 2 - text_h / 2 - (4 if is_zh else 0)
    draw_title(draw, cx, title_y, text, font, TITLE_COLOR, is_zh, tracking)

    rule_y = h / 2
    gap = 24
    half_w = text_w / 2
    line_len = 90
    draw.line([(cx - half_w - gap - line_len, rule_y), (cx - half_w - gap, rule_y)], fill=FRAME_GOLD, width=2)
    draw.line([(cx + half_w + gap, rule_y), (cx + half_w + gap + line_len, rule_y)], fill=FRAME_GOLD, width=2)
    draw_diamond(draw, cx - half_w - gap - line_len - 14, rule_y, 5, FRAME_GOLD)
    draw_diamond(draw, cx + half_w + gap + line_len + 14, rule_y, 5, FRAME_GOLD)

    out_path = OUT_DIR / out_name
    img.convert("RGB").save(out_path, "PNG")
    print(f"Wrote {out_path}")


SECTIONS = [
    ("overview", "Overview", "简介"),
    ("core_features", "Core Features", "核心内容"),
    ("six_stages", "The Six Stages", "六个阶段详解"),
    ("compatibility", "Compatibility", "兼容性"),
    ("credits", "Credits", "致谢"),
    ("links", "Links", "外部链接"),
]


def main() -> None:
    build_hero("GREAT PROJECT", False, "hero_banner_en.png")
    build_hero("伟大工程", True, "hero_banner_zh.png")

    for slug, en_text, zh_text in SECTIONS:
        build_section(en_text.upper(), False, f"section_{slug}_en.png")
        build_section(zh_text, True, f"section_{slug}_zh.png")


if __name__ == "__main__":
    main()
