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
untitled (zero-height header), left column a real piechart with a centered
built-in icon selected from the current wonder's stage data, right column
dynamically resolved stage flavor text, and a state color overlay (color_yellow_texture in progress /
color_light_green_texture done). The outer Ceremony card is 500px wide; its
content column is 462px wide, so every nested ceremony card is exactly 462px
wide and cannot expand the parent -- see docs/knowledge/risk_cards/wonders.md
for the verified piechart, dynamic-localization, and bounded-text precedents.

There is no ready state: a newly initialized ceremony has stage 0, which makes
only its first card visible and in progress. Each advancement completes the
current card and reveals the next one in progress.
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
PLAYER = "InternationalOrganizationsView.GetPlayer.MakeScope"
# The outer Ceremony card is 500px wide. Its card_common margins leave a 462px
# content column, and each nested card has another 15px left/right margin.
# 64px icon + 8px gap + 344px text stays below that 432px inner budget.
CARD_WIDTH = 462
CARD_HEIGHT = 144
CARD_CONTENT_WIDTH = 432
ICON_COLUMN_WIDTH = 64
TEXT_MAX_WIDTH = 344

def stage_value() -> str:
    return f"{PLAYER}.GetVariable('tv_wonder_ceremony_stage').GetValue"


def stage_completed_visible(stage: int) -> str:
    return (
        f"[GreaterThanOrEqualTo_CFixedPoint({stage_value()}, "
        f"'(CFixedPoint){stage}.0')]"
    )


def stage_active_visible(stage: int) -> str:
    return f"[Not(GreaterThanOrEqualTo_CFixedPoint({stage_value()}, '(CFixedPoint){stage}.0'))]"


def stage_flavor_text(stage: int, state: str) -> str:
    locked = f"{PLAYER}.GetVariable('tv_wonder_locked').GetValue"
    return (
        f"[Localize(Concatenate('TV_WONDER_CEREMONY_CARD_{state}_S{stage}_', "
        f"ToString_int32(FixedPointToInt({locked}))))]"
    )


def stage_icon_text(stage: int) -> str:
    locked = f"{PLAYER}.GetVariable('tv_wonder_locked').GetValue"
    return (
        f"[Localize(Concatenate('TV_WONDER_CEREMONY_CARD_ICON_S{stage}_', "
        f"ToString_int32(FixedPointToInt({locked}))))]"
    )


def append_piechart(
    lines: list[str],
    *,
    icon_text: str,
    value: float,
    texture: str,
    color: str,
    visible: str | None = None,
) -> None:
    """Append a rendered piechart with an inline built-in icon at its center."""
    value_text = f"{value:g}"
    remaining_text = f"{1 - value:g}"
    lines.append(f"{T}{T}{T}{T}{T}piechart = {{")
    if visible is not None:
        lines.append(f'{T}{T}{T}{T}{T}{T}visible = "{visible}"')
    lines.append(f"{T}{T}{T}{T}{T}{T}size = {{ 52 52 }}")
    lines.append(f"{T}{T}{T}{T}{T}{T}minimumsize = {{ 52 52 }}")
    lines.append(f"{T}{T}{T}{T}{T}{T}parentanchor = center")
    lines.append(f"{T}{T}{T}{T}{T}{T}widgetanchor = center")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = piechart_angles")
    lines.append(f"{T}{T}{T}{T}{T}{T}using = bg_circle_piechart_big")
    lines.append(f"{T}{T}{T}{T}{T}{T}pieslice = {{")
    lines.append(f'{T}{T}{T}{T}{T}{T}{T}texture = "{texture}"')
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}value = {value_text}")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}color = {color}")
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}{T}pieslice = {{")
    lines.append(f'{T}{T}{T}{T}{T}{T}{T}texture = "gfx/interface/pie_charts/pie_chart_alpha_80.dds"')
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}value = {remaining_text}")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}color = {{ 1 1 1 0 }}")
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}{T}text_single = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}parentanchor = center")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}size = {{ 100% 100% }}")
    lines.append(f'{T}{T}{T}{T}{T}{T}{T}text = "{icon_text}"')
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}fontsize = 17")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}align = center|nobaseline")
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}}}")


