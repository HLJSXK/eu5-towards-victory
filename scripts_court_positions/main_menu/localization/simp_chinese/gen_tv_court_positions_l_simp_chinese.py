import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts_court_positions.court_positions_codegen import load_positions, render_localization

SCRIPT_REL = "scripts_court_positions/main_menu/localization/simp_chinese/gen_tv_court_positions_l_simp_chinese.py"
OUT_FILE = REPO_ROOT / "src_court_positions/main_menu/localization/simp_chinese/tv_court_positions_l_simp_chinese.yml"


def main() -> None:
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_bytes(render_localization(load_positions(), SCRIPT_REL, "simp_chinese"))
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
