"""Generate the Academy world debate situation panel GUI."""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

REPO_ROOT = Path(__file__).resolve().parents[5]
DATA_FILE = REPO_ROOT / "data" / "philosophy_debates.yaml"
OUT_FILE = REPO_ROOT / "src" / "in_game" / "gui" / "panels" / "situation" / "tv_academy_world_debate_situation.gui"

T = "\t"
WORLD_SEATS = range(1, 51)


def emit(lines: list[str], level: int, text: str = "") -> None:
    lines.append((T * level + text) if text else "")


def situation_var(name: str) -> str:
    return f"SituationView.GetActiveSituation.GetSituation.MakeScope.GetVariable('{name}')"


def fixed_eq(var_expr: str, value: int) -> str:
    return f"EqualTo_CFixedPoint({var_expr}.GetValue, '(CFixedPoint){value}.0')"


def world_debate_seat_var(seat: int, suffix: str) -> str:
    return f"tv_academy_world_debate_seat_{seat}_{suffix}"


def issue_loc_key(issue: dict) -> str:
    return f"TV_ACADEMY_PHILOSOPHY_NAME_{issue['key'].upper()}"


def append_progress_footer(lines: list[str], level: int, tooltip: str, var_name: str) -> None:
    var_expr = situation_var(var_name)
    emit(lines, level, "hbox = {")
    emit(lines, level + 1, "layoutpolicy_horizontal = fixed")
    emit(lines, level + 1, "size = { 620 26 }")
    emit(lines, level + 1, "spacing = 10")
    emit(lines, level + 1, "widget = {")
    emit(lines, level + 2, "size = { 526 24 }")
    emit(lines, level + 2, "progressbar = {")
    emit(lines, level + 3, "size = { 526 18 }")
    emit(lines, level + 3, "parentanchor = vcenter")
    emit(lines, level + 3, "widgetanchor = vcenter")
    emit(lines, level + 3, "using = progress_bar_blue_alt")
    emit(lines, level + 3, "min = 0")
    emit(lines, level + 3, "max = 100")
    emit(lines, level + 3, f'value = "[{var_expr}.GetValue]"')
    emit(lines, level + 3, f'tooltip = "{tooltip}"')
    emit(lines, level + 2, "}")
    emit(lines, level + 1, "}")
    emit(lines, level + 1, "text_single = {")
    emit(lines, level + 2, "size = { 84 24 }")
    emit(lines, level + 2, f'raw_text = "[{var_expr}.GetValue|0]%"')
    emit(lines, level + 2, "fontsize = 13")
    emit(lines, level + 2, f'tooltip = "{tooltip}"')
    emit(lines, level + 2, "align = right|nobaseline")
    emit(lines, level + 1, "}")
    emit(lines, level, "}")


def append_world_seat_tint(lines: list[str], level: int, seat_set: str, stance_var: str, stance: int, texture: str) -> None:
    emit(lines, level, "widget = {")
    emit(lines, level + 1, f'visible = "[And({seat_set}, {fixed_eq(stance_var, stance)})]"')
    emit(lines, level + 1, "size = { 100% 100% }")
    emit(lines, level + 1, "using = bg_circle_piechart")
    emit(lines, level + 1, "modify_texture = {")
    emit(lines, level + 2, f"using = {texture}")
    emit(lines, level + 2, "blend_mode = overlay")
    emit(lines, level + 2, "alpha = 0.85")
    emit(lines, level + 1, "}")
    emit(lines, level, "}")


