import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ceremony_modifier_for_style,
    ceremony_styles,
    load_all_wonder_mechanics,
    mechanic_key,
    render_header,
    ritual_plan_for_style,
    ritual_blessing_modifier_name,
    ritual_burden_modifier_name,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "static_modifiers" / "tv_engineering_department_wonder_mechanics_modifiers.txt"
SCRIPT_REL = "scripts/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_mechanics_modifiers.py"
T = "\t"
DISPLAY_MODIFIER_PREFIX = "tv_wonder_display_"


def fmt_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def scaled_modifiers(base: dict, level: int, multiplier: int | float = 1) -> dict:
    result: dict[str, object] = {}
    for key, value in base.items():
        if isinstance(value, (int, float)):
            result[key] = value * level * multiplier
        else:
            result[key] = value
    return result


def burden_modifiers(buff: dict) -> dict:
    result: dict[str, object] = {}
    for key, value in buff.items():
        if isinstance(value, (int, float)):
            result[key] = value * -2
        else:
            result[key] = value
    return result


def modifier_block(name: str, modifiers: dict) -> list[str]:
    lines = [f"{name} = {{"]
    for key, value in modifiers.items():
        lines.append(f"{T}{key} = {fmt_value(value)}")
    lines.append("}")
    lines.append("")
    return lines


def display_modifier_name(wonder: dict, level: int) -> str:
    return f"{DISPLAY_MODIFIER_PREFIX}{wonder['id']}_level_{level}"


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        base = mechanics["base_modifiers"][mechanic_key(wonder)]
        multiplier = wonder.get("base_effect_multiplier", 1)
        for level in range(1, 7):
            modifiers = scaled_modifiers(base, level, multiplier)
            if modifiers:
                lines.extend(modifier_block(f"tv_wonder_{wonder['key']}_level_{level}", modifiers))
            lines.extend(modifier_block(display_modifier_name(wonder, level), modifiers))
    for wonder in wonders:
        has_timed_ritual = False
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            if ritual_plan["mode"] == "timed":
                timed = ritual_plan["timed"]
                blessing = timed.get("blessing_modifier", {})
                burden = timed.get("burden_modifier", {})
                if blessing:
                    lines.extend(modifier_block(ritual_blessing_modifier_name(wonder), blessing))
                if burden:
                    lines.extend(modifier_block(ritual_burden_modifier_name(wonder), burden))
                elif blessing:
                    lines.extend(modifier_block(ritual_burden_modifier_name(wonder), burden_modifiers(blessing)))
                has_timed_ritual = True
            if not wonder.get("is_unique"):
                continue
            ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
            if ceremony_modifier is None:
                continue
            modifier_name, modifiers = ceremony_modifier
            lines.extend(modifier_block(modifier_name, modifiers))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
