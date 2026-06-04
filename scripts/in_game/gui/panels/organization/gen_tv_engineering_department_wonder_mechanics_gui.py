import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ceremony_styles,
    final_building_for_style,
    load_all_wonder_mechanics_data,
    render_header,
    ritual_plan_for_style,
    suitability_current_actual_variable,
    suitability_current_revealed_variable,
    suitability_knowledge_for_wonder,
)

OUT_FILE = REPO_ROOT / "data" / "generated_fragments" / "tv_engineering_department_wonder_mechanics.gui"
SCRIPT_REL = "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py"
T = "\t"
PLAYER = "InternationalOrganizationsView.GetPlayer.MakeScope"
PLAYER_SCOPE = f"{PLAYER}.Self"
SUITABILITY_CONDITION_LOC_KEYS = {
    "topography_mountains": "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_MOUNTAINS",
    "topography_plateau": "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_PLATEAU",
    "topography_hills": "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_HILLS",
    "vegetation_forest": "TV_ENGINEERING_SUITABILITY_CONDITION_VEGETATION_FOREST",
    "vegetation_woods": "TV_ENGINEERING_SUITABILITY_CONDITION_VEGETATION_WOODS",
    "rank_rural": "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_RURAL",
    "rank_city": "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_CITY",
    "rank_megalopolis": "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_MEGALOPOLIS",
    "neighbor_city": "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_CITY",
    "neighbor_town": "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_TOWN",
    "has_monastery": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_MONASTERY",
    "has_cathedral": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_CATHEDRAL",
    "dominant_religion_owner": "TV_ENGINEERING_SUITABILITY_CONDITION_DOMINANT_RELIGION_OWNER",
    "has_bridge_infrastructure": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_BRIDGE_INFRASTRUCTURE",
    "neighbor_bridge_opening": "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_BRIDGE_OPENING",
    "waterway_or_port": "TV_ENGINEERING_SUITABILITY_CONDITION_WATERWAY_OR_PORT",
    "is_port": "TV_ENGINEERING_SUITABILITY_CONDITION_IS_PORT",
    "fort_level": "TV_ENGINEERING_SUITABILITY_CONDITION_FORT_LEVEL",
    "urban_rank": "TV_ENGINEERING_SUITABILITY_CONDITION_URBAN_RANK",
    "is_capital": "TV_ENGINEERING_SUITABILITY_CONDITION_IS_CAPITAL",
    "raw_coin_metal": "TV_ENGINEERING_SUITABILITY_CONDITION_RAW_COIN_METAL",
    "has_armory": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_ARMORY",
}
SUITABILITY_SOURCE_LOC_KEYS = {
    "development": "TV_ENGINEERING_SUITABILITY_SOURCE_DEVELOPMENT",
    "total_building_levels": "TV_ENGINEERING_SUITABILITY_SOURCE_TOTAL_BUILDING_LEVELS",
    "harbor_suitability": "TV_ENGINEERING_SUITABILITY_SOURCE_HARBOR_SUITABILITY",
    "average_location_literacy": "TV_ENGINEERING_SUITABILITY_SOURCE_AVERAGE_LOCATION_LITERACY",
}
SUITABILITY_KNOWLEDGE_COLUMNS_WIDTH = 444
SUITABILITY_KNOWLEDGE_COLUMN_WIDTH = 218
SUITABILITY_KNOWLEDGE_COLUMN_SPACING = 8
SUITABILITY_ROW_LABEL_MAX_WIDTH = 168
SUITABILITY_ROW_HIDDEN_MAX_WIDTH = 214
SUITABILITY_LOCATION_CONDITION_ROW_HEIGHT = 22


def eq(var: str, value: int) -> str:
    return f"EqualTo_CFixedPoint({PLAYER}.GetVariable('{var}').GetValue, '(CFixedPoint){value}.0')"


def fmt_decimal(value: Decimal) -> str:
    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def fmt_numeric_text(value: object) -> str:
    try:
        return fmt_decimal(Decimal(str(value)))
    except (InvalidOperation, ValueError):
        return str(value)


