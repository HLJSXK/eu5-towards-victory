import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_task_codegen import generate_triggers, load_data, write_output

SCRIPT = "scripts/in_game/common/scripted_triggers/gen_tv_victory_path_task_triggers.py"
OUT = REPO_ROOT / "src/in_game/common/scripted_triggers/tv_victory_path_task_triggers.txt"

if __name__ == "__main__":
    write_output(OUT, generate_triggers(load_data(), SCRIPT))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}")
