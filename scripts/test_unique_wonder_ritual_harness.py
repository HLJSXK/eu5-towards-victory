#!/usr/bin/env python3
"""Small in-memory tests for the unique wonder ritual Harness quality gates."""

import sys
from copy import deepcopy
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from gen_unique_wonder_ritual_code import (  # noqa: E402
    CodegenError,
    generate_fragments_for_payload,
)
from wonder_unique_ritual_harness import (  # noqa: E402
    load_capability_registry,
    load_template_registry,
    validate_capability_registry,
    validate_spec_payload,
)
from wonder_unique_ritual_harness import load_archetype_registry  # noqa: E402
from wonder_unique_ritual_harness import anti_flattening_warnings_for_payload  # noqa: E402


WONDER = {
    "id": 999,
    "key": "unique_test_wonder",
    "base_key": "great_lighthouse",
    "location": "testopolis",
}

NODE_KEYS = ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"]
TEMPLATES = [
    "sequential_event_chain",
    "branch_retry_event",
    "monthly_progress_gate",
    "simple_progress_track_ui_binding",
    "final_reward_dispatch_stub",
    "semantic_contract_fragment",
]
NON_MONTHLY_TEMPLATES = [
    "sequential_event_chain",
    "branch_retry_event",
    "simple_progress_track_ui_binding",
    "final_reward_dispatch_stub",
    "semantic_contract_fragment",
]
BACKEND_CAPABILITIES = [
    "actor_assignment_character_selector_backend",
    "repeated_entity_row_checklist_incident_log_backend",
    "branch_specific_reward_scaling",
    "finance_public_credit_interface_backend",
    "bounded_opposition_religious_community_pressure",
    "auxiliary_building_completion_listener_backend",
]


def event_row(event_id: int, node_key: str, *, retry: bool = False) -> dict:
    options = [f"event.{event_id}.a"]
    if retry:
        options.append(f"event.{event_id}.b")
    return {
        "event_id": event_id,
        "title_key": f"event.{event_id}.t",
        "desc_key": f"event.{event_id}.d",
        "option_keys": options,
        "node_key": node_key,
    }


def node(
    key: str,
    event_id: int,
    *,
    kind: str = "event",
    capabilities: list[str] | None = None,
    reads: list[str] | None = None,
    writes: list[str] | None = None,
    next_nodes: list[str] | None = None,
    failure_or_retry: bool = False,
    retry_target: str | None = None,
    scope_contract: dict | None = None,
    listener_contract: dict | None = None,
    output_kinds: list[str] | None = None,
    hidden_executor_handoff: str | None = None,
) -> dict:
    payload = {
        "key": key,
        "kind": kind,
        "capabilities": capabilities or ["event_chain"],
        "event_id": event_id,
        "player_visible": True,
        "historical_anchor": f"anchor_{key}",
        "enter_condition": f"{key}_enter_check",
        "completion_condition": f"{key}_complete_check",
        "failure_or_retry": failure_or_retry,
        "retry_target": retry_target,
        "next_nodes": next_nodes or [],
        "writes": writes or [],
        "reads": reads or [],
        "ui_state": {"variable_refs": reads or writes or []},
        "loc_refs": [f"node.{key}.label"],
    }
    if scope_contract is not None:
        payload["scope_contract"] = scope_contract
    if listener_contract is not None:
        payload["listener_contract"] = listener_contract
    if output_kinds is not None:
        payload["output_kinds"] = output_kinds
    if hidden_executor_handoff is not None:
        payload["hidden_executor_handoff"] = hidden_executor_handoff
    return payload


def valid_entry() -> dict:
    return {
        "identity": {
            "id": 999,
            "key": "unique_test_wonder",
            "base_key": "great_lighthouse",
            "location": "testopolis",
            "runtime_prefix": "tv_wonder_test",
            "status": "implementation_ready",
        },
        "event_ids": [
            {"id": 1001, "key": "opening"},
            {"id": 1002, "key": "materials"},
            {"id": 1003, "key": "monthly_gate"},
            {"id": 1004, "key": "retry_choice"},
            {"id": 1005, "key": "final_prep"},
            {"id": 1006, "key": "reward"},
        ],
        "node_graph": {
            "model": "state_machine_dsl_v1",
            "archetypes": ["monthly_pressure_countdown"],
            "historical_mechanic": "A visible historical testing mechanic with sequential steps and retry.",
            "mechanic_signature": {
                "wonder_specific_hook": "The test beacon forces a mock harbor council to balance lamp fuel, convoy timing, and a ceremonial final signal.",
                "core_interaction_loop": "The player alternates between preparing the visible stage, waiting for monthly signal progress, and choosing whether to retry failed preparation.",
                "player_decision_pattern": "Each visible step asks whether to spend state capacity now, hold progress for a better final handoff, or route back through an earlier preparation node.",
                "state_feedback_model": "The progress track and checklist expose stage state, monthly signal progress, retry status, and the final reward handoff in separate UI bindings.",
                "failure_or_tension_model": "A retry branch can send the ritual back to materials when the mock signal is untrusted, creating cost pressure without ending the project.",
                "reward_expression": "The final reward combines a national beacon blessing, a local lamp-room reward, and a one-time public-works payout tied to the ritual state.",
                "reuse_risk_mitigation": "The design uses the monthly countdown only as one axis; the signature keeps the beacon council, retry loop, and reward handoff distinct from stock templates.",
            },
            "cadence_signature": {
                "cadence_type": "hybrid",
                "cadence_rationale": "Monthly pacing is used only as a limited beacon-watch checkpoint because the harbor council needs recurring night signals to verify lamp reliability.",
                "player_agency_model": "The player actively commits materials, chooses whether to accept a failed signal or retry earlier preparations, and decides when the final ceremony is credible.",
                "non_monthly_triggers_or_reason": "Non-monthly action comes from the materials event, the retry branch decision, and the final preparation choice that can redirect the chain before reward dispatch.",
                "pacing_failure_mode": "The pacing fails when the monthly checkpoint becomes a passive wait, so the retry branch and final choice keep risk visible before the reward fires.",
            },
            "listeners": ["monthly"],
            "summary": "Test summary.",
            "entry_node": "opening",
            "terminal_nodes": ["reward"],
            "graph_shape": "sequential_retry_monthly_gate",
            "completion_policy": {"allow_terminal_outgoing": False},
            "variables": [
                {
                    "name": "tv_wonder_test_stage",
                    "scope": "country",
                    "type": "number",
                    "roles": ["stage_state", "reward_state"],
                    "initial_value": 0,
                    "writer_nodes": ["opening", "materials", "retry_choice", "final_prep", "reward"],
                    "reader_nodes": ["materials", "monthly_gate", "final_prep", "reward"],
                    "cleanup": "project_state_clear",
                },
                {
                    "name": "tv_wonder_test_progress",
                    "scope": "country",
                    "type": "number",
                    "roles": ["progress_counter"],
                    "initial_value": 0,
                    "writer_nodes": ["monthly_gate"],
                    "reader_nodes": ["monthly_gate", "retry_choice", "final_prep"],
                    "cleanup": "project_state_clear",
                },
            ],
            "nodes": [
                node("opening", 1001, writes=["tv_wonder_test_stage"], next_nodes=["materials"]),
                node(
                    "materials",
                    1002,
                    reads=["tv_wonder_test_stage"],
                    writes=["tv_wonder_test_stage"],
                    next_nodes=["monthly_gate"],
                ),
                node(
                    "monthly_gate",
                    1003,
                    kind="monthly_progress_gate",
                    capabilities=["monthly_progress"],
                    reads=["tv_wonder_test_stage", "tv_wonder_test_progress"],
                    writes=["tv_wonder_test_progress"],
                    next_nodes=["retry_choice"],
                ),
                node(
                    "retry_choice",
                    1004,
                    kind="retry_event",
                    capabilities=["retry_branch"],
                    reads=["tv_wonder_test_progress"],
                    writes=["tv_wonder_test_stage"],
                    next_nodes=["final_prep"],
                    failure_or_retry=True,
                    retry_target="materials",
                ),
                node(
                    "final_prep",
                    1005,
                    reads=["tv_wonder_test_stage", "tv_wonder_test_progress"],
                    writes=["tv_wonder_test_stage"],
                    next_nodes=["reward"],
                ),
                node(
                    "reward",
                    1006,
                    kind="final_reward_dispatch",
                    capabilities=["final_reward_handoff"],
                    reads=["tv_wonder_test_stage"],
                    writes=["tv_wonder_test_stage"],
                ),
            ],
            "edges": [
                {"from": "opening", "to": "materials", "condition": "always", "effect": "advance", "label_key": "edge.opening.materials"},
                {"from": "materials", "to": "monthly_gate", "condition": "always", "effect": "advance", "label_key": "edge.materials.monthly"},
                {"from": "monthly_gate", "to": "retry_choice", "condition": "progress_met", "effect": "advance", "label_key": "edge.monthly.retry"},
                {"from": "retry_choice", "to": "materials", "condition": "retry", "effect": "retry", "label_key": "edge.retry.materials"},
                {"from": "retry_choice", "to": "final_prep", "condition": "accepted", "effect": "advance", "label_key": "edge.retry.final"},
                {"from": "final_prep", "to": "reward", "condition": "always", "effect": "advance", "label_key": "edge.final.reward"},
            ],
            "actions": [
                {
                    "key": "start_chain",
                    "kind": "generator_template",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "sequential_event_chain",
                },
                {
                    "key": "retry_branch",
                    "kind": "generator_template",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "branch_retry_event",
                },
                {
                    "key": "monthly_gate",
                    "kind": "generator_template",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "monthly_progress_gate",
                },
                {
                    "key": "ui_progress",
                    "kind": "generator_template",
                    "scope": "gui_fragment",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "simple_progress_track_ui_binding",
                },
                {
                    "key": "reward_dispatch",
                    "kind": "reward_dispatch_stub",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "final_reward_dispatch_stub",
                },
            ],
            "checks": [
                {
                    "key": "stage_ready",
                    "kind": "generator_template",
                    "generator_template": "sequential_event_chain",
                    "tooltip_key": "check.stage_ready",
                },
                {
                    "key": "monthly_ready",
                    "kind": "generator_template",
                    "generator_template": "monthly_progress_gate",
                    "tooltip_key": "check.monthly_ready",
                },
            ],
        },
        "ui_model": {
            "components": [
                {"type": "progress_track", "key": "progress", "value_variable": "tv_wonder_test_progress"},
                {"type": "checklist", "key": "checklist", "status_variable": "tv_wonder_test_stage"},
            ],
            "bindings": [
                {
                    "key": "progress_binding",
                    "component_key": "progress",
                    "variable_refs": ["tv_wonder_test_stage", "tv_wonder_test_progress"],
                    "node_refs": ["monthly_gate", "reward"],
                    "loc_refs": ["ui.progress.label"],
                }
            ],
        },
        "generation": {
            "status": "ready_for_dry_run",
            "target_files": ["data/generated_fragments/unique_wonder_rituals/unique_test_wonder_ritual_codegen.md"],
            "verified_templates": TEMPLATES,
            "blocked_templates": [],
            "dry_run_notes": "In-memory fixture only.",
        },
        "rewards": {
            "permanent_country_modifier": {"status": "implemented", "description": "A country reward."},
            "local_building_reward": {"status": "implemented", "description": "A local reward."},
            "one_time_reward": {"status": "implemented", "description": "A one-time reward."},
        },
        "localization": {
            "event_keys": [
                event_row(1001, "opening"),
                event_row(1002, "materials"),
                event_row(1003, "monthly_gate"),
                event_row(1004, "retry_choice", retry=True),
                event_row(1005, "final_prep"),
                event_row(1006, "reward"),
            ]
        },
        "implementation_notes": {"needs_verification": []},
    }


