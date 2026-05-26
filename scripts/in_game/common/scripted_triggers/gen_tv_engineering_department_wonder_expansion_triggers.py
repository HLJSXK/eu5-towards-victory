import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_expansion_lib import NEW_WONDER_MAX_ID, NEW_WONDER_MIN_ID, load_wonder_data, render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_triggers" / "tv_engineering_department_wonder_expansion_triggers.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_expansion_triggers.py"
T = "\t"


def trigger_conditions(wonder: dict, indent: int = 1) -> list[str]:
    prefix = T * indent
    key = wonder["key"]
    lines: list[str] = []
    if key in {"large_canal_system", "giant_dam_project", "canal_hub_city"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}has_river = yes",
            f"{prefix}{T}is_adjacent_to_lake = yes",
            f"{prefix}{T}is_port = yes",
            f"{prefix}}}",
        ])
        if key == "canal_hub_city":
            lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:rural_settlement }}")
    elif key == "mountain_terrace_network":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}topography = mountains",
            f"{prefix}{T}topography = plateau",
            f"{prefix}{T}topography = hills",
            f"{prefix}}}",
        ])
    elif key in {"royal_granary_system", "imperial_post_road_network", "law_code_stele_project"}:
        lines.append(f"{prefix}always = yes")
    elif key == "frontier_colonization_belt":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}{T}location_rank ?= location_rank:rural_settlement",
            f"{prefix}{T}topography = hills",
            f"{prefix}}}",
        ])
    elif key in {"coastal_beacon_network", "maritime_trade_station_network"}:
        lines.append(f"{prefix}is_port = yes")
    elif key in {"knightly_fortress_order", "war_college_system", "great_clock_bell_system", "grand_theater_festival_district", "guild_alliance", "giant_workshop_complex"}:
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


def generate() -> str:
    wonders, _ = load_wonder_data()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        lines.append(f"tv_wonder_location_can_host_{wonder['key']}_trigger = {{")
        lines.extend(trigger_conditions(wonder))
        lines.append("}")
        lines.append("")
        lines.append(f"tv_wonder_can_build_{wonder['key']}_trigger = {{")
        lines.append(f"{T}any_owned_location = {{")
        lines.extend(trigger_conditions(wonder, 2))
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_new_has_any_feasible_proposal_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}has_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_has_valid_site_candidate_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}tv_wonder_can_build_{wonder['key']}_trigger = yes")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_location_can_host_new_locked_wonder_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}scope:actor = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}{T}tv_wonder_location_can_host_{wonder['key']}_trigger = yes")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_selected_survey_already_cached_trigger = {")
    lines.append(f"{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}AND = {{")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{wonder['key']} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_ceremony_ready_trigger = {")
    lines.append(f"{T}tv_wonder_has_selected_ceremony_trigger = yes")
    lines.append(f"{T}var:tv_wonder_locked ?= {{ this >= {NEW_WONDER_MIN_ID} }}")
    lines.append(f"{T}var:tv_wonder_locked ?= {{ this <= {NEW_WONDER_MAX_ID} }}")
    lines.append("}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
