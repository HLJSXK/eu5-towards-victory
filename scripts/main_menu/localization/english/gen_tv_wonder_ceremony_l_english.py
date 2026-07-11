"""Generate English localization for the Unique Wonder Ceremony framework."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_ceremony_lib import (  # noqa: E402
    STAGE_COUNT,
    ceremony_wonders,
    decline_option_key,
    desc_key,
    pay_option_key,
    render_header,
    title_key,
)

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_wonder_ceremony_l_english.yml"
SCRIPT_REL = "scripts/main_menu/localization/english/gen_tv_wonder_ceremony_l_english.py"
DATA_REL = "data/unique_wonders.yaml"


def q(text: str) -> str:
    return text.replace('"', '\\"')


def generate() -> str:
    wonders = ceremony_wonders()
    lines = ["l_english:"]
    for line in render_header(SCRIPT_REL, DATA_REL, str(OUT_FILE.relative_to(REPO_ROOT)).replace("\\", "/")):
        if line:
            lines.append(f" {line}")
        else:
            lines.append("")
    for stage in range(1, STAGE_COUNT + 1):
        lines.append(f' {pay_option_key(stage)}:0 "Pay the price."')
        lines.append(f' {decline_option_key(stage)}:0 "Not yet."')
        lines.append(f' TV_WONDER_CEREMONY_CARD_STAGE_{stage}_LABEL:0 "Stage {stage} of 8"')
    for wonder in wonders:
        stages = wonder["ceremony"]["stages"]
        for stage_index, stage_data in enumerate(stages, start=1):
            lines.append(f' {title_key(stage_index, wonder["id"])}:0 "{q(stage_data["title_en"])}"')
            lines.append(f' {desc_key(stage_index, wonder["id"])}:0 "{q(stage_data["desc_en"])}"')
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
