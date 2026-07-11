"""Generate the shared Unique Wonder Ceremony scripted_effects.

Wonder-id-generic mechanics (monthly tick, cost payment, stage advance) live as
a handful of shared effects; only the stage-1 one-time reward and the stage-4
"start building the real final building" dispatch branch per wonder id, matching
the existing 121-way `var:tv_wonder_locked ?= <id>` idiom already used in
tv_wonder_finalization_effects.txt.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_ceremony_lib import (  # noqa: E402
    COST_TYPE_IDS,
    COST_TYPE_PAY_LINES,
    STAGE_COUNT,
    T,
    ceremony_wonders,
    render_header,
    reward_effect_lines,
    script_rel,
    stage_event_id,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_wonder_ceremony_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_wonder_ceremony_effects.py"
DATA_REL = "data/unique_wonders.yaml"


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


def append_pay_cost(lines: list[str]) -> None:
    lines.append("tv_wonder_ceremony_pay_cost_effect = {")
    for index, (cost_type, cost_lines) in enumerate(COST_TYPE_PAY_LINES.items()):
        head = "if" if index == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_selected_ritual_cost_type ?= {COST_TYPE_IDS[cost_type]} }}")
        lines.extend(cost_lines)
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_stage_1_reward_dispatch(lines: list[str], wonders: list[dict]) -> None:
    lines.append("tv_wonder_ceremony_grant_stage_1_reward_effect = {")
    first = True
    for wonder in wonders:
        reward = wonder["ceremony"]["stage_1_reward"]
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
        building = wonder["final_buildings"][1]
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
        lines.append(f"{T}tv_wonder_ceremony_pay_cost_effect = yes")
        lines.append(f"{T}set_variable = {{ name = tv_wonder_ceremony_stage value = {stage} }}")
        lines.append(f"{T}set_variable = {{ name = tv_wonder_ceremony_quarter_month value = 0 }}")
        if stage == 1:
            lines.append(f"{T}tv_wonder_ceremony_grant_stage_1_reward_effect = yes")
        if stage == 4:
            lines.append(f"{T}tv_wonder_ceremony_start_stage_4_construction_effect = yes")
        lines.append("}")
        lines.append("")


def generate() -> str:
    wonders = ceremony_wonders()
    lines = render_header(SCRIPT_REL, DATA_REL, script_rel(OUT_FILE))
    append_monthly_tick(lines)
    append_pay_cost(lines)
    append_stage_1_reward_dispatch(lines, wonders)
    append_stage_4_construction_dispatch(lines, wonders)
    append_advance_stage_effects(lines)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("﻿" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
