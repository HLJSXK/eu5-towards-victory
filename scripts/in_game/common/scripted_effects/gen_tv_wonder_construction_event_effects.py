"""Generate Wonder Construction monthly random-event roll effect."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_construction_event_lib import build_events, indent_lines, load_data, render_header


OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_wonder_construction_event_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_wonder_construction_event_effects.py"
DATA_REL = "data/wonder_construction_events.yaml"
T = "\t"


def render_roll(events: list[dict]) -> str:
    lines = [
        "tv_wonder_construction_random_event_roll_effect = {",
        T + "random_list = {",
        T * 2 + "90 = { }",
        T * 2 + "10 = {",
        T * 3 + "random_list = {",
    ]
    for event in events:
        lines.extend(
            [
                T * 4 + f"{event['weight']} = {{",
                T * 5 + f"trigger = {{ tv_wonder_construction_event_{event['id']}_eligible_trigger = yes }}",
                T * 5 + f"trigger_event_non_silently = {{ id = tv_engineering_department.{event['id']} }}",
                T * 4 + "}",
            ]
        )
    lines.extend([T * 3 + "}", T * 2 + "}", T + "}", "}"])
    return "\n".join(lines)


def generate() -> str:
    data = load_data()
    events = build_events(data)
    header = render_header(SCRIPT_REL, DATA_REL, " # Towards Victory - generated Wonder Construction event roll.")
    return f"{header}\n{render_roll(events)}\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
