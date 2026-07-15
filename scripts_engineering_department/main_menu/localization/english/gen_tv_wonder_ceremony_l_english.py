"""Generate English localization for the Unique Wonder Ceremony framework."""

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
    used_ceremony_cost_tiers,
)
from wonder_mechanics.rituals import (  # noqa: E402
    ceremony_cost_country_modifier_name,
    ceremony_cost_local_modifier_name,
    load_cost_reward_unit_labels,
)

OUT_FILE = REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "english" / "tv_wonder_ceremony_l_english.yml"
SCRIPT_REL = "scripts_engineering_department/main_menu/localization/english/gen_tv_wonder_ceremony_l_english.py"
DATA_REL = "data/unique_wonders.yaml + data/cost_reward_units.yaml"


def q(text: str) -> str:
    return text.replace('"', '\\"')


def capitalize_first(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text


def first_sentence(text: str) -> str:
    match = re.search(r"[.!?](?=\s|$)", text)
    return text[: match.end()] if match else text


def card_flavor_text(stage_data: dict, status: str) -> str:
    title = q(stage_data["title_en"])
    flavor = q(first_sentence(stage_data["desc_en"]))
    return f"{status} — #high {title}#!\\n#F {flavor}#!"


def ceremony_hint(stage: int) -> str:
    if stage < STAGE_COUNT:
        return (
            "\\n\\n#weak Pay the required price to advance the ceremony to its "
            "next stage — or wait if the moment is not yet right.#!"
        )
    return (
        "\\n\\n#weak Pay the required price to complete the ceremony — the "
        "wonder's final building will rise as a result.#!"
    )


def generate() -> str:
    wonders = ceremony_wonders()
    lines = ["l_english:"]
    for line in render_header(SCRIPT_REL, DATA_REL, str(OUT_FILE.relative_to(REPO_ROOT)).replace("\\", "/")):
        if line:
            lines.append(f" {line}")
        else:
            lines.append("")
    for stage in range(1, STAGE_COUNT + 1):
        lines.append(f' {pay_option_key(stage)}:0 "[ROOT.Custom(\'{option_pay_cl_block(stage)}\')]"')
        lines.append(f' {decline_option_key(stage)}:0 "[ROOT.Custom(\'{option_decline_cl_block(stage)}\')]"')
        lines.append(f' {option_pay_fallback_key(stage)}:0 "Pay the price."')
        lines.append(f' {option_decline_fallback_key(stage)}:0 "Not yet."')
    for wonder in wonders:
        stages = wonder["ceremony"]["stages"]
        for stage_index, stage_data in enumerate(stages, start=1):
            lines.append(f' {card_icon_key(stage_index, wonder["id"])}:0 "@{stage_data["icon"]}!"')
            lines.append(
                f' TV_WONDER_CEREMONY_CARD_ACTIVE_S{stage_index}_{wonder["id"]}:0 '
                f'"{card_flavor_text(stage_data, "#Y In progress#!")}"'
            )
            lines.append(
                f' TV_WONDER_CEREMONY_CARD_COMPLETED_S{stage_index}_{wonder["id"]}:0 '
                f'"{card_flavor_text(stage_data, "#G Completed#!")}"'
            )
            lines.append(f' {title_key(stage_index, wonder["id"])}:0 "{q(stage_data["title_en"])}"')
            lines.append(
                f' {desc_key(stage_index, wonder["id"])}:0 "{q(stage_data["desc_en"] + ceremony_hint(stage_index))}"'
            )
            lines.append(
                f' {option_pay_text_key(stage_index, wonder["id"])}:0 "{q(stage_data["option_pay_en"])}"'
            )
            lines.append(
                f' {option_decline_text_key(stage_index, wonder["id"])}:0 "{q(stage_data["option_decline_en"])}"'
            )
    labels = load_cost_reward_unit_labels()
    for entry_id, tier in used_ceremony_cost_tiers(wonders, "country_modifier"):
        name = ceremony_cost_country_modifier_name(entry_id, tier)
        lines.append(f' STATIC_MODIFIER_NAME_{name}:0 "{q(capitalize_first(labels["country_modifier"][entry_id]["en"]))}"')
    for entry_id, tier in used_ceremony_cost_tiers(wonders, "local_modifier"):
        name = ceremony_cost_local_modifier_name(entry_id, tier)
        lines.append(f' STATIC_MODIFIER_NAME_{name}:0 "{q(capitalize_first(labels["local_modifier"][entry_id]["en"]))}"')
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
