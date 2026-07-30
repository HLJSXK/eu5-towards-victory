from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


REPO_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATHS = (
    Path("src/.metadata/metadata.json"),
    Path("src_engineering_department/.metadata/metadata.json"),
    Path("src_court_positions/.metadata/metadata.json"),
    Path("submods/tv_meiou_and_taxes_compat/.metadata/metadata.json"),
    Path("submods/tv_prosper_or_perish_compat/.metadata/metadata.json"),
    Path("submods/tv_standard_of_living_compat/.metadata/metadata.json"),
)
INTERNAL_DEPENDENCY_IDS = {"hades.towards_victory.great_project"}


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an ISO date (YYYY-MM-DD)") from exc


def expected_metadata(metadata: dict[str, object], version: str) -> dict[str, object]:
    updated = copy.deepcopy(metadata)
    updated["version"] = version

    relationships = updated.get("relationships", [])
    if not isinstance(relationships, list):
        raise ValueError("'relationships' must be a list")

    for relationship in relationships:
        if not isinstance(relationship, dict):
            raise ValueError("each relationship must be an object")
        if relationship.get("id") in INTERNAL_DEPENDENCY_IDS:
            relationship["version"] = version

    return updated


def read_metadata(path: Path) -> dict[str, object]:
    metadata = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(metadata, dict):
        raise ValueError("metadata root must be an object")
    return metadata


def write_metadata(path: Path, metadata: dict[str, object]) -> None:
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stamp all first-party mod metadata with a YYMMDD date version."
    )
    parser.add_argument(
        "--date",
        type=parse_date,
        default=date.today(),
        help="date to stamp in YYYY-MM-DD form (default: today)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report stale metadata without modifying files",
    )
    args = parser.parse_args()

    version = args.date.strftime("%y%m%d")
    pending: list[tuple[Path, dict[str, object]]] = []

    try:
        for relative_path in METADATA_PATHS:
            path = REPO_ROOT / relative_path
            current = read_metadata(path)
            expected = expected_metadata(current, version)
            if current != expected:
                pending.append((path, expected))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"[ERROR] Could not prepare mod version {version}: {exc}", file=sys.stderr)
        return 1

    if args.check:
        if pending:
            for path, _ in pending:
                print(f"[STALE] {path.relative_to(REPO_ROOT)}")
            print(f"[ERROR] Mod metadata is not stamped with version {version}.")
            return 1
        print(f"[OK] All mod metadata uses version {version}.")
        return 0

    try:
        for path, expected in pending:
            write_metadata(path, expected)
            print(f"[UPDATED] {path.relative_to(REPO_ROOT)} -> {version}")
    except OSError as exc:
        print(f"[ERROR] Could not write mod version {version}: {exc}", file=sys.stderr)
        return 1

    if not pending:
        print(f"[OK] All mod metadata already uses version {version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
