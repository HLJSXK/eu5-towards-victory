import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import load_all_wonder_mechanics_data, render_header

VANILLA_FILE = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "gui" / "location_window.gui"
OUT_FILE = REPO_ROOT / "src" / "in_game" / "gui" / "location_window.gui"
SCRIPT_REL = "scripts/in_game/gui/gen_location_window.py"
T = "\t"

COUNT_VAR = "LocationView.GetLocation.MakeScope.GetVariable('tv_wonder_display_count')"
PANEL_WIDTH = 380
PANEL_HEIGHTS = {1: 68, 2: 136, 3: 204}
PANEL_ROW_HEIGHT = 64
PANEL_SEPARATOR_HEIGHT = 4
TOOLTIP_ROW_WIDTH = 380
TOOLTIP_ROW_HEIGHT = 84
TOOLTIP_ROW_SPACING = 6
WONDER_PREVIEW_COLUMN_WIDTH = 120


def ordered_wonders() -> list[dict]:
    wonders, _ = load_all_wonder_mechanics_data()
    unique_wonders = [wonder for wonder in wonders if wonder.get("is_unique")]
    generic_wonders = [wonder for wonder in wonders if not wonder.get("is_unique")]
    return [*unique_wonders, *generic_wonders]


def preview_texture(wonder: dict) -> str:
    image = wonder.get("image", f"tv_wonder_{wonder['key']}")
    return f"gfx/interface/illustrations/towards_victory/wonders/{image}.dds"


def slot_id_var(slot: int) -> str:
    return f"LocationView.GetLocation.MakeScope.GetVariable('tv_wonder_display_slot_{slot}_id')"


def slot_level_var(slot: int) -> str:
    return f"LocationView.GetLocation.MakeScope.GetVariable('tv_wonder_display_slot_{slot}_level')"


def wonder_level_var(wonder: dict) -> str:
    return f"LocationView.GetLocation.MakeScope.GetVariable('tv_wonder_display_{wonder['key']}_level')"


def eq_fixed_point(var_expr: str, value: int) -> str:
    return f"And({var_expr}.IsSet, EqualTo_CFixedPoint({var_expr}.GetValue, '(CFixedPoint){value}.0'))"


def count_visible_expr(count: int) -> str:
    return eq_fixed_point(COUNT_VAR, count)


def slot_matches_expr(slot: int, wonder: dict) -> str:
    return eq_fixed_point(slot_id_var(slot), wonder["id"])


def level_is_expr(var_expr: str, level: int) -> str:
    return eq_fixed_point(var_expr, level)


