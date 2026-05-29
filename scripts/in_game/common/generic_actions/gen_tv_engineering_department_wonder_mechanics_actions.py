import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import load_all_wonder_mechanics_data, render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "generic_actions" / "tv_engineering_department_wonder_mechanics_actions.txt"
SCRIPT_REL = "scripts/in_game/common/generic_actions/gen_tv_engineering_department_wonder_mechanics_actions.py"
T = "\t"


def confirm_action_block(action_name: str, trigger_name: str, effect_name: str, price: str | None = None) -> list[str]:
    lines = [
        f"{action_name} = {{",
        f"{T}type = owncountry",
        f"{T}sound = UI_action_religion_generic",
        f"{T}ai_tick = monthly",
        f"{T}ai_tick_frequency = 99999",
        f"{T}potential = {{ scope:actor = {{ has_variable = tv_engineering_department_member }} }}",
        f"{T}allow = {{ scope:actor = {{ {trigger_name} = yes }} }}",
    ]
    if price is not None:
        lines.append(f"{T}price = price:{price}")
    lines.extend(
        [
            f"{T}effect = {{ scope:actor = {{ {effect_name} = yes }} }}",
            f"{T}ai_will_do = {{ add = -100 }}",
            "}",
            "",
        ]
    )
    return lines


def generate() -> str:
    load_all_wonder_mechanics_data()
    lines = render_header(SCRIPT_REL)
    lines.extend(confirm_action_block("tv_wonder_confirm_ceremony", "tv_wonder_ceremony_ready_for_free_confirmation_trigger", "tv_wonder_confirm_ceremony_effect"))
    lines.extend(
        confirm_action_block(
            "tv_wonder_confirm_ceremony_scaled_gold",
            "tv_wonder_ceremony_ready_for_scaled_gold_confirmation_trigger",
            "tv_wonder_confirm_ceremony_effect",
            "tv_wonder_ritual_style_3_scaled_gold_price",
        )
    )
    lines.extend(
        confirm_action_block(
            "tv_wonder_confirm_ceremony_prestige",
            "tv_wonder_ceremony_ready_for_prestige_confirmation_trigger",
            "tv_wonder_confirm_ceremony_effect",
            "tv_wonder_ritual_style_3_prestige_price",
        )
    )
    return "\n".join(lines)


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
