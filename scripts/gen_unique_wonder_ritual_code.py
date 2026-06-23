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
    archetype_registry_index,
    capability_registry_index,
    codegen_support_errors,
    list_index,
    load_archetype_registry,
    load_capability_registry,
    load_template_registry,
    load_spec_data,
    supported_archetype_keys,
    supported_capability_keys,
    supported_codegen_template_keys,
    template_registry_index,
    validate_spec_payload,
)

SCRIPT_REL = "scripts/gen_unique_wonder_ritual_code.py"
DATA_REL = "data/unique_wonder_ritual_specs.yaml + data/wonder_localization.yaml + data/unique_wonder_ritual_codegen_templates.yaml + data/unique_wonder_ritual_capabilities.yaml + data/unique_wonder_ritual_archetypes.yaml"
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


def _registry_contract_summary(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return ""
    return str(value)


def _used_node_capabilities(entry: dict[str, Any]) -> list[str]:
    capabilities: list[str] = []
    for node in ((entry.get("node_graph") or {}).get("nodes") or []):
        if not isinstance(node, dict):
            continue
        node_capabilities = node.get("capabilities")
        if not isinstance(node_capabilities, list):
            node_capabilities = [node_capabilities]
        capabilities.extend(str(capability) for capability in node_capabilities if capability)
    return sorted(dict.fromkeys(capabilities))


def _used_templates(entry: dict[str, Any]) -> list[str]:
    templates: list[str] = []
    generation = entry.get("generation") if isinstance(entry.get("generation"), dict) else {}
    templates.extend(str(template) for template in generation.get("verified_templates", []) or [])
    node_graph = entry.get("node_graph") or {}
    for action in node_graph.get("actions", []) or []:
        if isinstance(action, dict) and action.get("generator_template"):
            templates.append(str(action["generator_template"]))
    for check in node_graph.get("checks", []) or []:
        if isinstance(check, dict) and check.get("generator_template"):
            templates.append(str(check["generator_template"]))
    return sorted(dict.fromkeys(templates))


def _entity_rows(tracked: dict[str, Any]) -> str:
    rows: list[str] = []
    for entity in tracked.get("entities", []) or []:
        if not isinstance(entity, dict):
            rows.append(str(entity))
            continue
        label = entity.get("display_name") or entity.get("key") or ""
        key = entity.get("key")
        rows.append(f"{key} ({label})" if key and label and key != label else str(label or key))
    return ", ".join(rows)


def render_entry_fragment(
    entry: dict[str, Any],
    *,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
) -> str:
    errors = codegen_support_errors(
        entry,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if errors:
        raise CodegenError("; ".join(errors))

    identity = entry.get("identity") or {}
    node_graph = entry.get("node_graph") or {}
    generation = entry.get("generation") or {}
    mechanic_signature = node_graph.get("mechanic_signature") if isinstance(node_graph.get("mechanic_signature"), dict) else {}
    cadence_signature = node_graph.get("cadence_signature") if isinstance(node_graph.get("cadence_signature"), dict) else {}
    design_ir = entry.get("design_ir") if isinstance(entry.get("design_ir"), dict) else {}
    implementation_notes = entry.get("implementation_notes") if isinstance(entry.get("implementation_notes"), dict) else {}
    template_index = template_registry_index(template_registry)
    capability_index = capability_registry_index(capability_registry)
    archetype_index = archetype_registry_index(archetype_registry)
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
            f"- Archetypes: {_join(node_graph.get('archetypes'))}",
            f"- Target files declared by spec: {_join(generation.get('target_files'))}",
            "",
            "## Mechanic Signature",
            "",
        ]
    )
    signature_rows = [
        ["wonder_specific_hook", mechanic_signature.get("wonder_specific_hook", "")],
        ["core_interaction_loop", mechanic_signature.get("core_interaction_loop", "")],
        ["player_decision_pattern", mechanic_signature.get("player_decision_pattern", "")],
        ["state_feedback_model", mechanic_signature.get("state_feedback_model", "")],
        ["failure_or_tension_model", mechanic_signature.get("failure_or_tension_model", "")],
        ["reward_expression", mechanic_signature.get("reward_expression", "")],
        ["reuse_risk_mitigation", mechanic_signature.get("reuse_risk_mitigation", "")],
    ]
    if mechanic_signature.get("custom_archetype_statement"):
        signature_rows.append(["custom_archetype_statement", mechanic_signature.get("custom_archetype_statement", "")])
    lines.extend(_md_table(["field", "design"], signature_rows))
    lines.extend(["", "## Cadence Signature", ""])
    cadence_rows = [
        ["cadence_type", cadence_signature.get("cadence_type", "")],
        ["cadence_rationale", cadence_signature.get("cadence_rationale", "")],
        ["player_agency_model", cadence_signature.get("player_agency_model", "")],
        ["non_monthly_triggers_or_reason", cadence_signature.get("non_monthly_triggers_or_reason", "")],
        ["pacing_failure_mode", cadence_signature.get("pacing_failure_mode", "")],
    ]
    lines.extend(_md_table(["field", "design"], cadence_rows))
    lines.extend(
        [
            "",
            "## Archetype Summary",
            "",
        ]
    )
    archetype_rows: list[list[Any]] = []
    for archetype in node_graph.get("archetypes", []) or []:
        contract = archetype_index.get(str(archetype), {})
        archetype_rows.append(
            [
                archetype,
                _join(contract.get("required_capabilities")),
                _join(contract.get("required_variable_roles")),
                _join(contract.get("required_ui_components")),
                _join(contract.get("required_listeners")),
                f"{contract.get('min_nodes', '')}-{contract.get('max_nodes', '')}",
                contract.get("terminal_requires_capability", ""),
            ]
        )
    lines.extend(
        _md_table(
            ["archetype", "capabilities", "variable_roles", "ui", "listeners", "nodes", "terminal_capability"],
            archetype_rows,
        )
    )
    lines.extend(
        [
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
    lines.extend(["", "## Capability Summary", ""])
    capability_rows: list[list[Any]] = []
    for node in node_graph.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        capabilities = node.get("capabilities") if isinstance(node.get("capabilities"), list) else [node.get("capabilities")]
        capabilities = [capability for capability in capabilities if capability]
        capability_rows.append(
            [
                node.get("key", ""),
                node.get("kind", ""),
                _join(capabilities),
                _join(
                    sorted(
                        {
                            str(capability_index.get(str(capability), {}).get("verified_interface", ""))
                            for capability in capabilities
                            if capability_index.get(str(capability), {}).get("verified_interface")
                        }
                    )
                ),
            ]
        )
    lines.extend(_md_table(["node", "kind", "capabilities", "verified_interface"], capability_rows))
    lines.extend(
        [
            "",
            "## Template / Capability Contract Boundary",
            "",
            "All registry contracts used by this fragment are intermediate-only and must keep `may_write_src=false`.",
            "The output kinds below are Markdown fragments, skeletons, stubs, summaries, or localization drafts; they are not loadable EU5 source files.",
            "",
            "### Templates",
            "",
        ]
    )
    template_rows: list[list[Any]] = []
    for template_key in _used_templates(entry):
        contract = template_index.get(template_key, {})
        template_rows.append(
            [
                template_key,
                contract.get("verified_interface", ""),
                _join(contract.get("output_kinds")),
                _registry_contract_summary(contract.get("may_write_src")),
                contract.get("notes", ""),
            ]
        )
    lines.extend(_md_table(["template", "verified_interface", "output_kinds", "may_write_src", "notes"], template_rows))
    lines.extend(["", "### Capabilities", ""])
    contract_capability_rows: list[list[Any]] = []
    for capability_key in _used_node_capabilities(entry):
        contract = capability_index.get(capability_key, {})
        contract_capability_rows.append(
            [
                capability_key,
                contract.get("verified_interface", ""),
                _join(contract.get("output_kinds")),
                _registry_contract_summary(contract.get("may_write_src")),
                contract.get("notes", ""),
            ]
        )
    lines.extend(
        _md_table(
            ["capability", "verified_interface", "output_kinds", "may_write_src", "notes"],
            contract_capability_rows,
        )
    )
    lines.extend(["", "## Scope Contract Summary", ""])
    scope_rows: list[list[Any]] = []
    for node in node_graph.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        contract = node.get("scope_contract") if isinstance(node.get("scope_contract"), dict) else {}
        scope_rows.append(
            [
                node.get("key", ""),
                contract.get("root_scope", ""),
                contract.get("current_scope", ""),
                _join(contract.get("target_scopes")),
                contract.get("tooltip_safe", ""),
                contract.get("unsafe_pre_eval", ""),
            ]
        )
    lines.extend(
        _md_table(
            ["node", "root_scope", "current_scope", "target_scopes", "tooltip_safe", "unsafe_pre_eval"],
            scope_rows,
        )
    )
    lines.extend(["", "## Listener Contract Summary", ""])
    listener_rows: list[list[Any]] = []
    for node in node_graph.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        contract = node.get("listener_contract") if isinstance(node.get("listener_contract"), dict) else {}
        listener_rows.append(
            [
                node.get("key", ""),
                contract.get("listener", ""),
                contract.get("cadence", ""),
                _join(contract.get("reads")),
                _join(contract.get("writes")),
                contract.get("completion_check", ""),
                contract.get("failure_route", ""),
            ]
        )
    lines.extend(
        _md_table(
            ["node", "listener", "cadence", "reads", "writes", "completion_check", "failure_route"],
            listener_rows,
        )
    )
    lines.extend(["", "## Hidden Executor / Tooltip Safety Notes", ""])
    safety_rows: list[list[Any]] = []
    for node in node_graph.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        contract = node.get("scope_contract") if isinstance(node.get("scope_contract"), dict) else {}
        safety_rows.append(
            [
                node.get("key", ""),
                node.get("kind", ""),
                contract.get("tooltip_safe", ""),
                contract.get("unsafe_pre_eval", ""),
                contract.get("blocked_reason", ""),
                node.get("hidden_executor_handoff", ""),
                _join(node.get("output_kinds")),
            ]
        )
    lines.extend(
        _md_table(
            ["node", "kind", "tooltip_safe", "unsafe_pre_eval", "blocked_reason", "handoff", "output_kinds"],
            safety_rows,
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
    lines.extend(["", "## Design IR Preservation Summary", ""])
    lines.extend(
        [
            f"- Compiler primitives: {_join(design_ir.get('compiler_primitives'))}",
            f"- Projection notes: {design_ir.get('projection_notes', '')}",
            "",
            "### Tracked Entity Sets",
            "",
        ]
    )
    tracked_rows: list[list[Any]] = []
    for tracked in design_ir.get("tracked_entity_sets", []) or []:
        if not isinstance(tracked, dict):
            continue
        tracked_rows.append(
            [
                tracked.get("key", ""),
                tracked.get("entity_type", ""),
                _entity_rows(tracked),
                _join(tracked.get("state_values")),
                _join(tracked.get("per_entity_state")),
                tracked.get("selector", ""),
                tracked.get("ui_binding", ""),
            ]
        )
    lines.extend(
        _md_table(
            ["set", "entity_type", "entities", "states", "per_entity_state", "selector", "ui_binding"],
            tracked_rows,
        )
    )
    lines.extend(["", "### Selectors", ""])
    selector_rows: list[list[Any]] = []
    for selector in design_ir.get("selectors", []) or []:
        if isinstance(selector, dict):
            selector_rows.append(
                [
                    selector.get("key", ""),
                    selector.get("selection_space", ""),
                    selector.get("projection_state", ""),
                ]
            )
    lines.extend(_md_table(["selector", "selection_space", "projection_state"], selector_rows))
    lines.extend(["", "### Risk Branches", ""])
    risk_rows: list[list[Any]] = []
    for branch in design_ir.get("risk_branches", []) or []:
        if isinstance(branch, dict):
            risk_rows.append(
                [
                    branch.get("key", ""),
                    branch.get("risk", ""),
                    branch.get("retry_or_failure", ""),
                ]
            )
    lines.extend(_md_table(["branch", "risk", "retry_or_failure"], risk_rows))
    ui_feedback = design_ir.get("ui_feedback_model") if isinstance(design_ir.get("ui_feedback_model"), dict) else {}
    lines.extend(
        [
            "",
            "### UI Feedback / Uniqueness",
            "",
        ]
    )
    ui_rows = [
        ["components", _join(ui_feedback.get("components"))],
        ["repeated_rows", ui_feedback.get("repeated_rows") or ui_feedback.get("rows", "")],
        ["per_entity_status", ui_feedback.get("per_entity_status", "")],
        ["current_projection", ui_feedback.get("current_projection", "")],
        ["uniqueness_constraints", _join(design_ir.get("uniqueness_constraints"))],
    ]
    lines.extend(_md_table(["field", "design"], ui_rows))
    lines.extend(["", "## Compiler Gap Ledger", ""])
    gap_rows: list[list[Any]] = []
    for row in entry.get("compiler_gap_ledger", []) or []:
        if not isinstance(row, dict):
            continue
        gap_rows.append(
            [
                row.get("primitive", ""),
                row.get("verification_status", ""),
                row.get("harness_backlog_cluster", ""),
                row.get("design_semantics", ""),
                _join(row.get("codebase_evidence")),
                _join(row.get("blocked_by")),
                row.get("fallback_if_unavailable", ""),
            ]
        )
    lines.extend(
        _md_table(
            ["primitive", "status", "backlog_cluster", "semantics", "evidence", "blocked_by", "fallback"],
            gap_rows,
        )
    )
    lines.extend(["", "## Remaining Source Writer Blockers", ""])
    lines.extend(
        [
            "This fragment is not loadable EU5 source. It is an intermediate Harness artifact and does not write `src/` files.",
            "",
        ]
    )
    blockers = implementation_notes.get("remaining_source_writer_blockers", []) or []
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- No source-writer blockers were listed in the spec, but this v1 generator still emits only intermediate Markdown.")
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


def render_index(
    generated: list[dict[str, Any]],
    skipped: list[str],
    *,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
) -> str:
    lines = render_header(SCRIPT_REL, DATA_REL)
    lines.extend(
        [
            "# Unique Wonder Ritual Codegen Index",
            "",
            "This file records the current Harness codegen dry-run/write surface.",
            "The v1 generator emits intermediate Markdown fragments only; it does not write loadable EU5 source or `src/` files.",
            "",
            f"- Generated fragments: {len(generated)}",
            f"- Skipped non-codegen specs: {len(skipped)}",
            f"- Supported templates: {', '.join(sorted(supported_codegen_template_keys(template_registry)))}",
            f"- Supported capabilities: {', '.join(sorted(supported_capability_keys(capability_registry)))}",
            f"- Supported archetypes: {', '.join(sorted(supported_archetype_keys(archetype_registry)))}",
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
        lines.append("No eligible `source_codegen_ready`, `implementation_ready`, or `harness_generated` specs were selected.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate_fragments_for_payload(
    payload: dict[str, Any],
    *,
    wonder_keys: set[str] | None = None,
    write: bool = False,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected, skipped = _selected_entries(payload, wonder_keys)
    registry = template_registry if template_registry is not None else load_template_registry()
    capabilities = capability_registry if capability_registry is not None else load_capability_registry()
    archetypes = archetype_registry if archetype_registry is not None else load_archetype_registry()
    generated: list[dict[str, Any]] = []
    for entry in selected:
        text = render_entry_fragment(
            entry,
            template_registry=registry,
            capability_registry=capabilities,
            archetype_registry=archetypes,
        )
        path = target_path_for_entry(entry, output_dir)
        rel_path = path.relative_to(REPO_ROOT).as_posix() if path.is_absolute() else path.as_posix()
        generated.append({"key": entry_key(entry), "path": rel_path, "text": text})
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    index_path = output_dir / INDEX_FILE_NAME
    index_text = render_index(
        generated,
        skipped,
        template_registry=registry,
        capability_registry=capabilities,
        archetype_registry=archetypes,
    )
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
    template_registry = load_template_registry()
    capability_registry = load_capability_registry()
    archetype_registry = load_archetype_registry()
    errors = validate_spec_payload(
        payload,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
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
            template_registry=template_registry,
            capability_registry=capability_registry,
            archetype_registry=archetype_registry,
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