def safe_scope_contract(
    *,
    root_scope: str = "country",
    current_scope: str = "country",
    target_scopes: list[str] | None = None,
    tooltip_safe: bool = True,
    unsafe_pre_eval: bool = False,
    blocked_reason: str | None = None,
) -> dict:
    contract = {
        "root_scope": root_scope,
        "current_scope": current_scope,
        "target_scopes": target_scopes or [],
        "tooltip_safe": tooltip_safe,
        "unsafe_pre_eval": unsafe_pre_eval,
    }
    if blocked_reason:
        contract["blocked_reason"] = blocked_reason
    return contract


def add_fixture_event(entry: dict, event_id: int, key: str, localization: dict[str, str] | None = None) -> None:
    entry["event_ids"].append({"id": event_id, "key": key})
    entry["localization"]["event_keys"].append(event_row(event_id, key))
    if localization is not None:
        localization[f"event.{event_id}.t"] = f"Title {event_id}"
        localization[f"event.{event_id}.d"] = localization["event.1001.d"]
        localization[f"event.{event_id}.a"] = "Continue"
        localization[f"node.{key}.label"] = key


def actor_assignment_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["patronage_actor_assignment", "monthly_pressure_countdown"]
    graph["variables"].append(
        {
            "name": "tv_wonder_test_actor",
            "scope": "character",
            "type": "scope_ref",
            "roles": ["assigned_actor"],
            "initial_value": "none",
            "writer_nodes": ["materials"],
            "reader_nodes": ["materials"],
            "cleanup": "project_state_clear",
        }
    )
    materials = graph["nodes"][1]
    materials["kind"] = "assignment_gate"
    materials["capabilities"] = ["actor_assignment"]
    materials["scope_contract"] = safe_scope_contract(current_scope="character", target_scopes=["character"])
    materials["reads"].append("tv_wonder_test_actor")
    materials["writes"].append("tv_wonder_test_actor")
    materials["ui_state"]["variable_refs"].append("tv_wonder_test_actor")
    entry["ui_model"]["components"].append(
        {"type": "actor_slots", "key": "actor", "status_variable": "tv_wonder_test_actor"}
    )
    return entry