def append_world_seat(lines: list[str], level: int, seat: int) -> None:
    country_var = situation_var(world_debate_seat_var(seat, "country"))
    stance_var = situation_var(world_debate_seat_var(seat, "stance"))
    seat_set = f"{country_var}.IsSet"
    emit(lines, level, "widget = {")
    emit(lines, level + 1, "size = { 28 28 }")
    emit(lines, level + 1, "using = bg_circle_piechart")
    emit(lines, level + 1, 'tooltip = "TV_ACADEMY_WORLD_DEBATE_EMPTY_SEAT_TT"')
    append_world_seat_tint(lines, level + 1, seat_set, stance_var, 1, "color_light_green_texture")
    append_world_seat_tint(lines, level + 1, seat_set, stance_var, 2, "color_red_texture")
    append_world_seat_tint(lines, level + 1, seat_set, stance_var, 3, "color_yellow_texture")
    emit(lines, level + 1, "widget = {")
    emit(lines, level + 2, f'visible = "[{seat_set}]"')
    emit(lines, level + 2, "parentanchor = center")
    emit(lines, level + 2, "widgetanchor = center")
    emit(lines, level + 2, "size = { 24 15 }")
    emit(lines, level + 2, f'datacontext = "[{country_var}.GetCountry]"')
    emit(lines, level + 2, 'tooltip = "TV_ACADEMY_WORLD_DEBATE_SEAT_TT"')
    emit(lines, level + 2, "country_flag_small_plus = { size = { 24 15 } }")
    emit(lines, level + 1, "}")
    emit(lines, level + 1, "text_single = {")
    emit(lines, level + 2, f'visible = "[Not({seat_set})]"')
    emit(lines, level + 2, "parentanchor = center")
    emit(lines, level + 2, "size = { 100% 100% }")
    emit(lines, level + 2, 'raw_text = "@diplomacy!"')
    emit(lines, level + 2, "fontsize = 11")
    emit(lines, level + 2, "align = center|nobaseline")
    emit(lines, level + 1, "}")
    emit(lines, level, "}")


def append_issue_label(lines: list[str], level: int, issues: list[dict]) -> None:
    active_expr = situation_var("tv_academy_world_debate_active")
    issue_expr = situation_var("tv_academy_world_debate_issue")
    emit(lines, level, "text_single = {")
    emit(lines, level + 1, f'visible = "[Not({active_expr}.IsSet)]"')
    emit(lines, level + 1, "size = { 620 28 }")
    emit(lines, level + 1, 'text = "TV_ACADEMY_WORLD_DEBATE_EMPTY"')
    emit(lines, level + 1, "fontsize = 16")
    emit(lines, level + 1, "align = center|nobaseline")
    emit(lines, level, "}")
    for issue in issues:
        emit(lines, level, "text_single = {")
        emit(lines, level + 1, f'visible = "[And({active_expr}.IsSet, {fixed_eq(issue_expr, int(issue["id"]))})]"')
        emit(lines, level + 1, "size = { 620 28 }")
        emit(lines, level + 1, f'text = "{issue_loc_key(issue)}"')
        emit(lines, level + 1, "fontsize = 16")
        emit(lines, level + 1, "align = center|nobaseline")
        emit(lines, level, "}")


