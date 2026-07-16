"""Generate the 8 shared Unique Wonder Ceremony events.

One event per ceremony stage (namespace tv_engineering_department, ids
10000-10007). The mechanical body (trigger/options/effect calls) is identical
across all 121 non-bespoke unique wonders; only title/desc vary per active
wonder, expressed with the vanilla `first_valid`/`triggered_desc` idiom (see
reference_game_files/game/in_game/events/hre.txt and government_reforms.txt)
keyed on `var:tv_wonder_locked`.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_ceremony_lib import (  # noqa: E402
    CEREMONY_IMAGE,
    NAMESPACE,
    STAGE_COUNT,
    T,
    ceremony_wonders,
    decline_option_key,
    desc_key,
    pay_option_key,
    render_header,
    stage_event_id,
    title_key,
)

OUT_FILE = REPO_ROOT / "src_engineering_department" / "in_game" / "events" / "tv_wonder_ceremony_events.txt"
SCRIPT_REL = "scripts_engineering_department/in_game/events/gen_tv_wonder_ceremony_events.py"
DATA_REL = "data/unique_wonders.yaml"


def append_first_valid_block(lines: list[str], field: str, stage: int, wonders: list[dict], key_fn) -> None:
    lines.append(f"{T}{field} = {{")
    lines.append(f"{T}{T}first_valid = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}{T}triggered_desc = {{")
        lines.append(f"{T}{T}{T}{T}trigger = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}{T}{T}desc = {key_fn(stage, wonder['id'])}")
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")


def append_event(lines: list[str], stage: int, wonders: list[dict]) -> None:
    event_id = stage_event_id(stage)
    lines.append(f"# -- {NAMESPACE}.{event_id} (ceremony stage {stage}) ----------------------------------------------")
    lines.append(f"{NAMESPACE}.{event_id} = {{")
    lines.append(f"{T}type = country_event")
    append_first_valid_block(lines, "title", stage, wonders, title_key)
    append_first_valid_block(lines, "desc", stage, wonders, desc_key)
    lines.append(f'{T}image = "{CEREMONY_IMAGE}"')
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}trigger = {{")
    lines.append(f"{T}{T}has_variable = tv_engineering_department_member")
    lines.append(f"{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}has_variable = tv_wonder_ceremony_stage")
    lines.append(f"{T}{T}var:tv_wonder_ceremony_stage ?= {stage - 1}")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {pay_option_key(stage)}")
    lines.append(f"{T}{T}tv_wonder_ceremony_advance_to_stage_{stage}_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {decline_option_key(stage)}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    wonders = ceremony_wonders()
    lines = render_header(SCRIPT_REL, DATA_REL, str(OUT_FILE.relative_to(REPO_ROOT)).replace("\\", "/"))
    lines.append(f"namespace = {NAMESPACE}")
    lines.append("")
    for stage in range(1, STAGE_COUNT + 1):
        append_event(lines, stage, wonders)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("﻿" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