def fmt_bonus_text(value: object) -> str:
    text = fmt_numeric_text(value)
    if text.startswith("-"):
        return f"#N {text}#!"
    return f"#P +{text}#!"


def scaled_bonus_value(row: dict[str, str]) -> str:
    try:
        maximum = Decimal(str(row["max"]))
        multiplier = Decimal(str(row["multiplier"]))
        return fmt_decimal(maximum * multiplier)
    except (InvalidOperation, ValueError):
        return str(row["multiplier"])


def reveal_progress_visible(var: str, row_index: int) -> str:
    return (
        f"And({PLAYER}.GetVariable('{var}').IsSet, "
        f"GreaterThanOrEqualTo_CFixedPoint({PLAYER}.GetVariable('{var}').GetValue, '(CFixedPoint){row_index}.0'))"
    )


def fold_bool(op: str, terms: list[str]) -> str:
    if not terms:
        return "False" if op == "Or" else "True"
    if len(terms) == 1:
        return terms[0]
    expr = f"{op}({terms[0]}, {terms[1]})"
    for term in terms[2:]:
        expr = f"{op}({expr}, {term})"
    return expr


def wonder_visible(wonder_id: int) -> str:
    return (
        "[Or("
        f"And({PLAYER}.GetVariable('tv_wonder_locked').IsSet, {eq('tv_wonder_locked', wonder_id)}), "
        f"And3(Not({PLAYER}.GetVariable('tv_wonder_locked').IsSet), {PLAYER}.GetVariable('tv_wonder_proposal').IsSet, {eq('tv_wonder_proposal', wonder_id)})"
        ")]"
    )


def or_eq(var: str, values: list[int]) -> str:
    return fold_bool("Or", [eq(var, value) for value in values])


def ritual_pair_visible(pairs: list[tuple[int, int]]) -> str:
    return fold_bool(
        "Or",
        [f"And({eq('tv_wonder_locked', wonder_id)}, {eq('tv_wonder_ceremony_style', style)})" for wonder_id, style in pairs],
    )


def fixed_point_to_int_string(var_expr: str) -> str:
    return f"ToString_int32(FixedPointToInt({var_expr}.GetValue))"


def proposal_slot_var(slot: int) -> str:
    return f"{PLAYER}.GetVariable('tv_wonder_proposal_slot_{slot}')"


def proposal_button(slot: int) -> str:
    slot_var = proposal_slot_var(slot)
    slot_id_string = fixed_point_to_int_string(slot_var)
    text = f"[SelectGameConcept({slot_var}.IsSet, Concatenate('tv_wonder_display_', {slot_id_string}), 'tv_wonder_construction')]"
    return (
        f'{T}action_button_diamond = {{ size = {{ 152 30 }} visible = "[{slot_var}.IsSet]" '
        f'text = "{text}" title = "tv_wonder_select_proposal_slot_{slot}" '
        f'description = "tv_wonder_select_proposal_slot_{slot}_desc" actor = "[InternationalOrganizationsView.GetPlayer]" '
        f'left_action = {{ action_name = "tv_wonder_select_proposal_slot_{slot}" }} }}'
    )


def proposal_text(wonder: dict, suffix: str = "") -> str:
    key = f"TV_ENGINEERING_PROPOSAL{suffix}_{wonder['key'].upper()}_TEXT"
    return (
        f'{T}text_multi = {{ visible = "[{eq("tv_wonder_proposal", wonder["id"])}]" '
        f'max_width = 352 autoresize = yes text = "{key}" align = nobaseline|left }}'
    )


def locked_text(wonder: dict, max_width: int = 352) -> str:
    return (
        f'{T}text_multi = {{ visible = "[{eq("tv_wonder_locked", wonder["id"])}]" '
        f'max_width = {max_width} autoresize = yes text = "TV_ENGINEERING_LOCKED_{wonder["key"].upper()}_TEXT" align = nobaseline|left }}'
    )