def generate(data: dict) -> str:
    issues = sorted(data["issues"], key=lambda issue: int(issue["id"]))
    lines: list[str] = [
        "# @Generated by scripts/in_game/gui/panels/situation/gen_tv_academy_world_debate_situation_gui.py",
        "#   Data:    data/philosophy_debates.yaml",
        "#   Regen:   conda run --no-capture-output -n eu5 python scripts/in_game/gui/panels/situation/gen_tv_academy_world_debate_situation_gui.py",
        "# Do not edit directly - modify the data file and re-run the generator.",
        "# Towards Victory - Academy World Debate Situation Panel",
        "",
        "situation_panel = {",
    ]
    emit(lines, 1, 'blockoverride "panel_header" {')
    emit(lines, 2, "window_header_alt = {")
    emit(lines, 3, 'blockoverride "header_text_object" {')
    emit(lines, 4, "hbox = {")
    emit(lines, 5, "spacing = 5")
    emit(lines, 5, "expand = {}")
    emit(lines, 5, "text_single = {")
    emit(lines, 6, 'raw_text = "@diplomacy!"')
    emit(lines, 6, "size = { 30 30 }")
    emit(lines, 6, "fontsize = 22")
    emit(lines, 6, "align = center|nobaseline")
    emit(lines, 5, "}")
    emit(lines, 5, "text_single = {")
    emit(lines, 6, "align = nobaseline")
    emit(lines, 6, "using = Font_Type_Headers")
    emit(lines, 6, "using = Font_Size_Big")
    emit(lines, 6, "maximumsize = { 390 -1 }")
    emit(lines, 6, "autoresize = yes")
    emit(lines, 6, "default_format = \"#header_titles\"")
    emit(lines, 6, "text = \"[SituationView.GetActiveSituation.GetName]\"")
    emit(lines, 5, "}")
    emit(lines, 5, "expand = {}")
    emit(lines, 4, "}")
    emit(lines, 3, "}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0)

    emit(lines, 1, 'blockoverride "panel_content" {')
    emit(lines, 2, "vbox = {")
    emit(lines, 3, "using = layoutpolicy_expanding")
    emit(lines, 3, "using = bg_main_inner_notabs_alt")
    emit(lines, 3, "using = window_main_tabs_margin_alt")
    emit(lines, 3, "visible = \"[Not(SituationView.GetActiveSituation.HasEnded)]\"")
    emit(lines, 3, "spacing = 8")
    emit(lines, 3, "widget = {")
    emit(lines, 4, "layoutpolicy_horizontal = expanding")
    emit(lines, 4, "size = { -1 78 }")
    emit(lines, 4, "using = bg_paper_card_situations")
    emit(lines, 4, "vbox = {")
    emit(lines, 5, "parentanchor = center")
    emit(lines, 5, "widgetanchor = center")
    emit(lines, 5, "size = { 620 58 }")
    emit(lines, 5, "spacing = 4")
    emit(lines, 5, "text_single = {")
    emit(lines, 6, "size = { 620 26 }")
    emit(lines, 6, 'text = "TV_ACADEMY_WORLD_DEBATE_TITLE"')
    emit(lines, 6, "fontsize = 18")
    emit(lines, 6, "align = center|nobaseline")
    emit(lines, 5, "}")
    append_issue_label(lines, 5, issues)
    emit(lines, 4, "}")
    emit(lines, 3, "}")

    emit(lines, 3, "widget = {")
    emit(lines, 4, "layoutpolicy_horizontal = expanding")
    emit(lines, 4, "size = { -1 338 }")
    emit(lines, 4, "using = bg_paper_card_situations")
    emit(lines, 4, "vbox = {")
    emit(lines, 5, "parentanchor = center")
    emit(lines, 5, "widgetanchor = center")
    emit(lines, 5, "size = { 620 314 }")
    emit(lines, 5, "spacing = 8")
    seat = 1
    for _ in range(5):
        emit(lines, 5, "hbox = {")
        emit(lines, 6, "layoutpolicy_horizontal = fixed")
        emit(lines, 6, "size = { 352 28 }")
        emit(lines, 6, "parentanchor = hcenter")
        emit(lines, 6, "spacing = 8")
        for _ in range(10):
            append_world_seat(lines, 6, seat)
            seat += 1
        emit(lines, 5, "}")
    emit(lines, 5, "expand = {}")
    append_progress_footer(lines, 5, "TV_ACADEMY_WORLD_DEBATE_STRENGTH_TT", "tv_academy_world_debate_strength")
    append_progress_footer(lines, 5, "TV_ACADEMY_WORLD_DEBATE_PROGRESS_TT", "tv_academy_world_debate_progress")
    emit(lines, 4, "}")
    emit(lines, 3, "}")
    emit(lines, 3, "expand = {}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Print to stdout instead of writing")
    args = parser.parse_args()

    with DATA_FILE.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    content = generate(data)
    if args.dry:
        print(content)
    else:
        OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUT_FILE.write_text(content, encoding="utf-8-sig")
        print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
