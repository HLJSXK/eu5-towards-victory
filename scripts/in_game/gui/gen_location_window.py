import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import render_header

VANILLA_FILE = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "gui" / "location_window.gui"
OUT_FILE = REPO_ROOT / "src" / "in_game" / "gui" / "location_window.gui"
SCRIPT_REL = "scripts/in_game/gui/gen_location_window.py"
T = "\t"

ANY_WONDER_VAR = "LocationView.GetLocation.MakeScope.GetVariable('tv_wonder_display_any_wonder')"
OVERFLOW_VAR = "LocationView.GetLocation.MakeScope.GetVariable('tv_wonder_tooltip_overflow_count')"
LOCATION_SCOPE = "LocationView.GetLocation.MakeScope.Self"
DISPLAY_CONCEPT_PREFIX = "tv_wonder_display_"
IMAGE_CONCEPT_PREFIX = "tv_wonder_display_image_"
COMPACT_SLOT_MAX = 3
TOOLTIP_SLOT_MAX = 5
WONDER_TEXT_COLUMN_WIDTH = 120
WONDER_PREVIEW_COLUMN_WIDTH = 120
WONDER_ROW_SPACING = 4
PANEL_WIDTH = WONDER_TEXT_COLUMN_WIDTH + WONDER_ROW_SPACING + WONDER_PREVIEW_COLUMN_WIDTH
LOCATION_SCENE_CARD_MARGIN = 8
PANEL_ROW_HEIGHT = 64
PANEL_SEPARATOR_HEIGHT = 4
PANEL_HEIGHT = PANEL_ROW_HEIGHT * COMPACT_SLOT_MAX + PANEL_SEPARATOR_HEIGHT * (COMPACT_SLOT_MAX - 1)
PANEL_PREVIEW_HEIGHT = PANEL_ROW_HEIGHT - 8
TOOLTIP_ROW_WIDTH = 400
TOOLTIP_TEXT_COLUMN_WIDTH = (TOOLTIP_ROW_WIDTH - WONDER_ROW_SPACING) // 2
TOOLTIP_PREVIEW_COLUMN_WIDTH = TOOLTIP_ROW_WIDTH - WONDER_ROW_SPACING - TOOLTIP_TEXT_COLUMN_WIDTH
TOOLTIP_PREVIEW_HEIGHT = 116
TOOLTIP_ROW_SPACING = 6


def location_var(name: str) -> str:
    return f"LocationView.GetLocation.MakeScope.GetVariable('{name}')"


def compact_slot_var(slot: int, suffix: str) -> str:
    return location_var(f"tv_wonder_display_slot_{slot}_{suffix}")


def tooltip_slot_var(slot: int, suffix: str) -> str:
    return location_var(f"tv_wonder_tooltip_slot_{slot}_{suffix}")


def slot_id_var(slot_type: str, slot: int) -> str:
    return compact_slot_var(slot, "id") if slot_type == "compact" else tooltip_slot_var(slot, "id")


def slot_level_var(slot_type: str, slot: int) -> str:
    return compact_slot_var(slot, "level") if slot_type == "compact" else tooltip_slot_var(slot, "level")


def slot_ritual_style_var(slot_type: str, slot: int) -> str:
    return compact_slot_var(slot, "ritual_style") if slot_type == "compact" else tooltip_slot_var(slot, "ritual_style")


def fixed_point_to_int_string(var_expr: str) -> str:
    return f"ToString_int32(FixedPointToInt({var_expr}.GetValue))"


def slot_id_string(slot_type: str, slot: int) -> str:
    return fixed_point_to_int_string(slot_id_var(slot_type, slot))


def slot_level_string(slot_type: str, slot: int) -> str:
    return fixed_point_to_int_string(slot_level_var(slot_type, slot))


def slot_ritual_style_string(slot_type: str, slot: int) -> str:
    return fixed_point_to_int_string(slot_ritual_style_var(slot_type, slot))


def var_enabled_expr(var_expr: str) -> str:
    return f"And({var_expr}.IsSet, Not(EqualTo_CFixedPoint({var_expr}.GetValue, '(CFixedPoint)0.0')))"


def any_wonder_visible_expr() -> str:
    return var_enabled_expr(ANY_WONDER_VAR)


def slot_has_id_expr(slot_type: str, slot: int) -> str:
    return f"{slot_id_var(slot_type, slot)}.IsSet"


def slot_has_payload_expr(slot_type: str, slot: int) -> str:
    return (
        f"And({slot_id_var(slot_type, slot)}.IsSet, "
        f"And({slot_level_var(slot_type, slot)}.IsSet, {slot_ritual_style_var(slot_type, slot)}.IsSet))"
    )


