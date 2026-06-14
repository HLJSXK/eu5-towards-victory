import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ALL_WONDER_MIN_ID,
    FINAL_BUILDING_LEVEL_BY_TYPE_MAP,
    STYLE_3_REWARD_EFFECTS,
    UNIQUE_WONDER_MIN_ID,
    WONDER_MECHANICS_MAX_ID,
    ceremony_styles,
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
    SUITABILITY_ACTUAL_MAP,
    SUITABILITY_REVEAL_MAP,
    mechanic_key,
    suitability_current_actual_variable,
    suitability_current_revealed_variable,
    suitability_knowledge_for_wonder,
    wonder_static_display_modifier_name,
    wonder_static_local_display_modifier_name,
    wonder_ritual_composite_id,
    wonder_suitability_row_composite_id,
    unique_ceremony_modifier_name,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_engineering_department_wonder_mechanics_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py"
T = "\t"
DISPLAY_SLOT_MAX = 3
TOOLTIP_SLOT_MAX = 5
FEASIBLE_GENERIC_DECK_MAP = "tv_wonder_feasible_generic_deck"
FEASIBLE_UNIQUE_DECK_MAP = "tv_wonder_feasible_unique_deck"
LOCATION_SURVEYED_MAP = "tv_wonder_surveyed"
LOCATION_SURVEY_SCALE_MAP = "tv_wonder_survey_scale_competence"
LOCATION_SURVEY_LOGISTICS_MAP = "tv_wonder_survey_logistics_competence"
LOCATION_SURVEY_ORGANIZATION_MAP = "tv_wonder_survey_organization_competence"
LOCATION_SURVEY_SCALE_TIER_MAP = "tv_wonder_survey_scale_tier"
LOCATION_SURVEY_ACTUAL_MAP = "tv_wonder_survey_suitability_actual"
SUITABILITY_ROW_COUNT_MAP = "tv_wonder_mechanic_id_to_suitability_row_count"
SURVEY_WONDER_KEY_VAR = "tv_wonder_survey_wonder_key"
SURVEY_MECHANIC_KEY_VAR = "tv_wonder_survey_mechanic_key"
SURVEY_ROW_KEY_VAR = "tv_wonder_survey_row_key"
SURVEY_LOCATION_COPY_TEMP_VAR = "tv_wonder_survey_location_cache_temp"
SUITABILITY_ACTUAL_TEMP_VAR = "tv_wonder_suitability_row_temp"
SUITABILITY_MECHANIC_KEY_LOCAL = "tv_wonder_suitability_mechanic_key"
SUITABILITY_ROW_KEY_LOCAL = "tv_wonder_suitability_row_key"
SUITABILITY_ROW_COUNT_LOCAL = "tv_wonder_suitability_row_count"
SUITABILITY_REVEAL_VALUE_LOCAL = "tv_wonder_suitability_reveal_value"
FINAL_BUILDING_DISPLAY_ID_MAP = "tv_wonder_final_building_type_to_display_id"
FINAL_BUILDING_WONDER_ID_MAP = "tv_wonder_final_building_type_to_wonder_id"
FINAL_BUILDING_RITUAL_STYLE_MAP = "tv_wonder_final_building_type_to_ritual_style"
UNIQUE_WONDER_LOCATION_MAP = "tv_wonder_unique_id_to_location"
UNIQUE_WONDER_FINAL_BUILDING_TYPE_MAP = "tv_wonder_unique_id_to_final_building_type"
UNIQUE_RITUAL_COMPLETED_MAP = "tv_wonder_unique_ritual_completed"
EXISTING_UNIQUE_WONDERS_INITIALIZED_GLOBAL = "tv_wonder_existing_unique_wonders_initialized"
PRIORITY_CANDIDATE_WONDER_ID_VAR = "tv_wonder_priority_candidate_wonder_id"
PRIORITY_CANDIDATE_CURRENT_MODE_VAR = "tv_wonder_priority_candidate_current_mode"
LOCATION_DISPLAY_SCOPE = "tv_wonder_location_display_location"
LOCATION_DISPLAY_WONDER_ID_LOCAL = "tv_wonder_location_display_wonder_id"
LOCATION_DISPLAY_BUILDING_TYPE_LOCAL = "tv_wonder_location_display_building_type"
LOCATION_DISPLAY_ID_VAR = "tv_wonder_location_display_id"
LOCATION_DISPLAY_LEVEL_VAR = "tv_wonder_location_display_level"
LOCATION_DISPLAY_RITUAL_STYLE_VAR = "tv_wonder_location_display_ritual_style"
LOCATION_DISPLAY_RITUAL_COMPLETED_VAR = "tv_wonder_location_display_ritual_completed"
WONDER_MAP_UNIQUE_LEVEL_VAR = "tv_wonder_map_unique_level"
WONDER_MAP_GENERIC_LEVEL_VAR = "tv_wonder_map_generic_level"
WONDER_MAP_HAS_POTENTIAL_UNIQUE_VAR = "tv_wonder_map_has_potential_unique"
RITUAL_SHARED_RUNTIME_VARS = [
    "tv_wonder_ritual_auxiliary_building_finished",
    "tv_wonder_ritual_months_completed",
    "tv_wonder_ritual_progress_pct",
]
PHAROS_ROUTE_KEYS = [
    "constantinople",
    "venice",
    "genoa",
    "malta",
    "tunis",
    "palermo",
    "candia",
    "gibraltar",
]
PHAROS_ROUTE_IDS = {route_key: index for index, route_key in enumerate(PHAROS_ROUTE_KEYS, start=1)}
SUITABILITY_CONDITION_SCRIPTS = {
    "topography_mountains": "topography = mountains",
    "topography_plateau": "topography = plateau",
    "topography_hills": "topography = hills",
    "vegetation_forest": "vegetation = forest",
    "vegetation_woods": "vegetation = woods",
    "vegetation_forest_or_woods": "OR = {\n\tvegetation = forest\n\tvegetation = woods\n}",
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
    "free_building_levels": "modifier:free_building_levels",
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


def all_wonders_by_key(wonders: list[dict]) -> dict[str, dict]:
    return {str(wonder["key"]): wonder for wonder in wonders}


def mechanic_id_for_wonder(wonder: dict, by_key: dict[str, dict]) -> int:
    return int(by_key[mechanic_key(wonder)]["id"])


def suitability_row_key_for_wonder(wonder: dict, row_index: int, by_key: dict[str, dict]) -> int:
    return wonder_suitability_row_composite_id(mechanic_id_for_wonder(wonder, by_key), row_index)


def map_key_exists_condition(map_name: str, key: object, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}has_variable_map = {map_name}",
        f"{prefix}is_key_in_variable_map = {{ name = {map_name} target = {key} }}",
    ]


def map_replace_lines(map_name: str, key: object, value: str, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}remove_from_variable_map = {{ name = {map_name} key = {key} }}",
        f"{prefix}add_to_variable_map = {{ name = {map_name} key = {key} value = {value} }}",
    ]


def loc_level(building_ref: str, op: str, level: int) -> str:
    return f"location_building_level = {{ building_type = {building_ref} value {op} {level} }}"


def append_raise_building_to_initial_level(
    lines: list[str],
    building_ref: str,
    initial_level: int,
    indent: int,
) -> None:
    prefix = T * indent
    for level in range(2, initial_level + 1):
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ NOT = {{ {loc_level(building_ref, '>=', level)} }} }}")
        lines.append(
            f"{prefix}{T}change_building_level_in_location = {{ building = {building_ref} value = 1 owner = prev }}"
        )
        lines.append(f"{prefix}}}")


def append_seed_existing_unique_survey_maps(lines: list[str], wonder_id: int, indent: int) -> None:
    lines.extend(map_replace_lines(LOCATION_SURVEYED_MAP, wonder_id, "1", indent))
    lines.extend(map_replace_lines(LOCATION_SURVEY_SCALE_MAP, wonder_id, "100", indent))
    lines.extend(map_replace_lines(LOCATION_SURVEY_LOGISTICS_MAP, wonder_id, "100", indent))
    lines.extend(map_replace_lines(LOCATION_SURVEY_ORGANIZATION_MAP, wonder_id, "100", indent))
    lines.extend(map_replace_lines(LOCATION_SURVEY_SCALE_TIER_MAP, wonder_id, "6", indent))


