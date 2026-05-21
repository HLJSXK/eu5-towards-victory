"""Generate Simplified Chinese localization for Wonder Construction random events."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_construction_event_lib import build_events, format_desc, format_title, load_data, option_loc, render_header


OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_wonder_construction_events_l_simp_chinese.yml"
SCRIPT_REL = "scripts/main_menu/localization/simp_chinese/gen_tv_wonder_construction_events_l_simp_chinese.py"
DATA_REL = "data/wonder_construction_events.yaml"


def q(text: str) -> str:
    return text.replace('"', '\\"')


def generate() -> str:
    events = build_events(load_data())
    lines = ["l_simp_chinese:"]
    for line in render_header(SCRIPT_REL, DATA_REL).rstrip().splitlines():
        lines.append(f" {line}")
    lines.extend(
        [
            ' TV_ADD_WONDER_MATERIALS_STOCKPILE:0 "获得$VALUE|+$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_FIRST_ADD_WONDER_MATERIALS_STOCKPILE:0 "我们获得$VALUE|+$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_THIRD_ADD_WONDER_MATERIALS_STOCKPILE:0 "获得$VALUE|+$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_PAST_ADD_WONDER_MATERIALS_STOCKPILE:0 "已获得$VALUE|+$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_FIRST_PAST_ADD_WONDER_MATERIALS_STOCKPILE:0 "我们已获得$VALUE|+$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_THIRD_PAST_ADD_WONDER_MATERIALS_STOCKPILE:0 "已获得$VALUE|+$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "失去$VALUE|-$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_FIRST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "我们失去$VALUE|-$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_THIRD_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "失去$VALUE|-$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_PAST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "已失去$VALUE|-$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_FIRST_PAST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "我们已失去$VALUE|-$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_THIRD_PAST_SUBTRACT_WONDER_MATERIALS_STOCKPILE:0 "已失去$VALUE|-$#Y $tv_wonder_materials_stockpile$#!"',
            ' TV_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件获得$VALUE|+$#Y 建设进度#!"',
            ' TV_FIRST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "我们的当前奇观部件获得$VALUE|+$#Y 建设进度#!"',
            ' TV_THIRD_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件获得$VALUE|+$#Y 建设进度#!"',
            ' TV_PAST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件已获得$VALUE|+$#Y 建设进度#!"',
            ' TV_FIRST_PAST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "我们的当前奇观部件已获得$VALUE|+$#Y 建设进度#!"',
            ' TV_THIRD_PAST_ADD_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件已获得$VALUE|+$#Y 建设进度#!"',
            ' TV_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件失去$VALUE|-$#Y 建设进度#!"',
            ' TV_FIRST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "我们的当前奇观部件失去$VALUE|-$#Y 建设进度#!"',
            ' TV_THIRD_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件失去$VALUE|-$#Y 建设进度#!"',
            ' TV_PAST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件已失去$VALUE|-$#Y 建设进度#!"',
            ' TV_FIRST_PAST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "我们的当前奇观部件已失去$VALUE|-$#Y 建设进度#!"',
            ' TV_THIRD_PAST_SUBTRACT_WONDER_CONSTRUCTION_PROGRESS:0 "当前奇观部件已失去$VALUE|-$#Y 建设进度#!"',
            ' TV_WONDER_SITE_LABORER_CASUALTY:0 "已选奇观地点$VALUE|0$%的劳工死亡"',
            ' TV_FIRST_WONDER_SITE_LABORER_CASUALTY:0 "我们已选奇观地点$VALUE|0$%的劳工死亡"',
            ' TV_THIRD_WONDER_SITE_LABORER_CASUALTY:0 "已选奇观地点$VALUE|0$%的劳工死亡"',
            ' TV_PAST_WONDER_SITE_LABORER_CASUALTY:0 "已选奇观地点$VALUE|0$%的劳工已经死亡"',
            ' TV_FIRST_PAST_WONDER_SITE_LABORER_CASUALTY:0 "我们已选奇观地点$VALUE|0$%的劳工已经死亡"',
            ' TV_THIRD_PAST_WONDER_SITE_LABORER_CASUALTY:0 "已选奇观地点$VALUE|0$%的劳工已经死亡"',
        ]
    )
    for event in events:
        event_id = event["id"]
        lines.append(f' tv_engineering_department.{event_id}.t:0 "{q(format_title(event, "zh"))}"')
        lines.append(f' tv_engineering_department.{event_id}.d:0 "{q(format_desc(event, "zh"))}"')
        lines.append(f' tv_engineering_department.{event_id}.a:0 "{q(option_loc(event, "a", "zh"))}"')
        if event["kind"] in {"trade_noneng_for_eng", "choose_eng_or_noneng_loss"}:
            lines.append(f' tv_engineering_department.{event_id}.b:0 "{q(option_loc(event, "b", "zh"))}"')
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
