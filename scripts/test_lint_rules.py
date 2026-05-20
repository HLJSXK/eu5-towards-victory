#!/usr/bin/env python3
"""
Run fixture tests for anti-pattern lint regexes.

Fixtures live under:
  tests/fixtures/anti_patterns/<rule_id>/bad.*
  tests/fixtures/anti_patterns/<rule_id>/good.*
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("[ERROR] PyYAML not installed. Run: pip install pyyaml")
    raise SystemExit(1)

REPO_ROOT = Path(__file__).parent.parent
ANTI_PATTERNS = REPO_ROOT / "docs" / "knowledge" / "anti_patterns.yaml"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "anti_patterns"


def load_rules() -> dict[str, dict]:
    with ANTI_PATTERNS.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    return {entry["id"]: entry for entry in data if entry.get("id")}


def is_lint_rule(entry: dict) -> bool:
    detectability = entry.get("detectability")
    if detectability is None:
        detectability = "lint" if entry.get("pattern") else "advisory"
    return detectability == "lint"


def fixture_files(rule_dir: Path, prefix: str) -> list[Path]:
    return sorted(p for p in rule_dir.iterdir() if p.is_file() and p.name.startswith(prefix))


def main() -> None:
    rules = load_rules()
    if not FIXTURE_ROOT.exists():
        print("[OK] No anti-pattern fixtures found.")
        return

    failures: list[str] = []
    tested = 0
    for rule_dir in sorted(p for p in FIXTURE_ROOT.iterdir() if p.is_dir()):
        rule_id = rule_dir.name
        entry = rules.get(rule_id)
        if not entry:
            failures.append(f"{rule_id}: no matching rule in anti_patterns.yaml")
            continue
        if not is_lint_rule(entry):
            failures.append(f"{rule_id}: fixtures exist but rule is not detectability: lint")
            continue
        pattern = entry.get("pattern") or ""
        try:
            regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
        except re.error as exc:
            failures.append(f"{rule_id}: invalid regex: {exc}")
            continue

        bad_files = fixture_files(rule_dir, "bad")
        good_files = fixture_files(rule_dir, "good")
        if not bad_files:
            failures.append(f"{rule_id}: missing bad.* fixture")
        if not good_files:
            failures.append(f"{rule_id}: missing good.* fixture")

        for fixture in bad_files:
            text = fixture.read_text(encoding="utf-8-sig")
            if not regex.search(text):
                failures.append(f"{rule_id}/{fixture.name}: expected a match")
            tested += 1
        for fixture in good_files:
            text = fixture.read_text(encoding="utf-8-sig")
            if regex.search(text):
                failures.append(f"{rule_id}/{fixture.name}: expected no match")
            tested += 1

    if failures:
        print(f"[FAIL] {len(failures)} lint fixture failure(s):")
        for failure in failures:
            print(f"  {failure}")
        raise SystemExit(1)

    print(f"[OK] Tested {tested} anti-pattern fixture file(s).")


if __name__ == "__main__":
    main()
