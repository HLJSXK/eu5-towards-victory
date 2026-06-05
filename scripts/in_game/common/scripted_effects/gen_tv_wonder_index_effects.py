import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    PARTS,
    WONDER_MAP_SCHEMA_VERSION,
    WONDER_RITUAL_COST_TYPE_IDS,
    WONDER_RITUAL_LISTENER_KEYS,
    WONDER_RITUAL_MODE_IDS,
    WONDER_SIZE_IDS,
    ceremony_styles,
    load_all_wonder_mechanics,
    render_header,
    ritual_plan_for_style,
    ritual_has_custom_completion_trigger,
    ritual_uses_deferred_completion,
    suitability_knowledge_for_wonder,
    wonder_ritual_composite_id,
    wonder_suitability_row_composite_id,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_wonder_index_effects.txt"
SCRIPT_REL = "scripts/in_game/common/scripted_effects/gen_tv_wonder_index_effects.py"
T = "\t"

WONDER_CACHE_VARS = [
    "tv_wonder_locked_is_unique",
    "tv_wonder_locked_base_id",
    "tv_wonder_locked_mechanic_id",
    "tv_wonder_locked_size",
    "tv_wonder_locked_style_count",
    "tv_wonder_locked_display_id",
    "tv_wonder_locked_concept_display_id",
    "tv_wonder_locked_image_display_id",
]

RITUAL_CACHE_VARS = [
    "tv_wonder_selected_ritual_id",
    "tv_wonder_selected_ritual_wonder_id",
    "tv_wonder_selected_ritual_style",
    "tv_wonder_selected_ritual_mode",
    "tv_wonder_selected_ritual_cost_type",
    "tv_wonder_selected_ritual_deferred_completion",
    "tv_wonder_selected_ritual_has_confirmation_trigger",
    "tv_wonder_selected_ritual_has_custom_completion_trigger",
    *[f"tv_wonder_selected_ritual_listener_{listener}" for listener in WONDER_RITUAL_LISTENER_KEYS],
]

WONDER_MAP_NAMES = [
    "tv_wonder_id_to_is_unique",
    "tv_wonder_id_to_base_id",
    "tv_wonder_id_to_mechanic_id",
    "tv_wonder_id_to_size",
    "tv_wonder_id_to_style_count",
    "tv_wonder_id_to_display_id",
    "tv_wonder_id_to_concept_display_id",
    "tv_wonder_id_to_image_display_id",
]

RITUAL_MAP_NAMES = [
    "tv_wonder_ritual_key_to_id",
    "tv_wonder_ritual_id_to_wonder_id",
    "tv_wonder_ritual_id_to_style",
    "tv_wonder_ritual_id_to_mode",
    "tv_wonder_ritual_id_to_cost_type",
    "tv_wonder_ritual_id_to_deferred_completion",
    "tv_wonder_ritual_id_to_has_confirmation_trigger",
    "tv_wonder_ritual_id_to_has_custom_completion_trigger",
    *[f"tv_wonder_ritual_id_to_listener_{listener}" for listener in WONDER_RITUAL_LISTENER_KEYS],
]

SUITABILITY_ROW_MAP_NAMES = [
    "tv_wonder_mechanic_id_to_suitability_row_count",
    "tv_wonder_suitability_row_to_mechanic_id",
    "tv_wonder_suitability_row_to_row",
]

WONDER_CACHE_MAPS = [
    ("tv_wonder_id_to_is_unique", "tv_wonder_locked_is_unique"),
    ("tv_wonder_id_to_base_id", "tv_wonder_locked_base_id"),
    ("tv_wonder_id_to_mechanic_id", "tv_wonder_locked_mechanic_id"),
    ("tv_wonder_id_to_size", "tv_wonder_locked_size"),
    ("tv_wonder_id_to_style_count", "tv_wonder_locked_style_count"),
    ("tv_wonder_id_to_display_id", "tv_wonder_locked_display_id"),
    ("tv_wonder_id_to_concept_display_id", "tv_wonder_locked_concept_display_id"),
    ("tv_wonder_id_to_image_display_id", "tv_wonder_locked_image_display_id"),
]

