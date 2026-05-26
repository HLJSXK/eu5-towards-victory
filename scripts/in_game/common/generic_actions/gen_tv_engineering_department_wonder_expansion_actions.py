import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_expansion_lib import load_wonder_data, render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "generic_actions" / "tv_engineering_department_wonder_expansion_actions.txt"
SCRIPT_REL = "scripts/in_game/common/generic_actions/gen_tv_engineering_department_wonder_expansion_actions.py"
T = "\t"


def generate() -> str:
    load_wonder_data()
    lines = render_header(SCRIPT_REL)
    lines.extend(
        [
            "tv_wonder_confirm_new_ceremony = {",
            f"{T}type = owncountry",
            f"{T}sound = UI_action_religion_generic",
            f"{T}ai_tick = monthly",
            f"{T}ai_tick_frequency = 99999",
            f"{T}potential = {{ scope:actor = {{ has_variable = tv_engineering_department_member }} }}",
            f"{T}allow = {{ scope:actor = {{ tv_wonder_new_ceremony_ready_trigger = yes }} }}",
            f"{T}effect = {{ scope:actor = {{ tv_wonder_new_confirm_ceremony_effect = yes }} }}",
            f"{T}ai_will_do = {{ add = -100 }}",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
