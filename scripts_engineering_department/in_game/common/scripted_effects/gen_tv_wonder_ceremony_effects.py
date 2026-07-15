"""Generate the shared Unique Wonder Ceremony scripted_effects.

The monthly tick and stage-advance skeleton are wonder-id-generic shared effects;
the stage cost (data/unique_wonders.yaml ceremony.stages[i].cost, one authored
cost per stage), the stage-2 one-time reward, and the stage-4 generic ritual-annex
construction branch each dispatch per wonder id, matching the existing
121-way `var:tv_wonder_locked ?= <id>` idiom already used in
tv_wonder_finalization_effects.txt.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_ceremony_lib import (  # noqa: E402
    COMPLETION_EVENT_ID,
    STAGE_COUNT,
    T,
    ceremony_cost_effect_lines,
    ceremony_wonders_and_mechanics,
    render_header,
    reward_effect_lines,
    script_rel,
    stage_2_reward_for_wonder,
    stage_event_id,
)

OUT_FILE = REPO_ROOT / "src_engineering_department" / "in_game" / "common" / "scripted_effects" / "tv_wonder_ceremony_effects.txt"
SCRIPT_REL = "scripts_engineering_department/in_game/common/scripted_effects/gen_tv_wonder_ceremony_effects.py"
DATA_REL = "data/unique_wonders.yaml + data/wonder_generic_rituals.yaml + data/cost_reward_units.yaml"


def append_begin_effect(lines: list[str]) -> None:
    """Start the shared ceremony at stage zero without consuming a monthly tick.

    Construction completion invokes this after the selected ritual cache has been
    populated.  Leaving the progress effect untouched here makes the first
    stage transition occur only after three subsequent monthly pulses.
    """
    lines.append("tv_wonder_ceremony_begin_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}tv_wonder_selected_unique_ceremony_framework_trigger = yes")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = tv_wonder_ritual_in_progress }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_mechanics_clear_selected_ritual_runtime_effect = yes")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ritual_in_progress value = 1 }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_locked value = 1 }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_stage value = 0 }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_quarter_month value = 0 }}")
    lines.append(f"{T}{T}tv_wonder_mechanics_apply_selected_ritual_snapshot_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_monthly_tick(lines: list[str]) -> None:
    lines.append("tv_wonder_ceremony_monthly_tick_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ NOT = {{ has_variable = tv_wonder_ceremony_stage }} }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_stage value = 0 }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ceremony_quarter_month value = 0 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_ceremony_stage < {STAGE_COUNT} }}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_ceremony_quarter_month add = 1 }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:tv_wonder_ceremony_quarter_month >= 3 }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_ceremony_quarter_month value = 0 }}")
    for stage in range(1, STAGE_COUNT + 1):
        head = "if" if stage == 1 else "else_if"
        lines.append(f"{T}{T}{T}{head} = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ var:tv_wonder_ceremony_stage ?= {stage - 1} }}")
        lines.append(
            f"{T}{T}{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{stage_event_id(stage)} days = 1 }}"
        )
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_stage_cost_dispatch(lines: list[str], wonders: list[dict]) -> None:
    """One pay-cost effect per stage, dispatched by wonder id, so each of the 8 ceremony
    stages charges that wonder's own authored data/unique_wonders.yaml
    ceremony.stages[stage-1].cost instead of a single cost repeated across all 8 stages."""
    for stage in range(1, STAGE_COUNT + 1):
        lines.append(f"tv_wonder_ceremony_pay_stage_{stage}_cost_effect = {{")
        first = True
        for wonder in wonders:
            cost = wonder["ceremony"]["stages"][stage - 1]["cost"]
            head = "if" if first else "else_if"
            first = False
            lines.append(f"{T}{head} = {{")
            lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
            lines.extend(ceremony_cost_effect_lines(cost, 2, stage_index=stage))
            lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")


def append_stage_2_reward_dispatch(lines: list[str], wonders: list[dict], mechanics: dict) -> None:
    lines.append("tv_wonder_ceremony_grant_stage_2_reward_effect = {")
    first = True
    for wonder in wonders:
        reward = stage_2_reward_for_wonder(wonder, mechanics)
        if not reward:
            continue
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.extend(reward_effect_lines(reward, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_stage_4_construction_dispatch(lines: list[str], wonders: list[dict]) -> None:
    lines.append("tv_wonder_ceremony_start_stage_4_construction_effect = {")
    first = True
    for wonder in wonders:
        building = f"tv_wonder_{wonder['mechanic_key']}_ritual_annex"
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}var:tv_wonder_site ?= {{")
        lines.append(f"{T}{T}{T}if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ NOT = {{ has_building = building_type:{building} }} }}")
        lines.append(
            f"{T}{T}{T}{T}construct_building = {{ building_type = building_type:{building} "
            'cost_multiplier = 0 cost_multiplier_reason = "game_concept_event" instant = yes }'
        )
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_advance_stage_effects(lines: list[str]) -> None:
    for stage in range(1, STAGE_COUNT + 1):
        lines.append(f"tv_wonder_ceremony_advance_to_stage_{stage}_effect = {{")
        lines.append(f"{T}tv_wonder_ceremony_pay_stage_{stage}_cost_effect = yes")
        lines.append(f"{T}set_variable = {{ name = tv_wonder_ceremony_stage value = {stage} }}")
        lines.append(f"{T}set_variable = {{ name = tv_wonder_ceremony_quarter_month value = 0 }}")
        if stage == 2:
            lines.append(f"{T}tv_wonder_ceremony_grant_stage_2_reward_effect = yes")
        if stage == 4:
            lines.append(f"{T}tv_wonder_ceremony_start_stage_4_construction_effect = yes")
        if stage == STAGE_COUNT:
            lines.append(
                f"{T}trigger_event_silently = {{ id = tv_engineering_department.{COMPLETION_EVENT_ID} days = 1 }}"
            )
        lines.append("}")
        lines.append("")


def generate() -> str:
    wonders, mechanics = ceremony_wonders_and_mechanics()
    lines = render_header(SCRIPT_REL, DATA_REL, script_rel(OUT_FILE))
    append_begin_effect(lines)
    append_monthly_tick(lines)
    append_stage_cost_dispatch(lines, wonders)
    append_stage_2_reward_dispatch(lines, wonders, mechanics)
    append_stage_4_construction_dispatch(lines, wonders)
    append_advance_stage_effects(lines)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("﻿" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
