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
    audit_summary,
    list_index,
    load_unique_wonders,
    load_capability_registry,
    load_spec_data,
    load_template_registry,
    loc_english,
    validate_capability_registry,
    validate_spec_payload,
)
from wonder_unique_ritual_harness import load_archetype_registry  # noqa: E402
from wonder_unique_ritual_harness import anti_flattening_warnings_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_preflight_for_entry  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_preflight_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_source_plan_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_source_preview_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_source_bundle_preview_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_source_writer_readiness_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_source_body_candidate_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_source_file_preview_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_source_file_validation_evidence_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_source_generator_contract_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_event_source_generator_interface_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_scripted_trigger_source_generator_interface_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_gui_source_generator_interface_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_listener_source_generator_interface_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_localization_source_generator_interface_for_payload  # noqa: E402
from wonder_unique_ritual_harness import repeated_entity_row_alhambra_source_generator_interface_bundle_gate_for_payload  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_source_plan  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_source_preview  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_source_bundle_preview  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_source_writer_readiness  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_source_body_candidate  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_source_file_preview  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_source_file_validation_evidence  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_source_generator_contract  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_event_source_generator_interface  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_scripted_trigger_source_generator_interface  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_gui_source_generator_interface  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_listener_source_generator_interface  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_localization_source_generator_interface  # noqa: E402
from wonder_unique_ritual_harness import validate_repeated_entity_row_alhambra_source_generator_interface_bundle_gate  # noqa: E402


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
    "pilgrimage_route_certification_backend",
    "overland_relay_route_certification_backend",
    "maritime_trade_route_certification_backend",
    "branch_specific_reward_scaling",
    "finance_public_credit_interface_backend",
    "bounded_opposition_religious_community_pressure",
    "auxiliary_building_completion_listener_backend",
    "water_management_restoration_completion_backend",
]
REPEATED_ROW_PILOTS = {
    "unique_dome_of_the_rock": {
        "row_sets": {"sanctuary_access_groups", "custody_duties"},
        "ui": {"checklist", "incident_log"},
        "blockers": {
            "missing_cleanup",
            "missing_effect_writer",
            "missing_event_ownership",
            "missing_gui_rows",
            "missing_loc_rows",
            "missing_trigger_check",
        },
    },
    "unique_alhambra": {
        "row_sets": {"treaty_clause_register", "palace_risk_points"},
        "ui": {"checklist", "incident_log"},
        "blockers": {
            "missing_cleanup",
            "missing_effect_writer",
            "missing_event_ownership",
            "missing_gui_rows",
            "missing_listener_integration",
            "missing_loc_rows",
            "missing_trigger_check",
        },
    },
    "unique_st_peters_basilica": {
        "row_sets": {"sacred_official_candidates", "apostolic_service_duties"},
        "ui": {"actor_slots", "checklist", "incident_log"},
        "blockers": {
            "missing_cleanup",
            "missing_effect_writer",
            "missing_event_ownership",
            "missing_gui_rows",
            "missing_loc_rows",
            "missing_trigger_check",
        },
    },
    "unique_bank_of_saint_george": {
        "row_sets": {"charter_options", "public_credit_pledges"},
        "ui": {"checklist", "incident_log"},
        "blockers": {
            "missing_cleanup",
            "missing_effect_writer",
            "missing_event_ownership",
            "missing_gui_rows",
            "missing_loc_rows",
            "missing_trigger_check",
        },
    },
}
REPEATED_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS = {
    "scripted_effect_row_init",
    "scripted_effect_row_state_write",
    "scripted_effect_aggregate_refresh",
    "scripted_effect_branch_write",
    "scripted_effect_cleanup_write",
    "cleanup_completion",
    "cleanup_failure",
    "cleanup_ownership_loss",
    "cleanup_ritual_reset",
}
REPEATED_ROW_EFFECT_ARTIFACT_KINDS = {
    "scripted_effect_row_init",
    "scripted_effect_row_state_write",
    "scripted_effect_aggregate_refresh",
    "scripted_effect_branch_write",
    "scripted_effect_cleanup_write",
}
REPEATED_ROW_CLEANUP_ARTIFACT_KINDS = {
    "cleanup_completion",
    "cleanup_failure",
    "cleanup_ownership_loss",
    "cleanup_ritual_reset",
}
REPEATED_ROW_TRIGGER_ARTIFACT_KINDS = {
    "scripted_trigger_eligibility",
    "scripted_trigger_row_completion",
    "scripted_trigger_tooltip_safe_condition_group",
}
REPEATED_ROW_EVENT_ARTIFACT_KINDS = {
    "event_opening_skeleton",
    "event_update_skeleton",
    "event_retry_skeleton",
    "event_resolve_skeleton",
}
REPEATED_ROW_GUI_ARTIFACT_KINDS = {
    "gui_actor_slots_row",
    "gui_checklist_row",
    "gui_incident_log_row",
}
REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS = {
    "localization_row_labels",
    "localization_status_text",
    "localization_incident_text",
    "localization_tooltips",
    "localization_summary_text",
}
REPEATED_ROW_LISTENER_ARTIFACT_KINDS = {"listener_war_integration"}
REPEATED_ROW_LISTENER_EVIDENCE_PATHS = {
    "data/pulse_registry.yaml:112-117",
    "scripts/in_game/common/on_action/gen_tv_pulse_registry.py:47-48",
    "src/in_game/common/on_action/tv_pulse_bridges.txt:170-181",
    "src/in_game/common/on_action/tv_engineering_department_on_action.txt:270-293",
    "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt:30311",
    "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt:30317",
    "data/unique_wonder_ritual_specs.yaml:3231-3243",
}
REPEATED_ROW_STRUCTURED_EVIDENCE_ARTIFACT_KINDS = (
    REPEATED_ROW_EVENT_ARTIFACT_KINDS
    | REPEATED_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS
    | REPEATED_ROW_TRIGGER_ARTIFACT_KINDS
    | REPEATED_ROW_GUI_ARTIFACT_KINDS
    | REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS
    | REPEATED_ROW_LISTENER_ARTIFACT_KINDS
)
REPEATED_ROW_EVIDENCE_MAPPING_FIELDS = {
    "artifact_kind",
    "eu5_source_syntax_pattern",
    "evidence_source_paths",
    "generator_candidate",
    "generator_missing_reason",
    "source_target_boundary",
    "blocks_source_writer",
}
REPEATED_ROW_EVENT_CONTRACT_ALLOWED_STATUSES = {"no-write", "candidate", "blocked"}
REPEATED_ROW_EVENT_CONTRACT_REQUIRED_VALIDATIONS = {
    "event_id_uniqueness_collision",
    "localization_key_linkage",
    "node_event_id_linkage",
    "source_target_boundary_still_blocked",
}
REPEATED_ROW_EVENT_CONTRACT_BLOCKER_REASONS = {
    "missing real event source generator",
    "missing effect writer",
    "missing trigger writer",
    "missing GUI writer",
    "missing localization writer",
    "no verified source write contract",
}
REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_REQUIRED_VALIDATIONS = {
    "effect_name_uniqueness",
    "variable_writer_reader_linkage",
    "row_set_entity_coverage",
    "aggregate_projection_boundary",
    "cleanup_coverage",
    "source_target_boundary_still_blocked",
}
REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_BLOCKER_REASONS = {
    "missing real scripted-effect source generator",
    "missing row-state write schema",
    "missing trigger validation",
    "missing GUI/localization writers",
    "no verified source write contract",
}
REPEATED_ROW_TRIGGER_CONTRACT_REQUIRED_VALIDATIONS = {
    "trigger_name_uniqueness",
    "row_completion_variable_linkage",
    "eligibility_input_coverage",
    "tooltip_safe_scope_boundary",
    "source_target_boundary_still_blocked",
}
REPEATED_ROW_TRIGGER_CONTRACT_BLOCKER_REASONS = {
    "missing real scripted-trigger source generator",
    "missing trigger predicate schema",
    "missing effect writer validation",
    "missing GUI/localization coverage",
    "no verified source write contract",
}
REPEATED_ROW_GUI_CONTRACT_REQUIRED_VALIDATIONS = {
    "fixed_row_widget_boundary",
    "per_row_variable_binding",
    "actor_checklist_incident_row_policy",
    "tooltip_key_linkage",
    "aggregate_projection_boundary",
    "source_target_boundary_still_blocked",
}
REPEATED_ROW_GUI_CONTRACT_BLOCKER_REASONS = {
    "missing real GUI source generator",
    "missing EU5 GUI exact syntax/source writer contract",
    "missing source-target boundary validation",
}
REPEATED_ROW_LOCALIZATION_CONTRACT_REQUIRED_VALIDATIONS = {
    "english_simplified_chinese_coverage",
    "loc_key_namespace",
    "loc_line_escaping_bom",
    "row_status_incident_tooltip_summary_coverage",
    "gui_event_key_linkage",
    "source_target_boundary_still_blocked",
}
REPEATED_ROW_LOCALIZATION_CONTRACT_BLOCKER_REASONS = {
    "missing real localization source generator",
    "missing EU5 localization exact syntax/source writer contract",
    "missing source-target boundary validation",
}
REPEATED_ROW_LISTENER_CONTRACT_REQUIRED_VALIDATIONS = {
    "on_action_hook_linkage",
    "listener_scope_availability",
    "selected_ritual_trigger_linkage",
    "row_state_handoff_boundary",
    "source_target_boundary_still_blocked",
}
REPEATED_ROW_LISTENER_CONTRACT_BLOCKER_REASONS = {
    "missing real listener integration source generator",
    "missing war scope persistence contract",
    "missing Alhambra row-state write contract",
    "no verified source write contract",
}
REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_CLEANUP_SCOPES = {
    "scripted_effect_row_init": "non_cleanup_effect",
    "scripted_effect_row_state_write": "non_cleanup_effect",
    "scripted_effect_aggregate_refresh": "non_cleanup_effect",
    "scripted_effect_branch_write": "non_cleanup_effect",
    "scripted_effect_cleanup_write": "effect_cleanup_write",
    "cleanup_completion": "completion",
    "cleanup_failure": "failure",
    "cleanup_ownership_loss": "ownership_loss",
    "cleanup_ritual_reset": "reset",
}
PILGRIMAGE_ROUTE_BACKEND_OUTPUTS = {
    "markdown_fragment",
    "trigger_stub",
    "effect_stub",
    "gui_summary",
    "player_facing_tooltip",
}
OVERLAND_RELAY_BACKEND_OUTPUTS = {
    "markdown_fragment",
    "trigger_stub",
    "effect_stub",
    "gui_summary",
    "player_facing_tooltip",
}
MARITIME_TRADE_BACKEND_OUTPUTS = {
    "markdown_fragment",
    "trigger_stub",
    "effect_stub",
    "gui_summary",
    "player_facing_tooltip",
}
WATER_MANAGEMENT_BACKEND_OUTPUTS = {
    "markdown_fragment",
    "trigger_stub",
    "effect_stub",
    "gui_summary",
    "player_facing_tooltip",
}
NEW_JERUSALEM_ARCHETYPE_CAPABILITIES = {
    "event_chain",
    "route_gate",
    "resource_gate",
    "retry_branch",
    "final_reward_handoff",
    "pilgrimage_route_certification_backend",
}
OVERLAND_RELAY_ARCHETYPE_CAPABILITIES = {
    "event_chain",
    "route_gate",
    "retry_branch",
    "final_reward_handoff",
    "overland_relay_route_certification_backend",
}
MARITIME_TRADE_ARCHETYPE_CAPABILITIES = {
    "event_chain",
    "route_gate",
    "retry_branch",
    "final_reward_handoff",
    "maritime_trade_route_certification_backend",
}
POLDER_ARCHETYPE_CAPABILITIES = {
    "event_chain",
    "retry_branch",
    "resource_gate",
    "branch_specific_reward_scaling",
    "repeated_entity_row_checklist_incident_log_backend",
    "water_management_restoration_completion_backend",
    "final_reward_handoff",
}


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


def pilgrimage_route_certification_backend_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["new_jerusalem_rock_route"]
    graph["listeners"] = []
    graph["cadence_signature"] = {
        "cadence_type": "route_certification",
        "cadence_rationale": "The fixture resolves by certifying a named pilgrimage route, checking offerings at waypoints, resolving a broken-link incident, and handing the proof to the final reward path instead of waiting on a calendar tick.",
        "player_agency_model": "The player opens the route, supplies the waypoint offerings, chooses whether to repair a broken pilgrim link or accept a local-only fallback, and then commits the final recognition proof.",
        "non_monthly_triggers_or_reason": "Non-monthly validation comes from the route gate, the offering/resource gate, the incident retry branch, and the final reward handoff.",
        "pacing_failure_mode": "The pacing fails if pilgrimage certification becomes a single anonymous event, so route state, offering state, incident state, and recognition proof stay separate.",
    }
    graph["variables"] = [
        {
            "name": "tv_wonder_test_stage",
            "scope": "country",
            "type": "number",
            "roles": ["stage_state"],
            "initial_value": 0,
            "writer_nodes": ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
            "reader_nodes": ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_route",
            "scope": "country",
            "type": "number",
            "roles": ["route_state"],
            "initial_value": 0,
            "writer_nodes": ["materials", "retry_choice"],
            "reader_nodes": ["materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_offering",
            "scope": "country",
            "type": "number",
            "roles": ["resource_state"],
            "initial_value": 0,
            "writer_nodes": ["monthly_gate", "retry_choice"],
            "reader_nodes": ["monthly_gate", "retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_incident",
            "scope": "country",
            "type": "number",
            "roles": ["incident_state"],
            "initial_value": 0,
            "writer_nodes": ["retry_choice"],
            "reader_nodes": ["retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_reward",
            "scope": "country",
            "type": "number",
            "roles": ["reward_state"],
            "initial_value": 0,
            "writer_nodes": ["final_prep", "reward"],
            "reader_nodes": ["final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
    ]
    graph["nodes"][0]["reads"] = ["tv_wonder_test_stage"]
    graph["nodes"][0]["writes"] = ["tv_wonder_test_stage"]
    graph["nodes"][0]["ui_state"] = {"variable_refs": ["tv_wonder_test_stage"]}
    graph["nodes"][1]["kind"] = "route_gate"
    graph["nodes"][1]["capabilities"] = ["route_gate", "pilgrimage_route_certification_backend"]
    graph["nodes"][1]["reads"] = ["tv_wonder_test_stage", "tv_wonder_test_route"]
    graph["nodes"][1]["writes"] = ["tv_wonder_test_stage", "tv_wonder_test_route"]
    graph["nodes"][1]["ui_state"] = {"variable_refs": ["tv_wonder_test_route"]}
    graph["nodes"][1]["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["nodes"][2]["kind"] = "resource_gate"
    graph["nodes"][2]["capabilities"] = ["resource_gate", "pilgrimage_route_certification_backend"]
    graph["nodes"][2]["reads"] = ["tv_wonder_test_stage", "tv_wonder_test_route", "tv_wonder_test_offering"]
    graph["nodes"][2]["writes"] = ["tv_wonder_test_stage", "tv_wonder_test_offering"]
    graph["nodes"][2]["ui_state"] = {"variable_refs": ["tv_wonder_test_route", "tv_wonder_test_offering"]}
    graph["nodes"][2]["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["nodes"][3]["kind"] = "incident_event"
    graph["nodes"][3]["capabilities"] = ["event_chain", "retry_branch", "pilgrimage_route_certification_backend"]
    graph["nodes"][3]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_offering",
        "tv_wonder_test_incident",
    ]
    graph["nodes"][3]["writes"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_offering",
        "tv_wonder_test_incident",
    ]
    graph["nodes"][3]["ui_state"] = {
        "variable_refs": [
            "tv_wonder_test_route",
            "tv_wonder_test_offering",
            "tv_wonder_test_incident",
        ]
    }
    graph["nodes"][3]["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["nodes"][4]["kind"] = "choice_event"
    graph["nodes"][4]["capabilities"] = ["event_chain"]
    graph["nodes"][4]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_offering",
        "tv_wonder_test_incident",
        "tv_wonder_test_reward",
    ]
    graph["nodes"][4]["writes"] = ["tv_wonder_test_stage", "tv_wonder_test_reward"]
    graph["nodes"][4]["ui_state"] = {"variable_refs": ["tv_wonder_test_reward"]}
    graph["nodes"][5]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_offering",
        "tv_wonder_test_incident",
        "tv_wonder_test_reward",
    ]
    graph["nodes"][5]["writes"] = ["tv_wonder_test_stage", "tv_wonder_test_reward"]
    graph["nodes"][5]["ui_state"] = {"variable_refs": ["tv_wonder_test_reward"]}
    graph["actions"][2]["generator_template"] = "semantic_contract_fragment"
    graph["checks"][1]["generator_template"] = "semantic_contract_fragment"
    entry["generation"]["verified_templates"] = NON_MONTHLY_TEMPLATES
    entry["ui_model"] = {
        "components": [
            {"type": "route_map", "key": "route", "value_variable": "tv_wonder_test_route"},
            {"type": "incident_log", "key": "incident", "status_variable": "tv_wonder_test_incident"},
            {"type": "material_stockpile", "key": "offerings", "value_variable": "tv_wonder_test_offering"},
            {"type": "checklist", "key": "checklist", "status_variable": "tv_wonder_test_stage"},
        ],
        "bindings": [
            {
                "key": "route_binding",
                "component_key": "route",
                "variable_refs": [
                    "tv_wonder_test_route",
                    "tv_wonder_test_offering",
                    "tv_wonder_test_incident",
                    "tv_wonder_test_reward",
                ],
                "node_refs": ["materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
                "loc_refs": ["ui.progress.label"],
            }
        ],
    }
    return entry


def overland_relay_route_certification_backend_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["overland_relay_route_proof"]
    graph["listeners"] = []
    graph["cadence_signature"] = {
        "cadence_type": "route_certification",
        "cadence_rationale": "The fixture resolves by certifying named overland road segments, tambos, rope-bridge checkpoints, runner message handoffs, route incidents, and final reward handoff rather than waiting on a calendar tick.",
        "player_agency_model": "The player qualifies the endpoint and road segment, resolves bridge, supply, runner-delay, or awkward-route incidents, and chooses reroute or domestic-only fallback before reward dispatch.",
        "non_monthly_triggers_or_reason": "Non-monthly validation comes from the route gate, runner message handoff, incident retry branch, reroute choice, domestic-only fallback, and final reward handoff.",
        "pacing_failure_mode": "The pacing fails if relay certification becomes a generic route or pilgrimage counter, so road segment, relay message, incident, and reward branch state stay separate.",
    }
    graph["variables"] = [
        {
            "name": "tv_wonder_test_stage",
            "scope": "country",
            "type": "number",
            "roles": ["stage_state"],
            "initial_value": 0,
            "writer_nodes": ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
            "reader_nodes": ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_route",
            "scope": "country",
            "type": "number",
            "roles": ["route_state"],
            "initial_value": 0,
            "writer_nodes": ["materials", "monthly_gate", "retry_choice"],
            "reader_nodes": ["materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_relay_message",
            "scope": "country",
            "type": "number",
            "roles": ["relay_message_state"],
            "initial_value": 0,
            "writer_nodes": ["materials", "monthly_gate", "retry_choice"],
            "reader_nodes": ["materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_incident",
            "scope": "country",
            "type": "number",
            "roles": ["incident_state"],
            "initial_value": 0,
            "writer_nodes": ["retry_choice"],
            "reader_nodes": ["retry_choice", "final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_reward",
            "scope": "country",
            "type": "number",
            "roles": ["reward_state"],
            "initial_value": 0,
            "writer_nodes": ["final_prep", "reward"],
            "reader_nodes": ["final_prep", "reward"],
            "cleanup": "project_state_clear",
        },
    ]
    graph["nodes"][0]["reads"] = ["tv_wonder_test_stage"]
    graph["nodes"][0]["writes"] = ["tv_wonder_test_stage"]
    graph["nodes"][0]["ui_state"] = {"variable_refs": ["tv_wonder_test_stage"]}
    graph["nodes"][1]["kind"] = "route_gate"
    graph["nodes"][1]["capabilities"] = ["route_gate", "overland_relay_route_certification_backend"]
    graph["nodes"][1]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
    ]
    graph["nodes"][1]["writes"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
    ]
    graph["nodes"][1]["ui_state"] = {
        "variable_refs": ["tv_wonder_test_route", "tv_wonder_test_relay_message"]
    }
    graph["nodes"][1]["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["nodes"][2]["kind"] = "choice_event"
    graph["nodes"][2]["capabilities"] = ["event_chain", "overland_relay_route_certification_backend"]
    graph["nodes"][2]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
    ]
    graph["nodes"][2]["writes"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
    ]
    graph["nodes"][2]["ui_state"] = {
        "variable_refs": ["tv_wonder_test_route", "tv_wonder_test_relay_message"]
    }
    graph["nodes"][2]["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["nodes"][3]["kind"] = "incident_event"
    graph["nodes"][3]["capabilities"] = [
        "event_chain",
        "retry_branch",
        "overland_relay_route_certification_backend",
    ]
    graph["nodes"][3]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
        "tv_wonder_test_incident",
    ]
    graph["nodes"][3]["writes"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
        "tv_wonder_test_incident",
    ]
    graph["nodes"][3]["ui_state"] = {
        "variable_refs": [
            "tv_wonder_test_route",
            "tv_wonder_test_relay_message",
            "tv_wonder_test_incident",
        ]
    }
    graph["nodes"][3]["scope_contract"] = safe_scope_contract(target_scopes=["location"])
    graph["nodes"][4]["kind"] = "choice_event"
    graph["nodes"][4]["capabilities"] = ["event_chain"]
    graph["nodes"][4]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
        "tv_wonder_test_incident",
        "tv_wonder_test_reward",
    ]
    graph["nodes"][4]["writes"] = ["tv_wonder_test_stage", "tv_wonder_test_reward"]
    graph["nodes"][4]["ui_state"] = {"variable_refs": ["tv_wonder_test_reward"]}
    graph["nodes"][5]["reads"] = [
        "tv_wonder_test_stage",
        "tv_wonder_test_route",
        "tv_wonder_test_relay_message",
        "tv_wonder_test_incident",
        "tv_wonder_test_reward",
    ]
    graph["nodes"][5]["writes"] = ["tv_wonder_test_stage", "tv_wonder_test_reward"]
    graph["nodes"][5]["ui_state"] = {"variable_refs": ["tv_wonder_test_reward"]}
    graph["actions"][2]["generator_template"] = "semantic_contract_fragment"
    graph["checks"][1]["generator_template"] = "semantic_contract_fragment"
    entry["generation"]["verified_templates"] = NON_MONTHLY_TEMPLATES
    entry["ui_model"] = {
        "components": [
            {"type": "route_map", "key": "route", "value_variable": "tv_wonder_test_route"},
            {"type": "incident_log", "key": "incident", "status_variable": "tv_wonder_test_incident"},
        ],
        "bindings": [
            {
                "key": "route_binding",
                "component_key": "route",
                "variable_refs": [
                    "tv_wonder_test_route",
                    "tv_wonder_test_relay_message",
                    "tv_wonder_test_incident",
                    "tv_wonder_test_reward",
                ],
                "node_refs": ["materials", "monthly_gate", "retry_choice", "final_prep", "reward"],
                "loc_refs": ["ui.progress.label"],
            }
        ],
    }
    return entry


def maritime_trade_route_certification_backend_entry() -> dict:
    entry = valid_entry()
    graph = entry["node_graph"]
    graph["archetypes"] = ["maritime_trade_route_covenant"]
    graph["listeners"] = []
    graph["cadence_signature"] = {
        "cadence_type": "route_certification",
        "cadence_rationale": "The fixture resolves by certifying a named maritime monsoon endpoint, warehouse proof, translator and merchant-law compact, route incident branch, reroute or domestic fallback, and final reward handoff rather than waiting on a calendar tick.",
        "player_agency_model": "The player qualifies a monsoon route, proves warehouse custody and translated merchant law, resolves a blocked or unaffordable route, and chooses reroute or lower-prestige domestic certification before reward dispatch.",
        "non_monthly_triggers_or_reason": "Non-monthly validation comes from the route gate, warehouse certification choice, translator-law compact choice, route incident retry branch, domestic fallback branch, and final reward handoff.",
        "pacing_failure_mode": "The pacing fails if maritime certification becomes a generic route counter, so route endpoint, warehouse, translator-law, incident, and reward branch state stay separate.",
    }
    graph["mechanic_signature"] = {
        "wonder_specific_hook": "The fixture models Malacca-style port law by joining monsoon route timing, bonded warehouses, translators, shahbandars, and merchant judges into one maritime covenant proof.",
        "core_interaction_loop": "The player opens the covenant, certifies a route, seals warehouse proof, signs a translator-law compact, resolves a blocked route through reroute or domestic certification, and then hands the branch to rewards.",
        "player_decision_pattern": "Each decision weighs external merchant recognition against cost, delay, and domestic fallback: the player chooses whether a stronger reroute is worth more than a narrower local certificate.",
        "state_feedback_model": "The route_map shows endpoint status, the progress_track shows covenant stage, and the incident_log records warehouse trouble, translator-law disputes, reroute choice, and domestic certification.",
        "failure_or_tension_model": "A blocked, unaffordable, or diplomatically awkward route can loop back to route certification or continue as a lower-prestige domestic proof without pretending foreign merchants accepted the compact.",
        "reward_expression": "The full branch gives a foreign-recognized maritime covenant reward stub, while the domestic fallback still completes the handoff with lower prestige and narrower commercial recognition.",
        "reuse_risk_mitigation": "The fixture is not a pilgrimage, lighthouse visibility test, or overland relay; it depends on warehouses, translators, merchant law, and monsoon route economics.",
    }
    node_keys = list(NODE_KEYS)
    graph["variables"] = [
        {
            "name": "tv_wonder_test_stage",
            "scope": "country",
            "type": "number",
            "roles": ["stage_state"],
            "initial_value": 0,
            "writer_nodes": node_keys,
            "reader_nodes": node_keys,
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_route",
            "scope": "country",
            "type": "number",
            "roles": ["route_state"],
            "initial_value": 0,
            "writer_nodes": node_keys,
            "reader_nodes": node_keys,
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_warehouse",
            "scope": "country",
            "type": "number",
            "roles": ["warehouse_state"],
            "initial_value": 0,
            "writer_nodes": node_keys,
            "reader_nodes": node_keys,
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_translator_law",
            "scope": "country",
            "type": "number",
            "roles": ["translator_law_state"],
            "initial_value": 0,
            "writer_nodes": node_keys,
            "reader_nodes": node_keys,
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_incident",
            "scope": "country",
            "type": "number",
            "roles": ["incident_state"],
            "initial_value": 0,
            "writer_nodes": node_keys,
            "reader_nodes": node_keys,
            "cleanup": "project_state_clear",
        },
        {
            "name": "tv_wonder_test_reward",
            "scope": "country",
            "type": "number",
            "roles": ["reward_state"],
            "initial_value": 0,
            "writer_nodes": node_keys,
            "reader_nodes": node_keys,
            "cleanup": "project_state_clear",
        },
    ]
    all_variables = [variable["name"] for variable in graph["variables"]]
    for test_node in graph["nodes"]:
        test_node["reads"] = list(all_variables)
        test_node["writes"] = list(all_variables)
        test_node["ui_state"] = {"variable_refs": list(all_variables)}
        test_node["scope_contract"] = safe_scope_contract(target_scopes=["location"])

    graph["nodes"][0]["kind"] = "choice_event"
    graph["nodes"][0]["capabilities"] = ["event_chain", "maritime_trade_route_certification_backend"]
    graph["nodes"][1]["kind"] = "route_gate"
    graph["nodes"][1]["capabilities"] = ["route_gate", "maritime_trade_route_certification_backend"]
    graph["nodes"][2]["kind"] = "choice_event"
    graph["nodes"][2]["capabilities"] = ["event_chain", "maritime_trade_route_certification_backend"]
    graph["nodes"][3]["kind"] = "incident_event"
    graph["nodes"][3]["capabilities"] = [
        "event_chain",
        "retry_branch",
        "maritime_trade_route_certification_backend",
    ]
    graph["nodes"][4]["kind"] = "choice_event"
    graph["nodes"][4]["capabilities"] = ["event_chain", "maritime_trade_route_certification_backend"]
    graph["nodes"][5]["kind"] = "final_reward_dispatch"
    graph["nodes"][5]["capabilities"] = ["final_reward_handoff", "maritime_trade_route_certification_backend"]
    graph["actions"][2]["generator_template"] = "semantic_contract_fragment"
    graph["checks"][1]["generator_template"] = "semantic_contract_fragment"
    entry["generation"]["verified_templates"] = NON_MONTHLY_TEMPLATES
    entry["ui_model"] = {
        "components": [
            {"type": "route_map", "key": "route", "value_variable": "tv_wonder_test_route"},
            {"type": "progress_track", "key": "progress", "value_variable": "tv_wonder_test_stage"},
            {"type": "incident_log", "key": "incident", "status_variable": "tv_wonder_test_incident"},
        ],
        "bindings": [
            {
                "key": "maritime_route_binding",
                "component_key": "route",
                "variable_refs": list(all_variables),
                "node_refs": node_keys,
                "loc_refs": ["ui.progress.label"],
            }
        ],
    }
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


def repeated_row_preflight_negative_entry() -> dict:
    entry = high_fidelity_design_entry(status="source_codegen_ready", verification_status="backend_ready")
    row_set = entry["design_ir"]["tracked_entity_sets"][0]
    row_set["per_entity_state"] = {}
    row_set["ui_binding"] = ""
    entry["ui_model"]["components"] = [
        component
        for component in entry["ui_model"]["components"]
        if component.get("type") not in {"route_map", "checklist", "incident_log"}
    ]
    entry["ui_model"]["bindings"] = []
    entry["node_graph"]["variables"][0]["cleanup"] = ""
    entry["node_graph"]["variables"][0]["roles"] = ["stage_state", "checklist_state", "incident_state"]
    retry_choice = entry["node_graph"]["nodes"][3]
    retry_choice["capabilities"].append("repeated_entity_row_checklist_incident_log_backend")
    retry_choice["reads"] = ["tv_wonder_test_stage"]
    retry_choice["writes"] = ["tv_wonder_test_stage"]
    retry_choice["ui_state"] = {"variable_refs": ["tv_wonder_test_stage"]}
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


_REPO_SPEC_DATA: dict | None = None
_REPO_SPEC_INDEX: dict | None = None
_REPO_WONDERS: list[dict] | None = None
_REPO_LOCALIZATION: dict[str, str] | None = None
_REPO_TEMPLATE_REGISTRY: dict | None = None
_REPO_CAPABILITY_REGISTRY: dict | None = None
_REPO_ARCHETYPE_REGISTRY: dict | None = None


def repo_spec_data() -> dict:
    global _REPO_SPEC_DATA
    if _REPO_SPEC_DATA is None:
        _REPO_SPEC_DATA = load_spec_data()
    return _REPO_SPEC_DATA


def repo_spec_index() -> dict:
    global _REPO_SPEC_INDEX
    if _REPO_SPEC_INDEX is None:
        _REPO_SPEC_INDEX = list_index(repo_spec_data())
    return _REPO_SPEC_INDEX


def repo_wonders() -> list[dict]:
    global _REPO_WONDERS
    if _REPO_WONDERS is None:
        _REPO_WONDERS = load_unique_wonders()
    return _REPO_WONDERS


def repo_localization() -> dict[str, str]:
    global _REPO_LOCALIZATION
    if _REPO_LOCALIZATION is None:
        _REPO_LOCALIZATION = loc_english()
    return _REPO_LOCALIZATION


def repo_template_registry() -> dict:
    global _REPO_TEMPLATE_REGISTRY
    if _REPO_TEMPLATE_REGISTRY is None:
        _REPO_TEMPLATE_REGISTRY = load_template_registry()
    return _REPO_TEMPLATE_REGISTRY


def repo_capability_registry() -> dict:
    global _REPO_CAPABILITY_REGISTRY
    if _REPO_CAPABILITY_REGISTRY is None:
        _REPO_CAPABILITY_REGISTRY = load_capability_registry()
    return _REPO_CAPABILITY_REGISTRY


def repo_archetype_registry() -> dict:
    global _REPO_ARCHETYPE_REGISTRY
    if _REPO_ARCHETYPE_REGISTRY is None:
        _REPO_ARCHETYPE_REGISTRY = load_archetype_registry()
    return _REPO_ARCHETYPE_REGISTRY


def _repeated_row_event_contract_wonder_key(pilot_key: str) -> str:
    if pilot_key.startswith("unique_"):
        return pilot_key[len("unique_") :]
    return pilot_key


def _first_artifact(plan: dict, artifact_kinds: set[str]) -> dict:
    for entry in plan.get("entries", []) or []:
        for artifact in entry.get("artifacts", []) or []:
            if artifact.get("artifact_kind") in artifact_kinds:
                return artifact
    raise AssertionError(f"source-plan has no artifact in {sorted(artifact_kinds)}")


def _first_source_preview(report: dict, family: str) -> dict:
    for entry in report.get("entries", []) or []:
        for preview in entry.get("previews", []) or []:
            if preview.get("preview_family") == family:
                return preview
    raise AssertionError(f"source preview has no {family} preview")


def _first_readiness_artifact(report: dict, family: str | None = None) -> dict:
    for entry in report.get("entries", []) or []:
        for artifact in entry.get("artifacts", []) or []:
            if family is None or artifact.get("contract_family") == family:
                return artifact
    raise AssertionError(f"source-writer readiness has no {family or 'any'} artifact")


def _source_bundle(report: dict, pilot_key: str) -> dict:
    for bundle in report.get("bundles", []) or []:
        if bundle.get("key") == pilot_key:
            return bundle
    raise AssertionError(f"source bundle preview has no pilot bundle {pilot_key}")


def _first_source_bundle_artifact(report: dict, family: str, pilot_key: str | None = None) -> dict:
    for bundle in report.get("bundles", []) or []:
        if pilot_key is not None and bundle.get("key") != pilot_key:
            continue
        section = (bundle.get("sections") or {}).get(family, {})
        for artifact in section.get("artifacts", []) or []:
            return artifact
    raise AssertionError(f"source bundle preview has no {family} artifact")


def _first_alhambra_source_body_candidate(report: dict, family: str) -> dict:
    section = (report.get("sections") or {}).get(family, {})
    for candidate in section.get("structured_body_candidates", []) or []:
        return candidate
    raise AssertionError(f"Alhambra source body candidate has no {family} candidate")


def _alhambra_source_file_preview(report: dict, target_path: str) -> dict:
    for preview in report.get("file_previews", []) or []:
        if preview.get("target_path") == target_path:
            return preview
    raise AssertionError(f"Alhambra source file preview has no target {target_path}")


def _alhambra_source_file_validation_pack(report: dict, target_path: str) -> dict:
    for pack in report.get("evidence_packs", []) or []:
        if pack.get("target_path") == target_path:
            return pack
    raise AssertionError(f"Alhambra source file validation evidence has no target {target_path}")


def _alhambra_source_generator_contract(report: dict, target_path: str) -> dict:
    for contract in report.get("generator_contracts", []) or []:
        if contract.get("target_path") == target_path:
            return contract
    raise AssertionError(f"Alhambra source generator contract has no target {target_path}")


def _alhambra_event_source_file_contract_artifact(report: dict, artifact_kind: str) -> dict:
    for artifact in report.get("source_file_contract_artifacts", []) or []:
        if artifact.get("artifact_kind") == artifact_kind:
            return artifact
    raise AssertionError(f"Alhambra event source generator interface has no artifact {artifact_kind}")


def _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
    report: dict,
    artifact_kind: str,
) -> dict:
    for artifact in report.get("source_file_contract_artifacts", []) or []:
        if artifact.get("artifact_kind") == artifact_kind:
            return artifact
    raise AssertionError(
        f"Alhambra scripted-effect/cleanup source generator interface has no artifact {artifact_kind}"
    )


def _alhambra_scripted_trigger_source_file_contract_artifact(report: dict, artifact_kind: str) -> dict:
    for artifact in report.get("source_file_contract_artifacts", []) or []:
        if artifact.get("artifact_kind") == artifact_kind:
            return artifact
    raise AssertionError(f"Alhambra scripted-trigger source generator interface has no artifact {artifact_kind}")


def _alhambra_gui_source_file_contract_artifact(report: dict, artifact_kind: str) -> dict:
    for artifact in report.get("source_file_contract_artifacts", []) or []:
        if artifact.get("artifact_kind") == artifact_kind:
            return artifact
    raise AssertionError(f"Alhambra GUI source generator interface has no artifact {artifact_kind}")


def _alhambra_listener_source_file_contract_artifact(report: dict, artifact_kind: str) -> dict:
    for artifact in report.get("source_file_contract_artifacts", []) or []:
        if artifact.get("artifact_kind") == artifact_kind:
            return artifact
    raise AssertionError(f"Alhambra listener source generator interface has no artifact {artifact_kind}")


def _alhambra_localization_source_file_contract_artifact(
    report: dict,
    target_path: str,
    artifact_kind: str,
) -> dict:
    for artifact in report.get("source_file_contract_artifacts", []) or []:
        if artifact.get("target_path") == target_path and artifact.get("artifact_kind") == artifact_kind:
            return artifact
    raise AssertionError(
        "Alhambra localization source generator interface has no artifact "
        f"{artifact_kind} for {target_path}"
    )


def _sync_alhambra_generator_contract_ref_derivatives(contract: dict) -> None:
    refs = [ref for ref in contract.get("source_body_candidate_refs", []) or [] if isinstance(ref, dict)]
    family_counts: dict[str, int] = {}
    for ref in refs:
        family = str(ref.get("family", ""))
        if family.strip():
            family_counts[family] = family_counts.get(family, 0) + 1
    derived = {
        "source_body_candidate_ref_count": len(refs),
        "artifact_kinds": sorted(
            {
                str(ref.get("artifact_kind", ""))
                for ref in refs
                if str(ref.get("artifact_kind", "")).strip()
            }
        ),
        "family_artifact_counts": family_counts,
        "row_set_keys": sorted(
            {
                str(ref.get("row_set_key", ""))
                for ref in refs
                if str(ref.get("row_set_key", "")).strip()
            }
        ),
        "future_source_target_paths": sorted(
            {
                str(ref.get("future_source_target_path", ""))
                for ref in refs
                if str(ref.get("future_source_target_path", "")).strip()
            }
        ),
    }
    contract["source_body_candidate_ref_count"] = derived["source_body_candidate_ref_count"]
    for field in ("input_data_shape", "output_artifact_family"):
        if isinstance(contract.get(field), dict):
            contract[field].update(deepcopy(derived))
    evidence = contract.get("no_write_source_writer_contract_evidence")
    if isinstance(evidence, dict):
        evidence["input_data_shape"] = deepcopy(contract.get("input_data_shape"))
        evidence["output_artifact_family"] = deepcopy(contract.get("output_artifact_family"))
        evidence["source_body_candidate_ref_provenance"] = deepcopy(
            contract.get("source_body_candidate_ref_provenance")
        )


def _sync_alhambra_generator_report_ref_summary(report: dict) -> None:
    unique_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for contract in report.get("generator_contracts", []) or []
        if isinstance(contract, dict)
        for ref in contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    report["artifact_count"] = len(unique_ref_keys)
    report["source_body_candidate_ref_count"] = len(unique_ref_keys)
    if isinstance(report.get("summary"), dict):
        report["summary"]["artifact_count"] = len(unique_ref_keys)


def _repeated_row_event_contract_path(pilot_key: str) -> str:
    return (
        "src/in_game/events/"
        f"tv_wonder_unique_{_repeated_row_event_contract_wonder_key(str(pilot_key))}_ritual_events.txt"
    )


def _repeated_row_effect_contract_path(pilot_key: str) -> str:
    return (
        "src/in_game/common/scripted_effects/"
        f"tv_wonder_unique_{_repeated_row_event_contract_wonder_key(str(pilot_key))}_ritual_effects.txt"
    )


def _repeated_row_trigger_contract_path(pilot_key: str) -> str:
    return (
        "src/in_game/common/scripted_triggers/"
        f"tv_wonder_unique_{_repeated_row_event_contract_wonder_key(str(pilot_key))}_ritual_triggers.txt"
    )


def _repeated_row_gui_contract_path(pilot_key: str) -> str:
    return (
        "src/in_game/gui/panels/organization/"
        f"tv_wonder_unique_{_repeated_row_event_contract_wonder_key(str(pilot_key))}_ritual.gui"
    )


def _repeated_row_localization_contract_path(pilot_key: str) -> str:
    return (
        "src/main_menu/localization/<lang>/"
        f"tv_wonder_unique_{_repeated_row_event_contract_wonder_key(str(pilot_key))}_ritual_l_<lang>.yml"
    )


def _repeated_row_listener_contract_path(pilot_key: str) -> str:
    return (
        "src/in_game/common/on_action/"
        f"tv_wonder_unique_{_repeated_row_event_contract_wonder_key(str(pilot_key))}_ritual_on_actions.txt"
    )


def _assert_source_target_contract_negative(
    source_plan: dict,
    name: str,
    artifact_kinds: set[str],
    mutator,
    expected_error: str,
) -> None:
    negative_plan = deepcopy(source_plan)
    contract = _first_artifact(negative_plan, artifact_kinds)["source_target_contract"]
    mutator(contract)
    errors = validate_repeated_entity_row_source_plan(negative_plan)
    if not any(expected_error in error for error in errors):
        raise AssertionError(f"{name} source-plan negative was not caught: {errors}")


def assert_repeated_row_source_target_contracts(source_plan: dict) -> None:
    if source_plan.get("candidate_count") != 4:
        raise AssertionError(f"expected four repeated-row source-plan pilots, got {source_plan.get('candidate_count')}")
    if source_plan.get("validation_errors"):
        raise AssertionError(f"repeated-row source-plan unexpectedly failed validation: {source_plan['validation_errors']}")
    if source_plan.get("source_writer_allowed") is not False:
        raise AssertionError(f"repeated-row source-plan source_writer_allowed changed: {source_plan}")
    if source_plan.get("may_write_src_allowed") is not False:
        raise AssertionError(f"repeated-row source-plan may_write_src_allowed changed: {source_plan}")

    event_artifacts: list[dict] = []
    effect_artifacts: list[dict] = []
    cleanup_artifacts: list[dict] = []
    trigger_artifacts: list[dict] = []
    gui_artifacts: list[dict] = []
    localization_artifacts: list[dict] = []
    listener_artifacts_with_contracts: list[dict] = []
    non_contract_kinds: set[str] = set()
    for entry_plan in source_plan.get("entries", []) or []:
        pilot_key = entry_plan.get("key", "")
        if entry_plan.get("source_writer_allowed") is not False:
            raise AssertionError(f"{pilot_key} source_writer_allowed changed: {entry_plan}")
        if entry_plan.get("may_write_src_allowed") is not False:
            raise AssertionError(f"{pilot_key} may_write_src_allowed changed: {entry_plan}")
        expected_event_path = _repeated_row_event_contract_path(str(pilot_key))
        expected_effect_path = _repeated_row_effect_contract_path(str(pilot_key))
        expected_trigger_path = _repeated_row_trigger_contract_path(str(pilot_key))
        expected_gui_path = _repeated_row_gui_contract_path(str(pilot_key))
        expected_localization_path = _repeated_row_localization_contract_path(str(pilot_key))
        expected_listener_path = _repeated_row_listener_contract_path(str(pilot_key))
        for artifact in entry_plan.get("artifacts", []) or []:
            artifact_kind = artifact.get("artifact_kind")
            contract = artifact.get("source_target_contract")
            if artifact_kind not in (
                REPEATED_ROW_EVENT_ARTIFACT_KINDS
                | REPEATED_ROW_EFFECT_ARTIFACT_KINDS
                | REPEATED_ROW_CLEANUP_ARTIFACT_KINDS
                | REPEATED_ROW_TRIGGER_ARTIFACT_KINDS
                | REPEATED_ROW_GUI_ARTIFACT_KINDS
                | REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS
                | REPEATED_ROW_LISTENER_ARTIFACT_KINDS
            ):
                non_contract_kinds.add(str(artifact_kind))
                if contract is not None:
                    raise AssertionError(
                        f"{pilot_key} non source-target artifact should not have contract: {artifact}"
                    )
                continue

            if not isinstance(contract, dict):
                raise AssertionError(f"{pilot_key} artifact missing source_target_contract: {artifact}")
            if contract.get("status") == "source-ready":
                raise AssertionError(f"{pilot_key} source-target contract became source-ready: {contract}")
            if contract.get("status") != "blocked":
                raise AssertionError(f"{pilot_key} source-target contract should stay blocked: {contract}")
            if contract.get("status") not in REPEATED_ROW_EVENT_CONTRACT_ALLOWED_STATUSES:
                raise AssertionError(f"{pilot_key} source-target contract has invalid status: {contract}")
            if set(contract.get("allowed_statuses", [])) != REPEATED_ROW_EVENT_CONTRACT_ALLOWED_STATUSES:
                raise AssertionError(f"{pilot_key} source-target contract allowed_statuses changed: {contract}")
            if contract.get("future_target_only") is not True:
                raise AssertionError(f"{pilot_key} source-target contract must stay future-target-only: {contract}")
            if contract.get("source_writer_allowed") is not False:
                raise AssertionError(f"{pilot_key} source-target contract source_writer_allowed changed: {contract}")
            if contract.get("may_write_src") is not False:
                raise AssertionError(f"{pilot_key} source-target contract may_write_src changed: {contract}")

            if artifact_kind in REPEATED_ROW_EVENT_ARTIFACT_KINDS:
                event_artifacts.append(artifact)
                if contract.get("row_state_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} event contract allowed row-state writes: {contract}")
                if artifact.get("may_write_src") is not False:
                    raise AssertionError(f"{pilot_key} event artifact may_write_src changed: {artifact}")
                if artifact.get("blocks_source_writer") is not True:
                    raise AssertionError(f"{pilot_key} event artifact must block source writer: {artifact}")
                if artifact.get("evidence_status") != "interface_candidate":
                    raise AssertionError(f"{pilot_key} event artifact must stay interface_candidate: {artifact}")
                if contract.get("contract_family") != "event":
                    raise AssertionError(f"{pilot_key} event contract family changed: {contract}")
                if contract.get("namespace_policy") != "tv_engineering_department":
                    raise AssertionError(f"{pilot_key} event contract namespace changed: {contract}")
                if contract.get("event_id_sources") != ["spec.event_ids", "node_graph.nodes[].event_id"]:
                    raise AssertionError(f"{pilot_key} event contract event-id sources changed: {contract}")
                if contract.get("localization_key_policy") != "tv_engineering_department.<event_id>.t/d/a(/b)":
                    raise AssertionError(f"{pilot_key} event contract loc key policy changed: {contract}")
                if contract.get("candidate_future_source_target_path") != expected_event_path:
                    raise AssertionError(f"{pilot_key} event contract future target path changed: {contract}")
                handoff_rule = str(contract.get("option_effect_handoff_rule", "")).lower()
                if (
                    "future option/effect handoff only" not in handoff_rule
                    or "cannot inline row-state writes" not in handoff_rule
                ):
                    raise AssertionError(f"{pilot_key} event contract handoff rule changed: {contract}")
                missing_validations = REPEATED_ROW_EVENT_CONTRACT_REQUIRED_VALIDATIONS - set(
                    contract.get("required_validations", [])
                )
                if missing_validations:
                    raise AssertionError(f"{pilot_key} event contract missing validations: {contract}")
                missing_blockers = REPEATED_ROW_EVENT_CONTRACT_BLOCKER_REASONS - set(
                    contract.get("blocker_reasons", [])
                )
                if missing_blockers:
                    raise AssertionError(f"{pilot_key} event contract missing blocker reasons: {contract}")
            elif artifact_kind in REPEATED_ROW_EFFECT_ARTIFACT_KINDS:
                effect_artifacts.append(artifact)
                if contract.get("contract_family") != "effect":
                    raise AssertionError(f"{pilot_key} effect contract family changed: {contract}")
                if contract.get("candidate_future_source_target_path") != expected_effect_path:
                    raise AssertionError(f"{pilot_key} effect contract future target path changed: {contract}")
                if contract.get("source_type") != "common/scripted_effects":
                    raise AssertionError(f"{pilot_key} effect contract source_type changed: {contract}")
                if contract.get("effect_body_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} effect contract allowed effect body writes: {contract}")
                if contract.get("row_state_write_schema_allowed") is not False:
                    raise AssertionError(f"{pilot_key} effect contract allowed row-state write schema: {contract}")
                if (
                    contract.get("cleanup_lifecycle_scope")
                    != REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_CLEANUP_SCOPES[artifact_kind]
                ):
                    raise AssertionError(f"{pilot_key} effect contract cleanup scope changed: {contract}")
            elif artifact_kind in REPEATED_ROW_CLEANUP_ARTIFACT_KINDS:
                cleanup_artifacts.append(artifact)
                if contract.get("contract_family") != "cleanup":
                    raise AssertionError(f"{pilot_key} cleanup contract family changed: {contract}")
                if contract.get("candidate_future_source_target_path") != expected_effect_path:
                    raise AssertionError(f"{pilot_key} cleanup contract future target path changed: {contract}")
                if contract.get("source_type") != "common/scripted_effects":
                    raise AssertionError(f"{pilot_key} cleanup contract source_type changed: {contract}")
                if contract.get("effect_body_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} cleanup contract allowed effect body writes: {contract}")
                if contract.get("row_state_write_schema_allowed") is not False:
                    raise AssertionError(f"{pilot_key} cleanup contract allowed row-state write schema: {contract}")
                if (
                    contract.get("cleanup_lifecycle_scope")
                    != REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_CLEANUP_SCOPES[artifact_kind]
                ):
                    raise AssertionError(f"{pilot_key} cleanup contract lifecycle scope changed: {contract}")
            elif artifact_kind in REPEATED_ROW_TRIGGER_ARTIFACT_KINDS:
                trigger_artifacts.append(artifact)
                if contract.get("contract_family") != "trigger":
                    raise AssertionError(f"{pilot_key} trigger contract family changed: {contract}")
                if contract.get("candidate_future_source_target_path") != expected_trigger_path:
                    raise AssertionError(f"{pilot_key} trigger contract future target path changed: {contract}")
                if contract.get("source_type") != "common/scripted_triggers":
                    raise AssertionError(f"{pilot_key} trigger contract source_type changed: {contract}")
                if contract.get("trigger_body_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} trigger contract allowed trigger body writes: {contract}")
                if contract.get("tooltip_safe_unsafe_write_paths_allowed") is not False:
                    raise AssertionError(f"{pilot_key} trigger contract allowed unsafe tooltip write paths: {contract}")
                if contract.get("future_source_target_path_pattern") != (
                    "src/in_game/common/scripted_triggers/tv_wonder_unique_<wonder_key>_ritual_triggers.txt"
                ):
                    raise AssertionError(f"{pilot_key} trigger contract future path pattern changed: {contract}")
                source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
                if (
                    "future target only" not in source_generation_policy
                    or "not an actual scripted-trigger generator" not in source_generation_policy
                ):
                    raise AssertionError(f"{pilot_key} trigger contract generation policy changed: {contract}")
                tooltip_policy = str(contract.get("tooltip_safe_condition_group_policy", "")).lower()
                if "tooltip-safe condition groups" not in tooltip_policy or "must not call unsafe" not in tooltip_policy:
                    raise AssertionError(f"{pilot_key} trigger tooltip-safe policy changed: {contract}")
                aggregate_boundary = str(contract.get("aggregate_projection_boundary", "")).lower()
                if (
                    "aggregate_projection_variables" not in aggregate_boundary
                    or "cannot replace" not in aggregate_boundary
                    or "design_ir.tracked_entity_sets" not in aggregate_boundary
                ):
                    raise AssertionError(f"{pilot_key} trigger aggregate boundary changed: {contract}")
                missing_validations = REPEATED_ROW_TRIGGER_CONTRACT_REQUIRED_VALIDATIONS - set(
                    contract.get("required_validations", [])
                )
                if missing_validations:
                    raise AssertionError(f"{pilot_key} trigger contract missing validations: {contract}")
                missing_blockers = REPEATED_ROW_TRIGGER_CONTRACT_BLOCKER_REASONS - set(
                    contract.get("blocker_reasons", [])
                )
                if missing_blockers:
                    raise AssertionError(f"{pilot_key} trigger contract missing blocker reasons: {contract}")
            elif artifact_kind in REPEATED_ROW_GUI_ARTIFACT_KINDS:
                gui_artifacts.append(artifact)
                if contract.get("contract_family") != "gui":
                    raise AssertionError(f"{pilot_key} GUI contract family changed: {contract}")
                if contract.get("source_type") != "in_game/gui/panels/organization":
                    raise AssertionError(f"{pilot_key} GUI contract source_type changed: {contract}")
                if contract.get("candidate_future_source_target_path") != expected_gui_path:
                    raise AssertionError(f"{pilot_key} GUI contract future target path changed: {contract}")
                if contract.get("future_source_target_path_pattern") != (
                    "src/in_game/gui/panels/organization/tv_wonder_unique_<wonder_key>_ritual.gui"
                ):
                    raise AssertionError(f"{pilot_key} GUI contract future path pattern changed: {contract}")
                if contract.get("blocks_source_writer") is not True:
                    raise AssertionError(f"{pilot_key} GUI contract must block source writer: {contract}")
                if contract.get("gui_source_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} GUI contract allowed GUI source writes: {contract}")
                if contract.get("aggregate_only_row_reads_allowed") is not False:
                    raise AssertionError(f"{pilot_key} GUI contract allowed aggregate-only row reads: {contract}")
                if contract.get("row_state_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} GUI contract allowed row-state writes: {contract}")
                fixed_boundary = str(contract.get("fixed_row_widget_boundary", "")).lower()
                if "fixed row widgets" not in fixed_boundary or "actor slots" not in fixed_boundary:
                    raise AssertionError(f"{pilot_key} GUI fixed row widget boundary changed: {contract}")
                per_row_policy = str(contract.get("per_row_variable_binding_policy", "")).lower()
                if (
                    "design_ir.tracked_entity_sets" not in per_row_policy
                    or "per-row variables" not in per_row_policy
                    or "aggregate-only row reads are forbidden" not in per_row_policy
                ):
                    raise AssertionError(f"{pilot_key} GUI per-row binding policy changed: {contract}")
                row_policy = str(contract.get("actor_checklist_incident_row_policy", "")).lower()
                if "actor" not in row_policy or "checklist" not in row_policy or "incident" not in row_policy:
                    raise AssertionError(f"{pilot_key} GUI row policy changed: {contract}")
                tooltip_policy = str(contract.get("tooltip_key_linkage_policy", "")).lower()
                if "tooltip" not in tooltip_policy or "localization" not in tooltip_policy or "event keys" not in tooltip_policy:
                    raise AssertionError(f"{pilot_key} GUI tooltip/key linkage changed: {contract}")
                aggregate_boundary = str(contract.get("aggregate_projection_boundary", "")).lower()
                if (
                    "aggregate_projection_variables" not in aggregate_boundary
                    or "cannot replace" not in aggregate_boundary
                    or "design_ir.tracked_entity_sets" not in aggregate_boundary
                ):
                    raise AssertionError(f"{pilot_key} GUI aggregate boundary changed: {contract}")
                missing_validations = REPEATED_ROW_GUI_CONTRACT_REQUIRED_VALIDATIONS - set(
                    contract.get("required_validations", [])
                )
                if missing_validations:
                    raise AssertionError(f"{pilot_key} GUI contract missing validations: {contract}")
                missing_blockers = REPEATED_ROW_GUI_CONTRACT_BLOCKER_REASONS - set(
                    contract.get("blocker_reasons", [])
                )
                if missing_blockers:
                    raise AssertionError(f"{pilot_key} GUI contract missing blocker reasons: {contract}")
            elif artifact_kind in REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS:
                localization_artifacts.append(artifact)
                if contract.get("contract_family") != "localization":
                    raise AssertionError(f"{pilot_key} localization contract family changed: {contract}")
                if contract.get("source_type") != "main_menu/localization":
                    raise AssertionError(f"{pilot_key} localization contract source_type changed: {contract}")
                if contract.get("candidate_future_source_target_path") != expected_localization_path:
                    raise AssertionError(f"{pilot_key} localization contract future target path changed: {contract}")
                if contract.get("future_source_target_path_pattern") != (
                    "src/main_menu/localization/<lang>/tv_wonder_unique_<wonder_key>_ritual_l_<lang>.yml"
                ):
                    raise AssertionError(f"{pilot_key} localization contract future path pattern changed: {contract}")
                if contract.get("blocks_source_writer") is not True:
                    raise AssertionError(f"{pilot_key} localization contract must block source writer: {contract}")
                if contract.get("localization_source_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} localization contract allowed source writes: {contract}")
                if set(contract.get("required_languages", [])) != {"english", "simp_chinese"}:
                    raise AssertionError(f"{pilot_key} localization bilingual coverage changed: {contract}")
                if contract.get("missing_bilingual_coverage_allowed") is not False:
                    raise AssertionError(f"{pilot_key} localization contract allowed missing bilingual coverage: {contract}")
                if contract.get("unsafe_quote_newline_handling_allowed") is not False:
                    raise AssertionError(f"{pilot_key} localization contract allowed unsafe escaping: {contract}")
                namespace_policy = str(contract.get("loc_key_namespace_policy", "")).lower()
                if (
                    "tv_wonder_unique_<wonder_key>_ritual" not in namespace_policy
                    or "<row_set_key>" not in namespace_policy
                    or "<entity_key>" not in namespace_policy
                ):
                    raise AssertionError(f"{pilot_key} localization namespace policy changed: {contract}")
                escaping_policy = str(contract.get("loc_line_escaping_bom_policy", "")).lower()
                if (
                    "loc_line()" not in escaping_policy
                    or "quote/newline escaping" not in escaping_policy
                    or "utf-8 bom" not in escaping_policy
                ):
                    raise AssertionError(f"{pilot_key} localization escaping/BOM policy changed: {contract}")
                coverage_policy = str(contract.get("localization_coverage_policy", "")).lower()
                for phrase in ("row labels", "status text", "incident text", "tooltips", "summary text"):
                    if phrase not in coverage_policy:
                        raise AssertionError(f"{pilot_key} localization coverage policy changed: {contract}")
                linkage_policy = str(contract.get("gui_event_key_linkage_policy", "")).lower()
                if "gui" not in linkage_policy or "event" not in linkage_policy or "without authorizing" not in linkage_policy:
                    raise AssertionError(f"{pilot_key} localization GUI/event key linkage changed: {contract}")
                missing_validations = REPEATED_ROW_LOCALIZATION_CONTRACT_REQUIRED_VALIDATIONS - set(
                    contract.get("required_validations", [])
                )
                if missing_validations:
                    raise AssertionError(f"{pilot_key} localization contract missing validations: {contract}")
                missing_blockers = REPEATED_ROW_LOCALIZATION_CONTRACT_BLOCKER_REASONS - set(
                    contract.get("blocker_reasons", [])
                )
                if missing_blockers:
                    raise AssertionError(f"{pilot_key} localization contract missing blocker reasons: {contract}")
            elif artifact_kind in REPEATED_ROW_LISTENER_ARTIFACT_KINDS:
                listener_artifacts_with_contracts.append(artifact)
                if pilot_key != "unique_alhambra" or artifact_kind != "listener_war_integration":
                    raise AssertionError(f"{pilot_key} non-Alhambra listener contract appeared: {artifact}")
                if contract.get("contract_family") != "listener":
                    raise AssertionError(f"{pilot_key} listener contract family changed: {contract}")
                if contract.get("candidate_future_source_target_path") != expected_listener_path:
                    raise AssertionError(f"{pilot_key} listener contract future target path changed: {contract}")
                if contract.get("source_type") != "common/on_action":
                    raise AssertionError(f"{pilot_key} listener contract source_type changed: {contract}")
                if contract.get("listener_artifact_scope") != "unique_alhambra-only listener_war_integration":
                    raise AssertionError(f"{pilot_key} listener artifact scope changed: {contract}")
                if contract.get("listener_scope_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} listener contract allowed listener scope writes: {contract}")
                if contract.get("war_scope_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} listener contract allowed war scope writes: {contract}")
                if contract.get("row_state_writes_allowed") is not False:
                    raise AssertionError(f"{pilot_key} listener contract allowed row-state writes: {contract}")
                if contract.get("future_source_target_path_pattern") != (
                    "src/in_game/common/on_action/tv_wonder_unique_<wonder_key>_ritual_on_actions.txt"
                ):
                    raise AssertionError(f"{pilot_key} listener contract future path pattern changed: {contract}")
                source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
                if (
                    "future target only" not in source_generation_policy
                    or "not an actual listener integration generator" not in source_generation_policy
                ):
                    raise AssertionError(f"{pilot_key} listener contract generation policy changed: {contract}")
                bridge_policy = str(contract.get("on_action_bridge_policy", "")).lower()
                if "interface candidate only" not in bridge_policy or "no listener source writer" not in bridge_policy:
                    raise AssertionError(f"{pilot_key} listener bridge policy changed: {contract}")
                missing_validations = REPEATED_ROW_LISTENER_CONTRACT_REQUIRED_VALIDATIONS - set(
                    contract.get("required_validations", [])
                )
                if missing_validations:
                    raise AssertionError(f"{pilot_key} listener contract missing validations: {contract}")
                missing_blockers = REPEATED_ROW_LISTENER_CONTRACT_BLOCKER_REASONS - set(
                    contract.get("blocker_reasons", [])
                )
                if missing_blockers:
                    raise AssertionError(f"{pilot_key} listener contract missing blocker reasons: {contract}")

            if artifact_kind in REPEATED_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS:
                if contract.get("future_source_target_path_pattern") != (
                    "src/in_game/common/scripted_effects/tv_wonder_unique_<wonder_key>_ritual_effects.txt"
                ):
                    raise AssertionError(f"{pilot_key} effect/cleanup contract future path pattern changed: {contract}")
                source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
                if (
                    "future target only" not in source_generation_policy
                    or "not an actual scripted-effect generator" not in source_generation_policy
                ):
                    raise AssertionError(f"{pilot_key} effect/cleanup contract generation policy changed: {contract}")
                aggregate_boundary = str(contract.get("aggregate_projection_boundary", "")).lower()
                if (
                    "aggregate_projection_variables" not in aggregate_boundary
                    or "cannot replace" not in aggregate_boundary
                    or "design_ir.tracked_entity_sets" not in aggregate_boundary
                ):
                    raise AssertionError(f"{pilot_key} effect/cleanup aggregate boundary changed: {contract}")
                missing_validations = REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_REQUIRED_VALIDATIONS - set(
                    contract.get("required_validations", [])
                )
                if missing_validations:
                    raise AssertionError(f"{pilot_key} effect/cleanup contract missing validations: {contract}")
                missing_blockers = REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_BLOCKER_REASONS - set(
                    contract.get("blocker_reasons", [])
                )
                if missing_blockers:
                    raise AssertionError(f"{pilot_key} effect/cleanup contract missing blocker reasons: {contract}")

    if len(event_artifacts) != 32:
        raise AssertionError(f"expected 32 repeated-row event artifacts with contracts, got {len(event_artifacts)}")
    if len(effect_artifacts) != 40:
        raise AssertionError(
            f"expected 40 repeated-row scripted-effect artifacts with contracts, got {len(effect_artifacts)}"
        )
    if len(cleanup_artifacts) != 32:
        raise AssertionError(f"expected 32 repeated-row cleanup artifacts with contracts, got {len(cleanup_artifacts)}")
    if len(trigger_artifacts) != 24:
        raise AssertionError(f"expected 24 repeated-row trigger artifacts with contracts, got {len(trigger_artifacts)}")
    if len(gui_artifacts) != 8:
        raise AssertionError(f"expected 8 repeated-row GUI artifacts with contracts, got {len(gui_artifacts)}")
    if len(localization_artifacts) != 40:
        raise AssertionError(
            f"expected 40 repeated-row localization artifacts with contracts, got {len(localization_artifacts)}"
        )
    if len(listener_artifacts_with_contracts) != 1:
        raise AssertionError(
            "expected 1 repeated-row listener artifact with a contract, got "
            f"{len(listener_artifacts_with_contracts)}"
        )
    total_contracts = (
        len(event_artifacts)
        + len(effect_artifacts)
        + len(cleanup_artifacts)
        + len(trigger_artifacts)
        + len(gui_artifacts)
        + len(localization_artifacts)
        + len(listener_artifacts_with_contracts)
    )
    if total_contracts != 177:
        raise AssertionError(f"expected 177 repeated-row artifacts with contracts, got {total_contracts}")
    if non_contract_kinds:
        raise AssertionError(f"expected no repeated-row non-contract artifact kinds, got {sorted(non_contract_kinds)}")

    contract_families = (
        ("event", REPEATED_ROW_EVENT_ARTIFACT_KINDS),
        ("effect", REPEATED_ROW_EFFECT_ARTIFACT_KINDS),
        ("cleanup", REPEATED_ROW_CLEANUP_ARTIFACT_KINDS),
        ("trigger", REPEATED_ROW_TRIGGER_ARTIFACT_KINDS),
        ("gui", REPEATED_ROW_GUI_ARTIFACT_KINDS),
        ("localization", REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS),
        ("listener", REPEATED_ROW_LISTENER_ARTIFACT_KINDS),
    )
    for family_name, artifact_kinds in contract_families:
        missing_contract_plan = deepcopy(source_plan)
        del _first_artifact(missing_contract_plan, artifact_kinds)["source_target_contract"]
        missing_contract_errors = validate_repeated_entity_row_source_plan(missing_contract_plan)
        if not any("must declare source_target_contract" in error for error in missing_contract_errors):
            raise AssertionError(
                f"missing {family_name} contract source-plan negative was not caught: {missing_contract_errors}"
            )
        _assert_source_target_contract_negative(
            source_plan,
            f"source-ready {family_name} contract",
            artifact_kinds,
            lambda contract: contract.__setitem__("status", "source-ready"),
            "status must not be source-ready",
        )
        _assert_source_target_contract_negative(
            source_plan,
            f"writable {family_name} future target contract",
            artifact_kinds,
            lambda contract: contract.__setitem__("future_target_only", False),
            "future_target_only: true",
        )
        _assert_source_target_contract_negative(
            source_plan,
            f"may_write_src {family_name} contract",
            artifact_kinds,
            lambda contract: contract.__setitem__("may_write_src", True),
            "source_target_contract may_write_src must be false",
        )
        _assert_source_target_contract_negative(
            source_plan,
            f"source_writer_allowed {family_name} contract",
            artifact_kinds,
            lambda contract: contract.__setitem__("source_writer_allowed", True),
            "source_writer_allowed must be false",
        )

    for family_name, artifact_kinds in (
        ("event", REPEATED_ROW_EVENT_ARTIFACT_KINDS),
        ("effect", REPEATED_ROW_EFFECT_ARTIFACT_KINDS),
        ("cleanup", REPEATED_ROW_CLEANUP_ARTIFACT_KINDS),
        ("gui", REPEATED_ROW_GUI_ARTIFACT_KINDS),
        ("listener", REPEATED_ROW_LISTENER_ARTIFACT_KINDS),
    ):
        _assert_source_target_contract_negative(
            source_plan,
            f"row-state write {family_name} contract",
            artifact_kinds,
            lambda contract: contract.__setitem__("row_state_writes_allowed", True),
            "row_state_writes_allowed must be false",
        )

    for family_name, artifact_kinds in (
        ("effect", REPEATED_ROW_EFFECT_ARTIFACT_KINDS),
        ("cleanup", REPEATED_ROW_CLEANUP_ARTIFACT_KINDS),
    ):
        _assert_source_target_contract_negative(
            source_plan,
            f"row-state schema {family_name} contract",
            artifact_kinds,
            lambda contract: contract.__setitem__("row_state_write_schema_allowed", True),
            "row_state_write_schema_allowed must be false",
        )
        _assert_source_target_contract_negative(
            source_plan,
            f"effect body write {family_name} contract",
            artifact_kinds,
            lambda contract: contract.__setitem__("effect_body_writes_allowed", True),
            "effect_body_writes_allowed must be false",
        )

    _assert_source_target_contract_negative(
        source_plan,
        "trigger body write trigger contract",
        REPEATED_ROW_TRIGGER_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("trigger_body_writes_allowed", True),
        "trigger_body_writes_allowed must be false",
    )
    _assert_source_target_contract_negative(
        source_plan,
        "tooltip unsafe write trigger contract",
        REPEATED_ROW_TRIGGER_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("tooltip_safe_unsafe_write_paths_allowed", True),
        "tooltip_safe_unsafe_write_paths_allowed must be false",
    )
    _assert_source_target_contract_negative(
        source_plan,
        "listener scope write listener contract",
        REPEATED_ROW_LISTENER_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("listener_scope_writes_allowed", True),
        "listener_scope_writes_allowed must be false",
    )
    _assert_source_target_contract_negative(
        source_plan,
        "war scope write listener contract",
        REPEATED_ROW_LISTENER_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("war_scope_writes_allowed", True),
        "war_scope_writes_allowed must be false",
    )
    _assert_source_target_contract_negative(
        source_plan,
        "aggregate-only read GUI contract",
        REPEATED_ROW_GUI_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("aggregate_only_row_reads_allowed", True),
        "aggregate_only_row_reads_allowed must be false",
    )
    _assert_source_target_contract_negative(
        source_plan,
        "missing bilingual localization contract",
        REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("required_languages", ["english"]),
        "English and Simplified Chinese coverage",
    )
    _assert_source_target_contract_negative(
        source_plan,
        "missing bilingual coverage allowed localization contract",
        REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("missing_bilingual_coverage_allowed", True),
        "missing_bilingual_coverage_allowed must be false",
    )
    _assert_source_target_contract_negative(
        source_plan,
        "unsafe escaping localization contract",
        REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS,
        lambda contract: contract.__setitem__("unsafe_quote_newline_handling_allowed", True),
        "unsafe_quote_newline_handling_allowed must be false",
    )


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
        localization=localization if localization is not None else loc(),
        occupied_event_ids=occupied_event_ids,
        require_all_wonders=True,
        template_registry=template_registry if template_registry is not None else repo_template_registry(),
        capability_registry=capability_registry if capability_registry is not None else repo_capability_registry(),
        archetype_registry=archetype_registry if archetype_registry is not None else repo_archetype_registry(),
    )
    if not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected error containing {needle!r}, got {errors}")


def assert_codegen_error(
    name: str,
    entry: dict,
    needle: str,
    *,
    template_registry: dict | None = None,
    capability_registry: dict | None = None,
    archetype_registry: dict | None = None,
) -> None:
    try:
        generate_fragments_for_payload(
            {"unique_wonders": [entry]},
            wonder_keys={"unique_test_wonder"},
            template_registry=template_registry if template_registry is not None else repo_template_registry(),
            capability_registry=capability_registry if capability_registry is not None else repo_capability_registry(),
            archetype_registry=archetype_registry if archetype_registry is not None else repo_archetype_registry(),
        )
    except CodegenError as exc:
        if needle not in str(exc):
            raise AssertionError(f"{name}: expected codegen error containing {needle!r}, got {exc}") from exc
        return
    raise AssertionError(f"{name}: expected CodegenError containing {needle!r}")


def pilgrimage_backend_contract_errors(capability_registry: dict) -> list[str]:
    capability_index = {
        capability["key"]: capability
        for capability in capability_registry.get("capabilities", [])
        if isinstance(capability, dict) and capability.get("key")
    }
    contract = capability_index.get("pilgrimage_route_certification_backend")
    if contract is None:
        return ["missing pilgrimage_route_certification_backend"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("pilgrimage_route_certification_backend must declare may_write_src: false")
    if contract.get("verified_interface") != "harness_v1_intermediate_backend_contract":
        errors.append("pilgrimage_route_certification_backend must use the intermediate backend interface")
    output_kinds = set(str(kind) for kind in contract.get("output_kinds", []) or [])
    missing = sorted(PILGRIMAGE_ROUTE_BACKEND_OUTPUTS - output_kinds)
    extra = sorted(output_kinds - PILGRIMAGE_ROUTE_BACKEND_OUTPUTS)
    if missing:
        errors.append("pilgrimage_route_certification_backend missing output kind(s): " + ", ".join(missing))
    if extra:
        errors.append("pilgrimage_route_certification_backend has unsupported output kind(s): " + ", ".join(extra))
    return errors


def overland_relay_backend_contract_errors(capability_registry: dict) -> list[str]:
    capability_index = {
        capability["key"]: capability
        for capability in capability_registry.get("capabilities", [])
        if isinstance(capability, dict) and capability.get("key")
    }
    contract = capability_index.get("overland_relay_route_certification_backend")
    if contract is None:
        return ["missing overland_relay_route_certification_backend"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("overland_relay_route_certification_backend must declare may_write_src: false")
    if contract.get("verified_interface") != "harness_v1_intermediate_backend_contract":
        errors.append("overland_relay_route_certification_backend must use the intermediate backend interface")
    output_kinds = set(str(kind) for kind in contract.get("output_kinds", []) or [])
    missing = sorted(OVERLAND_RELAY_BACKEND_OUTPUTS - output_kinds)
    extra = sorted(output_kinds - OVERLAND_RELAY_BACKEND_OUTPUTS)
    if missing:
        errors.append("overland_relay_route_certification_backend missing output kind(s): " + ", ".join(missing))
    if extra:
        errors.append("overland_relay_route_certification_backend has unsupported output kind(s): " + ", ".join(extra))
    return errors


def maritime_trade_backend_contract_errors(capability_registry: dict) -> list[str]:
    capability_index = {
        capability["key"]: capability
        for capability in capability_registry.get("capabilities", [])
        if isinstance(capability, dict) and capability.get("key")
    }
    contract = capability_index.get("maritime_trade_route_certification_backend")
    if contract is None:
        return ["missing maritime_trade_route_certification_backend"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("maritime_trade_route_certification_backend must declare may_write_src: false")
    if contract.get("verified_interface") != "harness_v1_intermediate_backend_contract":
        errors.append("maritime_trade_route_certification_backend must use the intermediate backend interface")
    output_kinds = set(str(kind) for kind in contract.get("output_kinds", []) or [])
    missing = sorted(MARITIME_TRADE_BACKEND_OUTPUTS - output_kinds)
    extra = sorted(output_kinds - MARITIME_TRADE_BACKEND_OUTPUTS)
    if missing:
        errors.append("maritime_trade_route_certification_backend missing output kind(s): " + ", ".join(missing))
    if extra:
        errors.append("maritime_trade_route_certification_backend has unsupported output kind(s): " + ", ".join(extra))
    return errors


def water_management_backend_contract_errors(capability_registry: dict) -> list[str]:
    capability_index = {
        capability["key"]: capability
        for capability in capability_registry.get("capabilities", [])
        if isinstance(capability, dict) and capability.get("key")
    }
    contract = capability_index.get("water_management_restoration_completion_backend")
    if contract is None:
        return ["missing water_management_restoration_completion_backend"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("water_management_restoration_completion_backend must declare may_write_src: false")
    if contract.get("verified_interface") != "harness_v1_intermediate_backend_contract":
        errors.append("water_management_restoration_completion_backend must use the intermediate backend interface")
    output_kinds = set(str(kind) for kind in contract.get("output_kinds", []) or [])
    missing = sorted(WATER_MANAGEMENT_BACKEND_OUTPUTS - output_kinds)
    extra = sorted(output_kinds - WATER_MANAGEMENT_BACKEND_OUTPUTS)
    if missing:
        errors.append("water_management_restoration_completion_backend missing output kind(s): " + ", ".join(missing))
    if extra:
        errors.append("water_management_restoration_completion_backend has unsupported output kind(s): " + ", ".join(extra))
    return errors


def new_jerusalem_archetype_contract_errors(archetype_registry: dict) -> list[str]:
    archetype_index = {
        archetype["key"]: archetype
        for archetype in archetype_registry.get("archetypes", [])
        if isinstance(archetype, dict) and archetype.get("key")
    }
    contract = archetype_index.get("new_jerusalem_rock_route")
    if contract is None:
        return ["missing new_jerusalem_rock_route"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("new_jerusalem_rock_route must declare may_write_src: false")
    capabilities = set(str(capability) for capability in contract.get("required_capabilities", []) or [])
    missing_capabilities = sorted(NEW_JERUSALEM_ARCHETYPE_CAPABILITIES - capabilities)
    if missing_capabilities:
        errors.append("new_jerusalem_rock_route missing capability(s): " + ", ".join(missing_capabilities))
    ui_components = set(str(component) for component in contract.get("required_ui_components", []) or [])
    for component in ("route_map", "incident_log"):
        if component not in ui_components:
            errors.append(f"new_jerusalem_rock_route missing ui component {component!r}")
    return errors


def overland_relay_archetype_contract_errors(archetype_registry: dict) -> list[str]:
    archetype_index = {
        archetype["key"]: archetype
        for archetype in archetype_registry.get("archetypes", [])
        if isinstance(archetype, dict) and archetype.get("key")
    }
    contract = archetype_index.get("overland_relay_route_proof")
    if contract is None:
        return ["missing overland_relay_route_proof"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("overland_relay_route_proof must declare may_write_src: false")
    capabilities = set(str(capability) for capability in contract.get("required_capabilities", []) or [])
    missing_capabilities = sorted(OVERLAND_RELAY_ARCHETYPE_CAPABILITIES - capabilities)
    if missing_capabilities:
        errors.append("overland_relay_route_proof missing capability(s): " + ", ".join(missing_capabilities))
    roles = set(str(role) for role in contract.get("required_variable_roles", []) or [])
    if "relay_message_state" not in roles:
        errors.append("overland_relay_route_proof missing relay_message_state role")
    ui_components = set(str(component) for component in contract.get("required_ui_components", []) or [])
    for component in ("route_map", "incident_log"):
        if component not in ui_components:
            errors.append(f"overland_relay_route_proof missing ui component {component!r}")
    return errors


def maritime_trade_archetype_contract_errors(archetype_registry: dict) -> list[str]:
    archetype_index = {
        archetype["key"]: archetype
        for archetype in archetype_registry.get("archetypes", [])
        if isinstance(archetype, dict) and archetype.get("key")
    }
    contract = archetype_index.get("maritime_trade_route_covenant")
    if contract is None:
        return ["missing maritime_trade_route_covenant"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("maritime_trade_route_covenant must declare may_write_src: false")
    capabilities = set(str(capability) for capability in contract.get("required_capabilities", []) or [])
    missing_capabilities = sorted(MARITIME_TRADE_ARCHETYPE_CAPABILITIES - capabilities)
    if missing_capabilities:
        errors.append("maritime_trade_route_covenant missing capability(s): " + ", ".join(missing_capabilities))
    roles = set(str(role) for role in contract.get("required_variable_roles", []) or [])
    for role in ("warehouse_state", "translator_law_state"):
        if role not in roles:
            errors.append(f"maritime_trade_route_covenant missing variable role {role!r}")
    ui_components = set(str(component) for component in contract.get("required_ui_components", []) or [])
    for component in ("route_map", "progress_track", "incident_log"):
        if component not in ui_components:
            errors.append(f"maritime_trade_route_covenant missing ui component {component!r}")
    return errors


def polder_archetype_contract_errors(archetype_registry: dict) -> list[str]:
    archetype_index = {
        archetype["key"]: archetype
        for archetype in archetype_registry.get("archetypes", [])
        if isinstance(archetype, dict) and archetype.get("key")
    }
    contract = archetype_index.get("polder_water_board_closure_inspection")
    if contract is None:
        return ["missing polder_water_board_closure_inspection"]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append("polder_water_board_closure_inspection must declare may_write_src: false")
    capabilities = set(str(capability) for capability in contract.get("required_capabilities", []) or [])
    missing_capabilities = sorted(POLDER_ARCHETYPE_CAPABILITIES - capabilities)
    if missing_capabilities:
        errors.append("polder_water_board_closure_inspection missing capability(s): " + ", ".join(missing_capabilities))
    roles = set(str(role) for role in contract.get("required_variable_roles", []) or [])
    for role in ("checklist_state", "resource_state", "listener_state", "incident_state", "reward_state"):
        if role not in roles:
            errors.append(f"polder_water_board_closure_inspection missing variable role {role!r}")
    ui_components = set(str(component) for component in contract.get("required_ui_components", []) or [])
    for component in ("checklist", "material_stockpile", "incident_log"):
        if component not in ui_components:
            errors.append(f"polder_water_board_closure_inspection missing ui component {component!r}")
    listeners = set(str(listener) for listener in contract.get("required_listeners", []) or [])
    if "auxiliary_building_completion" not in listeners:
        errors.append("polder_water_board_closure_inspection missing auxiliary_building_completion listener")
    return errors


def lalibela_repo_entry() -> dict:
    return deepcopy(repo_spec_index()["unique_lalibela_churches"])


def inca_royal_road_repo_entry() -> dict:
    return deepcopy(repo_spec_index()["unique_inca_royal_road"])


def malacca_repo_entry() -> dict:
    return deepcopy(repo_spec_index()["unique_malacca_port"])


def dutch_polders_repo_entry() -> dict:
    return deepcopy(repo_spec_index()["unique_dutch_polders"])


def assert_lalibela_error(name: str, entry: dict, needle: str) -> None:
    errors = validate_spec_payload(
        {"unique_wonders": [entry]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=repo_template_registry(),
        capability_registry=repo_capability_registry(),
        archetype_registry=repo_archetype_registry(),
    )
    if not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected error containing {needle!r}, got {errors}")


def assert_inca_royal_road_error(name: str, entry: dict, needle: str) -> None:
    errors = validate_spec_payload(
        {"unique_wonders": [entry]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=repo_template_registry(),
        capability_registry=repo_capability_registry(),
        archetype_registry=repo_archetype_registry(),
    )
    if not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected error containing {needle!r}, got {errors}")


def assert_malacca_error(name: str, entry: dict, needle: str) -> None:
    errors = validate_spec_payload(
        {"unique_wonders": [entry]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=repo_template_registry(),
        capability_registry=repo_capability_registry(),
        archetype_registry=repo_archetype_registry(),
    )
    if not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected error containing {needle!r}, got {errors}")


def assert_dutch_polders_error(
    name: str,
    entry: dict,
    needle: str,
    *,
    capability_registry: dict | None = None,
    archetype_registry: dict | None = None,
) -> None:
    errors = validate_spec_payload(
        {"unique_wonders": [entry]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=repo_template_registry(),
        capability_registry=capability_registry if capability_registry is not None else repo_capability_registry(),
        archetype_registry=archetype_registry if archetype_registry is not None else repo_archetype_registry(),
    )
    if not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected error containing {needle!r}, got {errors}")


def main() -> None:
    spec_data = repo_spec_data()
    test_loc = loc()
    template_registry = repo_template_registry()
    capability_registry = repo_capability_registry()
    archetype_registry = repo_archetype_registry()

    good_errors = validate_spec_payload(
        {"unique_wonders": [valid_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if good_errors:
        raise AssertionError(f"valid entry unexpectedly failed: {good_errors}")

    design_complete_errors = validate_spec_payload(
        {"unique_wonders": [high_fidelity_design_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if design_complete_errors:
        raise AssertionError(f"design_complete fixture with compiler gaps unexpectedly failed: {design_complete_errors}")

    compiler_mapped_errors = validate_spec_payload(
        {"unique_wonders": [high_fidelity_design_entry(status="compiler_mapped")]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if compiler_mapped_errors:
        raise AssertionError(f"compiler_mapped fixture unexpectedly failed: {compiler_mapped_errors}")

    source_ready_errors = validate_spec_payload(
        {"unique_wonders": [high_fidelity_design_entry(status="source_codegen_ready", verification_status="backend_ready")]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if source_ready_errors:
        raise AssertionError(f"source_codegen_ready fixture unexpectedly failed: {source_ready_errors}")

    repeated_row_preflight = repeated_entity_row_preflight_for_payload(spec_data)
    if repeated_row_preflight["candidate_count"] != 4:
        raise AssertionError(f"expected four repeated-row pilots, got {repeated_row_preflight['candidate_count']}")
    if repeated_row_preflight["row_set_count"] != 8:
        raise AssertionError(f"expected eight repeated-row row sets, got {repeated_row_preflight['row_set_count']}")
    if repeated_row_preflight["entity_row_count"] != 40:
        raise AssertionError(f"expected forty repeated entity rows, got {repeated_row_preflight['entity_row_count']}")
    preflight_by_key = {entry["key"]: entry for entry in repeated_row_preflight["entries"]}
    for pilot_key, expected in REPEATED_ROW_PILOTS.items():
        entry_report = preflight_by_key.get(pilot_key)
        if entry_report is None:
            raise AssertionError(f"missing repeated-row preflight report for {pilot_key}")
        row_keys = {row_set["key"] for row_set in entry_report["row_sets"]}
        if row_keys != expected["row_sets"]:
            raise AssertionError(f"{pilot_key} row sets mismatch: expected {expected['row_sets']}, got {row_keys}")
        ui_types = set(entry_report["ui_component_types"])
        if not expected["ui"] <= ui_types:
            raise AssertionError(f"{pilot_key} UI component types missing {expected['ui'] - ui_types}")
        blockers = set(entry_report["blockers"])
        if blockers != expected["blockers"]:
            raise AssertionError(f"{pilot_key} blockers mismatch: expected {expected['blockers']}, got {blockers}")
        if "missing_row_variables" in blockers:
            raise AssertionError(f"{pilot_key} should preserve design_ir per-row variable patterns")
        if not entry_report["aggregate_projection_is_not_row_state"]:
            raise AssertionError(f"{pilot_key} aggregate projection variables must not replace design_ir row state")
        for row_set in entry_report["row_sets"]:
            if not row_set["entity_keys"]:
                raise AssertionError(f"{pilot_key} row set {row_set['key']} did not expose entity rows")
            if not row_set["per_row_variable_patterns"]:
                raise AssertionError(f"{pilot_key} row set {row_set['key']} did not expose per-row variable patterns")
            if not row_set["aggregate_projection_variables"]:
                raise AssertionError(f"{pilot_key} row set {row_set['key']} did not expose aggregate projection variables")

    negative_preflight = repeated_entity_row_preflight_for_entry(repeated_row_preflight_negative_entry())
    negative_blockers = set(negative_preflight["blockers"])
    for expected_blocker in ("missing_row_variables", "missing_gui_rows", "missing_cleanup"):
        if expected_blocker not in negative_blockers:
            raise AssertionError(f"negative repeated-row preflight missing blocker {expected_blocker}: {negative_preflight}")
    if not negative_preflight["aggregate_projection_variables"]:
        raise AssertionError("negative repeated-row fixture should still report aggregate projection variables")
    if not negative_preflight["aggregate_projection_is_not_row_state"]:
        raise AssertionError("negative repeated-row fixture must not treat aggregate variables as row-state replacement")

    source_plan = repeated_entity_row_source_plan_for_payload(spec_data)
    if source_plan["candidate_count"] != 4:
        raise AssertionError(f"expected four repeated-row source-plan pilots, got {source_plan['candidate_count']}")
    if source_plan["artifact_count"] != 177:
        raise AssertionError(f"expected 177 repeated-row source-plan artifacts, got {source_plan['artifact_count']}")
    if source_plan["validation_errors"]:
        raise AssertionError(f"repeated-row source-plan unexpectedly failed validation: {source_plan['validation_errors']}")
    if source_plan.get("source_writer_allowed") is not False:
        raise AssertionError(f"repeated-row source-plan source_writer_allowed changed: {source_plan}")
    if source_plan.get("may_write_src_allowed") is not False:
        raise AssertionError(f"repeated-row source-plan may_write_src_allowed changed: {source_plan}")
    assert_repeated_row_source_target_contracts(source_plan)
    source_plan_by_key = {entry["key"]: entry for entry in source_plan["entries"]}
    seen_event_artifact_kinds: set[str] = set()
    seen_effect_cleanup_artifact_kinds: set[str] = set()
    seen_trigger_artifact_kinds: set[str] = set()
    seen_gui_artifact_kinds: set[str] = set()
    seen_localization_artifact_kinds: set[str] = set()
    for pilot_key, expected in REPEATED_ROW_PILOTS.items():
        entry_plan = source_plan_by_key.get(pilot_key)
        if entry_plan is None:
            raise AssertionError(f"missing repeated-row source-plan report for {pilot_key}")
        if entry_plan.get("source_writer_allowed") is not False:
            raise AssertionError(f"{pilot_key} source_writer_allowed changed: {entry_plan}")
        if entry_plan.get("may_write_src_allowed") is not False:
            raise AssertionError(f"{pilot_key} may_write_src_allowed changed: {entry_plan}")
        row_keys = {row_set["key"] for row_set in entry_plan["row_sets"]}
        if row_keys != expected["row_sets"]:
            raise AssertionError(f"{pilot_key} source-plan row sets mismatch: expected {expected['row_sets']}, got {row_keys}")
        for artifact in entry_plan["artifacts"]:
            if artifact.get("may_write_src") is not False:
                raise AssertionError(f"{pilot_key} source-plan artifact may_write_src was not false: {artifact}")
            if artifact.get("blocks_source_writer") is not True:
                raise AssertionError(f"{pilot_key} source-plan artifact does not block source writer: {artifact}")
            artifact_kind = artifact["artifact_kind"]
            if artifact_kind in REPEATED_ROW_EVENT_ARTIFACT_KINDS:
                seen_event_artifact_kinds.add(artifact_kind)
                if artifact.get("evidence_status") != "interface_candidate":
                    raise AssertionError(f"{pilot_key} event artifact should stay interface_candidate: {artifact}")
            if artifact_kind in REPEATED_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS:
                seen_effect_cleanup_artifact_kinds.add(artifact_kind)
                if artifact.get("evidence_status") not in {"interface_candidate", "missing_eu5_evidence"}:
                    raise AssertionError(
                        f"{pilot_key} effect/cleanup artifact should not claim verified_existing: {artifact}"
                    )
                if artifact_kind == "cleanup_failure" and artifact.get("evidence_status") != "interface_candidate":
                    raise AssertionError(f"{pilot_key} cleanup_failure should be interface_candidate: {artifact}")
            if artifact_kind in REPEATED_ROW_TRIGGER_ARTIFACT_KINDS:
                seen_trigger_artifact_kinds.add(artifact_kind)
                if artifact.get("evidence_status") != "interface_candidate":
                    raise AssertionError(f"{pilot_key} trigger artifact should be interface_candidate: {artifact}")
            if artifact_kind in REPEATED_ROW_GUI_ARTIFACT_KINDS:
                seen_gui_artifact_kinds.add(artifact_kind)
                if artifact.get("evidence_status") not in {"interface_candidate", "missing_eu5_evidence"}:
                    raise AssertionError(
                        f"{pilot_key} GUI artifact should stay interface_candidate or missing evidence: {artifact}"
                    )
                if artifact.get("evidence_status") != "interface_candidate":
                    raise AssertionError(f"{pilot_key} GUI artifact should be interface_candidate: {artifact}")
            if artifact_kind in REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS:
                seen_localization_artifact_kinds.add(artifact_kind)
                if artifact.get("evidence_status") not in {"interface_candidate", "missing_eu5_evidence"}:
                    raise AssertionError(
                        f"{pilot_key} localization artifact should stay interface_candidate or missing evidence: "
                        f"{artifact}"
                    )
                if artifact.get("evidence_status") != "interface_candidate":
                    raise AssertionError(
                        f"{pilot_key} localization artifact should be interface_candidate: {artifact}"
                    )
            if artifact_kind in REPEATED_ROW_STRUCTURED_EVIDENCE_ARTIFACT_KINDS:
                evidence_mapping = artifact.get("evidence_mapping")
                if not isinstance(evidence_mapping, dict):
                    raise AssertionError(f"{pilot_key} structured-evidence artifact missing evidence_mapping: {artifact}")
                missing_mapping_fields = REPEATED_ROW_EVIDENCE_MAPPING_FIELDS - set(evidence_mapping)
                if missing_mapping_fields:
                    raise AssertionError(
                        f"{pilot_key} artifact {artifact_kind} evidence_mapping missing fields: "
                        f"{sorted(missing_mapping_fields)}"
                    )
                if evidence_mapping["artifact_kind"] != artifact_kind:
                    raise AssertionError(f"{pilot_key} artifact {artifact_kind} evidence kind mismatch")
                if evidence_mapping["source_target_boundary"] != artifact["source_target_boundary"]:
                    raise AssertionError(f"{pilot_key} artifact {artifact_kind} evidence boundary mismatch")
                if evidence_mapping["blocks_source_writer"] is not True:
                    raise AssertionError(f"{pilot_key} artifact {artifact_kind} evidence should block source writer")
                if not isinstance(evidence_mapping["evidence_source_paths"], list):
                    raise AssertionError(f"{pilot_key} artifact {artifact_kind} evidence paths must be a list")
                if not evidence_mapping["eu5_source_syntax_pattern"]:
                    raise AssertionError(f"{pilot_key} artifact {artifact_kind} missing EU5 syntax evidence or gap")
                if not evidence_mapping["evidence_source_paths"]:
                    raise AssertionError(f"{pilot_key} artifact {artifact_kind} missing EU5/source evidence paths")
                if not (
                    evidence_mapping["generator_candidate"] or evidence_mapping["generator_missing_reason"]
                ):
                    raise AssertionError(f"{pilot_key} artifact {artifact_kind} missing generator evidence rationale")
        for row_set in entry_plan["row_sets"]:
            kinds = set(row_set["artifact_kinds"])
            missing_event_kinds = REPEATED_ROW_EVENT_ARTIFACT_KINDS - kinds
            if missing_event_kinds:
                raise AssertionError(
                    f"{pilot_key} row set {row_set['key']} missing event artifact kinds: "
                    f"{sorted(missing_event_kinds)}"
                )
            missing_effect_cleanup_kinds = REPEATED_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS - kinds
            if missing_effect_cleanup_kinds:
                raise AssertionError(
                    f"{pilot_key} row set {row_set['key']} missing effect/cleanup artifact kinds: "
                    f"{sorted(missing_effect_cleanup_kinds)}"
                )
            if not any(kind.startswith("scripted_effect_") for kind in kinds):
                raise AssertionError(f"{pilot_key} row set {row_set['key']} missing effect artifact")
            if not any(kind.startswith("scripted_trigger_") for kind in kinds):
                raise AssertionError(f"{pilot_key} row set {row_set['key']} missing trigger artifact")
            if not any(kind.startswith("gui_") for kind in kinds):
                raise AssertionError(f"{pilot_key} row set {row_set['key']} missing GUI artifact")
            if not any(kind.startswith("localization_") for kind in kinds):
                raise AssertionError(f"{pilot_key} row set {row_set['key']} missing localization artifact")
            if not any(kind.startswith("cleanup_") for kind in kinds):
                raise AssertionError(f"{pilot_key} row set {row_set['key']} missing cleanup artifact")
        listener_artifacts = [
            artifact
            for artifact in entry_plan["artifacts"]
            if artifact["artifact_kind"].startswith("listener_")
        ]
        listener_kinds = {artifact["artifact_kind"] for artifact in listener_artifacts}
        if pilot_key == "unique_alhambra":
            if listener_kinds != REPEATED_ROW_LISTENER_ARTIFACT_KINDS or len(listener_artifacts) != 1:
                raise AssertionError(
                    "Alhambra source-plan must include exactly listener_war_integration: "
                    f"{listener_artifacts}"
                )
            listener_artifact = listener_artifacts[0]
            if listener_artifact.get("evidence_status") != "interface_candidate":
                raise AssertionError(
                    f"Alhambra listener evidence must stay interface_candidate: {listener_artifact}"
                )
            if listener_artifact.get("may_write_src") is not False:
                raise AssertionError(f"Alhambra listener may_write_src changed: {listener_artifact}")
            if listener_artifact.get("blocks_source_writer") is not True:
                raise AssertionError(f"Alhambra listener must block source writer: {listener_artifact}")
            listener_contract = listener_artifact.get("source_target_contract")
            if not isinstance(listener_contract, dict):
                raise AssertionError(f"Alhambra listener missing source_target_contract: {listener_artifact}")
            if listener_contract.get("contract_family") != "listener":
                raise AssertionError(f"Alhambra listener contract family changed: {listener_contract}")
            if listener_contract.get("listener_scope_writes_allowed") is not False:
                raise AssertionError(f"Alhambra listener contract allowed listener scope writes: {listener_contract}")
            if listener_contract.get("war_scope_writes_allowed") is not False:
                raise AssertionError(f"Alhambra listener contract allowed war scope writes: {listener_contract}")
            listener_mapping = listener_artifact.get("evidence_mapping")
            if not isinstance(listener_mapping, dict):
                raise AssertionError(f"Alhambra listener missing structured evidence mapping: {listener_artifact}")
            missing_listener_fields = REPEATED_ROW_EVIDENCE_MAPPING_FIELDS - set(listener_mapping)
            if missing_listener_fields:
                raise AssertionError(
                    "Alhambra listener evidence_mapping missing fields: "
                    f"{sorted(missing_listener_fields)}"
                )
            empty_listener_fields = [
                field
                for field in (
                    "artifact_kind",
                    "eu5_source_syntax_pattern",
                    "generator_candidate",
                    "generator_missing_reason",
                    "source_target_boundary",
                )
                if not str(listener_mapping.get(field, "")).strip()
            ]
            if empty_listener_fields:
                raise AssertionError(
                    "Alhambra listener evidence_mapping has empty fields: "
                    f"{empty_listener_fields}"
                )
            if listener_mapping.get("blocks_source_writer") is not True:
                raise AssertionError(
                    f"Alhambra listener evidence_mapping must block source writer: {listener_mapping}"
                )
            listener_paths = set(listener_mapping.get("evidence_source_paths", []))
            missing_listener_paths = REPEATED_ROW_LISTENER_EVIDENCE_PATHS - listener_paths
            if missing_listener_paths:
                raise AssertionError(
                    "Alhambra listener evidence paths changed or went missing: "
                    f"{sorted(missing_listener_paths)}"
                )
            listener_reason = str(listener_mapping.get("generator_missing_reason", ""))
            for expected_phrase in (
                "source writer ownership",
                "source-target boundary",
                "Alhambra row-state write contract",
            ):
                if expected_phrase not in listener_reason:
                    raise AssertionError(
                        "Alhambra listener missing source-writer blocker phrase "
                        f"{expected_phrase!r}: {listener_mapping}"
                    )
        elif listener_kinds:
            raise AssertionError(f"{pilot_key} should not receive generic listener artifacts: {listener_kinds}")
    if seen_event_artifact_kinds != REPEATED_ROW_EVENT_ARTIFACT_KINDS:
        raise AssertionError(
            "repeated-row source-plan did not cover every event evidence kind: "
            f"{sorted(REPEATED_ROW_EVENT_ARTIFACT_KINDS - seen_event_artifact_kinds)}"
        )
    if seen_effect_cleanup_artifact_kinds != REPEATED_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS:
        raise AssertionError(
            "repeated-row source-plan did not cover every effect/cleanup evidence kind: "
            f"{sorted(REPEATED_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS - seen_effect_cleanup_artifact_kinds)}"
        )
    if seen_trigger_artifact_kinds != REPEATED_ROW_TRIGGER_ARTIFACT_KINDS:
        raise AssertionError(
            "repeated-row source-plan did not cover every trigger evidence kind: "
            f"{sorted(REPEATED_ROW_TRIGGER_ARTIFACT_KINDS - seen_trigger_artifact_kinds)}"
        )
    if seen_gui_artifact_kinds != REPEATED_ROW_GUI_ARTIFACT_KINDS:
        raise AssertionError(
            "repeated-row source-plan did not cover every GUI evidence kind: "
            f"{sorted(REPEATED_ROW_GUI_ARTIFACT_KINDS - seen_gui_artifact_kinds)}"
        )
    if seen_localization_artifact_kinds != REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS:
        raise AssertionError(
            "repeated-row source-plan did not cover every localization evidence kind: "
            f"{sorted(REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS - seen_localization_artifact_kinds)}"
        )

    missing_row_set_plan = deepcopy(source_plan)
    missing_row_set_plan["entries"][0]["artifacts"] = [
        artifact
        for artifact in missing_row_set_plan["entries"][0]["artifacts"]
        if artifact["row_set_key"] != missing_row_set_plan["entries"][0]["row_sets"][0]["key"]
    ]
    missing_row_set_errors = validate_repeated_entity_row_source_plan(missing_row_set_plan)
    if not any("has no source-plan artifacts" in error for error in missing_row_set_errors):
        raise AssertionError(f"missing row-set source-plan negative was not caught: {missing_row_set_errors}")

    missing_owner_plan = deepcopy(source_plan)
    missing_owner_plan["entries"][0]["artifacts"][0]["owner_generator"] = ""
    missing_owner_errors = validate_repeated_entity_row_source_plan(missing_owner_plan)
    if not any("must declare owner_generator" in error for error in missing_owner_errors):
        raise AssertionError(f"missing owner_generator source-plan negative was not caught: {missing_owner_errors}")

    writable_plan = deepcopy(source_plan)
    writable_plan["entries"][0]["artifacts"][0]["may_write_src"] = True
    writable_plan_errors = validate_repeated_entity_row_source_plan(writable_plan)
    if not any("must declare may_write_src: false" in error for error in writable_plan_errors):
        raise AssertionError(f"may_write_src source-plan negative was not caught: {writable_plan_errors}")

    missing_evidence_mapping_plan = deepcopy(source_plan)
    del missing_evidence_mapping_plan["entries"][0]["artifacts"][0]["evidence_mapping"]
    missing_evidence_mapping_errors = validate_repeated_entity_row_source_plan(missing_evidence_mapping_plan)
    if not any("missing field(s): evidence_mapping" in error for error in missing_evidence_mapping_errors):
        raise AssertionError(
            f"missing evidence_mapping source-plan negative was not caught: {missing_evidence_mapping_errors}"
        )

    mismatched_evidence_kind_plan = deepcopy(source_plan)
    mismatched_evidence_kind_plan["entries"][0]["artifacts"][0]["evidence_mapping"]["artifact_kind"] = "wrong_kind"
    mismatched_evidence_kind_errors = validate_repeated_entity_row_source_plan(mismatched_evidence_kind_plan)
    if not any("evidence_mapping artifact_kind mismatch" in error for error in mismatched_evidence_kind_errors):
        raise AssertionError(
            f"mismatched evidence kind source-plan negative was not caught: {mismatched_evidence_kind_errors}"
        )

    mismatched_evidence_block_plan = deepcopy(source_plan)
    mismatched_evidence_block_plan["entries"][0]["artifacts"][0]["evidence_mapping"]["blocks_source_writer"] = False
    mismatched_evidence_block_errors = validate_repeated_entity_row_source_plan(mismatched_evidence_block_plan)
    if not any("evidence_mapping blocks_source_writer mismatch" in error for error in mismatched_evidence_block_errors):
        raise AssertionError(
            f"mismatched evidence block source-plan negative was not caught: {mismatched_evidence_block_errors}"
        )

    source_preview = repeated_entity_row_source_preview_for_payload(spec_data, source_plan=source_plan)
    if source_preview["validation_errors"]:
        raise AssertionError(f"repeated-row source preview unexpectedly failed validation: {source_preview['validation_errors']}")
    expected_preview_family_counts = {
        "event": 32,
        "localization": 40,
        "effect": 40,
        "cleanup": 32,
        "trigger": 24,
        "gui": 8,
        "listener": 1,
    }
    if source_preview.get("preview_count") != 177:
        raise AssertionError(f"expected 177 repeated-row source previews, got {source_preview.get('preview_count')}")
    for family, expected_count in expected_preview_family_counts.items():
        if source_preview.get("preview_family_summary", {}).get(family) != expected_count:
            raise AssertionError(
                f"expected {expected_count} repeated-row {family} previews, got "
                f"{source_preview.get('preview_family_summary')}"
            )
    if source_preview.get("source_writer_allowed") is not False:
        raise AssertionError(f"source preview source_writer_allowed changed: {source_preview}")
    if source_preview.get("may_write_src_allowed") is not False:
        raise AssertionError(f"source preview may_write_src_allowed changed: {source_preview}")
    if source_preview.get("writes_src") is not False:
        raise AssertionError(f"source preview writes_src changed: {source_preview}")
    if source_preview.get("source_plan_artifact_count") != 177:
        raise AssertionError(f"source preview should preserve 177-artifact source-plan: {source_preview}")
    skipped_preview_kinds: set[str] = set()
    preview_family_counts = {family: 0 for family in expected_preview_family_counts}
    for entry_preview in source_preview.get("entries", []) or []:
        if entry_preview.get("preview_only") is not True:
            raise AssertionError(f"entry source preview must be preview-only: {entry_preview}")
        skipped_preview_kinds.update(entry_preview.get("skipped_artifact_kinds", []))
        for preview in entry_preview.get("previews", []) or []:
            family = preview.get("preview_family")
            artifact_kind = preview.get("artifact_kind")
            if preview.get("preview_only") is not True:
                raise AssertionError(f"{artifact_kind} preview_only changed: {preview}")
            if preview.get("may_write_src") is not False:
                raise AssertionError(f"{artifact_kind} may_write_src changed: {preview}")
            if preview.get("source_writer_allowed") is not False:
                raise AssertionError(f"{artifact_kind} source_writer_allowed changed: {preview}")
            if preview.get("writes_src") is not False:
                raise AssertionError(f"{artifact_kind} writes_src changed: {preview}")
            if preview.get("blocks_source_writer") is not True:
                raise AssertionError(f"{artifact_kind} blocks_source_writer changed: {preview}")
            if preview.get("source_ready") is not False:
                raise AssertionError(f"{artifact_kind} preview became source-ready: {preview}")
            if family == "event":
                preview_family_counts["event"] += 1
                if artifact_kind not in REPEATED_ROW_EVENT_ARTIFACT_KINDS:
                    raise AssertionError(f"non-event artifact received event preview: {preview}")
                if preview.get("row_state_writes_allowed") is not False:
                    raise AssertionError(f"event preview allowed row-state writes: {preview}")
                body = preview.get("source_body_preview", {})
                if body.get("no_tooltip_heavy_finalization") is not True:
                    raise AssertionError(f"event preview lost tooltip-heavy finalization blocker: {preview}")
                if body.get("no_row_state_write") is not True:
                    raise AssertionError(f"event preview lost row-state write blocker: {preview}")
                if body.get("no_source_ready") is not True:
                    raise AssertionError(f"event preview lost source-ready blocker: {preview}")
            elif family == "localization":
                preview_family_counts["localization"] += 1
                if artifact_kind not in REPEATED_ROW_LOCALIZATION_ARTIFACT_KINDS:
                    raise AssertionError(f"non-localization artifact received localization preview: {preview}")
                if set(preview.get("required_languages", [])) != {"english", "simp_chinese"}:
                    raise AssertionError(f"localization preview bilingual coverage changed: {preview}")
            elif family == "effect":
                preview_family_counts["effect"] += 1
                if artifact_kind not in REPEATED_ROW_EFFECT_ARTIFACT_KINDS:
                    raise AssertionError(f"non-effect artifact received effect preview: {preview}")
                if preview.get("row_state_writes_allowed") is not False:
                    raise AssertionError(f"effect preview allowed row-state writes: {preview}")
                if preview.get("effect_body_writes_allowed") is not False:
                    raise AssertionError(f"effect preview allowed effect body writes: {preview}")
                body = preview.get("source_body_preview", {})
                if body.get("no_effect_body") is not True:
                    raise AssertionError(f"effect preview emitted effect body: {preview}")
                if body.get("no_row_state_write") is not True:
                    raise AssertionError(f"effect preview lost row-state write blocker: {preview}")
            elif family == "cleanup":
                preview_family_counts["cleanup"] += 1
                if artifact_kind not in REPEATED_ROW_CLEANUP_ARTIFACT_KINDS:
                    raise AssertionError(f"non-cleanup artifact received cleanup preview: {preview}")
                if preview.get("effect_body_writes_allowed") is not False:
                    raise AssertionError(f"cleanup preview allowed effect body writes: {preview}")
                body = preview.get("source_body_preview", {})
                if body.get("no_cleanup_body") is not True:
                    raise AssertionError(f"cleanup preview emitted cleanup body: {preview}")
                if not isinstance(preview.get("cleanup_scope_plan"), dict):
                    raise AssertionError(f"cleanup preview lost cleanup scope plan: {preview}")
                coverage = preview.get("cleanup_coverage")
                if not isinstance(coverage, dict) or not {
                    "completion",
                    "failure",
                    "ownership_loss",
                    "ritual_reset",
                } <= set(coverage):
                    raise AssertionError(f"cleanup preview lost lifecycle coverage: {preview}")
            elif family == "trigger":
                preview_family_counts["trigger"] += 1
                if artifact_kind not in REPEATED_ROW_TRIGGER_ARTIFACT_KINDS:
                    raise AssertionError(f"non-trigger artifact received trigger preview: {preview}")
                if preview.get("trigger_body_writes_allowed") is not False:
                    raise AssertionError(f"trigger preview allowed trigger body writes: {preview}")
                if preview.get("tooltip_safe_unsafe_write_paths_allowed") is not False:
                    raise AssertionError(f"trigger preview allowed unsafe tooltip write paths: {preview}")
                body = preview.get("source_body_preview", {})
                if body.get("no_trigger_body") is not True:
                    raise AssertionError(f"trigger preview emitted trigger body: {preview}")
                if body.get("no_unsafe_tooltip_write_path") is not True:
                    raise AssertionError(f"trigger preview lost tooltip write-path blocker: {preview}")
            elif family == "gui":
                preview_family_counts["gui"] += 1
                if artifact_kind not in REPEATED_ROW_GUI_ARTIFACT_KINDS:
                    raise AssertionError(f"non-GUI artifact received GUI preview: {preview}")
                if preview.get("aggregate_only_display_allowed") is not False:
                    raise AssertionError(f"GUI preview allowed aggregate-only display: {preview}")
                if preview.get("gui_source_body_allowed") is not False:
                    raise AssertionError(f"GUI preview allowed GUI body writes: {preview}")
                if preview.get("gui_source_writes_allowed") is not False:
                    raise AssertionError(f"GUI preview allowed GUI source writes: {preview}")
                if preview.get("row_state_writes_allowed") is not False:
                    raise AssertionError(f"GUI preview allowed row-state writes: {preview}")
                body = preview.get("source_body_preview", {})
                if body.get("no_gui_source_body") is not True:
                    raise AssertionError(f"GUI preview lost source body blocker: {preview}")
                if not isinstance(preview.get("fixed_row_widget_plan"), dict):
                    raise AssertionError(f"GUI preview lost fixed row widget plan: {preview}")
                if not isinstance(preview.get("per_row_variable_binding_plan"), dict):
                    raise AssertionError(f"GUI preview lost per-row binding plan: {preview}")
                if not isinstance(preview.get("tooltip_localization_linkage"), dict):
                    raise AssertionError(f"GUI preview lost tooltip/localization linkage: {preview}")
                if not isinstance(preview.get("gui_event_key_linkage"), dict):
                    raise AssertionError(f"GUI preview lost GUI/event linkage: {preview}")
            elif family == "listener":
                preview_family_counts["listener"] += 1
                if artifact_kind not in REPEATED_ROW_LISTENER_ARTIFACT_KINDS:
                    raise AssertionError(f"non-listener artifact received listener preview: {preview}")
                if preview.get("pilot_key") != "unique_alhambra":
                    raise AssertionError(f"listener preview should be Alhambra-only: {preview}")
                if preview.get("listener_body_allowed") is not False:
                    raise AssertionError(f"listener preview allowed listener body writes: {preview}")
                if preview.get("listener_scope_writes_allowed") is not False:
                    raise AssertionError(f"listener preview allowed listener scope writes: {preview}")
                if preview.get("war_scope_writes_allowed") is not False:
                    raise AssertionError(f"listener preview allowed war scope writes: {preview}")
                if preview.get("source_writes_allowed") is not False:
                    raise AssertionError(f"listener preview allowed source writes: {preview}")
                body = preview.get("source_body_preview", {})
                if body.get("no_listener_body") is not True:
                    raise AssertionError(f"listener preview emitted listener body: {preview}")
                if not isinstance(preview.get("on_action_hook_linkage_plan"), dict):
                    raise AssertionError(f"listener preview lost hook linkage plan: {preview}")
                if not isinstance(preview.get("selected_ritual_trigger_linkage"), dict):
                    raise AssertionError(f"listener preview lost selected ritual trigger linkage: {preview}")
                if not isinstance(preview.get("row_state_handoff_boundary"), dict):
                    raise AssertionError(f"listener preview lost row-state handoff boundary: {preview}")
            else:
                raise AssertionError(f"unsupported source body preview family {family}: {preview}")
    for family, expected_count in expected_preview_family_counts.items():
        if preview_family_counts[family] != expected_count:
            raise AssertionError(f"expected {expected_count} {family} previews, got {preview_family_counts[family]}")
    if skipped_preview_kinds:
        raise AssertionError(f"source preview should not skip artifact kinds: {sorted(skipped_preview_kinds)}")
    if source_preview.get("skipped_artifact_kinds") != []:
        raise AssertionError(f"source preview report skipped kinds should be empty: {source_preview}")

    row_state_preview = deepcopy(source_preview)
    _first_source_preview(row_state_preview, "event")["row_state_writes_allowed"] = True
    row_state_preview_errors = validate_repeated_entity_row_source_preview(row_state_preview)
    if not any("row-state writes must be false" in error for error in row_state_preview_errors):
        raise AssertionError(f"event row-state write preview negative was not caught: {row_state_preview_errors}")

    effect_row_state_preview = deepcopy(source_preview)
    _first_source_preview(effect_row_state_preview, "effect")["row_state_writes_allowed"] = True
    effect_row_state_errors = validate_repeated_entity_row_source_preview(effect_row_state_preview)
    if not any("effect preview row-state writes must be false" in error for error in effect_row_state_errors):
        raise AssertionError(f"effect row-state write preview negative was not caught: {effect_row_state_errors}")

    effect_body_preview = deepcopy(source_preview)
    _first_source_preview(effect_body_preview, "effect")["effect_body_writes_allowed"] = True
    effect_body_errors = validate_repeated_entity_row_source_preview(effect_body_preview)
    if not any("effect preview effect body writes must be false" in error for error in effect_body_errors):
        raise AssertionError(f"effect body write preview negative was not caught: {effect_body_errors}")

    missing_cleanup_scope_preview = deepcopy(source_preview)
    del _first_source_preview(missing_cleanup_scope_preview, "cleanup")["cleanup_scope_plan"]
    missing_cleanup_scope_errors = validate_repeated_entity_row_source_preview(missing_cleanup_scope_preview)
    if not any("source preview missing field(s)" in error for error in missing_cleanup_scope_errors):
        raise AssertionError(f"missing cleanup scope preview negative was not caught: {missing_cleanup_scope_errors}")

    missing_cleanup_coverage_preview = deepcopy(source_preview)
    _first_source_preview(missing_cleanup_coverage_preview, "cleanup")["cleanup_coverage"] = {}
    missing_cleanup_coverage_errors = validate_repeated_entity_row_source_preview(missing_cleanup_coverage_preview)
    if not any("cleanup preview missing cleanup coverage" in error for error in missing_cleanup_coverage_errors):
        raise AssertionError(f"missing cleanup coverage preview negative was not caught: {missing_cleanup_coverage_errors}")

    trigger_body_preview = deepcopy(source_preview)
    _first_source_preview(trigger_body_preview, "trigger")["trigger_body_writes_allowed"] = True
    trigger_body_errors = validate_repeated_entity_row_source_preview(trigger_body_preview)
    if not any("trigger preview trigger body writes must be false" in error for error in trigger_body_errors):
        raise AssertionError(f"trigger body write preview negative was not caught: {trigger_body_errors}")

    trigger_tooltip_preview = deepcopy(source_preview)
    _first_source_preview(trigger_tooltip_preview, "trigger")["tooltip_safe_unsafe_write_paths_allowed"] = True
    trigger_tooltip_errors = validate_repeated_entity_row_source_preview(trigger_tooltip_preview)
    if not any("trigger preview tooltip-safe unsafe write paths must be false" in error for error in trigger_tooltip_errors):
        raise AssertionError(f"trigger tooltip unsafe write path preview negative was not caught: {trigger_tooltip_errors}")

    missing_event_id_preview = deepcopy(source_preview)
    _first_source_preview(missing_event_id_preview, "event")["event_id_evidence"] = []
    missing_event_id_errors = validate_repeated_entity_row_source_preview(missing_event_id_preview)
    if not any("missing spec event IDs" in error for error in missing_event_id_errors):
        raise AssertionError(f"missing event ID preview negative was not caught: {missing_event_id_errors}")

    duplicate_event_id_preview = deepcopy(source_preview)
    duplicate_event_preview = _first_source_preview(duplicate_event_id_preview, "event")
    duplicate_event_preview["event_id_evidence"][1]["event_id"] = duplicate_event_preview["event_id_evidence"][0]["event_id"]
    duplicate_event_id_errors = validate_repeated_entity_row_source_preview(duplicate_event_id_preview)
    if not any("duplicate spec event IDs" in error for error in duplicate_event_id_errors):
        raise AssertionError(f"duplicate event ID preview negative was not caught: {duplicate_event_id_errors}")

    too_large_event_id_preview = deepcopy(source_preview)
    too_large_event_preview = _first_source_preview(too_large_event_id_preview, "event")
    too_large_event_preview["event_id_evidence"][0]["event_id"] = 10000
    too_large_event_preview["preview_event_id"] = 10000
    too_large_event_id_errors = validate_repeated_entity_row_source_preview(too_large_event_id_preview)
    if not any("event IDs must be <10000" in error for error in too_large_event_id_errors):
        raise AssertionError(f"large event ID preview negative was not caught: {too_large_event_id_errors}")

    missing_language_preview = deepcopy(source_preview)
    localization_preview = _first_source_preview(missing_language_preview, "localization")
    localization_preview["required_languages"] = ["english"]
    missing_language_errors = validate_repeated_entity_row_source_preview(missing_language_preview)
    if not any("missing English or Simplified Chinese" in error for error in missing_language_errors):
        raise AssertionError(f"missing localization language preview negative was not caught: {missing_language_errors}")

    duplicate_loc_key_preview = deepcopy(source_preview)
    first_localization_preview = _first_source_preview(duplicate_loc_key_preview, "localization")
    first_plan = first_localization_preview["loc_key_plan"]
    first_plan[1]["keys"] = deepcopy(first_plan[0]["keys"])
    duplicate_loc_key_errors = validate_repeated_entity_row_source_preview(duplicate_loc_key_preview)
    if not any("duplicate loc key" in error for error in duplicate_loc_key_errors):
        raise AssertionError(f"duplicate loc key preview negative was not caught: {duplicate_loc_key_errors}")

    unsafe_policy_preview = deepcopy(source_preview)
    unsafe_localization_preview = _first_source_preview(unsafe_policy_preview, "localization")
    unsafe_localization_preview["unsafe_quote_newline_handling_allowed"] = True
    unsafe_policy_errors = validate_repeated_entity_row_source_preview(unsafe_policy_preview)
    if not any("unsafe quote/newline policy must be false" in error for error in unsafe_policy_errors):
        raise AssertionError(f"unsafe quote/newline preview negative was not caught: {unsafe_policy_errors}")

    writable_preview = deepcopy(source_preview)
    _first_source_preview(writable_preview, "effect")["may_write_src"] = True
    writable_preview_errors = validate_repeated_entity_row_source_preview(writable_preview)
    if not any("may_write_src must be false" in error for error in writable_preview_errors):
        raise AssertionError(f"may_write_src preview negative was not caught: {writable_preview_errors}")

    writes_src_preview = deepcopy(source_preview)
    _first_source_preview(writes_src_preview, "trigger")["writes_src"] = True
    writes_src_preview_errors = validate_repeated_entity_row_source_preview(writes_src_preview)
    if not any("writes_src must be false" in error for error in writes_src_preview_errors):
        raise AssertionError(f"writes_src preview negative was not caught: {writes_src_preview_errors}")

    cleanup_may_write_src_preview = deepcopy(source_preview)
    _first_source_preview(cleanup_may_write_src_preview, "cleanup")["may_write_src"] = True
    cleanup_may_write_src_errors = validate_repeated_entity_row_source_preview(cleanup_may_write_src_preview)
    if not any("may_write_src must be false" in error for error in cleanup_may_write_src_errors):
        raise AssertionError(f"cleanup may_write_src preview negative was not caught: {cleanup_may_write_src_errors}")

    gui_aggregate_only_preview = deepcopy(source_preview)
    _first_source_preview(gui_aggregate_only_preview, "gui")["aggregate_only_display_allowed"] = True
    gui_aggregate_only_errors = validate_repeated_entity_row_source_preview(gui_aggregate_only_preview)
    if not any("GUI preview aggregate-only display must be false" in error for error in gui_aggregate_only_errors):
        raise AssertionError(f"GUI aggregate-only preview negative was not caught: {gui_aggregate_only_errors}")

    gui_body_preview = deepcopy(source_preview)
    _first_source_preview(gui_body_preview, "gui")["gui_source_body_allowed"] = True
    gui_body_errors = validate_repeated_entity_row_source_preview(gui_body_preview)
    if not any("GUI preview GUI body writes must be false" in error for error in gui_body_errors):
        raise AssertionError(f"GUI body write preview negative was not caught: {gui_body_errors}")

    gui_source_write_preview = deepcopy(source_preview)
    _first_source_preview(gui_source_write_preview, "gui")["gui_source_writes_allowed"] = True
    gui_source_write_errors = validate_repeated_entity_row_source_preview(gui_source_write_preview)
    if not any("GUI preview GUI source writes must be false" in error for error in gui_source_write_errors):
        raise AssertionError(f"GUI source write preview negative was not caught: {gui_source_write_errors}")

    missing_gui_widget_preview = deepcopy(source_preview)
    del _first_source_preview(missing_gui_widget_preview, "gui")["fixed_row_widget_plan"]
    missing_gui_widget_errors = validate_repeated_entity_row_source_preview(missing_gui_widget_preview)
    if not any("source preview missing field(s)" in error for error in missing_gui_widget_errors):
        raise AssertionError(f"missing GUI row widget preview negative was not caught: {missing_gui_widget_errors}")

    missing_gui_binding_preview = deepcopy(source_preview)
    del _first_source_preview(missing_gui_binding_preview, "gui")["per_row_variable_binding_plan"]
    missing_gui_binding_errors = validate_repeated_entity_row_source_preview(missing_gui_binding_preview)
    if not any("source preview missing field(s)" in error for error in missing_gui_binding_errors):
        raise AssertionError(f"missing GUI per-row binding preview negative was not caught: {missing_gui_binding_errors}")

    missing_gui_tooltip_preview = deepcopy(source_preview)
    del _first_source_preview(missing_gui_tooltip_preview, "gui")["tooltip_localization_linkage"]
    missing_gui_tooltip_errors = validate_repeated_entity_row_source_preview(missing_gui_tooltip_preview)
    if not any("source preview missing field(s)" in error for error in missing_gui_tooltip_errors):
        raise AssertionError(f"missing GUI tooltip/localization preview negative was not caught: {missing_gui_tooltip_errors}")

    gui_may_write_src_preview = deepcopy(source_preview)
    _first_source_preview(gui_may_write_src_preview, "gui")["may_write_src"] = True
    gui_may_write_src_errors = validate_repeated_entity_row_source_preview(gui_may_write_src_preview)
    if not any("may_write_src must be false" in error for error in gui_may_write_src_errors):
        raise AssertionError(f"GUI may_write_src preview negative was not caught: {gui_may_write_src_errors}")

    listener_non_alhambra_preview = deepcopy(source_preview)
    _first_source_preview(listener_non_alhambra_preview, "listener")["pilot_key"] = "unique_dome_of_the_rock"
    listener_non_alhambra_errors = validate_repeated_entity_row_source_preview(listener_non_alhambra_preview)
    if not any("listener preview must be Alhambra-only" in error for error in listener_non_alhambra_errors):
        raise AssertionError(f"non-Alhambra listener preview negative was not caught: {listener_non_alhambra_errors}")

    listener_body_preview = deepcopy(source_preview)
    _first_source_preview(listener_body_preview, "listener")["listener_body_allowed"] = True
    listener_body_errors = validate_repeated_entity_row_source_preview(listener_body_preview)
    if not any("listener preview listener body writes must be false" in error for error in listener_body_errors):
        raise AssertionError(f"listener body write preview negative was not caught: {listener_body_errors}")

    listener_war_scope_preview = deepcopy(source_preview)
    _first_source_preview(listener_war_scope_preview, "listener")["war_scope_writes_allowed"] = True
    listener_war_scope_errors = validate_repeated_entity_row_source_preview(listener_war_scope_preview)
    if not any("listener preview war scope writes must be false" in error for error in listener_war_scope_errors):
        raise AssertionError(f"listener war scope write preview negative was not caught: {listener_war_scope_errors}")

    missing_listener_hook_preview = deepcopy(source_preview)
    del _first_source_preview(missing_listener_hook_preview, "listener")["on_action_hook_linkage_plan"]
    missing_listener_hook_errors = validate_repeated_entity_row_source_preview(missing_listener_hook_preview)
    if not any("source preview missing field(s)" in error for error in missing_listener_hook_errors):
        raise AssertionError(f"missing listener hook linkage preview negative was not caught: {missing_listener_hook_errors}")

    missing_listener_trigger_preview = deepcopy(source_preview)
    del _first_source_preview(missing_listener_trigger_preview, "listener")["selected_ritual_trigger_linkage"]
    missing_listener_trigger_errors = validate_repeated_entity_row_source_preview(missing_listener_trigger_preview)
    if not any("source preview missing field(s)" in error for error in missing_listener_trigger_errors):
        raise AssertionError(
            f"missing listener selected ritual trigger preview negative was not caught: {missing_listener_trigger_errors}"
        )

    listener_writes_src_preview = deepcopy(source_preview)
    _first_source_preview(listener_writes_src_preview, "listener")["writes_src"] = True
    listener_writes_src_errors = validate_repeated_entity_row_source_preview(listener_writes_src_preview)
    if not any("writes_src must be false" in error for error in listener_writes_src_errors):
        raise AssertionError(f"listener writes_src preview negative was not caught: {listener_writes_src_errors}")

    source_writer_readiness = repeated_entity_row_source_writer_readiness_for_payload(
        spec_data,
        source_plan=source_plan,
        source_preview=source_preview,
    )
    if source_writer_readiness["validation_errors"]:
        raise AssertionError(
            "repeated-row source-writer readiness unexpectedly failed validation: "
            f"{source_writer_readiness['validation_errors']}"
        )
    if source_writer_readiness.get("artifact_count") != 177:
        raise AssertionError(
            "expected 177 repeated-row source-writer readiness artifacts, got "
            f"{source_writer_readiness.get('artifact_count')}"
        )
    if source_writer_readiness.get("source_plan_artifact_count") != 177:
        raise AssertionError(f"source-writer readiness should preserve 177-artifact source-plan: {source_writer_readiness}")
    if source_writer_readiness.get("source_preview_count") != 177:
        raise AssertionError(f"source-writer readiness should preserve 177 source previews: {source_writer_readiness}")
    if source_writer_readiness.get("ready_artifact_count") != 0:
        raise AssertionError(f"source-writer readiness must not mark artifacts ready: {source_writer_readiness}")
    if source_writer_readiness.get("blocked_artifact_count") != 177:
        raise AssertionError(f"source-writer readiness must keep every artifact blocked: {source_writer_readiness}")
    if source_writer_readiness.get("source_writer_allowed") is not False:
        raise AssertionError(f"source-writer readiness source_writer_allowed changed: {source_writer_readiness}")
    if source_writer_readiness.get("may_write_src_allowed") is not False:
        raise AssertionError(f"source-writer readiness may_write_src_allowed changed: {source_writer_readiness}")
    if source_writer_readiness.get("writes_src") is not False:
        raise AssertionError(f"source-writer readiness writes_src changed: {source_writer_readiness}")
    if source_writer_readiness.get("contract_family_summary") != expected_preview_family_counts:
        raise AssertionError(
            "source-writer readiness family summary changed: "
            f"{source_writer_readiness.get('contract_family_summary')}"
        )
    readiness_evidence_fields = {
        "eu5_syntax_evidence",
        "generator_ownership_evidence",
        "source_target_boundary_evidence",
        "validation_coverage_evidence",
        "lifecycle_semantics_evidence",
    }
    readiness_family_counts = {family: 0 for family in expected_preview_family_counts}
    readiness_identities: set[tuple[str, str, str]] = set()
    closure_family_counts = {family: 0 for family in expected_preview_family_counts}
    closure_pilots_by_family = {family: set() for family in closure_family_counts}
    if source_writer_readiness.get("closure_contract_count") != 177:
        raise AssertionError(
            "source-writer readiness should expose 177 closure contracts, got "
            f"{source_writer_readiness.get('closure_contract_count')}"
        )
    if source_writer_readiness.get("closure_family_summary") != expected_preview_family_counts:
        raise AssertionError(
            "source-writer readiness closure family summary changed: "
            f"{source_writer_readiness.get('closure_family_summary')}"
        )
    if source_writer_readiness.get("closure_missing_families") != []:
        raise AssertionError(
            "source-writer readiness closure missing families changed: "
            f"{source_writer_readiness.get('closure_missing_families')}"
        )
    if source_writer_readiness.get("closure_no_write_violation_count") != 0:
        raise AssertionError(
            "source-writer readiness closure no-write violation count changed: "
            f"{source_writer_readiness.get('closure_no_write_violation_count')}"
        )
    for entry_readiness in source_writer_readiness.get("entries", []) or []:
        if entry_readiness.get("source_writer_allowed") is not False:
            raise AssertionError(f"entry source-writer readiness source_writer_allowed changed: {entry_readiness}")
        if entry_readiness.get("may_write_src_allowed") is not False:
            raise AssertionError(f"entry source-writer readiness may_write_src_allowed changed: {entry_readiness}")
        if entry_readiness.get("writes_src") is not False:
            raise AssertionError(f"entry source-writer readiness writes_src changed: {entry_readiness}")
        if entry_readiness.get("ready_artifact_count") != 0:
            raise AssertionError(f"entry source-writer readiness should keep ready count at zero: {entry_readiness}")
        artifacts = entry_readiness.get("artifacts", []) or []
        if entry_readiness.get("blocked_artifact_count") != len(artifacts):
            raise AssertionError(f"entry source-writer readiness blocked count mismatch: {entry_readiness}")
        for artifact in artifacts:
            identity = (artifact.get("pilot_key"), artifact.get("row_set_key"), artifact.get("artifact_kind"))
            if identity in readiness_identities:
                raise AssertionError(f"duplicate source-writer readiness artifact identity: {identity}")
            readiness_identities.add(identity)
            family = artifact.get("contract_family")
            if family not in readiness_family_counts:
                raise AssertionError(f"unsupported source-writer readiness family: {artifact}")
            readiness_family_counts[family] += 1
            if artifact.get("preview_exists") is not True:
                raise AssertionError(f"source-writer readiness lost preview match: {artifact}")
            if artifact.get("current_contract_status") != "blocked":
                raise AssertionError(f"source-writer readiness contract status changed: {artifact}")
            if artifact.get("readiness_status") != "blocked":
                raise AssertionError(f"source-writer readiness promoted an artifact: {artifact}")
            if artifact.get("source_writer_allowed") is not False:
                raise AssertionError(f"source-writer readiness source_writer_allowed changed: {artifact}")
            if artifact.get("may_write_src") is not False:
                raise AssertionError(f"source-writer readiness may_write_src changed: {artifact}")
            if artifact.get("writes_src") is not False:
                raise AssertionError(f"source-writer readiness writes_src changed: {artifact}")
            if not artifact.get("unresolved_writer_blockers"):
                raise AssertionError(f"source-writer readiness lost blockers: {artifact}")
            contract_evidence = artifact.get("no_write_source_writer_contract_evidence")
            if not isinstance(contract_evidence, dict):
                raise AssertionError(f"source-writer readiness lost no-write contract evidence: {artifact}")
            if contract_evidence.get("artifact_kind") != artifact.get("artifact_kind"):
                raise AssertionError(f"no-write contract evidence artifact kind changed: {contract_evidence}")
            if contract_evidence.get("contract_family") != family:
                raise AssertionError(f"no-write contract evidence family changed: {contract_evidence}")
            target_paths = contract_evidence.get("target_paths")
            if not isinstance(target_paths, list) or not target_paths:
                raise AssertionError(f"no-write contract evidence lost target path: {contract_evidence}")
            if contract_evidence.get("target_path") not in target_paths:
                raise AssertionError(f"no-write contract evidence target_path is not explicit: {contract_evidence}")
            if any(not str(path).startswith("src/") or "<" in str(path) for path in target_paths):
                raise AssertionError(f"no-write contract evidence target paths must be explicit src paths: {contract_evidence}")
            if family == "localization" and len(target_paths) != 2:
                raise AssertionError(f"localization no-write evidence must expose split target paths: {contract_evidence}")
            if family != "localization" and len(target_paths) != 1:
                raise AssertionError(f"{family} no-write evidence should expose one target path: {contract_evidence}")
            if not contract_evidence.get("owner_generator") or not contract_evidence.get("owner_generator_candidate"):
                raise AssertionError(f"no-write contract evidence lost owner generator candidate: {contract_evidence}")
            syntax_evidence = contract_evidence.get("eu5_syntax_evidence")
            if (
                not isinstance(syntax_evidence, dict)
                or not syntax_evidence.get("summary")
                or not syntax_evidence.get("paths")
            ):
                raise AssertionError(f"no-write contract evidence lost EU5 syntax evidence: {contract_evidence}")
            commands = contract_evidence.get("verification_commands")
            if (
                not isinstance(commands, list)
                or not any("scripts\\test_unique_wonder_ritual_harness.py" in command for command in commands)
                or not any("scripts\\validate.py --changed --fix --ai-report" in command for command in commands)
            ):
                raise AssertionError(f"no-write contract evidence lost validation commands: {contract_evidence}")
            if not contract_evidence.get("validation_refs"):
                raise AssertionError(f"no-write contract evidence lost validation refs: {contract_evidence}")
            if (
                not contract_evidence.get("source_writer_blocker_reasons")
                or not contract_evidence.get("source_writer_still_blocked_reason")
            ):
                raise AssertionError(f"no-write contract evidence lost blocker reason: {contract_evidence}")
            if (
                contract_evidence.get("source_writer_allowed") is not False
                or contract_evidence.get("may_write_src") is not False
                or contract_evidence.get("writes_src") is not False
            ):
                raise AssertionError(f"no-write contract evidence allowed source writing: {contract_evidence}")
            if family == "event":
                closure_family_counts["event"] += 1
                closure_pilots_by_family["event"].add(str(artifact.get("pilot_key", "")))
                closure = artifact.get("closure_contract")
                if not isinstance(closure, dict):
                    raise AssertionError(f"event readiness lost closure contract: {artifact}")
                if closure.get("namespace") != "tv_engineering_department":
                    raise AssertionError(f"event closure namespace changed: {closure}")
                if closure.get("future_source_target_path") != _repeated_row_event_contract_path(artifact["pilot_key"]):
                    raise AssertionError(f"event closure future target changed: {closure}")
                if closure.get("may_write_src") is not False or closure.get("writes_src") is not False:
                    raise AssertionError(f"event closure no-write boundary changed: {closure}")
                if closure.get("source_writer_allowed") is not False or closure.get("readiness_status") != "blocked":
                    raise AssertionError(f"event closure source-writer boundary changed: {closure}")
                if not closure.get("event_id_evidence") or not closure.get("node_event_id_evidence"):
                    raise AssertionError(f"event closure lost event id evidence: {closure}")
                body = closure.get("source_body_preview")
                if not isinstance(body, dict) or body.get("namespace") != "tv_engineering_department":
                    raise AssertionError(f"event closure lost source body preview: {closure}")
                loc_handoff = closure.get("localization_key_handoff")
                if not isinstance(loc_handoff, dict) or not {
                    "title_key",
                    "desc_key",
                    "option_keys",
                } <= set(loc_handoff):
                    raise AssertionError(f"event closure lost localization handoff: {closure}")
                option_handoff = closure.get("option_effect_handoff")
                if not isinstance(option_handoff, dict) or option_handoff.get("handoff_only") is not True:
                    raise AssertionError(f"event closure lost option-effect handoff: {closure}")
                safety = closure.get("safety_notes")
                if (
                    not isinstance(safety, dict)
                    or safety.get("hidden_executor_handoff_only") is not True
                    or safety.get("tooltip_heavy_finalization_allowed") is not False
                    or safety.get("row_state_writes_allowed") is not False
                ):
                    raise AssertionError(f"event closure lost hidden-executor/tooltip safety: {closure}")
            elif family == "localization":
                closure_family_counts["localization"] += 1
                closure_pilots_by_family["localization"].add(str(artifact.get("pilot_key", "")))
                closure = artifact.get("closure_contract")
                if not isinstance(closure, dict):
                    raise AssertionError(f"localization readiness lost closure contract: {artifact}")
                if closure.get("future_source_target_path_pattern") != (
                    "src/main_menu/localization/<lang>/tv_wonder_unique_<wonder_key>_ritual_l_<lang>.yml"
                ):
                    raise AssertionError(f"localization closure future target pattern changed: {closure}")
                if closure.get("future_source_target_path") != _repeated_row_localization_contract_path(artifact["pilot_key"]):
                    raise AssertionError(f"localization closure future target changed: {closure}")
                if closure.get("may_write_src") is not False or closure.get("writes_src") is not False:
                    raise AssertionError(f"localization closure no-write boundary changed: {closure}")
                if closure.get("source_writer_allowed") is not False or closure.get("readiness_status") != "blocked":
                    raise AssertionError(f"localization closure source-writer boundary changed: {closure}")
                language_boundary = closure.get("language_ownership_boundary")
                if (
                    not isinstance(language_boundary, dict)
                    or set(language_boundary.get("required_languages", [])) != {"english", "simp_chinese"}
                    or language_boundary.get("missing_bilingual_coverage_allowed") is not False
                ):
                    raise AssertionError(f"localization closure lost bilingual boundary: {closure}")
                event_handoff = closure.get("event_key_handoff")
                if not isinstance(event_handoff, dict) or not {
                    "title_key",
                    "desc_key",
                    "option_key_pattern",
                } <= set(event_handoff):
                    raise AssertionError(f"localization closure lost event key handoff: {closure}")
                key_allocation = closure.get("key_allocation")
                required_groups = {"row_labels", "status_text", "incident_text", "tooltips", "summary_text"}
                if (
                    not isinstance(key_allocation, dict)
                    or not required_groups <= set(key_allocation.get("required_groups", []))
                    or not required_groups <= set((key_allocation.get("row_key_groups") or {}).keys())
                    or not key_allocation.get("loc_key_plan")
                ):
                    raise AssertionError(f"localization closure lost key allocation: {closure}")
                escaping = closure.get("escaping_bom_boundary")
                if (
                    not isinstance(escaping, dict)
                    or escaping.get("quote_escaped") is not True
                    or escaping.get("newline_escaped") is not True
                    or escaping.get("bom_encoding") != "utf-8-sig"
                    or escaping.get("writes_file") is not False
                ):
                    raise AssertionError(f"localization closure lost escaping/BOM boundary: {closure}")
            elif family == "effect":
                closure_family_counts["effect"] += 1
                closure_pilots_by_family["effect"].add(str(artifact.get("pilot_key", "")))
                closure = artifact.get("closure_contract")
                if not isinstance(closure, dict):
                    raise AssertionError(f"effect readiness lost closure contract: {artifact}")
                if closure.get("future_source_target_path") != _repeated_row_effect_contract_path(artifact["pilot_key"]):
                    raise AssertionError(f"effect closure future target changed: {closure}")
                if closure.get("source_type") != "common/scripted_effects":
                    raise AssertionError(f"effect closure source type changed: {closure}")
                if closure.get("may_write_src") is not False or closure.get("writes_src") is not False:
                    raise AssertionError(f"effect closure no-write boundary changed: {closure}")
                if closure.get("source_writer_allowed") is not False or closure.get("readiness_status") != "blocked":
                    raise AssertionError(f"effect closure source-writer boundary changed: {closure}")
                if (
                    closure.get("effect_body_writes_allowed") is not False
                    or closure.get("row_state_writes_allowed") is not False
                    or closure.get("row_state_write_schema_allowed") is not False
                ):
                    raise AssertionError(f"effect closure allowed scripted-effect writes: {closure}")
                operation_coverage = closure.get("effect_operation_coverage")
                required_operations = {
                    "row_init",
                    "row_state_write",
                    "branch_write",
                    "aggregate_refresh",
                    "cleanup_write_handoff",
                }
                if (
                    not isinstance(operation_coverage, dict)
                    or not required_operations <= set(operation_coverage.get("required_operations", []))
                    or operation_coverage.get("effect_body_emitted") is not False
                ):
                    raise AssertionError(f"effect closure lost operation coverage: {closure}")
                schema_boundary = closure.get("row_state_schema_boundary")
                if (
                    not isinstance(schema_boundary, dict)
                    or schema_boundary.get("schema_contract_only") is not True
                    or schema_boundary.get("row_state_write_schema_allowed") is not False
                    or not schema_boundary.get("entity_keys")
                ):
                    raise AssertionError(f"effect closure lost row-state schema boundary: {closure}")
                aggregate_boundary = closure.get("aggregate_refresh_boundary")
                if (
                    not isinstance(aggregate_boundary, dict)
                    or not isinstance(aggregate_boundary.get("aggregate_projection_refs"), list)
                    or not str(aggregate_boundary.get("aggregate_projection_boundary", "")).strip()
                    or aggregate_boundary.get("body_emitted") is not False
                ):
                    raise AssertionError(f"effect closure lost aggregate refresh boundary: {closure}")
                cleanup_handoff = closure.get("cleanup_write_handoff")
                if (
                    not isinstance(cleanup_handoff, dict)
                    or cleanup_handoff.get("handoff_only") is not True
                    or cleanup_handoff.get("cleanup_source_writer_allowed") is not False
                    or cleanup_handoff.get("body_emitted") is not False
                ):
                    raise AssertionError(f"effect closure lost cleanup write handoff: {closure}")
            elif family == "cleanup":
                closure_family_counts["cleanup"] += 1
                closure_pilots_by_family["cleanup"].add(str(artifact.get("pilot_key", "")))
                closure = artifact.get("closure_contract")
                if not isinstance(closure, dict):
                    raise AssertionError(f"cleanup readiness lost closure contract: {artifact}")
                if closure.get("future_source_target_path") != _repeated_row_effect_contract_path(artifact["pilot_key"]):
                    raise AssertionError(f"cleanup closure future target changed: {closure}")
                if closure.get("source_type") != "common/scripted_effects":
                    raise AssertionError(f"cleanup closure source type changed: {closure}")
                if closure.get("may_write_src") is not False or closure.get("writes_src") is not False:
                    raise AssertionError(f"cleanup closure no-write boundary changed: {closure}")
                if closure.get("source_writer_allowed") is not False or closure.get("readiness_status") != "blocked":
                    raise AssertionError(f"cleanup closure source-writer boundary changed: {closure}")
                if (
                    closure.get("effect_body_writes_allowed") is not False
                    or closure.get("row_state_write_schema_allowed") is not False
                ):
                    raise AssertionError(f"cleanup closure allowed scripted-effect writes: {closure}")
                if (
                    closure.get("cleanup_lifecycle_scope")
                    != REPEATED_ROW_EFFECT_CLEANUP_CONTRACT_CLEANUP_SCOPES[artifact["artifact_kind"]]
                ):
                    raise AssertionError(f"cleanup closure lost lifecycle scope: {closure}")
                coverage = closure.get("cleanup_coverage")
                if (
                    not isinstance(coverage, dict)
                    or not {"completion", "failure", "ownership_loss", "ritual_reset"} <= set(coverage)
                ):
                    raise AssertionError(f"cleanup closure lost cleanup coverage: {closure}")
                ownership_reset = closure.get("ownership_reset_branch_boundary")
                if (
                    not isinstance(ownership_reset, dict)
                    or not {"ownership_loss", "ritual_reset"} <= set(ownership_reset.get("required_branches", []))
                    or ownership_reset.get("ownership_loss_planned") is not True
                    or ownership_reset.get("ritual_reset_planned") is not True
                ):
                    raise AssertionError(f"cleanup closure lost ownership/reset branch: {closure}")
                lifecycle = closure.get("row_entity_lifecycle_coverage")
                if (
                    not isinstance(lifecycle, dict)
                    or not lifecycle.get("entity_keys")
                    or lifecycle.get("row_state_write_schema_allowed") is not False
                ):
                    raise AssertionError(f"cleanup closure lost row/entity lifecycle coverage: {closure}")
                aggregate_boundary = closure.get("aggregate_projection_boundary")
                if (
                    not isinstance(aggregate_boundary, dict)
                    or not isinstance(aggregate_boundary.get("aggregate_projection_refs"), list)
                    or not str(aggregate_boundary.get("aggregate_projection_boundary", "")).strip()
                    or aggregate_boundary.get("body_emitted") is not False
                ):
                    raise AssertionError(f"cleanup closure lost aggregate projection boundary: {closure}")
            elif family == "trigger":
                closure_family_counts["trigger"] += 1
                closure_pilots_by_family["trigger"].add(str(artifact.get("pilot_key", "")))
                closure = artifact.get("closure_contract")
                if not isinstance(closure, dict):
                    raise AssertionError(f"trigger readiness lost closure contract: {artifact}")
                if closure.get("future_source_target_path") != _repeated_row_trigger_contract_path(artifact["pilot_key"]):
                    raise AssertionError(f"trigger closure future target changed: {closure}")
                if closure.get("source_type") != "common/scripted_triggers":
                    raise AssertionError(f"trigger closure source type changed: {closure}")
                if closure.get("may_write_src") is not False or closure.get("writes_src") is not False:
                    raise AssertionError(f"trigger closure no-write boundary changed: {closure}")
                if closure.get("source_writer_allowed") is not False or closure.get("readiness_status") != "blocked":
                    raise AssertionError(f"trigger closure source-writer boundary changed: {closure}")
                if (
                    closure.get("trigger_body_writes_allowed") is not False
                    or closure.get("tooltip_safe_unsafe_write_paths_allowed") is not False
                ):
                    raise AssertionError(f"trigger closure allowed scripted-trigger writes: {closure}")
                condition_coverage = closure.get("condition_group_coverage")
                if (
                    not isinstance(condition_coverage, dict)
                    or not {"eligibility", "row_completion", "tooltip_safe"}
                    <= set(condition_coverage.get("required_groups", []))
                    or not isinstance(condition_coverage.get("eligibility"), dict)
                    or not isinstance(condition_coverage.get("row_completion"), dict)
                    or not isinstance(condition_coverage.get("tooltip_safe"), dict)
                ):
                    raise AssertionError(f"trigger closure lost condition group coverage: {closure}")
                forbidden_paths = closure.get("forbidden_write_paths")
                if (
                    not isinstance(forbidden_paths, dict)
                    or not {"tooltip", "pre_evaluation"} <= set(forbidden_paths.get("forbidden_contexts", []))
                    or forbidden_paths.get("unsafe_effect_calls_allowed") is not False
                    or forbidden_paths.get("row_state_writes_allowed") is not False
                    or forbidden_paths.get("source_writes_allowed") is not False
                ):
                    raise AssertionError(f"trigger closure lost forbidden write paths: {closure}")
            elif family == "gui":
                closure_family_counts["gui"] += 1
                closure_pilots_by_family["gui"].add(str(artifact.get("pilot_key", "")))
                closure = artifact.get("closure_contract")
                if not isinstance(closure, dict):
                    raise AssertionError(f"GUI readiness lost closure contract: {artifact}")
                if closure.get("future_source_target_path") != _repeated_row_gui_contract_path(artifact["pilot_key"]):
                    raise AssertionError(f"GUI closure future target changed: {closure}")
                if closure.get("source_type") != "in_game/gui/panels/organization":
                    raise AssertionError(f"GUI closure source type changed: {closure}")
                if closure.get("may_write_src") is not False or closure.get("writes_src") is not False:
                    raise AssertionError(f"GUI closure no-write boundary changed: {closure}")
                if closure.get("source_writer_allowed") is not False or closure.get("readiness_status") != "blocked":
                    raise AssertionError(f"GUI closure source-writer boundary changed: {closure}")
                if (
                    closure.get("aggregate_only_display_allowed") is not False
                    or closure.get("gui_source_body_allowed") is not False
                    or closure.get("gui_source_writes_allowed") is not False
                    or closure.get("row_state_writes_allowed") is not False
                ):
                    raise AssertionError(f"GUI closure allowed forbidden UI/source writes: {closure}")
                body = closure.get("source_body_preview")
                if not isinstance(body, dict) or body.get("no_gui_source_body") is not True:
                    raise AssertionError(f"GUI closure lost source body blocker: {closure}")
                fixed_plan = closure.get("fixed_row_widget_plan")
                if (
                    not isinstance(fixed_plan, dict)
                    or fixed_plan.get("row_widget_fixed") is not True
                    or fixed_plan.get("body_emitted") is not False
                ):
                    raise AssertionError(f"GUI closure lost fixed row widget plan: {closure}")
                binding_plan = closure.get("per_row_variable_binding_plan")
                if (
                    not isinstance(binding_plan, dict)
                    or binding_plan.get("binds_design_ir_tracked_entity_sets") is not True
                    or binding_plan.get("aggregate_only_row_reads_allowed") is not False
                    or not binding_plan.get("entity_keys")
                ):
                    raise AssertionError(f"GUI closure lost per-row binding plan: {closure}")
                row_policy = closure.get("actor_checklist_incident_row_policy")
                if (
                    not isinstance(row_policy, dict)
                    or row_policy.get("distinct_row_policies_required") is not True
                    or row_policy.get("aggregate_only_display_allowed") is not False
                ):
                    raise AssertionError(f"GUI closure lost actor/checklist/incident row policy: {closure}")
                tooltip_linkage = closure.get("tooltip_localization_linkage")
                if (
                    not isinstance(tooltip_linkage, dict)
                    or not tooltip_linkage.get("row_label_keys")
                    or not tooltip_linkage.get("tooltip_keys")
                ):
                    raise AssertionError(f"GUI closure lost tooltip/localization linkage: {closure}")
                key_linkage = closure.get("gui_event_localization_key_linkage")
                if (
                    not isinstance(key_linkage, dict)
                    or key_linkage.get("localization_linkage_only") is not True
                    or key_linkage.get("source_body_emitted") is not False
                    or key_linkage.get("gui_source_writer_allowed") is not False
                ):
                    raise AssertionError(f"GUI closure lost GUI/event/localization key linkage: {closure}")
                aggregate_boundary = closure.get("aggregate_projection_boundary")
                if (
                    not isinstance(aggregate_boundary, dict)
                    or not isinstance(aggregate_boundary.get("aggregate_projection_refs"), list)
                    or not str(aggregate_boundary.get("aggregate_projection_boundary", "")).strip()
                    or aggregate_boundary.get("aggregate_only_display_allowed") is not False
                ):
                    raise AssertionError(f"GUI closure lost aggregate projection boundary: {closure}")
            elif family == "listener":
                closure_family_counts["listener"] += 1
                closure_pilots_by_family["listener"].add(str(artifact.get("pilot_key", "")))
                closure = artifact.get("closure_contract")
                if not isinstance(closure, dict):
                    raise AssertionError(f"listener readiness lost closure contract: {artifact}")
                if artifact.get("pilot_key") != "unique_alhambra" or artifact.get("artifact_kind") != "listener_war_integration":
                    raise AssertionError(f"listener closure should be Alhambra-only: {artifact}")
                if closure.get("future_source_target_path") != _repeated_row_listener_contract_path(artifact["pilot_key"]):
                    raise AssertionError(f"listener closure future target changed: {closure}")
                if closure.get("listener_artifact_scope") != "unique_alhambra-only listener_war_integration":
                    raise AssertionError(f"listener closure scope changed: {closure}")
                if closure.get("may_write_src") is not False or closure.get("writes_src") is not False:
                    raise AssertionError(f"listener closure no-write boundary changed: {closure}")
                if closure.get("source_writer_allowed") is not False or closure.get("readiness_status") != "blocked":
                    raise AssertionError(f"listener closure source-writer boundary changed: {closure}")
                if (
                    closure.get("listener_body_allowed") is not False
                    or closure.get("listener_scope_writes_allowed") is not False
                    or closure.get("war_scope_writes_allowed") is not False
                    or closure.get("source_writes_allowed") is not False
                ):
                    raise AssertionError(f"listener closure allowed forbidden writes: {closure}")
                body = closure.get("source_body_preview")
                if not isinstance(body, dict) or body.get("no_listener_body") is not True:
                    raise AssertionError(f"listener closure emitted listener body: {closure}")
                hook_plan = closure.get("on_action_hook_linkage_plan")
                if (
                    not isinstance(hook_plan, dict)
                    or not {"on_pre_winning_war", "on_ending_war"} <= set(hook_plan.get("hooks", []))
                    or hook_plan.get("body_emitted") is not False
                ):
                    raise AssertionError(f"listener closure lost hook linkage plan: {closure}")
                trigger_linkage = closure.get("selected_ritual_trigger_linkage")
                if (
                    not isinstance(trigger_linkage, dict)
                    or trigger_linkage.get("trigger_name")
                    != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
                    or trigger_linkage.get("linkage_only") is not True
                ):
                    raise AssertionError(f"listener closure lost selected ritual trigger linkage: {closure}")
                war_scope_plan = closure.get("war_scope_availability_persistence_plan")
                if (
                    not isinstance(war_scope_plan, dict)
                    or war_scope_plan.get("persistence_contract_only") is not True
                    or war_scope_plan.get("war_scope_writes_allowed") is not False
                ):
                    raise AssertionError(f"listener closure lost war scope availability plan: {closure}")
                handoff_boundary = closure.get("row_state_handoff_boundary")
                if (
                    not isinstance(handoff_boundary, dict)
                    or handoff_boundary.get("handoff_only") is not True
                    or handoff_boundary.get("row_state_writes_allowed") is not False
                    or not handoff_boundary.get("entity_keys")
                ):
                    raise AssertionError(f"listener closure lost row-state handoff boundary: {closure}")
            for evidence_field in readiness_evidence_fields:
                evidence = artifact.get(evidence_field)
                if not isinstance(evidence, dict):
                    raise AssertionError(f"{evidence_field} missing readiness evidence block: {artifact}")
                if evidence.get("status") in {"verified", "source_ready", "source-ready"}:
                    raise AssertionError(f"{evidence_field} claimed verified/source-ready: {evidence}")
                if evidence.get("evidence_type") in {"verified", "source_ready", "source-ready"}:
                    raise AssertionError(f"{evidence_field} claimed verified/source-ready evidence type: {evidence}")
                if not isinstance(evidence.get("paths"), list):
                    raise AssertionError(f"{evidence_field} paths must be a list: {evidence}")
                if not isinstance(evidence.get("anchors"), dict):
                    raise AssertionError(f"{evidence_field} anchors must be a mapping: {evidence}")
                if not evidence.get("blockers"):
                    raise AssertionError(f"{evidence_field} must retain blockers: {evidence}")
    if len(readiness_identities) != 177:
        raise AssertionError(f"source-writer readiness identity coverage changed: {len(readiness_identities)}")
    for family, expected_count in expected_preview_family_counts.items():
        if readiness_family_counts[family] != expected_count:
            raise AssertionError(f"expected {expected_count} {family} readiness artifacts, got {readiness_family_counts[family]}")
    expected_closure_family_counts = dict(expected_preview_family_counts)
    for family, expected_count in expected_closure_family_counts.items():
        if closure_family_counts[family] != expected_count:
            raise AssertionError(f"expected {expected_count} {family} closure artifacts, got {closure_family_counts[family]}")
        expected_pilots = {"unique_alhambra"} if family == "listener" else set(REPEATED_ROW_PILOTS)
        if closure_pilots_by_family[family] != expected_pilots:
            raise AssertionError(f"{family} closure pilot coverage changed: {closure_pilots_by_family[family]}")

    missing_preview_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_preview_readiness, "event")["preview_exists"] = False
    missing_preview_errors = validate_repeated_entity_row_source_writer_readiness(missing_preview_readiness)
    if not any("missing preview" in error for error in missing_preview_errors):
        raise AssertionError(f"missing preview readiness negative was not caught: {missing_preview_errors}")

    missing_source_plan_readiness = deepcopy(source_writer_readiness)
    missing_source_plan_readiness["source_plan_artifact_count"] = 176
    missing_source_plan_errors = validate_repeated_entity_row_source_writer_readiness(missing_source_plan_readiness)
    if not any("177-artifact source-plan" in error for error in missing_source_plan_errors):
        raise AssertionError(f"missing source-plan readiness negative was not caught: {missing_source_plan_errors}")

    missing_evidence_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_evidence_readiness, "localization")["eu5_syntax_evidence"]
    missing_evidence_errors = validate_repeated_entity_row_source_writer_readiness(missing_evidence_readiness)
    if not any("missing field(s)" in error for error in missing_evidence_errors):
        raise AssertionError(f"missing evidence block readiness negative was not caught: {missing_evidence_errors}")

    missing_no_write_contract_evidence_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_no_write_contract_evidence_readiness, "event")[
        "no_write_source_writer_contract_evidence"
    ]
    missing_no_write_contract_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_no_write_contract_evidence_readiness
    )
    if not any("no_write_source_writer_contract_evidence" in error for error in missing_no_write_contract_errors):
        raise AssertionError(
            "missing no-write source-writer contract evidence negative was not caught: "
            f"{missing_no_write_contract_errors}"
        )

    missing_contract_target_readiness = deepcopy(source_writer_readiness)
    missing_contract_target = _first_readiness_artifact(missing_contract_target_readiness, "cleanup")[
        "no_write_source_writer_contract_evidence"
    ]
    missing_contract_target["target_path"] = ""
    missing_contract_target["target_paths"] = []
    missing_contract_target_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_contract_target_readiness
    )
    if not any("missing target path" in error for error in missing_contract_target_errors):
        raise AssertionError(f"missing contract target negative was not caught: {missing_contract_target_errors}")

    missing_contract_owner_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_contract_owner_readiness, "effect")["no_write_source_writer_contract_evidence"][
        "owner_generator_candidate"
    ] = ""
    missing_contract_owner_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_contract_owner_readiness
    )
    if not any("missing owner generator candidate" in error for error in missing_contract_owner_errors):
        raise AssertionError(f"missing contract owner negative was not caught: {missing_contract_owner_errors}")

    missing_contract_syntax_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_contract_syntax_readiness, "trigger")["no_write_source_writer_contract_evidence"][
        "eu5_syntax_evidence"
    ]["paths"] = []
    missing_contract_syntax_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_contract_syntax_readiness
    )
    if not any("missing EU5 syntax evidence paths" in error for error in missing_contract_syntax_errors):
        raise AssertionError(f"missing contract syntax negative was not caught: {missing_contract_syntax_errors}")

    missing_contract_command_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_contract_command_readiness, "gui")["no_write_source_writer_contract_evidence"][
        "verification_commands"
    ] = []
    missing_contract_command_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_contract_command_readiness
    )
    if not any("verification commands mismatch" in error for error in missing_contract_command_errors):
        raise AssertionError(f"missing contract command negative was not caught: {missing_contract_command_errors}")

    missing_contract_blocker_readiness = deepcopy(source_writer_readiness)
    missing_contract_blocker = _first_readiness_artifact(missing_contract_blocker_readiness, "listener")[
        "no_write_source_writer_contract_evidence"
    ]
    missing_contract_blocker["source_writer_blocker_reasons"] = []
    missing_contract_blocker["source_writer_still_blocked_reason"] = ""
    missing_contract_blocker_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_contract_blocker_readiness
    )
    if not any("missing source-writer blocker reasons" in error for error in missing_contract_blocker_errors):
        raise AssertionError(f"missing contract blocker negative was not caught: {missing_contract_blocker_errors}")

    missing_event_namespace_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_event_namespace_readiness, "event")["closure_contract"]["namespace"] = ""
    missing_event_namespace_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_event_namespace_readiness
    )
    if not any("event closure missing namespace" in error for error in missing_event_namespace_errors):
        raise AssertionError(f"missing event namespace closure negative was not caught: {missing_event_namespace_errors}")

    missing_event_path_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_event_path_readiness, "event")["closure_contract"]["future_source_target_path"] = ""
    missing_event_path_errors = validate_repeated_entity_row_source_writer_readiness(missing_event_path_readiness)
    if not any("event closure missing future target path" in error for error in missing_event_path_errors):
        raise AssertionError(f"missing event target closure negative was not caught: {missing_event_path_errors}")

    missing_event_loc_handoff_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_event_loc_handoff_readiness, "event")["closure_contract"][
        "localization_key_handoff"
    ]
    missing_event_loc_handoff_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_event_loc_handoff_readiness
    )
    if not any("event closure missing localization handoff" in error for error in missing_event_loc_handoff_errors):
        raise AssertionError(
            f"missing event loc handoff closure negative was not caught: {missing_event_loc_handoff_errors}"
        )

    missing_event_option_handoff_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_event_option_handoff_readiness, "event")["closure_contract"][
        "option_effect_handoff"
    ] = {}
    missing_event_option_handoff_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_event_option_handoff_readiness
    )
    if not any("event closure missing option-effect handoff" in error for error in missing_event_option_handoff_errors):
        raise AssertionError(
            f"missing event option handoff closure negative was not caught: {missing_event_option_handoff_errors}"
        )

    missing_event_safety_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_event_safety_readiness, "event")["closure_contract"]["safety_notes"]
    missing_event_safety_errors = validate_repeated_entity_row_source_writer_readiness(missing_event_safety_readiness)
    if not any("event closure missing safety notes" in error for error in missing_event_safety_errors):
        raise AssertionError(f"missing event safety closure negative was not caught: {missing_event_safety_errors}")

    missing_localization_language_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_localization_language_readiness, "localization")["closure_contract"][
        "language_ownership_boundary"
    ]["required_languages"] = ["english"]
    missing_localization_language_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_localization_language_readiness
    )
    if not any("localization closure missing language boundary" in error for error in missing_localization_language_errors):
        raise AssertionError(
            f"missing localization language closure negative was not caught: {missing_localization_language_errors}"
        )

    missing_localization_keys_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_localization_keys_readiness, "localization")["closure_contract"][
        "key_allocation"
    ]["loc_key_plan"] = []
    missing_localization_keys_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_localization_keys_readiness
    )
    if not any("localization closure missing key allocation" in error for error in missing_localization_keys_errors):
        raise AssertionError(
            f"missing localization key allocation closure negative was not caught: {missing_localization_keys_errors}"
        )

    missing_localization_event_handoff_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_localization_event_handoff_readiness, "localization")["closure_contract"][
        "event_key_handoff"
    ]
    missing_localization_event_handoff_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_localization_event_handoff_readiness
    )
    if not any("localization closure missing event key handoff" in error for error in missing_localization_event_handoff_errors):
        raise AssertionError(
            "missing localization event handoff closure negative was not caught: "
            f"{missing_localization_event_handoff_errors}"
        )

    missing_localization_bom_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_localization_bom_readiness, "localization")["closure_contract"][
        "escaping_bom_boundary"
    ]["bom_encoding"] = "utf-8"
    missing_localization_bom_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_localization_bom_readiness
    )
    if not any("localization closure missing escaping/BOM boundary" in error for error in missing_localization_bom_errors):
        raise AssertionError(
            f"missing localization BOM closure negative was not caught: {missing_localization_bom_errors}"
        )

    missing_localization_path_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_localization_path_readiness, "localization")["closure_contract"][
        "future_source_target_path_pattern"
    ] = ""
    missing_localization_path_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_localization_path_readiness
    )
    if not any("localization closure missing future target path pattern" in error for error in missing_localization_path_errors):
        raise AssertionError(
            f"missing localization path closure negative was not caught: {missing_localization_path_errors}"
        )

    event_closure_writable_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(event_closure_writable_readiness, "event")["closure_contract"]["may_write_src"] = True
    event_closure_writable_errors = validate_repeated_entity_row_source_writer_readiness(
        event_closure_writable_readiness
    )
    if not any("event closure may_write_src must be false" in error for error in event_closure_writable_errors):
        raise AssertionError(f"event closure may_write_src negative was not caught: {event_closure_writable_errors}")

    localization_closure_writes_src_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(localization_closure_writes_src_readiness, "localization")["closure_contract"][
        "writes_src"
    ] = True
    localization_closure_writes_src_errors = validate_repeated_entity_row_source_writer_readiness(
        localization_closure_writes_src_readiness
    )
    if not any(
        "localization closure writes_src must be false" in error
        for error in localization_closure_writes_src_errors
    ):
        raise AssertionError(
            f"localization closure writes_src negative was not caught: {localization_closure_writes_src_errors}"
        )

    localization_closure_source_writer_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(localization_closure_source_writer_readiness, "localization")["closure_contract"][
        "source_writer_allowed"
    ] = True
    localization_closure_source_writer_errors = validate_repeated_entity_row_source_writer_readiness(
        localization_closure_source_writer_readiness
    )
    if not any(
        "localization closure source_writer_allowed must be false" in error
        for error in localization_closure_source_writer_errors
    ):
        raise AssertionError(
            "localization closure source_writer_allowed negative was not caught: "
            f"{localization_closure_source_writer_errors}"
        )

    event_closure_ready_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(event_closure_ready_readiness, "event")["closure_contract"][
        "readiness_status"
    ] = "verified"
    event_closure_ready_errors = validate_repeated_entity_row_source_writer_readiness(event_closure_ready_readiness)
    if not any("event closure must stay blocked" in error for error in event_closure_ready_errors):
        raise AssertionError(f"event closure verified negative was not caught: {event_closure_ready_errors}")

    missing_effect_schema_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_effect_schema_readiness, "effect")["closure_contract"][
        "row_state_schema_boundary"
    ]
    missing_effect_schema_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_effect_schema_readiness
    )
    if not any("effect closure missing row-state schema boundary" in error for error in missing_effect_schema_errors):
        raise AssertionError(
            f"missing effect row-state schema closure negative was not caught: {missing_effect_schema_errors}"
        )

    missing_effect_aggregate_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_effect_aggregate_readiness, "effect")["closure_contract"][
        "aggregate_refresh_boundary"
    ] = {}
    missing_effect_aggregate_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_effect_aggregate_readiness
    )
    if not any("effect closure missing aggregate refresh boundary" in error for error in missing_effect_aggregate_errors):
        raise AssertionError(
            f"missing effect aggregate refresh closure negative was not caught: {missing_effect_aggregate_errors}"
        )

    missing_effect_path_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_effect_path_readiness, "effect")["closure_contract"][
        "future_source_target_path"
    ] = ""
    missing_effect_path_errors = validate_repeated_entity_row_source_writer_readiness(missing_effect_path_readiness)
    if not any("effect closure missing future target path" in error for error in missing_effect_path_errors):
        raise AssertionError(f"missing effect target closure negative was not caught: {missing_effect_path_errors}")

    missing_cleanup_lifecycle_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_cleanup_lifecycle_readiness, "cleanup")["closure_contract"][
        "cleanup_lifecycle_scope"
    ] = ""
    missing_cleanup_lifecycle_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_cleanup_lifecycle_readiness
    )
    if not any("cleanup closure missing lifecycle scope" in error for error in missing_cleanup_lifecycle_errors):
        raise AssertionError(
            f"missing cleanup lifecycle closure negative was not caught: {missing_cleanup_lifecycle_errors}"
        )

    missing_cleanup_coverage_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_cleanup_coverage_readiness, "cleanup")["closure_contract"][
        "cleanup_coverage"
    ] = {}
    missing_cleanup_coverage_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_cleanup_coverage_readiness
    )
    if not any("cleanup closure missing cleanup coverage" in error for error in missing_cleanup_coverage_errors):
        raise AssertionError(
            f"missing cleanup coverage closure negative was not caught: {missing_cleanup_coverage_errors}"
        )

    missing_cleanup_ownership_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_cleanup_ownership_readiness, "cleanup")["closure_contract"][
        "ownership_reset_branch_boundary"
    ] = {}
    missing_cleanup_ownership_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_cleanup_ownership_readiness
    )
    if not any("cleanup closure missing ownership/reset branch" in error for error in missing_cleanup_ownership_errors):
        raise AssertionError(
            f"missing cleanup ownership/reset closure negative was not caught: {missing_cleanup_ownership_errors}"
        )

    missing_trigger_eligibility_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_trigger_eligibility_readiness, "trigger")["closure_contract"][
        "condition_group_coverage"
    ]["eligibility"] = {}
    missing_trigger_eligibility_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_trigger_eligibility_readiness
    )
    if not any("trigger closure missing eligibility plan" in error for error in missing_trigger_eligibility_errors):
        raise AssertionError(
            f"missing trigger eligibility closure negative was not caught: {missing_trigger_eligibility_errors}"
        )

    missing_trigger_row_completion_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_trigger_row_completion_readiness, "trigger")["closure_contract"][
        "condition_group_coverage"
    ]["row_completion"] = {}
    missing_trigger_row_completion_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_trigger_row_completion_readiness
    )
    if not any("trigger closure missing row_completion plan" in error for error in missing_trigger_row_completion_errors):
        raise AssertionError(
            "missing trigger row-completion closure negative was not caught: "
            f"{missing_trigger_row_completion_errors}"
        )

    missing_trigger_tooltip_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_trigger_tooltip_readiness, "trigger")["closure_contract"][
        "condition_group_coverage"
    ]["tooltip_safe"] = {}
    missing_trigger_tooltip_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_trigger_tooltip_readiness
    )
    if not any("trigger closure missing tooltip_safe plan" in error for error in missing_trigger_tooltip_errors):
        raise AssertionError(
            f"missing trigger tooltip-safe closure negative was not caught: {missing_trigger_tooltip_errors}"
        )

    missing_trigger_forbidden_paths_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_trigger_forbidden_paths_readiness, "trigger")["closure_contract"][
        "forbidden_write_paths"
    ] = {}
    missing_trigger_forbidden_paths_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_trigger_forbidden_paths_readiness
    )
    if not any("trigger closure missing forbidden write paths" in error for error in missing_trigger_forbidden_paths_errors):
        raise AssertionError(
            f"missing trigger forbidden write paths negative was not caught: {missing_trigger_forbidden_paths_errors}"
        )

    effect_closure_writable_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(effect_closure_writable_readiness, "effect")["closure_contract"]["may_write_src"] = True
    effect_closure_writable_errors = validate_repeated_entity_row_source_writer_readiness(
        effect_closure_writable_readiness
    )
    if not any("effect closure may_write_src must be false" in error for error in effect_closure_writable_errors):
        raise AssertionError(f"effect closure may_write_src negative was not caught: {effect_closure_writable_errors}")

    cleanup_closure_writes_src_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(cleanup_closure_writes_src_readiness, "cleanup")["closure_contract"]["writes_src"] = True
    cleanup_closure_writes_src_errors = validate_repeated_entity_row_source_writer_readiness(
        cleanup_closure_writes_src_readiness
    )
    if not any("cleanup closure writes_src must be false" in error for error in cleanup_closure_writes_src_errors):
        raise AssertionError(
            f"cleanup closure writes_src negative was not caught: {cleanup_closure_writes_src_errors}"
        )

    trigger_closure_source_writer_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(trigger_closure_source_writer_readiness, "trigger")["closure_contract"][
        "source_writer_allowed"
    ] = True
    trigger_closure_source_writer_errors = validate_repeated_entity_row_source_writer_readiness(
        trigger_closure_source_writer_readiness
    )
    if not any("trigger closure source_writer_allowed must be false" in error for error in trigger_closure_source_writer_errors):
        raise AssertionError(
            "trigger closure source_writer_allowed negative was not caught: "
            f"{trigger_closure_source_writer_errors}"
        )

    trigger_closure_backend_ready_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(trigger_closure_backend_ready_readiness, "trigger")["closure_contract"][
        "readiness_status"
    ] = "backend_ready"
    trigger_closure_backend_ready_errors = validate_repeated_entity_row_source_writer_readiness(
        trigger_closure_backend_ready_readiness
    )
    if not any("trigger closure must stay blocked" in error for error in trigger_closure_backend_ready_errors):
        raise AssertionError(
            f"trigger closure backend_ready negative was not caught: {trigger_closure_backend_ready_errors}"
        )

    missing_gui_widget_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_gui_widget_readiness, "gui")["closure_contract"]["fixed_row_widget_plan"]
    missing_gui_widget_errors = validate_repeated_entity_row_source_writer_readiness(missing_gui_widget_readiness)
    if not any("GUI closure missing fixed row widget plan" in error for error in missing_gui_widget_errors):
        raise AssertionError(f"missing GUI widget closure negative was not caught: {missing_gui_widget_errors}")

    missing_gui_binding_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_gui_binding_readiness, "gui")["closure_contract"][
        "per_row_variable_binding_plan"
    ]
    missing_gui_binding_errors = validate_repeated_entity_row_source_writer_readiness(missing_gui_binding_readiness)
    if not any("GUI closure missing per-row binding plan" in error for error in missing_gui_binding_errors):
        raise AssertionError(f"missing GUI binding closure negative was not caught: {missing_gui_binding_errors}")

    missing_gui_tooltip_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_gui_tooltip_readiness, "gui")["closure_contract"][
        "tooltip_localization_linkage"
    ]
    missing_gui_tooltip_errors = validate_repeated_entity_row_source_writer_readiness(missing_gui_tooltip_readiness)
    if not any("GUI closure missing tooltip localization linkage" in error for error in missing_gui_tooltip_errors):
        raise AssertionError(f"missing GUI tooltip closure negative was not caught: {missing_gui_tooltip_errors}")

    missing_gui_path_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_gui_path_readiness, "gui")["closure_contract"]["future_source_target_path"] = ""
    missing_gui_path_errors = validate_repeated_entity_row_source_writer_readiness(missing_gui_path_readiness)
    if not any("GUI closure missing future target path" in error for error in missing_gui_path_errors):
        raise AssertionError(f"missing GUI path closure negative was not caught: {missing_gui_path_errors}")

    gui_aggregate_only_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(gui_aggregate_only_readiness, "gui")["closure_contract"][
        "aggregate_only_display_allowed"
    ] = True
    gui_aggregate_only_errors = validate_repeated_entity_row_source_writer_readiness(gui_aggregate_only_readiness)
    if not any("GUI closure aggregate-only UI must be false" in error for error in gui_aggregate_only_errors):
        raise AssertionError(f"GUI aggregate-only closure negative was not caught: {gui_aggregate_only_errors}")

    gui_source_body_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(gui_source_body_readiness, "gui")["closure_contract"]["gui_source_body_allowed"] = True
    gui_source_body_errors = validate_repeated_entity_row_source_writer_readiness(gui_source_body_readiness)
    if not any("GUI closure GUI source body emission must be false" in error for error in gui_source_body_errors):
        raise AssertionError(f"GUI source body closure negative was not caught: {gui_source_body_errors}")

    gui_source_write_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(gui_source_write_readiness, "gui")["closure_contract"]["gui_source_writes_allowed"] = True
    gui_source_write_errors = validate_repeated_entity_row_source_writer_readiness(gui_source_write_readiness)
    if not any("GUI closure GUI source writes must be false" in error for error in gui_source_write_errors):
        raise AssertionError(f"GUI source write closure negative was not caught: {gui_source_write_errors}")

    listener_non_alhambra_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(listener_non_alhambra_readiness, "listener")["closure_contract"][
        "pilot_key"
    ] = "unique_dome_of_the_rock"
    listener_non_alhambra_errors = validate_repeated_entity_row_source_writer_readiness(
        listener_non_alhambra_readiness
    )
    if not any("listener closure must be Alhambra-only" in error for error in listener_non_alhambra_errors):
        raise AssertionError(f"non-Alhambra listener closure negative was not caught: {listener_non_alhambra_errors}")

    missing_listener_hook_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_listener_hook_readiness, "listener")["closure_contract"][
        "on_action_hook_linkage_plan"
    ]
    missing_listener_hook_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_listener_hook_readiness
    )
    if not any("listener closure missing hook linkage plan" in error for error in missing_listener_hook_errors):
        raise AssertionError(f"missing listener hook closure negative was not caught: {missing_listener_hook_errors}")

    missing_listener_trigger_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_listener_trigger_readiness, "listener")["closure_contract"][
        "selected_ritual_trigger_linkage"
    ]
    missing_listener_trigger_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_listener_trigger_readiness
    )
    if not any(
        "listener closure missing selected ritual trigger linkage" in error
        for error in missing_listener_trigger_errors
    ):
        raise AssertionError(
            f"missing listener selected trigger closure negative was not caught: {missing_listener_trigger_errors}"
        )

    missing_listener_war_scope_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_listener_war_scope_readiness, "listener")["closure_contract"][
        "war_scope_availability_persistence_plan"
    ] = {}
    missing_listener_war_scope_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_listener_war_scope_readiness
    )
    if not any(
        "listener closure missing war scope availability plan" in error
        for error in missing_listener_war_scope_errors
    ):
        raise AssertionError(
            f"missing listener war-scope closure negative was not caught: {missing_listener_war_scope_errors}"
        )

    missing_listener_path_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(missing_listener_path_readiness, "listener")["closure_contract"][
        "future_source_target_path"
    ] = ""
    missing_listener_path_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_listener_path_readiness
    )
    if not any("listener closure missing future target path" in error for error in missing_listener_path_errors):
        raise AssertionError(f"missing listener path closure negative was not caught: {missing_listener_path_errors}")

    listener_body_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(listener_body_readiness, "listener")["closure_contract"]["listener_body_allowed"] = True
    listener_body_errors = validate_repeated_entity_row_source_writer_readiness(listener_body_readiness)
    if not any("listener closure listener body writes must be false" in error for error in listener_body_errors):
        raise AssertionError(f"listener body closure negative was not caught: {listener_body_errors}")

    listener_war_write_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(listener_war_write_readiness, "listener")["closure_contract"][
        "war_scope_writes_allowed"
    ] = True
    listener_war_write_errors = validate_repeated_entity_row_source_writer_readiness(listener_war_write_readiness)
    if not any("listener closure war scope writes must be false" in error for error in listener_war_write_errors):
        raise AssertionError(f"listener war-scope write closure negative was not caught: {listener_war_write_errors}")

    gui_closure_source_ready_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(gui_closure_source_ready_readiness, "gui")["closure_contract"][
        "readiness_status"
    ] = "source_ready"
    gui_closure_source_ready_errors = validate_repeated_entity_row_source_writer_readiness(
        gui_closure_source_ready_readiness
    )
    if not any("gui closure must stay blocked" in error for error in gui_closure_source_ready_errors):
        raise AssertionError(
            f"GUI source_ready closure negative was not caught: {gui_closure_source_ready_errors}"
        )

    listener_closure_backend_ready_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(listener_closure_backend_ready_readiness, "listener")["closure_contract"][
        "backend_ready"
    ] = True
    listener_closure_backend_ready_errors = validate_repeated_entity_row_source_writer_readiness(
        listener_closure_backend_ready_readiness
    )
    if not any("listener closure must not declare backend_ready" in error for error in listener_closure_backend_ready_errors):
        raise AssertionError(
            "listener backend_ready closure negative was not caught: "
            f"{listener_closure_backend_ready_errors}"
        )

    gui_closure_source_writer_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(gui_closure_source_writer_readiness, "gui")["closure_contract"][
        "source_writer_allowed"
    ] = True
    gui_closure_source_writer_errors = validate_repeated_entity_row_source_writer_readiness(
        gui_closure_source_writer_readiness
    )
    if not any("gui closure source_writer_allowed must be false" in error for error in gui_closure_source_writer_errors):
        raise AssertionError(
            f"GUI closure source_writer_allowed negative was not caught: {gui_closure_source_writer_errors}"
        )

    listener_closure_writes_src_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(listener_closure_writes_src_readiness, "listener")["closure_contract"][
        "writes_src"
    ] = True
    listener_closure_writes_src_errors = validate_repeated_entity_row_source_writer_readiness(
        listener_closure_writes_src_readiness
    )
    if not any("listener closure writes_src must be false" in error for error in listener_closure_writes_src_errors):
        raise AssertionError(
            f"listener closure writes_src negative was not caught: {listener_closure_writes_src_errors}"
        )

    missing_gui_closure_count_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_gui_closure_count_readiness, "gui")["closure_contract"]
    missing_gui_closure_count_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_gui_closure_count_readiness
    )
    if not any("expected 8 repeated-row gui closure artifacts" in error for error in missing_gui_closure_count_errors):
        raise AssertionError(
            f"GUI closure count negative was not caught: {missing_gui_closure_count_errors}"
        )

    missing_listener_closure_count_readiness = deepcopy(source_writer_readiness)
    del _first_readiness_artifact(missing_listener_closure_count_readiness, "listener")["closure_contract"]
    missing_listener_closure_count_errors = validate_repeated_entity_row_source_writer_readiness(
        missing_listener_closure_count_readiness
    )
    if not any(
        "expected 1 repeated-row listener closure artifacts" in error
        for error in missing_listener_closure_count_errors
    ):
        raise AssertionError(
            f"listener closure count negative was not caught: {missing_listener_closure_count_errors}"
        )

    writable_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(writable_readiness, "effect")["may_write_src"] = True
    writable_readiness_errors = validate_repeated_entity_row_source_writer_readiness(writable_readiness)
    if not any("may_write_src must be false" in error for error in writable_readiness_errors):
        raise AssertionError(f"may_write_src readiness negative was not caught: {writable_readiness_errors}")

    writes_src_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(writes_src_readiness, "trigger")["writes_src"] = True
    writes_src_readiness_errors = validate_repeated_entity_row_source_writer_readiness(writes_src_readiness)
    if not any("writes_src must be false" in error for error in writes_src_readiness_errors):
        raise AssertionError(f"writes_src readiness negative was not caught: {writes_src_readiness_errors}")

    source_writer_allowed_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(source_writer_allowed_readiness, "gui")["source_writer_allowed"] = True
    source_writer_allowed_errors = validate_repeated_entity_row_source_writer_readiness(
        source_writer_allowed_readiness
    )
    if not any("source_writer_allowed must be false" in error for error in source_writer_allowed_errors):
        raise AssertionError(f"source_writer_allowed readiness negative was not caught: {source_writer_allowed_errors}")

    source_ready_readiness = deepcopy(source_writer_readiness)
    _first_readiness_artifact(source_ready_readiness, "cleanup")["current_contract_status"] = "source_ready"
    source_ready_errors = validate_repeated_entity_row_source_writer_readiness(source_ready_readiness)
    if not any("must not be source-ready" in error for error in source_ready_errors):
        raise AssertionError(f"source_ready readiness negative was not caught: {source_ready_errors}")

    no_blockers_readiness = deepcopy(source_writer_readiness)
    no_blockers_artifact = _first_readiness_artifact(no_blockers_readiness, "listener")
    no_blockers_artifact["unresolved_writer_blockers"] = []
    for evidence_field in readiness_evidence_fields:
        no_blockers_artifact[evidence_field]["blockers"] = []
    no_blockers_errors = validate_repeated_entity_row_source_writer_readiness(no_blockers_readiness)
    if not any("missing blockers" in error for error in no_blockers_errors):
        raise AssertionError(f"no blockers readiness negative was not caught: {no_blockers_errors}")

    source_bundle_preview = repeated_entity_row_source_bundle_preview_for_payload(
        spec_data,
        source_writer_readiness=source_writer_readiness,
    )
    if source_bundle_preview["validation_errors"]:
        raise AssertionError(
            "repeated-row source bundle preview unexpectedly failed validation: "
            f"{source_bundle_preview['validation_errors']}"
        )
    expected_bundle_counts = {
        "unique_dome_of_the_rock": 44,
        "unique_alhambra": 45,
        "unique_st_peters_basilica": 44,
        "unique_bank_of_saint_george": 44,
    }
    if source_bundle_preview.get("bundle_count") != 4:
        raise AssertionError(f"expected 4 source bundle previews, got {source_bundle_preview.get('bundle_count')}")
    if source_bundle_preview.get("artifact_count") != 177:
        raise AssertionError(
            f"expected 177 source bundle preview artifacts, got {source_bundle_preview.get('artifact_count')}"
        )
    if source_bundle_preview.get("closure_contract_count") != 177:
        raise AssertionError(
            "expected 177 source bundle closure contracts, got "
            f"{source_bundle_preview.get('closure_contract_count')}"
        )
    if source_bundle_preview.get("source_ready_count") != 0:
        raise AssertionError(f"source bundle preview became source-ready: {source_bundle_preview}")
    if source_bundle_preview.get("source_writer_allowed_count") != 0:
        raise AssertionError(f"source bundle preview allowed source writer: {source_bundle_preview}")
    if source_bundle_preview.get("may_write_src_count") != 0:
        raise AssertionError(f"source bundle preview may_write_src changed: {source_bundle_preview}")
    if source_bundle_preview.get("writes_src_count") != 0:
        raise AssertionError(f"source bundle preview writes_src changed: {source_bundle_preview}")
    if source_bundle_preview.get("family_summary") != expected_preview_family_counts:
        raise AssertionError(f"source bundle family summary changed: {source_bundle_preview.get('family_summary')}")
    if not source_bundle_preview.get("blocker_summary"):
        raise AssertionError("source bundle preview must retain blocker summary")

    for pilot_key, expected_count in expected_bundle_counts.items():
        bundle = _source_bundle(source_bundle_preview, pilot_key)
        if bundle.get("artifact_count") != expected_count:
            raise AssertionError(f"{pilot_key} bundle artifact count changed: {bundle.get('artifact_count')}")
        if bundle.get("closure_contract_count") != expected_count:
            raise AssertionError(f"{pilot_key} bundle closure count changed: {bundle.get('closure_contract_count')}")
        if bundle.get("source_ready_count") != 0:
            raise AssertionError(f"{pilot_key} bundle became source-ready: {bundle}")
        if bundle.get("may_write_src_count") != 0 or bundle.get("writes_src_count") != 0:
            raise AssertionError(f"{pilot_key} bundle no-write count changed: {bundle}")
        if bundle.get("source_writer_allowed_count") != 0:
            raise AssertionError(f"{pilot_key} bundle source writer allowed count changed: {bundle}")
        sections = bundle.get("sections")
        if not isinstance(sections, dict):
            raise AssertionError(f"{pilot_key} bundle sections must be a mapping: {bundle}")
        missing_sections = set(expected_preview_family_counts) - set(sections)
        if missing_sections:
            raise AssertionError(f"{pilot_key} bundle missing sections: {missing_sections}")
        for family, section in sections.items():
            if section.get("family") != family:
                raise AssertionError(f"{pilot_key} section {family} family mismatch: {section}")
            if section.get("source_ready_count") != 0:
                raise AssertionError(f"{pilot_key} section {family} became source-ready: {section}")
            if section.get("may_write_src_count") != 0 or section.get("writes_src_count") != 0:
                raise AssertionError(f"{pilot_key} section {family} no-write count changed: {section}")
            if section.get("source_writer_allowed_count") != 0:
                raise AssertionError(f"{pilot_key} section {family} source writer count changed: {section}")
            if section.get("artifact_count") != len(section.get("artifacts", []) or []):
                raise AssertionError(f"{pilot_key} section {family} artifact count mismatch: {section}")
            if section.get("closure_contract_count") != len(section.get("closure_contract_refs", []) or []):
                raise AssertionError(f"{pilot_key} section {family} closure count mismatch: {section}")
            if family != "listener" and not section.get("required_validations"):
                raise AssertionError(f"{pilot_key} section {family} lost required validations: {section}")
            if family != "listener" and not section.get("unresolved_writer_blockers"):
                raise AssertionError(f"{pilot_key} section {family} lost unresolved blockers: {section}")

        listener_section = sections["listener"]
        if pilot_key == "unique_alhambra":
            if listener_section.get("artifact_count") != 1:
                raise AssertionError(f"Alhambra must carry one listener artifact: {listener_section}")
            listener_artifact = listener_section["artifacts"][0]
            if listener_artifact.get("artifact_kind") != "listener_war_integration":
                raise AssertionError(f"Alhambra listener artifact kind changed: {listener_artifact}")
        else:
            if listener_section.get("artifact_count") != 0:
                raise AssertionError(f"{pilot_key} must not forge listener artifacts: {listener_section}")
            absence = listener_section.get("listener_artifact_absence")
            if (
                not isinstance(absence, dict)
                or absence.get("explicit") is not True
                or absence.get("forged_artifact") is not False
                or absence.get("may_write_src") is not False
                or absence.get("writes_src") is not False
                or absence.get("source_writer_allowed") is not False
            ):
                raise AssertionError(f"{pilot_key} listener absence marker is incomplete: {listener_section}")

    event_bundle_artifact = _first_source_bundle_artifact(source_bundle_preview, "event")
    event_body = event_bundle_artifact.get("source_body_preview")
    if (
        not isinstance(event_body, dict)
        or event_body.get("kind") != "country_event_preview"
        or event_body.get("no_row_state_write") is not True
        or event_body.get("no_source_ready") is not True
    ):
        raise AssertionError(f"event bundle did not reuse event body preview: {event_bundle_artifact}")
    localization_bundle_artifact = _first_source_bundle_artifact(source_bundle_preview, "localization")
    localization_body = localization_bundle_artifact.get("source_body_preview")
    if (
        not isinstance(localization_body, dict)
        or localization_body.get("kind") != "localization_key_plan_preview"
        or not localization_body.get("loc_key_plan")
        or localization_body.get("contract_only") is not True
        or localization_body.get("body_emitted") is not False
    ):
        raise AssertionError(f"localization bundle lost loc key plan preview: {localization_bundle_artifact}")
    for family in ("effect", "cleanup", "trigger", "gui", "listener"):
        artifact = _first_source_bundle_artifact(source_bundle_preview, family)
        placeholder = artifact.get("source_body_placeholder")
        if not isinstance(placeholder, dict):
            raise AssertionError(f"{family} bundle missing source body placeholder: {artifact}")
        for flag, expected in {
            "contract_only": True,
            "body_emitted": False,
            "source_ready": False,
            "may_write_src": False,
            "writes_src": False,
            "source_writer_allowed": False,
        }.items():
            if placeholder.get(flag) is not expected:
                raise AssertionError(f"{family} source body placeholder lost {flag}: {placeholder}")

    missing_pilot_bundle = deepcopy(source_bundle_preview)
    missing_pilot_bundle["bundles"] = [
        bundle
        for bundle in missing_pilot_bundle["bundles"]
        if bundle.get("key") != "unique_bank_of_saint_george"
    ]
    missing_pilot_errors = validate_repeated_entity_row_source_bundle_preview(missing_pilot_bundle)
    if not any("missing pilot bundle" in error for error in missing_pilot_errors):
        raise AssertionError(f"missing pilot bundle negative was not caught: {missing_pilot_errors}")

    wrong_artifact_count_bundle = deepcopy(source_bundle_preview)
    wrong_artifact_count_bundle["artifact_count"] = 176
    wrong_artifact_count_errors = validate_repeated_entity_row_source_bundle_preview(wrong_artifact_count_bundle)
    if not any("expected 177 repeated-row source bundle artifacts" in error for error in wrong_artifact_count_errors):
        raise AssertionError(f"wrong artifact count bundle negative was not caught: {wrong_artifact_count_errors}")

    wrong_closure_count_bundle = deepcopy(source_bundle_preview)
    wrong_closure_count_bundle["closure_contract_count"] = 176
    wrong_closure_count_errors = validate_repeated_entity_row_source_bundle_preview(wrong_closure_count_bundle)
    if not any("expected 177 repeated-row source bundle closure contracts" in error for error in wrong_closure_count_errors):
        raise AssertionError(f"wrong closure count bundle negative was not caught: {wrong_closure_count_errors}")

    source_ready_bundle = deepcopy(source_bundle_preview)
    _first_source_bundle_artifact(source_ready_bundle, "cleanup")["source_ready"] = True
    source_ready_bundle_errors = validate_repeated_entity_row_source_bundle_preview(source_ready_bundle)
    if not any("source_ready/verified/backend_ready" in error for error in source_ready_bundle_errors):
        raise AssertionError(f"source_ready bundle negative was not caught: {source_ready_bundle_errors}")

    backend_ready_bundle = deepcopy(source_bundle_preview)
    _first_source_bundle_artifact(backend_ready_bundle, "listener")["source_body_placeholder"]["backend_ready"] = True
    backend_ready_bundle_errors = validate_repeated_entity_row_source_bundle_preview(backend_ready_bundle)
    if not any("source_ready/verified/backend_ready" in error for error in backend_ready_bundle_errors):
        raise AssertionError(f"backend_ready bundle negative was not caught: {backend_ready_bundle_errors}")

    verified_bundle = deepcopy(source_bundle_preview)
    _first_source_bundle_artifact(verified_bundle, "event")["source_body_preview"]["verified"] = True
    verified_bundle_errors = validate_repeated_entity_row_source_bundle_preview(verified_bundle)
    if not any("source_ready/verified/backend_ready" in error for error in verified_bundle_errors):
        raise AssertionError(f"verified bundle negative was not caught: {verified_bundle_errors}")

    writable_bundle = deepcopy(source_bundle_preview)
    _first_source_bundle_artifact(writable_bundle, "effect")["may_write_src"] = True
    writable_bundle_errors = validate_repeated_entity_row_source_bundle_preview(writable_bundle)
    if not any("may_write_src must be false" in error for error in writable_bundle_errors):
        raise AssertionError(f"may_write_src bundle negative was not caught: {writable_bundle_errors}")

    writes_src_bundle = deepcopy(source_bundle_preview)
    _first_source_bundle_artifact(writes_src_bundle, "trigger")["source_body_placeholder"]["writes_src"] = True
    writes_src_bundle_errors = validate_repeated_entity_row_source_bundle_preview(writes_src_bundle)
    if not any("writes_src must be false" in error for error in writes_src_bundle_errors):
        raise AssertionError(f"writes_src bundle negative was not caught: {writes_src_bundle_errors}")

    source_writer_allowed_bundle = deepcopy(source_bundle_preview)
    _first_source_bundle_artifact(source_writer_allowed_bundle, "gui")["source_writer_allowed"] = True
    source_writer_allowed_bundle_errors = validate_repeated_entity_row_source_bundle_preview(
        source_writer_allowed_bundle
    )
    if not any("source_writer_allowed must be false" in error for error in source_writer_allowed_bundle_errors):
        raise AssertionError(
            f"source_writer_allowed bundle negative was not caught: {source_writer_allowed_bundle_errors}"
        )

    forged_listener_bundle = deepcopy(source_bundle_preview)
    forged_listener_section = _source_bundle(forged_listener_bundle, "unique_dome_of_the_rock")["sections"]["listener"]
    forged_listener_section["artifacts"] = [
        deepcopy(_first_source_bundle_artifact(source_bundle_preview, "listener", "unique_alhambra"))
    ]
    forged_listener_section["artifacts"][0]["pilot_key"] = "unique_dome_of_the_rock"
    forged_listener_section["artifact_count"] = 1
    forged_listener_section["closure_contract_count"] = 1
    forged_listener_errors = validate_repeated_entity_row_source_bundle_preview(forged_listener_bundle)
    if not any("non-Alhambra pilot must not include listener artifact" in error for error in forged_listener_errors):
        raise AssertionError(f"forged listener bundle negative was not caught: {forged_listener_errors}")

    missing_alhambra_listener_bundle = deepcopy(source_bundle_preview)
    alhambra_listener_section = _source_bundle(missing_alhambra_listener_bundle, "unique_alhambra")["sections"]["listener"]
    alhambra_listener_section["artifacts"] = []
    alhambra_listener_section["artifact_count"] = 0
    alhambra_listener_section["closure_contract_count"] = 0
    missing_alhambra_listener_errors = validate_repeated_entity_row_source_bundle_preview(
        missing_alhambra_listener_bundle
    )
    if not any("missing listener_war_integration" in error for error in missing_alhambra_listener_errors):
        raise AssertionError(
            f"missing Alhambra listener bundle negative was not caught: {missing_alhambra_listener_errors}"
        )

    missing_placeholder_flag_bundle = deepcopy(source_bundle_preview)
    del _first_source_bundle_artifact(missing_placeholder_flag_bundle, "effect")["source_body_placeholder"]["contract_only"]
    missing_placeholder_flag_errors = validate_repeated_entity_row_source_bundle_preview(
        missing_placeholder_flag_bundle
    )
    if not any("source body placeholder missing no-write flag contract_only" in error for error in missing_placeholder_flag_errors):
        raise AssertionError(
            f"missing placeholder flag bundle negative was not caught: {missing_placeholder_flag_errors}"
        )

    alhambra_body_candidate = repeated_entity_row_alhambra_source_body_candidate_for_payload(
        spec_data,
        source_bundle_preview=source_bundle_preview,
    )
    if alhambra_body_candidate["validation_errors"]:
        raise AssertionError(
            "Alhambra source body candidate unexpectedly failed validation: "
            f"{alhambra_body_candidate['validation_errors']}"
        )
    alhambra_summary = alhambra_body_candidate.get("summary", {})
    if alhambra_body_candidate.get("pilot_key") != "unique_alhambra":
        raise AssertionError(f"Alhambra source body candidate pilot changed: {alhambra_body_candidate}")
    if alhambra_summary.get("pilot_key") != "unique_alhambra":
        raise AssertionError(f"Alhambra source body candidate summary pilot changed: {alhambra_summary}")
    if alhambra_summary.get("family_count") != 7:
        raise AssertionError(f"Alhambra source body candidate family_count changed: {alhambra_summary}")
    if alhambra_summary.get("artifact_count") != 45:
        raise AssertionError(f"Alhambra source body candidate artifact_count changed: {alhambra_summary}")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if alhambra_summary.get(count_key) != 0:
            raise AssertionError(f"Alhambra source body candidate {count_key} changed: {alhambra_summary}")
    if not alhambra_summary.get("blocker_summary"):
        raise AssertionError("Alhambra source body candidate must retain blocker summary")

    alhambra_bundle = _source_bundle(source_bundle_preview, "unique_alhambra")
    alhambra_sections = alhambra_body_candidate.get("sections")
    if set(alhambra_sections) != set(expected_preview_family_counts):
        raise AssertionError(f"Alhambra source body candidate sections changed: {alhambra_sections}")
    required_candidate_flags = {
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "may_write_src": False,
        "writes_src": False,
        "source_writer_allowed": False,
    }
    for family, section in alhambra_sections.items():
        bundle_section = alhambra_bundle["sections"][family]
        if section.get("artifact_count") != bundle_section.get("artifact_count"):
            raise AssertionError(f"{family} Alhambra candidate count does not match bundle: {section}")
        if section.get("closure_contract_refs") != [
            artifact.get("closure_contract_ref")
            for artifact in bundle_section.get("artifacts", []) or []
        ]:
            raise AssertionError(f"{family} Alhambra candidate closure refs do not match bundle: {section}")
        if not section.get("validation_refs") and family != "listener":
            raise AssertionError(f"{family} Alhambra candidate lost validation refs: {section}")
        if not section.get("unresolved_blockers"):
            raise AssertionError(f"{family} Alhambra candidate lost blockers: {section}")
        for flag, expected in required_candidate_flags.items():
            if section.get(flag) is not expected:
                raise AssertionError(f"{family} Alhambra candidate section lost {flag}: {section}")
        for candidate in section.get("structured_body_candidates", []) or []:
            body = candidate.get("structured_body_candidate")
            if not isinstance(body, dict):
                raise AssertionError(f"{family} Alhambra candidate missing structured body: {candidate}")
            for flag, expected in required_candidate_flags.items():
                if candidate.get(flag) is not expected:
                    raise AssertionError(f"{family} Alhambra candidate lost {flag}: {candidate}")
                if body.get(flag) is not expected:
                    raise AssertionError(f"{family} Alhambra candidate body lost {flag}: {body}")
            if family in {"effect", "cleanup", "trigger", "gui", "listener"}:
                placeholder = body.get("source_body_placeholder")
                if not isinstance(placeholder, dict):
                    raise AssertionError(f"{family} Alhambra candidate body lost placeholder: {body}")
                for flag, expected in {
                    "contract_only": True,
                    "body_emitted": False,
                    "source_ready": False,
                    "may_write_src": False,
                    "writes_src": False,
                    "source_writer_allowed": False,
                }.items():
                    if placeholder.get(flag) is not expected:
                        raise AssertionError(f"{family} Alhambra candidate placeholder lost {flag}: {placeholder}")

    event_candidate = _first_alhambra_source_body_candidate(alhambra_body_candidate, "event")
    event_bundle_artifact = _first_source_bundle_artifact(source_bundle_preview, "event", "unique_alhambra")
    if event_candidate.get("source_body_preview") != event_bundle_artifact.get("source_body_preview"):
        raise AssertionError(f"Alhambra event candidate did not reuse bundle preview: {event_candidate}")
    localization_candidate = _first_alhambra_source_body_candidate(alhambra_body_candidate, "localization")
    localization_bundle_artifact = _first_source_bundle_artifact(
        source_bundle_preview,
        "localization",
        "unique_alhambra",
    )
    if localization_candidate.get("source_body_preview") != localization_bundle_artifact.get("source_body_preview"):
        raise AssertionError(f"Alhambra localization candidate did not reuse loc plan: {localization_candidate}")

    listener_candidate = _first_alhambra_source_body_candidate(alhambra_body_candidate, "listener")
    listener_body = listener_candidate.get("structured_body_candidate", {})
    hook_plan = listener_body.get("on_action_hook_linkage_plan")
    if not isinstance(hook_plan, dict) or not {"on_pre_winning_war", "on_ending_war"} <= set(
        hook_plan.get("hooks", []) or []
    ):
        raise AssertionError(f"Alhambra listener candidate lost hook linkage: {listener_body}")
    trigger_linkage = listener_body.get("selected_ritual_trigger_linkage")
    if (
        not isinstance(trigger_linkage, dict)
        or trigger_linkage.get("trigger_name")
        != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
    ):
        raise AssertionError(f"Alhambra listener candidate lost selected trigger linkage: {listener_body}")
    war_scope_plan = listener_body.get("war_scope_availability_persistence_plan")
    if (
        not isinstance(war_scope_plan, dict)
        or war_scope_plan.get("listener_scope_writes_allowed") is not False
        or war_scope_plan.get("war_scope_writes_allowed") is not False
    ):
        raise AssertionError(f"Alhambra listener candidate lost war-scope plan: {listener_body}")

    wrong_pilot_candidate = deepcopy(alhambra_body_candidate)
    wrong_pilot_candidate["pilot_key"] = "unique_dome_of_the_rock"
    wrong_pilot_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(wrong_pilot_candidate)
    if not any("pilot_key must be unique_alhambra" in error for error in wrong_pilot_candidate_errors):
        raise AssertionError(f"wrong pilot Alhambra candidate negative was not caught: {wrong_pilot_candidate_errors}")

    missing_family_candidate = deepcopy(alhambra_body_candidate)
    del missing_family_candidate["sections"]["trigger"]
    missing_family_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(
        missing_family_candidate
    )
    if not any("missing family section" in error for error in missing_family_candidate_errors):
        raise AssertionError(
            f"missing family Alhambra candidate negative was not caught: {missing_family_candidate_errors}"
        )

    wrong_count_candidate = deepcopy(alhambra_body_candidate)
    wrong_count_candidate["artifact_count"] = 44
    wrong_count_candidate["summary"]["artifact_count"] = 44
    wrong_count_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(wrong_count_candidate)
    if not any("artifact_count must be 45" in error for error in wrong_count_candidate_errors):
        raise AssertionError(f"wrong count Alhambra candidate negative was not caught: {wrong_count_candidate_errors}")

    source_ready_candidate = deepcopy(alhambra_body_candidate)
    _first_alhambra_source_body_candidate(source_ready_candidate, "cleanup")["source_ready"] = True
    source_ready_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(source_ready_candidate)
    if not any("source_ready/verified/backend_ready" in error for error in source_ready_candidate_errors):
        raise AssertionError(
            f"source_ready Alhambra candidate negative was not caught: {source_ready_candidate_errors}"
        )

    backend_ready_candidate = deepcopy(alhambra_body_candidate)
    _first_alhambra_source_body_candidate(backend_ready_candidate, "listener")["structured_body_candidate"][
        "backend_ready"
    ] = True
    backend_ready_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(
        backend_ready_candidate
    )
    if not any("source_ready/verified/backend_ready" in error for error in backend_ready_candidate_errors):
        raise AssertionError(
            f"backend_ready Alhambra candidate negative was not caught: {backend_ready_candidate_errors}"
        )

    verified_candidate = deepcopy(alhambra_body_candidate)
    _first_alhambra_source_body_candidate(verified_candidate, "event")["structured_body_candidate"][
        "verified"
    ] = True
    verified_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(verified_candidate)
    if not any("source_ready/verified/backend_ready" in error for error in verified_candidate_errors):
        raise AssertionError(f"verified Alhambra candidate negative was not caught: {verified_candidate_errors}")

    writable_candidate = deepcopy(alhambra_body_candidate)
    _first_alhambra_source_body_candidate(writable_candidate, "effect")["may_write_src"] = True
    writable_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(writable_candidate)
    if not any("may_write_src must be false" in error for error in writable_candidate_errors):
        raise AssertionError(f"may_write_src Alhambra candidate negative was not caught: {writable_candidate_errors}")

    writes_src_candidate = deepcopy(alhambra_body_candidate)
    _first_alhambra_source_body_candidate(writes_src_candidate, "trigger")["structured_body_candidate"][
        "writes_src"
    ] = True
    writes_src_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(writes_src_candidate)
    if not any("writes_src must be false" in error for error in writes_src_candidate_errors):
        raise AssertionError(f"writes_src Alhambra candidate negative was not caught: {writes_src_candidate_errors}")

    source_writer_allowed_candidate = deepcopy(alhambra_body_candidate)
    _first_alhambra_source_body_candidate(source_writer_allowed_candidate, "gui")[
        "source_writer_allowed"
    ] = True
    source_writer_allowed_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(
        source_writer_allowed_candidate
    )
    if not any("source_writer_allowed must be false" in error for error in source_writer_allowed_candidate_errors):
        raise AssertionError(
            "source_writer_allowed Alhambra candidate negative was not caught: "
            f"{source_writer_allowed_candidate_errors}"
        )

    missing_hook_candidate = deepcopy(alhambra_body_candidate)
    del _first_alhambra_source_body_candidate(missing_hook_candidate, "listener")["structured_body_candidate"][
        "on_action_hook_linkage_plan"
    ]
    missing_hook_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(
        missing_hook_candidate
    )
    if not any("on_action hook linkage" in error for error in missing_hook_candidate_errors):
        raise AssertionError(f"missing hook Alhambra candidate negative was not caught: {missing_hook_candidate_errors}")

    missing_trigger_link_candidate = deepcopy(alhambra_body_candidate)
    del _first_alhambra_source_body_candidate(missing_trigger_link_candidate, "listener")[
        "structured_body_candidate"
    ]["selected_ritual_trigger_linkage"]
    missing_trigger_link_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(
        missing_trigger_link_candidate
    )
    if not any("selected ritual trigger linkage" in error for error in missing_trigger_link_candidate_errors):
        raise AssertionError(
            f"missing trigger linkage Alhambra candidate negative was not caught: "
            f"{missing_trigger_link_candidate_errors}"
        )

    missing_war_scope_candidate = deepcopy(alhambra_body_candidate)
    del _first_alhambra_source_body_candidate(missing_war_scope_candidate, "listener")["structured_body_candidate"][
        "war_scope_availability_persistence_plan"
    ]
    missing_war_scope_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(
        missing_war_scope_candidate
    )
    if not any("war-scope plan" in error for error in missing_war_scope_candidate_errors):
        raise AssertionError(
            f"missing war scope Alhambra candidate negative was not caught: {missing_war_scope_candidate_errors}"
        )

    for family in ("effect", "cleanup", "trigger", "gui"):
        missing_placeholder_candidate = deepcopy(alhambra_body_candidate)
        placeholder = _first_alhambra_source_body_candidate(missing_placeholder_candidate, family)[
            "structured_body_candidate"
        ]["source_body_placeholder"]
        del placeholder["contract_only"]
        missing_placeholder_candidate_errors = validate_repeated_entity_row_alhambra_source_body_candidate(
            missing_placeholder_candidate
        )
        if not any(
            "source body placeholder missing no-write flag contract_only" in error
            for error in missing_placeholder_candidate_errors
        ):
            raise AssertionError(
                f"{family} placeholder flag Alhambra candidate negative was not caught: "
                f"{missing_placeholder_candidate_errors}"
            )

    alhambra_source_file_preview = repeated_entity_row_alhambra_source_file_preview_for_payload(
        spec_data,
        source_body_candidate=alhambra_body_candidate,
    )
    if alhambra_source_file_preview["validation_errors"]:
        raise AssertionError(
            "Alhambra source file preview unexpectedly failed validation: "
            f"{alhambra_source_file_preview['validation_errors']}"
        )
    alhambra_file_targets = {
        "event": _repeated_row_event_contract_path("unique_alhambra"),
        "effect_cleanup": _repeated_row_effect_contract_path("unique_alhambra"),
        "trigger": _repeated_row_trigger_contract_path("unique_alhambra"),
        "gui": _repeated_row_gui_contract_path("unique_alhambra"),
        "listener": _repeated_row_listener_contract_path("unique_alhambra"),
        "english": "src/main_menu/localization/english/tv_wonder_unique_alhambra_ritual_l_english.yml",
        "simp_chinese": "src/main_menu/localization/simp_chinese/tv_wonder_unique_alhambra_ritual_l_simp_chinese.yml",
    }
    alhambra_file_summary = alhambra_source_file_preview.get("summary", {})
    if alhambra_source_file_preview.get("pilot_key") != "unique_alhambra":
        raise AssertionError(f"Alhambra source file preview pilot changed: {alhambra_source_file_preview}")
    if alhambra_file_summary.get("pilot_key") != "unique_alhambra":
        raise AssertionError(f"Alhambra source file preview summary pilot changed: {alhambra_file_summary}")
    if alhambra_file_summary.get("file_preview_count") != 7:
        raise AssertionError(f"Alhambra source file preview count changed: {alhambra_file_summary}")
    if alhambra_file_summary.get("artifact_count") != 45:
        raise AssertionError(f"Alhambra source file preview artifact_count changed: {alhambra_file_summary}")
    if alhambra_file_summary.get("family_count") != 7:
        raise AssertionError(f"Alhambra source file preview family_count changed: {alhambra_file_summary}")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if alhambra_file_summary.get(count_key) != 0:
            raise AssertionError(f"Alhambra source file preview {count_key} changed: {alhambra_file_summary}")
    if set(alhambra_source_file_preview.get("required_target_paths", [])) != set(alhambra_file_targets.values()):
        raise AssertionError(
            "Alhambra source file preview required target paths changed: "
            f"{alhambra_source_file_preview.get('required_target_paths')}"
        )
    if {
        preview.get("target_path")
        for preview in alhambra_source_file_preview.get("file_previews", []) or []
    } != set(alhambra_file_targets.values()):
        raise AssertionError(
            "Alhambra source file preview did not expose exact target paths: "
            f"{alhambra_source_file_preview.get('file_previews')}"
        )

    expected_alhambra_file_counts = {
        alhambra_file_targets["event"]: alhambra_body_candidate["family_summary"]["event"],
        alhambra_file_targets["effect_cleanup"]: (
            alhambra_body_candidate["family_summary"]["effect"]
            + alhambra_body_candidate["family_summary"]["cleanup"]
        ),
        alhambra_file_targets["trigger"]: alhambra_body_candidate["family_summary"]["trigger"],
        alhambra_file_targets["gui"]: alhambra_body_candidate["family_summary"]["gui"],
        alhambra_file_targets["listener"]: alhambra_body_candidate["family_summary"]["listener"],
        alhambra_file_targets["english"]: alhambra_body_candidate["family_summary"]["localization"],
        alhambra_file_targets["simp_chinese"]: alhambra_body_candidate["family_summary"]["localization"],
    }
    expected_alhambra_file_families = {
        alhambra_file_targets["event"]: ["event"],
        alhambra_file_targets["effect_cleanup"]: ["cleanup", "effect"],
        alhambra_file_targets["trigger"]: ["trigger"],
        alhambra_file_targets["gui"]: ["gui"],
        alhambra_file_targets["listener"]: ["listener"],
        alhambra_file_targets["english"]: ["localization"],
        alhambra_file_targets["simp_chinese"]: ["localization"],
    }
    alhambra_file_flags = {
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "may_write_src": False,
        "writes_src": False,
        "source_writer_allowed": False,
    }
    unique_source_refs: set[tuple[str, str, str, str]] = set()
    seen_file_families: set[str] = set()
    for target_path, expected_count in expected_alhambra_file_counts.items():
        file_preview = _alhambra_source_file_preview(alhambra_source_file_preview, target_path)
        if file_preview.get("artifact_count") != expected_count:
            raise AssertionError(f"{target_path} Alhambra file artifact count changed: {file_preview}")
        if file_preview.get("families") != expected_alhambra_file_families[target_path]:
            raise AssertionError(f"{target_path} Alhambra file families changed: {file_preview}")
        if not file_preview.get("validation_refs"):
            raise AssertionError(f"{target_path} Alhambra file preview lost validation refs: {file_preview}")
        if not file_preview.get("unresolved_blockers"):
            raise AssertionError(f"{target_path} Alhambra file preview lost blockers: {file_preview}")
        for flag, expected in alhambra_file_flags.items():
            if file_preview.get(flag) is not expected:
                raise AssertionError(f"{target_path} Alhambra file preview lost {flag}: {file_preview}")
        sections = file_preview.get("structured_body_sections")
        if not isinstance(sections, list) or len(sections) != expected_count:
            raise AssertionError(f"{target_path} Alhambra file preview sections changed: {file_preview}")
        for section in sections:
            family = section.get("family")
            seen_file_families.add(str(family))
            copied_candidate = section.get("source_body_candidate")
            if not isinstance(copied_candidate, dict):
                raise AssertionError(f"{target_path} Alhambra file preview lost copied body candidate: {section}")
            if section.get("structured_body_candidate") != copied_candidate.get("structured_body_candidate"):
                raise AssertionError(f"{target_path} Alhambra file preview did not copy structured body: {section}")
            for flag, expected in alhambra_file_flags.items():
                if section.get(flag) is not expected:
                    raise AssertionError(f"{target_path} Alhambra file section lost {flag}: {section}")
                body = section.get("structured_body_candidate", {})
                if body.get(flag) is not expected:
                    raise AssertionError(f"{target_path} Alhambra file section body lost {flag}: {body}")
            ref = section.get("source_body_candidate_ref")
            if not isinstance(ref, dict):
                raise AssertionError(f"{target_path} Alhambra file section missing source ref: {section}")
            unique_source_refs.add(
                (
                    str(ref.get("family", "")),
                    str(ref.get("row_set_key", "")),
                    str(ref.get("artifact_kind", "")),
                    str(ref.get("future_source_target_path", "")),
                )
            )
            if section.get("validation_refs") != copied_candidate.get("validation_refs"):
                raise AssertionError(f"{target_path} Alhambra file section validation refs changed: {section}")
            if section.get("unresolved_blockers") != copied_candidate.get("unresolved_blockers"):
                raise AssertionError(f"{target_path} Alhambra file section blockers changed: {section}")
    if len(unique_source_refs) != 45:
        raise AssertionError(f"Alhambra source file preview unique source refs changed: {len(unique_source_refs)}")
    if seen_file_families != set(expected_preview_family_counts):
        raise AssertionError(f"Alhambra source file preview families changed: {seen_file_families}")

    english_file = _alhambra_source_file_preview(alhambra_source_file_preview, alhambra_file_targets["english"])
    simp_chinese_file = _alhambra_source_file_preview(
        alhambra_source_file_preview,
        alhambra_file_targets["simp_chinese"],
    )
    if english_file.get("localization_language") != "english":
        raise AssertionError(f"English localization file preview language changed: {english_file}")
    if simp_chinese_file.get("localization_language") != "simp_chinese":
        raise AssertionError(f"Simplified Chinese localization file preview language changed: {simp_chinese_file}")
    for localization_file, language in ((english_file, "english"), (simp_chinese_file, "simp_chinese")):
        boundary = localization_file.get("localization_language_boundary")
        if (
            not isinstance(boundary, dict)
            or boundary.get("language") != language
            or set(boundary.get("required_languages", [])) != {"english", "simp_chinese"}
            or boundary.get("language_target_paths") != {
                "english": alhambra_file_targets["english"],
                "simp_chinese": alhambra_file_targets["simp_chinese"],
            }
            or boundary.get("separate_language_target") is not True
            or boundary.get("may_write_src") is not False
            or boundary.get("writes_src") is not False
            or boundary.get("source_writer_allowed") is not False
        ):
            raise AssertionError(f"{language} localization file preview lost split boundary: {localization_file}")
        for section in localization_file.get("structured_body_sections", []) or []:
            if section.get("localization_language") != language:
                raise AssertionError(f"{language} localization section language changed: {section}")

    listener_file = _alhambra_source_file_preview(alhambra_source_file_preview, alhambra_file_targets["listener"])
    if listener_file.get("families") != ["listener"] or listener_file.get("artifact_count") != 1:
        raise AssertionError(f"Alhambra listener file preview changed: {listener_file}")
    listener_file_body = listener_file["structured_body_sections"][0]["structured_body_candidate"]
    if not isinstance(listener_file_body.get("on_action_hook_linkage_plan"), dict):
        raise AssertionError(f"Alhambra listener file preview lost hook linkage: {listener_file}")
    if not isinstance(listener_file_body.get("selected_ritual_trigger_linkage"), dict):
        raise AssertionError(f"Alhambra listener file preview lost selected trigger linkage: {listener_file}")
    if not isinstance(listener_file_body.get("war_scope_availability_persistence_plan"), dict):
        raise AssertionError(f"Alhambra listener file preview lost war-scope plan: {listener_file}")

    def assert_alhambra_file_preview_error(name: str, report: dict, needle: str) -> None:
        errors = validate_repeated_entity_row_alhambra_source_file_preview(report)
        if not any(needle in error for error in errors):
            raise AssertionError(f"{name} Alhambra source file preview negative was not caught: {errors}")

    wrong_pilot_file_preview = deepcopy(alhambra_source_file_preview)
    wrong_pilot_file_preview["pilot_key"] = "unique_dome_of_the_rock"
    assert_alhambra_file_preview_error(
        "wrong pilot",
        wrong_pilot_file_preview,
        "pilot_key must be unique_alhambra",
    )

    missing_target_file_preview = deepcopy(alhambra_source_file_preview)
    missing_target_file_preview["file_previews"] = [
        preview
        for preview in missing_target_file_preview["file_previews"]
        if preview.get("target_path") != alhambra_file_targets["english"]
    ]
    assert_alhambra_file_preview_error(
        "missing target",
        missing_target_file_preview,
        "missing required target path",
    )

    wrong_count_file_preview = deepcopy(alhambra_source_file_preview)
    wrong_count_file_preview["artifact_count"] = 44
    wrong_count_file_preview["summary"]["artifact_count"] = 44
    assert_alhambra_file_preview_error(
        "wrong artifact count",
        wrong_count_file_preview,
        "artifact_count must be 45",
    )

    source_ready_file_preview = deepcopy(alhambra_source_file_preview)
    _alhambra_source_file_preview(source_ready_file_preview, alhambra_file_targets["effect_cleanup"])[
        "structured_body_sections"
    ][0]["source_ready"] = True
    assert_alhambra_file_preview_error(
        "source_ready",
        source_ready_file_preview,
        "source_ready/verified/backend_ready",
    )

    backend_ready_file_preview = deepcopy(alhambra_source_file_preview)
    _alhambra_source_file_preview(backend_ready_file_preview, alhambra_file_targets["listener"])[
        "structured_body_sections"
    ][0]["structured_body_candidate"]["backend_ready"] = True
    assert_alhambra_file_preview_error(
        "backend_ready",
        backend_ready_file_preview,
        "source_ready/verified/backend_ready",
    )

    verified_file_preview = deepcopy(alhambra_source_file_preview)
    _alhambra_source_file_preview(verified_file_preview, alhambra_file_targets["event"])[
        "structured_body_sections"
    ][0]["structured_body_candidate"]["verified"] = True
    assert_alhambra_file_preview_error(
        "verified",
        verified_file_preview,
        "source_ready/verified/backend_ready",
    )

    writable_file_preview = deepcopy(alhambra_source_file_preview)
    _alhambra_source_file_preview(writable_file_preview, alhambra_file_targets["effect_cleanup"])[
        "may_write_src"
    ] = True
    assert_alhambra_file_preview_error(
        "may_write_src",
        writable_file_preview,
        "may_write_src must be false",
    )

    writes_src_file_preview = deepcopy(alhambra_source_file_preview)
    _alhambra_source_file_preview(writes_src_file_preview, alhambra_file_targets["trigger"])[
        "structured_body_sections"
    ][0]["structured_body_candidate"]["writes_src"] = True
    assert_alhambra_file_preview_error(
        "writes_src",
        writes_src_file_preview,
        "writes_src must be false",
    )

    source_writer_allowed_file_preview = deepcopy(alhambra_source_file_preview)
    _alhambra_source_file_preview(source_writer_allowed_file_preview, alhambra_file_targets["gui"])[
        "source_writer_allowed"
    ] = True
    assert_alhambra_file_preview_error(
        "source_writer_allowed",
        source_writer_allowed_file_preview,
        "source_writer_allowed must be false",
    )

    collapsed_localization_file_preview = deepcopy(alhambra_source_file_preview)
    del _alhambra_source_file_preview(
        collapsed_localization_file_preview,
        alhambra_file_targets["english"],
    )["localization_language_boundary"]
    assert_alhambra_file_preview_error(
        "missing localization boundary",
        collapsed_localization_file_preview,
        "localization language boundary",
    )

    missing_hook_file_preview = deepcopy(alhambra_source_file_preview)
    del _alhambra_source_file_preview(missing_hook_file_preview, alhambra_file_targets["listener"])[
        "structured_body_sections"
    ][0]["structured_body_candidate"]["on_action_hook_linkage_plan"]
    assert_alhambra_file_preview_error(
        "missing listener hook",
        missing_hook_file_preview,
        "on_action hook linkage",
    )

    missing_trigger_file_preview = deepcopy(alhambra_source_file_preview)
    del _alhambra_source_file_preview(missing_trigger_file_preview, alhambra_file_targets["listener"])[
        "structured_body_sections"
    ][0]["structured_body_candidate"]["selected_ritual_trigger_linkage"]
    assert_alhambra_file_preview_error(
        "missing selected trigger",
        missing_trigger_file_preview,
        "selected ritual trigger linkage",
    )

    missing_war_scope_file_preview = deepcopy(alhambra_source_file_preview)
    del _alhambra_source_file_preview(missing_war_scope_file_preview, alhambra_file_targets["listener"])[
        "structured_body_sections"
    ][0]["structured_body_candidate"]["war_scope_availability_persistence_plan"]
    assert_alhambra_file_preview_error(
        "missing war scope",
        missing_war_scope_file_preview,
        "war-scope persistence plan",
    )

    alhambra_source_file_validation_evidence = (
        repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
            spec_data,
            source_file_preview=alhambra_source_file_preview,
        )
    )
    if alhambra_source_file_validation_evidence["validation_errors"]:
        raise AssertionError(
            "Alhambra source file validation evidence unexpectedly failed validation: "
            f"{alhambra_source_file_validation_evidence['validation_errors']}"
        )
    validation_summary = alhambra_source_file_validation_evidence.get("summary", {})
    if alhambra_source_file_validation_evidence.get("pilot_key") != "unique_alhambra":
        raise AssertionError(
            f"Alhambra source file validation evidence pilot changed: {alhambra_source_file_validation_evidence}"
        )
    if validation_summary.get("evidence_pack_count") != 7:
        raise AssertionError(f"Alhambra source file validation evidence pack count changed: {validation_summary}")
    if validation_summary.get("artifact_count") != 45:
        raise AssertionError(f"Alhambra source file validation evidence artifact count changed: {validation_summary}")
    if alhambra_source_file_validation_evidence.get("file_section_count") != 55:
        raise AssertionError(
            "Alhambra source file validation evidence expanded file-section count changed: "
            f"{alhambra_source_file_validation_evidence}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if validation_summary.get(count_key) != 0:
            raise AssertionError(f"Alhambra source file validation evidence {count_key} changed: {validation_summary}")
        if alhambra_source_file_validation_evidence.get(count_key) != 0:
            raise AssertionError(
                f"Alhambra source file validation evidence report {count_key} changed: "
                f"{alhambra_source_file_validation_evidence}"
            )
    if {
        pack.get("target_path")
        for pack in alhambra_source_file_validation_evidence.get("evidence_packs", []) or []
    } != set(alhambra_file_targets.values()):
        raise AssertionError(
            "Alhambra source file validation evidence did not expose exact target paths: "
            f"{alhambra_source_file_validation_evidence.get('evidence_packs')}"
        )

    allowed_evidence_statuses = {"interface_candidate", "blocked"}
    validation_source_refs: set[tuple[str, str, str, str]] = set()
    for target_path, expected_count in expected_alhambra_file_counts.items():
        pack = _alhambra_source_file_validation_pack(alhambra_source_file_validation_evidence, target_path)
        preview = _alhambra_source_file_preview(alhambra_source_file_preview, target_path)
        if pack.get("artifact_count") != expected_count:
            raise AssertionError(f"{target_path} validation evidence artifact count changed: {pack}")
        if pack.get("families") != expected_alhambra_file_families[target_path]:
            raise AssertionError(f"{target_path} validation evidence families changed: {pack}")
        if pack.get("source_file_preview_ref", {}).get("artifact_count") != preview.get("artifact_count"):
            raise AssertionError(f"{target_path} validation evidence lost preview artifact count: {pack}")
        if pack.get("source_file_preview_ref", {}).get("families") != preview.get("families"):
            raise AssertionError(f"{target_path} validation evidence lost preview families: {pack}")
        if pack.get("evidence_status") not in allowed_evidence_statuses:
            raise AssertionError(f"{target_path} validation evidence status changed: {pack}")
        if not pack.get("syntax_reference_paths"):
            raise AssertionError(f"{target_path} validation evidence lost syntax refs: {pack}")
        for syntax_path in pack.get("syntax_reference_paths", []) or []:
            if not (REPO_ROOT / syntax_path).exists():
                raise AssertionError(f"{target_path} syntax reference does not exist: {syntax_path}")
        generator_candidate = pack.get("generator_ownership_candidate")
        if (
            not isinstance(generator_candidate, dict)
            or generator_candidate.get("status") not in allowed_evidence_statuses
            or generator_candidate.get("planned_source_writer_exists") is not False
            or generator_candidate.get("source_writer_allowed") is not False
            or generator_candidate.get("may_write_src") is not False
            or generator_candidate.get("writes_src") is not False
        ):
            raise AssertionError(f"{target_path} validation evidence lost generator ownership boundary: {pack}")
        source_boundary = pack.get("source_target_boundary")
        if (
            not isinstance(source_boundary, dict)
            or source_boundary.get("status") not in allowed_evidence_statuses
            or source_boundary.get("target_path") != target_path
            or source_boundary.get("future_target_only") is not True
            or source_boundary.get("source_writer_allowed") is not False
            or source_boundary.get("may_write_src") is not False
            or source_boundary.get("writes_src") is not False
            or source_boundary.get("source_ready") is not False
            or source_boundary.get("body_emitted") is not False
        ):
            raise AssertionError(f"{target_path} validation evidence lost source-target boundary: {pack}")
        validation_requirements = pack.get("validation_requirements")
        if (
            not isinstance(validation_requirements, dict)
            or validation_requirements.get("status") not in allowed_evidence_statuses
            or sorted(validation_requirements.get("required_validations", []) or [])
            != sorted(preview.get("validation_refs", []) or [])
            or validation_requirements.get("source_writer_allowed") is not False
        ):
            raise AssertionError(f"{target_path} validation evidence lost validation requirements: {pack}")
        if not pack.get("unresolved_blockers"):
            raise AssertionError(f"{target_path} validation evidence lost blockers: {pack}")
        for flag, expected in alhambra_file_flags.items():
            if pack.get(flag) is not expected:
                raise AssertionError(f"{target_path} validation evidence lost {flag}: {pack}")
        for ref in pack.get("source_body_candidate_refs", []) or []:
            validation_source_refs.add(
                (
                    str(ref.get("family", "")),
                    str(ref.get("row_set_key", "")),
                    str(ref.get("artifact_kind", "")),
                    str(ref.get("future_source_target_path", "")),
                )
            )
    if len(validation_source_refs) != 45:
        raise AssertionError(f"Alhambra validation evidence unique source refs changed: {len(validation_source_refs)}")

    english_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        alhambra_file_targets["english"],
    )
    simp_chinese_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        alhambra_file_targets["simp_chinese"],
    )
    for localization_pack, language in (
        (english_validation_pack, "english"),
        (simp_chinese_validation_pack, "simp_chinese"),
    ):
        boundary = localization_pack.get("localization_language_boundary")
        if (
            localization_pack.get("localization_language") != language
            or not isinstance(boundary, dict)
            or boundary.get("language") != language
            or set(boundary.get("required_languages", [])) != {"english", "simp_chinese"}
            or boundary.get("language_target_paths") != {
                "english": alhambra_file_targets["english"],
                "simp_chinese": alhambra_file_targets["simp_chinese"],
            }
            or boundary.get("separate_language_target") is not True
            or boundary.get("may_write_src") is not False
            or boundary.get("writes_src") is not False
            or boundary.get("source_writer_allowed") is not False
        ):
            raise AssertionError(f"{language} validation evidence lost localization split boundary: {localization_pack}")

    listener_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        alhambra_file_targets["listener"],
    )
    listener_linkage = listener_validation_pack.get("listener_linkage_evidence")
    if not isinstance(listener_linkage, dict):
        raise AssertionError(f"Alhambra listener validation evidence lost linkage block: {listener_validation_pack}")
    hook_plan = listener_linkage.get("on_action_hook_linkage_plan")
    if not isinstance(hook_plan, dict) or not {"on_pre_winning_war", "on_ending_war"} <= set(
        hook_plan.get("hooks", []) or []
    ):
        raise AssertionError(f"Alhambra listener validation evidence lost hooks: {listener_validation_pack}")
    if not isinstance(listener_linkage.get("selected_ritual_trigger_linkage"), dict):
        raise AssertionError(f"Alhambra listener validation evidence lost selected trigger: {listener_validation_pack}")
    war_scope = listener_linkage.get("war_scope_availability_persistence_plan")
    if (
        not isinstance(war_scope, dict)
        or war_scope.get("persistence_contract_only") is not True
        or war_scope.get("war_scope_writes_allowed") is not False
    ):
        raise AssertionError(f"Alhambra listener validation evidence lost war-scope boundary: {listener_validation_pack}")

    def assert_alhambra_file_validation_error(name: str, report: dict, needle: str) -> None:
        errors = validate_repeated_entity_row_alhambra_source_file_validation_evidence(report)
        if not any(needle in error for error in errors):
            raise AssertionError(f"{name} Alhambra source file validation evidence negative was not caught: {errors}")

    missing_target_validation = deepcopy(alhambra_source_file_validation_evidence)
    missing_target_validation["evidence_packs"] = [
        pack
        for pack in missing_target_validation["evidence_packs"]
        if pack.get("target_path") != alhambra_file_targets["english"]
    ]
    assert_alhambra_file_validation_error(
        "missing target",
        missing_target_validation,
        "missing required target path",
    )

    wrong_artifact_count_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        wrong_artifact_count_validation,
        alhambra_file_targets["event"],
    )["artifact_count"] = 9
    assert_alhambra_file_validation_error(
        "wrong artifact count",
        wrong_artifact_count_validation,
        "artifact_count mismatch",
    )

    missing_syntax_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        missing_syntax_validation,
        alhambra_file_targets["trigger"],
    )["syntax_reference_paths"] = []
    assert_alhambra_file_validation_error(
        "missing syntax refs",
        missing_syntax_validation,
        "missing syntax_reference_paths",
    )

    missing_generator_validation = deepcopy(alhambra_source_file_validation_evidence)
    del _alhambra_source_file_validation_pack(
        missing_generator_validation,
        alhambra_file_targets["effect_cleanup"],
    )["generator_ownership_candidate"]
    assert_alhambra_file_validation_error(
        "missing generator ownership",
        missing_generator_validation,
        "missing generator ownership candidate",
    )

    missing_boundary_validation = deepcopy(alhambra_source_file_validation_evidence)
    del _alhambra_source_file_validation_pack(
        missing_boundary_validation,
        alhambra_file_targets["gui"],
    )["source_target_boundary"]
    assert_alhambra_file_validation_error(
        "missing source target boundary",
        missing_boundary_validation,
        "missing source target boundary",
    )

    missing_requirements_validation = deepcopy(alhambra_source_file_validation_evidence)
    del _alhambra_source_file_validation_pack(
        missing_requirements_validation,
        alhambra_file_targets["event"],
    )["validation_requirements"]
    assert_alhambra_file_validation_error(
        "missing validation requirements",
        missing_requirements_validation,
        "missing validation requirements",
    )

    no_blockers_validation = deepcopy(alhambra_source_file_validation_evidence)
    no_blockers_pack = _alhambra_source_file_validation_pack(no_blockers_validation, alhambra_file_targets["listener"])
    no_blockers_pack["unresolved_blockers"] = []
    no_blockers_pack["unresolved_writer_blockers"] = []
    assert_alhambra_file_validation_error(
        "cleared blockers",
        no_blockers_validation,
        "unresolved blockers must not be empty",
    )

    writable_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        writable_validation,
        alhambra_file_targets["effect_cleanup"],
    )["may_write_src"] = True
    assert_alhambra_file_validation_error(
        "may_write_src",
        writable_validation,
        "may_write_src must be false",
    )

    writes_src_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        writes_src_validation,
        alhambra_file_targets["trigger"],
    )["validation_requirements"]["writes_src"] = True
    assert_alhambra_file_validation_error(
        "writes_src",
        writes_src_validation,
        "writes_src must be false",
    )

    source_writer_allowed_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        source_writer_allowed_validation,
        alhambra_file_targets["gui"],
    )["source_target_boundary"]["source_writer_allowed"] = True
    assert_alhambra_file_validation_error(
        "source_writer_allowed",
        source_writer_allowed_validation,
        "source_writer_allowed must be false",
    )

    source_ready_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        source_ready_validation,
        alhambra_file_targets["event"],
    )["source_ready"] = True
    assert_alhambra_file_validation_error(
        "source_ready",
        source_ready_validation,
        "source_ready/verified/backend_ready",
    )

    verified_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        verified_validation,
        alhambra_file_targets["event"],
    )["verified"] = True
    assert_alhambra_file_validation_error(
        "verified",
        verified_validation,
        "source_ready/verified/backend_ready",
    )

    backend_ready_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        backend_ready_validation,
        alhambra_file_targets["listener"],
    )["generator_ownership_candidate"]["backend_ready"] = True
    assert_alhambra_file_validation_error(
        "backend_ready",
        backend_ready_validation,
        "source_ready/verified/backend_ready",
    )

    verified_status_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        verified_status_validation,
        alhambra_file_targets["trigger"],
    )["evidence_status"] = "verified"
    assert_alhambra_file_validation_error(
        "verified status",
        verified_status_validation,
        "status must be interface_candidate or blocked",
    )

    collapsed_localization_validation = deepcopy(alhambra_source_file_validation_evidence)
    _alhambra_source_file_validation_pack(
        collapsed_localization_validation,
        alhambra_file_targets["english"],
    )["localization_language_boundary"]["language_target_paths"]["simp_chinese"] = alhambra_file_targets["english"]
    assert_alhambra_file_validation_error(
        "merged localization boundary",
        collapsed_localization_validation,
        "target paths must stay split",
    )

    missing_listener_hook_validation = deepcopy(alhambra_source_file_validation_evidence)
    del _alhambra_source_file_validation_pack(
        missing_listener_hook_validation,
        alhambra_file_targets["listener"],
    )["listener_linkage_evidence"]["on_action_hook_linkage_plan"]
    assert_alhambra_file_validation_error(
        "missing listener hook",
        missing_listener_hook_validation,
        "hook linkage",
    )

    missing_listener_trigger_validation = deepcopy(alhambra_source_file_validation_evidence)
    del _alhambra_source_file_validation_pack(
        missing_listener_trigger_validation,
        alhambra_file_targets["listener"],
    )["listener_linkage_evidence"]["selected_ritual_trigger_linkage"]
    assert_alhambra_file_validation_error(
        "missing listener trigger",
        missing_listener_trigger_validation,
        "selected ritual trigger linkage",
    )

    missing_listener_war_scope_validation = deepcopy(alhambra_source_file_validation_evidence)
    del _alhambra_source_file_validation_pack(
        missing_listener_war_scope_validation,
        alhambra_file_targets["listener"],
    )["listener_linkage_evidence"]["war_scope_availability_persistence_plan"]
    assert_alhambra_file_validation_error(
        "missing listener war scope",
        missing_listener_war_scope_validation,
        "war-scope boundary",
    )

    alhambra_source_generator_contract = repeated_entity_row_alhambra_source_generator_contract_for_payload(
        spec_data,
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )
    if alhambra_source_generator_contract["validation_errors"]:
        raise AssertionError(
            "Alhambra source generator contract unexpectedly failed validation: "
            f"{alhambra_source_generator_contract['validation_errors']}"
        )
    evidence_bound_generator_errors = validate_repeated_entity_row_alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )
    if evidence_bound_generator_errors:
        raise AssertionError(
            "Alhambra source generator contract unexpectedly failed external evidence-bound validation: "
            f"{evidence_bound_generator_errors}"
        )
    generator_contract_summary = alhambra_source_generator_contract.get("summary", {})
    if alhambra_source_generator_contract.get("pilot_key") != "unique_alhambra":
        raise AssertionError(f"Alhambra source generator contract pilot changed: {alhambra_source_generator_contract}")
    if generator_contract_summary.get("generator_contract_count") != 7:
        raise AssertionError(f"Alhambra source generator contract count changed: {generator_contract_summary}")
    if generator_contract_summary.get("artifact_count") != 45:
        raise AssertionError(f"Alhambra source generator contract artifact count changed: {generator_contract_summary}")
    if generator_contract_summary.get("generator_interface_status_summary") != {"contract_drafted": 7}:
        raise AssertionError(f"Alhambra source generator contract statuses changed: {generator_contract_summary}")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if generator_contract_summary.get(count_key) != 0:
            raise AssertionError(f"Alhambra source generator contract {count_key} changed: {generator_contract_summary}")
        if alhambra_source_generator_contract.get(count_key) != 0:
            raise AssertionError(
                f"Alhambra source generator contract report {count_key} changed: "
                f"{alhambra_source_generator_contract}"
            )
    if {
        contract.get("target_path")
        for contract in alhambra_source_generator_contract.get("generator_contracts", []) or []
    } != set(alhambra_file_targets.values()):
        raise AssertionError(
            "Alhambra source generator contract did not expose exact target paths: "
            f"{alhambra_source_generator_contract.get('generator_contracts')}"
        )

    allowed_generator_interface_statuses = {"contract_drafted", "blocked"}
    expected_alhambra_owner_generators = {
        alhambra_file_targets["event"]: "unique_wonder_ritual_event_source_generator",
        alhambra_file_targets["effect_cleanup"]: "unique_wonder_ritual_scripted_effect_source_generator",
        alhambra_file_targets["trigger"]: "unique_wonder_ritual_scripted_trigger_source_generator",
        alhambra_file_targets["gui"]: "unique_wonder_ritual_gui_row_source_generator",
        alhambra_file_targets["listener"]: "unique_wonder_ritual_listener_integration_source_generator",
        alhambra_file_targets["english"]: "unique_wonder_ritual_localization_source_generator",
        alhambra_file_targets["simp_chinese"]: "unique_wonder_ritual_localization_source_generator",
    }
    generator_contract_source_refs: set[tuple[str, str, str, str]] = set()
    for target_path, expected_count in expected_alhambra_file_counts.items():
        contract = _alhambra_source_generator_contract(alhambra_source_generator_contract, target_path)
        validation_pack = _alhambra_source_file_validation_pack(alhambra_source_file_validation_evidence, target_path)
        if contract.get("artifact_count") != expected_count:
            raise AssertionError(f"{target_path} generator contract artifact count changed: {contract}")
        if contract.get("families") != expected_alhambra_file_families[target_path]:
            raise AssertionError(f"{target_path} generator contract families changed: {contract}")
        if contract.get("evidence_pack_ref", {}).get("artifact_count") != validation_pack.get("artifact_count"):
            raise AssertionError(f"{target_path} generator contract lost evidence pack artifact count: {contract}")
        if contract.get("evidence_pack_ref", {}).get("families") != validation_pack.get("families"):
            raise AssertionError(f"{target_path} generator contract lost evidence pack families: {contract}")
        if contract.get("owner_generator") != expected_alhambra_owner_generators[target_path]:
            raise AssertionError(f"{target_path} generator contract owner changed: {contract}")
        if contract.get("generator_interface_status") not in allowed_generator_interface_statuses:
            raise AssertionError(f"{target_path} generator contract status changed: {contract}")
        if contract.get("planned_source_writer_exists") != "interface_contract_exists":
            raise AssertionError(f"{target_path} generator contract did not draft interface contract: {contract}")
        expected_call_signature = (
            f"{expected_alhambra_owner_generators[target_path]}.emit_source_file_contract("
            "source_file_validation_pack: Mapping[str, Any], *, dry_run: bool = True"
            ") -> dict[str, Any]"
        )
        validation_refs = [
            ref
            for ref in validation_pack.get("source_body_candidate_refs", []) or []
            if isinstance(ref, dict)
        ]
        expected_artifact_kinds = sorted(
            {
                str(ref.get("artifact_kind", ""))
                for ref in validation_refs
                if str(ref.get("artifact_kind", "")).strip()
            }
        )
        expected_family_artifact_counts: dict[str, int] = {}
        for ref in validation_refs:
            family = str(ref.get("family", ""))
            if family.strip():
                expected_family_artifact_counts[family] = expected_family_artifact_counts.get(family, 0) + 1
        expected_row_set_keys = sorted(
            {
                str(ref.get("row_set_key", ""))
                for ref in validation_refs
                if str(ref.get("row_set_key", "")).strip()
            }
        )
        expected_future_source_target_paths = sorted(
            {
                str(ref.get("future_source_target_path", ""))
                for ref in validation_refs
                if str(ref.get("future_source_target_path", "")).strip()
            }
        )
        interface_draft = contract.get("generator_interface_draft")
        if (
            not isinstance(interface_draft, dict)
            or interface_draft.get("interface_name")
            != f"{expected_alhambra_owner_generators[target_path]}.emit_source_file_contract"
            or interface_draft.get("proposed_function_name") != "emit_source_file_contract"
            or interface_draft.get("owner_generator") != expected_alhambra_owner_generators[target_path]
            or interface_draft.get("input_parameter") != "source_file_validation_pack"
            or interface_draft.get("output_contract") != "source_file_contract_artifacts"
            or interface_draft.get("call_signature_draft") != expected_call_signature
            or interface_draft.get("target_path") != target_path
            or interface_draft.get("families") != expected_alhambra_file_families[target_path]
            or interface_draft.get("generator_interface_status") != "contract_drafted"
            or interface_draft.get("dry_run_required") is not True
            or interface_draft.get("source_file_level_contract") is not True
            or interface_draft.get("body_emitted") is not False
            or interface_draft.get("source_writer_allowed") is not False
            or interface_draft.get("may_write_src") is not False
            or interface_draft.get("writes_src") is not False
        ):
            raise AssertionError(f"{target_path} generator contract lost source-file interface draft: {contract}")
        input_shape = contract.get("input_data_shape")
        if (
            not isinstance(input_shape, dict)
            or input_shape.get("target_path") != target_path
            or input_shape.get("families") != expected_alhambra_file_families[target_path]
            or input_shape.get("artifact_count") != expected_count
            or input_shape.get("source_body_candidate_ref_count") != expected_count
            or input_shape.get("artifact_kinds") != expected_artifact_kinds
            or input_shape.get("family_artifact_counts") != expected_family_artifact_counts
            or input_shape.get("row_set_keys") != expected_row_set_keys
            or input_shape.get("future_source_target_paths") != expected_future_source_target_paths
            or input_shape.get("source_file_validation_evidence_only") is not True
            or input_shape.get("source_writer_allowed") is not False
            or input_shape.get("may_write_src") is not False
            or input_shape.get("writes_src") is not False
        ):
            raise AssertionError(f"{target_path} generator contract lost input data shape: {contract}")
        output_family = contract.get("output_artifact_family")
        if (
            not isinstance(output_family, dict)
            or output_family.get("target_path") != target_path
            or output_family.get("families") != expected_alhambra_file_families[target_path]
            or output_family.get("artifact_count") != expected_count
            or output_family.get("source_body_candidate_ref_count") != expected_count
            or output_family.get("artifact_kinds") != expected_artifact_kinds
            or output_family.get("family_artifact_counts") != expected_family_artifact_counts
            or output_family.get("row_set_keys") != expected_row_set_keys
            or output_family.get("future_source_target_paths") != expected_future_source_target_paths
            or output_family.get("output_kind") != "source_file_contract_artifacts"
            or output_family.get("output_is_loadable_source") is not False
            or output_family.get("body_emitted") is not False
            or output_family.get("source_writer_allowed") is not False
            or output_family.get("may_write_src") is not False
            or output_family.get("writes_src") is not False
        ):
            raise AssertionError(f"{target_path} generator contract lost output artifact family: {contract}")
        if (
            not isinstance(contract.get("verification_commands"), list)
            or not any("scripts\\test_unique_wonder_ritual_harness.py" in command for command in contract["verification_commands"])
            or not any("scripts\\validate.py --changed --fix --ai-report" in command for command in contract["verification_commands"])
        ):
            raise AssertionError(f"{target_path} generator contract lost verification commands: {contract}")
        if (
            contract.get("source_writer_blocker_reasons") != contract.get("remaining_blockers")
            or not contract.get("source_writer_still_blocked_reason")
        ):
            raise AssertionError(f"{target_path} generator contract lost still-blocked source-writer reasons: {contract}")
        no_write_evidence = contract.get("no_write_source_writer_contract_evidence")
        if (
            not isinstance(no_write_evidence, dict)
            or no_write_evidence.get("target_path") != target_path
            or no_write_evidence.get("target_paths") != [target_path]
            or no_write_evidence.get("generator_interface_draft") != interface_draft
            or no_write_evidence.get("input_data_shape") != input_shape
            or no_write_evidence.get("output_artifact_family") != output_family
            or no_write_evidence.get("verification_commands") != contract.get("verification_commands")
            or no_write_evidence.get("source_writer_blocker_reasons") != contract.get("remaining_blockers")
            or no_write_evidence.get("source_writer_allowed") is not False
            or no_write_evidence.get("may_write_src") is not False
            or no_write_evidence.get("writes_src") is not False
        ):
            raise AssertionError(f"{target_path} generator contract lost source-file no-write evidence: {contract}")
        if not contract.get("required_validations"):
            raise AssertionError(f"{target_path} generator contract lost required validations: {contract}")
        if not contract.get("remaining_blockers"):
            raise AssertionError(f"{target_path} generator contract lost remaining blockers: {contract}")
        source_boundary = contract.get("source_target_boundary")
        if (
            not isinstance(source_boundary, dict)
            or source_boundary.get("status") != "blocked"
            or source_boundary.get("target_path") != target_path
            or source_boundary.get("source_writer_allowed") is not False
            or source_boundary.get("may_write_src") is not False
            or source_boundary.get("writes_src") is not False
            or source_boundary.get("source_ready") is not False
            or source_boundary.get("body_emitted") is not False
        ):
            raise AssertionError(f"{target_path} generator contract lost blocked source-target boundary: {contract}")
        for flag, expected in {
            **alhambra_file_flags,
            "verified": False,
            "backend_ready": False,
        }.items():
            if contract.get(flag) is not expected:
                raise AssertionError(f"{target_path} generator contract lost {flag}: {contract}")
        for ref in contract.get("source_body_candidate_refs", []) or []:
            generator_contract_source_refs.add(
                (
                    str(ref.get("family", "")),
                    str(ref.get("row_set_key", "")),
                    str(ref.get("artifact_kind", "")),
                    str(ref.get("future_source_target_path", "")),
                )
            )
    if len(generator_contract_source_refs) != 45:
        raise AssertionError(
            f"Alhambra generator contract unique source refs changed: {len(generator_contract_source_refs)}"
        )

    english_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        alhambra_file_targets["english"],
    )
    simp_chinese_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        alhambra_file_targets["simp_chinese"],
    )
    for localization_contract, language in (
        (english_generator_contract, "english"),
        (simp_chinese_generator_contract, "simp_chinese"),
    ):
        boundary = localization_contract.get("localization_language_boundary")
        if (
            localization_contract.get("localization_language") != language
            or not isinstance(boundary, dict)
            or boundary.get("language") != language
            or boundary.get("language_target_paths") != {
                "english": alhambra_file_targets["english"],
                "simp_chinese": alhambra_file_targets["simp_chinese"],
            }
            or boundary.get("separate_language_target") is not True
            or boundary.get("may_write_src") is not False
            or boundary.get("writes_src") is not False
            or boundary.get("source_writer_allowed") is not False
        ):
            raise AssertionError(f"{language} generator contract lost localization split boundary: {localization_contract}")

    listener_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        alhambra_file_targets["listener"],
    )
    listener_contract = listener_generator_contract.get("listener_linkage_contract")
    if not isinstance(listener_contract, dict):
        raise AssertionError(f"Alhambra listener generator contract lost linkage block: {listener_generator_contract}")
    listener_hook_plan = listener_contract.get("on_action_hook_linkage_plan")
    if not isinstance(listener_hook_plan, dict) or not {"on_pre_winning_war", "on_ending_war"} <= set(
        listener_hook_plan.get("hooks", []) or []
    ):
        raise AssertionError(f"Alhambra listener generator contract lost hooks: {listener_generator_contract}")
    if not isinstance(listener_contract.get("selected_ritual_trigger_linkage"), dict):
        raise AssertionError(f"Alhambra listener generator contract lost selected trigger: {listener_generator_contract}")
    listener_war_scope = listener_contract.get("war_scope_availability_persistence_plan")
    if (
        not isinstance(listener_war_scope, dict)
        or listener_war_scope.get("persistence_contract_only") is not True
        or listener_war_scope.get("war_scope_writes_allowed") is not False
    ):
        raise AssertionError(f"Alhambra listener generator contract lost war-scope boundary: {listener_generator_contract}")

    def assert_alhambra_generator_contract_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_file_validation_evidence: dict | None = None,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_source_generator_contract(
            report,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(f"{name} Alhambra source generator contract negative was not caught: {errors}")

    missing_target_generator_contract = deepcopy(alhambra_source_generator_contract)
    missing_target_generator_contract["generator_contracts"] = [
        contract
        for contract in missing_target_generator_contract["generator_contracts"]
        if contract.get("target_path") != alhambra_file_targets["english"]
    ]
    assert_alhambra_generator_contract_error(
        "missing target",
        missing_target_generator_contract,
        "missing required target path",
    )

    wrong_artifact_count_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        wrong_artifact_count_generator_contract,
        alhambra_file_targets["event"],
    )["artifact_count"] = 9
    assert_alhambra_generator_contract_error(
        "wrong artifact count",
        wrong_artifact_count_generator_contract,
        "artifact_count mismatch",
    )

    missing_evidence_ref_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_evidence_ref_generator_contract,
        alhambra_file_targets["trigger"],
    )["evidence_pack_ref"]
    assert_alhambra_generator_contract_error(
        "missing evidence pack ref",
        missing_evidence_ref_generator_contract,
        "missing evidence_pack_ref",
    )

    missing_owner_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_owner_generator_contract,
        alhambra_file_targets["effect_cleanup"],
    )["owner_generator"]
    assert_alhambra_generator_contract_error(
        "missing owner generator",
        missing_owner_generator_contract,
        "missing field(s): owner_generator",
    )

    missing_interface_draft_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_interface_draft_generator_contract,
        alhambra_file_targets["event"],
    )["generator_interface_draft"]
    assert_alhambra_generator_contract_error(
        "missing source-file interface draft",
        missing_interface_draft_generator_contract,
        "missing field(s): generator_interface_draft",
    )

    synced_wrong_interface_generator_contract = deepcopy(alhambra_source_generator_contract)
    synced_wrong_interface_contract = _alhambra_source_generator_contract(
        synced_wrong_interface_generator_contract,
        alhambra_file_targets["event"],
    )
    synced_wrong_interface_draft = synced_wrong_interface_contract["generator_interface_draft"]
    synced_wrong_interface_draft["interface_name"] = (
        f"{synced_wrong_interface_contract['owner_generator']}.emit_loadable_source_file"
    )
    synced_wrong_interface_draft["proposed_function_name"] = "emit_loadable_source_file"
    synced_wrong_interface_draft["input_parameter"] = "source_file_pack"
    synced_wrong_interface_draft["output_contract"] = "loadable_source_file"
    synced_wrong_interface_draft["call_signature_draft"] = (
        f"{synced_wrong_interface_contract['owner_generator']}.emit_loadable_source_file("
        "source_file_pack: Mapping[str, Any], *, dry_run: bool = False"
        ") -> str"
    )
    synced_wrong_interface_contract["no_write_source_writer_contract_evidence"]["generator_interface_draft"] = deepcopy(
        synced_wrong_interface_draft
    )
    assert_alhambra_generator_contract_error(
        "synced wrong interface draft",
        synced_wrong_interface_generator_contract,
        "generator interface draft interface_name mismatch",
    )

    missing_input_shape_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_input_shape_generator_contract,
        alhambra_file_targets["english"],
    )["input_data_shape"]
    assert_alhambra_generator_contract_error(
        "missing input data shape",
        missing_input_shape_generator_contract,
        "missing field(s): input_data_shape",
    )

    synced_wrong_input_shape_generator_contract = deepcopy(alhambra_source_generator_contract)
    synced_wrong_input_contract = _alhambra_source_generator_contract(
        synced_wrong_input_shape_generator_contract,
        alhambra_file_targets["english"],
    )
    synced_wrong_input_contract["input_data_shape"]["row_set_keys"] = ["forged_row_set"]
    synced_wrong_input_contract["no_write_source_writer_contract_evidence"]["input_data_shape"] = deepcopy(
        synced_wrong_input_contract["input_data_shape"]
    )
    assert_alhambra_generator_contract_error(
        "synced wrong input row sets",
        synced_wrong_input_shape_generator_contract,
        "input data shape row set keys mismatch",
    )

    collapsed_output_family_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        collapsed_output_family_generator_contract,
        alhambra_file_targets["effect_cleanup"],
    )["output_artifact_family"]["families"] = ["effect"]
    assert_alhambra_generator_contract_error(
        "collapsed output artifact family",
        collapsed_output_family_generator_contract,
        "output artifact family families mismatch",
    )

    synced_wrong_output_family_generator_contract = deepcopy(alhambra_source_generator_contract)
    synced_wrong_output_contract = _alhambra_source_generator_contract(
        synced_wrong_output_family_generator_contract,
        alhambra_file_targets["gui"],
    )
    synced_wrong_output_contract["output_artifact_family"]["future_source_target_paths"] = [
        "src/in_game/gui/panels/organization/forged_unique_alhambra_ritual.gui"
    ]
    synced_wrong_output_contract["no_write_source_writer_contract_evidence"]["output_artifact_family"] = deepcopy(
        synced_wrong_output_contract["output_artifact_family"]
    )
    assert_alhambra_generator_contract_error(
        "synced wrong output future target paths",
        synced_wrong_output_family_generator_contract,
        "output artifact family future source target paths mismatch",
    )

    synced_forged_ref_row_set_generator_contract = deepcopy(alhambra_source_generator_contract)
    synced_forged_ref_row_set_contract = _alhambra_source_generator_contract(
        synced_forged_ref_row_set_generator_contract,
        alhambra_file_targets["event"],
    )
    synced_forged_ref_row_set_contract["source_body_candidate_refs"][0]["row_set_key"] = "forged_row_set"
    _sync_alhambra_generator_contract_ref_derivatives(synced_forged_ref_row_set_contract)
    _sync_alhambra_generator_report_ref_summary(synced_forged_ref_row_set_generator_contract)
    assert_alhambra_generator_contract_error(
        "synced forged source ref row set",
        synced_forged_ref_row_set_generator_contract,
        "source body candidate refs provenance mismatch",
    )

    synced_forged_ref_future_path_generator_contract = deepcopy(alhambra_source_generator_contract)
    synced_forged_ref_future_path_contract = _alhambra_source_generator_contract(
        synced_forged_ref_future_path_generator_contract,
        alhambra_file_targets["gui"],
    )
    synced_forged_ref_future_path_contract["source_body_candidate_refs"][0]["future_source_target_path"] = (
        "src/in_game/gui/panels/organization/forged_unique_alhambra_ritual.gui"
    )
    _sync_alhambra_generator_contract_ref_derivatives(synced_forged_ref_future_path_contract)
    _sync_alhambra_generator_report_ref_summary(synced_forged_ref_future_path_generator_contract)
    assert_alhambra_generator_contract_error(
        "synced forged source ref future target path",
        synced_forged_ref_future_path_generator_contract,
        "source body candidate refs provenance mismatch",
    )

    external_evidence_forged_ref_validation = deepcopy(alhambra_source_file_validation_evidence)
    external_evidence_forged_ref_pack = _alhambra_source_file_validation_pack(
        external_evidence_forged_ref_validation,
        alhambra_file_targets["event"],
    )
    external_evidence_forged_ref_pack["source_body_candidate_refs"][0]["row_set_key"] = "forged_row_set"
    external_evidence_forged_ref_generator_contract = repeated_entity_row_alhambra_source_generator_contract_for_payload(
        spec_data,
        source_file_validation_evidence=external_evidence_forged_ref_validation,
    )
    if external_evidence_forged_ref_generator_contract["validation_errors"]:
        raise AssertionError(
            "Externally forged Alhambra generator contract should remain internally self-consistent before "
            "the original validation evidence is applied: "
            f"{external_evidence_forged_ref_generator_contract['validation_errors']}"
        )
    assert_alhambra_generator_contract_error(
        "external evidence-bound synced forged source refs",
        external_evidence_forged_ref_generator_contract,
        "external validation evidence mismatch",
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )

    missing_verification_command_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        missing_verification_command_generator_contract,
        alhambra_file_targets["trigger"],
    )["verification_commands"] = []
    assert_alhambra_generator_contract_error(
        "missing verification commands",
        missing_verification_command_generator_contract,
        "verification commands mismatch",
    )

    missing_no_write_source_file_evidence_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_no_write_source_file_evidence_generator_contract,
        alhambra_file_targets["simp_chinese"],
    )["no_write_source_writer_contract_evidence"]
    assert_alhambra_generator_contract_error(
        "missing source-file no-write evidence",
        missing_no_write_source_file_evidence_generator_contract,
        "missing field(s): no_write_source_writer_contract_evidence",
    )

    mismatched_family_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        mismatched_family_generator_contract,
        alhambra_file_targets["gui"],
    )["families"] = ["event"]
    assert_alhambra_generator_contract_error(
        "family target mismatch",
        mismatched_family_generator_contract,
        "families mismatch",
    )

    unblocked_boundary_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        unblocked_boundary_generator_contract,
        alhambra_file_targets["listener"],
    )["source_target_boundary"]["status"] = "contract_drafted"
    assert_alhambra_generator_contract_error(
        "unblocked boundary",
        unblocked_boundary_generator_contract,
        "source target boundary must stay blocked",
    )

    missing_validations_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        missing_validations_generator_contract,
        alhambra_file_targets["event"],
    )["required_validations"] = []
    assert_alhambra_generator_contract_error(
        "missing required validations",
        missing_validations_generator_contract,
        "required_validations must not be empty",
    )

    cleared_blockers_generator_contract = deepcopy(alhambra_source_generator_contract)
    cleared_blockers_contract = _alhambra_source_generator_contract(
        cleared_blockers_generator_contract,
        alhambra_file_targets["listener"],
    )
    cleared_blockers_contract["remaining_blockers"] = []
    cleared_blockers_contract["unresolved_writer_blockers"] = []
    assert_alhambra_generator_contract_error(
        "cleared blockers",
        cleared_blockers_generator_contract,
        "remaining_blockers must not be empty",
    )

    source_ready_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        source_ready_generator_contract,
        alhambra_file_targets["event"],
    )["source_ready"] = True
    assert_alhambra_generator_contract_error(
        "source_ready",
        source_ready_generator_contract,
        "source_ready/verified/backend_ready",
    )

    verified_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        verified_generator_contract,
        alhambra_file_targets["event"],
    )["verified"] = True
    assert_alhambra_generator_contract_error(
        "verified",
        verified_generator_contract,
        "source_ready/verified/backend_ready",
    )

    backend_ready_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        backend_ready_generator_contract,
        alhambra_file_targets["listener"],
    )["backend_ready"] = True
    assert_alhambra_generator_contract_error(
        "backend_ready",
        backend_ready_generator_contract,
        "source_ready/verified/backend_ready",
    )

    source_writer_allowed_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        source_writer_allowed_generator_contract,
        alhambra_file_targets["gui"],
    )["source_writer_allowed"] = True
    assert_alhambra_generator_contract_error(
        "source_writer_allowed",
        source_writer_allowed_generator_contract,
        "source_writer_allowed must be false",
    )

    may_write_src_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        may_write_src_generator_contract,
        alhambra_file_targets["effect_cleanup"],
    )["may_write_src"] = True
    assert_alhambra_generator_contract_error(
        "may_write_src",
        may_write_src_generator_contract,
        "may_write_src must be false",
    )

    writes_src_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        writes_src_generator_contract,
        alhambra_file_targets["trigger"],
    )["writes_src"] = True
    assert_alhambra_generator_contract_error(
        "writes_src",
        writes_src_generator_contract,
        "writes_src must be false",
    )

    collapsed_localization_generator_contract = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        collapsed_localization_generator_contract,
        alhambra_file_targets["english"],
    )["localization_language_boundary"]["language_target_paths"]["simp_chinese"] = alhambra_file_targets["english"]
    assert_alhambra_generator_contract_error(
        "merged localization boundary",
        collapsed_localization_generator_contract,
        "target paths must stay split",
    )

    missing_listener_hook_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_listener_hook_generator_contract,
        alhambra_file_targets["listener"],
    )["listener_linkage_contract"]["on_action_hook_linkage_plan"]
    assert_alhambra_generator_contract_error(
        "missing listener hook",
        missing_listener_hook_generator_contract,
        "hook linkage",
    )

    missing_listener_trigger_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_listener_trigger_generator_contract,
        alhambra_file_targets["listener"],
    )["listener_linkage_contract"]["selected_ritual_trigger_linkage"]
    assert_alhambra_generator_contract_error(
        "missing listener trigger",
        missing_listener_trigger_generator_contract,
        "selected ritual trigger linkage",
    )

    missing_listener_war_scope_generator_contract = deepcopy(alhambra_source_generator_contract)
    del _alhambra_source_generator_contract(
        missing_listener_war_scope_generator_contract,
        alhambra_file_targets["listener"],
    )["listener_linkage_contract"]["war_scope_availability_persistence_plan"]
    assert_alhambra_generator_contract_error(
        "missing listener war scope",
        missing_listener_war_scope_generator_contract,
        "war-scope boundary",
    )

    alhambra_event_source_generator_interface = (
        repeated_entity_row_alhambra_event_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if alhambra_event_source_generator_interface["validation_errors"]:
        raise AssertionError(
            "Alhambra event source generator interface unexpectedly failed validation: "
            f"{alhambra_event_source_generator_interface['validation_errors']}"
        )
    evidence_bound_event_interface_errors = (
        validate_repeated_entity_row_alhambra_event_source_generator_interface(
            alhambra_event_source_generator_interface,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if evidence_bound_event_interface_errors:
        raise AssertionError(
            "Alhambra event source generator interface unexpectedly failed external evidence-bound validation: "
            f"{evidence_bound_event_interface_errors}"
        )
    event_interface_target = alhambra_file_targets["event"]
    event_interface_summary = alhambra_event_source_generator_interface.get("summary", {})
    if event_interface_summary.get("interface_count") != 1:
        raise AssertionError(f"Alhambra event source generator interface count changed: {event_interface_summary}")
    if event_interface_summary.get("artifact_count") != 8:
        raise AssertionError(
            f"Alhambra event source generator interface artifact count changed: {event_interface_summary}"
        )
    if event_interface_summary.get("output_kind") != "source_file_contract_artifacts":
        raise AssertionError(f"Alhambra event source generator interface output kind changed: {event_interface_summary}")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if event_interface_summary.get(count_key) != 0:
            raise AssertionError(
                f"Alhambra event source generator interface {count_key} changed: {event_interface_summary}"
            )
        if alhambra_event_source_generator_interface.get(count_key) != 0:
            raise AssertionError(
                "Alhambra event source generator interface report no-write count changed: "
                f"{alhambra_event_source_generator_interface}"
            )
    if alhambra_event_source_generator_interface.get("required_target_paths") != [event_interface_target]:
        raise AssertionError(
            "Alhambra event source generator interface should expose only the event target: "
            f"{alhambra_event_source_generator_interface.get('required_target_paths')}"
        )
    if alhambra_event_source_generator_interface.get("output_is_loadable_source") is not False:
        raise AssertionError("Alhambra event source generator interface must not output loadable source")
    if (
        alhambra_event_source_generator_interface.get("source_writer_allowed") is not False
        or alhambra_event_source_generator_interface.get("may_write_src") is not False
        or alhambra_event_source_generator_interface.get("writes_src") is not False
    ):
        raise AssertionError(f"Alhambra event source generator interface no-write flags changed")

    event_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        event_interface_target,
    )
    event_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        event_interface_target,
    )
    event_generator_interfaces = alhambra_event_source_generator_interface.get("source_generator_interfaces", [])
    if len(event_generator_interfaces) != 1:
        raise AssertionError(
            f"Alhambra event source generator interface should expose one interface: {event_generator_interfaces}"
        )
    event_generator_interface = event_generator_interfaces[0]
    if (
        event_generator_interface.get("family") != "event"
        or event_generator_interface.get("target_path") != event_interface_target
        or event_generator_interface.get("owner_generator") != "unique_wonder_ritual_event_source_generator"
        or event_generator_interface.get("output_contract") != "source_file_contract_artifacts"
        or event_generator_interface.get("dry_run_required") is not True
        or event_generator_interface.get("memory_report_only") is not True
        or event_generator_interface.get("source_writer_allowed") is not False
        or event_generator_interface.get("may_write_src") is not False
        or event_generator_interface.get("writes_src") is not False
        or event_generator_interface.get("source_file_validation_evidence_ref")
        != event_generator_contract.get("evidence_pack_ref")
    ):
        raise AssertionError(
            f"Alhambra event source generator interface lost no-write interface shape: {event_generator_interface}"
        )

    event_contract_artifacts = alhambra_event_source_generator_interface.get("source_file_contract_artifacts", [])
    if len(event_contract_artifacts) != expected_alhambra_file_counts[event_interface_target]:
        raise AssertionError(
            f"Alhambra event source generator interface artifact list changed: {event_contract_artifacts}"
        )
    event_contract_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for ref in event_generator_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    event_artifact_ref_keys = {
        (
            str(artifact.get("source_body_candidate_ref", {}).get("family", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("row_set_key", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("artifact_kind", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("future_source_target_path", "")),
        )
        for artifact in event_contract_artifacts
        if isinstance(artifact, dict)
    }
    if event_artifact_ref_keys != event_contract_ref_keys or len(event_artifact_ref_keys) != 8:
        raise AssertionError(
            "Alhambra event source generator interface lost external source refs: "
            f"{event_artifact_ref_keys}"
        )
    for artifact in event_contract_artifacts:
        if (
            artifact.get("family") != "event"
            or artifact.get("target_path") != event_interface_target
            or artifact.get("future_source_target_path") != event_interface_target
            or artifact.get("output_kind") != "source_file_contract_artifacts"
            or artifact.get("output_is_loadable_source") is not False
            or artifact.get("source_file_contract_artifact_only") is not True
            or artifact.get("source_generator_interface_prototype_only") is not True
            or artifact.get("event_family_only") is not True
            or artifact.get("memory_report_only") is not True
            or artifact.get("dry_run") is not True
            or artifact.get("dry_run_required") is not True
            or artifact.get("source_file_validation_evidence_ref") != event_generator_contract.get("evidence_pack_ref")
            or artifact.get("source_body_candidate_ref_provenance")
            != event_generator_contract.get("source_body_candidate_ref_provenance")
            or artifact.get("no_write_source_writer_contract_evidence")
            != event_generator_contract.get("no_write_source_writer_contract_evidence")
            or artifact.get("body_emitted") is not False
            or artifact.get("source_ready") is not False
            or artifact.get("verified") is not False
            or artifact.get("backend_ready") is not False
            or artifact.get("source_writer_allowed") is not False
            or artifact.get("may_write_src") is not False
            or artifact.get("writes_src") is not False
        ):
            raise AssertionError(
                f"Alhambra event source generator interface artifact lost no-write contract shape: {artifact}"
            )
    event_draft_ids: list[int] = []
    event_draft_stage_counts: dict[str, int] = {}
    all_contract_source_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for contract in alhambra_source_generator_contract.get("generator_contracts", []) or []
        if isinstance(contract, dict)
        for ref in contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    all_evidence_source_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for pack in alhambra_source_file_validation_evidence.get("evidence_packs", []) or []
        if isinstance(pack, dict)
        for ref in pack.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    for artifact in event_contract_artifacts:
        draft = artifact.get("event_source_body_draft", {})
        if not isinstance(draft, dict):
            raise AssertionError(f"Alhambra event artifact missing source-body draft: {artifact}")
        event_id = draft.get("event_id")
        event_draft_ids.append(event_id)
        stage = str(draft.get("event_stage", ""))
        event_draft_stage_counts[stage] = event_draft_stage_counts.get(stage, 0) + 1
        prefix = f"tv_engineering_department.{event_id}"
        loc_refs = draft.get("localization_key_refs", {})
        allocation = draft.get("event_id_allocation", {})
        option_handoff = draft.get("option_handoff", {})
        options = option_handoff.get("options", []) if isinstance(option_handoff, dict) else []
        expected_slots = ("a", "b") if stage == "retry" else ("a",)
        if (
            draft.get("kind") != "event_source_body_draft"
            or draft.get("event_type") != "country_event"
            or draft.get("namespace") != "tv_engineering_department"
            or draft.get("target_path") != event_interface_target
            or draft.get("future_source_target_path") != event_interface_target
            or draft.get("output_is_loadable_source") is not False
            or draft.get("body_emitted") is not False
            or draft.get("source_writer_allowed") is not False
            or draft.get("may_write_src") is not False
            or draft.get("writes_src") is not False
            or not isinstance(loc_refs, dict)
            or loc_refs.get("title_key") != f"{prefix}.t"
            or loc_refs.get("desc_key") != f"{prefix}.d"
            or loc_refs.get("all_bound") is not True
            or loc_refs.get("unbound_keys") != []
            or allocation.get("declared_source_event_id_window") != "unique_alhambra event_ids 7309-7316"
            or tuple(option.get("option_slot") for option in options) != expected_slots
        ):
            raise AssertionError(f"Alhambra event source-body draft shape changed: {draft}")
        for option in options:
            if (
                option.get("localization_key_ref") != f"{prefix}.{option.get('option_slot')}"
                or option.get("handoff_only") is not True
                or option.get("inline_effect_body_allowed") is not False
                or option.get("inline_trigger_body_allowed") is not False
                or option.get("body_emitted") is not False
                or not option.get("effect_refs")
                or not option.get("trigger_refs")
            ):
                raise AssertionError(f"Alhambra event option handoff draft changed: {option}")
            option_effect_ref_keys = {
                (
                    str(ref.get("family", "")),
                    str(ref.get("row_set_key", "")),
                    str(ref.get("artifact_kind", "")),
                    str(ref.get("future_source_target_path", "")),
                )
                for ref in option.get("effect_refs", []) or []
                if isinstance(ref, dict)
            }
            option_trigger_ref_keys = {
                (
                    str(ref.get("family", "")),
                    str(ref.get("row_set_key", "")),
                    str(ref.get("artifact_kind", "")),
                    str(ref.get("future_source_target_path", "")),
                )
                for ref in option.get("trigger_refs", []) or []
                if isinstance(ref, dict)
            }
            if not option_effect_ref_keys <= all_contract_source_ref_keys & all_evidence_source_ref_keys:
                raise AssertionError(f"Alhambra event option effect refs lost contract/evidence binding: {option}")
            if not option_trigger_ref_keys <= all_contract_source_ref_keys & all_evidence_source_ref_keys:
                raise AssertionError(f"Alhambra event option trigger refs lost contract/evidence binding: {option}")
    if event_draft_ids != list(range(7309, 7317)) or len(set(event_draft_ids)) != 8:
        raise AssertionError(f"Alhambra event source-body draft ids changed: {event_draft_ids}")
    if event_draft_stage_counts != {"opening": 2, "update": 2, "retry": 2, "resolve": 2}:
        raise AssertionError(f"Alhambra event source-body draft stage coverage changed: {event_draft_stage_counts}")
    if event_validation_pack.get("target_path") != event_interface_target:
        raise AssertionError(f"Alhambra event validation pack target changed: {event_validation_pack}")

    def assert_alhambra_event_source_generator_interface_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_generator_contract: dict | None = alhambra_source_generator_contract,
        source_file_validation_evidence: dict | None = alhambra_source_file_validation_evidence,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_event_source_generator_interface(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(
                f"{name} Alhambra event source generator interface negative was not caught: {errors}"
            )

    missing_event_artifact_interface = deepcopy(alhambra_event_source_generator_interface)
    missing_event_artifact_interface["source_file_contract_artifacts"] = (
        missing_event_artifact_interface["source_file_contract_artifacts"][:-1]
    )
    assert_alhambra_event_source_generator_interface_error(
        "missing event artifact",
        missing_event_artifact_interface,
        "artifact_count mismatch",
    )

    writable_event_artifact_interface = deepcopy(alhambra_event_source_generator_interface)
    _alhambra_event_source_file_contract_artifact(
        writable_event_artifact_interface,
        "event_opening_skeleton",
    )["may_write_src"] = True
    assert_alhambra_event_source_generator_interface_error(
        "writable event artifact",
        writable_event_artifact_interface,
        "may_write_src must be false",
    )

    wrong_output_event_interface = deepcopy(alhambra_event_source_generator_interface)
    wrong_output_event_interface["output_kind"] = "loadable_source_file"
    assert_alhambra_event_source_generator_interface_error(
        "wrong output kind",
        wrong_output_event_interface,
        "output_kind must be source_file_contract_artifacts",
    )

    duplicate_event_id_interface = deepcopy(alhambra_event_source_generator_interface)
    duplicate_event_id_interface["source_file_contract_artifacts"][1]["event_source_body_draft"]["event_id"] = (
        duplicate_event_id_interface["source_file_contract_artifacts"][0]["event_source_body_draft"]["event_id"]
    )
    assert_alhambra_event_source_generator_interface_error(
        "duplicate event source-body draft id",
        duplicate_event_id_interface,
        "event source-body draft event ids must be unique",
    )

    drifted_event_id_window_interface = deepcopy(alhambra_event_source_generator_interface)
    for artifact in drifted_event_id_window_interface["source_file_contract_artifacts"]:
        artifact["event_source_body_draft"]["event_id_allocation"][
            "declared_source_event_id_window"
        ] = "unique_alhambra event_ids 7309-7312"
    assert_alhambra_event_source_generator_interface_error(
        "drifted event source-body draft declared id window",
        drifted_event_id_window_interface,
        "declared source event id window must match actual event_source_body_draft.event_id min/max",
    )

    unbound_loc_event_interface = deepcopy(alhambra_event_source_generator_interface)
    _alhambra_event_source_file_contract_artifact(
        unbound_loc_event_interface,
        "event_opening_skeleton",
    )["event_source_body_draft"]["localization_key_refs"]["all_bound"] = False
    assert_alhambra_event_source_generator_interface_error(
        "unbound event source-body draft loc keys",
        unbound_loc_event_interface,
        "localization key refs must be fully bound",
    )

    forged_effect_ref_event_interface = deepcopy(alhambra_event_source_generator_interface)
    _alhambra_event_source_file_contract_artifact(
        forged_effect_ref_event_interface,
        "event_update_skeleton",
    )["event_source_body_draft"]["option_handoff"]["options"][0]["effect_refs"][0][
        "artifact_kind"
    ] = "forged_effect_ref"
    assert_alhambra_event_source_generator_interface_error(
        "forged event source-body draft option effect ref",
        forged_effect_ref_event_interface,
        "option effect refs must come from existing contract/evidence",
    )

    forged_trigger_ref_event_interface = deepcopy(alhambra_event_source_generator_interface)
    _alhambra_event_source_file_contract_artifact(
        forged_trigger_ref_event_interface,
        "event_resolve_skeleton",
    )["event_source_body_draft"]["option_handoff"]["options"][0]["trigger_refs"][0][
        "artifact_kind"
    ] = "forged_trigger_ref"
    assert_alhambra_event_source_generator_interface_error(
        "forged event source-body draft option trigger ref",
        forged_trigger_ref_event_interface,
        "option trigger refs must come from existing contract/evidence",
    )

    forged_ref_event_interface = deepcopy(alhambra_event_source_generator_interface)
    _alhambra_event_source_file_contract_artifact(
        forged_ref_event_interface,
        "event_retry_skeleton",
    )["source_body_candidate_ref"]["row_set_key"] = "forged_row_set"
    assert_alhambra_event_source_generator_interface_error(
        "forged event source ref",
        forged_ref_event_interface,
        "external validation evidence mismatch",
    )

    external_evidence_forged_event_validation = deepcopy(alhambra_source_file_validation_evidence)
    external_evidence_forged_event_pack = _alhambra_source_file_validation_pack(
        external_evidence_forged_event_validation,
        event_interface_target,
    )
    external_evidence_forged_event_pack["source_body_candidate_refs"][0]["row_set_key"] = "forged_row_set"
    external_evidence_forged_event_generator_contract = (
        repeated_entity_row_alhambra_source_generator_contract_for_payload(
            spec_data,
            source_file_validation_evidence=external_evidence_forged_event_validation,
        )
    )
    external_evidence_forged_event_interface = (
        repeated_entity_row_alhambra_event_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=external_evidence_forged_event_generator_contract,
            source_file_validation_evidence=external_evidence_forged_event_validation,
        )
    )
    if not any(
        "event source-body draft effect refs must not be empty" in error
        or "event source-body draft trigger refs must not be empty" in error
        for error in external_evidence_forged_event_interface["validation_errors"]
    ):
        raise AssertionError(
            "Externally forged Alhambra event interface should fail its own source-body "
            "draft ref binding before the original validation evidence is applied: "
            f"{external_evidence_forged_event_interface['validation_errors']}"
        )
    assert_alhambra_event_source_generator_interface_error(
        "external evidence-bound forged event interface",
        external_evidence_forged_event_interface,
        "external validation evidence",
        source_generator_contract=external_evidence_forged_event_generator_contract,
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )

    detached_event_interface_validation = deepcopy(alhambra_event_source_generator_interface)
    assert_alhambra_event_source_generator_interface_error(
        "missing external validation evidence",
        detached_event_interface_validation,
        "requires external source-file validation evidence",
        source_file_validation_evidence=None,
    )

    alhambra_scripted_effect_cleanup_source_generator_interface = (
        repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if alhambra_scripted_effect_cleanup_source_generator_interface["validation_errors"]:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface unexpectedly failed validation: "
            f"{alhambra_scripted_effect_cleanup_source_generator_interface['validation_errors']}"
        )
    evidence_bound_effect_cleanup_interface_errors = (
        validate_repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface(
            alhambra_scripted_effect_cleanup_source_generator_interface,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if evidence_bound_effect_cleanup_interface_errors:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface unexpectedly failed "
            "external evidence-bound validation: "
            f"{evidence_bound_effect_cleanup_interface_errors}"
        )
    effect_cleanup_interface_target = alhambra_file_targets["effect_cleanup"]
    effect_cleanup_interface_summary = alhambra_scripted_effect_cleanup_source_generator_interface.get("summary", {})
    if effect_cleanup_interface_summary.get("interface_count") != 1:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface count changed: "
            f"{effect_cleanup_interface_summary}"
        )
    if effect_cleanup_interface_summary.get("artifact_count") != expected_alhambra_file_counts[effect_cleanup_interface_target]:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface artifact count changed: "
            f"{effect_cleanup_interface_summary}"
        )
    if effect_cleanup_interface_summary.get("output_kind") != "source_file_contract_artifacts":
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface output kind changed: "
            f"{effect_cleanup_interface_summary}"
        )
    if effect_cleanup_interface_summary.get("family_artifact_counts") != {"cleanup": 8, "effect": 10}:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface family split changed: "
            f"{effect_cleanup_interface_summary}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if effect_cleanup_interface_summary.get(count_key) != 0:
            raise AssertionError(
                "Alhambra scripted-effect/cleanup source generator interface "
                f"{count_key} changed: {effect_cleanup_interface_summary}"
            )
        if alhambra_scripted_effect_cleanup_source_generator_interface.get(count_key) != 0:
            raise AssertionError(
                "Alhambra scripted-effect/cleanup source generator interface report no-write count changed: "
                f"{alhambra_scripted_effect_cleanup_source_generator_interface}"
            )
    if alhambra_scripted_effect_cleanup_source_generator_interface.get("required_target_paths") != [
        effect_cleanup_interface_target
    ]:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface should expose only the shared "
            "scripted-effect target: "
            f"{alhambra_scripted_effect_cleanup_source_generator_interface.get('required_target_paths')}"
        )
    if alhambra_scripted_effect_cleanup_source_generator_interface.get("output_is_loadable_source") is not False:
        raise AssertionError("Alhambra scripted-effect/cleanup source generator interface must not output loadable source")
    if (
        alhambra_scripted_effect_cleanup_source_generator_interface.get("source_writer_allowed") is not False
        or alhambra_scripted_effect_cleanup_source_generator_interface.get("may_write_src") is not False
        or alhambra_scripted_effect_cleanup_source_generator_interface.get("writes_src") is not False
    ):
        raise AssertionError("Alhambra scripted-effect/cleanup source generator interface no-write flags changed")

    effect_cleanup_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        effect_cleanup_interface_target,
    )
    effect_cleanup_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        effect_cleanup_interface_target,
    )
    effect_cleanup_generator_interfaces = (
        alhambra_scripted_effect_cleanup_source_generator_interface.get("source_generator_interfaces", [])
    )
    if len(effect_cleanup_generator_interfaces) != 1:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface should expose one interface: "
            f"{effect_cleanup_generator_interfaces}"
        )
    effect_cleanup_generator_interface = effect_cleanup_generator_interfaces[0]
    if (
        effect_cleanup_generator_interface.get("family") != "scripted_effect_cleanup"
        or effect_cleanup_generator_interface.get("families") != ["cleanup", "effect"]
        or effect_cleanup_generator_interface.get("target_path") != effect_cleanup_interface_target
        or effect_cleanup_generator_interface.get("owner_generator")
        != "unique_wonder_ritual_scripted_effect_source_generator"
        or effect_cleanup_generator_interface.get("output_contract") != "source_file_contract_artifacts"
        or effect_cleanup_generator_interface.get("dry_run_required") is not True
        or effect_cleanup_generator_interface.get("memory_report_only") is not True
        or effect_cleanup_generator_interface.get("source_writer_allowed") is not False
        or effect_cleanup_generator_interface.get("may_write_src") is not False
        or effect_cleanup_generator_interface.get("writes_src") is not False
        or effect_cleanup_generator_interface.get("source_file_validation_evidence_ref")
        != effect_cleanup_generator_contract.get("evidence_pack_ref")
    ):
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface lost no-write interface shape: "
            f"{effect_cleanup_generator_interface}"
        )

    effect_cleanup_contract_artifacts = (
        alhambra_scripted_effect_cleanup_source_generator_interface.get("source_file_contract_artifacts", [])
    )
    if len(effect_cleanup_contract_artifacts) != expected_alhambra_file_counts[effect_cleanup_interface_target]:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface artifact list changed: "
            f"{effect_cleanup_contract_artifacts}"
        )
    effect_cleanup_contract_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for ref in effect_cleanup_generator_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    effect_cleanup_artifact_ref_keys = {
        (
            str(artifact.get("source_body_candidate_ref", {}).get("family", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("row_set_key", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("artifact_kind", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("future_source_target_path", "")),
        )
        for artifact in effect_cleanup_contract_artifacts
        if isinstance(artifact, dict)
    }
    if (
        effect_cleanup_artifact_ref_keys != effect_cleanup_contract_ref_keys
        or len(effect_cleanup_artifact_ref_keys) != expected_alhambra_file_counts[effect_cleanup_interface_target]
    ):
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface lost external source refs: "
            f"{effect_cleanup_artifact_ref_keys}"
        )
    effect_cleanup_artifact_family_counts: dict[str, int] = {}
    effect_cleanup_operation_by_artifact = {
        "scripted_effect_row_init": "row_init",
        "scripted_effect_row_state_write": "row_state_write",
        "scripted_effect_branch_write": "branch_write",
        "scripted_effect_aggregate_refresh": "aggregate_refresh",
        "scripted_effect_cleanup_write": "cleanup_write",
        "cleanup_completion": "completion",
        "cleanup_failure": "failure",
        "cleanup_ownership_loss": "ownership_loss",
        "cleanup_ritual_reset": "reset",
    }
    effect_cleanup_source_body_draft_coverage: dict[str, dict[str, set[str]]] = {}
    for artifact in effect_cleanup_contract_artifacts:
        family = str(artifact.get("family", ""))
        artifact_kind = str(artifact.get("artifact_kind", ""))
        row_set_key = str(artifact.get("row_set_key", ""))
        effect_cleanup_artifact_family_counts[family] = effect_cleanup_artifact_family_counts.get(family, 0) + 1
        if (
            artifact.get("interface_family") != "scripted_effect_cleanup"
            or artifact.get("family") not in {"effect", "cleanup"}
            or artifact.get("target_families") != ["cleanup", "effect"]
            or artifact.get("target_path") != effect_cleanup_interface_target
            or artifact.get("future_source_target_path") != effect_cleanup_interface_target
            or artifact.get("output_kind") != "source_file_contract_artifacts"
            or artifact.get("output_is_loadable_source") is not False
            or artifact.get("source_file_contract_artifact_only") is not True
            or artifact.get("source_generator_interface_prototype_only") is not True
            or artifact.get("scripted_effect_cleanup_target_only") is not True
            or artifact.get("memory_report_only") is not True
            or artifact.get("dry_run") is not True
            or artifact.get("dry_run_required") is not True
            or artifact.get("source_file_validation_evidence_ref")
            != effect_cleanup_generator_contract.get("evidence_pack_ref")
            or artifact.get("source_body_candidate_ref_provenance")
            != effect_cleanup_generator_contract.get("source_body_candidate_ref_provenance")
            or artifact.get("no_write_source_writer_contract_evidence")
            != effect_cleanup_generator_contract.get("no_write_source_writer_contract_evidence")
            or artifact.get("body_emitted") is not False
            or artifact.get("source_ready") is not False
            or artifact.get("verified") is not False
            or artifact.get("backend_ready") is not False
            or artifact.get("source_writer_allowed") is not False
            or artifact.get("may_write_src") is not False
            or artifact.get("writes_src") is not False
        ):
            raise AssertionError(
                "Alhambra scripted-effect/cleanup source generator interface artifact lost no-write contract shape: "
                f"{artifact}"
            )
        draft = artifact.get("scripted_effect_cleanup_source_body_draft", {})
        expected_operation = effect_cleanup_operation_by_artifact.get(artifact_kind, "")
        coverage = draft.get("operation_coverage", {}) if isinstance(draft, dict) else {}
        outline = draft.get("source_body_outline", {}) if isinstance(draft, dict) else {}
        cleanup_boundary = draft.get("cleanup_lifecycle_boundary", {}) if isinstance(draft, dict) else {}
        if (
            not isinstance(draft, dict)
            or draft.get("kind") != "scripted_effect_cleanup_source_body_draft"
            or draft.get("family") != family
            or draft.get("interface_family") != "scripted_effect_cleanup"
            or draft.get("artifact_kind") != artifact_kind
            or draft.get("row_set_key") != row_set_key
            or draft.get("target_path") != effect_cleanup_interface_target
            or draft.get("future_source_target_path") != effect_cleanup_interface_target
            or draft.get("source_type") != "common/scripted_effects"
            or draft.get("operation") != expected_operation
            or draft.get("output_is_loadable_source") is not False
            or draft.get("body_emitted") is not False
            or draft.get("source_ready") is not False
            or draft.get("verified") is not False
            or draft.get("backend_ready") is not False
            or draft.get("source_writer_allowed") is not False
            or draft.get("may_write_src") is not False
            or draft.get("writes_src") is not False
            or coverage.get(expected_operation) is not True
            or coverage.get("body_emitted") is not False
            or outline.get("source_body_emitted") is not False
            or outline.get("loadable_effect_body_allowed") is not False
            or cleanup_boundary.get("cleanup_source_writer_allowed") is not False
        ):
            raise AssertionError(
                "Alhambra scripted-effect/cleanup source-body draft shape changed: "
                f"{draft}"
            )
        row_coverage = effect_cleanup_source_body_draft_coverage.setdefault(
            row_set_key,
            {"effect": set(), "cleanup": set()},
        )
        if family == "effect":
            row_coverage["effect"].add(expected_operation)
        if family == "cleanup":
            row_coverage["cleanup"].add(expected_operation)
    if effect_cleanup_artifact_family_counts != {"cleanup": 8, "effect": 10}:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface artifact family counts changed: "
            f"{effect_cleanup_artifact_family_counts}"
        )
    for row_set_key, coverage in effect_cleanup_source_body_draft_coverage.items():
        if coverage["effect"] != {
            "row_init",
            "row_state_write",
            "branch_write",
            "aggregate_refresh",
            "cleanup_write",
        }:
            raise AssertionError(
                "Alhambra scripted-effect source-body draft effect coverage changed: "
                f"{row_set_key}: {coverage}"
            )
        if coverage["cleanup"] != {"completion", "failure", "ownership_loss", "reset"}:
            raise AssertionError(
                "Alhambra cleanup source-body draft lifecycle coverage changed: "
                f"{row_set_key}: {coverage}"
            )
    if effect_cleanup_validation_pack.get("target_path") != effect_cleanup_interface_target:
        raise AssertionError(f"Alhambra effect/cleanup validation pack target changed: {effect_cleanup_validation_pack}")

    def assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_generator_contract: dict | None = alhambra_source_generator_contract,
        source_file_validation_evidence: dict | None = alhambra_source_file_validation_evidence,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(
                f"{name} Alhambra scripted-effect/cleanup source generator interface negative was not caught: "
                f"{errors}"
            )

    missing_effect_cleanup_artifact_interface = deepcopy(alhambra_scripted_effect_cleanup_source_generator_interface)
    missing_effect_cleanup_artifact_interface["source_file_contract_artifacts"] = (
        missing_effect_cleanup_artifact_interface["source_file_contract_artifacts"][:-1]
    )
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "missing scripted-effect/cleanup artifact",
        missing_effect_cleanup_artifact_interface,
        "artifact_count mismatch",
    )

    writable_effect_cleanup_artifact_interface = deepcopy(alhambra_scripted_effect_cleanup_source_generator_interface)
    _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
        writable_effect_cleanup_artifact_interface,
        "scripted_effect_row_init",
    )["may_write_src"] = True
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "writable scripted-effect artifact",
        writable_effect_cleanup_artifact_interface,
        "may_write_src must be false",
    )

    missing_effect_cleanup_source_body_draft_interface = deepcopy(
        alhambra_scripted_effect_cleanup_source_generator_interface
    )
    del _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
        missing_effect_cleanup_source_body_draft_interface,
        "scripted_effect_row_init",
    )["scripted_effect_cleanup_source_body_draft"]
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "missing scripted-effect/cleanup source-body draft",
        missing_effect_cleanup_source_body_draft_interface,
        "scripted_effect_cleanup_source_body_draft",
    )

    broken_effect_cleanup_source_body_draft_interface = deepcopy(
        alhambra_scripted_effect_cleanup_source_generator_interface
    )
    _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
        broken_effect_cleanup_source_body_draft_interface,
        "cleanup_ownership_loss",
    )["scripted_effect_cleanup_source_body_draft"]["cleanup_lifecycle_boundary"]["ownership_loss"] = False
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "broken scripted-effect/cleanup source-body draft lifecycle coverage",
        broken_effect_cleanup_source_body_draft_interface,
        "active cleanup lifecycle missing",
    )

    wrong_output_effect_cleanup_interface = deepcopy(alhambra_scripted_effect_cleanup_source_generator_interface)
    wrong_output_effect_cleanup_interface["output_kind"] = "loadable_source_file"
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "wrong scripted-effect/cleanup output kind",
        wrong_output_effect_cleanup_interface,
        "output_kind must be source_file_contract_artifacts",
    )

    forged_ref_effect_cleanup_interface = deepcopy(alhambra_scripted_effect_cleanup_source_generator_interface)
    _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
        forged_ref_effect_cleanup_interface,
        "scripted_effect_row_state_write",
    )["source_body_candidate_ref"]["row_set_key"] = "forged_row_set"
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "forged scripted-effect/cleanup source ref",
        forged_ref_effect_cleanup_interface,
        "external validation evidence mismatch",
    )

    external_evidence_forged_effect_cleanup_validation = deepcopy(alhambra_source_file_validation_evidence)
    external_evidence_forged_effect_cleanup_pack = _alhambra_source_file_validation_pack(
        external_evidence_forged_effect_cleanup_validation,
        effect_cleanup_interface_target,
    )
    external_evidence_forged_effect_cleanup_pack["source_body_candidate_refs"][0][
        "row_set_key"
    ] = "forged_row_set"
    external_evidence_forged_effect_cleanup_generator_contract = (
        repeated_entity_row_alhambra_source_generator_contract_for_payload(
            spec_data,
            source_file_validation_evidence=external_evidence_forged_effect_cleanup_validation,
        )
    )
    external_evidence_forged_effect_cleanup_interface = (
        repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=external_evidence_forged_effect_cleanup_generator_contract,
            source_file_validation_evidence=external_evidence_forged_effect_cleanup_validation,
        )
    )
    if not any(
        "source-body draft missing effect operation coverage" in error
        or "source-body draft missing cleanup lifecycle coverage" in error
        for error in external_evidence_forged_effect_cleanup_interface["validation_errors"]
    ):
        raise AssertionError(
            "Externally forged Alhambra scripted-effect/cleanup interface should fail its own "
            "source-body draft row-set coverage before the original validation evidence is applied: "
            f"{external_evidence_forged_effect_cleanup_interface['validation_errors']}"
        )
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "external evidence-bound forged scripted-effect/cleanup interface",
        external_evidence_forged_effect_cleanup_interface,
        "external validation evidence",
        source_generator_contract=external_evidence_forged_effect_cleanup_generator_contract,
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )

    detached_effect_cleanup_interface_validation = deepcopy(alhambra_scripted_effect_cleanup_source_generator_interface)
    assert_alhambra_scripted_effect_cleanup_source_generator_interface_error(
        "missing external validation evidence",
        detached_effect_cleanup_interface_validation,
        "requires external source-file validation evidence",
        source_file_validation_evidence=None,
    )

    alhambra_scripted_trigger_source_generator_interface = (
        repeated_entity_row_alhambra_scripted_trigger_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if alhambra_scripted_trigger_source_generator_interface["validation_errors"]:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface unexpectedly failed validation: "
            f"{alhambra_scripted_trigger_source_generator_interface['validation_errors']}"
        )
    evidence_bound_trigger_interface_errors = (
        validate_repeated_entity_row_alhambra_scripted_trigger_source_generator_interface(
            alhambra_scripted_trigger_source_generator_interface,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if evidence_bound_trigger_interface_errors:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface unexpectedly failed external evidence-bound "
            f"validation: {evidence_bound_trigger_interface_errors}"
        )
    trigger_interface_target = alhambra_file_targets["trigger"]
    trigger_interface_summary = alhambra_scripted_trigger_source_generator_interface.get("summary", {})
    if trigger_interface_summary.get("interface_count") != 1:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface count changed: "
            f"{trigger_interface_summary}"
        )
    if trigger_interface_summary.get("artifact_count") != expected_alhambra_file_counts[trigger_interface_target]:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface artifact count changed: "
            f"{trigger_interface_summary}"
        )
    if trigger_interface_summary.get("output_kind") != "source_file_contract_artifacts":
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface output kind changed: "
            f"{trigger_interface_summary}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if trigger_interface_summary.get(count_key) != 0:
            raise AssertionError(
                "Alhambra scripted-trigger source generator interface "
                f"{count_key} changed: {trigger_interface_summary}"
            )
        if alhambra_scripted_trigger_source_generator_interface.get(count_key) != 0:
            raise AssertionError(
                "Alhambra scripted-trigger source generator interface report no-write count changed: "
                f"{alhambra_scripted_trigger_source_generator_interface}"
            )
    if alhambra_scripted_trigger_source_generator_interface.get("required_target_paths") != [
        trigger_interface_target
    ]:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface should expose only the scripted-trigger target: "
            f"{alhambra_scripted_trigger_source_generator_interface.get('required_target_paths')}"
        )
    if alhambra_scripted_trigger_source_generator_interface.get("output_is_loadable_source") is not False:
        raise AssertionError("Alhambra scripted-trigger source generator interface must not output loadable source")
    if (
        alhambra_scripted_trigger_source_generator_interface.get("source_writer_allowed") is not False
        or alhambra_scripted_trigger_source_generator_interface.get("may_write_src") is not False
        or alhambra_scripted_trigger_source_generator_interface.get("writes_src") is not False
    ):
        raise AssertionError("Alhambra scripted-trigger source generator interface no-write flags changed")

    trigger_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        trigger_interface_target,
    )
    trigger_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        trigger_interface_target,
    )
    trigger_generator_interfaces = (
        alhambra_scripted_trigger_source_generator_interface.get("source_generator_interfaces", [])
    )
    if len(trigger_generator_interfaces) != 1:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface should expose one interface: "
            f"{trigger_generator_interfaces}"
        )
    trigger_generator_interface = trigger_generator_interfaces[0]
    if (
        trigger_generator_interface.get("family") != "trigger"
        or trigger_generator_interface.get("target_path") != trigger_interface_target
        or trigger_generator_interface.get("owner_generator")
        != "unique_wonder_ritual_scripted_trigger_source_generator"
        or trigger_generator_interface.get("output_contract") != "source_file_contract_artifacts"
        or trigger_generator_interface.get("dry_run_required") is not True
        or trigger_generator_interface.get("memory_report_only") is not True
        or trigger_generator_interface.get("source_writer_allowed") is not False
        or trigger_generator_interface.get("may_write_src") is not False
        or trigger_generator_interface.get("writes_src") is not False
        or trigger_generator_interface.get("source_file_validation_evidence_ref")
        != trigger_generator_contract.get("evidence_pack_ref")
    ):
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface lost no-write interface shape: "
            f"{trigger_generator_interface}"
        )

    trigger_contract_artifacts = (
        alhambra_scripted_trigger_source_generator_interface.get("source_file_contract_artifacts", [])
    )
    if len(trigger_contract_artifacts) != expected_alhambra_file_counts[trigger_interface_target]:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface artifact list changed: "
            f"{trigger_contract_artifacts}"
        )
    trigger_contract_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for ref in trigger_generator_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    trigger_artifact_ref_keys = {
        (
            str(artifact.get("source_body_candidate_ref", {}).get("family", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("row_set_key", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("artifact_kind", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("future_source_target_path", "")),
        )
        for artifact in trigger_contract_artifacts
        if isinstance(artifact, dict)
    }
    if (
        trigger_artifact_ref_keys != trigger_contract_ref_keys
        or len(trigger_artifact_ref_keys) != expected_alhambra_file_counts[trigger_interface_target]
    ):
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface lost external source refs: "
            f"{trigger_artifact_ref_keys}"
        )
    for artifact in trigger_contract_artifacts:
        if (
            artifact.get("family") != "trigger"
            or artifact.get("target_path") != trigger_interface_target
            or artifact.get("future_source_target_path") != trigger_interface_target
            or artifact.get("output_kind") != "source_file_contract_artifacts"
            or artifact.get("output_is_loadable_source") is not False
            or artifact.get("source_file_contract_artifact_only") is not True
            or artifact.get("source_generator_interface_prototype_only") is not True
            or artifact.get("scripted_trigger_target_only") is not True
            or artifact.get("memory_report_only") is not True
            or artifact.get("dry_run") is not True
            or artifact.get("dry_run_required") is not True
            or artifact.get("source_file_validation_evidence_ref") != trigger_generator_contract.get("evidence_pack_ref")
            or artifact.get("source_body_candidate_ref_provenance")
            != trigger_generator_contract.get("source_body_candidate_ref_provenance")
            or artifact.get("no_write_source_writer_contract_evidence")
            != trigger_generator_contract.get("no_write_source_writer_contract_evidence")
            or artifact.get("body_emitted") is not False
            or artifact.get("source_ready") is not False
            or artifact.get("verified") is not False
            or artifact.get("backend_ready") is not False
            or artifact.get("source_writer_allowed") is not False
            or artifact.get("may_write_src") is not False
            or artifact.get("writes_src") is not False
        ):
            raise AssertionError(
                "Alhambra scripted-trigger source generator interface artifact lost no-write contract shape: "
                f"{artifact}"
            )
    expected_trigger_draft_groups = {
        "eligibility",
        "row_completion",
        "tooltip_safe_condition_group",
    }
    trigger_draft_coverage: dict[str, set[str]] = {}
    for artifact in trigger_contract_artifacts:
        draft = artifact.get("scripted_trigger_source_body_draft")
        if not isinstance(draft, dict):
            raise AssertionError(f"Alhambra scripted-trigger artifact missing source-body draft: {artifact}")
        row_set_key = str(artifact.get("row_set_key", ""))
        artifact_kind = str(artifact.get("artifact_kind", ""))
        expected_group = {
            "scripted_trigger_eligibility": "eligibility",
            "scripted_trigger_row_completion": "row_completion",
            "scripted_trigger_tooltip_safe_condition_group": "tooltip_safe_condition_group",
        }.get(artifact_kind)
        trigger_draft_coverage.setdefault(row_set_key, set()).add(str(draft.get("tooltip_safe_condition_grouping", {}).get("active_group", "")))
        expected_trigger_name = f"tv_wonder_unique_alhambra_ritual_{row_set_key}_{artifact_kind}_trigger"
        if (
            draft.get("kind") != "scripted_trigger_source_body_draft"
            or draft.get("trigger_name") != expected_trigger_name
            or draft.get("row_set_key") != row_set_key
            or draft.get("artifact_kind") != artifact_kind
            or draft.get("source_type") != "common/scripted_triggers"
            or draft.get("output_is_loadable_source") is not False
            or draft.get("body_emitted") is not False
            or draft.get("source_ready") is not False
            or draft.get("verified") is not False
            or draft.get("backend_ready") is not False
            or draft.get("source_writer_allowed") is not False
            or draft.get("may_write_src") is not False
            or draft.get("writes_src") is not False
        ):
            raise AssertionError(f"Alhambra scripted-trigger source-body draft shape changed: {draft}")
        scope_contract = draft.get("scope_contract", {})
        if (
            scope_contract.get("trigger_name") != expected_trigger_name
            or scope_contract.get("root_scope") != "country"
            or scope_contract.get("scripted_trigger_scope") != "country"
            or scope_contract.get("tooltip_safe") is not True
            or scope_contract.get("row_state_writes_allowed") is not False
            or scope_contract.get("may_write_src") is not False
            or scope_contract.get("body_emitted") is not False
        ):
            raise AssertionError(f"Alhambra scripted-trigger source-body draft scope contract changed: {draft}")
        row_refs = draft.get("row_variable_read_refs", {})
        aggregate_refs = draft.get("aggregate_variable_read_refs", {})
        if (
            row_refs.get("all_bound") is not True
            or not row_refs.get("entity_keys")
            or not row_refs.get("per_row_variable_patterns")
            or aggregate_refs.get("all_bound") is not True
            or not aggregate_refs.get("aggregate_projection_variables")
            or not aggregate_refs.get("node_read_refs")
            or aggregate_refs.get("aggregate_only_row_reads_allowed") is not False
        ):
            raise AssertionError(f"Alhambra scripted-trigger source-body draft variable refs changed: {draft}")
        grouping = draft.get("tooltip_safe_condition_grouping", {})
        if (
            set(grouping.get("required_groups", [])) != expected_trigger_draft_groups
            or grouping.get("active_group") != expected_group
            or grouping.get("condition_group_ref_count") != 3
            or grouping.get("condition_group_refs_bound") is not True
            or grouping.get("custom_tooltip_group_required") is not True
            or grouping.get("predicate_group_only") is not True
            or grouping.get("tooltip_safe") is not True
            or grouping.get("unsafe_write_paths_allowed") is not False
            or grouping.get("inline_effect_calls_allowed") is not False
        ):
            raise AssertionError(f"Alhambra scripted-trigger source-body draft condition grouping changed: {draft}")
        handoff = draft.get("event_effect_handoff_refs", {})
        if (
            handoff.get("all_bound") is not True
            or not handoff.get("event_refs")
            or not handoff.get("effect_refs")
            or not handoff.get("cleanup_refs")
            or handoff.get("handoff_only") is not True
            or handoff.get("inline_event_body_allowed") is not False
            or handoff.get("inline_effect_body_allowed") is not False
            or handoff.get("may_write_src") is not False
            or handoff.get("body_emitted") is not False
        ):
            raise AssertionError(f"Alhambra scripted-trigger source-body draft handoff refs changed: {draft}")
    expected_trigger_draft_coverage = {
        "palace_risk_points": expected_trigger_draft_groups,
        "treaty_clause_register": expected_trigger_draft_groups,
    }
    if trigger_draft_coverage != expected_trigger_draft_coverage:
        raise AssertionError(
            "Alhambra scripted-trigger source-body draft coverage changed: "
            f"{trigger_draft_coverage}"
        )
    if trigger_validation_pack.get("target_path") != trigger_interface_target:
        raise AssertionError(f"Alhambra trigger validation pack target changed: {trigger_validation_pack}")

    def assert_alhambra_scripted_trigger_source_generator_interface_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_generator_contract: dict | None = alhambra_source_generator_contract,
        source_file_validation_evidence: dict | None = alhambra_source_file_validation_evidence,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_scripted_trigger_source_generator_interface(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(
                f"{name} Alhambra scripted-trigger source generator interface negative was not caught: "
                f"{errors}"
            )

    missing_trigger_artifact_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    missing_trigger_artifact_interface["source_file_contract_artifacts"] = (
        missing_trigger_artifact_interface["source_file_contract_artifacts"][:-1]
    )
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "missing scripted-trigger artifact",
        missing_trigger_artifact_interface,
        "artifact_count mismatch",
    )

    writable_trigger_artifact_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        writable_trigger_artifact_interface,
        "scripted_trigger_row_completion",
    )["may_write_src"] = True
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "writable scripted-trigger artifact",
        writable_trigger_artifact_interface,
        "may_write_src must be false",
    )

    missing_trigger_draft_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        missing_trigger_draft_interface,
        "scripted_trigger_row_completion",
    )["scripted_trigger_source_body_draft"] = None
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "missing scripted-trigger source-body draft",
        missing_trigger_draft_interface,
        "missing scripted-trigger source-body draft",
    )

    wrong_row_set_trigger_draft_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        wrong_row_set_trigger_draft_interface,
        "scripted_trigger_eligibility",
    )["scripted_trigger_source_body_draft"]["row_set_key"] = "forged_row_set"
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "wrong scripted-trigger draft row set",
        wrong_row_set_trigger_draft_interface,
        "row_set_key mismatch",
    )

    unbound_variable_ref_trigger_draft_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        unbound_variable_ref_trigger_draft_interface,
        "scripted_trigger_eligibility",
    )["scripted_trigger_source_body_draft"]["row_variable_read_refs"]["all_bound"] = False
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "unbound scripted-trigger draft variable refs",
        unbound_variable_ref_trigger_draft_interface,
        "variable read refs must be bound",
    )

    unsafe_tooltip_group_trigger_draft_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        unsafe_tooltip_group_trigger_draft_interface,
        "scripted_trigger_tooltip_safe_condition_group",
    )["scripted_trigger_source_body_draft"]["tooltip_safe_condition_grouping"]["unsafe_write_paths_allowed"] = True
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "unsafe scripted-trigger draft tooltip group",
        unsafe_tooltip_group_trigger_draft_interface,
        "tooltip-safe condition grouping",
    )

    writable_trigger_draft_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        writable_trigger_draft_interface,
        "scripted_trigger_row_completion",
    )["scripted_trigger_source_body_draft"]["may_write_src"] = True
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "writable scripted-trigger draft",
        writable_trigger_draft_interface,
        "may_write_src must be false",
    )

    body_emitted_trigger_draft_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        body_emitted_trigger_draft_interface,
        "scripted_trigger_row_completion",
    )["scripted_trigger_source_body_draft"]["body_emitted"] = True
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "body-emitted scripted-trigger draft",
        body_emitted_trigger_draft_interface,
        "body_emitted must be false",
    )

    wrong_output_trigger_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    wrong_output_trigger_interface["output_kind"] = "loadable_source_file"
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "wrong scripted-trigger output kind",
        wrong_output_trigger_interface,
        "output_kind must be source_file_contract_artifacts",
    )

    forged_ref_trigger_interface = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    _alhambra_scripted_trigger_source_file_contract_artifact(
        forged_ref_trigger_interface,
        "scripted_trigger_eligibility",
    )["source_body_candidate_ref"]["row_set_key"] = "forged_row_set"
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "forged scripted-trigger source ref",
        forged_ref_trigger_interface,
        "external validation evidence mismatch",
    )

    external_evidence_forged_trigger_validation = deepcopy(alhambra_source_file_validation_evidence)
    external_evidence_forged_trigger_pack = _alhambra_source_file_validation_pack(
        external_evidence_forged_trigger_validation,
        trigger_interface_target,
    )
    external_evidence_forged_trigger_pack["source_body_candidate_refs"][0]["row_set_key"] = "forged_row_set"
    external_evidence_forged_trigger_generator_contract = (
        repeated_entity_row_alhambra_source_generator_contract_for_payload(
            spec_data,
            source_file_validation_evidence=external_evidence_forged_trigger_validation,
        )
    )
    external_evidence_forged_trigger_interface = (
        repeated_entity_row_alhambra_scripted_trigger_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=external_evidence_forged_trigger_generator_contract,
            source_file_validation_evidence=external_evidence_forged_trigger_validation,
        )
    )
    if not any(
        "variable read refs must be bound" in error
        or "source-body draft coverage" in error
        for error in external_evidence_forged_trigger_interface["validation_errors"]
    ):
        raise AssertionError(
            "Externally forged Alhambra scripted-trigger interface should fail its own source-body "
            "draft row-set binding before the original validation evidence is applied: "
            f"{external_evidence_forged_trigger_interface['validation_errors']}"
        )
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "external evidence-bound forged scripted-trigger interface",
        external_evidence_forged_trigger_interface,
        "external validation evidence",
        source_generator_contract=external_evidence_forged_trigger_generator_contract,
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )

    detached_trigger_interface_validation = deepcopy(alhambra_scripted_trigger_source_generator_interface)
    assert_alhambra_scripted_trigger_source_generator_interface_error(
        "missing external validation evidence",
        detached_trigger_interface_validation,
        "requires external source-file validation evidence",
        source_file_validation_evidence=None,
    )

    alhambra_gui_source_generator_interface = (
        repeated_entity_row_alhambra_gui_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if alhambra_gui_source_generator_interface["validation_errors"]:
        raise AssertionError(
            "Alhambra GUI source generator interface unexpectedly failed validation: "
            f"{alhambra_gui_source_generator_interface['validation_errors']}"
        )
    evidence_bound_gui_interface_errors = (
        validate_repeated_entity_row_alhambra_gui_source_generator_interface(
            alhambra_gui_source_generator_interface,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if evidence_bound_gui_interface_errors:
        raise AssertionError(
            "Alhambra GUI source generator interface unexpectedly failed external evidence-bound validation: "
            f"{evidence_bound_gui_interface_errors}"
        )
    gui_interface_target = alhambra_file_targets["gui"]
    gui_interface_summary = alhambra_gui_source_generator_interface.get("summary", {})
    if gui_interface_summary.get("interface_count") != 1:
        raise AssertionError(
            "Alhambra GUI source generator interface count changed: "
            f"{gui_interface_summary}"
        )
    if gui_interface_summary.get("artifact_count") != expected_alhambra_file_counts[gui_interface_target]:
        raise AssertionError(
            "Alhambra GUI source generator interface artifact count changed: "
            f"{gui_interface_summary}"
        )
    if gui_interface_summary.get("artifact_count") != 2:
        raise AssertionError(
            "Alhambra GUI source generator interface must emit exactly 2 report-level artifacts: "
            f"{gui_interface_summary}"
        )
    if gui_interface_summary.get("output_kind") != "source_file_contract_artifacts":
        raise AssertionError(
            "Alhambra GUI source generator interface output kind changed: "
            f"{gui_interface_summary}"
        )
    if gui_interface_summary.get("listener_interface_declared") is not False:
        raise AssertionError(
            "Alhambra GUI source generator interface must not declare listener interface: "
            f"{gui_interface_summary}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if gui_interface_summary.get(count_key) != 0:
            raise AssertionError(
                "Alhambra GUI source generator interface "
                f"{count_key} changed: {gui_interface_summary}"
            )
        if alhambra_gui_source_generator_interface.get(count_key) != 0:
            raise AssertionError(
                "Alhambra GUI source generator interface report no-write count changed: "
                f"{alhambra_gui_source_generator_interface}"
            )
    if alhambra_gui_source_generator_interface.get("required_target_paths") != [gui_interface_target]:
        raise AssertionError(
            "Alhambra GUI source generator interface should expose only the GUI target: "
            f"{alhambra_gui_source_generator_interface.get('required_target_paths')}"
        )
    if alhambra_gui_source_generator_interface.get("output_is_loadable_source") is not False:
        raise AssertionError("Alhambra GUI source generator interface must not output loadable source")
    if (
        alhambra_gui_source_generator_interface.get("source_writer_allowed") is not False
        or alhambra_gui_source_generator_interface.get("may_write_src") is not False
        or alhambra_gui_source_generator_interface.get("writes_src") is not False
    ):
        raise AssertionError("Alhambra GUI source generator interface no-write flags changed")
    if alhambra_gui_source_generator_interface.get("listener_interface_declared") is not False:
        raise AssertionError("Alhambra GUI source generator interface must not declare listener interface")

    gui_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        gui_interface_target,
    )
    gui_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        gui_interface_target,
    )
    gui_generator_interfaces = alhambra_gui_source_generator_interface.get("source_generator_interfaces", [])
    if len(gui_generator_interfaces) != 1:
        raise AssertionError(
            "Alhambra GUI source generator interface should expose one interface: "
            f"{gui_generator_interfaces}"
        )
    gui_generator_interface = gui_generator_interfaces[0]
    if (
        gui_generator_interface.get("family") != "gui"
        or gui_generator_interface.get("target_path") != gui_interface_target
        or gui_generator_interface.get("owner_generator") != "unique_wonder_ritual_gui_row_source_generator"
        or gui_generator_interface.get("output_contract") != "source_file_contract_artifacts"
        or gui_generator_interface.get("dry_run_required") is not True
        or gui_generator_interface.get("memory_report_only") is not True
        or gui_generator_interface.get("gui_family_only") is not True
        or gui_generator_interface.get("gui_target_only") is not True
        or gui_generator_interface.get("listener_interface_declared") is not False
        or gui_generator_interface.get("source_writer_allowed") is not False
        or gui_generator_interface.get("may_write_src") is not False
        or gui_generator_interface.get("writes_src") is not False
        or gui_generator_interface.get("source_file_validation_evidence_ref")
        != gui_generator_contract.get("evidence_pack_ref")
    ):
        raise AssertionError(
            "Alhambra GUI source generator interface lost no-write interface shape: "
            f"{gui_generator_interface}"
        )

    gui_contract_artifacts = alhambra_gui_source_generator_interface.get("source_file_contract_artifacts", [])
    if len(gui_contract_artifacts) != 2:
        raise AssertionError(
            "Alhambra GUI source generator interface artifact list changed: "
            f"{gui_contract_artifacts}"
        )
    gui_contract_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for ref in gui_generator_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    gui_artifact_ref_keys = {
        (
            str(artifact.get("source_body_candidate_ref", {}).get("family", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("row_set_key", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("artifact_kind", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("future_source_target_path", "")),
        )
        for artifact in gui_contract_artifacts
        if isinstance(artifact, dict)
    }
    if (
        gui_artifact_ref_keys != gui_contract_ref_keys
        or len(gui_artifact_ref_keys) != expected_alhambra_file_counts[gui_interface_target]
    ):
        raise AssertionError(
            "Alhambra GUI source generator interface lost external source refs: "
            f"{gui_artifact_ref_keys}"
        )
    if {
        artifact.get("artifact_kind")
        for artifact in gui_contract_artifacts
    } != {"gui_checklist_row", "gui_incident_log_row"}:
        raise AssertionError(
            "Alhambra GUI source generator interface artifact kinds changed: "
            f"{gui_contract_artifacts}"
        )
    for artifact in gui_contract_artifacts:
        draft = artifact.get("gui_source_body_draft")
        if not isinstance(draft, dict) or draft.get("kind") != "gui_source_body_draft":
            raise AssertionError(
                "Alhambra GUI source generator interface artifact lost GUI source-body draft: "
                f"{artifact}"
            )
        if (
            draft.get("row_set_key") != artifact.get("row_set_key")
            or draft.get("artifact_kind") != artifact.get("artifact_kind")
            or draft.get("body_emitted") is not False
            or draft.get("may_write_src") is not False
            or draft.get("loc_key_refs", {}).get("all_bound") is not True
            or draft.get("trigger_effect_handoff_refs", {}).get("all_bound") is not True
            or draft.get("variable_read_refs", {}).get("all_bound") is not True
        ):
            raise AssertionError(
                "Alhambra GUI source-body draft lost row/loc/variable/handoff binding: "
                f"{draft}"
            )
        if (
            artifact.get("family") != "gui"
            or artifact.get("target_path") != gui_interface_target
            or artifact.get("future_source_target_path") != gui_interface_target
            or artifact.get("output_kind") != "source_file_contract_artifacts"
            or artifact.get("output_is_loadable_source") is not False
            or artifact.get("source_file_contract_artifact_only") is not True
            or artifact.get("source_generator_interface_prototype_only") is not True
            or artifact.get("gui_family_only") is not True
            or artifact.get("gui_target_only") is not True
            or artifact.get("listener_interface_declared") is not False
            or artifact.get("memory_report_only") is not True
            or artifact.get("dry_run") is not True
            or artifact.get("dry_run_required") is not True
            or artifact.get("source_file_validation_evidence_ref") != gui_generator_contract.get("evidence_pack_ref")
            or artifact.get("source_body_candidate_ref_provenance")
            != gui_generator_contract.get("source_body_candidate_ref_provenance")
            or artifact.get("no_write_source_writer_contract_evidence")
            != gui_generator_contract.get("no_write_source_writer_contract_evidence")
            or artifact.get("body_emitted") is not False
            or artifact.get("source_ready") is not False
            or artifact.get("verified") is not False
            or artifact.get("backend_ready") is not False
            or artifact.get("source_writer_allowed") is not False
            or artifact.get("may_write_src") is not False
            or artifact.get("writes_src") is not False
        ):
            raise AssertionError(
                "Alhambra GUI source generator interface artifact lost no-write contract shape: "
                f"{artifact}"
            )
    if gui_validation_pack.get("target_path") != gui_interface_target:
        raise AssertionError(f"Alhambra GUI validation pack target changed: {gui_validation_pack}")

    def assert_alhambra_gui_source_generator_interface_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_generator_contract: dict | None = alhambra_source_generator_contract,
        source_file_validation_evidence: dict | None = alhambra_source_file_validation_evidence,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_gui_source_generator_interface(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(
                f"{name} Alhambra GUI source generator interface negative was not caught: "
                f"{errors}"
            )

    missing_gui_artifact_interface = deepcopy(alhambra_gui_source_generator_interface)
    missing_gui_artifact_interface["source_file_contract_artifacts"] = (
        missing_gui_artifact_interface["source_file_contract_artifacts"][:-1]
    )
    assert_alhambra_gui_source_generator_interface_error(
        "missing GUI artifact",
        missing_gui_artifact_interface,
        "artifact_count mismatch",
    )

    writable_gui_artifact_interface = deepcopy(alhambra_gui_source_generator_interface)
    _alhambra_gui_source_file_contract_artifact(
        writable_gui_artifact_interface,
        "gui_checklist_row",
    )["may_write_src"] = True
    assert_alhambra_gui_source_generator_interface_error(
        "writable GUI artifact",
        writable_gui_artifact_interface,
        "may_write_src must be false",
    )

    listener_declared_gui_interface = deepcopy(alhambra_gui_source_generator_interface)
    listener_declared_gui_interface["listener_interface_declared"] = True
    assert_alhambra_gui_source_generator_interface_error(
        "listener-declaring GUI interface",
        listener_declared_gui_interface,
        "must not declare listener interface",
    )

    source_ready_gui_interface = deepcopy(alhambra_gui_source_generator_interface)
    _alhambra_gui_source_file_contract_artifact(
        source_ready_gui_interface,
        "gui_incident_log_row",
    )["source_ready"] = True
    assert_alhambra_gui_source_generator_interface_error(
        "source-ready GUI artifact",
        source_ready_gui_interface,
        "source_ready/verified/backend_ready",
    )

    wrong_output_gui_interface = deepcopy(alhambra_gui_source_generator_interface)
    wrong_output_gui_interface["output_kind"] = "loadable_source_file"
    assert_alhambra_gui_source_generator_interface_error(
        "wrong GUI output kind",
        wrong_output_gui_interface,
        "output_kind must be source_file_contract_artifacts",
    )

    forged_ref_gui_interface = deepcopy(alhambra_gui_source_generator_interface)
    _alhambra_gui_source_file_contract_artifact(
        forged_ref_gui_interface,
        "gui_checklist_row",
    )["source_body_candidate_ref"]["row_set_key"] = "forged_row_set"
    assert_alhambra_gui_source_generator_interface_error(
        "forged GUI source ref",
        forged_ref_gui_interface,
        "external validation evidence mismatch",
    )

    missing_gui_loc_key_interface = deepcopy(alhambra_gui_source_generator_interface)
    _alhambra_gui_source_file_contract_artifact(
        missing_gui_loc_key_interface,
        "gui_checklist_row",
    )["gui_source_body_draft"]["loc_key_refs"]["row_label_keys"] = []
    assert_alhambra_gui_source_generator_interface_error(
        "GUI draft missing loc key",
        missing_gui_loc_key_interface,
        "loc key refs must be bound",
    )

    body_emitted_gui_draft_interface = deepcopy(alhambra_gui_source_generator_interface)
    _alhambra_gui_source_file_contract_artifact(
        body_emitted_gui_draft_interface,
        "gui_incident_log_row",
    )["gui_source_body_draft"]["body_emitted"] = True
    assert_alhambra_gui_source_generator_interface_error(
        "GUI draft emitted body",
        body_emitted_gui_draft_interface,
        "body_emitted must be false",
    )

    external_evidence_forged_gui_validation = deepcopy(alhambra_source_file_validation_evidence)
    external_evidence_forged_gui_pack = _alhambra_source_file_validation_pack(
        external_evidence_forged_gui_validation,
        gui_interface_target,
    )
    external_evidence_forged_gui_pack["source_body_candidate_refs"][0]["row_set_key"] = "forged_row_set"
    external_evidence_forged_gui_generator_contract = (
        repeated_entity_row_alhambra_source_generator_contract_for_payload(
            spec_data,
            source_file_validation_evidence=external_evidence_forged_gui_validation,
        )
    )
    external_evidence_forged_gui_interface = (
        repeated_entity_row_alhambra_gui_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=external_evidence_forged_gui_generator_contract,
            source_file_validation_evidence=external_evidence_forged_gui_validation,
        )
    )
    if not any("row_set_key mismatch" in error for error in external_evidence_forged_gui_interface["validation_errors"]):
        raise AssertionError(
            "Externally forged Alhambra GUI interface must reject wrong row set before "
            "the original validation evidence is applied: "
            f"{external_evidence_forged_gui_interface['validation_errors']}"
        )
    assert_alhambra_gui_source_generator_interface_error(
        "external evidence-bound forged GUI interface",
        external_evidence_forged_gui_interface,
        "external validation evidence",
        source_generator_contract=external_evidence_forged_gui_generator_contract,
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )

    detached_gui_interface_validation = deepcopy(alhambra_gui_source_generator_interface)
    assert_alhambra_gui_source_generator_interface_error(
        "missing external validation evidence",
        detached_gui_interface_validation,
        "requires external source-file validation evidence",
        source_file_validation_evidence=None,
    )

    alhambra_listener_source_generator_interface = (
        repeated_entity_row_alhambra_listener_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if alhambra_listener_source_generator_interface["validation_errors"]:
        raise AssertionError(
            "Alhambra listener source generator interface unexpectedly failed validation: "
            f"{alhambra_listener_source_generator_interface['validation_errors']}"
        )
    evidence_bound_listener_interface_errors = (
        validate_repeated_entity_row_alhambra_listener_source_generator_interface(
            alhambra_listener_source_generator_interface,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if evidence_bound_listener_interface_errors:
        raise AssertionError(
            "Alhambra listener source generator interface unexpectedly failed external evidence-bound validation: "
            f"{evidence_bound_listener_interface_errors}"
        )
    listener_interface_target = alhambra_file_targets["listener"]
    listener_interface_summary = alhambra_listener_source_generator_interface.get("summary", {})
    if listener_interface_summary.get("interface_count") != 1:
        raise AssertionError(
            "Alhambra listener source generator interface count changed: "
            f"{listener_interface_summary}"
        )
    if listener_interface_summary.get("artifact_count") != expected_alhambra_file_counts[listener_interface_target]:
        raise AssertionError(
            "Alhambra listener source generator interface artifact count changed: "
            f"{listener_interface_summary}"
        )
    if listener_interface_summary.get("artifact_count") != 1:
        raise AssertionError(
            "Alhambra listener source generator interface must emit exactly 1 report-level artifact: "
            f"{listener_interface_summary}"
        )
    if listener_interface_summary.get("artifact_kind") != "listener_war_integration":
        raise AssertionError(
            "Alhambra listener source generator interface artifact kind changed: "
            f"{listener_interface_summary}"
        )
    if listener_interface_summary.get("output_kind") != "source_file_contract_artifacts":
        raise AssertionError(
            "Alhambra listener source generator interface output kind changed: "
            f"{listener_interface_summary}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if listener_interface_summary.get(count_key) != 0:
            raise AssertionError(
                "Alhambra listener source generator interface "
                f"{count_key} changed: {listener_interface_summary}"
            )
        if alhambra_listener_source_generator_interface.get(count_key) != 0:
            raise AssertionError(
                "Alhambra listener source generator interface report no-write count changed: "
                f"{alhambra_listener_source_generator_interface}"
            )
    if alhambra_listener_source_generator_interface.get("required_target_paths") != [listener_interface_target]:
        raise AssertionError(
            "Alhambra listener source generator interface should expose only the listener target: "
            f"{alhambra_listener_source_generator_interface.get('required_target_paths')}"
        )
    if alhambra_listener_source_generator_interface.get("output_is_loadable_source") is not False:
        raise AssertionError("Alhambra listener source generator interface must not output loadable source")
    if (
        alhambra_listener_source_generator_interface.get("source_writer_allowed") is not False
        or alhambra_listener_source_generator_interface.get("may_write_src") is not False
        or alhambra_listener_source_generator_interface.get("writes_src") is not False
    ):
        raise AssertionError("Alhambra listener source generator interface no-write flags changed")

    listener_generator_contract = _alhambra_source_generator_contract(
        alhambra_source_generator_contract,
        listener_interface_target,
    )
    listener_validation_pack = _alhambra_source_file_validation_pack(
        alhambra_source_file_validation_evidence,
        listener_interface_target,
    )
    listener_linkage_evidence = listener_validation_pack.get("listener_linkage_evidence", {})
    listener_generator_interfaces = alhambra_listener_source_generator_interface.get("source_generator_interfaces", [])
    if len(listener_generator_interfaces) != 1:
        raise AssertionError(
            "Alhambra listener source generator interface should expose one interface: "
            f"{listener_generator_interfaces}"
        )
    listener_generator_interface = listener_generator_interfaces[0]
    if (
        listener_generator_interface.get("family") != "listener"
        or listener_generator_interface.get("target_path") != listener_interface_target
        or listener_generator_interface.get("owner_generator")
        != "unique_wonder_ritual_listener_integration_source_generator"
        or listener_generator_interface.get("output_contract") != "source_file_contract_artifacts"
        or listener_generator_interface.get("dry_run_required") is not True
        or listener_generator_interface.get("memory_report_only") is not True
        or listener_generator_interface.get("listener_family_only") is not True
        or listener_generator_interface.get("listener_target_only") is not True
        or listener_generator_interface.get("source_writer_allowed") is not False
        or listener_generator_interface.get("may_write_src") is not False
        or listener_generator_interface.get("writes_src") is not False
        or listener_generator_interface.get("source_file_validation_evidence_ref")
        != listener_generator_contract.get("evidence_pack_ref")
        or listener_generator_interface.get("listener_linkage_evidence_ref") != listener_linkage_evidence
        or set(listener_generator_interface.get("on_action_hook_linkage_plan", {}).get("hooks", []))
        != {"on_pre_winning_war", "on_ending_war"}
        or listener_generator_interface.get("selected_ritual_trigger_linkage", {}).get("trigger_name")
        != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
        or set(
            listener_generator_interface.get("war_scope_availability_persistence_plan", {}).get(
                "war_scope_available_from_hooks",
                [],
            )
        )
        != {"on_pre_winning_war", "on_ending_war"}
    ):
        raise AssertionError(
            "Alhambra listener source generator interface lost no-write linkage shape: "
            f"{listener_generator_interface}"
        )

    listener_contract_artifacts = alhambra_listener_source_generator_interface.get("source_file_contract_artifacts", [])
    if len(listener_contract_artifacts) != 1:
        raise AssertionError(
            "Alhambra listener source generator interface artifact list changed: "
            f"{listener_contract_artifacts}"
        )
    listener_contract_ref_keys = {
        (
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(ref.get("future_source_target_path", "")),
        )
        for ref in listener_generator_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    }
    listener_artifact_ref_keys = {
        (
            str(artifact.get("source_body_candidate_ref", {}).get("family", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("row_set_key", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("artifact_kind", "")),
            str(artifact.get("source_body_candidate_ref", {}).get("future_source_target_path", "")),
        )
        for artifact in listener_contract_artifacts
        if isinstance(artifact, dict)
    }
    if listener_artifact_ref_keys != listener_contract_ref_keys or len(listener_artifact_ref_keys) != 1:
        raise AssertionError(
            "Alhambra listener source generator interface lost external source refs: "
            f"{listener_artifact_ref_keys}"
        )
    listener_artifact = listener_contract_artifacts[0]
    if (
        listener_artifact.get("family") != "listener"
        or listener_artifact.get("artifact_kind") != "listener_war_integration"
        or listener_artifact.get("target_path") != listener_interface_target
        or listener_artifact.get("future_source_target_path") != listener_interface_target
        or listener_artifact.get("output_kind") != "source_file_contract_artifacts"
        or listener_artifact.get("output_is_loadable_source") is not False
        or listener_artifact.get("source_file_contract_artifact_only") is not True
        or listener_artifact.get("source_generator_interface_prototype_only") is not True
        or listener_artifact.get("listener_family_only") is not True
        or listener_artifact.get("listener_target_only") is not True
        or listener_artifact.get("memory_report_only") is not True
        or listener_artifact.get("dry_run") is not True
        or listener_artifact.get("dry_run_required") is not True
        or listener_artifact.get("source_file_validation_evidence_ref")
        != listener_generator_contract.get("evidence_pack_ref")
        or listener_artifact.get("source_body_candidate_ref_provenance")
        != listener_generator_contract.get("source_body_candidate_ref_provenance")
        or listener_artifact.get("no_write_source_writer_contract_evidence")
        != listener_generator_contract.get("no_write_source_writer_contract_evidence")
        or listener_artifact.get("listener_linkage_evidence_ref") != listener_linkage_evidence
        or set(listener_artifact.get("on_action_hook_linkage_plan", {}).get("hooks", []))
        != {"on_pre_winning_war", "on_ending_war"}
        or listener_artifact.get("selected_ritual_trigger_linkage", {}).get("trigger_name")
        != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
        or listener_artifact.get("war_scope_availability_persistence_plan", {}).get("persistence_contract_only")
        is not True
        or listener_artifact.get("body_emitted") is not False
        or listener_artifact.get("source_ready") is not False
        or listener_artifact.get("verified") is not False
        or listener_artifact.get("backend_ready") is not False
        or listener_artifact.get("source_writer_allowed") is not False
        or listener_artifact.get("may_write_src") is not False
        or listener_artifact.get("writes_src") is not False
        or listener_artifact.get("listener_body_allowed") is not False
        or listener_artifact.get("listener_scope_writes_allowed") is not False
        or listener_artifact.get("war_scope_writes_allowed") is not False
        or listener_artifact.get("source_writes_allowed") is not False
    ):
        raise AssertionError(
            "Alhambra listener source generator interface artifact lost no-write linkage shape: "
            f"{listener_artifact}"
        )
    listener_draft = listener_artifact.get("listener_source_body_draft")
    if not isinstance(listener_draft, dict) or listener_draft.get("kind") != "listener_source_body_draft":
        raise AssertionError(
            "Alhambra listener source generator interface artifact lost listener source-body draft: "
            f"{listener_artifact}"
        )
    if (
        listener_draft.get("artifact_kind") != "listener_war_integration"
        or listener_draft.get("target_path") != listener_interface_target
        or listener_draft.get("future_source_target_path") != listener_interface_target
        or listener_draft.get("body_emitted") is not False
        or listener_draft.get("may_write_src") is not False
        or listener_draft.get("listener_body_allowed") is not False
        or listener_draft.get("listener_scope_writes_allowed") is not False
        or listener_draft.get("war_scope_writes_allowed") is not False
        or set(listener_draft.get("on_action_hook_linkage_plan", {}).get("hooks", []))
        != {"on_pre_winning_war", "on_ending_war"}
        or listener_draft.get("war_scope_contract", {}).get("persistence_contract_only") is not True
        or set(listener_draft.get("war_scope_contract", {}).get("war_scope_available_from_hooks", []))
        != {"on_pre_winning_war", "on_ending_war"}
        or listener_draft.get("selected_ritual_trigger_refs", {}).get("trigger_name")
        != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
        or listener_draft.get("selected_ritual_trigger_refs", {}).get("all_bound") is not True
        or listener_draft.get("event_effect_cleanup_handoff_refs", {}).get("all_bound") is not True
    ):
        raise AssertionError(
            "Alhambra listener source-body draft lost hook/war-scope/trigger/handoff binding: "
            f"{listener_draft}"
        )
    for ref_label in ("event", "trigger", "effect", "cleanup"):
        refs = listener_draft.get("event_effect_cleanup_handoff_refs", {}).get(f"{ref_label}_refs")
        if not isinstance(refs, list) or not refs:
            raise AssertionError(
                "Alhambra listener source-body draft lost "
                f"{ref_label} handoff refs: {listener_draft}"
            )
    if listener_validation_pack.get("target_path") != listener_interface_target:
        raise AssertionError(f"Alhambra listener validation pack target changed: {listener_validation_pack}")

    def assert_alhambra_listener_source_generator_interface_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_generator_contract: dict | None = alhambra_source_generator_contract,
        source_file_validation_evidence: dict | None = alhambra_source_file_validation_evidence,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_listener_source_generator_interface(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(
                f"{name} Alhambra listener source generator interface negative was not caught: "
                f"{errors}"
            )

    missing_listener_artifact_interface = deepcopy(alhambra_listener_source_generator_interface)
    missing_listener_artifact_interface["source_file_contract_artifacts"] = []
    assert_alhambra_listener_source_generator_interface_error(
        "missing listener artifact",
        missing_listener_artifact_interface,
        "artifact_count mismatch",
    )

    writable_listener_artifact_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        writable_listener_artifact_interface,
        "listener_war_integration",
    )["may_write_src"] = True
    assert_alhambra_listener_source_generator_interface_error(
        "writable listener artifact",
        writable_listener_artifact_interface,
        "may_write_src must be false",
    )

    missing_listener_hook_interface = deepcopy(alhambra_listener_source_generator_interface)
    del _alhambra_listener_source_file_contract_artifact(
        missing_listener_hook_interface,
        "listener_war_integration",
    )["listener_linkage_evidence_ref"]["on_action_hook_linkage_plan"]
    assert_alhambra_listener_source_generator_interface_error(
        "missing listener hook evidence",
        missing_listener_hook_interface,
        "hook linkage",
    )

    missing_listener_trigger_interface = deepcopy(alhambra_listener_source_generator_interface)
    del _alhambra_listener_source_file_contract_artifact(
        missing_listener_trigger_interface,
        "listener_war_integration",
    )["listener_linkage_evidence_ref"]["selected_ritual_trigger_linkage"]
    assert_alhambra_listener_source_generator_interface_error(
        "missing listener trigger evidence",
        missing_listener_trigger_interface,
        "selected ritual trigger linkage",
    )

    missing_listener_war_scope_interface = deepcopy(alhambra_listener_source_generator_interface)
    del _alhambra_listener_source_file_contract_artifact(
        missing_listener_war_scope_interface,
        "listener_war_integration",
    )["listener_linkage_evidence_ref"]["war_scope_availability_persistence_plan"]
    assert_alhambra_listener_source_generator_interface_error(
        "missing listener war-scope evidence",
        missing_listener_war_scope_interface,
        "war-scope boundary",
    )

    missing_listener_draft_interface = deepcopy(alhambra_listener_source_generator_interface)
    del _alhambra_listener_source_file_contract_artifact(
        missing_listener_draft_interface,
        "listener_war_integration",
    )["listener_source_body_draft"]
    assert_alhambra_listener_source_generator_interface_error(
        "missing listener source-body draft",
        missing_listener_draft_interface,
        "missing listener source-body draft",
    )

    missing_listener_draft_hook_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        missing_listener_draft_hook_interface,
        "listener_war_integration",
    )["listener_source_body_draft"]["on_action_hook_linkage_plan"]["hooks"] = ["on_pre_winning_war"]
    assert_alhambra_listener_source_generator_interface_error(
        "missing listener draft hook",
        missing_listener_draft_hook_interface,
        "hook linkage",
    )

    wrong_listener_draft_war_scope_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        wrong_listener_draft_war_scope_interface,
        "listener_war_integration",
    )["listener_source_body_draft"]["war_scope_contract"]["war_scope_writes_allowed"] = True
    assert_alhambra_listener_source_generator_interface_error(
        "wrong listener draft war scope",
        wrong_listener_draft_war_scope_interface,
        "war scope contract mismatch",
    )

    unbound_listener_draft_effect_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        unbound_listener_draft_effect_interface,
        "listener_war_integration",
    )["listener_source_body_draft"]["event_effect_cleanup_handoff_refs"]["effect_refs"] = []
    assert_alhambra_listener_source_generator_interface_error(
        "unbound listener draft effect refs",
        unbound_listener_draft_effect_interface,
        "effect refs must not be empty",
    )

    wrong_listener_draft_target_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        wrong_listener_draft_target_interface,
        "listener_war_integration",
    )["listener_source_body_draft"]["target_path"] = "src/in_game/common/on_action/forged.txt"
    assert_alhambra_listener_source_generator_interface_error(
        "wrong listener draft target",
        wrong_listener_draft_target_interface,
        "target path mismatch",
    )

    body_emitted_listener_draft_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        body_emitted_listener_draft_interface,
        "listener_war_integration",
    )["listener_source_body_draft"]["body_emitted"] = True
    assert_alhambra_listener_source_generator_interface_error(
        "body-emitted listener draft",
        body_emitted_listener_draft_interface,
        "body_emitted must be false",
    )

    may_write_listener_draft_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        may_write_listener_draft_interface,
        "listener_war_integration",
    )["listener_source_body_draft"]["may_write_src"] = True
    assert_alhambra_listener_source_generator_interface_error(
        "writable listener draft",
        may_write_listener_draft_interface,
        "may_write_src must be false",
    )

    forged_ref_listener_interface = deepcopy(alhambra_listener_source_generator_interface)
    _alhambra_listener_source_file_contract_artifact(
        forged_ref_listener_interface,
        "listener_war_integration",
    )["source_body_candidate_ref"]["row_set_key"] = "forged_row_set"
    assert_alhambra_listener_source_generator_interface_error(
        "forged listener source ref",
        forged_ref_listener_interface,
        "external validation evidence mismatch",
    )

    external_evidence_forged_listener_validation = deepcopy(alhambra_source_file_validation_evidence)
    external_evidence_forged_listener_pack = _alhambra_source_file_validation_pack(
        external_evidence_forged_listener_validation,
        listener_interface_target,
    )
    external_evidence_forged_listener_pack["source_body_candidate_refs"][0]["row_set_key"] = "forged_row_set"
    external_evidence_forged_listener_generator_contract = (
        repeated_entity_row_alhambra_source_generator_contract_for_payload(
            spec_data,
            source_file_validation_evidence=external_evidence_forged_listener_validation,
        )
    )
    external_evidence_forged_listener_interface = (
        repeated_entity_row_alhambra_listener_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=external_evidence_forged_listener_generator_contract,
            source_file_validation_evidence=external_evidence_forged_listener_validation,
        )
    )
    if not any(
        "listener source-body draft" in error
        or "refs must not be empty" in error
        or "source-body draft completeness" in error
        for error in external_evidence_forged_listener_interface["validation_errors"]
    ):
        raise AssertionError(
            "Externally forged Alhambra listener interface should fail its own source-body "
            "draft binding before the original validation evidence is applied: "
            f"{external_evidence_forged_listener_interface['validation_errors']}"
        )
    assert_alhambra_listener_source_generator_interface_error(
        "external evidence-bound forged listener interface",
        external_evidence_forged_listener_interface,
        "external validation evidence",
        source_generator_contract=external_evidence_forged_listener_generator_contract,
        source_file_validation_evidence=alhambra_source_file_validation_evidence,
    )

    detached_listener_interface_validation = deepcopy(alhambra_listener_source_generator_interface)
    assert_alhambra_listener_source_generator_interface_error(
        "missing external validation evidence",
        detached_listener_interface_validation,
        "requires external source-file validation evidence",
        source_file_validation_evidence=None,
    )

    alhambra_localization_source_generator_interface = (
        repeated_entity_row_alhambra_localization_source_generator_interface_for_payload(
            spec_data,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if alhambra_localization_source_generator_interface["validation_errors"]:
        raise AssertionError(
            "Alhambra localization source generator interface unexpectedly failed validation: "
            f"{alhambra_localization_source_generator_interface['validation_errors']}"
        )
    evidence_bound_localization_interface_errors = (
        validate_repeated_entity_row_alhambra_localization_source_generator_interface(
            alhambra_localization_source_generator_interface,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if evidence_bound_localization_interface_errors:
        raise AssertionError(
            "Alhambra localization source generator interface unexpectedly failed external evidence-bound "
            f"validation: {evidence_bound_localization_interface_errors}"
        )
    localization_interface_targets = [
        alhambra_file_targets["english"],
        alhambra_file_targets["simp_chinese"],
    ]
    localization_interface_summary = alhambra_localization_source_generator_interface.get("summary", {})
    if localization_interface_summary.get("interface_count") != 2:
        raise AssertionError(
            "Alhambra localization source generator interface count changed: "
            f"{localization_interface_summary}"
        )
    if localization_interface_summary.get("artifact_count") != 20:
        raise AssertionError(
            "Alhambra localization source generator interface artifact count changed: "
            f"{localization_interface_summary}"
        )
    if localization_interface_summary.get("target_artifact_counts") != {
        alhambra_file_targets["english"]: 10,
        alhambra_file_targets["simp_chinese"]: 10,
    }:
        raise AssertionError(
            "Alhambra localization source generator interface target split changed: "
            f"{localization_interface_summary}"
        )
    if localization_interface_summary.get("language_artifact_counts") != {
        "english": 10,
        "simp_chinese": 10,
    }:
        raise AssertionError(
            "Alhambra localization source generator interface language split changed: "
            f"{localization_interface_summary}"
        )
    if localization_interface_summary.get("output_kind") != "source_file_contract_artifacts":
        raise AssertionError(
            "Alhambra localization source generator interface output kind changed: "
            f"{localization_interface_summary}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if localization_interface_summary.get(count_key) != 0:
            raise AssertionError(
                "Alhambra localization source generator interface "
                f"{count_key} changed: {localization_interface_summary}"
            )
        if alhambra_localization_source_generator_interface.get(count_key) != 0:
            raise AssertionError(
                "Alhambra localization source generator interface report no-write count changed: "
                f"{alhambra_localization_source_generator_interface}"
            )
    if alhambra_localization_source_generator_interface.get("required_target_paths") != localization_interface_targets:
        raise AssertionError(
            "Alhambra localization source generator interface should expose only the two localization targets: "
            f"{alhambra_localization_source_generator_interface.get('required_target_paths')}"
        )
    if alhambra_localization_source_generator_interface.get("output_is_loadable_source") is not False:
        raise AssertionError("Alhambra localization source generator interface must not output loadable source")
    if (
        alhambra_localization_source_generator_interface.get("source_writer_allowed") is not False
        or alhambra_localization_source_generator_interface.get("may_write_src") is not False
        or alhambra_localization_source_generator_interface.get("writes_src") is not False
    ):
        raise AssertionError("Alhambra localization source generator interface no-write flags changed")

    localization_generator_interfaces = (
        alhambra_localization_source_generator_interface.get("source_generator_interfaces", [])
    )
    if len(localization_generator_interfaces) != 2:
        raise AssertionError(
            "Alhambra localization source generator interface should expose one interface per target: "
            f"{localization_generator_interfaces}"
        )
    expected_localization_languages = {
        alhambra_file_targets["english"]: "english",
        alhambra_file_targets["simp_chinese"]: "simp_chinese",
    }
    for localization_interface in localization_generator_interfaces:
        target_path = localization_interface.get("target_path")
        localization_generator_contract = _alhambra_source_generator_contract(
            alhambra_source_generator_contract,
            target_path,
        )
        if (
            localization_interface.get("family") != "localization"
            or localization_interface.get("localization_language") != expected_localization_languages[target_path]
            or localization_interface.get("owner_generator")
            != "unique_wonder_ritual_localization_source_generator"
            or localization_interface.get("output_contract") != "source_file_contract_artifacts"
            or localization_interface.get("dry_run_required") is not True
            or localization_interface.get("memory_report_only") is not True
            or localization_interface.get("localization_family_only") is not True
            or localization_interface.get("source_writer_allowed") is not False
            or localization_interface.get("may_write_src") is not False
            or localization_interface.get("writes_src") is not False
            or localization_interface.get("source_file_validation_evidence_ref")
            != localization_generator_contract.get("evidence_pack_ref")
            or localization_interface.get("localization_language_boundary", {}).get("language_target_paths")
            != {
                "english": alhambra_file_targets["english"],
                "simp_chinese": alhambra_file_targets["simp_chinese"],
            }
        ):
            raise AssertionError(
                "Alhambra localization source generator interface lost no-write interface shape: "
                f"{localization_interface}"
            )

    localization_contract_artifacts = (
        alhambra_localization_source_generator_interface.get("source_file_contract_artifacts", [])
    )
    if len(localization_contract_artifacts) != 20:
        raise AssertionError(
            "Alhambra localization source generator interface artifact list changed: "
            f"{localization_contract_artifacts}"
        )
    for target_path in localization_interface_targets:
        localization_generator_contract = _alhambra_source_generator_contract(
            alhambra_source_generator_contract,
            target_path,
        )
        localization_validation_pack = _alhambra_source_file_validation_pack(
            alhambra_source_file_validation_evidence,
            target_path,
        )
        target_artifacts = [
            artifact
            for artifact in localization_contract_artifacts
            if artifact.get("target_path") == target_path
        ]
        if len(target_artifacts) != expected_alhambra_file_counts[target_path]:
            raise AssertionError(
                "Alhambra localization source generator interface target artifact list changed: "
                f"{target_path}: {target_artifacts}"
            )
        localization_contract_ref_keys = {
            (
                str(ref.get("family", "")),
                str(ref.get("row_set_key", "")),
                str(ref.get("artifact_kind", "")),
                str(ref.get("future_source_target_path", "")),
            )
            for ref in localization_generator_contract.get("source_body_candidate_refs", []) or []
            if isinstance(ref, dict)
        }
        localization_artifact_ref_keys = {
            (
                str(artifact.get("source_body_candidate_ref", {}).get("family", "")),
                str(artifact.get("source_body_candidate_ref", {}).get("row_set_key", "")),
                str(artifact.get("source_body_candidate_ref", {}).get("artifact_kind", "")),
                str(artifact.get("source_body_candidate_ref", {}).get("future_source_target_path", "")),
            )
            for artifact in target_artifacts
            if isinstance(artifact, dict)
        }
        if (
            localization_artifact_ref_keys != localization_contract_ref_keys
            or len(localization_artifact_ref_keys) != expected_alhambra_file_counts[target_path]
        ):
            raise AssertionError(
                "Alhambra localization source generator interface lost external source refs: "
                f"{target_path}: {localization_artifact_ref_keys}"
            )
        for artifact in target_artifacts:
            draft = artifact.get("localization_source_body_draft")
            if not isinstance(draft, dict) or draft.get("kind") != "localization_source_body_draft":
                raise AssertionError(
                    "Alhambra localization source generator interface artifact lost localization "
                    f"source-body draft: {artifact}"
                )
            if (
                draft.get("localization_language") != expected_localization_languages[target_path]
                or draft.get("target_path") != target_path
                or draft.get("row_set_key") != artifact.get("row_set_key")
                or draft.get("artifact_kind") != artifact.get("artifact_kind")
                or draft.get("body_emitted") is not False
                or draft.get("may_write_src") is not False
                or draft.get("language_target", {}).get("separate_language_target") is not True
                or draft.get("localization_key_refs", {}).get("all_bound") is not True
                or draft.get("reverse_binding_refs", {}).get("all_bound") is not True
            ):
                raise AssertionError(
                    "Alhambra localization source-body draft lost language/key/reverse binding: "
                    f"{draft}"
                )
            if (
                artifact.get("family") != "localization"
                or artifact.get("localization_language") != expected_localization_languages[target_path]
                or artifact.get("target_path") != target_path
                or artifact.get("future_source_target_path") != target_path
                or artifact.get("source_candidate_future_target_path")
                != artifact.get("source_body_candidate_ref", {}).get("future_source_target_path")
                or artifact.get("output_kind") != "source_file_contract_artifacts"
                or artifact.get("output_is_loadable_source") is not False
                or artifact.get("source_file_contract_artifact_only") is not True
                or artifact.get("source_generator_interface_prototype_only") is not True
                or artifact.get("localization_family_only") is not True
                or artifact.get("memory_report_only") is not True
                or artifact.get("dry_run") is not True
                or artifact.get("dry_run_required") is not True
                or artifact.get("source_file_validation_evidence_ref")
                != localization_generator_contract.get("evidence_pack_ref")
                or artifact.get("source_body_candidate_ref_provenance")
                != localization_generator_contract.get("source_body_candidate_ref_provenance")
                or artifact.get("no_write_source_writer_contract_evidence")
                != localization_generator_contract.get("no_write_source_writer_contract_evidence")
                or artifact.get("localization_language_boundary")
                != localization_generator_contract.get("localization_language_boundary")
                or artifact.get("body_emitted") is not False
                or artifact.get("source_ready") is not False
                or artifact.get("verified") is not False
                or artifact.get("backend_ready") is not False
                or artifact.get("source_writer_allowed") is not False
                or artifact.get("may_write_src") is not False
                or artifact.get("writes_src") is not False
            ):
                raise AssertionError(
                    "Alhambra localization source generator interface artifact lost no-write contract shape: "
                    f"{artifact}"
                )
        if localization_validation_pack.get("target_path") != target_path:
            raise AssertionError(f"Alhambra localization validation pack target changed: {localization_validation_pack}")

    def assert_alhambra_localization_source_generator_interface_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_generator_contract: dict | None = alhambra_source_generator_contract,
        source_file_validation_evidence: dict | None = alhambra_source_file_validation_evidence,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_localization_source_generator_interface(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(
                f"{name} Alhambra localization source generator interface negative was not caught: "
                f"{errors}"
            )

    missing_english_localization_artifact_interface = deepcopy(alhambra_localization_source_generator_interface)
    missing_english_localization_artifact_interface["source_file_contract_artifacts"] = [
        artifact
        for artifact in missing_english_localization_artifact_interface["source_file_contract_artifacts"]
        if not (
            artifact.get("target_path") == alhambra_file_targets["english"]
            and artifact.get("artifact_kind") == "localization_row_labels"
        )
    ]
    assert_alhambra_localization_source_generator_interface_error(
        "missing English localization artifact",
        missing_english_localization_artifact_interface,
        "report-only artifacts per target",
    )

    writable_localization_artifact_interface = deepcopy(alhambra_localization_source_generator_interface)
    _alhambra_localization_source_file_contract_artifact(
        writable_localization_artifact_interface,
        alhambra_file_targets["simp_chinese"],
        "localization_status_text",
    )["may_write_src"] = True
    assert_alhambra_localization_source_generator_interface_error(
        "writable localization artifact",
        writable_localization_artifact_interface,
        "may_write_src must be false",
    )

    wrong_output_localization_interface = deepcopy(alhambra_localization_source_generator_interface)
    wrong_output_localization_interface["output_kind"] = "loadable_source_file"
    assert_alhambra_localization_source_generator_interface_error(
        "wrong localization output kind",
        wrong_output_localization_interface,
        "output_kind must be source_file_contract_artifacts",
    )

    collapsed_localization_interface = deepcopy(alhambra_localization_source_generator_interface)
    collapsed_localization_interface["localization_target_paths"]["simp_chinese"] = alhambra_file_targets["english"]
    assert_alhambra_localization_source_generator_interface_error(
        "merged localization interface boundary",
        collapsed_localization_interface,
        "target paths must stay split",
    )

    forged_ref_localization_interface = deepcopy(alhambra_localization_source_generator_interface)
    _alhambra_localization_source_file_contract_artifact(
        forged_ref_localization_interface,
        alhambra_file_targets["english"],
        "localization_tooltips",
    )["source_body_candidate_ref"]["row_set_key"] = "forged_row_set"
    assert_alhambra_localization_source_generator_interface_error(
        "forged localization source ref",
        forged_ref_localization_interface,
        "external validation evidence mismatch",
    )

    missing_localization_key_interface = deepcopy(alhambra_localization_source_generator_interface)
    _alhambra_localization_source_file_contract_artifact(
        missing_localization_key_interface,
        alhambra_file_targets["english"],
        "localization_row_labels",
    )["localization_source_body_draft"]["localization_key_refs"]["keys"] = []
    assert_alhambra_localization_source_generator_interface_error(
        "localization draft missing loc key",
        missing_localization_key_interface,
        "missing loc key",
    )

    body_emitted_localization_draft_interface = deepcopy(alhambra_localization_source_generator_interface)
    _alhambra_localization_source_file_contract_artifact(
        body_emitted_localization_draft_interface,
        alhambra_file_targets["simp_chinese"],
        "localization_summary_text",
    )["localization_source_body_draft"]["body_emitted"] = True
    assert_alhambra_localization_source_generator_interface_error(
        "localization draft emitted body",
        body_emitted_localization_draft_interface,
        "body_emitted must be false",
    )

    merged_language_draft_interface = deepcopy(alhambra_localization_source_generator_interface)
    merged_language_draft = _alhambra_localization_source_file_contract_artifact(
        merged_language_draft_interface,
        alhambra_file_targets["simp_chinese"],
        "localization_tooltips",
    )["localization_source_body_draft"]
    merged_language_draft["language_target"]["language_targets_merged"] = True
    merged_language_draft["language_target"]["target_path"] = alhambra_file_targets["english"]
    assert_alhambra_localization_source_generator_interface_error(
        "localization draft merged language target",
        merged_language_draft_interface,
        "language target must stay split",
    )

    external_evidence_forged_localization_validation = deepcopy(alhambra_source_file_validation_evidence)
    external_evidence_forged_localization_pack = _alhambra_source_file_validation_pack(
        external_evidence_forged_localization_validation,
        alhambra_file_targets["english"],
    )
    external_evidence_forged_localization_pack["source_body_candidate_refs"][0]["row_set_key"] = "forged_row_set"
    assert_alhambra_localization_source_generator_interface_error(
        "external evidence-bound forged localization interface",
        alhambra_localization_source_generator_interface,
        "external validation evidence",
        source_file_validation_evidence=external_evidence_forged_localization_validation,
    )

    detached_localization_interface_validation = deepcopy(alhambra_localization_source_generator_interface)
    assert_alhambra_localization_source_generator_interface_error(
        "missing external validation evidence",
        detached_localization_interface_validation,
        "requires external source-file validation evidence",
        source_file_validation_evidence=None,
    )

    alhambra_source_generator_interface_bundle_gate = (
        repeated_entity_row_alhambra_source_generator_interface_bundle_gate_for_payload(
            spec_data,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
            event_source_generator_interface=alhambra_event_source_generator_interface,
            scripted_effect_cleanup_source_generator_interface=(
                alhambra_scripted_effect_cleanup_source_generator_interface
            ),
            scripted_trigger_source_generator_interface=alhambra_scripted_trigger_source_generator_interface,
            gui_source_generator_interface=alhambra_gui_source_generator_interface,
            listener_source_generator_interface=alhambra_listener_source_generator_interface,
            localization_source_generator_interface=alhambra_localization_source_generator_interface,
        )
    )
    if alhambra_source_generator_interface_bundle_gate["validation_errors"]:
        raise AssertionError(
            "Alhambra source generator interface bundle gate unexpectedly failed validation: "
            f"{alhambra_source_generator_interface_bundle_gate['validation_errors']}"
        )
    evidence_bound_bundle_errors = (
        validate_repeated_entity_row_alhambra_source_generator_interface_bundle_gate(
            alhambra_source_generator_interface_bundle_gate,
            source_generator_contract=alhambra_source_generator_contract,
            source_file_validation_evidence=alhambra_source_file_validation_evidence,
        )
    )
    if evidence_bound_bundle_errors:
        raise AssertionError(
            "Alhambra source generator interface bundle gate unexpectedly failed external evidence-bound validation: "
            f"{evidence_bound_bundle_errors}"
        )
    bundle_gate_summary = alhambra_source_generator_interface_bundle_gate.get("summary", {})
    if bundle_gate_summary.get("interface_group_count") != 6:
        raise AssertionError(f"Alhambra bundle interface group count changed: {bundle_gate_summary}")
    if bundle_gate_summary.get("target_file_count") != 7:
        raise AssertionError(f"Alhambra bundle target file count changed: {bundle_gate_summary}")
    if bundle_gate_summary.get("artifact_count") != 55:
        raise AssertionError(f"Alhambra bundle artifact count changed: {bundle_gate_summary}")
    if bundle_gate_summary.get("report_only_artifact_count") != 55:
        raise AssertionError(f"Alhambra bundle report-only artifact count changed: {bundle_gate_summary}")
    if bundle_gate_summary.get("interface_group_artifact_counts") != {
        "event": 8,
        "scripted_effect_cleanup": 18,
        "trigger": 6,
        "gui": 2,
        "listener": 1,
        "localization": 20,
    }:
        raise AssertionError(f"Alhambra bundle interface group counts changed: {bundle_gate_summary}")
    if bundle_gate_summary.get("source_body_draft_artifact_counts") != {
        "event": 8,
        "scripted_effect_cleanup": 18,
        "trigger": 6,
        "gui": 2,
        "listener": 1,
        "localization": 20,
    }:
        raise AssertionError(f"Alhambra bundle source-body draft counts changed: {bundle_gate_summary}")
    source_body_draft_gate = bundle_gate_summary.get("source_body_draft_completeness_gate", {})
    if (
        source_body_draft_gate.get("all_source_body_draft_groups_complete") is not True
        or source_body_draft_gate.get("source_body_draft_count") != 55
        or source_body_draft_gate.get("missing_source_body_draft_groups") != []
    ):
        raise AssertionError(f"Alhambra bundle source-body draft completeness changed: {bundle_gate_summary}")
    if bundle_gate_summary.get("target_artifact_counts") != {
        alhambra_file_targets["event"]: 8,
        alhambra_file_targets["effect_cleanup"]: 18,
        alhambra_file_targets["trigger"]: 6,
        alhambra_file_targets["gui"]: 2,
        alhambra_file_targets["listener"]: 1,
        alhambra_file_targets["english"]: 10,
        alhambra_file_targets["simp_chinese"]: 10,
    }:
        raise AssertionError(f"Alhambra bundle target artifact counts changed: {bundle_gate_summary}")
    if (
        bundle_gate_summary.get("source_ready_count") != 0
        or bundle_gate_summary.get("source_writer_allowed_count") != 0
        or bundle_gate_summary.get("may_write_src_count") != 0
        or bundle_gate_summary.get("writes_src_count") != 0
    ):
        raise AssertionError(f"Alhambra bundle no-write/readiness counts changed: {bundle_gate_summary}")
    if (
        alhambra_source_generator_interface_bundle_gate.get("output_is_loadable_source") is not False
        or alhambra_source_generator_interface_bundle_gate.get("body_emitted") is not False
        or alhambra_source_generator_interface_bundle_gate.get("source_writer_allowed") is not False
        or alhambra_source_generator_interface_bundle_gate.get("may_write_src") is not False
        or alhambra_source_generator_interface_bundle_gate.get("writes_src") is not False
    ):
        raise AssertionError(
            "Alhambra bundle gate must remain report-only/no-write: "
            f"{alhambra_source_generator_interface_bundle_gate}"
        )

    def assert_alhambra_bundle_gate_error(
        name: str,
        report: dict,
        needle: str,
        *,
        source_generator_contract: dict | None = alhambra_source_generator_contract,
        source_file_validation_evidence: dict | None = alhambra_source_file_validation_evidence,
    ) -> None:
        errors = validate_repeated_entity_row_alhambra_source_generator_interface_bundle_gate(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if not any(needle in error for error in errors):
            raise AssertionError(f"{name} Alhambra bundle gate negative was not caught: {errors}")

    missing_group_bundle = deepcopy(alhambra_source_generator_interface_bundle_gate)
    del missing_group_bundle["interface_reports"]["gui"]
    assert_alhambra_bundle_gate_error(
        "missing interface group",
        missing_group_bundle,
        "missing interface group",
    )

    duplicate_missing_target_bundle = deepcopy(alhambra_source_generator_interface_bundle_gate)
    duplicate_missing_target_artifact = duplicate_missing_target_bundle["interface_reports"]["trigger"][
        "source_file_contract_artifacts"
    ][0]
    duplicate_missing_target_artifact["target_path"] = alhambra_file_targets["event"]
    duplicate_missing_target_artifact["future_source_target_path"] = alhambra_file_targets["event"]
    assert_alhambra_bundle_gate_error(
        "duplicate and missing target",
        duplicate_missing_target_bundle,
        "target artifact counts mismatch",
    )

    wrong_bundle_artifact_count = deepcopy(alhambra_source_generator_interface_bundle_gate)
    wrong_bundle_artifact_count["interface_reports"]["event"]["source_file_contract_artifacts"].pop()
    assert_alhambra_bundle_gate_error(
        "artifact count mismatch",
        wrong_bundle_artifact_count,
        "expected 55 report-only artifacts",
    )

    missing_bundle_listener_linkage = deepcopy(alhambra_source_generator_interface_bundle_gate)
    del missing_bundle_listener_linkage["interface_reports"]["listener"]["source_file_contract_artifacts"][0][
        "war_scope_availability_persistence_plan"
    ]
    assert_alhambra_bundle_gate_error(
        "listener linkage missing",
        missing_bundle_listener_linkage,
        "listener linkage missing",
    )

    missing_bundle_listener_draft = deepcopy(alhambra_source_generator_interface_bundle_gate)
    del missing_bundle_listener_draft["interface_reports"]["listener"]["source_file_contract_artifacts"][0][
        "listener_source_body_draft"
    ]
    assert_alhambra_bundle_gate_error(
        "listener source-body draft missing",
        missing_bundle_listener_draft,
        "source-body draft completeness",
    )

    merged_bundle_localization_targets = deepcopy(alhambra_source_generator_interface_bundle_gate)
    merged_bundle_localization_targets["localization_target_paths"]["simp_chinese"] = alhambra_file_targets[
        "english"
    ]
    assert_alhambra_bundle_gate_error(
        "merged localization targets",
        merged_bundle_localization_targets,
        "localization target paths must stay split",
    )

    external_contract_may_write_src_bundle = deepcopy(alhambra_source_generator_contract)
    _alhambra_source_generator_contract(
        external_contract_may_write_src_bundle,
        alhambra_file_targets["effect_cleanup"],
    )["may_write_src"] = True
    assert_alhambra_bundle_gate_error(
        "external contract may_write_src",
        alhambra_source_generator_interface_bundle_gate,
        "may_write_src must be false",
        source_generator_contract=external_contract_may_write_src_bundle,
    )

    nested_report_may_write_src_bundle = deepcopy(alhambra_source_generator_interface_bundle_gate)
    nested_report_may_write_src_bundle["interface_reports"]["event"]["source_file_contract_artifacts"][0][
        "may_write_src"
    ] = True
    assert_alhambra_bundle_gate_error(
        "nested report may_write_src",
        nested_report_may_write_src_bundle,
        "may_write_src must be false",
    )

    emitted_source_body_bundle = deepcopy(alhambra_source_generator_interface_bundle_gate)
    emitted_source_body_bundle["interface_reports"]["gui"]["source_file_contract_artifacts"][0][
        "body_emitted"
    ] = True
    assert_alhambra_bundle_gate_error(
        "source body emission",
        emitted_source_body_bundle,
        "body_emitted must be false",
    )

    promoted_bundle = deepcopy(alhambra_source_generator_interface_bundle_gate)
    promoted_bundle["implementation_ready"] = True
    assert_alhambra_bundle_gate_error(
        "implementation_ready promotion",
        promoted_bundle,
        "implementation_ready must be false",
    )

    generated_bundle = deepcopy(alhambra_source_generator_interface_bundle_gate)
    generated_bundle["harness_generated"] = True
    assert_alhambra_bundle_gate_error(
        "harness_generated promotion",
        generated_bundle,
        "harness_generated must be false",
    )

    non_monthly_errors = validate_spec_payload(
        {"unique_wonders": [pure_non_monthly_cadence_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if non_monthly_errors:
        raise AssertionError(f"pure non-monthly cadence fixture unexpectedly failed: {non_monthly_errors}")

    hybrid_monthly_errors = validate_spec_payload(
        {"unique_wonders": [valid_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if hybrid_monthly_errors:
        raise AssertionError(f"hybrid monthly cadence fixture unexpectedly failed: {hybrid_monthly_errors}")

    no_archetype = valid_entry()
    del no_archetype["node_graph"]["archetypes"]
    no_archetype_errors = validate_spec_payload(
        {"unique_wonders": [no_archetype]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
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
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if custom_archetype_errors:
        raise AssertionError(f"custom archetype fixture unexpectedly failed: {custom_archetype_errors}")

    actor_errors = validate_spec_payload(
        {"unique_wonders": [actor_assignment_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if actor_errors:
        raise AssertionError(f"actor assignment fixture unexpectedly failed: {actor_errors}")

    mixed_shape = actor_assignment_entry()
    mixed_shape["node_graph"]["archetypes"] = ["monthly_pressure_countdown"]
    mixed_shape_errors = validate_spec_payload(
        {"unique_wonders": [mixed_shape]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if mixed_shape_errors:
        raise AssertionError(f"mixed archetype/capability fixture unexpectedly failed: {mixed_shape_errors}")

    route_errors = validate_spec_payload(
        {"unique_wonders": [route_incident_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if route_errors:
        raise AssertionError(f"route/incident fixture unexpectedly failed: {route_errors}")

    pilgrimage_route_errors = validate_spec_payload(
        {"unique_wonders": [pilgrimage_route_certification_backend_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if pilgrimage_route_errors:
        raise AssertionError(f"pilgrimage route certification fixture unexpectedly failed: {pilgrimage_route_errors}")

    maritime_route_errors = validate_spec_payload(
        {"unique_wonders": [maritime_trade_route_certification_backend_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if maritime_route_errors:
        raise AssertionError(f"maritime trade route certification fixture unexpectedly failed: {maritime_route_errors}")

    lalibela = lalibela_repo_entry()
    if lalibela["identity"]["status"] != "compiler_mapped":
        raise AssertionError(f"Lalibela status should be compiler_mapped, got {lalibela['identity']['status']!r}")
    if lalibela["node_graph"]["model"] != "state_machine_dsl_v1":
        raise AssertionError(f"Lalibela node_graph should be state_machine_dsl_v1, got {lalibela['node_graph']['model']!r}")
    lalibela_errors = validate_spec_payload(
        {"unique_wonders": [lalibela]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if lalibela_errors:
        raise AssertionError(f"Lalibela compiler_mapped fixture unexpectedly failed: {lalibela_errors}")

    lalibela_source_gap = next(
        row
        for row in lalibela["compiler_gap_ledger"]
        if row.get("primitive") == "source_compiler_pilgrimage_route_generation"
    )
    if lalibela_source_gap.get("verification_status") != "needs_codebase_search":
        raise AssertionError("Lalibela source compiler gap must remain needs_codebase_search")

    lalibela_missing_backend = lalibela_repo_entry()
    for test_node in lalibela_missing_backend["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "pilgrimage_route_certification_backend"
        ]
    assert_lalibela_error(
        "Lalibela missing pilgrimage backend",
        lalibela_missing_backend,
        "archetype 'new_jerusalem_rock_route' missing required capability(s): pilgrimage_route_certification_backend",
    )

    lalibela_source_ready_with_gap = lalibela_repo_entry()
    lalibela_source_ready_with_gap["identity"]["status"] = "source_codegen_ready"
    assert_lalibela_error(
        "Lalibela source_codegen_ready unresolved compiler gap",
        lalibela_source_ready_with_gap,
        "source-codegen-ready status has unresolved compiler gap(s): source_compiler_pilgrimage_route_generation",
    )

    inca = inca_royal_road_repo_entry()
    if inca["identity"]["status"] != "compiler_mapped":
        raise AssertionError(f"Inca Royal Road status should be compiler_mapped, got {inca['identity']['status']!r}")
    if inca["node_graph"]["model"] != "state_machine_dsl_v1":
        raise AssertionError(f"Inca Royal Road node_graph should be state_machine_dsl_v1, got {inca['node_graph']['model']!r}")
    inca_errors = validate_spec_payload(
        {"unique_wonders": [inca]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if inca_errors:
        raise AssertionError(f"Inca Royal Road compiler_mapped fixture unexpectedly failed: {inca_errors}")

    inca_source_gap = next(
        row
        for row in inca["compiler_gap_ledger"]
        if row.get("primitive") == "source_compiler_overland_relay_route_generation"
    )
    if inca_source_gap.get("verification_status") != "needs_codebase_search":
        raise AssertionError("Inca Royal Road source compiler gap must remain needs_codebase_search")

    inca_missing_backend = inca_royal_road_repo_entry()
    for test_node in inca_missing_backend["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "overland_relay_route_certification_backend"
        ]
    assert_inca_royal_road_error(
        "Inca Royal Road missing overland backend",
        inca_missing_backend,
        "archetype 'overland_relay_route_proof' missing required capability(s): overland_relay_route_certification_backend",
    )

    malacca = malacca_repo_entry()
    if malacca["identity"]["status"] != "compiler_mapped":
        raise AssertionError(f"Malacca status should be compiler_mapped, got {malacca['identity']['status']!r}")
    if malacca["node_graph"]["model"] != "state_machine_dsl_v1":
        raise AssertionError(f"Malacca node_graph should be state_machine_dsl_v1, got {malacca['node_graph']['model']!r}")
    malacca_errors = validate_spec_payload(
        {"unique_wonders": [malacca]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if malacca_errors:
        raise AssertionError(f"Malacca compiler_mapped fixture unexpectedly failed: {malacca_errors}")

    malacca_source_gap = next(
        row
        for row in malacca["compiler_gap_ledger"]
        if row.get("primitive") == "source_compiler_maritime_trade_route_generation"
    )
    if malacca_source_gap.get("verification_status") != "needs_codebase_search":
        raise AssertionError("Malacca source compiler gap must remain needs_codebase_search")

    malacca_missing_backend = malacca_repo_entry()
    for test_node in malacca_missing_backend["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "maritime_trade_route_certification_backend"
        ]
    assert_malacca_error(
        "Malacca missing maritime backend",
        malacca_missing_backend,
        "archetype 'maritime_trade_route_covenant' missing required capability(s): maritime_trade_route_certification_backend",
    )

    malacca_source_ready_with_gap = malacca_repo_entry()
    malacca_source_ready_with_gap["identity"]["status"] = "source_codegen_ready"
    assert_malacca_error(
        "Malacca source_codegen_ready unresolved compiler gap",
        malacca_source_ready_with_gap,
        "source-codegen-ready status has unresolved compiler gap(s): source_compiler_maritime_trade_route_generation",
    )

    dutch = dutch_polders_repo_entry()
    if dutch["identity"]["status"] != "compiler_mapped":
        raise AssertionError(f"Dutch Polders status should be compiler_mapped, got {dutch['identity']['status']!r}")
    if dutch["node_graph"]["model"] != "state_machine_dsl_v1":
        raise AssertionError(f"Dutch Polders node_graph should be state_machine_dsl_v1, got {dutch['node_graph']['model']!r}")
    dutch_errors = validate_spec_payload(
        {"unique_wonders": [dutch]},
        wonders=repo_wonders(),
        localization=repo_localization(),
        require_all_wonders=False,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if dutch_errors:
        raise AssertionError(f"Dutch Polders compiler_mapped fixture unexpectedly failed: {dutch_errors}")

    dutch_source_gap = next(
        row
        for row in dutch["compiler_gap_ledger"]
        if row.get("primitive") == "source_compiler_water_management_restoration_generation"
    )
    if dutch_source_gap.get("verification_status") != "needs_codebase_search":
        raise AssertionError("Dutch Polders source compiler gap must remain needs_codebase_search")

    dutch_missing_backend = dutch_polders_repo_entry()
    for test_node in dutch_missing_backend["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "water_management_restoration_completion_backend"
        ]
    assert_dutch_polders_error(
        "Dutch Polders missing water-management backend",
        dutch_missing_backend,
        "archetype 'polder_water_board_closure_inspection' missing required capability(s): water_management_restoration_completion_backend",
    )

    dutch_missing_checklist_ui = dutch_polders_repo_entry()
    dutch_missing_checklist_ui["ui_model"]["components"] = [
        component
        for component in dutch_missing_checklist_ui["ui_model"]["components"]
        if component.get("type") != "checklist"
    ]
    assert_dutch_polders_error(
        "Dutch Polders missing checklist UI",
        dutch_missing_checklist_ui,
        "archetype 'polder_water_board_closure_inspection' missing ui component(s): checklist",
    )

    dutch_source_ready_with_gap = dutch_polders_repo_entry()
    dutch_source_ready_with_gap["identity"]["status"] = "source_codegen_ready"
    assert_dutch_polders_error(
        "Dutch Polders source_codegen_ready unresolved compiler gap",
        dutch_source_ready_with_gap,
        "source-codegen-ready status has unresolved compiler gap(s): source_compiler_water_management_restoration_generation",
    )

    incident_errors = validate_spec_payload(
        {"unique_wonders": [incident_retry_entry()]},
        wonders=[WONDER],
        localization=test_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if incident_errors:
        raise AssertionError(f"incident retry fixture unexpectedly failed: {incident_errors}")

    route_hidden_loc = loc()
    route_hidden_errors = validate_spec_payload(
        {"unique_wonders": [route_hidden_entry(route_hidden_loc)]},
        wonders=[WONDER],
        localization=route_hidden_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if route_hidden_errors:
        raise AssertionError(f"route/hidden fixture unexpectedly failed: {route_hidden_errors}")

    listener_loc = loc()
    listener_errors = validate_spec_payload(
        {"unique_wonders": [resource_listener_hidden_entry(listener_loc)]},
        wonders=[WONDER],
        localization=listener_loc,
        require_all_wonders=True,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    if listener_errors:
        raise AssertionError(f"resource/listener/hidden fixture unexpectedly failed: {listener_errors}")

    capability_errors = validate_capability_registry(capability_registry)
    if capability_errors:
        raise AssertionError(f"capability registry unexpectedly failed: {capability_errors}")
    pilgrimage_contract_errors = pilgrimage_backend_contract_errors(capability_registry)
    if pilgrimage_contract_errors:
        raise AssertionError(f"pilgrimage route backend contract unexpectedly failed: {pilgrimage_contract_errors}")
    overland_contract_errors = overland_relay_backend_contract_errors(capability_registry)
    if overland_contract_errors:
        raise AssertionError(f"overland relay backend contract unexpectedly failed: {overland_contract_errors}")
    maritime_contract_errors = maritime_trade_backend_contract_errors(capability_registry)
    if maritime_contract_errors:
        raise AssertionError(f"maritime trade backend contract unexpectedly failed: {maritime_contract_errors}")
    water_management_contract_errors = water_management_backend_contract_errors(capability_registry)
    if water_management_contract_errors:
        raise AssertionError(f"water management backend contract unexpectedly failed: {water_management_contract_errors}")
    archetype_contract_errors = new_jerusalem_archetype_contract_errors(archetype_registry)
    if archetype_contract_errors:
        raise AssertionError(f"new Jerusalem archetype contract unexpectedly failed: {archetype_contract_errors}")
    overland_archetype_contract_errors = overland_relay_archetype_contract_errors(archetype_registry)
    if overland_archetype_contract_errors:
        raise AssertionError(f"overland relay archetype contract unexpectedly failed: {overland_archetype_contract_errors}")
    maritime_archetype_contract_errors = maritime_trade_archetype_contract_errors(archetype_registry)
    if maritime_archetype_contract_errors:
        raise AssertionError(f"maritime trade archetype contract unexpectedly failed: {maritime_archetype_contract_errors}")
    polder_archetype_errors = polder_archetype_contract_errors(archetype_registry)
    if polder_archetype_errors:
        raise AssertionError(f"polder water-board archetype contract unexpectedly failed: {polder_archetype_errors}")
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
        ("pilgrimage route certification backend", pilgrimage_route_certification_backend_entry()),
        ("overland relay route certification backend", overland_relay_route_certification_backend_entry()),
        ("maritime trade route certification backend", maritime_trade_route_certification_backend_entry()),
    ):
        backend_errors = validate_spec_payload(
            {"unique_wonders": [entry]},
            wonders=[WONDER],
            localization=test_loc,
            require_all_wonders=True,
            template_registry=template_registry,
            capability_registry=capability_registry,
            archetype_registry=archetype_registry,
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

    pilgrimage_missing_backend = pilgrimage_route_certification_backend_entry()
    for test_node in pilgrimage_missing_backend["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "pilgrimage_route_certification_backend"
        ]
    assert_has_error(
        "new Jerusalem archetype missing pilgrimage backend",
        pilgrimage_missing_backend,
        "archetype 'new_jerusalem_rock_route' missing required capability(s): pilgrimage_route_certification_backend",
    )

    pilgrimage_missing_route_ui = pilgrimage_route_certification_backend_entry()
    pilgrimage_missing_route_ui["ui_model"]["components"] = [
        component
        for component in pilgrimage_missing_route_ui["ui_model"]["components"]
        if component.get("type") != "route_map"
    ]
    assert_has_error(
        "new Jerusalem archetype missing route map",
        pilgrimage_missing_route_ui,
        "archetype 'new_jerusalem_rock_route' missing ui component(s): route_map",
    )

    pilgrimage_missing_incident_ui = pilgrimage_route_certification_backend_entry()
    pilgrimage_missing_incident_ui["ui_model"]["components"] = [
        component
        for component in pilgrimage_missing_incident_ui["ui_model"]["components"]
        if component.get("type") != "incident_log"
    ]
    assert_has_error(
        "new Jerusalem archetype missing incident log",
        pilgrimage_missing_incident_ui,
        "archetype 'new_jerusalem_rock_route' missing ui component(s): incident_log",
    )

    overland_missing_backend = overland_relay_route_certification_backend_entry()
    for test_node in overland_missing_backend["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "overland_relay_route_certification_backend"
        ]
    assert_has_error(
        "overland relay archetype missing backend",
        overland_missing_backend,
        "archetype 'overland_relay_route_proof' missing required capability(s): overland_relay_route_certification_backend",
    )

    overland_missing_route_ui = overland_relay_route_certification_backend_entry()
    overland_missing_route_ui["ui_model"]["components"] = [
        component
        for component in overland_missing_route_ui["ui_model"]["components"]
        if component.get("type") != "route_map"
    ]
    assert_has_error(
        "overland relay archetype missing route map",
        overland_missing_route_ui,
        "archetype 'overland_relay_route_proof' missing ui component(s): route_map",
    )

    overland_missing_incident_ui = overland_relay_route_certification_backend_entry()
    overland_missing_incident_ui["ui_model"]["components"] = [
        component
        for component in overland_missing_incident_ui["ui_model"]["components"]
        if component.get("type") != "incident_log"
    ]
    assert_has_error(
        "overland relay archetype missing incident log",
        overland_missing_incident_ui,
        "archetype 'overland_relay_route_proof' missing ui component(s): incident_log",
    )

    maritime_missing_backend = maritime_trade_route_certification_backend_entry()
    for test_node in maritime_missing_backend["node_graph"]["nodes"]:
        test_node["capabilities"] = [
            capability
            for capability in test_node.get("capabilities", [])
            if capability != "maritime_trade_route_certification_backend"
        ]
    assert_has_error(
        "maritime trade archetype missing backend",
        maritime_missing_backend,
        "archetype 'maritime_trade_route_covenant' missing required capability(s): maritime_trade_route_certification_backend",
    )

    maritime_missing_progress_ui = maritime_trade_route_certification_backend_entry()
    maritime_missing_progress_ui["ui_model"]["components"] = [
        component
        for component in maritime_missing_progress_ui["ui_model"]["components"]
        if component.get("type") != "progress_track"
    ]
    assert_has_error(
        "maritime trade archetype missing progress track",
        maritime_missing_progress_ui,
        "archetype 'maritime_trade_route_covenant' missing ui component(s): progress_track",
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
            localization=test_loc,
            require_all_wonders=True,
            template_registry=template_registry,
            capability_registry=capability_registry,
            archetype_registry=archetype_registry,
        )
        if backend_gap_errors:
            raise AssertionError(f"backend_ready gap for {capability_key} unexpectedly failed: {backend_gap_errors}")

    result = generate_fragments_for_payload(
        {"unique_wonders": [valid_entry()]},
        wonder_keys={"unique_test_wonder"},
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
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
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
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

    full_repo_codegen = generate_fragments_for_payload(
        spec_data,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    full_repo_generated_keys = {row["key"] for row in full_repo_codegen["generated"]}
    if len(full_repo_generated_keys) != 4:
        raise AssertionError(f"full repo codegen should generate 4 fragments, got {sorted(full_repo_generated_keys)}")
    if "unique_lalibela_churches" in full_repo_generated_keys:
        raise AssertionError("Lalibela must remain skipped by source-codegen dry-run")
    if "unique_dutch_polders" in full_repo_generated_keys:
        raise AssertionError("Dutch Polders must remain skipped by source-codegen dry-run")

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

    writable_capability_registry = deepcopy(capability_registry)
    writable_capability_registry["capabilities"][0]["may_write_src"] = True
    assert_has_error(
        "capability may_write_src",
        valid_entry(),
        "must declare may_write_src: false",
        capability_registry=writable_capability_registry,
    )

    finance_writable_registry = deepcopy(capability_registry)
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

    finance_source_output_registry = deepcopy(capability_registry)
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

    pilgrimage_writable_registry = deepcopy(capability_registry)
    for capability in pilgrimage_writable_registry["capabilities"]:
        if capability.get("key") == "pilgrimage_route_certification_backend":
            capability["may_write_src"] = True
            break
    assert_has_error(
        "pilgrimage route capability may_write_src",
        pilgrimage_route_certification_backend_entry(),
        "must declare may_write_src: false",
        capability_registry=pilgrimage_writable_registry,
    )

    pilgrimage_source_output_registry = deepcopy(capability_registry)
    for capability in pilgrimage_source_output_registry["capabilities"]:
        if capability.get("key") == "pilgrimage_route_certification_backend":
            capability["output_kinds"].append("loadable_src")
            break
    assert_has_error(
        "pilgrimage route capability source output",
        pilgrimage_route_certification_backend_entry(),
        "unsupported value(s): loadable_src",
        capability_registry=pilgrimage_source_output_registry,
    )

    pilgrimage_missing_output_registry = deepcopy(capability_registry)
    for capability in pilgrimage_missing_output_registry["capabilities"]:
        if capability.get("key") == "pilgrimage_route_certification_backend":
            capability["output_kinds"] = [
                output_kind
                for output_kind in capability.get("output_kinds", [])
                if output_kind != "effect_stub"
            ]
            break
    missing_output_errors = pilgrimage_backend_contract_errors(pilgrimage_missing_output_registry)
    if not any("missing output kind(s): effect_stub" in error for error in missing_output_errors):
        raise AssertionError(f"pilgrimage backend missing output fixture did not fail: {missing_output_errors}")

    overland_writable_registry = deepcopy(capability_registry)
    for capability in overland_writable_registry["capabilities"]:
        if capability.get("key") == "overland_relay_route_certification_backend":
            capability["may_write_src"] = True
            break
    assert_has_error(
        "overland relay capability may_write_src",
        overland_relay_route_certification_backend_entry(),
        "must declare may_write_src: false",
        capability_registry=overland_writable_registry,
    )

    overland_source_output_registry = deepcopy(capability_registry)
    for capability in overland_source_output_registry["capabilities"]:
        if capability.get("key") == "overland_relay_route_certification_backend":
            capability["output_kinds"].append("loadable_src")
            break
    assert_has_error(
        "overland relay capability source output",
        overland_relay_route_certification_backend_entry(),
        "unsupported value(s): loadable_src",
        capability_registry=overland_source_output_registry,
    )

    overland_missing_output_registry = deepcopy(capability_registry)
    for capability in overland_missing_output_registry["capabilities"]:
        if capability.get("key") == "overland_relay_route_certification_backend":
            capability["output_kinds"] = [
                output_kind
                for output_kind in capability.get("output_kinds", [])
                if output_kind != "effect_stub"
            ]
            break
    overland_missing_output_errors = overland_relay_backend_contract_errors(overland_missing_output_registry)
    if not any("missing output kind(s): effect_stub" in error for error in overland_missing_output_errors):
        raise AssertionError(
            f"overland relay backend missing output fixture did not fail: {overland_missing_output_errors}"
        )

    maritime_writable_registry = deepcopy(capability_registry)
    for capability in maritime_writable_registry["capabilities"]:
        if capability.get("key") == "maritime_trade_route_certification_backend":
            capability["may_write_src"] = True
            break
    assert_has_error(
        "maritime trade capability may_write_src",
        maritime_trade_route_certification_backend_entry(),
        "must declare may_write_src: false",
        capability_registry=maritime_writable_registry,
    )

    maritime_source_output_registry = deepcopy(capability_registry)
    for capability in maritime_source_output_registry["capabilities"]:
        if capability.get("key") == "maritime_trade_route_certification_backend":
            capability["output_kinds"].append("loadable_src")
            break
    assert_has_error(
        "maritime trade capability source output",
        maritime_trade_route_certification_backend_entry(),
        "unsupported value(s): loadable_src",
        capability_registry=maritime_source_output_registry,
    )

    maritime_missing_output_registry = deepcopy(capability_registry)
    for capability in maritime_missing_output_registry["capabilities"]:
        if capability.get("key") == "maritime_trade_route_certification_backend":
            capability["output_kinds"] = [
                output_kind
                for output_kind in capability.get("output_kinds", [])
                if output_kind != "effect_stub"
            ]
            break
    maritime_missing_output_errors = maritime_trade_backend_contract_errors(maritime_missing_output_registry)
    if not any("missing output kind(s): effect_stub" in error for error in maritime_missing_output_errors):
        raise AssertionError(
            f"maritime trade backend missing output fixture did not fail: {maritime_missing_output_errors}"
        )

    water_management_writable_registry = deepcopy(capability_registry)
    for capability in water_management_writable_registry["capabilities"]:
        if capability.get("key") == "water_management_restoration_completion_backend":
            capability["may_write_src"] = True
            break
    assert_dutch_polders_error(
        "water management capability may_write_src",
        dutch_polders_repo_entry(),
        "must declare may_write_src: false",
        capability_registry=water_management_writable_registry,
    )

    water_management_source_output_registry = deepcopy(capability_registry)
    for capability in water_management_source_output_registry["capabilities"]:
        if capability.get("key") == "water_management_restoration_completion_backend":
            capability["output_kinds"].append("loadable_src")
            break
    assert_dutch_polders_error(
        "water management capability source output",
        dutch_polders_repo_entry(),
        "unsupported value(s): loadable_src",
        capability_registry=water_management_source_output_registry,
    )

    water_management_missing_output_registry = deepcopy(capability_registry)
    for capability in water_management_missing_output_registry["capabilities"]:
        if capability.get("key") == "water_management_restoration_completion_backend":
            capability["output_kinds"] = [
                output_kind
                for output_kind in capability.get("output_kinds", [])
                if output_kind != "effect_stub"
            ]
            break
    water_management_missing_output_errors = water_management_backend_contract_errors(
        water_management_missing_output_registry
    )
    if not any("missing output kind(s): effect_stub" in error for error in water_management_missing_output_errors):
        raise AssertionError(
            "water management backend missing output fixture did not fail: "
            f"{water_management_missing_output_errors}"
        )

    auxiliary_writable_registry = deepcopy(capability_registry)
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

    auxiliary_source_output_registry = deepcopy(capability_registry)
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

    registry_may_write_src = deepcopy(archetype_registry)
    registry_may_write_src["archetypes"][0]["may_write_src"] = True
    assert_has_error(
        "archetype registry may write src",
        valid_entry(),
        "must declare may_write_src: false",
        archetype_registry=registry_may_write_src,
    )

    public_credit_writable_archetype_registry = deepcopy(archetype_registry)
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

    maritime_writable_archetype_registry = deepcopy(archetype_registry)
    for archetype in maritime_writable_archetype_registry["archetypes"]:
        if archetype.get("key") == "maritime_trade_route_covenant":
            archetype["may_write_src"] = True
            break
    assert_has_error(
        "maritime trade archetype may_write_src",
        maritime_trade_route_certification_backend_entry(),
        "must declare may_write_src: false",
        archetype_registry=maritime_writable_archetype_registry,
    )

    polder_writable_archetype_registry = deepcopy(archetype_registry)
    for archetype in polder_writable_archetype_registry["archetypes"]:
        if archetype.get("key") == "polder_water_board_closure_inspection":
            archetype["may_write_src"] = True
            break
    assert_dutch_polders_error(
        "polder archetype may_write_src",
        dutch_polders_repo_entry(),
        "must declare may_write_src: false",
        archetype_registry=polder_writable_archetype_registry,
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

    registry_min_nodes = deepcopy(archetype_registry)
    for archetype in registry_min_nodes["archetypes"]:
        if archetype["key"] == "monthly_pressure_countdown":
            archetype["min_nodes"] = 7
    assert_has_error(
        "archetype min nodes",
        valid_entry(),
        "archetype 'monthly_pressure_countdown' requires at least 7 node(s)",
        archetype_registry=registry_min_nodes,
    )

    registry_max_nodes = deepcopy(archetype_registry)
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

    registry_missing_template = deepcopy(template_registry)
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

    registry_unsupported_kind = deepcopy(template_registry)
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

    summary = audit_summary(
        wonders=repo_wonders(),
        specs=spec_data,
        localization=repo_localization(),
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
        repeated_entity_row_preflight=repeated_row_preflight,
        repeated_entity_row_source_plan=source_plan,
        repeated_entity_row_source_preview=source_preview,
        repeated_entity_row_source_writer_readiness=source_writer_readiness,
        repeated_entity_row_source_bundle_preview=source_bundle_preview,
        repeated_entity_row_alhambra_source_generator_contract=alhambra_source_generator_contract,
        repeated_entity_row_alhambra_event_source_generator_interface=alhambra_event_source_generator_interface,
        repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface=(
            alhambra_scripted_effect_cleanup_source_generator_interface
        ),
        repeated_entity_row_alhambra_scripted_trigger_source_generator_interface=(
            alhambra_scripted_trigger_source_generator_interface
        ),
        repeated_entity_row_alhambra_gui_source_generator_interface=(
            alhambra_gui_source_generator_interface
        ),
        repeated_entity_row_alhambra_listener_source_generator_interface=(
            alhambra_listener_source_generator_interface
        ),
        repeated_entity_row_alhambra_localization_source_generator_interface=(
            alhambra_localization_source_generator_interface
        ),
        repeated_entity_row_alhambra_source_generator_interface_bundle_gate=(
            alhambra_source_generator_interface_bundle_gate
        ),
    )
    if summary["source_codegen_ready_count"] != 4:
        raise AssertionError(f"source_codegen_ready count should remain 4, got {summary['source_codegen_ready_count']}")
    if summary["implementation_ready_count"] != 0:
        raise AssertionError(
            f"implementation_ready count should remain 0, got {summary['implementation_ready_count']}"
        )
    if summary["harness_generated_count"] != 0:
        raise AssertionError(f"harness_generated count should remain 0, got {summary['harness_generated_count']}")
    if summary["codegen_tier_summary"]["may_write_src"] != 0:
        raise AssertionError(
            "codegen tier may_write_src count should remain 0, got "
            f"{summary['codegen_tier_summary']['may_write_src']}"
        )
    readiness_summary = summary["repeated_entity_row_source_writer_readiness"]
    if readiness_summary["ready_artifact_count"] != 0:
        raise AssertionError(
            "source-writer readiness ready_artifact_count should remain 0, got "
            f"{readiness_summary['ready_artifact_count']}"
        )
    if readiness_summary["blocked_artifact_count"] != 177:
        raise AssertionError(
            "source-writer readiness blocked_artifact_count should remain 177, got "
            f"{readiness_summary['blocked_artifact_count']}"
        )
    bundle_summary = summary["repeated_entity_row_source_bundle_preview"]
    if bundle_summary["bundle_count"] != 4:
        raise AssertionError(f"source bundle preview count should remain 4, got {bundle_summary['bundle_count']}")
    if bundle_summary["artifact_count"] != 177 or bundle_summary["closure_contract_count"] != 177:
        raise AssertionError(f"source bundle preview should preserve 177 closure artifacts: {bundle_summary}")
    if (
        bundle_summary["source_ready_count"] != 0
        or bundle_summary["source_writer_allowed_count"] != 0
        or bundle_summary["may_write_src_count"] != 0
        or bundle_summary["writes_src_count"] != 0
    ):
        raise AssertionError(f"source bundle preview no-write/readiness counts changed: {bundle_summary}")
    alhambra_generator_summary = summary["repeated_entity_row_alhambra_source_generator_contract"]["summary"]
    if alhambra_generator_summary["generator_contract_count"] != 7:
        raise AssertionError(
            "Alhambra source generator contract count should remain 7, got "
            f"{alhambra_generator_summary['generator_contract_count']}"
        )
    if alhambra_generator_summary["artifact_count"] != 45:
        raise AssertionError(
            "Alhambra source generator contract artifact_count should remain 45, got "
            f"{alhambra_generator_summary['artifact_count']}"
        )
    if (
        alhambra_generator_summary["source_writer_allowed_count"] != 0
        or alhambra_generator_summary["may_write_src_count"] != 0
        or alhambra_generator_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra source generator contract no-write counts changed: "
            f"{alhambra_generator_summary}"
        )
    alhambra_event_interface_summary = summary[
        "repeated_entity_row_alhambra_event_source_generator_interface"
    ]["summary"]
    if alhambra_event_interface_summary["interface_count"] != 1:
        raise AssertionError(
            "Alhambra event source generator interface count should remain 1, got "
            f"{alhambra_event_interface_summary['interface_count']}"
        )
    if alhambra_event_interface_summary["artifact_count"] != 8:
        raise AssertionError(
            "Alhambra event source generator interface artifact_count should remain 8, got "
            f"{alhambra_event_interface_summary['artifact_count']}"
        )
    if (
        alhambra_event_interface_summary["source_writer_allowed_count"] != 0
        or alhambra_event_interface_summary["may_write_src_count"] != 0
        or alhambra_event_interface_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra event source generator interface no-write counts changed: "
            f"{alhambra_event_interface_summary}"
        )
    alhambra_effect_cleanup_interface_summary = summary[
        "repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface"
    ]["summary"]
    if alhambra_effect_cleanup_interface_summary["interface_count"] != 1:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface count should remain 1, got "
            f"{alhambra_effect_cleanup_interface_summary['interface_count']}"
        )
    if alhambra_effect_cleanup_interface_summary["artifact_count"] != 18:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface artifact_count should remain 18, got "
            f"{alhambra_effect_cleanup_interface_summary['artifact_count']}"
        )
    if alhambra_effect_cleanup_interface_summary["family_artifact_counts"] != {"cleanup": 8, "effect": 10}:
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface family split changed: "
            f"{alhambra_effect_cleanup_interface_summary}"
        )
    if (
        alhambra_effect_cleanup_interface_summary["source_writer_allowed_count"] != 0
        or alhambra_effect_cleanup_interface_summary["may_write_src_count"] != 0
        or alhambra_effect_cleanup_interface_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra scripted-effect/cleanup source generator interface no-write counts changed: "
            f"{alhambra_effect_cleanup_interface_summary}"
        )
    alhambra_trigger_interface_summary = summary[
        "repeated_entity_row_alhambra_scripted_trigger_source_generator_interface"
    ]["summary"]
    if alhambra_trigger_interface_summary["interface_count"] != 1:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface count should remain 1, got "
            f"{alhambra_trigger_interface_summary['interface_count']}"
        )
    if alhambra_trigger_interface_summary["artifact_count"] != 6:
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface artifact_count should remain 6, got "
            f"{alhambra_trigger_interface_summary['artifact_count']}"
        )
    if (
        alhambra_trigger_interface_summary["source_writer_allowed_count"] != 0
        or alhambra_trigger_interface_summary["may_write_src_count"] != 0
        or alhambra_trigger_interface_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra scripted-trigger source generator interface no-write counts changed: "
            f"{alhambra_trigger_interface_summary}"
        )
    alhambra_gui_interface_summary = summary[
        "repeated_entity_row_alhambra_gui_source_generator_interface"
    ]["summary"]
    if alhambra_gui_interface_summary["interface_count"] != 1:
        raise AssertionError(
            "Alhambra GUI source generator interface count should remain 1, got "
            f"{alhambra_gui_interface_summary['interface_count']}"
        )
    if alhambra_gui_interface_summary["artifact_count"] != 2:
        raise AssertionError(
            "Alhambra GUI source generator interface artifact_count should remain 2, got "
            f"{alhambra_gui_interface_summary['artifact_count']}"
        )
    if alhambra_gui_interface_summary["listener_interface_declared"] is not False:
        raise AssertionError(
            "Alhambra GUI source generator interface must not declare listener interface: "
            f"{alhambra_gui_interface_summary}"
        )
    if (
        alhambra_gui_interface_summary["source_writer_allowed_count"] != 0
        or alhambra_gui_interface_summary["may_write_src_count"] != 0
        or alhambra_gui_interface_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra GUI source generator interface no-write counts changed: "
            f"{alhambra_gui_interface_summary}"
        )
    alhambra_listener_interface_summary = summary[
        "repeated_entity_row_alhambra_listener_source_generator_interface"
    ]["summary"]
    if alhambra_listener_interface_summary["interface_count"] != 1:
        raise AssertionError(
            "Alhambra listener source generator interface count should remain 1, got "
            f"{alhambra_listener_interface_summary['interface_count']}"
        )
    if alhambra_listener_interface_summary["artifact_count"] != 1:
        raise AssertionError(
            "Alhambra listener source generator interface artifact_count should remain 1, got "
            f"{alhambra_listener_interface_summary['artifact_count']}"
        )
    if alhambra_listener_interface_summary["artifact_kind"] != "listener_war_integration":
        raise AssertionError(
            "Alhambra listener source generator interface artifact kind changed: "
            f"{alhambra_listener_interface_summary}"
        )
    if (
        alhambra_listener_interface_summary["source_writer_allowed_count"] != 0
        or alhambra_listener_interface_summary["may_write_src_count"] != 0
        or alhambra_listener_interface_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra listener source generator interface no-write counts changed: "
            f"{alhambra_listener_interface_summary}"
        )
    alhambra_localization_interface_summary = summary[
        "repeated_entity_row_alhambra_localization_source_generator_interface"
    ]["summary"]
    if alhambra_localization_interface_summary["interface_count"] != 2:
        raise AssertionError(
            "Alhambra localization source generator interface count should remain 2, got "
            f"{alhambra_localization_interface_summary['interface_count']}"
        )
    if alhambra_localization_interface_summary["artifact_count"] != 20:
        raise AssertionError(
            "Alhambra localization source generator interface artifact_count should remain 20, got "
            f"{alhambra_localization_interface_summary['artifact_count']}"
        )
    if alhambra_localization_interface_summary["target_artifact_counts"] != {
        alhambra_file_targets["english"]: 10,
        alhambra_file_targets["simp_chinese"]: 10,
    }:
        raise AssertionError(
            "Alhambra localization source generator interface target counts changed: "
            f"{alhambra_localization_interface_summary}"
        )
    if (
        alhambra_localization_interface_summary["source_writer_allowed_count"] != 0
        or alhambra_localization_interface_summary["may_write_src_count"] != 0
        or alhambra_localization_interface_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra localization source generator interface no-write counts changed: "
            f"{alhambra_localization_interface_summary}"
        )
    alhambra_bundle_gate_summary = summary[
        "repeated_entity_row_alhambra_source_generator_interface_bundle_gate"
    ]["summary"]
    if alhambra_bundle_gate_summary["interface_group_count"] != 6:
        raise AssertionError(
            "Alhambra source generator interface bundle gate group count should remain 6, got "
            f"{alhambra_bundle_gate_summary['interface_group_count']}"
        )
    if alhambra_bundle_gate_summary["target_file_count"] != 7:
        raise AssertionError(
            "Alhambra source generator interface bundle gate target count should remain 7, got "
            f"{alhambra_bundle_gate_summary['target_file_count']}"
        )
    if (
        alhambra_bundle_gate_summary["artifact_count"] != 55
        or alhambra_bundle_gate_summary["report_only_artifact_count"] != 55
    ):
        raise AssertionError(
            "Alhambra source generator interface bundle gate report-only artifact count should remain 55: "
            f"{alhambra_bundle_gate_summary}"
        )
    if alhambra_bundle_gate_summary["interface_group_artifact_counts"] != {
        "event": 8,
        "scripted_effect_cleanup": 18,
        "trigger": 6,
        "gui": 2,
        "listener": 1,
        "localization": 20,
    }:
        raise AssertionError(
            "Alhambra source generator interface bundle gate family counts changed: "
            f"{alhambra_bundle_gate_summary}"
        )
    if alhambra_bundle_gate_summary["source_body_draft_artifact_counts"] != {
        "event": 8,
        "scripted_effect_cleanup": 18,
        "trigger": 6,
        "gui": 2,
        "listener": 1,
        "localization": 20,
    }:
        raise AssertionError(
            "Alhambra source generator interface bundle gate source-body draft counts changed: "
            f"{alhambra_bundle_gate_summary}"
        )
    audit_source_body_draft_gate = alhambra_bundle_gate_summary["source_body_draft_completeness_gate"]
    if (
        audit_source_body_draft_gate["all_source_body_draft_groups_complete"] is not True
        or audit_source_body_draft_gate["source_body_draft_count"] != 55
        or audit_source_body_draft_gate["missing_source_body_draft_groups"] != []
    ):
        raise AssertionError(
            "Alhambra source generator interface bundle gate source-body draft completeness changed: "
            f"{alhambra_bundle_gate_summary}"
        )
    if (
        alhambra_bundle_gate_summary["source_writer_allowed_count"] != 0
        or alhambra_bundle_gate_summary["may_write_src_count"] != 0
        or alhambra_bundle_gate_summary["writes_src_count"] != 0
    ):
        raise AssertionError(
            "Alhambra source generator interface bundle gate no-write counts changed: "
            f"{alhambra_bundle_gate_summary}"
        )

    print("[OK] Unique wonder ritual Harness quality-gate tests passed.")


if __name__ == "__main__":
    main()
