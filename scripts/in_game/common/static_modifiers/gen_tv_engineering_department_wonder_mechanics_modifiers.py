import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (
    ceremony_styles,
    load_all_wonder_mechanics,
    render_header,
    ritual_blessing_modifier_name,
    ritual_plan_for_style,
    ritual_burden_modifier_name,
    unique_ceremony_modifier_name,
    wonder_static_base_modifier_name,
    wonder_static_display_modifier_name,
    wonder_base_country_modifiers,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "static_modifiers" / "tv_engineering_department_wonder_mechanics_modifiers.txt"
SCRIPT_REL = "scripts/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_mechanics_modifiers.py"
T = "\t"


def fmt_value(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def burden_modifiers(buff: dict) -> dict:
    result: dict[str, object] = {}
    for key, value in buff.items():
        if isinstance(value, bool):
            result[key] = not value
        elif isinstance(value, (int, float)):
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


def generate() -> str:
    wonders, mechanics = load_all_wonder_mechanics()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        for level in range(1, 7):
            modifiers = wonder_base_country_modifiers(wonder, mechanics, level)
            if modifiers:
                lines.extend(modifier_block(wonder_static_base_modifier_name(wonder, level), modifiers))
            lines.extend(modifier_block(wonder_static_display_modifier_name(wonder, level), modifiers))
    for wonder in wonders:
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
            if not wonder.get("is_unique"):
                continue
            modifiers = ritual_plan.get("country_modifier", {})
            if modifiers:
                lines.extend(modifier_block(unique_ceremony_modifier_name(wonder), modifiers))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
