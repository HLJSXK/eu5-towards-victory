"""Generate the Unique Wonder Ceremony's country-scope temporary cost static modifiers.

One tiny static modifier per (country_modifier catalog id, tier) pair actually referenced
by an authored ceremony stage cost in data/unique_wonders.yaml -- not the full catalog x
tier cross product. Applied via `add_country_modifier = { modifier = <name> years = 5
mode = add_and_extend }` (see scripts/wonder_ceremony_lib.py's ceremony_cost_effect_lines()).
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_ceremony_lib import (  # noqa: E402
    T,
    ceremony_wonders,
    render_header,
    script_rel,
    used_ceremony_cost_tiers,
)
from wonder_mechanics.rituals import (  # noqa: E402
    ceremony_cost_country_modifier_name,
    load_cost_reward_units,
)

OUT_FILE = (
    REPO_ROOT
    / "src_engineering_department" / "main_menu"
    / "common"
    / "static_modifiers"
    / "tv_wonder_ceremony_cost_country_modifiers.txt"
)
SCRIPT_REL = "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_wonder_ceremony_cost_country_modifiers.py"
DATA_REL = "data/unique_wonders.yaml + data/cost_reward_units.yaml"


def fmt_value(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def generate() -> str:
    wonders = ceremony_wonders()
    country_modifiers = load_cost_reward_units()["country_modifier"]
    lines = render_header(SCRIPT_REL, DATA_REL, script_rel(OUT_FILE))
    for entry_id, tier in used_ceremony_cost_tiers(wonders, "country_modifier"):
        value = -1 * country_modifiers[entry_id] * tier
        lines.append(f"{ceremony_cost_country_modifier_name(entry_id, tier)} = {{")
        lines.append(f"{T}{entry_id} = {fmt_value(value)}")
        lines.append("}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("﻿" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
