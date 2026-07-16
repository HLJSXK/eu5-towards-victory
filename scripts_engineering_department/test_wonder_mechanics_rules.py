#!/usr/bin/env python3
"""Validate scale-based Engineering Department wonder data rules."""

from collections import Counter
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "scripts_engineering_department") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))
TRIGGER_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "in_game"
    / "common"
    / "scripted_triggers"
    / "gen_tv_engineering_department_wonder_mechanics_triggers.py"
)
EFFECT_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "in_game"
    / "common"
    / "scripted_effects"
    / "gen_tv_engineering_department_wonder_mechanics_effects.py"
)
CEREMONY_EFFECT_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "in_game"
    / "common"
    / "scripted_effects"
    / "gen_tv_wonder_ceremony_effects.py"
)
CEREMONY_EVENT_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "in_game"
    / "events"
    / "gen_tv_wonder_ceremony_events.py"
)
CEREMONY_GUI_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "in_game"
    / "gui"
    / "panels"
    / "organization"
    / "gen_tv_wonder_ceremony_cards_gui.py"
)
MECHANICS_GUI_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "in_game"
    / "gui"
    / "panels"
    / "organization"
    / "gen_tv_engineering_department_wonder_mechanics_gui.py"
)
CEREMONY_ENGLISH_LOC_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "main_menu"
    / "localization"
    / "english"
    / "gen_tv_wonder_ceremony_l_english.py"
)
CEREMONY_CHINESE_LOC_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "main_menu"
    / "localization"
    / "simp_chinese"
    / "gen_tv_wonder_ceremony_l_simp_chinese.py"
)
WONDER_MECHANICS_ENGLISH_LOC_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "main_menu"
    / "localization"
    / "english"
    / "gen_tv_engineering_department_wonder_mechanics_l_english.py"
)
WONDER_MECHANICS_CHINESE_LOC_GENERATOR = (
    REPO_ROOT
    / "scripts_engineering_department" / "main_menu"
    / "localization"
    / "simp_chinese"
    / "gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py"
)
ENGINEERING_DEPARTMENT_EFFECTS = (
    REPO_ROOT
    / "src_engineering_department" / "in_game"
    / "common"
    / "scripted_effects"
    / "tv_engineering_department_effects.txt"
)

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.modifiers import (
    is_value_movement_modifier,
    validate_wonder_size_base_country_modifier_rules,
    wonder_base_country_modifiers,
)
from wonder_mechanics.rituals import (
    SUPPORTED_CEREMONY_STAGE_ICONS,
    ceremony_cost_computed_value,
    ceremony_styles,
    normalize_unique_ceremony,
    ritual_plan_for_style,
)
from wonder_mechanics.schema import validate_unique_wonder_single_site_shape
from wonder_ceremony_lib import (
    COMPLETION_EVENT_ID,
    card_icon_key,
    reward_effect_lines,
    stage_2_reward_for_wonder,
)
from wonder_localization_lib import load_engineering_department_suffix_map, load_wonder_localization_data
from towards_victory_editor_web.services.wonder_localization import (
    WONDER_DATA_REGEN_SCRIPTS,
    build_unique_ceremony_editor_state,
    ceremony_stage_cost_options,
    render_expected_localization_output,
    unique_ceremony_from_editor_state,
    validate_canonical_localization_data,
)


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


def load_mechanics_gui_generator():
    spec = importlib.util.spec_from_file_location("wonder_mechanics_gui_generator", MECHANICS_GUI_GENERATOR)
    require(spec is not None and spec.loader is not None, "Could not load wonder mechanics GUI generator.")
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


def validate_existing_unique_initialization_seeds_survey_maps(wonders: list[dict]) -> None:
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
    expected_survey_seed = {
        "tv_wonder_surveyed": 1,
        "tv_wonder_survey_scale_competence": 100,
        "tv_wonder_survey_logistics_competence": 85,
        "tv_wonder_survey_organization_competence": 85,
        "tv_wonder_survey_scale_tier": 6,
    }
    for wonder_id in existing_unique_ids:
        for map_name, value in expected_survey_seed.items():
            require(
                f"add_to_variable_map = {{ name = {map_name} key = {wonder_id} value = {value} }}" in init_block,
                f"Game-start unique wonder {wonder_id} must seed {map_name} with {value}.",
            )


