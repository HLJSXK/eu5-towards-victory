"""Patch the current-research progress row in the Eureka GUI override."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GUI_DIR = REPO_ROOT / "src_eureka" / "in_game" / "gui"
TARGET_FILE = GUI_DIR / "technology_lateralview.gui"

OLD_BLOCK = re.compile(
    r'''TooltipStringPairList = \{
\s+blockoverride "block_title" \{
\s+text = "\[Player\.GetCurrentResearch\.GetProgressInfo\]"
\s+\}
\s+textcontext = "\[Player\.GetCurrentResearch\.GetResearchCost\]"
\s+\}''',
    flags=re.MULTILINE,
)

CURRENT_PROGRESS = (
    "Select_float(EqualTo_string("
    "Player.GetCurrentResearch.GetAdvance.GetDefinition.GetNameWithNoTooltip, Localize('guilds')), "
    "Min_float(Add_float(Player.GetCurrentResearch.GetProgress, "
    "FixedPointToFloat(Player.MakeScope.GetVariable('tv_eureka_visual_boost_guilds').GetValue)), "
    "'(float)1.0'), Player.GetCurrentResearch.GetProgress)"
)

NEW_BLOCK = f'''hbox = {{
\t\t\t\t\t\t\t\t\t\tlayoutpolicy_horizontal = expanding
\t\t\t\t\t\t\t\t\t\ttext_single = {{
\t\t\t\t\t\t\t\t\t\t\ttext = "TV_EUREKA_PROGRESS_INFO"
\t\t\t\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\t\t\t\texpand = {{}}
\t\t\t\t\t\t\t\t\t\ttext_single = {{
\t\t\t\t\t\t\t\t\t\t\ttext = "[{CURRENT_PROGRESS}|0%]"
\t\t\t\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\t\t\t\ttext_single = {{
\t\t\t\t\t\t\t\t\t\t\traw_text = " / "
\t\t\t\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\t\t\t\ttext_single = {{
\t\t\t\t\t\t\t\t\t\t\ttext = "[Player.GetCurrentResearch.GetResearchCost]"
\t\t\t\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\t\t\t\t}}'''


def patch_progress_info():
    """Replace the vanilla tooltip pair with a guilds-gated progress row."""
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not TARGET_FILE.exists():
        print(f"Error: {TARGET_FILE} not found. Run patch_gui_progress.py first.")
        return

    content = TARGET_FILE.read_text(encoding="utf-8")
    patched, count = OLD_BLOCK.subn(NEW_BLOCK, content, count=1)

    if count:
        TARGET_FILE.write_text(patched, encoding="utf-8")
        print(f"OK: Patched GetProgressInfo in {TARGET_FILE.name}")
    else:
        print(f"Warning: GetProgressInfo pattern not found in {TARGET_FILE.name}")


if __name__ == "__main__":
    patch_progress_info()
