"""Static regression checks for the generated Victory Path task system."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.victory_task_codegen import (
    PATH_IDS,
    SLOTS,
    _extract_top_level_block,
    action_name,
    all_tasks,
    load_data,
    refresh_effect,
    slot_prefix,
)


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8-sig")


def next_fixed_threshold(thresholds: list[int], claimed_index: int, current: float) -> tuple[int, int] | None:
    for index, threshold in enumerate(thresholds, 1):
        if index > claimed_index and current < threshold:
            return index, threshold
    return None


def main() -> None:
    data = load_data()
    tasks = all_tasks(data)
    assert len(tasks) == 77
    assert [len(data["paths"][path_id]["tasks"]) for path_id in PATH_IDS] == [10, 10, 11, 9, 13, 24]
    assert data["national_special"]["tasks"] == []
    assert {task["event_id"] for task in tasks if task.get("event_id")} == {1, 2, 5, 8, 18, 19, 20, 29, 30}

    artwork_task = next(task for task in tasks if task["id"] == 5001)
    assert artwork_task["thresholds"] == list(range(10, 201, 10))
    assert next_fixed_threshold([100, 200, 300], 0, 99) == (1, 100)
    assert next_fixed_threshold([100, 200, 300], 1, 150) == (2, 200)
    assert next_fixed_threshold([100, 200, 300], 2, 300) is None

    effects = read("src/in_game/common/scripted_effects/tv_victory_path_task_effects.txt")
    actions = read("src/in_game/common/generic_actions/tv_victory_path_task_actions.txt")
    ai_list = read("src/in_game/common/generic_action_ai_lists/tv_victory_path_task_actions_list.txt")
    triggers = read("src/in_game/common/scripted_triggers/tv_victory_path_task_triggers.txt")
    gui = read("src/in_game/gui/panels/situation/tv_victory_situation.gui")
    task_on_actions = read("src/in_game/common/on_action/tv_victory_path_task_on_actions.txt")
    pulse_registry = read("data/pulse_registry.yaml")
    pulse_bridge = read("src/in_game/common/on_action/tv_pulse_bridges.txt")

    action_ids = re.findall(r"(?m)^(tv_victory_claim_[a-z0-9_]+)\s*=\s*\{", actions)
    assert len(action_ids) == 18 and len(set(action_ids)) == 18
    assert actions.count("ai_tick = never") == 18
    assert actions.count("automation_tick = never") == 18
    assert "potential = { always = no }" in ai_list

    monthly = _extract_top_level_block(effects, "tv_victory_path_tasks_monthly_pulse_effect")
    assert "tv_victory_path_tasks_refresh_conquest_slot_1_effect" in monthly
    assert "tv_conquest_task_slot_1_id ?= 1101" not in monthly
    assert "tv_science_task_slot_1_id ?= 6001" not in monthly
    yearly = _extract_top_level_block(effects, "tv_victory_path_tasks_yearly_pulse_effect")
    assert yearly.count("?= 6001") == 3

    for path_id in PATH_IDS:
        assert effects.count(f"change_variable = {{ name = tv_{path_id}_tree_points add = 1 }}") == 3
        init = _extract_top_level_block(effects, f"tv_victory_path_tasks_initialize_{path_id}_effect")
        assert f"set_variable = {{ name = tv_{path_id}_tree_points value = 0 }}" in init
        assert f"tv_victory_path_tasks_refresh_all_{path_id}_effect = yes" in init
        for slot in SLOTS:
            prefix = slot_prefix(path_id, slot)
            claim = _extract_top_level_block(effects, f"tv_victory_path_tasks_claim_{path_id}_slot_{slot}_effect")
            assert claim.count(f"{refresh_effect(path_id, slot)} = yes") == 1
            assert f"tv_victory_path_tasks_refresh_all_{path_id}_effect" not in claim
            for other in SLOTS:
                if other != slot:
                    assert f"NOT = {{ var:{slot_prefix(path_id, other)}_id ?=" in effects
            assert f"Country.Custom('{prefix}_icon')" in gui
            assert f"Country.Custom('{prefix}_name')" in gui
            assert f"ShowTriggerConditions('{prefix}_display_trigger', PlayerScope.Self)" in gui
            assert f'action_name = "{action_name(path_id, slot)}"' in gui

        tree_marker = f"tv_victory_{path_id}_tree.dds"
        task_marker = f"Country.Custom('tv_{path_id}_task_slot_1_icon')"
        overview_marker = f"TV_{path_id.upper()}_OVERVIEW_TITLE"
        assert gui.index(tree_marker) < gui.index(task_marker) < gui.index(overview_marker)

    assert gui.count('texture = "gfx/interface/icons/text_icons/trigger_yes.dds"') == 18
    assert gui.count("_task_slot_") > 100
    assert "random_culture_group" not in effects
    assert effects.count("every_culture_group = {") >= 3
    art_quality_metric = _extract_top_level_block(effects, "tv_victory_task_refresh_metric_best_art_quality_pct_effect")
    assert "value = prev.art_quality" in art_quality_metric
    assert "multiply = 100" not in art_quality_metric
    assert "root.art_quality >= 80" in effects
    assert "union ?= { country_is_senior_partner = { country = root } }" in triggers
    assert "any_location_in_the_world" in _extract_top_level_block(
        triggers, "tv_victory_task_1101_current_condition"
    )
    for slot in SLOTS:
        culture_group_display = _extract_top_level_block(
            triggers, f"tv_conquest_task_slot_{slot}_display_trigger"
        )
        assert "any_location_in_the_world" in culture_group_display
    assert "tv_local_exhibition_last_rating" in effects
    assert "tv_victory_path_task_national_special_historical_tag_eligible" in triggers
    assert "has_or_had_tag = $tag$" in triggers

    assert "tv_victory_path_tasks_monthly_pulse" in task_on_actions
    assert "tv_victory_path_tasks_yearly_pulse" in task_on_actions
    assert "tv_victory_tree_points_monthly_pulse" not in pulse_registry
    assert "tv_victory_tree_points_monthly_pulse" not in pulse_bridge
    assert "tv_victory_path_tasks_on_location_changed_owner" in pulse_bridge
    assert "tv_victory_path_tasks_on_international_organization_changed_leader" not in pulse_bridge
    assert "tv_victory_path_tasks_on_io_leader_changed" in pulse_bridge

    victory_effects = read("src/in_game/common/scripted_effects/towards_victory_effects.txt")
    tree_effects = read("src/in_game/common/scripted_effects/tv_victory_tree_effects.txt")
    assert "tree_points value = 1000" not in victory_effects
    assert "tv_victory_tree_points_monthly_pulse" not in tree_effects
    for path_id in PATH_IDS:
        assert f"tv_victory_path_tasks_initialize_{path_id}_effect = yes" in victory_effects
        assert f"tv_victory_path_tasks_refresh_all_{path_id}_effect = yes" not in tree_effects

    price_events = read("src/in_game/events/tv_victory_path_task_price_events.txt")
    for event_id in (1, 2, 5, 8, 18, 19, 20, 29, 30):
        assert price_events.count(f"tv_victory_task_prices_{event_id}_callback_effect = yes") == 1
    for event_id in (1, 2, 8):
        callback = _extract_top_level_block(effects, f"tv_victory_task_prices_{event_id}_callback_effect")
        guarded = _extract_top_level_block(callback, "if")
        assert f"has_global_variable = tv_victory_task_price_{event_id}_triggered" in guarded
        assert "every_country = {" in guarded
    prices_30 = _extract_top_level_block(price_events, "prices.30")
    assert "OR = {\n\t\t\treligion.group = religion_group:christian\n\t\t\treligion.group = religion_group:muslim" in prices_30

    buildings = read("src/in_game/common/building_types/tv_victory_path_task_buildings.txt")
    assert "tv_victory_task_build_library_callback_effect = yes" in buildings
    assert "tv_victory_task_build_university_callback_effect = yes" in buildings
    assert "tv_victory_task_callback_local_exhibition_ended_effect = yes" in read(
        "src/in_game/common/scripted_effects/tv_arts_exhibition_effects.txt"
    )
    assert "tv_victory_task_callback_arts_exchange_started_effect = yes" in read(
        "src/in_game/common/scripted_effects/tv_arts_exhibition_effects.txt"
    )
    assert "tv_victory_task_callback_concentrated_research_completed_effect = yes" in read(
        "src/in_game/common/scripted_effects/tv_research_subprocess_effects.txt"
    )
    debate_effects = read("src/in_game/common/scripted_effects/tv_academy_philosophy_debate_effects.txt")
    assert debate_effects.count("tv_victory_task_callback_academy_debate_resolved_effect = yes") == 2

    italian_callback = _extract_top_level_block(
        effects, "tv_victory_task_italian_wars_ended_callback_effect"
    )
    assert italian_callback.count("total_locations_owned >= 200") == 7
    assert "tv_victory_task_mark_4105_complete_effect = yes" in italian_callback
    generated_destroy = _extract_top_level_block(effects, "destroy_all_italian_leagues")
    vanilla_destroy = _extract_top_level_block(
        read("reference_game_files/game/in_game/common/scripted_effects/international_organization_effects.txt"),
        "destroy_all_italian_leagues",
    )
    assert generated_destroy.replace(
        "\n\ttv_victory_task_italian_wars_ended_callback_effect = yes", "", 1
    ) == vanilla_destroy

    print("[OK] Victory Path task static checks passed")


if __name__ == "__main__":
    main()