def render_separator(indent: str, *, visible: str | None = None) -> list[str]:
    lines = [f"{indent}widget = {{"]
    if visible is not None:
        lines.append(f'{indent}{T}visible = "[{visible}]"')
    lines.extend(
        [
            f"{indent}{T}layoutpolicy_horizontal = expanding",
            f"{indent}{T}size = {{ -1 {PANEL_SEPARATOR_HEIGHT} }}",
            f"{indent}{T}background = {{",
            f'{indent}{T}{T}texture = "gfx/interface/colors/black.dds"',
            f"{indent}{T}{T}alpha = 0.16",
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_slot_name_branches(indent: str, *, slot: int) -> list[str]:
    lines: list[str] = []
    for wonder in ordered_wonders():
        lines.extend(
            [
                f"{indent}text_single = {{",
                f'{indent}{T}visible = "[{slot_matches_expr(slot, wonder)}]"',
                f"{indent}{T}layoutpolicy_horizontal = expanding",
                f'{indent}{T}text = "[{wonder["concept"]}|E]"',
                f"{indent}{T}align = left|nobaseline",
                f"{indent}{T}autoresize = no",
                f"{indent}{T}fontsize = 15",
                f"{indent}}}",
            ]
        )
    return lines


def render_slot_modifier_blocks(indent: str, *, slot: int) -> list[str]:
    slot_level = slot_level_var(slot)
    lines: list[str] = []
    for wonder in ordered_wonders():
        for level in range(1, 7):
            lines.extend(
                [
                    f"{indent}TooltipStringPairList = {{",
                    f'{indent}{T}visible = "[And({slot_matches_expr(slot, wonder)}, {level_is_expr(slot_level, level)})]"',
                    f'{indent}{T}textcontext = "[ShowModifierEffect(\'tv_wonder_{wonder["key"]}_level_{level}\')]"',
                    f"{indent}}}",
                ]
            )
        lines.extend(
            [
                f"{indent}text_single = {{",
                f'{indent}{T}visible = "[And({slot_matches_expr(slot, wonder)}, {level_is_expr(slot_level, 0)})]"',
                f"{indent}{T}layoutpolicy_horizontal = expanding",
                f'{indent}{T}text = "TV_LOCATION_WONDER_NO_EFFECT"',
                f"{indent}{T}fontsize = 13",
                f"{indent}{T}align = left|nobaseline",
                f"{indent}}}",
            ]
        )
    return lines


def render_slot_image_branches(indent: str, *, slot: int) -> list[str]:
    lines: list[str] = []
    for wonder in ordered_wonders():
        lines.extend(
            [
                f"{indent}widget = {{",
                f'{indent}{T}visible = "[{slot_matches_expr(slot, wonder)}]"',
                f"{indent}{T}layoutpolicy_horizontal = expanding",
                f"{indent}{T}layoutpolicy_vertical = expanding",
                f"{indent}{T}background = {{",
                f'{indent}{T}{T}texture = "{preview_texture(wonder)}"',
                f"{indent}{T}{T}texture_density = 2",
                f"{indent}{T}{T}fittype = centercrop",
                f"{indent}{T}}}",
                f"{indent}}}",
            ]
        )
    return lines


def render_slot_row(indent: str, *, slot: int) -> list[str]:
    slot_level = slot_level_var(slot)
    lines = [
        f"{indent}widget = {{",
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}size = {{ -1 {PANEL_ROW_HEIGHT} }}",
        f"{indent}{T}using = bg_dark_paper_card",
        f"{indent}{T}hbox = {{",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}spacing = 4",
        f"{indent}{T}{T}widget = {{",
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}layoutstretchfactor_horizontal = 1",
        f"{indent}{T}{T}{T}vbox = {{",
        f"{indent}{T}{T}{T}{T}margin_left = 8",
        f"{indent}{T}{T}{T}{T}margin_right = 8",
        f"{indent}{T}{T}{T}{T}margin_top = 6",
        f"{indent}{T}{T}{T}{T}margin_bottom = 6",
        f"{indent}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}{T}spacing = 2",
        f"{indent}{T}{T}{T}{T}hbox = {{",
        f"{indent}{T}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}{T}{T}size = {{ -1 18 }}",
        f"{indent}{T}{T}{T}{T}{T}spacing = 4",
        f"{indent}{T}{T}{T}{T}{T}ignoreinvisible = yes",
    ]
    lines.extend(render_slot_name_branches(indent + T * 6, slot=slot))
    lines.extend(
        [
            f"{indent}{T}{T}{T}{T}{T}text_single = {{",
            f'{indent}{T}{T}{T}{T}{T}{T}text = "TV_LOCATION_WONDER_LEVEL_SHORT"',
            f"{indent}{T}{T}{T}{T}{T}{T}align = right|nobaseline",
            f"{indent}{T}{T}{T}{T}{T}{T}fontsize = 13",
            f"{indent}{T}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}{T}{T}text_single = {{",
            f'{indent}{T}{T}{T}{T}{T}{T}visible = "[{slot_level}.IsSet]"',
            f'{indent}{T}{T}{T}{T}{T}{T}text = "[{slot_level}.GetValue|0]"',
            f"{indent}{T}{T}{T}{T}{T}{T}align = right|nobaseline",
            f"{indent}{T}{T}{T}{T}{T}{T}fontsize = 13",
            f"{indent}{T}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}{T}{T}using = layoutpolicy_expanding",
        ]
    )
    lines.extend(render_slot_modifier_blocks(indent + T * 5, slot=slot))
    lines.extend(
        [
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}}}",
            f"{indent}{T}{T}}}",
            f"{indent}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}size = {{ {WONDER_PREVIEW_COLUMN_WIDTH} {PANEL_ROW_HEIGHT} }}",
            f"{indent}{T}{T}{T}vbox = {{",
            f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{indent}{T}{T}{T}layoutpolicy_vertical = expanding",
            f"{indent}{T}{T}{T}margin_top = 4",
            f"{indent}{T}{T}{T}margin_bottom = 4",
            f"{indent}{T}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{indent}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
            f"{indent}{T}{T}{T}{T}using = bg_cabinet_card_frame",
        ]
    )
    lines.extend(render_slot_image_branches(indent + T * 5, slot=slot))
    lines.extend(
        [
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}}}",
            f"{indent}{T}{T}}}",
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_panel_card(indent: str, *, count: int) -> list[str]:
    height = PANEL_HEIGHTS[count]
    lines = [
        f"{indent}widget = {{",
        f'{indent}{T}visible = "[{count_visible_expr(count)}]"',
        f"{indent}{T}size = {{ {PANEL_WIDTH} {height} }}",
        f"{indent}{T}parentanchor = right|top",
        f"{indent}{T}widgetanchor = right|top",
        f"{indent}{T}position = {{ -8 8 }}",
        f"{indent}{T}allow_outside = yes",
        f"{indent}{T}using = bg_paper_card",
        f"{indent}{T}using = bg_cabinet_card_frame",
        f"{indent}{T}button = {{",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}tooltipwidget = {{ using = tv_location_wonder_tooltip }}",
        f"{indent}{T}{T}vbox = {{",
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}spacing = {PANEL_SEPARATOR_HEIGHT}",
    ]
    for slot in range(1, count + 1):
        lines.extend(render_slot_row(indent + T * 4, slot=slot))
        if slot < count:
            lines.extend(render_separator(indent + T * 4))
    lines.extend(
        [
            f"{indent}{T}{T}}}",
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_tooltip_modifier_blocks(indent: str, *, wonder: dict) -> list[str]:
    level_var = wonder_level_var(wonder)
    lines: list[str] = []
    for level in range(1, 7):
        lines.extend(
            [
                f"{indent}TooltipStringPairList = {{",
                f'{indent}{T}visible = "[{level_is_expr(level_var, level)}]"',
                f'{indent}{T}textcontext = "[ShowModifierEffect(\'tv_wonder_{wonder["key"]}_level_{level}\')]"',
                f"{indent}}}",
            ]
        )
    lines.extend(
        [
            f"{indent}TooltipTextBlock = {{",
            f'{indent}{T}visible = "[{level_is_expr(level_var, 0)}]"',
            f'{indent}{T}blockoverride "text" {{',
            f'{indent}{T}{T}text = "TV_LOCATION_WONDER_NO_EFFECT"',
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_tooltip_row(indent: str, *, wonder: dict) -> list[str]:
    level_var = wonder_level_var(wonder)
    lines = [
        f"{indent}widget = {{",
        f'{indent}{T}visible = "[{level_var}.IsSet]"',
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}size = {{ {TOOLTIP_ROW_WIDTH} {TOOLTIP_ROW_HEIGHT} }}",
        f"{indent}{T}using = bg_paper_card",
        f"{indent}{T}using = bg_cabinet_card_frame",
        f"{indent}{T}hbox = {{",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}spacing = 4",
        f"{indent}{T}{T}widget = {{",
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}layoutstretchfactor_horizontal = 1",
        f"{indent}{T}{T}{T}vbox = {{",
        f"{indent}{T}{T}{T}{T}margin_left = 8",
        f"{indent}{T}{T}{T}{T}margin_right = 8",
        f"{indent}{T}{T}{T}{T}margin_top = 6",
        f"{indent}{T}{T}{T}{T}margin_bottom = 6",
        f"{indent}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}{T}spacing = 2",
        f"{indent}{T}{T}{T}{T}hbox = {{",
        f"{indent}{T}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}{T}{T}size = {{ -1 18 }}",
        f"{indent}{T}{T}{T}{T}{T}spacing = 4",
        f"{indent}{T}{T}{T}{T}{T}text_single = {{",
        f'{indent}{T}{T}{T}{T}{T}{T}layoutpolicy_horizontal = expanding',
        f'{indent}{T}{T}{T}{T}{T}{T}text = "[{wonder["concept"]}|E]"',
        f"{indent}{T}{T}{T}{T}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}{T}{T}{T}{T}autoresize = no",
        f"{indent}{T}{T}{T}{T}{T}{T}fontsize = 15",
        f"{indent}{T}{T}{T}{T}{T}}}",
        f"{indent}{T}{T}{T}{T}{T}text_single = {{",
        f'{indent}{T}{T}{T}{T}{T}{T}text = "TV_LOCATION_WONDER_LEVEL_SHORT"',
        f"{indent}{T}{T}{T}{T}{T}{T}align = right|nobaseline",
        f"{indent}{T}{T}{T}{T}{T}{T}fontsize = 13",
        f"{indent}{T}{T}{T}{T}{T}}}",
        f"{indent}{T}{T}{T}{T}{T}text_single = {{",
        f'{indent}{T}{T}{T}{T}{T}{T}text = "[{level_var}.GetValue|0]"',
        f"{indent}{T}{T}{T}{T}{T}{T}align = right|nobaseline",
            f"{indent}{T}{T}{T}{T}{T}{T}fontsize = 13",
            f"{indent}{T}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}{T}{T}using = layoutpolicy_expanding",
        ]
    lines.extend(render_tooltip_modifier_blocks(indent + T * 5, wonder=wonder))
    lines.extend(
        [
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}}}",
            f"{indent}{T}{T}}}",
            f"{indent}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}size = {{ {WONDER_PREVIEW_COLUMN_WIDTH} {TOOLTIP_ROW_HEIGHT} }}",
            f"{indent}{T}{T}{T}vbox = {{",
            f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{indent}{T}{T}{T}layoutpolicy_vertical = expanding",
            f"{indent}{T}{T}{T}margin_top = 4",
            f"{indent}{T}{T}{T}margin_bottom = 4",
            f"{indent}{T}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{indent}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
            f"{indent}{T}{T}{T}{T}using = bg_cabinet_card_frame",
            f"{indent}{T}{T}{T}{T}background = {{",
            f'{indent}{T}{T}{T}{T}{T}texture = "{preview_texture(wonder)}"',
            f"{indent}{T}{T}{T}{T}{T}texture_density = 2",
            f"{indent}{T}{T}{T}{T}{T}fittype = centercrop",
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}}}",
            f"{indent}{T}{T}}}",
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_tooltip_template() -> str:
    lines = [
        "template tv_location_wonder_tooltip {",
        f"{T}ContextualTooltipType = {{",
        f'{T}{T}blockoverride "title_text" {{ text = "TV_LOCATION_WONDER_TOOLTIP_TITLE" }}',
        f'{T}{T}blockoverride "title_icon_texture" {{',
        f'{T}{T}{T}texture = "gfx/interface/icons/location_icons/new/prosperity.dds"',
        f"{T}{T}}}",
        f'{T}{T}blockoverride "concept_link" {{ text = "[tv_wonder_construction|E]" }}',
        f'{T}{T}blockoverride "tooltip_content" {{',
        f"{T}{T}{T}widget = {{",
        f"{T}{T}{T}{T}vbox = {{",
        f"{T}{T}{T}{T}{T}spacing = {TOOLTIP_ROW_SPACING}",
    ]
    for wonder in ordered_wonders():
        lines.extend(render_tooltip_row(T * 5, wonder=wonder))
    lines.extend(
        [
            f"{T}{T}{T}{T}}}",
            f"{T}{T}{T}}}",
            f"{T}{T}}}",
            f"{T}}}",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def render_scene_overlay() -> str:
    lines: list[str] = []
    for count in (1, 2, 3):
        lines.extend(render_panel_card(T * 4, count=count))
    return "\n".join(lines)


def inject_overlay(vanilla: str) -> str:
    marker = "\n\t\t\t\tvbox = {\n\t\t\t\t\texpand = {}\n"
    replacement = "\n" + render_scene_overlay() + marker
    if marker not in vanilla:
        raise RuntimeError("Could not find location scene overlay insertion point in vanilla location_window.gui")
    return vanilla.replace(marker, replacement, 1)


def generate() -> str:
    vanilla = VANILLA_FILE.read_text(encoding="utf-8-sig")
    lines = render_header(SCRIPT_REL)
    lines.append(render_tooltip_template())
    lines.append(inject_overlay(vanilla))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
