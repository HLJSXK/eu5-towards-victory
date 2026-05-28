import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import ceremony_styles, final_building_for_style, load_all_wonder_mechanics_data, render_header

OUT_FILE = REPO_ROOT / "data" / "generated_fragments" / "tv_engineering_department_wonder_mechanics.gui"
SCRIPT_REL = "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py"
T = "\t"
PLAYER = "InternationalOrganizationsView.GetPlayer.MakeScope"


def eq(var: str, value: int) -> str:
    return f"EqualTo_CFixedPoint({PLAYER}.GetVariable('{var}').GetValue, '(CFixedPoint){value}.0')"


def wonder_visible(wonder_id: int) -> str:
    return (
        "[Or("
        f"And({PLAYER}.GetVariable('tv_wonder_locked').IsSet, {eq('tv_wonder_locked', wonder_id)}), "
        f"And3(Not({PLAYER}.GetVariable('tv_wonder_locked').IsSet), {PLAYER}.GetVariable('tv_wonder_proposal').IsSet, {eq('tv_wonder_proposal', wonder_id)})"
        ")]"
    )


def proposal_button(slot: int, wonder: dict) -> str:
    visible = eq(f"tv_wonder_proposal_slot_{slot}", wonder["id"])
    return (
        f'{T}action_button_diamond = {{ size = {{ 152 30 }} visible = "[{visible}]" '
        f'text = "TV_ENGINEERING_PROPOSAL_BUTTON_{wonder["key"].upper()}" title = "tv_wonder_select_proposal_slot_{slot}" '
        f'description = "tv_wonder_select_proposal_slot_{slot}_desc" actor = "[InternationalOrganizationsView.GetPlayer]" '
        f'left_action = {{ action_name = "tv_wonder_select_proposal_slot_{slot}" }} }}'
    )


def proposal_text(wonder: dict, suffix: str = "") -> str:
    key = f"TV_ENGINEERING_PROPOSAL{suffix}_{wonder['key'].upper()}_TEXT"
    return (
        f'{T}text_multi = {{ visible = "[{eq("tv_wonder_proposal", wonder["id"])}]" '
        f'max_width = 352 autoresize = yes text = "{key}" align = nobaseline|left }}'
    )


def locked_text(wonder: dict) -> str:
    return (
        f'{T}text_multi = {{ visible = "[{eq("tv_wonder_locked", wonder["id"])}]" '
        f'max_width = 352 autoresize = yes text = "TV_ENGINEERING_LOCKED_{wonder["key"].upper()}_TEXT" align = nobaseline|left }}'
    )


def preview_texture(wonder: dict) -> str:
    image = wonder.get("image", f"tv_wonder_{wonder['key']}")
    return f"gfx/interface/illustrations/towards_victory/wonders/{image}.dds"


def ceremony_select_button(wonder: dict, style: int) -> str:
    building = final_building_for_style(wonder, style)
    locked_visible = eq("tv_wonder_locked", wonder["id"])
    selected_down = eq("tv_wonder_ceremony_style", style)
    loc_key = f"TV_ENGINEERING_CEREMONY_{building.removeprefix('tv_wonder_').upper()}_BUTTON"
    return (
        f'{T}action_button_diamond = {{ visible = "[{locked_visible}]" size = {{ 150 30 }} '
        f'text = "{loc_key}" '
        f'down = "[{selected_down}]" title = "tv_wonder_choose_ceremony_style_{style}" '
        f'description = "tv_wonder_choose_ceremony_style_{style}_desc" actor = "[InternationalOrganizationsView.GetPlayer]" '
        f'left_action = {{ action_name = "tv_wonder_choose_ceremony_style_{style}" }} }}'
    )


def active_ritual_text(wonder: dict, style: int) -> str:
    visible = f"And({eq('tv_wonder_locked', wonder['id'])}, {eq('tv_wonder_ceremony_style', style)})"
    return (
        f'{T}text_multi = {{ visible = "[{visible}]" '
        f'max_width = 446 autoresize = yes text = "TV_ENGINEERING_ACTIVE_RITUAL_{wonder["key"].upper()}_{style}" align = nobaseline|left }}'
    )


def hold_button() -> str:
    visible = (
        f"And3({PLAYER}.GetVariable('tv_wonder_locked').IsSet, "
        f"{PLAYER}.GetVariable('tv_wonder_ceremony_style').IsSet, "
        f"LessThanOrEqualTo_CFixedPoint({PLAYER}.GetVariable('tv_wonder_locked').GetValue, '(CFixedPoint)140.0'))"
    )
    return (
        f'{T}action_button_diamond = {{ visible = "[{visible}]" '
        'size = { 180 30 } text = "TV_ENGINEERING_HOLD_CEREMONY_BUTTON" title = "tv_wonder_confirm_ceremony" '
        'description = "tv_wonder_confirm_ceremony_desc" actor = "[InternationalOrganizationsView.GetPlayer]" '
        'left_action = { action_name = "tv_wonder_confirm_ceremony" } }'
    )


def generate() -> str:
    wonders, _ = load_all_wonder_mechanics_data()
    lines = render_header(SCRIPT_REL)
    lines.append("### BEGIN TV_WONDER_MECHANICS_PREVIEW_WIDGETS")
    for wonder in wonders:
        lines.extend(
            [
                "widget = {",
                f'{T}visible = "{wonder_visible(wonder["id"])}"',
                f"{T}size = {{ 100% 100% }}",
                f"{T}background = {{",
                f'{T}{T}texture = "{preview_texture(wonder)}"',
                f"{T}{T}texture_density = 2",
                f"{T}{T}fittype = centercrop",
                f"{T}}}",
                "}",
            ]
        )
    lines.append("### END TV_WONDER_MECHANICS_PREVIEW_WIDGETS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_TEXTS")
    for wonder in wonders:
        lines.append(proposal_text(wonder))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_RESUME_TEXTS")
    for wonder in wonders:
        lines.append(proposal_text(wonder, "_RESUME"))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_RESUME_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_EXPAND_TEXTS")
    for wonder in wonders:
        lines.append(proposal_text(wonder, "_EXPAND"))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_EXPAND_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_LOCKED_TEXTS")
    for wonder in wonders:
        lines.append(locked_text(wonder))
    lines.append("### END TV_WONDER_MECHANICS_LOCKED_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_PROPOSAL_BUTTONS")
    for slot in range(1, 4):
        for wonder in wonders:
            lines.append(proposal_button(slot, wonder))
    lines.append("### END TV_WONDER_MECHANICS_PROPOSAL_BUTTONS")
    lines.append("")
    for style in range(1, 4):
        lines.append(f"### BEGIN TV_WONDER_MECHANICS_CEREMONY_STYLE_{style}_BUTTONS")
        for wonder in wonders:
            if not wonder.get("is_unique") and style in ceremony_styles(wonder):
                lines.append(ceremony_select_button(wonder, style))
        lines.append(f"### END TV_WONDER_MECHANICS_CEREMONY_STYLE_{style}_BUTTONS")
        lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS")
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            lines.append(active_ritual_text(wonder, style))
    lines.append("### END TV_WONDER_MECHANICS_ACTIVE_RITUAL_TEXTS")
    lines.append("")
    lines.append("### BEGIN TV_WONDER_MECHANICS_HOLD_BUTTONS")
    lines.append(hold_button())
    lines.append("### END TV_WONDER_MECHANICS_HOLD_BUTTONS")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(generate(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