def append_register_existing_unique_priority_candidate(
    lines: list[str],
    wonder_id: int,
    indent: int,
) -> None:
    prefix = T * indent
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{ has_owner = yes }}")
    lines.append(f"{prefix}{T}save_scope_as = tv_wonder_priority_site")
    lines.append(f"{prefix}{T}owner ?= {{")
    lines.append(f"{prefix}{T}{T}save_scope_as = tv_wonder_priority_owner")
    lines.append(
        f"{prefix}{T}{T}set_variable = {{ name = {PRIORITY_CANDIDATE_WONDER_ID_VAR} value = {wonder_id} }}"
    )
    lines.append(
        f"{prefix}{T}{T}set_variable = {{ name = {PRIORITY_CANDIDATE_CURRENT_MODE_VAR} value = 2 }}"
    )
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}{T}if = {{")
    lines.append(f"{prefix}{T}{T}limit = {{ exists = scope:tv_wonder_priority_owner }}")
    lines.append(f"{prefix}{T}{T}scope:tv_wonder_priority_owner = {{")
    lines.append(f"{prefix}{T}{T}{T}tv_wonder_register_current_priority_candidate_effect = yes")
    lines.append(f"{prefix}{T}{T}{T}remove_variable = {PRIORITY_CANDIDATE_WONDER_ID_VAR}")
    lines.append(f"{prefix}{T}{T}{T}remove_variable = {PRIORITY_CANDIDATE_CURRENT_MODE_VAR}")
    lines.append(f"{prefix}{T}{T}}}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


def set_suitability_row_key_lines(row_index: int, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}set_local_variable = {{ name = {SUITABILITY_ROW_KEY_LOCAL} value = local_var:{SUITABILITY_MECHANIC_KEY_LOCAL} }}",
        f"{prefix}change_local_variable = {{ name = {SUITABILITY_ROW_KEY_LOCAL} multiply = 10 }}",
        f"{prefix}change_local_variable = {{ name = {SUITABILITY_ROW_KEY_LOCAL} add = {row_index} }}",
    ]


def set_survey_row_key_var_lines(row_index: int, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}set_variable = {{ name = {SURVEY_ROW_KEY_VAR} value = var:{SURVEY_MECHANIC_KEY_VAR} }}",
        f"{prefix}change_variable = {{ name = {SURVEY_ROW_KEY_VAR} multiply = 10 }}",
        f"{prefix}change_variable = {{ name = {SURVEY_ROW_KEY_VAR} add = {row_index} }}",
    ]


def clear_current_suitability_actual_cache_lines(max_rows: int, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}remove_variable = {suitability_current_actual_variable(row_index)}"
        for row_index in range(1, max_rows + 1)
    ]


def clear_current_suitability_display_cache_lines(max_rows: int, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}remove_variable = {suitability_current_revealed_variable()}",
        *clear_current_suitability_actual_cache_lines(max_rows, indent),
    ]


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
            elif scope == "country_scale_block":
                lines.append(f"{prefix}{effect} = {{ scale = {value} }}")
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
        reward_type = entry["type"]
        spec = STYLE_3_REWARD_EFFECTS.get(reward_type, {})
        if spec.get("scope") == "location_scalar":
            lines.append(f"{prefix}var:tv_wonder_site ?= {{ {spec['effect']} = {fmt_value(entry['value'])} }}")
        else:
            lines.extend(country_reward_effect_lines([entry], indent))
    return lines


def location_tooltip_reward_effect_lines(reward: list[dict], indent: int = 1) -> list[str]:
    prefix = T * indent
    lines: list[str] = []
    for entry in reward:
        reward_type = entry["type"]
        spec = STYLE_3_REWARD_EFFECTS.get(reward_type, {})
        if spec.get("scope") == "location_scalar":
            lines.append(f"{prefix}{spec['effect']} = {fmt_value(entry['value'])}")
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


def selected_ritual_limit(wonder: dict, style: int) -> str:
    ritual_id = wonder_ritual_composite_id(int(wonder["id"]), int(style))
    return f"var:tv_wonder_selected_ritual_id ?= {ritual_id}"


def append_pharos_set_route_projection_lines(lines: list[str], route_key: str, indent: int) -> None:
    prefix = T * indent
    route_id = PHAROS_ROUTE_IDS[route_key]
    location_var = f"tv_wonder_pharos_route_{route_key}_location"
    status_var = f"tv_wonder_pharos_route_{route_key}_status"
    owner_var = f"tv_wonder_pharos_route_{route_key}_owner"
    lines.append(f"{prefix}remove_variable = {location_var}")
    lines.append(f"{prefix}remove_variable = {owner_var}")
    lines.append(f"{prefix}location:{route_key} = {{")
    lines.append(f"{prefix}{T}save_scope_as = tv_wonder_pharos_projection_location")
    lines.append(
        f"{prefix}{T}root = {{ set_variable = {{ name = {location_var} value = scope:tv_wonder_pharos_projection_location }} }}"
    )
    lines.append(f"{prefix}{T}if = {{")
    lines.append(f"{prefix}{T}{T}limit = {{ has_owner = yes }}")
    lines.append(f"{prefix}{T}{T}owner = {{")
    lines.append(f"{prefix}{T}{T}{T}save_scope_as = tv_wonder_pharos_projection_owner")
    lines.append(
        f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = {owner_var} value = scope:tv_wonder_pharos_projection_owner }} }}"
    )
    lines.append(f"{prefix}{T}{T}}}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{ tv_wonder_pharos_route_{route_key}_controlled_trigger = yes }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = {status_var} value = 1 }}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}else_if = {{")
    lines.append(f"{prefix}{T}limit = {{ tv_wonder_pharos_route_{route_key}_basing_trigger = yes }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = {status_var} value = 2 }}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}else = {{")
    lines.append(f"{prefix}{T}set_variable = {{ name = {status_var} value = 0 }}")
    lines.append(f"{prefix}}}")
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{")
    lines.append(f"{prefix}{T}{T}has_variable = tv_wonder_pharos_active_route")
    lines.append(f"{prefix}{T}{T}var:tv_wonder_pharos_active_route ?= {route_id}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route_id value = {route_id} }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route_status value = var:{status_var} }}")
    lines.append(f"{prefix}{T}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{prefix}{T}if = {{")
    lines.append(f"{prefix}{T}{T}limit = {{ has_variable = {owner_var} }}")
    lines.append(f"{prefix}{T}{T}set_variable = {{ name = tv_wonder_pharos_active_route_owner value = var:{owner_var} }}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


def append_pharos_select_route_lines(lines: list[str], route_key: str, indent: int) -> None:
    prefix = T * indent
    route_id = PHAROS_ROUTE_IDS[route_key]
    lines.append(f"{prefix}set_variable = {{ name = tv_wonder_pharos_active_route value = {route_id} }}")
    lines.append(f"{prefix}set_variable = {{ name = tv_wonder_pharos_active_route_id value = {route_id} }}")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_event_route_location")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_event_route_owner")
    lines.append(f"{prefix}remove_variable = tv_wonder_pharos_event_route_has_owner")
    lines.append(f"{prefix}location:{route_key} = {{")
    lines.append(f"{prefix}{T}save_scope_as = tv_wonder_pharos_selected_route_location")
    lines.append(
        f"{prefix}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_event_route_location value = scope:tv_wonder_pharos_selected_route_location }} }}"
    )
    lines.append(f"{prefix}{T}if = {{")
    lines.append(f"{prefix}{T}{T}limit = {{ has_owner = yes }}")
    lines.append(f"{prefix}{T}{T}owner = {{")
    lines.append(f"{prefix}{T}{T}{T}save_scope_as = tv_wonder_pharos_selected_route_owner")
    lines.append(
        f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_event_route_owner value = scope:tv_wonder_pharos_selected_route_owner }} }}"
    )
    lines.append(f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_event_route_has_owner value = 1 }} }}")
    lines.append(
        f"{prefix}{T}{T}{T}root = {{ set_variable = {{ name = tv_wonder_pharos_active_route_owner value = scope:tv_wonder_pharos_selected_route_owner }} }}"
    )
    lines.append(f"{prefix}{T}{T}}}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


def append_pharos_selected_route_completion_lines(lines: list[str], route_key: str, indent: int) -> None:
    prefix = T * indent
    route_id = PHAROS_ROUTE_IDS[route_key]
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{")
    lines.append(f"{prefix}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
    lines.append(f"{prefix}{T}{T}tv_wonder_pharos_route_{route_key}_pending_trigger = yes")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_route_{route_key}_passed value = 1 }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route value = {route_id} }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = tv_wonder_pharos_active_route_id value = {route_id} }}")
    lines.append(f"{prefix}{T}change_variable = {{ name = tv_wonder_pharos_route_progress add = 1 }}")
    lines.append(f"{prefix}}}")


