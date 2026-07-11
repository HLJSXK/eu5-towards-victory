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

OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_wonder_ownership_l_english.yml"
SCRIPT_REL = "scripts/main_menu/localization/english/gen_tv_wonder_ownership_l_english.py"
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
    "tv_wonder_ownership.800.d": (
        "\n\n#weak The wonder now belongs to us — review its effects in the "
        "Engineering Department and consider whether it can be expanded "
        "further.#!"
    ),
    "tv_wonder_ownership.900.d": (
        "\n\n#weak With the province lost, the wonder's fixed benefits are "
        "gone — if it is retaken later, confirm its status in the Engineering "
        "Department.#!"
    ),
}


def generate() -> str:
    localization = load_wonder_localization_data()["english"]
    lines = ["l_english:"]
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
