import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ALL_WONDER_MIN_ID,
    STYLE_3_REWARD_EFFECTS,
    WONDER_MECHANICS_MAX_ID,
    ceremony_modifier_for_style,
    ceremony_styles,
    final_building_for_style,
    indent_script_block,
    load_all_wonder_mechanics,
    render_header,
    ritual_plan_for_style,
    ritual_auxiliary_building,
    ritual_auxiliary_display_modifier_name,
    ritual_blessing_modifier_name,
    ritual_burden_modifier_name,
    ritual_uses_deferred_completion,
    site_preference_lines_for_wonder,
    suitability_actual_variable_for_wonder,
    suitability_knowledge_for_wonder,
    suitability_reveal_variable_for_wonder,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_engineering_department_wonder_mechanics_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py"
T = "\t"
DISPLAY_SLOT_MAX = 3
TOOLTIP_SLOT_MAX = 5
FEASIBLE_GENERIC_DECK_MAP = "tv_wonder_feasible_generic_deck"
FEASIBLE_UNIQUE_DECK_MAP = "tv_wonder_feasible_unique_deck"
RITUAL_SHARED_RUNTIME_VARS = [
    "tv_wonder_ritual_auxiliary_building_finished",
    "tv_wonder_ritual_total_buildings_baseline",
    "tv_wonder_ritual_current_total_buildings",
]
SUITABILITY_CONDITION_SCRIPTS = {
    "topography_mountains": "topography = mountains",
    "topography_plateau": "topography = plateau",
    "topography_hills": "topography = hills",
    "vegetation_forest": "vegetation = forest",
    "vegetation_woods": "vegetation = woods",
    "rank_rural": "location_rank ?= location_rank:rural_settlement",
    "rank_city": "location_rank ?= location_rank:city",
    "rank_megalopolis": "location_rank ?= location_rank:megalopolis",
    "neighbor_city": "any_neighbor_location = { tv_wonder_location_is_city_trigger = yes }",
    "neighbor_town": (
        "NOT = { any_neighbor_location = { tv_wonder_location_is_city_trigger = yes } }\n"
        "any_neighbor_location = { tv_wonder_location_is_town_trigger = yes }"
    ),
    "has_monastery": "has_building = building_type:monastery",
    "has_cathedral": "has_building = building_type:cathedral",
    "dominant_religion_owner": "dominant_religion = owner.religion",
    "has_bridge_infrastructure": "has_building = building_type:bridge_infrastructure",
    "neighbor_bridge_opening": "any_neighbor_location = { has_building = building_type:tv_wonder_bridge_opening }",
    "waterway_or_port": "OR = {\n\thas_river = yes\n\tis_adjacent_to_lake = yes\n\tis_port = yes\n}",
    "is_port": "is_port = yes",
    "fort_level": "modifier:fort_level > 0",
    "urban_rank": "OR = {\n\tlocation_rank ?= location_rank:city\n\tlocation_rank ?= location_rank:megalopolis\n}",
    "is_capital": "is_capital = yes",
    "raw_coin_metal": "OR = {\n\traw_material = goods:goods_gold\n\traw_material = goods:silver\n\traw_material = goods:copper\n}",
    "has_armory": "has_building = building_type:armory",
}
SUITABILITY_SOURCE_EXPRESSIONS = {
    "development": "development",
    "total_building_levels": "total_building_levels",
    "harbor_suitability": "modifier:harbor_suitability",
    "average_location_literacy": "average_location_literacy",
}


def add_site_preference(wonder: dict, mechanics: dict, indent: int = 2) -> list[str]:
    prefix = T * indent
    lines = site_preference_lines_for_wonder(mechanics, wonder, indent)
    if wonder.get("is_unique"):
        lines.append(f"{prefix}tv_wonder_change_scale_competence_target_effect = {{ value = 100 }}")
        lines.append(f"{prefix}tv_wonder_change_logistics_competence_target_effect = {{ value = 20 }}")
        lines.append(f"{prefix}tv_wonder_change_organization_competence_target_effect = {{ value = 20 }}")
    return lines


def fmt_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def country_reward_effect_lines(reward: list[dict], indent: int = 1) -> list[str]:
    prefix = T * indent
    lines: list[str] = []
    for entry in reward:
        effect_type = entry["type"]
        if effect_type in STYLE_3_REWARD_EFFECTS:
            spec = STYLE_3_REWARD_EFFECTS[effect_type]
            effect = spec["effect"]
            scope = spec["scope"]
            value = fmt_value(entry["value"])
            if scope in {"country_scalar", "country_raw"}:
                lines.append(f"{prefix}{effect} = {value}")
            elif scope == "country_value_block":
                lines.append(f"{prefix}{effect} = {{ value = {value} }}")
            elif scope == "ruler_scalar":
                lines.append(f"{prefix}ruler ?= {{ {effect} = {value} }}")
            elif scope == "culture_scalar":
                lines.append(f"{prefix}culture = {{ {effect} = {value} }}")
            elif scope == "location_scalar":
                raise ValueError(f"Location ritual reward effect type must be handled outside country scope: {effect_type}")
            else:
                raise ValueError(f"Unsupported ritual reward scope for {effect_type}: {scope}")
        elif effect_type == "estate_satisfaction":
            estate = entry["estate"]
            lines.append(f"{prefix}if = {{")
            lines.append(f"{prefix}{T}limit = {{ country_has_estate = estate_type:{estate} }}")
            lines.append(f"{prefix}{T}add_estate_satisfaction = {{ type = estate_type:{estate} value = {fmt_value(entry['value'])} }}")
            lines.append(f"{prefix}}}")
        else:
            raise ValueError(f"Unsupported ritual reward effect type: {effect_type}")
    return lines


def reward_effect_lines(reward: list[dict], indent: int = 1) -> list[str]:
    prefix = T * indent
    lines: list[str] = []
    for entry in reward:
        if entry["type"] == "site_prosperity":
            lines.append(f"{prefix}var:tv_wonder_site ?= {{ change_prosperity = {fmt_value(entry['value'])} }}")
        else:
            lines.extend(country_reward_effect_lines([entry], indent))
    return lines