def append_pharos_effects(lines: list[str]) -> None:
    lines.append("tv_wonder_pharos_refresh_threat_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_privateer_threat_pct value = 0 }}")
    for count, pct in ((4, 100), (3, 75), (2, 50), (1, 25)):
        head = "if" if count == 4 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ tv_wonder_pharos_alexandria_hostile_privateers_at_least_{count}_trigger = yes }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_pharos_privateer_threat_pct value = {pct} }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_refresh_route_progress_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_route_progress value = 0 }}")
    for route_key in PHAROS_ROUTE_KEYS:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_pharos_route_{route_key}_passed }}")
        lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_pharos_route_progress add = 1 }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}clamp_variable = {{ name = tv_wonder_pharos_route_progress min = 0 max = {len(PHAROS_ROUTE_KEYS)} }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_refresh_display_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= 101")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_pharos_refresh_threat_effect = yes")
    lines.append(f"{T}{T}tv_wonder_pharos_refresh_route_progress_effect = yes")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_id")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_owner")
    for route_key in PHAROS_ROUTE_KEYS:
        append_pharos_set_route_projection_lines(lines, route_key, 2)
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_clear_privateers_effect = {")
    lines.append(f"{T}location:alexandria = {{")
    lines.append(f"{T}{T}sea_zone = {{")
    lines.append(f"{T}{T}{T}area = {{")
    lines.append(f"{T}{T}{T}{T}every_privateer_in_area = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ NOT = {{ owner = root }} }}")
    lines.append(f"{T}{T}{T}{T}{T}change_privateer_power = -0.4")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_enter_stage_2_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_stage value = 2 }}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_quarter_month value = 0 }}")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route_id")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_event_route_location")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_event_route_owner")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_event_route_has_owner")
    lines.append(f"{T}add_prestige = 5")
    lines.append(f"{T}change_gold_effect = {{ scale = 1 }}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_complete_selected_controlled_route_effect = {")
    for route_key in PHAROS_ROUTE_KEYS:
        append_pharos_selected_route_completion_lines(lines, route_key, 1)
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_active_route_status value = 1 }}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append(f"{T}tv_wonder_pharos_maybe_finish_routes_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_complete_selected_basing_route_effect = {")
    for route_key in PHAROS_ROUTE_KEYS:
        append_pharos_selected_route_completion_lines(lines, route_key, 1)
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_active_route_status value = 2 }}")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append(f"{T}tv_wonder_pharos_maybe_finish_routes_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_create_selected_route_basing_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ exists = scope:tv_wonder_pharos_event_route_owner }}")
    lines.append(f"{T}{T}create_relation = {{")
    lines.append(f"{T}{T}{T}first = root")
    lines.append(f"{T}{T}{T}second = scope:tv_wonder_pharos_event_route_owner")
    lines.append(f"{T}{T}{T}type = relation_type:fleet_basing_rights")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}create_relation = {{")
    lines.append(f"{T}{T}{T}first = scope:tv_wonder_pharos_event_route_owner")
    lines.append(f"{T}{T}{T}second = root")
    lines.append(f"{T}{T}{T}type = relation_type:fleet_basing_rights")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_pharos_active_route_owner value = scope:tv_wonder_pharos_event_route_owner }}")
    lines.append(f"{T}{T}tv_wonder_pharos_complete_selected_basing_route_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_evaluate_selected_route_effect = {")
    lines.append(f"{T}tv_wonder_pharos_refresh_display_effect = yes")
    first = True
    for route_key in PHAROS_ROUTE_KEYS:
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_{route_key}_controlled_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7305 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_{route_key}_basing_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7306 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_selected_{route_key}_trigger = yes")
        lines.append(f"{T}{T}{T}tv_wonder_pharos_route_{route_key}_has_owner_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7307 }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_roll_route_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_pharos_has_pending_route_trigger = yes }}")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_id")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_status")
    lines.append(f"{T}{T}remove_variable = tv_wonder_pharos_active_route_owner")
    lines.append(f"{T}{T}random_list = {{")
    for route_key in PHAROS_ROUTE_KEYS:
        lines.append(f"{T}{T}{T}10 = {{")
        lines.append(f"{T}{T}{T}{T}trigger = {{ tv_wonder_pharos_route_{route_key}_pending_trigger = yes }}")
        append_pharos_select_route_lines(lines, route_key, 4)
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_pharos_evaluate_selected_route_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_pharos_maybe_finish_routes_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_maybe_finish_routes_effect = {")
    lines.append(f"{T}tv_wonder_pharos_refresh_route_progress_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_pharos_route_progress")
    lines.append(f"{T}{T}{T}var:tv_wonder_pharos_route_progress >= {len(PHAROS_ROUTE_KEYS)}")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = tv_wonder_pharos_routes_complete_pending_event }}")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = tv_wonder_pharos_routes_complete }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_pharos_routes_complete_pending_event value = 1 }}")
    lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.7308 }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_pharos_finish_ritual_effect = {")
    lines.append(f"{T}remove_variable = tv_wonder_pharos_routes_complete_pending_event")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_pharos_routes_complete value = 1 }}")
    lines.append(f"{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append("}")
    lines.append("")


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


def completion_ritual_payload_lines(ritual_plan: dict, indent: int) -> list[str]:
    lines: list[str] = []
    lines.extend(reward_effect_lines(ritual_plan.get("reward", []), indent))
    lines.extend(indent_script_block(ritual_plan.get("completion_effect_script", ""), indent))
    return lines


def add_country_modifier_preview_line(modifier_name: str, years: int, indent: int) -> str:
    return (
        f"{T * indent}add_country_modifier = {{ modifier = {modifier_name} "
        f"years = {years} mode = add_and_extend }}"
    )