def append_card(lines: list[str], stage: int) -> None:
    stage_var = "tv_wonder_ceremony_stage"
    locked = f"{PLAYER}.GetVariable('tv_wonder_locked')"
    stage_scope = f"{PLAYER}.GetVariable('{stage_var}')"
    card_visible = (
        f"[And3({locked}.IsSet, {stage_scope}.IsSet, "
        f"GreaterThanOrEqualTo_CFixedPoint({stage_scope}.GetValue, '(CFixedPoint){stage - 1}.0'))]"
    )
    lines.append(f"{T}tv_engineering_department_card_common = {{")
    lines.append(f'{T}{T}visible = "{card_visible}"')
    lines.append(f"{T}{T}layoutpolicy_vertical = fixed")
    lines.append(f"{T}{T}minimumsize = {{ {CARD_WIDTH} {CARD_HEIGHT} }}")
    lines.append(f"{T}{T}maximumsize = {{ {CARD_WIDTH} {CARD_HEIGHT} }}")
    lines.append(f"{T}{T}blockoverride \"header_size\" {{ size = {{ -1 0 }} }}")
    lines.append(f"{T}{T}blockoverride \"header_decor_templates\" {{}}")
    lines.append(f"{T}{T}blockoverride \"common_header\" {{}}")
    lines.append(f"{T}{T}blockoverride \"card_bg\" {{")
    lines.append(f"{T}{T}{T}background = {{")
    lines.append(f'{T}{T}{T}{T}texture = "gfx/interface/cards/paper_card_fancy_01.dds"')
    lines.append(f"{T}{T}{T}{T}texture_density = 2")
    lines.append(f"{T}{T}{T}{T}spriteType = corneredstretched")
    lines.append(f"{T}{T}{T}{T}spriteborder = {{ 100 100 }}")
    lines.append(f"{T}{T}{T}{T}margin = {{ 1 1 }}")
    lines.append(f"{T}{T}{T}{T}margin_bottom = 2")
    lines.append(f"{T}{T}{T}{T}alpha = 0.4")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}background = {{")
    lines.append(f'{T}{T}{T}{T}texture = "gfx/interface/cards/paper_card_fancy_01.dds"')
    lines.append(f"{T}{T}{T}{T}texture_density = 2")
    lines.append(f"{T}{T}{T}{T}spriteType = corneredstretched")
    lines.append(f"{T}{T}{T}{T}spriteborder = {{ 100 100 }}")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}using = color_paper_texture")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}using = color_black_texture")
    lines.append(f"{T}{T}{T}{T}{T}alpha = 0.3")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}using = overlay_paper_03")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f"{T}{T}{T}{T}{T}using = overlay_cloth_texture")
    lines.append(f"{T}{T}{T}{T}{T}blend_mode = overlay")
    lines.append(f"{T}{T}{T}{T}{T}alpha = 0.2")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f'{T}{T}{T}{T}{T}visible = "{stage_completed_visible(stage)}"')
    lines.append(f"{T}{T}{T}{T}{T}using = color_light_green_texture")
    lines.append(f"{T}{T}{T}{T}{T}blend_mode = overlay")
    lines.append(f"{T}{T}{T}{T}{T}alpha = 0.85")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}modify_texture = {{")
    lines.append(f'{T}{T}{T}{T}{T}visible = "{stage_active_visible(stage)}"')
    lines.append(f"{T}{T}{T}{T}{T}using = color_yellow_texture")
    lines.append(f"{T}{T}{T}{T}{T}blend_mode = overlay")
    lines.append(f"{T}{T}{T}{T}{T}alpha = 0.55")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}blockoverride \"common_bottom_content\" {{")
    lines.append(f"{T}{T}{T}hbox = {{")
    lines.append(f"{T}{T}{T}{T}size = {{ {CARD_CONTENT_WIDTH} 104 }}")
    lines.append(f"{T}{T}{T}{T}spacing = 8")
    lines.append(f"{T}{T}{T}{T}widget = {{")
    lines.append(f"{T}{T}{T}{T}layoutpolicy_horizontal = fixed")
    lines.append(f"{T}{T}{T}{T}size = {{ {ICON_COLUMN_WIDTH} 104 }}")
    append_piechart(
        lines,
        icon_text=stage_icon_text(stage),
        value=1,
        texture="gfx/interface/pie_charts/pie_chart_alpha_80_green.dds",
        color="{ 1 1 1 1 }",
        visible=stage_completed_visible(stage),
    )
    append_piechart(
        lines,
        icon_text=stage_icon_text(stage),
        value=0.5,
        texture="gfx/interface/pie_charts/pie_chart_alpha_80.dds",
        color="{ 0.95 0.76 0.25 1 }",
        visible=stage_active_visible(stage),
    )
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}text_multi = {{")
    lines.append(f'{T}{T}{T}{T}visible = "{stage_completed_visible(stage)}"')
    lines.append(f"{T}{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}{T}{T}{T}max_width = {TEXT_MAX_WIDTH}")
    lines.append(f"{T}{T}{T}{T}autoresize = yes")
    lines.append(f'{T}{T}{T}{T}text = "{stage_flavor_text(stage, "COMPLETED")}"')
    lines.append(f"{T}{T}{T}{T}align = nobaseline|left")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}text_multi = {{")
    lines.append(f'{T}{T}{T}{T}visible = "{stage_active_visible(stage)}"')
    lines.append(f"{T}{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}{T}{T}{T}max_width = {TEXT_MAX_WIDTH}")
    lines.append(f"{T}{T}{T}{T}autoresize = yes")
    lines.append(f'{T}{T}{T}{T}text = "{stage_flavor_text(stage, "ACTIVE")}"')
    lines.append(f"{T}{T}{T}{T}align = nobaseline|left")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}expand = {{}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")


def generate() -> str:
    lines = render_header(SCRIPT_REL, DATA_REL, str(OUT_FILE.relative_to(REPO_ROOT)).replace("\\", "/"))
    lines.append(f"### BEGIN {MARKER}")
    lines.append(f"# BEGIN GENERATED {MARKER}")
    lines.append("vbox = {")
    lines.append(f"{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{T}ignoreinvisible = yes")
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