def preview_texture(wonder: dict) -> str:
    image = wonder.get("image", f"tv_wonder_{wonder['key']}")
    return f"gfx/interface/illustrations/towards_victory/wonders/{image}.dds"


def ceremony_name_key(wonder: dict, style: int) -> str:
    building = final_building_for_style(wonder, style)
    return f"TV_ENGINEERING_CEREMONY_{building.removeprefix('tv_wonder_').upper()}_BUTTON"


def ceremony_select_button(wonder: dict, style: int) -> str:
    locked_visible = eq("tv_wonder_locked", wonder["id"])
    selected_down = eq("tv_wonder_ceremony_style", style)
    return (
        f'{T}action_button_diamond = {{ visible = "[{locked_visible}]" size = {{ 150 30 }} '
        f'text = "{ceremony_name_key(wonder, style)}" '
        f'down = "[{selected_down}]" title = "tv_wonder_choose_ceremony_style_{style}" '
        f'description = "tv_wonder_choose_ceremony_style_{style}_desc" actor = "[InternationalOrganizationsView.GetPlayer]" '
        f'left_action = {{ action_name = "tv_wonder_choose_ceremony_style_{style}" }} }}'
    )


def ritual_requirement_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_requirement_tooltip_effect"


def ritual_effect_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_effect_tooltip_effect"


def active_ritual_visible(wonder: dict, style: int) -> str:
    return (
        f"And3({PLAYER}.GetVariable('tv_wonder_locked').IsSet, "
        f"{PLAYER}.GetVariable('tv_wonder_ceremony_style').IsSet, "
        f"And({eq('tv_wonder_locked', wonder['id'])}, {eq('tv_wonder_ceremony_style', style)}))"
    )


def scripted_effect_tooltip(effect_name: str, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}TooltipRequirementsList = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f'{prefix}{T}textcontext = "[ShowScriptedEffectForScope(\'{effect_name}\',{PLAYER_SCOPE})]"',
        f'{prefix}{T}blockoverride "block_title" {{',
        f'{prefix}{T}{T}block "block_title" {{',
        f"{prefix}{T}{T}{T}visible = no",
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}}}",
        f'{prefix}{T}blockoverride "requirementslist_datamodel_is_empty" {{',
        f"{prefix}{T}{T}visible = no",
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]


