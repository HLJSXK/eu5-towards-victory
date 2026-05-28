import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ALL_WONDER_MIN_ID,
    WONDER_MECHANICS_MAX_ID,
    ceremony_modifier_for_style,
    ceremony_styles,
    final_building_for_style,
    load_all_wonder_mechanics,
    mechanic_key,
    render_header,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_engineering_department_wonder_mechanics_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py"
T = "\t"


def add_site_preference(wonder: dict, indent: int = 2) -> list[str]:
    key = mechanic_key(wonder)
    prefix = T * indent
    lines: list[str] = []
    def bonus(value: str | int | float) -> None:
        lines.append(f"{prefix}tv_wonder_change_all_survey_competence_target_effect = {{ value = {value} }}")

    if key == "sacred_mountain":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = hills }} }}")
        bonus(0)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ vegetation = forest }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ vegetation = woods }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key in {"triumphal_axis", "palace_of_nations"}:
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.2 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:megalopolis }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key in {"great_port", "great_lighthouse"}:
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.modifier:harbor_suitability }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 1 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 25 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "giant_necropolis":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = hills }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ any_neighbor_location = {{ tv_wonder_location_is_city_trigger = yes }} }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ any_neighbor_location = {{ tv_wonder_location_is_town_trigger = yes }} }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key == "hydraulic_workshop":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.total_building_levels }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.25 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "mining_city":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.2 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:rural_settlement }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "giant_observatory":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.average_location_literacy }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "university_city":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:city }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:megalopolis }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.average_location_literacy }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.2 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key in {"sky_dome_grand_temple", "giant_tower_temple"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:monastery }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:cathedral }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ dominant_religion = owner.religion }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
    elif key == "river_extension":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:bridge_infrastructure }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ any_neighbor_location = {{ has_building = building_type:tv_wonder_bridge_opening }} }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "national_shipyard":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.modifier:harbor_suitability }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 1 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 15 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "star_fortress_city":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ modifier:fort_level > 0 }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ location_rank ?= location_rank:city location_rank ?= location_rank:megalopolis }} }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key == "great_wall":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ modifier:fort_level > 0 }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:rural_settlement }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key == "giant_armory":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:armory }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ location_rank ?= location_rank:city location_rank ?= location_rank:megalopolis }} }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.15 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "library_of_nation":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.15 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:city }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:megalopolis }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key in {"large_canal_system", "giant_dam_project", "canal_hub_city"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ has_river = yes is_adjacent_to_lake = yes is_port = yes }} }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        if key == "canal_hub_city":
            lines.append(f"{prefix}if = {{")
            lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ location_rank ?= location_rank:city location_rank ?= location_rank:megalopolis }} }} }}")
            bonus(5)
            lines.append(f"{prefix}}}")
    elif key == "mountain_terrace_network":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = hills }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key in {"royal_granary_system", "frontier_colonization_belt"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:rural_settlement }} }}")
        bonus(10 if key == "frontier_colonization_belt" else 5)
        lines.append(f"{prefix}}}")
    elif key in {"coastal_beacon_network", "maritime_trade_station_network"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ is_port = yes }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
    elif key == "knightly_fortress_order":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ modifier:fort_level > 0 }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
    elif key == "royal_mint_system":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ raw_material = goods:goods_gold raw_material = goods:silver raw_material = goods:copper }} }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
    elif key in {"royal_art_district", "world_embassy_quarter", "law_code_stele_project", "world_monument_group"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}{T}limit = {{ var:tv_wonder_survey_site ?= {{ is_capital = yes }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")

    if key not in {
        "sacred_mountain",
        "triumphal_axis",
        "great_port",
        "giant_necropolis",
        "great_lighthouse",
        "hydraulic_workshop",
        "mining_city",
        "giant_observatory",
        "palace_of_nations",
        "university_city",
        "sky_dome_grand_temple",
        "giant_tower_temple",
        "river_extension",
        "national_shipyard",
        "star_fortress_city",
        "great_wall",
        "giant_armory",
        "library_of_nation",
        "mountain_terrace_network",
        "coastal_beacon_network",
        "maritime_trade_station_network",
    }:
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    if wonder.get("is_unique"):
        lines.append(f"{prefix}tv_wonder_change_scale_competence_target_effect = {{ value = 100 }}")
        lines.append(f"{prefix}tv_wonder_change_logistics_competence_target_effect = {{ value = 20 }}")
        lines.append(f"{prefix}tv_wonder_change_organization_competence_target_effect = {{ value = 20 }}")
    return lines


def generate() -> str:
    all_wonders, mechanics = load_all_wonder_mechanics()
    generic_wonders = [wonder for wonder in all_wonders if not wonder.get("is_unique")]
    unique_wonders = [wonder for wonder in all_wonders if wonder.get("is_unique")]
    lines = render_header(SCRIPT_REL)

    lines.append("tv_wonder_mechanics_clear_feasible_deck_effect = {")
    for wonder in all_wonders:
        lines.append(f"{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_rebuild_feasible_deck_effect = {")
    for wonder in all_wonders:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ tv_wonder_can_build_{wonder['key']}_trigger = yes }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_feasible_{wonder['key']} value = 1 }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_generic_roll_random_feasible_proposal_effect = {")
    lines.append(f"{T}random_list = {{")
    for wonder in generic_wonders:
        lines.append(f"{T}{T}1 = {{")
        lines.append(f"{T}{T}{T}trigger = {{ has_variable = tv_wonder_feasible_{wonder['key']} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_proposal value = {wonder['id']} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_unique_roll_random_feasible_proposal_effect = {")
    lines.append(f"{T}random_list = {{")
    for wonder in unique_wonders:
        lines.append(f"{T}{T}1 = {{")
        lines.append(f"{T}{T}{T}trigger = {{ has_variable = tv_wonder_feasible_{wonder['key']} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_proposal value = {wonder['id']} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_roll_next_slot_from_priority_deck_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_unique_has_any_feasible_proposal_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_unique_roll_random_feasible_proposal_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_generic_has_any_feasible_proposal_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_generic_roll_random_feasible_proposal_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_remove_current_proposal_from_deck_effect = {")
    for wonder in all_wonders:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_proposal ?= {wonder['id']} }}")
        lines.append(f"{T}{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_accept_proposal_tooltip_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_proposal ?= {wonder['id']} }}")
        lines.append(f"{T}{T}custom_tooltip = {{ text = TV_WONDER_LOCK_{wonder['key'].upper()}_TT }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    for wonder in all_wonders:
        key = wonder["key"]
        lines.append(f"tv_wonder_copy_{key}_survey_from_location_effect = {{")
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ exists = scope:tv_wonder_selected_survey_site }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_scale_competence value = scope:tv_wonder_selected_survey_site.var:tv_wonder_{key}_scale_competence }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_logistics_competence value = scope:tv_wonder_selected_survey_site.var:tv_wonder_{key}_logistics_competence }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_organization_competence value = scope:tv_wonder_selected_survey_site.var:tv_wonder_{key}_organization_competence }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_complete value = 1 }}")
        lines.append(f"{T}{T}remove_variable = tv_wonder_survey_active")
        lines.append(f"{T}{T}tv_wonder_set_io_survey_progress_effect = {{ value = 100 }}")
        lines.append(f"{T}{T}tv_wonder_update_construction_tiers_from_competence_effect = yes")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")

    lines.append("tv_wonder_mechanics_copy_completed_survey_from_location_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        key = wonder["key"]
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}exists = scope:tv_wonder_selected_survey_site")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{key} }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}tv_wonder_copy_{key}_survey_from_location_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_store_survey_on_location_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        key = wonder["key"]
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}tv_wonder_survey_site_selected_trigger = yes")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}{T}var:tv_wonder_survey_site ?= {{")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_surveyed_{key} value = 1 }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_scale_competence value = prev.var:tv_wonder_scale_competence }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_logistics_competence value = prev.var:tv_wonder_logistics_competence }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_organization_competence value = prev.var:tv_wonder_organization_competence }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_{key}_scale_tier value = prev.var:tv_wonder_scale_tier }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_survey_site_preference_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{")
        lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
        lines.append(f"{T}{T}{T}tv_wonder_survey_site_selected_trigger = yes")
        lines.append(f"{T}{T}}}")
        lines.extend(add_site_preference(wonder, 2))
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_selected_survey_already_cached_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}OR = {{")
    for wonder in all_wonders:
        lines.append(f"{T}{T}{T}{T}AND = {{ var:tv_wonder_locked ?= {wonder['id']} scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{wonder['key']} }} }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_copy_completed_survey_from_location_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_start_survey_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}exists = scope:target")
    lines.append(f"{T}{T}{T}scope:target = {{ NOT = {{ tv_wonder_location_has_any_wonder_project_building_trigger = yes }} }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_clear_current_survey_effect = yes")
    lines.append(f"{T}{T}scope:target = {{ save_scope_as = tv_wonder_selected_survey_site }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_site value = scope:target }}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_stage value = 2 }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_selected_survey_already_cached_trigger = yes }}")
    lines.append(f"{T}{T}{T}tv_wonder_copy_completed_survey_from_location_effect = yes")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else = {{")
    lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_survey_active value = 1 }}")
    lines.append(f"{T}{T}{T}tv_wonder_prepare_survey_competence_targets_effect = yes")
    lines.append(f"{T}{T}{T}tv_wonder_set_io_survey_progress_effect = {{ value = 0 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_complete_survey_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_survey_active_trigger = yes }}")
    lines.append(f"{T}{T}clamp_variable = {{ name = tv_wonder_scale_competence min = 0 max = 100 }}")
    lines.append(f"{T}{T}clamp_variable = {{ name = tv_wonder_logistics_competence min = 0 max = 100 }}")
    lines.append(f"{T}{T}clamp_variable = {{ name = tv_wonder_organization_competence min = 0 max = 100 }}")
    lines.append(f"{T}{T}tv_wonder_update_construction_tiers_from_competence_effect = yes")
    lines.append(f"{T}{T}tv_wonder_store_survey_on_location_effect = yes")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_complete value = 1 }}")
    lines.append(f"{T}{T}remove_variable = tv_wonder_survey_active")
    lines.append(f"{T}{T}remove_variable = tv_wonder_survey_speed")
    lines.append(f"{T}{T}remove_variable = tv_wonder_scale_competence_target")
    lines.append(f"{T}{T}remove_variable = tv_wonder_logistics_competence_target")
    lines.append(f"{T}{T}remove_variable = tv_wonder_organization_competence_target")
    lines.append(f"{T}{T}remove_variable = tv_wonder_scale_competence_monthly_gain")
    lines.append(f"{T}{T}remove_variable = tv_wonder_logistics_competence_monthly_gain")
    lines.append(f"{T}{T}remove_variable = tv_wonder_organization_competence_monthly_gain")
    lines.append(f"{T}{T}tv_wonder_set_io_survey_progress_effect = {{ value = 100 }}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ tv_wonder_survey_site_selected_trigger = yes }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_survey_site ?= {{ save_scope_as = tv_wonder_event_location }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_survey_competence_average value = var:tv_wonder_scale_competence }}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_survey_competence_average add = var:tv_wonder_logistics_competence }}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_survey_competence_average add = var:tv_wonder_organization_competence }}")
    lines.append(f"{T}{T}change_variable = {{ name = tv_wonder_survey_competence_average divide = 3 }}")
    lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.300 }}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_base_modifier_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        for level in range(1, 7):
            level_head = "if" if level == 1 else "else_if"
            lines.append(f"{T}{T}{level_head} = {{ limit = {{ var:tv_wonder_level ?= {level} }} add_country_modifier = {{ modifier = tv_wonder_{wonder['key']}_level_{level} years = -1 mode = add_and_extend }} }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_apply_ceremony_modifier_effect = {")
    first = True
    for wonder in all_wonders:
        for style in ceremony_styles(wonder):
            ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
            if ceremony_modifier is None:
                continue
            modifier_name, _ = ceremony_modifier
            head = "if" if first else "else_if"
            first = False
            lines.append(f"{T}{head} = {{")
            lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
            lines.append(f"{T}{T}add_country_modifier = {{ modifier = {modifier_name} years = -1 mode = add_and_extend }}")
            lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_construct_final_building_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}tv_wonder_construction_site_selected_trigger = yes")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this >= {ALL_WONDER_MIN_ID} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this <= {WONDER_MECHANICS_MAX_ID} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_ceremony_style ?= {{ this >= 1 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_ceremony_style ?= {{ this <= 3 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this >= 1 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this <= 6 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}var:tv_wonder_site ?= {{")
    first = True
    for wonder in all_wonders:
        for style in ceremony_styles(wonder):
            building = final_building_for_style(wonder, style)
            head = "if" if first else "else_if"
            first = False
            lines.append(f"{T}{T}{T}{head} = {{")
            lines.append(f"{T}{T}{T}{T}limit = {{ prev = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }} }}")
            lines.append(f"{T}{T}{T}{T}prev = {{ set_variable = {{ name = tv_wonder_final_building value = {wonder['id']}{style:02d} }} }}")
            lines.append(f"{T}{T}{T}{T}tv_wonder_construct_final_building_in_site_effect = {{ building = building_type:{building} }}")
            lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_broadcast_completion_event_effect = {")
    for idx, wonder in enumerate(all_wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}save_scope_as = tv_wonder_completed_{wonder['key']}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_confirm_ceremony_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_ceremony_ready_for_confirmation_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_finalize_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_mechanics_clear_project_state_effect = {")
    for wonder in all_wonders:
        lines.append(f"{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append("}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
