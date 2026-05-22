"""Generate English localization for Wonder Construction random events."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_construction_event_lib import build_events, format_desc, format_title, load_data, option_loc, render_header


OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_wonder_construction_events_l_english.yml"
SCRIPT_REL = "scripts/main_menu/localization/english/gen_tv_wonder_construction_events_l_english.py"
DATA_REL = "data/wonder_construction_events.yaml"


def q(text: str) -> str:
    return text.replace('"', '\\"')


def generate() -> str:
    events = build_events(load_data())
    lines = ["l_english:"]
    for line in render_header(SCRIPT_REL, DATA_REL).rstrip().splitlines():
        lines.append(f" {line}")
    lines.extend(
        [
            ' TV_ADD_WONDER_MATERIALS_STOCKPILE:0 "Gains $VALUE|+$ [tv_wonder_materials|E]"',
            ' TV_FIRST_ADD_WONDER_MATERIALS_STOCKPILE:0 "We gain $VALUE|+$ [tv_wonder_materials|E]"',
            ' TV_THIRD_ADD_WONDER_MATERIALS_STOCKPILE:0 "Gains $VALUE|+$ [tv_wonder_materials|E]"',
            ' TV_PAST_ADD_WONDER_MATERIALS_STOCKPILE:0 "Gained $VALUE|+$ [tv_wonder_materials|E]"',
            ' TV_FIRST_PAST_ADD_WONDER_MATERIALS_STOCKPILE:0 "We gained $VALUE|+$ [tv_wonder_materials|E]"',
            ' TV_THIRD_PAST_ADD_WONDER_MATERIALS_STOCKPILE:0 "Gained $VALUE|+$ [tv_wonder_materials|E]"',
            ' TV_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "Loses $VALUE|-$ [tv_wonder_materials|E]"',
            ' TV_FIRST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "We lose $VALUE|-$ [tv_wonder_materials|E]"',
            ' TV_THIRD_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "Loses $VALUE|-$ [tv_wonder_materials|E]"',
            ' TV_PAST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "Lost $VALUE|-$ [tv_wonder_materials|E]"',
            ' TV_FIRST_PAST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "We lost $VALUE|-$ [tv_wonder_materials|E]"',
            ' TV_THIRD_PAST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "Lost $VALUE|-$ [tv_wonder_materials|E]"',
            ' TV_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "Gains $VALUE|+$ [tv_wonder_construction|E] progress on the active wonder part"',
            ' TV_FIRST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "We gain $VALUE|+$ [tv_wonder_construction|E] progress on the active wonder part"',
            ' TV_THIRD_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "Gains $VALUE|+$ [tv_wonder_construction|E] progress on the active wonder part"',
            ' TV_PAST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "Gained $VALUE|+$ [tv_wonder_construction|E] progress on the active wonder part"',
            ' TV_FIRST_PAST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "We gained $VALUE|+$ [tv_wonder_construction|E] progress on the active wonder part"',
            ' TV_THIRD_PAST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "Gained $VALUE|+$ [tv_wonder_construction|E] progress on the active wonder part"',
            ' TV_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "Loses $VALUE|-$ [tv_wonder_construction|E] progress from the active wonder part"',
            ' TV_FIRST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "We lose $VALUE|-$ [tv_wonder_construction|E] progress from the active wonder part"',
            ' TV_THIRD_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "Loses $VALUE|-$ [tv_wonder_construction|E] progress from the active wonder part"',
            ' TV_PAST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "Lost $VALUE|-$ [tv_wonder_construction|E] progress from the active wonder part"',
            ' TV_FIRST_PAST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "We lost $VALUE|-$ [tv_wonder_construction|E] progress from the active wonder part"',
            ' TV_THIRD_PAST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "Lost $VALUE|-$ [tv_wonder_construction|E] progress from the active wonder part"',
            ' TV_WONDER_SITE_LABORER_CASUALTY:0 "$VALUE|0$% of the laboring [population|E] at the selected wonder site die"',
            ' TV_FIRST_WONDER_SITE_LABORER_CASUALTY:0 "$VALUE|0$% of the laboring [population|E] at our selected wonder site die"',
            ' TV_THIRD_WONDER_SITE_LABORER_CASUALTY:0 "$VALUE|0$% of the laboring [population|E] at the selected wonder site die"',
            ' TV_PAST_WONDER_SITE_LABORER_CASUALTY:0 "$VALUE|0$% of the laboring [population|E] at the selected wonder site died"',
            ' TV_FIRST_PAST_WONDER_SITE_LABORER_CASUALTY:0 "$VALUE|0$% of the laboring [population|E] at our selected wonder site died"',
            ' TV_THIRD_PAST_WONDER_SITE_LABORER_CASUALTY:0 "$VALUE|0$% of the laboring [population|E] at the selected wonder site died"',
        ]
    )
    for event in events:
        event_id = event["id"]
        lines.append(f' tv_engineering_department.{event_id}.t:0 "{q(format_title(event, "en"))}"')
        lines.append(f' tv_engineering_department.{event_id}.d:0 "{q(format_desc(event, "en"))}"')
        lines.append(f' tv_engineering_department.{event_id}.a:0 "{q(option_loc(event["kind"], "a", "en"))}"')
        if event["kind"] in {"trade_noneng_for_eng", "choose_eng_or_noneng_loss"}:
            lines.append(f' tv_engineering_department.{event_id}.b:0 "{q(option_loc(event["kind"], "b", "en"))}"')
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
