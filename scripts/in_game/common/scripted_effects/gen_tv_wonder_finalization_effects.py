"""Generate Engineering Department wonder finalization effects."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.naming import (
    FINAL_BUILDING_LEVEL_BY_TYPE_MAP,
    construct_final_building_effect_name,
    finalization_event_id,
    finalization_hidden_event_execute_effect_name,
    finalization_hidden_event_id,
    finalization_hidden_event_trigger_effect_name,
    finalization_hidden_effect_name,
    finalization_visible_effect_name,
    finalization_world_event_id,
)
from wonder_mechanics.render import render_header
from wonder_mechanics.rituals import ceremony_styles

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_wonder_finalization_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_wonder_finalization_effects.py"
T = "\t"

def building_type_ref(building: str) -> str:
    return building if building.startswith("building_type:") else f"building_type:{building}"


def loc_level(building: str, op: str, level: int) -> str:
    return f"location_building_level = {{ building_type = {building_type_ref(building)} value {op} {level} }}"


def change_level_lines(building: str, value: int, indent: int) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}change_building_level_in_location = {{",
        f"{prefix}{T}building = {building_type_ref(building)}",
        f"{prefix}{T}value = {value}",
        f"{prefix}{T}owner = prev",
        f"{prefix}}}",
    ]


def append_store_final_building_level(lines: list[str], building: str, level: str, indent: int) -> None:
    prefix = T * indent
    building_type = building_type_ref(building)
    lines.append(f"{prefix}remove_from_variable_map = {{ name = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP} key = {building_type} }}")
    lines.append(
        f"{prefix}add_to_variable_map = {{ name = {FINAL_BUILDING_LEVEL_BY_TYPE_MAP} "
        f"key = {building_type} value = {level} }}"
    )
    lines.append(f"{prefix}tv_wonder_mechanics_refresh_location_display_state_effect = yes")


def append_hidden_event_trigger_effect(lines: list[str]) -> None:
    lines.append(f"{finalization_hidden_event_trigger_effect_name()} = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_finalization_preview_ready")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_ceremony_style")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}trigger_event_silently = tv_engineering_department.{finalization_hidden_event_id()}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_hidden_event_execute_effect(lines: list[str], wonders: list[dict]) -> None:
    lines.append(f"{finalization_hidden_event_execute_effect_name()} = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_finalization_preview_ready")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_ceremony_style")
    lines.append(f"{T}{T}}}")
    first_wonder = True
    for wonder in wonders:
        wonder_head = "if" if first_wonder else "else_if"
        first_wonder = False
        lines.append(f"{T}{T}{wonder_head} = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        styles = ceremony_styles(wonder)
        if len(styles) == 1:
            lines.append(f"{T}{T}{T}{finalization_hidden_effect_name(wonder, styles[0])} = yes")
        else:
            for index, style in enumerate(styles):
                style_head = "if" if index == 0 else "else_if"
                lines.append(f"{T}{T}{T}{style_head} = {{")
                lines.append(f"{T}{T}{T}{T}limit = {{ var:tv_wonder_ceremony_style ?= {style} }}")
                lines.append(f"{T}{T}{T}{T}{finalization_hidden_effect_name(wonder, style)} = yes")
                lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def destroy_intermediate_effect_name(wonder: dict) -> str:
    return f"tv_wonder_{wonder['key']}_destroy_finalization_intermediate_buildings_effect"


def broadcast_effect_name(wonder: dict) -> str:
    return f"tv_wonder_{wonder['key']}_broadcast_finalization_completion_event_effect"


def append_static_final_building_construction(lines: list[str], building: str, indent: int) -> None:
    prefix = T * indent
    lines.append(f"{prefix}if = {{")
    lines.append(f"{prefix}{T}limit = {{")
    lines.append(f"{prefix}{T}{T}NOT = {{ has_building = {building_type_ref(building)} }}")
    lines.append(f"{prefix}{T}{T}prev = {{ var:tv_wonder_level ?= {{ this >= 1 }} }}")
    lines.append(f"{prefix}{T}}}")
    lines.append(
        f"{prefix}{T}construct_building = {{ building_type = {building_type_ref(building)} "
        f"cost_multiplier = 0 cost_multiplier_reason = \"game_concept_event\" instant = yes }}"
    )
    for level in range(6, 1, -1):
        head = "if" if level == 6 else "else_if"
        lines.append(f"{prefix}{T}{head} = {{")
        lines.append(f"{prefix}{T}{T}limit = {{ prev = {{ var:tv_wonder_level ?= {{ this >= {level} }} }} }}")
        lines.append(
            f"{prefix}{T}{T}change_building_level_in_location = {{ "
            f"building = {building_type_ref(building)} value = {level - 1} owner = prev }}"
        )
        lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
    for current_level in range(5, 0, -1):
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}{T}limit = {{ {loc_level(building, '>=', current_level)} }}")
        first_target = True
        for target_level in range(6, current_level, -1):
            delta = target_level - current_level
            head = "if" if first_target else "else_if"
            first_target = False
            lines.append(f"{prefix}{T}{head} = {{")
            lines.append(f"{prefix}{T}{T}limit = {{ prev = {{ var:tv_wonder_level ?= {{ this >= {target_level} }} }} }}")
            lines.append(
                f"{prefix}{T}{T}change_building_level_in_location = {{ "
                f"building = {building_type_ref(building)} value = {delta} owner = prev }}"
            )
            lines.append(f"{prefix}{T}}}")
        lines.append(f"{prefix}}}")
    append_store_final_building_level(lines, building, "prev.var:tv_wonder_level", indent)


def append_trigger_event_dispatch_effect(lines: list[str], wonders: list[dict]) -> None:
    lines.append("tv_wonder_mechanics_trigger_finalization_event_effect = {")
    first = True
    for wonder in wonders:
        head = "if" if first else "else_if"
        first = False
        lines.append(f"{T}{head} = {{")
        lines.append(f"{T}{T}limit = {{ var:tv_wonder_locked ?= {wonder['id']} }}")
        lines.append(f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{finalization_event_id(wonder)} }}")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_construct_final_building_effect(lines: list[str], wonder: dict, style: int) -> None:
    building = wonder["final_buildings"][style]
    lines.append(f"{construct_final_building_effect_name(wonder, style)} = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_variable = tv_wonder_finalization_preview_ready")
    lines.append(f"{T}{T}{T}var:tv_wonder_locked ?= {wonder['id']}")
    lines.append(f"{T}{T}{T}var:tv_wonder_ceremony_style ?= {int(style)}")
    lines.append(f"{T}{T}{T}tv_wonder_construction_site_selected_trigger = yes")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this >= 1 }}")
    lines.append(f"{T}{T}{T}var:tv_wonder_level ?= {{ this <= 6 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}save_scope_as = tv_wonder_finalization_owner")
    lines.append(f"{T}{T}var:tv_wonder_site ?= {{")
    append_static_final_building_construction(lines, building, 3)
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_destroy_intermediate_buildings_effect(lines: list[str], wonder: dict) -> None:
    # Part module buildings represent unmerged surplus units by finalization time.
    # Only the merged helper is consumed by the final building.
    buildings = [f"tv_wonder_{wonder['key']}"]
    lines.append(f"{destroy_intermediate_effect_name(wonder)} = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_construction_site_selected_trigger = yes }}")
    lines.append(f"{T}{T}save_scope_as = tv_wonder_module_owner")
    lines.append(f"{T}{T}var:tv_wonder_site ?= {{")
    for building in buildings:
        lines.append(f"{T}{T}{T}if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ has_building = {building_type_ref(building)} }}")
        lines.extend(change_level_lines(building, -6, 4))
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_broadcast_effect(lines: list[str], wonder: dict) -> None:
    lines.append(f"{broadcast_effect_name(wonder)} = {{")
    lines.append(f"{T}save_scope_as = tv_wonder_builder_country")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_construction_site_selected_trigger = yes }}")
    lines.append(f"{T}{T}var:tv_wonder_site ?= {{ save_scope_as = tv_wonder_completed_site }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}every_country = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}exists = capital")
    lines.append(f"{T}{T}{T}exists = scope:tv_wonder_builder_country")
    lines.append(f"{T}{T}{T}exists = scope:tv_wonder_completed_site")
    lines.append(f"{T}{T}{T}NOT = {{ this = scope:tv_wonder_builder_country }}")
    lines.append(f"{T}{T}}}")
    lines.append(
        f"{T}{T}trigger_event_non_silently = {{ id = tv_engineering_department.{finalization_world_event_id(wonder)} }}"
    )
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_visible_effect(lines: list[str], wonder: dict) -> None:
    lines.append(f"{finalization_visible_effect_name(wonder)} = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ has_variable = tv_wonder_finalization_preview_ready var:tv_wonder_locked ?= {wonder['id']} }}")
    lines.append(f"{T}{T}tv_wonder_apply_finalization_visible_rewards_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_hidden_effect(lines: list[str], wonder: dict, style: int) -> None:
    lines.append(f"{finalization_hidden_effect_name(wonder, style)} = {{")
    lines.append(f"{T}if = {{")
    lines.append(
        f"{T}{T}limit = {{ has_variable = tv_wonder_finalization_preview_ready "
        f"var:tv_wonder_locked ?= {wonder['id']} var:tv_wonder_ceremony_style ?= {int(style)} }}"
    )
    lines.append(f"{T}{T}hidden_effect = {{")
    lines.append(f"{T}{T}{T}tv_wonder_complete_finalization_cleanup_effect = yes")
    lines.append(f"{T}{T}{T}{destroy_intermediate_effect_name(wonder)} = yes")
    lines.append(f"{T}{T}{T}{broadcast_effect_name(wonder)} = yes")
    lines.append(f"{T}{T}{T}tv_wonder_register_current_project_priority_candidate_from_variables_effect = yes")
    lines.append(f"{T}{T}{T}tv_wonder_clear_project_state_core_effect = yes")
    lines.append(f"{T}{T}{T}tv_wonder_start_concept_effect = {{ reason = 3 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    wonders, _mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    append_hidden_event_trigger_effect(lines)
    append_hidden_event_execute_effect(lines, wonders)
    append_trigger_event_dispatch_effect(lines, wonders)
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            append_construct_final_building_effect(lines, wonder, style)
        append_destroy_intermediate_buildings_effect(lines, wonder)
        append_broadcast_effect(lines, wonder)
        append_visible_effect(lines, wonder)
        for style in ceremony_styles(wonder):
            append_hidden_effect(lines, wonder, style)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("\ufeff" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
