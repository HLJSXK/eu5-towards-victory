"""Generate Hagia Sophia unique ritual event chain."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_wonder_unique_hagia_sophia_ritual_events.txt"
SCRIPT_REL = "scripts/in_game/events/gen_tv_wonder_unique_hagia_sophia_ritual_events.py"
DATA_REL = "data/unique_wonders.yaml + data/wonder_localization.yaml"
T = "\t"
HAGIA_IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_hagia_sophia_cropped.dds"


EVENTS = [
    {"id": 6301, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_1_effect = yes", "retry": True},
    {"id": 6302, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_2_effect = yes", "retry": True},
    {"id": 6303, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_3_effect = yes", "retry": True},
    {"id": 6304, "outcome": "good", "effect": "tv_wonder_hagia_complete_step_4_effect = yes", "retry": False},
    {"id": 6305, "outcome": "good", "effect": "tv_wonder_hagia_complete_step_5_effect = yes", "retry": False},
    {"id": 6306, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_6_effect = yes", "retry": True},
    {"id": 6307, "outcome": "neutral", "effect": "tv_wonder_hagia_complete_step_7_effect = yes", "retry": True},
    {"id": 6308, "outcome": "good", "effect": "tv_wonder_hagia_complete_step_8_effect = yes", "retry": False},
]


def indent_lines(text: str, level: int) -> list[str]:
    prefix = T * level
    return [f"{prefix}{line}" if line else line for line in text.splitlines()]


def render_option(event: dict) -> list[str]:
    event_id = event["id"]
    lines = [
        f"{T}option = {{",
        f"{T}{T}name = tv_engineering_department.{event_id}.a",
    ]
    lines.extend(indent_lines(event["effect"], 2))
    lines.append(f"{T}}}")
    if event.get("retry"):
        lines.extend(
            [
                "",
                f"{T}option = {{",
                f"{T}{T}name = tv_engineering_department.{event_id}.b",
                f"{T}{T}tv_wonder_hagia_retry_step_effect = yes",
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
        f'{T}image = "{HAGIA_IMAGE}"',
        f"{T}outcome = {event['outcome']}",
        "",
    ]
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
