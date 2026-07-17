"""Generate Simplified Chinese localization for the Unique Wonder Ceremony framework."""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_ceremony_lib import (  # noqa: E402
    STAGE_COUNT,
    card_icon_key,
    ceremony_stage_cost_entries,
    ceremony_wonders,
    decline_option_key,
    desc_key,
    option_decline_cl_block,
    option_decline_fallback_key,
    option_decline_text_key,
    option_pay_cl_block,
    option_pay_fallback_key,
    option_pay_text_key,
    pay_option_key,
    render_header,
    title_key,
)
from wonder_mechanics.rituals import (  # noqa: E402
    ceremony_stage_cost_country_modifier_name,
    ceremony_stage_cost_local_modifier_name,
)

OUT_FILE = REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "simp_chinese" / "tv_wonder_ceremony_l_simp_chinese.yml"
SCRIPT_REL = "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_wonder_ceremony_l_simp_chinese.py"
DATA_REL = "data/unique_wonders.yaml + data/cost_reward_units.yaml"


def q(text: str) -> str:
    return text.replace('"', '\\"')


def first_sentence(text: str) -> str:
    match = re.search(r"[。！？]", text)
    return text[: match.end()] if match else text


def card_flavor_text(stage_data: dict, status: str) -> str:
    title = q(stage_data["title_zh"])
    flavor = q(first_sentence(stage_data["desc_zh"]))
    return f"{status} — #high {title}#!\\n#F {flavor}#!"


def ceremony_hint(stage: int) -> str:
    if stage < STAGE_COUNT:
        return "\\n\\n#weak 支付所需的代价，即可将仪式推进至下一阶段；若尚未准备好，也可以静待时机。#!"
    return "\\n\\n#weak 支付所需的代价，即可完成这场仪式，奇观的最终建筑将随之落成。#!"


def generate() -> str:
    wonders = ceremony_wonders()
    lines = ["l_simp_chinese:"]
    for line in render_header(SCRIPT_REL, DATA_REL, str(OUT_FILE.relative_to(REPO_ROOT)).replace("\\", "/")):
        if line:
            lines.append(f" {line}")
        else:
            lines.append("")
    for stage in range(1, STAGE_COUNT + 1):
        lines.append(f' {pay_option_key(stage)}:0 "[ROOT.GetCountry.Custom(\'{option_pay_cl_block(stage)}\')]"')
        lines.append(f' {decline_option_key(stage)}:0 "[ROOT.GetCountry.Custom(\'{option_decline_cl_block(stage)}\')]"')
        lines.append(f' {option_pay_fallback_key(stage)}:0 "支付代价。"')
        lines.append(f' {option_decline_fallback_key(stage)}:0 "暂缓。"')
    for wonder in wonders:
        stages = wonder["ceremony"]["stages"]
        for stage_index, stage_data in enumerate(stages, start=1):
            lines.append(f' {card_icon_key(stage_index, wonder["id"])}:0 "@{stage_data["icon"]}!"')
            lines.append(
                f' TV_WONDER_CEREMONY_CARD_ACTIVE_S{stage_index}_{wonder["id"]}:0 '
                f'"{card_flavor_text(stage_data, "#Y 进行中#!")}"'
            )
            lines.append(
                f' TV_WONDER_CEREMONY_CARD_COMPLETED_S{stage_index}_{wonder["id"]}:0 '
                f'"{card_flavor_text(stage_data, "#G 已完成#!")}"'
            )
            lines.append(f' {title_key(stage_index, wonder["id"])}:0 "[tv_wonder_ceremony|E]：{q(stage_data["title_zh"])}"')
            lines.append(
                f' {desc_key(stage_index, wonder["id"])}:0 "{q(stage_data["desc_zh"] + ceremony_hint(stage_index))}"'
            )
            lines.append(
                f' {option_pay_text_key(stage_index, wonder["id"])}:0 "{q(stage_data["option_pay_zh"])}"'
            )
            lines.append(
                f' {option_decline_text_key(stage_index, wonder["id"])}:0 "{q(stage_data["option_decline_zh"])}"'
            )
    for wonder, stage_index, _entry_id in ceremony_stage_cost_entries(wonders, "country_modifier"):
        name = ceremony_stage_cost_country_modifier_name(wonder["key"], stage_index)
        title = q(wonder["ceremony"]["stages"][stage_index - 1]["title_zh"])
        lines.append(f' STATIC_MODIFIER_NAME_{name}:0 "{title}"')
    for wonder, stage_index, _entry_id in ceremony_stage_cost_entries(wonders, "local_modifier"):
        name = ceremony_stage_cost_local_modifier_name(wonder["key"], stage_index)
        title = q(wonder["ceremony"]["stages"][stage_index - 1]["title_zh"])
        lines.append(f' STATIC_MODIFIER_NAME_{name}:0 "{title}"')
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
