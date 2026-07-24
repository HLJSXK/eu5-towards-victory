import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_task_codegen import generate_actions, load_data, write_output

SCRIPT = "scripts/in_game/common/generic_actions/gen_tv_victory_path_task_actions.py"
OUT = REPO_ROOT / "src/in_game/common/generic_actions/tv_victory_path_task_actions.txt"

if __name__ == "__main__":
    write_output(OUT, generate_actions(load_data(), SCRIPT))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}")