def location_tooltip_reward_effect_lines(reward: list[dict], indent: int = 1) -> list[str]:
    prefix = T * indent
    lines: list[str] = []
    for entry in reward:
        if entry["type"] == "site_prosperity":
            lines.append(f"{prefix}change_prosperity = {fmt_value(entry['value'])}")
        else:
            lines.append(f"{prefix}owner ?= {{")
            lines.extend(country_reward_effect_lines([entry], indent + 1))
            lines.append(f"{prefix}}}")
    return lines


def ritual_entries(wonders: list[dict], mechanics: dict) -> list[tuple[dict, int, dict]]:
    entries: list[tuple[dict, int, dict]] = []
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            entries.append((wonder, style, ritual_plan_for_style(wonder, mechanics, style)))
    return entries


def ritual_runtime_variables(ritual_plan: dict) -> list[str]:
    variables = list(RITUAL_SHARED_RUNTIME_VARS)
    for variable in ritual_plan.get("runtime_variables", []):
        if variable not in variables:
            variables.append(variable)
    return variables


def immediate_ritual_payload_lines(ritual_plan: dict, indent: int) -> list[str]:
    lines: list[str] = []
    lines.extend(indent_script_block(ritual_plan.get("start_effect_script", ""), indent))
    lines.extend(reward_effect_lines(ritual_plan.get("reward", []), indent))
    lines.extend(indent_script_block(ritual_plan.get("completion_effect_script", ""), indent))
    return lines


def snapshot_ritual_payload_lines(ritual_plan: dict, indent: int) -> list[str]:
    return indent_script_block(ritual_plan.get("snapshot_effect_script", ""), indent)


def progress_ritual_payload_lines(ritual_plan: dict, indent: int) -> list[str]:
    return indent_script_block(ritual_plan.get("progress_effect_script", ""), indent)


def completion_ritual_payload_lines(wonder: dict, ritual_plan: dict, indent: int) -> list[str]:
    lines: list[str] = []
    timed = ritual_plan.get("timed", {})
    blessing_modifier = timed.get("blessing_modifier", {})
    if blessing_modifier:
        lines.append(
            f"{T * indent}add_country_modifier = {{ modifier = {ritual_blessing_modifier_name(wonder)} years = -1 mode = add_and_extend }}"
        )
    lines.extend(reward_effect_lines(ritual_plan.get("reward", []), indent))
    lines.extend(indent_script_block(ritual_plan.get("completion_effect_script", ""), indent))
    return lines


def ritual_requirement_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_requirement_tooltip_effect"


def ritual_effect_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_effect_tooltip_effect"


def ritual_location_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_location_tooltip_effect"


def ritual_location_tooltip_effect_alias_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_display_{wonder['id']}_ritual_{style}_location_tooltip_effect"


