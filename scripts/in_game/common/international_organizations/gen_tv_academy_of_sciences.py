"""Generate the Academy of Sciences international_organization_type definition."""

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.philosophy_debate_codegen import generate_academy_io, load_data, write_output

OUT_FILE = (
    REPO_ROOT
    / "src"
    / "in_game"
    / "common"
    / "international_organizations"
    / "tv_academy_of_sciences.txt"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Print to stdout instead of writing")
    args = parser.parse_args()

    content = generate_academy_io(load_data())
    if args.dry:
        print(content)
    else:
        write_output(OUT_FILE, content)
        print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
