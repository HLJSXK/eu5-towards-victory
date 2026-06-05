import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    PARTS,
    WONDER_RITUAL_COST_TYPE_IDS,
    WONDER_RITUAL_LISTENER_KEYS,
    WONDER_RITUAL_MODE_IDS,
    ceremony_styles,
    indent_script_block,
    load_all_wonder_mechanics,
    render_header,
    ritual_plan_for_style,
    site_trigger_lines_for_wonder,
    wonder_ritual_composite_id,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_triggers" / "tv_engineering_department_wonder_mechanics_triggers.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py"
T = "\t"
FEASIBLE_GENERIC_DECK_MAP = "tv_wonder_feasible_generic_deck"
FEASIBLE_UNIQUE_DECK_MAP = "tv_wonder_feasible_unique_deck"
LOCATION_SURVEYED_MAP = "tv_wonder_surveyed"
LOCATION_SURVEY_SCALE_TIER_MAP = "tv_wonder_survey_scale_tier"
SITE_RULE_DISPATCH_VAR = "tv_wonder_site_rule_dispatch_id"


def trigger_conditions(wonder: dict, mechanics: dict, indent: int = 1) -> list[str]:
    return site_trigger_lines_for_wonder(mechanics, wonder, indent)


def building_or_block(buildings: list[str], indent: int) -> list[str]:
    prefix = T * indent
    lines = [f"{prefix}OR = {{"]
    for building in buildings:
        lines.append(f"{prefix}{T}has_building = building_type:{building}")
    lines.append(f"{prefix}}}")
    return lines


def intermediate_buildings(wonder: dict) -> list[str]:
    key = wonder["key"]
    return [f"tv_wonder_{key}", *[f"tv_wonder_{key}_{part}" for part in PARTS]]


def final_buildings(wonder: dict) -> list[str]:
    return list(dict.fromkeys(wonder["final_buildings"].values()))


def loc_level(building: str, op: str, level: int) -> str:
    return f"location_building_level = {{ building_type = building_type:{building} value {op} {level} }}"


def final_building_level_exact(building: str, level: int, indent: int) -> list[str]:
    prefix = T * indent
    lines = [f"{prefix}{loc_level(building, '>=', level)}"]
    if level < 6:
        lines.append(f"{prefix}NOT = {{ {loc_level(building, '>=', level + 1)} }}")
    return lines