RITUAL_CACHE_MAPS = [
    ("tv_wonder_ritual_key_to_id", "tv_wonder_selected_ritual_id"),
    ("tv_wonder_ritual_id_to_wonder_id", "tv_wonder_selected_ritual_wonder_id"),
    ("tv_wonder_ritual_id_to_style", "tv_wonder_selected_ritual_style"),
    ("tv_wonder_ritual_id_to_mode", "tv_wonder_selected_ritual_mode"),
    ("tv_wonder_ritual_id_to_cost_type", "tv_wonder_selected_ritual_cost_type"),
    ("tv_wonder_ritual_id_to_deferred_completion", "tv_wonder_selected_ritual_deferred_completion"),
    ("tv_wonder_ritual_id_to_has_confirmation_trigger", "tv_wonder_selected_ritual_has_confirmation_trigger"),
    ("tv_wonder_ritual_id_to_has_custom_completion_trigger", "tv_wonder_selected_ritual_has_custom_completion_trigger"),
    *[
        (f"tv_wonder_ritual_id_to_listener_{listener}", f"tv_wonder_selected_ritual_listener_{listener}")
        for listener in WONDER_RITUAL_LISTENER_KEYS
    ],
]


def module_building_type_map_name(part: str) -> str:
    return f"tv_wonder_id_to_{part}_module_building_type"


def final_building_type_map_name(style: int) -> str:
    return f"tv_wonder_id_to_style_{style}_final_building_type"


def map_replace_line(map_name: str, key: str, value: object, indent: int = 1) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}remove_from_global_variable_map = {{ name = {map_name} key = {key} }}",
        f"{prefix}add_to_global_variable_map = {{ name = {map_name} key = {key} value = {value} }}",
    ]


def map_init_lines(map_name: str, indent: int = 1, value: object = 0) -> list[str]:
    prefix = T * indent
    return [
        f"{prefix}remove_from_global_variable_map = {{ name = {map_name} key = 0 }}",
        f"{prefix}add_to_global_variable_map = {{ name = {map_name} key = 0 value = {value} }}",
    ]


def append_clear_cache_effect(lines: list[str], name: str, variables: list[str]) -> None:
    lines.append(f"{name} = {{")
    for variable in variables:
        lines.append(f"{T}remove_variable = {variable}")
    lines.append("}")
    lines.append("")


def append_cache_effect(
    lines: list[str],
    *,
    name: str,
    local_key: str,
    clear_effect: str,
    key_setup_lines: list[str],
    cache_maps: list[tuple[str, str]],
) -> None:
    required_map = cache_maps[0][0]
    lines.append(f"{name} = {{")
    lines.append(f"{T}{clear_effect} = yes")
    for line in key_setup_lines:
        lines.append(f"{T}{line}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}has_local_variable = {local_key}")
    lines.append(f"{T}{T}{T}has_global_variable_map = {required_map}")
    lines.append(f"{T}{T}{T}is_key_in_global_variable_map = {{ name = {required_map} target = local_var:{local_key} }}")
    lines.append(f"{T}{T}}}")
    for map_name, variable in cache_maps:
        lines.append(f"{T}{T}set_variable = {{ name = {variable} value = \"global_variable_map({map_name}|local_var:{local_key})\" }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_local_variable = {local_key}")
    lines.append("}")
    lines.append("")


def append_refresh_country_cache(lines: list[str]) -> None:
    lines.append("tv_wonder_index_refresh_country_cache_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_has_locked_wonder_trigger = yes }}")
    lines.append(f"{T}{T}tv_wonder_index_cache_locked_wonder_attributes_effect = {{ wonder_id = var:tv_wonder_locked }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_index_clear_locked_wonder_cache_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ tv_wonder_has_selected_ceremony_trigger = yes }}")
    lines.append(
        f"{T}{T}tv_wonder_index_cache_selected_ritual_attributes_effect = {{ "
        f"wonder_id = var:tv_wonder_locked style = var:tv_wonder_ceremony_style }}"
    )
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}tv_wonder_index_clear_selected_ritual_cache_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}tv_wonder_mechanics_refresh_current_suitability_display_cache_effect = yes")
    lines.append("}")
    lines.append("")


