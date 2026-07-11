"""Generate the 8 Unique Wonder Ceremony status cards as a standalone fragment.

Merged into src/in_game/gui/panels/organization/tv_engineering_department.gui's
Construction-and-ceremony tab by
scripts/in_game/gui/panels/organization/merge_tv_wonder_ceremony_cards_gui.py,
which inserts (or replaces) a dedicated `# BEGIN/END GENERATED
TV_WONDER_CEREMONY_CARDS` marker pair right after the existing
`TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS` block (the Pharos/Hagia hand-coded
step display) -- this feature's `tv_wonder_ceremony_stage` variable is only
ever set for the other 121 unique wonders, so the two displays are mutually
exclusive by construction, not by an explicit id check.

Card layout (per stage, 8 total): built on this mod's own
tv_engineering_department_card_common (defined in that same panel file),
untitled (zero-height header), left column a bg_circle_piechart badge with the
wonder's flavor icon, right column the stage's flavor text, and a state color
overlay (color_yellow_texture in progress / color_light_green_texture done) --
see docs/knowledge/risk_cards/wonders.md and this mod's tv_victory_situation.gui
for the verified precedents (bg_circle_piechart usage, modify_texture overlay
idiom, and text_multi width-bounding per risk card rule 11).
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_ceremony_lib import STAGE_COUNT, T, render_header  # noqa: E402

OUT_FILE = REPO_ROOT / "data" / "generated_fragments" / "tv_wonder_ceremony_cards.gui"
SCRIPT_REL = "scripts/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py"
DATA_REL = "data/unique_wonders.yaml"
MARKER = "TV_WONDER_CEREMONY_CARDS"


def append_card(lines: list[str], stage: int) -> None:
    stage_var = "tv_wonder_ceremony_stage"
    lines.append(f"{T}widget = {{")
    lines.append(f"{T}{T}visible = \"[And3(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable('tv_wonder_locked').IsSet, InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable('{stage_var}').IsSet, GreaterThanOrEqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable('{stage_var}').GetValue, '(CFixedPoint){stage - 1}.0'))]\"")
    lines.append(f"{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}{T}tv_engineering_department_card_common = {{")
    lines.append(f"{T}{T}{T}blockoverride \"header_size\" {{ size = {{ -1 0 }} }}")
    lines.append(f"{T}{T}{T}blockoverride \"header_decor_templates\" {{}}")
    lines.append(f"{T}{T}{T}blockoverride \"common_header_back_decor\" {{}}")
    lines.append(f"{T}{T}{T}blockoverride \"card_bg\" {{")
    lines.append(f"{T}{T}{T}{T}background = {{")
    lines.append(f'{T}{T}{T}{T}{T}texture = "gfx/interface/cards/paper_card_fancy_01.dds"')
    lines.append(f"{T}{T}{T}{T}{T}texture_density = 2")
    lines.append(f"{T}{T}{T}{T}{T}spriteType = corneredstretched")
    lines.append(f"{T}{T}{T}{T}{T}spriteborder = {{ 100 100 }}")
    lines.append(f"{T}{T}{T}{T}{T}margin = {{ 1 1 }}")
    lines.append(f"{T}{T}{T}{T}{T}margin_bottom = 2")
    lines.append(f"{T}{T}{T}{T}{T}alpha = 0.4")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}background = {{")
    lines.append(f'{T}{T}{T}{T}{T}texture = "gfx/interface/cards/paper_card_fancy_01.dds"')
    lines.append(f"{T}{T}{T}{T}{T}texture_density = 2")
    lines.append(f"{T}{T}{T}{T}{T}spriteType = corneredstretched")
    lines.append(f"{T}{T}{T}{T}{T}spriteborder = {{ 100 100 }}")
    lines.append(f"{T}{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = color_paper_texture")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = color_black_texture")
    lines.append(f"{T}{T}{T}{T}{T}{T}alpha = 0.3")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = overlay_paper_03")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = overlay_cloth_texture")
    lines.append(f"{T}{T}{T}{T}{T}{T}blend_mode = overlay")
    lines.append(f"{T}{T}{T}{T}{T}{T}alpha = 0.2")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}modify_texture = {{")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}visible = \"[GreaterThanOrEqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable('{stage_var}').GetValue, '(CFixedPoint){stage}.0')]\""
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}using = color_light_green_texture")
    lines.append(f"{T}{T}{T}{T}{T}{T}blend_mode = overlay")
    lines.append(f"{T}{T}{T}{T}{T}{T}alpha = 0.85")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}modify_texture = {{")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}visible = \"[Not(GreaterThanOrEqualTo_CFixedPoint(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable('{stage_var}').GetValue, '(CFixedPoint){stage}.0'))]\""
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}using = color_yellow_texture")
    lines.append(f"{T}{T}{T}{T}{T}{T}blend_mode = overlay")
    lines.append(f"{T}{T}{T}{T}{T}{T}alpha = 0.55")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}blockoverride \"common_bottom_content\" {{")
    lines.append(f"{T}{T}{T}{T}widget = {{")
    lines.append(f"{T}{T}{T}{T}{T}layoutpolicy_horizontal = fixed")
    lines.append(f"{T}{T}{T}{T}{T}size = {{ 60 60 }}")
    lines.append(f"{T}{T}{T}{T}{T}widget = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}size = {{ 52 52 }}")
    lines.append(f"{T}{T}{T}{T}{T}{T}parentanchor = center")
    lines.append(f"{T}{T}{T}{T}{T}{T}widgetanchor = center")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = bg_circle_piechart_big")
    lines.append(f"{T}{T}{T}{T}{T}{T}icon = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}parentanchor = center")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}size = {{ 70% 70% }}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}texture = \"[GetConceptTexture(Concatenate('tv_wonder_display_', ToString_int32(FixedPointToInt(InternationalOrganizationsView.GetPlayer.MakeScope.GetVariable('tv_wonder_locked').GetValue))))]\""
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}widget = {{")
    lines.append(f"{T}{T}{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}{T}{T}{T}{T}text_multi = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}layoutpolicy_horizontal = fixed")
    lines.append(f"{T}{T}{T}{T}{T}{T}max_width = 380")
    lines.append(f"{T}{T}{T}{T}{T}{T}autoresize = yes")
    lines.append(f'{T}{T}{T}{T}{T}{T}text = "TV_WONDER_CEREMONY_CARD_STAGE_{stage}_LABEL"')
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}expand = {{}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")


def generate() -> str:
    lines = render_header(SCRIPT_REL, DATA_REL, str(OUT_FILE.relative_to(REPO_ROOT)).replace("\\", "/"))
    lines.append(f"### BEGIN {MARKER}")
    lines.append(f"# BEGIN GENERATED {MARKER}")
    lines.append("vbox = {")
    lines.append(f"{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}spacing = 4")
    for stage in range(1, STAGE_COUNT + 1):
        append_card(lines, stage)
    lines.append("}")
    lines.append(f"# END GENERATED {MARKER}")
    lines.append(f"### END {MARKER}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("﻿" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
