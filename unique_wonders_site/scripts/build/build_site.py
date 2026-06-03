#!/usr/bin/env python
"""Build the static Unique Wonders Map site."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
SITE_ROOT = REPO_ROOT / "unique_wonders_site"
DIST_ROOT = SITE_ROOT / "dist"
DATA_ROOT = DIST_ROOT / "data"
REFERENCE_DIST = REPO_ROOT / "reference_mods" / "national_destinies_site" / "dist"
HERE = Path(__file__).resolve().parent


def require_path(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {label}: {path}")


def step(label: str, action) -> None:
    print(f"\n=== {label} ===", flush=True)
    started = time.time()
    action()
    print(f"--- {label} done in {time.time() - started:.1f}s ---", flush=True)


def copy_map_assets() -> None:
    require_path(REFERENCE_DIST / "tiles", "reference map tiles")
    require_path(REFERENCE_DIST / "data" / "locations_index.json", "reference locations index")

    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        REFERENCE_DIST / "data" / "locations_index.json",
        DATA_ROOT / "locations_index.json",
    )
    shutil.copytree(
        REFERENCE_DIST / "tiles",
        DIST_ROOT / "tiles",
        dirs_exist_ok=True,
    )


def build_wonders() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(HERE / "build_wonders.py"),
            "--locations-index",
            str(DATA_ROOT / "locations_index.json"),
            "--out",
            str(DATA_ROOT / "unique_wonders.json"),
        ],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def build_static_indexes() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "gen_index.py"),
        ],
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-map-assets",
        action="store_true",
        help="Do not refresh copied reference tiles or locations_index.json.",
    )
    args = parser.parse_args()

    if not args.skip_map_assets:
        step("map assets", copy_map_assets)
    step("static localization indexes", build_static_indexes)
    step("unique wonders data", build_wonders)
    print("\n=== unique_wonders_site build complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