def slot_level_is_expr(slot_type: str, slot: int, level: int) -> str:
    level_var = slot_level_var(slot_type, slot)
    return f"And({level_var}.IsSet, EqualTo_CFixedPoint({level_var}.GetValue, '(CFixedPoint){level}.0'))"


def slot_has_effect_payload_expr(slot_type: str, slot: int) -> str:
    return f"And({slot_has_payload_expr(slot_type, slot)}, Not({slot_level_is_expr(slot_type, slot, 0)}))"


def slot_name_expr(slot_type: str, slot: int) -> str:
    return f"Localize(Concatenate('game_concept_{DISPLAY_CONCEPT_PREFIX}', {slot_id_string(slot_type, slot)}))"


def slot_image_expr(slot_type: str, slot: int) -> str:
    return f"GetConceptTexture(Concatenate('{IMAGE_CONCEPT_PREFIX}', {slot_id_string(slot_type, slot)}))"


def slot_modifier_key_expr(slot_type: str, slot: int) -> str:
    return (
        f"Concatenate('{DISPLAY_CONCEPT_PREFIX}', "
        f"Concatenate({slot_id_string(slot_type, slot)}, Concatenate('_level_', {slot_level_string(slot_type, slot)})))"
    )


def slot_ritual_effect_key_expr(slot_type: str, slot: int) -> str:
    return (
        f"Concatenate('{DISPLAY_CONCEPT_PREFIX}', "
        f"Concatenate({slot_id_string(slot_type, slot)}, "
        f"Concatenate('_ritual_', Concatenate({slot_ritual_style_string(slot_type, slot)}, "
        "'_location_tooltip_effect'))))"
    )


def render_separator(indent: str) -> list[str]:
    return [
        f"{indent}widget = {{",
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}size = {{ -1 {PANEL_SEPARATOR_HEIGHT} }}",
        f"{indent}{T}background = {{",
        f'{indent}{T}{T}texture = "gfx/interface/colors/black.dds"',
        f"{indent}{T}{T}alpha = 0.16",
        f"{indent}{T}}}",
        f"{indent}}}",
    ]


def render_level_line(indent: str, *, slot_type: str, slot: int) -> list[str]:
    level_var = slot_level_var(slot_type, slot)
    return [
        f"{indent}hbox = {{",
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}layoutpolicy_vertical = fixed",
        f"{indent}{T}size = {{ -1 18 }}",
        f"{indent}{T}spacing = 4",
        f"{indent}{T}text_single = {{",
        f'{indent}{T}{T}text = "TV_LOCATION_WONDER_LEVEL_SHORT"',
        f"{indent}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}fontsize = 13",
        f"{indent}{T}}}",
        f"{indent}{T}text_single = {{",
        f'{indent}{T}{T}visible = "[{level_var}.IsSet]"',
        f'{indent}{T}{T}text = "[{level_var}.GetValue|0]"',
        f"{indent}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}fontsize = 13",
        f"{indent}{T}}}",
        f"{indent}}}",
    ]


def render_compact_slot_summary(indent: str, *, slot: int) -> list[str]:
    visible = slot_has_id_expr("compact", slot)
    lines = [
        f"{indent}text_single = {{",
        f'{indent}{T}visible = "[{visible}]"',
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f'{indent}{T}text = "[{slot_name_expr("compact", slot)}]"',
        f"{indent}{T}align = left|nobaseline",
        f"{indent}{T}autoresize = no",
        f"{indent}{T}fontsize = 15",
        f"{indent}}}",
    ]
    lines.extend(render_level_line(indent, slot_type="compact", slot=slot))
    return lines


def render_dynamic_image(indent: str, *, slot_type: str, slot: int, width: int, height: int) -> list[str]:
    visible = slot_has_id_expr(slot_type, slot)
    return [
        f"{indent}widget = {{",
        f'{indent}{T}visible = "[{visible}]"',
        f"{indent}{T}layoutpolicy_horizontal = fixed",
        f"{indent}{T}layoutpolicy_vertical = fixed",
        f"{indent}{T}size = {{ {width} {height} }}",
        f"{indent}{T}background = {{",
        f'{indent}{T}{T}texture = "[{slot_image_expr(slot_type, slot)}]"',
        f"{indent}{T}{T}texture_density = 2",
        f"{indent}{T}{T}fittype = centercrop",
        f"{indent}{T}}}",
        f"{indent}}}",
    ]