def validate_generated_ceremony_flow(wonders: list[dict], mechanics: dict) -> None:
    ceremony_wonders = [wonder for wonder in wonders if wonder.get("is_unique") and wonder.get("ceremony") is not None]
    require(ceremony_wonders, "Expected ceremony-enabled unique wonders.")

    ceremony_effects = load_ceremony_effect_generator().generate()
    stage_2_rewards = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_grant_stage_2_reward_effect")
    stage_1_advance = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_advance_to_stage_1_effect")
    stage_2_advance = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_advance_to_stage_2_effect")
    stage_4_construction = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_start_stage_4_construction_effect")
    stage_8_advance = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_advance_to_stage_8_effect")
    completion_triggers = extract_trigger_block(
        load_trigger_generator().generate(),
        "tv_wonder_selected_ritual_custom_completion_requirements_met_trigger",
    )

    for wonder in ceremony_wonders:
        require(
            "stage_1_reward" not in wonder["ceremony"] and "stage_2_reward" not in wonder["ceremony"],
            f"{wonder['key']} must derive its stage-two reward from generic style 3 data.",
        )
        reward = stage_2_reward_for_wonder(wonder, mechanics)
        require(reward, f"{wonder['key']} needs a generic style-3 reward for ceremony stage two.")
        reward_lines = "\n".join(reward_effect_lines(reward, 2))
        reward_branch = f"limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}\n{reward_lines}"
        require(
            reward_branch in stage_2_rewards,
            f"{wonder['key']} stage two must emit its generic style-3 reward.",
        )
        require(
            wonder["ritual"]["country_modifier"] == {},
            f"{wonder['key']} must not keep a unique stage-eight country modifier.",
        )
        require(
            ritual_plan_for_style(wonder, mechanics, 1)["country_modifier"]
            == mechanics["generic_rituals"][wonder["mechanic_key"]]["style_1"]["country_modifier"],
            f"{wonder['key']} stage eight must derive its country modifier from generic style 1 data.",
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
    require(
        "tv_wonder_ceremony_grant_stage_2_reward_effect = yes" not in stage_1_advance,
        "Stage one must not grant the one-time reward.",
    )
    require(
        "tv_wonder_ceremony_grant_stage_2_reward_effect = yes" in stage_2_advance,
        "Stage two must grant the one-time reward.",
    )
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


def validate_generated_ceremony_autostart(wonders: list[dict]) -> None:
    ceremony_wonders = [wonder for wonder in wonders if wonder.get("is_unique") and wonder.get("ceremony") is not None]
    expected_ids = {int(wonder["id"]) for wonder in ceremony_wonders}
    require(len(expected_ids) == 121, "The shared automatic ceremony must cover exactly 121 unique wonders.")

    trigger_script = load_trigger_generator().generate()
    framework_trigger = extract_trigger_block(
        trigger_script,
        "tv_wonder_selected_unique_ceremony_framework_trigger",
    )
    id_prefix = "var:tv_wonder_locked ?= "
    actual_ids = {
        int(line.strip().removeprefix(id_prefix))
        for line in framework_trigger.splitlines()
        if line.strip().startswith(id_prefix)
    }
    require(
        actual_ids == expected_ids,
        "The automatic ceremony framework trigger must dispatch exactly to ceremony-enabled unique wonders.",
    )
    require(not {101, 102}.intersection(actual_ids), "Pharos and Hagia Sophia must remain outside the shared ceremony.")

    confirmation_trigger = extract_trigger_block(
        trigger_script,
        "tv_wonder_ceremony_ready_for_confirmation_trigger",
    )
    require(
        "NOT = { tv_wonder_selected_unique_ceremony_framework_trigger = yes }" in confirmation_trigger,
        "Shared ceremony wonders must not re-enter through the manual confirmation trigger.",
    )

    ceremony_effects = load_ceremony_effect_generator().generate()
    begin_effect = extract_trigger_block(ceremony_effects, "tv_wonder_ceremony_begin_effect")
    for line in (
        "tv_wonder_selected_unique_ceremony_framework_trigger = yes",
        "NOT = { has_variable = tv_wonder_ritual_in_progress }",
        "set_variable = { name = tv_wonder_ritual_in_progress value = 1 }",
        "set_variable = { name = tv_wonder_ceremony_locked value = 1 }",
        "set_variable = { name = tv_wonder_ceremony_stage value = 0 }",
        "set_variable = { name = tv_wonder_ceremony_quarter_month value = 0 }",
        "tv_wonder_mechanics_apply_selected_ritual_snapshot_effect = yes",
    ):
        require(line in begin_effect, f"Automatic ceremony begin effect must include: {line}")
    require(
        "tv_wonder_complete_active_ritual_effect = yes" not in begin_effect,
        "Automatic ceremony begin must not immediately complete a ritual.",
    )
    require(
        "tv_wonder_ceremony_monthly_tick_effect = yes" not in begin_effect,
        "Automatic ceremony begin must leave the first stage event to later monthly ticks.",
    )

    initializer_source = ENGINEERING_DEPARTMENT_EFFECTS.read_text(encoding="utf-8-sig")
    finish_construction = extract_trigger_block(initializer_source, "tv_wonder_finish_construction_effect")
    initializer = extract_trigger_block(initializer_source, "tv_wonder_initialize_ceremony_runtime_state_effect")
    require(
        "tv_wonder_initialize_ceremony_runtime_state_effect = yes" in finish_construction,
        "Finishing construction must initialize the automatic ceremony state.",
    )
    require(
        "tv_wonder_ceremony_begin_effect = yes" in initializer,
        "Construction initialization must begin the shared ceremony.",
    )
    require(
        initializer.index("tv_wonder_index_refresh_country_cache_effect = yes")
        < initializer.index("tv_wonder_ceremony_begin_effect = yes"),
        "Construction initialization must refresh the selected ritual cache before automatic ceremony begin.",
    )

    ritual_effects = load_effect_generator().generate_ritual_effects()
    deferred_start = extract_trigger_block(
        ritual_effects,
        "tv_wonder_mechanics_start_deferred_immediate_ritual_effect",
    )
    for wonder_id in expected_ids:
        require(
            f"var:tv_wonder_selected_ritual_id ?= {wonder_id}01" not in deferred_start,
            f"Shared ceremony wonder {wonder_id} must not use the manual deferred-immediate starter.",
        )


def validate_generated_ceremony_gui(wonders: list[dict]) -> None:
    ceremony_wonders = [wonder for wonder in wonders if wonder.get("is_unique") and wonder.get("ceremony") is not None]
    expected_flavor_key_count = len(ceremony_wonders) * 8
    fragment = load_ceremony_gui_generator().generate()
    generator_source = CEREMONY_GUI_GENERATOR.read_text(encoding="utf-8")

    require("GetConceptTexture" not in fragment, "Ceremony stage cards must not route icons through concepts.")
    require("STAGE_ICONS" not in generator_source, "Ceremony card icons must not use a global stage-number mapping.")
    require(fragment.count("piechart = {") == 16, "Ceremony cards need active/completed piecharts for all eight stages.")
    require(fragment.count("minimumsize = { 462 144 }") == 8, "Every stage card must keep the 462x144 size contract.")
    require("minimumsize = { 500" not in fragment, "Nested ceremony cards must not use the outer 500px width.")
    require("TV_WONDER_CEREMONY_READY_" not in fragment, "Automatic ceremonies must not show a ready card.")
    require("TV_WONDER_CEREMONY_CARD_STAGE_" not in fragment, "Ceremony cards must not fall back to static x/8 labels.")

    icon_sequences: dict[tuple[str, ...], str] = {}
    for wonder in ceremony_wonders:
        stages = wonder["ceremony"]["stages"]
        require(len(stages) == 8, f"{wonder['key']} must retain all eight ceremony stages.")
        icons = tuple(stage_data["icon"] for stage_data in stages)
        require(
            len(set(icons)) == len(icons),
            f"{wonder['key']} must use a distinct icon for each of its eight ceremony acts.",
        )
        require(
            icons not in icon_sequences,
            f"{wonder['key']} must not repeat {icon_sequences.get(icons)}'s full ceremony icon design.",
        )
        icon_sequences[icons] = wonder["key"]
        for stage_index, stage_data in enumerate(stages, start=1):
            icon = stage_data["icon"]
            require(
                icon in SUPPORTED_CEREMONY_STAGE_ICONS,
                f"{wonder['key']} stage {stage_index} must use a verified vanilla font icon.",
            )
            require(
                bool(stage_data["icon_rationale"].strip()),
                f"{wonder['key']} stage {stage_index} needs an icon rationale tied to its flavor.",
            )
    for stage in range(1, 9):
        require(
            fragment.count(f"TV_WONDER_CEREMONY_CARD_ACTIVE_S{stage}_") == 1,
            f"Stage {stage} needs one active dynamic flavor route.",
        )
        require(
            fragment.count(f"TV_WONDER_CEREMONY_CARD_COMPLETED_S{stage}_") == 1,
            f"Stage {stage} needs one completed dynamic flavor route.",
        )
        require(
            fragment.count(f"TV_WONDER_CEREMONY_CARD_ICON_S{stage}_") == 2,
            f"Stage {stage} needs one data-driven icon route for each piechart state.",
        )
        stage_icon_counts = Counter(
            wonder["ceremony"]["stages"][stage - 1]["icon"] for wonder in ceremony_wonders
        )
        most_common_icon, most_common_count = stage_icon_counts.most_common(1)[0]
        require(
            most_common_count * 100 <= len(ceremony_wonders) * 25,
            f"Stage {stage} overuses @{most_common_icon}! ({most_common_count}/{len(ceremony_wonders)}); "
            "select icons from each wonder's actual ritual flavor instead of a global stage pattern.",
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
        require(
            localization.count("TV_WONDER_CEREMONY_CARD_ICON_S") == expected_flavor_key_count,
            f"{name} must generate one data-driven icon key per ceremony stage.",
        )
        for wonder in ceremony_wonders:
            for stage_index, stage_data in enumerate(wonder["ceremony"]["stages"], start=1):
                expected_icon_line = f' {card_icon_key(stage_index, wonder["id"])}:0 "@{stage_data["icon"]}!"'
                require(
                    expected_icon_line in localization,
                    f"{name} must render {wonder['key']} stage {stage_index}'s selected icon.",
                )
        require("TV_WONDER_CEREMONY_READY_" not in localization, f"{name} must not emit ready-card localization.")
        require("TV_WONDER_CEREMONY_CARD_STAGE_" not in localization, f"{name} must not emit static stage labels.")

    hold_buttons = load_mechanics_gui_generator().generate()
    require(
        "TV_ENGINEERING_HOLD_CEREMONY_BUTTON" in hold_buttons,
        "Generic (non-unique) wonders must still get the shared manual confirm button "
        "for their player-chosen ceremony style.",
    )
    for action_name in (
        "tv_wonder_confirm_ceremony_scaled_gold",
        "tv_wonder_confirm_ceremony_prestige",
    ):
        require(
            f'action_name = "{action_name}"' in hold_buttons,
            f"The shared {action_name} confirmation button must be emitted for generic wonders.",
        )
    require(
        hold_buttons.count("tv_wonder_locked_is_unique") >= 3,
        "The three shared generic confirm buttons must each gate on tv_wonder_locked_is_unique "
        "so they never overlap with Pharos/Hagia's bespoke buttons.",
    )
    for label, wonder_id in (
        ("TV_ENGINEERING_PHAROS_BUILD_BUTTON", 101),
        ("TV_ENGINEERING_HAGIA_START_BUTTON", 102),
    ):
        require(label in hold_buttons, f"{label} must remain available for its bespoke ritual.")
        require(
            f"(CFixedPoint){wonder_id}.0" in hold_buttons,
            f"{label} must remain limited to wonder {wonder_id}.",
        )


def validate_unique_ceremony_editor_support(wonders: list[dict]) -> None:
    ceremony_wonders = [
        wonder
        for wonder in wonders
        if wonder.get("is_unique") and wonder.get("ceremony") is not None
    ]
    require(ceremony_wonders, "Expected ceremony-enabled unique wonders.")

    for wonder in ceremony_wonders:
        state = build_unique_ceremony_editor_state(wonder["ceremony"], cost_type_options=[])
        parsed = unique_ceremony_from_editor_state(state, context=f"{wonder['key']}.ceremony")
        normalized = normalize_unique_ceremony({**wonder, "ceremony": parsed})
        require(
            normalized == wonder["ceremony"],
            f"{wonder['key']} ceremony must round-trip through the editor state.",
        )

    dome_of_the_rock = next(wonder for wonder in ceremony_wonders if wonder["id"] == 103)
    editor_state = build_unique_ceremony_editor_state(
        dome_of_the_rock["ceremony"],
        cost_type_options=ceremony_stage_cost_options(),
    )
    require(len(editor_state["stages"]) == 8, "The ceremony editor must render all eight fixed stages.")
    require(
        editor_state["stages"][0]["cost"]["options"],
        "The ceremony editor must expose the restricted stage cost vocabulary.",
    )
    require(
        editor_state["stages"][0]["icon"] == dome_of_the_rock["ceremony"]["stages"][0]["icon"],
        "The ceremony editor must preserve each stage's data-owned icon.",
    )
    require(
        editor_state["stages"][0]["icon_rationale"] == dome_of_the_rock["ceremony"]["stages"][0]["icon_rationale"],
        "The ceremony editor must preserve each stage's icon rationale.",
    )

    editor_state["stages"][0]["title_en"] = "Editor round-trip stage"
    editor_state["stages"][0]["icon"] = "government"
    editor_state["stages"][0]["icon_rationale"] = "Represents the public decree beginning the ceremony."
    saved_ceremony = normalize_unique_ceremony(
        {
            **dome_of_the_rock,
            "ceremony": unique_ceremony_from_editor_state(
                json.dumps(editor_state, ensure_ascii=False),
                context="unique_dome_of_the_rock.ceremony",
            ),
        }
    )
    require(
        saved_ceremony["stages"][0]["title_en"] == "Editor round-trip stage",
        "The ceremony editor must preserve edited stage text through normalization.",
    )
    require(
        saved_ceremony["stages"][0]["icon"] == "government"
        and saved_ceremony["stages"][0]["icon_rationale"] == "Represents the public decree beginning the ceremony.",
        "The ceremony editor must preserve edited stage icon metadata through normalization.",
    )

    for wonder_id in (101, 102):
        bespoke_wonder = next(wonder for wonder in wonders if wonder["id"] == wonder_id)
        require(
            bespoke_wonder["ceremony"] is None,
            f"Bespoke unique wonder {wonder_id} must remain outside the shared ceremony.",
        )

    invalid_state = deepcopy(editor_state)
    invalid_state["stages"] = invalid_state["stages"][:-1]
    try:
        normalize_unique_ceremony(
            {
                **ceremony_wonders[0],
                "ceremony": unique_ceremony_from_editor_state(invalid_state, context="invalid ceremony"),
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("The ceremony editor must reject fewer than eight stages.")

    recomputed_cost_state = deepcopy(editor_state)
    cost_type = recomputed_cost_state["stages"][0]["cost"]["options"][0]["value"]
    catalog, _, entry_id = cost_type.partition(":")
    recomputed_cost_state["stages"][0]["cost"]["rows"] = [{"type": cost_type, "value": "999999"}]
    recomputed_ceremony = unique_ceremony_from_editor_state(
        recomputed_cost_state,
        context="recomputed ceremony cost",
    )
    require(
        recomputed_ceremony["stages"][0]["cost"]
        == [
            {
                "catalog": catalog,
                "type": entry_id,
                "value": ceremony_cost_computed_value(catalog, entry_id, 1),
            }
        ],
        "The ceremony editor must recompute costs from catalog, type, and stage instead of trusting the value cell.",
    )

    invalid_ceremony = deepcopy(recomputed_ceremony)
    invalid_ceremony["stages"][0]["cost"][0]["value"] += 1
    try:
        normalize_unique_ceremony(
            {
                **dome_of_the_rock,
                "ceremony": invalid_ceremony,
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Ceremony normalization must reject a cost value that drifts from its computed magnitude.")

    invalid_state = deepcopy(editor_state)
    invalid_state["stages"][0]["icon"] = "not_a_real_font_icon"
    try:
        normalize_unique_ceremony(
            {
                **ceremony_wonders[0],
                "ceremony": unique_ceremony_from_editor_state(invalid_state, context="invalid ceremony"),
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError("The ceremony editor must reject an unknown font icon.")

    ceremony_regen_scripts = (
        "scripts_engineering_department/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_mechanics_modifiers.py",
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "scripts_engineering_department/in_game/common/customizable_localization/gen_tv_wonder_ceremony_options.py",
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_country_modifiers.py",
        "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_local_modifiers.py",
        "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ceremony_effects.py",
        "scripts_engineering_department/in_game/events/gen_tv_wonder_ceremony_events.py",
        "scripts_engineering_department/main_menu/localization/english/gen_tv_wonder_ceremony_l_english.py",
        "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_wonder_ceremony_l_simp_chinese.py",
        "scripts_engineering_department/in_game/gui/panels/organization/gen_tv_wonder_ceremony_cards_gui.py",
        "scripts_engineering_department/in_game/gui/panels/organization/merge_tv_wonder_ceremony_cards_gui.py",
    )
    for script in ceremony_regen_scripts:
        require(script in WONDER_DATA_REGEN_SCRIPTS, f"Ceremony edits must regenerate {script}.")
    require(
        WONDER_DATA_REGEN_SCRIPTS.index(
            "scripts_engineering_department/in_game/gui/panels/organization/merge_tv_engineering_department_wonder_mechanics_gui.py"
        )
        < WONDER_DATA_REGEN_SCRIPTS.index(ceremony_regen_scripts[-1]),
        "The ceremony card merge must run after the main mechanics GUI merge.",
    )


def validate_editor_localization_ignores_design_only_english(wonders: list[dict], mechanics: dict) -> None:
    localization_data = load_wonder_localization_data()
    required_keys = validate_canonical_localization_data(
        wonders,
        mechanics,
        load_engineering_department_suffix_map(),
        localization_data,
    )
    design_only_english = set(localization_data["english"]) - set(localization_data["simp_chinese"])
    require(design_only_english, "Expected Harness design-only English localization inventory.")
    require(
        design_only_english.isdisjoint(required_keys),
        "Design-only English localization must not be treated as required gameplay/editor text.",
    )


def validate_editor_localization_rendering_matches_generators() -> None:
    localization_data = load_wonder_localization_data()
    for language, name, path in (
        ("english", "wonder_mechanics_english_loc_generator", WONDER_MECHANICS_ENGLISH_LOC_GENERATOR),
        ("simp_chinese", "wonder_mechanics_chinese_loc_generator", WONDER_MECHANICS_CHINESE_LOC_GENERATOR),
    ):
        actual = load_ceremony_loc_generator(name, path).generate()
        expected = render_expected_localization_output(language, localization_data)
        require(actual == expected, f"Editor localization rendering must match {name}.")


def main() -> None:
    wonders, mechanics = load_all_wonder_mechanics()

    validate_wonder_size_base_country_modifier_rules(wonders, mechanics)
    validate_generated_trigger_scope_layers(wonders)
    validate_existing_unique_initialization_seeds_survey_maps(wonders)
    validate_generated_ceremony_flow(wonders, mechanics)
    validate_generated_ceremony_autostart(wonders)
    validate_generated_ceremony_gui(wonders)
    validate_unique_ceremony_editor_support(wonders)
    validate_editor_localization_ignores_design_only_english(wonders, mechanics)
    validate_editor_localization_rendering_matches_generators()

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