def location_tooltip_country_modifier_lines(modifier_name: str, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}owner ?= {{",
        f"{prefix}{T}add_country_modifier = {{ modifier = {modifier_name} years = -1 mode = add_and_extend }}",
        f"{prefix}}}",
    ]


def immediate_ritual_cost_lines(ritual_plan: dict, indent: int) -> list[str]:
    prefix = T * indent
    cost_type = ritual_plan.get("cost_type")
    if cost_type is None:
        return []
    if cost_type == "artwork":
        return [
            f"{prefix}random_work_of_art_in_country = {{ save_scope_as = tv_wonder_sacrificed_artwork }}",
            f"{prefix}destroy_art = scope:tv_wonder_sacrificed_artwork",
        ]
    if cost_type == "scaled_gold":
        return [f"{prefix}change_gold_effect = {{ scale = -5 }}"]
    if cost_type == "prestige":
        return [f"{prefix}add_prestige = -50"]
    raise ValueError(f"Unsupported ritual cost type for tooltip effect: {cost_type}")


def ritual_requirement_tooltip_lines(wonder: dict, ritual_plan: dict, indent: int) -> list[str]:
    mode = ritual_plan["mode"]
    if mode == "timed":
        timed = ritual_plan.get("timed", {})
        if timed.get("burden_modifier", {}) or timed.get("blessing_modifier", {}):
            return [
                f"{T * indent}add_country_modifier = {{ modifier = {ritual_burden_modifier_name(wonder)} years = {timed.get('years', 1)} mode = add_and_extend }}"
            ]
        return []
    if mode == "auxiliary_building":
        return [
            f"{T * indent}var:tv_wonder_site ?= {{",
            f"{T * (indent + 1)}construct_building = {{ building_type = building_type:{ritual_auxiliary_building(wonder)} }}",
            f"{T * indent}}}",
        ]
    if mode == "immediate":
        return immediate_ritual_cost_lines(ritual_plan, indent)
    raise ValueError(f"Unsupported ritual mode for requirement tooltip effect: {mode}")


def ritual_effect_tooltip_lines(wonder: dict, mechanics: dict, style: int, ritual_plan: dict, indent: int) -> list[str]:
    if wonder.get("is_unique"):
        ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
        if ceremony_modifier is None:
            return []
        modifier_name, _ = ceremony_modifier
        return [f"{T * indent}add_country_modifier = {{ modifier = {modifier_name} years = -1 mode = add_and_extend }}"]

    mode = ritual_plan["mode"]
    if mode == "timed":
        return completion_ritual_payload_lines(wonder, ritual_plan, indent)
    if mode == "auxiliary_building":
        return [
            f"{T * indent}var:tv_wonder_site ?= {{",
            f"{T * (indent + 1)}add_location_modifier = {{ modifier = {ritual_auxiliary_display_modifier_name(wonder)} years = -1 mode = add_and_extend }}",
            f"{T * indent}}}",
        ]
    if mode == "immediate":
        lines = reward_effect_lines(ritual_plan.get("reward", []), indent)
        lines.extend(indent_script_block(ritual_plan.get("completion_effect_script", ""), indent))
        return lines
    raise ValueError(f"Unsupported ritual mode for effect tooltip effect: {mode}")


def ritual_location_tooltip_lines(wonder: dict, mechanics: dict, style: int, ritual_plan: dict, indent: int) -> list[str]:
    if wonder.get("is_unique"):
        ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
        if ceremony_modifier is None:
            return []
        modifier_name, _ = ceremony_modifier
        return location_tooltip_country_modifier_lines(modifier_name, indent)

    mode = ritual_plan["mode"]
    if mode == "timed":
        lines: list[str] = []
        blessing_modifier = ritual_plan.get("timed", {}).get("blessing_modifier", {})
        if blessing_modifier:
            lines.extend(location_tooltip_country_modifier_lines(ritual_blessing_modifier_name(wonder), indent))
        lines.extend(location_tooltip_reward_effect_lines(ritual_plan.get("reward", []), indent))
        return lines
    if mode == "auxiliary_building":
        return [
            f"{T * indent}add_location_modifier = {{ modifier = {ritual_auxiliary_display_modifier_name(wonder)} years = -1 mode = add_and_extend }}"
        ]
    if mode == "immediate":
        return location_tooltip_reward_effect_lines(ritual_plan.get("reward", []), indent)
    raise ValueError(f"Unsupported ritual mode for location tooltip effect: {mode}")


def append_ritual_tooltip_effects(lines: list[str], ritual_entry_list: list[tuple[dict, int, dict]], mechanics: dict) -> None:
    for wonder, style, ritual_plan in ritual_entry_list:
        if not wonder.get("is_unique"):
            lines.append(f"{ritual_requirement_tooltip_effect_name(wonder, style)} = {{")
            requirement_lines = ritual_requirement_tooltip_lines(wonder, ritual_plan, 1)
            lines.extend(requirement_lines or [f"{T}custom_tooltip = {{ text = NOTHING_HAPPENS_EFFECT }}"])
            lines.append("}")
            lines.append("")

        lines.append(f"{ritual_effect_tooltip_effect_name(wonder, style)} = {{")
        effect_lines = ritual_effect_tooltip_lines(wonder, mechanics, style, ritual_plan, 1)
        lines.extend(effect_lines or [f"{T}custom_tooltip = {{ text = NOTHING_HAPPENS_EFFECT }}"])
        lines.append("}")
        lines.append("")

        lines.append(f"{ritual_location_tooltip_effect_name(wonder, style)} = {{")
        location_effect_lines = ritual_location_tooltip_lines(wonder, mechanics, style, ritual_plan, 1)
        lines.extend(location_effect_lines or [f"{T}custom_tooltip = {{ text = NOTHING_HAPPENS_EFFECT }}"])
        lines.append("}")
        lines.append("")

        lines.append(f"{ritual_location_tooltip_effect_alias_name(wonder, style)} = {{")
        lines.append(f"{T}{ritual_location_tooltip_effect_name(wonder, style)} = yes")
        lines.append("}")
        lines.append("")


def loc_level(building: str, op: str, level: int) -> str:
    return f"location_building_level = {{ building_type = building_type:{building} value {op} {level} }}"


def location_display_level_var(wonder: dict) -> str:
    return f"tv_wonder_display_{wonder['key']}_level"


def location_display_ritual_style_var(wonder: dict) -> str:
    return f"tv_wonder_display_{wonder['key']}_ritual_style"


def slot_id_var(slot: int) -> str:
    return f"tv_wonder_display_slot_{slot}_id"


def slot_level_var(slot: int) -> str:
    return f"tv_wonder_display_slot_{slot}_level"


def slot_ritual_style_var(slot: int) -> str:
    return f"tv_wonder_display_slot_{slot}_ritual_style"


def tooltip_slot_id_var(slot: int) -> str:
    return f"tv_wonder_tooltip_slot_{slot}_id"


def tooltip_slot_level_var(slot: int) -> str:
    return f"tv_wonder_tooltip_slot_{slot}_level"


def tooltip_slot_ritual_style_var(slot: int) -> str:
    return f"tv_wonder_tooltip_slot_{slot}_ritual_style"


def append_location_display_level_detection(lines: list[str], wonder: dict, *, indent: int, var_name: str) -> None:
    prefix = T * indent
    for level in range(6, 0, -1):
        head = "if" if level == 6 else "else_if"
        lines.append(f"{prefix}{head} = {{")
        lines.append(f"{prefix}{T}limit = {{")
        lines.append(f"{prefix}{T}{T}OR = {{")
        for building in wonder["final_buildings"].values():
            lines.append(f"{prefix}{T}{T}{T}{loc_level(building, '>=', level)}")
        lines.append(f"{prefix}{T}{T}}}")
        lines.append(f"{prefix}{T}}}")
        lines.append(f"{prefix}{T}set_variable = {{ name = {var_name} value = {level} }}")
        lines.append(f"{prefix}}}")


def append_location_display_ritual_style_detection(lines: list[str], wonder: dict, *, indent: int, var_name: str) -> None:
    prefix = T * indent
    for style in ceremony_styles(wonder):
        building = final_building_for_style(wonder, style)
        head = "if" if style == ceremony_styles(wonder)[0] else "else_if"
        lines.append(f"{prefix}{head} = {{")
        lines.append(f"{prefix}{T}limit = {{ has_building = building_type:{building} }}")
        lines.append(f"{prefix}{T}set_variable = {{ name = {var_name} value = {style} }}")
        lines.append(f"{prefix}}}")


def append_location_display_push_effects(lines: list[str]) -> None:
    lines.append("tv_wonder_mechanics_push_location_display_slot_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ NOT = {{ has_variable = tv_wonder_display_count }} }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_display_count value = 0 }}")
    lines.append(f"{T}}}")
    for slot in range(1, DISPLAY_SLOT_MAX + 1):
        head = "if" if slot == 1 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_display_count < {slot} }}")
        lines.append(f"{T}{T}set_variable = {{ name = {slot_id_var(slot)} value = $wonder_id$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {slot_level_var(slot)} value = $wonder_level$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {slot_ritual_style_var(slot)} value = $wonder_ritual_style$ }}")
        lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_display_count add = 1 }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_push_location_tooltip_slot_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ NOT = {{ has_variable = tv_wonder_tooltip_fill_count }} }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_tooltip_fill_count value = 0 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ NOT = {{ has_variable = tv_wonder_tooltip_overflow_count }} }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_tooltip_overflow_count value = 0 }}")
    lines.append(f"{T}}}")
    for slot in range(1, TOOLTIP_SLOT_MAX + 1):
        head = "if" if slot == 1 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_tooltip_fill_count < {slot} }}")
        lines.append(f"{T}{T}set_variable = {{ name = {tooltip_slot_id_var(slot)} value = $wonder_id$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {tooltip_slot_level_var(slot)} value = $wonder_level$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {tooltip_slot_ritual_style_var(slot)} value = $wonder_ritual_style$ }}")
        lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_tooltip_fill_count add = 1 }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_tooltip_overflow_count add = 1 }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_location_display_clear_effect(lines: list[str], all_wonders: list[dict]) -> None:
    lines.append("tv_wonder_mechanics_clear_location_display_state_effect = {")
    lines.append(f"{T}remove_variable = tv_wonder_display_id")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_display_count value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_display_any_wonder value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_tooltip_fill_count value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_tooltip_overflow_count value = 0 }}")
    for slot in range(1, DISPLAY_SLOT_MAX + 1):
        lines.append(f"{T}remove_variable = {slot_id_var(slot)}")
        lines.append(f"{T}remove_variable = {slot_level_var(slot)}")
        lines.append(f"{T}remove_variable = {slot_ritual_style_var(slot)}")
    for slot in range(1, TOOLTIP_SLOT_MAX + 1):
        lines.append(f"{T}remove_variable = {tooltip_slot_id_var(slot)}")
        lines.append(f"{T}remove_variable = {tooltip_slot_level_var(slot)}")
        lines.append(f"{T}remove_variable = {tooltip_slot_ritual_style_var(slot)}")
    for wonder in all_wonders:
        lines.append(f"{T}remove_variable = {location_display_level_var(wonder)}")
        lines.append(f"{T}remove_variable = {location_display_ritual_style_var(wonder)}")
    lines.append("}")
    lines.append("")


