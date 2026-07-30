import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts_court_positions.court_positions_codegen import load_positions, render_action_ai_list

SCRIPT_REL = "scripts_court_positions/in_game/common/generic_action_ai_lists/gen_tv_court_positions_actions_list.py"
OUT_FILE = REPO_ROOT / "src_court_positions/in_game/common/generic_action_ai_lists/tv_court_positions_actions_list.txt"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(render_action_ai_list(load_positions(), SCRIPT_REL), encoding="utf-8-sig")
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