def render_compact_slot_row(indent: str, *, slot: int) -> list[str]:
    lines = [
        f"{indent}widget = {{",
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}size = {{ -1 {PANEL_ROW_HEIGHT} }}",
        f"{indent}{T}using = bg_dark_paper_card",
        f"{indent}{T}hbox = {{",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}spacing = {WONDER_ROW_SPACING}",
        f"{indent}{T}{T}widget = {{",
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = fixed",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}size = {{ {WONDER_TEXT_COLUMN_WIDTH} {PANEL_ROW_HEIGHT} }}",
        f"{indent}{T}{T}{T}vbox = {{",
        f"{indent}{T}{T}{T}{T}margin_left = 8",
        f"{indent}{T}{T}{T}{T}margin_right = 8",
        f"{indent}{T}{T}{T}{T}margin_top = 6",
        f"{indent}{T}{T}{T}{T}margin_bottom = 6",
        f"{indent}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}{T}spacing = 4",
        f"{indent}{T}{T}{T}{T}ignoreinvisible = yes",
    ]
    lines.extend(render_compact_slot_summary(indent + T * 4, slot=slot))
    lines.extend(
        [
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}}}",
            f"{indent}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}layoutpolicy_horizontal = fixed",
            f"{indent}{T}{T}{T}layoutpolicy_vertical = fixed",
            f"{indent}{T}{T}{T}size = {{ {WONDER_PREVIEW_COLUMN_WIDTH} {PANEL_ROW_HEIGHT} }}",
            f"{indent}{T}{T}{T}vbox = {{",
            f"{indent}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
            f"{indent}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
            f"{indent}{T}{T}{T}{T}margin_top = 4",
            f"{indent}{T}{T}{T}{T}margin_bottom = 4",
            f"{indent}{T}{T}{T}{T}widget = {{",
            f"{indent}{T}{T}{T}{T}{T}layoutpolicy_horizontal = fixed",
            f"{indent}{T}{T}{T}{T}{T}layoutpolicy_vertical = fixed",
            f"{indent}{T}{T}{T}{T}{T}using = bg_cabinet_card_frame",
            f"{indent}{T}{T}{T}{T}{T}size = {{ {WONDER_PREVIEW_COLUMN_WIDTH} {PANEL_PREVIEW_HEIGHT} }}",
        ]
    )
    lines.extend(render_dynamic_image(indent + T * 6, slot_type="compact", slot=slot, width=WONDER_PREVIEW_COLUMN_WIDTH, height=PANEL_PREVIEW_HEIGHT))
    lines.extend(
        [
            f"{indent}{T}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}{T}}}",
            f"{indent}{T}{T}{T}}}",
            f"{indent}{T}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_panel_card(indent: str) -> list[str]:
    lines = [
        f"{indent}widget = {{",
        f'{indent}{T}visible = "[{any_wonder_visible_expr()}]"',
        f"{indent}{T}size = {{ {PANEL_WIDTH} {PANEL_HEIGHT} }}",
        f"{indent}{T}parentanchor = right|top",
        f"{indent}{T}widgetanchor = right|top",
        f"{indent}{T}position = {{ -{LOCATION_SCENE_CARD_MARGIN} {LOCATION_SCENE_CARD_MARGIN} }}",
        f"{indent}{T}allow_outside = yes",
        f"{indent}{T}using = bg_paper_card",
        f"{indent}{T}using = bg_cabinet_card_frame",
        f"{indent}{T}button = {{",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}size = {{ 100% 100% }}",
        f"{indent}{T}{T}tooltipwidget = {{ using = tv_location_wonder_tooltip }}",
        f"{indent}{T}{T}vbox = {{",
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}{T}spacing = {PANEL_SEPARATOR_HEIGHT}",
    ]
    for slot in range(1, COMPACT_SLOT_MAX + 1):
        lines.extend(render_compact_slot_row(indent + T * 4, slot=slot))
        if slot < COMPACT_SLOT_MAX:
            lines.extend(render_separator(indent + T * 4))
    lines.extend(
        [
            f"{indent}{T}{T}}}",
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_tooltip_text_column(indent: str, *, slot: int) -> list[str]:
    visible = slot_has_id_expr("tooltip", slot)
    lines = [
        f"{indent}widget = {{",
        f"{indent}{T}layoutpolicy_horizontal = fixed",
        f"{indent}{T}layoutpolicy_vertical = fixed",
        f"{indent}{T}size = {{ {TOOLTIP_TEXT_COLUMN_WIDTH} {TOOLTIP_PREVIEW_HEIGHT} }}",
        f"{indent}{T}vbox = {{",
        f"{indent}{T}{T}margin_left = 8",
        f"{indent}{T}{T}margin_right = 8",
        f"{indent}{T}{T}margin_top = 6",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}spacing = 4",
        f"{indent}{T}{T}ignoreinvisible = yes",
        f"{indent}{T}{T}text_single = {{",
        f'{indent}{T}{T}{T}visible = "[{visible}]"',
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f'{indent}{T}{T}{T}text = "[{slot_name_expr("tooltip", slot)}]"',
        f"{indent}{T}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}{T}autoresize = no",
        f"{indent}{T}{T}{T}fontsize = 15",
        f"{indent}{T}{T}}}",
    ]
    lines.extend(render_level_line(indent + T * 2, slot_type="tooltip", slot=slot))
    lines.extend(
        [
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_tooltip_preview_column(indent: str, *, slot: int) -> list[str]:
    lines = [
        f"{indent}widget = {{",
        f"{indent}{T}layoutpolicy_horizontal = fixed",
        f"{indent}{T}layoutpolicy_vertical = fixed",
        f"{indent}{T}size = {{ {TOOLTIP_PREVIEW_COLUMN_WIDTH} {TOOLTIP_PREVIEW_HEIGHT} }}",
        f"{indent}{T}vbox = {{",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = expanding",
        f"{indent}{T}{T}margin_top = 6",
        f"{indent}{T}{T}widget = {{",
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = fixed",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = fixed",
        f"{indent}{T}{T}{T}using = bg_cabinet_card_frame",
        f"{indent}{T}{T}{T}size = {{ {TOOLTIP_PREVIEW_COLUMN_WIDTH} {TOOLTIP_PREVIEW_HEIGHT} }}",
    ]
    lines.extend(render_dynamic_image(indent + T * 4, slot_type="tooltip", slot=slot, width=TOOLTIP_PREVIEW_COLUMN_WIDTH, height=TOOLTIP_PREVIEW_HEIGHT))
    lines.extend(
        [
            f"{indent}{T}{T}{T}}}",
            f"{indent}{T}{T}}}",
            f"{indent}{T}}}",
        ]
    )
    return lines


def render_tooltip_effect_block(indent: str, *, slot: int) -> list[str]:
    visible = slot_has_effect_payload_expr("tooltip", slot)
    no_effect_visible = slot_level_is_expr("tooltip", slot, 0)
    modifier_key = slot_modifier_key_expr("tooltip", slot)
    ritual_effect_key = slot_ritual_effect_key_expr("tooltip", slot)
    return [
        f"{indent}widget = {{",
        f"{indent}{T}layoutpolicy_horizontal = fixed",
        f"{indent}{T}layoutpolicy_vertical = shrinking",
        f"{indent}{T}size = {{ {TOOLTIP_ROW_WIDTH} -1 }}",
        f"{indent}{T}vbox = {{",
        f"{indent}{T}{T}set_parent_size_to_minimum = yes",
        f"{indent}{T}{T}margin_left = 8",
        f"{indent}{T}{T}margin_right = 8",
        f"{indent}{T}{T}margin_bottom = 6",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = shrinking",
        f"{indent}{T}{T}spacing = 0",
        f"{indent}{T}{T}ignoreinvisible = yes",
        f"{indent}{T}{T}TooltipTextBlock = {{",
        f'{indent}{T}{T}{T}visible = "[{no_effect_visible}]"',
        f'{indent}{T}{T}{T}blockoverride "text" {{',
        f'{indent}{T}{T}{T}{T}text = "TV_LOCATION_WONDER_NO_EFFECT"',
        f"{indent}{T}{T}{T}}}",
        f"{indent}{T}{T}}}",
        f"{indent}{T}{T}TooltipStringPairList = {{",
        f'{indent}{T}{T}{T}visible = "[{visible}]"',
        f'{indent}{T}{T}{T}textcontext = "[ShowModifierEffect({modifier_key})]"',
        f"{indent}{T}{T}}}",
        f"{indent}{T}{T}hbox = {{",
        f'{indent}{T}{T}{T}visible = "[{visible}]"',
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = shrinking",
        f"{indent}{T}{T}{T}margin_top = 6",
        f"{indent}{T}{T}{T}text_single = {{",
        f'{indent}{T}{T}{T}{T}text = "TV_LOCATION_WONDER_RITUAL_TITLE_PREFIX"',
        f"{indent}{T}{T}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}{T}{T}fontsize = 13",
        f"{indent}{T}{T}{T}}}",
        f"{indent}{T}{T}}}",
        f"{indent}{T}{T}TooltipRequirementsList = {{",
        f'{indent}{T}{T}{T}visible = "[{visible}]"',
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f'{indent}{T}{T}{T}textcontext = "[ShowScriptedEffectForScope({ritual_effect_key},{LOCATION_SCOPE})]"',
        f'{indent}{T}{T}{T}blockoverride "block_title" {{',
        f'{indent}{T}{T}{T}{T}block "block_title" {{',
        f"{indent}{T}{T}{T}{T}{T}visible = no",
        f"{indent}{T}{T}{T}{T}}}",
        f"{indent}{T}{T}{T}}}",
        f'{indent}{T}{T}{T}blockoverride "requirementslist_datamodel_is_empty" {{',
        f"{indent}{T}{T}{T}{T}visible = no",
        f"{indent}{T}{T}{T}}}",
        f"{indent}{T}{T}}}",
        f"{indent}{T}}}",
        f"{indent}}}",
    ]


def render_tooltip_row(indent: str, *, slot: int) -> list[str]:
    visible = slot_has_id_expr("tooltip", slot)
    lines = [
        f"{indent}widget = {{",
        f'{indent}{T}visible = "[{visible}]"',
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}layoutpolicy_vertical = shrinking",
        f"{indent}{T}minimumsize = {{ {TOOLTIP_ROW_WIDTH} -1 }}",
        f"{indent}{T}using = bg_paper_card",
        f"{indent}{T}using = bg_cabinet_card_frame",
        f"{indent}{T}vbox = {{",
        f"{indent}{T}{T}set_parent_size_to_minimum = yes",
        f"{indent}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}layoutpolicy_vertical = shrinking",
        f"{indent}{T}{T}spacing = {WONDER_ROW_SPACING}",
        f"{indent}{T}{T}hbox = {{",
        f"{indent}{T}{T}{T}set_parent_size_to_minimum = yes",
        f"{indent}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}{T}{T}layoutpolicy_vertical = shrinking",
        f"{indent}{T}{T}{T}spacing = {WONDER_ROW_SPACING}",
    ]
    lines.extend(render_tooltip_text_column(indent + T * 3, slot=slot))
    lines.extend(render_tooltip_preview_column(indent + T * 3, slot=slot))
    lines.append(f"{indent}{T}{T}}}")
    lines.extend(render_tooltip_effect_block(indent + T * 2, slot=slot))
    lines.extend(
        [
            f"{indent}{T}}}",
            f"{indent}}}",
        ]
    )
    return lines


def render_overflow_line(indent: str) -> list[str]:
    visible = var_enabled_expr(OVERFLOW_VAR)
    return [
        f"{indent}hbox = {{",
        f'{indent}{T}visible = "[{visible}]"',
        f"{indent}{T}layoutpolicy_horizontal = expanding",
        f"{indent}{T}layoutpolicy_vertical = fixed",
        f"{indent}{T}size = {{ {TOOLTIP_ROW_WIDTH} 20 }}",
        f"{indent}{T}margin_left = 8",
        f"{indent}{T}spacing = 4",
        f"{indent}{T}text_single = {{",
        f'{indent}{T}{T}text = "TV_LOCATION_WONDER_OVERFLOW_PREFIX"',
        f"{indent}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}fontsize = 13",
        f"{indent}{T}}}",
        f"{indent}{T}text_single = {{",
        f'{indent}{T}{T}text = "[{OVERFLOW_VAR}.GetValue|0]"',
        f"{indent}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}fontsize = 13",
        f"{indent}{T}}}",
        f"{indent}{T}text_single = {{",
        f'{indent}{T}{T}text = "TV_LOCATION_WONDER_OVERFLOW_SUFFIX"',
        f"{indent}{T}{T}align = left|nobaseline",
        f"{indent}{T}{T}fontsize = 13",
        f"{indent}{T}}}",
        f"{indent}}}",
    ]


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
        f"{T}{T}{T}{T}{T}set_parent_dimension_to_minimum = height",
        f"{T}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{T}{T}{T}{T}{T}ignoreinvisible = yes",
        f"{T}{T}{T}{T}{T}spacing = {TOOLTIP_ROW_SPACING}",
    ]
    for slot in range(1, TOOLTIP_SLOT_MAX + 1):
        lines.extend(render_tooltip_row(T * 5, slot=slot))
    lines.extend(render_overflow_line(T * 5))
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
    return "\n".join(render_panel_card(T * 4))


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
    return "\n".join(line.rstrip() for line in "\n".join(lines).splitlines()).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