def trigger_conditions_list(trigger_name: str, indent: int, width: int | None = None) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}TooltipRequirementsList = {{",
        f"{prefix}{T}layoutpolicy_horizontal = {'fixed' if width is not None else 'expanding'}",
        f'{prefix}{T}textcontext = "[ShowTriggerConditions(\'{trigger_name}\', PlayerScope.Self)]"',
    ]
    if width is not None:
        lines.extend(
            [
                f"{prefix}{T}maximumsize = {{ {width} -1 }}",
                f'{prefix}{T}blockoverride "tooltip_minimumsize" {{ minimumsize = {{ {width} -1 }} }}',
            ]
        )
    lines.extend(
        [
            f'{prefix}{T}blockoverride "field_text_format" {{',
            f"{prefix}{T}{T}fontsize = 13",
            f"{prefix}{T}}}",
            f'{prefix}{T}blockoverride "row_size" {{',
            f"{prefix}{T}{T}maximumsize = {{ -1 {SUITABILITY_LOCATION_CONDITION_ROW_HEIGHT} }}",
            f"{prefix}{T}{T}minimumsize = {{ -1 {SUITABILITY_LOCATION_CONDITION_ROW_HEIGHT} }}",
            f"{prefix}{T}}}",
            f'{prefix}{T}blockoverride "block_title" {{',
            f'{prefix}{T}{T}block "block_title" {{',
            f"{prefix}{T}{T}{T}visible = no",
            f"{prefix}{T}{T}}}",
            f"{prefix}{T}}}",
            f'{prefix}{T}blockoverride "requirementslist_datamodel_is_empty" {{',
            f"{prefix}{T}{T}visible = no",
            f"{prefix}{T}}}",
            f"{prefix}}}",
        ]
    )
    return lines


def suitability_row_label_key(row: dict[str, str]) -> str:
    if row["type"] == "condition_bonus":
        condition = row["condition"]
        if condition not in SUITABILITY_CONDITION_LOC_KEYS:
            raise ValueError(f"Missing suitability condition loc key mapping for {condition}")
        return SUITABILITY_CONDITION_LOC_KEYS[condition]
    source = row["source"]
    if source not in SUITABILITY_SOURCE_LOC_KEYS:
        raise ValueError(f"Missing suitability source loc key mapping for {source}")
    return SUITABILITY_SOURCE_LOC_KEYS[source]


def suitability_row_value(row: dict[str, str]) -> str:
    if row["type"] == "condition_bonus":
        return fmt_bonus_text(row["value"])
    return fmt_bonus_text(scaled_bonus_value(row))


def suitability_row_actual_complete_visible(actual_var: str) -> str:
    return (
        f"And({PLAYER}.GetVariable('tv_wonder_survey_complete').IsSet, "
        f"{PLAYER}.GetVariable('{actual_var}').IsSet)"
    )


def suitability_row_actual_text(actual_var: str, row: dict[str, str]) -> str:
    maximum = suitability_row_value(row)
    return f"#P [{PLAYER}.GetVariable('{actual_var}').GetValue|+=]#!/{maximum}"


def suitability_row_unknown_text(row: dict[str, str]) -> str:
    return f"#T ?#!/{suitability_row_value(row)}"


def suitability_knowledge_row(row: dict[str, str], reveal_var: str, row_index: int, indent: int) -> list[str]:
    prefix = T * indent
    revealed = reveal_progress_visible(reveal_var, row_index)
    actual_var = suitability_current_actual_variable(row_index)
    completed = suitability_row_actual_complete_visible(actual_var)
    return [
        f"{prefix}hbox = {{",
        f'{prefix}{T}visible = "[{revealed}]"',
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}spacing = 4",
        f'{prefix}{T}text_single = {{ text = "{suitability_row_label_key(row)}" max_width = {SUITABILITY_ROW_LABEL_MAX_WIDTH} fontsize = 13 align = nobaseline|left }}',
        f"{prefix}{T}expand = {{}}",
        f'{prefix}{T}text_single = {{ visible = "[{completed}]" raw_text = "{suitability_row_actual_text(actual_var, row)}" fontsize = 13 align = nobaseline|right }}',
        f'{prefix}{T}text_single = {{ visible = "[Not({completed})]" raw_text = "{suitability_row_unknown_text(row)}" fontsize = 13 align = nobaseline|right }}',
        f"{prefix}}}",
        f"{prefix}text_single = {{",
        f'{prefix}{T}visible = "[Not({revealed})]"',
        f'{prefix}{T}text = "TV_ENGINEERING_SUITABILITY_ROW_HIDDEN"',
        f"{prefix}{T}max_width = {SUITABILITY_ROW_HIDDEN_MAX_WIDTH}",
        f"{prefix}{T}fontsize = 13",
        f"{prefix}{T}align = nobaseline|left",
        f"{prefix}}}",
    ]