def append_rebuild_global_maps(lines: list[str], wonders: list[dict], mechanics: dict) -> None:
    by_key = {wonder["key"]: wonder for wonder in wonders}
    all_map_names = [*WONDER_MAP_NAMES, *RITUAL_MAP_NAMES, *SUITABILITY_ROW_MAP_NAMES]
    first_wonder = wonders[0]
    all_styles = sorted({style for wonder in wonders for style in ceremony_styles(wonder)})
    building_map_defaults = [
        ("tv_wonder_id_to_helper_building_type", f"building_type:tv_wonder_{first_wonder['key']}"),
        *[
            (module_building_type_map_name(part), f"building_type:tv_wonder_{first_wonder['key']}_{part}")
            for part in PARTS
        ],
        *[
            (
                final_building_type_map_name(style),
                f"building_type:{next(wonder for wonder in wonders if style in ceremony_styles(wonder))['final_buildings'][style]}",
            )
            for style in all_styles
        ],
    ]

    lines.append("tv_wonder_index_rebuild_global_maps_effect = {")
    lines.append(f"{T}# ID contract: existing wonder ids are canonical. Runtime map keys use numeric ids directly.")
    lines.append(f"{T}# Ritual branch id = wonder_id * 100 + style.")
    lines.append(f"{T}# Tooltip-safe module/final building maps key each fixed part/style directly by wonder_id.")
    lines.append(f"{T}# Event option tooltips can render dynamic local_var building types, but not same-chain computed map keys.")
    lines.append(f"{T}# Suitability row id = mechanic_id * 10 + row, because unique wonders share mechanic rows.")
    for map_name in all_map_names:
        lines.extend(map_init_lines(map_name))
    for map_name, default_value in building_map_defaults:
        lines.extend(map_init_lines(map_name, value=default_value))

    for wonder in wonders:
        wonder_id = int(wonder["id"])
        key = str(wonder_id)
        base_id = int(by_key[wonder["base_key"]]["id"])
        mechanic_id = int(by_key[wonder["mechanic_key"]]["id"])
        size = wonder["size"]
        if size not in WONDER_SIZE_IDS:
            raise ValueError(f"Unsupported wonder size for {wonder['key']}: {size}")
        lines.extend(map_replace_line("tv_wonder_id_to_is_unique", key, 1 if wonder.get("is_unique") else 0))
        lines.extend(map_replace_line("tv_wonder_id_to_base_id", key, base_id))
        lines.extend(map_replace_line("tv_wonder_id_to_mechanic_id", key, mechanic_id))
        lines.extend(map_replace_line("tv_wonder_id_to_size", key, WONDER_SIZE_IDS[size]))
        lines.extend(map_replace_line("tv_wonder_id_to_style_count", key, len(ceremony_styles(wonder))))
        lines.extend(map_replace_line("tv_wonder_id_to_display_id", key, wonder_id))
        lines.extend(map_replace_line("tv_wonder_id_to_concept_display_id", key, wonder_id))
        lines.extend(map_replace_line("tv_wonder_id_to_image_display_id", key, wonder_id))
        lines.extend(map_replace_line("tv_wonder_id_to_helper_building_type", key, f"building_type:tv_wonder_{wonder['key']}"))

        for part in PARTS:
            module_building = f"building_type:tv_wonder_{wonder['key']}_{part}"
            lines.extend(map_replace_line(module_building_type_map_name(part), key, module_building))

        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            mode = ritual_plan["mode"]
            cost_type = ritual_plan["cost_type"]
            if mode not in WONDER_RITUAL_MODE_IDS:
                raise ValueError(f"Unsupported ritual mode for {wonder['key']} style {style}: {mode}")
            if cost_type not in WONDER_RITUAL_COST_TYPE_IDS:
                raise ValueError(f"Unsupported ritual cost type for {wonder['key']} style {style}: {cost_type}")
            ritual_key = str(wonder_ritual_composite_id(wonder_id, style))
            lines.extend(map_replace_line("tv_wonder_ritual_key_to_id", ritual_key, wonder_ritual_composite_id(wonder_id, style)))
            lines.extend(map_replace_line("tv_wonder_ritual_id_to_wonder_id", ritual_key, wonder_id))
            lines.extend(map_replace_line("tv_wonder_ritual_id_to_style", ritual_key, style))
            lines.extend(map_replace_line("tv_wonder_ritual_id_to_mode", ritual_key, WONDER_RITUAL_MODE_IDS[mode]))
            lines.extend(map_replace_line("tv_wonder_ritual_id_to_cost_type", ritual_key, WONDER_RITUAL_COST_TYPE_IDS[cost_type]))
            lines.extend(
                map_replace_line(
                    "tv_wonder_ritual_id_to_deferred_completion",
                    ritual_key,
                    1 if ritual_uses_deferred_completion(ritual_plan) else 0,
                )
            )
            lines.extend(
                map_replace_line(
                    "tv_wonder_ritual_id_to_has_confirmation_trigger",
                    ritual_key,
                    1 if ritual_plan.get("confirmation_trigger_script") else 0,
                )
            )
            lines.extend(
                map_replace_line(
                    "tv_wonder_ritual_id_to_has_custom_completion_trigger",
                    ritual_key,
                    1 if ritual_has_custom_completion_trigger(ritual_plan) else 0,
                )
            )
            listeners = set(ritual_plan.get("listeners", []))
            for listener in WONDER_RITUAL_LISTENER_KEYS:
                lines.extend(
                    map_replace_line(
                        f"tv_wonder_ritual_id_to_listener_{listener}",
                        ritual_key,
                        1 if listener in listeners else 0,
                    )
                )
            final_building = f"building_type:{wonder['final_buildings'][style]}"
            lines.extend(map_replace_line(final_building_type_map_name(style), key, final_building))

    for wonder in wonders:
        if wonder.get("is_unique"):
            continue
        mechanic_id = int(wonder["id"])
        rows = suitability_knowledge_for_wonder(mechanics, wonder)
        lines.extend(map_replace_line("tv_wonder_mechanic_id_to_suitability_row_count", str(mechanic_id), len(rows)))
        for row_index, _row in enumerate(rows, start=1):
            if row_index > 9:
                raise ValueError(f"Suitability row key only reserves row 1..9: {wonder['key']} row {row_index}")
            row_key = str(wonder_suitability_row_composite_id(mechanic_id, row_index))
            lines.extend(
                map_replace_line(
                    "tv_wonder_suitability_row_to_mechanic_id",
                    row_key,
                    mechanic_id,
                )
            )
            lines.extend(map_replace_line("tv_wonder_suitability_row_to_row", row_key, row_index))

    lines.append(f"{T}set_global_variable = {{ name = tv_wonder_map_version value = {WONDER_MAP_SCHEMA_VERSION} }}")
    lines.append("}")
    lines.append("")


