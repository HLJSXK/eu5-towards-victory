"""Generate building-driven Engineering Department wonder country auto modifiers."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.io import load_all_wonder_mechanics
from wonder_mechanics.modifiers import wonder_base_country_modifiers
from wonder_mechanics.naming import (
    TV_WONDER_AUTO_LEVEL_BY_WONDER_ID_MAP,
    wonder_auto_modifier_name,
    wonder_auto_unscaled_modifier_name,
)
from wonder_mechanics.render import render_header

OUT_FILE = (
    REPO_ROOT
    / "src"
    / "in_game"
    / "common"
    / "auto_modifiers"
    / "tv_engineering_department_wonder_mechanics_auto_modifiers.txt"
)
SCRIPT_REL = "scripts/in_game/common/auto_modifiers/gen_tv_engineering_department_wonder_mechanics_auto_modifiers.py"
T = "\t"


def fmt_value(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def is_numeric_modifier_value(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def split_scaled_modifiers(modifiers: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    scaled: dict[str, object] = {}
    unscaled: dict[str, object] = {}
    for key, value in modifiers.items():
        if is_numeric_modifier_value(value):
            scaled[key] = value
        else:
            unscaled[key] = value
    return scaled, unscaled


def append_cached_level_potential(lines: list[str], wonder_id: int, indent: int) -> None:
    prefix = T * indent
    lines.append(f"{prefix}potential_trigger = {{")
    lines.append(f"{prefix}{T}has_variable_map = {TV_WONDER_AUTO_LEVEL_BY_WONDER_ID_MAP}")
    lines.append(
        f"{prefix}{T}is_key_in_variable_map = {{ "
        f"name = {TV_WONDER_AUTO_LEVEL_BY_WONDER_ID_MAP} target = {wonder_id} }}"
    )
    lines.append(f"{prefix}}}")


def append_modifier_block(
    lines: list[str],
    name: str,
    modifiers: dict[str, object],
    wonder_id: int,
    *,
    scaled: bool,
    hidden: bool = False,
) -> None:
    if not modifiers:
        return
    lines.append(f"{name} = {{")
    lines.append(f"{T}category = country")
    if hidden:
        lines.append(f"{T}hide_effects = yes")
    append_cached_level_potential(lines, wonder_id, 1)
    if scaled:
        lines.append(f"{T}scales_with = {{")
        lines.append(f"{T}{T}value = \"variable_map({TV_WONDER_AUTO_LEVEL_BY_WONDER_ID_MAP}|{wonder_id})\"")
        lines.append(f"{T}}}")
    for key, value in modifiers.items():
        lines.append(f"{T}{key} = {fmt_value(value)}")
    lines.append("}")
    lines.append("")


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        scaled_modifiers, unscaled_modifiers = split_scaled_modifiers(
            wonder_base_country_modifiers(wonder, mechanics, level=1)
        )
        append_modifier_block(
            lines,
            wonder_auto_modifier_name(wonder),
            scaled_modifiers,
            int(wonder["id"]),
            scaled=True,
        )
        append_modifier_block(
            lines,
            wonder_auto_unscaled_modifier_name(wonder),
            unscaled_modifiers,
            int(wonder["id"]),
            scaled=False,
            hidden=True,
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
