import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    authored_final_building_local_modifiers,
    load_all_wonder_mechanics,
    render_header,
    ritual_auxiliary_display_modifier_name,
    ritual_auxiliary_modifiers,
    ritual_plan_for_style,
    ceremony_styles,
)

OUT_FILE = (
    REPO_ROOT
    / "src"
    / "main_menu"
    / "common"
    / "static_modifiers"
    / "tv_engineering_department_wonder_ritual_auxiliary_location_modifiers.txt"
)
SCRIPT_REL = "scripts/main_menu/common/static_modifiers/gen_tv_engineering_department_wonder_ritual_auxiliary_location_modifiers.py"
T = "\t"
DISPLAY_MODIFIER_PREFIX = "tv_wonder_display_"


def fmt_value(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def modifier_block(name: str, modifiers: dict) -> list[str]:
    lines = [f"{name} = {{"]
    for key, value in modifiers.items():
        lines.append(f"{T}{key} = {fmt_value(value)}")
    lines.extend(
        [
            f"{T}game_data = {{",
            f"{T}{T}category = location",
            f"{T}}}",
            "}",
            "",
        ]
    )
    return lines


def scaled_modifiers(base: dict, level: int) -> dict:
    result: dict[str, object] = {}
    for key, value in base.items():
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            result[key] = value * level
        else:
            result[key] = value
    return result


def display_local_modifier_name(wonder: dict, level: int) -> str:
    return f"{DISPLAY_MODIFIER_PREFIX}{wonder['id']}_local_level_{level}"


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        local_base = authored_final_building_local_modifiers(wonder, mechanics)
        for level in range(1, 7):
            lines.extend(
                modifier_block(
                    display_local_modifier_name(wonder, level),
                    scaled_modifiers(local_base, level),
                )
            )
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            if ritual_plan["mode"] != "auxiliary_building":
                continue
            lines.extend(
                modifier_block(
                    ritual_auxiliary_display_modifier_name(wonder),
                    ritual_auxiliary_modifiers(wonder, ritual_plan),
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
