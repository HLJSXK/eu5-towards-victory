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
        print(f"Implemented parity count: {summary['implemented_parity_count']}")
        print(f"Design-complete count: {summary['design_complete_count']}")
        print(f"Compiler-mapped count: {summary['compiler_mapped_count']}")
        print(f"Evidence-verified count: {summary['evidence_verified_count']}")
        print(f"Source-codegen-ready count: {summary['source_codegen_ready_count']}")
        print(f"Implementation-ready count: {summary['implementation_ready_count']}")
        print(f"Harness-generated count: {summary['harness_generated_count']}")
        print(f"Stub specs: {summary['stub_specs']}")
        print(f"Codegen-supported count: {summary['codegen_supported_count']}")
        print(f"Codegen-blocked count: {summary['codegen_blocked_count']}")
        print(f"Codegen tier summary: {summary['codegen_tier_summary']}")
        print(f"Capability coverage summary: {summary['capability_coverage_summary']}")
        print(f"Archetype coverage summary: {summary['archetype_coverage_summary']}")
        print(f"Node kind summary: {summary['node_kind_summary']}")
        print(f"Graph reachable nodes: {summary['graph_reachable_count']}")
        print(f"Graph unreachable nodes: {summary['graph_unreachable_count']}")
        print(f"Lifecycle error count: {summary['lifecycle_error_count']}")
        print(f"Archetype contract error count: {summary['archetype_contract_error_count']}")
        print(f"Listener contract error count: {summary['listener_contract_error_count']}")
        print(f"Scope contract error count: {summary['scope_contract_error_count']}")
        print(f"Occupied Engineering Department event IDs: {summary['occupied_engineering_event_ids']}")
        print("")
        _print_list("Missing design entries", summary["missing_designs"])
        _print_list("Placeholder design entries", summary["placeholder_designs"])
        _print_list("Missing prompt entries", summary["missing_prompts"])
        _print_list("Missing spec entries", summary["missing_specs"])
        _print_list("Missing finalization/world-news loc rows", summary["missing_finalization_or_world_news_loc"])
        _print_list("Unsupported codegen templates", summary["unsupported_templates"])
        _print_list("Anti-flattening warnings", summary["anti_flattening_warnings"])
        _print_list("Template registry errors", summary["template_registry_errors"])
        _print_list("Capability registry errors", summary["capability_registry_errors"])
        _print_list("Archetype registry errors", summary["archetype_registry_errors"])
        _print_list("Graph validation errors", summary["graph_validation_errors"])
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
