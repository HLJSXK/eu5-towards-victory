"""Generate Eureka GUI overrides from the checked-in vanilla GUI files.

Each run starts with the corresponding file under ``reference_game_files``
and applies anchored, count-checked replacements.  This keeps the deployable
GUI files as reproducible vanilla copies instead of hand-maintained forks.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
VANILLA_IN_GAME_GUI = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "gui"
VANILLA_SHARED_GUI = REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "gui" / "shared"
OUTPUT_IN_GAME_GUI = REPO_ROOT / "src_eureka" / "in_game" / "gui"
OUTPUT_SHARED_GUI = REPO_ROOT / "src_eureka" / "main_menu" / "gui" / "shared"

TARGET_IN_GAME_FILES = (
    "technology_lateralview.gui",
    "agenda_view.gui",
    "advances_lateralview.gui",
    "hud_topbar.gui",
)

PROGRESS_PATTERN = re.compile(r'(value\s*=\s*"\[)Player\.GetCurrentResearch\.GetProgress(\]")')
SUBTRACT_PATTERN = re.compile(
    r"(value\s*=\s*\"\[Subtract_float\('?\(float\)1\.0'?,\s*)"
    r"Player\.GetCurrentResearch\.GetProgress(\)\]\")"
)
TEXT_PATTERN = re.compile(
    r'(text\s*=\s*"\[)Player\.GetCurrentResearch\.GetProgress(\|[^]]+\]")'
)

BOOST_EXPR = (
    "Min_float(Add_float(Player.GetCurrentResearch.GetProgress, "
    "FixedPointToFloat(Player.MakeScope.GetVariable('tv_eureka_visual_boost_guilds').GetValue)), "
    "'(float)1.0')"
)
NODE_PROGRESS_EXPR = (
    "Select_float(EqualTo_string(AdvanceNode.GetItem.GetKey, 'guilds'), "
    f"{BOOST_EXPR}, Player.GetCurrentResearch.GetProgress)"
)
ITEM_PROGRESS_EXPR = (
    "Select_float(EqualTo_string(AdvanceItem.GetKey, 'guilds'), "
    f"{BOOST_EXPR}, Player.GetCurrentResearch.GetProgress)"
)
CURRENT_PROGRESS_EXPR = (
    "Select_float(EqualTo_string("
    "Player.GetCurrentResearch.GetAdvance.GetDefinition.GetNameWithNoTooltip, Localize('guilds')), "
    f"{BOOST_EXPR}, Player.GetCurrentResearch.GetProgress)"
)

EUREKA_TEMPLATE = """template tv_eureka_guilds_research_bonus_tooltip {
\tTooltipTextBlock = {
\t\tvisible = \"[And3(Player.GetCurrentResearch.IsActive, EqualTo_string(Player.GetCurrentResearch.GetAdvance.GetDefinition.GetNameWithNoTooltip, Localize('guilds')), Player.MakeScope.GetVariable('tv_eureka_boost_active_guilds').IsSet)]\"
\t\tblockoverride \"text\" {
\t\t\ttext = \"TV_EUREKA_GUILDS_RESEARCH_SPEED_TOOLTIP\"
\t\t}
\t}
}
"""


def _configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _read_gui(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def _write_gui(path: Path, content: str) -> None:
    # Keep the established UTF-8 BOM convention for deployable text files.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip("\n") + "\n", encoding="utf-8-sig", newline="\n")


def _replace_regex(
    content: str,
    pattern: re.Pattern[str],
    replacement: str | Callable[[re.Match[str]], str],
    expected: int,
    label: str,
) -> str:
    content, count = pattern.subn(replacement, content)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} replacement(s), found {count}")
    return content


def _replace_literal(content: str, old: str, new: str, expected: int, label: str) -> str:
    count = content.count(old)
    if count != expected:
        raise RuntimeError(f"{label}: expected {expected} occurrence(s), found {count}")
    return content.replace(old, new)


def _patch_progress_bindings(filename: str, content: str) -> str:
    expected = {
        "technology_lateralview.gui": (4, 4, 2),
        "agenda_view.gui": (2, 2, 0),
        "advances_lateralview.gui": (2, 2, 1),
        "hud_topbar.gui": (1, 1, 0),
    }[filename]
    direct_index = subtract_index = text_index = 0

    def direct(match: re.Match[str]) -> str:
        nonlocal direct_index
        direct_index += 1
        if filename == "technology_lateralview.gui" and direct_index <= 2:
            expression = NODE_PROGRESS_EXPR
        elif filename == "advances_lateralview.gui":
            expression = ITEM_PROGRESS_EXPR
        else:
            expression = CURRENT_PROGRESS_EXPR
        return f"{match.group(1)}{expression}{match.group(2)}"

    def subtract(match: re.Match[str]) -> str:
        nonlocal subtract_index
        subtract_index += 1
        if filename == "technology_lateralview.gui" and subtract_index <= 2:
            expression = NODE_PROGRESS_EXPR
        elif filename == "advances_lateralview.gui":
            expression = ITEM_PROGRESS_EXPR
        else:
            expression = CURRENT_PROGRESS_EXPR
        return f"{match.group(1)}{expression}{match.group(2)}"

    def text(match: re.Match[str]) -> str:
        nonlocal text_index
        text_index += 1
        if filename == "technology_lateralview.gui" and text_index <= 1:
            expression = NODE_PROGRESS_EXPR
        elif filename == "advances_lateralview.gui":
            expression = ITEM_PROGRESS_EXPR
        else:
            expression = CURRENT_PROGRESS_EXPR
        return f"{match.group(1)}{expression}{match.group(2)}"

    content = PROGRESS_PATTERN.sub(direct, content)
    content = SUBTRACT_PATTERN.sub(subtract, content)
    content = TEXT_PATTERN.sub(text, content)
    observed = (direct_index, subtract_index, text_index)
    if observed != expected:
        raise RuntimeError(f"{filename}: expected progress match counts {expected}, found {observed}")
    return content


def _patch_advances_effect_list(content: str) -> str:
    datamodel = re.compile(
        r'(?m)^(?P<i>[ \t]*)datacontext = "\[StringToStringPairList\(AdvanceItem\.GetEffects\)\]"\n'
        r'(?P=i)datamodel = "\[StringPairList\.GetRows\]"'
    )
    content = _replace_regex(
        content,
        datamodel,
        lambda m: f'{m.group("i")}datamodel = "[AdvanceItem.GetAdvanceEffectItemsNoTooltip]"\n'
        f'{m.group("i")}ignoreinvisible = yes',
        1,
        "advances effect-list datamodel",
    )
    row_layout = re.compile(
        r'(?m)^(?P<i>[ \t]*)layoutpolicy_horizontal = expanding\n'
        r'(?P=i)margin = \{ 5 0 \}'
    )
    content = _replace_regex(
        content,
        row_layout,
        lambda m: f'{m.group("i")}layoutpolicy_horizontal = expanding\n'
        f'{m.group("i")}visible = "[Not(And(Player.MakeScope.GetVariable(Concatenate(\'tv_eureka_boost_active_\', AdvanceItem.GetKey)).IsSet, StringContains(AdvanceEffectItem.GetIcon, \'research_speed\')))]"\n'
        f'{m.group("i")}margin = {{ 5 0 }}',
        1,
        "advances effect-list row visibility",
    )
    content = _replace_literal(
        content,
        'text = "[StringViewPair.GetLeft.GetStringView]"',
        'text = "[AdvanceEffectItem.GetTitleEffect]"',
        1,
        "advances effect title",
    )
    return _replace_literal(
        content,
        'text = "[StringViewPair.GetRight.GetStringView]"',
        'text = "[AdvanceEffectItem.GetDescEffect]"',
        1,
        "advances effect description",
    )


def _patch_technology_effect_lists(content: str) -> str:
    datamodel = re.compile(
        r'(?m)^(?P<i>[ \t]*)datamodel = "\[AdvanceNode\.GetItem\.GetAdvanceEffectItemsNoTooltip\]"$'
    )
    content = _replace_regex(
        content,
        datamodel,
        lambda m: f'{m.group("i")}datamodel = "[AdvanceNode.GetItem.GetAdvanceEffectItemsNoTooltip]"\n'
        f'{m.group("i")}ignoreinvisible = yes',
        2,
        "technology effect-list datamodel",
    )
    row_layout = re.compile(
        r'(?m)^(?P<i>[ \t]*)layoutpolicy_horizontal = expanding\n'
        r'(?:(?P<blank>[ \t]*\n))?(?P=i)using = bg_text_mask_container_brown'
    )
    return _replace_regex(
        content,
        row_layout,
        lambda m: f'{m.group("i")}layoutpolicy_horizontal = expanding\n'
        f'{m.group("i")}visible = "[Not(And(Player.MakeScope.GetVariable(Concatenate(\'tv_eureka_boost_active_\', AdvanceNode.GetItem.GetKey)).IsSet, StringContains(AdvanceEffectItem.GetIcon, \'research_speed\')))]"\n'
        f'{m.group("blank") or ""}{m.group("i")}using = bg_text_mask_container_brown',
        2,
        "technology effect-list row visibility",
    )


def _patch_progress_info(content: str) -> str:
    old = re.compile(
        r'(?m)^(?P<i>[ \t]*)TooltipStringPairList = \{\n'
        r'(?P=i)\tblockoverride "block_title" \{\n'
        r'(?P=i)\t\ttext = "\[Player\.GetCurrentResearch\.GetProgressInfo\]"\n'
        r'(?P=i)\t\}\n'
        r'(?P=i)\ttextcontext = "\[Player\.GetCurrentResearch\.GetResearchCost\]"\n'
        r'(?P=i)\}'
    )

    def replacement(match: re.Match[str]) -> str:
        i = match.group("i")
        return "\n".join(
            [
                f"{i}hbox = {{",
                f"{i}\tlayoutpolicy_horizontal = expanding",
                f'{i}\ttext_single = {{',
                f'{i}\t\ttext = "TV_EUREKA_PROGRESS_INFO"',
                f"{i}\t}}",
                f"{i}\texpand = {{}}",
                f'{i}\ttext_single = {{',
                f'{i}\t\ttext = "[{CURRENT_PROGRESS_EXPR}|0%]"',
                f"{i}\t}}",
                f'{i}\ttext_single = {{',
                f'{i}\t\traw_text = " / "',
                f"{i}\t}}",
                f'{i}\ttext_single = {{',
                f'{i}\t\ttext = "[Player.GetCurrentResearch.GetResearchCost]"',
                f"{i}\t}}",
                f"{i}}}",
            ]
        )

    return _replace_regex(content, old, replacement, 1, "technology current-research progress row")


def patch_in_game_file(filename: str) -> None:
    source = VANILLA_IN_GAME_GUI / filename
    if not source.exists():
        raise FileNotFoundError(source)
    content = _patch_progress_bindings(filename, _read_gui(source))
    if filename == "advances_lateralview.gui":
        content = _patch_advances_effect_list(content)
    elif filename == "technology_lateralview.gui":
        content = _patch_technology_effect_lists(content)
        content = _patch_progress_info(content)
    output = OUTPUT_IN_GAME_GUI / filename
    _write_gui(output, content)
    print(f"OK {output.relative_to(REPO_ROOT)}")


def _patch_shared_tooltips() -> None:
    source = VANILLA_SHARED_GUI / "advances_tooltips.gui"
    content = EUREKA_TEMPLATE + _read_gui(source)
    content = _replace_regex(
        content,
        PROGRESS_PATTERN,
        lambda m: f"{m.group(1)}{CURRENT_PROGRESS_EXPR}{m.group(2)}",
        2,
        "shared tooltip progress slices",
    )
    content = _replace_regex(
        content,
        SUBTRACT_PATTERN,
        lambda m: f"{m.group(1)}{CURRENT_PROGRESS_EXPR}{m.group(2)}",
        2,
        "shared tooltip progress remainder slices",
    )

    active_pair = re.compile(
        r'(?m)^(?P<i>\t{5})TooltipStringPairList = \{[ \t]*\n'
        r'(?P=i)\tblockoverride "block_title" \{\n'
        r'(?P=i)\t\ttext = "RES_MONTHLY_PROGRESS"\n'
        r'(?P=i)\t\}\n'
        r'(?P=i)\ttextcontext = "\[Player\.GetDoubleDescriptionFor\(\'research_speed\', \'research_speed_modifier\'\)\]"\n'
        r'(?P=i)\}'
    )
    content = _replace_regex(
        content,
        active_pair,
        lambda m: m.group(0) + f'\n{m.group("i")}using = tv_eureka_guilds_research_bonus_tooltip',
        1,
        "active research-speed tooltip Eureka row",
    )
    for target in ("TechnologyLateralView.GetResearchSpeedTooltip", "AdvancesLateralView.GetResearchSpeedTooltip"):
        needle = f'\t\t\t\ttextcontext = "[{target}]"\n\t\t\t}}\n'
        content = _replace_literal(
            content,
            needle,
            needle + '\t\t\tusing = tv_eureka_guilds_research_bonus_tooltip\n',
            1,
            f"{target} Eureka row",
        )
    output = OUTPUT_SHARED_GUI / "advances_tooltips.gui"
    _write_gui(output, content)
    print(f"OK {output.relative_to(REPO_ROOT)}")


def generate() -> None:
    for filename in TARGET_IN_GAME_FILES:
        patch_in_game_file(filename)
    _patch_shared_tooltips()


def main() -> int:
    _configure_stdio()
    print("Generating Eureka GUI overrides from reference_game_files...\n")
    try:
        generate()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