def suitability_knowledge_display(wonder: dict, mechanics: dict) -> str:
    rows = suitability_knowledge_for_wonder(mechanics, wonder)
    reveal_var = suitability_current_revealed_variable()
    visible = f"And({PLAYER}.GetVariable('tv_wonder_locked').IsSet, {eq('tv_wonder_locked', wonder['id'])})"
    min_height = 82 + len(rows) * 20
    lines: list[str] = [
        f"{T}widget = {{",
        f'{T}{T}visible = "[{visible}]"',
        f"{T}{T}layoutpolicy_vertical = shrinking",
        f"{T}{T}minimumsize = {{ 462 {min_height} }}",
        f"{T}{T}using = bg_text_mask_container_dark_blue",
        "",
        f"{T}{T}vbox = {{",
        f"{T}{T}{T}set_parent_size_to_minimum = yes",
        f"{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{T}{T}{T}layoutpolicy_vertical = shrinking",
        f"{T}{T}{T}margin = {{ 6 5 }}",
        f"{T}{T}{T}ignoreinvisible = yes",
        f"{T}{T}{T}spacing = 3",
        f'{T}{T}{T}text_single = {{ text = "TV_ENGINEERING_SUITABILITY_KNOWLEDGE_TITLE" fontsize = 18 align = nobaseline|left }}',
        f"{T}{T}{T}hbox = {{",
        f"{T}{T}{T}{T}layoutpolicy_horizontal = fixed",
        f"{T}{T}{T}{T}size = {{ {SUITABILITY_KNOWLEDGE_COLUMNS_WIDTH} -1 }}",
        f"{T}{T}{T}{T}spacing = {SUITABILITY_KNOWLEDGE_COLUMN_SPACING}",
        f"{T}{T}{T}{T}ignoreinvisible = yes",
        f"{T}{T}{T}{T}vbox = {{",
        f"{T}{T}{T}{T}{T}layoutpolicy_horizontal = fixed",
        f"{T}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
        f"{T}{T}{T}{T}{T}minimumsize = {{ {SUITABILITY_KNOWLEDGE_COLUMN_WIDTH} -1 }}",
        f"{T}{T}{T}{T}{T}maximumsize = {{ {SUITABILITY_KNOWLEDGE_COLUMN_WIDTH} -1 }}",
        f"{T}{T}{T}{T}{T}ignoreinvisible = yes",
        f"{T}{T}{T}{T}{T}spacing = 3",
        f'{T}{T}{T}{T}{T}text_single = {{ text = "TV_ENGINEERING_SUITABILITY_LOCATION_CONDITIONS_TITLE" max_width = {SUITABILITY_KNOWLEDGE_COLUMN_WIDTH} fontsize = 13 align = nobaseline|left }}',
    ]
    lines.extend(
        trigger_conditions_list(
            f"tv_wonder_player_visible_site_rules_{wonder['key']}_trigger",
            5,
            width=SUITABILITY_KNOWLEDGE_COLUMN_WIDTH,
        )
    )
    lines.extend(
        [
            f"{T}{T}{T}{T}}}",
            f"{T}{T}{T}{T}vbox = {{",
            f"{T}{T}{T}{T}{T}layoutpolicy_horizontal = fixed",
            f"{T}{T}{T}{T}{T}layoutpolicy_vertical = expanding",
            f"{T}{T}{T}{T}{T}minimumsize = {{ {SUITABILITY_KNOWLEDGE_COLUMN_WIDTH} -1 }}",
            f"{T}{T}{T}{T}{T}maximumsize = {{ {SUITABILITY_KNOWLEDGE_COLUMN_WIDTH} -1 }}",
            f"{T}{T}{T}{T}{T}ignoreinvisible = yes",
            f"{T}{T}{T}{T}{T}spacing = 3",
        ]
    )
    if rows:
        lines.extend(
            [
                f'{T}{T}{T}{T}{T}text_single = {{ text = "TV_ENGINEERING_SUITABILITY_CONDITIONS_TITLE" max_width = {SUITABILITY_KNOWLEDGE_COLUMN_WIDTH} fontsize = 13 align = nobaseline|left }}',
            ]
        )
    for row_index, row in enumerate(rows, start=1):
        lines.extend(suitability_knowledge_row(row, reveal_var, row_index, 5))
    lines.extend(
        [
            f"{T}{T}{T}{T}{T}expand = {{}}",
            f"{T}{T}{T}{T}}}",
            f"{T}{T}{T}}}",
            f"{T}{T}}}",
            f"{T}}}",
        ]
    )
    return "\n".join(lines)


