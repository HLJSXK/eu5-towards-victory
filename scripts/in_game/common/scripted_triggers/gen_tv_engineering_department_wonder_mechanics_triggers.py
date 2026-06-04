import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ALL_WONDER_MAX_ID,
    ALL_WONDER_MIN_ID,
    PARTS,
    WONDER_RITUAL_COST_TYPE_IDS,
    WONDER_RITUAL_MODE_IDS,
    ceremony_styles,
    indent_script_block,
    load_all_wonder_mechanics,
    render_header,
    ritual_has_custom_completion_trigger,
    ritual_listens_to,
    ritual_plan_for_style,
    ritual_uses_deferred_completion,
    site_trigger_lines_for_wonder,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_triggers" / "tv_engineering_department_wonder_mechanics_triggers.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py"
T = "\t"


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


def project_buildings(wonder: dict) -> list[str]:
    return [*intermediate_buildings(wonder), *final_buildings(wonder)]


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
    tier_var = f"tv_wonder_{wonder['key']}_scale_tier"
    lines = final_building_level_exact(final_building, level, indent)
    lines.append(f"{prefix}OR = {{")
    lines.append(f"{prefix}{T}var:{tier_var} ?= {{ this >= {level + 1} }}")
    lines.append(f"{prefix}{T}NOT = {{ has_variable = {tier_var} }}")
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
        lines.append(f"tv_wonder_location_has_{key}_project_building_trigger = {{")
        lines.extend(building_or_block(project_buildings(wonder), 1))
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


def grouped_selected_trigger(
    name: str,
    wonders: list[dict],
    mechanics: dict,
    predicate,
    *,
    include_confirmation_script: bool = False,
) -> list[str]:
    lines = [f"{name} = {{", f"{T}tv_wonder_has_selected_ceremony_trigger = yes"]
    matched = False
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            if not predicate(wonder, style, ritual_plan):
                continue
            head = "trigger_if" if not matched else "trigger_else_if"
            matched = True
            lines.append(f"{T}{head} = {{")
            lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
            if include_confirmation_script:
                confirmation_lines = indent_script_block(ritual_plan.get("confirmation_trigger_script", ""), 2)
                if confirmation_lines:
                    lines.extend(confirmation_lines)
                else:
                    lines.append(f"{T}{T}always = yes")
            else:
                lines.append(f"{T}{T}always = yes")
            lines.append(f"{T}}}")
    if matched:
        lines.append(f"{T}trigger_else = {{ always = no }}")
    else:
        lines.append(f"{T}always = no")
    lines.append("}")
    lines.append("")
    return lines


def selected_ritual_attribute_trigger(name: str, cache_var: str, expected_value: int) -> list[str]:
    return [
        f"{name} = {{",
        f"{T}tv_wonder_has_selected_ceremony_trigger = yes",
        f"{T}has_variable = {cache_var}",
        f"{T}var:{cache_var} ?= {expected_value}",
        "}",
        "",
    ]


def completion_trigger_lines(ritual_plan: dict, indent: int) -> list[str]:
    if ritual_has_custom_completion_trigger(ritual_plan):
        return indent_script_block(ritual_plan.get("completion_trigger_script", ""), indent)

    prefix = T * indent
    if ritual_plan["mode"] == "timed":
        return [f"{prefix}NOT = {{ has_variable = tv_wonder_ritual_timer }}"]
    if ritual_plan["mode"] == "auxiliary_building":
        return [f"{prefix}has_variable = tv_wonder_ritual_auxiliary_building_finished"]
    return [f"{prefix}always = yes"]


def grouped_selected_completion_trigger(name: str, wonders: list[dict], mechanics: dict) -> list[str]:
    lines = [f"{name} = {{", f"{T}tv_wonder_has_selected_ceremony_trigger = yes"]
    matched = False
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            if not ritual_uses_deferred_completion(ritual_plan):
                continue
            head = "trigger_if" if not matched else "trigger_else_if"
            matched = True
            lines.append(f"{T}{head} = {{")
            lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
            completion_lines = completion_trigger_lines(ritual_plan, 2)
            if completion_lines:
                lines.extend(completion_lines)
            else:
                lines.append(f"{T}{T}always = yes")
            lines.append(f"{T}}}")
    if matched:
        lines.append(f"{T}trigger_else = {{ always = no }}")
    else:
        lines.append(f"{T}always = no")
    lines.append("}")
    lines.append("")
    return lines


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

    lines.append("tv_wonder_mechanics_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in all_wonders:
        lines.append(f"{T}{T}has_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_generic_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in generic_wonders:
        lines.append(f"{T}{T}has_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_unique_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in unique_wonders:
        lines.append(f"{T}{T}has_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_has_valid_site_candidate_trigger = {")
    for idx, wonder in enumerate(all_wonders):
        head = "trigger_if" if idx == 0 else "trigger_else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}tv_wonder_can_build_{wonder['key']}_trigger = yes")
        lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = no }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_can_host_locked_wonder_trigger = {")
    for idx, wonder in enumerate(all_wonders):
        head = "trigger_if" if idx == 0 else "trigger_else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ scope:actor = {{ var:tv_wonder_locked ?= {wonder['id']} }} }}")
        lines.append(f"{T}{T}tv_wonder_location_can_host_{wonder['key']}_trigger = yes")
        lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = no }}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_selected_survey_already_cached_trigger = {")
    for idx, wonder in enumerate(all_wonders):
        head = "trigger_if" if idx == 0 else "trigger_else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{wonder['key']} }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}trigger_else = {{ always = no }}")
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
    lines.extend(
        grouped_selected_trigger(
            "tv_wonder_selected_deferred_immediate_ritual_trigger",
            all_wonders,
            mechanics,
            lambda _wonder, _style, ritual_plan: ritual_plan["mode"] == "immediate" and ritual_uses_deferred_completion(ritual_plan),
        )
    )
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
        grouped_selected_trigger(
            "tv_wonder_selected_ritual_confirmation_requirements_met_trigger",
            all_wonders,
            mechanics,
            lambda _wonder, _style, _ritual_plan: True,
            include_confirmation_script=True,
        )
    )
    lines.extend(
        grouped_selected_trigger(
            "tv_wonder_selected_ritual_monthly_listener_trigger",
            all_wonders,
            mechanics,
            lambda _wonder, _style, ritual_plan: ritual_listens_to(ritual_plan, "monthly"),
        )
    )
    lines.extend(
        grouped_selected_trigger(
            "tv_wonder_selected_ritual_ruler_death_listener_trigger",
            all_wonders,
            mechanics,
            lambda _wonder, _style, ritual_plan: ritual_listens_to(ritual_plan, "ruler_death"),
        )
    )
    lines.extend(
        grouped_selected_trigger(
            "tv_wonder_selected_ritual_pre_winning_war_listener_trigger",
            all_wonders,
            mechanics,
            lambda _wonder, _style, ritual_plan: ritual_listens_to(ritual_plan, "pre_winning_war"),
        )
    )
    lines.extend(
        grouped_selected_trigger(
            "tv_wonder_selected_ritual_ending_war_listener_trigger",
            all_wonders,
            mechanics,
            lambda _wonder, _style, ritual_plan: ritual_listens_to(ritual_plan, "ending_war"),
        )
    )
    lines.extend(grouped_selected_completion_trigger("tv_wonder_selected_ritual_completion_requirements_met_trigger", all_wonders, mechanics))

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
