#!/usr/bin/env python3
"""Regenerate all script-managed submod outputs before deployment."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

REPO_ROOT = Path(__file__).resolve().parents[1]
GENERATED_REGISTRY = REPO_ROOT / "data" / "generated_files.yaml"
SUBMOD_PREFIX = "submods/"


def normalize_relative_path(value: object) -> str:
    return str(value or "").replace("\\", "/").lstrip("./")


def load_registry() -> dict[str, Any]:
    try:
        data = yaml.safe_load(GENERATED_REGISTRY.read_text(encoding="utf-8-sig")) or {}
    except OSError as exc:
        print(f"[ERROR] Could not read {GENERATED_REGISTRY.relative_to(REPO_ROOT)}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not isinstance(data, dict):
        print(f"[ERROR] {GENERATED_REGISTRY.relative_to(REPO_ROOT)} must contain a YAML mapping.", file=sys.stderr)
        raise SystemExit(1)
    return data


def submod_generator_scripts(registry: dict[str, Any]) -> list[str]:
    scripts: list[str] = []
    seen: set[str] = set()
    entries = registry.get("generated", [])
    if not isinstance(entries, list):
        print(f"[ERROR] {GENERATED_REGISTRY.relative_to(REPO_ROOT)} generated entry must be a list.", file=sys.stderr)
        raise SystemExit(1)

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        output = normalize_relative_path(entry.get("output"))
        if not output.startswith(SUBMOD_PREFIX):
            continue
        script = normalize_relative_path(entry.get("script"))
        if not script:
            print(f"[ERROR] Generated submod output {output} has no script entry.", file=sys.stderr)
            raise SystemExit(1)
        if script not in seen:
            scripts.append(script)
            seen.add(script)

    return scripts


def run_generator(script: str) -> int:
    script_path = REPO_ROOT / script
    if not script_path.exists():
        print(f"[ERROR] Generator not found: {script}", file=sys.stderr)
        return 1

    print(f"=== Regenerating {script} ===", flush=True)
    completed = subprocess.run([sys.executable, str(script_path)], cwd=REPO_ROOT)
    if completed.returncode != 0:
        print(f"[ERROR] {script} failed with exit code {completed.returncode}.", file=sys.stderr)
    return completed.returncode


def main() -> int:
    scripts = submod_generator_scripts(load_registry())
    if not scripts:
        print("[OK] No generated submod outputs are registered.", flush=True)
        return 0

    print(f"[INFO] Regenerating {len(scripts)} submod generator(s).", flush=True)
    for script in scripts:
        result = run_generator(script)
        if result != 0:
            return result

    print("[OK] Regenerated all generated submod outputs.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