def append_rebuild_if_needed(lines: list[str], first_wonder: dict) -> None:
    first_key = str(int(first_wonder["id"]))
    lines.append("tv_wonder_index_rebuild_global_maps_if_needed_effect = {")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ NOT = {{ has_global_variable = tv_wonder_map_version }} }}")
    lines.append(f"{T}{T}tv_wonder_index_rebuild_global_maps_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ NOT = {{ global_var:tv_wonder_map_version = {WONDER_MAP_SCHEMA_VERSION} }} }}")
    lines.append(f"{T}{T}tv_wonder_index_rebuild_global_maps_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ NOT = {{ has_global_variable_map = tv_wonder_id_to_is_unique }} }}")
    lines.append(f"{T}{T}tv_wonder_index_rebuild_global_maps_effect = yes")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(
        f"{T}{T}limit = {{ "
        f"NOT = {{ is_key_in_global_variable_map = {{ name = tv_wonder_id_to_is_unique target = {first_key} }} }} }}"
    )
    lines.append(f"{T}{T}tv_wonder_index_rebuild_global_maps_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    wonders = sorted(wonders, key=lambda item: int(item["id"]))

    lines = render_header(SCRIPT_REL)
    append_rebuild_global_maps(lines, wonders, mechanics)
    append_rebuild_if_needed(lines, wonders[0])
    append_clear_cache_effect(lines, "tv_wonder_index_clear_locked_wonder_cache_effect", WONDER_CACHE_VARS)
    append_clear_cache_effect(lines, "tv_wonder_index_clear_selected_ritual_cache_effect", RITUAL_CACHE_VARS)
    append_cache_effect(
        lines,
        name="tv_wonder_index_cache_locked_wonder_attributes_effect",
        local_key="tv_wonder_index_key",
        clear_effect="tv_wonder_index_clear_locked_wonder_cache_effect",
        key_setup_lines=[
            "remove_local_variable = tv_wonder_index_key",
            "set_local_variable = { name = tv_wonder_index_key value = $wonder_id$ }",
        ],
        cache_maps=WONDER_CACHE_MAPS,
    )
    append_cache_effect(
        lines,
        name="tv_wonder_index_cache_selected_ritual_attributes_effect",
        local_key="tv_wonder_ritual_index_key",
        clear_effect="tv_wonder_index_clear_selected_ritual_cache_effect",
        key_setup_lines=[
            "remove_local_variable = tv_wonder_ritual_index_key",
            "set_local_variable = { name = tv_wonder_ritual_index_key value = $wonder_id$ }",
            "change_local_variable = { name = tv_wonder_ritual_index_key multiply = 100 }",
            "change_local_variable = { name = tv_wonder_ritual_index_key add = $style$ }",
        ],
        cache_maps=RITUAL_CACHE_MAPS,
    )
    append_refresh_country_cache(lines)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("\ufeff" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
