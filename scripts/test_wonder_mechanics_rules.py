#!/usr/bin/env python3
"""Validate scale-based Engineering Department wonder data rules."""

import importlib.util
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
TRIGGER_GENERATOR = (
    REPO_ROOT
    / "scripts"
    / "in_game"
    / "common"
    / "scripted_triggers"
    / "gen_tv_engineering_department_wonder_mechanics_triggers.py"
)
EFFECT_GENERATOR = (
    REPO_ROOT
    / "scripts"
    / "in_game"
    / "common"
    / "scripted_effects"
    / "gen_tv_engineering_department_wonder_mechanics_effects.py"
)

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.modifiers import (
    is_value_movement_modifier,
    validate_wonder_size_base_country_modifier_rules,
    wonder_base_country_modifiers,
)
from wonder_mechanics.rituals import ceremony_styles
from wonder_mechanics.schema import validate_unique_wonder_single_site_shape


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_trigger_generator():
    spec = importlib.util.spec_from_file_location("wonder_mechanics_trigger_generator", TRIGGER_GENERATOR)
    require(spec is not None and spec.loader is not None, "Could not load wonder mechanics trigger generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_effect_generator():
    spec = importlib.util.spec_from_file_location("wonder_mechanics_effect_generator", EFFECT_GENERATOR)
    require(spec is not None and spec.loader is not None, "Could not load wonder mechanics effect generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extract_trigger_block(script: str, name: str) -> str:
    marker = f"{name} = {{"
    start = script.find(marker)
    require(start >= 0, f"Missing generated trigger {name}.")
    depth = 0
    for index in range(start, len(script)):
        char = script[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return script[start : index + 1]
    raise AssertionError(f"Generated trigger {name} is not closed.")


def validate_generated_trigger_scope_layers(wonders: list[dict]) -> None:
    trigger_script = load_trigger_generator().generate()
    require(
        "tv_wonder_can_start_project_" not in trigger_script,
        "Generator must not emit country-level start-project target pre-scans for survey selectors.",
    )
    for wonder in wonders:
        key = wonder["key"]
        country_gate = f"tv_wonder_country_has_{key}_project_or_final_trigger"
        location_host = extract_trigger_block(trigger_script, f"tv_wonder_location_can_host_{key}_trigger")
        require(
            country_gate not in location_host,
            f"Location host trigger for {key} must not contain country-level uniqueness gates.",
        )
        require(
            "scope:actor" not in location_host,
            f"Location host trigger for {key} must not depend on actor scope.",
        )

        can_build = extract_trigger_block(trigger_script, f"tv_wonder_can_build_{key}_trigger")
        if wonder["size"] == "small":
            require(country_gate not in can_build, f"Small can-build trigger for {key} should not be unique-gated.")
        else:
            require(country_gate in can_build, f"{key} can-build trigger must enforce country uniqueness.")

        if int(wonder.get("initial_level") or 0) > 0:
            expandable = extract_trigger_block(
                trigger_script,
                f"tv_wonder_location_has_{key}_expandable_final_building_trigger",
            )
            require(
                f"is_key_in_variable_map = {{ name = tv_wonder_surveyed target = {int(wonder['id'])} }}"
                in expandable,
                f"{key} initial final building must remain expandable before its first survey.",
            )


def validate_existing_unique_initialization_does_not_seed_survey_maps(wonders: list[dict]) -> None:
    location_display_script = load_effect_generator().generate_location_display_effects()
    init_block = extract_trigger_block(
        location_display_script,
        "tv_wonder_initialize_existing_unique_wonders_effect",
    )
    existing_unique_ids = [
        int(wonder["id"])
        for wonder in wonders
        if wonder.get("is_unique") and int(wonder.get("initial_level") or 0) > 0
    ]
    require(existing_unique_ids, "Expected at least one game-start unique wonder.")
    for wonder_id in existing_unique_ids:
        for map_name in (
            "tv_wonder_surveyed",
            "tv_wonder_survey_scale_competence",
            "tv_wonder_survey_logistics_competence",
            "tv_wonder_survey_organization_competence",
            "tv_wonder_survey_scale_tier",
        ):
            require(
                f"name = {map_name} key = {wonder_id}" not in init_block,
                f"Game-start unique wonder {wonder_id} must not seed {map_name}.",
            )


def main() -> None:
    wonders, mechanics = load_all_wonder_mechanics()

    validate_wonder_size_base_country_modifier_rules(wonders, mechanics)
    validate_generated_trigger_scope_layers(wonders)
    validate_existing_unique_initialization_does_not_seed_survey_maps(wonders)

    small_violations: list[str] = []
    medium_large_non_value: list[str] = []
    for wonder in wonders:
        modifiers = wonder_base_country_modifiers(wonder, mechanics, 1)
        non_value = [key for key in modifiers if not is_value_movement_modifier(key)]
        if wonder["size"] == "small":
            if non_value:
                small_violations.append(f"{wonder['key']}: {', '.join(sorted(non_value))}")
        else:
            medium_large_non_value.extend(f"{wonder['key']}.{key}" for key in non_value)

    require(
        not small_violations,
        "Small wonders have non-value-movement base country modifiers: "
        + "; ".join(small_violations),
    )
    require(
        bool(medium_large_non_value),
        "Test data should include at least one medium/large non-value base country modifier "
        "so the unrestricted side of the rule is covered.",
    )

    unique_wonders = [wonder for wonder in wonders if wonder.get("is_unique")]
    require(unique_wonders, "Expected unique wonder data to be loaded.")
    for wonder in unique_wonders:
        validate_unique_wonder_single_site_shape(wonder)
        require(ceremony_styles(wonder) == [1], f"{wonder['key']} must have exactly one ceremony style.")
        require(bool(wonder.get("location")), f"{wonder['key']} must have a fixed location.")

    pirate_port = next(wonder for wonder in wonders if wonder["key"] == "pirate_port")
    require(pirate_port["size"] == "medium", "Pirate Port must remain a medium wonder.")
    pirate_base = wonder_base_country_modifiers(pirate_port, mechanics, 1)
    require(
        {
            "can_hire_privateers",
            "hire_privateer_cost_modifier",
            "privateer_maintenance_cost_modifier",
            "privateer_durability",
            "monthly_towards_naval",
        }.issubset(pirate_base),
        "Pirate Port privateer country effects should live in base_modifiers as a medium wonder.",
    )
    pirate_ritual = mechanics["generic_rituals"]["pirate_port"]["style_1"]["country_modifier"]
    require(
        {"can_hire_privateers", "privateer_durability"}.isdisjoint(pirate_ritual),
        "Pirate Port style 1 ritual should not duplicate base privateer enabling or durability.",
    )

    print(
        "[OK] Wonder mechanics scale rules validated: "
        f"{len(wonders)} wonders, {len(unique_wonders)} unique wonders."
    )


if __name__ == "__main__":
    main()
