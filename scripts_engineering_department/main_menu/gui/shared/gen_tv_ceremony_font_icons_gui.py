"""Generate normalized texticon aliases for every Unique Wonder Ceremony card icon.

The 8 ceremony status cards (gen_tv_wonder_ceremony_cards_gui.py) render each wonder's
per-stage icon as inline text-icon markup at a shared fontsize = 17. Vanilla's own
font_icons.gui defines each icon's size/offset/fontsize individually and inconsistently
(e.g. construction is 14x14@fontsize14, wealth is 20x20@fontsize18, topography is
24x24@fontsize16), so the same call-site fontsize renders wildly different pixel sizes
per wonder. This generator defines one `tv_ceremony_<name>` texticon alias per distinct
icon name actually used in data/unique_wonders.yaml's ceremony stages, reusing the same
vanilla texture but with a uniform size/offset/fontsize (32x32, no offset, fontsize 17 to
match the card call site, so the render-time scale factor is exactly 1 for every icon).
See docs/knowledge/risk_cards/wonders.md for the full rationale and the mod-precedent for
adding custom texticon blocks that reuse a vanilla texture with different sizing.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_ceremony_lib import T, ceremony_wonders, render_header, script_rel  # noqa: E402
from wonder_mechanics._core import FONT_ICON_TEXTURES  # noqa: E402

OUT_FILE = (
    REPO_ROOT
    / "src_engineering_department" / "main_menu"
    / "gui" / "shared"
    / "tv_ceremony_font_icons.gui"
)
SCRIPT_REL = "scripts_engineering_department/main_menu/gui/shared/gen_tv_ceremony_font_icons_gui.py"
DATA_REL = (
    "data/unique_wonders.yaml + reference_game_files/game/main_menu/gui/shared/font_icons.gui"
)
ICON_SIZE = 32
ICON_FONTSIZE = 17


def distinct_stage_icons(wonders: list[dict]) -> list[str]:
    names: set[str] = set()
    for wonder in wonders:
        for stage in wonder["ceremony"]["stages"]:
            names.add(stage["icon"])
    return sorted(names)


def generate() -> str:
    wonders = ceremony_wonders()
    names = distinct_stage_icons(wonders)
    lines = render_header(SCRIPT_REL, DATA_REL, script_rel(OUT_FILE))
    for name in names:
        texture = FONT_ICON_TEXTURES[name]
        lines.append("texticon = {")
        lines.append(f"{T}icon = tv_ceremony_{name}")
        lines.append(f"{T}iconsize = {{")
        lines.append(f'{T}{T}texture = "{texture}"')
        lines.append(f"{T}{T}size = {{ {ICON_SIZE} {ICON_SIZE} }}")
        lines.append(f"{T}{T}offset = {{ 0 0 }}")
        lines.append(f"{T}{T}fontsize = {ICON_FONTSIZE}")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text("﻿" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
