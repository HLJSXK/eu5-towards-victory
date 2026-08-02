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
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import validate  # noqa: E402


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


def has_fixture_files(rule_dir: Path) -> bool:
    return any(p.is_file() for p in rule_dir.iterdir())


VALIDATOR_BY_RULE = {
    "effect_localization_positive_negative_share_loc_key": validate.check_effect_loc_positive_negative_pairs,
    "parentanchor_under_hbox_vbox": validate.check_gui_parentanchor_under_hbox_vbox,
    "construct_building_cost_multiplier_needs_reason": validate.check_construct_building_cost_multiplier_reason,
    "marked_local_variable_cleanup_missing": validate.check_marked_local_variable_cleanup,
}


def validator_matches(entry: dict, fixture: Path) -> bool:
    validator_name = entry.get("validator")
    validator = VALIDATOR_BY_RULE.get(fixture.parent.name)
    if validator is None:
        raise ValueError(f"validator {validator_name} is not registered in test_lint_rules.py")

    before_issues = len(validate.issues)
    before_warnings = len(validate.warnings)
    try:
        validator(fixture, fixture.read_text(encoding="utf-8-sig"))
        return len(validate.issues) > before_issues or len(validate.warnings) > before_warnings
    finally:
        del validate.issues[before_issues:]
        del validate.warnings[before_warnings:]


def main() -> None:
    rules = load_rules()
    if not FIXTURE_ROOT.exists():
        print("[OK] No anti-pattern fixtures found.")
        return

    failures: list[str] = []
    tested = 0
    for rule_dir in sorted(p for p in FIXTURE_ROOT.iterdir() if p.is_dir()):
        if not has_fixture_files(rule_dir):
            continue
        rule_id = rule_dir.name
        entry = rules.get(rule_id)
        if not entry:
            failures.append(f"{rule_id}: no matching rule in anti_patterns.yaml")
            continue
        if not is_lint_rule(entry):
            failures.append(f"{rule_id}: fixtures exist but rule is not detectability: lint")
            continue
        pattern = entry.get("pattern") or ""
        validator_name = entry.get("validator")
        regex = None
        if pattern:
            try:
                regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
            except re.error as exc:
                failures.append(f"{rule_id}: invalid regex: {exc}")
                continue
        elif validator_name:
            if rule_id not in VALIDATOR_BY_RULE:
                failures.append(f"{rule_id}: validator {validator_name} is not registered in test_lint_rules.py")
                continue
        else:
            failures.append(f"{rule_id}: lint rule has neither pattern nor registered validator")
            continue

        bad_files = fixture_files(rule_dir, "bad")
        good_files = fixture_files(rule_dir, "good")
        if not bad_files:
            failures.append(f"{rule_id}: missing bad.* fixture")
        if not good_files:
            failures.append(f"{rule_id}: missing good.* fixture")

        for fixture in bad_files:
            text = fixture.read_text(encoding="utf-8-sig")
            matched = bool(regex.search(text)) if regex is not None else validator_matches(entry, fixture)
            if not matched:
                failures.append(f"{rule_id}/{fixture.name}: expected a match")
            tested += 1
        for fixture in good_files:
            text = fixture.read_text(encoding="utf-8-sig")
            matched = bool(regex.search(text)) if regex is not None else validator_matches(entry, fixture)
            if matched:
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
