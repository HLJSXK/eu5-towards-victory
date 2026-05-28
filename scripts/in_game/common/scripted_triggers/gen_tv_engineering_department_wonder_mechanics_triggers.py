import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ALL_WONDER_MAX_ID,
    ALL_WONDER_MIN_ID,
    PARTS,
    load_all_wonder_mechanics,
    mechanic_key,
    render_header,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_triggers" / "tv_engineering_department_wonder_mechanics_triggers.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py"
T = "\t"


def trigger_conditions(wonder: dict, indent: int = 1) -> list[str]:
    prefix = T * indent
    key = mechanic_key(wonder)
    lines: list[str] = []
    if key in {"sacred_mountain", "giant_observatory", "mountain_terrace_network"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}topography = mountains",
            f"{prefix}{T}topography = plateau",
            f"{prefix}{T}topography = hills",
            f"{prefix}}}",
        ])
    elif key == "triumphal_axis":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}location_rank ?= location_rank:city",
            f"{prefix}{T}location_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    elif key in {"great_port", "great_lighthouse", "national_shipyard", "coastal_beacon_network", "maritime_trade_station_network"}:
        lines.append(f"{prefix}is_port = yes")
    elif key == "giant_necropolis":
        lines.append(f"{prefix}location_rank ?= location_rank:rural_settlement")
    elif key in {"hydraulic_workshop", "river_extension"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}has_river = yes",
            f"{prefix}{T}is_adjacent_to_lake = yes",
            f"{prefix}}}",
        ])
    elif key == "mining_city":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}raw_material = goods:iron",
            f"{prefix}{T}raw_material = goods:copper",
            f"{prefix}{T}raw_material = goods:tin",
            f"{prefix}{T}raw_material = goods:lead",
            f"{prefix}{T}raw_material = goods:silver",
            f"{prefix}{T}raw_material = goods:goods_gold",
            f"{prefix}}}",
        ])
    elif key in {"palace_of_nations", "library_of_nation"}:
        lines.append(f"{prefix}is_capital = yes")
    elif key in {"university_city", "star_fortress_city", "giant_armory", "war_college_system", "great_clock_bell_system", "grand_theater_festival_district", "guild_alliance", "giant_workshop_complex"}:
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:rural_settlement }}")
    elif key == "sky_dome_grand_temple":
        lines.append(f"{prefix}dominant_religion = owner.religion")
    elif key == "giant_tower_temple":
        lines.append(f"{prefix}always = yes")
    elif key == "great_wall":
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:city }}")
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:megalopolis }}")
    elif key in {"large_canal_system", "giant_dam_project", "canal_hub_city"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}has_river = yes",
            f"{prefix}{T}is_adjacent_to_lake = yes",
            f"{prefix}{T}is_port = yes",
            f"{prefix}}}",
        ])
        if key == "canal_hub_city":
            lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:rural_settlement }}")
    elif key in {"royal_granary_system", "imperial_post_road_network", "law_code_stele_project"}:
        lines.append(f"{prefix}always = yes")
    elif key == "frontier_colonization_belt":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}location_rank ?= location_rank:rural_settlement",
            f"{prefix}{T}topography = hills",
            f"{prefix}}}",
        ])
    elif key == "knightly_fortress_order":
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:rural_settlement }}")
    elif key == "royal_art_district":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}is_capital = yes",
            f"{prefix}{T}location_rank ?= location_rank:city",
            f"{prefix}{T}location_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    elif key == "world_embassy_quarter":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}is_capital = yes",
            f"{prefix}{T}NOT = {{ location_rank ?= location_rank:rural_settlement }}",
            f"{prefix}}}",
        ])
    elif key == "world_market":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}is_port = yes",
            f"{prefix}{T}location_rank ?= location_rank:city",
            f"{prefix}{T}location_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    elif key == "royal_mint_system":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}location_rank ?= location_rank:city",
            f"{prefix}{T}location_rank ?= location_rank:megalopolis",
            f"{prefix}{T}raw_material = goods:goods_gold",
            f"{prefix}{T}raw_material = goods:silver",
            f"{prefix}{T}raw_material = goods:copper",
            f"{prefix}}}",
        ])
    elif key == "world_monument_group":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}is_capital = yes",
            f"{prefix}{T}location_rank ?= location_rank:city",
            f"{prefix}{T}location_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    else:
        raise ValueError(f"No site trigger mapping for {key}")
    return lines


def building_or_block(buildings: list[str], indent: int) -> list[str]:
    prefix = T * indent
    lines = [f"{prefix}OR = {{"]
    for building in buildings:
        lines.append(f"{prefix}{T}has_building = building_type:{building}")
    lines.append(f"{prefix}}}")
    return lines


def intermediate_buildings(wonder: dict) -> list[str]:
    key = wonder["key"]
    return [f"tv_wonder_{key}", *[f"tv_wonder_{key}_{part}" for part in PARTS]]


def final_buildings(wonder: dict) -> list[str]:
    return list(dict.fromkeys(wonder["final_buildings"].values()))


def project_buildings(wonder: dict) -> list[str]:
    return [*intermediate_buildings(wonder), *final_buildings(wonder)]


def loc_level(building: str, op: str, level: int) -> str:
    return f"location_building_level = {{ building_type = building_type:{building} value {op} {level} }}"


def final_building_level_exact(building: str, level: int, indent: int) -> list[str]:
    prefix = T * indent
    lines = [f"{prefix}{loc_level(building, '>=', level)}"]
    if level < 6:
        lines.append(f"{prefix}NOT = {{ {loc_level(building, '>=', level + 1)} }}")
    return lines


