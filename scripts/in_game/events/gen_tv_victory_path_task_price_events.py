import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_task_codegen import generate_price_events, load_data, write_output

SCRIPT = "scripts/in_game/events/gen_tv_victory_path_task_price_events.py"
OUT = REPO_ROOT / "src/in_game/events/0000_tv_victory_path_task_price_events.txt"

if __name__ == "__main__":
    write_output(OUT, generate_price_events(load_data(), SCRIPT))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}")
