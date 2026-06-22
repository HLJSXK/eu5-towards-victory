#!/usr/bin/env python3
"""Report unique wonder ritual Harness coverage, debt, and event-id health."""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_unique_ritual_harness import audit_summary  # noqa: E402


def _print_list(label: str, values: list[str], *, limit: int = 20) -> None:
    print(f"{label}: {len(values)}")
    if not values:
        return
    shown = values[:limit]
    print("  " + ", ".join(shown))
    if len(values) > limit:
        print(f"  ... +{len(values) - limit} more")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--fail-on-spec-errors",
        action="store_true",
        help="Exit non-zero when the structured spec quality gates fail.",
    )
    parser.add_argument(
        "--fail-on-coverage-debt",
        action="store_true",
        help="Exit non-zero when design/spec/localization coverage is missing.",
    )
    parser.add_argument(
        "--fail-on-authoring-debt",
        action="store_true",
        help="Exit non-zero when placeholder designs or missing AI prompt entries remain.",
    )
    args = parser.parse_args()

    summary = audit_summary()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("# Unique Wonder Ritual Harness Audit")
        print(f"Unique wonders: {summary['unique_wonders']}")
        print(f"Design entries: {summary['designs']}")
        print(f"Prompt entries: {summary['prompts']}")
        print(f"Spec entries: {summary['specs']}")
        print(f"Implemented/parity specs: {summary['implemented_specs']}")
        print(f"Stub specs: {summary['stub_specs']}")
        print(f"Occupied Engineering Department event IDs: {summary['occupied_engineering_event_ids']}")
        print("")
        _print_list("Missing design entries", summary["missing_designs"])
        _print_list("Placeholder design entries", summary["placeholder_designs"])
        _print_list("Missing prompt entries", summary["missing_prompts"])
        _print_list("Missing spec entries", summary["missing_specs"])
        _print_list("Missing finalization/world-news loc rows", summary["missing_finalization_or_world_news_loc"])
        _print_list("Spec quality errors", summary["spec_errors"])

    has_coverage_debt = any(
        summary[key]
        for key in (
            "missing_designs",
            "missing_specs",
            "missing_finalization_or_world_news_loc",
        )
    )
    if (args.fail_on_spec_errors and summary["spec_errors"]) or (
        args.fail_on_coverage_debt and has_coverage_debt
    ) or (
        args.fail_on_authoring_debt
        and (summary["placeholder_designs"] or summary["missing_prompts"])
    ):
        sys.exit(1)


if __name__ == "__main__":
    main()
