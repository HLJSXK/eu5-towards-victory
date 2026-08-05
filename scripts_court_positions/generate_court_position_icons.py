#!/usr/bin/env python3
"""Launch the Court Positions icon batch through the shared DDS generator."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = REPO_ROOT / "scripts" / "generate_dds_icon.py"
TARGET = "court_position_icons"


def _forward_args(argv: list[str]) -> list[str]:
    forwarded: list[str] = []
    skip_next = False
    value_flags = {"--target", "--config"}
    standalone_flags = {"--no-local-config"}
    for arg in argv:
        if skip_next:
            skip_next = False
            continue
        if arg in standalone_flags:
            continue
        if arg in value_flags:
            skip_next = True
            continue
        if any(arg.startswith(f"{flag}=") for flag in value_flags | standalone_flags):
            continue
        forwarded.append(arg)
    return forwarded


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    command = [sys.executable, str(GENERATOR), "--target", TARGET, *_forward_args(args)]
    result = subprocess.run(command, cwd=REPO_ROOT)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
