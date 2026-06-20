import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from in_game.common.scripted_effects.gen_tv_engineering_department_wonder_mechanics_effects import (
    generate_proposal_effects,
)

OUT_FILE = REPO_ROOT / "src" / "in_game" / "common" / "scripted_effects" / "tv_wonder_proposal_effects.txt"


def main() -> None:
    OUT_FILE.write_text("\ufeff" + generate_proposal_effects(), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
