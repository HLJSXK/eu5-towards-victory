#!/usr/bin/env python3
"""Allocate free Engineering Department event IDs for unique ritual specs."""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_unique_ritual_harness import (  # noqa: E402
    SPEC_FILE,
    allocate_event_ids,
    collect_occupied_engineering_event_ids,
    event_ids_in_entry,
    load_spec_data,
)


def spec_event_ids() -> set[int]:
    if not SPEC_FILE.exists():
        return set()
    payload = load_spec_data()
    ids: set[int] = set()
    for entry in payload.get("unique_wonders", []) or []:
        if isinstance(entry, dict):
            ids.update(event_ids_in_entry(entry))
    return ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, help="Number of IDs to allocate.")
    parser.add_argument(
        "--nodes",
        nargs="+",
        help="Optional node keys; prints a ready-to-paste event_ids YAML block.",
    )
    parser.add_argument("--start", type=int, default=1000, help="Inclusive allocation range start.")
    parser.add_argument("--end", type=int, default=4999, help="Inclusive allocation range end.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    if args.count is None and not args.nodes:
        parser.error("provide --count or --nodes")
    count = len(args.nodes) if args.nodes else int(args.count)
    if args.nodes and args.count is not None and args.count != len(args.nodes):
        parser.error("--count must match the number of --nodes when both are provided")

    occupied = collect_occupied_engineering_event_ids() | spec_event_ids()
    ids = allocate_event_ids(count, occupied, start=args.start, end=args.end)

    if args.json:
        rows = [{"id": event_id, "key": node} for event_id, node in zip(ids, args.nodes or [])]
        print(json.dumps({"event_ids": rows or ids}, ensure_ascii=False, indent=2))
        return

    if args.nodes:
        print("event_ids:")
        for event_id, node in zip(ids, args.nodes):
            print(f"- id: {event_id}")
            print(f"  key: {node}")
    else:
        for event_id in ids:
            print(event_id)


if __name__ == "__main__":
    main()