def stored_tier_can_expand(wonder: dict, final_building: str, level: int, indent: int) -> list[str]:
    prefix = T * indent
    tier_var = f"tv_wonder_{wonder['key']}_scale_tier"
    lines = final_building_level_exact(final_building, level, indent)
    lines.append(f"{prefix}OR = {{")
    lines.append(f"{prefix}{T}var:{tier_var} ?= {{ this >= {level + 1} }}")
    lines.append(f"{prefix}{T}NOT = {{ has_variable = {tier_var} }}")
    lines.append(f"{prefix}}}")
    return lines


def final_building_below_cap_conditions(wonder: dict, indent: int) -> list[str]:
    prefix = T * indent
    lines = [f"{prefix}OR = {{"]
    for final_building in final_buildings(wonder):
        for level in range(1, 6):
            lines.append(f"{prefix}{T}AND = {{")
            lines.extend(stored_tier_can_expand(wonder, final_building, level, indent + 2))
            lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
    return lines


def add_project_occupancy_triggers(lines: list[str], wonders: list[dict]) -> None:
    for wonder in wonders:
        key = wonder["key"]
        lines.append(f"tv_wonder_location_has_{key}_intermediate_building_trigger = {{")
        lines.extend(building_or_block(intermediate_buildings(wonder), 1))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_location_has_{key}_final_building_trigger = {{")
        lines.extend(building_or_block(final_buildings(wonder), 1))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_location_has_{key}_project_building_trigger = {{")
        lines.extend(building_or_block(project_buildings(wonder), 1))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_location_has_{key}_expandable_final_building_trigger = {{")
        lines.extend(final_building_below_cap_conditions(wonder, 1))
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_location_has_any_wonder_final_building_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}tv_wonder_location_has_{wonder['key']}_final_building_trigger = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_has_any_wonder_project_building_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}tv_wonder_location_has_{wonder['key']}_project_building_trigger = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_has_locked_wonder_intermediate_building_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}prev = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}{T}tv_wonder_location_has_{wonder['key']}_intermediate_building_trigger = yes")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_has_locked_wonder_expandable_final_building_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}prev = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}{T}tv_wonder_location_has_{wonder['key']}_expandable_final_building_trigger = yes")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_is_valid_priority_project_for_locked_wonder_trigger = {")
    lines.append(f"{T}OR = {{")
    lines.append(f"{T}{T}AND = {{")
    lines.append(f"{T}{T}{T}tv_wonder_location_has_locked_wonder_intermediate_building_trigger = yes")
    lines.append(f"{T}{T}{T}NOT = {{ tv_wonder_location_has_any_wonder_final_building_trigger = yes }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_location_has_locked_wonder_expandable_final_building_trigger = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    all_wonders, _ = load_all_wonder_mechanics()
    generic_wonders = [wonder for wonder in all_wonders if not wonder.get("is_unique")]
    unique_wonders = [wonder for wonder in all_wonders if wonder.get("is_unique")]
    lines = render_header(SCRIPT_REL)
    add_project_occupancy_triggers(lines, all_wonders)
    for wonder in all_wonders:
        lines.append(f"tv_wonder_location_can_host_{wonder['key']}_trigger = {{")
        lines.append(f"{T}NOT = {{ tv_wonder_location_has_any_wonder_project_building_trigger = yes }}")
        if wonder.get("is_unique"):
            lines.append(f"{T}this = location:{wonder['fixed_location']}")
        lines.extend(trigger_conditions(wonder))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_can_build_{wonder['key']}_trigger = {{")
        if wonder.get("is_unique"):
            lines.append(f"{T}owns = location:{wonder['fixed_location']}")
            lines.append(f"{T}location:{wonder['fixed_location']} = {{")
            lines.append(f"{T}{T}NOT = {{ tv_wonder_location_has_any_wonder_project_building_trigger = yes }}")
            lines.extend(trigger_conditions(wonder, 2))
            lines.append(f"{T}}}")
        else:
            lines.append(f"{T}any_owned_location = {{")
            lines.append(f"{T}{T}NOT = {{ tv_wonder_location_has_any_wonder_project_building_trigger = yes }}")
            lines.extend(trigger_conditions(wonder, 2))
            lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_mechanics_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in all_wonders:
        lines.append(f"{T}{T}has_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_generic_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in generic_wonders:
        lines.append(f"{T}{T}has_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_unique_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in unique_wonders:
        lines.append(f"{T}{T}has_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_has_valid_site_candidate_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in all_wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}tv_wonder_can_build_{wonder['key']}_trigger = yes")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_can_host_locked_wonder_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in all_wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}scope:actor = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}{T}tv_wonder_location_can_host_{wonder['key']}_trigger = yes")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_selected_survey_already_cached_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in all_wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{wonder['key']} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_ceremony_ready_for_confirmation_trigger = {")
    lines.append(f"{T}tv_wonder_has_selected_ceremony_trigger = yes")
    lines.append(f"{T}OR = {{")
    lines.append(f"{T}{T}AND = {{")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this >= {ALL_WONDER_MIN_ID} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this <= {ALL_WONDER_MAX_ID} }}")
    lines.append(f"{T}{T}}}")
    for wonder in all_wonders:
        if wonder.get("is_unique"):
            lines.append(f"{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_unique_locked_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in all_wonders:
        if wonder.get("is_unique"):
            lines.append(f"{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
