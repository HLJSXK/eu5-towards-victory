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
CEREMONY_EFFECT_GENERATOR = (
    REPO_ROOT
    / "scripts"
    / "in_game"
    / "common"
    / "scripted_effects"
    / "gen_tv_wonder_ceremony_effects.py"
)
CEREMONY_EVENT_GENERATOR = (
    REPO_ROOT
    / "scripts"
    / "in_game"
    / "events"
    / "gen_tv_wonder_ceremony_events.py"
)
CEREMONY_GUI_GENERATOR = (
    REPO_ROOT
    / "scripts"
    / "in_game"
    / "gui"
    / "panels"
    / "organization"
    / "gen_tv_wonder_ceremony_cards_gui.py"
)
CEREMONY_ENGLISH_LOC_GENERATOR = (
    REPO_ROOT
    / "scripts"
    / "main_menu"
    / "localization"
    / "english"
    / "gen_tv_wonder_ceremony_l_english.py"
)
CEREMONY_CHINESE_LOC_GENERATOR = (
    REPO_ROOT
    / "scripts"
    / "main_menu"
    / "localization"
    / "simp_chinese"
    / "gen_tv_wonder_ceremony_l_simp_chinese.py"
)

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.modifiers import (
    is_value_movement_modifier,
    validate_wonder_size_base_country_modifier_rules,
    wonder_base_country_modifiers,
)
from wonder_mechanics.rituals import ceremony_styles
from wonder_mechanics.schema import validate_unique_wonder_single_site_shape
from wonder_ceremony_lib import COMPLETION_EVENT_ID, reward_effect_lines, stage_1_reward_for_wonder


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


