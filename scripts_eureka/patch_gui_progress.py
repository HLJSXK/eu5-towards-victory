"""
Towards Victory — Eureka Prototype: GUI Progress Value Patcher

This script patches GUI progress rows with a visual Eureka offset.  Rows that
already expose an `AdvanceNode`/`AdvanceItem` use that typed object's key;
global current-research widgets use the current advance definition's scope key.

The resulting expression is deliberately visual-only: the scripted research
speed modifier remains the source of truth for actual research progress.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]  # scripts_eureka/ is one level below repo root

VANILLA_GUI = REPO_ROOT / "reference_game_files" / "game" / "in_game" / "gui"
OUTPUT_GUI = REPO_ROOT / "src_eureka" / "in_game" / "gui"

# Files to patch
TARGET_FILES = [
    "technology_lateralview.gui",
    "agenda_view.gui",
    "advances_lateralview.gui",
    "hud_topbar.gui",
]

# Pattern: find `value = "[Player.GetCurrentResearch.GetProgress]"`
# Node/list rows replace it with a key-gated visual progress expression.
#
# Also handle: `value = "[Subtract_float('(float)1.0', Player.GetCurrentResearch.GetProgress)]"`
# Replace with a key-gated expression that uses the same boosted value only
# when the row's `AdvanceNode` or `AdvanceItem` key is `guilds`.
#
# Also handle text displays: `text = "[Player.GetCurrentResearch.GetProgress|2%]"`.

PROGRESS_PATTERN = re.compile(
    r'(value\s*=\s*"\[)Player\.GetCurrentResearch\.GetProgress(\]")'
)

SUBTRACT_PATTERN = re.compile(
    r"(value\s*=\s*\"\[Subtract_float\('?\(float\)1\.0'?,\s*)Player\.GetCurrentResearch\.GetProgress(\)\]\")"
)

TEXT_PATTERN = re.compile(
    r'(text\s*=\s*"\[)Player\.GetCurrentResearch\.GetProgress(\|[^]]+\]")'
)

BOOST_EXPR = "Min_float(Add_float(Player.GetCurrentResearch.GetProgress, FixedPointToFloat(Player.MakeScope.GetVariable('tv_eureka_visual_boost_guilds').GetValue)), '(float)1.0')"
NODE_PROGRESS_EXPR = "Select_float(EqualTo_string(AdvanceNode.GetItem.GetKey, 'guilds'), {boost}, Player.GetCurrentResearch.GetProgress)"
ITEM_PROGRESS_EXPR = "Select_float(EqualTo_string(AdvanceItem.GetKey, 'guilds'), {boost}, Player.GetCurrentResearch.GetProgress)"
# Current-research widgets do not expose a verified raw advance key accessor.
# Compare the tooltip-free display name to the same localization key instead of
# using MakeScope.GetFlagName, which Jomini may localize before returning it.
CURRENT_PROGRESS_EXPR = "Select_float(EqualTo_string(Player.GetCurrentResearch.GetAdvance.GetDefinition.GetNameWithNoTooltip, Localize('guilds')), {boost}, Player.GetCurrentResearch.GetProgress)"


def patch_file(input_path: Path, output_path: Path):
    """Patch one GUI file with an advance-key-gated eureka formula."""
    content = input_path.read_text(encoding="utf-8")
    original = content

    # Tree rows have an AdvanceNode context, while list rows have AdvanceItem.
    if input_path.name == "technology_lateralview.gui":
        progress_expr = NODE_PROGRESS_EXPR.format(boost=BOOST_EXPR)
        # The first two pie slices and first percentage belong to tree nodes.
        direct_seen = 0
        subtract_seen = 0
        text_seen = 0

        current_expr = CURRENT_PROGRESS_EXPR.format(boost=BOOST_EXPR)

        def replace_direct(match):
            nonlocal direct_seen
            direct_seen += 1
            expression = progress_expr if direct_seen <= 2 else current_expr
            return rf"{match.group(1)}{expression}{match.group(2)}"

        def replace_subtract(match):
            nonlocal subtract_seen
            subtract_seen += 1
            expression = progress_expr if subtract_seen <= 2 else current_expr
            return rf"{match.group(1)}{expression}{match.group(2)}"

        def replace_text(match):
            nonlocal text_seen
            text_seen += 1
            expression = progress_expr if text_seen <= 1 else current_expr
            return rf"{match.group(1)}{expression}{match.group(2)}"

        content = PROGRESS_PATTERN.sub(replace_direct, content)
        content = SUBTRACT_PATTERN.sub(replace_subtract, content)
        content = TEXT_PATTERN.sub(replace_text, content)
    elif input_path.name == "advances_lateralview.gui":
        progress_expr = ITEM_PROGRESS_EXPR.format(boost=BOOST_EXPR)
        content = PROGRESS_PATTERN.sub(rf'\1{progress_expr}\2', content)
        content = SUBTRACT_PATTERN.sub(rf'\1{progress_expr}\2', content)
        content = TEXT_PATTERN.sub(rf'\1{progress_expr}\2', content)
    else:
        # Agenda and top-bar widgets only expose CurrentResearch.
        current_expr = CURRENT_PROGRESS_EXPR.format(boost=BOOST_EXPR)
        content = PROGRESS_PATTERN.sub(rf'\1{current_expr}\2', content)
        content = SUBTRACT_PATTERN.sub(rf'\1{current_expr}\2', content)
        content = TEXT_PATTERN.sub(rf'\1{current_expr}\2', content)

    # Always emit a copy so generated output stays in sync with vanilla.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    # Count source matches for a useful regeneration summary.
    direct_count = len(PROGRESS_PATTERN.findall(original))
    subtract_count = len(SUBTRACT_PATTERN.findall(original))
    text_count = len(TEXT_PATTERN.findall(original))
    total = direct_count + subtract_count + text_count
    changed = "updated" if content != original else "copied"
    print(f"OK {input_path.name}: {changed}; {total} source matches ({direct_count} direct, {subtract_count} subtract, {text_count} text)")
    return total


def main():
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("Patching GUI files for eureka visual progress boost...\n")

    total_replacements = 0
    for filename in TARGET_FILES:
        input_path = VANILLA_GUI / filename
        output_path = OUTPUT_GUI / filename

        if not input_path.exists():
            print(f"X {filename}: source file not found")
            continue

        replacements = patch_file(input_path, output_path)
        total_replacements += replacements

    # Keep the current-research tooltip row in sync with the same gated
    # expression; this row lives inside technology_lateralview.gui too.
    from patch_gui_progress_info import patch_progress_info
    patch_progress_info()

    print(f"\nDone. {total_replacements} total replacements across {len(TARGET_FILES)} files.")
    print(f"Output: {OUTPUT_GUI}")


if __name__ == "__main__":
    main()
