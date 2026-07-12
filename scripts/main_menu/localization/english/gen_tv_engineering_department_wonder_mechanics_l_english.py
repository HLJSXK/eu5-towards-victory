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
from wonder_localization_lib import (
    engineering_department_wonder_mechanics_localization_map,
    load_wonder_localization_data,
)

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_engineering_department_wonder_mechanics_l_english.yml"
SCRIPT_REL = "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py"
DATA_REL = "data/wonders.yaml + data/wonder_final_buildings.yaml + data/wonder_generic_rituals.yaml + data/wonder_base_modifiers.yaml + data/wonder_site_rules.yaml + data/unique_wonders.yaml + data/wonder_localization.yaml"
def generate() -> str:
    localization = load_wonder_localization_data()["english"]
    lines = ["l_english:"]
    for line in render_header(SCRIPT_REL, DATA_REL):
        lines.append(f" {line}")
    for key, value in engineering_department_wonder_mechanics_localization_map("english", localization).items():
        lines.append(loc_line(key, value))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