def location_owner_country_modifier_preview_lines(modifier_name: str, years: int, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}owner ?= {{",
        add_country_modifier_preview_line(modifier_name, years, indent + 1),
        f"{prefix}}}",
    ]


def ritual_requirement_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_requirement_tooltip_effect"


def ritual_effect_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_effect_tooltip_effect"


def ritual_location_tooltip_effect_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_{style}_location_tooltip_effect"


def ritual_location_tooltip_effect_alias_name(wonder: dict, style: int) -> str:
    return f"tv_wonder_display_{wonder['id']}_ritual_{style}_location_tooltip_effect"


def append_display_modifier_reference_effect(lines: list[str], wonders: list[dict]) -> None:
    lines.append("tv_wonder_mechanics_reference_display_modifiers_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ always = no }}")
    lines.append(f"{T}{T}# Static references for dynamic ShowModifierEffect display keys.")
    for wonder in wonders:
        for level in range(1, 7):
            lines.append(
                f"{T}{T}add_country_modifier = {{ "
                f"modifier = {wonder_static_display_modifier_name(wonder, level)} "
                "years = -1 mode = add_and_extend }"
            )
    lines.append(f"{T}{T}capital = {{")
    for wonder in wonders:
        for level in range(1, 7):
            lines.append(
                f"{T}{T}{T}add_location_modifier = {{ "
                f"modifier = {wonder_static_local_display_modifier_name(wonder, level)} "
                "years = -1 mode = add_and_extend }"
            )
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


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
            return [add_country_modifier_preview_line(ritual_burden_modifier_name(wonder), timed.get("years", 1), indent)]
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


def ritual_effect_tooltip_lines(wonder: dict, style: int, ritual_plan: dict, indent: int) -> list[str]:
    if wonder.get("is_unique"):
        lines: list[str] = []
        if ritual_plan.get("country_modifier", {}):
            lines.append(add_country_modifier_preview_line(unique_ceremony_modifier_name(wonder), -1, indent))
        lines.extend(reward_effect_lines(ritual_plan.get("reward", []), indent))
        lines.extend(indent_script_block(ritual_plan.get("completion_effect_script", ""), indent))
        return lines

    mode = ritual_plan["mode"]
    if mode == "timed":
        lines: list[str] = []
        timed = ritual_plan.get("timed", {})
        if timed.get("blessing_modifier", {}):
            lines.append(add_country_modifier_preview_line(ritual_blessing_modifier_name(wonder), -1, indent))
        lines.extend(completion_ritual_payload_lines(ritual_plan, indent))
        return lines
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


def ritual_location_tooltip_lines(wonder: dict, style: int, ritual_plan: dict, indent: int) -> list[str]:
    if wonder.get("is_unique"):
        lines: list[str] = []
        if ritual_plan.get("country_modifier", {}):
            lines.extend(location_owner_country_modifier_preview_lines(unique_ceremony_modifier_name(wonder), -1, indent))
        lines.extend(location_tooltip_reward_effect_lines(ritual_plan.get("reward", []), indent))
        return lines

    mode = ritual_plan["mode"]
    if mode == "timed":
        lines: list[str] = []
        timed = ritual_plan.get("timed", {})
        if timed.get("blessing_modifier", {}):
            lines.extend(
                location_owner_country_modifier_preview_lines(
                    ritual_blessing_modifier_name(wonder),
                    -1,
                    indent,
                )
            )
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
        effect_lines = ritual_effect_tooltip_lines(wonder, style, ritual_plan, 1)
        lines.extend(effect_lines or [f"{T}custom_tooltip = {{ text = NOTHING_HAPPENS_EFFECT }}"])
        lines.append("}")
        lines.append("")

        lines.append(f"{ritual_location_tooltip_effect_name(wonder, style)} = {{")
        location_effect_lines = ritual_location_tooltip_lines(wonder, style, ritual_plan, 1)
        lines.extend(location_effect_lines or [f"{T}custom_tooltip = {{ text = NOTHING_HAPPENS_EFFECT }}"])
        lines.append("}")
        lines.append("")

        lines.append(f"{ritual_location_tooltip_effect_alias_name(wonder, style)} = {{")
        lines.append(f"{T}{ritual_location_tooltip_effect_name(wonder, style)} = yes")
        lines.append("}")
        lines.append("")
    append_selected_ritual_tooltip_dispatch_effect(
        lines,
        "tv_wonder_selected_ritual_requirement_tooltip_effect",
        [
            (wonder, style, ritual_requirement_tooltip_effect_name(wonder, style))
            for wonder, style, _ritual_plan in ritual_entry_list
            if not wonder.get("is_unique")
        ],
    )
    append_selected_ritual_tooltip_dispatch_effect(
        lines,
        "tv_wonder_selected_ritual_effect_tooltip_effect",
        [
            (wonder, style, ritual_effect_tooltip_effect_name(wonder, style))
            for wonder, style, _ritual_plan in ritual_entry_list
        ],
    )


def append_selected_ritual_tooltip_dispatch_effect(
    lines: list[str],
    effect_name: str,
    dispatch_entries: list[tuple[dict, int, str]],
) -> None:
    lines.append(f"{effect_name} = {{")
    for index, (wonder, style, target_effect_name) in enumerate(dispatch_entries):
        branch = "if" if index == 0 else "else_if"
        lines.append(f"{T}{branch} = {{")
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
        lines.append(f"{T}{T}{target_effect_name} = yes")
        lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}custom_tooltip = {{ text = NOTHING_HAPPENS_EFFECT }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def slot_id_var(slot: int) -> str:
    return f"tv_wonder_display_slot_{slot}_id"


def slot_level_var(slot: int) -> str:
    return f"tv_wonder_display_slot_{slot}_level"


def slot_ritual_style_var(slot: int) -> str:
    return f"tv_wonder_display_slot_{slot}_ritual_style"


def slot_ritual_completed_var(slot: int) -> str:
    return f"tv_wonder_display_slot_{slot}_ritual_completed"


def tooltip_slot_id_var(slot: int) -> str:
    return f"tv_wonder_tooltip_slot_{slot}_id"


def tooltip_slot_level_var(slot: int) -> str:
    return f"tv_wonder_tooltip_slot_{slot}_level"


def tooltip_slot_ritual_style_var(slot: int) -> str:
    return f"tv_wonder_tooltip_slot_{slot}_ritual_style"


def tooltip_slot_ritual_completed_var(slot: int) -> str:
    return f"tv_wonder_tooltip_slot_{slot}_ritual_completed"


def append_wonder_map_level_update(
    lines: list[str],
    *,
    indent: int,
    source_level_var: str,
    target_level_var: str,
) -> None:
    prefix = T * indent
    for level in range(6, 0, -1):
        head = "if" if level == 6 else "else_if"
        lines.append(f"{prefix}{head} = {{")
        lines.append(f"{prefix}{T}limit = {{")
        lines.append(f"{prefix}{T}{T}var:{source_level_var} ?= {{ this >= {level} }}")
        lines.append(f"{prefix}{T}{T}NOT = {{ var:{target_level_var} ?= {{ this >= {level} }} }}")
        lines.append(f"{prefix}{T}}}")
        lines.append(f"{prefix}{T}set_variable = {{ name = {target_level_var} value = {level} }}")
        lines.append(f"{prefix}}}")


def append_location_display_slot_push(lines: list[str], *, indent: int, compact: bool) -> None:
    prefix = T * indent
    if compact:
        lines.append(
            f"{prefix}tv_wonder_mechanics_push_location_display_slot_effect = {{ "
            f"wonder_id = var:{LOCATION_DISPLAY_ID_VAR} "
            f"wonder_level = var:{LOCATION_DISPLAY_LEVEL_VAR} "
            f"wonder_ritual_style = var:{LOCATION_DISPLAY_RITUAL_STYLE_VAR} "
            f"wonder_ritual_completed = var:{LOCATION_DISPLAY_RITUAL_COMPLETED_VAR} }}"
        )
    lines.append(
        f"{prefix}tv_wonder_mechanics_push_location_tooltip_slot_effect = {{ "
        f"wonder_id = var:{LOCATION_DISPLAY_ID_VAR} "
        f"wonder_level = var:{LOCATION_DISPLAY_LEVEL_VAR} "
        f"wonder_ritual_style = var:{LOCATION_DISPLAY_RITUAL_STYLE_VAR} "
        f"wonder_ritual_completed = var:{LOCATION_DISPLAY_RITUAL_COMPLETED_VAR} }}"
    )


def append_location_display_push_effects(lines: list[str]) -> None:
    lines.append("tv_wonder_mechanics_push_location_display_slot_effect = {")
    for slot in range(1, DISPLAY_SLOT_MAX + 1):
        head = "if" if slot == 1 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ NOT = {{ has_variable = {slot_id_var(slot)} }} }}")
        lines.append(f"{T}{T}set_variable = {{ name = {slot_id_var(slot)} value = $wonder_id$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {slot_level_var(slot)} value = $wonder_level$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {slot_ritual_style_var(slot)} value = $wonder_ritual_style$ }}")
        lines.append(
            f"{T}{T}set_variable = {{ name = {slot_ritual_completed_var(slot)} value = $wonder_ritual_completed$ }}"
        )
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_push_location_tooltip_slot_effect = {")
    for slot in range(1, TOOLTIP_SLOT_MAX + 1):
        head = "if" if slot == 1 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ NOT = {{ has_variable = {tooltip_slot_id_var(slot)} }} }}")
        lines.append(f"{T}{T}set_variable = {{ name = {tooltip_slot_id_var(slot)} value = $wonder_id$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {tooltip_slot_level_var(slot)} value = $wonder_level$ }}")
        lines.append(f"{T}{T}set_variable = {{ name = {tooltip_slot_ritual_style_var(slot)} value = $wonder_ritual_style$ }}")
        lines.append(
            f"{T}{T}set_variable = {{ name = {tooltip_slot_ritual_completed_var(slot)} value = $wonder_ritual_completed$ }}"
        )
        lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ has_variable = tv_wonder_tooltip_overflow_count }}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = tv_wonder_tooltip_overflow_count add = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else = {{")
    lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_tooltip_overflow_count value = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_location_display_clear_effect(lines: list[str]) -> None:
    lines.append("tv_wonder_mechanics_clear_location_display_state_effect = {")
    lines.append(f"{T}remove_variable = {LOCATION_DISPLAY_ID_VAR}")
    lines.append(f"{T}remove_variable = {LOCATION_DISPLAY_LEVEL_VAR}")
    lines.append(f"{T}remove_variable = {LOCATION_DISPLAY_RITUAL_STYLE_VAR}")
    lines.append(f"{T}remove_variable = {LOCATION_DISPLAY_RITUAL_COMPLETED_VAR}")
    lines.append(f"{T}remove_variable = {WONDER_MAP_UNIQUE_LEVEL_VAR}")
    lines.append(f"{T}remove_variable = {WONDER_MAP_GENERIC_LEVEL_VAR}")
    lines.append(f"{T}remove_variable = {WONDER_MAP_HAS_POTENTIAL_UNIQUE_VAR}")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_tooltip_overflow_count value = 0 }}")
    for slot in range(1, DISPLAY_SLOT_MAX + 1):
        lines.append(f"{T}remove_variable = {slot_id_var(slot)}")
        lines.append(f"{T}remove_variable = {slot_level_var(slot)}")
        lines.append(f"{T}remove_variable = {slot_ritual_style_var(slot)}")
        lines.append(f"{T}remove_variable = {slot_ritual_completed_var(slot)}")
    for slot in range(1, TOOLTIP_SLOT_MAX + 1):
        lines.append(f"{T}remove_variable = {tooltip_slot_id_var(slot)}")
        lines.append(f"{T}remove_variable = {tooltip_slot_level_var(slot)}")
        lines.append(f"{T}remove_variable = {tooltip_slot_ritual_style_var(slot)}")
        lines.append(f"{T}remove_variable = {tooltip_slot_ritual_completed_var(slot)}")
    lines.append("}")
    lines.append("")


