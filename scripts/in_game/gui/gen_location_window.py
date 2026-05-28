import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import load_all_wonder_mechanics_data, render_header

VANILLA_FILE = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "gui" / "location_window.gui"
OUT_FILE = REPO_ROOT / "src" / "in_game" / "gui" / "location_window.gui"
SCRIPT_REL = "scripts/in_game/gui/gen_location_window.py"
T = "\t"
DISPLAY_VAR = "LocationView.GetLocation.MakeScope.GetVariable('tv_wonder_display_id')"


def eq_display(wonder_id: int) -> str:
    return f"And({DISPLAY_VAR}.IsSet, EqualTo_CFixedPoint({DISPLAY_VAR}.GetValue, '(CFixedPoint){wonder_id}.0'))"


def preview_texture(wonder: dict) -> str:
    image = wonder.get("image", f"tv_wonder_{wonder['key']}")
    return f"gfx/interface/illustrations/towards_victory/wonders/{image}.dds"


def render_wonder_image_branches(indent: str, *, size: str = "100% 100%") -> list[str]:
    wonders, _ = load_all_wonder_mechanics_data()
    lines: list[str] = []
    for wonder in wonders:
        lines.extend(
            [
                f"{indent}widget = {{",
                f'{indent}{T}visible = "[{eq_display(wonder["id"])}]"',
                f"{indent}{T}size = {{ {size} }}",
                f"{indent}{T}background = {{",
                f'{indent}{T}{T}texture = "{preview_texture(wonder)}"',
                f"{indent}{T}{T}texture_density = 2",
                f"{indent}{T}{T}fittype = centercrop",
                f"{indent}{T}}}",
                f"{indent}}}",
            ]
        )
    return lines


def render_tooltip_wonder_names(indent: str) -> list[str]:
    wonders, _ = load_all_wonder_mechanics_data()
    lines: list[str] = []
    for wonder in wonders:
        concept = wonder["concept"]
        lines.extend(
            [
                f"{indent}text_single = {{",
                f'{indent}{T}visible = "[{eq_display(wonder["id"])}]"',
                f"{indent}{T}text = \"[{concept}|E]\"",
                f"{indent}{T}align = center|nobaseline",
                f"{indent}{T}maximumsize = {{ 272 28 }}",
                f"{indent}{T}using = Font_Type_Headers",
                f"{indent}}}",
            ]
        )
    return lines


def render_tooltip_template() -> str:
    lines = [
        "template tv_location_wonder_tooltip {",
        f"{T}ContextualTooltipType = {{",
        f'{T}{T}blockoverride "title_text" {{ text = "TV_LOCATION_WONDER_TOOLTIP_TITLE" }}',
        f'{T}{T}blockoverride "title_icon_texture" {{',
        f'{T}{T}{T}texture = "gfx/interface/icons/location_icons/new/prosperity.dds"',
        f"{T}{T}}}",
        f'{T}{T}blockoverride "concept_link" {{ text = "[tv_wonder_construction|E]" }}',
        f'{T}{T}blockoverride "tooltip_content" {{',
        f"{T}{T}{T}widget = {{",
        f"{T}{T}{T}{T}size = {{ 280 204 }}",
        f"{T}{T}{T}{T}vbox = {{",
        f"{T}{T}{T}{T}{T}layoutpolicy_horizontal = expanding",
        f"{T}{T}{T}{T}{T}spacing = 6",
        f"{T}{T}{T}{T}{T}widget = {{",
        f"{T}{T}{T}{T}{T}{T}size = {{ 272 156 }}",
        f"{T}{T}{T}{T}{T}{T}using = bg_paper_card",
        f"{T}{T}{T}{T}{T}{T}using = bg_cabinet_card_frame",
    ]
    lines.extend(render_wonder_image_branches(T * 7, size="100% 100%"))
    lines.extend(
        [
            f"{T}{T}{T}{T}{T}}}",
            f"{T}{T}{T}{T}{T}widget = {{",
            f"{T}{T}{T}{T}{T}{T}size = {{ 272 28 }}",
            f"{T}{T}{T}{T}{T}{T}using = bg_dark_paper_card",
        ]
    )
    lines.extend(render_tooltip_wonder_names(T * 7))
    lines.extend(
        [
            f"{T}{T}{T}{T}{T}}}",
            f"{T}{T}{T}{T}}}",
            f"{T}{T}{T}}}",
            f"{T}{T}}}",
            f"{T}}}",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def render_scene_overlay() -> str:
    lines = [
        f"{T}{T}{T}{T}widget = {{",
        f'{T}{T}{T}{T}{T}visible = "[{DISPLAY_VAR}.IsSet]"',
        f"{T}{T}{T}{T}{T}size = {{ 62 62 }}",
        f"{T}{T}{T}{T}{T}parentanchor = right|top",
        f"{T}{T}{T}{T}{T}widgetanchor = right|top",
        f"{T}{T}{T}{T}{T}position = {{ -12 12 }}",
        f"{T}{T}{T}{T}{T}allow_outside = yes",
        f"{T}{T}{T}{T}{T}background = {{",
        f'{T}{T}{T}{T}{T}{T}texture = "gfx/interface/component_tiles/hud_corners/circle_background.dds"',
        f"{T}{T}{T}{T}{T}{T}texture_density = 2",
        f"{T}{T}{T}{T}{T}{T}alpha = 0.92",
        f"{T}{T}{T}{T}{T}}}",
        f"{T}{T}{T}{T}{T}button = {{",
        f"{T}{T}{T}{T}{T}{T}parentanchor = center",
        f"{T}{T}{T}{T}{T}{T}size = {{ 52 52 }}",
        f"{T}{T}{T}{T}{T}{T}tooltipwidget = {{ using = tv_location_wonder_tooltip }}",
    ]
    lines.extend(render_wonder_image_branches(T * 7, size="100% 100%"))
    lines.extend(
        [
            f"{T}{T}{T}{T}{T}}}",
            f"{T}{T}{T}{T}}}",
        ]
    )
    return "\n".join(lines)


def inject_overlay(vanilla: str) -> str:
    marker = "\n\t\t\t\tvbox = {\n\t\t\t\t\texpand = {}\n"
    replacement = "\n" + render_scene_overlay() + marker
    if marker not in vanilla:
        raise RuntimeError("Could not find location scene overlay insertion point in vanilla location_window.gui")
    return vanilla.replace(marker, replacement, 1)


def generate() -> str:
    vanilla = VANILLA_FILE.read_text(encoding="utf-8-sig")
    lines = render_header(SCRIPT_REL)
    lines.append(render_tooltip_template())
    lines.append(inject_overlay(vanilla))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8-sig")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
