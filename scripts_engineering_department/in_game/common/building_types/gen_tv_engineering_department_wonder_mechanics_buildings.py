import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.modifiers import (
    authored_final_building_local_modifiers,
    final_building_maintenance,
    merge_numeric_modifier_mappings,
    wonder_base_country_modifiers,
)
from wonder_mechanics.naming import (
    final_building_for_style,
    mechanic_key,
)
from wonder_mechanics.render import render_header
from wonder_mechanics.rituals import (
    ceremony_styles,
    ritual_auxiliary_modifiers,
    ritual_plan_for_style,
    ritual_auxiliary_building,
)

OUT_FILE = REPO_ROOT / "src_engineering_department" / "in_game" / "common" / "building_types" / "tv_engineering_department_wonder_mechanics_buildings.txt"
SCRIPT_REL = "scripts_engineering_department/in_game/common/building_types/gen_tv_engineering_department_wonder_mechanics_buildings.py"
T = "\t"
RAW_MODIFIER_KEYS = {"fort_level"}
PORT_WONDERS = {
    "great_port",
    "great_lighthouse",
    "national_shipyard",
    "coastal_beacon_network",
    "maritime_trade_station_network",
}

def fmt_value(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
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
    return merge_numeric_modifier_mappings(merged, *maps)


def split_modifiers(modifiers: dict) -> tuple[dict, dict]:
    normal: dict[str, object] = {}
    raw: dict[str, object] = {}
    for key, value in modifiers.items():
        if key in RAW_MODIFIER_KEYS:
            raw[key] = value
        else:
            normal[key] = value
    return normal, raw


def build_profile(wonder: dict) -> tuple[str, str, str]:
    if wonder["key"] in PORT_WONDERS:
        return "large_port_building_time", "port_building_construction", f"tv_wonder_ritual_annex_{wonder['size']}_price"
    if wonder["category"] == "military_category":
        return "small_fort_building", "fort_construction", f"tv_wonder_ritual_annex_{wonder['size']}_price"
    if wonder["category"] == "government_category":
        return "government_build_time", "capital_building_construction", f"tv_wonder_ritual_annex_{wonder['size']}_price"
    if wonder["pop_type"] == "clergy":
        return "religious_building_time", "town_building_construction", f"tv_wonder_ritual_annex_{wonder['size']}_price"
    if wonder["category"] == "cultural_category":
        return "large_cultural_building_time", "library_construction", f"tv_wonder_ritual_annex_{wonder['size']}_price"
    return "infrastructure_build_time", "basic_construction_needs", f"tv_wonder_ritual_annex_{wonder['size']}_price"


def building_block(
    name: str,
    wonder: dict,
    modifiers: dict,
    maintenance: str,
    *,
    attributes: dict | None = None,
    max_levels: int = 6,
    build_time: str = "large_cultural_building_time",
    construction_demand: str | None = None,
    price: str | None = None,
    on_built_lines: list[str] | None = None,
    on_destroyed_lines: list[str] | None = None,
    on_construction_ended_lines: list[str] | None = None,
    can_destroy: str = "no",
) -> list[str]:
    attrs = attributes or {}
    normal_modifier, raw_modifier = split_modifiers(modifiers)
    lines = [
        f"{name} = {{",
        f"{T}is_special = yes",
        f"{T}is_foreign = no",
        f"{T}pop_type = {attrs.get('pop_type', wonder['pop_type'])}",
        f"{T}max_levels = {max_levels}",
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
        f"{T}can_destroy = {{ always = {can_destroy} }}",
        "",
    ]
    if price is not None:
        lines.append(f"{T}price = {price}")
        lines.append("")
    lines.append(f"{T}build_time = {build_time}")
    if construction_demand is not None:
        lines.append(f"{T}construction_demand = {construction_demand}")
    lines.append("")
    lines.append(f"{T}modifier = {{")
    for mod_key, mod_value in normal_modifier.items():
        lines.append(f"{T}{T}{mod_key} = {fmt_value(mod_value)}")
    lines.append(f"{T}}}")
    if raw_modifier:
        lines.append("")
        lines.append(f"{T}raw_modifier = {{")
        for mod_key, mod_value in raw_modifier.items():
            lines.append(f"{T}{T}{mod_key} = {fmt_value(mod_value)}")
        lines.append(f"{T}}}")
    lines.extend(
        [
            "",
            f"{T}possible_production_methods = {{",
            f"{T}{T}{maintenance}",
            f"{T}}}",
        ]
    )
    if on_built_lines:
        lines.extend(["", f"{T}on_built = {{"])
        lines.extend(on_built_lines)
        lines.append(f"{T}}}")
    if on_destroyed_lines:
        lines.extend(["", f"{T}on_destroyed = {{"])
        lines.extend(on_destroyed_lines)
        lines.append(f"{T}}}")
    if on_construction_ended_lines:
        lines.extend(["", f"{T}on_construction_ended = {{"])
        lines.extend(on_construction_ended_lines)
        lines.append(f"{T}}}")
    lines.extend(["}", ""])
    return lines


def auxiliary_on_built_lines(wonder: dict, style: int) -> list[str]:
    return [
        f"{T}{T}hidden_effect = {{",
        f"{T}{T}{T}location.owner = {{",
        f"{T}{T}{T}{T}if = {{",
        f"{T}{T}{T}{T}{T}limit = {{",
        f"{T}{T}{T}{T}{T}{T}has_variable = tv_wonder_ritual_in_progress",
        f"{T}{T}{T}{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}",
        f"{T}{T}{T}{T}{T}{T}var:tv_wonder_ceremony_style ?= {style}",
        f"{T}{T}{T}{T}{T}}}",
        f"{T}{T}{T}{T}{T}set_variable = {{ name = tv_wonder_ritual_auxiliary_building_finished value = 1 }}",
        f"{T}{T}{T}{T}{T}tv_wonder_complete_active_ritual_effect = yes",
        f"{T}{T}{T}{T}}}",
        f"{T}{T}{T}}}",
        f"{T}{T}}}",
    ]


def auxiliary_on_construction_ended_lines() -> list[str]:
    return [
        f"{T}{T}hidden_effect = {{",
        f"{T}{T}{T}owner = {{",
        f"{T}{T}{T}{T}tv_wonder_mechanics_mark_completed_auxiliary_building_ritual_effect = yes",
        f"{T}{T}{T}}}",
        f"{T}{T}}}",
    ]


def final_building_on_built_lines() -> list[str]:
    return [
        f"{T}{T}hidden_effect = {{",
        f"{T}{T}{T}location = {{",
        f"{T}{T}{T}{T}tv_wonder_mechanics_refresh_location_display_state_effect = yes",
        f"{T}{T}{T}}}",
        f"{T}{T}}}",
    ]


def final_building_on_destroyed_lines() -> list[str]:
    return [
        f"{T}{T}hidden_effect = {{",
        f"{T}{T}{T}location = {{",
        f"{T}{T}{T}{T}tv_wonder_mechanics_sync_location_final_building_level_map_from_buildings_effect = yes",
        f"{T}{T}{T}{T}tv_wonder_mechanics_refresh_location_display_state_effect = yes",
        f"{T}{T}{T}{T}owner ?= {{",
        f"{T}{T}{T}{T}{T}tv_wonder_mechanics_refresh_country_auto_level_map_effect = yes",
        f"{T}{T}{T}{T}}}",
        f"{T}{T}{T}}}",
        f"{T}{T}}}",
    ]


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        building_design = mechanics["buildings"][mechanic_key(wonder)]
        authored_local_modifiers = authored_final_building_local_modifiers(wonder, mechanics)
        base_country_modifiers = wonder_base_country_modifiers(wonder, mechanics)
        for style in ceremony_styles(wonder):
            building = final_building_for_style(wonder, style)
            modifiers = merge_modifiers(
                authored_local_modifiers,
                base_country_modifiers,
            )
            maintenance = final_building_maintenance(wonder, building_design, building)
            attributes = building_design.get("final_attributes", {}).get(building, {})
            lines.extend(
                building_block(
                    building,
                    wonder,
                    modifiers,
                    maintenance,
                    attributes=attributes,
                    on_built_lines=final_building_on_built_lines(),
                    on_destroyed_lines=final_building_on_destroyed_lines(),
                    can_destroy="yes",
                )
            )
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            if ritual_plan["mode"] != "auxiliary_building":
                continue
            build_time, construction_demand, price = build_profile(wonder)
            auxiliary = ritual_plan["auxiliary_building"]
            maintenance = auxiliary.get("maintenance") or building_design.get("maintenance", wonder["maintenance"])
            lines.extend(
                building_block(
                    ritual_auxiliary_building(wonder),
                    wonder,
                    ritual_auxiliary_modifiers(wonder, ritual_plan),
                    maintenance,
                    max_levels=auxiliary.get("max_levels", 6),
                    build_time=auxiliary.get("build_time") or build_time,
                    construction_demand=auxiliary.get("construction_demand") or construction_demand,
                    price=auxiliary.get("price") or price,
                    attributes=auxiliary.get("attributes", {}),
                    on_built_lines=auxiliary_on_built_lines(wonder, style),
                    on_construction_ended_lines=auxiliary_on_construction_ended_lines(),
                    can_destroy="yes",
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