def stored_tier_can_expand(wonder: dict, final_building: str, level: int, indent: int) -> list[str]:
    prefix = T * indent
    wonder_id = int(wonder["id"])
    lines = final_building_level_exact(final_building, level, indent)
    lines.append(f"{prefix}OR = {{")
    lines.append(f"{prefix}{T}NOT = {{ has_variable_map = {LOCATION_SURVEY_SCALE_TIER_MAP} }}")
    lines.append(f"{prefix}{T}AND = {{")
    lines.append(f"{prefix}{T}{T}has_variable_map = {LOCATION_SURVEY_SCALE_TIER_MAP}")
    lines.append(
        f"{prefix}{T}{T}NOT = {{ is_key_in_variable_map = {{ "
        f"name = {LOCATION_SURVEY_SCALE_TIER_MAP} target = {wonder_id} }} }}"
    )
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}{T}AND = {{")
    lines.append(f"{prefix}{T}{T}has_variable_map = {LOCATION_SURVEY_SCALE_TIER_MAP}")
    lines.append(f"{prefix}{T}{T}is_key_in_variable_map = {{ name = {LOCATION_SURVEY_SCALE_TIER_MAP} target = {wonder_id} }}")
    lines.append(f"{prefix}{T}{T}\"variable_map({LOCATION_SURVEY_SCALE_TIER_MAP}|{wonder_id})\" ?= {{ this >= {level + 1} }}")
    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
    return lines


def final_building_below_cap_conditions(wonder: dict, indent: int) -> list[str]:
    prefix = T * indent
    lines = [f"{prefix}OR = {{"]
    for final_building in final_buildings(wonder):
        for level in range(1, 6):
            lines.append(f"{prefix}{T}AND = {{")
            lines.extend(stored_tier_can_expand(wonder, final_building, level, indent + 2))
            lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
    return lines


def fresh_site_candidate_conditions(wonder: dict, mechanics: dict, indent: int) -> list[str]:
    prefix = T * indent
    lines = [f"{prefix}AND = {{"]
    if wonder.get("is_unique"):
        lines.append(f"{prefix}{T}this = location:{wonder['location']}")
    lines.extend(trigger_conditions(wonder, mechanics, indent + 1))
    lines.append(f"{prefix}{T}NOT = {{ tv_wonder_location_has_{wonder['key']}_capped_final_building_trigger = yes }}")
    lines.append(f"{prefix}}}")
    return lines


def player_visible_site_rule_conditions(wonder: dict, mechanics: dict, indent: int) -> list[str]:
    prefix = T * indent
    if wonder.get("is_unique"):
        return [f"{prefix}owns = location:{wonder['location']}"]

    lines = [f"{prefix}any_owned_location = {{"]
    lines.extend(trigger_conditions(wonder, mechanics, indent + 1))
    lines.append(f"{prefix}}}")
    return lines


def add_project_occupancy_triggers(lines: list[str], wonders: list[dict]) -> None:
    for wonder in wonders:
        key = wonder["key"]
        lines.append(f"tv_wonder_location_has_{key}_intermediate_building_trigger = {{")
        lines.extend(building_or_block(intermediate_buildings(wonder), 1))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_location_has_{key}_final_building_trigger = {{")
        lines.extend(building_or_block(final_buildings(wonder), 1))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_location_has_{key}_expandable_final_building_trigger = {{")
        lines.extend(final_building_below_cap_conditions(wonder, 1))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_location_has_{key}_capped_final_building_trigger = {{")
        lines.append(f"{T}tv_wonder_location_has_{key}_final_building_trigger = yes")
        lines.append(f"{T}NOT = {{ tv_wonder_location_has_{key}_expandable_final_building_trigger = yes }}")
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_location_is_valid_priority_project_for_{key}_trigger = {{")
        lines.append(f"{T}trigger_if = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_location_has_{key}_intermediate_building_trigger = yes")
        lines.append(f"{T}{T}{T}NOT = {{ tv_wonder_location_has_any_wonder_final_building_trigger = yes }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}always = yes")
        lines.append(f"{T}}}")
        lines.append(f"{T}trigger_else_if = {{")
        lines.append(f"{T}{T}limit = {{ tv_wonder_location_has_{key}_expandable_final_building_trigger = yes }}")
        lines.append(f"{T}{T}always = yes")
        lines.append(f"{T}}}")
        lines.append(f"{T}trigger_else = {{ always = no }}")
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_location_has_any_wonder_final_building_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}tv_wonder_location_has_{wonder['key']}_final_building_trigger = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_has_locked_wonder_intermediate_building_trigger = {")
    for idx, wonder in enumerate(wonders):
        head = "trigger_if" if idx == 0 else "trigger_else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}tv_wonder_location_has_{wonder['key']}_intermediate_building_trigger = yes")
        lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = no }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_has_locked_wonder_expandable_final_building_trigger = {")
    for idx, wonder in enumerate(wonders):
        head = "trigger_if" if idx == 0 else "trigger_else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}tv_wonder_location_has_{wonder['key']}_expandable_final_building_trigger = yes")
        lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = no }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_is_valid_priority_project_for_locked_wonder_trigger = {")
    lines.append(f"{T}trigger_if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}tv_wonder_location_has_locked_wonder_intermediate_building_trigger = yes")
    lines.append(f"{T}{T}{T}NOT = {{ tv_wonder_location_has_any_wonder_final_building_trigger = yes }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}always = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else_if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_location_has_locked_wonder_expandable_final_building_trigger = yes }}")
    lines.append(f"{T}{T}always = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = no }}")
    lines.append("}")
    lines.append("")


def has_any_key_in_map_trigger(map_name: str, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}has_variable_map = {map_name}",
        f"{prefix}any_key_in_variable_map = {{",
        f"{prefix}{T}variable = {map_name}",
        f"{prefix}{T}always = yes",
        f"{prefix}}}",
    ]


def selected_ritual_attribute_trigger(name: str, cache_var: str, expected_value: int) -> list[str]:
    return [
        f"{name} = {{",
        f"{T}tv_wonder_has_selected_ceremony_trigger = yes",
        f"{T}has_variable = {cache_var}",
        f"{T}var:{cache_var} ?= {expected_value}",
        "}",
        "",
    ]


def selected_ritual_id_limit(wonder: dict, style: int) -> str:
    return f"var:tv_wonder_selected_ritual_id ?= {wonder_ritual_composite_id(int(wonder['id']), int(style))}"


def selected_ritual_script_trigger(
    name: str,
    wonders: list[dict],
    mechanics: dict,
    *,
    script_field: str,
) -> list[str]:
    lines = [f"{name} = {{", f"{T}tv_wonder_has_selected_ceremony_trigger = yes"]
    matched = False
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            script_lines = indent_script_block(ritual_plan.get(script_field, ""), 2)
            if not script_lines:
                continue
            head = "trigger_if" if not matched else "trigger_else_if"
            matched = True
            lines.append(f"{T}{head} = {{")
            lines.append(f"{T}{T}limit = {{ {selected_ritual_id_limit(wonder, style)} }}")
            lines.extend(script_lines)
            lines.append(f"{T}}}")
    if matched:
        lines.append(f"{T}trigger_else = {{ always = no }}")
    else:
        lines.append(f"{T}always = no")
    lines.append("}")
    lines.append("")
    return lines


def append_id_dispatch_trigger(
    lines: list[str],
    name: str,
    wonders: list[dict],
    *,
    limit_line,
    target_line,
) -> None:
    lines.append(f"{name} = {{")
    for idx, wonder in enumerate(wonders):
        head = "trigger_if" if idx == 0 else "trigger_else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ {limit_line(wonder)} }}")
        lines.append(f"{T}{T}{target_line(wonder)}")
        lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = no }}")
    lines.append("}")
    lines.append("")


def append_site_rule_dispatch_triggers(lines: list[str], wonders: list[dict]) -> None:
    append_id_dispatch_trigger(
        lines,
        "tv_wonder_site_rule_can_build_candidate_trigger",
        wonders,
        limit_line=lambda wonder: f"var:{SITE_RULE_DISPATCH_VAR} ?= {wonder['id']}",
        target_line=lambda wonder: f"tv_wonder_can_build_{wonder['key']}_trigger = yes",
    )
    append_id_dispatch_trigger(
        lines,
        "tv_wonder_site_rule_can_build_locked_wonder_trigger",
        wonders,
        limit_line=lambda wonder: f"var:tv_wonder_locked ?= {wonder['id']}",
        target_line=lambda wonder: f"tv_wonder_can_build_{wonder['key']}_trigger = yes",
    )
    append_id_dispatch_trigger(
        lines,
        "tv_wonder_site_rule_player_visible_locked_wonder_trigger",
        wonders,
        limit_line=lambda wonder: f"var:tv_wonder_locked ?= {wonder['id']}",
        target_line=lambda wonder: f"tv_wonder_player_visible_site_rules_{wonder['key']}_trigger = yes",
    )
    append_id_dispatch_trigger(
        lines,
        "tv_wonder_location_can_host_locked_wonder_trigger",
        wonders,
        limit_line=lambda wonder: (
            f"exists = scope:actor scope:actor = {{ var:tv_wonder_locked ?= {wonder['id']} }}"
        ),
        target_line=lambda wonder: f"tv_wonder_location_can_host_{wonder['key']}_trigger = yes",
    )


def generate() -> str:
    all_wonders, mechanics = load_all_wonder_mechanics()
    generic_wonders = [wonder for wonder in all_wonders if not wonder.get("is_unique")]
    unique_wonders = [wonder for wonder in all_wonders if wonder.get("is_unique")]
    lines = render_header(SCRIPT_REL)
    add_project_occupancy_triggers(lines, all_wonders)
    for wonder in all_wonders:
        lines.append(f"tv_wonder_location_can_host_{wonder['key']}_trigger = {{")
        lines.append(f"{T}OR = {{")
        lines.append(f"{T}{T}tv_wonder_location_is_valid_priority_project_for_{wonder['key']}_trigger = yes")
        lines.extend(fresh_site_candidate_conditions(wonder, mechanics, 2))
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_can_build_{wonder['key']}_trigger = {{")
        if wonder.get("is_unique"):
            lines.append(f"{T}owns = location:{wonder['location']}")
            lines.append(f"{T}location:{wonder['location']} = {{")
            lines.append(f"{T}{T}tv_wonder_location_can_host_{wonder['key']}_trigger = yes")
            lines.append(f"{T}}}")
        else:
            lines.append(f"{T}any_owned_location = {{")
            lines.append(f"{T}{T}tv_wonder_location_can_host_{wonder['key']}_trigger = yes")
            lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_player_visible_site_rules_{wonder['key']}_trigger = {{")
        lines.extend(player_visible_site_rule_conditions(wonder, mechanics, 1))
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_generic_has_any_feasible_proposal_trigger = {")
    lines.extend(has_any_key_in_map_trigger(FEASIBLE_GENERIC_DECK_MAP, 1))
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_unique_has_any_feasible_proposal_trigger = {")
    lines.extend(has_any_key_in_map_trigger(FEASIBLE_UNIQUE_DECK_MAP, 1))
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    lines.append(f"{T}{T}tv_wonder_generic_has_any_feasible_proposal_trigger = yes")
    lines.append(f"{T}{T}tv_wonder_unique_has_any_feasible_proposal_trigger = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    append_site_rule_dispatch_triggers(lines, all_wonders)

    lines.append("tv_wonder_mechanics_has_valid_site_candidate_trigger = {")
    lines.append(f"{T}tv_wonder_site_rule_can_build_locked_wonder_trigger = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_selected_survey_already_cached_trigger = {")
    lines.append(f"{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}scope:tv_wonder_selected_survey_site = {{")
    lines.append(f"{T}{T}has_variable_map = {LOCATION_SURVEYED_MAP}")
    lines.append(f"{T}{T}is_key_in_variable_map = {{ name = {LOCATION_SURVEYED_MAP} target = prev.var:tv_wonder_locked }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.extend(
        selected_ritual_attribute_trigger(
            "tv_wonder_selected_generic_timed_ritual_trigger",
            "tv_wonder_selected_ritual_mode",
            WONDER_RITUAL_MODE_IDS["timed"],
        )
    )
    lines.extend(
        selected_ritual_attribute_trigger(
            "tv_wonder_selected_generic_auxiliary_building_ritual_trigger",
            "tv_wonder_selected_ritual_mode",
            WONDER_RITUAL_MODE_IDS["auxiliary_building"],
        )
    )
    lines.extend(
        selected_ritual_attribute_trigger(
            "tv_wonder_selected_generic_immediate_ritual_trigger",
            "tv_wonder_selected_ritual_mode",
            WONDER_RITUAL_MODE_IDS["immediate"],
        )
    )
    lines.append("tv_wonder_selected_deferred_immediate_ritual_trigger = {")
    lines.append(f"{T}tv_wonder_selected_generic_immediate_ritual_trigger = yes")
    lines.append(f"{T}has_variable = tv_wonder_selected_ritual_deferred_completion")
    lines.append(f"{T}var:tv_wonder_selected_ritual_deferred_completion ?= 1")
    lines.append("}")
    lines.append("")
    lines.extend(
        selected_ritual_attribute_trigger(
            "tv_wonder_selected_generic_no_decoration_cost_ritual_trigger",
            "tv_wonder_selected_ritual_cost_type",
            WONDER_RITUAL_COST_TYPE_IDS[None],
        )
    )
    lines.extend(
        selected_ritual_attribute_trigger(
            "tv_wonder_selected_generic_artwork_decoration_ritual_trigger",
            "tv_wonder_selected_ritual_cost_type",
            WONDER_RITUAL_COST_TYPE_IDS["artwork"],
        )
    )
    lines.extend(
        selected_ritual_attribute_trigger(
            "tv_wonder_selected_generic_scaled_gold_decoration_ritual_trigger",
            "tv_wonder_selected_ritual_cost_type",
            WONDER_RITUAL_COST_TYPE_IDS["scaled_gold"],
        )
    )
    lines.extend(
        selected_ritual_attribute_trigger(
            "tv_wonder_selected_generic_prestige_decoration_ritual_trigger",
            "tv_wonder_selected_ritual_cost_type",
            WONDER_RITUAL_COST_TYPE_IDS["prestige"],
        )
    )

    lines.extend(
        selected_ritual_script_trigger(
            "tv_wonder_selected_ritual_custom_confirmation_requirements_met_trigger",
            all_wonders,
            mechanics,
            script_field="confirmation_trigger_script",
        )
    )
    lines.append("tv_wonder_selected_ritual_confirmation_requirements_met_trigger = {")
    lines.append(f"{T}tv_wonder_has_selected_ceremony_trigger = yes")
    lines.append(f"{T}trigger_if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_selected_ritual_has_confirmation_trigger")
    lines.append(f"{T}{T}{T}var:tv_wonder_selected_ritual_has_confirmation_trigger ?= 1")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_selected_ritual_custom_confirmation_requirements_met_trigger = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = yes }}")
    lines.append("}")
    lines.append("")

    for listener in WONDER_RITUAL_LISTENER_KEYS:
        lines.extend(
            selected_ritual_attribute_trigger(
                f"tv_wonder_selected_ritual_{listener}_listener_trigger",
                f"tv_wonder_selected_ritual_listener_{listener}",
                1,
            )
        )

    lines.extend(
        selected_ritual_script_trigger(
            "tv_wonder_selected_ritual_custom_completion_requirements_met_trigger",
            all_wonders,
            mechanics,
            script_field="completion_trigger_script",
        )
    )
    lines.append("tv_wonder_selected_ritual_completion_requirements_met_trigger = {")
    lines.append(f"{T}tv_wonder_has_selected_ceremony_trigger = yes")
    lines.append(f"{T}trigger_if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_selected_ritual_has_custom_completion_trigger")
    lines.append(f"{T}{T}{T}var:tv_wonder_selected_ritual_has_custom_completion_trigger ?= 1")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_selected_ritual_custom_completion_requirements_met_trigger = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else_if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_selected_generic_timed_ritual_trigger = yes }}")
    lines.append(f"{T}{T}NOT = {{ has_variable = tv_wonder_ritual_timer }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else_if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_selected_generic_auxiliary_building_ritual_trigger = yes }}")
    lines.append(f"{T}{T}has_variable = tv_wonder_ritual_auxiliary_building_finished")
    lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = yes }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_ceremony_ready_for_confirmation_trigger = {")
    lines.append(f"{T}tv_wonder_has_selected_ceremony_trigger = yes")
    lines.append(f"{T}NOT = {{ has_variable = tv_wonder_ritual_in_progress }}")
    lines.append(f"{T}tv_wonder_selected_ritual_confirmation_requirements_met_trigger = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_ceremony_ready_for_free_confirmation_trigger = {")
    lines.append(f"{T}tv_wonder_ceremony_ready_for_confirmation_trigger = yes")
    lines.append(f"{T}OR = {{")
    lines.append(f"{T}{T}AND = {{")
    lines.append(f"{T}{T}{T}tv_wonder_selected_generic_immediate_ritual_trigger = yes")
    lines.append(f"{T}{T}{T}tv_wonder_selected_generic_no_decoration_cost_ritual_trigger = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_selected_generic_timed_ritual_trigger = yes")
    lines.append(f"{T}{T}tv_wonder_selected_generic_auxiliary_building_ritual_trigger = yes")
    lines.append(f"{T}{T}AND = {{")
    lines.append(f"{T}{T}{T}tv_wonder_selected_generic_artwork_decoration_ritual_trigger = yes")
    lines.append(f"{T}{T}{T}tv_wonder_artwork_loss_agenda_available_trigger = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_ceremony_ready_for_scaled_gold_confirmation_trigger = {")
    lines.append(f"{T}tv_wonder_ceremony_ready_for_confirmation_trigger = yes")
    lines.append(f"{T}tv_wonder_selected_generic_scaled_gold_decoration_ritual_trigger = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_ceremony_ready_for_prestige_confirmation_trigger = {")
    lines.append(f"{T}tv_wonder_ceremony_ready_for_confirmation_trigger = yes")
    lines.append(f"{T}tv_wonder_selected_generic_prestige_decoration_ritual_trigger = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_unique_locked_trigger = {")
    lines.append(f"{T}tv_wonder_has_locked_wonder_trigger = yes")
    lines.append(f"{T}has_variable = tv_wonder_locked_is_unique")
    lines.append(f"{T}var:tv_wonder_locked_is_unique ?= 1")
    lines.append("}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
