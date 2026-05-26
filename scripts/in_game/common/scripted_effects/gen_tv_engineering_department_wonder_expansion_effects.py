import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_expansion_lib import NEW_WONDER_MAX_ID, NEW_WONDER_MIN_ID, final_building_for_style, load_wonder_data, render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_engineering_department_wonder_expansion_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_expansion_effects.py"
T = "\t"


def add_site_preference(wonder: dict, indent: int = 2) -> list[str]:
    key = wonder["key"]
    prefix = T * indent
    lines: list[str] = []
    def bonus(value: str | int | float) -> None:
        lines.append(f"{prefix}tv_wonder_change_all_survey_competence_target_effect = {{ value = {value} }}")

    if key in {"large_canal_system", "giant_dam_project", "canal_hub_city"}:
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

    if key not in {"mountain_terrace_network", "coastal_beacon_network", "maritime_trade_station_network"}:
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    return lines


def generate() -> str:
    wonders, _ = load_wonder_data()
    lines = render_header(SCRIPT_REL)

    lines.append("tv_wonder_new_clear_feasible_deck_effect = {")
    for wonder in wonders:
        lines.append(f"{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_rebuild_feasible_deck_effect = {")
    for wonder in wonders:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ tv_wonder_can_build_{wonder['key']}_trigger = yes }}")
        lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_feasible_{wonder['key']} value = 1 }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_roll_random_feasible_proposal_effect = {")
    lines.append(f"{T}random_list = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}1 = {{")
        lines.append(f"{T}{T}{T}trigger = {{ has_variable = tv_wonder_feasible_{wonder['key']} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_proposal value = {wonder['id']} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_remove_current_proposal_from_deck_effect = {")
    for wonder in wonders:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_proposal ?= {wonder['id']} }}")
        lines.append(f"{T}{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_accept_proposal_tooltip_effect = {")
    for idx, wonder in enumerate(wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_proposal ?= {wonder['id']} }}")
        lines.append(f"{T}{T}custom_tooltip = {{ text = TV_WONDER_LOCK_{wonder['key'].upper()}_TT }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    for wonder in wonders:
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

    lines.append("tv_wonder_new_copy_completed_survey_from_location_effect = {")
    for idx, wonder in enumerate(wonders):
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

    lines.append("tv_wonder_new_store_survey_on_location_effect = {")
    for idx, wonder in enumerate(wonders):
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

    lines.append("tv_wonder_new_apply_survey_site_preference_effect = {")
    for idx, wonder in enumerate(wonders):
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

    lines.append("tv_wonder_new_selected_survey_already_cached_trigger_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}OR = {{")
    for wonder in wonders:
        lines.append(f"{T}{T}{T}{T}AND = {{ var:tv_wonder_locked ?= {wonder['id']} scope:tv_wonder_selected_survey_site = {{ has_variable = tv_wonder_surveyed_{wonder['key']} }} }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}tv_wonder_copy_completed_survey_from_location_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_apply_base_modifier_effect = {")
    for idx, wonder in enumerate(wonders):
        head = "if" if idx == 0 else "else_if"
        key = wonder["key"]
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        for level in range(1, 7):
            level_head = "if" if level == 1 else "else_if"
            lines.append(f"{T}{T}{level_head} = {{ limit = {{ var:tv_wonder_level ?= {level} }} add_country_modifier = {{ modifier = tv_wonder_{key}_level_{level} years = -1 mode = add_and_extend }} }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_apply_ceremony_modifier_effect = {")
    first = True
    for wonder in wonders:
        for style in range(1, 4):
            building = final_building_for_style(wonder, style)
            head = "if" if first else "else_if"
            first = False
            lines.append(f"{T}{head} = {{")
            lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {style} }}")
            lines.append(f"{T}{T}add_country_modifier = {{ modifier = {building}_modifier years = -1 mode = add_and_extend }}")
            lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_construct_final_building_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}tv_wonder_construction_site_selected_trigger = yes")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this >= {NEW_WONDER_MIN_ID} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {{ this <= {NEW_WONDER_MAX_ID} }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_ceremony_style ?= {{ this >= 1 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_ceremony_style ?= {{ this <= 3 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this >= 1 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this <= 6 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}var:tv_wonder_site ?= {{")
    first = True
    for wonder in wonders:
        for style in range(1, 4):
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

    lines.append("tv_wonder_new_broadcast_completion_event_effect = {")
    for idx, wonder in enumerate(wonders):
        head = "if" if idx == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}save_scope_as = tv_wonder_completed_{wonder['key']}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_confirm_ceremony_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_new_ceremony_ready_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_finalize_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("tv_wonder_new_clear_project_state_effect = {")
    for wonder in wonders:
        lines.append(f"{T}remove_variable = tv_wonder_feasible_{wonder['key']}")
    lines.append("}")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
