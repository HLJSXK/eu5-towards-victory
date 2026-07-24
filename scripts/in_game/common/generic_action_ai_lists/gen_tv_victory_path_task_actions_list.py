import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_task_codegen import generate_ai_list, load_data, write_output

SCRIPT = "scripts/in_game/common/generic_action_ai_lists/gen_tv_victory_path_task_actions_list.py"
OUT = REPO_ROOT / "src/in_game/common/generic_action_ai_lists/tv_victory_path_task_actions_list.txt"

if __name__ == "__main__":
    write_output(OUT, generate_ai_list(load_data(), SCRIPT))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}")
