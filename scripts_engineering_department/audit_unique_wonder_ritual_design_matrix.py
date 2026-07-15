#!/usr/bin/env python3
"""Audit the full-corpus Unique Wonder Ritual design matrix."""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

from wonder_mechanics.io import load_yaml  # noqa: E402
from wonder_unique_ritual_harness import (  # noqa: E402
    SUPPORTED_CADENCE_TYPES,
    SUPPORTED_LISTENERS,
    SUPPORTED_UI_COMPONENTS,
    supported_capability_keys,
)

MATRIX_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_design_matrix.yaml"
UNIQUE_WONDERS_FILE = REPO_ROOT / "data" / "unique_wonders.yaml"
PROMPT_LIBRARY_FILE = REPO_ROOT / "docs" / "guides" / "Unique_Wonder_Ritual_Design_Prompt_Library.md"

ALLOWED_IMPLEMENTATION_FEASIBILITY = {
    "current_harness_ready",
    "needs_trigger_check_only",
    "needs_new_capability",
    "needs_new_listener",
    "needs_eu5_verification",
    "blocked",
}
FUTURE_GAP_FEASIBILITIES = {
    "needs_new_capability",
    "needs_new_listener",
    "needs_eu5_verification",
    "blocked",
}
ALLOWED_AUTHORING_STATUSES = {"unassigned", "drafted", "reviewed", "frozen"}
REQUIRED_ENTRY_FIELDS = {
    "wonder_id",
    "wonder_key",
    "wonder_name",
    "base_wonder_type",
    "category",
    "location",
    "culture",
    "religion",
    "region",
    "historical_design_hook",
    "primary_cadence_type",
    "secondary_cadence_type",
    "cadence_rationale",
    "mechanic_prompt_atoms",
    "proposed_core_mechanic",
    "player_agency_model",
    "expected_ui_model",
    "expected_capabilities",
    "expected_listeners",
    "non_monthly_validation_point",
    "risk_or_failure_branch",
    "implementation_feasibility",
    "uniqueness_notes",
    "similarity_group",
    "authoring_status",
}
LIST_FIELDS = {
    "mechanic_prompt_atoms",
    "expected_ui_model",
    "expected_capabilities",
    "expected_listeners",
}
CADENCE_FIELDS = ("primary_cadence_type", "secondary_cadence_type")


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if isinstance(value, list) and not [item for item in value if not _is_blank(item)]:
        return True
    return False


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return re.sub(r"_+", "_", slug)


def _atom_aliases() -> dict[str, str]:
    aliases: dict[str, str] = {}
    pattern = re.compile(r"^### Atom (\d{2}) - (.+)$")
    text = PROMPT_LIBRARY_FILE.read_text(encoding="utf-8")
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        number, title = match.groups()
        canonical = f"atom_{number}"
        title_slug = _slug(title)
        for alias in {
            number,
            str(int(number)),
            f"atom_{number}",
            f"atom {number}",
            f"atom-{number}",
            title_slug,
            f"{number}_{title_slug}",
            f"atom_{number}_{title_slug}",
        }:
            aliases[_slug(alias)] = canonical
    return aliases


def _normalize_atom(raw: str, aliases: dict[str, str]) -> str | None:
    value = raw.strip()
    match = re.match(r"(?i)^atom[\s_-]*(\d{1,2})(?:\s*-\s*.+)?$", value)
    if match:
        key = f"atom_{int(match.group(1)):02d}"
        return key if _slug(key) in aliases else None
    if re.match(r"^\d{1,2}$", value):
        key = f"atom_{int(value):02d}"
        return key if _slug(key) in aliases else None
    return aliases.get(_slug(value))


def _entry_label(entry: dict[str, Any]) -> str:
    return f"{entry.get('wonder_key', '<missing-key>')} ({entry.get('wonder_id', '<missing-id>')})"


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _limited(values: list[str], limit: int = 20) -> list[str]:
    if len(values) <= limit:
        return values
    return values[:limit] + [f"... +{len(values) - limit} more"]


def _validate_list_field(
    *,
    field: str,
    value: Any,
    label: str,
    supported: set[str] | None,
    errors: list[str],
) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, (list, str)):
        errors.append(f"{label}: {field} must be a list, string, or null")
        return []
    values = _as_list(value)
    if supported is not None:
        unsupported = sorted({item for item in values if item not in supported})
        if unsupported:
            errors.append(f"{label}: {field} has unsupported value(s): {', '.join(unsupported)}")
    return values