def append_location_display_unique_location_projection(lines: list[str], *, compact: bool) -> None:
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_global_variable_map = {UNIQUE_WONDER_LOCATION_MAP}")
    lines.append(f"{T}{T}{T}has_global_variable_map = {UNIQUE_WONDER_FINAL_BUILDING_TYPE_MAP}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}every_key_in_global_variable_map = {{")
    lines.append(f"{T}{T}{T}variable = {UNIQUE_WONDER_LOCATION_MAP}")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}is_key_in_global_variable_map = {{ name = {UNIQUE_WONDER_FINAL_BUILDING_TYPE_MAP} target = this }}")
    lines.append(
        f"{T}{T}{T}{T}\"global_variable_map({UNIQUE_WONDER_LOCATION_MAP}|this)\" = {{ "
        f"this = scope:{LOCATION_DISPLAY_SCOPE} }}"
    )
    lines.append(
        f"{T}{T}{T}{T}\"global_variable_map({UNIQUE_WONDER_FINAL_BUILDING_TYPE_MAP}|this)\" = {{"
    )
    lines.append(f"{T}{T}{T}{T}{T}scope:{LOCATION_DISPLAY_SCOPE} = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}NOT = {{ has_building = prev }}")
    lines.append(f"{T}{T}{T}{T}{T}{T}OR = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}NOT = {{ has_variable_map = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP} }}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}NOT = {{ "
        f"is_key_in_variable_map = {{ name = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP} target = prev }} }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}scope:{LOCATION_DISPLAY_SCOPE} = {{")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {WONDER_MAP_HAS_POTENTIAL_UNIQUE_VAR} value = 1 }}")
    lines.append(f"{T}{T}{T}{T}set_local_variable = {{ name = {LOCATION_DISPLAY_WONDER_ID_LOCAL} value = prev }}")
    lines.append(f"{T}{T}{T}{T}set_local_variable = {{")
    lines.append(f"{T}{T}{T}{T}{T}name = {LOCATION_DISPLAY_BUILDING_TYPE_LOCAL}")
    lines.append(
        f"{T}{T}{T}{T}{T}value = "
        f"\"global_variable_map({UNIQUE_WONDER_FINAL_BUILDING_TYPE_MAP}|local_var:{LOCATION_DISPLAY_WONDER_ID_LOCAL})\""
    )
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_ID_VAR} "
        f"value = local_var:{LOCATION_DISPLAY_WONDER_ID_LOCAL} }}"
    )
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_LEVEL_VAR} value = 0 }}")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_RITUAL_STYLE_VAR} value = 0 }}")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_RITUAL_COMPLETED_VAR} value = 0 }}")
    append_location_display_slot_push(lines, indent=4, compact=compact)
    lines.append(f"{T}{T}{T}{T}remove_local_variable = {LOCATION_DISPLAY_BUILDING_TYPE_LOCAL}")
    lines.append(f"{T}{T}{T}{T}remove_local_variable = {LOCATION_DISPLAY_WONDER_ID_LOCAL}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")


