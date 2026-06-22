#!/usr/bin/env python3
"""Generate conservative intermediate fragments from unique wonder ritual DSL specs."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.render import render_header  # noqa: E402
from wonder_unique_ritual_harness import (  # noqa: E402
    CODEGEN_ELIGIBLE_STATUSES,
    SUPPORTED_CODEGEN_TEMPLATES,
    codegen_support_errors,
    list_index,
    load_spec_data,
    templates_used_by_entry,
    validate_spec_payload,
)

SCRIPT_REL = "scripts/gen_unique_wonder_ritual_code.py"
DATA_REL = "data/unique_wonder_ritual_specs.yaml + data/wonder_localization.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "generated_fragments" / "unique_wonder_rituals"
INDEX_FILE_NAME = "unique_wonder_ritual_codegen_index.md"


class CodegenError(ValueError):
    """Raised when a spec asks codegen to do something outside the verified slice."""


def entry_key(entry: dict[str, Any]) -> str:
    return str((entry.get("identity") or {}).get("key", "<unknown>"))


def entry_status(entry: dict[str, Any]) -> str:
    return str((entry.get("identity") or {}).get("status", ""))


def target_path_for_entry(entry: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    return output_dir / f"{entry_key(entry)}_ritual_codegen.md"


def _event_rows_by_node(entry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in ((entry.get("localization") or {}).get("event_keys") or []):
        if not isinstance(row, dict):
            continue
        if row.get("node_key"):
            rows[str(row["node_key"])] = row
        elif row.get("event_id") is not None:
            rows[str(row["event_id"])] = row
    return rows


def _join(values: Any) -> str:
    if values is None:
        return ""
    if isinstance(values, list):
        return ", ".join(str(value) for value in values)
    return str(values)


def _md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |")
    return lines


def _collect_loc_refs(entry: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    node_graph = entry.get("node_graph") or {}
    for node in node_graph.get("nodes", []) or []:
        if isinstance(node, dict):
            refs.extend(str(ref) for ref in node.get("loc_refs", []) or [])
    for edge in node_graph.get("edges", []) or []:
        if isinstance(edge, dict) and edge.get("label_key"):
            refs.append(str(edge["label_key"]))
    for check in node_graph.get("checks", []) or []:
        if isinstance(check, dict) and check.get("tooltip_key"):
            refs.append(str(check["tooltip_key"]))
    for binding in ((entry.get("ui_model") or {}).get("bindings") or []):
        if isinstance(binding, dict):
            refs.extend(str(ref) for ref in binding.get("loc_refs", []) or [])
    for row in ((entry.get("localization") or {}).get("event_keys") or []):
        if not isinstance(row, dict):
            continue
        refs.extend(str(key) for key in [row.get("title_key"), row.get("desc_key")] if key)
        refs.extend(str(key) for key in row.get("option_keys", []) or [])
    return sorted(dict.fromkeys(refs))


def render_entry_fragment(entry: dict[str, Any]) -> str:
    errors = codegen_support_errors(entry)
    if errors:
        raise CodegenError("; ".join(errors))

    identity = entry.get("identity") or {}
    node_graph = entry.get("node_graph") or {}
    generation = entry.get("generation") or {}
    event_rows = _event_rows_by_node(entry)
    lines = render_header(SCRIPT_REL, DATA_REL)
    lines.extend(
        [
            f"# Unique Wonder Ritual Codegen Fragment: {entry_key(entry)}",
            "",
            "This is a Harness-owned intermediate fragment, not a directly loadable EU5 script file.",
            "It intentionally avoids unverified event, GUI, scripted_effect, and scripted_trigger syntax.",
            "",
            "## Identity",
            "",
            f"- Wonder id: {identity.get('id')}",
            f"- Status: {entry_status(entry)}",
            f"- Runtime prefix: {identity.get('runtime_prefix')}",
            f"- Generation status: {generation.get('status')}",
            f"- Verified templates: {_join(generation.get('verified_templates'))}",
            f"- Target files declared by spec: {_join(generation.get('target_files'))}",
            "",
            "## Event Skeleton",
            "",
        ]
    )
    event_rows_table: list[list[Any]] = []
    for node in node_graph.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        loc_row = event_rows.get(str(node.get("key"))) or event_rows.get(str(node.get("event_id"))) or {}
        event_rows_table.append(
            [
                node.get("key", ""),
                node.get("kind", ""),
                f"tv_engineering_department.{node.get('event_id')}",
                loc_row.get("title_key", ""),
                loc_row.get("desc_key", ""),
                _join(loc_row.get("option_keys")),
                _join(node.get("next_nodes")),
                node.get("retry_target") or "",
            ]
        )
    lines.extend(
        _md_table(
            ["node", "kind", "event_id", "title_key", "desc_key", "options", "next", "retry"],
            event_rows_table,
        )
    )
    lines.extend(["", "## Scripted Effect Stubs", ""])
    action_rows: list[list[Any]] = []
    for action in node_graph.get("actions", []) or []:
        if not isinstance(action, dict):
            continue
        action_rows.append(
            [
                action.get("key", ""),
                action.get("kind", ""),
                action.get("scope", ""),
                action.get("verified_interface", ""),
                action.get("generator_template") or ("effect_script" if action.get("effect_script") else ""),
            ]
        )
    lines.extend(_md_table(["action", "kind", "scope", "verified_interface", "source"], action_rows))
    lines.extend(["", "## Scripted Trigger Stubs", ""])
    check_rows: list[list[Any]] = []
    for check in node_graph.get("checks", []) or []:
        if not isinstance(check, dict):
            continue
        check_rows.append(
            [
                check.get("key", ""),
                check.get("kind", ""),
                check.get("tooltip_key", ""),
                check.get("generator_template") or ("trigger_script" if check.get("trigger_script") else ""),
            ]
        )
    lines.extend(_md_table(["check", "kind", "tooltip_key", "source"], check_rows))
    lines.extend(["", "## Variable Table", ""])
    variable_rows: list[list[Any]] = []
    for variable in node_graph.get("variables", []) or []:
        if not isinstance(variable, dict):
            continue
        variable_rows.append(
            [
                variable.get("name", ""),
                variable.get("scope", ""),
                variable.get("type", ""),
                variable.get("initial_value", ""),
                _join(variable.get("writer_nodes")),
                _join(variable.get("reader_nodes")),
                variable.get("cleanup", ""),
            ]
        )
    lines.extend(_md_table(["name", "scope", "type", "initial", "writers", "readers", "cleanup"], variable_rows))
    lines.extend(["", "## UI Binding Summary", ""])
    binding_rows: list[list[Any]] = []
    for binding in ((entry.get("ui_model") or {}).get("bindings") or []):
        if not isinstance(binding, dict):
            continue
        binding_rows.append(
            [
                binding.get("key", ""),
                binding.get("component_key", ""),
                _join(binding.get("variable_refs")),
                _join(binding.get("node_refs")),
                _join(binding.get("loc_refs")),
            ]
        )
    lines.extend(_md_table(["binding", "component", "variables", "nodes", "loc_refs"], binding_rows))
    lines.extend(["", "## Localization Draft Inventory", ""])
    for loc_key in _collect_loc_refs(entry):
        lines.append(f"- `{loc_key}`")
    lines.extend(
        [
            "",
            "## Reward Dispatch Stub",
            "",
            "```text",
            f"# {identity.get('runtime_prefix')}_dispatch_final_reward_stub_effect",
            "# Template: final_reward_dispatch_stub",
            "# Keep this as a stub until the exact EU5 effect integration point is verified.",
            "# Intended final handoff: call the existing active-ritual completion/finalization path.",
            "```",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _selected_entries(payload: dict[str, Any], wonder_keys: set[str] | None) -> tuple[list[dict[str, Any]], list[str]]:
    entries = payload.get("unique_wonders", []) or []
    index = list_index(payload)
    selected: list[dict[str, Any]] = []
    skipped: list[str] = []
    if wonder_keys:
        missing = sorted(wonder_keys - set(index))
        if missing:
            raise CodegenError("Unknown ritual spec(s): " + ", ".join(missing))
        for key in sorted(wonder_keys):
            entry = index[key]
            if entry_status(entry) not in CODEGEN_ELIGIBLE_STATUSES:
                raise CodegenError(f"{key}: status {entry_status(entry)!r} cannot be generated by Harness codegen")
            selected.append(entry)
        return selected, skipped

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry_status(entry) in CODEGEN_ELIGIBLE_STATUSES:
            selected.append(entry)
        else:
            skipped.append(entry_key(entry))
    return selected, skipped


def render_index(generated: list[dict[str, Any]], skipped: list[str]) -> str:
    lines = render_header(SCRIPT_REL, DATA_REL)
    lines.extend(
        [
            "# Unique Wonder Ritual Codegen Index",
            "",
            "This file records the current Harness codegen dry-run/write surface.",
            "",
            f"- Generated fragments: {len(generated)}",
            f"- Skipped non-codegen specs: {len(skipped)}",
            f"- Supported templates: {', '.join(sorted(SUPPORTED_CODEGEN_TEMPLATES))}",
            "",
        ]
    )
    if generated:
        lines.append("## Generated")
        lines.append("")
        for row in generated:
            lines.append(f"- `{row['key']}` -> `{row['path']}`")
        lines.append("")
    else:
        lines.append("No eligible `implementation_ready` or `harness_generated` specs were selected.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_fragments_for_payload(
    payload: dict[str, Any],
    *,
    wonder_keys: set[str] | None = None,
    write: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    selected, skipped = _selected_entries(payload, wonder_keys)
    generated: list[dict[str, Any]] = []
    for entry in selected:
        text = render_entry_fragment(entry)
        path = target_path_for_entry(entry, output_dir)
        rel_path = path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()
        generated.append({"key": entry_key(entry), "path": rel_path, "text": text})
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    index_path = output_dir / INDEX_FILE_NAME
    index_text = render_index(generated, skipped)
    if write:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(index_text, encoding="utf-8")
    return {
        "generated": generated,
        "skipped": skipped,
        "index_path": index_path.relative_to(REPO_ROOT).as_posix(),
        "index_text": index_text,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write generated intermediate fragments.")
    parser.add_argument("--wonder", action="append", help="Specific unique wonder key to generate.")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    args = parser.parse_args()

    payload = load_spec_data()
    errors = validate_spec_payload(payload)
    if errors:
        print("[FAIL] Unique wonder ritual specs failed validation:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    try:
        result = generate_fragments_for_payload(
            payload,
            wonder_keys=set(args.wonder) if args.wonder else None,
            write=args.write,
        )
    except CodegenError as exc:
        print(f"[FAIL] {exc}")
        sys.exit(1)

    if args.json:
        summary = {
            "write": args.write,
            "generated": [{key: row[key] for key in ("key", "path")} for row in result["generated"]],
            "skipped_count": len(result["skipped"]),
            "index_path": result["index_path"],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    mode = "Wrote" if args.write else "Dry-run"
    print(f"{mode} {len(result['generated'])} unique ritual fragment(s).")
    print(f"Index: {result['index_path']}")
    if not args.write:
        print("No files were written. Re-run with --write to update generated fragments.")
    for row in result["generated"]:
        print(f"  - {row['key']}: {row['path']}")


if __name__ == "__main__":
    main()