def ritual_info_container(title_key: str, subtitle_key: str, effect_name: str | None, indent: int) -> list[str]:
    prefix = T * indent
    lines = [
        f"{prefix}widget = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}size = {{ 462 136 }}",
        f"{prefix}{T}using = bg_text_mask_container_dark_blue",
        "",
        f"{prefix}{T}vbox = {{",
        f"{prefix}{T}{T}margin = {{ 8 7 }}",
        f"{prefix}{T}{T}ignoreinvisible = yes",
        f"{prefix}{T}{T}spacing = 4",
        f'{prefix}{T}{T}text_single = {{ text = "{title_key}" align = nobaseline|left }}',
        f'{prefix}{T}{T}text_multi = {{ max_width = 446 autoresize = yes text = "{subtitle_key}" align = nobaseline|left }}',
    ]
    if effect_name is not None:
        lines.extend(scripted_effect_tooltip(effect_name, indent + 2))
    lines.extend(
        [
            f"{prefix}{T}}}",
            f"{prefix}}}",
        ]
    )
    return lines


def active_ritual_display(wonder: dict, style: int) -> str:
    visible = active_ritual_visible(wonder, style)
    lines: list[str] = []
    if wonder.get("is_unique"):
        lines.append(f"{T}# TODO: Expand unique-wonder ritual requirements/effects after bespoke ritual designs are finalized.")
    lines.extend(
        [
            f"{T}vbox = {{",
            f'{T}{T}visible = "[{visible}]"',
            f"{T}{T}layoutpolicy_horizontal = expanding",
            f"{T}{T}ignoreinvisible = yes",
            f"{T}{T}spacing = 6",
        ]
    )
    if wonder.get("is_unique"):
        lines.extend(
            ritual_info_container(
                "TV_ENGINEERING_RITUAL_REQUIREMENTS_TITLE",
                "TV_ENGINEERING_RITUAL_REQUIREMENT_UNIQUE_NONE",
                None,
                2,
            )
        )
        lines.extend(
            ritual_info_container(
                "TV_ENGINEERING_RITUAL_EFFECTS_TITLE",
                "TV_ENGINEERING_RITUAL_EFFECT_UNIQUE_SUBTITLE",
                ritual_effect_tooltip_effect_name(wonder, style),
                2,
            )
        )
    else:
        lines.extend(
            ritual_info_container(
                "TV_ENGINEERING_RITUAL_REQUIREMENTS_TITLE",
                f"TV_ENGINEERING_RITUAL_REQUIREMENT_STYLE_{style}_SUBTITLE",
                ritual_requirement_tooltip_effect_name(wonder, style),
                2,
            )
        )
        lines.extend(
            ritual_info_container(
                "TV_ENGINEERING_RITUAL_EFFECTS_TITLE",
                f"TV_ENGINEERING_RITUAL_EFFECT_STYLE_{style}_SUBTITLE",
                ritual_effect_tooltip_effect_name(wonder, style),
                2,
            )
        )
    lines.append(f"{T}}}")
    return "\n".join(lines)


def hold_button_base_visible(max_wonder_id: int) -> str:
    # Once a ritual starts, hide the button instead of leaving a disabled action
    # that still forces EU5 to render the heavy generic-action tooltip.
    return (
        f"And3("
        f"And3({PLAYER}.GetVariable('tv_wonder_locked').IsSet, "
        f"{PLAYER}.GetVariable('tv_wonder_ceremony_style').IsSet, "
        f"LessThanOrEqualTo_CFixedPoint({PLAYER}.GetVariable('tv_wonder_locked').GetValue, '(CFixedPoint){max_wonder_id}.0')), "
        f"Not({PLAYER}.GetVariable('tv_wonder_finalized').IsSet), "
        f"Not({PLAYER}.GetVariable('tv_wonder_ritual_in_progress').IsSet)"
        f")"
    )