def append_location_display_final_building_projection(lines: list[str], *, compact: bool) -> None:
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_global_variable_map = {FINAL_BUILDING_WONDER_ID_MAP}")
    lines.append(f"{T}{T}{T}has_global_variable_map = {FINAL_BUILDING_RITUAL_STYLE_MAP}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}every_key_in_global_variable_map = {{")
    lines.append(f"{T}{T}{T}variable = {FINAL_BUILDING_WONDER_ID_MAP}")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(
        f"{T}{T}{T}{T}is_key_in_global_variable_map = {{ "
        f"name = {FINAL_BUILDING_RITUAL_STYLE_MAP} target = this }}"
    )
    lines.append(f"{T}{T}{T}{T}scope:{LOCATION_DISPLAY_SCOPE} = {{")
    lines.append(f"{T}{T}{T}{T}{T}has_variable_map = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP}")
    lines.append(
        f"{T}{T}{T}{T}{T}is_key_in_variable_map = {{ "
        f"name = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP} target = prev }}"
    )
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}scope:{LOCATION_DISPLAY_SCOPE} = {{")
    lines.append(f"{T}{T}{T}{T}set_local_variable = {{ name = {LOCATION_DISPLAY_BUILDING_TYPE_LOCAL} value = prev }}")
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_ID_VAR} "
        f"value = \"global_variable_map({FINAL_BUILDING_WONDER_ID_MAP}|local_var:{LOCATION_DISPLAY_BUILDING_TYPE_LOCAL})\" }}"
    )
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_RITUAL_STYLE_VAR} "
        f"value = \"global_variable_map({FINAL_BUILDING_RITUAL_STYLE_MAP}|local_var:{LOCATION_DISPLAY_BUILDING_TYPE_LOCAL})\" }}"
    )
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_LEVEL_VAR} "
        f"value = \"variable_map({FINAL_BUILDING_LEVEL_BY_TYPE_MAP}|local_var:{LOCATION_DISPLAY_BUILDING_TYPE_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_RITUAL_COMPLETED_VAR} value = 1 }}")
    lines.append(f"{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ var:{LOCATION_DISPLAY_ID_VAR} ?= {{ this >= {UNIQUE_WONDER_MIN_ID} }} }}")
    lines.append(
        f"{T}{T}{T}{T}{T}set_local_variable = {{ name = {LOCATION_DISPLAY_WONDER_ID_LOCAL} "
        f"value = var:{LOCATION_DISPLAY_ID_VAR} }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {LOCATION_DISPLAY_RITUAL_COMPLETED_VAR} value = 0 }}")
    lines.append(f"{T}{T}{T}{T}{T}owner ?= {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}{T}has_variable_map = {UNIQUE_RITUAL_COMPLETED_MAP}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}{T}is_key_in_variable_map = {{ "
        f"name = {UNIQUE_RITUAL_COMPLETED_MAP} target = local_var:{LOCATION_DISPLAY_WONDER_ID_LOCAL} }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}prev = {{ "
        f"set_variable = {{ name = {LOCATION_DISPLAY_RITUAL_COMPLETED_VAR} value = 1 }} }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}remove_local_variable = {LOCATION_DISPLAY_WONDER_ID_LOCAL}")
    append_wonder_map_level_update(
        lines,
        indent=5,
        source_level_var=LOCATION_DISPLAY_LEVEL_VAR,
        target_level_var=WONDER_MAP_UNIQUE_LEVEL_VAR,
    )
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}else = {{")
    append_wonder_map_level_update(
        lines,
        indent=5,
        source_level_var=LOCATION_DISPLAY_LEVEL_VAR,
        target_level_var=WONDER_MAP_GENERIC_LEVEL_VAR,
    )
    lines.append(f"{T}{T}{T}{T}}}")
    append_location_display_slot_push(lines, indent=4, compact=compact)
    lines.append(f"{T}{T}{T}{T}remove_local_variable = {LOCATION_DISPLAY_BUILDING_TYPE_LOCAL}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")


def append_location_display_effects(lines: list[str]) -> None:
    append_location_display_push_effects(lines)
    append_location_display_clear_effect(lines)

    lines.append("tv_wonder_mechanics_refresh_location_display_state_effect = {")
    lines.append(f"{T}tv_wonder_mechanics_clear_location_display_state_effect = yes")
    lines.append(f"{T}save_scope_as = {LOCATION_DISPLAY_SCOPE}")
    append_location_display_unique_location_projection(lines, compact=True)
    append_location_display_final_building_projection(lines, compact=True)
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_refresh_world_location_display_state_effect = {")
    lines.append(f"{T}every_location_in_the_world = {{")
    lines.append(f"{T}{T}tv_wonder_mechanics_refresh_location_display_state_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_existing_unique_wonders_initialization_effect(lines: list[str], unique_wonders: list[dict]) -> None:
    existing_wonders = [wonder for wonder in unique_wonders if int(wonder["initial_level"]) > 0]
    lines.append("tv_wonder_initialize_existing_unique_wonders_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}NOT = {{ has_global_variable = {EXISTING_UNIQUE_WONDERS_INITIALIZED_GLOBAL} }}")
    lines.append(f"{T}{T}}}")
    lines.append(
        f"{T}{T}set_global_variable = {{ name = {EXISTING_UNIQUE_WONDERS_INITIALIZED_GLOBAL} value = yes }}"
    )
    for wonder in existing_wonders:
        initial_level = int(wonder["initial_level"])
        final_building = wonder["final_buildings"].get(1)
        if not final_building:
            raise ValueError(f"{wonder['key']} must define final_buildings[1] for game-start initialization")
        building_ref = f"building_type:{final_building}"
        lines.append(f"{T}{T}location:{wonder['location']} = {{")
        lines.append(f"{T}{T}{T}if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ NOT = {{ has_building = {building_ref} }} }}")
        lines.append(
            f"{T}{T}{T}{T}construct_building = {{ building_type = {building_ref} "
            'cost_multiplier = 0 cost_multiplier_reason = "game_concept_event" instant = yes }'
        )
        lines.append(f"{T}{T}{T}}}")
        append_raise_building_to_initial_level(lines, building_ref, initial_level, 3)
        lines.extend(map_replace_lines(FINAL_BUILDING_LEVEL_BY_TYPE_MAP, building_ref, str(initial_level), 3))
        append_seed_existing_unique_survey_maps(lines, int(wonder["id"]), 3)
        if initial_level < 6:
            append_register_existing_unique_priority_candidate(lines, int(wonder["id"]), 3)
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_current_suitability_display_cache_effects(
    lines: list[str],
    wonders: list[dict],
    mechanics: dict,
) -> None:
    max_rows = max(len(suitability_knowledge_for_wonder(mechanics, wonder)) for wonder in wonders)
    lines.append("tv_wonder_mechanics_clear_current_suitability_display_cache_effect = {")
    lines.extend(clear_current_suitability_display_cache_lines(max_rows, 1))
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_clear_current_suitability_actual_cache_effect = {")
    lines.extend(clear_current_suitability_actual_cache_lines(max_rows, 1))
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_refresh_current_suitability_display_cache_effect = {")
    lines.append(f"{T}tv_wonder_mechanics_clear_current_suitability_display_cache_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_locked_mechanic_id }}")
    lines.append(f"{T}{T}set_variable = {{ name = {suitability_current_revealed_variable()} value = 0 }}")
    lines.append(f"{T}{T}set_local_variable = {{ name = {SUITABILITY_MECHANIC_KEY_LOCAL} value = var:tv_wonder_locked_mechanic_id }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.extend(map_key_exists_condition(SUITABILITY_REVEAL_MAP, f"local_var:{SUITABILITY_MECHANIC_KEY_LOCAL}", 4))
    lines.append(f"{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}set_variable = {{ name = {suitability_current_revealed_variable()} "
        f"value = \"variable_map({SUITABILITY_REVEAL_MAP}|local_var:{SUITABILITY_MECHANIC_KEY_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}}}")
    for row_index in range(1, max_rows + 1):
        current_actual = suitability_current_actual_variable(row_index)
        lines.append(f"{T}{T}set_local_variable = {{ name = {SUITABILITY_ROW_KEY_LOCAL} value = var:tv_wonder_locked_mechanic_id }}")
        lines.append(f"{T}{T}change_local_variable = {{ name = {SUITABILITY_ROW_KEY_LOCAL} multiply = 10 }}")
        lines.append(f"{T}{T}change_local_variable = {{ name = {SUITABILITY_ROW_KEY_LOCAL} add = {row_index} }}")
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{")
        lines.extend(map_key_exists_condition(SUITABILITY_ACTUAL_MAP, f"local_var:{SUITABILITY_ROW_KEY_LOCAL}", 4))
        lines.append(f"{T}{T}{T}}}")
        lines.append(
            f"{T}{T}{T}set_variable = {{ name = {current_actual} "
            f"value = \"variable_map({SUITABILITY_ACTUAL_MAP}|local_var:{SUITABILITY_ROW_KEY_LOCAL})\" }}"
        )
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}remove_local_variable = {SUITABILITY_ROW_KEY_LOCAL}")
    lines.append(f"{T}{T}remove_local_variable = {SUITABILITY_MECHANIC_KEY_LOCAL}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_suitability_reveal_effect(lines: list[str]) -> None:
    lines.append("tv_wonder_mechanics_reveal_suitability_knowledge_effect = {")
    lines.append(f"{T}tv_wonder_index_refresh_country_cache_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked_mechanic_id")
    lines.append(f"{T}{T}{T}has_global_variable_map = {SUITABILITY_ROW_COUNT_MAP}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_local_variable = {{ name = {SUITABILITY_MECHANIC_KEY_LOCAL} value = var:tv_wonder_locked_mechanic_id }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}is_key_in_global_variable_map = {{ name = {SUITABILITY_ROW_COUNT_MAP} target = local_var:{SUITABILITY_MECHANIC_KEY_LOCAL} }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}set_local_variable = {{ name = {SUITABILITY_ROW_COUNT_LOCAL} "
        f"value = \"global_variable_map({SUITABILITY_ROW_COUNT_MAP}|local_var:{SUITABILITY_MECHANIC_KEY_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}{T}OR = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}NOT = {{ has_variable_map = {SUITABILITY_REVEAL_MAP} }}")
    lines.append(f"{T}{T}{T}{T}{T}{T}AND = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}has_variable_map = {SUITABILITY_REVEAL_MAP}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}NOT = {{ is_key_in_variable_map = {{ "
        f"name = {SUITABILITY_REVEAL_MAP} target = local_var:{SUITABILITY_MECHANIC_KEY_LOCAL} }} }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.extend(map_replace_lines(SUITABILITY_REVEAL_MAP, f"local_var:{SUITABILITY_MECHANIC_KEY_LOCAL}", "0", 4))
    lines.append(f"{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}set_local_variable = {{ name = {SUITABILITY_REVEAL_VALUE_LOCAL} "
        f"value = \"variable_map({SUITABILITY_REVEAL_MAP}|local_var:{SUITABILITY_MECHANIC_KEY_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ local_var:{SUITABILITY_REVEAL_VALUE_LOCAL} < local_var:{SUITABILITY_ROW_COUNT_LOCAL} }}")
    lines.append(f"{T}{T}{T}{T}change_local_variable = {{ name = {SUITABILITY_REVEAL_VALUE_LOCAL} add = 1 }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ local_var:{SUITABILITY_REVEAL_VALUE_LOCAL} > local_var:{SUITABILITY_ROW_COUNT_LOCAL} }}")
    lines.append(f"{T}{T}{T}{T}set_local_variable = {{ name = {SUITABILITY_REVEAL_VALUE_LOCAL} value = local_var:{SUITABILITY_ROW_COUNT_LOCAL} }}")
    lines.append(f"{T}{T}{T}}}")
    lines.extend(
        map_replace_lines(
            SUITABILITY_REVEAL_MAP,
            f"local_var:{SUITABILITY_MECHANIC_KEY_LOCAL}",
            f"local_var:{SUITABILITY_REVEAL_VALUE_LOCAL}",
            3,
        )
    )
    lines.append(f"{T}{T}{T}tv_wonder_mechanics_refresh_current_suitability_display_cache_effect = yes")
    lines.append(f"{T}{T}{T}remove_local_variable = {SUITABILITY_REVEAL_VALUE_LOCAL}")
    lines.append(f"{T}{T}{T}remove_local_variable = {SUITABILITY_ROW_COUNT_LOCAL}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}remove_local_variable = {SUITABILITY_MECHANIC_KEY_LOCAL}")
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


def append_suitability_actual_row(
    lines: list[str],
    wonder: dict,
    row: dict[str, str],
    row_index: int,
    by_key: dict[str, dict],
    indent: int,
) -> None:
    prefix = T * indent
    row_key = suitability_row_key_for_wonder(wonder, row_index, by_key)
    lines.extend(map_replace_lines(SUITABILITY_ACTUAL_MAP, row_key, "0", indent))
    if row["type"] == "condition_bonus":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{")
        append_suitability_condition_limit(lines, row["condition"], indent + 2)
        lines.append(f"{prefix}{T}}}")
        lines.extend(map_replace_lines(SUITABILITY_ACTUAL_MAP, row_key, fmt_value(row["value"]), indent + 1))
        lines.append(f"{prefix}}}")
        return

    source = row["source"]
    if source not in SUITABILITY_SOURCE_EXPRESSIONS:
        raise ValueError(f"Missing suitability actual source expression for {source}")
    source_expression = SUITABILITY_SOURCE_EXPRESSIONS[source]
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{ tv_wonder_survey_site_selected_trigger = yes }}")
    lines.append(f"{prefix}{T}set_variable = {{ name = {SUITABILITY_ACTUAL_TEMP_VAR} value = var:tv_wonder_survey_site.{source_expression} }}")
    lines.append(
        f"{prefix}{T}clamp_variable = {{ name = {SUITABILITY_ACTUAL_TEMP_VAR} "
        f"min = {fmt_value(row['min'])} max = {fmt_value(row['max'])} }}"
    )
    lines.append(f"{prefix}{T}change_variable = {{ name = {SUITABILITY_ACTUAL_TEMP_VAR} multiply = {fmt_value(row['multiplier'])} }}")
    lines.extend(map_replace_lines(SUITABILITY_ACTUAL_MAP, row_key, f"var:{SUITABILITY_ACTUAL_TEMP_VAR}", indent + 1))
    lines.append(f"{prefix}{T}remove_variable = {SUITABILITY_ACTUAL_TEMP_VAR}")
    lines.append(f"{prefix}}}")


def append_suitability_actual_effects(
    lines: list[str],
    wonders: list[dict],
    mechanics: dict,
    by_key: dict[str, dict],
) -> None:
    lines.append("tv_wonder_mechanics_clear_suitability_actuals_effect = {")
    lines.append(f"{T}clear_variable_map = {SUITABILITY_ACTUAL_MAP}")
    lines.append(f"{T}tv_wonder_mechanics_clear_current_suitability_actual_cache_effect = yes")
    lines.append("}")
    lines.append("")

    for wonder in wonders:
        rows = suitability_knowledge_for_wonder(mechanics, wonder)
        lines.append(f"tv_wonder_calculate_{wonder['key']}_suitability_actuals_effect = {{")
        for row_index, row in enumerate(rows, start=1):
            append_suitability_actual_row(lines, wonder, row, row_index, by_key, 1)
        lines.append(f"{T}tv_wonder_mechanics_refresh_current_suitability_display_cache_effect = yes")
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


def append_survey_cache_transfer_effects(lines: list[str], max_rows: int) -> None:
    completed_survey_maps = [
        LOCATION_SURVEYED_MAP,
        LOCATION_SURVEY_SCALE_MAP,
        LOCATION_SURVEY_LOGISTICS_MAP,
        LOCATION_SURVEY_ORGANIZATION_MAP,
        LOCATION_SURVEY_SCALE_TIER_MAP,
    ]
    competence_maps = [
        (LOCATION_SURVEY_SCALE_MAP, "tv_wonder_scale_competence"),
        (LOCATION_SURVEY_LOGISTICS_MAP, "tv_wonder_logistics_competence"),
        (LOCATION_SURVEY_ORGANIZATION_MAP, "tv_wonder_organization_competence"),
        (LOCATION_SURVEY_SCALE_TIER_MAP, "tv_wonder_scale_tier"),
    ]

    lines.append("tv_wonder_mechanics_copy_completed_survey_from_location_effect = {")
    lines.append(f"{T}tv_wonder_index_refresh_country_cache_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked_mechanic_id")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = {SURVEY_WONDER_KEY_VAR} value = var:tv_wonder_locked }}")
    lines.append(f"{T}{T}set_variable = {{ name = {SURVEY_MECHANIC_KEY_VAR} value = var:tv_wonder_locked_mechanic_id }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = {SURVEY_WONDER_KEY_VAR}")
    lines.append(f"{T}{T}{T}has_variable = {SURVEY_MECHANIC_KEY_VAR}")
    lines.append(f"{T}{T}{T}exists = scope:tv_wonder_selected_survey_site")
    lines.append(f"{T}{T}{T}scope:tv_wonder_selected_survey_site = {{")
    lines.extend(map_key_exists_condition(LOCATION_SURVEYED_MAP, "prev.var:" + SURVEY_WONDER_KEY_VAR, 4))
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}scope:tv_wonder_selected_survey_site = {{")
    for map_name, target_var in competence_maps:
        lines.append(f"{T}{T}{T}if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{")
        lines.extend(map_key_exists_condition(map_name, "prev.var:" + SURVEY_WONDER_KEY_VAR, 5))
        lines.append(f"{T}{T}{T}{T}}}")
        lines.append(
            f"{T}{T}{T}{T}set_variable = {{ name = {SURVEY_LOCATION_COPY_TEMP_VAR} "
            f"value = \"variable_map({map_name}|prev.var:{SURVEY_WONDER_KEY_VAR})\" }}"
        )
        lines.append(
            f"{T}{T}{T}{T}prev = {{ set_variable = {{ name = {target_var} "
            f"value = scope:tv_wonder_selected_survey_site.var:{SURVEY_LOCATION_COPY_TEMP_VAR} }} }}"
        )
        lines.append(f"{T}{T}{T}{T}remove_variable = {SURVEY_LOCATION_COPY_TEMP_VAR}")
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_complete value = 1 }}")
    lines.append(f"{T}{T}remove_variable = tv_wonder_survey_active")
    lines.append(f"{T}{T}tv_wonder_set_io_survey_progress_effect = {{ value = 100 }}")
    lines.append(f"{T}{T}tv_wonder_update_construction_tiers_from_competence_effect = yes")
    lines.append(f"{T}{T}tv_wonder_mechanics_calculate_suitability_actuals_effect = yes")
    for row_index in range(1, max_rows + 1):
        lines.extend(set_survey_row_key_var_lines(row_index, 2))
        lines.append(f"{T}{T}scope:tv_wonder_selected_survey_site = {{")
        lines.append(f"{T}{T}{T}if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{")
        lines.extend(map_key_exists_condition(LOCATION_SURVEY_ACTUAL_MAP, "prev.var:" + SURVEY_ROW_KEY_VAR, 5))
        lines.append(f"{T}{T}{T}{T}}}")
        lines.append(
            f"{T}{T}{T}{T}set_variable = {{ name = {SURVEY_LOCATION_COPY_TEMP_VAR} "
            f"value = \"variable_map({LOCATION_SURVEY_ACTUAL_MAP}|prev.var:{SURVEY_ROW_KEY_VAR})\" }}"
        )
        lines.append(f"{T}{T}{T}{T}prev = {{")
        lines.extend(
            map_replace_lines(
                SUITABILITY_ACTUAL_MAP,
                "var:" + SURVEY_ROW_KEY_VAR,
                f"scope:tv_wonder_selected_survey_site.var:{SURVEY_LOCATION_COPY_TEMP_VAR}",
                5,
            )
        )
        lines.append(f"{T}{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}{T}remove_variable = {SURVEY_LOCATION_COPY_TEMP_VAR}")
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_mechanics_refresh_current_suitability_display_cache_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {SURVEY_ROW_KEY_VAR}")
    lines.append(f"{T}remove_variable = {SURVEY_MECHANIC_KEY_VAR}")
    lines.append(f"{T}remove_variable = {SURVEY_WONDER_KEY_VAR}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_clear_completed_survey_from_location_effect = {")
    lines.append(f"{T}tv_wonder_index_refresh_country_cache_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}exists = scope:tv_wonder_selected_survey_site")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked_mechanic_id")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = {SURVEY_WONDER_KEY_VAR} value = var:tv_wonder_locked }}")
    lines.append(f"{T}{T}set_variable = {{ name = {SURVEY_MECHANIC_KEY_VAR} value = var:tv_wonder_locked_mechanic_id }}")
    lines.append(f"{T}{T}scope:tv_wonder_selected_survey_site = {{")
    for map_name in completed_survey_maps:
        lines.append(f"{T}{T}{T}remove_from_variable_map = {{ name = {map_name} key = prev.var:{SURVEY_WONDER_KEY_VAR} }}")
    lines.append(f"{T}{T}}}")
    for row_index in range(1, max_rows + 1):
        lines.extend(set_survey_row_key_var_lines(row_index, 2))
        lines.append(f"{T}{T}scope:tv_wonder_selected_survey_site = {{")
        lines.append(f"{T}{T}{T}remove_from_variable_map = {{ name = {LOCATION_SURVEY_ACTUAL_MAP} key = prev.var:{SURVEY_ROW_KEY_VAR} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}remove_variable = {SURVEY_ROW_KEY_VAR}")
    lines.append(f"{T}{T}remove_variable = {SURVEY_MECHANIC_KEY_VAR}")
    lines.append(f"{T}{T}remove_variable = {SURVEY_WONDER_KEY_VAR}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_store_survey_on_location_effect = {")
    lines.append(f"{T}tv_wonder_index_refresh_country_cache_effect = yes")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}tv_wonder_survey_site_selected_trigger = yes")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked_mechanic_id")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_mechanics_calculate_suitability_actuals_effect = yes")
    lines.append(f"{T}{T}set_variable = {{ name = {SURVEY_WONDER_KEY_VAR} value = var:tv_wonder_locked }}")
    lines.append(f"{T}{T}set_variable = {{ name = {SURVEY_MECHANIC_KEY_VAR} value = var:tv_wonder_locked_mechanic_id }}")
    lines.append(f"{T}{T}var:tv_wonder_survey_site ?= {{")
    lines.extend(map_replace_lines(LOCATION_SURVEYED_MAP, "prev.var:" + SURVEY_WONDER_KEY_VAR, "1", 3))
    lines.extend(map_replace_lines(LOCATION_SURVEY_SCALE_MAP, "prev.var:" + SURVEY_WONDER_KEY_VAR, "prev.var:tv_wonder_scale_competence", 3))
    lines.extend(map_replace_lines(LOCATION_SURVEY_LOGISTICS_MAP, "prev.var:" + SURVEY_WONDER_KEY_VAR, "prev.var:tv_wonder_logistics_competence", 3))
    lines.extend(map_replace_lines(LOCATION_SURVEY_ORGANIZATION_MAP, "prev.var:" + SURVEY_WONDER_KEY_VAR, "prev.var:tv_wonder_organization_competence", 3))
    lines.extend(map_replace_lines(LOCATION_SURVEY_SCALE_TIER_MAP, "prev.var:" + SURVEY_WONDER_KEY_VAR, "prev.var:tv_wonder_scale_tier", 3))
    lines.append(f"{T}{T}}}")
    for row_index in range(1, max_rows + 1):
        lines.extend(set_survey_row_key_var_lines(row_index, 2))
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{")
        lines.extend(map_key_exists_condition(SUITABILITY_ACTUAL_MAP, "var:" + SURVEY_ROW_KEY_VAR, 4))
        lines.append(f"{T}{T}{T}}}")
        lines.append(
            f"{T}{T}{T}set_variable = {{ name = {SURVEY_LOCATION_COPY_TEMP_VAR} "
            f"value = \"variable_map({SUITABILITY_ACTUAL_MAP}|var:{SURVEY_ROW_KEY_VAR})\" }}"
        )
        lines.append(f"{T}{T}{T}var:tv_wonder_survey_site ?= {{")
        lines.extend(
            map_replace_lines(
                LOCATION_SURVEY_ACTUAL_MAP,
                "prev.var:" + SURVEY_ROW_KEY_VAR,
                f"prev.var:{SURVEY_LOCATION_COPY_TEMP_VAR}",
                4,
            )
        )
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}remove_variable = {SURVEY_LOCATION_COPY_TEMP_VAR}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}remove_variable = {SURVEY_ROW_KEY_VAR}")
    lines.append(f"{T}{T}remove_variable = {SURVEY_MECHANIC_KEY_VAR}")
    lines.append(f"{T}{T}remove_variable = {SURVEY_WONDER_KEY_VAR}")
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
    by_key = all_wonders_by_key(all_wonders)
    generic_wonders = [wonder for wonder in all_wonders if not wonder.get("is_unique")]
    unique_wonders = [wonder for wonder in all_wonders if wonder.get("is_unique")]
    lines = render_header(SCRIPT_REL)
    append_display_modifier_reference_effect(lines, all_wonders)

    lines.append("tv_wonder_mechanics_clear_feasible_deck_effect = {")
    lines.append(f"{T}clear_variable_map = {FEASIBLE_GENERIC_DECK_MAP}")
    lines.append(f"{T}clear_variable_map = {FEASIBLE_UNIQUE_DECK_MAP}")
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

    append_current_suitability_display_cache_effects(lines, all_wonders, mechanics)
    append_suitability_actual_effects(lines, all_wonders, mechanics, by_key)
    max_rows = max(len(suitability_knowledge_for_wonder(mechanics, wonder)) for wonder in all_wonders)
    append_survey_cache_transfer_effects(lines, max_rows)
    append_pharos_effects(lines)

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

    append_ritual_tooltip_effects(lines, ritual_entries(all_wonders, mechanics), mechanics)

    append_existing_unique_wonders_initialization_effect(lines, unique_wonders)
    append_location_display_effects(lines)
    append_suitability_reveal_effect(lines)

    ritual_entry_list = ritual_entries(all_wonders, mechanics)

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
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
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
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
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
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
        lines.extend(progress_ritual_payload_lines(ritual_plan, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_refresh_timed_ritual_progress_display_effect = {")
    lines.append(f"{T}set_variable = {{ name = tv_wonder_ritual_progress_pct value = var:tv_wonder_ritual_months_completed }}")
    lines.append(f"{T}change_variable = {{ name = tv_wonder_ritual_progress_pct multiply = 100 }}")
    lines.append(f"{T}change_variable = {{ name = tv_wonder_ritual_progress_pct divide = 12 }}")
    lines.append(f"{T}clamp_variable = {{ name = tv_wonder_ritual_progress_pct min = 0 max = 100 }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_advance_timed_ritual_month_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}tv_wonder_selected_generic_timed_ritual_trigger = yes")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_ritual_in_progress")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ NOT = {{ has_variable = tv_wonder_ritual_months_completed }} }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_ritual_months_completed value = 0 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_ritual_months_completed add = 1 }}")
    lines.append(f"{T}{T}clamp_variable = {{ name = tv_wonder_ritual_months_completed min = 0 max = 12 }}")
    lines.append(f"{T}{T}tv_wonder_mechanics_refresh_timed_ritual_progress_display_effect = yes")
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
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
        lines.append(f"{T}{T}tv_wonder_mechanics_clear_selected_ritual_runtime_effect = yes")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_in_progress value = 1 }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_locked value = 1 }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_timer value = 1 years = {timed.get('years', 1)} }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_months_completed value = 0 }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_progress_pct value = 0 }}")
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
        lines.append(f"{T}{T}{T}{T}limit = {{ prev = {{ {selected_ritual_limit(wonder, style)} }} }}")
        lines.append(f"{T}{T}{T}{T}construct_building = {{ building_type = building_type:{ritual_auxiliary_building(wonder)} }}")
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    for wonder, style, ritual_plan in ritual_entry_list:
        if ritual_plan["mode"] != "auxiliary_building":
            continue
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
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
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
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
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
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
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
        lines.extend(completion_ritual_payload_lines(ritual_plan, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_selected_ritual_static_modifier_effect = {")
    first = True
    for wonder, style, ritual_plan in ritual_entry_list:
        modifier_name: str | None = None
        if wonder.get("is_unique"):
            if ritual_plan.get("country_modifier", {}):
                modifier_name = unique_ceremony_modifier_name(wonder)
        elif ritual_plan["mode"] == "timed" and ritual_plan.get("timed", {}).get("blessing_modifier", {}):
            modifier_name = ritual_blessing_modifier_name(wonder)
        if modifier_name is None:
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ {selected_ritual_limit(wonder, style)} }}")
        lines.append(f"{T}{T}add_country_modifier = {{ modifier = {modifier_name} years = -1 mode = add_and_extend }}")
        if wonder.get("is_unique"):
            lines.extend(map_replace_lines(UNIQUE_RITUAL_COMPLETED_MAP, wonder["id"], "1", 2))
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
    lines.append(f"{T}{T}tv_wonder_mechanics_apply_selected_ritual_static_modifier_effect = yes")
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
    lines.append(f"{T}{T}{T}{T}tv_wonder_mechanics_apply_selected_ritual_static_modifier_effect = yes")
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
    lines.append(f"{T}{T}{T}tv_wonder_mechanics_apply_selected_ritual_static_modifier_effect = yes")
    lines.append(f"{T}{T}{T}tv_wonder_finalize_effect = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_clear_project_state_effect = {")
    lines.append(f"{T}clear_variable_map = {FEASIBLE_GENERIC_DECK_MAP}")
    lines.append(f"{T}clear_variable_map = {FEASIBLE_UNIQUE_DECK_MAP}")
    runtime_cleanup_vars: list[str] = list(RITUAL_SHARED_RUNTIME_VARS)
    for _wonder, _style, ritual_plan in ritual_entry_list:
        for variable in ritual_plan.get("runtime_variables", []):
            if variable not in runtime_cleanup_vars:
                runtime_cleanup_vars.append(variable)
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