def load_ceremony_effect_generator():
    spec = importlib.util.spec_from_file_location("wonder_ceremony_effect_generator", CEREMONY_EFFECT_GENERATOR)
    require(spec is not None and spec.loader is not None, "Could not load wonder ceremony effect generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_ceremony_event_generator():
    spec = importlib.util.spec_from_file_location("wonder_ceremony_event_generator", CEREMONY_EVENT_GENERATOR)
    require(spec is not None and spec.loader is not None, "Could not load wonder ceremony event generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_ceremony_gui_generator():
    spec = importlib.util.spec_from_file_location("wonder_ceremony_gui_generator", CEREMONY_GUI_GENERATOR)
    require(spec is not None and spec.loader is not None, "Could not load wonder ceremony GUI generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_ceremony_loc_generator(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Could not load {name}.")
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


def validate_generated_ceremony_flow(wonders: list[dict], mechanics: dict) -> None:
    ceremony_wonders = [wonder for wonder in wonders if wonder.get("is_unique") and wonder.get("ceremony") is not None]
    require(ceremony_wonders, "Expected ceremony-enabled unique wonders.")

    ceremony_effects = load_ceremony_effect_generator().generate()
    stage_1_rewards = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_grant_stage_1_reward_effect")
    stage_4_construction = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_start_stage_4_construction_effect")
    stage_8_advance = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_advance_to_stage_8_effect")
    completion_triggers = extract_trigger_block(
        load_trigger_generator().generate(),
        "tv_wonder_selected_ritual_custom_completion_requirements_met_trigger",
    )

    for wonder in ceremony_wonders:
        require(
            "stage_1_reward" not in wonder["ceremony"],
            f"{wonder['key']} must derive its stage-one reward from generic style 3 data.",
        )
        reward = stage_1_reward_for_wonder(wonder, mechanics)
        require(reward, f"{wonder['key']} needs a generic style-3 reward for ceremony stage one.")
        reward_lines = "\n".join(reward_effect_lines(reward, 2))
        reward_branch = f"limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}\n{reward_lines}"
        require(
            reward_branch in stage_1_rewards,
            f"{wonder['key']} stage one must emit its generic style-3 reward.",
        )

        dispatch_start = stage_4_construction.find(f"limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        require(dispatch_start >= 0, f"Missing stage-four construction dispatch for {wonder['key']}.")
        dispatch = stage_4_construction[dispatch_start : dispatch_start + 800]
        annex = f"building_type = building_type:tv_wonder_{wonder['mechanic_key']}_ritual_annex"
        require(annex in dispatch, f"{wonder['key']} stage four must construct its generic ritual annex.")

        ritual_id = f"{wonder['id']}01"
        completion_start = completion_triggers.find(f"var:tv_wonder_selected_ritual_id ?= {ritual_id}")
        require(completion_start >= 0, f"Missing completion trigger dispatch for {wonder['key']}.")
        completion_dispatch = completion_triggers[completion_start : completion_start + 400]
        require(
            "var:tv_wonder_ceremony_stage ?= 8" in completion_dispatch,
            f"{wonder['key']} completion trigger must wait for ceremony stage eight.",
        )

    scheduler = f"trigger_event_silently = {{ id = tv_engineering_department.{COMPLETION_EVENT_ID} days = 1 }}"
    require(scheduler in stage_8_advance, "Stage eight must schedule the hidden ceremony completion event.")

    completion_event = extract_trigger_block(
        load_ceremony_event_generator().generate(),
        f"tv_engineering_department.{COMPLETION_EVENT_ID}",
    )
    require("hidden = yes" in completion_event, "Ceremony completion event must remain hidden.")
    require(
        "tv_wonder_complete_active_ritual_effect = yes" in completion_event,
        "Ceremony completion event must use the canonical ritual finalization chain.",
    )


def validate_generated_ceremony_gui(wonders: list[dict]) -> None:
    ceremony_wonders = [wonder for wonder in wonders if wonder.get("is_unique") and wonder.get("ceremony") is not None]
    expected_flavor_key_count = len(ceremony_wonders) * 8
    fragment = load_ceremony_gui_generator().generate()

    require("GetConceptTexture" not in fragment, "Ceremony stage cards must not route icons through concepts.")
    require(fragment.count("piechart = {") == 17, "Ceremony cards need a real ready piechart and active/completed piecharts for all eight stages.")
    require(fragment.count("minimumsize = { 462 144 }") == 9, "Every nested ceremony card must keep the 462x144 size contract.")
    require("minimumsize = { 500" not in fragment, "Nested ceremony cards must not use the outer 500px width.")
    require("TV_WONDER_CEREMONY_CARD_STAGE_" not in fragment, "Ceremony cards must not fall back to static x/8 labels.")

    for icon in (
        "government",
        "topography",
        "laborers",
        "construction",
        "building_levels",
        "building",
        "art_work",
        "building_open",
    ):
        require(f"@{icon}!" in fragment, f"Ceremony cards must render the built-in @{icon}! stage icon.")
    for stage in range(1, 9):
        require(
            fragment.count(f"TV_WONDER_CEREMONY_CARD_ACTIVE_S{stage}_") == 1,
            f"Stage {stage} needs one active dynamic flavor route.",
        )
        require(
            fragment.count(f"TV_WONDER_CEREMONY_CARD_COMPLETED_S{stage}_") == 1,
            f"Stage {stage} needs one completed dynamic flavor route.",
        )

    for name, path in (
        ("wonder_ceremony_english_loc_generator", CEREMONY_ENGLISH_LOC_GENERATOR),
        ("wonder_ceremony_chinese_loc_generator", CEREMONY_CHINESE_LOC_GENERATOR),
    ):
        localization = load_ceremony_loc_generator(name, path).generate()
        require(
            localization.count("TV_WONDER_CEREMONY_CARD_ACTIVE_S") == expected_flavor_key_count,
            f"{name} must generate one active flavor key per ceremony stage.",
        )
        require(
            localization.count("TV_WONDER_CEREMONY_CARD_COMPLETED_S") == expected_flavor_key_count,
            f"{name} must generate one completed flavor key per ceremony stage.",
        )
        require("TV_WONDER_CEREMONY_CARD_STAGE_" not in localization, f"{name} must not emit static stage labels.")


def main() -> None:
    wonders, mechanics = load_all_wonder_mechanics()

    validate_wonder_size_base_country_modifier_rules(wonders, mechanics)
    validate_generated_trigger_scope_layers(wonders)
    validate_existing_unique_initialization_does_not_seed_survey_maps(wonders)
    validate_generated_ceremony_flow(wonders, mechanics)
    validate_generated_ceremony_gui(wonders)

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
