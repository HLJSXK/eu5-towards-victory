import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.modifiers import (
    authored_final_building_local_modifiers,
    scale_numeric_modifier_mapping,
)
from wonder_mechanics.naming import wonder_static_local_display_modifier_name
from wonder_mechanics.render import render_header
from wonder_mechanics.rituals import (
    ritual_auxiliary_display_modifier_name,
    ritual_auxiliary_modifiers,
    ritual_plan_for_style,
    ceremony_styles,
)

OUT_FILE = (
    REPO_ROOT
    / "src_engineering_department" / "main_menu"
    / "common"
    / "static_modifiers"
    / "tv_engineering_department_wonder_ritual_auxiliary_location_modifiers.txt"
)
SCRIPT_REL = "scripts_engineering_department/main_menu/common/static_modifiers/gen_tv_engineering_department_wonder_ritual_auxiliary_location_modifiers.py"
T = "\t"


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


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        local_base = authored_final_building_local_modifiers(wonder, mechanics)
        for level in range(1, 7):
            lines.extend(
                modifier_block(
                    wonder_static_local_display_modifier_name(wonder, level),
                    scale_numeric_modifier_mapping(local_base, level),
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
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
