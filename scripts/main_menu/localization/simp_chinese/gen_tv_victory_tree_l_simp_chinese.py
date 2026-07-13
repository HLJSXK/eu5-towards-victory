"""Generate Victory Path Tree node Simplified Chinese localization from data/victory_path_tree_variant.yaml."""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_tree_node_codegen import generate_loc, load_data, write_output

REGEN_SCRIPT = "scripts/main_menu/localization/simp_chinese/gen_tv_victory_tree_l_simp_chinese.py"
OUT_FILE = REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_victory_tree_l_simp_chinese.yml"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Print to stdout instead of writing")
    args = parser.parse_args()

    content = generate_loc(load_data(), REGEN_SCRIPT, lang="zh")
    if args.dry:
        print(content)
    else:
        write_output(OUT_FILE, content)
        print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