def route_incident_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["expedition_route_chain", "monthly_pressure_countdown"]
    graph["variables"].append(
        {
            "name": "tv_wonder_test_route",
            "scope": "country",
            "type": "number",
            "roles": ["route_state"],
            "initial_value": 0,
            "writer_nodes": ["materials"],
            "reader_nodes": ["materials"],
            "cleanup": "project_state_clear",
        }
    )
    materials = graph["nodes"][1]
    materials["kind"] = "route_gate"
    materials["capabilities"] = ["route_gate"]
    materials["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    materials["reads"].append("tv_wonder_test_route")
    materials["writes"].append("tv_wonder_test_route")
    materials["ui_state"]["variable_refs"].append("tv_wonder_test_route")
    final_prep = graph["nodes"][4]
    final_prep["kind"] = "incident_event"
    final_prep["capabilities"] = ["event_chain"]
    entry["ui_model"]["components"].append(
        {"type": "route_map", "key": "route", "value_variable": "tv_wonder_test_route"}
    )
    return entry


def incident_retry_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["incident_retry_gauntlet", "monthly_pressure_countdown"]
    final_prep = graph["nodes"][4]
    final_prep["kind"] = "incident_event"
    final_prep["capabilities"] = ["event_chain"]
    entry["ui_model"]["components"].append(
        {"type": "incident_log", "key": "incident", "status_variable": "tv_wonder_test_stage"}
    )
    return entry


def actor_selector_backend_entry() -> dict:
    entry = actor_assignment_entry()
    entry["node_graph"]["nodes"][1]["capabilities"].append("actor_assignment_character_selector_backend")
    return entry


def repeated_row_backend_entry() -> dict:
    entry = incident_retry_entry()
    graph = entry["node_graph"]
    graph["variables"][0]["roles"].extend(["incident_state", "checklist_state"])
    graph["variables"][0]["reader_nodes"].append("retry_choice")
    retry_choice = graph["nodes"][3]
    retry_choice["capabilities"].append("repeated_entity_row_checklist_incident_log_backend")
    retry_choice["ui_state"]["variable_refs"].append("tv_wonder_test_stage")
    return entry


def branch_scaling_backend_entry() -> dict:
    entry = valid_entry()
    reward = entry["node_graph"]["nodes"][5]
    reward["capabilities"].append("branch_specific_reward_scaling")
    return entry


def finance_public_credit_backend_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["public_credit_charter_retry"]
    graph["listeners"] = []
    graph["cadence_signature"] = {
        "cadence_type": "instant_but_branching",
        "cadence_rationale": "The public-credit fixture resolves through an immediate charter bargain, pledge-risk incident, and final fiscal handoff rather than a monthly counter.",
        "player_agency_model": "The player chooses which credit compact receives authority, handles the first default-pressure incident, and accepts the fiscal or social cost before reward dispatch.",
        "non_monthly_triggers_or_reason": "Non-monthly validation comes from the charter option, creditor or open-market incident branch, and final public-credit reward handoff.",
        "pacing_failure_mode": "The pacing fails if public credit becomes a passive timer, so the fixture keeps charter choice, pledge risk, and retry pressure visible.",
    }
    graph["variables"][0]["roles"] = ["stage_state", "reward_state", "incident_state", "checklist_state"]
    graph["variables"][0]["writer_nodes"] = ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"]
    graph["variables"][0]["reader_nodes"] = ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"]
    graph["variables"][1]["roles"] = ["incident_state", "reward_state", "checklist_state"]
    graph["variables"][1]["writer_nodes"] = ["monthly_gate"]
    graph["variables"][1]["reader_nodes"] = ["monthly_gate", "retry_choice", "final_prep"]

    for test_node in graph["nodes"]:
        test_node["reads"] = sorted(set(test_node.get("reads", [])) | {"tv_wonder_test_stage"})
        test_node["writes"] = sorted(set(test_node.get("writes", [])) | {"tv_wonder_test_stage"})
        test_node["ui_state"] = {"variable_refs": sorted(set(test_node.get("ui_state", {}).get("variable_refs", [])) | {"tv_wonder_test_stage"})}
        test_node["scope_contract"] = safe_scope_contract(target_scopes=["country"])

    graph["nodes"][1]["capabilities"].append("finance_public_credit_interface_backend")
    graph["nodes"][2]["kind"] = "choice_event"
    graph["nodes"][2]["capabilities"] = ["event_chain", "finance_public_credit_interface_backend"]
    graph["nodes"][3]["capabilities"].append("finance_public_credit_interface_backend")
    graph["nodes"][3]["capabilities"].append("repeated_entity_row_checklist_incident_log_backend")
    graph["nodes"][4]["kind"] = "incident_event"
    graph["nodes"][4]["capabilities"] = ["event_chain", "finance_public_credit_interface_backend"]
    graph["nodes"][5]["capabilities"].append("finance_public_credit_interface_backend")
    graph["nodes"][5]["capabilities"].append("branch_specific_reward_scaling")

    graph["actions"][2]["generator_template"] = "semantic_contract_fragment"
    graph["checks"][1]["generator_template"] = "semantic_contract_fragment"
    entry["generation"]["verified_templates"] = NON_MONTHLY_TEMPLATES
    entry["ui_model"]["components"].append(
        {"type": "incident_log", "key": "credit_incident", "status_variable": "tv_wonder_test_progress"}
    )
    return entry


def finance_public_credit_missing_backend_entry() -> dict:
    entry = finance_public_credit_backend_entry()
    for test_node in entry["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "finance_public_credit_interface_backend"
        ]
    return entry


def bounded_religious_pressure_backend_entry() -> dict:
    entry = valid_entry()
    opening = entry["node_graph"]["nodes"][0]
    opening["capabilities"].append("bounded_opposition_religious_community_pressure")
    opening["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    return entry


def route_hidden_entry(localization: dict[str, str] | None = None) -> dict:
    entry = route_incident_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = [
        "expedition_route_chain",
        "monthly_pressure_countdown",
        "hidden_executor_finalization",
    ]
    graph["variables"][0]["writer_nodes"].insert(-1, "hidden_exec")
    graph["variables"][0]["reader_nodes"].insert(-1, "hidden_exec")
    final_prep = graph["nodes"][4]
    final_prep["next_nodes"] = ["hidden_exec"]
    final_prep["hidden_executor_handoff"] = "hidden_exec"
    hidden_exec = node(
        "hidden_exec",
        1007,
        kind="hidden_executor_handoff",
        capabilities=["final_reward_handoff"],
        reads=["tv_wonder_test_stage"],
        writes=["tv_wonder_test_stage"],
        next_nodes=["reward"],
    )
    hidden_exec["player_visible"] = False
    graph["nodes"].insert(5, hidden_exec)
    graph["edges"] = [
        edge
        for edge in graph["edges"]
        if not (edge["from"] == "final_prep" and edge["to"] == "reward")
    ]
    graph["edges"].extend(
        [
            {"from": "final_prep", "to": "hidden_exec", "condition": "complete", "effect": "handoff", "label_key": "edge.final.hidden"},
            {"from": "hidden_exec", "to": "reward", "condition": "always", "effect": "advance", "label_key": "edge.hidden.reward"},
        ]
    )
    add_fixture_event(entry, 1007, "hidden_exec", localization)
    return entry


def resource_listener_hidden_entry(localization: dict[str, str] | None = None) -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = [
        "resource_accumulation_ritual",
        "listener_resolution_ritual",
        "hidden_executor_finalization",
    ]
    graph["variables"][0]["writer_nodes"].insert(-1, "hidden_exec")
    graph["variables"][0]["reader_nodes"].insert(-1, "hidden_exec")
    graph["variables"][1]["roles"] = ["progress_counter", "resource_state"]
    graph["variables"].append(
        {
            "name": "tv_wonder_test_listener",
            "scope": "country",
            "type": "number",
            "roles": ["listener_state"],
            "initial_value": 0,
            "writer_nodes": ["final_prep"],
            "reader_nodes": ["final_prep"],
            "cleanup": "project_state_clear",
        }
    )
    monthly_gate = graph["nodes"][2]
    monthly_gate["kind"] = "resource_gate"
    monthly_gate["capabilities"] = ["resource_gate"]
    monthly_gate["scope_contract"] = safe_scope_contract(target_scopes=["country"])
    final_prep = graph["nodes"][4]
    final_prep["kind"] = "listener_gate"
    final_prep["capabilities"] = ["listener_gate"]
    final_prep["reads"].append("tv_wonder_test_listener")
    final_prep["writes"].append("tv_wonder_test_listener")
    final_prep["next_nodes"] = ["hidden_exec"]
    final_prep["scope_contract"] = safe_scope_contract(
        unsafe_pre_eval=True,
        tooltip_safe=False,
        target_scopes=["country"],
    )
    final_prep["hidden_executor_handoff"] = "hidden_exec"
    final_prep["listener_contract"] = {
        "listener": "monthly",
        "cadence": "monthly",
        "reads": ["tv_wonder_test_listener"],
        "writes": ["tv_wonder_test_listener"],
        "completion_check": "listener_complete",
        "failure_route": "retry_choice",
    }
    hidden_exec = node(
        "hidden_exec",
        1007,
        kind="hidden_executor_handoff",
        capabilities=["final_reward_handoff"],
        reads=["tv_wonder_test_stage"],
        writes=["tv_wonder_test_stage"],
        next_nodes=["reward"],
    )
    hidden_exec["player_visible"] = False
    graph["nodes"].insert(5, hidden_exec)
    graph["edges"] = [
        edge
        for edge in graph["edges"]
        if not (edge["from"] == "final_prep" and edge["to"] == "reward")
    ]
    graph["edges"].extend(
        [
            {"from": "final_prep", "to": "hidden_exec", "condition": "complete", "effect": "handoff", "label_key": "edge.final.hidden"},
            {"from": "hidden_exec", "to": "reward", "condition": "always", "effect": "advance", "label_key": "edge.hidden.reward"},
        ]
    )
    add_fixture_event(entry, 1007, "hidden_exec", localization)
    entry["ui_model"]["components"].append(
        {"type": "material_stockpile", "key": "stockpile", "value_variable": "tv_wonder_test_progress"}
    )
    entry["ui_model"]["components"].append(
        {"type": "incident_log", "key": "listener_incident", "status_variable": "tv_wonder_test_stage"}
    )
    return entry


def auxiliary_completion_backend_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["listeners"] = ["monthly", "auxiliary_building_completion"]
    graph["variables"].append(
        {
            "name": "tv_wonder_test_auxiliary_listener",
            "scope": "country",
            "type": "number",
            "roles": ["listener_state"],
            "initial_value": 0,
            "writer_nodes": ["final_prep"],
            "reader_nodes": ["final_prep"],
            "cleanup": "project_state_clear",
        }
    )
    final_prep = graph["nodes"][4]
    final_prep["kind"] = "listener_gate"
    final_prep["capabilities"] = ["auxiliary_building_completion_listener_backend"]
    final_prep["reads"].append("tv_wonder_test_auxiliary_listener")
    final_prep["writes"].append("tv_wonder_test_auxiliary_listener")
    final_prep["ui_state"]["variable_refs"].append("tv_wonder_test_auxiliary_listener")
    final_prep["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    final_prep["listener_contract"] = {
        "listener": "auxiliary_building_completion",
        "cadence": "auxiliary_building_completion_or_annex_inspection",
        "reads": ["tv_wonder_test_auxiliary_listener"],
        "writes": ["tv_wonder_test_auxiliary_listener"],
        "completion_check": "auxiliary_completion_marked",
        "failure_route": "retry_choice",
    }
    return entry


def arsenal_ropewalk_launch_inspection_entry() -> dict:
    entry = auxiliary_completion_backend_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["arsenal_ropewalk_launch_inspection"]
    graph["listeners"] = ["auxiliary_building_completion"]
    graph["cadence_signature"] = {
        "cadence_type": "construction_or_auxiliary_building",
        "cadence_rationale": "The fixture resolves when an auxiliary building or annex inspection completes, then routes through repair or reward rather than monthly progress.",
        "player_agency_model": "The player chooses the arsenal work package, prepares visible stockpiles, and decides whether the completion inspection should be repaired or accepted.",
        "non_monthly_triggers_or_reason": "Non-monthly validation is the auxiliary-building completion listener plus a repair branch that can return to material preparation before final reward dispatch.",
        "pacing_failure_mode": "The pacing fails if construction completion becomes a one-click finish, so the fixture keeps a stockpile gate, listener contract, and retry branch visible.",
    }
    graph["variables"][1]["roles"] = ["resource_state"]
    resource_gate = graph["nodes"][2]
    resource_gate["kind"] = "resource_gate"
    resource_gate["capabilities"] = ["resource_gate"]
    resource_gate["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["actions"][2]["generator_template"] = "semantic_contract_fragment"
    graph["checks"][1]["generator_template"] = "semantic_contract_fragment"
    entry["generation"]["verified_templates"] = NON_MONTHLY_TEMPLATES
    entry["ui_model"]["components"].append(
        {"type": "material_stockpile", "key": "stockpile", "value_variable": "tv_wonder_test_progress"}
    )
    return entry


def arsenal_missing_completion_backend_entry() -> dict:
    entry = arsenal_ropewalk_launch_inspection_entry()
    for test_node in entry["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "auxiliary_building_completion_listener_backend"
        ]
    return entry


def pure_non_monthly_cadence_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = []
    graph["listeners"] = []
    graph["cadence_signature"] = {
        "cadence_type": "route_certification",
        "cadence_rationale": "The ritual resolves through route proof events and player choices rather than any recurring calendar tick.",
        "player_agency_model": "The player certifies a route, handles a contested passage event, chooses whether to retry certification, and then commits the final reward handoff.",
        "non_monthly_triggers_or_reason": "Non-monthly triggers are the route gate action, the contested event branch, and the retry decision that can send the player back to materials.",
        "pacing_failure_mode": "The pacing fails if route certification becomes a single click, so the route gate must feed a retry branch before final preparation can resolve.",
    }
    graph["variables"][1]["roles"] = ["route_state"]
    route_gate = graph["nodes"][2]
    route_gate["kind"] = "route_gate"
    route_gate["capabilities"] = ["route_gate"]
    route_gate["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["actions"][2]["generator_template"] = "semantic_contract_fragment"
    graph["checks"][1]["generator_template"] = "semantic_contract_fragment"
    entry["generation"]["verified_templates"] = NON_MONTHLY_TEMPLATES
    return entry


def design_ir_fixture() -> dict:
    return {
        "compiler_primitives": ["test_route_rows"],
        "phases": [{"key": "route_test", "gameplay_stage": "Prove a named route without flattening it."}],
        "player_proofs": ["The player proves a named route and its incident state."],
        "tracked_entity_sets": [
            {
                "key": "test_routes",
                "entity_type": "route",
                "entities": [{"key": "alpha"}, {"key": "beta"}],
                "state_values": ["pending", "controlled", "basing", "unresolved"],
                "per_entity_state": {"status_variable_pattern": "tv_wonder_test_route_<route>_status"},
                "selector": "The next pending route is selected by a route gate.",
                "ui_binding": "route_map:test_routes renders one row per route.",
            }
        ],
        "selectors": [{"key": "active_route", "selection_space": "pending test routes"}],
        "risk_branches": [{"key": "route_failed", "risk": "A route incident can delay certification."}],
        "player_actions": ["Choose whether to pay, delay, or accept reduced route proof."],
        "map_scope_evidence": ["A route endpoint must resolve to location or owner scope evidence."],
        "ui_feedback_model": {"components": ["route_map", "progress_track"], "rows": "Repeated route rows."},
        "uniqueness_constraints": ["The route set is specific enough that a generic event chain would flatten it."],
        "projection_notes": "The node_graph projection preserves design intent but compresses repeated route rows.",
    }


def compiler_gap_row(verification_status: str = "needs_codebase_search") -> dict:
    codebase_evidence = ["fixture evidence"]
    if verification_status == "backend_ready":
        codebase_evidence = ["capability:route_gate", "template:semantic_contract_fragment"]
    return {
        "primitive": "test_route_rows",
        "design_semantics": "Repeated named route rows must survive design even before source compiler support exists.",
        "required_game_interfaces": ["route map UI", "per-route variables"],
        "codebase_evidence": codebase_evidence,
        "verification_status": verification_status,
        "search_questions": ["Which source compiler primitive should own repeated route rows?"],
        "blocked_by": ["fixture unresolved gap"],
        "fallback_if_unavailable": "Keep the high-fidelity design_ir and project to a simple node graph.",
    }


def high_fidelity_design_entry(
    *,
    status: str = "design_complete",
    verification_status: str = "needs_codebase_search",
) -> dict:
    entry = valid_entry()
    entry["identity"]["status"] = status
    entry["design_ir"] = design_ir_fixture()
    entry["compiler_gap_ledger"] = [compiler_gap_row(verification_status)]
    entry["implementation_notes"]["remaining_source_writer_blockers"] = [
        "Fixture backend is intermediate-only and not loadable EU5 source."
    ]
    return entry


def loc() -> dict[str, str]:
    long_text = "This event description is intentionally long enough to satisfy the ritual text density gate. " * 2
    data: dict[str, str] = {}
    for event_id in range(1001, 1007):
        data[f"event.{event_id}.t"] = f"Title {event_id}"
        data[f"event.{event_id}.d"] = long_text
        data[f"event.{event_id}.a"] = "Continue"
        data[f"event.{event_id}.b"] = "Retry"
    for key in NODE_KEYS:
        data[f"node.{key}.label"] = key
    for key in (
        "edge.opening.materials",
        "edge.materials.monthly",
        "edge.monthly.retry",
        "edge.retry.materials",
        "edge.retry.final",
        "edge.final.reward",
        "edge.final.hidden",
        "edge.hidden.reward",
        "check.stage_ready",
        "check.monthly_ready",
        "ui.progress.label",
    ):
        data[key] = key
    return data


def assert_has_error(
    name: str,
    entry: dict,
    needle: str,
    *,
    localization: dict[str, str] | None = None,
    occupied_event_ids: set[int] | None = None,
    template_registry: dict | None = None,
    capability_registry: dict | None = None,
    archetype_registry: dict | None = None,
) -> None:
    errors = validate_spec_payload(
        {"unique_wonders": [entry]},
        wonders=[WONDER],
        localization=localization or loc(),
        occupied_event_ids=occupied_event_ids,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected error containing {needle!r}, got {errors}")


def assert_codegen_error(
    name: str,
    entry: dict,
    needle: str,
    *,
    template_registry: dict | None = None,
    archetype_registry: dict | None = None,
) -> None:
    try:
        generate_fragments_for_payload(
            {"unique_wonders": [entry]},
            wonder_keys={"unique_test_wonder"},
            template_registry=template_registry,
            archetype_registry=archetype_registry,
        )
    except CodegenError as exc:
        if needle not in str(exc):
            raise AssertionError(f"{name}: expected codegen error containing {needle!r}, got {exc}") from exc
        return
    raise AssertionError(f"{name}: expected CodegenError containing {needle!r}")


def main() -> None:
    good_errors = validate_spec_payload(
        {"unique_wonders": [valid_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if good_errors:
        raise AssertionError(f"valid entry unexpectedly failed: {good_errors}")

    design_complete_errors = validate_spec_payload(
        {"unique_wonders": [high_fidelity_design_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if design_complete_errors:
        raise AssertionError(f"design_complete fixture with compiler gaps unexpectedly failed: {design_complete_errors}")

    compiler_mapped_errors = validate_spec_payload(
        {"unique_wonders": [high_fidelity_design_entry(status="compiler_mapped")]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if compiler_mapped_errors:
        raise AssertionError(f"compiler_mapped fixture unexpectedly failed: {compiler_mapped_errors}")

    source_ready_errors = validate_spec_payload(
        {"unique_wonders": [high_fidelity_design_entry(status="source_codegen_ready", verification_status="backend_ready")]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if source_ready_errors:
        raise AssertionError(f"source_codegen_ready fixture unexpectedly failed: {source_ready_errors}")

    non_monthly_errors = validate_spec_payload(
        {"unique_wonders": [pure_non_monthly_cadence_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if non_monthly_errors:
        raise AssertionError(f"pure non-monthly cadence fixture unexpectedly failed: {non_monthly_errors}")

    hybrid_monthly_errors = validate_spec_payload(
        {"unique_wonders": [valid_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if hybrid_monthly_errors:
        raise AssertionError(f"hybrid monthly cadence fixture unexpectedly failed: {hybrid_monthly_errors}")

    no_archetype = valid_entry()
    del no_archetype["node_graph"]["archetypes"]
    no_archetype_errors = validate_spec_payload(
        {"unique_wonders": [no_archetype]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if no_archetype_errors:
        raise AssertionError(f"no-archetype fixture unexpectedly failed: {no_archetype_errors}")

    custom_archetype = valid_entry()
    custom_archetype["node_graph"]["archetypes"] = ["custom_beacon_council_signal_table"]
    custom_archetype["node_graph"]["mechanic_signature"]["custom_archetype_statement"] = (
        "This custom shape treats the ritual as a beacon council signal table, not as a registry blueprint; "
        "monthly progress, retry choices, and final reward handoff remain validated by capabilities."
    )
    custom_archetype_errors = validate_spec_payload(
        {"unique_wonders": [custom_archetype]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if custom_archetype_errors:
        raise AssertionError(f"custom archetype fixture unexpectedly failed: {custom_archetype_errors}")

    actor_errors = validate_spec_payload(
        {"unique_wonders": [actor_assignment_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if actor_errors:
        raise AssertionError(f"actor assignment fixture unexpectedly failed: {actor_errors}")

    mixed_shape = actor_assignment_entry()
    mixed_shape["node_graph"]["archetypes"] = ["monthly_pressure_countdown"]
    mixed_shape_errors = validate_spec_payload(
        {"unique_wonders": [mixed_shape]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if mixed_shape_errors:
        raise AssertionError(f"mixed archetype/capability fixture unexpectedly failed: {mixed_shape_errors}")

    route_errors = validate_spec_payload(
        {"unique_wonders": [route_incident_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if route_errors:
        raise AssertionError(f"route/incident fixture unexpectedly failed: {route_errors}")

    incident_errors = validate_spec_payload(
        {"unique_wonders": [incident_retry_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if incident_errors:
        raise AssertionError(f"incident retry fixture unexpectedly failed: {incident_errors}")

    route_hidden_loc = loc()
    route_hidden_errors = validate_spec_payload(
        {"unique_wonders": [route_hidden_entry(route_hidden_loc)]},
        wonders=[WONDER],
        localization=route_hidden_loc,
        require_all_wonders=True,
    )
    if route_hidden_errors:
        raise AssertionError(f"route/hidden fixture unexpectedly failed: {route_hidden_errors}")

    listener_loc = loc()
    listener_errors = validate_spec_payload(
        {"unique_wonders": [resource_listener_hidden_entry(listener_loc)]},
        wonders=[WONDER],
        localization=listener_loc,
        require_all_wonders=True,
    )
    if listener_errors:
        raise AssertionError(f"resource/listener/hidden fixture unexpectedly failed: {listener_errors}")

    capability_registry = load_capability_registry()
    capability_errors = validate_capability_registry(capability_registry)
    if capability_errors:
        raise AssertionError(f"capability registry unexpectedly failed: {capability_errors}")
    capability_index = {
        capability["key"]: capability
        for capability in capability_registry["capabilities"]
    }
    for capability_key in BACKEND_CAPABILITIES:
        contract = capability_index.get(capability_key)
        if contract is None:
            raise AssertionError(f"missing backend capability contract {capability_key!r}")
        if contract.get("may_write_src") is not False:
            raise AssertionError(f"backend capability {capability_key!r} may write src")
        if any("src" in str(kind).lower() for kind in contract.get("output_kinds", [])):
            raise AssertionError(f"backend capability {capability_key!r} advertises source output")

    for name, entry in (
        ("actor selector backend", actor_selector_backend_entry()),
        ("repeated row backend", repeated_row_backend_entry()),
        ("branch scaling backend", branch_scaling_backend_entry()),
        ("finance public credit backend", finance_public_credit_backend_entry()),
        ("bounded religious pressure backend", bounded_religious_pressure_backend_entry()),
        ("auxiliary completion backend", auxiliary_completion_backend_entry()),
        ("arsenal ropewalk launch inspection", arsenal_ropewalk_launch_inspection_entry()),
    ):
        backend_errors = validate_spec_payload(
            {"unique_wonders": [entry]},
            wonders=[WONDER],
            localization=loc(),
            require_all_wonders=True,
        )
        if backend_errors:
            raise AssertionError(f"{name} fixture unexpectedly failed: {backend_errors}")

    assert_has_error(
        "public credit archetype missing finance backend",
        finance_public_credit_missing_backend_entry(),
        "archetype 'public_credit_charter_retry' missing required capability(s): finance_public_credit_interface_backend",
    )

    assert_has_error(
        "arsenal archetype missing completion backend",
        arsenal_missing_completion_backend_entry(),
        "archetype 'arsenal_ropewalk_launch_inspection' missing required capability(s): auxiliary_building_completion_listener_backend",
    )

    for capability_key in BACKEND_CAPABILITIES:
        backend_gap = high_fidelity_design_entry(verification_status="backend_ready")
        backend_gap["compiler_gap_ledger"][0]["codebase_evidence"] = [
            f"capability:{capability_key}",
            "manual evidence would not be enough by itself",
        ]
        backend_gap_errors = validate_spec_payload(
            {"unique_wonders": [backend_gap]},
            wonders=[WONDER],
            localization=loc(),
            require_all_wonders=True,
        )
        if backend_gap_errors:
            raise AssertionError(f"backend_ready gap for {capability_key} unexpectedly failed: {backend_gap_errors}")

    result = generate_fragments_for_payload(
        {"unique_wonders": [valid_entry()]},
        wonder_keys={"unique_test_wonder"},
    )
    generated_text = result["generated"][0]["text"]
    for expected in (
        "## Mechanic Signature",
        "## Cadence Signature",
        "## Archetype Summary",
        "## Event Skeleton",
        "## Capability Summary",
        "## Template / Capability Contract Boundary",
        "## Scope Contract Summary",
        "## Listener Contract Summary",
        "## Hidden Executor / Tooltip Safety Notes",
        "## Variable Table",
        "## UI Binding Summary",
        "## Reward Dispatch Stub",
        "tv_engineering_department.1006",
    ):
        if expected not in generated_text:
            raise AssertionError(f"codegen dry-run missing {expected!r}")

    high_fidelity_result = generate_fragments_for_payload(
        {"unique_wonders": [high_fidelity_design_entry(status="source_codegen_ready", verification_status="backend_ready")]},
        wonder_keys={"unique_test_wonder"},
    )
    high_fidelity_text = high_fidelity_result["generated"][0]["text"]
    for expected in (
        "## Design IR Preservation Summary",
        "test_routes",
        "alpha, beta",
        "Repeated route rows",
        "The node_graph projection preserves design intent",
        "## Compiler Gap Ledger",
        "test_route_rows",
        "backend_ready",
        "capability:route_gate",
        "## Remaining Source Writer Blockers",
        "not loadable EU5 source",
        "Fixture backend is intermediate-only",
        "`may_write_src=false`",
        "| may_write_src |",
        "| event_chain |",
    ):
        if expected not in high_fidelity_text:
            raise AssertionError(f"high-fidelity codegen dry-run missing {expected!r}")
    if "may_write_src | true" in high_fidelity_text:
        raise AssertionError("high-fidelity codegen dry-run implies source-writing support")

    duplicate = valid_entry()
    duplicate["event_ids"][2]["id"] = 1002
    assert_has_error("duplicate event id", duplicate, "duplicates")

    duplicate_node_event_id = valid_entry()
    duplicate_node_event_id["node_graph"]["nodes"][4]["event_id"] = duplicate_node_event_id["node_graph"]["nodes"][2]["event_id"]
    assert_has_error(
        "duplicate node event id",
        duplicate_node_event_id,
        "node final_prep event_id 1003 duplicates node monthly_gate",
    )

    missing_reward = valid_entry()
    missing_reward["rewards"]["one_time_reward"]["status"] = "pending"
    assert_has_error("missing reward", missing_reward, "one_time_reward")

    short_text = valid_entry()
    short_loc = loc()
    for event_id in range(1001, 1007):
        short_loc[f"event.{event_id}.d"] = "Short."
    assert_has_error("short text", short_text, "too thin", localization=short_loc)

    one_event = valid_entry()
    one_event["event_ids"] = one_event["event_ids"][:1]
    one_event["node_graph"]["nodes"] = one_event["node_graph"]["nodes"][:1]
    assert_has_error("one-event ritual", one_event, "3 player-visible ritual nodes")

    bad_runtime = valid_entry()
    bad_runtime["node_graph"]["variables"][0]["name"] = "tv_other_stage"
    assert_has_error("runtime prefix", bad_runtime, "must start with tv_wonder_test")

    unsupported_listener = valid_entry()
    unsupported_listener["node_graph"]["listeners"] = ["unsupported_listener"]
    assert_has_error("unsupported listener", unsupported_listener, "unsupported listener")

    unknown_status = valid_entry()
    unknown_status["identity"]["status"] = "almost_ready"
    assert_has_error("unknown status", unknown_status, "identity.status 'almost_ready' is unsupported")

    invalid_gap_status = high_fidelity_design_entry(verification_status="maybe_later")
    assert_has_error("invalid compiler gap status", invalid_gap_status, "invalid verification_status")

    verified_without_evidence = high_fidelity_design_entry(verification_status="verified_existing")
    verified_without_evidence["compiler_gap_ledger"][0]["codebase_evidence"] = []
    assert_has_error(
        "verified existing missing evidence",
        verified_without_evidence,
        "verified_existing requires codebase_evidence",
    )

    backend_without_registry_evidence = high_fidelity_design_entry(verification_status="backend_ready")
    backend_without_registry_evidence["compiler_gap_ledger"][0]["codebase_evidence"] = [
        "scripts/manual_evidence_only.py"
    ]
    assert_has_error(
        "backend ready missing registry evidence",
        backend_without_registry_evidence,
        "backend_ready requires valid capability:<key> or template:<key>",
    )

    writable_capability_registry = deepcopy(load_capability_registry())
    writable_capability_registry["capabilities"][0]["may_write_src"] = True
    assert_has_error(
        "capability may_write_src",
        valid_entry(),
        "must declare may_write_src: false",
        capability_registry=writable_capability_registry,
    )

    finance_writable_registry = deepcopy(load_capability_registry())
    for capability in finance_writable_registry["capabilities"]:
        if capability.get("key") == "finance_public_credit_interface_backend":
            capability["may_write_src"] = True
            break
    assert_has_error(
        "finance capability may_write_src",
        finance_public_credit_backend_entry(),
        "must declare may_write_src: false",
        capability_registry=finance_writable_registry,
    )

    finance_source_output_registry = deepcopy(load_capability_registry())
    for capability in finance_source_output_registry["capabilities"]:
        if capability.get("key") == "finance_public_credit_interface_backend":
            capability["output_kinds"].append("loadable_src")
            break
    assert_has_error(
        "finance capability source output",
        finance_public_credit_backend_entry(),
        "unsupported value(s): loadable_src",
        capability_registry=finance_source_output_registry,
    )

    auxiliary_writable_registry = deepcopy(load_capability_registry())
    for capability in auxiliary_writable_registry["capabilities"]:
        if capability.get("key") == "auxiliary_building_completion_listener_backend":
            capability["may_write_src"] = True
            break
    assert_has_error(
        "auxiliary completion capability may_write_src",
        auxiliary_completion_backend_entry(),
        "must declare may_write_src: false",
        capability_registry=auxiliary_writable_registry,
    )

    auxiliary_source_output_registry = deepcopy(load_capability_registry())
    for capability in auxiliary_source_output_registry["capabilities"]:
        if capability.get("key") == "auxiliary_building_completion_listener_backend":
            capability["output_kinds"].append("loadable_src")
            break
    assert_has_error(
        "auxiliary completion capability source output",
        auxiliary_completion_backend_entry(),
        "unsupported value(s): loadable_src",
        capability_registry=auxiliary_source_output_registry,
    )

    needs_search_without_questions = high_fidelity_design_entry()
    needs_search_without_questions["compiler_gap_ledger"][0]["search_questions"] = []
    assert_has_error(
        "needs_codebase_search missing questions",
        needs_search_without_questions,
        "needs_codebase_search requires meaningful search_questions",
    )

    source_ready_with_gap = high_fidelity_design_entry(status="source_codegen_ready")
    assert_has_error(
        "source_codegen_ready unresolved compiler gap",
        source_ready_with_gap,
        "unresolved compiler gap",
    )

    source_ready_verified_existing = high_fidelity_design_entry(
        status="source_codegen_ready",
        verification_status="verified_existing",
    )
    assert_has_error(
        "source_codegen_ready verified_existing gap",
        source_ready_verified_existing,
        "not backend_ready",
    )

    implementation_ready_verified_existing = high_fidelity_design_entry(
        status="implementation_ready",
        verification_status="verified_existing",
    )
    assert_has_error(
        "implementation_ready verified_existing gap",
        implementation_ready_verified_existing,
        "not backend_ready",
    )

    flattened_route = high_fidelity_design_entry()
    flattened_route["design_ir"]["tracked_entity_sets"][0]["key"] = "single_progress_counter"
    flattened_route["design_ir"]["tracked_entity_sets"][0]["entity_type"] = "counter"
    flattening_warnings = anti_flattening_warnings_for_payload(
        {"unique_wonders": [flattened_route]},
        design_matrix={
            "unique_wonders": [
                {
                    "wonder_key": "unique_test_wonder",
                    "expected_ui_model": ["route_map"],
                    "proposed_core_mechanic": "Certify two named Mediterranean routes without flattening them.",
                    "player_agency_model": "The player chooses the active route.",
                    "risk_or_failure_branch": "A route can fail and require a retry.",
                    "uniqueness_notes": "Mediterranean routes are the historical interface.",
                    "primary_cadence_type": "route_certification",
                }
            ]
        },
    )
    if not any("tracked route set" in warning for warning in flattening_warnings):
        raise AssertionError(f"flattened route fixture did not warn: {flattening_warnings}")

    many_named_routes_without_projection = high_fidelity_design_entry()
    many_named_routes_without_projection["design_ir"]["tracked_entity_sets"][0]["entities"] = [
        {"key": f"route_{idx}"} for idx in range(1, 7)
    ]
    many_named_routes_without_projection["design_ir"]["projection_notes"] = ""
    named_route_warnings = anti_flattening_warnings_for_payload(
        {"unique_wonders": [many_named_routes_without_projection]},
        design_matrix={"unique_wonders": []},
    )
    if not any("6 named entities" in warning and "projection strategy" in warning for warning in named_route_warnings):
        raise AssertionError(f"many named routes fixture did not warn: {named_route_warnings}")

    repeated_rows_without_projection = high_fidelity_design_entry()
    repeated_rows_without_projection["design_ir"]["projection_notes"] = "Manual note preserves the high-fidelity idea."
    repeated_rows_warnings = anti_flattening_warnings_for_payload(
        {"unique_wonders": [repeated_rows_without_projection]},
        design_matrix={"unique_wonders": []},
    )
    if not any("row/status projection" in warning for warning in repeated_rows_warnings):
        raise AssertionError(f"repeated rows fixture did not warn: {repeated_rows_warnings}")

    public_debt_without_projection = high_fidelity_design_entry()
    public_debt_without_projection["design_ir"]["tracked_entity_sets"][0] = {
        "key": "public_debt_pledges",
        "entity_type": "debt_pledge",
        "entities": [{"key": f"pledge_{idx}"} for idx in range(1, 7)],
        "state_values": ["open", "honored", "defaulted"],
        "per_entity_state": {"status_variable_pattern": "tv_wonder_test_pledge_<pledge>_status"},
        "selector": "The player selects which pledge backs the founding bargain.",
        "ui_binding": "incident_log:public_debt_pledges renders pledge risk state.",
    }
    public_debt_without_projection["design_ir"]["ui_feedback_model"] = {
        "components": ["incident_log", "checklist"],
        "per_entity_status": "Each public debt pledge has a separate risk status.",
    }
    public_debt_without_projection["design_ir"]["projection_notes"] = ""
    public_debt_warnings = anti_flattening_warnings_for_payload(
        {"unique_wonders": [public_debt_without_projection]},
        design_matrix={"unique_wonders": []},
    )
    if not any("6 named entities" in warning for warning in public_debt_warnings):
        raise AssertionError(f"public debt fixture did not warn on named entities: {public_debt_warnings}")

    occupied_event_id = valid_entry()
    assert_has_error(
        "occupied event id",
        occupied_event_id,
        "collides with an occupied Engineering Department event id",
        occupied_event_ids={1002},
    )

    edge_missing_node = valid_entry()
    edge_missing_node["node_graph"]["edges"][0]["to"] = "missing"
    assert_has_error("edge missing node", edge_missing_node, "edge to references undeclared node missing")

    missing_entry_node = valid_entry()
    missing_entry_node["node_graph"]["entry_node"] = "missing"
    assert_has_error("missing entry node", missing_entry_node, "entry_node references undeclared node missing")

    missing_terminal_node = valid_entry()
    missing_terminal_node["node_graph"]["terminal_nodes"] = ["missing"]
    assert_has_error(
        "missing terminal node",
        missing_terminal_node,
        "terminal_nodes references undeclared node missing",
    )

    unreachable = valid_entry()
    unreachable["event_ids"].append({"id": 1007, "key": "stray"})
    unreachable["node_graph"]["variables"][0]["reader_nodes"].append("stray")
    unreachable["node_graph"]["nodes"].append(
        node("stray", 1007, reads=["tv_wonder_test_stage"], next_nodes=["reward"])
    )
    unreachable["localization"]["event_keys"].append(event_row(1007, "stray"))
    unreachable_loc = loc()
    unreachable_loc["event.1007.t"] = "Title 1007"
    unreachable_loc["event.1007.d"] = unreachable_loc["event.1001.d"]
    unreachable_loc["event.1007.a"] = "Continue"
    unreachable_loc["node.stray.label"] = "stray"
    assert_has_error("unreachable node", unreachable, "node stray is unreachable", localization=unreachable_loc)

    non_terminal_dead_end = valid_entry()
    non_terminal_dead_end["node_graph"]["nodes"][4]["next_nodes"] = []
    non_terminal_dead_end["node_graph"]["edges"] = [
        edge for edge in non_terminal_dead_end["node_graph"]["edges"] if edge["from"] != "final_prep"
    ]
    assert_has_error("non-terminal dead end", non_terminal_dead_end, "non-terminal node final_prep has no next_nodes")

    retry_to_terminal = valid_entry()
    retry_to_terminal["node_graph"]["nodes"][3]["retry_target"] = "reward"
    assert_has_error("retry target terminal", retry_to_terminal, "retry_target must not point to terminal node reward")

    monthly_without_progress = valid_entry()
    monthly_without_progress["node_graph"]["nodes"][2]["reads"] = ["tv_wonder_test_stage"]
    monthly_without_progress["node_graph"]["nodes"][2]["writes"] = ["tv_wonder_test_stage"]
    monthly_without_progress["node_graph"]["variables"][0]["writer_nodes"].append("monthly_gate")
    monthly_without_progress["node_graph"]["variables"][1]["writer_nodes"] = []
    monthly_without_progress["node_graph"]["variables"][1]["reader_nodes"] = ["retry_choice", "final_prep"]
    assert_has_error(
        "monthly gate no progress variable",
        monthly_without_progress,
        "monthly_progress_gate node monthly_gate must read and write at least one progress/count variable",
    )

    final_reward_not_terminal = valid_entry()
    final_reward_not_terminal["node_graph"]["terminal_nodes"] = ["final_prep"]
    assert_has_error(
        "final reward not terminal",
        final_reward_not_terminal,
        "final_reward_dispatch node reward must be listed in node_graph.terminal_nodes",
    )

    node_undeclared_read = valid_entry()
    node_undeclared_read["node_graph"]["nodes"][0]["reads"] = ["tv_wonder_test_missing"]
    assert_has_error("node undeclared read", node_undeclared_read, "reads undeclared variable tv_wonder_test_missing")

    binding_undeclared_variable = valid_entry()
    binding_undeclared_variable["ui_model"]["bindings"][0]["variable_refs"].append("tv_wonder_test_missing")
    assert_has_error(
        "binding undeclared variable",
        binding_undeclared_variable,
        "ui binding progress_binding references undeclared variable tv_wonder_test_missing",
    )

    missing_retry_target = valid_entry()
    missing_retry_target["node_graph"]["nodes"][3]["retry_target"] = "missing"
    assert_has_error("missing retry target", missing_retry_target, "retry_target references undeclared node missing")

    harness_generated_without_targets = valid_entry()
    harness_generated_without_targets["identity"]["status"] = "harness_generated"
    harness_generated_without_targets["generation"]["target_files"] = []
    assert_has_error(
        "harness generated target files",
        harness_generated_without_targets,
        "harness_generated must declare generation.target_files",
    )

    unsupported_node_kind = valid_entry()
    unsupported_node_kind["node_graph"]["nodes"][0]["kind"] = "unsupported_node"
    assert_has_error("unsupported node kind", unsupported_node_kind, "unsupported kind 'unsupported_node'")

    unknown_capability = valid_entry()
    unknown_capability["node_graph"]["nodes"][0]["capabilities"] = ["unknown_capability"]
    assert_has_error("unknown capability", unknown_capability, "unknown capability 'unknown_capability'")

    unsupported_capability_kind = valid_entry()
    unsupported_capability_kind["node_graph"]["nodes"][0]["capabilities"] = ["resource_gate"]
    assert_has_error(
        "capability unsupported node kind",
        unsupported_capability_kind,
        "capability 'resource_gate' does not support node kind 'event'",
    )

    missing_signature = valid_entry()
    del missing_signature["node_graph"]["mechanic_signature"]
    assert_has_error(
        "missing mechanic signature",
        missing_signature,
        "node_graph.mechanic_signature is required",
    )
    assert_codegen_error(
        "codegen missing mechanic signature",
        missing_signature,
        "node_graph.mechanic_signature is required",
    )

    thin_signature = valid_entry()
    thin_signature["node_graph"]["mechanic_signature"]["core_interaction_loop"] = "Too short."
    assert_has_error(
        "thin mechanic signature",
        thin_signature,
        "node_graph.mechanic_signature.core_interaction_loop is too thin",
    )

    monthly_without_cadence_rationale = valid_entry()
    monthly_without_cadence_rationale["node_graph"]["cadence_signature"]["cadence_rationale"] = ""
    assert_has_error(
        "monthly without cadence rationale",
        monthly_without_cadence_rationale,
        "node_graph.cadence_signature.cadence_rationale is required",
    )

    monthly_institutionalization_without_non_monthly = valid_entry()
    monthly_institutionalization_without_non_monthly["node_graph"]["cadence_signature"]["cadence_type"] = (
        "monthly_institutionalization"
    )
    monthly_institutionalization_without_non_monthly["node_graph"]["cadence_signature"]["cadence_rationale"] = (
        "Monthly institutionalization fits this test beacon because recurring harbor watch certification is historically central."
    )
    monthly_institutionalization_without_non_monthly["node_graph"]["cadence_signature"]["non_monthly_triggers_or_reason"] = (
        "None; the ritual is a pure monthly progress bar for twelve months."
    )
    assert_has_error(
        "monthly institutionalization no non-monthly interaction",
        monthly_institutionalization_without_non_monthly,
        "monthly_institutionalization requires non_monthly_triggers_or_reason",
    )

    unknown_cadence_type = valid_entry()
    unknown_cadence_type["node_graph"]["cadence_signature"]["cadence_type"] = "annual_cycle"
    assert_has_error(
        "unknown cadence type",
        unknown_cadence_type,
        "node_graph.cadence_signature.cadence_type unknown cadence type 'annual_cycle'",
    )

    custom_archetype_missing_statement = valid_entry()
    custom_archetype_missing_statement["node_graph"]["archetypes"] = ["custom_beacon_unregistered_shape"]
    assert_has_error(
        "custom archetype missing statement",
        custom_archetype_missing_statement,
        "custom archetype(s) require node_graph.mechanic_signature.custom_archetype_statement",
    )

    unknown_archetype = valid_entry()
    unknown_archetype["node_graph"]["archetypes"] = ["unknown_archetype"]
    assert_has_error(
        "unknown archetype",
        unknown_archetype,
        "node_graph.archetypes unknown archetype 'unknown_archetype'",
    )

    unknown_stub_archetype = valid_entry()
    unknown_stub_archetype["identity"]["status"] = "stub"
    unknown_stub_archetype["node_graph"]["archetypes"] = ["unknown_archetype"]
    assert_has_error(
        "unknown stub archetype",
        unknown_stub_archetype,
        "node_graph.archetypes unknown archetype 'unknown_archetype'",
    )

    bad_archetype_registry = {"metadata": {"generated_game_code": False}, "archetypes": "bad"}
    assert_has_error(
        "bad archetype registry",
        valid_entry(),
        "archetype registry archetypes must be a list",
        archetype_registry=bad_archetype_registry,
    )

    registry_may_write_src = deepcopy(load_archetype_registry())
    registry_may_write_src["archetypes"][0]["may_write_src"] = True
    assert_has_error(
        "archetype registry may write src",
        valid_entry(),
        "must declare may_write_src: false",
        archetype_registry=registry_may_write_src,
    )

    public_credit_writable_archetype_registry = deepcopy(load_archetype_registry())
    for archetype in public_credit_writable_archetype_registry["archetypes"]:
        if archetype.get("key") == "public_credit_charter_retry":
            archetype["may_write_src"] = True
            break
    assert_has_error(
        "public credit archetype may_write_src",
        finance_public_credit_backend_entry(),
        "must declare may_write_src: false",
        archetype_registry=public_credit_writable_archetype_registry,
    )

    archetype_missing_capability = valid_entry()
    archetype_missing_capability["node_graph"]["archetypes"] = ["resource_accumulation_ritual"]
    assert_has_error(
        "archetype missing capability",
        archetype_missing_capability,
        "archetype 'resource_accumulation_ritual' missing required capability(s): resource_gate",
    )

    archetype_missing_role = valid_entry()
    archetype_missing_role["node_graph"]["variables"][1]["roles"] = []
    assert_has_error(
        "archetype missing variable role",
        archetype_missing_role,
        "archetype 'monthly_pressure_countdown' missing variable role 'progress_counter'",
    )

    archetype_missing_ui = valid_entry()
    archetype_missing_ui["ui_model"]["components"] = [
        {"type": "progress_track", "key": "progress", "value_variable": "tv_wonder_test_progress"}
    ]
    assert_has_error(
        "archetype missing ui component",
        archetype_missing_ui,
        "archetype 'monthly_pressure_countdown' missing ui component(s): checklist",
    )

    archetype_missing_listener = valid_entry()
    archetype_missing_listener["node_graph"]["listeners"] = []
    assert_has_error(
        "archetype missing listener",
        archetype_missing_listener,
        "archetype 'monthly_pressure_countdown' missing listener(s): monthly",
    )

    registry_min_nodes = deepcopy(load_archetype_registry())
    for archetype in registry_min_nodes["archetypes"]:
        if archetype["key"] == "monthly_pressure_countdown":
            archetype["min_nodes"] = 7
    assert_has_error(
        "archetype min nodes",
        valid_entry(),
        "archetype 'monthly_pressure_countdown' requires at least 7 node(s)",
        archetype_registry=registry_min_nodes,
    )

    registry_max_nodes = deepcopy(load_archetype_registry())
    for archetype in registry_max_nodes["archetypes"]:
        if archetype["key"] == "monthly_pressure_countdown":
            archetype["max_nodes"] = 5
    assert_has_error(
        "archetype max nodes",
        valid_entry(),
        "archetype 'monthly_pressure_countdown' allows at most 5 node(s)",
        archetype_registry=registry_max_nodes,
    )

    archetype_missing_retry = valid_entry()
    archetype_missing_retry["node_graph"]["nodes"][3]["failure_or_retry"] = False
    archetype_missing_retry["node_graph"]["nodes"][3]["retry_target"] = None
    assert_has_error(
        "archetype missing retry path",
        archetype_missing_retry,
        "archetype 'monthly_pressure_countdown' requires a retry path",
    )

    archetype_missing_hidden = valid_entry()
    archetype_missing_hidden["node_graph"]["archetypes"] = [
        "monthly_pressure_countdown",
        "hidden_executor_finalization",
    ]
    assert_has_error(
        "archetype missing hidden handoff",
        archetype_missing_hidden,
        "archetype 'hidden_executor_finalization' requires a hidden executor handoff",
    )

    terminal_missing_capability = valid_entry()
    terminal_missing_capability["node_graph"]["nodes"][5]["capabilities"] = ["event_chain"]
    assert_has_error(
        "archetype terminal missing capability",
        terminal_missing_capability,
        "terminal node reward must declare capability 'final_reward_handoff'",
    )

    missing_listener_contract = resource_listener_hidden_entry()
    del missing_listener_contract["node_graph"]["nodes"][4]["listener_contract"]
    assert_has_error(
        "listener gate missing listener contract",
        missing_listener_contract,
        "listener_gate node final_prep must declare listener_contract",
    )

    unsupported_listener_contract = resource_listener_hidden_entry()
    unsupported_listener_contract["node_graph"]["nodes"][4]["listener_contract"]["listener"] = "ruler_birth"
    assert_has_error(
        "listener contract unsupported listener",
        unsupported_listener_contract,
        "listener_contract uses unsupported listener 'ruler_birth'",
    )

    unknown_scope = actor_assignment_entry()
    unknown_scope["node_graph"]["nodes"][1]["scope_contract"]["root_scope"] = "province"
    assert_has_error(
        "scope contract unknown scope",
        unknown_scope,
        "scope_contract.root_scope has unknown scope 'province'",
    )

    unsafe_without_handoff = resource_listener_hidden_entry()
    unsafe_without_handoff["node_graph"]["nodes"][4].pop("hidden_executor_handoff")
    assert_has_error(
        "unsafe pre eval no handoff",
        unsafe_without_handoff,
        "scope_contract.unsafe_pre_eval=true requires blocked_reason or hidden_executor_handoff",
    )

    tooltip_unsafe_output = actor_assignment_entry()
    tooltip_unsafe_output["node_graph"]["nodes"][1]["scope_contract"]["tooltip_safe"] = False
    tooltip_unsafe_output["node_graph"]["nodes"][1]["output_kinds"] = ["player_facing_tooltip"]
    assert_has_error(
        "tooltip unsafe output",
        tooltip_unsafe_output,
        "tooltip_safe=false cannot output player_facing_tooltip",
    )

    missing_required_capability_field = actor_assignment_entry()
    del missing_required_capability_field["node_graph"]["nodes"][1]["scope_contract"]
    assert_has_error(
        "required capability field missing",
        missing_required_capability_field,
        "capability 'actor_assignment' missing required field node.scope_contract",
    )

    unsupported_action_kind = valid_entry()
    unsupported_action_kind["node_graph"]["actions"][0]["kind"] = "unsupported_action"
    assert_has_error("unsupported action kind", unsupported_action_kind, "unsupported kind 'unsupported_action'")

    unsupported_check_kind = valid_entry()
    unsupported_check_kind["node_graph"]["checks"][0]["kind"] = "unsupported_check"
    assert_has_error("unsupported check kind", unsupported_check_kind, "unsupported kind 'unsupported_check'")

    registry_missing_template = deepcopy(load_template_registry())
    registry_missing_template["templates"] = [
        template
        for template in registry_missing_template["templates"]
        if template["key"] != "final_reward_dispatch_stub"
    ]
    assert_has_error(
        "registry missing template",
        valid_entry(),
        "unknown template 'final_reward_dispatch_stub'",
        template_registry=registry_missing_template,
    )
    assert_codegen_error(
        "codegen registry missing template",
        valid_entry(),
        "unknown template(s): final_reward_dispatch_stub",
        template_registry=registry_missing_template,
    )

    registry_unsupported_kind = deepcopy(load_template_registry())
    for template in registry_unsupported_kind["templates"]:
        if template["key"] == "sequential_event_chain":
            template["supported_action_kinds"] = []
    assert_has_error(
        "registry unsupported action kind",
        valid_entry(),
        "action start_chain template 'sequential_event_chain' does not support kind 'generator_template'",
        template_registry=registry_unsupported_kind,
    )

    unverified = valid_entry()
    unverified["implementation_notes"]["needs_verification"] = ["modifier_key"]
    assert_has_error("unverified implementation", unverified, "unverified implementation note")

    unverified_token = valid_entry()
    unverified_token["generation"]["dry_run_notes"] = "needs_verification"
    assert_has_error("needs verification token", unverified_token, "cannot contain needs_verification")

    explicit_stub = valid_entry()
    explicit_stub["identity"]["status"] = "stub"
    assert_codegen_error("explicit stub codegen", explicit_stub, "cannot be generated by Harness codegen")

    print("[OK] Unique wonder ritual Harness quality-gate tests passed.")


if __name__ == "__main__":
    main()
