#!/usr/bin/env python
"""Build the static Unique Wonders Map site."""

from __future__ import annotations

import argparse
import json
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
WONDER_IMAGE_SOURCE_ROOT = REPO_ROOT / "data" / "generated_wonders"


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


def copy_wonder_images() -> None:
    payload_path = DATA_ROOT / "unique_wonders.json"
    require_path(payload_path, "unique wonders data")

    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    records = payload.get("wonders", [])
    if not isinstance(records, list):
        raise TypeError(f"{payload_path}.wonders must be a list")

    copied = 0
    missing: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            continue

        image_id = str(record.get("image") or record.get("key") or "").strip()
        image_path = str(record.get("image_path") or "").strip()
        if not image_path:
            missing.append(image_id)
            continue

        relative_image_path = Path(image_path)
        if relative_image_path.is_absolute() or ".." in relative_image_path.parts:
            raise ValueError(f"Invalid wonder image path in {payload_path}: {image_path}")

        source = WONDER_IMAGE_SOURCE_ROOT / relative_image_path.name
        if not source.exists():
            missing.append(image_id)
            continue

        destination = DIST_ROOT / relative_image_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied += 1

    print(f"copied {copied} wonder images", flush=True)
    if missing:
        print(f"missing wonder images: {', '.join(missing)}", flush=True)


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
    step("wonder image assets", copy_wonder_images)
    print("\n=== unique_wonders_site build complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
