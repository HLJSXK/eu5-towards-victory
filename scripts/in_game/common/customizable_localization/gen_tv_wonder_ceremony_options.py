"""Generate the Unique Wonder Ceremony's per-stage option-text Customizable Localization
dispatch blocks (16 blocks: 8 stages x pay/decline). Each block is `type = country` with one
`text` entry per ceremony-enabled unique wonder (dispatched on `var:tv_wonder_locked`) plus a
`fallback` entry, so the two event options at each stage read as that wonder's own authored
flavor text instead of one generic pair reused across all 121 wonders. The event's
`option.name` field itself is unchanged (still a single flat key); only that key's
localization value calls `Custom(<block name>)` to resolve per-wonder.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_ceremony_lib import (  # noqa: E402
    STAGE_COUNT,
    append_option_customizable_localization_block,
    ceremony_wonders,
    render_header,
    script_rel,
)

OUT_FILE = (
    REPO_ROOT
    / "src"
    / "in_game"
    / "common"
    / "customizable_localization"
    / "tv_wonder_ceremony_options.txt"
)
SCRIPT_REL = "scripts/in_game/common/customizable_localization/gen_tv_wonder_ceremony_options.py"
DATA_REL = "data/unique_wonders.yaml"


def generate() -> str:
    wonders = ceremony_wonders()
    lines = render_header(SCRIPT_REL, DATA_REL, script_rel(OUT_FILE))
    for stage in range(1, STAGE_COUNT + 1):
        append_option_customizable_localization_block(lines, stage, wonders, pay=True)
        append_option_customizable_localization_block(lines, stage, wonders, pay=False)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("﻿" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