def append_location_display_wonder_projection(lines: list[str], wonder: dict, *, compact: bool) -> None:
    level_var = location_display_level_var(wonder)
    ritual_style_var = location_display_ritual_style_var(wonder)
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}OR = {{")
    if wonder.get("is_unique"):
        lines.append(f"{T}{T}{T}{T}this = location:{wonder['location']}")
    for building in wonder["final_buildings"].values():
        lines.append(f"{T}{T}{T}{T}has_building = building_type:{building}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = {level_var} value = 0 }}")
    lines.append(f"{T}{T}set_variable = {{ name = {ritual_style_var} value = 0 }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_display_any_wonder value = 1 }}")
    append_location_display_level_detection(lines, wonder, indent=2, var_name=level_var)
    append_location_display_ritual_style_detection(lines, wonder, indent=2, var_name=ritual_style_var)
    if compact:
        lines.append(
            f"{T}{T}tv_wonder_mechanics_push_location_display_slot_effect = {{ "
            f"wonder_id = {wonder['id']} wonder_level = var:{level_var} wonder_ritual_style = var:{ritual_style_var} }}"
        )
    lines.append(
        f"{T}{T}tv_wonder_mechanics_push_location_tooltip_slot_effect = {{ "
        f"wonder_id = {wonder['id']} wonder_level = var:{level_var} wonder_ritual_style = var:{ritual_style_var} }}"
    )
    lines.append(f"{T}}}")


def append_location_display_effects(
    lines: list[str],
    *,
    unique_wonders: list[dict],
    generic_wonders: list[dict],
) -> None:
    all_wonders = [*unique_wonders, *generic_wonders]

    append_location_display_push_effects(lines)
    append_location_display_clear_effect(lines, all_wonders)

    lines.append("tv_wonder_mechanics_refresh_location_display_state_effect = {")
    lines.append(f"{T}tv_wonder_mechanics_clear_location_display_state_effect = yes")
    for wonder in unique_wonders:
        append_location_display_wonder_projection(lines, wonder, compact=True)
    for wonder in generic_wonders:
        append_location_display_wonder_projection(lines, wonder, compact=True)
    lines.append(f"{T}remove_variable = tv_wonder_tooltip_fill_count")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_refresh_world_location_display_state_effect = {")
    lines.append(f"{T}every_location_in_the_world = {{")
    lines.append(f"{T}{T}tv_wonder_mechanics_refresh_location_display_state_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_suitability_reveal_effect(lines: list[str], wonders: list[dict], mechanics: dict) -> None:
    lines.append("tv_wonder_mechanics_reveal_suitability_knowledge_effect = {")
    for idx, wonder in enumerate(wonders):
        head = "if" if idx == 0 else "else_if"
        reveal_var = suitability_reveal_variable_for_wonder(wonder)
        row_count = len(suitability_knowledge_for_wonder(mechanics, wonder))
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ NOT = {{ has_variable = {reveal_var} }} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {reveal_var} value = 0 }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{reveal_var} < {row_count} }}")
        lines.append(f"{T}{T}{T}change_variable = {{ name = {reveal_var} add = 1 }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}clamp_variable = {{ name = {reveal_var} min = 0 max = {row_count} }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_suitability_condition_limit(lines: list[str], condition: str, indent: int) -> None:
    if condition not in SUITABILITY_CONDITION_SCRIPTS:
        raise ValueError(f"Missing suitability actual condition script for {condition}")
    prefix = T * indent
    lines.append(f"{prefix}var:tv_wonder_survey_site ?= {{")
    lines.extend(indent_script_block(SUITABILITY_CONDITION_SCRIPTS[condition], indent + 1))
    lines.append(f"{prefix}}}")


def append_suitability_actual_row(lines: list[str], wonder: dict, row: dict[str, str], row_index: int, indent: int) -> None:
    prefix = T * indent
    variable = suitability_actual_variable_for_wonder(wonder, row_index)
    lines.append(f"{prefix}set_variable = {{ name = {variable} value = 0 }}")
    if row["type"] == "condition_bonus":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{")
        append_suitability_condition_limit(lines, row["condition"], indent + 2)
        lines.append(f"{prefix}{T}}}")
        lines.append(f"{prefix}{T}set_variable = {{ name = {variable} value = {fmt_value(row['value'])} }}")
        lines.append(f"{prefix}}}")
        return

    source = row["source"]
    if source not in SUITABILITY_SOURCE_EXPRESSIONS:
        raise ValueError(f"Missing suitability actual source expression for {source}")
    source_expression = SUITABILITY_SOURCE_EXPRESSIONS[source]
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{ tv_wonder_survey_site_selected_trigger = yes }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = {variable} value = var:tv_wonder_survey_site.{source_expression} }}")
    lines.append(f"{prefix}{T}clamp_variable = {{ name = {variable} min = {fmt_value(row['min'])} max = {fmt_value(row['max'])} }}")
    lines.append(f"{prefix}{T}change_variable = {{ name = {variable} multiply = {fmt_value(row['multiplier'])} }}")
    lines.append(f"{prefix}}}")


def append_suitability_actual_effects(lines: list[str], wonders: list[dict], mechanics: dict) -> None:
    lines.append("tv_wonder_mechanics_clear_suitability_actuals_effect = {")
    for wonder in wonders:
        rows = suitability_knowledge_for_wonder(mechanics, wonder)
        for row_index, _row in enumerate(rows, start=1):
            lines.append(f"{T}remove_variable = {suitability_actual_variable_for_wonder(wonder, row_index)}")
    lines.append("}")
    lines.append("")

    for wonder in wonders:
        rows = suitability_knowledge_for_wonder(mechanics, wonder)
        lines.append(f"tv_wonder_calculate_{wonder['key']}_suitability_actuals_effect = {{")
        for row_index, row in enumerate(rows, start=1):
            append_suitability_actual_row(lines, wonder, row, row_index, 1)
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_mechanics_calculate_suitability_actuals_effect = {")
    for idx, wonder in enumerate(wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}tv_wonder_calculate_{wonder['key']}_suitability_actuals_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_base_modifier_effect(lines: list[str], name: str, wonders: list[dict]) -> None:
    lines.append(f"{name} = {{")
    for idx, wonder in enumerate(wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        for level in range(1, 7):
            level_head = "if" if level == 1 else "else_if"
            lines.append(
                f"{T}{T}{level_head} = {{ limit = {{ var:tv_wonder_level ?= {level} }} "
                f"add_country_modifier = {{ modifier = tv_wonder_{wonder['key']}_level_{level} years = -1 mode = add_and_extend }} }}"
            )
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_ceremony_modifier_effect(lines: list[str], name: str, wonders: list[dict], mechanics: dict) -> None:
    lines.append(f"{name} = {{")
    first = True
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
            if ceremony_modifier is None:
                continue
            modifier_name, _ = ceremony_modifier
            head = "if" if first else "else_if"
            first = False
            lines.append(f"{T}{head} = {{")
            lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
            lines.append(f"{T}{T}add_country_modifier = {{ modifier = {modifier_name} years = -1 mode = add_and_extend }}")
            lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_construct_final_building_effect(lines: list[str], name: str, wonders: list[dict]) -> None:
    min_id = min(wonder["id"] for wonder in wonders)
    max_id = max(wonder["id"] for wonder in wonders)
    max_style = max(max(ceremony_styles(wonder)) for wonder in wonders)
    lines.append(f"{name} = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}tv_wonder_construction_site_selected_trigger = yes")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this >= {min_id} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this <= {max_id} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_ceremony_style ?= {{ this >= 1 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_ceremony_style ?= {{ this <= {max_style} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this >= 1 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this <= 6 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}var:tv_wonder_site ?= {{")
    first = True
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            building = final_building_for_style(wonder, style)
            head = "if" if first else "else_if"
            first = False
            lines.append(f"{T}{T}{T}{head} = {{")
            lines.append(f"{T}{T}{T}{T}limit = {{ prev = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }} }}")
            lines.append(f"{T}{T}{T}{T}prev = {{ set_variable = {{ name = tv_wonder_final_building value = {wonder['id']}{style:02d} }} }}")
            lines.append(f"{T}{T}{T}{T}tv_wonder_construct_final_building_in_site_effect = {{ building = building_type:{building} }}")
            lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_completion_broadcast_scope_effect(lines: list[str], name: str, wonders: list[dict]) -> None:
    lines.append(f"{name} = {{")
    for idx, wonder in enumerate(wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}save_scope_as = tv_wonder_completed_{wonder['key']}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_roll_random_feasible_proposal_effect(lines: list[str], name: str, deck_map: str) -> None:
    lines.append(f"{name} = {{")
    lines.append(f"{T}remove_variable = tv_wonder_proposal")
    lines.append(f"{T}save_scope_as = tv_wonder_proposal_owner")
    lines.append(f"{T}random_key_in_variable_map = {{")
    lines.append(f"{T}{T}variable = {deck_map}")
    lines.append(f"{T}{T}scope:tv_wonder_proposal_owner = {{")
    lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_proposal value = prev }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    all_wonders, mechanics = load_all_wonder_mechanics()
    generic_wonders = [wonder for wonder in all_wonders if not wonder.get("is_unique")]
    unique_wonders = [wonder for wonder in all_wonders if wonder.get("is_unique")]
    lines = render_header(SCRIPT_REL)

    lines.append("tv_wonder_mechanics_clear_feasible_deck_effect = {")
    lines.append(f"{T}clear_variable_map = {FEASIBLE_GENERIC_DECK_MAP}")
    lines.append(f"{T}clear_variable_map = {FEASIBLE_UNIQUE_DECK_MAP}")
    lines.append(f"{T}# Legacy cleanup for pre-id-deck saves.")
    for wonder in all_wonders:
        lines.append(f"{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_rebuild_feasible_deck_effect = {")
    for wonder in all_wonders:
        deck_map = FEASIBLE_UNIQUE_DECK_MAP if wonder.get("is_unique") else FEASIBLE_GENERIC_DECK_MAP
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ tv_wonder_can_build_{wonder['key']}_trigger = yes }}")
        lines.append(f"{T}{T}add_to_variable_map = {{ name = {deck_map} key = {wonder['id']} value = 1 }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    append_roll_random_feasible_proposal_effect(
        lines,
        "tv_wonder_generic_roll_random_feasible_proposal_effect",
        FEASIBLE_GENERIC_DECK_MAP,
    )
    append_roll_random_feasible_proposal_effect(
        lines,
        "tv_wonder_unique_roll_random_feasible_proposal_effect",
        FEASIBLE_UNIQUE_DECK_MAP,
    )

    lines.append("tv_wonder_roll_next_slot_from_priority_deck_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_unique_has_any_feasible_proposal_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_unique_roll_random_feasible_proposal_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_generic_has_any_feasible_proposal_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_generic_roll_random_feasible_proposal_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_remove_current_proposal_from_deck_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_proposal ?= {{ this >= {ALL_WONDER_MIN_ID} }} }}")
    lines.append(f"{T}{T}set_local_variable = {{ name = tv_wonder_current_proposal_id value = var:tv_wonder_proposal }}")
    lines.append(f"{T}{T}remove_from_variable_map = {{ name = {FEASIBLE_GENERIC_DECK_MAP} key = local_var:tv_wonder_current_proposal_id }}")
    lines.append(f"{T}{T}remove_from_variable_map = {{ name = {FEASIBLE_UNIQUE_DECK_MAP} key = local_var:tv_wonder_current_proposal_id }}")
    lines.append(f"{T}{T}remove_local_variable = tv_wonder_current_proposal_id")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_accept_proposal_tooltip_effect = {")
    lines.append(f"{T}custom_tooltip = {{ text = tv_wonder_accept_proposal_desc }}")
    lines.append("}")
    lines.append("")

    append_suitability_actual_effects(lines, all_wonders, mechanics)

    for wonder in all_wonders:
        key = wonder["key"]
        rows = suitability_knowledge_for_wonder(mechanics, wonder)
        lines.append(f"tv_wonder_copy_{key}_survey_from_location_effect = {{")
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ exists = scope:tv_wonder_selected_survey_site }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_scale_competence value = scope:tv_wonder_selected_survey_site.var:tv_wonder_{key}_scale_competence }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_logistics_competence value = scope:tv_wonder_selected_survey_site.var:tv_wonder_{key}_logistics_competence }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_organization_competence value = scope:tv_wonder_selected_survey_site.var:tv_wonder_{key}_organization_competence }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_complete value = 1 }}")
        lines.append(f"{T}{T}remove_variable = tv_wonder_survey_active")
        lines.append(f"{T}{T}tv_wonder_set_io_survey_progress_effect = {{ value = 100 }}")
        lines.append(f"{T}{T}tv_wonder_update_construction_tiers_from_competence_effect = yes")
        lines.append(f"{T}{T}tv_wonder_calculate_{key}_suitability_actuals_effect = yes")
        for row_index, _row in enumerate(rows, start=1):
            actual_var = suitability_actual_variable_for_wonder(wonder, row_index)
            lines.append(f"{T}{T}if = {{")
            lines.append(f"{T}{T}{T}limit = {{ scope:tv_wonder_selected_survey_site = {{ has_variable = {actual_var} }} }}")
            lines.append(f"{T}{T}{T}set_variable = {{ name = {actual_var} value = scope:tv_wonder_selected_survey_site.var:{actual_var} }}")
            lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_mechanics_copy_completed_survey_from_location_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        key = wonder["key"]
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}exists = scope:tv_wonder_selected_survey_site")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{key} }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}tv_wonder_copy_{key}_survey_from_location_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_clear_completed_survey_from_location_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        key = wonder["key"]
        rows = suitability_knowledge_for_wonder(mechanics, wonder)
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}exists = scope:tv_wonder_selected_survey_site")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}scope:tv_wonder_selected_survey_site = {{")
        lines.append(f"{T}{T}{T}remove_variable = tv_wonder_surveyed_{key}")
        lines.append(f"{T}{T}{T}remove_variable = tv_wonder_{key}_scale_competence")
        lines.append(f"{T}{T}{T}remove_variable = tv_wonder_{key}_logistics_competence")
        lines.append(f"{T}{T}{T}remove_variable = tv_wonder_{key}_organization_competence")
        lines.append(f"{T}{T}{T}remove_variable = tv_wonder_{key}_scale_tier")
        for row_index, _row in enumerate(rows, start=1):
            actual_var = suitability_actual_variable_for_wonder(wonder, row_index)
            lines.append(f"{T}{T}{T}remove_variable = {actual_var}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_store_survey_on_location_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        key = wonder["key"]
        rows = suitability_knowledge_for_wonder(mechanics, wonder)
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_survey_site_selected_trigger = yes")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}tv_wonder_calculate_{key}_suitability_actuals_effect = yes")
        lines.append(f"{T}{T}var:tv_wonder_survey_site ?= {{")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_surveyed_{key} value = 1 }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_scale_competence value = prev.var:tv_wonder_scale_competence }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_logistics_competence value = prev.var:tv_wonder_logistics_competence }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_organization_competence value = prev.var:tv_wonder_organization_competence }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_scale_tier value = prev.var:tv_wonder_scale_tier }}")
        for row_index, _row in enumerate(rows, start=1):
            actual_var = suitability_actual_variable_for_wonder(wonder, row_index)
            lines.append(f"{T}{T}{T}set_variable = {{ name = {actual_var} value = prev.var:{actual_var} }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_survey_site_preference_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}tv_wonder_survey_site_selected_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.extend(add_site_preference(wonder, mechanics, 2))
        lines.append(f"{T}{T}tv_wonder_calculate_{wonder['key']}_suitability_actuals_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_selected_survey_already_cached_effect = {")
    first = True
    for wonder in all_wonders:
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{wonder['key']} }} }}")
        lines.append(f"{T}{T}tv_wonder_copy_completed_survey_from_location_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_start_survey_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}exists = scope:target")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_clear_current_survey_effect = yes")
    lines.append(f"{T}{T}tv_wonder_mechanics_clear_suitability_actuals_effect = yes")
    lines.append(f"{T}{T}scope:target = {{ save_scope_as = tv_wonder_selected_survey_site }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_site value = scope:target }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_stage value = 2 }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_selected_survey_already_cached_trigger = yes }}")
    lines.append(f"{T}{T}{T}tv_wonder_copy_completed_survey_from_location_effect = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else = {{")
    lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_survey_active value = 1 }}")
    lines.append(f"{T}{T}{T}tv_wonder_prepare_survey_competence_targets_effect = yes")
    lines.append(f"{T}{T}{T}tv_wonder_set_io_survey_progress_effect = {{ value = 0 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_complete_survey_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_survey_active_trigger = yes }}")
    lines.append(f"{T}{T}clamp_variable = {{ name = tv_wonder_scale_competence min = 0 max = 100 }}")
    lines.append(f"{T}{T}clamp_variable = {{ name = tv_wonder_logistics_competence min = 0 max = 100 }}")
    lines.append(f"{T}{T}clamp_variable = {{ name = tv_wonder_organization_competence min = 0 max = 100 }}")
    lines.append(f"{T}{T}tv_wonder_update_construction_tiers_from_competence_effect = yes")
    lines.append(f"{T}{T}tv_wonder_store_survey_on_location_effect = yes")
    lines.append(f"{T}{T}tv_wonder_mechanics_reveal_suitability_knowledge_effect = yes")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_complete value = 1 }}")
    lines.append(f"{T}{T}remove_variable = tv_wonder_survey_active")
    lines.append(f"{T}{T}remove_variable = tv_wonder_survey_speed")
    lines.append(f"{T}{T}remove_variable = tv_wonder_scale_competence_target")
    lines.append(f"{T}{T}remove_variable = tv_wonder_logistics_competence_target")
    lines.append(f"{T}{T}remove_variable = tv_wonder_organization_competence_target")
    lines.append(f"{T}{T}remove_variable = tv_wonder_scale_competence_monthly_gain")
    lines.append(f"{T}{T}remove_variable = tv_wonder_logistics_competence_monthly_gain")
    lines.append(f"{T}{T}remove_variable = tv_wonder_organization_competence_monthly_gain")
    lines.append(f"{T}{T}tv_wonder_set_io_survey_progress_effect = {{ value = 100 }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_survey_site_selected_trigger = yes }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_survey_site ?= {{ save_scope_as = tv_wonder_event_location }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_competence_average value = var:tv_wonder_scale_competence }}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_survey_competence_average add = var:tv_wonder_logistics_competence }}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_survey_competence_average add = var:tv_wonder_organization_competence }}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_survey_competence_average divide = 3 }}")
    lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.300 }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    append_base_modifier_effect(lines, "tv_wonder_mechanics_apply_generic_base_modifier_effect", generic_wonders)
    append_base_modifier_effect(lines, "tv_wonder_mechanics_apply_unique_base_modifier_effect", unique_wonders)
    lines.append("tv_wonder_mechanics_apply_base_modifier_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_unique_locked_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_mechanics_apply_unique_base_modifier_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_mechanics_apply_generic_base_modifier_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    append_ceremony_modifier_effect(lines, "tv_wonder_mechanics_apply_unique_ceremony_modifier_effect", unique_wonders, mechanics)
    lines.append("tv_wonder_mechanics_apply_ceremony_modifier_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_unique_locked_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_mechanics_apply_unique_ceremony_modifier_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    append_ritual_tooltip_effects(lines, ritual_entries(all_wonders, mechanics), mechanics)

    append_location_display_effects(lines, unique_wonders=unique_wonders, generic_wonders=generic_wonders)
    append_suitability_reveal_effect(lines, all_wonders, mechanics)

    append_construct_final_building_effect(lines, "tv_wonder_mechanics_construct_generic_final_building_effect", generic_wonders)
    append_construct_final_building_effect(lines, "tv_wonder_mechanics_construct_unique_final_building_effect", unique_wonders)
    lines.append("tv_wonder_mechanics_construct_final_building_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_unique_locked_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_mechanics_construct_unique_final_building_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_mechanics_construct_generic_final_building_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    ritual_entry_list = ritual_entries(all_wonders, mechanics)

    lines.append("tv_wonder_mechanics_recalculate_total_owned_buildings_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_ritual_current_total_buildings value = 0 }}")
    lines.append(f"{T}every_owned_location = {{")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_ritual_current_total_buildings add = this.num_buildings }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_snapshot_total_owned_buildings_effect = {")
    lines.append(f"{T}tv_wonder_mechanics_recalculate_total_owned_buildings_effect = yes")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_ritual_total_buildings_baseline value = var:tv_wonder_ritual_current_total_buildings }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_clear_selected_ritual_runtime_effect = {")
    for variable in RITUAL_SHARED_RUNTIME_VARS:
        lines.append(f"{T}remove_variable = {variable}")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        custom_variables = [variable for variable in ritual_plan.get("runtime_variables", []) if variable not in RITUAL_SHARED_RUNTIME_VARS]
        if not custom_variables:
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        for variable in custom_variables:
            lines.append(f"{T}{T}remove_variable = {variable}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_selected_ritual_snapshot_effect = {")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        if not ritual_plan.get("snapshot_effect_script"):
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        lines.extend(snapshot_ritual_payload_lines(ritual_plan, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_selected_ritual_progress_effect = {")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        if not ritual_plan.get("progress_effect_script"):
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        lines.extend(progress_ritual_payload_lines(ritual_plan, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_start_timed_ritual_effect = {")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        if ritual_plan["mode"] != "timed":
            continue
        head = "if" if first else "else_if"
        first = False
        timed = ritual_plan.get("timed", {})
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        lines.append(f"{T}{T}tv_wonder_mechanics_clear_selected_ritual_runtime_effect = yes")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_in_progress value = 1 }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_locked value = 1 }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_timer value = 1 years = {timed.get('years', 1)} }}")
        if timed.get("burden_modifier", {}) or timed.get("blessing_modifier", {}):
            lines.append(f"{T}{T}add_country_modifier = {{ modifier = {ritual_burden_modifier_name(wonder)} years = {timed.get('years', 1)} mode = add_and_extend }}")
        lines.extend(indent_script_block(ritual_plan.get("start_effect_script", ""), 2))
        lines.append(f"{T}{T}tv_wonder_mechanics_apply_selected_ritual_snapshot_effect = yes")
        lines.append(f"{T}{T}tv_wonder_complete_active_ritual_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_start_auxiliary_building_ritual_effect = {")
    lines.append(f"{T}tv_wonder_mechanics_clear_selected_ritual_runtime_effect = yes")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_ritual_in_progress value = 1 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_ceremony_locked value = 1 }}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_construction_site_selected_trigger = yes }}")
    lines.append(f"{T}{T}var:tv_wonder_site ?= {{")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        if ritual_plan["mode"] != "auxiliary_building":
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{T}{T}{head} = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ prev = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }} }}")
        lines.append(f"{T}{T}{T}{T}construct_building = {{ building_type = building_type:{ritual_auxiliary_building(wonder)} }}")
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    for wonder, style, ritual_plan in ritual_entry_list:
        if ritual_plan["mode"] != "auxiliary_building":
            continue
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        lines.extend(indent_script_block(ritual_plan.get("start_effect_script", ""), 3))
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append(f"{T}tv_wonder_mechanics_apply_selected_ritual_snapshot_effect = yes")
    lines.append(f"{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_mark_completed_auxiliary_building_ritual_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_ritual_in_progress")
    lines.append(f"{T}{T}{T}tv_wonder_selected_generic_auxiliary_building_ritual_trigger = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_auxiliary_building_finished value = 1 }}")
    lines.append(f"{T}{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_start_deferred_immediate_ritual_effect = {")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        if ritual_plan["mode"] != "immediate" or not ritual_uses_deferred_completion(ritual_plan):
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        lines.append(f"{T}{T}tv_wonder_mechanics_clear_selected_ritual_runtime_effect = yes")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_in_progress value = 1 }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_locked value = 1 }}")
        lines.extend(indent_script_block(ritual_plan.get("start_effect_script", ""), 2))
        lines.append(f"{T}{T}tv_wonder_mechanics_apply_selected_ritual_snapshot_effect = yes")
        lines.append(f"{T}{T}tv_wonder_complete_active_ritual_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_immediate_ritual_effect = {")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        if ritual_plan["mode"] != "immediate" or ritual_uses_deferred_completion(ritual_plan):
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        lines.extend(immediate_ritual_payload_lines(ritual_plan, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_selected_ritual_completion_effect = {")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        if not ritual_uses_deferred_completion(ritual_plan):
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
        lines.extend(completion_ritual_payload_lines(wonder, ritual_plan, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_maybe_complete_active_ritual_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_ritual_in_progress")
    lines.append(f"{T}{T}{T}tv_wonder_selected_ritual_completion_requirements_met_trigger = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_mechanics_apply_selected_ritual_completion_effect = yes")
    lines.append(f"{T}{T}remove_variable = tv_wonder_ritual_in_progress")
    lines.append(f"{T}{T}remove_variable = tv_wonder_ritual_timer")
    lines.append(f"{T}{T}tv_wonder_mechanics_clear_selected_ritual_runtime_effect = yes")
    lines.append(f"{T}{T}tv_wonder_finalize_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_complete_active_ritual_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_ritual_in_progress }}")
    lines.append(f"{T}{T}tv_wonder_mechanics_apply_selected_ritual_progress_effect = yes")
    lines.append(f"{T}{T}tv_wonder_mechanics_maybe_complete_active_ritual_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    append_completion_broadcast_scope_effect(lines, "tv_wonder_mechanics_broadcast_generic_completion_event_effect", generic_wonders)
    append_completion_broadcast_scope_effect(lines, "tv_wonder_mechanics_broadcast_unique_completion_event_effect", unique_wonders)
    lines.append("tv_wonder_mechanics_broadcast_completion_event_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_unique_locked_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_mechanics_broadcast_unique_completion_event_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_mechanics_broadcast_generic_completion_event_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_confirm_ceremony_effect = {")
    lines.append(f"{T}tv_wonder_index_refresh_country_cache_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_ceremony_ready_for_confirmation_trigger = yes }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_selected_generic_timed_ritual_trigger = yes }}")
    lines.append(f"{T}{T}{T}tv_wonder_mechanics_start_timed_ritual_effect = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_selected_generic_auxiliary_building_ritual_trigger = yes }}")
    lines.append(f"{T}{T}{T}tv_wonder_mechanics_start_auxiliary_building_ritual_effect = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_selected_generic_artwork_decoration_ritual_trigger = yes }}")
    lines.append(f"{T}{T}{T}random_work_of_art_in_country = {{ save_scope_as = tv_wonder_sacrificed_artwork }}")
    lines.append(f"{T}{T}{T}destroy_art = scope:tv_wonder_sacrificed_artwork")
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ tv_wonder_selected_deferred_immediate_ritual_trigger = yes }}")
    lines.append(f"{T}{T}{T}{T}tv_wonder_mechanics_start_deferred_immediate_ritual_effect = yes")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}else = {{")
    lines.append(f"{T}{T}{T}{T}tv_wonder_mechanics_apply_immediate_ritual_effect = yes")
    lines.append(f"{T}{T}{T}{T}tv_wonder_finalize_effect = yes")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_selected_deferred_immediate_ritual_trigger = yes }}")
    lines.append(f"{T}{T}{T}tv_wonder_mechanics_start_deferred_immediate_ritual_effect = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}OR = {{")
    lines.append(f"{T}{T}{T}{T}{T}tv_wonder_selected_generic_immediate_ritual_trigger = yes")
    lines.append(f"{T}{T}{T}{T}{T}tv_wonder_selected_generic_scaled_gold_decoration_ritual_trigger = yes")
    lines.append(f"{T}{T}{T}{T}{T}tv_wonder_selected_generic_prestige_decoration_ritual_trigger = yes")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}tv_wonder_mechanics_apply_immediate_ritual_effect = yes")
    lines.append(f"{T}{T}{T}tv_wonder_finalize_effect = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_clear_project_state_effect = {")
    runtime_cleanup_vars: list[str] = list(RITUAL_SHARED_RUNTIME_VARS)
    for _wonder, _style, ritual_plan in ritual_entry_list:
        for variable in ritual_plan.get("runtime_variables", []):
            if variable not in runtime_cleanup_vars:
                runtime_cleanup_vars.append(variable)
    for wonder in all_wonders:
        lines.append(f"{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
    for variable in runtime_cleanup_vars:
        lines.append(f"{T}remove_variable = {variable}")
    for wonder in all_wonders:
        if any(ritual_plan_for_style(wonder, mechanics, style)["mode"] == "timed" for style in ceremony_styles(wonder)):
            lines.append(f"{T}remove_country_modifier = {ritual_burden_modifier_name(wonder)}")
    lines.append("}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("\ufeff" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
