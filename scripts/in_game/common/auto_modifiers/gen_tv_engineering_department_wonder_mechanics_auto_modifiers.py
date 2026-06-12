"""Generate building-driven Engineering Department wonder country auto modifiers."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ceremony_styles,
    final_building_for_style,
    load_all_wonder_mechanics,
    render_header,
    wonder_auto_base_modifier_name,
    wonder_base_country_modifiers,
)

OUT_FILE = (
    REPO_ROOT
    / "src"
    / "in_game"
    / "common"
    / "auto_modifiers"
    / "tv_engineering_department_wonder_mechanics_auto_modifiers.txt"
)
SCRIPT_REL = "scripts/in_game/common/auto_modifiers/gen_tv_engineering_department_wonder_mechanics_auto_modifiers.py"
T = "\t"


def fmt_value(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def building_type_ref(building: str) -> str:
    return building if building.startswith("building_type:") else f"building_type:{building}"


def loc_level(building: str, op: str, level: int) -> str:
    return f"location_building_level = {{ building_type = {building_type_ref(building)} value {op} {level} }}"


def append_owned_building_level_trigger(lines: list[str], buildings: list[str], level: int, indent: int) -> None:
    prefix = T * indent
    lines.append(f"{prefix}any_owned_location = {{")
    if len(buildings) == 1:
        lines.append(f"{prefix}{T}{loc_level(buildings[0], '>=', level)}")
    else:
        lines.append(f"{prefix}{T}OR = {{")
        for building in buildings:
            lines.append(f"{prefix}{T}{T}{loc_level(building, '>=', level)}")
        lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


def append_base_potential(lines: list[str], buildings: list[str], level: int, indent: int) -> None:
    prefix = T * indent
    lines.append(f"{prefix}potential_trigger = {{")
    append_owned_building_level_trigger(lines, buildings, level, indent + 1)
    if level < 6:
        lines.append(f"{prefix}{T}NOT = {{")
        append_owned_building_level_trigger(lines, buildings, level + 1, indent + 2)
        lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")


def append_modifier_block(lines: list[str], name: str, modifiers: dict[str, object], potential_lines: list[str]) -> None:
    if not modifiers:
        return
    lines.append(f"{name} = {{")
    lines.append(f"{T}category = country")
    lines.extend(potential_lines)
    for key, value in modifiers.items():
        lines.append(f"{T}{key} = {fmt_value(value)}")
    lines.append("}")
    lines.append("")


def generated_potential_lines(callback, *args: object) -> list[str]:
    lines: list[str] = []
    callback(lines, *args, 1)
    return lines


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        final_buildings = [final_building_for_style(wonder, style) for style in ceremony_styles(wonder)]
        for level in range(1, 7):
            append_modifier_block(
                lines,
                wonder_auto_base_modifier_name(wonder, level),
                wonder_base_country_modifiers(wonder, mechanics, level),
                generated_potential_lines(append_base_potential, final_buildings, level),
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