def audit_matrix(matrix_path: Path = MATRIX_FILE, repeat_threshold: int = 3) -> dict[str, Any]:
    payload = load_yaml(matrix_path)
    source = load_yaml(UNIQUE_WONDERS_FILE)
    source_entries = source.get("unique_wonders", [])
    expected_by_id = {int(entry["id"]): entry for entry in source_entries if isinstance(entry, dict) and entry.get("id")}
    expected_ids = set(expected_by_id)
    aliases = _atom_aliases()
    capability_keys = supported_capability_keys()

    errors: list[str] = []
    warnings: list[str] = []
    entries = payload.get("unique_wonders")
    if not isinstance(entries, list):
        return {
            "matrix": _display_path(matrix_path),
            "source_unique_wonders": len(expected_ids),
            "matrix_entries": 0,
            "covered_unique_wonders": 0,
            "coverage_complete": False,
            "errors": ["unique_wonders must be a list"],
            "warnings": [],
            "distributions": {},
        }

    seen_ids: Counter[int] = Counter()
    source_key_mismatches: list[str] = []
    missing_required_fields: list[str] = []
    cadence_primary: Counter[str] = Counter()
    cadence_secondary: Counter[str] = Counter()
    cadence_any: Counter[str] = Counter()
    atom_usage: Counter[str] = Counter()
    ui_usage: Counter[str] = Counter()
    capability_usage: Counter[str] = Counter()
    listener_usage: Counter[str] = Counter()
    similarity_usage: Counter[str] = Counter()
    feasibility_usage: Counter[str] = Counter()
    status_usage: Counter[str] = Counter()
    duplicate_groups: dict[tuple[str, tuple[str, ...], tuple[str, ...]], list[str]] = defaultdict(list)
    monthly_entries: list[str] = []
    monthly_missing_rationale: list[str] = []
    missing_validation: list[str] = []
    missing_uniqueness: list[str] = []
    future_gap_entries: list[dict[str, str]] = []

    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            errors.append(f"entry #{index} must be a mapping")
            continue
        label = _entry_label(entry)
        missing = sorted(REQUIRED_ENTRY_FIELDS - set(entry))
        if missing:
            missing_required_fields.append(f"{label}: {', '.join(missing)}")
            errors.append(f"{label}: missing required field(s): {', '.join(missing)}")

        raw_id = entry.get("wonder_id")
        try:
            wonder_id = int(raw_id)
        except (TypeError, ValueError):
            errors.append(f"{label}: wonder_id must be an integer")
            wonder_id = None
        if wonder_id is not None:
            seen_ids[wonder_id] += 1
            expected = expected_by_id.get(wonder_id)
            if expected and entry.get("wonder_key") and entry.get("wonder_key") != expected.get("key"):
                source_key_mismatches.append(
                    f"{label}: wonder_key should be {expected.get('key')} for source id {wonder_id}"
                )
                errors.append(source_key_mismatches[-1])

        for cadence_field, counter in (
            ("primary_cadence_type", cadence_primary),
            ("secondary_cadence_type", cadence_secondary),
        ):
            value = entry.get(cadence_field)
            if not _is_blank(value):
                cadence = str(value).strip()
                if cadence not in SUPPORTED_CADENCE_TYPES:
                    errors.append(f"{label}: {cadence_field} has unsupported value {cadence!r}")
                counter[cadence] += 1
                cadence_any[cadence] += 1

        status = entry.get("authoring_status")
        if _is_blank(status):
            errors.append(f"{label}: authoring_status must not be blank")
        else:
            status = str(status).strip()
            status_usage[status] += 1
            if status not in ALLOWED_AUTHORING_STATUSES:
                errors.append(f"{label}: authoring_status has unsupported value {status!r}")

        feasibility = entry.get("implementation_feasibility")
        if _is_blank(feasibility):
            if status != "unassigned":
                errors.append(f"{label}: implementation_feasibility may be null only when authoring_status is unassigned")
        else:
            feasibility = str(feasibility).strip()
            feasibility_usage[feasibility] += 1
            if feasibility not in ALLOWED_IMPLEMENTATION_FEASIBILITY:
                errors.append(f"{label}: implementation_feasibility has unsupported value {feasibility!r}")
            elif feasibility in FUTURE_GAP_FEASIBILITIES:
                future_gap_entries.append({"entry": label, "implementation_feasibility": feasibility})

        canonical_atoms: list[str] = []
        atom_values = _validate_list_field(
            field="mechanic_prompt_atoms",
            value=entry.get("mechanic_prompt_atoms"),
            label=label,
            supported=None,
            errors=errors,
        )
        for atom in atom_values:
            canonical = _normalize_atom(atom, aliases)
            if canonical is None:
                errors.append(f"{label}: mechanic_prompt_atoms references unknown atom {atom!r}")
                continue
            canonical_atoms.append(canonical)
            atom_usage[canonical] += 1

        ui_values = _validate_list_field(
            field="expected_ui_model",
            value=entry.get("expected_ui_model"),
            label=label,
            supported=SUPPORTED_UI_COMPONENTS,
            errors=errors,
        )
        capability_values = _validate_list_field(
            field="expected_capabilities",
            value=entry.get("expected_capabilities"),
            label=label,
            supported=capability_keys,
            errors=errors,
        )
        listener_values = _validate_list_field(
            field="expected_listeners",
            value=entry.get("expected_listeners"),
            label=label,
            supported=SUPPORTED_LISTENERS,
            errors=errors,
        )
        for value in ui_values:
            ui_usage[value] += 1
        for value in capability_values:
            capability_usage[value] += 1
        for value in listener_values:
            listener_usage[value] += 1

        if not _is_blank(entry.get("similarity_group")):
            similarity_usage[str(entry["similarity_group"]).strip()] += 1

        primary = str(entry.get("primary_cadence_type") or "").strip()
        secondary = str(entry.get("secondary_cadence_type") or "").strip()
        if "monthly_institutionalization" in {primary, secondary}:
            monthly_entries.append(label)
            if _is_blank(entry.get("cadence_rationale")) or _is_blank(entry.get("non_monthly_validation_point")):
                monthly_missing_rationale.append(label)

        if _is_blank(entry.get("non_monthly_validation_point")):
            missing_validation.append(label)
        if _is_blank(entry.get("uniqueness_notes")):
            missing_uniqueness.append(label)

        if primary and canonical_atoms and ui_values:
            duplicate_groups[(primary, tuple(sorted(set(canonical_atoms))), tuple(sorted(set(ui_values))))].append(label)

    matrix_ids = set(seen_ids)
    duplicate_ids = sorted(wonder_id for wonder_id, count in seen_ids.items() if count > 1)
    missing_ids = sorted(expected_ids - matrix_ids)
    unknown_ids = sorted(matrix_ids - expected_ids)
    if missing_ids:
        errors.append(f"missing unique wonder ids: {', '.join(str(item) for item in missing_ids)}")
    if unknown_ids:
        errors.append(f"unknown wonder ids: {', '.join(str(item) for item in unknown_ids)}")
    if duplicate_ids:
        errors.append(f"duplicate wonder ids: {', '.join(str(item) for item in duplicate_ids)}")

    repeated_groups = []
    for (cadence, atoms, ui_values), labels in sorted(duplicate_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(labels) > repeat_threshold:
            repeated_groups.append(
                {
                    "primary_cadence_type": cadence,
                    "mechanic_prompt_atoms": list(atoms),
                    "expected_ui_model": list(ui_values),
                    "count": len(labels),
                    "entries": labels,
                }
            )
    if repeated_groups:
        warnings.append(
            f"high-risk repeated cadence/atom/UI groups over threshold {repeat_threshold}: {len(repeated_groups)}"
        )
    if monthly_missing_rationale:
        warnings.append(
            f"monthly_institutionalization entries missing cadence_rationale or non_monthly_validation_point: {len(monthly_missing_rationale)}"
        )
    if missing_validation:
        warnings.append(f"entries missing non_monthly_validation_point: {len(missing_validation)}")
    if missing_uniqueness:
        warnings.append(f"entries missing uniqueness_notes: {len(missing_uniqueness)}")
    if future_gap_entries:
        warnings.append(f"entries marked as future Harness/EU5 gaps: {len(future_gap_entries)}")

    return {
        "matrix": _display_path(matrix_path),
        "source_unique_wonders": len(expected_ids),
        "matrix_entries": len(entries),
        "covered_unique_wonders": len(matrix_ids & expected_ids),
        "coverage_complete": not missing_ids and not unknown_ids and not duplicate_ids,
        "missing_wonder_ids": missing_ids,
        "unknown_wonder_ids": unknown_ids,
        "duplicate_wonder_ids": duplicate_ids,
        "missing_required_fields": missing_required_fields,
        "source_key_mismatches": source_key_mismatches,
        "errors": errors,
        "warnings": warnings,
        "monthly_institutionalization_count": len(monthly_entries),
        "monthly_missing_rationale_entries": monthly_missing_rationale,
        "missing_non_monthly_validation_point_entries": missing_validation,
        "missing_uniqueness_notes_entries": missing_uniqueness,
        "future_gap_entries": future_gap_entries,
        "repeated_groups": repeated_groups,
        "supported": {
            "cadence_types": sorted(SUPPORTED_CADENCE_TYPES),
            "listeners": sorted(SUPPORTED_LISTENERS),
            "ui_components": sorted(SUPPORTED_UI_COMPONENTS),
            "capabilities": sorted(capability_keys),
            "prompt_atoms": sorted(set(aliases.values())),
            "implementation_feasibility": sorted(ALLOWED_IMPLEMENTATION_FEASIBILITY),
            "authoring_status": sorted(ALLOWED_AUTHORING_STATUSES),
        },
        "distributions": {
            "primary_cadence_type": _counter_dict(cadence_primary),
            "secondary_cadence_type": _counter_dict(cadence_secondary),
            "any_cadence_type": _counter_dict(cadence_any),
            "mechanic_prompt_atoms": _counter_dict(atom_usage),
            "expected_ui_model": _counter_dict(ui_usage),
            "expected_capabilities": _counter_dict(capability_usage),
            "expected_listeners": _counter_dict(listener_usage),
            "similarity_group": _counter_dict(similarity_usage),
            "implementation_feasibility": _counter_dict(feasibility_usage),
            "authoring_status": _counter_dict(status_usage),
        },
    }


def _print_counter(label: str, values: dict[str, int], *, limit: int = 20) -> None:
    print(f"{label}: {sum(values.values())}")
    if not values:
        print("  (none)")
        return
    for key, count in list(values.items())[:limit]:
        print(f"  {key}: {count}")
    if len(values) > limit:
        print(f"  ... +{len(values) - limit} more")


def _print_list(label: str, values: list[str], *, limit: int = 20) -> None:
    print(f"{label}: {len(values)}")
    for value in _limited(values, limit):
        print(f"  - {value}")


def print_human(summary: dict[str, Any]) -> None:
    print("# Unique Wonder Ritual Design Matrix Audit")
    print(f"Matrix: {summary['matrix']}")
    print(f"Unique wonders in source: {summary['source_unique_wonders']}")
    print(f"Matrix entries: {summary['matrix_entries']}")
    print(f"Covered unique wonders: {summary['covered_unique_wonders']}/{summary['source_unique_wonders']}")
    print(f"Coverage complete: {summary['coverage_complete']}")
    print(f"Structural errors: {len(summary['errors'])}")
    print(f"Warnings: {len(summary['warnings'])}")
    print("")

    if summary["warnings"]:
        print("## WARNING Summary")
        for warning in summary["warnings"]:
            print(f"WARNING: {warning}")
        print("")

    distributions = summary["distributions"]
    print("## Distributions")
    _print_counter("Primary cadence", distributions["primary_cadence_type"])
    _print_counter("Secondary cadence", distributions["secondary_cadence_type"])
    _print_counter("Any cadence", distributions["any_cadence_type"])
    _print_counter("Prompt atoms", distributions["mechanic_prompt_atoms"])
    _print_counter("Expected UI model", distributions["expected_ui_model"])
    _print_counter("Expected capabilities", distributions["expected_capabilities"])
    _print_counter("Expected listeners", distributions["expected_listeners"])
    _print_counter("Similarity groups", distributions["similarity_group"])
    _print_counter("Implementation feasibility", distributions["implementation_feasibility"])
    _print_counter("Authoring status", distributions["authoring_status"])
    print("")

    _print_list("Missing non-monthly validation point", summary["missing_non_monthly_validation_point_entries"])
    _print_list("Missing uniqueness notes", summary["missing_uniqueness_notes_entries"])
    _print_list(
        "Monthly entries missing rationale/validation",
        summary["monthly_missing_rationale_entries"],
    )
    _print_list(
        "Future Harness/EU5 gap entries",
        [f"{item['entry']}: {item['implementation_feasibility']}" for item in summary["future_gap_entries"]],
    )
    if summary["repeated_groups"]:
        print(f"High-risk repeated cadence/atom/UI groups: {len(summary['repeated_groups'])}")
        for group in summary["repeated_groups"][:20]:
            print(
                "  - "
                f"{group['primary_cadence_type']} + {','.join(group['mechanic_prompt_atoms'])} "
                f"+ {','.join(group['expected_ui_model'])}: {group['count']}"
            )
        if len(summary["repeated_groups"]) > 20:
            print(f"  ... +{len(summary['repeated_groups']) - 20} more")
    else:
        print("High-risk repeated cadence/atom/UI groups: 0")
    print("")

    if summary["errors"]:
        print("## Structural Errors")
        for error in _limited(summary["errors"], 60):
            print(f"ERROR: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        default=MATRIX_FILE,
        help="Path to the design matrix YAML file.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--repeat-threshold",
        type=int,
        default=3,
        help="Warn when a non-empty cadence + atom combo + UI group appears more than this many times.",
    )
    args = parser.parse_args()

    summary = audit_matrix(args.matrix, args.repeat_threshold)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human(summary)

    if summary["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
