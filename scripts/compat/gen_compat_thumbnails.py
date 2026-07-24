import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
ED_THUMBNAIL = REPO_ROOT / "src_engineering_department" / ".metadata" / "thumbnail.png"
OUTPUT_SIZE = (640, 640)
# Steam Workshop rejects preview images over 1 MiB; keep real margin below that.
MAX_BYTES = 900_000

# (external mod thumbnail, output submod thumbnail)
TARGETS = [
    (
        REPO_ROOT / "reference_mods" / "3735059838" / ".metadata" / "thumbnail.png",
        REPO_ROOT / "submods" / "tv_meiou_and_taxes_compat" / ".metadata" / "thumbnail.png",
    ),
    (
        REPO_ROOT / "reference_mods" / "3698931463" / ".metadata" / "thumbnail.png",
        REPO_ROOT / "submods" / "tv_standard_of_living_compat" / ".metadata" / "thumbnail.png",
    ),
    (
        REPO_ROOT / "reference_mods" / "3613232232" / ".metadata" / "thumbnail.png",
        REPO_ROOT / "submods" / "tv_prosper_or_perish_compat" / ".metadata" / "thumbnail.png",
    ),
]


def load_square(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB").resize(OUTPUT_SIZE, Image.LANCZOS)


def diagonal_mask() -> Image.Image:
    # 255 (Great Project side) above/right of the top-left -> bottom-right diagonal,
    # 0 (external mod side) below/left of it.
    width, height = OUTPUT_SIZE
    mask = Image.new("L", OUTPUT_SIZE, 0)
    pixels = mask.load()
    for y in range(height):
        for x in range(width):
            if x * height > y * width:
                pixels[x, y] = 255
    return mask


def generate(external_thumbnail: Path, out_path: Path, mask: Image.Image) -> None:
    ed_img = load_square(ED_THUMBNAIL)
    ext_img = load_square(external_thumbnail)
    composited = Image.composite(ed_img, ext_img, mask)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    composited.save(out_path, format="PNG", optimize=True, compress_level=9)
    size = out_path.stat().st_size
    if size > MAX_BYTES:
        raise RuntimeError(
            f"{out_path.relative_to(REPO_ROOT)} is {size} bytes, over the {MAX_BYTES}-byte "
            "budget -- shrink OUTPUT_SIZE before shipping (Steam Workshop rejects >1 MiB previews)."
        )
    print(f"Wrote {out_path.relative_to(REPO_ROOT)} ({size} bytes)")


def main() -> None:
    mask = diagonal_mask()
    for external_thumbnail, out_path in TARGETS:
        generate(external_thumbnail, out_path, mask)


if __name__ == "__main__":
    main()
