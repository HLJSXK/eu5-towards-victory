import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ceremony_styles,
    final_building_for_style,
    final_building_maintenance,
    load_all_wonder_mechanics,
    mechanic_key,
    render_header,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "building_types" / "tv_engineering_department_wonder_mechanics_buildings.txt"
SCRIPT_REL = "scripts/in_game/common/building_types/gen_tv_engineering_department_wonder_mechanics_buildings.py"
T = "\t"


def fmt_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def fmt_yes_no(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def merge_modifiers(*maps: dict | None) -> dict:
    merged: dict[str, object] = {
        "local_cultural_tradition": 0.5,
        "local_cultural_influence": 0.5,
    }
    for mapping in maps:
        if not mapping:
            continue
        for key, value in mapping.items():
            if isinstance(value, (int, float)) and isinstance(merged.get(key), (int, float)):
                merged[key] = merged[key] + value
            else:
                merged[key] = value
    return merged


def building_block(name: str, wonder: dict, modifiers: dict, maintenance: str, attributes: dict | None = None) -> list[str]:
    attrs = attributes or {}
    lines = [
        f"{name} = {{",
        f"{T}is_special = yes",
        f"{T}is_foreign = no",
        f"{T}pop_type = {attrs.get('pop_type', wonder['pop_type'])}",
        f"{T}max_levels = 6",
        f"{T}employment_size = 0.1",
        f"{T}category = {attrs.get('category', wonder['category'])}",
        "",
        f"{T}town = {fmt_yes_no(attrs.get('town', 'yes'))}",
        f"{T}city = {fmt_yes_no(attrs.get('city', 'yes'))}",
        f"{T}megalopolis = {fmt_yes_no(attrs.get('megalopolis', 'yes'))}",
        f"{T}rural_settlement = {fmt_yes_no(attrs.get('rural_settlement', 'yes'))}",
        "",
        f"{T}important_for_AI = no",
        f"{T}automation_build_allowed = no",
        f"{T}country_potential = {{ always = no }}",
        f"{T}allow = {{",
        f"{T}{T}custom_tooltip = {{",
        f"{T}{T}{T}text = TV_WONDER_ENGINEERING_ONLY_BUILDING_TT",
        f"{T}{T}{T}always = no",
        f"{T}{T}}}",
        f"{T}}}",
        f"{T}can_destroy = {{ always = no }}",
        "",
        f"{T}build_time = large_cultural_building_time",
        "",
        f"{T}modifier = {{",
    ]
    for mod_key, mod_value in modifiers.items():
        lines.append(f"{T}{T}{mod_key} = {fmt_value(mod_value)}")
    lines.extend(
        [
            f"{T}}}",
            "",
        f"{T}possible_production_methods = {{",
        f"{T}{T}{maintenance}",
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
        building_design = mechanics["buildings"][mechanic_key(wonder)]
        base_local = building_design.get("base_local", {})
        final_local = building_design.get("final_local", {})
        for style in ceremony_styles(wonder):
            building = final_building_for_style(wonder, style)
            modifiers = merge_modifiers(base_local, final_local.get(building, {}))
            maintenance = final_building_maintenance(wonder, building_design, building)
            attributes = building_design.get("final_attributes", {}).get(building, {})
            lines.extend(building_block(building, wonder, modifiers, maintenance, attributes))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
