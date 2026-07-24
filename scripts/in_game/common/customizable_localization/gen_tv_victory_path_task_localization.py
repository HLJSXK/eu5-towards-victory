import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_task_codegen import generate_customizable_localization, load_data, write_output

SCRIPT = "scripts/in_game/common/customizable_localization/gen_tv_victory_path_task_localization.py"
OUT = REPO_ROOT / "src/in_game/common/customizable_localization/tv_victory_path_task_localization.txt"

if __name__ == "__main__":
    write_output(OUT, generate_customizable_localization(load_data(), SCRIPT))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}")
