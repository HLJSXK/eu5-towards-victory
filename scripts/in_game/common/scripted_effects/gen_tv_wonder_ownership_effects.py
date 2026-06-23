"""Generate Engineering Department wonder ownership-transfer effects."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.naming import (
    FINAL_BUILDING_LEVEL_BY_TYPE_MAP,
    ownership_gain_event_id,
    ownership_loss_event_id,
)
from wonder_mechanics.render import render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_wonder_ownership_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_wonder_ownership_effects.py"
T = "\t"

FINAL_BUILDING_WONDER_ID_MAP = "tv_wonder_final_building_type_to_wonder_id"
LOCATION_SURVEY_SCALE_TIER_MAP = "tv_wonder_survey_scale_tier"
PRIORITY_CANDIDATE_WONDER_ID_VAR = "tv_wonder_priority_candidate_wonder_id"
PRIORITY_CANDIDATE_CURRENT_MODE_VAR = "tv_wonder_priority_candidate_current_mode"
OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL = "tv_wonder_ownership_final_building_type"
OWNERSHIP_FINAL_BUILDING_LEVEL_VAR = "tv_wonder_ownership_final_building_level"
OWNERSHIP_SCALE_TIER_VAR = "tv_wonder_ownership_scale_tier"
OWNERSHIP_EVENT_WONDER_ID_VAR = "tv_wonder_ownership_event_wonder_id"
OWNERSHIP_LOSS_RETAINS_SAME_WONDER_VAR = "tv_wonder_ownership_loss_retains_same_wonder"
OWNERSHIP_TARGET_WONDER_ID_LOCAL = "tv_wonder_ownership_target_wonder_id"
OWNERSHIP_SCANNED_WONDER_ID_LOCAL = "tv_wonder_ownership_scanned_wonder_id"


def append_location_owner_changed_handler(lines: list[str]) -> None:
    lines.append("# Root: changed location. scope:winner is the new owner; scope:loser is the old owner.")
    lines.append("# Scans final-building maps so all non-event ownership work remains data-driven.")
    lines.append("tv_wonder_ownership_handle_location_owner_changed_effect = {")
    lines.append(f"{T}save_scope_as = tv_wonder_priority_site")
    lines.append(f"{T}save_scope_as = tv_wonder_ownership_site")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ has_global_variable_map = {FINAL_BUILDING_WONDER_ID_MAP} }}")
    lines.append(f"{T}{T}every_key_in_global_variable_map = {{")
    lines.append(f"{T}{T}{T}variable = {FINAL_BUILDING_WONDER_ID_MAP}")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}scope:tv_wonder_ownership_site = {{")
    lines.append(f"{T}{T}{T}{T}{T}has_variable_map = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP}")
    lines.append(
        f"{T}{T}{T}{T}{T}is_key_in_variable_map = {{ "
        f"name = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP} target = prev }}"
    )
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}scope:tv_wonder_ownership_site = {{")
    lines.append(
        f"{T}{T}{T}{T}set_local_variable = {{ "
        f"name = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL} value = prev }}"
    )
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ name = {OWNERSHIP_FINAL_BUILDING_LEVEL_VAR} "
        f"value = \"variable_map({FINAL_BUILDING_LEVEL_BY_TYPE_MAP}|local_var:{OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}{T}{T}remove_local_variable = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}scope:loser ?= {{")
    lines.append(
        f"{T}{T}{T}{T}set_local_variable = {{ "
        f"name = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL} value = prev }}"
    )
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ name = {PRIORITY_CANDIDATE_WONDER_ID_VAR} "
        f"value = \"global_variable_map({FINAL_BUILDING_WONDER_ID_MAP}|local_var:{OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}{T}{T}tv_wonder_unregister_current_site_priority_candidate_effect = yes")
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ "
        f"name = {OWNERSHIP_EVENT_WONDER_ID_VAR} value = var:{PRIORITY_CANDIDATE_WONDER_ID_VAR} }}"
    )
    lines.append(f"{T}{T}{T}{T}tv_wonder_ownership_trigger_loss_event_effect = yes")
    lines.append(f"{T}{T}{T}{T}remove_variable = {OWNERSHIP_EVENT_WONDER_ID_VAR}")
    lines.append(f"{T}{T}{T}{T}remove_variable = {PRIORITY_CANDIDATE_WONDER_ID_VAR}")
    lines.append(f"{T}{T}{T}{T}remove_local_variable = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}scope:winner ?= {{")
    lines.append(
        f"{T}{T}{T}{T}set_local_variable = {{ "
        f"name = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL} value = prev }}"
    )
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ name = {PRIORITY_CANDIDATE_WONDER_ID_VAR} "
        f"value = \"global_variable_map({FINAL_BUILDING_WONDER_ID_MAP}|local_var:{OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}{T}{T}tv_wonder_unregister_current_site_priority_candidate_effect = yes")
    lines.append(f"{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}scope:tv_wonder_ownership_site = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}has_variable_map = {LOCATION_SURVEY_SCALE_TIER_MAP}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}is_key_in_variable_map = {{ "
        f"name = {LOCATION_SURVEY_SCALE_TIER_MAP} target = prev.var:{PRIORITY_CANDIDATE_WONDER_ID_VAR} }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}scope:tv_wonder_ownership_site = {{")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}set_variable = {{ name = {OWNERSHIP_SCALE_TIER_VAR} "
        f"value = \"variable_map({LOCATION_SURVEY_SCALE_TIER_MAP}|prev.var:{PRIORITY_CANDIDATE_WONDER_ID_VAR})\" }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}scope:tv_wonder_ownership_site = {{")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}{T}var:{OWNERSHIP_SCALE_TIER_VAR} > "
        f"var:{OWNERSHIP_FINAL_BUILDING_LEVEL_VAR}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}set_variable = {{ "
        f"name = {PRIORITY_CANDIDATE_CURRENT_MODE_VAR} value = 2 }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}tv_wonder_register_current_priority_candidate_effect = yes")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}scope:tv_wonder_ownership_site = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}remove_variable = {OWNERSHIP_SCALE_TIER_VAR}")
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}{T}set_variable = {{ "
        f"name = {OWNERSHIP_EVENT_WONDER_ID_VAR} value = var:{PRIORITY_CANDIDATE_WONDER_ID_VAR} }}"
    )
    lines.append(f"{T}{T}{T}{T}tv_wonder_ownership_trigger_gain_event_effect = yes")
    lines.append(f"{T}{T}{T}{T}remove_variable = {OWNERSHIP_EVENT_WONDER_ID_VAR}")
    lines.append(f"{T}{T}{T}{T}remove_variable = {PRIORITY_CANDIDATE_WONDER_ID_VAR}")
    lines.append(f"{T}{T}{T}{T}remove_variable = {PRIORITY_CANDIDATE_CURRENT_MODE_VAR}")
    lines.append(f"{T}{T}{T}{T}remove_local_variable = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}scope:tv_wonder_ownership_site = {{")
    lines.append(f"{T}{T}{T}{T}remove_variable = {OWNERSHIP_FINAL_BUILDING_LEVEL_VAR}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_event_dispatch_effects(lines: list[str], all_wonders: list[dict]) -> None:
    lines.append("# Intentional per-wonder dispatch: events need static ids and static images.")
    lines.append("tv_wonder_ownership_trigger_gain_event_effect = {")
    for index, wonder in enumerate(all_wonders):
        head = "if" if index == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:{OWNERSHIP_EVENT_WONDER_ID_VAR} ?= {int(wonder['id'])} }}")
        lines.append(
            f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{ownership_gain_event_id(wonder)} }}"
        )
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append("# Intentional per-wonder dispatch: events need static ids and static images.")
    lines.append("tv_wonder_ownership_trigger_loss_event_effect = {")
    for index, wonder in enumerate(all_wonders):
        head = "if" if index == 0 else "else_if"
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:{OWNERSHIP_EVENT_WONDER_ID_VAR} ?= {int(wonder['id'])} }}")
        lines.append(
            f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{ownership_loss_event_id(wonder)} }}"
        )
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_loss_retention_probe(lines: list[str]) -> None:
    lines.append("# Root: losing country. Reads tv_wonder_ownership_event_wonder_id and writes a result flag.")
    lines.append("# This is an effect because safe map-driven comparison needs local-variable captures.")
    lines.append("tv_wonder_ownership_compute_loss_retains_same_wonder_effect = {")
    lines.append(f"{T}save_scope_as = tv_wonder_ownership_loss_country")
    lines.append(f"{T}remove_variable = {OWNERSHIP_LOSS_RETAINS_SAME_WONDER_VAR}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ has_global_variable_map = {FINAL_BUILDING_WONDER_ID_MAP} }}")
    lines.append(
        f"{T}{T}set_local_variable = {{ "
        f"name = {OWNERSHIP_TARGET_WONDER_ID_LOCAL} value = var:{OWNERSHIP_EVENT_WONDER_ID_VAR} }}"
    )
    lines.append(f"{T}{T}every_owned_location = {{")
    lines.append(f"{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}OR = {{")
    lines.append(f"{T}{T}{T}{T}{T}NOT = {{ exists = scope:tv_wonder_ownership_site }}")
    lines.append(f"{T}{T}{T}{T}{T}NOT = {{ this = scope:tv_wonder_ownership_site }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}save_scope_as = tv_wonder_ownership_other_site")
    lines.append(f"{T}{T}{T}every_key_in_global_variable_map = {{")
    lines.append(f"{T}{T}{T}{T}variable = {FINAL_BUILDING_WONDER_ID_MAP}")
    lines.append(f"{T}{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}{T}scope:tv_wonder_ownership_other_site = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}has_variable_map = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}is_key_in_variable_map = {{ "
        f"name = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP} target = prev }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}scope:tv_wonder_ownership_loss_country = {{")
    lines.append(
        f"{T}{T}{T}{T}{T}set_local_variable = {{ "
        f"name = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL} value = prev }}"
    )
    lines.append(
        f"{T}{T}{T}{T}{T}set_local_variable = {{ name = {OWNERSHIP_SCANNED_WONDER_ID_LOCAL} "
        f"value = \"global_variable_map({FINAL_BUILDING_WONDER_ID_MAP}|local_var:{OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL})\" }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}{T}limit = {{")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}NOT = {{ "
        f"local_var:{OWNERSHIP_SCANNED_WONDER_ID_LOCAL} < local_var:{OWNERSHIP_TARGET_WONDER_ID_LOCAL} }}"
    )
    lines.append(
        f"{T}{T}{T}{T}{T}{T}{T}NOT = {{ "
        f"local_var:{OWNERSHIP_SCANNED_WONDER_ID_LOCAL} > local_var:{OWNERSHIP_TARGET_WONDER_ID_LOCAL} }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}{T}{T}{T}set_variable = {{ "
        f"name = {OWNERSHIP_LOSS_RETAINS_SAME_WONDER_VAR} value = 1 }}"
    )
    lines.append(f"{T}{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}{T}remove_local_variable = {OWNERSHIP_SCANNED_WONDER_ID_LOCAL}")
    lines.append(f"{T}{T}{T}{T}{T}remove_local_variable = {OWNERSHIP_FINAL_BUILDING_TYPE_LOCAL}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}remove_local_variable = {OWNERSHIP_TARGET_WONDER_ID_LOCAL}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    all_wonders, _mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    lines.append("# Wonder ownership-transfer lifecycle.")
    lines.append("# Keep event dispatch static; keep final-building detection and cache updates map-driven.")
    lines.append("")
    append_location_owner_changed_handler(lines)
    append_event_dispatch_effects(lines, all_wonders)
    append_loss_retention_probe(lines)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
