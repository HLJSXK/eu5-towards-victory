import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.render import (
    loc_line,
    render_header,
)
from wonder_localization_lib import load_wonder_localization_data

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_wonder_mechanics_l_simp_chinese.yml"
SCRIPT_REL = "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py"
DATA_REL = "data/wonders.yaml + data/wonder_final_buildings.yaml + data/wonder_generic_rituals.yaml + data/wonder_base_modifiers.yaml + data/wonder_site_rules.yaml + data/unique_wonders.yaml + data/wonder_localization.yaml"
EXCLUDED_LOC_KEYS = {
    "tv_wonder_ownership.800.t",
    "tv_wonder_ownership.800.d",
    "tv_wonder_ownership.800.a",
    "tv_wonder_ownership.900.t",
    "tv_wonder_ownership.900.d",
    "tv_wonder_ownership.900.a",
    # Superseded single-track drafts from data/wonder_localization.yaml that predate the
    # repeated-row pilot redesign (scripts/gen_repeated_row_pilot_wonders.py). Event IDs
    # 1000-1003 and 1012-1015 are now the Dome of the Rock custody_duties row set and the
    # Bank of Saint George public_credit_pledges row set respectively; those generated
    # dotted keys live in the per-wonder tv_wonder_unique_*_ritual_l_simp_chinese.yml files,
    # so this shared file must not also define them or the two definitions collide.
    "tv_engineering_department.1000.t",
    "tv_engineering_department.1000.d",
    "tv_engineering_department.1000.a",
    "tv_engineering_department.1001.t",
    "tv_engineering_department.1001.d",
    "tv_engineering_department.1001.a",
    "tv_engineering_department.1001.b",
    "tv_engineering_department.1001.c",
    "tv_engineering_department.1002.t",
    "tv_engineering_department.1002.d",
    "tv_engineering_department.1002.a",
    "tv_engineering_department.1002.b",
    "tv_engineering_department.1003.t",
    "tv_engineering_department.1003.d",
    "tv_engineering_department.1003.a",
    "tv_engineering_department.1012.t",
    "tv_engineering_department.1012.d",
    "tv_engineering_department.1012.a",
    "tv_engineering_department.1013.t",
    "tv_engineering_department.1013.d",
    "tv_engineering_department.1013.a",
    "tv_engineering_department.1013.b",
    "tv_engineering_department.1013.c",
    "tv_engineering_department.1014.t",
    "tv_engineering_department.1014.d",
    "tv_engineering_department.1014.a",
    "tv_engineering_department.1014.b",
    "tv_engineering_department.1015.t",
    "tv_engineering_department.1015.d",
    "tv_engineering_department.1015.a",
}


FINALIZATION_VISIBLE_DESC_PREFIX = "tv_engineering_department.500.d"
FINALIZATION_HINT = "\n\n#weak 奇观的建设已经完成，最终建筑即将落成：可前往工程部或该地点查看其效果。#!"


def generate() -> str:
    localization = load_wonder_localization_data()["simp_chinese"]
    lines = ["l_simp_chinese:"]
    for line in render_header(SCRIPT_REL, DATA_REL):
        lines.append(f" {line}")
    for key, value in localization.items():
        if key in EXCLUDED_LOC_KEYS:
            continue
        if key.startswith(FINALIZATION_VISIBLE_DESC_PREFIX):
            value = value + FINALIZATION_HINT
        lines.append(loc_line(key, value))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
