"""Generate Pharos Lighthouse unique ritual event chain."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_wonder_unique_pharos_lighthouse_ritual_events.txt"
SCRIPT_REL = "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py"
DATA_REL = "data/unique_wonders.yaml + data/wonder_localization.yaml"
T = "\t"
PHAROS_IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_pharos_lighthouse_cropped.dds"


EVENTS = [
    {"id": 7300, "outcome": "neutral", "option": "a", "effect": "tv_wonder_pharos_refresh_display_effect = yes"},
    {
        "id": 7301,
        "outcome": "neutral",
        "option": "a",
        "effect": "change_gold_effect = { scale = -1 }\ntv_wonder_pharos_clear_privateers_effect = yes",
        "decline": "b",
    },
    {
        "id": 7302,
        "outcome": "neutral",
        "option": "a",
        "effect": "add_prestige = -10\ntv_wonder_pharos_clear_privateers_effect = yes",
        "decline": "b",
    },
    {
        "id": 7303,
        "outcome": "neutral",
        "option": "a",
        "effect": "add_estate_satisfaction = { type = estate_type:burghers_estate value = -0.05 }\ntv_wonder_pharos_clear_privateers_effect = yes",
        "decline": "b",
    },
    {"id": 7304, "outcome": "good", "option": "a", "effect": "tv_wonder_pharos_enter_stage_2_effect = yes"},
    {
        "id": 7305,
        "outcome": "good",
        "option": "a",
        "effect": "tv_wonder_pharos_complete_selected_controlled_route_effect = yes",
    },
    {
        "id": 7306,
        "outcome": "good",
        "option": "a",
        "effect": "tv_wonder_pharos_complete_selected_basing_route_effect = yes",
    },
    {
        "id": 7307,
        "outcome": "neutral",
        "option": "a",
        "effect": "change_gold_effect = { scale = -1 }\ntv_wonder_pharos_create_selected_route_basing_effect = yes",
    },
    {"id": 7308, "outcome": "good", "option": "a", "effect": "tv_wonder_pharos_finish_ritual_effect = yes"},
]


def indent_lines(text: str, level: int) -> list[str]:
    prefix = T * level
    return [f"{prefix}{line}" if line else line for line in text.splitlines()]


def render_immediate(event_id: int) -> list[str]:
    lines = [
        f"{T}immediate = {{",
        f"{T}{T}if = {{",
        f"{T}{T}{T}limit = {{ has_variable = tv_wonder_pharos_event_route_location }}",
        f"{T}{T}{T}var:tv_wonder_pharos_event_route_location ?= {{ save_scope_as = tv_wonder_pharos_event_route_location }}",
        f"{T}{T}}}",
        f"{T}{T}if = {{",
        f"{T}{T}{T}limit = {{ has_variable = tv_wonder_pharos_event_route_owner }}",
        f"{T}{T}{T}var:tv_wonder_pharos_event_route_owner ?= {{ save_scope_as = tv_wonder_pharos_event_route_owner }}",
        f"{T}{T}}}",
    ]
    if event_id in {7305, 7306, 7307}:
        lines.append(f"{T}{T}tv_wonder_pharos_refresh_display_effect = yes")
    lines.append(f"{T}}}")
    return lines


def render_option(event: dict) -> list[str]:
    lines = [
        f"{T}option = {{",
        f"{T}{T}name = tv_engineering_department.{event['id']}.{event['option']}",
    ]
    lines.extend(indent_lines(event["effect"], 2))
    lines.append(f"{T}}}")
    if "decline" in event:
        lines.extend(
            [
                "",
                f"{T}option = {{",
                f"{T}{T}name = tv_engineering_department.{event['id']}.{event['decline']}",
                f"{T}}}",
            ]
        )
    return lines


def render_event(event: dict) -> list[str]:
    event_id = event["id"]
    lines = [
        f"# -- tv_engineering_department.{event_id} ----------------------------------------------",
        f"tv_engineering_department.{event_id} = {{",
        f"{T}type = country_event",
        f"{T}title = tv_engineering_department.{event_id}.t",
        f"{T}desc = tv_engineering_department.{event_id}.d",
        f'{T}image = "{PHAROS_IMAGE}"',
        f"{T}outcome = {event['outcome']}",
        "",
    ]
    lines.extend(render_immediate(event_id))
    lines.append("")
    lines.extend(render_option(event))
    lines.append("}")
    return lines


def generate() -> str:
    lines = render_header(SCRIPT_REL, DATA_REL)
    lines.append("namespace = tv_engineering_department")
    lines.append("")
    for event in EVENTS:
        lines.extend(render_event(event))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("\ufeff" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
