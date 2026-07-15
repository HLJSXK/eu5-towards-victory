import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department" / "in_game" / "gui"))

import gen_location_window as tv_location_window
from wonder_mechanics.render import render_header

BASE_FILE = REPO_ROOT / "reference_mods" / "3735059838" / "in_game" / "gui" / "location_window.gui"
OUT_FILE = REPO_ROOT / "submods" / "tv_meiou_and_taxes_compat" / "in_game" / "gui" / "location_window.gui"
SCRIPT_REL = "scripts/compat/gen_tv_meiou_and_taxes_location_window.py"
DATA_REL = (
    "reference_mods/3735059838/in_game/gui/location_window.gui + "
    "data/wonders.yaml + data/wonder_final_buildings.yaml + data/wonder_generic_rituals.yaml + data/wonder_base_modifiers.yaml + data/wonder_site_rules.yaml + data/unique_wonders.yaml"
)
OVERLAY_MARKER = "\n\t\t\t\tvbox = {\n\t\t\t\t\texpand = {}\n"


def inject_tv_overlay(base_gui: str) -> str:
    if OVERLAY_MARKER not in base_gui:
        raise RuntimeError("Could not find location scene overlay insertion point in M&T location_window.gui")
    replacement = "\n" + tv_location_window.render_scene_overlay() + OVERLAY_MARKER
    return base_gui.replace(OVERLAY_MARKER, replacement, 1)


def generate() -> str:
    base_gui = BASE_FILE.read_text(encoding="utf-8-sig")
    lines = render_header(SCRIPT_REL, DATA_REL)
    lines.append(tv_location_window.render_tooltip_template())
    lines.append(inject_tv_overlay(base_gui))
    return "\n".join(line.rstrip() for line in "\n".join(lines).splitlines()).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
