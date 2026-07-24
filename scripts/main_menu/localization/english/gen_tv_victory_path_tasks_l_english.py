import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_task_codegen import generate_localization, load_data, write_output

SCRIPT = "scripts/main_menu/localization/english/gen_tv_victory_path_tasks_l_english.py"
OUT = REPO_ROOT / "src/main_menu/localization/english/tv_victory_path_tasks_l_english.yml"

if __name__ == "__main__":
    write_output(OUT, generate_localization(load_data(), SCRIPT, language="english"))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}")
