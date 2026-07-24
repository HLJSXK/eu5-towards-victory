"""Generate Victory Path Tree unlock effects + points trickle from data/victory_path_tree_variant.yaml."""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.victory_tree_node_codegen import generate_effects, load_data, write_output

REGEN_SCRIPT = "scripts/in_game/common/scripted_effects/gen_tv_victory_tree_effects.py"
OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_victory_tree_effects.txt"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Print to stdout instead of writing")
    args = parser.parse_args()

    content = generate_effects(load_data(), REGEN_SCRIPT)
    if args.dry:
        print(content)
    else:
        write_output(OUT_FILE, content)
        print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
