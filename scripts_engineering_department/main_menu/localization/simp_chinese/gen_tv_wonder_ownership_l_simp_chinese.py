import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_mechanics.render import (
    loc_line,
    render_header,
)
from wonder_localization_lib import load_wonder_localization_data

OUT_FILE = REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "simp_chinese" / "tv_wonder_ownership_l_simp_chinese.yml"
SCRIPT_REL = "scripts_engineering_department/main_menu/localization/simp_chinese/gen_tv_wonder_ownership_l_simp_chinese.py"
DATA_REL = "data/wonder_localization.yaml"
OWNERSHIP_LOC_KEYS = [
    "tv_wonder_ownership.800.t",
    "tv_wonder_ownership.800.d",
    "tv_wonder_ownership.800.a",
    "tv_wonder_ownership.900.t",
    "tv_wonder_ownership.900.d",
    "tv_wonder_ownership.900.a",
]


OWNERSHIP_HINTS = {
    "tv_wonder_ownership.800.d": "\n\n#weak 该奇观现已归属于我们：可前往工程部查看其效果，并评估进一步扩建的可能。#!",
    "tv_wonder_ownership.900.d": "\n\n#weak 随着该省份易主，这座奇观带来的固定效果已经失去：日后若重新夺回，可在工程部确认其状态。#!",
}


def generate() -> str:
    localization = load_wonder_localization_data()["simp_chinese"]
    lines = ["l_simp_chinese:"]
    for line in render_header(SCRIPT_REL, DATA_REL):
        lines.append(f" {line}")
    for key in OWNERSHIP_LOC_KEYS:
        value = localization[key] + OWNERSHIP_HINTS.get(key, "")
        lines.append(loc_line(key, value))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
