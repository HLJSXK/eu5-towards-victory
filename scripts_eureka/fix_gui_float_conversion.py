"""Fix GUI files: wrap GetValue in FixedPointToFloat"""

from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
GUI_DIR = REPO_ROOT / "src_eureka" / "in_game" / "gui"

def fix_file(path: Path):
    content = path.read_text(encoding="utf-8")
    original = content

    # Replace: Player.MakeScope.GetVariable('tv_eureka_visual_boost_guilds').GetValue
    # With: FixedPointToFloat(Player.MakeScope.GetVariable('tv_eureka_visual_boost_guilds').GetValue)

    pattern = r"Player\.MakeScope\.GetVariable\('tv_eureka_visual_boost_guilds'\)\.GetValue"
    replacement = r"FixedPointToFloat(Player.MakeScope.GetVariable('tv_eureka_visual_boost_guilds').GetValue)"

    content = re.sub(pattern, replacement, content)

    if content != original:
        path.write_text(content, encoding="utf-8")
        count = content.count(replacement)
        print(f"Fixed {path.name}: {count} replacements")
        return count
    return 0

def main():
    total = 0
    for gui_file in GUI_DIR.glob("*.gui"):
        total += fix_file(gui_file)
    print(f"\nTotal: {total} replacements")

if __name__ == "__main__":
    main()
