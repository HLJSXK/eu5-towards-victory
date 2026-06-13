"""Generate per-wonder ownership transfer notification events."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    load_all_wonder_mechanics,
    ownership_gain_event_id,
    ownership_loss_event_id,
    persistent_ritual_country_modifier_name,
    render_header,
    wonder_image_name,
)
from wonder_image_crop_lib import cropped_wonder_image_name

OUT_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_wonder_ownership_events.txt"
SCRIPT_REL = "scripts/in_game/events/gen_tv_wonder_ownership_events.py"
T = "\t"
WONDER_IMAGE_DIR = "gfx/interface/icons/towards_victory/wonders"


def wonder_event_image(wonder: dict) -> str:
    return f"{WONDER_IMAGE_DIR}/{cropped_wonder_image_name(wonder_image_name(wonder))}.dds"


def append_ownership_gain_event(lines: list[str], wonder: dict) -> None:
    lines.append(f"tv_engineering_department.{ownership_gain_event_id(wonder)} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = tv_wonder_ownership.800.t")
    lines.append(f"{T}desc = tv_wonder_ownership.800.d")
    lines.append(f'{T}image = "{wonder_event_image(wonder)}"')
    lines.append(f"{T}outcome = good")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = tv_wonder_ownership.800.a")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def append_unique_ritual_key_cleanup(lines: list[str], wonder: dict) -> None:
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{T}{T}has_variable_map = tv_wonder_unique_ritual_completed")
    lines.append(
        f"{T}{T}{T}{T}{T}is_key_in_variable_map = {{ "
        f"name = tv_wonder_unique_ritual_completed target = {int(wonder['id'])} }}"
    )
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(
        f"{T}{T}{T}{T}remove_from_variable_map = {{ "
        f"name = tv_wonder_unique_ritual_completed key = {int(wonder['id'])} }}"
    )
    lines.append(f"{T}{T}{T}}}")


def append_ownership_loss_event(lines: list[str], wonder: dict, mechanics: dict) -> None:
    modifier_name = persistent_ritual_country_modifier_name(wonder, mechanics)
    lines.append(f"tv_engineering_department.{ownership_loss_event_id(wonder)} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = tv_wonder_ownership.900.t")
    lines.append(f"{T}desc = tv_wonder_ownership.900.d")
    lines.append(f'{T}image = "{wonder_event_image(wonder)}"')
    lines.append(f"{T}outcome = bad")
    lines.append("")
    lines.append(f"{T}immediate = {{")
    lines.append(f"{T}{T}# Run before the option renders so the ritual benefit is already gone.")
    lines.append(f"{T}{T}set_variable = {{ name = tv_wonder_ownership_event_wonder_id value = {int(wonder['id'])} }}")
    lines.append(f"{T}{T}tv_wonder_ownership_compute_loss_retains_same_wonder_effect = yes")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ NOT = {{ has_variable = tv_wonder_ownership_loss_retains_same_wonder }} }}")
    if modifier_name is not None:
        lines.append(f"{T}{T}{T}remove_country_modifier = {modifier_name}")
    if wonder.get("is_unique"):
        append_unique_ritual_key_cleanup(lines, wonder)
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}remove_variable = tv_wonder_ownership_loss_retains_same_wonder")
    lines.append(f"{T}{T}remove_variable = tv_wonder_ownership_event_wonder_id")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = tv_wonder_ownership.900.a")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    all_wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    lines.append("namespace = tv_engineering_department")
    lines.append("")
    lines.append("# Event IDs intentionally remain 8000 + wonder id and 9000 + wonder id.")
    lines.append("# Only event dispatch is per-wonder; ownership state handling is in tv_wonder_ownership_effects.txt.")
    lines.append("")
    for wonder in all_wonders:
        append_ownership_gain_event(lines, wonder)
    for wonder in all_wonders:
        append_ownership_loss_event(lines, wonder, mechanics)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text("\ufeff" + generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
