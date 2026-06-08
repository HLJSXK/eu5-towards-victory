import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ceremony_styles,
    load_all_wonder_mechanics_data,
    render_header,
)

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "common" / "game_concepts" / "tv_engineering_department_wonder_mechanics_concepts.txt"
SCRIPT_REL = "scripts/main_menu/common/game_concepts/gen_tv_engineering_department_wonder_mechanics_concepts.py"

ICONS = {
    "infrastructure_category": "gfx/interface/icons/location_icons/new/prosperity.dds",
    "military_category": "gfx/interface/icons/flat_icons/tabicons/military.dds",
    "cultural_category": "gfx/interface/icons/flat_icons/cultural_influence.dds",
    "government_category": "gfx/interface/icons/flat_icons/diplomatic_reputation.dds",
}
WONDER_DISPLAY_CONCEPT_PREFIX = "tv_wonder_display_"
WONDER_IMAGE_CONCEPT_PREFIX = "tv_wonder_display_image_"
WONDER_RITUAL_DISPLAY_CONCEPT_PREFIX = "tv_wonder_display_"


def wonder_image_texture(wonder: dict) -> str:
    image = wonder.get("image", f"tv_wonder_{wonder['key']}")
    return f"gfx/interface/icons/towards_victory/wonders/{image}.dds"


def generate() -> str:
    wonders, _ = load_all_wonder_mechanics_data()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        texture = ICONS.get(wonder["category"], ICONS["infrastructure_category"])
        lines.extend(
            [
                f"{wonder['concept']} = {{",
                f'\ttexture = "{texture}"',
                "}",
                "",
            ]
        )
    for wonder in wonders:
        texture = ICONS.get(wonder["category"], ICONS["infrastructure_category"])
        lines.extend(
            [
                f"{WONDER_DISPLAY_CONCEPT_PREFIX}{wonder['id']} = {{",
                f'\ttexture = "{texture}"',
                "}",
                "",
            ]
        )
    for wonder in wonders:
        lines.extend(
            [
                f"{WONDER_IMAGE_CONCEPT_PREFIX}{wonder['id']} = {{",
                f'\ttexture = "{wonder_image_texture(wonder)}"',
                "}",
                "",
            ]
        )
    for wonder in wonders:
        texture = ICONS.get(wonder["category"], ICONS["infrastructure_category"])
        for style in ceremony_styles(wonder):
            lines.extend(
                [
                    f"{WONDER_RITUAL_DISPLAY_CONCEPT_PREFIX}{wonder['id']}_ritual_{style} = {{",
                    f'\ttexture = "{texture}"',
                    "}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