def hold_button(action_name: str, visible: str) -> str:
    return (
        f'{T}action_button_diamond = {{ visible = "[{visible}]" '
        'size = { 180 30 } text = "TV_ENGINEERING_HOLD_CEREMONY_BUTTON" title = "tv_wonder_confirm_ceremony" '
        'description = "tv_wonder_confirm_ceremony_desc" actor = "[InternationalOrganizationsView.GetPlayer]" '
        f'left_action = {{ action_name = "{action_name}" }} }}'
    )


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics_data()
    max_wonder_id = max(wonder["id"] for wonder in wonders)
    gold_ritual_pairs: list[tuple[int, int]] = []
    prestige_ritual_pairs: list[tuple[int, int]] = []
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            cost_type = ritual_plan["cost_type"]
            if cost_type == "scaled_gold":
                gold_ritual_pairs.append((wonder["id"], style))
            elif cost_type == "prestige":
                prestige_ritual_pairs.append((wonder["id"], style))

    lines = render_header(SCRIPT_REL)
    lines.append("### BEGIN TV_WONDER_MECHANICS_PREVIEW_WIDGETS")
    for wonder in wonders:
        lines.extend(
            [
                "widget = {",
                f'{T}visible = "{wonder_visible(wonder["id"])}"',
                f"{T}size = {{ 100% 100% }}",
                f"{T}background = {{",
                f'{T}{T}texture = "{preview_texture(wonder)}"',
                f"{T}{T}texture_density = 2",
                f"{T}{T}fittype = centercrop",
                f"{T}}}",
                "}",
            ]
        )
    lines.append("### END TV_WONDER_MECHANICS_PREVIEW_WIDGETS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_TEXTS")
    for wonder in wonders:
        lines.append(proposal_text(wonder))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_RESUME_TEXTS")
    for wonder in wonders:
        lines.append(proposal_text(wonder, "_RESUME"))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_RESUME_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_EXPAND_TEXTS")
    for wonder in wonders:
        lines.append(proposal_text(wonder, "_EXPAND"))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_EXPAND_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_LOCKED_TEXTS")
    for wonder in wonders:
        lines.append(locked_text(wonder))
    lines.append("### END TV_WONDER_MECHANICS_LOCKED_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_SUITABILITY_KNOWLEDGE")
    for wonder in wonders:
        lines.append(suitability_knowledge_display(wonder, mechanics))
    lines.append("### END TV_WONDER_MECHANICS_SUITABILITY_KNOWLEDGE")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_BUTTONS")
    for slot in range(1, 4):
        lines.append(proposal_button(slot))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_BUTTONS")
    lines.append("")
    for style in range(1, 4):
        lines.append(f"### BEGIN TV_WONDER_MECHANICS_CEREMONY_STYLE_{style}_BUTTONS")
        for wonder in wonders:
            if not wonder.get("is_unique") and style in ceremony_styles(wonder):
                lines.append(ceremony_select_button(wonder, style))
        lines.append(f"### END TV_WONDER_MECHANICS_CEREMONY_STYLE_{style}_BUTTONS")
        lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS")
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            lines.append(active_ritual_display(wonder, style))
    lines.append("### END TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_HOLD_BUTTONS")
    base_visible = hold_button_base_visible(max_wonder_id)
    gold_pair_visible = ritual_pair_visible(gold_ritual_pairs)
    prestige_pair_visible = ritual_pair_visible(prestige_ritual_pairs)
    gold_visible = f"And({base_visible}, {gold_pair_visible})"
    prestige_visible = f"And({base_visible}, {prestige_pair_visible})"
    free_visible = f"And3({base_visible}, Not({gold_pair_visible}), Not({prestige_pair_visible}))"
    lines.append(hold_button("tv_wonder_confirm_ceremony", free_visible))
    lines.append(hold_button("tv_wonder_confirm_ceremony_scaled_gold", gold_visible))
    lines.append(hold_button("tv_wonder_confirm_ceremony_prestige", prestige_visible))
    lines.append("### END TV_WONDER_MECHANICS_HOLD_BUTTONS")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
