import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_expansion_lib import final_building_for_style, load_wonder_data, render_header

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "static_modifiers" / "tv_engineering_department_wonder_expansion_modifiers.txt"
SCRIPT_REL = "scripts/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_expansion_modifiers.py"
T = "\t"


def fmt_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".")
    return str(value)


def scaled_modifiers(base: dict, level: int) -> dict:
    result: dict[str, object] = {"great_power_score": 10 * level}
    for key, value in base.items():
        if isinstance(value, (int, float)):
            result[key] = value * level
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
    wonders, expansion = load_wonder_data()
    lines = render_header(SCRIPT_REL)
    for wonder in wonders:
        base = expansion["base_modifiers"][wonder["key"]]
        for level in range(1, 7):
            lines.extend(modifier_block(f"tv_wonder_{wonder['key']}_level_{level}", scaled_modifiers(base, level)))
    for wonder in wonders:
        for style in range(1, 4):
            building = final_building_for_style(wonder, style)
            modifiers = expansion["ceremony_modifiers"].get(building, {})
            lines.extend(modifier_block(f"{building}_modifier", modifiers))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
