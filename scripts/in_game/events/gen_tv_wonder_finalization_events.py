"""Generate one Engineering Department finalization event per wonder."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_localization_lib import load_wonder_localization_data
from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.naming import (
    construct_final_building_effect_name,
    finalization_event_id,
    finalization_hidden_event_execute_effect_name,
    finalization_hidden_event_id,
    finalization_hidden_event_trigger_effect_name,
    finalization_visible_effect_name,
    finalization_world_event_id,
    wonder_image_name,
)
from wonder_mechanics.render import render_header
from wonder_mechanics.rituals import ceremony_styles
from wonder_image_crop_lib import cropped_wonder_image_name

OUT_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_wonder_finalization_events.txt"
SCRIPT_REL = "scripts/in_game/events/gen_tv_wonder_finalization_events.py"
T = "\t"
WONDER_IMAGE_DIR = "gfx/interface/icons/towards_victory/wonders"

GENERIC_FINALIZATION_DESC_SUFFIXES = {
    "sacred_mountain": "sacred",
    "triumphal_axis": "axis",
    "great_port": "port",
    "giant_necropolis": "necropolis",
    "great_lighthouse": "lighthouse",
    "hydraulic_workshop": "hydraulic",
    "mining_city": "mining",
    "giant_observatory": "observatory",
    "palace_of_nations": "palace",
    "university_city": "university",
    "sky_dome_grand_temple": "sky_dome",
    "giant_tower_temple": "tower_temple",
    "river_extension": "river",
    "national_shipyard": "shipyard",
    "star_fortress_city": "star_fortress",
    "giant_armory": "armory",
    "library_of_nation": "library",
}


def known_loc_keys() -> set[str]:
    localization = load_wonder_localization_data()
    return set(localization["english"]) & set(localization["simp_chinese"])


def generic_desc_key(wonder: dict, style: int) -> str:
    suffix = GENERIC_FINALIZATION_DESC_SUFFIXES.get(wonder["key"], wonder["key"])
    return f"tv_engineering_department.500.d_{suffix}_{style}"


def unique_desc_key(wonder: dict) -> str:
    return f"tv_engineering_department.500.d_{wonder['key']}"


def world_desc_key(wonder: dict, loc_keys: set[str]) -> str:
    if wonder.get("is_unique"):
        desc_key = f"tv_engineering_department.600.d_{wonder['key']}"
        return desc_key if desc_key in loc_keys else "tv_engineering_department.600.d"
    suffix = GENERIC_FINALIZATION_DESC_SUFFIXES.get(wonder["key"], wonder["key"])
    desc_key = f"tv_engineering_department.600.d_{suffix}"
    return desc_key if desc_key in loc_keys else "tv_engineering_department.600.d"


def wonder_event_image(wonder: dict) -> str:
    return f"{WONDER_IMAGE_DIR}/{cropped_wonder_image_name(wonder_image_name(wonder))}.dds"


def append_desc(lines: list[str], wonder: dict, loc_keys: set[str]) -> None:
    styles = ceremony_styles(wonder)
    if len(styles) == 1:
        lines.append(f"{T}desc = {desc_key_for_style(wonder, styles[0], loc_keys)}")
        return

    lines.append(f"{T}desc = {{")
    lines.append(f"{T}{T}first_valid = {{")
    for style in styles:
        lines.append(f"{T}{T}{T}triggered_desc = {{")
        lines.append(f"{T}{T}{T}{T}trigger = {{ var:tv_wonder_ceremony_style ?= {style} }}")
        lines.append(f"{T}{T}{T}{T}desc = {desc_key_for_style(wonder, style, loc_keys)}")
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}desc = {desc_key_for_style(wonder, styles[0], loc_keys)}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")


def append_hidden_style_dispatch(lines: list[str], wonder: dict) -> None:
    lines.append(f"{T}{T}hidden_effect = {{")
    lines.append(f"{T}{T}{T}{finalization_hidden_event_trigger_effect_name()} = yes")
    lines.append(f"{T}{T}}}")


def append_visible_construction_dispatch(lines: list[str], wonder: dict) -> None:
    styles = ceremony_styles(wonder)
    if len(styles) == 1:
        lines.append(f"{T}{T}{construct_final_building_effect_name(wonder, styles[0])} = yes")
        return

    for index, style in enumerate(styles):
        head = "if" if index == 0 else "else_if"
        lines.append(f"{T}{T}{head} = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:tv_wonder_ceremony_style ?= {style} }}")
        lines.append(f"{T}{T}{T}{construct_final_building_effect_name(wonder, style)} = yes")
        lines.append(f"{T}{T}}}")


def append_finalization_option(lines: list[str], wonder: dict) -> None:
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = tv_engineering_department.500.a")
    append_visible_construction_dispatch(lines, wonder)
    lines.append(f"{T}{T}{finalization_visible_effect_name(wonder)} = yes")
    append_hidden_style_dispatch(lines, wonder)
    lines.append(f"{T}}}")


def desc_key_for_style(wonder: dict, style: int, loc_keys: set[str]) -> str:
    if wonder.get("is_unique"):
        desc_key = unique_desc_key(wonder)
        return desc_key if desc_key in loc_keys else "tv_engineering_department.500.d"
    desc_key = generic_desc_key(wonder, style)
    return desc_key if desc_key in loc_keys else "tv_engineering_department.500.d"


def append_event(lines: list[str], wonder: dict, loc_keys: set[str]) -> None:
    lines.append(f"tv_engineering_department.{finalization_event_id(wonder)} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = tv_engineering_department.500.t")
    append_desc(lines, wonder, loc_keys)
    lines.append(f'{T}image = "{wonder_event_image(wonder)}"')
    lines.append(f"{T}outcome = positive")
    lines.append("")
    append_finalization_option(lines, wonder)
    lines.append("}")
    lines.append("")


def append_world_news_event(lines: list[str], wonder: dict, loc_keys: set[str]) -> None:
    lines.append(f"tv_engineering_department.{finalization_world_event_id(wonder)} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = tv_engineering_department.600.t")
    lines.append(f"{T}desc = {world_desc_key(wonder, loc_keys)}")
    lines.append(f'{T}image = "{wonder_event_image(wonder)}"')
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = tv_engineering_department.600.a")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_hidden_finalization_event(lines: list[str]) -> None:
    lines.append(f"tv_engineering_department.{finalization_hidden_event_id()} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}outcome = neutral")
    lines.append(f"{T}title = empty_text")
    lines.append(f"{T}desc = empty_text")
    lines.append(f"{T}hidden = yes")
    lines.append("")
    lines.append(f"{T}immediate = {{")
    lines.append(f"{T}{T}{finalization_hidden_event_execute_effect_name()} = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    wonders, _mechanics = load_all_wonder_mechanics()
    loc_keys = known_loc_keys()
    lines = render_header(SCRIPT_REL)
    lines.append("namespace = tv_engineering_department")
    lines.append("")
    for wonder in wonders:
        append_event(lines, wonder, loc_keys)
    append_hidden_finalization_event(lines)
    for wonder in wonders:
        append_world_news_event(lines, wonder, loc_keys)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("\ufeff" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
