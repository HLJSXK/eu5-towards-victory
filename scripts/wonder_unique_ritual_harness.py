import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics.io import (  # noqa: E402
    dump_yaml_document,
    load_unique_wonders_source_data,
    load_yaml,
)
from wonder_mechanics._core import loc_line  # noqa: E402

SPEC_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_specs.yaml"
TEMPLATE_REGISTRY_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_codegen_templates.yaml"
CAPABILITY_REGISTRY_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_capabilities.yaml"
ARCHETYPE_REGISTRY_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_archetypes.yaml"
DESIGN_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_designs.yaml"
DESIGN_MATRIX_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_design_matrix.yaml"
PROMPTS_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_prompts.yaml"
LOCALIZATION_FILE = REPO_ROOT / "data" / "wonder_localization.yaml"
LOCALIZATION_INDEX_FILE = REPO_ROOT / "data" / "index" / "loc_keys_en.txt"

LEGACY_CODEGEN_READY_STATUSES = {"implementation_ready"}
SOURCE_CODEGEN_READY_STATUSES = {"source_codegen_ready", "harness_generated"} | LEGACY_CODEGEN_READY_STATUSES
CODEGEN_ELIGIBLE_STATUSES = SOURCE_CODEGEN_READY_STATUSES
DESIGN_STATUS_ORDER = {
    "design_complete",
    "compiler_mapped",
    "evidence_verified",
    "source_codegen_ready",
}
DESIGN_IR_REQUIRED_STATUSES = set(DESIGN_STATUS_ORDER)
SEMANTIC_GRAPH_STATUSES = {"compiler_mapped"} | SOURCE_CODEGEN_READY_STATUSES
IMPLEMENTED_STATUSES = {"implemented_parity"} | DESIGN_IR_REQUIRED_STATUSES | SOURCE_CODEGEN_READY_STATUSES
STUB_STATUSES = {"stub", "needs_design"}
ALLOWED_STATUSES = IMPLEMENTED_STATUSES | STUB_STATUSES
COMPILER_GAP_VERIFICATION_STATUSES = {
    "semantic_only",
    "needs_codebase_search",
    "interface_candidate",
    "verified_existing",
    "backend_ready",
}
UNRESOLVED_COMPILER_GAP_STATUSES = {
    "semantic_only",
    "needs_codebase_search",
    "interface_candidate",
}
DESIGN_IR_REQUIRED_FIELDS = {
    "phases",
    "player_proofs",
    "tracked_entity_sets",
    "selectors",
    "risk_branches",
    "player_actions",
    "map_scope_evidence",
    "ui_feedback_model",
    "uniqueness_constraints",
    "projection_notes",
}
TRACKED_ENTITY_SET_REQUIRED_FIELDS = {
    "key",
    "entity_type",
    "state_values",
    "per_entity_state",
    "selector",
    "ui_binding",
}
COMPILER_GAP_REQUIRED_FIELDS = {
    "primitive",
    "design_semantics",
    "required_game_interfaces",
    "codebase_evidence",
    "verification_status",
    "search_questions",
    "blocked_by",
    "fallback_if_unavailable",
}
SUPPORTED_UI_COMPONENTS = {
    "checklist",
    "route_map",
    "actor_slots",
    "material_stockpile",
    "incident_log",
    "progress_track",
}
SUPPORTED_LISTENERS = {
    "monthly",
    "ruler_death",
    "pre_winning_war",
    "ending_war",
    "auxiliary_building_completion",
}
SUPPORTED_CADENCE_TYPES = {
    "instant_but_branching",
    "event_driven",
    "player_action_sequence",
    "construction_or_auxiliary_building",
    "war_validated",
    "succession_validated",
    "route_certification",
    "actor_assignment",
    "resource_delivery",
    "monthly_institutionalization",
    "hybrid",
}
SUPPORTED_NODE_KINDS = {
    "assignment_gate",
    "choice_event",
    "event",
    "retry_event",
    "resource_gate",
    "route_gate",
    "listener_gate",
    "incident_event",
    "hidden_executor_handoff",
    "monthly_progress_gate",
    "final_reward_dispatch",
}
SUPPORTED_ACTION_KINDS = {
    "effect_script",
    "generator_template",
    "reward_dispatch_stub",
}
SUPPORTED_CHECK_KINDS = {
    "trigger_script",
    "generator_template",
}
SUPPORTED_TEMPLATE_OUTPUT_KINDS = {
    "markdown_fragment",
    "event_skeleton",
    "effect_stub",
    "trigger_stub",
    "gui_summary",
    "loc_draft",
}
SUPPORTED_CAPABILITY_OUTPUT_KINDS = SUPPORTED_TEMPLATE_OUTPUT_KINDS | {
    "player_facing_tooltip",
    "hidden_executor_note",
}
SUPPORTED_SCOPE_CONTRACT_SCOPES = {
    "country",
    "location",
    "character",
    "international_organization",
    "gui_fragment",
    "none",
}
TEMPLATE_CONTRACT_REQUIRED_FIELDS = {
    "key",
    "supported_node_kinds",
    "supported_action_kinds",
    "supported_check_kinds",
    "required_fields",
    "output_kinds",
    "verified_interface",
    "may_write_src",
    "notes",
}
CAPABILITY_CONTRACT_REQUIRED_FIELDS = {
    "key",
    "supported_node_kinds",
    "required_node_fields",
    "required_variable_roles",
    "supported_listener_kinds",
    "supported_ui_components",
    "output_kinds",
    "verified_interface",
    "may_write_src",
    "notes",
}
ARCHETYPE_CONTRACT_REQUIRED_FIELDS = {
    "key",
    "required_capabilities",
    "allowed_node_kinds",
    "required_variable_roles",
    "required_ui_components",
    "required_listeners",
    "min_nodes",
    "max_nodes",
    "requires_retry_path",
    "requires_hidden_executor_handoff",
    "terminal_requires_capability",
    "verification_tier",
    "may_write_src",
    "notes",
}
NODE_REQUIRED_FIELDS = {
    "key",
    "kind",
    "capabilities",
    "event_id",
    "player_visible",
    "historical_anchor",
    "enter_condition",
    "completion_condition",
    "failure_or_retry",
    "retry_target",
    "next_nodes",
    "writes",
    "reads",
    "ui_state",
    "loc_refs",
}
EDGE_REQUIRED_FIELDS = {"from", "to", "condition", "effect", "label_key"}
ACTION_REQUIRED_FIELDS = {"key", "kind", "scope", "verified_interface"}
CHECK_REQUIRED_FIELDS = {"key", "kind", "tooltip_key"}
VARIABLE_REQUIRED_FIELDS = {
    "name",
    "scope",
    "type",
    "initial_value",
    "writer_nodes",
    "reader_nodes",
    "cleanup",
}
UI_BINDING_REQUIRED_FIELDS = {"key", "component_key", "variable_refs", "node_refs", "loc_refs"}
SCOPE_CONTRACT_REQUIRED_FIELDS = {
    "root_scope",
    "current_scope",
    "target_scopes",
    "tooltip_safe",
    "unsafe_pre_eval",
}
LISTENER_CONTRACT_REQUIRED_FIELDS = {
    "listener",
    "cadence",
    "reads",
    "writes",
    "completion_check",
    "failure_route",
}
GENERATION_REQUIRED_FIELDS = {
    "status",
    "target_files",
    "verified_templates",
    "blocked_templates",
    "dry_run_notes",
}
UI_VARIABLE_FIELDS = {
    "value_variable",
    "status_variable",
    "progress_variable",
    "counter_variable",
    "flag_variable",
}
REQUIRED_REWARD_CHANNELS = (
    "permanent_country_modifier",
    "local_building_reward",
    "one_time_reward",
)
CUSTOM_ARCHETYPE_PREFIX = "custom_"
MECHANIC_SIGNATURE_REQUIRED_FIELDS = {
    "wonder_specific_hook",
    "core_interaction_loop",
    "player_decision_pattern",
    "state_feedback_model",
    "failure_or_tension_model",
    "reward_expression",
    "reuse_risk_mitigation",
}
MECHANIC_SIGNATURE_MIN_FIELD_CHARS = 32
MECHANIC_SIGNATURE_MIN_TOTAL_CHARS = 420
MECHANIC_SIGNATURE_PLACEHOLDER_TOKENS = {
    "needs_design",
    "to be authored",
    "placeholder",
    "generic ritual",
    "standard ritual",
    "same as existing",
}
CADENCE_SIGNATURE_REQUIRED_FIELDS = {
    "cadence_type",
    "cadence_rationale",
    "player_agency_model",
    "non_monthly_triggers_or_reason",
    "pacing_failure_mode",
}
CADENCE_SIGNATURE_MIN_FIELD_CHARS = 32
CADENCE_SIGNATURE_MIN_TOTAL_CHARS = 260
CADENCE_SIGNATURE_PLACEHOLDER_TOKENS = MECHANIC_SIGNATURE_PLACEHOLDER_TOKENS | {
    "tbd",
    "n/a",
    "none",
    "not applicable",
}
CADENCE_NON_MONTHLY_MIN_CHARS = 80
CADENCE_NON_MONTHLY_INTERACTION_TOKENS = {
    "action",
    "actor",
    "assignment",
    "branch",
    "building",
    "choice",
    "choose",
    "construction",
    "decision",
    "delivery",
    "event",
    "fail",
    "failure",
    "incident",
    "listener",
    "resource",
    "risk",
    "route",
    "succession",
    "trigger",
    "war",
}
CADENCE_NON_MONTHLY_BLOCKED_PATTERNS = (
    re.compile(r"\bnone\b"),
    re.compile(r"\bn/a\b"),
    re.compile(r"\bnot applicable\b"),
    re.compile(r"\bno non[- ]monthly\b"),
    re.compile(r"\bpure monthly\b"),
    re.compile(r"\bonly monthly\b"),
    re.compile(r"\bjust monthly\b"),
)
CADENCE_HYBRID_MONTHLY_LOCAL_ROLE_TOKENS = {
    "auxiliary",
    "background",
    "checkpoint",
    "limited",
    "local",
    "one axis",
    "partial",
    "secondary",
    "substep",
    "supporting",
}
EVENT_ID_PATTERN = re.compile(r"\btv_engineering_department\.([0-9]+)\b")
_LOCALIZATION_INDEX_KEYS_CACHE: set[str] | None = None


def load_unique_wonders() -> list[dict[str, Any]]:
    return list(load_unique_wonders_source_data().get("unique_wonders", []))


def load_optional_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_yaml(path)


def load_spec_data(path: Path = SPEC_FILE) -> dict[str, Any]:
    return load_optional_yaml(path) or {"metadata": {}, "unique_wonders": []}


def load_template_registry(path: Path = TEMPLATE_REGISTRY_FILE) -> dict[str, Any]:
    return load_optional_yaml(path) or {"metadata": {}, "templates": []}


def load_capability_registry(path: Path = CAPABILITY_REGISTRY_FILE) -> dict[str, Any]:
    return load_optional_yaml(path) or {"metadata": {}, "capabilities": []}


def load_archetype_registry(path: Path = ARCHETYPE_REGISTRY_FILE) -> dict[str, Any]:
    return load_optional_yaml(path) or {"metadata": {}, "archetypes": []}


def template_registry_index(registry: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    payload = registry if registry is not None else load_template_registry()
    templates = payload.get("templates", []) if isinstance(payload, dict) else []
    index: dict[str, dict[str, Any]] = {}
    if not isinstance(templates, list):
        return index
    for template in templates:
        if isinstance(template, dict) and template.get("key"):
            index[str(template["key"])] = template
    return index


def supported_codegen_template_keys(registry: dict[str, Any] | None = None) -> set[str]:
    return set(template_registry_index(registry))


def capability_registry_index(registry: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    payload = registry if registry is not None else load_capability_registry()
    capabilities = payload.get("capabilities", []) if isinstance(payload, dict) else []
    index: dict[str, dict[str, Any]] = {}
    if not isinstance(capabilities, list):
        return index
    for capability in capabilities:
        if isinstance(capability, dict) and capability.get("key"):
            index[str(capability["key"])] = capability
    return index


def supported_capability_keys(registry: dict[str, Any] | None = None) -> set[str]:
    return set(capability_registry_index(registry))


def archetype_registry_index(registry: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    payload = registry if registry is not None else load_archetype_registry()
    archetypes = payload.get("archetypes", []) if isinstance(payload, dict) else []
    index: dict[str, dict[str, Any]] = {}
    if not isinstance(archetypes, list):
        return index
    for archetype in archetypes:
        if isinstance(archetype, dict) and archetype.get("key"):
            index[str(archetype["key"])] = archetype
    return index


def supported_archetype_keys(registry: dict[str, Any] | None = None) -> set[str]:
    return set(archetype_registry_index(registry))


def validate_template_registry(
    registry: dict[str, Any] | None = None,
    *,
    path: Path = TEMPLATE_REGISTRY_FILE,
) -> list[str]:
    errors: list[str] = []
    if registry is None:
        if not path.exists():
            return [f"{path.relative_to(REPO_ROOT).as_posix()} is missing"]
        registry = load_template_registry(path)
    if not isinstance(registry, dict):
        return ["template registry must be a mapping"]

    metadata = registry.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("template registry metadata must be a mapping")
    elif metadata.get("generated_game_code") is not False:
        errors.append("template registry metadata.generated_game_code must be false")

    templates = registry.get("templates")
    if not isinstance(templates, list):
        errors.append("template registry templates must be a list")
        return errors
    if not templates:
        errors.append("template registry templates must not be empty")

    seen: set[str] = set()
    for idx, template in enumerate(templates, 1):
        if not isinstance(template, dict):
            errors.append(f"template registry templates[{idx}] must be a mapping")
            continue
        key = str(template.get("key", f"<missing:{idx}>"))
        for field in _missing_required(template, TEMPLATE_CONTRACT_REQUIRED_FIELDS):
            errors.append(f"template registry {key} missing required field {field}")
        if not template.get("key"):
            continue
        if key in seen:
            errors.append(f"template registry duplicate template {key}")
        seen.add(key)
        if template.get("may_write_src") is not False:
            errors.append(f"template registry {key} must declare may_write_src: false")
        if not str(template.get("verified_interface", "")).strip():
            errors.append(f"template registry {key} verified_interface must not be empty")
        for field, allowed in (
            ("supported_node_kinds", SUPPORTED_NODE_KINDS),
            ("supported_action_kinds", SUPPORTED_ACTION_KINDS),
            ("supported_check_kinds", SUPPORTED_CHECK_KINDS),
            ("output_kinds", SUPPORTED_TEMPLATE_OUTPUT_KINDS),
        ):
            values = template.get(field)
            if not isinstance(values, list):
                errors.append(f"template registry {key} {field} must be a list")
                continue
            unsupported = sorted(str(value) for value in values if value not in allowed)
            if unsupported:
                errors.append(
                    f"template registry {key} {field} has unsupported value(s): {', '.join(unsupported)}"
                )
        required_fields = template.get("required_fields")
        if not isinstance(required_fields, list):
            errors.append(f"template registry {key} required_fields must be a list")
        elif any(not str(field).strip() for field in required_fields):
            errors.append(f"template registry {key} required_fields must contain non-empty strings")
    return errors


def validate_capability_registry(
    registry: dict[str, Any] | None = None,
    *,
    path: Path = CAPABILITY_REGISTRY_FILE,
) -> list[str]:
    errors: list[str] = []
    if registry is None:
        if not path.exists():
            return [f"{path.relative_to(REPO_ROOT).as_posix()} is missing"]
        registry = load_capability_registry(path)
    if not isinstance(registry, dict):
        return ["capability registry must be a mapping"]

    metadata = registry.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("capability registry metadata must be a mapping")
    elif metadata.get("generated_game_code") is not False:
        errors.append("capability registry metadata.generated_game_code must be false")

    capabilities = registry.get("capabilities")
    if not isinstance(capabilities, list):
        errors.append("capability registry capabilities must be a list")
        return errors
    if not capabilities:
        errors.append("capability registry capabilities must not be empty")

    seen: set[str] = set()
    for idx, capability in enumerate(capabilities, 1):
        if not isinstance(capability, dict):
            errors.append(f"capability registry capabilities[{idx}] must be a mapping")
            continue
        key = str(capability.get("key", f"<missing:{idx}>"))
        for field in _missing_required(capability, CAPABILITY_CONTRACT_REQUIRED_FIELDS):
            errors.append(f"capability registry {key} missing required field {field}")
        if not capability.get("key"):
            continue
        if key in seen:
            errors.append(f"capability registry duplicate capability {key}")
        seen.add(key)
        if capability.get("may_write_src") is not False:
            errors.append(f"capability registry {key} must declare may_write_src: false")
        if not str(capability.get("verified_interface", "")).strip():
            errors.append(f"capability registry {key} verified_interface must not be empty")
        for field, allowed in (
            ("supported_node_kinds", SUPPORTED_NODE_KINDS),
            ("supported_listener_kinds", SUPPORTED_LISTENERS),
            ("supported_ui_components", SUPPORTED_UI_COMPONENTS),
            ("output_kinds", SUPPORTED_CAPABILITY_OUTPUT_KINDS),
        ):
            values = capability.get(field)
            if not isinstance(values, list):
                errors.append(f"capability registry {key} {field} must be a list")
                continue
            unsupported = sorted(str(value) for value in values if value not in allowed)
            if unsupported:
                errors.append(
                    f"capability registry {key} {field} has unsupported value(s): {', '.join(unsupported)}"
                )
        for field in ("required_node_fields", "required_variable_roles"):
            values = capability.get(field)
            if not isinstance(values, list):
                errors.append(f"capability registry {key} {field} must be a list")
            elif any(not str(value).strip() for value in values):
                errors.append(f"capability registry {key} {field} must contain non-empty strings")
    return errors


def validate_archetype_registry(
    registry: dict[str, Any] | None = None,
    *,
    path: Path = ARCHETYPE_REGISTRY_FILE,
    capability_registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if registry is None:
        if not path.exists():
            return [f"{path.relative_to(REPO_ROOT).as_posix()} is missing"]
        registry = load_archetype_registry(path)
    if not isinstance(registry, dict):
        return ["archetype registry must be a mapping"]

    metadata = registry.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("archetype registry metadata must be a mapping")
    elif metadata.get("generated_game_code") is not False:
        errors.append("archetype registry metadata.generated_game_code must be false")

    archetypes = registry.get("archetypes")
    if not isinstance(archetypes, list):
        errors.append("archetype registry archetypes must be a list")
        return errors
    if not archetypes:
        errors.append("archetype registry archetypes must not be empty")

    capability_keys = supported_capability_keys(capability_registry)
    seen: set[str] = set()
    for idx, archetype in enumerate(archetypes, 1):
        if not isinstance(archetype, dict):
            errors.append(f"archetype registry archetypes[{idx}] must be a mapping")
            continue
        key = str(archetype.get("key", f"<missing:{idx}>"))
        for field in _missing_required(archetype, ARCHETYPE_CONTRACT_REQUIRED_FIELDS):
            errors.append(f"archetype registry {key} missing required field {field}")
        if not archetype.get("key"):
            continue
        if key in seen:
            errors.append(f"archetype registry duplicate archetype {key}")
        seen.add(key)
        if archetype.get("may_write_src") is not False:
            errors.append(f"archetype registry {key} must declare may_write_src: false")
        if str(archetype.get("verification_tier", "")) != "harness_v1_mechanic_blueprint":
            errors.append(f"archetype registry {key} verification_tier must be harness_v1_mechanic_blueprint")
        if not str(archetype.get("notes", "")).strip():
            errors.append(f"archetype registry {key} notes must not be empty")
        for field, allowed in (
            ("required_capabilities", capability_keys),
            ("allowed_node_kinds", SUPPORTED_NODE_KINDS),
            ("required_ui_components", SUPPORTED_UI_COMPONENTS),
            ("required_listeners", SUPPORTED_LISTENERS),
        ):
            values = archetype.get(field)
            if not isinstance(values, list):
                errors.append(f"archetype registry {key} {field} must be a list")
                continue
            unsupported = sorted(str(value) for value in values if value not in allowed)
            if unsupported:
                errors.append(
                    f"archetype registry {key} {field} has unsupported value(s): {', '.join(unsupported)}"
                )
        required_variable_roles = archetype.get("required_variable_roles")
        if not isinstance(required_variable_roles, list):
            errors.append(f"archetype registry {key} required_variable_roles must be a list")
        elif any(not str(value).strip() for value in required_variable_roles):
            errors.append(f"archetype registry {key} required_variable_roles must contain non-empty strings")
        terminal_capability = archetype.get("terminal_requires_capability")
        if terminal_capability is not None and str(terminal_capability) not in capability_keys:
            errors.append(
                f"archetype registry {key} terminal_requires_capability has unsupported value {terminal_capability!r}"
            )
        for field in ("requires_retry_path", "requires_hidden_executor_handoff"):
            if not isinstance(archetype.get(field), bool):
                errors.append(f"archetype registry {key} {field} must be a boolean")
        try:
            min_nodes = int(archetype.get("min_nodes"))
            max_nodes = int(archetype.get("max_nodes"))
        except (TypeError, ValueError):
            errors.append(f"archetype registry {key} min_nodes and max_nodes must be integers")
            continue
        if min_nodes < 1:
            errors.append(f"archetype registry {key} min_nodes must be positive")
        if max_nodes < min_nodes:
            errors.append(f"archetype registry {key} max_nodes must be greater than or equal to min_nodes")
    return errors


def wonder_index(wonders: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(wonder["key"]): wonder for wonder in wonders}


def list_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for entry in data.get("unique_wonders", []) or []:
        if isinstance(entry, dict) and entry.get("key"):
            index[str(entry["key"])] = entry
        elif isinstance(entry, dict):
            identity = entry.get("identity", {})
            if isinstance(identity, dict) and identity.get("key"):
                index[str(identity["key"])] = entry
    return index


def loc_english(data: dict[str, Any] | None = None) -> dict[str, str]:
    payload = data if data is not None else load_optional_yaml(LOCALIZATION_FILE)
    return dict((payload.get("wonder_localization") or {}).get("english") or {})


def runtime_prefix_for_wonder(wonder: dict[str, Any]) -> str:
    explicit = {
        "unique_pharos_lighthouse": "tv_wonder_pharos",
        "unique_hagia_sophia": "tv_wonder_hagia",
    }
    key = str(wonder["key"])
    return explicit.get(key, "tv_wonder_" + key.removeprefix("unique_"))


def base_identity(wonder: dict[str, Any], status: str) -> dict[str, Any]:
    return {
        "id": int(wonder["id"]),
        "key": str(wonder["key"]),
        "base_key": str(wonder["base_key"]),
        "location": str(wonder["location"]),
        "runtime_prefix": runtime_prefix_for_wonder(wonder),
        "status": status,
    }


def pending_rewards() -> dict[str, dict[str, str]]:
    return {
        channel: {
            "status": "pending",
            "source": "needs_design",
            "description": "To be authored before this ritual can pass the Harness quality gates.",
        }
        for channel in REQUIRED_REWARD_CHANNELS
    }


def stub_spec(wonder: dict[str, Any]) -> dict[str, Any]:
    ritual_key = str((wonder.get("ritual") or {}).get("key") or "ritual")
    return {
        "identity": base_identity(wonder, "stub"),
        "event_ids": [],
        "node_graph": {
            "model": "not_authored",
            "historical_mechanic": "",
            "listeners": [],
            "summary": (
                f"{wonder['key']} needs a full playable unique ritual spec. "
                "The entry exists only so audit tooling can track coverage."
            ),
            "nodes": [],
        },
        "ui_model": {"components": []},
        "rewards": pending_rewards(),
        "localization": {
            "panel_text_keys": [],
            "event_keys": [],
            "world_news_keys": [
                f"tv_engineering_department.600.d_{wonder['key']}",
            ],
        },
        "implementation_notes": {
            "source_ritual_key": ritual_key,
            "implementation_source": "none",
            "verification_status": "needs_design",
            "verified_interfaces": [],
            "needs_verification": ["full_ritual_design", "node_graph", "ui_model", "event_ids"],
        },
    }


def _event_key(event_id: int, key: str, *, has_decline: bool = False) -> dict[str, Any]:
    option_keys = [f"tv_engineering_department.{event_id}.a"]
    if has_decline:
        option_keys.append(f"tv_engineering_department.{event_id}.b")
    return {
        "event_id": event_id,
        "title_key": f"tv_engineering_department.{event_id}.t",
        "desc_key": f"tv_engineering_department.{event_id}.d",
        "option_keys": option_keys,
        "node_key": key,
    }


def pharos_design_ir() -> dict[str, Any]:
    routes = [
        {"key": "constantinople", "display_name": "Constantinople", "route_id": 1},
        {"key": "venice", "display_name": "Venice", "route_id": 2},
        {"key": "genoa", "display_name": "Genoa", "route_id": 3},
        {"key": "malta", "display_name": "Malta", "route_id": 4},
        {"key": "tunis", "display_name": "Tunis", "route_id": 5},
        {"key": "palermo", "display_name": "Palermo", "route_id": 6},
        {"key": "candia", "display_name": "Candia", "route_id": 7},
        {"key": "gibraltar", "display_name": "Gibraltar", "route_id": 8},
    ]
    return {
        "compiler_primitives": [
            "alexandria_hostile_privateer_clearance",
            "mediterranean_named_route_set",
            "route_map_scope_feedback",
            "per_route_status_projection",
            "active_route_selection",
            "controlled_route_pass",
            "basing_route_pass",
            "foreign_harbor_bargain",
            "privateer_threat_progress",
            "route_progress_counter",
            "repeated_route_ui_rows",
            "incident_log_progress_track_projection",
            "source_compiler_route_row_generation",
        ],
        "phases": [
            {
                "key": "clear_alexandria_privateers",
                "gameplay_stage": "Harbor security before the light can be trusted.",
                "entry_condition": "Pharos ritual annex has finished and hostile privateers threaten Alexandria.",
                "exit_condition": "Privateer threat progress is cleared through costed player options.",
            },
            {
                "key": "certify_mediterranean_routes",
                "gameplay_stage": "Monthly route audit rolls pending named routes until all eight lanes pass.",
                "entry_condition": "Stage 2 begins after Alexandria clearance.",
                "exit_condition": "Every route is controlled or accepted through basing/foreign harbor bargain.",
            },
            {
                "key": "eighth_light_completion",
                "gameplay_stage": "Final route count proves the Pharos as a Mediterranean navigation system.",
                "entry_condition": "Route progress reaches eight certified routes.",
                "exit_condition": "Existing ritual completion event dispatches the implemented reward.",
            },
        ],
        "player_proofs": [
            "Prove Alexandria's harbor light cannot be suppressed by hostile privateers.",
            "Prove the lighthouse can guide or negotiate access across eight named Mediterranean routes.",
            "Prove each route individually through control, reciprocal fleet basing, or a foreign harbor bargain.",
        ],
        "tracked_entity_sets": [
            {
                "key": "mediterranean_routes",
                "entity_type": "route",
                "entities": routes,
                "state_values": ["pending", "controlled", "basing", "unresolved"],
                "per_entity_state": {
                    "status_variable_pattern": "tv_wonder_pharos_route_<route_key>_status",
                    "passed_variable_pattern": "tv_wonder_pharos_route_<route_key>_passed",
                    "location_variable_pattern": "tv_wonder_pharos_route_<route_key>_location",
                    "owner_variable_pattern": "tv_wonder_pharos_route_<route_key>_owner",
                },
                "selector": "tv_wonder_pharos_roll_route_effect chooses one pending route and writes tv_wonder_pharos_active_route.",
                "ui_binding": "route_map:mediterranean_routes renders one repeated row per route with owner and controlled/basing/unresolved status.",
            }
        ],
        "selectors": [
            {
                "key": "active_route_selection",
                "selection_space": "pending mediterranean_routes",
                "selection_state": "tv_wonder_pharos_active_route and tv_wonder_pharos_active_route_id",
                "resolution_events": [7305, 7306, 7307],
            }
        ],
        "risk_branches": [
            {
                "key": "privateer_clearance_cost",
                "risk": "Hostile privateers force gold, prestige, or burgher-satisfaction costs before route certification can begin.",
                "player_response": "Pay for watch boats, take a prestige hit, or lean on merchants.",
            },
            {
                "key": "foreign_harbor_bargain",
                "risk": "A selected route is neither controlled nor already covered by fleet basing.",
                "player_response": "Pay for reciprocal basing or leave the route unresolved for a later roll.",
            },
        ],
        "player_actions": [
            "Choose how to clear Alexandria privateers in events 7301-7303.",
            "Accept controlled route passes in event 7305.",
            "Accept existing basing route passes in event 7306.",
            "Pay for a foreign harbor bargain in event 7307.",
        ],
        "map_scope_evidence": [
            "Alexandria sea_zone area scans hostile privateers.",
            "Route locations are concrete location scopes: Constantinople, Venice, Genoa, Malta, Tunis, Palermo, Candia, Gibraltar.",
            "Per-route owner scopes project into UI rows and foreign harbor bargain event scopes.",
            "Controlled routes use ownership; basing routes use reciprocal fleet-basing relation checks.",
        ],
        "ui_feedback_model": {
            "components": ["progress_track", "route_map"],
            "privateer_threat": "Circular progress track bound to tv_wonder_pharos_privateer_threat_pct.",
            "route_progress": "Circular progress track bound to tv_wonder_pharos_route_progress out of eight.",
            "repeated_rows": "Eight fixed route rows show location, owner, and controlled/basing/unresolved status.",
            "incident_log": "The current event chain acts as the incident log through privateer and foreign harbor events.",
        },
        "uniqueness_constraints": [
            "The ritual depends on Alexandria as a lighthouse whose value is visual trust across sea lanes.",
            "The eight Mediterranean routes make navigation visibility the proof; ordinary ports cannot reuse this without losing the Pharos claim.",
            "The controlled/basing/foreign-bargain branch ties diplomacy and naval logistics to the light itself.",
        ],
        "projection_notes": (
            "The current node_graph is an existing_plugin_parity projection. It preserves the manual implementation evidence "
            "and event IDs but compresses per-route rows, route selector state, controlled/basing route passes, and the foreign "
            "harbor bargain into lightweight event nodes rather than a full source-codegen-ready graph."
        ),
    }


def pharos_compiler_gap_ledger() -> list[dict[str, Any]]:
    no_search = ["No remaining codebase search for this primitive; manual implementation evidence is listed below."]
    return [
        {
            "primitive": "alexandria_hostile_privateer_clearance",
            "design_semantics": "Clear hostile privateer pressure around Alexandria before the lighthouse can certify routes.",
            "required_game_interfaces": ["sea_zone area privateer scan", "privateer power mutation", "monthly delayed event"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_triggers emits tv_wonder_pharos_alexandria_hostile_privateers_trigger and tv_wonder_pharos_alexandria_hostile_privateers_at_least_<count>_trigger with any_privateer_in_area",
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_effects emits tv_wonder_pharos_clear_privateers_effect with every_privateer_in_area and change_privateer_power = -0.4",
                "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event ids 7301-7303 call tv_wonder_pharos_clear_privateers_effect; 7304 calls tv_wonder_pharos_enter_stage_2_effect",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Keep the manual privateer-clearance event chain as the authoritative implementation.",
        },
        {
            "primitive": "mediterranean_named_route_set",
            "design_semantics": "Track eight named Mediterranean routes as distinct certifiable entities.",
            "required_game_interfaces": ["fixed location scopes", "per-route variable projection"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:PHAROS_ROUTE_KEYS defines constantinople, venice, genoa, malta, tunis, palermo, candia, and gibraltar",
                "scripts/wonder_unique_rituals/pharos.py:PHAROS_ROUTE_IDS assigns stable route ids 1-8 for tv_wonder_pharos_active_route",
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_triggers emits per-route triggers for every PHAROS_ROUTE_KEYS entry",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Keep the route set as authored data in the manual Pharos plugin.",
        },
        {
            "primitive": "route_map_scope_feedback",
            "design_semantics": "Show route-map or equivalent map/scope feedback for each named route's location and owner.",
            "required_game_interfaces": ["GUI scope variables", "location display", "owner country display", "route_map-style UI"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:pharos_route_row reads tv_wonder_pharos_route_<route>_location and tv_wonder_pharos_route_<route>_owner",
                "scripts/wonder_unique_rituals/pharos.py:pharos_stage_2_card loops PHAROS_ROUTE_KEYS and appends pharos_route_row for every route",
                "src/in_game/gui/panels/organization/tv_engineering_department.gui:Pharos generated rows call GetLocation.GetName and GetCountry.GetNameWithFlag from route variables",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Use route_map summary text only as a projection and keep per-route scope feedback in design_ir.",
        },
        {
            "primitive": "per_route_status_projection",
            "design_semantics": "Expose pending, controlled, basing, and unresolved state per route.",
            "required_game_interfaces": ["country variables", "location owner projection", "GUI variable reads"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_set_route_projection_lines writes tv_wonder_pharos_route_<route>_location, _owner, and _status",
                "scripts/wonder_unique_rituals/pharos.py:pharos_status_visible reads tv_wonder_pharos_route_<route>_status in GUI visibility expressions",
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_selected_route_completion_lines writes tv_wonder_pharos_route_<route>_passed for completed rows",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Summarize route progress while preserving the high-fidelity route set in design_ir.",
        },
        {
            "primitive": "active_route_selection",
            "design_semantics": "Select one pending route at a time and save active route/location/owner state for events.",
            "required_game_interfaces": ["random_list trigger filters", "saved route variables", "monthly event scheduling"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_roll_route_effect uses random_list branches filtered by tv_wonder_pharos_route_<route>_pending_trigger",
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_select_route_lines writes tv_wonder_pharos_active_route, tv_wonder_pharos_active_route_id, tv_wonder_pharos_event_route_location, and tv_wonder_pharos_event_route_owner",
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_evaluate_selected_route_effect dispatches selected routes to event ids 7305, 7306, or 7307",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Retain the manual selector and do not flatten routes into a single anonymous progress gate.",
        },
        {
            "primitive": "controlled_route_pass",
            "design_semantics": "A route passes immediately when the builder controls the route location.",
            "required_game_interfaces": ["owns = location:<route>", "route passed variable"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_triggers emits tv_wonder_pharos_route_<route>_controlled_trigger with owns = location:<route>",
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_complete_selected_controlled_route_effect sets tv_wonder_pharos_active_route_status = 1",
                "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event id 7305 calls tv_wonder_pharos_complete_selected_controlled_route_effect",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Record controlled pass as a semantic design primitive until source compiler support exists.",
        },
        {
            "primitive": "basing_route_pass",
            "design_semantics": "A route passes when the foreign owner already has reciprocal fleet basing with the builder.",
            "required_game_interfaces": ["fleet basing relation trigger", "route passed variable"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:append_pharos_triggers emits tv_wonder_pharos_route_<route>_basing_trigger with gives_fleet_basing_rights_to and receives_fleet_basing_rights_from",
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_complete_selected_basing_route_effect sets tv_wonder_pharos_active_route_status = 2",
                "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event id 7306 calls tv_wonder_pharos_complete_selected_basing_route_effect",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Preserve basing as a ledger primitive rather than replacing it with generic route progress.",
        },
        {
            "primitive": "foreign_harbor_bargain",
            "design_semantics": "If a foreign route has an owner but no qualifying basing, the player can pay to create reciprocal basing.",
            "required_game_interfaces": ["route owner scope", "create_relation fleet_basing_rights", "costed event option"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_evaluate_selected_route_effect dispatches owned foreign route scopes to event id 7307 when no control or basing pass exists",
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_create_selected_route_basing_effect creates bidirectional relation_type:fleet_basing_rights with scope:tv_wonder_pharos_event_route_owner",
                "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event id 7307 charges change_gold_effect and calls tv_wonder_pharos_create_selected_route_basing_effect",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Leave the route unresolved and retry later while keeping the bargain in design_ir.",
        },
        {
            "primitive": "privateer_threat_progress",
            "design_semantics": "Project hostile privateer count into a visible threat percentage.",
            "required_game_interfaces": ["counted privateer triggers", "progress_track GUI"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_refresh_threat_effect writes tv_wonder_pharos_privateer_threat_pct from hostile privateer count thresholds",
                "scripts/wonder_unique_rituals/pharos.py:pharos_stage_1_card renders pharos_piechart bound to tv_wonder_pharos_privateer_threat_pct",
                "scripts/wonder_unique_rituals/pharos.py:events 7301-7303 clear privateers and refresh display before event 7304 enters route stage",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Keep the visible stage text but do not remove the privateer proof from design_ir.",
        },
        {
            "primitive": "route_progress_counter",
            "design_semantics": "Count certified routes from zero to eight and fire the final light event at completion.",
            "required_game_interfaces": ["per-route passed variables", "clamped counter", "completion event"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_refresh_route_progress_effect counts tv_wonder_pharos_route_<route>_passed and clamps tv_wonder_pharos_route_progress to 0-8",
                "scripts/wonder_unique_rituals/pharos.py:tv_wonder_pharos_maybe_finish_routes_effect checks tv_wonder_pharos_route_progress >= PHAROS_ROUTE_COUNT and schedules event id 7308",
                "scripts/wonder_unique_rituals/pharos.py:pharos_stage_2_card renders pharos_piechart and x/8 raw_text from tv_wonder_pharos_route_progress",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Use a summary progress counter only as projection, never as replacement for tracked routes.",
        },
        {
            "primitive": "repeated_route_ui_rows",
            "design_semantics": "Render one route-map row per Mediterranean route with location, owner, and status.",
            "required_game_interfaces": ["fixed GUI rows", "location and owner variable projection", "status localization"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:pharos_route_row builds one fixed-height row with route location, owner, and Control/Basing/Unheld status labels",
                "scripts/wonder_unique_rituals/pharos.py:pharos_stage_2_card iterates PHAROS_ROUTE_KEYS and emits eight pharos_route_row blocks",
                "src/in_game/gui/panels/organization/tv_engineering_department.gui:generated Pharos block contains per-route rows for constantinople, venice, genoa, malta, tunis, palermo, candia, and gibraltar",
            ],
            "verification_status": "verified_existing",
            "search_questions": no_search,
            "blocked_by": [],
            "fallback_if_unavailable": "Use route_map summary plus projection_notes until repeated-row source codegen exists.",
        },
        {
            "primitive": "incident_log_progress_track_projection",
            "design_semantics": "Combine visible progress tracks with event-chain incident history for privateer and foreign-harbor route incidents.",
            "required_game_interfaces": ["progress_track GUI", "event-chain incident projection", "stage text localization"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py:pharos_stage_1_card and pharos_stage_2_card render separate progress piecharts for threat and route count",
                "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event ids 7301-7303 and 7307 provide the incident-like player-facing choices",
                "data/unique_wonder_ritual_specs.yaml:design_ir.ui_feedback_model records incident_log as current event-chain projection rather than a generated source UI component",
            ],
            "verification_status": "interface_candidate",
            "search_questions": [
                "Should the source compiler model event-chain incident history as a first-class incident_log UI binding or leave it as projection_notes?",
                "Which Harness projection rule should connect multiple progress_track widgets to incident event rows without flattening either axis?",
            ],
            "blocked_by": ["No source compiler or Harness UI generator owns combined incident_log plus progress_track projection yet."],
            "fallback_if_unavailable": "Keep Pharos event-chain incidents and progress tracks as manual projection evidence without claiming backend readiness.",
        },
        {
            "primitive": "source_compiler_route_row_generation",
            "design_semantics": "Future source compiler should generate per-route state, selectors, and repeated UI rows from design_ir.",
            "required_game_interfaces": ["source compiler route-set expansion", "GUI row generation", "event/effect generation"],
            "codebase_evidence": [
                "scripts/wonder_unique_rituals/pharos.py provides existing manual generation patterns for route rows, selectors, triggers, and effects",
                "data/unique_wonder_ritual_codegen_templates.yaml has no source-writing route-row expansion template; all v1 templates are intermediate-only",
                "data/unique_wonder_ritual_capabilities.yaml:route_gate documents route semantics but may_write_src is false",
            ],
            "verification_status": "needs_codebase_search",
            "search_questions": [
                "Which existing generator owns repeated Engineering Department ritual UI row expansion?",
                "Can the future source compiler emit per-route trigger/effect families without exceeding event-id limits?",
            ],
            "blocked_by": ["No source compiler is in scope for this round."],
            "fallback_if_unavailable": "Keep Pharos manual implementation and emit only high-fidelity design/projection metadata.",
        },
    ]


def pharos_spec(wonder: dict[str, Any]) -> dict[str, Any]:
    event_ids = [
        (7300, "annex_finished", False),
        (7301, "silver_for_watch_boats", True),
        (7302, "names_read_from_quay", True),
        (7303, "merchants_night_watch", True),
        (7304, "privateers_cleared", False),
        (7305, "controlled_route_passes", False),
        (7306, "basing_route_passes", False),
        (7307, "foreign_harbor_bargain", False),
        (7308, "eighth_light", False),
    ]
    return {
        "identity": base_identity(wonder, "implemented_parity"),
        "event_ids": [{"id": event_id, "key": key} for event_id, key, _decline in event_ids],
        "node_graph": {
            "model": "existing_plugin_parity",
            "historical_mechanic": "Mediterranean harbor-lighting network and pilotage oath.",
            "listeners": ["monthly"],
            "summary": (
                "The Pharos ritual first clears hostile privateers from Alexandria, then audits "
                "eight named Mediterranean harbor routes until every route is controlled or has "
                "friendly basing access."
            ),
            "runtime_variables": [
                "tv_wonder_pharos_stage",
                "tv_wonder_pharos_quarter_month",
                "tv_wonder_pharos_route_progress",
                "tv_wonder_pharos_privateer_threat_pct",
                "tv_wonder_pharos_active_route",
                "tv_wonder_pharos_routes_complete",
            ],
            "nodes": [
                {
                    "key": key,
                    "event_id": event_id,
                    "player_visible": True,
                    "type": "event",
                    "historical_anchor": key,
                    "decision_or_check": "choice" if decline else "check",
                    "failure_or_retry": decline,
                }
                for event_id, key, decline in event_ids
            ],
        },
        "design_ir": pharos_design_ir(),
        "compiler_gap_ledger": pharos_compiler_gap_ledger(),
        "ui_model": {
            "components": [
                {"type": "progress_track", "key": "privateer_threat", "value_variable": "tv_wonder_pharos_privateer_threat_pct"},
                {"type": "route_map", "key": "mediterranean_routes", "value_variable": "tv_wonder_pharos_route_progress"},
            ]
        },
        "rewards": {
            "permanent_country_modifier": {
                "status": "implemented",
                "source": "data/unique_wonders.yaml ritual.country_modifier",
                "description": "Naval and trade range from the completed Pharos ceremony modifier.",
            },
            "local_building_reward": {
                "status": "implemented",
                "source": "tv_wonder_unique_pharos_lighthouse_ritual_annex",
                "description": "Pilotage annex with harbor suitability and maritime presence effects.",
            },
            "one_time_reward": {
                "status": "implemented",
                "source": "stage transition and final route events",
                "description": "Prestige, gold, and route/basing outcomes during the harbor-lighting chain.",
            },
        },
        "localization": {
            "panel_text_keys": [
                "TV_ENGINEERING_PHAROS_STAGE_1_TEXT",
                "TV_ENGINEERING_PHAROS_STAGE_2_TEXT",
            ],
            "event_keys": [_event_key(event_id, key, has_decline=decline) for event_id, key, decline in event_ids],
            "world_news_keys": [f"tv_engineering_department.600.d_{wonder['key']}"],
        },
        "implementation_notes": {
            "source_ritual_key": "harbor_lighting_and_pilotage_oath",
            "implementation_source": "scripts/wonder_unique_rituals/pharos.py + scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py",
            "verification_status": "verified_existing",
            "verified_interfaces": [
                "monthly listener",
                "route status projection",
                "monthly delayed events",
                "special Engineering Department GUI cards",
            ],
            "needs_verification": [],
        },
    }


def hagia_spec(wonder: dict[str, Any]) -> dict[str, Any]:
    event_ids = [(6300 + step, f"synaxis_step_{step}", step in {1, 2, 3, 6, 7}) for step in range(1, 9)]
    return {
        "identity": base_identity(wonder, "implemented_parity"),
        "event_ids": [{"id": event_id, "key": key} for event_id, key, _decline in event_ids],
        "node_graph": {
            "model": "existing_plugin_parity",
            "historical_mechanic": "Eight office-and-procession steps for the Great Church synaxis.",
            "listeners": ["monthly"],
            "summary": (
                "Hagia Sophia assigns characters to eight sequential offices, waits three months "
                "per active assignment, resolves step events with costs or retries, then completes "
                "after a public procession and Constantinople prosperity check."
            ),
            "runtime_variables": [
                "tv_wonder_hagia_step",
                "tv_wonder_hagia_months",
                "tv_wonder_hagia_pending_event",
                "tv_wonder_hagia_completed",
                "tv_wonder_hagia_prosperity_active",
            ],
            "nodes": [
                {
                    "key": key,
                    "event_id": event_id,
                    "player_visible": True,
                    "type": "actor_slot_event",
                    "historical_anchor": key,
                    "decision_or_check": "choice" if decline else "assignment_check",
                    "failure_or_retry": decline,
                }
                for event_id, key, decline in event_ids
            ],
        },
        "ui_model": {
            "components": [
                {"type": "actor_slots", "key": "synaxis_offices", "count": 8},
                {"type": "progress_track", "key": "three_month_wait", "value_variable": "tv_wonder_hagia_months"},
            ]
        },
        "rewards": {
            "permanent_country_modifier": {
                "status": "implemented",
                "source": "data/unique_wonders.yaml ritual.country_modifier and step modifiers",
                "description": "Tolerance and stability investment plus permanent procession/endowment effects.",
            },
            "local_building_reward": {
                "status": "implemented",
                "source": "Hagia sanctuary/procession local effects",
                "description": "Local sanctuary/procession state represented by the existing Hagia plugin effects.",
            },
            "one_time_reward": {
                "status": "implemented",
                "source": "step event costs and completion effects",
                "description": "Prestige, gold, art, prosperity, privilege, and character assignment outcomes.",
            },
        },
        "localization": {
            "panel_text_keys": [f"TV_ENGINEERING_HAGIA_STEP_{step}_ACTIVE" for step in range(1, 9)],
            "event_keys": [_event_key(event_id, key, has_decline=decline) for event_id, key, decline in event_ids],
            "world_news_keys": [f"tv_engineering_department.600.d_{wonder['key']}"],
        },
        "implementation_notes": {
            "source_ritual_key": "justinianic_synaxis_of_the_great_church",
            "implementation_source": "scripts/wonder_unique_rituals/hagia.py + scripts/in_game/events/gen_tv_wonder_unique_hagia_sophia_ritual_events.py",
            "verification_status": "verified_existing",
            "verified_interfaces": [
                "monthly listener",
                "character assignment action slots",
                "monthly delayed events",
                "special Engineering Department GUI cards",
            ],
            "needs_verification": [],
        },
    }


def default_spec_for_wonder(wonder: dict[str, Any]) -> dict[str, Any]:
    if wonder["key"] == "unique_pharos_lighthouse":
        return pharos_spec(wonder)
    if wonder["key"] == "unique_hagia_sophia":
        return hagia_spec(wonder)
    return stub_spec(wonder)


def design_harness_spec_index(designs: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    payload = designs if designs is not None else load_optional_yaml(DESIGN_FILE)
    specs: dict[str, dict[str, Any]] = {}
    if not isinstance(payload, dict):
        return specs
    for key, entry in list_index(payload).items():
        harness_spec = entry.get("harness_spec") if isinstance(entry, dict) else None
        if isinstance(harness_spec, dict):
            specs[key] = harness_spec
    return specs


def _spec_entry_status(entry: dict[str, Any]) -> str:
    identity = entry.get("identity")
    if isinstance(identity, dict) and identity.get("status"):
        return str(identity["status"])
    if entry.get("status"):
        return str(entry["status"])
    return "stub"


def design_placeholder_block(wonder: dict[str, Any]) -> str:
    ritual_key = str((wonder.get("ritual") or {}).get("key") or "ritual")
    title = ritual_key.replace("_", " ").title()
    return f"""  - id: {int(wonder["id"])}
    key: {wonder["key"]}
    base_key: {wonder["base_key"]}
    location: {wonder["location"]}
    source_ritual_key: {ritual_key}
    status: needs_design
    ritual_design:
      title: "{title}"
      historical_flavor: >
        Placeholder design entry for {wonder["key"]}. This unique wonder was added
        after the first design pass and must receive a full playable ritual
        design before implementation.
      mode: custom_node_graph
      duration: >
        To be authored through data/unique_wonder_ritual_specs.yaml using
        the unique ritual Harness quality gates.
      listeners: []
      confirmation_logic: >
        To be authored. Must include ownership/control of the fixed site,
        final unique wonder building presence, solvency, and any historical
        hard gates required by the ritual theme.
      start_logic: >
        To be authored as a playable opening state, not a one-click completion.
      progress_logic: >
        To be authored with visible player-facing state, event cadence,
        decision points, and at least one theme-specific mechanic.
      completion_logic: >
        To be authored with the permanent country modifier, local reward
        building, and one-time reward channels assigned explicitly.
      failure_or_timeout_logic: >
        To be authored with failure, retry, or restart behavior for the
        current ritual step.
      implementation_mapping:
        confirmation_trigger_script: needs_verification
        start_effect_script: needs_verification
        snapshot_effect_script: needs_verification
        progress_effect_script: needs_verification
        completion_trigger_script: needs_verification
        completion_effect_script: needs_verification
      intended_rewards:
        permanent_country_modifier: >
          To be authored from this wonder's existing country modifier theme.
        local_building_reward: >
          To be authored as a unique local reward building at the fixed site.
        one_time_reward: >
          To be authored from the approved one-time reward catalog.
      notes: >
        Placeholder only. The audit script should treat this as design debt
        until the entry is expanded into a concrete ritual design.
"""


def append_missing_design_placeholders() -> list[str]:
    wonders = load_unique_wonders()
    designs = load_optional_yaml(DESIGN_FILE)
    existing = set(list_index(designs))
    missing = [wonder for wonder in wonders if str(wonder["key"]) not in existing]
    if not missing:
        return []
    current = DESIGN_FILE.read_text(encoding="utf-8")
    separator = "" if current.endswith("\n") else "\n"
    block = "\n".join(design_placeholder_block(wonder).rstrip() for wonder in missing)
    DESIGN_FILE.write_text(current + separator + block + "\n", encoding="utf-8")
    return [str(wonder["key"]) for wonder in missing]


def build_spec_payload(existing: dict[str, Any] | None = None) -> dict[str, Any]:
    wonders = load_unique_wonders()
    existing_by_key = list_index(existing or {})
    design_specs_by_key = design_harness_spec_index()
    entries = []
    for wonder in wonders:
        key = str(wonder["key"])
        default_entry = default_spec_for_wonder(wonder)
        design_entry = design_specs_by_key.get(key)
        existing_entry = deepcopy(existing_by_key[key]) if key in existing_by_key else None
        if existing_entry is None:
            entry = deepcopy(design_entry) if design_entry is not None else deepcopy(default_entry)
        elif design_entry is not None and _spec_entry_status(existing_entry) in STUB_STATUSES:
            entry = deepcopy(design_entry)
        else:
            entry = existing_entry
        if isinstance(entry.get("node_graph"), dict):
            entry["node_graph"].setdefault("listeners", (default_entry.get("node_graph") or {}).get("listeners", []))
        entry["identity"] = {**base_identity(wonder, entry.get("identity", {}).get("status", "stub")), **entry.get("identity", {})}
        entry["identity"]["id"] = int(wonder["id"])
        entry["identity"]["key"] = key
        entry["identity"]["base_key"] = str(wonder["base_key"])
        entry["identity"]["location"] = str(wonder["location"])
        entry["identity"].setdefault("runtime_prefix", runtime_prefix_for_wonder(wonder))
        entries.append(entry)
    return {
        "metadata": {
            "purpose": "Executable planning source for unique wonder ritual implementation.",
            "source_data": "data/unique_wonders.yaml",
            "generated_by": "scripts/gen_unique_wonder_ritual_specs.py",
            "generated_game_code": False,
            "status_policy": {
                "stub": "Coverage placeholder only; cannot be generated into game code.",
                "needs_design": "Design debt placeholder from the design source.",
                "implemented_parity": "Spec mirrors an already implemented custom ritual.",
                "design_complete": "High-fidelity design_ir is complete; compiler gaps may remain.",
                "compiler_mapped": "High-fidelity design has a Harness node_graph projection that passes semantic graph validation.",
                "evidence_verified": "Key design primitives have codebase evidence; this is not a source-codegen guarantee.",
                "source_codegen_ready": "Spec has no unresolved compiler gaps and passes source codegen readiness gates.",
                "implementation_ready": "Legacy alias for source_codegen_ready; do not use as a design-complete status.",
                "harness_generated": "Generated implementation is owned by the Harness node-graph generator.",
            },
            "quality_contract": {
                "minimum_player_visible_nodes": 3,
                "minimum_event_count": 3,
                "design_ir_statuses": list(sorted(DESIGN_IR_REQUIRED_STATUSES)),
                "semantic_graph_statuses": list(sorted(SEMANTIC_GRAPH_STATUSES)),
                "source_codegen_statuses": list(sorted(CODEGEN_ELIGIBLE_STATUSES)),
                "allowed_compiler_gap_verification_statuses": list(sorted(COMPILER_GAP_VERIFICATION_STATUSES)),
                "unresolved_compiler_gap_statuses": list(sorted(UNRESOLVED_COMPILER_GAP_STATUSES)),
                "required_design_ir_fields": list(sorted(DESIGN_IR_REQUIRED_FIELDS)),
                "required_tracked_entity_set_fields": list(sorted(TRACKED_ENTITY_SET_REQUIRED_FIELDS)),
                "required_compiler_gap_fields": list(sorted(COMPILER_GAP_REQUIRED_FIELDS)),
                "required_reward_channels": list(REQUIRED_REWARD_CHANNELS),
                "required_mechanic_signature_fields": list(sorted(MECHANIC_SIGNATURE_REQUIRED_FIELDS)),
                "required_cadence_signature_fields": list(sorted(CADENCE_SIGNATURE_REQUIRED_FIELDS)),
                "supported_cadence_types": list(sorted(SUPPORTED_CADENCE_TYPES)),
                "custom_archetype_prefix": CUSTOM_ARCHETYPE_PREFIX,
                "required_ui_components": list(sorted(SUPPORTED_UI_COMPONENTS)),
                "event_id_rule": "Every declared event id must be explicit, unique within this file, and < 10000; every node.event_id must be unique within its spec.",
                "state_machine_dsl_statuses": list(sorted(SEMANTIC_GRAPH_STATUSES)),
                "supported_node_kinds": list(sorted(SUPPORTED_NODE_KINDS)),
                "supported_action_kinds": list(sorted(SUPPORTED_ACTION_KINDS)),
                "supported_check_kinds": list(sorted(SUPPORTED_CHECK_KINDS)),
                "supported_codegen_templates": list(sorted(supported_codegen_template_keys())),
                "supported_capabilities": list(sorted(supported_capability_keys())),
                "supported_archetypes": list(sorted(supported_archetype_keys())),
                "archetype_policy": (
                    "Registry archetypes are optional, non-exclusive reference tags. "
                    "They add contract checks when used, but custom_* archetype labels are allowed "
                    "when mechanic_signature.custom_archetype_statement explains the new shape."
                ),
                "cadence_policy": (
                    "Implementation-ready specs must declare cadence_signature. Monthly listeners, "
                    "monthly_progress_gate nodes, monthly_progress capabilities, or monthly_progress_gate "
                    "templates require monthly_institutionalization or hybrid cadence with a concrete "
                    "historical rationale and at least one non-monthly player interaction, risk, listener, "
                    "event branch, trigger, or decision point."
                ),
                "supported_scope_contract_scopes": list(sorted(SUPPORTED_SCOPE_CONTRACT_SCOPES)),
            },
            "ai_prompt_contract": {
                "batch_size": "1-5 unique wonders per authoring pass",
                "required_output_sections": [
                    "mechanic_signature",
                    "cadence_signature",
                    "gameplay_loop_summary",
                    "node_table",
                    "state_variable_table",
                    "event_text_inventory",
                    "reward_table",
                    "risk_verification_checklist",
                ],
                "handoff_rule": "AI must write or update structured specs first; game code generation is allowed only after the spec passes Harness validation.",
            },
        },
        "unique_wonders": entries,
    }


def event_ids_in_entry(entry: dict[str, Any]) -> list[int]:
    ids = []
    for raw in entry.get("event_ids", []) or []:
        if isinstance(raw, dict) and "id" in raw:
            ids.append(int(raw["id"]))
        elif isinstance(raw, int):
            ids.append(raw)
    return ids


def collect_occupied_engineering_event_ids(root: Path = REPO_ROOT) -> set[int]:
    roots = [
        root / "src" / "in_game",
        root / "scripts" / "in_game",
        root / "scripts" / "wonder_unique_rituals",
        root / "data" / "wonder_localization.yaml",
    ]
    ids: set[int] = set()
    for base in roots:
        paths = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in paths:
            if not path.is_file() or path.suffix not in {".txt", ".py", ".yml", ".yaml"}:
                continue
            try:
                text = path.read_text(encoding="utf-8-sig", errors="replace")
            except OSError:
                continue
            ids.update(int(match.group(1)) for match in EVENT_ID_PATTERN.finditer(text))
    return ids


def allocate_event_ids(count: int, occupied: set[int], *, start: int = 1000, end: int = 4999) -> list[int]:
    if count < 1:
        return []
    free = [event_id for event_id in range(start, end + 1) if event_id not in occupied]
    if len(free) < count:
        raise ValueError(f"Only {len(free)} free event ids in {start}-{end}, need {count}")
    return free[:count]


def _issue(entry: dict[str, Any], message: str) -> str:
    identity = entry.get("identity", {})
    key = identity.get("key", "<unknown>")
    return f"{key}: {message}"


def _is_custom_archetype(archetype: str) -> bool:
    return archetype.startswith(CUSTOM_ARCHETYPE_PREFIX) and len(archetype) > len(CUSTOM_ARCHETYPE_PREFIX)


def _mechanic_signature_text(signature: dict[str, Any]) -> str:
    values = [signature.get(field, "") for field in sorted(MECHANIC_SIGNATURE_REQUIRED_FIELDS)]
    if signature.get("custom_archetype_statement"):
        values.append(signature["custom_archetype_statement"])
    return " ".join(str(value).strip() for value in values if str(value).strip())


def _mechanic_signature_errors(
    entry: dict[str, Any],
    node_graph: dict[str, Any],
    *,
    archetype_registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    signature = node_graph.get("mechanic_signature")
    if not isinstance(signature, dict):
        return [_issue(entry, "node_graph.mechanic_signature is required for implementation_ready or harness_generated specs")]

    for field in sorted(MECHANIC_SIGNATURE_REQUIRED_FIELDS):
        value = signature.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(_issue(entry, f"node_graph.mechanic_signature.{field} is required"))
            continue
        if len(value.strip()) < MECHANIC_SIGNATURE_MIN_FIELD_CHARS:
            errors.append(
                _issue(
                    entry,
                    f"node_graph.mechanic_signature.{field} is too thin; describe the wonder-specific design intent",
                )
            )

    text = _mechanic_signature_text(signature)
    if len(text) < MECHANIC_SIGNATURE_MIN_TOTAL_CHARS:
        errors.append(_issue(entry, "node_graph.mechanic_signature is too thin; define a distinctive ritual loop before codegen"))
    lowered = text.lower()
    for token in sorted(MECHANIC_SIGNATURE_PLACEHOLDER_TOKENS):
        if token in lowered:
            errors.append(_issue(entry, f"node_graph.mechanic_signature cannot contain placeholder token {token!r}"))

    archetype_index = archetype_registry_index(archetype_registry)
    custom_archetypes = [
        archetype
        for archetype in _string_refs(node_graph.get("archetypes"))
        if archetype not in archetype_index and _is_custom_archetype(archetype)
    ]
    if custom_archetypes:
        custom_statement = signature.get("custom_archetype_statement")
        if not isinstance(custom_statement, str) or len(custom_statement.strip()) < MECHANIC_SIGNATURE_MIN_FIELD_CHARS:
            errors.append(
                _issue(
                    entry,
                    "custom archetype(s) require node_graph.mechanic_signature.custom_archetype_statement",
                )
            )
    return errors


def _cadence_signature_text(signature: dict[str, Any]) -> str:
    values = [
        signature.get(field, "")
        for field in sorted(CADENCE_SIGNATURE_REQUIRED_FIELDS - {"cadence_type"})
    ]
    return " ".join(str(value).strip() for value in values if str(value).strip())


def _node_graph_uses_monthly_cadence(entry: dict[str, Any], node_graph: dict[str, Any]) -> bool:
    if "monthly" in _string_refs(node_graph.get("listeners")):
        return True
    for node in node_graph.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        if node.get("kind") == "monthly_progress_gate":
            return True
        if "monthly_progress" in _string_refs(node.get("capabilities")):
            return True
        listener_contract = node.get("listener_contract")
        if isinstance(listener_contract, dict):
            if "monthly" in _string_refs(listener_contract.get("listener")):
                return True
            if "month" in str(listener_contract.get("cadence", "")).lower():
                return True
    return "monthly_progress_gate" in templates_used_by_entry(entry)


def _has_non_monthly_interaction(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < CADENCE_NON_MONTHLY_MIN_CHARS:
        return False
    lowered = stripped.lower()
    if any(pattern.search(lowered) for pattern in CADENCE_NON_MONTHLY_BLOCKED_PATTERNS):
        return False
    return any(token in lowered for token in CADENCE_NON_MONTHLY_INTERACTION_TOKENS)


def _has_hybrid_monthly_local_role(text: str) -> bool:
    lowered = text.lower()
    return "month" in lowered and any(token in lowered for token in CADENCE_HYBRID_MONTHLY_LOCAL_ROLE_TOKENS)


def _cadence_signature_errors(entry: dict[str, Any], node_graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    signature = node_graph.get("cadence_signature")
    if not isinstance(signature, dict):
        return [_issue(entry, "node_graph.cadence_signature is required for implementation_ready or harness_generated specs")]

    cadence_type = signature.get("cadence_type")
    if not isinstance(cadence_type, str) or not cadence_type.strip():
        errors.append(_issue(entry, "node_graph.cadence_signature.cadence_type is required"))
        cadence_type = ""
    else:
        cadence_type = cadence_type.strip()
        if cadence_type not in SUPPORTED_CADENCE_TYPES:
            errors.append(_issue(entry, f"node_graph.cadence_signature.cadence_type unknown cadence type {cadence_type!r}"))

    for field in sorted(CADENCE_SIGNATURE_REQUIRED_FIELDS - {"cadence_type"}):
        value = signature.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(_issue(entry, f"node_graph.cadence_signature.{field} is required"))
            continue
        if len(value.strip()) < CADENCE_SIGNATURE_MIN_FIELD_CHARS:
            errors.append(
                _issue(
                    entry,
                    f"node_graph.cadence_signature.{field} is too thin; describe the ritual pacing and trigger design",
                )
            )

    text = _cadence_signature_text(signature)
    if len(text) < CADENCE_SIGNATURE_MIN_TOTAL_CHARS:
        errors.append(_issue(entry, "node_graph.cadence_signature is too thin; define a distinctive pacing model before codegen"))
    lowered = text.lower()
    for token in sorted(CADENCE_SIGNATURE_PLACEHOLDER_TOKENS):
        if token in lowered:
            errors.append(_issue(entry, f"node_graph.cadence_signature cannot contain placeholder token {token!r}"))

    uses_monthly = _node_graph_uses_monthly_cadence(entry, node_graph)
    if uses_monthly:
        if cadence_type not in {"monthly_institutionalization", "hybrid"}:
            errors.append(
                _issue(
                    entry,
                    "monthly usage requires node_graph.cadence_signature.cadence_type to be monthly_institutionalization or hybrid",
                )
            )
        rationale = str(signature.get("cadence_rationale", ""))
        if "month" not in rationale.lower():
            errors.append(
                _issue(
                    entry,
                    "monthly usage requires node_graph.cadence_signature.cadence_rationale to explicitly discuss monthly pacing",
                )
            )

    non_monthly = str(signature.get("non_monthly_triggers_or_reason", ""))
    if cadence_type == "monthly_institutionalization" and not _has_non_monthly_interaction(non_monthly):
        errors.append(
            _issue(
                entry,
                "monthly_institutionalization requires non_monthly_triggers_or_reason to describe at least one non-monthly decision point, risk point, listener, event branch, or player action",
            )
        )
    if uses_monthly and cadence_type == "hybrid":
        if not _has_non_monthly_interaction(non_monthly):
            errors.append(
                _issue(
                    entry,
                    "hybrid cadence with monthly usage requires non_monthly_triggers_or_reason to describe the non-monthly trigger, decision, risk, or branch",
                )
            )
        if not _has_hybrid_monthly_local_role(text):
            errors.append(
                _issue(
                    entry,
                    "hybrid cadence with monthly usage must explain monthly pacing as a local or supporting role",
                )
            )
    return errors


def loc_key_inventory(localization: dict[str, str] | None = None) -> set[str]:
    keys = set((localization if localization is not None else loc_english()).keys())
    global _LOCALIZATION_INDEX_KEYS_CACHE
    if _LOCALIZATION_INDEX_KEYS_CACHE is None:
        _LOCALIZATION_INDEX_KEYS_CACHE = set()
        if LOCALIZATION_INDEX_FILE.exists():
            _LOCALIZATION_INDEX_KEYS_CACHE.update(
                line.strip()
                for line in LOCALIZATION_INDEX_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
                if line.strip()
            )
    keys.update(_LOCALIZATION_INDEX_KEYS_CACHE)
    return keys


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _string_refs(value: Any) -> list[str]:
    return [str(item) for item in _as_list(value) if str(item).strip()]


def _missing_required(mapping: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(field for field in required if field not in mapping)


def _has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_has_content(item) for item in value)
    if isinstance(value, dict):
        return any(_has_content(item) for item in value.values())
    return True


def _is_status_requiring_design_ir(status: str) -> bool:
    return status in DESIGN_IR_REQUIRED_STATUSES


def _validate_design_ir(entry: dict[str, Any], *, required: bool) -> list[str]:
    errors: list[str] = []
    design_ir = entry.get("design_ir")
    if design_ir is None:
        if required:
            errors.append(_issue(entry, "design_ir is required for high-fidelity design statuses"))
        return errors
    if not isinstance(design_ir, dict):
        return [_issue(entry, "design_ir must be a mapping")]

    for field in _missing_required(design_ir, DESIGN_IR_REQUIRED_FIELDS):
        errors.append(_issue(entry, f"design_ir missing required field {field}"))
    for field in sorted(DESIGN_IR_REQUIRED_FIELDS):
        if field in design_ir and not _has_content(design_ir.get(field)):
            errors.append(_issue(entry, f"design_ir.{field} must not be empty"))

    tracked_sets = design_ir.get("tracked_entity_sets")
    if isinstance(tracked_sets, list):
        for idx, tracked in enumerate(tracked_sets, 1):
            if not isinstance(tracked, dict):
                errors.append(_issue(entry, f"design_ir.tracked_entity_sets[{idx}] must be a mapping"))
                continue
            key = tracked.get("key", f"<missing:{idx}>")
            for field in _missing_required(tracked, TRACKED_ENTITY_SET_REQUIRED_FIELDS):
                errors.append(_issue(entry, f"tracked entity set {key} missing required field {field}"))
            if not _has_content(tracked.get("state_values")):
                errors.append(_issue(entry, f"tracked entity set {key} must declare state_values"))
            if not _has_content(tracked.get("per_entity_state")):
                errors.append(_issue(entry, f"tracked entity set {key} must declare per_entity_state"))
    elif tracked_sets is not None:
        errors.append(_issue(entry, "design_ir.tracked_entity_sets must be a list"))

    compiler_primitives = _string_refs(design_ir.get("compiler_primitives"))
    if compiler_primitives:
        ledger_primitives = {
            str(row.get("primitive"))
            for row in entry.get("compiler_gap_ledger", []) or []
            if isinstance(row, dict) and row.get("primitive")
        }
        missing = sorted(set(compiler_primitives) - ledger_primitives)
        if missing:
            errors.append(
                _issue(entry, "design_ir.compiler_primitives missing compiler_gap_ledger row(s): " + ", ".join(missing))
            )

    return errors


def _ledger_evidence_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, dict):
        return [f"{key}:{child}".strip() for key, child in value.items() if str(child).strip()]
    text = str(value).strip()
    return [text] if text else []


def _is_meaningful_search_questions(value: Any) -> bool:
    questions = _string_refs(value)
    if not questions:
        return False
    empty_markers = {"none", "n/a", "na", "no", "not applicable", "already verified"}
    return any(question.strip().lower().rstrip(".") not in empty_markers for question in questions)


def _valid_backend_ready_evidence_tokens(
    row: dict[str, Any],
    *,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
) -> list[str]:
    templates = supported_codegen_template_keys(template_registry)
    capabilities = supported_capability_keys(capability_registry)
    valid: list[str] = []
    for evidence in _ledger_evidence_strings(row.get("codebase_evidence")):
        prefix, sep, key = evidence.partition(":")
        if not sep:
            continue
        prefix = prefix.strip().lower()
        key = key.strip()
        if prefix == "template" and key in templates:
            valid.append(evidence)
        elif prefix == "capability" and key in capabilities:
            valid.append(evidence)
    return valid


def _validate_compiler_gap_ledger(
    entry: dict[str, Any],
    *,
    required: bool,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    ledger = entry.get("compiler_gap_ledger")
    if ledger is None:
        if required:
            errors.append(_issue(entry, "compiler_gap_ledger is required for high-fidelity design statuses"))
        return errors
    if not isinstance(ledger, list):
        return [_issue(entry, "compiler_gap_ledger must be a list")]
    if required and not ledger:
        errors.append(_issue(entry, "compiler_gap_ledger must not be empty for high-fidelity design statuses"))
    seen: set[str] = set()
    for idx, row in enumerate(ledger, 1):
        if not isinstance(row, dict):
            errors.append(_issue(entry, f"compiler_gap_ledger[{idx}] must be a mapping"))
            continue
        primitive = str(row.get("primitive", f"<missing:{idx}>"))
        for field in _missing_required(row, COMPILER_GAP_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"compiler_gap_ledger {primitive} missing required field {field}"))
        if row.get("primitive"):
            if primitive in seen:
                errors.append(_issue(entry, f"compiler_gap_ledger duplicate primitive {primitive}"))
            seen.add(primitive)
        for field in sorted(COMPILER_GAP_REQUIRED_FIELDS - {"blocked_by", "codebase_evidence"}):
            if field in row and not _has_content(row.get(field)):
                errors.append(_issue(entry, f"compiler_gap_ledger {primitive}.{field} must not be empty"))
        status = row.get("verification_status")
        if status not in COMPILER_GAP_VERIFICATION_STATUSES:
            errors.append(_issue(entry, f"compiler_gap_ledger {primitive} has invalid verification_status {status!r}"))
            continue
        if status == "needs_codebase_search" and not _is_meaningful_search_questions(row.get("search_questions")):
            errors.append(_issue(entry, f"compiler_gap_ledger {primitive} needs_codebase_search requires meaningful search_questions"))
        if status == "verified_existing" and not _has_content(row.get("codebase_evidence")):
            errors.append(_issue(entry, f"compiler_gap_ledger {primitive} verified_existing requires codebase_evidence"))
        if status == "backend_ready" and not _valid_backend_ready_evidence_tokens(
            row,
            template_registry=template_registry,
            capability_registry=capability_registry,
        ):
            errors.append(
                _issue(
                    entry,
                    f"compiler_gap_ledger {primitive} backend_ready requires valid capability:<key> or template:<key> codebase_evidence",
                )
            )
    return errors


def unresolved_compiler_gap_rows(entry: dict[str, Any]) -> list[dict[str, Any]]:
    ledger = entry.get("compiler_gap_ledger")
    if not isinstance(ledger, list):
        return []
    return [
        row
        for row in ledger
        if isinstance(row, dict) and row.get("verification_status") in UNRESOLVED_COMPILER_GAP_STATUSES
    ]


def _dotted_path_exists(root: dict[str, Any], path: str) -> bool:
    current: Any = root
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    if current is None:
        return False
    if isinstance(current, str) and not current.strip():
        return False
    return True


def _variable_names_with_role(variables: list[Any], role: str) -> set[str]:
    names: set[str] = set()
    for variable in variables:
        if not isinstance(variable, dict) or not variable.get("name"):
            continue
        if role in set(_string_refs(variable.get("roles"))):
            names.add(str(variable["name"]))
    return names


def _has_hidden_executor_handoff(
    node: dict[str, Any],
    node_by_key: dict[str, dict[str, Any]],
) -> bool:
    if node.get("kind") == "hidden_executor_handoff":
        return True
    handoff = node.get("hidden_executor_handoff")
    if handoff is True:
        return True
    if isinstance(handoff, str) and handoff.strip():
        target = node_by_key.get(handoff)
        return bool(target and target.get("kind") == "hidden_executor_handoff")
    return False


def _loc_ref_errors(
    entry: dict[str, Any],
    context: str,
    refs: Any,
    loc_keys: set[str],
) -> list[str]:
    errors: list[str] = []
    for loc_key in _string_refs(refs):
        if loc_key not in loc_keys:
            errors.append(_issue(entry, f"{context} loc_ref {loc_key} is not present in localization inventory"))
    return errors


def _ui_state_variable_refs(ui_state: Any) -> list[str]:
    if isinstance(ui_state, dict):
        refs = _string_refs(ui_state.get("variable_refs"))
        refs.extend(_string_refs(ui_state.get("variables")))
        return refs
    if isinstance(ui_state, list):
        return _string_refs(ui_state)
    if isinstance(ui_state, str) and ui_state.strip():
        return [ui_state]
    return []


def _needs_verification_paths(value: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            found.extend(_needs_verification_paths(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            found.extend(_needs_verification_paths(child, f"{path}[{idx}]"))
    elif isinstance(value, str) and value.strip() == "needs_verification":
        found.append(path or "<root>")
    return found


def declared_runtime_variables(entry: dict[str, Any]) -> set[str]:
    identity = entry.get("identity") or {}
    status = str(identity.get("status", ""))
    node_graph = entry.get("node_graph") or {}
    if (status in SEMANTIC_GRAPH_STATUSES or status in DESIGN_IR_REQUIRED_STATUSES) and isinstance(node_graph.get("variables"), list):
        return {
            str(variable.get("name"))
            for variable in node_graph.get("variables", [])
            if isinstance(variable, dict) and variable.get("name")
        }
    return set(str(variable) for variable in node_graph.get("runtime_variables", []) or [])


def _template_errors(
    entry: dict[str, Any],
    context: str,
    template: Any,
    template_index: dict[str, dict[str, Any]],
) -> list[str]:
    if template in {None, ""}:
        return []
    template_key = str(template)
    contract = template_index.get(template_key)
    if contract is None:
        return [_issue(entry, f"{context} unknown template {template_key!r}")]
    errors: list[str] = []
    if contract.get("may_write_src") is not False:
        errors.append(_issue(entry, f"{context} template {template_key!r} is not allowed to write src"))
    return errors


def _template_kind_support_errors(
    entry: dict[str, Any],
    context: str,
    template: Any,
    field: str,
    kind: Any,
    template_index: dict[str, dict[str, Any]],
) -> list[str]:
    if template in {None, ""} or kind in {None, ""}:
        return []
    template_key = str(template)
    contract = template_index.get(template_key)
    if contract is None:
        return []
    supported = set(str(value) for value in contract.get(field, []) or [])
    if str(kind) not in supported:
        return [_issue(entry, f"{context} template {template_key!r} does not support kind {kind!r}")]
    return []


def templates_used_by_entry(entry: dict[str, Any]) -> set[str]:
    node_graph = entry.get("node_graph") or {}
    used: set[str] = set()
    for section in ("actions", "checks"):
        for item in node_graph.get(section, []) or []:
            if isinstance(item, dict) and item.get("generator_template"):
                used.add(str(item["generator_template"]))
    generation = entry.get("generation") or {}
    for template in generation.get("verified_templates", []) or []:
        used.add(str(template))
    for template in generation.get("blocked_templates", []) or []:
        used.add(str(template))
    return used


def capabilities_used_by_entry(entry: dict[str, Any]) -> set[str]:
    node_graph = entry.get("node_graph") or {}
    used: set[str] = set()
    for node in node_graph.get("nodes", []) or []:
        if isinstance(node, dict):
            used.update(_string_refs(node.get("capabilities")))
    return used


def archetypes_used_by_entry(entry: dict[str, Any]) -> set[str]:
    node_graph = entry.get("node_graph") or {}
    if not isinstance(node_graph, dict):
        return set()
    return set(_string_refs(node_graph.get("archetypes")))


def _archetype_contract_errors(
    entry: dict[str, Any],
    node_graph: dict[str, Any],
    variables: list[Any],
    *,
    archetype_registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    archetype_index = archetype_registry_index(archetype_registry)
    declared_archetypes = _string_refs(node_graph.get("archetypes"))
    if not declared_archetypes:
        return errors

    nodes = node_graph.get("nodes", [])
    nodes = nodes if isinstance(nodes, list) else []
    node_by_key = {
        str(node["key"]): node
        for node in nodes
        if isinstance(node, dict) and node.get("key")
    }
    node_count = len(node_by_key)
    graph_capabilities = {
        capability
        for node in node_by_key.values()
        for capability in _string_refs(node.get("capabilities"))
    }
    component_types = {
        str(component.get("type"))
        for component in ((entry.get("ui_model") or {}).get("components") or [])
        if isinstance(component, dict) and component.get("type")
    }
    declared_listeners = set(_string_refs(node_graph.get("listeners")))
    terminal_nodes = _string_refs(node_graph.get("terminal_nodes"))
    has_retry_path = any(bool(node.get("failure_or_retry") or node.get("retry_target")) for node in node_by_key.values())
    has_hidden_executor_handoff = any(_has_hidden_executor_handoff(node, node_by_key) for node in node_by_key.values())

    for archetype_key in declared_archetypes:
        contract = archetype_index.get(archetype_key)
        if contract is None:
            if not _is_custom_archetype(archetype_key):
                errors.append(_issue(entry, f"node_graph.archetypes unknown archetype {archetype_key!r}"))
            continue
        if contract.get("may_write_src") is not False:
            errors.append(_issue(entry, f"archetype {archetype_key!r} is not allowed to write src"))
        missing_capabilities = sorted(set(_string_refs(contract.get("required_capabilities"))) - graph_capabilities)
        if missing_capabilities:
            errors.append(
                _issue(
                    entry,
                    f"archetype {archetype_key!r} missing required capability(s): {', '.join(missing_capabilities)}",
                )
            )
        for role in _string_refs(contract.get("required_variable_roles")):
            if not _variable_names_with_role(variables, role):
                errors.append(_issue(entry, f"archetype {archetype_key!r} missing variable role {role!r}"))
        missing_ui = sorted(set(_string_refs(contract.get("required_ui_components"))) - component_types)
        if missing_ui:
            errors.append(
                _issue(entry, f"archetype {archetype_key!r} missing ui component(s): {', '.join(missing_ui)}")
            )
        missing_listeners = sorted(set(_string_refs(contract.get("required_listeners"))) - declared_listeners)
        if missing_listeners:
            errors.append(
                _issue(entry, f"archetype {archetype_key!r} missing listener(s): {', '.join(missing_listeners)}")
            )
        try:
            min_nodes = int(contract.get("min_nodes"))
            max_nodes = int(contract.get("max_nodes"))
        except (TypeError, ValueError):
            continue
        if node_count < min_nodes:
            errors.append(_issue(entry, f"archetype {archetype_key!r} requires at least {min_nodes} node(s)"))
        if node_count > max_nodes:
            errors.append(_issue(entry, f"archetype {archetype_key!r} allows at most {max_nodes} node(s)"))
        if contract.get("requires_retry_path") is True and not has_retry_path:
            errors.append(_issue(entry, f"archetype {archetype_key!r} requires a retry path"))
        if contract.get("requires_hidden_executor_handoff") is True and not has_hidden_executor_handoff:
            errors.append(_issue(entry, f"archetype {archetype_key!r} requires a hidden executor handoff"))
        terminal_capability = contract.get("terminal_requires_capability")
        if terminal_capability:
            for terminal in terminal_nodes:
                terminal_node = node_by_key.get(terminal)
                if not terminal_node:
                    continue
                if str(terminal_capability) not in set(_string_refs(terminal_node.get("capabilities"))):
                    errors.append(
                        _issue(
                            entry,
                            f"terminal node {terminal} must declare capability {terminal_capability!r} for archetype {archetype_key!r}",
                        )
                    )

    return errors


def _semantic_contract_errors(
    entry: dict[str, Any],
    node_graph: dict[str, Any],
    variables: list[Any],
    *,
    capability_registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    capability_index = capability_registry_index(capability_registry)
    declared_listeners = set(_string_refs(node_graph.get("listeners")))
    nodes = node_graph.get("nodes", [])
    node_by_key = {
        str(node["key"]): node
        for node in nodes
        if isinstance(node, dict) and node.get("key")
    }
    component_types = {
        str(component.get("type"))
        for component in ((entry.get("ui_model") or {}).get("components") or [])
        if isinstance(component, dict) and component.get("type")
    }

    for node in nodes if isinstance(nodes, list) else []:
        if not isinstance(node, dict):
            continue
        key = str(node.get("key", "<unknown>"))
        kind = str(node.get("kind", ""))
        node_capabilities = _string_refs(node.get("capabilities"))
        if not node_capabilities:
            errors.append(_issue(entry, f"node {key} must declare at least one capability"))

        contracts: list[dict[str, Any]] = []
        for capability_key in node_capabilities:
            contract = capability_index.get(capability_key)
            if contract is None:
                errors.append(_issue(entry, f"node {key} unknown capability {capability_key!r}"))
                continue
            contracts.append(contract)
            supported_node_kinds = set(_string_refs(contract.get("supported_node_kinds")))
            if kind not in supported_node_kinds:
                errors.append(
                    _issue(
                        entry,
                        f"node {key} capability {capability_key!r} does not support node kind {kind!r}",
                    )
                )
            if contract.get("may_write_src") is not False:
                errors.append(_issue(entry, f"node {key} capability {capability_key!r} is not allowed to write src"))
            supported_ui = set(_string_refs(contract.get("supported_ui_components")))
            if supported_ui and component_types and not (supported_ui & component_types):
                errors.append(
                    _issue(
                        entry,
                        f"node {key} capability {capability_key!r} requires one of ui components "
                        + ", ".join(sorted(supported_ui)),
                    )
                )
            dotted_root = {"entry": entry, "node_graph": node_graph, "node": node, "ui_model": entry.get("ui_model") or {}}
            for field_path in _string_refs(contract.get("required_node_fields")):
                if not _dotted_path_exists(dotted_root, field_path):
                    errors.append(
                        _issue(entry, f"node {key} capability {capability_key!r} missing required field {field_path}")
                    )
            node_variables = set(_string_refs(node.get("reads"))) | set(_string_refs(node.get("writes")))
            for role in _string_refs(contract.get("required_variable_roles")):
                role_variables = _variable_names_with_role(variables, role)
                if not role_variables:
                    errors.append(
                        _issue(entry, f"node {key} capability {capability_key!r} missing variable role {role!r}")
                    )
                elif not (role_variables & node_variables):
                    errors.append(
                        _issue(
                            entry,
                            f"node {key} capability {capability_key!r} requires node read/write variable role {role!r}",
                        )
                    )

        scope_contract = node.get("scope_contract")
        if scope_contract is not None:
            if not isinstance(scope_contract, dict):
                errors.append(_issue(entry, f"node {key} scope_contract must be a mapping"))
            else:
                for field in _missing_required(scope_contract, SCOPE_CONTRACT_REQUIRED_FIELDS):
                    errors.append(_issue(entry, f"node {key} scope_contract missing required field {field}"))
                for field in ("root_scope", "current_scope"):
                    scope_value = scope_contract.get(field)
                    if scope_value is not None and str(scope_value) not in SUPPORTED_SCOPE_CONTRACT_SCOPES:
                        errors.append(_issue(entry, f"node {key} scope_contract.{field} has unknown scope {scope_value!r}"))
                target_scopes = scope_contract.get("target_scopes")
                if target_scopes is not None and not isinstance(target_scopes, list):
                    errors.append(_issue(entry, f"node {key} scope_contract.target_scopes must be a list"))
                for scope_value in _string_refs(target_scopes):
                    if scope_value not in SUPPORTED_SCOPE_CONTRACT_SCOPES:
                        errors.append(_issue(entry, f"node {key} scope_contract.target_scopes has unknown scope {scope_value!r}"))
                if scope_contract.get("tooltip_safe") is False and "player_facing_tooltip" in set(_string_refs(node.get("output_kinds"))):
                    errors.append(_issue(entry, f"node {key} scope_contract.tooltip_safe=false cannot output player_facing_tooltip"))
                if scope_contract.get("unsafe_pre_eval") is True and not scope_contract.get("blocked_reason") and not _has_hidden_executor_handoff(node, node_by_key):
                    errors.append(
                        _issue(
                            entry,
                            f"node {key} scope_contract.unsafe_pre_eval=true requires blocked_reason or hidden_executor_handoff",
                        )
                    )

        listener_contract = node.get("listener_contract")
        if kind == "listener_gate" and not isinstance(listener_contract, dict):
            errors.append(_issue(entry, f"listener_gate node {key} must declare listener_contract"))
        if listener_contract is not None:
            if not isinstance(listener_contract, dict):
                errors.append(_issue(entry, f"node {key} listener_contract must be a mapping"))
            else:
                for field in _missing_required(listener_contract, LISTENER_CONTRACT_REQUIRED_FIELDS):
                    errors.append(_issue(entry, f"node {key} listener_contract missing required field {field}"))
                listener = listener_contract.get("listener")
                if listener is not None:
                    listener = str(listener)
                    if listener not in SUPPORTED_LISTENERS:
                        errors.append(_issue(entry, f"node {key} listener_contract uses unsupported listener {listener!r}"))
                    if listener not in declared_listeners:
                        errors.append(_issue(entry, f"node {key} listener_contract listener {listener!r} is not declared in node_graph.listeners"))
                    supported_by_capability = {
                        supported
                        for contract in contracts
                        for supported in _string_refs(contract.get("supported_listener_kinds"))
                    }
                    if listener not in supported_by_capability:
                        errors.append(_issue(entry, f"node {key} listener_contract listener {listener!r} is not supported by declared capabilities"))
                for field in ("reads", "writes"):
                    for variable in _string_refs(listener_contract.get(field)):
                        if variable not in set(_string_refs(node.get(field))):
                            errors.append(
                                _issue(
                                    entry,
                                    f"node {key} listener_contract.{field} references variable {variable} not declared in node.{field}",
                                )
                            )

    for action in node_graph.get("actions", []) or []:
        if not isinstance(action, dict):
            continue
        key = str(action.get("key", "<unknown>"))
        scope_contract = action.get("scope_contract")
        if isinstance(scope_contract, dict) and scope_contract.get("tooltip_safe") is False:
            if "player_facing_tooltip" in set(_string_refs(action.get("output_kinds"))):
                errors.append(_issue(entry, f"action {key} scope_contract.tooltip_safe=false cannot output player_facing_tooltip"))
        if isinstance(scope_contract, dict) and scope_contract.get("unsafe_pre_eval") is True and not scope_contract.get("blocked_reason"):
            errors.append(_issue(entry, f"action {key} scope_contract.unsafe_pre_eval=true requires blocked_reason"))
    return errors


def _progress_or_count_variables(variables: list[Any]) -> set[str]:
    names: set[str] = set()
    for variable in variables:
        if not isinstance(variable, dict) or not variable.get("name"):
            continue
        name = str(variable["name"])
        var_type = str(variable.get("type", "")).lower()
        lowered_name = name.lower()
        if "progress" in lowered_name or "count" in lowered_name or var_type in {"progress", "counter", "count"}:
            names.add(name)
    return names


def _graph_lifecycle_summary(entry: dict[str, Any], node_graph: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    nodes = node_graph.get("nodes", [])
    if not isinstance(nodes, list):
        return {"errors": errors, "reachable_count": 0, "unreachable_count": 0}
    node_by_key = {
        str(node["key"]): node
        for node in nodes
        if isinstance(node, dict) and node.get("key")
    }
    node_keys = set(node_by_key)

    entry_node = node_graph.get("entry_node")
    if not entry_node:
        errors.append(_issue(entry, "node_graph.entry_node is required"))
    elif str(entry_node) not in node_keys:
        errors.append(_issue(entry, f"node_graph.entry_node references undeclared node {entry_node}"))

    terminal_nodes = _string_refs(node_graph.get("terminal_nodes"))
    if not terminal_nodes:
        errors.append(_issue(entry, "node_graph.terminal_nodes must not be empty"))
    terminal_set = set()
    for terminal in terminal_nodes:
        if terminal not in node_keys:
            errors.append(_issue(entry, f"node_graph.terminal_nodes references undeclared node {terminal}"))
        else:
            terminal_set.add(terminal)

    outgoing: dict[str, set[str]] = {key: set() for key in node_keys}
    for key, node in node_by_key.items():
        outgoing[key].update(next_node for next_node in _string_refs(node.get("next_nodes")) if next_node in node_keys)
    edges = node_graph.get("edges", [])
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            from_node = edge.get("from")
            to_node = edge.get("to")
            if from_node is not None and to_node is not None and str(from_node) in node_keys and str(to_node) in node_keys:
                outgoing[str(from_node)].add(str(to_node))

    reachable: set[str] = set()
    if entry_node and str(entry_node) in node_keys:
        stack = [str(entry_node)]
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            reachable.add(current)
            stack.extend(sorted(outgoing.get(current, set()) - reachable))
    unreachable = sorted(node_keys - reachable)
    for node_key in unreachable:
        errors.append(_issue(entry, f"node {node_key} is unreachable from entry_node {entry_node}"))

    allow_terminal_outgoing = bool(
        isinstance(node_graph.get("completion_policy"), dict)
        and node_graph["completion_policy"].get("allow_terminal_outgoing")
    )
    for key, node in node_by_key.items():
        has_outgoing = bool(outgoing.get(key))
        if key not in terminal_set and not has_outgoing:
            errors.append(_issue(entry, f"non-terminal node {key} has no next_nodes or outgoing edge"))
        if key in terminal_set and has_outgoing and not allow_terminal_outgoing:
            errors.append(_issue(entry, f"terminal node {key} must not have ordinary outgoing edges"))
        retry_target = node.get("retry_target")
        if retry_target and str(retry_target) in terminal_set:
            errors.append(_issue(entry, f"node {key} retry_target must not point to terminal node {retry_target}"))
        if node.get("kind") == "final_reward_dispatch" and key not in terminal_set:
            errors.append(_issue(entry, f"final_reward_dispatch node {key} must be listed in node_graph.terminal_nodes"))

    variables = node_graph.get("variables", [])
    progress_or_count = _progress_or_count_variables(variables if isinstance(variables, list) else [])
    for key, node in node_by_key.items():
        if node.get("kind") != "monthly_progress_gate":
            continue
        read_write_progress = (
            set(_string_refs(node.get("reads")))
            & set(_string_refs(node.get("writes")))
            & progress_or_count
        )
        if not read_write_progress:
            errors.append(
                _issue(entry, f"monthly_progress_gate node {key} must read and write at least one progress/count variable")
            )

    if isinstance(variables, list):
        actual_writers: dict[str, set[str]] = {}
        actual_readers: dict[str, set[str]] = {}
        for key, node in node_by_key.items():
            for variable in _string_refs(node.get("writes")):
                actual_writers.setdefault(variable, set()).add(key)
            for variable in _string_refs(node.get("reads")):
                actual_readers.setdefault(variable, set()).add(key)
        for variable in variables:
            if not isinstance(variable, dict) or not variable.get("name"):
                continue
            name = str(variable["name"])
            declared_writers = set(_string_refs(variable.get("writer_nodes")))
            declared_readers = set(_string_refs(variable.get("reader_nodes")))
            if declared_writers != actual_writers.get(name, set()):
                errors.append(
                    _issue(
                        entry,
                        f"variable {name} writer_nodes do not match node writes "
                        f"(declared={sorted(declared_writers)}, actual={sorted(actual_writers.get(name, set()))})",
                    )
                )
            if declared_readers != actual_readers.get(name, set()):
                errors.append(
                    _issue(
                        entry,
                        f"variable {name} reader_nodes do not match node reads "
                        f"(declared={sorted(declared_readers)}, actual={sorted(actual_readers.get(name, set()))})",
                    )
                )
    return {
        "errors": errors,
        "reachable_count": len(reachable),
        "unreachable_count": len(unreachable),
    }


def _validate_codegen_node_graph(
    entry: dict[str, Any],
    node_graph: dict[str, Any],
    entry_event_id_set: set[int],
    loc_keys: set[str],
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
    *,
    require_generation: bool = True,
) -> list[str]:
    errors: list[str] = []
    identity = entry.get("identity") or {}
    status = str(identity.get("status", ""))
    runtime_prefix = str(identity.get("runtime_prefix", ""))
    template_index = template_registry_index(template_registry)

    variables = node_graph.get("variables", [])
    if not isinstance(variables, list):
        errors.append(_issue(entry, "node_graph.variables must be a list"))
        variables = []
    variable_names: set[str] = set()
    for variable in variables:
        if not isinstance(variable, dict):
            errors.append(_issue(entry, "node_graph.variables entries must be mappings"))
            continue
        for field in _missing_required(variable, VARIABLE_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"variable {variable.get('name', '<unknown>')} missing required field {field}"))
        name = variable.get("name")
        if not name:
            continue
        name = str(name)
        if name in variable_names:
            errors.append(_issue(entry, f"duplicate variable {name}"))
        variable_names.add(name)
        if runtime_prefix and not name.startswith(runtime_prefix):
            errors.append(_issue(entry, f"runtime variable {name} must start with {runtime_prefix}"))

    nodes = node_graph.get("nodes", [])
    if not isinstance(nodes, list):
        errors.append(_issue(entry, "node_graph.nodes must be a list"))
        return errors

    node_keys: set[str] = set()
    node_event_ids: dict[int, str] = {}
    for node in nodes:
        if not isinstance(node, dict):
            errors.append(_issue(entry, "node_graph.nodes entries must be mappings"))
            continue
        for field in _missing_required(node, NODE_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"node {node.get('key', '<unknown>')} missing required field {field}"))
        key = node.get("key")
        if not key:
            continue
        key = str(key)
        if key in node_keys:
            errors.append(_issue(entry, f"duplicate node {key}"))
        node_keys.add(key)
        kind = node.get("kind")
        if kind not in SUPPORTED_NODE_KINDS:
            errors.append(_issue(entry, f"node {key} unsupported kind {kind!r}"))
        try:
            event_id = int(node.get("event_id"))
        except (TypeError, ValueError):
            errors.append(_issue(entry, f"node {key} has invalid event_id {node.get('event_id')!r}"))
        else:
            if event_id not in entry_event_id_set:
                errors.append(_issue(entry, f"node {key} references undeclared event id {event_id}"))
            if event_id in node_event_ids:
                errors.append(
                    _issue(
                        entry,
                        f"node {key} event_id {event_id} duplicates node {node_event_ids[event_id]}",
                    )
                )
            else:
                node_event_ids[event_id] = key

    errors.extend(
        _semantic_contract_errors(
            entry,
            node_graph,
            variables,
            capability_registry=capability_registry,
        )
    )
    errors.extend(
        _archetype_contract_errors(
            entry,
            node_graph,
            variables,
            archetype_registry=archetype_registry,
        )
    )
    errors.extend(
        _mechanic_signature_errors(
            entry,
            node_graph,
            archetype_registry=archetype_registry,
        )
    )
    errors.extend(_cadence_signature_errors(entry, node_graph))

    for variable in variables:
        if not isinstance(variable, dict):
            continue
        name = str(variable.get("name", "<unknown>"))
        for field in ("writer_nodes", "reader_nodes"):
            for node_key in _string_refs(variable.get(field)):
                if node_key not in node_keys:
                    errors.append(_issue(entry, f"variable {name} {field} references undeclared node {node_key}"))

    for node in nodes:
        if not isinstance(node, dict):
            continue
        key = str(node.get("key", "<unknown>"))
        for field in ("reads", "writes"):
            for variable in _string_refs(node.get(field)):
                if variable not in variable_names:
                    errors.append(_issue(entry, f"node {key} {field} undeclared variable {variable}"))
        for variable in _ui_state_variable_refs(node.get("ui_state")):
            if variable not in variable_names:
                errors.append(_issue(entry, f"node {key} ui_state undeclared variable {variable}"))
        for next_node in _string_refs(node.get("next_nodes")):
            if next_node not in node_keys:
                errors.append(_issue(entry, f"node {key} next_nodes references undeclared node {next_node}"))
        retry_target = node.get("retry_target")
        if node.get("failure_or_retry") and not retry_target:
            errors.append(_issue(entry, f"node {key} failure_or_retry requires retry_target"))
        if retry_target and str(retry_target) not in node_keys:
            errors.append(_issue(entry, f"node {key} retry_target references undeclared node {retry_target}"))
        errors.extend(_loc_ref_errors(entry, f"node {key}", node.get("loc_refs"), loc_keys))

    edges = node_graph.get("edges", [])
    if not isinstance(edges, list):
        errors.append(_issue(entry, "node_graph.edges must be a list"))
        edges = []
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append(_issue(entry, "node_graph.edges entries must be mappings"))
            continue
        for field in _missing_required(edge, EDGE_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"edge missing required field {field}"))
        from_node = edge.get("from")
        to_node = edge.get("to")
        if from_node and str(from_node) not in node_keys:
            errors.append(_issue(entry, f"edge from references undeclared node {from_node}"))
        if to_node and str(to_node) not in node_keys:
            errors.append(_issue(entry, f"edge to references undeclared node {to_node}"))
        errors.extend(_loc_ref_errors(entry, f"edge {from_node}->{to_node}", [edge.get("label_key")], loc_keys))

    errors.extend(_graph_lifecycle_summary(entry, node_graph)["errors"])

    actions = node_graph.get("actions", [])
    if not isinstance(actions, list):
        errors.append(_issue(entry, "node_graph.actions must be a list"))
        actions = []
    for action in actions:
        if not isinstance(action, dict):
            errors.append(_issue(entry, "node_graph.actions entries must be mappings"))
            continue
        for field in _missing_required(action, ACTION_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"action {action.get('key', '<unknown>')} missing required field {field}"))
        key = str(action.get("key", "<unknown>"))
        kind = action.get("kind")
        if kind not in SUPPORTED_ACTION_KINDS:
            errors.append(_issue(entry, f"action {key} unsupported kind {kind!r}"))
        if not action.get("effect_script") and not action.get("generator_template"):
            errors.append(_issue(entry, f"action {key} must declare effect_script or generator_template"))
        errors.extend(_template_errors(entry, f"action {key}", action.get("generator_template"), template_index))
        errors.extend(
            _template_kind_support_errors(
                entry,
                f"action {key}",
                action.get("generator_template"),
                "supported_action_kinds",
                kind,
                template_index,
            )
        )

    checks = node_graph.get("checks", [])
    if not isinstance(checks, list):
        errors.append(_issue(entry, "node_graph.checks must be a list"))
        checks = []
    for check in checks:
        if not isinstance(check, dict):
            errors.append(_issue(entry, "node_graph.checks entries must be mappings"))
            continue
        for field in _missing_required(check, CHECK_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"check {check.get('key', '<unknown>')} missing required field {field}"))
        key = str(check.get("key", "<unknown>"))
        kind = check.get("kind")
        if kind not in SUPPORTED_CHECK_KINDS:
            errors.append(_issue(entry, f"check {key} unsupported kind {kind!r}"))
        if not check.get("trigger_script") and not check.get("generator_template"):
            errors.append(_issue(entry, f"check {key} must declare trigger_script or generator_template"))
        errors.extend(_template_errors(entry, f"check {key}", check.get("generator_template"), template_index))
        errors.extend(
            _template_kind_support_errors(
                entry,
                f"check {key}",
                check.get("generator_template"),
                "supported_check_kinds",
                kind,
                template_index,
            )
        )
        errors.extend(_loc_ref_errors(entry, f"check {key}", [check.get("tooltip_key")], loc_keys))

    generation = entry.get("generation")
    if require_generation:
        if not isinstance(generation, dict):
            errors.append(_issue(entry, "generation must be a mapping for source-codegen-ready specs"))
            generation = {}
        for field in _missing_required(generation, GENERATION_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"generation missing required field {field}"))
        for template in generation.get("verified_templates", []) or []:
            errors.extend(_template_errors(entry, "generation.verified_templates", template, template_index))
        for template in generation.get("blocked_templates", []) or []:
            errors.extend(_template_errors(entry, "generation.blocked_templates", template, template_index))
            errors.append(_issue(entry, f"generation.blocked_templates contains blocked template {template}"))
        verified = set(str(template) for template in generation.get("verified_templates", []) or [])
        used_templates = templates_used_by_entry(entry) - verified
        unverified_used = sorted(template for template in used_templates if template in template_index)
        if unverified_used:
            errors.append(
                _issue(
                    entry,
                    "template(s) not listed in generation.verified_templates: " + ", ".join(unverified_used),
                )
            )
        covered_node_kinds: set[str] = set()
        for template in verified:
            covered_node_kinds.update(str(kind) for kind in template_index.get(template, {}).get("supported_node_kinds", []) or [])
        for kind in sorted({
            str(node.get("kind"))
            for node in nodes
            if isinstance(node, dict) and node.get("kind") in SUPPORTED_NODE_KINDS
        }):
            if kind not in covered_node_kinds:
                errors.append(_issue(entry, f"node kind {kind!r} is not covered by generation.verified_templates"))
        if status == "harness_generated":
            if not generation.get("target_files"):
                errors.append(_issue(entry, "harness_generated must declare generation.target_files"))
            if not generation.get("verified_templates"):
                errors.append(_issue(entry, "harness_generated must declare generation.verified_templates"))

        for path in _needs_verification_paths(entry):
            errors.append(_issue(entry, f"source-codegen-ready specs cannot contain needs_verification at {path}"))

    return errors


def validate_codegen_graph_entry(
    entry: dict[str, Any],
    *,
    localization: dict[str, str] | None = None,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
    require_generation: bool = True,
) -> list[str]:
    node_graph = entry.get("node_graph") or {}
    if not isinstance(node_graph, dict):
        return [_issue(entry, "node_graph must be a mapping")]
    return _validate_codegen_node_graph(
        entry,
        node_graph,
        set(event_ids_in_entry(entry)),
        loc_key_inventory(localization),
        template_registry,
        capability_registry,
        archetype_registry,
        require_generation=require_generation,
    )


def validate_codegen_ui_bindings(
    entry: dict[str, Any],
    *,
    localization: dict[str, str] | None = None,
) -> list[str]:
    errors: list[str] = []
    node_graph = entry.get("node_graph") or {}
    ui_model = entry.get("ui_model") or {}
    loc_keys = loc_key_inventory(localization)
    node_keys = {
        str(node.get("key"))
        for node in node_graph.get("nodes", []) or []
        if isinstance(node, dict) and node.get("key")
    }
    variable_names = declared_runtime_variables(entry)
    components = ui_model.get("components", []) if isinstance(ui_model, dict) else []
    component_keys = {
        str(component.get("key"))
        for component in components
        if isinstance(component, dict) and component.get("key")
    }
    bindings = ui_model.get("bindings", []) if isinstance(ui_model, dict) else []
    if not isinstance(bindings, list):
        return [_issue(entry, "ui_model.bindings must be a list")]
    if not bindings:
        errors.append(_issue(entry, "ui_model.bindings must not be empty for implementation_ready or harness_generated specs"))
    for binding in bindings:
        if not isinstance(binding, dict):
            errors.append(_issue(entry, "ui_model.bindings entries must be mappings"))
            continue
        for field in _missing_required(binding, UI_BINDING_REQUIRED_FIELDS):
            errors.append(_issue(entry, f"ui binding {binding.get('key', '<unknown>')} missing required field {field}"))
        key = str(binding.get("key", "<unknown>"))
        component_key = binding.get("component_key")
        if component_key and str(component_key) not in component_keys:
            errors.append(_issue(entry, f"ui binding {key} references undeclared component {component_key}"))
        for variable in _string_refs(binding.get("variable_refs")):
            if variable not in variable_names:
                errors.append(_issue(entry, f"ui binding {key} references undeclared variable {variable}"))
        for node_key in _string_refs(binding.get("node_refs")):
            if node_key not in node_keys:
                errors.append(_issue(entry, f"ui binding {key} references undeclared node {node_key}"))
        errors.extend(_loc_ref_errors(entry, f"ui binding {key}", binding.get("loc_refs"), loc_keys))
    return errors


def codegen_support_errors(
    entry: dict[str, Any],
    *,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
    validate_registries: bool = True,
) -> list[str]:
    identity = entry.get("identity") or {}
    key = str(identity.get("key", "<unknown>"))
    status = str(identity.get("status", ""))
    if status not in CODEGEN_ELIGIBLE_STATUSES:
        return [f"{key}: status {status!r} is not eligible for Harness codegen"]
    if validate_registries:
        registry_errors = (
            validate_template_registry(template_registry) if template_registry is not None else validate_template_registry()
        )
        if registry_errors:
            return [f"{key}: template registry error: {error}" for error in registry_errors]
        capability_registry_errors = (
            validate_capability_registry(capability_registry)
            if capability_registry is not None
            else validate_capability_registry()
        )
        if capability_registry_errors:
            return [f"{key}: capability registry error: {error}" for error in capability_registry_errors]
        archetype_registry_errors = (
            validate_archetype_registry(archetype_registry, capability_registry=capability_registry)
            if archetype_registry is not None
            else validate_archetype_registry(capability_registry=capability_registry)
        )
        if archetype_registry_errors:
            return [f"{key}: archetype registry error: {error}" for error in archetype_registry_errors]
    template_index = template_registry_index(template_registry)
    capability_index = capability_registry_index(capability_registry)
    archetype_index = archetype_registry_index(archetype_registry)
    generation = entry.get("generation") or {}
    errors: list[str] = []
    unresolved_gaps = unresolved_compiler_gap_rows(entry)
    if unresolved_gaps:
        errors.append(
            f"{key}: source-codegen-ready status has unresolved compiler gap(s): "
            + ", ".join(str(row.get("primitive", "<unknown>")) for row in unresolved_gaps)
        )
    ledger = entry.get("compiler_gap_ledger", [])
    non_backend_ready = [
        row
        for row in ledger
        if isinstance(row, dict) and row.get("verification_status") != "backend_ready"
    ]
    if non_backend_ready:
        errors.append(
            f"{key}: source-codegen-ready status has compiler gap row(s) not backend_ready: "
            + ", ".join(str(row.get("primitive", "<unknown>")) for row in non_backend_ready)
        )
    for row in ledger if isinstance(ledger, list) else []:
        if not isinstance(row, dict) or row.get("verification_status") != "backend_ready":
            continue
        if not _valid_backend_ready_evidence_tokens(
            row,
            template_registry=template_registry,
            capability_registry=capability_registry,
        ):
            errors.append(
                f"{key}: compiler gap {row.get('primitive', '<unknown>')} backend_ready requires valid capability:<key> or template:<key> codebase_evidence"
            )
    verified = set(str(template) for template in generation.get("verified_templates", []) or [])
    blocked = set(str(template) for template in generation.get("blocked_templates", []) or [])
    used = templates_used_by_entry(entry)
    unknown = sorted(template for template in used if template not in template_index)
    if unknown:
        errors.append(f"{key}: unknown template(s): {', '.join(unknown)}")
    if blocked:
        errors.append(f"{key}: blocked template(s): {', '.join(sorted(blocked))}")
    unverified = sorted(template for template in used if template not in verified)
    if unverified:
        errors.append(f"{key}: template(s) not listed in generation.verified_templates: {', '.join(unverified)}")
    node_graph = entry.get("node_graph") or {}
    declared_archetypes = _string_refs(node_graph.get("archetypes")) if isinstance(node_graph, dict) else []
    for archetype_key in declared_archetypes:
        contract = archetype_index.get(archetype_key)
        if contract is None:
            if not _is_custom_archetype(archetype_key):
                errors.append(f"{key}: unknown archetype(s): {archetype_key}")
            continue
        if contract.get("may_write_src") is not False:
            errors.append(f"{key}: archetype {archetype_key!r} is not allowed to write src")
    variables = node_graph.get("variables", []) if isinstance(node_graph, dict) else []
    if isinstance(node_graph, dict) and isinstance(variables, list):
        errors.extend(
            _archetype_contract_errors(
                entry,
                node_graph,
                variables,
                archetype_registry=archetype_registry,
            )
        )
        errors.extend(
            _mechanic_signature_errors(
                entry,
                node_graph,
                archetype_registry=archetype_registry,
            )
        )
        errors.extend(_cadence_signature_errors(entry, node_graph))
    for section, field in (("actions", "supported_action_kinds"), ("checks", "supported_check_kinds")):
        for item in node_graph.get(section, []) or []:
            if not isinstance(item, dict) or not item.get("generator_template"):
                continue
            template = str(item["generator_template"])
            contract = template_index.get(template)
            if contract is None:
                continue
            kind = str(item.get("kind", ""))
            if kind not in set(str(value) for value in contract.get(field, []) or []):
                errors.append(f"{key}: {section[:-1]} {item.get('key', '<unknown>')} template {template!r} does not support kind {kind!r}")
    verified_node_kinds: set[str] = set()
    for template in verified:
        verified_node_kinds.update(str(kind) for kind in template_index.get(template, {}).get("supported_node_kinds", []) or [])
    for node in node_graph.get("nodes", []) or []:
        if isinstance(node, dict) and node.get("kind") in SUPPORTED_NODE_KINDS and str(node["kind"]) not in verified_node_kinds:
            errors.append(f"{key}: node kind {node['kind']!r} is not covered by generation.verified_templates")
        if not isinstance(node, dict):
            continue
        node_key = str(node.get("key", "<unknown>"))
        node_capabilities = _string_refs(node.get("capabilities"))
        if not node_capabilities:
            errors.append(f"{key}: node {node_key} must declare at least one capability")
        for capability_key in node_capabilities:
            contract = capability_index.get(capability_key)
            if contract is None:
                errors.append(f"{key}: node {node_key} unknown capability {capability_key!r}")
                continue
            if str(node.get("kind", "")) not in set(_string_refs(contract.get("supported_node_kinds"))):
                errors.append(
                    f"{key}: node {node_key} capability {capability_key!r} does not support node kind {node.get('kind')!r}"
                )
    return errors


def graph_validation_errors_for_payload(
    payload: dict[str, Any],
    *,
    localization: dict[str, str] | None = None,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    for entry in payload.get("unique_wonders", []) or []:
        if not isinstance(entry, dict):
            continue
        status = str((entry.get("identity") or {}).get("status", ""))
        if status in SEMANTIC_GRAPH_STATUSES:
            errors.extend(
                validate_codegen_graph_entry(
                    entry,
                    localization=localization,
                    template_registry=template_registry,
                    capability_registry=capability_registry,
                    archetype_registry=archetype_registry,
                    require_generation=status in CODEGEN_ELIGIBLE_STATUSES,
                )
            )
            errors.extend(validate_codegen_ui_bindings(entry, localization=localization))
    return errors


def graph_lifecycle_summary_for_payload(payload: dict[str, Any]) -> dict[str, Any]:
    reachable_count = 0
    unreachable_count = 0
    lifecycle_errors: list[str] = []
    for entry in payload.get("unique_wonders", []) or []:
        if not isinstance(entry, dict):
            continue
        status = str((entry.get("identity") or {}).get("status", ""))
        if status not in SEMANTIC_GRAPH_STATUSES:
            continue
        node_graph = entry.get("node_graph") or {}
        if not isinstance(node_graph, dict):
            continue
        summary = _graph_lifecycle_summary(entry, node_graph)
        reachable_count += int(summary["reachable_count"])
        unreachable_count += int(summary["unreachable_count"])
        lifecycle_errors.extend(summary["errors"])
    return {
        "graph_reachable_count": reachable_count,
        "graph_unreachable_count": unreachable_count,
        "lifecycle_errors": lifecycle_errors,
        "lifecycle_error_count": len(lifecycle_errors),
    }


def archetype_coverage_summary_for_payload(payload: dict[str, Any]) -> dict[str, Any]:
    used: dict[str, int] = {}
    eligible_specs = 0
    specs_without_archetypes = 0
    for entry in payload.get("unique_wonders", []) or []:
        if not isinstance(entry, dict):
            continue
        if str((entry.get("identity") or {}).get("status", "")) not in CODEGEN_ELIGIBLE_STATUSES:
            continue
        eligible_specs += 1
        archetypes = archetypes_used_by_entry(entry)
        if not archetypes:
            specs_without_archetypes += 1
        for archetype in archetypes:
            used[archetype] = used.get(archetype, 0) + 1
    return {
        "eligible_specs": eligible_specs,
        "specs_without_archetypes": specs_without_archetypes,
        "archetypes": dict(sorted(used.items())),
    }


def codegen_tier_summary_for_payload(
    payload: dict[str, Any],
    *,
    template_registry: dict[str, Any] | None = None,
) -> dict[str, int]:
    template_index = template_registry_index(template_registry)
    summary = {
        "eligible_specs": 0,
        "intermediate_only": 0,
        "blocked_or_unknown": 0,
        "may_write_src": 0,
    }
    intermediate_outputs = SUPPORTED_TEMPLATE_OUTPUT_KINDS
    for entry in payload.get("unique_wonders", []) or []:
        if not isinstance(entry, dict):
            continue
        if str((entry.get("identity") or {}).get("status", "")) not in CODEGEN_ELIGIBLE_STATUSES:
            continue
        summary["eligible_specs"] += 1
        used = templates_used_by_entry(entry)
        contracts = [template_index.get(template) for template in used]
        if any(contract is None for contract in contracts):
            summary["blocked_or_unknown"] += 1
            continue
        if any(contract.get("may_write_src") is not False for contract in contracts if contract):
            summary["may_write_src"] += 1
            continue
        output_kinds = {
            str(output)
            for contract in contracts
            if contract
            for output in contract.get("output_kinds", []) or []
        }
        if output_kinds and output_kinds <= intermediate_outputs:
            summary["intermediate_only"] += 1
        else:
            summary["blocked_or_unknown"] += 1
    return summary


def capability_coverage_summary_for_payload(payload: dict[str, Any]) -> dict[str, Any]:
    used: dict[str, int] = {}
    eligible_specs = 0
    node_count = 0
    nodes_without_capabilities = 0
    for entry in payload.get("unique_wonders", []) or []:
        if not isinstance(entry, dict):
            continue
        if str((entry.get("identity") or {}).get("status", "")) not in CODEGEN_ELIGIBLE_STATUSES:
            continue
        eligible_specs += 1
        node_graph = entry.get("node_graph") or {}
        for node in node_graph.get("nodes", []) or []:
            if not isinstance(node, dict):
                continue
            node_count += 1
            capabilities = _string_refs(node.get("capabilities"))
            if not capabilities:
                nodes_without_capabilities += 1
            for capability in capabilities:
                used[capability] = used.get(capability, 0) + 1
    return {
        "eligible_specs": eligible_specs,
        "node_count": node_count,
        "nodes_without_capabilities": nodes_without_capabilities,
        "capabilities": dict(sorted(used.items())),
    }


def node_kind_summary_for_payload(payload: dict[str, Any]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for entry in payload.get("unique_wonders", []) or []:
        if not isinstance(entry, dict):
            continue
        if str((entry.get("identity") or {}).get("status", "")) not in CODEGEN_ELIGIBLE_STATUSES:
            continue
        node_graph = entry.get("node_graph") or {}
        for node in node_graph.get("nodes", []) or []:
            if isinstance(node, dict) and node.get("kind"):
                kind = str(node["kind"])
                summary[kind] = summary.get(kind, 0) + 1
    return dict(sorted(summary.items()))


REPEATED_ENTITY_ROW_BACKEND = "repeated_entity_row_checklist_incident_log_backend"
REPEATED_ENTITY_ROW_UI_COMPONENTS = {
    "actor_slots",
    "checklist",
    "incident_log",
    "material_stockpile",
    "route_map",
}
REPEATED_ENTITY_ROW_BLOCKERS = {
    "missing_cleanup",
    "missing_effect_writer",
    "missing_event_ownership",
    "missing_gui_rows",
    "missing_listener_integration",
    "missing_loc_rows",
    "missing_row_variables",
    "missing_trigger_check",
}
REPEATED_ENTITY_ROW_SOURCE_PLAN_EVIDENCE_STATUSES = {
    "missing_eu5_evidence",
    "interface_candidate",
    "verified_existing",
    "backend_ready_intermediate",
}
REPEATED_ENTITY_ROW_SOURCE_PLAN_ARTIFACT_REQUIRED_FIELDS = {
    "artifact_kind",
    "owner_generator",
    "source_target_boundary",
    "required_eu5_interfaces",
    "evidence_status",
    "evidence_mapping",
    "may_write_src",
    "blocks_source_writer",
    "pilot_key",
    "row_set_key",
    "entity_keys",
    "aggregate_projection_variables",
}
REPEATED_ENTITY_ROW_SOURCE_PLAN_ARTIFACT_OPTIONAL_FIELDS = {
    "source_target_contract",
}
REPEATED_ENTITY_ROW_SOURCE_PLAN_EVIDENCE_MAPPING_REQUIRED_FIELDS = {
    "artifact_kind",
    "eu5_source_syntax_pattern",
    "evidence_source_paths",
    "generator_candidate",
    "generator_missing_reason",
    "source_target_boundary",
    "blocks_source_writer",
}
REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS = {
    "event": "unique_wonder_ritual_event_source_generator",
    "effect": "unique_wonder_ritual_scripted_effect_source_generator",
    "trigger": "unique_wonder_ritual_scripted_trigger_source_generator",
    "gui": "unique_wonder_ritual_gui_row_source_generator",
    "localization": "unique_wonder_ritual_localization_source_generator",
    "listener": "unique_wonder_ritual_listener_integration_source_generator",
}
REPEATED_ENTITY_ROW_SOURCE_PLAN_EXISTING_GENERATORS: set[str] = set()
REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS = {
    "event": [
        "event_opening_skeleton",
        "event_update_skeleton",
        "event_retry_skeleton",
        "event_resolve_skeleton",
    ],
    "effect": [
        "scripted_effect_row_init",
        "scripted_effect_row_state_write",
        "scripted_effect_aggregate_refresh",
        "scripted_effect_branch_write",
        "scripted_effect_cleanup_write",
    ],
    "trigger": [
        "scripted_trigger_row_completion",
        "scripted_trigger_eligibility",
        "scripted_trigger_tooltip_safe_condition_group",
    ],
    "localization": [
        "localization_row_labels",
        "localization_status_text",
        "localization_incident_text",
        "localization_tooltips",
        "localization_summary_text",
    ],
    "cleanup": [
        "cleanup_completion",
        "cleanup_failure",
        "cleanup_ownership_loss",
        "cleanup_ritual_reset",
    ],
}
REPEATED_ENTITY_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS = set(REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["effect"]) | set(
    REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["cleanup"]
)
REPEATED_ENTITY_ROW_EFFECT_ARTIFACT_KINDS = set(REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["effect"])
REPEATED_ENTITY_ROW_CLEANUP_ARTIFACT_KINDS = set(REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["cleanup"])
REPEATED_ENTITY_ROW_EVENT_ARTIFACT_KINDS = set(REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["event"])
REPEATED_ENTITY_ROW_TRIGGER_ARTIFACT_KINDS = set(REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["trigger"])
REPEATED_ENTITY_ROW_GUI_ARTIFACT_KINDS = {
    "gui_actor_slots_row",
    "gui_checklist_row",
    "gui_incident_log_row",
}
REPEATED_ENTITY_ROW_LOCALIZATION_ARTIFACT_KINDS = set(
    REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["localization"]
)
REPEATED_ENTITY_ROW_LISTENER_ARTIFACT_KINDS = {"listener_war_integration"}
REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES = (
    "no-write",
    "candidate",
    "blocked",
)
REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES = (
    "no-write",
    "candidate",
    "blocked",
)
REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS = {
    "status",
    "allowed_statuses",
    "contract_family",
    "namespace_policy",
    "event_id_sources",
    "localization_key_policy",
    "future_source_target_path_pattern",
    "candidate_future_source_target_path",
    "future_target_only",
    "source_writer_allowed",
    "may_write_src",
    "row_state_writes_allowed",
    "option_effect_handoff_rule",
    "required_validations",
    "blocker_reasons",
    "source_target_boundary",
}
REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS = (
    "event_id_uniqueness_collision",
    "localization_key_linkage",
    "node_event_id_linkage",
    "source_target_boundary_still_blocked",
)
REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS = (
    "missing real event source generator",
    "missing effect writer",
    "missing trigger writer",
    "missing GUI writer",
    "missing localization writer",
    "no verified source write contract",
)
REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS = {
    "status",
    "allowed_statuses",
    "contract_family",
    "source_type",
    "future_source_target_path_pattern",
    "candidate_future_source_target_path",
    "future_target_only",
    "source_generation_policy",
    "source_writer_allowed",
    "may_write_src",
    "effect_body_writes_allowed",
    "row_state_writes_allowed",
    "row_state_write_schema_allowed",
    "cleanup_lifecycle_scope",
    "aggregate_projection_boundary",
    "required_validations",
    "blocker_reasons",
    "source_target_boundary",
}
REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS = (
    "effect_name_uniqueness",
    "variable_writer_reader_linkage",
    "row_set_entity_coverage",
    "aggregate_projection_boundary",
    "cleanup_coverage",
    "source_target_boundary_still_blocked",
)
REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS = (
    "missing real scripted-effect source generator",
    "missing row-state write schema",
    "missing trigger validation",
    "missing GUI/localization writers",
    "no verified source write contract",
)
REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS = {
    "status",
    "allowed_statuses",
    "contract_family",
    "source_type",
    "future_source_target_path_pattern",
    "candidate_future_source_target_path",
    "future_target_only",
    "source_generation_policy",
    "source_writer_allowed",
    "may_write_src",
    "trigger_body_writes_allowed",
    "tooltip_safe_unsafe_write_paths_allowed",
    "tooltip_safe_condition_group_policy",
    "aggregate_projection_boundary",
    "required_validations",
    "blocker_reasons",
    "source_target_boundary",
}
REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS = (
    "trigger_name_uniqueness",
    "row_completion_variable_linkage",
    "eligibility_input_coverage",
    "tooltip_safe_scope_boundary",
    "source_target_boundary_still_blocked",
)
REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS = (
    "missing real scripted-trigger source generator",
    "missing trigger predicate schema",
    "missing effect writer validation",
    "missing GUI/localization coverage",
    "no verified source write contract",
)
REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS = {
    "status",
    "allowed_statuses",
    "contract_family",
    "source_type",
    "future_source_target_path_pattern",
    "candidate_future_source_target_path",
    "future_target_only",
    "source_generation_policy",
    "source_writer_allowed",
    "may_write_src",
    "blocks_source_writer",
    "gui_source_writes_allowed",
    "aggregate_only_row_reads_allowed",
    "row_state_writes_allowed",
    "fixed_row_widget_boundary",
    "per_row_variable_binding_policy",
    "actor_checklist_incident_row_policy",
    "tooltip_key_linkage_policy",
    "aggregate_projection_boundary",
    "required_validations",
    "blocker_reasons",
    "source_target_boundary",
}
REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS = (
    "fixed_row_widget_boundary",
    "per_row_variable_binding",
    "actor_checklist_incident_row_policy",
    "tooltip_key_linkage",
    "aggregate_projection_boundary",
    "source_target_boundary_still_blocked",
)
REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS = (
    "missing real GUI source generator",
    "missing EU5 GUI exact syntax/source writer contract",
    "missing source-target boundary validation",
)
REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS = {
    "status",
    "allowed_statuses",
    "contract_family",
    "source_type",
    "future_source_target_path_pattern",
    "candidate_future_source_target_path",
    "future_target_only",
    "source_generation_policy",
    "source_writer_allowed",
    "may_write_src",
    "blocks_source_writer",
    "localization_source_writes_allowed",
    "required_languages",
    "missing_bilingual_coverage_allowed",
    "loc_key_namespace_policy",
    "loc_line_escaping_bom_policy",
    "unsafe_quote_newline_handling_allowed",
    "localization_coverage_policy",
    "gui_event_key_linkage_policy",
    "required_validations",
    "blocker_reasons",
    "source_target_boundary",
}
REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS = (
    "english_simplified_chinese_coverage",
    "loc_key_namespace",
    "loc_line_escaping_bom",
    "row_status_incident_tooltip_summary_coverage",
    "gui_event_key_linkage",
    "source_target_boundary_still_blocked",
)
REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS = (
    "missing real localization source generator",
    "missing EU5 localization exact syntax/source writer contract",
    "missing source-target boundary validation",
)
REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS = {
    "status",
    "allowed_statuses",
    "contract_family",
    "source_type",
    "future_source_target_path_pattern",
    "candidate_future_source_target_path",
    "future_target_only",
    "source_generation_policy",
    "source_writer_allowed",
    "may_write_src",
    "listener_artifact_scope",
    "on_action_bridge_policy",
    "listener_scope_writes_allowed",
    "war_scope_writes_allowed",
    "row_state_writes_allowed",
    "required_validations",
    "blocker_reasons",
    "source_target_boundary",
}
REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS = (
    "on_action_hook_linkage",
    "listener_scope_availability",
    "selected_ritual_trigger_linkage",
    "row_state_handoff_boundary",
    "source_target_boundary_still_blocked",
)
REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS = (
    "missing real listener integration source generator",
    "missing war scope persistence contract",
    "missing Alhambra row-state write contract",
    "no verified source write contract",
)
REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS = {
    "preview_only",
    "preview_family",
    "artifact_kind",
    "pilot_key",
    "wonder_key",
    "row_set_key",
    "entity_refs",
    "future_source_target_path",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
    "blocks_source_writer",
    "blocker_reasons",
    "source_ready",
    "source_body_preview",
    "contract_status",
}
REPEATED_ENTITY_ROW_EVENT_SOURCE_PREVIEW_REQUIRED_FIELDS = (
    REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS
    | {
        "event_id_evidence_sources",
        "event_id_evidence",
        "node_event_id_evidence",
        "preview_event_id",
        "preview_node_key",
        "preview_node_kind",
        "option_effect_handoff",
        "row_state_writes_allowed",
        "tooltip_heavy_finalization_allowed",
        "source_ready_allowed",
    }
)
REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_PREVIEW_REQUIRED_FIELDS = (
    REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS
    | {
        "required_languages",
        "missing_bilingual_coverage_allowed",
        "loc_key_namespace",
        "loc_key_plan",
        "loc_line_policy",
        "loc_line_policy_probe",
        "unsafe_quote_newline_handling_allowed",
    }
)
REPEATED_ENTITY_ROW_EFFECT_SOURCE_PREVIEW_REQUIRED_FIELDS = (
    REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS
    | {
        "future_effect_name_plan",
        "row_entity_refs",
        "aggregate_projection_refs",
        "aggregate_projection_boundary",
        "handoff_responsibility",
        "row_state_writes_allowed",
        "effect_body_writes_allowed",
        "source_ready_allowed",
    }
)
REPEATED_ENTITY_ROW_CLEANUP_SOURCE_PREVIEW_REQUIRED_FIELDS = (
    REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS
    | {
        "cleanup_scope_plan",
        "cleanup_coverage",
        "row_entity_refs",
        "aggregate_projection_refs",
        "aggregate_projection_boundary",
        "effect_body_writes_allowed",
        "source_ready_allowed",
    }
)
REPEATED_ENTITY_ROW_TRIGGER_SOURCE_PREVIEW_REQUIRED_FIELDS = (
    REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS
    | {
        "future_trigger_name_plan",
        "eligibility_condition_group_plan",
        "row_completion_condition_group_plan",
        "tooltip_safe_condition_group_plan",
        "aggregate_projection_refs",
        "aggregate_boundary",
        "trigger_body_writes_allowed",
        "tooltip_safe_unsafe_write_paths_allowed",
        "source_ready_allowed",
    }
)
REPEATED_ENTITY_ROW_GUI_SOURCE_PREVIEW_REQUIRED_FIELDS = (
    REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS
    | {
        "fixed_row_widget_plan",
        "per_row_variable_binding_plan",
        "row_entity_refs",
        "tooltip_localization_linkage",
        "gui_event_key_linkage",
        "aggregate_projection_refs",
        "aggregate_projection_boundary",
        "aggregate_only_display_allowed",
        "gui_source_body_allowed",
        "gui_source_writes_allowed",
        "row_state_writes_allowed",
        "source_ready_allowed",
    }
)
REPEATED_ENTITY_ROW_LISTENER_SOURCE_PREVIEW_REQUIRED_FIELDS = (
    REPEATED_ENTITY_ROW_SOURCE_PREVIEW_REQUIRED_FIELDS
    | {
        "on_action_target_path_plan",
        "on_action_hook_linkage_plan",
        "selected_ritual_trigger_linkage",
        "war_scope_availability_persistence_plan",
        "row_state_handoff_boundary",
        "listener_body_allowed",
        "listener_scope_writes_allowed",
        "war_scope_writes_allowed",
        "source_writes_allowed",
        "source_ready_allowed",
    }
)
REPEATED_ENTITY_ROW_SOURCE_WRITER_READINESS_REQUIRED_EVIDENCE_FIELDS = {
    "status",
    "evidence_type",
    "summary",
    "paths",
    "anchors",
    "blockers",
}
REPEATED_ENTITY_ROW_SOURCE_WRITER_READINESS_EVIDENCE_FIELDS = {
    "eu5_syntax_evidence",
    "generator_ownership_evidence",
    "source_target_boundary_evidence",
    "validation_coverage_evidence",
    "lifecycle_semantics_evidence",
}
REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_CONTRACT_EVIDENCE_REQUIRED_FIELDS = {
    "contract_evidence_only",
    "artifact_kind",
    "contract_family",
    "target_path",
    "target_paths",
    "owner_generator",
    "owner_generator_candidate",
    "eu5_syntax_evidence",
    "validation_refs",
    "validation_command",
    "verification_commands",
    "source_writer_blocker_reasons",
    "source_writer_still_blocked_reason",
    "source_target_boundary",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
}
REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS = (
    r"C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\test_unique_wonder_ritual_harness.py",
    r"C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\validate.py --changed --fix --ai-report",
)
REPEATED_ENTITY_ROW_SOURCE_WRITER_READINESS_REQUIRED_FIELDS = {
    "artifact_kind",
    "contract_family",
    "pilot_key",
    "row_set_key",
    "current_contract_status",
    "preview_exists",
    "readiness_status",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
    "unresolved_writer_blockers",
    "no_write_source_writer_contract_evidence",
} | REPEATED_ENTITY_ROW_SOURCE_WRITER_READINESS_EVIDENCE_FIELDS
REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS = {
    "event": 32,
    "localization": 40,
    "effect": 40,
    "cleanup": 32,
    "trigger": 24,
    "gui": 8,
    "listener": 1,
}
REPEATED_ENTITY_ROW_SOURCE_BUNDLE_EXPECTED_PILOTS = (
    "unique_dome_of_the_rock",
    "unique_alhambra",
    "unique_st_peters_basilica",
    "unique_bank_of_saint_george",
)
REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES = tuple(
    REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS
)
REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS = {
    "contract_only": True,
    "body_emitted": False,
    "source_ready": False,
    "may_write_src": False,
    "writes_src": False,
    "source_writer_allowed": False,
}
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT = "unique_alhambra"
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT = 45
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_FLAGS = {
    "candidate_only": True,
    **REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS,
}
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS = {
    "english": "src/main_menu/localization/english/tv_wonder_unique_alhambra_ritual_l_english.yml",
    "simp_chinese": "src/main_menu/localization/simp_chinese/tv_wonder_unique_alhambra_ritual_l_simp_chinese.yml",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS = (
    "src/in_game/events/tv_wonder_unique_alhambra_ritual_events.txt",
    "src/in_game/common/scripted_effects/tv_wonder_unique_alhambra_ritual_effects.txt",
    "src/in_game/common/scripted_triggers/tv_wonder_unique_alhambra_ritual_triggers.txt",
    "src/in_game/gui/panels/organization/tv_wonder_unique_alhambra_ritual.gui",
    "src/in_game/common/on_action/tv_wonder_unique_alhambra_ritual_on_actions.txt",
    REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS["english"],
    REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS["simp_chinese"],
)
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_ALLOWED_STATUSES = {
    "blocked",
    "interface_candidate",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_GENERATOR_CONTRACT_ALLOWED_STATUSES = {
    "blocked",
    "contract_drafted",
}
REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_TARGET_PATH = (
    "src/in_game/events/tv_wonder_unique_alhambra_ritual_events.txt"
)
REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_FAMILY = "event"
REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_STATUS = "dry_run_contract_artifacts"
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_PATH = (
    "src/in_game/common/scripted_effects/tv_wonder_unique_alhambra_ritual_effects.txt"
)
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_FAMILY = (
    "scripted_effect_cleanup"
)
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_FAMILIES = (
    "cleanup",
    "effect",
)
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_STATUS = (
    REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_STATUS
)
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_TARGET_PATH = (
    "src/in_game/common/scripted_triggers/tv_wonder_unique_alhambra_ritual_triggers.txt"
)
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_FAMILY = "trigger"
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_STATUS = (
    REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_STATUS
)
REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_TARGET_PATHS = (
    REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS["english"],
    REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS["simp_chinese"],
)
REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_FAMILY = "localization"
REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_STATUS = (
    REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_STATUS
)
REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS = {
    "pilot_key",
    "family",
    "target_path",
    "owner_generator",
    "interface_name",
    "call_signature",
    "input_contract",
    "output_contract",
    "output_kind",
    "artifact_count",
    "source_file_contract_artifact_count",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "dry_run",
    "dry_run_required",
    "source_file_level_contract",
    "source_generator_interface_prototype_only",
    "event_family_only",
    "memory_report_only",
    "contract_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS = {
    "pilot_key",
    "family",
    "families",
    "target_path",
    "owner_generator",
    "interface_name",
    "call_signature",
    "input_contract",
    "output_contract",
    "output_kind",
    "artifact_count",
    "source_file_contract_artifact_count",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "dry_run",
    "dry_run_required",
    "source_file_level_contract",
    "source_generator_interface_prototype_only",
    "scripted_effect_cleanup_target_only",
    "memory_report_only",
    "contract_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS = {
    "pilot_key",
    "family",
    "target_path",
    "owner_generator",
    "interface_name",
    "call_signature",
    "input_contract",
    "output_contract",
    "output_kind",
    "artifact_count",
    "source_file_contract_artifact_count",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "dry_run",
    "dry_run_required",
    "source_file_level_contract",
    "source_generator_interface_prototype_only",
    "scripted_trigger_target_only",
    "memory_report_only",
    "contract_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
}
REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS = {
    "pilot_key",
    "family",
    "localization_language",
    "target_path",
    "owner_generator",
    "interface_name",
    "call_signature",
    "input_contract",
    "output_contract",
    "output_kind",
    "artifact_count",
    "source_file_contract_artifact_count",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "localization_language_boundary",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "dry_run",
    "dry_run_required",
    "source_file_level_contract",
    "source_generator_interface_prototype_only",
    "localization_family_only",
    "memory_report_only",
    "contract_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
}
REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS = {
    "artifact_key",
    "artifact_index",
    "artifact_kind",
    "pilot_key",
    "family",
    "row_set_key",
    "target_path",
    "future_source_target_path",
    "owner_generator",
    "generator_interface_status",
    "output_kind",
    "output_is_loadable_source",
    "source_file_contract_artifact_only",
    "source_generator_interface_prototype_only",
    "event_family_only",
    "memory_report_only",
    "dry_run",
    "dry_run_required",
    "contract_only",
    "candidate_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
    "source_body_candidate_ref",
    "source_body_candidate_ref_key",
    "source_body_candidate_ref_provenance",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "input_data_shape",
    "output_artifact_family",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "unresolved_writer_blockers",
    "no_write_source_writer_contract_evidence",
}
REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS = {
    "artifact_key",
    "artifact_index",
    "artifact_kind",
    "pilot_key",
    "family",
    "localization_language",
    "row_set_key",
    "target_path",
    "future_source_target_path",
    "source_candidate_future_target_path",
    "owner_generator",
    "generator_interface_status",
    "output_kind",
    "output_is_loadable_source",
    "source_file_contract_artifact_only",
    "source_generator_interface_prototype_only",
    "localization_family_only",
    "memory_report_only",
    "dry_run",
    "dry_run_required",
    "contract_only",
    "candidate_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
    "source_body_candidate_ref",
    "source_body_candidate_ref_key",
    "source_body_candidate_ref_provenance",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "localization_language_boundary",
    "input_data_shape",
    "output_artifact_family",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "unresolved_writer_blockers",
    "no_write_source_writer_contract_evidence",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS = {
    "artifact_key",
    "artifact_index",
    "artifact_kind",
    "pilot_key",
    "family",
    "row_set_key",
    "target_path",
    "future_source_target_path",
    "owner_generator",
    "generator_interface_status",
    "output_kind",
    "output_is_loadable_source",
    "source_file_contract_artifact_only",
    "source_generator_interface_prototype_only",
    "scripted_trigger_target_only",
    "memory_report_only",
    "dry_run",
    "dry_run_required",
    "contract_only",
    "candidate_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
    "source_body_candidate_ref",
    "source_body_candidate_ref_key",
    "source_body_candidate_ref_provenance",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "input_data_shape",
    "output_artifact_family",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "unresolved_writer_blockers",
    "no_write_source_writer_contract_evidence",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS = {
    "artifact_key",
    "artifact_index",
    "artifact_kind",
    "pilot_key",
    "family",
    "interface_family",
    "target_families",
    "row_set_key",
    "target_path",
    "future_source_target_path",
    "owner_generator",
    "generator_interface_status",
    "output_kind",
    "output_is_loadable_source",
    "source_file_contract_artifact_only",
    "source_generator_interface_prototype_only",
    "scripted_effect_cleanup_target_only",
    "memory_report_only",
    "dry_run",
    "dry_run_required",
    "contract_only",
    "candidate_only",
    "body_emitted",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
    "source_body_candidate_ref",
    "source_body_candidate_ref_key",
    "source_body_candidate_ref_provenance",
    "source_generator_contract_ref",
    "source_file_validation_evidence_ref",
    "generator_interface_draft",
    "input_data_shape",
    "output_artifact_family",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "unresolved_writer_blockers",
    "no_write_source_writer_contract_evidence",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_REQUIRED_FIELDS = {
    "target_path",
    "families",
    "artifact_count",
    "source_file_preview_ref",
    "syntax_reference_paths",
    "generator_ownership_candidate",
    "source_target_boundary",
    "validation_requirements",
    "unresolved_blockers",
    "candidate_only",
    "contract_only",
    "source_ready",
    "body_emitted",
    "may_write_src",
    "writes_src",
    "source_writer_allowed",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_GENERATOR_CONTRACT_REQUIRED_FIELDS = {
    "target_path",
    "families",
    "artifact_count",
    "evidence_pack_ref",
    "source_body_candidate_ref_provenance",
    "owner_generator",
    "generator_interface_status",
    "planned_source_writer_exists",
    "generator_interface_draft",
    "input_data_shape",
    "output_artifact_family",
    "verification_commands",
    "source_writer_blocker_reasons",
    "source_writer_still_blocked_reason",
    "no_write_source_writer_contract_evidence",
    "source_target_boundary",
    "required_validations",
    "remaining_blockers",
    "source_ready",
    "verified",
    "backend_ready",
    "source_writer_allowed",
    "may_write_src",
    "writes_src",
}
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_REF_KEY_FIELDS = (
    "family",
    "row_set_key",
    "artifact_kind",
    "future_source_target_path",
)
REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA = {
    "src/in_game/events/tv_wonder_unique_alhambra_ritual_events.txt": {
        "families": ("event",),
        "artifact_count": 8,
        "owner_candidate": "unique_wonder_ritual_event_source_generator",
        "syntax_reference_paths": (
            "src/in_game/events/tv_wonder_unique_pharos_lighthouse_ritual_events.txt",
            "src/in_game/events/tv_wonder_unique_hagia_sophia_ritual_events.txt",
            "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py",
            "scripts/in_game/events/gen_tv_wonder_unique_hagia_sophia_ritual_events.py",
        ),
    },
    "src/in_game/common/scripted_effects/tv_wonder_unique_alhambra_ritual_effects.txt": {
        "families": ("cleanup", "effect"),
        "artifact_count": 18,
        "owner_candidate": "unique_wonder_ritual_scripted_effect_source_generator",
        "syntax_reference_paths": (
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt",
            "src/in_game/common/scripted_effects/tv_wonder_index_effects.txt",
            "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
            "scripts/in_game/common/scripted_effects/gen_tv_wonder_index_effects.py",
        ),
    },
    "src/in_game/common/scripted_triggers/tv_wonder_unique_alhambra_ritual_triggers.txt": {
        "families": ("trigger",),
        "artifact_count": 6,
        "owner_candidate": "unique_wonder_ritual_scripted_trigger_source_generator",
        "syntax_reference_paths": (
            "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt",
            "src/in_game/common/scripted_triggers/tv_wonder_construction_event_triggers.txt",
            "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py",
            "scripts/in_game/common/scripted_triggers/gen_tv_wonder_construction_event_triggers.py",
        ),
    },
    "src/in_game/gui/panels/organization/tv_wonder_unique_alhambra_ritual.gui": {
        "families": ("gui",),
        "artifact_count": 2,
        "owner_candidate": "unique_wonder_ritual_gui_row_source_generator",
        "syntax_reference_paths": (
            "src/in_game/gui/panels/organization/tv_engineering_department.gui",
            "src/in_game/gui/panels/organization/tv_trade_league.gui",
            "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
            "scripts/in_game/gui/panels/organization/merge_tv_engineering_department_wonder_mechanics_gui.py",
        ),
    },
    "src/in_game/common/on_action/tv_wonder_unique_alhambra_ritual_on_actions.txt": {
        "families": ("listener",),
        "artifact_count": 1,
        "owner_candidate": "unique_wonder_ritual_listener_integration_source_generator",
        "syntax_reference_paths": (
            "src/in_game/common/on_action/tv_engineering_department_on_action.txt",
            "src/in_game/common/on_action/tv_pulse_bridges.txt",
            "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt",
            "scripts/in_game/common/on_action/gen_tv_pulse_registry.py",
        ),
    },
    REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS["english"]: {
        "families": ("localization",),
        "artifact_count": 10,
        "owner_candidate": "unique_wonder_ritual_localization_source_generator",
        "syntax_reference_paths": (
            "src/main_menu/localization/english/tv_engineering_department_wonder_mechanics_l_english.yml",
            "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
            "scripts/wonder_localization_lib.py",
        ),
    },
    REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS["simp_chinese"]: {
        "families": ("localization",),
        "artifact_count": 10,
        "owner_candidate": "unique_wonder_ritual_localization_source_generator",
        "syntax_reference_paths": (
            "src/main_menu/localization/simp_chinese/tv_engineering_department_wonder_mechanics_l_simp_chinese.yml",
            "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py",
            "scripts/wonder_localization_lib.py",
        ),
    },
}
REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS = ("english", "simp_chinese")
REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUP_BY_ARTIFACT_KIND = {
    "localization_row_labels": "row_labels",
    "localization_status_text": "status_text",
    "localization_incident_text": "incident_text",
    "localization_tooltips": "tooltips",
    "localization_summary_text": "summary_text",
}
REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUPS = (
    "row_labels",
    "status_text",
    "incident_text",
    "tooltips",
    "summary_text",
)
REPEATED_ENTITY_ROW_EVENT_PREVIEW_NODE_INDEX = {
    "event_opening_skeleton": 0,
    "event_update_skeleton": 1,
    "event_retry_skeleton": 2,
    "event_resolve_skeleton": 3,
}
REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_CLEANUP_SCOPES = {
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
REPEATED_ENTITY_ROW_SOURCE_PREVIEW_CLEANUP_COVERAGE_SCOPES = (
    "completion",
    "failure",
    "ownership_loss",
    "ritual_reset",
)
REPEATED_ENTITY_ROW_SOURCE_EVIDENCE_BY_ARTIFACT_KIND = {
    "event_opening_skeleton": {
        "eu5_source_syntax_pattern": (
            "country_event skeleton declares namespace-owned event id, type, title, desc, image/outcome, "
            "and opening option localization; option effects must hand row initialization to scripted effects."
        ),
        "evidence_source_paths": [
            "src/in_game/events/tv_wonder_unique_pharos_lighthouse_ritual_events.txt:8",
            "src/in_game/events/tv_wonder_unique_pharos_lighthouse_ritual_events.txt:27",
            "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:112",
            "scripts/allocate_unique_wonder_ritual_event_ids.py:33",
        ],
        "generator_candidate": "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py",
        "generator_missing_reason": (
            "Candidate only: existing generated Pharos opening-style events and the allocator prove event id, "
            "title/desc/option localization, and option-effect syntax, but repeated-row event ID ownership and "
            "event source file target ownership are still unassigned. Opening events must hand row-state writes "
            "to scripted effects/triggers and cannot carry unsafe hidden executor or tooltip behavior."
        ),
        "evidence_status": "interface_candidate",
    },
    "event_update_skeleton": {
        "eu5_source_syntax_pattern": (
            "country_event update skeleton uses localized title/desc/option keys, optional immediate scope refresh, "
            "and option effect calls that update row state through scripted-effect handoff."
        ),
        "evidence_source_paths": [
            "src/in_game/events/tv_wonder_unique_pharos_lighthouse_ritual_events.txt:35",
            "src/in_game/events/tv_wonder_unique_pharos_lighthouse_ritual_events.txt:41",
            "src/in_game/events/tv_wonder_unique_pharos_lighthouse_ritual_events.txt:52",
            "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:72",
            "scripts/in_game/events/gen_tv_wonder_construction_events.py:154",
        ],
        "generator_candidate": "scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py",
        "generator_missing_reason": (
            "Candidate only: Pharos and construction event generators prove update-event syntax, localization "
            "linkage, and option effect handoff, but no generic repeated-row event generator owns per-row update "
            "event IDs or target files. Update events must delegate row-state effects/triggers and keep tooltip "
            "and hidden executor safety outside player-facing option text."
        ),
        "evidence_status": "interface_candidate",
    },
    "event_retry_skeleton": {
        "eu5_source_syntax_pattern": (
            "country_event retry skeleton uses primary and retry option blocks with localized option keys; retry "
            "option effects call dedicated scripted effects instead of embedding row-state reset logic."
        ),
        "evidence_source_paths": [
            "src/in_game/events/tv_wonder_unique_hagia_sophia_ritual_events.txt:8",
            "src/in_game/events/tv_wonder_unique_hagia_sophia_ritual_events.txt:16",
            "src/in_game/events/tv_wonder_unique_hagia_sophia_ritual_events.txt:21",
            "scripts/in_game/events/gen_tv_wonder_unique_hagia_sophia_ritual_events.py:38",
            "scripts/in_game/events/gen_tv_wonder_construction_events.py:129",
        ],
        "generator_candidate": "scripts/in_game/events/gen_tv_wonder_unique_hagia_sophia_ritual_events.py",
        "generator_missing_reason": (
            "Candidate only: generated Hagia retry options prove retry option localization and effect-call syntax, "
            "but repeated-row retry event ownership, event ID allocation, and event file targets remain contract-only. "
            "Retry events must hand failure/reset state to scripted effects/triggers and avoid unsafe tooltip or "
            "hidden executor work in option bodies."
        ),
        "evidence_status": "interface_candidate",
    },
    "event_resolve_skeleton": {
        "eu5_source_syntax_pattern": (
            "country_event resolve/finalization skeleton uses localized title/desc/option keys, visible option "
            "effects, and hidden_effect dispatch for non-tooltip-safe final executor handoff."
        ),
        "evidence_source_paths": [
            "src/in_game/events/tv_wonder_finalization_events.txt:8",
            "src/in_game/events/tv_wonder_finalization_events.txt:25",
            "src/in_game/events/tv_wonder_finalization_events.txt:42",
            "scripts/in_game/events/gen_tv_wonder_finalization_events.py:99",
            "scripts/in_game/events/gen_tv_wonder_finalization_events.py:119",
            "scripts/in_game/events/gen_tv_wonder_finalization_events.py:164",
        ],
        "generator_candidate": "scripts/in_game/events/gen_tv_wonder_finalization_events.py",
        "generator_missing_reason": (
            "Candidate only: finalization events prove resolve-event localization, option effects, and hidden "
            "executor dispatch boundaries, but repeated-row resolve event IDs and source targets are not owned. "
            "Resolve events must hand completion row-state effects/triggers to their source families and keep "
            "hidden executor work out of tooltip/player-facing pre-evaluation paths."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_trigger_row_completion": {
        "eu5_source_syntax_pattern": (
            "scripted_trigger row-completion checks use has_variable/NOT has_variable and var comparisons, "
            "with OR aggregation for pending rows and selected ritual completion dispatch."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt:29786",
            "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt:29984",
            "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt:30323",
            "scripts/wonder_unique_rituals/pharos.py:352",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py",
        "generator_missing_reason": (
            "Candidate only: generated Pharos and selected-ritual completion triggers prove syntax, "
            "but no generic repeated-row trigger writer maps arbitrary design_ir row completion states."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_trigger_eligibility": {
        "eu5_source_syntax_pattern": (
            "scripted_trigger eligibility blocks combine reusable activation triggers with variable comparisons "
            "and scope checks before event or row selection."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_triggers/tv_wonder_construction_event_triggers.txt:8",
            "src/in_game/common/scripted_triggers/tv_wonder_construction_event_triggers.txt:13",
            "scripts/in_game/common/scripted_triggers/gen_tv_wonder_construction_event_triggers.py:123",
            "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py:523",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_triggers/gen_tv_wonder_construction_event_triggers.py",
        "generator_missing_reason": (
            "Candidate only: construction-event eligibility generation proves trigger syntax, "
            "but not ownership or validation for repeated-row ritual eligibility."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_trigger_tooltip_safe_condition_group": {
        "eu5_source_syntax_pattern": (
            "scripted_trigger condition groups can wrap player-facing requirements in custom_tooltip blocks "
            "while preserving scope-safe variable and nested condition checks."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_triggers/towards_victory_triggers.txt:12",
            "src/in_game/common/scripted_triggers/towards_victory_triggers.txt:16",
            "src/in_game/common/scripted_triggers/towards_victory_triggers.txt:462",
            "src/in_game/common/scripted_triggers/towards_victory_triggers.txt:478",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py",
        "generator_missing_reason": (
            "Candidate only: existing tooltip-safe trigger syntax is reusable evidence, "
            "but no repeated-row trigger generator emits validated tooltip-safe condition groups."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_effect_row_init": {
        "eu5_source_syntax_pattern": (
            "scripted_effect body guarded by selected ritual id, followed by set_variable row-state initialization."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:8008",
            "scripts/wonder_unique_rituals/pharos.py:141",
            "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py:1677",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: existing ritual generator proves bespoke row initialization patterns, "
            "but no repeated-row source-writer contract maps arbitrary design_ir row sets to loadable effects."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_effect_row_state_write": {
        "eu5_source_syntax_pattern": (
            "scripted_effect branch writes per-row variables with set_variable after row-specific limits."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:408",
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:494",
            "scripts/wonder_unique_rituals/pharos.py:111",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: Pharos row-state writes are generated for one bespoke ritual, not for the "
            "four repeated-row pilot schemas or their cleanup lifecycle."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_effect_aggregate_refresh": {
        "eu5_source_syntax_pattern": (
            "scripted_effect recomputes display/aggregate variables from per-row state and is called after row writes."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:63",
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:384",
            "scripts/wonder_unique_rituals/pharos.py:134",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: existing aggregate refresh is ritual-specific and does not prove a generic "
            "aggregate refresh interface for tracked_entity_sets."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_effect_branch_write": {
        "eu5_source_syntax_pattern": (
            "scripted_effect uses if/else_if/random_list branches to write row progress and schedule branch events."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:8019",
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:8043",
            "scripts/wonder_unique_rituals/pharos.py:227",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: branch writes exist for bespoke ritual events, but source-target boundaries "
            "and validation for arbitrary row-set branches are not assigned."
        ),
        "evidence_status": "interface_candidate",
    },
    "scripted_effect_cleanup_write": {
        "eu5_source_syntax_pattern": (
            "scripted_effect cleanup removes row variables with remove_variable and resets runtime state."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:7913",
            "src/in_game/common/scripted_effects/tv_engineering_department_wonder_mechanics_effects.txt:6",
            "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py:1591",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: existing cleanup proves syntax for generated ritual runtime variables, "
            "but not complete cleanup ownership for each repeated-row pilot row set."
        ),
        "evidence_status": "interface_candidate",
    },
    "cleanup_completion": {
        "eu5_source_syntax_pattern": (
            "completion flow applies ritual completion effects, clears runtime variables, and enters finalization cleanup."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:11028",
            "src/in_game/common/scripted_effects/tv_wonder_finalization_effects.txt:17",
            "scripts/in_game/common/scripted_effects/gen_tv_wonder_finalization_effects.py:245",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: completion cleanup exists for current ritual/finalization flow, but the "
            "source writer has no verified row-set completion contract."
        ),
        "evidence_status": "interface_candidate",
    },
    "cleanup_failure": {
        "eu5_source_syntax_pattern": (
            "failure or retry-failure paths reset progress/runtime variables with set_variable/remove_variable, "
            "and selected ritual runtime cleanup clears row variables before restart or finalization."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:1097",
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:1184",
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:767",
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:7913",
            "scripts/wonder_unique_rituals/pharos.py:258",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: existing Hagia retry and Pharos re-roll/runtime cleanup prove adjacent failure "
            "cleanup syntax, but no generic repeated-row abort/failure cleanup writer or lifecycle tests exist."
        ),
        "evidence_status": "interface_candidate",
    },
    "cleanup_ownership_loss": {
        "eu5_source_syntax_pattern": (
            "ownership-loss event/effect probes retained same-wonder ownership, removes unique ritual map entries when lost."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ownership_effects.txt:11",
            "src/in_game/common/scripted_effects/tv_wonder_ownership_effects.txt:1506",
            "src/in_game/events/tv_wonder_ownership_events.txt:2145",
            "scripts/in_game/common/scripted_effects/gen_tv_wonder_ownership_effects.py:178",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ownership_effects.py",
        "generator_missing_reason": (
            "Candidate only: completed-wonder ownership cleanup is generated, but repeated-row ritual row "
            "ownership-loss cleanup has no assigned source target or tests."
        ),
        "evidence_status": "interface_candidate",
    },
    "cleanup_ritual_reset": {
        "eu5_source_syntax_pattern": (
            "ritual reset clears selected ritual runtime variables and finalization hidden effects clear project state."
        ),
        "evidence_source_paths": [
            "src/in_game/common/scripted_effects/tv_wonder_ritual_effects.txt:7913",
            "src/in_game/common/scripted_effects/tv_wonder_finalization_effects.txt:2452",
            "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py:1905",
        ],
        "generator_candidate": "scripts/in_game/common/scripted_effects/gen_tv_wonder_ritual_effects.py",
        "generator_missing_reason": (
            "Candidate only: reset cleanup exists for ritual/project runtime state, but not as a verified "
            "generic row-set reset contract."
        ),
        "evidence_status": "interface_candidate",
    },
    "gui_checklist_row": {
        "eu5_source_syntax_pattern": (
            "GUI checklist rows use fixed generated widget/hbox rows, visibility expressions over player-scope "
            "variables, localized status text keys, and per-row state styling. Aggregate projection variables are "
            "display summaries only; a repeated-row GUI source interface must preserve design_ir.tracked_entity_sets "
            "row keys, entity labels, and per-row variable semantics."
        ),
        "evidence_source_paths": [
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6265",
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6281",
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6340",
            "scripts/wonder_unique_rituals/pharos.py:486",
            "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py:681",
            "scripts/in_game/gui/panels/organization/merge_tv_engineering_department_wonder_mechanics_gui.py:10",
        ],
        "generator_candidate": "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
        "generator_missing_reason": (
            "Candidate only: Pharos proves generated repeated-row widget syntax, localized status labels, and "
            "per-row variable reads for one bespoke route checklist/status display, but no generic GUI fragment "
            "generator maps arbitrary design_ir.tracked_entity_sets checklist rows to loadable GUI source. The "
            "future generator must keep per-row semantics instead of reading only aggregate projection variables."
        ),
        "evidence_status": "interface_candidate",
    },
    "gui_incident_log_row": {
        "eu5_source_syntax_pattern": (
            "GUI incident-log rows use fixed generated row widgets with per-row visible/hidden state, localized "
            "incident/status text, and variable-driven success/failure coloring. Existing evidence is pattern-level "
            "only; incident rows must retain design_ir.tracked_entity_sets row identities and cannot be collapsed "
            "to aggregate projection variables."
        ),
        "evidence_source_paths": [
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6335",
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6340",
            "src/in_game/gui/panels/organization/tv_engineering_department.gui:8493",
            "src/in_game/gui/panels/organization/tv_engineering_department.gui:8498",
            "scripts/wonder_unique_rituals/pharos.py:486",
            "scripts/wonder_unique_rituals/pharos.py:543",
        ],
        "generator_candidate": "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
        "generator_missing_reason": (
            "Candidate only: generated Pharos rows prove incident/status row rendering patterns, but they do not "
            "assign a generic source target, loc-key contract, or validation layer for arbitrary repeated-row "
            "incident logs. The future GUI fragment generator must bind each design_ir row and its failure/retry "
            "branch semantics, not only an aggregate status projection."
        ),
        "evidence_status": "interface_candidate",
    },
    "gui_actor_slots_row": {
        "eu5_source_syntax_pattern": (
            "GUI actor-slot rows use generated widgets with portrait_standard_head_button, action_button_diamond, "
            "actor/action metadata, visibility expressions, and localized waiting/active/done text keys. Actor-slot "
            "source generation must preserve per-row actor candidate semantics from design_ir.tracked_entity_sets."
        ),
        "evidence_source_paths": [
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6755",
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6758",
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6764",
            "data/generated_fragments/tv_engineering_department_wonder_mechanics.gui:6787",
            "src/in_game/gui/panels/organization/tv_engineering_department.gui:8913",
            "scripts/wonder_unique_rituals/hagia.py:363",
        ],
        "generator_candidate": "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
        "generator_missing_reason": (
            "Candidate only: Hagia proves actor portrait/action slot syntax for a bespoke ritual, but no generic "
            "GUI fragment generator owns repeated actor-slot rows, per-candidate role/quality/risk bindings, or "
            "row validation for future repeated-row pilots. Aggregate projection variables cannot replace the "
            "design_ir.tracked_entity_sets actor candidate rows."
        ),
        "evidence_status": "interface_candidate",
    },
    "localization_row_labels": {
        "eu5_source_syntax_pattern": (
            "Localization row labels use key:0 quoted strings in English and Simplified Chinese YAML files, with "
            "source text originating from canonical localization data or design_ir row labels. Current evidence "
            "proves bilingual loc syntax and row-label inputs, not a repeated-row loc source writer."
        ),
        "evidence_source_paths": [
            "data/unique_wonder_ritual_specs.yaml:1317",
            "data/unique_wonder_ritual_specs.yaml:3416",
            "data/unique_wonder_ritual_specs.yaml:7553",
            "data/unique_wonder_ritual_specs.yaml:14969",
            "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py:30",
            "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py:30",
        ],
        "generator_candidate": "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
        "generator_missing_reason": (
            "Candidate only: design_ir exposes repeated-row display names and the current bilingual localization "
            "generators prove output syntax, but no repeated-row localization generator owns stable row-label key "
            "naming, English/Simplified Chinese source boundaries, or coverage validation for arbitrary row sets."
        ),
        "evidence_status": "interface_candidate",
    },
    "localization_status_text": {
        "eu5_source_syntax_pattern": (
            "Status localization uses generated YAML loc lines with language headers, key:0 quoted values, and "
            "English/Simplified Chinese canonical data. Existing status keys prove source syntax and bilingual "
            "boundaries, but repeated-row status text remains contract-only."
        ),
        "evidence_source_paths": [
            "data/wonder_localization.yaml:5077",
            "data/wonder_localization.yaml:5094",
            "data/wonder_localization.yaml:5110",
            "data/wonder_localization.yaml:5127",
            "data/wonder_localization.yaml:11126",
            "scripts/wonder_mechanics/_core.py:1688",
        ],
        "generator_candidate": "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
        "generator_missing_reason": (
            "Candidate only: canonical English and Simplified Chinese status strings plus loc_line generation "
            "prove YAML/BOM/quote-safe output boundaries, but no repeated-row source writer maps every "
            "design_ir state value to loadable status localization keys."
        ),
        "evidence_status": "interface_candidate",
    },
    "localization_incident_text": {
        "eu5_source_syntax_pattern": (
            "Incident localization uses event title/description/option and GUI incident status keys emitted as "
            "quoted YAML loc lines for English and Simplified Chinese. Existing text proves bilingual syntax, not "
            "row-set incident-log source readiness."
        ),
        "evidence_source_paths": [
            "data/wonder_localization.yaml:5078",
            "data/wonder_localization.yaml:5102",
            "data/wonder_localization.yaml:5120",
            "data/wonder_localization.yaml:5128",
            "data/wonder_localization.yaml:11127",
            "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py:42",
        ],
        "generator_candidate": "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py",
        "generator_missing_reason": (
            "Candidate only: existing bilingual incident and branch text proves localization source syntax and "
            "encoding boundaries, but the source-plan still lacks a generator contract for one incident text set "
            "per design_ir row, retry/failure branch, and row-set summary."
        ),
        "evidence_status": "interface_candidate",
    },
    "localization_tooltips": {
        "eu5_source_syntax_pattern": (
            "Tooltip localization uses generated key:0 quoted values referenced by GUI title/description fields "
            "and tooltip/action loc keys. Current loc_line escaping handles quotes and newlines, while generators "
            "write UTF-8 with BOM; repeated-row tooltip key ownership is still unassigned."
        ),
        "evidence_source_paths": [
            "data/wonder_localization.yaml:1930",
            "data/wonder_localization.yaml:1996",
            "data/wonder_localization.yaml:2128",
            "data/wonder_localization.yaml:2384",
            "scripts/wonder_mechanics/_core.py:1672",
            "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py:42",
        ],
        "generator_candidate": "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
        "generator_missing_reason": (
            "Candidate only: existing tooltip/action localization and generator escaping prove YAML quoting, "
            "newline escaping, and BOM output behavior, but no repeated-row localization generator owns tooltip "
            "keys for row labels, row states, failure reasons, or GUI action descriptions."
        ),
        "evidence_status": "interface_candidate",
    },
    "localization_summary_text": {
        "eu5_source_syntax_pattern": (
            "Summary localization uses generated event/GUI summary loc keys in English and Simplified Chinese "
            "YAML, with canonical data expanded by the localization library. Existing summary text proves source "
            "syntax and bilingual boundaries, not repeated-row source writer readiness."
        ),
        "evidence_source_paths": [
            "data/wonder_localization.yaml:5057",
            "data/wonder_localization.yaml:5107",
            "data/wonder_localization.yaml:5124",
            "data/wonder_localization.yaml:5315",
            "src/main_menu/localization/english/tv_engineering_department_wonder_mechanics_l_english.yml:4651",
            "scripts/wonder_localization_lib.py:578",
        ],
        "generator_candidate": "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
        "generator_missing_reason": (
            "Candidate only: generated summary/news localization proves the English and Simplified Chinese source "
            "boundary, but repeated-row summary loc still needs row-set key ownership, coverage tests, and source "
            "target assignment before any source writer can be allowed."
        ),
        "evidence_status": "interface_candidate",
    },
    "listener_war_integration": {
        "eu5_source_syntax_pattern": (
            "Hardcoded war on_actions are bridged through the pulse registry into TV-owned Engineering "
            "Department ritual on_actions; those on_actions call selected-ritual scripted triggers for "
            "pre_winning_war/ending_war and dispatch completion through hidden_effect. This proves only an "
            "Alhambra war-listener interface candidate, not generator-owned Alhambra source code or row-state "
            "writes."
        ),
        "evidence_source_paths": [
            "data/pulse_registry.yaml:112-117",
            "scripts/in_game/common/on_action/gen_tv_pulse_registry.py:47-48",
            "src/in_game/common/on_action/tv_pulse_bridges.txt:170-181",
            "src/in_game/common/on_action/tv_engineering_department_on_action.txt:270-293",
            "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt:30311",
            "src/in_game/common/scripted_triggers/tv_engineering_department_wonder_mechanics_triggers.txt:30317",
            "data/unique_wonder_ritual_specs.yaml:3231-3243",
        ],
        "generator_candidate": "scripts/in_game/common/on_action/gen_tv_pulse_registry.py",
        "generator_missing_reason": (
            "Candidate only: the existing pulse registry, on_action bridge, scripted listener triggers, and "
            "completion hidden_effect prove that a war-listener interface exists for Alhambra semantics, but "
            "they do not assign source writer ownership, validate the source-target boundary for an Alhambra "
            "listener artifact, or define the Alhambra row-state write contract for treaty clauses, palace "
            "risk rows, failure routing, and reward-branch state."
        ),
        "evidence_status": "interface_candidate",
    },
}
REPEATED_ENTITY_ROW_SOURCE_PLAN_BLOCKER_ARTIFACTS = {
    "missing_cleanup": [
        "scripted_effect_cleanup_write",
        "cleanup_completion",
        "cleanup_failure",
        "cleanup_ownership_loss",
        "cleanup_ritual_reset",
    ],
    "missing_effect_writer": [
        "scripted_effect_row_init",
        "scripted_effect_row_state_write",
        "scripted_effect_aggregate_refresh",
        "scripted_effect_branch_write",
        "scripted_effect_cleanup_write",
    ],
    "missing_event_ownership": [
        "event_opening_skeleton",
        "event_update_skeleton",
        "event_retry_skeleton",
        "event_resolve_skeleton",
    ],
    "missing_gui_rows": ["gui_actor_slots_row", "gui_checklist_row", "gui_incident_log_row"],
    "missing_listener_integration": ["listener_war_integration"],
    "missing_loc_rows": [
        "localization_row_labels",
        "localization_status_text",
        "localization_incident_text",
        "localization_tooltips",
        "localization_summary_text",
    ],
    "missing_row_variables": [
        "scripted_effect_row_init",
        "scripted_effect_row_state_write",
        "scripted_trigger_row_completion",
    ],
    "missing_trigger_check": [
        "scripted_trigger_row_completion",
        "scripted_trigger_eligibility",
        "scripted_trigger_tooltip_safe_condition_group",
    ],
}
_ROW_TOKEN_STOPWORDS = {
    "and",
    "binding",
    "checklist",
    "entity",
    "entities",
    "group",
    "incident",
    "log",
    "one",
    "pattern",
    "per",
    "row",
    "rows",
    "should",
    "state",
    "states",
    "status",
    "the",
    "tv",
    "ui",
    "variable",
    "variables",
    "wonder",
}


def _identifier_tokens(value: Any) -> set[str]:
    text = str(value or "").lower()
    raw_tokens = re.split(r"[^a-z0-9]+", text)
    tokens: set[str] = set()
    for token in raw_tokens:
        if not token or token in _ROW_TOKEN_STOPWORDS:
            continue
        tokens.add(token)
        if token.endswith("ies") and len(token) > 4:
            tokens.add(token[:-3] + "y")
        elif token.endswith("s") and len(token) > 3:
            tokens.add(token[:-1])
    return tokens


def _per_entity_variable_patterns(row_set: dict[str, Any]) -> list[str]:
    per_entity_state = row_set.get("per_entity_state")
    if not isinstance(per_entity_state, dict):
        return []
    patterns: list[str] = []
    for key, value in per_entity_state.items():
        value_text = str(value or "").strip()
        if key.endswith("_variable_pattern") or "<" in value_text:
            patterns.append(value_text)
    return [pattern for pattern in patterns if pattern]


def _variable_matches_row_pattern(variable_name: str, pattern: str) -> bool:
    if "<" not in pattern:
        return variable_name == pattern
    regex = re.escape(pattern)
    regex = re.sub(r"<[^>]+>", r"[^_]+(?:_[^_]+)*", regex)
    return re.fullmatch(regex, variable_name) is not None


def _row_set_match_tokens(row_set: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for field in ("key", "entity_type", "ui_binding"):
        tokens.update(_identifier_tokens(row_set.get(field)))
    per_entity_state = row_set.get("per_entity_state")
    if isinstance(per_entity_state, dict):
        for key in per_entity_state:
            tokens.update(_identifier_tokens(key))
    return tokens


def _related_variables_for_row_set(
    row_set: dict[str, Any],
    variables: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    patterns = _per_entity_variable_patterns(row_set)
    row_tokens = _row_set_match_tokens(row_set)
    related: list[dict[str, Any]] = []
    for variable in variables:
        if not isinstance(variable, dict):
            continue
        name = str(variable.get("name", ""))
        if not name:
            continue
        pattern_match = any(_variable_matches_row_pattern(name, pattern) for pattern in patterns)
        token_match = bool(row_tokens & _identifier_tokens(name))
        if pattern_match or token_match:
            related.append(variable)
    return related


def _row_set_ui_type(row_set: dict[str, Any]) -> str:
    ui_binding = str(row_set.get("ui_binding", "") or "")
    if ":" in ui_binding:
        candidate = ui_binding.split(":", 1)[0].strip()
        if candidate:
            return candidate
    return ""


def _ui_bindings_for_variables(
    bindings: list[dict[str, Any]],
    variable_names: set[str],
) -> list[dict[str, Any]]:
    if not variable_names:
        return []
    matched: list[dict[str, Any]] = []
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        refs = set(_string_refs(binding.get("variable_refs")))
        if refs & variable_names:
            matched.append(binding)
    return matched


def _nodes_for_variables(
    nodes: list[dict[str, Any]],
    variable_names: set[str],
) -> list[dict[str, Any]]:
    if not variable_names:
        return []
    matched: list[dict[str, Any]] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        refs = set(_string_refs(node.get("reads"))) | set(_string_refs(node.get("writes")))
        ui_state = node.get("ui_state") if isinstance(node.get("ui_state"), dict) else {}
        refs.update(_string_refs(ui_state.get("variable_refs")))
        if refs & variable_names:
            matched.append(node)
    return matched


def _node_io_summary(nodes: list[dict[str, Any]], variable_names: set[str]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for node in _nodes_for_variables(nodes, variable_names):
        reads = sorted(set(_string_refs(node.get("reads"))) & variable_names)
        writes = sorted(set(_string_refs(node.get("writes"))) & variable_names)
        ui_state = node.get("ui_state") if isinstance(node.get("ui_state"), dict) else {}
        ui_refs = sorted(set(_string_refs(ui_state.get("variable_refs"))) & variable_names)
        summary.append(
            {
                "key": str(node.get("key", "")),
                "kind": str(node.get("kind", "")),
                "capabilities": _string_refs(node.get("capabilities")),
                "reads": reads,
                "writes": writes,
                "ui_state_refs": ui_refs,
            }
        )
    return summary


def _row_set_source_blockers(
    *,
    has_row_variable_patterns: bool,
    has_ui_component: bool,
    cleanup_expectations: list[str],
    listener_backed: bool,
) -> list[str]:
    blockers = {
        "missing_effect_writer",
        "missing_event_ownership",
        "missing_gui_rows",
        "missing_loc_rows",
        "missing_trigger_check",
    }
    if not has_row_variable_patterns:
        blockers.add("missing_row_variables")
    if not has_ui_component:
        blockers.add("missing_gui_rows")
    if not cleanup_expectations:
        blockers.add("missing_cleanup")
    else:
        # Existing Harness cleanup metadata is not a verified loadable EU5 cleanup effect.
        blockers.add("missing_cleanup")
    if listener_backed:
        blockers.add("missing_listener_integration")
    return sorted(blockers)


def repeated_entity_row_preflight_for_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Summarize repeated-row source-compiler readiness without writing source."""

    identity = entry.get("identity") if isinstance(entry.get("identity"), dict) else {}
    key = str(identity.get("key", entry.get("key", "")))
    status = str(identity.get("status", ""))
    design_ir = entry.get("design_ir") if isinstance(entry.get("design_ir"), dict) else {}
    node_graph = entry.get("node_graph") if isinstance(entry.get("node_graph"), dict) else {}
    ui_model = entry.get("ui_model") if isinstance(entry.get("ui_model"), dict) else {}
    nodes = [node for node in node_graph.get("nodes", []) or [] if isinstance(node, dict)]
    variables = [variable for variable in node_graph.get("variables", []) or [] if isinstance(variable, dict)]
    components = [component for component in ui_model.get("components", []) or [] if isinstance(component, dict)]
    bindings = [binding for binding in ui_model.get("bindings", []) or [] if isinstance(binding, dict)]
    repeated_nodes = [
        str(node.get("key", ""))
        for node in nodes
        if REPEATED_ENTITY_ROW_BACKEND in set(_string_refs(node.get("capabilities")))
    ]
    tracked_sets = [
        row_set
        for row_set in design_ir.get("tracked_entity_sets", []) or []
        if isinstance(row_set, dict)
    ]
    component_types = sorted(
        {
            str(component.get("type"))
            for component in components
            if str(component.get("type")) in REPEATED_ENTITY_ROW_UI_COMPONENTS
        }
    )
    row_reports: list[dict[str, Any]] = []
    blocker_summary = {blocker: 0 for blocker in sorted(REPEATED_ENTITY_ROW_BLOCKERS)}
    aggregate_projection_variables: set[str] = set()
    listener_integration_required = False

    for row_set in tracked_sets:
        patterns = _per_entity_variable_patterns(row_set)
        related_variables = _related_variables_for_row_set(row_set, variables)
        related_names = {str(variable.get("name")) for variable in related_variables if variable.get("name")}
        aggregate_projection_variables.update(related_names)
        row_nodes = _nodes_for_variables(nodes, related_names)
        listener_backed = any(str(node.get("kind")) == "listener_gate" for node in row_nodes)
        listener_integration_required = listener_integration_required or listener_backed
        cleanup_expectations = sorted(
            {
                str(variable.get("cleanup"))
                for variable in related_variables
                if str(variable.get("cleanup", "")).strip()
            }
        )
        expected_ui_type = _row_set_ui_type(row_set)
        has_ui_component = bool(expected_ui_type and expected_ui_type in component_types)
        related_bindings = _ui_bindings_for_variables(bindings, related_names)
        blockers = _row_set_source_blockers(
            has_row_variable_patterns=bool(patterns),
            has_ui_component=has_ui_component,
            cleanup_expectations=cleanup_expectations,
            listener_backed=listener_backed,
        )
        for blocker in blockers:
            blocker_summary[blocker] += 1
        entities = row_set.get("entities") if isinstance(row_set.get("entities"), list) else []
        row_reports.append(
            {
                "key": str(row_set.get("key", "")),
                "entity_type": str(row_set.get("entity_type", "")),
                "entity_keys": [
                    str(entity.get("key", ""))
                    for entity in entities
                    if isinstance(entity, dict) and entity.get("key")
                ],
                "state_values": _string_refs(row_set.get("state_values")),
                "per_row_variable_patterns": patterns,
                "selector": str(row_set.get("selector", "") or ""),
                "ui_binding": str(row_set.get("ui_binding", "") or ""),
                "expected_ui_component_type": expected_ui_type,
                "ui_component_present": has_ui_component,
                "cleanup_expectations": cleanup_expectations,
                "aggregate_projection_variables": sorted(related_names),
                "node_read_write_coverage": _node_io_summary(nodes, related_names),
                "node_reads_writes_cover_row_state": any(
                    set(item["reads"]) or set(item["writes"])
                    for item in _node_io_summary(nodes, related_names)
                ),
                "ui_bindings": [
                    {
                        "key": str(binding.get("key", "")),
                        "component_key": str(binding.get("component_key", "")),
                        "variable_refs": _string_refs(binding.get("variable_refs")),
                        "node_refs": _string_refs(binding.get("node_refs")),
                    }
                    for binding in related_bindings
                ],
                "blockers": blockers,
            }
        )

    entity_row_count = sum(len(row_set["entity_keys"]) for row_set in row_reports)
    all_blockers = sorted({blocker for row_set in row_reports for blocker in row_set["blockers"]})
    return {
        "key": key,
        "status": status,
        "uses_repeated_entity_row_backend": bool(repeated_nodes),
        "repeated_backend_nodes": repeated_nodes,
        "row_set_count": len(row_reports),
        "entity_row_count": entity_row_count,
        "row_sets": row_reports,
        "ui_component_types": component_types,
        "ui_bindings_present": [
            str(binding.get("key", ""))
            for binding in bindings
            if set(_string_refs(binding.get("variable_refs"))) & aggregate_projection_variables
        ],
        "aggregate_projection_variables": sorted(aggregate_projection_variables),
        "compression_summary": (
            "design_ir.tracked_entity_sets owns per-row semantics; node_graph.variables currently "
            "summarize those rows through aggregate projection variables and are not a substitute "
            "for source-level per-row state."
        ),
        "aggregate_projection_is_not_row_state": True,
        "listener_integration_required": listener_integration_required,
        "blockers": all_blockers,
        "blocker_summary": {key: count for key, count in blocker_summary.items() if count},
        "source_writer_allowed": False,
    }


def repeated_entity_row_preflight_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
) -> dict[str, Any]:
    statuses = statuses or {"source_codegen_ready"}
    entries = payload.get("unique_wonders", []) or []
    reports: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        identity = entry.get("identity") if isinstance(entry.get("identity"), dict) else {}
        if str(identity.get("status", "")) not in statuses:
            continue
        report = repeated_entity_row_preflight_for_entry(entry)
        if report["uses_repeated_entity_row_backend"] or report["row_set_count"]:
            reports.append(report)

    blocker_summary: dict[str, int] = {}
    for report in reports:
        for blocker, count in report.get("blocker_summary", {}).items():
            blocker_summary[blocker] = blocker_summary.get(blocker, 0) + int(count)
    return {
        "statuses": sorted(statuses),
        "candidate_count": len(reports),
        "row_set_count": sum(int(report["row_set_count"]) for report in reports),
        "entity_row_count": sum(int(report["entity_row_count"]) for report in reports),
        "blocker_summary": dict(sorted(blocker_summary.items())),
        "entries": reports,
        "source_writer_allowed": False,
        "notes": [
            "This is a Harness source-compiler preflight only.",
            "backend_ready repeated-row evidence is intermediate-only and does not permit src writes.",
        ],
    }


def _repeated_row_source_evidence_mapping(
    *,
    artifact_kind: str,
    source_target_boundary: str,
    blocks_source_writer: bool,
) -> dict[str, Any]:
    evidence = REPEATED_ENTITY_ROW_SOURCE_EVIDENCE_BY_ARTIFACT_KIND.get(artifact_kind)
    if evidence is None:
        return {
            "artifact_kind": artifact_kind,
            "eu5_source_syntax_pattern": "not evaluated in this effect/cleanup evidence slice",
            "evidence_source_paths": [],
            "generator_candidate": "",
            "generator_missing_reason": (
                "Evidence mapping is required by the source-plan schema, but this artifact kind is "
                "outside the current scripted effect and cleanup family."
            ),
            "source_target_boundary": source_target_boundary,
            "blocks_source_writer": blocks_source_writer,
        }
    return {
        "artifact_kind": artifact_kind,
        "eu5_source_syntax_pattern": str(evidence["eu5_source_syntax_pattern"]),
        "evidence_source_paths": _string_refs(evidence.get("evidence_source_paths")),
        "generator_candidate": str(evidence.get("generator_candidate", "")),
        "generator_missing_reason": str(evidence["generator_missing_reason"]),
        "source_target_boundary": source_target_boundary,
        "blocks_source_writer": blocks_source_writer,
    }


def _repeated_row_source_plan_evidence_status(artifact_kind: str, default: str) -> str:
    evidence = REPEATED_ENTITY_ROW_SOURCE_EVIDENCE_BY_ARTIFACT_KIND.get(artifact_kind)
    if evidence is None:
        return default
    return str(evidence.get("evidence_status", default))


def _repeated_row_event_contract_wonder_key(pilot_key: str) -> str:
    if pilot_key.startswith("unique_"):
        return pilot_key[len("unique_") :]
    return pilot_key


def _repeated_row_event_source_target_contract(
    *,
    pilot_key: str,
    source_target_boundary: str,
) -> dict[str, Any]:
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    target_path_pattern = "src/in_game/events/tv_wonder_unique_<wonder_key>_ritual_events.txt"
    return {
        "status": "blocked",
        "allowed_statuses": list(REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES),
        "contract_family": "event",
        "namespace_policy": "tv_engineering_department",
        "event_id_sources": ["spec.event_ids", "node_graph.nodes[].event_id"],
        "localization_key_policy": "tv_engineering_department.<event_id>.t/d/a(/b)",
        "future_source_target_path_pattern": target_path_pattern,
        "candidate_future_source_target_path": target_path_pattern.replace("<wonder_key>", wonder_key),
        "future_target_only": True,
        "source_writer_allowed": False,
        "may_write_src": False,
        "row_state_writes_allowed": False,
        "option_effect_handoff_rule": (
            "event artifacts may declare future option/effect handoff only; they cannot inline "
            "row-state writes, effect bodies, trigger bodies, GUI rows, or localization writes"
        ),
        "required_validations": list(REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS),
        "blocker_reasons": list(REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_target_boundary": source_target_boundary,
    }


def _repeated_row_effect_cleanup_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    source_target_boundary: str,
) -> dict[str, Any]:
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    target_path_pattern = "src/in_game/common/scripted_effects/tv_wonder_unique_<wonder_key>_ritual_effects.txt"
    contract_family = "cleanup" if artifact_kind in REPEATED_ENTITY_ROW_CLEANUP_ARTIFACT_KINDS else "effect"
    return {
        "status": "blocked",
        "allowed_statuses": list(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES),
        "contract_family": contract_family,
        "source_type": "common/scripted_effects",
        "future_source_target_path_pattern": target_path_pattern,
        "candidate_future_source_target_path": target_path_pattern.replace("<wonder_key>", wonder_key),
        "future_target_only": True,
        "source_generation_policy": (
            "future target only; not an actual scripted-effect generator and cannot write effect bodies"
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "effect_body_writes_allowed": False,
        "row_state_writes_allowed": False,
        "row_state_write_schema_allowed": False,
        "cleanup_lifecycle_scope": REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_CLEANUP_SCOPES[
            artifact_kind
        ],
        "aggregate_projection_boundary": (
            "aggregate_projection_variables are projection/display variables only and cannot replace "
            "design_ir.tracked_entity_sets row/entity semantics"
        ),
        "required_validations": list(
            REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS
        ),
        "blocker_reasons": list(REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_target_boundary": source_target_boundary,
    }


def _repeated_row_trigger_source_target_contract(
    *,
    pilot_key: str,
    source_target_boundary: str,
) -> dict[str, Any]:
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    target_path_pattern = "src/in_game/common/scripted_triggers/tv_wonder_unique_<wonder_key>_ritual_triggers.txt"
    return {
        "status": "blocked",
        "allowed_statuses": list(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES),
        "contract_family": "trigger",
        "source_type": "common/scripted_triggers",
        "future_source_target_path_pattern": target_path_pattern,
        "candidate_future_source_target_path": target_path_pattern.replace("<wonder_key>", wonder_key),
        "future_target_only": True,
        "source_generation_policy": (
            "future target only; not an actual scripted-trigger generator and cannot write trigger bodies"
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "trigger_body_writes_allowed": False,
        "tooltip_safe_unsafe_write_paths_allowed": False,
        "tooltip_safe_condition_group_policy": (
            "tooltip-safe condition groups may declare future predicate checks only and must not call "
            "unsafe effects, row-state writes, or source write paths"
        ),
        "aggregate_projection_boundary": (
            "aggregate_projection_variables are projection/display variables only and cannot replace "
            "design_ir.tracked_entity_sets row/entity semantics"
        ),
        "required_validations": list(
            REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS
        ),
        "blocker_reasons": list(REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_target_boundary": source_target_boundary,
    }


def _repeated_row_gui_source_target_contract(
    *,
    pilot_key: str,
    source_target_boundary: str,
) -> dict[str, Any]:
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    target_path_pattern = "src/in_game/gui/panels/organization/tv_wonder_unique_<wonder_key>_ritual.gui"
    return {
        "status": "blocked",
        "allowed_statuses": list(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES),
        "contract_family": "gui",
        "source_type": "in_game/gui/panels/organization",
        "future_source_target_path_pattern": target_path_pattern,
        "candidate_future_source_target_path": target_path_pattern.replace("<wonder_key>", wonder_key),
        "future_target_only": True,
        "source_generation_policy": (
            "future target only; not an actual GUI source generator and cannot write GUI source files"
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "blocks_source_writer": True,
        "gui_source_writes_allowed": False,
        "aggregate_only_row_reads_allowed": False,
        "row_state_writes_allowed": False,
        "fixed_row_widget_boundary": (
            "future GUI rows must use fixed row widgets for actor slots, checklist rows, and incident rows; "
            "this contract is only a boundary and emits no widgets"
        ),
        "per_row_variable_binding_policy": (
            "each GUI row must bind design_ir.tracked_entity_sets entity keys and per-row variables; "
            "aggregate-only row reads are forbidden"
        ),
        "actor_checklist_incident_row_policy": (
            "actor, checklist, and incident rows remain distinct row policies and cannot be collapsed into "
            "one aggregate-only display"
        ),
        "tooltip_key_linkage_policy": (
            "tooltips and text keys must link to localization row/status/incident/summary keys and event keys"
        ),
        "aggregate_projection_boundary": (
            "aggregate_projection_variables are summary display variables only and cannot replace "
            "design_ir.tracked_entity_sets row/entity semantics"
        ),
        "required_validations": list(REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS),
        "blocker_reasons": list(REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_target_boundary": source_target_boundary,
    }


def _repeated_row_localization_source_target_contract(
    *,
    pilot_key: str,
    source_target_boundary: str,
) -> dict[str, Any]:
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    target_path_pattern = "src/main_menu/localization/<lang>/tv_wonder_unique_<wonder_key>_ritual_l_<lang>.yml"
    return {
        "status": "blocked",
        "allowed_statuses": list(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES),
        "contract_family": "localization",
        "source_type": "main_menu/localization",
        "future_source_target_path_pattern": target_path_pattern,
        "candidate_future_source_target_path": target_path_pattern.replace("<wonder_key>", wonder_key),
        "future_target_only": True,
        "source_generation_policy": (
            "future target only; not an actual localization source generator and cannot write localization files"
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "blocks_source_writer": True,
        "localization_source_writes_allowed": False,
        "required_languages": ["english", "simp_chinese"],
        "missing_bilingual_coverage_allowed": False,
        "loc_key_namespace_policy": "tv_wonder_unique_<wonder_key>_ritual.<row_set_key>.<artifact_kind>.<entity_key>",
        "loc_line_escaping_bom_policy": (
            "future localization must use loc_line() quote/newline escaping and UTF-8 BOM output for English "
            "and Simplified Chinese files"
        ),
        "unsafe_quote_newline_handling_allowed": False,
        "localization_coverage_policy": (
            "row labels, status text, incident text, tooltips, and summary text require English and "
            "Simplified Chinese coverage"
        ),
        "gui_event_key_linkage_policy": (
            "localization keys must link GUI row/tooltips and event title/description/option text without "
            "authorizing a localization writer"
        ),
        "required_validations": list(
            REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS
        ),
        "blocker_reasons": list(REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_target_boundary": source_target_boundary,
    }


def _repeated_row_listener_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    source_target_boundary: str,
) -> dict[str, Any]:
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    target_path_pattern = "src/in_game/common/on_action/tv_wonder_unique_<wonder_key>_ritual_on_actions.txt"
    return {
        "status": "blocked",
        "allowed_statuses": list(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES),
        "contract_family": "listener",
        "source_type": "common/on_action",
        "future_source_target_path_pattern": target_path_pattern,
        "candidate_future_source_target_path": target_path_pattern.replace("<wonder_key>", wonder_key),
        "future_target_only": True,
        "source_generation_policy": (
            "future target only; not an actual listener integration generator and cannot write on_action bodies"
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "listener_artifact_scope": f"{pilot_key}-only {artifact_kind}",
        "on_action_bridge_policy": (
            "existing on_action bridge remains an interface candidate only; no listener source writer is assigned"
        ),
        "listener_scope_writes_allowed": False,
        "war_scope_writes_allowed": False,
        "row_state_writes_allowed": False,
        "required_validations": list(
            REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS
        ),
        "blocker_reasons": list(REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_target_boundary": source_target_boundary,
    }


def _repeated_row_source_plan_artifact(
    *,
    artifact_kind: str,
    owner_generator: str,
    source_target_boundary: str,
    required_eu5_interfaces: list[str],
    evidence_status: str,
    pilot_key: str,
    row_set_key: str,
    entity_keys: list[str],
    aggregate_projection_variables: list[str],
) -> dict[str, Any]:
    evidence_status = _repeated_row_source_plan_evidence_status(artifact_kind, evidence_status)
    blocks_source_writer = True
    artifact = {
        "artifact_kind": artifact_kind,
        "owner_generator": owner_generator,
        "source_target_boundary": source_target_boundary,
        "required_eu5_interfaces": required_eu5_interfaces,
        "evidence_status": evidence_status,
        "evidence_mapping": _repeated_row_source_evidence_mapping(
            artifact_kind=artifact_kind,
            source_target_boundary=source_target_boundary,
            blocks_source_writer=blocks_source_writer,
        ),
        "may_write_src": False,
        "blocks_source_writer": blocks_source_writer,
        "pilot_key": pilot_key,
        "row_set_key": row_set_key,
        "entity_keys": entity_keys,
        "aggregate_projection_variables": aggregate_projection_variables,
    }
    if artifact_kind in REPEATED_ENTITY_ROW_EVENT_ARTIFACT_KINDS:
        artifact["source_target_contract"] = _repeated_row_event_source_target_contract(
            pilot_key=pilot_key,
            source_target_boundary=source_target_boundary,
        )
    elif artifact_kind in REPEATED_ENTITY_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS:
        artifact["source_target_contract"] = _repeated_row_effect_cleanup_source_target_contract(
            pilot_key=pilot_key,
            artifact_kind=artifact_kind,
            source_target_boundary=source_target_boundary,
        )
    elif artifact_kind in REPEATED_ENTITY_ROW_TRIGGER_ARTIFACT_KINDS:
        artifact["source_target_contract"] = _repeated_row_trigger_source_target_contract(
            pilot_key=pilot_key,
            source_target_boundary=source_target_boundary,
        )
    elif artifact_kind in REPEATED_ENTITY_ROW_GUI_ARTIFACT_KINDS:
        artifact["source_target_contract"] = _repeated_row_gui_source_target_contract(
            pilot_key=pilot_key,
            source_target_boundary=source_target_boundary,
        )
    elif artifact_kind in REPEATED_ENTITY_ROW_LOCALIZATION_ARTIFACT_KINDS:
        artifact["source_target_contract"] = _repeated_row_localization_source_target_contract(
            pilot_key=pilot_key,
            source_target_boundary=source_target_boundary,
        )
    elif artifact_kind in REPEATED_ENTITY_ROW_LISTENER_ARTIFACT_KINDS:
        artifact["source_target_contract"] = _repeated_row_listener_source_target_contract(
            pilot_key=pilot_key,
            artifact_kind=artifact_kind,
            source_target_boundary=source_target_boundary,
        )
    return artifact


def _repeated_row_gui_artifact_kind(row_set: dict[str, Any]) -> str:
    expected_ui_type = str(row_set.get("expected_ui_component_type", "") or "").strip()
    if expected_ui_type:
        return f"gui_{expected_ui_type}_row"
    return "gui_repeated_row"


def _repeated_row_source_plan_artifacts_for_row_set(
    *,
    pilot_key: str,
    row_set: dict[str, Any],
) -> list[dict[str, Any]]:
    row_set_key = str(row_set.get("key", ""))
    entity_keys = _string_refs(row_set.get("entity_keys"))
    aggregate_projection_variables = _string_refs(row_set.get("aggregate_projection_variables"))
    artifacts: list[dict[str, Any]] = []

    for artifact_kind in REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["event"]:
        artifacts.append(
            _repeated_row_source_plan_artifact(
                artifact_kind=artifact_kind,
                owner_generator=REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS["event"],
                source_target_boundary="contract_only_no_event_file_or_event_id_allocation",
                required_eu5_interfaces=["country_event", "event_option", "hidden_effect"],
                evidence_status="missing_eu5_evidence",
                pilot_key=pilot_key,
                row_set_key=row_set_key,
                entity_keys=entity_keys,
                aggregate_projection_variables=aggregate_projection_variables,
            )
        )

    for artifact_kind in REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["effect"]:
        artifacts.append(
            _repeated_row_source_plan_artifact(
                artifact_kind=artifact_kind,
                owner_generator=REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS["effect"],
                source_target_boundary="contract_only_no_scripted_effect_file",
                required_eu5_interfaces=["scripted_effect", "set_variable", "remove_variable", "hidden_effect"],
                evidence_status="interface_candidate",
                pilot_key=pilot_key,
                row_set_key=row_set_key,
                entity_keys=entity_keys,
                aggregate_projection_variables=aggregate_projection_variables,
            )
        )

    for artifact_kind in REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["trigger"]:
        artifacts.append(
            _repeated_row_source_plan_artifact(
                artifact_kind=artifact_kind,
                owner_generator=REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS["trigger"],
                source_target_boundary="contract_only_no_scripted_trigger_file",
                required_eu5_interfaces=["scripted_trigger", "tooltip_safe_trigger", "variable_check"],
                evidence_status="interface_candidate",
                pilot_key=pilot_key,
                row_set_key=row_set_key,
                entity_keys=entity_keys,
                aggregate_projection_variables=aggregate_projection_variables,
            )
        )

    artifacts.append(
        _repeated_row_source_plan_artifact(
            artifact_kind=_repeated_row_gui_artifact_kind(row_set),
            owner_generator=REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS["gui"],
            source_target_boundary="contract_only_no_gui_file",
            required_eu5_interfaces=["gui_repeated_row", "gui_variable_binding", "tooltip"],
            evidence_status="interface_candidate",
            pilot_key=pilot_key,
            row_set_key=row_set_key,
            entity_keys=entity_keys,
            aggregate_projection_variables=aggregate_projection_variables,
        )
    )

    for artifact_kind in REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["localization"]:
        artifacts.append(
            _repeated_row_source_plan_artifact(
                artifact_kind=artifact_kind,
                owner_generator=REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS["localization"],
                source_target_boundary="contract_only_no_localization_file",
                required_eu5_interfaces=["localization_key", "event_text", "gui_tooltip"],
                evidence_status="missing_eu5_evidence",
                pilot_key=pilot_key,
                row_set_key=row_set_key,
                entity_keys=entity_keys,
                aggregate_projection_variables=aggregate_projection_variables,
            )
        )

    for artifact_kind in REPEATED_ENTITY_ROW_SOURCE_PLAN_KIND_GROUPS["cleanup"]:
        artifacts.append(
            _repeated_row_source_plan_artifact(
                artifact_kind=artifact_kind,
                owner_generator=REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS["effect"],
                source_target_boundary="contract_only_no_cleanup_effect_file",
                required_eu5_interfaces=["scripted_effect", "on_completion", "on_failure", "ownership_loss", "reset"],
                evidence_status="missing_eu5_evidence",
                pilot_key=pilot_key,
                row_set_key=row_set_key,
                entity_keys=entity_keys,
                aggregate_projection_variables=aggregate_projection_variables,
            )
        )

    return artifacts


def _repeated_row_source_plan_blocker_contracts(
    blockers: list[str],
    *,
    artifact_kinds: set[str] | None = None,
) -> dict[str, list[str]]:
    artifact_kinds = artifact_kinds or set()
    contracts: dict[str, list[str]] = {}
    for blocker in sorted(set(blockers)):
        planned = list(REPEATED_ENTITY_ROW_SOURCE_PLAN_BLOCKER_ARTIFACTS.get(blocker, []))
        if blocker == "missing_gui_rows":
            planned = sorted(kind for kind in artifact_kinds if kind.startswith("gui_")) or planned
        elif blocker == "missing_listener_integration":
            planned = sorted(kind for kind in artifact_kinds if kind.startswith("listener_")) or planned
        contracts[blocker] = planned
    return contracts


def _repeated_row_source_plan_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    artifact_kind_summary: dict[str, int] = {}
    owner_generator_summary: dict[str, int] = {}
    evidence_status_summary: dict[str, int] = {}
    artifact_count_by_pilot: dict[str, int] = {}
    missing_owner_generators: set[str] = set()
    blocker_contracts: dict[str, set[str]] = {}

    for entry in entries:
        pilot_key = str(entry.get("key", ""))
        artifacts = [artifact for artifact in entry.get("artifacts", []) if isinstance(artifact, dict)]
        artifact_count_by_pilot[pilot_key] = len(artifacts)
        for artifact in artifacts:
            artifact_kind = str(artifact.get("artifact_kind", ""))
            owner_generator = str(artifact.get("owner_generator", ""))
            evidence_status = str(artifact.get("evidence_status", ""))
            artifact_kind_summary[artifact_kind] = artifact_kind_summary.get(artifact_kind, 0) + 1
            owner_generator_summary[owner_generator] = owner_generator_summary.get(owner_generator, 0) + 1
            evidence_status_summary[evidence_status] = evidence_status_summary.get(evidence_status, 0) + 1
            if owner_generator not in REPEATED_ENTITY_ROW_SOURCE_PLAN_EXISTING_GENERATORS:
                missing_owner_generators.add(owner_generator)
        for blocker, artifact_kinds in entry.get("blocker_contracts", {}).items():
            blocker_contracts.setdefault(str(blocker), set()).update(_string_refs(artifact_kinds))

    most_missing_artifact_kinds = [
        key
        for key, _count in sorted(
            artifact_kind_summary.items(),
            key=lambda item: (-item[1], item[0]),
        )[:10]
    ]
    return {
        "artifact_count_by_pilot": dict(sorted(artifact_count_by_pilot.items())),
        "artifact_kind_summary": dict(sorted(artifact_kind_summary.items())),
        "most_missing_artifact_kinds": most_missing_artifact_kinds,
        "owner_generator_summary": dict(sorted(owner_generator_summary.items())),
        "missing_owner_generators": sorted(missing_owner_generators),
        "evidence_status_summary": dict(sorted(evidence_status_summary.items())),
        "blocker_contracts": {
            blocker: sorted(artifact_kinds)
            for blocker, artifact_kinds in sorted(blocker_contracts.items())
        },
    }


def repeated_entity_row_source_plan_for_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Produce a repeated-row source-plan contract without assigning source outputs."""

    preflight = repeated_entity_row_preflight_for_entry(entry)
    artifacts: list[dict[str, Any]] = []
    row_set_reports: list[dict[str, Any]] = []
    listener_artifacts: list[dict[str, Any]] = []
    for row_set in preflight.get("row_sets", []):
        if not isinstance(row_set, dict):
            continue
        row_artifacts = _repeated_row_source_plan_artifacts_for_row_set(
            pilot_key=str(preflight.get("key", "")),
            row_set=row_set,
        )
        if (
            preflight.get("key") == "unique_alhambra"
            and "missing_listener_integration" in set(_string_refs(row_set.get("blockers")))
        ):
            listener_artifact = _repeated_row_source_plan_artifact(
                artifact_kind="listener_war_integration",
                owner_generator=REPEATED_ENTITY_ROW_SOURCE_PLAN_OWNER_GENERATORS["listener"],
                source_target_boundary="contract_only_no_on_action_or_listener_file",
                required_eu5_interfaces=["on_action", "war_listener", "listener_scope_bridge"],
                evidence_status="interface_candidate",
                pilot_key=str(preflight.get("key", "")),
                row_set_key=str(row_set.get("key", "")),
                entity_keys=_string_refs(row_set.get("entity_keys")),
                aggregate_projection_variables=_string_refs(row_set.get("aggregate_projection_variables")),
            )
            row_artifacts.append(listener_artifact)
            listener_artifacts.append(listener_artifact)
        artifacts.extend(row_artifacts)
        row_set_reports.append(
            {
                "key": str(row_set.get("key", "")),
                "entity_keys": _string_refs(row_set.get("entity_keys")),
                "aggregate_projection_variables": _string_refs(row_set.get("aggregate_projection_variables")),
                "artifact_count": len(row_artifacts),
                "artifact_kinds": [str(artifact["artifact_kind"]) for artifact in row_artifacts],
                "artifacts": row_artifacts,
            }
        )

    blocker_contracts = _repeated_row_source_plan_blocker_contracts(
        _string_refs(preflight.get("blockers")),
        artifact_kinds={str(artifact.get("artifact_kind", "")) for artifact in artifacts},
    )
    return {
        "key": str(preflight.get("key", "")),
        "status": str(preflight.get("status", "")),
        "row_set_count": int(preflight.get("row_set_count", 0)),
        "entity_row_count": int(preflight.get("entity_row_count", 0)),
        "artifact_count": len(artifacts),
        "row_sets": row_set_reports,
        "listener_artifacts": listener_artifacts,
        "artifacts": artifacts,
        "artifact_kind_summary": _count_by_key(artifacts, "artifact_kind"),
        "owner_generator_summary": _count_by_key(artifacts, "owner_generator"),
        "missing_owner_generators": sorted(
            {
                str(artifact.get("owner_generator", ""))
                for artifact in artifacts
                if str(artifact.get("owner_generator", "")) not in REPEATED_ENTITY_ROW_SOURCE_PLAN_EXISTING_GENERATORS
            }
        ),
        "blockers": _string_refs(preflight.get("blockers")),
        "blocker_contracts": blocker_contracts,
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "notes": [
            "This is a source-plan contract only; it assigns no loadable EU5 source targets.",
            "Every artifact blocks the future source writer until exact EU5 interfaces and generator ownership are verified.",
            "Aggregate node_graph variables remain lossy projections and do not replace design_ir row state.",
        ],
    }


def _count_by_key(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key, ""))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _validate_repeated_row_event_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    missing = _missing_required(contract, REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if missing:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing field(s): {', '.join(missing)}"
        )
        return errors
    extra = sorted(set(contract) - REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if extra:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract has unsupported field(s): "
            f"{', '.join(extra)}"
        )

    allowed_statuses = set(REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES)
    declared_allowed_statuses = set(_string_refs(contract.get("allowed_statuses")))
    if declared_allowed_statuses != allowed_statuses or "source-ready" in declared_allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract allowed_statuses must be "
            "no-write, candidate, blocked"
        )
    status = str(contract.get("status", ""))
    if status == "source-ready":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract status must not be source-ready")
    elif status not in allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract status must be "
            "no-write, candidate, or blocked"
        )

    expected_path_pattern = "src/in_game/events/tv_wonder_unique_<wonder_key>_ritual_events.txt"
    expected_path = expected_path_pattern.replace("<wonder_key>", _repeated_row_event_contract_wonder_key(pilot_key))
    if contract.get("contract_family") != "event":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract contract_family must be event")
    if contract.get("namespace_policy") != "tv_engineering_department":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract namespace_policy changed")
    if _string_refs(contract.get("event_id_sources")) != ["spec.event_ids", "node_graph.nodes[].event_id"]:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract event_id_sources changed")
    if contract.get("localization_key_policy") != "tv_engineering_department.<event_id>.t/d/a(/b)":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract localization_key_policy changed")
    if contract.get("future_source_target_path_pattern") != expected_path_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract future path pattern changed")
    if contract.get("candidate_future_source_target_path") != expected_path:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract candidate future path changed")
    if contract.get("future_target_only") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract must declare future_target_only: true")
    if contract.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_writer_allowed must be false")
    if contract.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract may_write_src must be false")
    if contract.get("row_state_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract row_state_writes_allowed must be false"
        )
    if str(contract.get("source_target_boundary", "")) != str(artifact.get("source_target_boundary", "")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract boundary mismatch")

    handoff_rule = str(contract.get("option_effect_handoff_rule", "")).lower()
    if "future option/effect handoff only" not in handoff_rule or "cannot inline row-state writes" not in handoff_rule:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract handoff rule is incomplete")
    required_validations = set(_string_refs(contract.get("required_validations")))
    missing_validations = sorted(
        set(REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS) - required_validations
    )
    if missing_validations:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing validation(s): "
            f"{', '.join(missing_validations)}"
        )
    blocker_reasons = set(_string_refs(contract.get("blocker_reasons")))
    missing_blockers = sorted(
        set(REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS) - blocker_reasons
    )
    if missing_blockers:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing blocker reason(s): "
            f"{', '.join(missing_blockers)}"
        )
    return errors


def _validate_repeated_row_effect_cleanup_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    missing = _missing_required(contract, REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if missing:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing field(s): {', '.join(missing)}"
        )
        return errors
    extra = sorted(set(contract) - REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if extra:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract has unsupported field(s): "
            f"{', '.join(extra)}"
        )

    allowed_statuses = set(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES)
    declared_allowed_statuses = set(_string_refs(contract.get("allowed_statuses")))
    if declared_allowed_statuses != allowed_statuses or "source-ready" in declared_allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract allowed_statuses must be "
            "no-write, candidate, blocked"
        )
    status = str(contract.get("status", ""))
    if status == "source-ready":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract status must not be source-ready")
    elif status not in allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract status must be "
            "no-write, candidate, or blocked"
        )

    expected_family = "cleanup" if artifact_kind in REPEATED_ENTITY_ROW_CLEANUP_ARTIFACT_KINDS else "effect"
    expected_path_pattern = "src/in_game/common/scripted_effects/tv_wonder_unique_<wonder_key>_ritual_effects.txt"
    expected_path = expected_path_pattern.replace("<wonder_key>", _repeated_row_event_contract_wonder_key(pilot_key))
    if contract.get("contract_family") != expected_family:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract contract_family must be {expected_family}"
        )
    if contract.get("source_type") != "common/scripted_effects":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_type changed")
    if contract.get("future_source_target_path_pattern") != expected_path_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract future path pattern changed")
    if contract.get("candidate_future_source_target_path") != expected_path:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract candidate future path changed")
    if contract.get("future_target_only") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract must declare future_target_only: true")
    source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
    if "future target only" not in source_generation_policy or "not an actual scripted-effect generator" not in source_generation_policy:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract source_generation_policy is incomplete"
        )
    if contract.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_writer_allowed must be false")
    if contract.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract may_write_src must be false")
    if contract.get("effect_body_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract effect_body_writes_allowed must be false"
        )
    if contract.get("row_state_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract row_state_writes_allowed must be false"
        )
    if contract.get("row_state_write_schema_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract row_state_write_schema_allowed must be false"
        )
    expected_cleanup_scope = REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_CLEANUP_SCOPES[artifact_kind]
    if contract.get("cleanup_lifecycle_scope") != expected_cleanup_scope:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract cleanup lifecycle scope changed")
    aggregate_boundary = str(contract.get("aggregate_projection_boundary", "")).lower()
    if (
        "aggregate_projection_variables" not in aggregate_boundary
        or "cannot replace" not in aggregate_boundary
        or "design_ir.tracked_entity_sets" not in aggregate_boundary
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract aggregate projection boundary is incomplete"
        )
    if str(contract.get("source_target_boundary", "")) != str(artifact.get("source_target_boundary", "")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract boundary mismatch")

    required_validations = set(_string_refs(contract.get("required_validations")))
    missing_validations = sorted(
        set(REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS) - required_validations
    )
    if missing_validations:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing validation(s): "
            f"{', '.join(missing_validations)}"
        )
    blocker_reasons = set(_string_refs(contract.get("blocker_reasons")))
    missing_blockers = sorted(
        set(REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS) - blocker_reasons
    )
    if missing_blockers:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing blocker reason(s): "
            f"{', '.join(missing_blockers)}"
        )
    return errors


def _validate_repeated_row_trigger_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    missing = _missing_required(contract, REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if missing:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing field(s): {', '.join(missing)}"
        )
        return errors
    extra = sorted(set(contract) - REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if extra:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract has unsupported field(s): "
            f"{', '.join(extra)}"
        )

    allowed_statuses = set(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES)
    declared_allowed_statuses = set(_string_refs(contract.get("allowed_statuses")))
    if declared_allowed_statuses != allowed_statuses or "source-ready" in declared_allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract allowed_statuses must be "
            "no-write, candidate, blocked"
        )
    status = str(contract.get("status", ""))
    if status == "source-ready":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract status must not be source-ready")
    elif status not in allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract status must be "
            "no-write, candidate, or blocked"
        )

    expected_path_pattern = "src/in_game/common/scripted_triggers/tv_wonder_unique_<wonder_key>_ritual_triggers.txt"
    expected_path = expected_path_pattern.replace("<wonder_key>", _repeated_row_event_contract_wonder_key(pilot_key))
    if contract.get("contract_family") != "trigger":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract contract_family must be trigger")
    if contract.get("source_type") != "common/scripted_triggers":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_type changed")
    if contract.get("future_source_target_path_pattern") != expected_path_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract future path pattern changed")
    if contract.get("candidate_future_source_target_path") != expected_path:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract candidate future path changed")
    if contract.get("future_target_only") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract must declare future_target_only: true")
    source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
    if (
        "future target only" not in source_generation_policy
        or "not an actual scripted-trigger generator" not in source_generation_policy
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract source_generation_policy is incomplete"
        )
    if contract.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_writer_allowed must be false")
    if contract.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract may_write_src must be false")
    if contract.get("trigger_body_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract trigger_body_writes_allowed must be false"
        )
    if contract.get("tooltip_safe_unsafe_write_paths_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract "
            "tooltip_safe_unsafe_write_paths_allowed must be false"
        )
    tooltip_policy = str(contract.get("tooltip_safe_condition_group_policy", "")).lower()
    if "tooltip-safe condition groups" not in tooltip_policy or "must not call unsafe" not in tooltip_policy:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract tooltip-safe policy is incomplete"
        )
    aggregate_boundary = str(contract.get("aggregate_projection_boundary", "")).lower()
    if (
        "aggregate_projection_variables" not in aggregate_boundary
        or "cannot replace" not in aggregate_boundary
        or "design_ir.tracked_entity_sets" not in aggregate_boundary
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract aggregate projection boundary is incomplete"
        )
    if str(contract.get("source_target_boundary", "")) != str(artifact.get("source_target_boundary", "")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract boundary mismatch")

    required_validations = set(_string_refs(contract.get("required_validations")))
    missing_validations = sorted(
        set(REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS) - required_validations
    )
    if missing_validations:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing validation(s): "
            f"{', '.join(missing_validations)}"
        )
    blocker_reasons = set(_string_refs(contract.get("blocker_reasons")))
    missing_blockers = sorted(
        set(REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS) - blocker_reasons
    )
    if missing_blockers:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing blocker reason(s): "
            f"{', '.join(missing_blockers)}"
        )
    return errors


def _validate_repeated_row_gui_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    missing = _missing_required(contract, REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if missing:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing field(s): {', '.join(missing)}"
        )
        return errors
    extra = sorted(set(contract) - REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if extra:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract has unsupported field(s): "
            f"{', '.join(extra)}"
        )

    allowed_statuses = set(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES)
    declared_allowed_statuses = set(_string_refs(contract.get("allowed_statuses")))
    if declared_allowed_statuses != allowed_statuses or "source-ready" in declared_allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract allowed_statuses must be "
            "no-write, candidate, blocked"
        )
    status = str(contract.get("status", ""))
    if status == "source-ready":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract status must not be source-ready")
    elif status not in allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract status must be "
            "no-write, candidate, or blocked"
        )

    expected_path_pattern = "src/in_game/gui/panels/organization/tv_wonder_unique_<wonder_key>_ritual.gui"
    expected_path = expected_path_pattern.replace("<wonder_key>", _repeated_row_event_contract_wonder_key(pilot_key))
    if contract.get("contract_family") != "gui":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract contract_family must be gui")
    if contract.get("source_type") != "in_game/gui/panels/organization":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_type changed")
    if contract.get("future_source_target_path_pattern") != expected_path_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract future path pattern changed")
    if contract.get("candidate_future_source_target_path") != expected_path:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract candidate future path changed")
    if contract.get("future_target_only") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract must declare future_target_only: true")
    source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
    if "future target only" not in source_generation_policy or "not an actual gui source generator" not in source_generation_policy:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract source_generation_policy is incomplete"
        )
    if contract.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_writer_allowed must be false")
    if contract.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract may_write_src must be false")
    if contract.get("blocks_source_writer") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract blocks_source_writer must be true")
    if contract.get("gui_source_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract gui_source_writes_allowed must be false"
        )
    if contract.get("aggregate_only_row_reads_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract "
            "aggregate_only_row_reads_allowed must be false"
        )
    if contract.get("row_state_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract row_state_writes_allowed must be false"
        )
    fixed_boundary = str(contract.get("fixed_row_widget_boundary", "")).lower()
    if "fixed row widgets" not in fixed_boundary or "actor slots" not in fixed_boundary or "checklist" not in fixed_boundary or "incident" not in fixed_boundary:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract fixed row widget boundary is incomplete")
    per_row_policy = str(contract.get("per_row_variable_binding_policy", "")).lower()
    if (
        "design_ir.tracked_entity_sets" not in per_row_policy
        or "per-row variables" not in per_row_policy
        or "aggregate-only row reads are forbidden" not in per_row_policy
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract per-row variable binding policy is incomplete"
        )
    row_policy = str(contract.get("actor_checklist_incident_row_policy", "")).lower()
    if "actor" not in row_policy or "checklist" not in row_policy or "incident" not in row_policy or "aggregate-only" not in row_policy:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract actor/checklist/incident row policy is incomplete"
        )
    tooltip_policy = str(contract.get("tooltip_key_linkage_policy", "")).lower()
    if "tooltip" not in tooltip_policy or "localization" not in tooltip_policy or "event keys" not in tooltip_policy:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract tooltip/key linkage policy is incomplete")
    aggregate_boundary = str(contract.get("aggregate_projection_boundary", "")).lower()
    if (
        "aggregate_projection_variables" not in aggregate_boundary
        or "cannot replace" not in aggregate_boundary
        or "design_ir.tracked_entity_sets" not in aggregate_boundary
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract aggregate projection boundary is incomplete"
        )
    if str(contract.get("source_target_boundary", "")) != str(artifact.get("source_target_boundary", "")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract boundary mismatch")

    required_validations = set(_string_refs(contract.get("required_validations")))
    missing_validations = sorted(
        set(REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS) - required_validations
    )
    if missing_validations:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing validation(s): "
            f"{', '.join(missing_validations)}"
        )
    blocker_reasons = set(_string_refs(contract.get("blocker_reasons")))
    missing_blockers = sorted(
        set(REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS) - blocker_reasons
    )
    if missing_blockers:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing blocker reason(s): "
            f"{', '.join(missing_blockers)}"
        )
    return errors


def _validate_repeated_row_localization_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    missing = _missing_required(contract, REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if missing:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing field(s): {', '.join(missing)}"
        )
        return errors
    extra = sorted(set(contract) - REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if extra:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract has unsupported field(s): "
            f"{', '.join(extra)}"
        )

    allowed_statuses = set(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES)
    declared_allowed_statuses = set(_string_refs(contract.get("allowed_statuses")))
    if declared_allowed_statuses != allowed_statuses or "source-ready" in declared_allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract allowed_statuses must be "
            "no-write, candidate, blocked"
        )
    status = str(contract.get("status", ""))
    if status == "source-ready":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract status must not be source-ready")
    elif status not in allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract status must be "
            "no-write, candidate, or blocked"
        )

    expected_path_pattern = "src/main_menu/localization/<lang>/tv_wonder_unique_<wonder_key>_ritual_l_<lang>.yml"
    expected_path = expected_path_pattern.replace("<wonder_key>", _repeated_row_event_contract_wonder_key(pilot_key))
    if contract.get("contract_family") != "localization":
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract contract_family must be localization"
        )
    if contract.get("source_type") != "main_menu/localization":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_type changed")
    if contract.get("future_source_target_path_pattern") != expected_path_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract future path pattern changed")
    if contract.get("candidate_future_source_target_path") != expected_path:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract candidate future path changed")
    if contract.get("future_target_only") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract must declare future_target_only: true")
    source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
    if (
        "future target only" not in source_generation_policy
        or "not an actual localization source generator" not in source_generation_policy
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract source_generation_policy is incomplete"
        )
    if contract.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_writer_allowed must be false")
    if contract.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract may_write_src must be false")
    if contract.get("blocks_source_writer") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract blocks_source_writer must be true")
    if contract.get("localization_source_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract "
            "localization_source_writes_allowed must be false"
        )
    if set(_string_refs(contract.get("required_languages"))) != {"english", "simp_chinese"}:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract must declare English and Simplified Chinese coverage"
        )
    if contract.get("missing_bilingual_coverage_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing_bilingual_coverage_allowed must be false"
        )
    namespace_policy = str(contract.get("loc_key_namespace_policy", "")).lower()
    if (
        "tv_wonder_unique_<wonder_key>_ritual" not in namespace_policy
        or "<row_set_key>" not in namespace_policy
        or "<entity_key>" not in namespace_policy
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract loc key namespace policy is incomplete")
    escaping_policy = str(contract.get("loc_line_escaping_bom_policy", "")).lower()
    if (
        "loc_line()" not in escaping_policy
        or "quote/newline escaping" not in escaping_policy
        or "utf-8 bom" not in escaping_policy
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract loc_line escaping/BOM policy is incomplete"
        )
    if contract.get("unsafe_quote_newline_handling_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract "
            "unsafe_quote_newline_handling_allowed must be false"
        )
    coverage_policy = str(contract.get("localization_coverage_policy", "")).lower()
    for coverage_phrase in ("row labels", "status text", "incident text", "tooltips", "summary text"):
        if coverage_phrase not in coverage_policy:
            errors.append(
                f"{pilot_key}: artifact {artifact_kind} source_target_contract localization coverage policy is incomplete"
            )
            break
    linkage_policy = str(contract.get("gui_event_key_linkage_policy", "")).lower()
    if "gui" not in linkage_policy or "event" not in linkage_policy or "without authorizing" not in linkage_policy:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract GUI/event key linkage policy is incomplete")
    if str(contract.get("source_target_boundary", "")) != str(artifact.get("source_target_boundary", "")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract boundary mismatch")

    required_validations = set(_string_refs(contract.get("required_validations")))
    missing_validations = sorted(
        set(REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS) - required_validations
    )
    if missing_validations:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing validation(s): "
            f"{', '.join(missing_validations)}"
        )
    blocker_reasons = set(_string_refs(contract.get("blocker_reasons")))
    missing_blockers = sorted(
        set(REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS) - blocker_reasons
    )
    if missing_blockers:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing blocker reason(s): "
            f"{', '.join(missing_blockers)}"
        )
    return errors


def _validate_repeated_row_listener_source_target_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    contract: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    missing = _missing_required(contract, REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if missing:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing field(s): {', '.join(missing)}"
        )
        return errors
    extra = sorted(set(contract) - REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_REQUIRED_FIELDS)
    if extra:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract has unsupported field(s): "
            f"{', '.join(extra)}"
        )

    allowed_statuses = set(REPEATED_ENTITY_ROW_SOURCE_TARGET_CONTRACT_ALLOWED_STATUSES)
    declared_allowed_statuses = set(_string_refs(contract.get("allowed_statuses")))
    if declared_allowed_statuses != allowed_statuses or "source-ready" in declared_allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract allowed_statuses must be "
            "no-write, candidate, blocked"
        )
    status = str(contract.get("status", ""))
    if status == "source-ready":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract status must not be source-ready")
    elif status not in allowed_statuses:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract status must be "
            "no-write, candidate, or blocked"
        )

    expected_path_pattern = "src/in_game/common/on_action/tv_wonder_unique_<wonder_key>_ritual_on_actions.txt"
    expected_path = expected_path_pattern.replace("<wonder_key>", _repeated_row_event_contract_wonder_key(pilot_key))
    if pilot_key != "unique_alhambra" or artifact_kind != "listener_war_integration":
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract listener must be Alhambra-only"
        )
    if contract.get("contract_family") != "listener":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract contract_family must be listener")
    if contract.get("source_type") != "common/on_action":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_type changed")
    if contract.get("future_source_target_path_pattern") != expected_path_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract future path pattern changed")
    if contract.get("candidate_future_source_target_path") != expected_path:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract candidate future path changed")
    if contract.get("future_target_only") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract must declare future_target_only: true")
    source_generation_policy = str(contract.get("source_generation_policy", "")).lower()
    if (
        "future target only" not in source_generation_policy
        or "not an actual listener integration generator" not in source_generation_policy
    ):
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract source_generation_policy is incomplete"
        )
    if contract.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract source_writer_allowed must be false")
    if contract.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract may_write_src must be false")
    if contract.get("listener_artifact_scope") != "unique_alhambra-only listener_war_integration":
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract listener scope changed")
    bridge_policy = str(contract.get("on_action_bridge_policy", "")).lower()
    if "interface candidate only" not in bridge_policy or "no listener source writer" not in bridge_policy:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract on_action bridge policy is incomplete"
        )
    if contract.get("listener_scope_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract listener_scope_writes_allowed must be false"
        )
    if contract.get("war_scope_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract war_scope_writes_allowed must be false"
        )
    if contract.get("row_state_writes_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract row_state_writes_allowed must be false"
        )
    if str(contract.get("source_target_boundary", "")) != str(artifact.get("source_target_boundary", "")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} source_target_contract boundary mismatch")

    required_validations = set(_string_refs(contract.get("required_validations")))
    missing_validations = sorted(
        set(REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_REQUIRED_VALIDATIONS) - required_validations
    )
    if missing_validations:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing validation(s): "
            f"{', '.join(missing_validations)}"
        )
    blocker_reasons = set(_string_refs(contract.get("blocker_reasons")))
    missing_blockers = sorted(
        set(REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS) - blocker_reasons
    )
    if missing_blockers:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} source_target_contract missing blocker reason(s): "
            f"{', '.join(missing_blockers)}"
        )
    return errors


def validate_repeated_entity_row_source_plan(plan: dict[str, Any]) -> list[str]:
    """Validate the repeated-row source-plan schema and safety contract."""

    errors: list[str] = []
    entries = plan.get("entries") if isinstance(plan.get("entries"), list) else [plan]
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("source-plan entry must be a mapping")
            continue
        pilot_key = str(entry.get("key", "<unknown>"))
        if entry.get("source_writer_allowed") is not False:
            errors.append(f"{pilot_key}: source_writer_allowed must be false")
        row_sets = [row_set for row_set in entry.get("row_sets", []) or [] if isinstance(row_set, dict)]
        artifacts = [artifact for artifact in entry.get("artifacts", []) or [] if isinstance(artifact, dict)]
        row_set_keys = {str(row_set.get("key", "")) for row_set in row_sets if row_set.get("key")}
        artifact_row_set_keys = {
            str(artifact.get("row_set_key", ""))
            for artifact in artifacts
            if str(artifact.get("row_set_key", "")) != "__pilot_listener__"
        }
        missing_row_sets = sorted(row_set_keys - artifact_row_set_keys)
        for row_set_key in missing_row_sets:
            errors.append(f"{pilot_key}: row set {row_set_key} has no source-plan artifacts")

        for row_set in row_sets:
            row_set_key = str(row_set.get("key", ""))
            row_artifacts = [
                artifact
                for artifact in artifacts
                if str(artifact.get("row_set_key", "")) == row_set_key
            ]
            row_artifact_kinds = {str(artifact.get("artifact_kind", "")) for artifact in row_artifacts}
            if not any(kind.startswith("scripted_effect_") for kind in row_artifact_kinds):
                errors.append(f"{pilot_key}: row set {row_set_key} missing effect artifact")
            if not any(kind.startswith("scripted_trigger_") for kind in row_artifact_kinds):
                errors.append(f"{pilot_key}: row set {row_set_key} missing trigger artifact")
            if not any(kind.startswith("gui_") for kind in row_artifact_kinds):
                errors.append(f"{pilot_key}: row set {row_set_key} missing GUI artifact")
            if not any(kind.startswith("localization_") for kind in row_artifact_kinds):
                errors.append(f"{pilot_key}: row set {row_set_key} missing localization artifact")
            if not any(kind.startswith("cleanup_") for kind in row_artifact_kinds):
                errors.append(f"{pilot_key}: row set {row_set_key} missing cleanup artifact")

        for artifact in artifacts:
            missing = _missing_required(artifact, REPEATED_ENTITY_ROW_SOURCE_PLAN_ARTIFACT_REQUIRED_FIELDS)
            artifact_kind = str(artifact.get("artifact_kind", "<unknown>"))
            if missing:
                errors.append(f"{pilot_key}: artifact {artifact_kind} missing field(s): {', '.join(missing)}")
                continue
            allowed_artifact_fields = (
                REPEATED_ENTITY_ROW_SOURCE_PLAN_ARTIFACT_REQUIRED_FIELDS
                | REPEATED_ENTITY_ROW_SOURCE_PLAN_ARTIFACT_OPTIONAL_FIELDS
            )
            extra = sorted(set(artifact) - allowed_artifact_fields)
            if extra:
                errors.append(f"{pilot_key}: artifact {artifact_kind} has unsupported field(s): {', '.join(extra)}")
            if not str(artifact.get("owner_generator", "")).strip():
                errors.append(f"{pilot_key}: artifact {artifact_kind} must declare owner_generator")
            if artifact.get("may_write_src") is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} must declare may_write_src: false")
            if artifact.get("blocks_source_writer") is not True:
                errors.append(f"{pilot_key}: artifact {artifact_kind} must declare blocks_source_writer: true")
            if str(artifact.get("evidence_status", "")) not in REPEATED_ENTITY_ROW_SOURCE_PLAN_EVIDENCE_STATUSES:
                errors.append(f"{pilot_key}: artifact {artifact_kind} has invalid evidence_status")
            if not isinstance(artifact.get("required_eu5_interfaces"), list) or not artifact.get("required_eu5_interfaces"):
                errors.append(f"{pilot_key}: artifact {artifact_kind} must declare required_eu5_interfaces")
            if not isinstance(artifact.get("entity_keys"), list):
                errors.append(f"{pilot_key}: artifact {artifact_kind} entity_keys must be a list")
            if not isinstance(artifact.get("aggregate_projection_variables"), list):
                errors.append(f"{pilot_key}: artifact {artifact_kind} aggregate_projection_variables must be a list")

            source_target_contract = artifact.get("source_target_contract")
            if artifact_kind in REPEATED_ENTITY_ROW_EVENT_ARTIFACT_KINDS:
                if str(artifact.get("evidence_status", "")) != "interface_candidate":
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} event evidence_status must stay interface_candidate"
                    )
                if not isinstance(source_target_contract, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must declare source_target_contract")
                else:
                    errors.extend(
                        _validate_repeated_row_event_source_target_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            contract=source_target_contract,
                        )
                    )
            elif artifact_kind in REPEATED_ENTITY_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS:
                if not isinstance(source_target_contract, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must declare source_target_contract")
                else:
                    errors.extend(
                        _validate_repeated_row_effect_cleanup_source_target_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            contract=source_target_contract,
                        )
                    )
            elif artifact_kind in REPEATED_ENTITY_ROW_TRIGGER_ARTIFACT_KINDS:
                if not isinstance(source_target_contract, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must declare source_target_contract")
                else:
                    errors.extend(
                        _validate_repeated_row_trigger_source_target_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            contract=source_target_contract,
                        )
                    )
            elif artifact_kind in REPEATED_ENTITY_ROW_GUI_ARTIFACT_KINDS:
                if str(artifact.get("evidence_status", "")) != "interface_candidate":
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} GUI evidence_status must stay interface_candidate"
                    )
                if not isinstance(source_target_contract, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must declare source_target_contract")
                else:
                    errors.extend(
                        _validate_repeated_row_gui_source_target_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            contract=source_target_contract,
                        )
                    )
            elif artifact_kind in REPEATED_ENTITY_ROW_LOCALIZATION_ARTIFACT_KINDS:
                if str(artifact.get("evidence_status", "")) != "interface_candidate":
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} localization evidence_status must stay interface_candidate"
                    )
                if not isinstance(source_target_contract, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must declare source_target_contract")
                else:
                    errors.extend(
                        _validate_repeated_row_localization_source_target_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            contract=source_target_contract,
                        )
                    )
            elif artifact_kind in REPEATED_ENTITY_ROW_LISTENER_ARTIFACT_KINDS:
                if not isinstance(source_target_contract, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must declare source_target_contract")
                else:
                    errors.extend(
                        _validate_repeated_row_listener_source_target_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            contract=source_target_contract,
                        )
                    )
            elif "source_target_contract" in artifact:
                errors.append(f"{pilot_key}: artifact {artifact_kind} must not declare source_target_contract")

            evidence_mapping = artifact.get("evidence_mapping")
            if not isinstance(evidence_mapping, dict):
                errors.append(f"{pilot_key}: artifact {artifact_kind} evidence_mapping must be a mapping")
                continue
            mapping_missing = _missing_required(
                evidence_mapping,
                REPEATED_ENTITY_ROW_SOURCE_PLAN_EVIDENCE_MAPPING_REQUIRED_FIELDS,
            )
            if mapping_missing:
                errors.append(
                    f"{pilot_key}: artifact {artifact_kind} evidence_mapping missing field(s): "
                    f"{', '.join(mapping_missing)}"
                )
                continue
            mapping_extra = sorted(
                set(evidence_mapping) - REPEATED_ENTITY_ROW_SOURCE_PLAN_EVIDENCE_MAPPING_REQUIRED_FIELDS
            )
            if mapping_extra:
                errors.append(
                    f"{pilot_key}: artifact {artifact_kind} evidence_mapping has unsupported field(s): "
                    f"{', '.join(mapping_extra)}"
                )
            if str(evidence_mapping.get("artifact_kind", "")) != artifact_kind:
                errors.append(f"{pilot_key}: artifact {artifact_kind} evidence_mapping artifact_kind mismatch")
            if str(evidence_mapping.get("source_target_boundary", "")) != str(artifact.get("source_target_boundary", "")):
                errors.append(f"{pilot_key}: artifact {artifact_kind} evidence_mapping source_target_boundary mismatch")
            if evidence_mapping.get("blocks_source_writer") is not artifact.get("blocks_source_writer"):
                errors.append(f"{pilot_key}: artifact {artifact_kind} evidence_mapping blocks_source_writer mismatch")
            if not isinstance(evidence_mapping.get("evidence_source_paths"), list):
                errors.append(f"{pilot_key}: artifact {artifact_kind} evidence_mapping evidence_source_paths must be a list")
            if artifact_kind in REPEATED_ENTITY_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS:
                if str(artifact.get("evidence_status", "")) not in {"interface_candidate", "missing_eu5_evidence"}:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} effect/cleanup evidence_status must stay "
                        "interface_candidate or missing_eu5_evidence"
                    )
            if artifact_kind in (
                REPEATED_ENTITY_ROW_EVENT_ARTIFACT_KINDS
                | REPEATED_ENTITY_ROW_EFFECT_CLEANUP_ARTIFACT_KINDS
                | REPEATED_ENTITY_ROW_TRIGGER_ARTIFACT_KINDS
                | REPEATED_ENTITY_ROW_GUI_ARTIFACT_KINDS
                | REPEATED_ENTITY_ROW_LOCALIZATION_ARTIFACT_KINDS
                | REPEATED_ENTITY_ROW_LISTENER_ARTIFACT_KINDS
            ):
                if not str(evidence_mapping.get("eu5_source_syntax_pattern", "")).strip():
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} evidence_mapping must declare EU5 syntax pattern or gap"
                    )
                if not str(evidence_mapping.get("generator_candidate", "")).strip() and not str(
                    evidence_mapping.get("generator_missing_reason", "")
                ).strip():
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} evidence_mapping must declare generator candidate or missing reason"
                    )
    return errors


def repeated_entity_row_source_plan_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
) -> dict[str, Any]:
    statuses = statuses or {"source_codegen_ready"}
    entries = payload.get("unique_wonders", []) or []
    reports: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        identity = entry.get("identity") if isinstance(entry.get("identity"), dict) else {}
        if str(identity.get("status", "")) not in statuses:
            continue
        report = repeated_entity_row_source_plan_for_entry(entry)
        if report["row_set_count"]:
            reports.append(report)

    summary = _repeated_row_source_plan_summary(reports)
    plan = {
        "statuses": sorted(statuses),
        "candidate_count": len(reports),
        "row_set_count": sum(int(report["row_set_count"]) for report in reports),
        "entity_row_count": sum(int(report["entity_row_count"]) for report in reports),
        "artifact_count": sum(int(report["artifact_count"]) for report in reports),
        **summary,
        "entries": reports,
        "validation_errors": [],
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "notes": [
            "Repeated-row source-plan is a source-writer prerequisite contract, not generated EU5 source.",
            "All planned source generators are currently missing and must stay may_write_src=false.",
            "Exact EU5 event/effect/trigger/GUI/localization/listener syntax evidence is still required.",
        ],
    }
    plan["validation_errors"] = validate_repeated_entity_row_source_plan(plan)
    return plan


def _repeated_row_source_preview_spec_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str((entry.get("identity") or {}).get("key", "")): entry
        for entry in payload.get("unique_wonders", []) or []
        if isinstance(entry, dict) and isinstance(entry.get("identity"), dict)
    }


def _repeated_row_node_event_id_evidence(entry: dict[str, Any]) -> list[dict[str, Any]]:
    node_graph = entry.get("node_graph") if isinstance(entry.get("node_graph"), dict) else {}
    evidence: list[dict[str, Any]] = []
    for node in node_graph.get("nodes", []) or []:
        if not isinstance(node, dict):
            continue
        if "event_id" not in node:
            continue
        evidence.append(
            {
                "node_key": str(node.get("key", "")),
                "node_kind": str(node.get("kind", "")),
                "event_id": int(node.get("event_id")),
            }
        )
    return evidence


def _repeated_row_event_id_evidence(entry: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for raw in entry.get("event_ids", []) or []:
        if isinstance(raw, dict) and "id" in raw:
            evidence.append({"event_id": int(raw["id"]), "key": str(raw.get("key", ""))})
        elif isinstance(raw, int):
            evidence.append({"event_id": raw, "key": ""})
    return evidence


def _repeated_row_preview_event_node(
    *,
    artifact_kind: str,
    node_evidence: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not node_evidence:
        return None
    index = REPEATED_ENTITY_ROW_EVENT_PREVIEW_NODE_INDEX.get(artifact_kind, 0)
    return node_evidence[min(index, len(node_evidence) - 1)]


def _repeated_row_event_source_preview_for_artifact(
    *,
    artifact: dict[str, Any],
    spec_entry: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    event_id_evidence = _repeated_row_event_id_evidence(spec_entry)
    node_event_id_evidence = _repeated_row_node_event_id_evidence(spec_entry)
    preview_node = _repeated_row_preview_event_node(
        artifact_kind=artifact_kind,
        node_evidence=node_event_id_evidence,
    )
    preview_event_id = preview_node.get("event_id") if preview_node else None
    handoff_name = (
        f"tv_wonder_unique_{wonder_key}_ritual_{artifact.get('row_set_key')}_{artifact_kind}_future_effect"
    )
    return {
        "preview_only": True,
        "preview_family": "event",
        "artifact_kind": artifact_kind,
        "pilot_key": pilot_key,
        "wonder_key": wonder_key,
        "row_set_key": str(artifact.get("row_set_key", "")),
        "entity_refs": _string_refs(artifact.get("entity_keys")),
        "future_source_target_path": str(contract.get("candidate_future_source_target_path", "")),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "blocks_source_writer": True,
        "blocker_reasons": list(REPEATED_ENTITY_ROW_EVENT_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_ready": False,
        "source_body_preview": {
            "kind": "country_event_preview",
            "namespace": str(contract.get("namespace_policy", "tv_engineering_department")),
            "event_id": preview_event_id,
            "title_key": f"tv_engineering_department.{preview_event_id}.t" if preview_event_id else "",
            "desc_key": f"tv_engineering_department.{preview_event_id}.d" if preview_event_id else "",
            "option_keys": [f"tv_engineering_department.{preview_event_id}.a"] if preview_event_id else [],
            "option_effect_handoff": handoff_name,
            "no_tooltip_heavy_finalization": True,
            "no_row_state_write": True,
            "no_source_ready": True,
        },
        "contract_status": str(contract.get("status", "")),
        "event_id_evidence_sources": ["spec.event_ids", "node_graph.nodes[].event_id"],
        "event_id_evidence": event_id_evidence,
        "node_event_id_evidence": node_event_id_evidence,
        "preview_event_id": preview_event_id,
        "preview_node_key": str(preview_node.get("node_key", "")) if preview_node else "",
        "preview_node_kind": str(preview_node.get("node_kind", "")) if preview_node else "",
        "option_effect_handoff": {
            "handoff_only": True,
            "future_scripted_effect_name": handoff_name,
            "placeholder_contract": "future_scripted_effect_contract_only_no_inline_row_state_write",
        },
        "row_state_writes_allowed": False,
        "tooltip_heavy_finalization_allowed": False,
        "source_ready_allowed": False,
    }


def _repeated_row_loc_line_policy_probe() -> dict[str, Any]:
    sample = loc_line("tv_preview_probe", 'Quote "and"\nnewline')
    return {
        "function": "wonder_mechanics._core.loc_line",
        "quote_escaped": '\\"' in sample,
        "newline_escaped": "\\n" in sample,
        "bom_encoding": "utf-8-sig",
        "writes_file": False,
        "sample": sample,
    }


def _repeated_row_localization_source_preview_for_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(artifact.get("entity_keys"))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    loc_group = REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUP_BY_ARTIFACT_KIND.get(artifact_kind, artifact_kind)
    namespace = f"tv_wonder_unique_{wonder_key}_ritual.{row_set_key}"
    loc_key_plan: list[dict[str, Any]] = []

    loc_scopes = entity_refs if loc_group != "summary_text" else ["summary"]
    for entity_key in loc_scopes:
        base_key = f"{namespace}.{entity_key}.{loc_group}"
        loc_key_plan.append(
            {
                "loc_group": loc_group,
                "entity_key": entity_key,
                "keys": {
                    language: base_key
                    for language in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS
                },
                "preview_lines": {
                    language: loc_line(
                        base_key,
                        f"{wonder_key} {row_set_key} {entity_key} {loc_group} preview",
                    )
                    for language in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS
                },
            }
        )

    return {
        "preview_only": True,
        "preview_family": "localization",
        "artifact_kind": artifact_kind,
        "pilot_key": pilot_key,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "entity_refs": entity_refs,
        "future_source_target_path": str(contract.get("candidate_future_source_target_path", "")),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "blocks_source_writer": True,
        "blocker_reasons": list(REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_ready": False,
        "source_body_preview": {
            "kind": "localization_key_plan_preview",
            "loc_group": loc_group,
            "no_source_file": True,
            "no_source_ready": True,
        },
        "contract_status": str(contract.get("status", "")),
        "required_languages": list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS),
        "missing_bilingual_coverage_allowed": False,
        "loc_key_namespace": namespace,
        "loc_key_plan": loc_key_plan,
        "loc_line_policy": (
            "dry-run only; preview mirrors wonder_mechanics._core.loc_line() quote/newline escaping "
            "and records utf-8-sig BOM output policy without writing files"
        ),
        "loc_line_policy_probe": _repeated_row_loc_line_policy_probe(),
        "unsafe_quote_newline_handling_allowed": False,
    }


def _repeated_row_future_script_name(
    *,
    wonder_key: str,
    row_set_key: str,
    artifact_kind: str,
    suffix: str,
) -> str:
    return f"tv_wonder_unique_{wonder_key}_ritual_{row_set_key}_{artifact_kind}_{suffix}"


def _repeated_row_effect_source_preview_for_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(artifact.get("entity_keys"))
    aggregate_projection_refs = _string_refs(artifact.get("aggregate_projection_variables"))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    future_effect_name = _repeated_row_future_script_name(
        wonder_key=wonder_key,
        row_set_key=row_set_key,
        artifact_kind=artifact_kind,
        suffix="effect",
    )
    return {
        "preview_only": True,
        "preview_family": "effect",
        "artifact_kind": artifact_kind,
        "pilot_key": pilot_key,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "entity_refs": entity_refs,
        "future_source_target_path": str(contract.get("candidate_future_source_target_path", "")),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "blocks_source_writer": True,
        "blocker_reasons": list(REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_ready": False,
        "source_body_preview": {
            "kind": "scripted_effect_plan_preview",
            "no_effect_body": True,
            "no_row_state_write": True,
            "no_source_ready": True,
        },
        "contract_status": str(contract.get("status", "")),
        "future_effect_name_plan": {
            "name": future_effect_name,
            "name_only": True,
            "body_emitted": False,
        },
        "row_entity_refs": {
            "row_set_key": row_set_key,
            "entity_keys": entity_refs,
        },
        "aggregate_projection_refs": aggregate_projection_refs,
        "aggregate_projection_boundary": str(contract.get("aggregate_projection_boundary", "")),
        "handoff_responsibility": {
            "handoff_only": True,
            "owner_generator": str(artifact.get("owner_generator", "")),
            "source_target_boundary": str(artifact.get("source_target_boundary", "")),
            "no_inline_row_state_write": True,
        },
        "row_state_writes_allowed": False,
        "effect_body_writes_allowed": False,
        "source_ready_allowed": False,
    }


def _repeated_row_cleanup_source_preview_for_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(artifact.get("entity_keys"))
    aggregate_projection_refs = _string_refs(artifact.get("aggregate_projection_variables"))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    cleanup_scope = str(contract.get("cleanup_lifecycle_scope", ""))
    return {
        "preview_only": True,
        "preview_family": "cleanup",
        "artifact_kind": artifact_kind,
        "pilot_key": pilot_key,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "entity_refs": entity_refs,
        "future_source_target_path": str(contract.get("candidate_future_source_target_path", "")),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "blocks_source_writer": True,
        "blocker_reasons": list(REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_ready": False,
        "source_body_preview": {
            "kind": "cleanup_scope_plan_preview",
            "no_cleanup_body": True,
            "no_effect_body": True,
            "no_source_ready": True,
        },
        "contract_status": str(contract.get("status", "")),
        "cleanup_scope_plan": {
            "scope": cleanup_scope,
            "target_path": str(contract.get("candidate_future_source_target_path", "")),
            "scope_only": True,
            "body_emitted": False,
        },
        "cleanup_coverage": {
            "completion": artifact_kind == "cleanup_completion",
            "failure": artifact_kind == "cleanup_failure",
            "ownership_loss": artifact_kind == "cleanup_ownership_loss",
            "ritual_reset": artifact_kind == "cleanup_ritual_reset",
            "coverage_group": list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_CLEANUP_COVERAGE_SCOPES),
        },
        "row_entity_refs": {
            "row_set_key": row_set_key,
            "entity_keys": entity_refs,
        },
        "aggregate_projection_refs": aggregate_projection_refs,
        "aggregate_projection_boundary": str(contract.get("aggregate_projection_boundary", "")),
        "effect_body_writes_allowed": False,
        "source_ready_allowed": False,
    }


def _repeated_row_trigger_source_preview_for_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(artifact.get("entity_keys"))
    aggregate_projection_refs = _string_refs(artifact.get("aggregate_projection_variables"))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    future_trigger_name = _repeated_row_future_script_name(
        wonder_key=wonder_key,
        row_set_key=row_set_key,
        artifact_kind=artifact_kind,
        suffix="trigger",
    )
    return {
        "preview_only": True,
        "preview_family": "trigger",
        "artifact_kind": artifact_kind,
        "pilot_key": pilot_key,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "entity_refs": entity_refs,
        "future_source_target_path": str(contract.get("candidate_future_source_target_path", "")),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "blocks_source_writer": True,
        "blocker_reasons": list(REPEATED_ENTITY_ROW_TRIGGER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_ready": False,
        "source_body_preview": {
            "kind": "scripted_trigger_plan_preview",
            "no_trigger_body": True,
            "no_unsafe_tooltip_write_path": True,
            "no_source_ready": True,
        },
        "contract_status": str(contract.get("status", "")),
        "future_trigger_name_plan": {
            "name": future_trigger_name,
            "name_only": True,
            "body_emitted": False,
        },
        "eligibility_condition_group_plan": {
            "planned": artifact_kind == "scripted_trigger_eligibility",
            "predicate_group_only": True,
            "entity_keys": entity_refs,
        },
        "row_completion_condition_group_plan": {
            "planned": artifact_kind == "scripted_trigger_row_completion",
            "predicate_group_only": True,
            "entity_keys": entity_refs,
        },
        "tooltip_safe_condition_group_plan": {
            "planned": artifact_kind == "scripted_trigger_tooltip_safe_condition_group",
            "predicate_group_only": True,
            "unsafe_write_paths_allowed": False,
            "policy": str(contract.get("tooltip_safe_condition_group_policy", "")),
        },
        "aggregate_projection_refs": aggregate_projection_refs,
        "aggregate_boundary": str(contract.get("aggregate_projection_boundary", "")),
        "trigger_body_writes_allowed": False,
        "tooltip_safe_unsafe_write_paths_allowed": False,
        "source_ready_allowed": False,
    }


def _repeated_row_gui_source_preview_for_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(artifact.get("entity_keys"))
    aggregate_projection_refs = _string_refs(artifact.get("aggregate_projection_variables"))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    widget_kind = artifact_kind.removeprefix("gui_").removesuffix("_row")
    loc_namespace = f"tv_wonder_unique_{wonder_key}_ritual.{row_set_key}"
    event_key_prefix = "tv_engineering_department.<event_id>"
    return {
        "preview_only": True,
        "preview_family": "gui",
        "artifact_kind": artifact_kind,
        "pilot_key": pilot_key,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "entity_refs": entity_refs,
        "future_source_target_path": str(contract.get("candidate_future_source_target_path", "")),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "blocks_source_writer": True,
        "blocker_reasons": list(REPEATED_ENTITY_ROW_GUI_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_ready": False,
        "source_body_preview": {
            "kind": "gui_row_contract_preview",
            "widget_kind": widget_kind,
            "body_emitted": False,
            "no_gui_source_body": True,
            "no_gui_source_write": True,
            "no_row_state_write": True,
            "no_source_ready": True,
        },
        "contract_status": str(contract.get("status", "")),
        "fixed_row_widget_plan": {
            "widget_kind": widget_kind,
            "row_widget_fixed": True,
            "row_widget_boundary": str(contract.get("fixed_row_widget_boundary", "")),
            "body_emitted": False,
        },
        "per_row_variable_binding_plan": {
            "binds_design_ir_tracked_entity_sets": True,
            "entity_keys": entity_refs,
            "aggregate_only_row_reads_allowed": False,
            "policy": str(contract.get("per_row_variable_binding_policy", "")),
        },
        "row_entity_refs": {
            "row_set_key": row_set_key,
            "entity_keys": entity_refs,
        },
        "tooltip_localization_linkage": {
            "loc_key_namespace": loc_namespace,
            "row_label_keys": [f"{loc_namespace}.{entity_key}.row_labels" for entity_key in entity_refs],
            "status_text_keys": [f"{loc_namespace}.{entity_key}.status_text" for entity_key in entity_refs],
            "incident_text_keys": [f"{loc_namespace}.{entity_key}.incident_text" for entity_key in entity_refs],
            "tooltip_keys": [f"{loc_namespace}.{entity_key}.tooltips" for entity_key in entity_refs],
            "policy": str(contract.get("tooltip_key_linkage_policy", "")),
        },
        "gui_event_key_linkage": {
            "event_key_prefix": event_key_prefix,
            "event_title_key_pattern": f"{event_key_prefix}.t",
            "event_desc_key_pattern": f"{event_key_prefix}.d",
            "event_option_key_pattern": f"{event_key_prefix}.a",
            "linkage_only": True,
            "source_body_emitted": False,
        },
        "aggregate_projection_refs": aggregate_projection_refs,
        "aggregate_projection_boundary": str(contract.get("aggregate_projection_boundary", "")),
        "aggregate_only_display_allowed": False,
        "gui_source_body_allowed": False,
        "gui_source_writes_allowed": False,
        "row_state_writes_allowed": False,
        "source_ready_allowed": False,
    }


def _repeated_row_listener_source_preview_for_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(artifact.get("entity_keys"))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    target_path = str(contract.get("candidate_future_source_target_path", ""))
    selected_trigger = "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
    return {
        "preview_only": True,
        "preview_family": "listener",
        "artifact_kind": artifact_kind,
        "pilot_key": pilot_key,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "entity_refs": entity_refs,
        "future_source_target_path": target_path,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "blocks_source_writer": True,
        "blocker_reasons": list(REPEATED_ENTITY_ROW_LISTENER_SOURCE_TARGET_CONTRACT_BLOCKER_REASONS),
        "source_ready": False,
        "source_body_preview": {
            "kind": "listener_on_action_contract_preview",
            "body_emitted": False,
            "no_listener_body": True,
            "no_listener_scope_write": True,
            "no_war_scope_write": True,
            "no_source_ready": True,
        },
        "contract_status": str(contract.get("status", "")),
        "on_action_target_path_plan": {
            "target_path": target_path,
            "target_only": True,
            "body_emitted": False,
        },
        "on_action_hook_linkage_plan": {
            "hooks": ["on_pre_winning_war", "on_ending_war"],
            "bridge_policy": str(contract.get("on_action_bridge_policy", "")),
            "linkage_only": True,
            "body_emitted": False,
        },
        "selected_ritual_trigger_linkage": {
            "trigger_name": selected_trigger,
            "selected_ritual_only": True,
            "linkage_only": True,
        },
        "war_scope_availability_persistence_plan": {
            "war_scope_available_from_hooks": ["on_pre_winning_war", "on_ending_war"],
            "persistence_contract_only": True,
            "listener_scope_writes_allowed": False,
            "war_scope_writes_allowed": False,
        },
        "row_state_handoff_boundary": {
            "row_set_key": row_set_key,
            "entity_keys": entity_refs,
            "handoff_only": True,
            "row_state_writes_allowed": False,
            "source_target_boundary": str(artifact.get("source_target_boundary", "")),
        },
        "listener_body_allowed": False,
        "listener_scope_writes_allowed": False,
        "war_scope_writes_allowed": False,
        "source_writes_allowed": False,
        "source_ready_allowed": False,
    }


def repeated_entity_row_source_preview_for_entry(
    entry_plan: dict[str, Any],
    *,
    spec_entry: dict[str, Any],
) -> dict[str, Any]:
    previews: list[dict[str, Any]] = []
    skipped_artifact_kinds: list[str] = []
    for artifact in entry_plan.get("artifacts", []) or []:
        if not isinstance(artifact, dict):
            continue
        artifact_kind = str(artifact.get("artifact_kind", ""))
        if artifact_kind in REPEATED_ENTITY_ROW_EVENT_ARTIFACT_KINDS:
            previews.append(
                _repeated_row_event_source_preview_for_artifact(
                    artifact=artifact,
                    spec_entry=spec_entry,
                )
            )
        elif artifact_kind in REPEATED_ENTITY_ROW_LOCALIZATION_ARTIFACT_KINDS:
            previews.append(_repeated_row_localization_source_preview_for_artifact(artifact))
        elif artifact_kind in REPEATED_ENTITY_ROW_EFFECT_ARTIFACT_KINDS:
            previews.append(_repeated_row_effect_source_preview_for_artifact(artifact))
        elif artifact_kind in REPEATED_ENTITY_ROW_CLEANUP_ARTIFACT_KINDS:
            previews.append(_repeated_row_cleanup_source_preview_for_artifact(artifact))
        elif artifact_kind in REPEATED_ENTITY_ROW_TRIGGER_ARTIFACT_KINDS:
            previews.append(_repeated_row_trigger_source_preview_for_artifact(artifact))
        elif artifact_kind in REPEATED_ENTITY_ROW_GUI_ARTIFACT_KINDS:
            previews.append(_repeated_row_gui_source_preview_for_artifact(artifact))
        elif artifact_kind in REPEATED_ENTITY_ROW_LISTENER_ARTIFACT_KINDS:
            previews.append(_repeated_row_listener_source_preview_for_artifact(artifact))
        else:
            skipped_artifact_kinds.append(artifact_kind)

    return {
        "key": str(entry_plan.get("key", "")),
        "preview_only": True,
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "writes_src": False,
        "preview_count": len(previews),
        "preview_family_summary": _count_by_key(previews, "preview_family"),
        "skipped_artifact_kinds": sorted(set(skipped_artifact_kinds)),
        "previews": previews,
        "notes": [
            "Dry-run source preview only; no src files are written.",
            "GUI and listener artifacts now receive no-body dry-run previews and remain source-writer blockers.",
        ],
    }


def repeated_entity_row_source_preview_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_plan is None:
        source_plan = repeated_entity_row_source_plan_for_payload(payload, statuses=statuses)
    spec_index = _repeated_row_source_preview_spec_index(payload)
    entries: list[dict[str, Any]] = []
    for entry_plan in source_plan.get("entries", []) or []:
        if not isinstance(entry_plan, dict):
            continue
        pilot_key = str(entry_plan.get("key", ""))
        spec_entry = spec_index.get(pilot_key, {})
        entries.append(
            repeated_entity_row_source_preview_for_entry(
                entry_plan,
                spec_entry=spec_entry,
            )
        )

    previews = [
        preview
        for entry in entries
        for preview in entry.get("previews", []) or []
        if isinstance(preview, dict)
    ]
    skipped_artifact_kinds = sorted(
        {
            str(artifact_kind)
            for entry in entries
            for artifact_kind in entry.get("skipped_artifact_kinds", []) or []
        }
    )
    report = {
        "statuses": sorted(statuses or {"source_codegen_ready"}),
        "preview_only": True,
        "candidate_count": len(entries),
        "preview_count": len(previews),
        "preview_family_summary": _count_by_key(previews, "preview_family"),
        "skipped_artifact_kinds": skipped_artifact_kinds,
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "writes_src": False,
        "source_plan_artifact_count": int(source_plan.get("artifact_count", 0)),
        "source_plan_contract_validation_errors": list(source_plan.get("validation_errors", [])),
        "entries": entries,
        "validation_errors": [],
        "notes": [
            "Repeated-row source preview is a no-write dry-run compiler layer.",
            "It emits event/localization/effect/cleanup/trigger/GUI/listener preview fragments only and does not authorize src writes.",
            "It does not make any source-plan contract source-ready.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_source_preview(report)
    return report


def validate_repeated_entity_row_source_preview(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("preview_only") is not True:
        errors.append("source preview report must declare preview_only: true")
    if report.get("source_writer_allowed") is not False:
        errors.append("source preview report source_writer_allowed must be false")
    if report.get("may_write_src_allowed") is not False:
        errors.append("source preview report may_write_src_allowed must be false")
    if report.get("writes_src") is not False:
        errors.append("source preview report writes_src must be false")
    if report.get("source_plan_artifact_count") != 177:
        errors.append("source preview report must be based on the 177-artifact source-plan")
    if report.get("source_plan_contract_validation_errors"):
        errors.append("source preview report source-plan contract validation must be clean")

    preview_family_counts = {
        "event": 0,
        "localization": 0,
        "effect": 0,
        "cleanup": 0,
        "trigger": 0,
        "gui": 0,
        "listener": 0,
    }
    all_loc_keys: dict[str, str] = {}
    skipped_artifact_kinds = _string_refs(report.get("skipped_artifact_kinds"))
    if skipped_artifact_kinds:
        errors.append(
            "source preview report skipped_artifact_kinds must be empty: "
            f"{', '.join(sorted(set(skipped_artifact_kinds)))}"
        )
    entries = report.get("entries") if isinstance(report.get("entries"), list) else []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("source preview entry must be a mapping")
            continue
        pilot_key = str(entry.get("key", "<unknown>"))
        if entry.get("preview_only") is not True:
            errors.append(f"{pilot_key}: source preview entry must declare preview_only: true")
        if entry.get("source_writer_allowed") is not False:
            errors.append(f"{pilot_key}: source preview entry source_writer_allowed must be false")
        if entry.get("may_write_src_allowed") is not False:
            errors.append(f"{pilot_key}: source preview entry may_write_src_allowed must be false")
        if entry.get("writes_src") is not False:
            errors.append(f"{pilot_key}: source preview entry writes_src must be false")
        entry_skipped_artifact_kinds = _string_refs(entry.get("skipped_artifact_kinds"))
        if entry_skipped_artifact_kinds:
            errors.append(
                f"{pilot_key}: source preview entry skipped_artifact_kinds must be empty: "
                f"{', '.join(sorted(set(entry_skipped_artifact_kinds)))}"
            )

        for preview in entry.get("previews", []) or []:
            if not isinstance(preview, dict):
                errors.append(f"{pilot_key}: source preview must be a mapping")
                continue
            artifact_kind = str(preview.get("artifact_kind", "<unknown>"))
            family = str(preview.get("preview_family", ""))
            if family == "event":
                required_fields = REPEATED_ENTITY_ROW_EVENT_SOURCE_PREVIEW_REQUIRED_FIELDS
                preview_family_counts["event"] += 1
            elif family == "localization":
                required_fields = REPEATED_ENTITY_ROW_LOCALIZATION_SOURCE_PREVIEW_REQUIRED_FIELDS
                preview_family_counts["localization"] += 1
            elif family == "effect":
                required_fields = REPEATED_ENTITY_ROW_EFFECT_SOURCE_PREVIEW_REQUIRED_FIELDS
                preview_family_counts["effect"] += 1
            elif family == "cleanup":
                required_fields = REPEATED_ENTITY_ROW_CLEANUP_SOURCE_PREVIEW_REQUIRED_FIELDS
                preview_family_counts["cleanup"] += 1
            elif family == "trigger":
                required_fields = REPEATED_ENTITY_ROW_TRIGGER_SOURCE_PREVIEW_REQUIRED_FIELDS
                preview_family_counts["trigger"] += 1
            elif family == "gui":
                required_fields = REPEATED_ENTITY_ROW_GUI_SOURCE_PREVIEW_REQUIRED_FIELDS
                preview_family_counts["gui"] += 1
            elif family == "listener":
                required_fields = REPEATED_ENTITY_ROW_LISTENER_SOURCE_PREVIEW_REQUIRED_FIELDS
                preview_family_counts["listener"] += 1
            else:
                errors.append(
                    f"{pilot_key}: artifact {artifact_kind} unsupported source body preview family {family!r}"
                )
                continue
            missing = _missing_required(preview, required_fields)
            if missing:
                errors.append(f"{pilot_key}: artifact {artifact_kind} source preview missing field(s): {', '.join(missing)}")
                continue
            extra = sorted(set(preview) - required_fields)
            if extra:
                errors.append(
                    f"{pilot_key}: artifact {artifact_kind} source preview has unsupported field(s): "
                    f"{', '.join(extra)}"
                )
            if preview.get("preview_only") is not True:
                errors.append(f"{pilot_key}: artifact {artifact_kind} preview_only must be true")
            if preview.get("source_writer_allowed") is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} source_writer_allowed must be false")
            if preview.get("may_write_src") is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} may_write_src must be false")
            if preview.get("writes_src") is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} writes_src must be false")
            if preview.get("blocks_source_writer") is not True:
                errors.append(f"{pilot_key}: artifact {artifact_kind} blocks_source_writer must be true")
            if preview.get("source_ready") is not False or preview.get("contract_status") == "source-ready":
                errors.append(f"{pilot_key}: artifact {artifact_kind} source preview must not be source-ready")
            if preview.get("contract_status") != "blocked":
                errors.append(f"{pilot_key}: artifact {artifact_kind} source preview contract_status must be blocked")
            if not str(preview.get("future_source_target_path", "")).startswith("src/"):
                errors.append(f"{pilot_key}: artifact {artifact_kind} future source target path is missing")
            if not isinstance(preview.get("blocker_reasons"), list) or not preview.get("blocker_reasons"):
                errors.append(f"{pilot_key}: artifact {artifact_kind} source preview missing blocker reasons")

            if family == "event":
                if artifact_kind not in REPEATED_ENTITY_ROW_EVENT_ARTIFACT_KINDS:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must not receive an event source body preview")
                if preview.get("row_state_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event preview row-state writes must be false")
                if preview.get("tooltip_heavy_finalization_allowed") is not False:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} event preview tooltip-heavy finalization must be false"
                    )
                if preview.get("source_ready_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event preview source-ready must be false")
                source_body_preview = preview.get("source_body_preview")
                if not isinstance(source_body_preview, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event source_body_preview must be a mapping")
                else:
                    if source_body_preview.get("no_row_state_write") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} event preview must declare no row-state write")
                    if source_body_preview.get("no_tooltip_heavy_finalization") is not True:
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} event preview must declare no tooltip-heavy finalization"
                        )
                    if source_body_preview.get("no_source_ready") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} event preview must declare no source-ready")
                event_ids = [int(item["event_id"]) for item in preview.get("event_id_evidence", []) or [] if isinstance(item, dict) and "event_id" in item]
                node_event_ids = [
                    int(item["event_id"])
                    for item in preview.get("node_event_id_evidence", []) or []
                    if isinstance(item, dict) and "event_id" in item
                ]
                if not event_ids:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event preview missing spec event IDs")
                if not node_event_ids:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event preview missing node event IDs")
                if len(event_ids) != len(set(event_ids)):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event preview duplicate spec event IDs")
                if len(node_event_ids) != len(set(node_event_ids)):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event preview duplicate node event IDs")
                too_large = sorted({event_id for event_id in event_ids + node_event_ids if event_id >= 10000})
                if too_large:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} event preview event IDs must be <10000: {too_large}"
                    )
                preview_event_id = preview.get("preview_event_id")
                if preview_event_id not in event_ids or preview_event_id not in node_event_ids:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} event preview must use existing spec/node event ID"
                    )
                handoff = preview.get("option_effect_handoff")
                if not isinstance(handoff, dict) or handoff.get("handoff_only") is not True:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} event preview must hand off to future effect only")
                else:
                    if "row_state" in str(handoff.get("inline_body", "")).lower():
                        errors.append(f"{pilot_key}: artifact {artifact_kind} event preview must not inline row-state writes")

            if family == "localization":
                if artifact_kind not in REPEATED_ENTITY_ROW_LOCALIZATION_ARTIFACT_KINDS:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must not receive a localization source body preview")
                if set(_string_refs(preview.get("required_languages"))) != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} localization preview missing English or Simplified Chinese"
                    )
                if preview.get("missing_bilingual_coverage_allowed") is not False:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} localization preview missing bilingual coverage must be false"
                    )
                if preview.get("unsafe_quote_newline_handling_allowed") is not False:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} localization preview unsafe quote/newline policy must be false"
                    )
                policy_probe = preview.get("loc_line_policy_probe")
                if not isinstance(policy_probe, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} localization preview missing loc_line policy probe")
                elif (
                    policy_probe.get("quote_escaped") is not True
                    or policy_probe.get("newline_escaped") is not True
                    or policy_probe.get("bom_encoding") != "utf-8-sig"
                    or policy_probe.get("writes_file") is not False
                ):
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} localization preview unsafe quote/newline policy allowed"
                    )
                namespace = str(preview.get("loc_key_namespace", ""))
                wonder_key = str(preview.get("wonder_key", ""))
                row_set_key = str(preview.get("row_set_key", ""))
                if (
                    f"tv_wonder_unique_{wonder_key}_ritual" not in namespace
                    or row_set_key not in namespace
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} localization preview namespace is incomplete")
                loc_key_plan = preview.get("loc_key_plan")
                if not isinstance(loc_key_plan, list) or not loc_key_plan:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} localization preview missing loc key plan")
                    continue
                for item in loc_key_plan:
                    if not isinstance(item, dict):
                        errors.append(f"{pilot_key}: artifact {artifact_kind} localization loc key plan item must be mapping")
                        continue
                    keys = item.get("keys")
                    if not isinstance(keys, dict):
                        errors.append(f"{pilot_key}: artifact {artifact_kind} localization loc key plan keys must be mapping")
                        continue
                    if set(keys) != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} localization loc key plan missing language coverage"
                        )
                    for language, loc_key in keys.items():
                        loc_key_text = str(loc_key)
                        if f"tv_wonder_unique_{wonder_key}_ritual" not in loc_key_text or row_set_key not in loc_key_text:
                            errors.append(
                                f"{pilot_key}: artifact {artifact_kind} localization loc key namespace is incomplete"
                            )
                        duplicate_key = f"{language}:{loc_key_text}"
                        owner = f"{pilot_key}:{artifact_kind}:{row_set_key}"
                        if duplicate_key in all_loc_keys:
                            errors.append(
                                f"{pilot_key}: artifact {artifact_kind} localization duplicate loc key {duplicate_key}"
                            )
                        all_loc_keys[duplicate_key] = owner

            if family == "effect":
                if artifact_kind not in REPEATED_ENTITY_ROW_EFFECT_ARTIFACT_KINDS:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must not receive an effect source body preview")
                if preview.get("row_state_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview row-state writes must be false")
                if preview.get("effect_body_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview effect body writes must be false")
                if preview.get("source_ready_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview source-ready must be false")
                source_body_preview = preview.get("source_body_preview")
                if not isinstance(source_body_preview, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect source_body_preview must be a mapping")
                else:
                    if source_body_preview.get("no_effect_body") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview must declare no effect body")
                    if source_body_preview.get("no_row_state_write") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview must declare no row-state write")
                    if source_body_preview.get("no_source_ready") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview must declare no source-ready")
                name_plan = preview.get("future_effect_name_plan")
                if (
                    not isinstance(name_plan, dict)
                    or not str(name_plan.get("name", "")).startswith(f"tv_wonder_unique_{preview.get('wonder_key')}_ritual_")
                    or name_plan.get("body_emitted") is not False
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview missing future effect name plan")
                handoff = preview.get("handoff_responsibility")
                if not isinstance(handoff, dict) or handoff.get("handoff_only") is not True:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview missing handoff responsibility")
                elif handoff.get("no_inline_row_state_write") is not True:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview must forbid inline row-state writes")
                if not isinstance(preview.get("row_entity_refs"), dict) or not preview.get("row_entity_refs", {}).get("entity_keys"):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview missing row/entity refs")
                if not isinstance(preview.get("aggregate_projection_refs"), list):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview missing aggregate projection refs")
                if not str(preview.get("aggregate_projection_boundary", "")).strip():
                    errors.append(f"{pilot_key}: artifact {artifact_kind} effect preview missing aggregate projection boundary")

            if family == "cleanup":
                if artifact_kind not in REPEATED_ENTITY_ROW_CLEANUP_ARTIFACT_KINDS:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must not receive a cleanup source body preview")
                if preview.get("effect_body_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview effect body writes must be false")
                if preview.get("source_ready_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview source-ready must be false")
                source_body_preview = preview.get("source_body_preview")
                if not isinstance(source_body_preview, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup source_body_preview must be a mapping")
                else:
                    if source_body_preview.get("no_cleanup_body") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview must declare no cleanup body")
                    if source_body_preview.get("no_effect_body") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview must declare no effect body")
                    if source_body_preview.get("no_source_ready") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview must declare no source-ready")
                scope_plan = preview.get("cleanup_scope_plan")
                expected_scope = REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_CLEANUP_SCOPES.get(
                    artifact_kind
                )
                if not isinstance(scope_plan, dict) or scope_plan.get("scope") != expected_scope:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview missing cleanup scope")
                elif scope_plan.get("body_emitted") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview must not emit cleanup body")
                coverage = preview.get("cleanup_coverage")
                if not isinstance(coverage, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview missing cleanup coverage")
                else:
                    missing_coverage = [
                        scope
                        for scope in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_CLEANUP_COVERAGE_SCOPES
                        if scope not in coverage
                    ]
                    if missing_coverage:
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} cleanup preview missing cleanup coverage"
                        )
                    expected_coverage_key = "ritual_reset" if artifact_kind == "cleanup_ritual_reset" else str(expected_scope)
                    if coverage.get(expected_coverage_key) is not True:
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} cleanup preview missing cleanup coverage"
                        )
                if not isinstance(preview.get("row_entity_refs"), dict) or not preview.get("row_entity_refs", {}).get("entity_keys"):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview missing row/entity refs")
                if not isinstance(preview.get("aggregate_projection_refs"), list):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview missing aggregate projection refs")
                if not str(preview.get("aggregate_projection_boundary", "")).strip():
                    errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup preview missing aggregate projection boundary")

            if family == "trigger":
                if artifact_kind not in REPEATED_ENTITY_ROW_TRIGGER_ARTIFACT_KINDS:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must not receive a trigger source body preview")
                if preview.get("trigger_body_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview trigger body writes must be false")
                if preview.get("tooltip_safe_unsafe_write_paths_allowed") is not False:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} trigger preview tooltip-safe unsafe write paths must be false"
                    )
                if preview.get("source_ready_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview source-ready must be false")
                source_body_preview = preview.get("source_body_preview")
                if not isinstance(source_body_preview, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} trigger source_body_preview must be a mapping")
                else:
                    if source_body_preview.get("no_trigger_body") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview must declare no trigger body")
                    if source_body_preview.get("no_unsafe_tooltip_write_path") is not True:
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} trigger preview must forbid unsafe tooltip write path"
                        )
                    if source_body_preview.get("no_source_ready") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview must declare no source-ready")
                name_plan = preview.get("future_trigger_name_plan")
                if (
                    not isinstance(name_plan, dict)
                    or not str(name_plan.get("name", "")).startswith(f"tv_wonder_unique_{preview.get('wonder_key')}_ritual_")
                    or name_plan.get("body_emitted") is not False
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview missing future trigger name plan")
                condition_plan_by_kind = {
                    "scripted_trigger_eligibility": "eligibility_condition_group_plan",
                    "scripted_trigger_row_completion": "row_completion_condition_group_plan",
                    "scripted_trigger_tooltip_safe_condition_group": "tooltip_safe_condition_group_plan",
                }
                expected_plan_key = condition_plan_by_kind.get(artifact_kind, "")
                for plan_key in condition_plan_by_kind.values():
                    condition_plan = preview.get(plan_key)
                    if not isinstance(condition_plan, dict):
                        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview missing {plan_key}")
                        continue
                    if plan_key == expected_plan_key and condition_plan.get("planned") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview missing condition group plan")
                    if condition_plan.get("predicate_group_only") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview must stay predicate-group only")
                tooltip_plan = preview.get("tooltip_safe_condition_group_plan")
                if isinstance(tooltip_plan, dict) and tooltip_plan.get("unsafe_write_paths_allowed") is not False:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} trigger preview tooltip-safe unsafe write paths must be false"
                    )
                if not isinstance(preview.get("aggregate_projection_refs"), list):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview missing aggregate projection refs")
                if not str(preview.get("aggregate_boundary", "")).strip():
                    errors.append(f"{pilot_key}: artifact {artifact_kind} trigger preview missing aggregate boundary")

            if family == "gui":
                if artifact_kind not in REPEATED_ENTITY_ROW_GUI_ARTIFACT_KINDS:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} must not receive a GUI source body preview")
                if preview.get("aggregate_only_display_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview aggregate-only display must be false")
                if preview.get("gui_source_body_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview GUI body writes must be false")
                if preview.get("gui_source_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview GUI source writes must be false")
                if preview.get("row_state_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview row-state writes must be false")
                if preview.get("source_ready_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview source-ready must be false")
                source_body_preview = preview.get("source_body_preview")
                if not isinstance(source_body_preview, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI source_body_preview must be a mapping")
                else:
                    if source_body_preview.get("no_gui_source_body") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview must declare no GUI source body")
                    if source_body_preview.get("no_gui_source_write") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview must declare no GUI source write")
                    if source_body_preview.get("no_row_state_write") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview must declare no row-state write")
                    if source_body_preview.get("no_source_ready") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview must declare no source-ready")
                    if source_body_preview.get("body_emitted") is not False:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview must not emit GUI source body")
                fixed_plan = preview.get("fixed_row_widget_plan")
                if (
                    not isinstance(fixed_plan, dict)
                    or fixed_plan.get("row_widget_fixed") is not True
                    or fixed_plan.get("body_emitted") is not False
                    or not str(fixed_plan.get("row_widget_boundary", "")).strip()
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview missing fixed row widget plan")
                binding_plan = preview.get("per_row_variable_binding_plan")
                if (
                    not isinstance(binding_plan, dict)
                    or binding_plan.get("binds_design_ir_tracked_entity_sets") is not True
                    or binding_plan.get("aggregate_only_row_reads_allowed") is not False
                    or not binding_plan.get("entity_keys")
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview missing per-row binding plan")
                if not isinstance(preview.get("row_entity_refs"), dict) or not preview.get("row_entity_refs", {}).get("entity_keys"):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview missing row/entity refs")
                tooltip_linkage = preview.get("tooltip_localization_linkage")
                if not isinstance(tooltip_linkage, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview missing tooltip/localization linkage")
                else:
                    required_linkage_keys = {"loc_key_namespace", "row_label_keys", "status_text_keys", "tooltip_keys"}
                    if not required_linkage_keys <= set(tooltip_linkage):
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} GUI preview missing tooltip/localization linkage"
                        )
                    if not str(tooltip_linkage.get("loc_key_namespace", "")).startswith("tv_wonder_unique_"):
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} GUI preview missing tooltip/localization linkage"
                        )
                gui_event_linkage = preview.get("gui_event_key_linkage")
                if (
                    not isinstance(gui_event_linkage, dict)
                    or gui_event_linkage.get("linkage_only") is not True
                    or gui_event_linkage.get("source_body_emitted") is not False
                    or not str(gui_event_linkage.get("event_key_prefix", "")).strip()
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview missing GUI/event key linkage")
                if not isinstance(preview.get("aggregate_projection_refs"), list):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview missing aggregate projection refs")
                if not str(preview.get("aggregate_projection_boundary", "")).strip():
                    errors.append(f"{pilot_key}: artifact {artifact_kind} GUI preview missing aggregate projection boundary")

            if family == "listener":
                preview_pilot_key = str(preview.get("pilot_key", ""))
                if (
                    pilot_key != "unique_alhambra"
                    or preview_pilot_key != "unique_alhambra"
                    or artifact_kind != "listener_war_integration"
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview must be Alhambra-only")
                if preview.get("listener_body_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview listener body writes must be false")
                if preview.get("listener_scope_writes_allowed") is not False:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} listener preview listener scope writes must be false"
                    )
                if preview.get("war_scope_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview war scope writes must be false")
                if preview.get("source_writes_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview source writes must be false")
                if preview.get("source_ready_allowed") is not False:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview source-ready must be false")
                source_body_preview = preview.get("source_body_preview")
                if not isinstance(source_body_preview, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener source_body_preview must be a mapping")
                else:
                    if source_body_preview.get("no_listener_body") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview must declare no listener body")
                    if source_body_preview.get("no_listener_scope_write") is not True:
                        errors.append(
                            f"{pilot_key}: artifact {artifact_kind} listener preview must declare no listener scope write"
                        )
                    if source_body_preview.get("no_war_scope_write") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview must declare no war scope write")
                    if source_body_preview.get("no_source_ready") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview must declare no source-ready")
                    if source_body_preview.get("body_emitted") is not False:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview must not emit listener body")
                target_plan = preview.get("on_action_target_path_plan")
                if (
                    not isinstance(target_plan, dict)
                    or target_plan.get("target_only") is not True
                    or target_plan.get("body_emitted") is not False
                    or not str(target_plan.get("target_path", "")).startswith("src/in_game/common/on_action/")
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview missing on_action target path plan")
                hook_plan = preview.get("on_action_hook_linkage_plan")
                if (
                    not isinstance(hook_plan, dict)
                    or hook_plan.get("linkage_only") is not True
                    or hook_plan.get("body_emitted") is not False
                    or not {"on_pre_winning_war", "on_ending_war"} <= set(_string_refs(hook_plan.get("hooks")))
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview missing hook linkage plan")
                trigger_linkage = preview.get("selected_ritual_trigger_linkage")
                if (
                    not isinstance(trigger_linkage, dict)
                    or trigger_linkage.get("selected_ritual_only") is not True
                    or trigger_linkage.get("linkage_only") is not True
                    or not str(trigger_linkage.get("trigger_name", "")).strip()
                ):
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} listener preview missing selected ritual trigger linkage"
                    )
                war_scope_plan = preview.get("war_scope_availability_persistence_plan")
                if (
                    not isinstance(war_scope_plan, dict)
                    or war_scope_plan.get("persistence_contract_only") is not True
                    or war_scope_plan.get("listener_scope_writes_allowed") is not False
                    or war_scope_plan.get("war_scope_writes_allowed") is not False
                    or not {"on_pre_winning_war", "on_ending_war"} <= set(
                        _string_refs(war_scope_plan.get("war_scope_available_from_hooks"))
                    )
                ):
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} listener preview missing war scope availability plan"
                    )
                handoff_boundary = preview.get("row_state_handoff_boundary")
                if (
                    not isinstance(handoff_boundary, dict)
                    or handoff_boundary.get("handoff_only") is not True
                    or handoff_boundary.get("row_state_writes_allowed") is not False
                    or not handoff_boundary.get("entity_keys")
                ):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} listener preview missing row-state handoff boundary")

    expected_preview_family_counts = {
        "event": 32,
        "localization": 40,
        "effect": 40,
        "cleanup": 32,
        "trigger": 24,
        "gui": 8,
        "listener": 1,
    }
    for family, expected_count in expected_preview_family_counts.items():
        actual_count = preview_family_counts[family]
        if actual_count != expected_count:
            errors.append(f"expected {expected_count} repeated-row {family} previews, got {actual_count}")
    total_preview_count = sum(preview_family_counts.values())
    if int(report.get("preview_count", -1)) != total_preview_count:
        errors.append("source preview report preview_count mismatch")
    if int(report.get("preview_count", -1)) != 177:
        errors.append(f"expected 177 repeated-row source previews, got {report.get('preview_count')}")
    return errors


def _repeated_row_artifact_identity(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(item.get("pilot_key", "")),
        str(item.get("row_set_key", "")),
        str(item.get("artifact_kind", "")),
    )


def _repeated_row_source_writer_evidence_block(
    *,
    status: str,
    evidence_type: str,
    summary: str,
    paths: list[str] | None = None,
    anchors: dict[str, Any] | None = None,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "evidence_type": evidence_type,
        "summary": summary,
        "paths": paths or [],
        "anchors": anchors or {},
        "blockers": blockers or [],
    }


def _repeated_row_event_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    preview_event_id = preview_data.get("preview_event_id")
    source_body_preview = dict(preview_data.get("source_body_preview", {}))
    namespace = str(
        source_body_preview.get("namespace")
        or contract.get("namespace_policy")
        or "tv_engineering_department"
    )
    title_key = str(source_body_preview.get("title_key", ""))
    desc_key = str(source_body_preview.get("desc_key", ""))
    option_keys = _string_refs(source_body_preview.get("option_keys"))
    future_target = str(
        contract.get(
            "candidate_future_source_target_path",
            preview_data.get("future_source_target_path", ""),
        )
    )
    return {
        "contract_family": "event",
        "pilot_key": pilot_key,
        "artifact_kind": str(artifact.get("artifact_kind", "")),
        "wonder_key": wonder_key,
        "row_set_key": str(artifact.get("row_set_key", "")),
        "readiness_status": "blocked",
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "namespace": namespace,
        "event_id_evidence_sources": ["spec.event_ids", "node_graph.nodes[].event_id"],
        "event_id_evidence": list(preview_data.get("event_id_evidence", []) or []),
        "node_event_id_evidence": list(preview_data.get("node_event_id_evidence", []) or []),
        "preview_event_id": preview_event_id,
        "source_body_preview": source_body_preview,
        "localization_key_handoff": {
            "title_key": title_key,
            "desc_key": desc_key,
            "option_keys": option_keys,
            "key_policy": str(contract.get("localization_key_policy", "")),
            "handoff_only": True,
            "localization_source_writer_allowed": False,
        },
        "option_effect_handoff": dict(preview_data.get("option_effect_handoff", {})),
        "safety_notes": {
            "hidden_executor_handoff_only": True,
            "tooltip_heavy_finalization_allowed": False,
            "row_state_writes_allowed": False,
            "source_ready_allowed": False,
        },
        "future_source_target_path": future_target,
        "future_source_target_path_pattern": str(contract.get("future_source_target_path_pattern", "")),
    }


def _repeated_row_localization_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    preview_event_id = preview_data.get("preview_event_id", "<event_id>")
    event_key_prefix = f"tv_engineering_department.{preview_event_id}"
    loc_key_plan = list(preview_data.get("loc_key_plan", []) or [])
    loc_group = str((preview_data.get("source_body_preview") or {}).get("loc_group", ""))
    namespace = str(preview_data.get("loc_key_namespace", ""))
    entity_refs = _string_refs(preview_data.get("entity_refs") or artifact.get("entity_keys"))
    row_key_groups: dict[str, list[dict[str, Any]]] = {}
    for group in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUPS:
        loc_scopes = entity_refs if group != "summary_text" else ["summary"]
        row_key_groups[group] = [
            {
                "loc_group": group,
                "entity_key": entity_key,
                "keys": {
                    language: f"{namespace}.{entity_key}.{group}"
                    for language in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS
                },
                "contract_only": True,
            }
            for entity_key in loc_scopes
        ]
    future_target_pattern = str(contract.get("future_source_target_path_pattern", ""))
    return {
        "contract_family": "localization",
        "pilot_key": pilot_key,
        "artifact_kind": str(artifact.get("artifact_kind", "")),
        "wonder_key": wonder_key,
        "row_set_key": str(artifact.get("row_set_key", "")),
        "readiness_status": "blocked",
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "language_ownership_boundary": {
            "required_languages": list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS),
            "english_owner": "src/main_menu/localization/english",
            "simp_chinese_owner": "src/main_menu/localization/simp_chinese",
            "missing_bilingual_coverage_allowed": False,
        },
        "event_key_handoff": {
            "title_key": f"{event_key_prefix}.t",
            "desc_key": f"{event_key_prefix}.d",
            "option_key_pattern": f"{event_key_prefix}.a",
            "handoff_only": True,
            "event_source_writer_allowed": False,
        },
        "key_allocation": {
            "loc_key_namespace": namespace,
            "loc_group": loc_group,
            "required_groups": list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUPS),
            "row_key_groups": row_key_groups,
            "loc_key_plan": loc_key_plan,
        },
        "escaping_bom_boundary": {
            "loc_line_function": "wonder_mechanics._core.loc_line",
            "quote_escaped": (preview_data.get("loc_line_policy_probe") or {}).get("quote_escaped"),
            "newline_escaped": (preview_data.get("loc_line_policy_probe") or {}).get("newline_escaped"),
            "bom_encoding": (preview_data.get("loc_line_policy_probe") or {}).get("bom_encoding"),
            "writes_file": False,
            "unsafe_quote_newline_handling_allowed": False,
        },
        "future_source_target_path_pattern": future_target_pattern,
        "future_source_target_path": str(
            contract.get(
                "candidate_future_source_target_path",
                preview_data.get("future_source_target_path", ""),
            )
        ),
    }


def _repeated_row_effect_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(preview_data.get("entity_refs") or artifact.get("entity_keys"))
    aggregate_projection_refs = _string_refs(
        preview_data.get("aggregate_projection_refs") or artifact.get("aggregate_projection_variables")
    )
    future_target_pattern = str(contract.get("future_source_target_path_pattern", ""))
    future_target = str(contract.get("candidate_future_source_target_path", preview_data.get("future_source_target_path", "")))
    operation_by_artifact = {
        "scripted_effect_row_init": "row_init",
        "scripted_effect_row_state_write": "row_state_write",
        "scripted_effect_branch_write": "branch_write",
        "scripted_effect_aggregate_refresh": "aggregate_refresh",
        "scripted_effect_cleanup_write": "cleanup_write_handoff",
    }
    active_operation = operation_by_artifact.get(artifact_kind, "")
    required_operations = [
        "row_init",
        "row_state_write",
        "branch_write",
        "aggregate_refresh",
        "cleanup_write_handoff",
    ]
    return {
        "contract_family": "effect",
        "pilot_key": pilot_key,
        "artifact_kind": artifact_kind,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "readiness_status": "blocked",
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_type": "common/scripted_effects",
        "effect_body_writes_allowed": False,
        "row_state_writes_allowed": False,
        "row_state_write_schema_allowed": False,
        "source_body_preview": dict(preview_data.get("source_body_preview", {})),
        "future_effect_name_plan": dict(preview_data.get("future_effect_name_plan", {})),
        "effect_operation_coverage": {
            "required_operations": required_operations,
            "active_operation": active_operation,
            "row_init": artifact_kind == "scripted_effect_row_init",
            "row_state_write": artifact_kind == "scripted_effect_row_state_write",
            "branch_write": artifact_kind == "scripted_effect_branch_write",
            "aggregate_refresh": artifact_kind == "scripted_effect_aggregate_refresh",
            "cleanup_write_handoff": artifact_kind == "scripted_effect_cleanup_write",
            "coverage_only": True,
            "effect_body_emitted": False,
        },
        "row_state_schema_boundary": {
            "row_set_key": row_set_key,
            "entity_keys": entity_refs,
            "row_entity_refs": dict(preview_data.get("row_entity_refs", {})),
            "schema_contract_only": True,
            "row_state_writes_allowed": False,
            "row_state_write_schema_allowed": False,
            "source_target_boundary": str(artifact.get("source_target_boundary", "")),
        },
        "aggregate_refresh_boundary": {
            "aggregate_projection_refs": aggregate_projection_refs,
            "aggregate_projection_boundary": str(
                contract.get(
                    "aggregate_projection_boundary",
                    preview_data.get("aggregate_projection_boundary", ""),
                )
            ),
            "aggregate_refresh_operation": artifact_kind == "scripted_effect_aggregate_refresh",
            "projection_only": True,
            "body_emitted": False,
        },
        "cleanup_write_handoff": {
            "handoff_only": True,
            "cleanup_lifecycle_scope": str(contract.get("cleanup_lifecycle_scope", "")),
            "effect_cleanup_artifact": artifact_kind == "scripted_effect_cleanup_write",
            "handoff_responsibility": dict(preview_data.get("handoff_responsibility", {})),
            "cleanup_source_writer_allowed": False,
            "row_state_writes_allowed": False,
            "body_emitted": False,
        },
        "required_validations": _string_refs(contract.get("required_validations")),
        "blocker_reasons": _string_refs(contract.get("blocker_reasons")),
        "future_source_target_path_pattern": future_target_pattern,
        "future_source_target_path": future_target,
    }


def _repeated_row_cleanup_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(preview_data.get("entity_refs") or artifact.get("entity_keys"))
    aggregate_projection_refs = _string_refs(
        preview_data.get("aggregate_projection_refs") or artifact.get("aggregate_projection_variables")
    )
    cleanup_coverage = dict(preview_data.get("cleanup_coverage", {}))
    cleanup_coverage.setdefault("coverage_group", list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_CLEANUP_COVERAGE_SCOPES))
    cleanup_scope = str(contract.get("cleanup_lifecycle_scope", ""))
    future_target_pattern = str(contract.get("future_source_target_path_pattern", ""))
    future_target = str(contract.get("candidate_future_source_target_path", preview_data.get("future_source_target_path", "")))
    return {
        "contract_family": "cleanup",
        "pilot_key": pilot_key,
        "artifact_kind": artifact_kind,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "readiness_status": "blocked",
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_type": "common/scripted_effects",
        "effect_body_writes_allowed": False,
        "row_state_writes_allowed": False,
        "row_state_write_schema_allowed": False,
        "source_body_preview": dict(preview_data.get("source_body_preview", {})),
        "cleanup_lifecycle_scope": cleanup_scope,
        "cleanup_coverage": cleanup_coverage,
        "cleanup_scope_plan": dict(preview_data.get("cleanup_scope_plan", {})),
        "ownership_reset_branch_boundary": {
            "required_branches": ["ownership_loss", "ritual_reset"],
            "ownership_loss_cleanup_artifact_kind": "cleanup_ownership_loss",
            "ritual_reset_cleanup_artifact_kind": "cleanup_ritual_reset",
            "ownership_loss_planned": "ownership_loss" in _string_refs(cleanup_coverage.get("coverage_group")),
            "ritual_reset_planned": "ritual_reset" in _string_refs(cleanup_coverage.get("coverage_group")),
            "unsafe_pre_eval_writes_allowed": False,
            "effect_body_writes_allowed": False,
            "body_emitted": False,
        },
        "row_entity_lifecycle_coverage": {
            "row_set_key": row_set_key,
            "entity_keys": entity_refs,
            "row_entity_refs": dict(preview_data.get("row_entity_refs", {})),
            "cleanup_lifecycle_scope": cleanup_scope,
            "lifecycle_scopes": list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_CLEANUP_COVERAGE_SCOPES),
            "schema_contract_only": True,
            "row_state_write_schema_allowed": False,
        },
        "aggregate_projection_boundary": {
            "aggregate_projection_refs": aggregate_projection_refs,
            "aggregate_projection_boundary": str(
                contract.get(
                    "aggregate_projection_boundary",
                    preview_data.get("aggregate_projection_boundary", ""),
                )
            ),
            "projection_only": True,
            "body_emitted": False,
        },
        "required_validations": _string_refs(contract.get("required_validations")),
        "blocker_reasons": _string_refs(contract.get("blocker_reasons")),
        "future_source_target_path_pattern": future_target_pattern,
        "future_source_target_path": future_target,
    }


def _repeated_row_trigger_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    aggregate_projection_refs = _string_refs(
        preview_data.get("aggregate_projection_refs") or artifact.get("aggregate_projection_variables")
    )
    future_target_pattern = str(contract.get("future_source_target_path_pattern", ""))
    future_target = str(contract.get("candidate_future_source_target_path", preview_data.get("future_source_target_path", "")))
    eligibility_plan = dict(preview_data.get("eligibility_condition_group_plan", {}))
    row_completion_plan = dict(preview_data.get("row_completion_condition_group_plan", {}))
    tooltip_safe_plan = dict(preview_data.get("tooltip_safe_condition_group_plan", {}))
    return {
        "contract_family": "trigger",
        "pilot_key": pilot_key,
        "artifact_kind": artifact_kind,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "readiness_status": "blocked",
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_type": "common/scripted_triggers",
        "trigger_body_writes_allowed": False,
        "tooltip_safe_unsafe_write_paths_allowed": False,
        "source_body_preview": dict(preview_data.get("source_body_preview", {})),
        "future_trigger_name_plan": dict(preview_data.get("future_trigger_name_plan", {})),
        "condition_group_coverage": {
            "required_groups": ["eligibility", "row_completion", "tooltip_safe"],
            "active_group": {
                "scripted_trigger_eligibility": "eligibility",
                "scripted_trigger_row_completion": "row_completion",
                "scripted_trigger_tooltip_safe_condition_group": "tooltip_safe",
            }.get(artifact_kind, ""),
            "eligibility": eligibility_plan,
            "row_completion": row_completion_plan,
            "tooltip_safe": tooltip_safe_plan,
            "predicate_group_only": True,
        },
        "forbidden_write_paths": {
            "forbidden_contexts": ["tooltip", "pre_evaluation"],
            "tooltip_context_write_paths_allowed": False,
            "pre_evaluation_write_paths_allowed": False,
            "unsafe_effect_calls_allowed": False,
            "row_state_writes_allowed": False,
            "source_writes_allowed": False,
            "tooltip_safe_unsafe_write_paths_allowed": False,
        },
        "aggregate_projection_boundary": {
            "aggregate_projection_refs": aggregate_projection_refs,
            "aggregate_projection_boundary": str(
                contract.get(
                    "aggregate_projection_boundary",
                    preview_data.get("aggregate_boundary", ""),
                )
            ),
            "projection_only": True,
        },
        "required_validations": _string_refs(contract.get("required_validations")),
        "blocker_reasons": _string_refs(contract.get("blocker_reasons")),
        "future_source_target_path_pattern": future_target_pattern,
        "future_source_target_path": future_target,
    }


def _repeated_row_gui_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(preview_data.get("entity_refs") or artifact.get("entity_keys"))
    aggregate_projection_refs = _string_refs(
        preview_data.get("aggregate_projection_refs") or artifact.get("aggregate_projection_variables")
    )
    future_target_pattern = str(contract.get("future_source_target_path_pattern", ""))
    future_target = str(contract.get("candidate_future_source_target_path", preview_data.get("future_source_target_path", "")))
    return {
        "contract_family": "gui",
        "pilot_key": pilot_key,
        "artifact_kind": artifact_kind,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "readiness_status": "blocked",
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_type": "in_game/gui/panels/organization",
        "source_body_preview": dict(preview_data.get("source_body_preview", {})),
        "fixed_row_widget_plan": dict(preview_data.get("fixed_row_widget_plan", {})),
        "per_row_variable_binding_plan": dict(preview_data.get("per_row_variable_binding_plan", {})),
        "actor_checklist_incident_row_policy": {
            "artifact_kind": artifact_kind,
            "row_policy": str(contract.get("actor_checklist_incident_row_policy", "")),
            "actor_slots_policy_applies": artifact_kind == "gui_actor_slots_row",
            "checklist_policy_applies": artifact_kind == "gui_checklist_row",
            "incident_log_policy_applies": artifact_kind == "gui_incident_log_row",
            "distinct_row_policies_required": True,
            "aggregate_only_display_allowed": False,
            "gui_body_emitted": False,
        },
        "tooltip_localization_linkage": dict(preview_data.get("tooltip_localization_linkage", {})),
        "gui_event_localization_key_linkage": {
            "gui_event_key_linkage": dict(preview_data.get("gui_event_key_linkage", {})),
            "tooltip_localization_linkage": dict(preview_data.get("tooltip_localization_linkage", {})),
            "localization_linkage_only": True,
            "gui_source_writer_allowed": False,
            "localization_source_writer_allowed": False,
            "event_source_writer_allowed": False,
            "source_body_emitted": False,
        },
        "aggregate_projection_boundary": {
            "aggregate_projection_refs": aggregate_projection_refs,
            "aggregate_projection_boundary": str(
                contract.get(
                    "aggregate_projection_boundary",
                    preview_data.get("aggregate_projection_boundary", ""),
                )
            ),
            "projection_only": True,
            "aggregate_only_display_allowed": False,
            "body_emitted": False,
        },
        "row_entity_refs": dict(
            preview_data.get(
                "row_entity_refs",
                {
                    "row_set_key": row_set_key,
                    "entity_keys": entity_refs,
                },
            )
        ),
        "aggregate_only_display_allowed": False,
        "gui_source_body_allowed": False,
        "gui_source_writes_allowed": False,
        "row_state_writes_allowed": False,
        "source_ready_allowed": False,
        "required_validations": _string_refs(contract.get("required_validations")),
        "blocker_reasons": _string_refs(contract.get("blocker_reasons")),
        "future_source_target_path_pattern": future_target_pattern,
        "future_source_target_path": future_target,
    }


def _repeated_row_listener_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    pilot_key = str(artifact.get("pilot_key", ""))
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    artifact_kind = str(artifact.get("artifact_kind", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    entity_refs = _string_refs(preview_data.get("entity_refs") or artifact.get("entity_keys"))
    future_target_pattern = str(contract.get("future_source_target_path_pattern", ""))
    future_target = str(contract.get("candidate_future_source_target_path", preview_data.get("future_source_target_path", "")))
    return {
        "contract_family": "listener",
        "pilot_key": pilot_key,
        "artifact_kind": artifact_kind,
        "wonder_key": wonder_key,
        "row_set_key": row_set_key,
        "readiness_status": "blocked",
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_type": "common/on_action",
        "listener_artifact_scope": str(contract.get("listener_artifact_scope", "")),
        "source_body_preview": dict(preview_data.get("source_body_preview", {})),
        "on_action_target_path_plan": dict(preview_data.get("on_action_target_path_plan", {})),
        "on_action_hook_linkage_plan": dict(preview_data.get("on_action_hook_linkage_plan", {})),
        "selected_ritual_trigger_linkage": dict(preview_data.get("selected_ritual_trigger_linkage", {})),
        "war_scope_availability_persistence_plan": dict(
            preview_data.get("war_scope_availability_persistence_plan", {})
        ),
        "row_state_handoff_boundary": dict(
            preview_data.get(
                "row_state_handoff_boundary",
                {
                    "row_set_key": row_set_key,
                    "entity_keys": entity_refs,
                    "handoff_only": True,
                    "row_state_writes_allowed": False,
                },
            )
        ),
        "listener_body_allowed": False,
        "listener_scope_writes_allowed": False,
        "war_scope_writes_allowed": False,
        "row_state_writes_allowed": False,
        "source_writes_allowed": False,
        "source_ready_allowed": False,
        "required_validations": _string_refs(contract.get("required_validations")),
        "blocker_reasons": _string_refs(contract.get("blocker_reasons")),
        "future_source_target_path_pattern": future_target_pattern,
        "future_source_target_path": future_target,
    }


def _repeated_row_source_writer_closure_contract(
    *,
    artifact: dict[str, Any],
    preview_data: dict[str, Any],
    contract: dict[str, Any],
    contract_family: str,
) -> dict[str, Any] | None:
    if contract_family == "event":
        return _repeated_row_event_source_writer_closure_contract(
            artifact=artifact,
            preview_data=preview_data,
            contract=contract,
        )
    if contract_family == "localization":
        return _repeated_row_localization_source_writer_closure_contract(
            artifact=artifact,
            preview_data=preview_data,
            contract=contract,
        )
    if contract_family == "effect":
        return _repeated_row_effect_source_writer_closure_contract(
            artifact=artifact,
            preview_data=preview_data,
            contract=contract,
        )
    if contract_family == "cleanup":
        return _repeated_row_cleanup_source_writer_closure_contract(
            artifact=artifact,
            preview_data=preview_data,
            contract=contract,
        )
    if contract_family == "trigger":
        return _repeated_row_trigger_source_writer_closure_contract(
            artifact=artifact,
            preview_data=preview_data,
            contract=contract,
        )
    if contract_family == "gui":
        return _repeated_row_gui_source_writer_closure_contract(
            artifact=artifact,
            preview_data=preview_data,
            contract=contract,
        )
    if contract_family == "listener":
        return _repeated_row_listener_source_writer_closure_contract(
            artifact=artifact,
            preview_data=preview_data,
            contract=contract,
        )
    return None


def _repeated_row_no_write_source_writer_target_paths(
    *,
    contract_family: str,
    pilot_key: str,
    candidate_path: str,
    path_pattern: str,
) -> list[str]:
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    if contract_family == "localization":
        localization_pattern = path_pattern or candidate_path
        return [
            localization_pattern.replace("<wonder_key>", wonder_key).replace("<lang>", language)
            for language in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS
        ]
    target_path = candidate_path or path_pattern.replace("<wonder_key>", wonder_key)
    if target_path:
        target_path = target_path.replace("<wonder_key>", wonder_key)
    return [target_path] if target_path else []


def _repeated_row_no_write_source_writer_contract_evidence(
    *,
    artifact_kind: str,
    contract_family: str,
    target_paths: list[str],
    owner_generator: str,
    owner_generator_candidate: str,
    syntax_summary: str,
    syntax_paths: list[str],
    validation_refs: list[str],
    blocker_reasons: list[str],
    source_target_boundary: Any,
) -> dict[str, Any]:
    normalized_target_paths = sorted({path for path in _string_refs(target_paths) if path})
    normalized_blockers = sorted({blocker for blocker in _string_refs(blocker_reasons) if blocker})
    return {
        "contract_evidence_only": True,
        "artifact_kind": artifact_kind,
        "contract_family": contract_family,
        "target_path": normalized_target_paths[0] if normalized_target_paths else "",
        "target_paths": normalized_target_paths,
        "owner_generator": owner_generator,
        "owner_generator_candidate": owner_generator_candidate,
        "eu5_syntax_evidence": {
            "summary": syntax_summary,
            "paths": _string_refs(syntax_paths),
        },
        "validation_refs": sorted({validation for validation in _string_refs(validation_refs) if validation}),
        "validation_command": REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS[0],
        "verification_commands": list(REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS),
        "source_writer_blocker_reasons": normalized_blockers,
        "source_writer_still_blocked_reason": "; ".join(normalized_blockers),
        "source_target_boundary": source_target_boundary,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _repeated_row_source_writer_readiness_artifact(
    *,
    artifact: dict[str, Any],
    preview: dict[str, Any] | None,
) -> dict[str, Any]:
    artifact_kind = str(artifact.get("artifact_kind", ""))
    pilot_key = str(artifact.get("pilot_key", ""))
    row_set_key = str(artifact.get("row_set_key", ""))
    contract = artifact.get("source_target_contract") if isinstance(artifact.get("source_target_contract"), dict) else {}
    evidence_mapping = artifact.get("evidence_mapping") if isinstance(artifact.get("evidence_mapping"), dict) else {}
    preview_exists = isinstance(preview, dict)
    preview_data = preview if isinstance(preview, dict) else {}
    contract_family = str(contract.get("contract_family", preview_data.get("preview_family", "")))
    current_contract_status = str(contract.get("status", preview_data.get("contract_status", "")))
    blocker_sources = (
        _string_refs(contract.get("blocker_reasons"))
        + _string_refs(preview_data.get("blocker_reasons"))
        + _string_refs(evidence_mapping.get("generator_missing_reason"))
    )
    unresolved_writer_blockers = sorted(set(blocker for blocker in blocker_sources if blocker.strip()))
    if not preview_exists:
        unresolved_writer_blockers.append("missing source preview")
    if not unresolved_writer_blockers:
        unresolved_writer_blockers.append("missing verified source-writer evidence chain")

    validation_anchors: dict[str, Any] = {
        "required_validations": _string_refs(contract.get("required_validations")),
        "preview_family": str(preview_data.get("preview_family", "")),
        "source_preview_closed": bool(preview_exists and preview_data.get("source_ready") is False),
    }
    for key in (
        "event_id_evidence_sources",
        "event_id_evidence",
        "node_event_id_evidence",
        "loc_line_policy_probe",
        "cleanup_coverage",
        "fixed_row_widget_plan",
        "per_row_variable_binding_plan",
        "on_action_hook_linkage_plan",
    ):
        if key in preview_data:
            validation_anchors[key] = preview_data[key]

    lifecycle_anchors: dict[str, Any] = {
        "row_set_key": row_set_key,
        "entity_refs": _string_refs(preview_data.get("entity_refs") or artifact.get("entity_keys")),
        "aggregate_projection_variables": _string_refs(artifact.get("aggregate_projection_variables")),
        "aggregate_projection_boundary": str(
            contract.get(
                "aggregate_projection_boundary",
                preview_data.get("aggregate_projection_boundary", preview_data.get("aggregate_boundary", "")),
            )
        ),
    }
    for key in (
        "cleanup_scope_plan",
        "cleanup_coverage",
        "row_entity_refs",
        "handoff_responsibility",
        "option_effect_handoff",
        "tooltip_safe_condition_group_plan",
        "war_scope_availability_persistence_plan",
        "row_state_handoff_boundary",
    ):
        if key in preview_data:
            lifecycle_anchors[key] = preview_data[key]

    boundary_paths = _string_refs(evidence_mapping.get("evidence_source_paths"))
    future_target = str(contract.get("candidate_future_source_target_path", preview_data.get("future_source_target_path", "")))
    target_paths = _repeated_row_no_write_source_writer_target_paths(
        contract_family=contract_family,
        pilot_key=pilot_key,
        candidate_path=future_target,
        path_pattern=str(contract.get("future_source_target_path_pattern", "")),
    )
    if future_target:
        boundary_paths = sorted(set(boundary_paths + [future_target]))

    readiness_artifact = {
        "artifact_kind": artifact_kind,
        "contract_family": contract_family,
        "pilot_key": pilot_key,
        "row_set_key": row_set_key,
        "current_contract_status": current_contract_status,
        "preview_exists": preview_exists,
        "readiness_status": "blocked",
        "eu5_syntax_evidence": _repeated_row_source_writer_evidence_block(
            status=str(artifact.get("evidence_status", "interface_candidate")),
            evidence_type="interface_candidate",
            summary=str(evidence_mapping.get("eu5_source_syntax_pattern", "")),
            paths=_string_refs(evidence_mapping.get("evidence_source_paths")),
            anchors={
                "source_body_preview": preview_data.get("source_body_preview", {}),
                "required_eu5_interfaces": _string_refs(artifact.get("required_eu5_interfaces")),
            },
            blockers=unresolved_writer_blockers,
        ),
        "generator_ownership_evidence": _repeated_row_source_writer_evidence_block(
            status="interface_candidate",
            evidence_type="interface_candidate",
            summary=str(evidence_mapping.get("generator_missing_reason", "")),
            paths=[path for path in [str(evidence_mapping.get("generator_candidate", ""))] if path],
            anchors={
                "owner_generator": str(artifact.get("owner_generator", "")),
                "planned_owner_exists": str(artifact.get("owner_generator", ""))
                in REPEATED_ENTITY_ROW_SOURCE_PLAN_EXISTING_GENERATORS,
            },
            blockers=[
                "planned owner generator is not registered as an existing source writer",
                *unresolved_writer_blockers,
            ],
        ),
        "source_target_boundary_evidence": _repeated_row_source_writer_evidence_block(
            status="blocked",
            evidence_type="source_target_boundary",
            summary=str(artifact.get("source_target_boundary", "")),
            paths=boundary_paths,
            anchors={
                "contract_family": contract_family,
                "future_target_only": contract.get("future_target_only"),
                "future_source_target_path_pattern": str(contract.get("future_source_target_path_pattern", "")),
                "candidate_future_source_target_path": future_target,
                "preview_future_source_target_path": str(preview_data.get("future_source_target_path", "")),
            },
            blockers=unresolved_writer_blockers,
        ),
        "validation_coverage_evidence": _repeated_row_source_writer_evidence_block(
            status="interface_candidate",
            evidence_type="validation_coverage",
            summary=(
                "Validation requirements and preview probes are present as contract data only; "
                "they do not prove source-writer readiness."
            ),
            paths=[],
            anchors=validation_anchors,
            blockers=unresolved_writer_blockers,
        ),
        "lifecycle_semantics_evidence": _repeated_row_source_writer_evidence_block(
            status="interface_candidate",
            evidence_type="lifecycle_semantics",
            summary=(
                "Row/entity lifecycle semantics are preserved from source-plan and source-preview data, "
                "but remain blocked until a writer owns row-state effects, triggers, GUI, localization, and cleanup."
            ),
            paths=[],
            anchors=lifecycle_anchors,
            blockers=unresolved_writer_blockers,
        ),
        "unresolved_writer_blockers": unresolved_writer_blockers,
        "no_write_source_writer_contract_evidence": _repeated_row_no_write_source_writer_contract_evidence(
            artifact_kind=artifact_kind,
            contract_family=contract_family,
            target_paths=target_paths,
            owner_generator=str(artifact.get("owner_generator", "")),
            owner_generator_candidate=str(evidence_mapping.get("generator_candidate", "")),
            syntax_summary=str(evidence_mapping.get("eu5_source_syntax_pattern", "")),
            syntax_paths=_string_refs(evidence_mapping.get("evidence_source_paths")),
            validation_refs=_string_refs(contract.get("required_validations")),
            blocker_reasons=unresolved_writer_blockers,
            source_target_boundary=artifact.get("source_target_boundary", ""),
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }
    closure_contract = _repeated_row_source_writer_closure_contract(
        artifact=artifact,
        preview_data=preview_data,
        contract=contract,
        contract_family=contract_family,
    )
    if closure_contract is not None:
        readiness_artifact["closure_contract"] = closure_contract
    return readiness_artifact


def _repeated_row_source_writer_readiness_entry(
    *,
    entry_plan: dict[str, Any],
    entry_preview: dict[str, Any] | None,
) -> dict[str, Any]:
    previews = [
        preview
        for preview in (entry_preview or {}).get("previews", []) or []
        if isinstance(preview, dict)
    ]
    preview_by_identity = {
        _repeated_row_artifact_identity(preview): preview
        for preview in previews
    }
    artifacts = [
        _repeated_row_source_writer_readiness_artifact(
            artifact=artifact,
            preview=preview_by_identity.get(_repeated_row_artifact_identity(artifact)),
        )
        for artifact in entry_plan.get("artifacts", []) or []
        if isinstance(artifact, dict)
    ]
    return {
        "key": str(entry_plan.get("key", "")),
        "artifact_count": len(artifacts),
        "ready_artifact_count": sum(1 for artifact in artifacts if artifact.get("readiness_status") == "ready"),
        "blocked_artifact_count": sum(1 for artifact in artifacts if artifact.get("readiness_status") == "blocked"),
        "contract_family_summary": _count_by_key(artifacts, "contract_family"),
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "writes_src": False,
        "artifacts": artifacts,
    }


def _repeated_row_source_writer_closure_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    closure_family_counts = {family: 0 for family in REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS}
    no_write_violation_count = 0
    for artifact in artifacts:
        if artifact.get("may_write_src") is True:
            no_write_violation_count += 1
        if artifact.get("writes_src") is True:
            no_write_violation_count += 1
        if artifact.get("source_writer_allowed") is True:
            no_write_violation_count += 1
        closure = artifact.get("closure_contract")
        if not isinstance(closure, dict):
            continue
        family = str(closure.get("contract_family", artifact.get("contract_family", "")))
        if family in closure_family_counts:
            closure_family_counts[family] += 1
        if closure.get("may_write_src") is True:
            no_write_violation_count += 1
        if closure.get("writes_src") is True:
            no_write_violation_count += 1
        if closure.get("source_writer_allowed") is True:
            no_write_violation_count += 1
    missing_families = [
        family
        for family, expected_count in REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS.items()
        if closure_family_counts[family] != expected_count
    ]
    return {
        "closure_contract_count": sum(closure_family_counts.values()),
        "closure_family_summary": dict(sorted(closure_family_counts.items())),
        "closure_missing_families": missing_families,
        "closure_no_write_violation_count": no_write_violation_count,
    }


def repeated_entity_row_source_writer_readiness_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_plan: dict[str, Any] | None = None,
    source_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_plan is None:
        source_plan = repeated_entity_row_source_plan_for_payload(payload, statuses=statuses)
    if source_preview is None:
        source_preview = repeated_entity_row_source_preview_for_payload(
            payload,
            statuses=statuses,
            source_plan=source_plan,
        )
    preview_by_key = {
        str(entry.get("key", "")): entry
        for entry in source_preview.get("entries", []) or []
        if isinstance(entry, dict)
    }
    entries = [
        _repeated_row_source_writer_readiness_entry(
            entry_plan=entry_plan,
            entry_preview=preview_by_key.get(str(entry_plan.get("key", ""))),
        )
        for entry_plan in source_plan.get("entries", []) or []
        if isinstance(entry_plan, dict)
    ]
    artifacts = [
        artifact
        for entry in entries
        for artifact in entry.get("artifacts", []) or []
        if isinstance(artifact, dict)
    ]
    closure_summary = _repeated_row_source_writer_closure_summary(artifacts)
    report = {
        "statuses": sorted(statuses or {"source_codegen_ready"}),
        "artifact_count": len(artifacts),
        "ready_artifact_count": sum(1 for artifact in artifacts if artifact.get("readiness_status") == "ready"),
        "blocked_artifact_count": sum(1 for artifact in artifacts if artifact.get("readiness_status") == "blocked"),
        "contract_family_summary": _count_by_key(artifacts, "contract_family"),
        **closure_summary,
        "source_plan_artifact_count": int(source_plan.get("artifact_count", 0)),
        "source_preview_count": int(source_preview.get("preview_count", 0)),
        "source_preview_validation_errors": list(source_preview.get("validation_errors", [])),
        "source_plan_validation_errors": list(source_plan.get("validation_errors", [])),
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "writes_src": False,
        "entries": entries,
        "validation_errors": [],
        "notes": [
            "Repeated-row source-writer readiness is a no-write evidence ledger.",
            "It records remaining source-writer blockers after the 177/177 source preview closure.",
            "It does not promote source_codegen_ready or authorize src writes.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_source_writer_readiness(report)
    return report


def _readiness_status_is_forbidden_ready(value: Any) -> bool:
    return str(value or "").strip().lower().replace("-", "_") in {
        "source_ready",
        "ready",
        "verified",
        "backend_ready",
        "source_codegen_ready",
        "implementation_ready",
        "harness_generated",
    }


def _readiness_evidence_claims_verified(evidence: dict[str, Any]) -> bool:
    status = str(evidence.get("status", "")).strip().lower().replace("-", "_")
    evidence_type = str(evidence.get("evidence_type", "")).strip().lower().replace("-", "_")
    return status in {"verified", "source_ready", "backend_ready"} or evidence_type in {
        "verified",
        "source_ready",
        "backend_ready",
    }


def _validate_repeated_row_no_write_source_writer_contract_evidence(
    *,
    pilot_key: str,
    artifact_kind: str,
    contract_family: str,
    evidence: Any,
    expected_target_paths: list[str],
    expected_blockers: list[str],
) -> list[str]:
    errors: list[str] = []
    context = f"{pilot_key}: artifact {artifact_kind} no-write source-writer contract evidence"
    if not isinstance(evidence, dict) or not evidence:
        return [f"{context} missing"]
    missing = _missing_required(
        evidence,
        REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_CONTRACT_EVIDENCE_REQUIRED_FIELDS,
    )
    if missing:
        errors.append(f"{context} missing field(s): {', '.join(missing)}")
        return errors
    if evidence.get("contract_evidence_only") is not True:
        errors.append(f"{context} must be contract evidence only")
    if evidence.get("artifact_kind") != artifact_kind:
        errors.append(f"{context} artifact_kind mismatch")
    if evidence.get("contract_family") != contract_family:
        errors.append(f"{context} contract_family mismatch")

    target_paths = _string_refs(evidence.get("target_paths"))
    target_path = str(evidence.get("target_path", ""))
    if not target_path or target_path not in target_paths:
        errors.append(f"{context} missing target path")
    if sorted(target_paths) != sorted(_string_refs(expected_target_paths)):
        errors.append(f"{context} target paths mismatch")
    for path in target_paths:
        if not path.startswith("src/") or "<" in path or ">" in path:
            errors.append(f"{context} target path must be an explicit future src/ path: {path}")

    if not str(evidence.get("owner_generator", "")).strip():
        errors.append(f"{context} missing owner generator")
    if not str(evidence.get("owner_generator_candidate", "")).strip():
        errors.append(f"{context} missing owner generator candidate")

    syntax_evidence = evidence.get("eu5_syntax_evidence")
    if not isinstance(syntax_evidence, dict):
        errors.append(f"{context} missing EU5 syntax evidence")
    else:
        if not str(syntax_evidence.get("summary", "")).strip():
            errors.append(f"{context} missing EU5 syntax evidence summary")
        if not _string_refs(syntax_evidence.get("paths")):
            errors.append(f"{context} missing EU5 syntax evidence paths")

    validation_refs = _string_refs(evidence.get("validation_refs"))
    if not validation_refs:
        errors.append(f"{context} missing validation refs")
    verification_commands = _string_refs(evidence.get("verification_commands"))
    if tuple(verification_commands) != REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS:
        errors.append(f"{context} verification commands mismatch")
    if evidence.get("validation_command") != REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS[0]:
        errors.append(f"{context} validation command mismatch")

    blockers = sorted({blocker for blocker in _string_refs(evidence.get("source_writer_blocker_reasons")) if blocker})
    expected_blocker_set = sorted({blocker for blocker in _string_refs(expected_blockers) if blocker})
    if not blockers:
        errors.append(f"{context} missing source-writer blocker reasons")
    if blockers != expected_blocker_set:
        errors.append(f"{context} source-writer blocker reasons mismatch")
    if not str(evidence.get("source_writer_still_blocked_reason", "")).strip():
        errors.append(f"{context} missing still-blocked reason")
    if not evidence.get("source_target_boundary"):
        errors.append(f"{context} missing source-target boundary")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src"):
        if evidence.get(flag) is not False:
            errors.append(f"{context} {flag} must be false")
    return errors


def _validate_repeated_row_no_write_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    contract_family: str,
    closure: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if closure.get("contract_family") != contract_family:
        errors.append(f"{pilot_key}: artifact {artifact_kind} {contract_family} closure contract_family changed")
    if closure.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} {contract_family} closure source_writer_allowed must be false")
    if closure.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} {contract_family} closure may_write_src must be false")
    if closure.get("writes_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} {contract_family} closure writes_src must be false")
    if _readiness_status_is_forbidden_ready(closure.get("readiness_status")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} {contract_family} closure must stay blocked")
    if str(closure.get("readiness_status", "")) != "blocked":
        errors.append(f"{pilot_key}: artifact {artifact_kind} {contract_family} closure readiness_status must be blocked")
    for forbidden_field in (
        "verified",
        "source_ready",
        "backend_ready",
        "source_codegen_ready",
        "implementation_ready",
        "harness_generated",
    ):
        if forbidden_field in closure:
            errors.append(
                f"{pilot_key}: artifact {artifact_kind} {contract_family} closure must not declare {forbidden_field}"
            )
    for field, value in closure.items():
        if field == "readiness_status":
            continue
        if field.endswith("status") and _readiness_status_is_forbidden_ready(value):
            errors.append(
                f"{pilot_key}: artifact {artifact_kind} {contract_family} closure must not claim source-ready status"
            )
    nested_source_ready_fields = [
        field
        for field in _closure_source_ready_field_names(closure)
        if field not in {
            "readiness_status",
            "source_ready_allowed",
        }
        and not field.endswith(".source_ready_allowed")
    ]
    for field in nested_source_ready_fields:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} {contract_family} closure must not declare source-ready field {field}"
        )
    return errors


def _closure_source_ready_field_names(closure: dict[str, Any]) -> list[str]:
    forbidden_names = {
        "verified",
        "source_ready",
        "backend_ready",
        "source_codegen_ready",
        "implementation_ready",
        "harness_generated",
    }
    found: list[str] = []

    def visit(value: Any, path: str) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key)
                child_path = f"{path}.{key_text}" if path else key_text
                if key_text in forbidden_names:
                    found.append(child_path)
                if key_text.endswith("status") and _readiness_status_is_forbidden_ready(child):
                    found.append(child_path)
                visit(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")

    visit(closure, "")
    return found


def _validate_repeated_row_event_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    errors = _validate_repeated_row_no_write_source_writer_closure_contract(
        pilot_key=pilot_key,
        artifact_kind=artifact_kind,
        contract_family="event",
        closure=closure,
    )
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    expected_target = f"src/in_game/events/tv_wonder_unique_{wonder_key}_ritual_events.txt"
    if closure.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure source_writer_allowed must be false")
    if closure.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure may_write_src must be false")
    if closure.get("writes_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure writes_src must be false")
    if _readiness_status_is_forbidden_ready(closure.get("readiness_status")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure must stay blocked")
    if str(closure.get("readiness_status", "")) != "blocked":
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure readiness_status must be blocked")
    if closure.get("namespace") != "tv_engineering_department":
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing namespace")
    if closure.get("future_source_target_path") != expected_target:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing future target path")

    event_ids = [
        int(item["event_id"])
        for item in closure.get("event_id_evidence", []) or []
        if isinstance(item, dict) and "event_id" in item
    ]
    node_event_ids = [
        int(item["event_id"])
        for item in closure.get("node_event_id_evidence", []) or []
        if isinstance(item, dict) and "event_id" in item
    ]
    if not event_ids:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing spec event IDs")
    if not node_event_ids:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing node event IDs")
    preview_event_id = closure.get("preview_event_id")
    if preview_event_id not in event_ids or preview_event_id not in node_event_ids:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure must use existing spec/node event ID")

    source_body_preview = closure.get("source_body_preview")
    if not isinstance(source_body_preview, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing source body preview")
    else:
        if source_body_preview.get("namespace") != "tv_engineering_department":
            errors.append(f"{pilot_key}: artifact {artifact_kind} event body preview missing namespace")
        if source_body_preview.get("event_id") != preview_event_id:
            errors.append(f"{pilot_key}: artifact {artifact_kind} event body preview missing event id")
        if source_body_preview.get("no_row_state_write") is not True:
            errors.append(f"{pilot_key}: artifact {artifact_kind} event closure must forbid row-state writes")
        if source_body_preview.get("no_tooltip_heavy_finalization") is not True:
            errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing tooltip safety")
        if source_body_preview.get("no_source_ready") is not True:
            errors.append(f"{pilot_key}: artifact {artifact_kind} event closure must not be source-ready")

    loc_handoff = closure.get("localization_key_handoff")
    if not isinstance(loc_handoff, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing localization handoff")
    else:
        expected_prefix = f"tv_engineering_department.{preview_event_id}"
        if loc_handoff.get("handoff_only") is not True or loc_handoff.get("localization_source_writer_allowed") is not False:
            errors.append(f"{pilot_key}: artifact {artifact_kind} event closure localization handoff must be no-write")
        if loc_handoff.get("title_key") != f"{expected_prefix}.t":
            errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing title localization handoff")
        if loc_handoff.get("desc_key") != f"{expected_prefix}.d":
            errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing desc localization handoff")
        option_keys = _string_refs(loc_handoff.get("option_keys"))
        if f"{expected_prefix}.a" not in option_keys:
            errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing option localization handoff")

    option_handoff = closure.get("option_effect_handoff")
    if not isinstance(option_handoff, dict) or option_handoff.get("handoff_only") is not True:
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing option-effect handoff")
    elif not str(option_handoff.get("future_scripted_effect_name", "")).startswith(
        f"tv_wonder_unique_{wonder_key}_ritual_"
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure option-effect handoff is incomplete")

    safety_notes = closure.get("safety_notes")
    if not isinstance(safety_notes, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure missing safety notes")
    elif (
        safety_notes.get("hidden_executor_handoff_only") is not True
        or safety_notes.get("tooltip_heavy_finalization_allowed") is not False
        or safety_notes.get("row_state_writes_allowed") is not False
        or safety_notes.get("source_ready_allowed") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} event closure safety notes are incomplete")

    return errors


def _validate_repeated_row_localization_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    errors = _validate_repeated_row_no_write_source_writer_closure_contract(
        pilot_key=pilot_key,
        artifact_kind=artifact_kind,
        contract_family="localization",
        closure=closure,
    )
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    expected_pattern = "src/main_menu/localization/<lang>/tv_wonder_unique_<wonder_key>_ritual_l_<lang>.yml"
    expected_target = expected_pattern.replace("<wonder_key>", wonder_key)
    if closure.get("source_writer_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure source_writer_allowed must be false")
    if closure.get("may_write_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure may_write_src must be false")
    if closure.get("writes_src") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure writes_src must be false")
    if _readiness_status_is_forbidden_ready(closure.get("readiness_status")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure must stay blocked")
    if str(closure.get("readiness_status", "")) != "blocked":
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure readiness_status must be blocked")
    if closure.get("future_source_target_path_pattern") != expected_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing future target path pattern")
    if closure.get("future_source_target_path") != expected_target:
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing future target path")

    language_boundary = closure.get("language_ownership_boundary")
    if not isinstance(language_boundary, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing language boundary")
    else:
        if set(_string_refs(language_boundary.get("required_languages"))) != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing language boundary")
        if not str(language_boundary.get("english_owner", "")).endswith("english"):
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing English boundary")
        if not str(language_boundary.get("simp_chinese_owner", "")).endswith("simp_chinese"):
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing Simplified Chinese boundary")
        if language_boundary.get("missing_bilingual_coverage_allowed") is not False:
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure must forbid missing bilingual coverage")

    event_handoff = closure.get("event_key_handoff")
    if not isinstance(event_handoff, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing event key handoff")
    elif (
        not str(event_handoff.get("title_key", "")).endswith(".t")
        or not str(event_handoff.get("desc_key", "")).endswith(".d")
        or not str(event_handoff.get("option_key_pattern", "")).endswith(".a")
        or event_handoff.get("handoff_only") is not True
        or event_handoff.get("event_source_writer_allowed") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure event key handoff is incomplete")

    key_allocation = closure.get("key_allocation")
    if not isinstance(key_allocation, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing key allocation")
    else:
        namespace = str(key_allocation.get("loc_key_namespace", ""))
        if f"tv_wonder_unique_{wonder_key}_ritual" not in namespace:
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure key namespace is incomplete")
        required_groups = set(_string_refs(key_allocation.get("required_groups")))
        if set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUPS) - required_groups:
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing key allocation groups")
        row_key_groups = key_allocation.get("row_key_groups")
        if not isinstance(row_key_groups, dict):
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing row key groups")
        else:
            missing_groups = [
                group
                for group in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUPS
                if group not in row_key_groups
            ]
            if missing_groups:
                errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing row key groups")
            loc_group = str(key_allocation.get("loc_group", ""))
            if loc_group not in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LOC_GROUPS:
                errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure loc group is invalid")
            elif not row_key_groups.get(loc_group):
                errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing active loc group keys")
        loc_key_plan = key_allocation.get("loc_key_plan")
        if not isinstance(loc_key_plan, list) or not loc_key_plan:
            errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing key allocation")
        else:
            for item in loc_key_plan:
                if not isinstance(item, dict) or not isinstance(item.get("keys"), dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure key allocation item is incomplete")
                    continue
                if set(item["keys"]) != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing bilingual key allocation")
                for loc_key in item["keys"].values():
                    loc_key_text = str(loc_key)
                    if f"tv_wonder_unique_{wonder_key}_ritual" not in loc_key_text:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure key namespace is incomplete")

    escaping = closure.get("escaping_bom_boundary")
    if not isinstance(escaping, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing escaping/BOM boundary")
    elif (
        escaping.get("quote_escaped") is not True
        or escaping.get("newline_escaped") is not True
        or escaping.get("bom_encoding") != "utf-8-sig"
        or escaping.get("writes_file") is not False
        or escaping.get("unsafe_quote_newline_handling_allowed") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} localization closure missing escaping/BOM boundary")

    return errors


def _validate_repeated_row_effect_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    errors = _validate_repeated_row_no_write_source_writer_closure_contract(
        pilot_key=pilot_key,
        artifact_kind=artifact_kind,
        contract_family="effect",
        closure=closure,
    )
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    expected_pattern = "src/in_game/common/scripted_effects/tv_wonder_unique_<wonder_key>_ritual_effects.txt"
    expected_target = expected_pattern.replace("<wonder_key>", wonder_key)
    if closure.get("source_type") != "common/scripted_effects":
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure source_type changed")
    if closure.get("future_source_target_path_pattern") != expected_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing future target path pattern")
    if closure.get("future_source_target_path") != expected_target:
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing future target path")
    if closure.get("effect_body_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure effect_body_writes_allowed must be false")
    if closure.get("row_state_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure row_state_writes_allowed must be false")
    if closure.get("row_state_write_schema_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure row_state_write_schema_allowed must be false")

    operation_coverage = closure.get("effect_operation_coverage")
    operation_by_artifact = {
        "scripted_effect_row_init": "row_init",
        "scripted_effect_row_state_write": "row_state_write",
        "scripted_effect_branch_write": "branch_write",
        "scripted_effect_aggregate_refresh": "aggregate_refresh",
        "scripted_effect_cleanup_write": "cleanup_write_handoff",
    }
    required_operations = {
        "row_init",
        "row_state_write",
        "branch_write",
        "aggregate_refresh",
        "cleanup_write_handoff",
    }
    if not isinstance(operation_coverage, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing operation coverage")
    else:
        if not required_operations <= set(_string_refs(operation_coverage.get("required_operations"))):
            errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing operation coverage")
        expected_operation = operation_by_artifact.get(artifact_kind, "")
        if expected_operation and operation_coverage.get(expected_operation) is not True:
            errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing operation coverage")
        if operation_coverage.get("effect_body_emitted") is not False:
            errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure must not emit effect body")

    schema_boundary = closure.get("row_state_schema_boundary")
    if not isinstance(schema_boundary, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing row-state schema boundary")
    elif (
        schema_boundary.get("schema_contract_only") is not True
        or schema_boundary.get("row_state_writes_allowed") is not False
        or schema_boundary.get("row_state_write_schema_allowed") is not False
        or not _string_refs(schema_boundary.get("entity_keys"))
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing row-state schema boundary")

    aggregate_boundary = closure.get("aggregate_refresh_boundary")
    if not isinstance(aggregate_boundary, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing aggregate refresh boundary")
    elif (
        not isinstance(aggregate_boundary.get("aggregate_projection_refs"), list)
        or not str(aggregate_boundary.get("aggregate_projection_boundary", "")).strip()
        or aggregate_boundary.get("projection_only") is not True
        or aggregate_boundary.get("body_emitted") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing aggregate refresh boundary")

    cleanup_handoff = closure.get("cleanup_write_handoff")
    if not isinstance(cleanup_handoff, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing cleanup write handoff")
    elif (
        cleanup_handoff.get("handoff_only") is not True
        or cleanup_handoff.get("cleanup_source_writer_allowed") is not False
        or cleanup_handoff.get("row_state_writes_allowed") is not False
        or cleanup_handoff.get("body_emitted") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} effect closure missing cleanup write handoff")

    return errors


def _validate_repeated_row_cleanup_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    errors = _validate_repeated_row_no_write_source_writer_closure_contract(
        pilot_key=pilot_key,
        artifact_kind=artifact_kind,
        contract_family="cleanup",
        closure=closure,
    )
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    expected_pattern = "src/in_game/common/scripted_effects/tv_wonder_unique_<wonder_key>_ritual_effects.txt"
    expected_target = expected_pattern.replace("<wonder_key>", wonder_key)
    if closure.get("source_type") != "common/scripted_effects":
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure source_type changed")
    if closure.get("future_source_target_path_pattern") != expected_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing future target path pattern")
    if closure.get("future_source_target_path") != expected_target:
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing future target path")
    if closure.get("effect_body_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure effect_body_writes_allowed must be false")
    if closure.get("row_state_write_schema_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure row_state_write_schema_allowed must be false")

    expected_scope = REPEATED_ENTITY_ROW_EFFECT_CLEANUP_SOURCE_TARGET_CONTRACT_CLEANUP_SCOPES.get(artifact_kind)
    if closure.get("cleanup_lifecycle_scope") != expected_scope:
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing lifecycle scope")

    coverage = closure.get("cleanup_coverage")
    if not isinstance(coverage, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing cleanup coverage")
    else:
        missing_coverage = [
            scope
            for scope in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_CLEANUP_COVERAGE_SCOPES
            if scope not in coverage
        ]
        if missing_coverage:
            errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing cleanup coverage")
        expected_coverage_key = "ritual_reset" if artifact_kind == "cleanup_ritual_reset" else str(expected_scope)
        if expected_coverage_key and coverage.get(expected_coverage_key) is not True:
            errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing cleanup coverage")

    ownership_reset = closure.get("ownership_reset_branch_boundary")
    if not isinstance(ownership_reset, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing ownership/reset branch")
    else:
        required_branches = set(_string_refs(ownership_reset.get("required_branches")))
        if {"ownership_loss", "ritual_reset"} - required_branches:
            errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing ownership/reset branch")
        if ownership_reset.get("ownership_loss_planned") is not True or ownership_reset.get("ritual_reset_planned") is not True:
            errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing ownership/reset branch")
        if ownership_reset.get("unsafe_pre_eval_writes_allowed") is not False:
            errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing ownership/reset branch")

    lifecycle = closure.get("row_entity_lifecycle_coverage")
    if not isinstance(lifecycle, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing row/entity lifecycle coverage")
    elif (
        not _string_refs(lifecycle.get("entity_keys"))
        or set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_CLEANUP_COVERAGE_SCOPES)
        - set(_string_refs(lifecycle.get("lifecycle_scopes")))
        or lifecycle.get("row_state_write_schema_allowed") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing row/entity lifecycle coverage")

    aggregate_boundary = closure.get("aggregate_projection_boundary")
    if not isinstance(aggregate_boundary, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing aggregate projection boundary")
    elif (
        not isinstance(aggregate_boundary.get("aggregate_projection_refs"), list)
        or not str(aggregate_boundary.get("aggregate_projection_boundary", "")).strip()
        or aggregate_boundary.get("projection_only") is not True
        or aggregate_boundary.get("body_emitted") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} cleanup closure missing aggregate projection boundary")

    return errors


def _validate_repeated_row_trigger_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    errors = _validate_repeated_row_no_write_source_writer_closure_contract(
        pilot_key=pilot_key,
        artifact_kind=artifact_kind,
        contract_family="trigger",
        closure=closure,
    )
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    expected_pattern = "src/in_game/common/scripted_triggers/tv_wonder_unique_<wonder_key>_ritual_triggers.txt"
    expected_target = expected_pattern.replace("<wonder_key>", wonder_key)
    if closure.get("source_type") != "common/scripted_triggers":
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure source_type changed")
    if closure.get("future_source_target_path_pattern") != expected_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing future target path pattern")
    if closure.get("future_source_target_path") != expected_target:
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing future target path")
    if closure.get("trigger_body_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure trigger_body_writes_allowed must be false")
    if closure.get("tooltip_safe_unsafe_write_paths_allowed") is not False:
        errors.append(
            f"{pilot_key}: artifact {artifact_kind} trigger closure tooltip_safe_unsafe_write_paths_allowed must be false"
        )

    condition_coverage = closure.get("condition_group_coverage")
    expected_group_by_artifact = {
        "scripted_trigger_eligibility": "eligibility",
        "scripted_trigger_row_completion": "row_completion",
        "scripted_trigger_tooltip_safe_condition_group": "tooltip_safe",
    }
    if not isinstance(condition_coverage, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing condition group coverage")
    else:
        required_groups = {"eligibility", "row_completion", "tooltip_safe"}
        if required_groups - set(_string_refs(condition_coverage.get("required_groups"))):
            errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing condition group coverage")
        for group in sorted(required_groups):
            plan = condition_coverage.get(group)
            if not isinstance(plan, dict) or not plan:
                errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing {group} plan")
                continue
            if plan.get("predicate_group_only") is not True:
                errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure {group} plan must be predicate-only")
        expected_group = expected_group_by_artifact.get(artifact_kind, "")
        expected_plan = condition_coverage.get(expected_group) if expected_group else None
        if not isinstance(expected_plan, dict) or expected_plan.get("planned") is not True:
            errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing condition group coverage")

    forbidden_write_paths = closure.get("forbidden_write_paths")
    if not isinstance(forbidden_write_paths, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing forbidden write paths")
    else:
        contexts = set(_string_refs(forbidden_write_paths.get("forbidden_contexts")))
        if {"tooltip", "pre_evaluation"} - contexts:
            errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing forbidden write paths")
        for key in (
            "tooltip_context_write_paths_allowed",
            "pre_evaluation_write_paths_allowed",
            "unsafe_effect_calls_allowed",
            "row_state_writes_allowed",
            "source_writes_allowed",
            "tooltip_safe_unsafe_write_paths_allowed",
        ):
            if forbidden_write_paths.get(key) is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing forbidden write paths")
                break

    aggregate_boundary = closure.get("aggregate_projection_boundary")
    if not isinstance(aggregate_boundary, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing aggregate projection boundary")
    elif (
        not isinstance(aggregate_boundary.get("aggregate_projection_refs"), list)
        or not str(aggregate_boundary.get("aggregate_projection_boundary", "")).strip()
        or aggregate_boundary.get("projection_only") is not True
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} trigger closure missing aggregate projection boundary")

    return errors


def _validate_repeated_row_gui_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    errors = _validate_repeated_row_no_write_source_writer_closure_contract(
        pilot_key=pilot_key,
        artifact_kind=artifact_kind,
        contract_family="gui",
        closure=closure,
    )
    wonder_key = _repeated_row_event_contract_wonder_key(pilot_key)
    expected_pattern = "src/in_game/gui/panels/organization/tv_wonder_unique_<wonder_key>_ritual.gui"
    expected_target = expected_pattern.replace("<wonder_key>", wonder_key)
    if artifact_kind not in REPEATED_ENTITY_ROW_GUI_ARTIFACT_KINDS:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure artifact kind changed")
    if closure.get("source_type") != "in_game/gui/panels/organization":
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure source_type changed")
    if closure.get("future_source_target_path_pattern") != expected_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing future target path pattern")
    if closure.get("future_source_target_path") != expected_target:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing future target path")
    if closure.get("aggregate_only_display_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure aggregate-only UI must be false")
    if closure.get("gui_source_body_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure GUI source body emission must be false")
    if closure.get("gui_source_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure GUI source writes must be false")
    if closure.get("row_state_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure row-state writes must be false")
    if closure.get("source_ready_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure source-ready must be false")

    source_body_preview = closure.get("source_body_preview")
    if not isinstance(source_body_preview, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing source body preview")
    elif (
        source_body_preview.get("no_gui_source_body") is not True
        or source_body_preview.get("no_gui_source_write") is not True
        or source_body_preview.get("no_row_state_write") is not True
        or source_body_preview.get("no_source_ready") is not True
        or source_body_preview.get("body_emitted") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure must not emit GUI source body")

    fixed_plan = closure.get("fixed_row_widget_plan")
    if not isinstance(fixed_plan, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing fixed row widget plan")
    elif (
        fixed_plan.get("row_widget_fixed") is not True
        or fixed_plan.get("body_emitted") is not False
        or not str(fixed_plan.get("row_widget_boundary", "")).strip()
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing fixed row widget plan")

    binding_plan = closure.get("per_row_variable_binding_plan")
    if not isinstance(binding_plan, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing per-row binding plan")
    elif (
        binding_plan.get("binds_design_ir_tracked_entity_sets") is not True
        or binding_plan.get("aggregate_only_row_reads_allowed") is not False
        or not _string_refs(binding_plan.get("entity_keys"))
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing per-row binding plan")

    row_policy = closure.get("actor_checklist_incident_row_policy")
    expected_policy_flag = {
        "gui_actor_slots_row": "actor_slots_policy_applies",
        "gui_checklist_row": "checklist_policy_applies",
        "gui_incident_log_row": "incident_log_policy_applies",
    }.get(artifact_kind, "")
    if not isinstance(row_policy, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing row policy")
    elif (
        row_policy.get("distinct_row_policies_required") is not True
        or row_policy.get("aggregate_only_display_allowed") is not False
        or row_policy.get("gui_body_emitted") is not False
        or (expected_policy_flag and row_policy.get(expected_policy_flag) is not True)
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing row policy")

    tooltip_linkage = closure.get("tooltip_localization_linkage")
    if not isinstance(tooltip_linkage, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing tooltip localization linkage")
    else:
        required_linkage_keys = {
            "loc_key_namespace",
            "row_label_keys",
            "status_text_keys",
            "tooltip_keys",
        }
        if not required_linkage_keys <= set(tooltip_linkage):
            errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing tooltip localization linkage")
        if not str(tooltip_linkage.get("loc_key_namespace", "")).startswith("tv_wonder_unique_"):
            errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing tooltip localization linkage")
        for key in ("row_label_keys", "status_text_keys", "tooltip_keys"):
            if not _string_refs(tooltip_linkage.get(key)):
                errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing tooltip localization linkage")
                break

    key_linkage = closure.get("gui_event_localization_key_linkage")
    if not isinstance(key_linkage, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing GUI/event/localization key linkage")
    else:
        gui_event_linkage = key_linkage.get("gui_event_key_linkage")
        tooltip_key_linkage = key_linkage.get("tooltip_localization_linkage")
        if (
            not isinstance(gui_event_linkage, dict)
            or gui_event_linkage.get("linkage_only") is not True
            or gui_event_linkage.get("source_body_emitted") is not False
            or not str(gui_event_linkage.get("event_key_prefix", "")).strip()
            or not isinstance(tooltip_key_linkage, dict)
            or key_linkage.get("localization_linkage_only") is not True
            or key_linkage.get("gui_source_writer_allowed") is not False
            or key_linkage.get("localization_source_writer_allowed") is not False
            or key_linkage.get("event_source_writer_allowed") is not False
            or key_linkage.get("source_body_emitted") is not False
        ):
            errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing GUI/event/localization key linkage")

    aggregate_boundary = closure.get("aggregate_projection_boundary")
    if not isinstance(aggregate_boundary, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing aggregate projection boundary")
    elif (
        not isinstance(aggregate_boundary.get("aggregate_projection_refs"), list)
        or not str(aggregate_boundary.get("aggregate_projection_boundary", "")).strip()
        or aggregate_boundary.get("projection_only") is not True
        or aggregate_boundary.get("aggregate_only_display_allowed") is not False
        or aggregate_boundary.get("body_emitted") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing aggregate projection boundary")

    row_entity_refs = closure.get("row_entity_refs")
    if not isinstance(row_entity_refs, dict) or not _string_refs(row_entity_refs.get("entity_keys")):
        errors.append(f"{pilot_key}: artifact {artifact_kind} GUI closure missing row/entity refs")

    return errors


def _validate_repeated_row_listener_source_writer_closure_contract(
    *,
    pilot_key: str,
    artifact_kind: str,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    errors = _validate_repeated_row_no_write_source_writer_closure_contract(
        pilot_key=pilot_key,
        artifact_kind=artifact_kind,
        contract_family="listener",
        closure=closure,
    )
    expected_pattern = "src/in_game/common/on_action/tv_wonder_unique_<wonder_key>_ritual_on_actions.txt"
    expected_target = expected_pattern.replace("<wonder_key>", _repeated_row_event_contract_wonder_key(pilot_key))
    if pilot_key != "unique_alhambra" or artifact_kind != "listener_war_integration":
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure must be Alhambra-only")
    if closure.get("pilot_key") != "unique_alhambra" or closure.get("artifact_kind") != "listener_war_integration":
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure must be Alhambra-only")
    if closure.get("listener_artifact_scope") != "unique_alhambra-only listener_war_integration":
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure must be Alhambra-only")
    if closure.get("source_type") != "common/on_action":
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure source_type changed")
    if closure.get("future_source_target_path_pattern") != expected_pattern:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing future target path pattern")
    if closure.get("future_source_target_path") != expected_target:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing future target path")
    if closure.get("listener_body_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure listener body writes must be false")
    if closure.get("listener_scope_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure listener scope writes must be false")
    if closure.get("war_scope_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure war scope writes must be false")
    if closure.get("row_state_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure row-state writes must be false")
    if closure.get("source_writes_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure source writes must be false")
    if closure.get("source_ready_allowed") is not False:
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure source-ready must be false")

    source_body_preview = closure.get("source_body_preview")
    if not isinstance(source_body_preview, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing source body preview")
    elif (
        source_body_preview.get("no_listener_body") is not True
        or source_body_preview.get("no_listener_scope_write") is not True
        or source_body_preview.get("no_war_scope_write") is not True
        or source_body_preview.get("no_source_ready") is not True
        or source_body_preview.get("body_emitted") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure must not emit listener body")

    target_plan = closure.get("on_action_target_path_plan")
    if not isinstance(target_plan, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing on_action target path plan")
    elif (
        target_plan.get("target_path") != expected_target
        or target_plan.get("target_only") is not True
        or target_plan.get("body_emitted") is not False
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing on_action target path plan")

    hook_plan = closure.get("on_action_hook_linkage_plan")
    if not isinstance(hook_plan, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing hook linkage plan")
    elif (
        hook_plan.get("linkage_only") is not True
        or hook_plan.get("body_emitted") is not False
        or {"on_pre_winning_war", "on_ending_war"} - set(_string_refs(hook_plan.get("hooks")))
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing hook linkage plan")

    trigger_linkage = closure.get("selected_ritual_trigger_linkage")
    if not isinstance(trigger_linkage, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing selected ritual trigger linkage")
    elif (
        trigger_linkage.get("selected_ritual_only") is not True
        or trigger_linkage.get("linkage_only") is not True
        or trigger_linkage.get("trigger_name") != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing selected ritual trigger linkage")

    war_scope_plan = closure.get("war_scope_availability_persistence_plan")
    if not isinstance(war_scope_plan, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing war scope availability plan")
    elif (
        war_scope_plan.get("persistence_contract_only") is not True
        or war_scope_plan.get("listener_scope_writes_allowed") is not False
        or war_scope_plan.get("war_scope_writes_allowed") is not False
        or {"on_pre_winning_war", "on_ending_war"}
        - set(_string_refs(war_scope_plan.get("war_scope_available_from_hooks")))
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing war scope availability plan")

    handoff_boundary = closure.get("row_state_handoff_boundary")
    if not isinstance(handoff_boundary, dict):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing row-state handoff boundary")
    elif (
        handoff_boundary.get("handoff_only") is not True
        or handoff_boundary.get("row_state_writes_allowed") is not False
        or not _string_refs(handoff_boundary.get("entity_keys"))
    ):
        errors.append(f"{pilot_key}: artifact {artifact_kind} listener closure missing row-state handoff boundary")

    return errors


def validate_repeated_entity_row_source_writer_readiness(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if int(report.get("source_plan_artifact_count", -1)) != 177:
        errors.append("source-writer readiness must be based on the 177-artifact source-plan")
    if int(report.get("source_preview_count", -1)) != 177:
        errors.append("source-writer readiness must be based on 177 source previews")
    if int(report.get("artifact_count", -1)) != 177:
        errors.append(f"expected 177 repeated-row source-writer readiness artifacts, got {report.get('artifact_count')}")
    if int(report.get("ready_artifact_count", -1)) != 0:
        errors.append("source-writer readiness ready_artifact_count must be 0")
    if int(report.get("blocked_artifact_count", -1)) != 177:
        errors.append("source-writer readiness blocked_artifact_count must be 177")
    if report.get("source_writer_allowed") is not False:
        errors.append("source-writer readiness report source_writer_allowed must be false")
    if report.get("may_write_src_allowed") is not False:
        errors.append("source-writer readiness report may_write_src_allowed must be false")
    if report.get("writes_src") is not False:
        errors.append("source-writer readiness report writes_src must be false")
    if report.get("source_plan_validation_errors"):
        errors.append("source-writer readiness source-plan validation must be clean")
    if report.get("source_preview_validation_errors"):
        errors.append("source-writer readiness source-preview validation must be clean")

    family_counts = {family: 0 for family in REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS}
    closure_family_counts = {family: 0 for family in REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS}
    closure_no_write_violation_count = 0
    artifact_identities: set[tuple[str, str, str]] = set()
    entries = report.get("entries") if isinstance(report.get("entries"), list) else []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("source-writer readiness entry must be a mapping")
            continue
        pilot_key = str(entry.get("key", "<unknown>"))
        if entry.get("source_writer_allowed") is not False:
            errors.append(f"{pilot_key}: source-writer readiness entry source_writer_allowed must be false")
        if entry.get("may_write_src_allowed") is not False:
            errors.append(f"{pilot_key}: source-writer readiness entry may_write_src_allowed must be false")
        if entry.get("writes_src") is not False:
            errors.append(f"{pilot_key}: source-writer readiness entry writes_src must be false")
        entry_artifacts = entry.get("artifacts") if isinstance(entry.get("artifacts"), list) else []
        if int(entry.get("artifact_count", -1)) != len(entry_artifacts):
            errors.append(f"{pilot_key}: source-writer readiness entry artifact_count mismatch")
        if int(entry.get("ready_artifact_count", -1)) != 0:
            errors.append(f"{pilot_key}: source-writer readiness entry ready_artifact_count must be 0")
        if int(entry.get("blocked_artifact_count", -1)) != len(entry_artifacts):
            errors.append(f"{pilot_key}: source-writer readiness entry blocked_artifact_count mismatch")

        for artifact in entry_artifacts:
            if not isinstance(artifact, dict):
                errors.append(f"{pilot_key}: source-writer readiness artifact must be a mapping")
                continue
            artifact_kind = str(artifact.get("artifact_kind", "<unknown>"))
            missing = _missing_required(artifact, REPEATED_ENTITY_ROW_SOURCE_WRITER_READINESS_REQUIRED_FIELDS)
            if missing:
                errors.append(
                    f"{pilot_key}: artifact {artifact_kind} source-writer readiness missing field(s): "
                    f"{', '.join(missing)}"
                )
                continue
            identity = _repeated_row_artifact_identity(artifact)
            if identity in artifact_identities:
                errors.append(f"{pilot_key}: artifact {artifact_kind} duplicate source-writer readiness artifact")
            artifact_identities.add(identity)
            contract_family = str(artifact.get("contract_family", ""))
            if contract_family in family_counts:
                family_counts[contract_family] += 1
            else:
                errors.append(
                    f"{pilot_key}: artifact {artifact_kind} unsupported source-writer readiness family {contract_family!r}"
                )
            if artifact.get("preview_exists") is not True:
                errors.append(f"{pilot_key}: artifact {artifact_kind} source-writer readiness missing preview")
            if artifact.get("source_writer_allowed") is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} source_writer_allowed must be false")
                if artifact.get("source_writer_allowed") is True:
                    closure_no_write_violation_count += 1
            if artifact.get("may_write_src") is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} may_write_src must be false")
                if artifact.get("may_write_src") is True:
                    closure_no_write_violation_count += 1
            if artifact.get("writes_src") is not False:
                errors.append(f"{pilot_key}: artifact {artifact_kind} writes_src must be false")
                if artifact.get("writes_src") is True:
                    closure_no_write_violation_count += 1
            if _readiness_status_is_forbidden_ready(artifact.get("current_contract_status")):
                errors.append(f"{pilot_key}: artifact {artifact_kind} source-writer readiness must not be source-ready")
            if _readiness_status_is_forbidden_ready(artifact.get("readiness_status")):
                errors.append(f"{pilot_key}: artifact {artifact_kind} source-writer readiness status must stay blocked")
            if str(artifact.get("readiness_status", "")) != "blocked":
                errors.append(f"{pilot_key}: artifact {artifact_kind} source-writer readiness status must be blocked")
            unresolved = _string_refs(artifact.get("unresolved_writer_blockers"))
            if not unresolved:
                errors.append(f"{pilot_key}: artifact {artifact_kind} source-writer readiness missing blockers")

            closure_for_target = (
                artifact.get("closure_contract") if isinstance(artifact.get("closure_contract"), dict) else {}
            )
            expected_target_paths = _repeated_row_no_write_source_writer_target_paths(
                contract_family=contract_family,
                pilot_key=pilot_key,
                candidate_path=str(closure_for_target.get("future_source_target_path", "")),
                path_pattern=str(closure_for_target.get("future_source_target_path_pattern", "")),
            )
            errors.extend(
                _validate_repeated_row_no_write_source_writer_contract_evidence(
                    pilot_key=pilot_key,
                    artifact_kind=artifact_kind,
                    contract_family=contract_family,
                    evidence=artifact.get("no_write_source_writer_contract_evidence"),
                    expected_target_paths=expected_target_paths,
                    expected_blockers=unresolved,
                )
            )

            closure = artifact.get("closure_contract")
            if not isinstance(closure, dict):
                errors.append(f"{pilot_key}: artifact {artifact_kind} {contract_family} closure missing closure_contract")
            else:
                closure_family = str(closure.get("contract_family", ""))
                if closure_family in closure_family_counts:
                    closure_family_counts[closure_family] += 1
                if closure.get("source_writer_allowed") is True:
                    closure_no_write_violation_count += 1
                if closure.get("may_write_src") is True:
                    closure_no_write_violation_count += 1
                if closure.get("writes_src") is True:
                    closure_no_write_violation_count += 1
                if contract_family == "event":
                    errors.extend(
                        _validate_repeated_row_event_source_writer_closure_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            closure=closure,
                        )
                    )
                elif contract_family == "localization":
                    errors.extend(
                        _validate_repeated_row_localization_source_writer_closure_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            closure=closure,
                        )
                    )
                elif contract_family == "effect":
                    errors.extend(
                        _validate_repeated_row_effect_source_writer_closure_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            closure=closure,
                        )
                    )
                elif contract_family == "cleanup":
                    errors.extend(
                        _validate_repeated_row_cleanup_source_writer_closure_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            closure=closure,
                        )
                    )
                elif contract_family == "trigger":
                    errors.extend(
                        _validate_repeated_row_trigger_source_writer_closure_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            closure=closure,
                        )
                    )
                elif contract_family == "gui":
                    errors.extend(
                        _validate_repeated_row_gui_source_writer_closure_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            closure=closure,
                        )
                    )
                elif contract_family == "listener":
                    errors.extend(
                        _validate_repeated_row_listener_source_writer_closure_contract(
                            pilot_key=pilot_key,
                            artifact_kind=artifact_kind,
                            artifact=artifact,
                            closure=closure,
                        )
                    )

            for evidence_key in REPEATED_ENTITY_ROW_SOURCE_WRITER_READINESS_EVIDENCE_FIELDS:
                evidence = artifact.get(evidence_key)
                if not isinstance(evidence, dict):
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} source-writer readiness missing evidence block "
                        f"{evidence_key}"
                    )
                    continue
                evidence_missing = _missing_required(
                    evidence,
                    REPEATED_ENTITY_ROW_SOURCE_WRITER_READINESS_REQUIRED_EVIDENCE_FIELDS,
                )
                if evidence_missing:
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} {evidence_key} missing field(s): "
                        f"{', '.join(evidence_missing)}"
                    )
                    continue
                if _readiness_evidence_claims_verified(evidence) and (
                    not str(evidence.get("summary", "")).strip()
                    or (not evidence.get("paths") and not evidence.get("anchors"))
                    or not _string_refs(evidence.get("blockers"))
                ):
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} {evidence_key} cannot claim verified/source-ready "
                        "with empty evidence or blockers"
                    )
                if _readiness_evidence_claims_verified(evidence):
                    errors.append(
                        f"{pilot_key}: artifact {artifact_kind} {evidence_key} must not claim verified/source-ready"
                    )

    for family, expected_count in REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS.items():
        if family_counts[family] != expected_count:
            errors.append(
                f"expected {expected_count} repeated-row {family} readiness artifacts, got {family_counts[family]}"
            )
        if closure_family_counts[family] != expected_count:
            errors.append(
                f"expected {expected_count} repeated-row {family} closure artifacts, got {closure_family_counts[family]}"
            )
    if int(report.get("artifact_count", -1)) != len(artifact_identities):
        errors.append("source-writer readiness artifact_count mismatch")
    if report.get("contract_family_summary") != dict(sorted(family_counts.items())):
        errors.append("source-writer readiness contract_family_summary mismatch")
    actual_closure_count = sum(closure_family_counts.values())
    actual_closure_summary = dict(sorted(closure_family_counts.items()))
    actual_missing_families = [
        family
        for family, expected_count in REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS.items()
        if closure_family_counts[family] != expected_count
    ]
    if int(report.get("closure_contract_count", -1)) != actual_closure_count:
        errors.append("source-writer readiness closure_contract_count mismatch")
    if report.get("closure_family_summary") != actual_closure_summary:
        errors.append("source-writer readiness closure_family_summary mismatch")
    if report.get("closure_missing_families") != actual_missing_families:
        errors.append("source-writer readiness closure_missing_families mismatch")
    if int(report.get("closure_no_write_violation_count", -1)) != closure_no_write_violation_count:
        errors.append("source-writer readiness closure_no_write_violation_count mismatch")
    if actual_closure_count != 177:
        errors.append(f"expected 177 repeated-row closure contracts, got {actual_closure_count}")
    if actual_missing_families:
        errors.append(f"source-writer readiness closure missing families: {', '.join(actual_missing_families)}")
    if closure_no_write_violation_count:
        errors.append(
            f"source-writer readiness closure no-write violation count must be 0, got {closure_no_write_violation_count}"
        )
    return errors


def _repeated_row_source_bundle_no_write_boundary() -> dict[str, Any]:
    return {
        "contract_only": True,
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_writer_allowed_count": 0,
        "may_write_src_count": 0,
        "writes_src_count": 0,
    }


def _repeated_row_source_bundle_blocker_summary(artifacts: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for artifact in artifacts:
        for blocker in _string_refs(artifact.get("unresolved_writer_blockers")):
            summary[blocker] = summary.get(blocker, 0) + 1
    return dict(sorted(summary.items()))


def _repeated_row_source_bundle_validation_refs(
    *,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> list[str]:
    validations = _string_refs(closure.get("required_validations"))
    evidence = artifact.get("validation_coverage_evidence")
    if isinstance(evidence, dict):
        anchors = evidence.get("anchors")
        if isinstance(anchors, dict):
            validations.extend(_string_refs(anchors.get("required_validations")))
    return sorted(set(validations))


def _repeated_row_source_bundle_closure_ref(
    *,
    artifact: dict[str, Any],
    closure: dict[str, Any],
) -> dict[str, Any]:
    return {
        "pilot_key": str(artifact.get("pilot_key", "")),
        "row_set_key": str(artifact.get("row_set_key", "")),
        "artifact_kind": str(artifact.get("artifact_kind", "")),
        "contract_family": str(closure.get("contract_family", artifact.get("contract_family", ""))),
        "readiness_status": str(closure.get("readiness_status", "")),
        "future_source_target_path": str(closure.get("future_source_target_path", "")),
        "future_source_target_path_pattern": str(closure.get("future_source_target_path_pattern", "")),
    }


def _repeated_row_source_bundle_placeholder(
    *,
    family: str,
    artifact_kind: str,
    closure_ref: dict[str, Any],
) -> dict[str, Any]:
    return {
        "kind": f"{family}_source_body_placeholder",
        "placeholder_family": family,
        "artifact_kind": artifact_kind,
        "future_source_target_path": str(closure_ref.get("future_source_target_path", "")),
        "reason": "Closure contract only; no loadable EU5 source body is emitted by this preview.",
        **REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS,
    }


def _repeated_row_source_bundle_localization_preview(closure: dict[str, Any]) -> dict[str, Any]:
    key_allocation = closure.get("key_allocation") if isinstance(closure.get("key_allocation"), dict) else {}
    return {
        "kind": "localization_key_plan_preview",
        "loc_key_namespace": str(key_allocation.get("loc_key_namespace", "")),
        "required_groups": _string_refs(key_allocation.get("required_groups")),
        "loc_key_plan": list(key_allocation.get("loc_key_plan", []) or []),
        "row_key_groups": dict(key_allocation.get("row_key_groups", {}) or {}),
        "event_key_handoff": dict(closure.get("event_key_handoff", {}) or {}),
        "language_ownership_boundary": dict(closure.get("language_ownership_boundary", {}) or {}),
        **REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS,
    }


def _repeated_row_source_bundle_candidate_context(closure: dict[str, Any]) -> dict[str, Any]:
    return deepcopy(closure)


def _repeated_row_source_bundle_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    closure = artifact.get("closure_contract") if isinstance(artifact.get("closure_contract"), dict) else {}
    family = str(closure.get("contract_family", artifact.get("contract_family", "")))
    artifact_kind = str(artifact.get("artifact_kind", ""))
    blockers = sorted(set(_string_refs(artifact.get("unresolved_writer_blockers"))))
    closure_ref = _repeated_row_source_bundle_closure_ref(artifact=artifact, closure=closure)
    future_target = str(closure_ref.get("future_source_target_path", ""))
    bundled = {
        "artifact_kind": artifact_kind,
        "contract_family": family,
        "pilot_key": str(artifact.get("pilot_key", "")),
        "row_set_key": str(artifact.get("row_set_key", "")),
        "readiness_status": str(artifact.get("readiness_status", "")),
        "current_contract_status": str(artifact.get("current_contract_status", "")),
        "closure_readiness_status": str(closure.get("readiness_status", "")),
        "closure_contract_ref": closure_ref,
        "future_source_target_path": future_target,
        "future_source_target_path_pattern": str(closure_ref.get("future_source_target_path_pattern", "")),
        "future_target_paths": [future_target] if future_target else [],
        "required_validations": _repeated_row_source_bundle_validation_refs(
            artifact=artifact,
            closure=closure,
        ),
        "closure_candidate_context": _repeated_row_source_bundle_candidate_context(closure),
        "unresolved_writer_blockers": blockers,
        "blocker_summary": dict(sorted((blocker, blockers.count(blocker)) for blocker in set(blockers))),
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }
    if family == "event":
        bundled["source_body_preview"] = dict(closure.get("source_body_preview", {}) or {})
    elif family == "localization":
        bundled["source_body_preview"] = _repeated_row_source_bundle_localization_preview(closure)
    else:
        bundled["source_body_placeholder"] = _repeated_row_source_bundle_placeholder(
            family=family,
            artifact_kind=artifact_kind,
            closure_ref=closure_ref,
        )
    return bundled


def _repeated_row_source_bundle_listener_absence(pilot_key: str) -> dict[str, Any]:
    return {
        "explicit": True,
        "pilot_key": pilot_key,
        "artifact_kind": "",
        "reason": "No listener closure_contract exists for this pilot; listener_war_integration is Alhambra-only.",
        "forged_artifact": False,
        **REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS,
    }


def _repeated_row_source_bundle_section(
    *,
    pilot_key: str,
    family: str,
    readiness_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    artifacts = [_repeated_row_source_bundle_artifact(artifact) for artifact in readiness_artifacts]
    closure_refs = [artifact["closure_contract_ref"] for artifact in artifacts]
    future_target_paths = sorted(
        {
            str(path)
            for artifact in artifacts
            for path in artifact.get("future_target_paths", []) or []
            if str(path).strip()
        }
    )
    required_validations = sorted(
        {
            validation
            for artifact in artifacts
            for validation in _string_refs(artifact.get("required_validations"))
        }
    )
    unresolved_writer_blockers = sorted(
        {
            blocker
            for artifact in artifacts
            for blocker in _string_refs(artifact.get("unresolved_writer_blockers"))
        }
    )
    section = {
        "family": family,
        "artifact_count": len(artifacts),
        "closure_contract_count": len(closure_refs),
        "closure_contract_refs": closure_refs,
        "future_target_paths": future_target_paths,
        "source_body_previews": [
            artifact["source_body_preview"]
            for artifact in artifacts
            if isinstance(artifact.get("source_body_preview"), dict)
        ],
        "source_body_placeholders": [
            artifact["source_body_placeholder"]
            for artifact in artifacts
            if isinstance(artifact.get("source_body_placeholder"), dict)
        ],
        "required_validations": required_validations,
        "unresolved_writer_blockers": unresolved_writer_blockers,
        "blocker_summary": _repeated_row_source_bundle_blocker_summary(artifacts),
        "source_ready_count": sum(1 for artifact in artifacts if artifact.get("source_ready") is True),
        "source_writer_allowed_count": sum(
            1 for artifact in artifacts if artifact.get("source_writer_allowed") is True
        ),
        "may_write_src_count": sum(1 for artifact in artifacts if artifact.get("may_write_src") is True),
        "writes_src_count": sum(1 for artifact in artifacts if artifact.get("writes_src") is True),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_ready": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "artifacts": artifacts,
    }
    if family == "listener" and pilot_key != "unique_alhambra" and not artifacts:
        section["listener_artifact_absence"] = _repeated_row_source_bundle_listener_absence(pilot_key)
    return section


def _repeated_row_source_bundle_entry(entry: dict[str, Any]) -> dict[str, Any]:
    pilot_key = str(entry.get("key", ""))
    artifacts = [
        artifact
        for artifact in entry.get("artifacts", []) or []
        if isinstance(artifact, dict)
    ]
    artifacts_by_family: dict[str, list[dict[str, Any]]] = {
        family: []
        for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES
    }
    for artifact in artifacts:
        family = str(artifact.get("contract_family", ""))
        if family in artifacts_by_family:
            artifacts_by_family[family].append(artifact)

    sections = {
        family: _repeated_row_source_bundle_section(
            pilot_key=pilot_key,
            family=family,
            readiness_artifacts=artifacts_by_family[family],
        )
        for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES
    }
    bundled_artifacts = [
        artifact
        for section in sections.values()
        for artifact in section.get("artifacts", []) or []
        if isinstance(artifact, dict)
    ]
    return {
        "key": pilot_key,
        "bundle_preview_only": True,
        "artifact_count": len(bundled_artifacts),
        "closure_contract_count": sum(
            int(section.get("closure_contract_count", 0))
            for section in sections.values()
            if isinstance(section, dict)
        ),
        "family_summary": {
            family: int(section.get("artifact_count", 0))
            for family, section in sections.items()
        },
        "source_ready_count": sum(1 for artifact in bundled_artifacts if artifact.get("source_ready") is True),
        "source_writer_allowed_count": sum(
            1 for artifact in bundled_artifacts if artifact.get("source_writer_allowed") is True
        ),
        "may_write_src_count": sum(1 for artifact in bundled_artifacts if artifact.get("may_write_src") is True),
        "writes_src_count": sum(1 for artifact in bundled_artifacts if artifact.get("writes_src") is True),
        "blocker_summary": _repeated_row_source_bundle_blocker_summary(bundled_artifacts),
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "writes_src": False,
        "sections": sections,
    }


def repeated_entity_row_source_bundle_preview_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_writer_readiness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    readiness = source_writer_readiness
    if readiness is None:
        readiness = repeated_entity_row_source_writer_readiness_for_payload(payload, statuses=statuses)
    bundles = [
        _repeated_row_source_bundle_entry(entry)
        for entry in readiness.get("entries", []) or []
        if isinstance(entry, dict)
    ]
    artifacts = [
        artifact
        for bundle in bundles
        for section in (bundle.get("sections") or {}).values()
        if isinstance(section, dict)
        for artifact in section.get("artifacts", []) or []
        if isinstance(artifact, dict)
    ]
    report = {
        "statuses": sorted(statuses or {"source_codegen_ready"}),
        "bundle_preview_only": True,
        "bundle_count": len(bundles),
        "artifact_count": len(artifacts),
        "closure_contract_count": sum(
            int(bundle.get("closure_contract_count", 0))
            for bundle in bundles
            if isinstance(bundle, dict)
        ),
        "family_summary": _count_by_key(artifacts, "contract_family"),
        "source_ready_count": sum(1 for artifact in artifacts if artifact.get("source_ready") is True),
        "source_writer_allowed_count": sum(
            1 for artifact in artifacts if artifact.get("source_writer_allowed") is True
        ),
        "may_write_src_count": sum(1 for artifact in artifacts if artifact.get("may_write_src") is True),
        "writes_src_count": sum(1 for artifact in artifacts if artifact.get("writes_src") is True),
        "blocker_count": sum(
            len(_string_refs(artifact.get("unresolved_writer_blockers")))
            for artifact in artifacts
        ),
        "blocker_summary": _repeated_row_source_bundle_blocker_summary(artifacts),
        "source_writer_readiness_artifact_count": int(readiness.get("artifact_count", 0)),
        "source_writer_readiness_closure_contract_count": int(readiness.get("closure_contract_count", 0)),
        "source_writer_readiness_validation_errors": list(readiness.get("validation_errors", [])),
        "source_writer_allowed": False,
        "may_write_src_allowed": False,
        "writes_src": False,
        "bundles": bundles,
        "validation_errors": [],
        "notes": [
            "Repeated-row source bundle preview is a no-write source compiler prototype.",
            "It groups readiness closure_contract evidence for dry-run review only.",
            "It does not emit loadable EU5 source and does not authorize AI-generated src writes.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_source_bundle_preview(report)
    return report


def _source_bundle_forbidden_ready_paths(value: Any, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.strip().lower().replace("-", "_")
            child_path = f"{path}.{key_text}" if path else key_text
            if normalized_key in {"source_ready", "source_ready_allowed", "verified", "backend_ready"} and child is True:
                paths.append(child_path)
            if normalized_key.endswith("status") and _readiness_status_is_forbidden_ready(child):
                paths.append(child_path)
            paths.extend(_source_bundle_forbidden_ready_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_source_bundle_forbidden_ready_paths(child, f"{path}[{index}]"))
    return paths


def _source_bundle_true_flag_paths(value: Any, flag: str, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}" if path else key_text
            if key_text == flag and child is True:
                paths.append(child_path)
            paths.extend(_source_bundle_true_flag_paths(child, flag, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_source_bundle_true_flag_paths(child, flag, f"{path}[{index}]"))
    return paths


def _validate_source_bundle_placeholder(
    *,
    pilot_key: str,
    family: str,
    artifact_kind: str,
    placeholder: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(placeholder, dict):
        return [f"{pilot_key}: artifact {artifact_kind} {family} source body placeholder missing"]
    for flag, expected in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS.items():
        if placeholder.get(flag) is not expected:
            errors.append(f"{pilot_key}: artifact {artifact_kind} {family} source body placeholder missing no-write flag {flag}")
    if str(placeholder.get("placeholder_family", "")) != family:
        errors.append(f"{pilot_key}: artifact {artifact_kind} {family} source body placeholder family mismatch")
    if str(placeholder.get("artifact_kind", "")) != artifact_kind:
        errors.append(f"{pilot_key}: artifact {artifact_kind} {family} source body placeholder artifact mismatch")
    if not str(placeholder.get("future_source_target_path", "")).startswith("src/"):
        errors.append(f"{pilot_key}: artifact {artifact_kind} {family} source body placeholder missing future target path")
    return errors


def _validate_source_bundle_no_write_boundary(
    *,
    context: str,
    value: dict[str, Any],
    errors: list[str],
) -> None:
    if value.get("source_ready") is not False:
        errors.append(f"{context} source_ready must be false")
    if value.get("source_writer_allowed") is not False:
        errors.append(f"{context} source_writer_allowed must be false")
    if value.get("may_write_src") is not False:
        errors.append(f"{context} may_write_src must be false")
    if value.get("writes_src") is not False:
        errors.append(f"{context} writes_src must be false")


def validate_repeated_entity_row_source_bundle_preview(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("bundle_preview_only") is not True:
        errors.append("source bundle preview report must declare bundle_preview_only: true")
    if int(report.get("source_writer_readiness_artifact_count", -1)) != 177:
        errors.append("source bundle preview must be based on the 177-artifact readiness ledger")
    if int(report.get("source_writer_readiness_closure_contract_count", -1)) != 177:
        errors.append("source bundle preview must be based on 177 closure contracts")
    if report.get("source_writer_readiness_validation_errors"):
        errors.append("source bundle preview source-writer readiness validation must be clean")
    if report.get("source_writer_allowed") is not False:
        errors.append("source bundle preview report source_writer_allowed must be false")
    if report.get("may_write_src_allowed") is not False:
        errors.append("source bundle preview report may_write_src_allowed must be false")
    if report.get("writes_src") is not False:
        errors.append("source bundle preview report writes_src must be false")

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(f"source bundle preview must not claim source_ready/verified/backend_ready at {path}")
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"source bundle preview {flag} must be false at {path}")

    bundles = report.get("bundles") if isinstance(report.get("bundles"), list) else []
    bundle_by_key = {
        str(bundle.get("key", "")): bundle
        for bundle in bundles
        if isinstance(bundle, dict)
    }
    expected_pilots = set(REPEATED_ENTITY_ROW_SOURCE_BUNDLE_EXPECTED_PILOTS)
    actual_pilots = set(bundle_by_key)
    missing_pilots = sorted(expected_pilots - actual_pilots)
    extra_pilots = sorted(actual_pilots - expected_pilots)
    if missing_pilots:
        errors.append(f"source bundle preview missing pilot bundle(s): {', '.join(missing_pilots)}")
    if extra_pilots:
        errors.append(f"source bundle preview has unexpected pilot bundle(s): {', '.join(extra_pilots)}")
    if int(report.get("bundle_count", -1)) != len(bundles):
        errors.append("source bundle preview bundle_count mismatch")
    if int(report.get("bundle_count", -1)) != 4:
        errors.append(f"expected 4 repeated-row source bundles, got {report.get('bundle_count')}")

    global_artifacts: list[dict[str, Any]] = []
    global_family_counts = {family: 0 for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES}
    for bundle in bundles:
        if not isinstance(bundle, dict):
            errors.append("source bundle preview bundle must be a mapping")
            continue
        pilot_key = str(bundle.get("key", "<unknown>"))
        if bundle.get("bundle_preview_only") is not True:
            errors.append(f"{pilot_key}: source bundle must declare bundle_preview_only: true")
        if bundle.get("source_writer_allowed") is not False:
            errors.append(f"{pilot_key}: source bundle source_writer_allowed must be false")
        if bundle.get("may_write_src_allowed") is not False:
            errors.append(f"{pilot_key}: source bundle may_write_src_allowed must be false")
        if bundle.get("writes_src") is not False:
            errors.append(f"{pilot_key}: source bundle writes_src must be false")

        sections = bundle.get("sections") if isinstance(bundle.get("sections"), dict) else {}
        missing_sections = [
            family
            for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES
            if family not in sections
        ]
        if missing_sections:
            errors.append(f"{pilot_key}: source bundle missing section(s): {', '.join(missing_sections)}")

        bundle_artifacts: list[dict[str, Any]] = []
        bundle_blocker_summary: dict[str, int] = {}
        bundle_family_counts: dict[str, int] = {}
        bundle_closure_count = 0
        for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES:
            section = sections.get(family)
            if not isinstance(section, dict):
                continue
            if section.get("family") != family:
                errors.append(f"{pilot_key}: source bundle section {family} family mismatch")
            _validate_source_bundle_no_write_boundary(
                context=f"{pilot_key}: section {family}",
                value=section,
                errors=errors,
            )
            section_artifacts = section.get("artifacts") if isinstance(section.get("artifacts"), list) else []
            section_artifacts = [
                artifact
                for artifact in section_artifacts
                if isinstance(artifact, dict)
            ]
            if family == "listener" and pilot_key != "unique_alhambra":
                if section_artifacts:
                    errors.append(f"{pilot_key}: non-Alhambra pilot must not include listener artifact")
                absence = section.get("listener_artifact_absence")
                if not isinstance(absence, dict):
                    errors.append(f"{pilot_key}: listener section missing explicit listener artifact absence")
                else:
                    if absence.get("explicit") is not True or absence.get("forged_artifact") is not False:
                        errors.append(f"{pilot_key}: listener section must explicitly record no forged listener artifact")
                    for flag, expected in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS.items():
                        if absence.get(flag) is not expected:
                            errors.append(f"{pilot_key}: listener absence missing no-write flag {flag}")
            if family == "listener" and pilot_key == "unique_alhambra":
                if len(section_artifacts) != 1 or section_artifacts[0].get("artifact_kind") != "listener_war_integration":
                    errors.append("unique_alhambra: source bundle missing listener_war_integration artifact")

            closure_refs = [artifact.get("closure_contract_ref") for artifact in section_artifacts]
            expected_refs = [
                ref
                for ref in closure_refs
                if isinstance(ref, dict)
            ]
            expected_target_paths = sorted(
                {
                    str(artifact.get("future_source_target_path", ""))
                    for artifact in section_artifacts
                    if str(artifact.get("future_source_target_path", "")).strip()
                }
            )
            expected_validations = sorted(
                {
                    validation
                    for artifact in section_artifacts
                    for validation in _string_refs(artifact.get("required_validations"))
                }
            )
            expected_blockers = sorted(
                {
                    blocker
                    for artifact in section_artifacts
                    for blocker in _string_refs(artifact.get("unresolved_writer_blockers"))
                }
            )
            expected_blocker_summary = _repeated_row_source_bundle_blocker_summary(section_artifacts)
            if int(section.get("artifact_count", -1)) != len(section_artifacts):
                errors.append(f"{pilot_key}: section {family} artifact_count mismatch")
            if int(section.get("closure_contract_count", -1)) != len(section_artifacts):
                errors.append(f"{pilot_key}: section {family} closure_contract_count mismatch")
            if section.get("closure_contract_refs") != expected_refs:
                errors.append(f"{pilot_key}: section {family} closure_contract_refs mismatch")
            if section.get("future_target_paths") != expected_target_paths:
                errors.append(f"{pilot_key}: section {family} future target paths mismatch")
            if section.get("required_validations") != expected_validations:
                errors.append(f"{pilot_key}: section {family} required validations mismatch")
            if section.get("unresolved_writer_blockers") != expected_blockers:
                errors.append(f"{pilot_key}: section {family} unresolved writer blockers mismatch")
            if section.get("blocker_summary") != expected_blocker_summary:
                errors.append(f"{pilot_key}: section {family} blocker summary mismatch")
            if int(section.get("source_ready_count", -1)) != 0:
                errors.append(f"{pilot_key}: section {family} source_ready_count must be 0")
            if int(section.get("source_writer_allowed_count", -1)) != 0:
                errors.append(f"{pilot_key}: section {family} source_writer_allowed_count must be 0")
            if int(section.get("may_write_src_count", -1)) != 0:
                errors.append(f"{pilot_key}: section {family} may_write_src_count must be 0")
            if int(section.get("writes_src_count", -1)) != 0:
                errors.append(f"{pilot_key}: section {family} writes_src_count must be 0")

            expected_previews = [
                artifact.get("source_body_preview")
                for artifact in section_artifacts
                if isinstance(artifact.get("source_body_preview"), dict)
            ]
            expected_placeholders = [
                artifact.get("source_body_placeholder")
                for artifact in section_artifacts
                if isinstance(artifact.get("source_body_placeholder"), dict)
            ]
            if section.get("source_body_previews") != expected_previews:
                errors.append(f"{pilot_key}: section {family} source body previews mismatch")
            if section.get("source_body_placeholders") != expected_placeholders:
                errors.append(f"{pilot_key}: section {family} source body placeholders mismatch")

            for artifact in section_artifacts:
                artifact_kind = str(artifact.get("artifact_kind", "<unknown>"))
                _validate_source_bundle_no_write_boundary(
                    context=f"{pilot_key}: artifact {artifact_kind}",
                    value=artifact,
                    errors=errors,
                )
                if artifact.get("pilot_key") != pilot_key:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} pilot_key mismatch")
                if artifact.get("contract_family") != family:
                    errors.append(f"{pilot_key}: artifact {artifact_kind} contract_family mismatch")
                if _readiness_status_is_forbidden_ready(artifact.get("readiness_status")):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} source bundle readiness must stay blocked")
                if str(artifact.get("readiness_status", "")) != "blocked":
                    errors.append(f"{pilot_key}: artifact {artifact_kind} source bundle readiness_status must be blocked")
                if _readiness_status_is_forbidden_ready(artifact.get("current_contract_status")):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} source bundle must not be source-ready")
                if _readiness_status_is_forbidden_ready(artifact.get("closure_readiness_status")):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} closure readiness must stay blocked")
                if not _string_refs(artifact.get("required_validations")):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} source bundle missing required validations")
                if not _string_refs(artifact.get("unresolved_writer_blockers")):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} source bundle missing unresolved writer blockers")
                ref = artifact.get("closure_contract_ref")
                if not isinstance(ref, dict):
                    errors.append(f"{pilot_key}: artifact {artifact_kind} source bundle missing closure_contract_ref")
                else:
                    if ref.get("pilot_key") != pilot_key or ref.get("artifact_kind") != artifact_kind:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} closure_contract_ref mismatch")
                    if ref.get("contract_family") != family:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} closure_contract_ref family mismatch")
                    if ref.get("future_source_target_path") != artifact.get("future_source_target_path"):
                        errors.append(f"{pilot_key}: artifact {artifact_kind} future target path mismatch")
                    if not str(ref.get("future_source_target_path", "")).startswith("src/"):
                        errors.append(f"{pilot_key}: artifact {artifact_kind} closure_contract_ref missing future target path")
                if family == "event":
                    body = artifact.get("source_body_preview")
                    if not isinstance(body, dict) or body.get("kind") != "country_event_preview":
                        errors.append(f"{pilot_key}: artifact {artifact_kind} event source body preview missing")
                    elif body.get("no_row_state_write") is not True or body.get("no_source_ready") is not True:
                        errors.append(f"{pilot_key}: artifact {artifact_kind} event source body preview lost no-write flags")
                elif family == "localization":
                    body = artifact.get("source_body_preview")
                    if not isinstance(body, dict) or body.get("kind") != "localization_key_plan_preview":
                        errors.append(f"{pilot_key}: artifact {artifact_kind} localization source body preview missing")
                    elif not isinstance(body.get("loc_key_plan"), list) or not body.get("loc_key_plan"):
                        errors.append(f"{pilot_key}: artifact {artifact_kind} localization source body preview missing loc key plan")
                    else:
                        for flag, expected in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS.items():
                            if body.get(flag) is not expected:
                                errors.append(
                                    f"{pilot_key}: artifact {artifact_kind} localization source body preview missing no-write flag {flag}"
                                )
                else:
                    errors.extend(
                        _validate_source_bundle_placeholder(
                            pilot_key=pilot_key,
                            family=family,
                            artifact_kind=artifact_kind,
                            placeholder=artifact.get("source_body_placeholder"),
                        )
                    )

            section_blocker_summary = expected_blocker_summary
            for blocker, count in section_blocker_summary.items():
                bundle_blocker_summary[blocker] = bundle_blocker_summary.get(blocker, 0) + count
            bundle_artifacts.extend(section_artifacts)
            bundle_family_counts[family] = len(section_artifacts)
            bundle_closure_count += len(section_artifacts)

        if int(bundle.get("artifact_count", -1)) != len(bundle_artifacts):
            errors.append(f"{pilot_key}: source bundle artifact_count mismatch")
        if int(bundle.get("closure_contract_count", -1)) != bundle_closure_count:
            errors.append(f"{pilot_key}: source bundle closure_contract_count mismatch")
        expected_family_summary = {
            family: bundle_family_counts.get(family, 0)
            for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES
        }
        if bundle.get("family_summary") != expected_family_summary:
            errors.append(f"{pilot_key}: source bundle family_summary mismatch")
        if bundle.get("blocker_summary") != dict(sorted(bundle_blocker_summary.items())):
            errors.append(f"{pilot_key}: source bundle blocker_summary mismatch")
        if int(bundle.get("source_ready_count", -1)) != 0:
            errors.append(f"{pilot_key}: source bundle source_ready_count must be 0")
        if int(bundle.get("source_writer_allowed_count", -1)) != 0:
            errors.append(f"{pilot_key}: source bundle source_writer_allowed_count must be 0")
        if int(bundle.get("may_write_src_count", -1)) != 0:
            errors.append(f"{pilot_key}: source bundle may_write_src_count must be 0")
        if int(bundle.get("writes_src_count", -1)) != 0:
            errors.append(f"{pilot_key}: source bundle writes_src_count must be 0")
        global_artifacts.extend(bundle_artifacts)
        for family, count in expected_family_summary.items():
            global_family_counts[family] += count

    if int(report.get("artifact_count", -1)) != len(global_artifacts):
        errors.append("source bundle preview artifact_count mismatch")
    if int(report.get("artifact_count", -1)) != 177:
        errors.append(f"expected 177 repeated-row source bundle artifacts, got {report.get('artifact_count')}")
    if int(report.get("closure_contract_count", -1)) != len(global_artifacts):
        errors.append("source bundle preview closure_contract_count mismatch")
    if int(report.get("closure_contract_count", -1)) != 177:
        errors.append(f"expected 177 repeated-row source bundle closure contracts, got {report.get('closure_contract_count')}")
    if report.get("family_summary") != dict(sorted(global_family_counts.items())):
        errors.append("source bundle preview family_summary mismatch")
    for family, expected_count in REPEATED_ENTITY_ROW_SOURCE_WRITER_EXPECTED_FAMILY_COUNTS.items():
        if global_family_counts[family] != expected_count:
            errors.append(f"expected {expected_count} repeated-row {family} source bundle artifacts, got {global_family_counts[family]}")
    if int(report.get("source_ready_count", -1)) != 0:
        errors.append("source bundle preview source_ready_count must be 0")
    if int(report.get("source_writer_allowed_count", -1)) != 0:
        errors.append("source bundle preview source_writer_allowed_count must be 0")
    if int(report.get("may_write_src_count", -1)) != 0:
        errors.append("source bundle preview may_write_src_count must be 0")
    if int(report.get("writes_src_count", -1)) != 0:
        errors.append("source bundle preview writes_src_count must be 0")
    expected_blocker_summary = _repeated_row_source_bundle_blocker_summary(global_artifacts)
    if report.get("blocker_summary") != expected_blocker_summary:
        errors.append("source bundle preview blocker_summary mismatch")
    expected_blocker_count = sum(
        len(_string_refs(artifact.get("unresolved_writer_blockers")))
        for artifact in global_artifacts
    )
    if int(report.get("blocker_count", -1)) != expected_blocker_count:
        errors.append("source bundle preview blocker_count mismatch")
    return errors


def _alhambra_source_body_candidate_flags() -> dict[str, bool]:
    return dict(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_FLAGS)


def _alhambra_source_body_candidate_blocker_summary(candidates: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for candidate in candidates:
        for blocker in _string_refs(candidate.get("unresolved_blockers")):
            summary[blocker] = summary.get(blocker, 0) + 1
    return dict(sorted(summary.items()))


def _alhambra_source_body_candidate_draft(
    *,
    family: str,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    context = artifact.get("closure_candidate_context") if isinstance(artifact.get("closure_candidate_context"), dict) else {}
    flags = _alhambra_source_body_candidate_flags()
    future_target = str(artifact.get("future_source_target_path", ""))
    common = {
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "may_write_src": False,
        "writes_src": False,
        "source_writer_allowed": False,
        "future_source_target_path": future_target,
        "future_source_target_path_pattern": str(artifact.get("future_source_target_path_pattern", "")),
        "source_type": str(context.get("source_type", "")),
        "no_write_placeholder_flags": flags,
    }
    if family == "event":
        preview = deepcopy(artifact.get("source_body_preview", {}) or {})
        return {
            "kind": "country_event_structured_body_candidate",
            "source_body_preview": preview,
            "namespace": str(preview.get("namespace", context.get("namespace", ""))),
            "event_id": preview.get("event_id", context.get("preview_event_id")),
            "localization_key_handoff": deepcopy(context.get("localization_key_handoff", {}) or {}),
            "option_effect_handoff": deepcopy(context.get("option_effect_handoff", {}) or {}),
            "safety_notes": deepcopy(context.get("safety_notes", {}) or {}),
            **common,
        }
    if family == "localization":
        preview = deepcopy(artifact.get("source_body_preview", {}) or {})
        return {
            "kind": "localization_structured_body_candidate",
            "source_body_preview": preview,
            "loc_key_namespace": str(preview.get("loc_key_namespace", "")),
            "loc_key_plan": deepcopy(preview.get("loc_key_plan", []) or []),
            "event_key_handoff": deepcopy(preview.get("event_key_handoff", {}) or {}),
            "language_ownership_boundary": deepcopy(preview.get("language_ownership_boundary", {}) or {}),
            **common,
        }

    placeholder = deepcopy(artifact.get("source_body_placeholder", {}) or {})
    if family == "effect":
        draft = {
            "kind": "scripted_effect_structured_body_candidate",
            "source_body_placeholder": placeholder,
            "source_body_preview": deepcopy(context.get("source_body_preview", {}) or {}),
            "future_effect_name_plan": deepcopy(context.get("future_effect_name_plan", {}) or {}),
            "effect_operation_coverage": deepcopy(context.get("effect_operation_coverage", {}) or {}),
            "row_state_schema_boundary": deepcopy(context.get("row_state_schema_boundary", {}) or {}),
            "aggregate_refresh_boundary": deepcopy(context.get("aggregate_refresh_boundary", {}) or {}),
            "cleanup_write_handoff": deepcopy(context.get("cleanup_write_handoff", {}) or {}),
        }
    elif family == "cleanup":
        draft = {
            "kind": "cleanup_structured_body_candidate",
            "source_body_placeholder": placeholder,
            "source_body_preview": deepcopy(context.get("source_body_preview", {}) or {}),
            "cleanup_lifecycle_scope": str(context.get("cleanup_lifecycle_scope", "")),
            "cleanup_scope_plan": deepcopy(context.get("cleanup_scope_plan", {}) or {}),
            "cleanup_coverage": deepcopy(context.get("cleanup_coverage", {}) or {}),
            "ownership_reset_branch_boundary": deepcopy(context.get("ownership_reset_branch_boundary", {}) or {}),
            "row_entity_lifecycle_coverage": deepcopy(context.get("row_entity_lifecycle_coverage", {}) or {}),
            "aggregate_projection_boundary": deepcopy(context.get("aggregate_projection_boundary", {}) or {}),
        }
    elif family == "trigger":
        draft = {
            "kind": "scripted_trigger_structured_body_candidate",
            "source_body_placeholder": placeholder,
            "source_body_preview": deepcopy(context.get("source_body_preview", {}) or {}),
            "future_trigger_name_plan": deepcopy(context.get("future_trigger_name_plan", {}) or {}),
            "condition_group_coverage": deepcopy(context.get("condition_group_coverage", {}) or {}),
            "forbidden_write_paths": deepcopy(context.get("forbidden_write_paths", {}) or {}),
            "aggregate_projection_boundary": deepcopy(context.get("aggregate_projection_boundary", {}) or {}),
        }
    elif family == "gui":
        draft = {
            "kind": "gui_structured_body_candidate",
            "source_body_placeholder": placeholder,
            "source_body_preview": deepcopy(context.get("source_body_preview", {}) or {}),
            "fixed_row_widget_plan": deepcopy(context.get("fixed_row_widget_plan", {}) or {}),
            "per_row_variable_binding_plan": deepcopy(context.get("per_row_variable_binding_plan", {}) or {}),
            "actor_checklist_incident_row_policy": deepcopy(
                context.get("actor_checklist_incident_row_policy", {}) or {}
            ),
            "tooltip_localization_linkage": deepcopy(context.get("tooltip_localization_linkage", {}) or {}),
            "gui_event_localization_key_linkage": deepcopy(
                context.get("gui_event_localization_key_linkage", {}) or {}
            ),
            "aggregate_projection_boundary": deepcopy(context.get("aggregate_projection_boundary", {}) or {}),
            "row_entity_refs": deepcopy(context.get("row_entity_refs", {}) or {}),
        }
    elif family == "listener":
        draft = {
            "kind": "listener_on_action_structured_body_candidate",
            "source_body_placeholder": placeholder,
            "source_body_preview": deepcopy(context.get("source_body_preview", {}) or {}),
            "on_action_target_path_plan": deepcopy(context.get("on_action_target_path_plan", {}) or {}),
            "on_action_hook_linkage_plan": deepcopy(context.get("on_action_hook_linkage_plan", {}) or {}),
            "selected_ritual_trigger_linkage": deepcopy(context.get("selected_ritual_trigger_linkage", {}) or {}),
            "war_scope_availability_persistence_plan": deepcopy(
                context.get("war_scope_availability_persistence_plan", {}) or {}
            ),
            "row_state_handoff_boundary": deepcopy(context.get("row_state_handoff_boundary", {}) or {}),
            "listener_artifact_scope": str(context.get("listener_artifact_scope", "")),
        }
    else:
        draft = {
            "kind": f"{family}_structured_body_candidate",
            "source_body_placeholder": placeholder,
        }
    return {
        **draft,
        **common,
    }


def _alhambra_source_body_candidate_for_artifact(
    *,
    family: str,
    artifact: dict[str, Any],
) -> dict[str, Any]:
    flags = _alhambra_source_body_candidate_flags()
    closure_ref = deepcopy(artifact.get("closure_contract_ref", {}) or {})
    candidate = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": family,
        "artifact_kind": str(artifact.get("artifact_kind", "")),
        "row_set_key": str(artifact.get("row_set_key", "")),
        "closure_contract_ref": closure_ref,
        "future_source_target_path": str(artifact.get("future_source_target_path", "")),
        "future_source_target_path_pattern": str(artifact.get("future_source_target_path_pattern", "")),
        "validation_refs": _string_refs(artifact.get("required_validations")),
        "unresolved_blockers": sorted(set(_string_refs(artifact.get("unresolved_writer_blockers")))),
        "blocker_summary": dict(artifact.get("blocker_summary", {}) or {}),
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": flags,
        "structured_body_candidate": _alhambra_source_body_candidate_draft(
            family=family,
            artifact=artifact,
        ),
        **flags,
    }
    if family == "event" and isinstance(artifact.get("source_body_preview"), dict):
        candidate["source_body_preview"] = deepcopy(artifact.get("source_body_preview", {}) or {})
    if family == "localization" and isinstance(artifact.get("source_body_preview"), dict):
        candidate["source_body_preview"] = deepcopy(artifact.get("source_body_preview", {}) or {})
    return candidate


def _alhambra_source_body_candidate_section(
    *,
    family: str,
    source_bundle_section: dict[str, Any],
) -> dict[str, Any]:
    artifacts = [
        artifact
        for artifact in source_bundle_section.get("artifacts", []) or []
        if isinstance(artifact, dict)
    ]
    candidates = [
        _alhambra_source_body_candidate_for_artifact(family=family, artifact=artifact)
        for artifact in artifacts
    ]
    closure_refs = [candidate["closure_contract_ref"] for candidate in candidates]
    future_target_paths = sorted(
        {
            str(candidate.get("future_source_target_path", ""))
            for candidate in candidates
            if str(candidate.get("future_source_target_path", "")).strip()
        }
    )
    validation_refs = sorted(
        {
            validation
            for candidate in candidates
            for validation in _string_refs(candidate.get("validation_refs"))
        }
    )
    unresolved_blockers = sorted(
        {
            blocker
            for candidate in candidates
            for blocker in _string_refs(candidate.get("unresolved_blockers"))
        }
    )
    return {
        "family": family,
        "source_body_candidate_only": True,
        "bundle_preview_input_only": True,
        "artifact_count": len(candidates),
        "closure_contract_count": len(closure_refs),
        "closure_contract_refs": closure_refs,
        "future_target_paths": future_target_paths,
        "validation_refs": validation_refs,
        "required_validations": validation_refs,
        "unresolved_blockers": unresolved_blockers,
        "unresolved_writer_blockers": unresolved_blockers,
        "blocker_summary": _alhambra_source_body_candidate_blocker_summary(candidates),
        "structured_body_candidates": candidates,
        "source_ready_count": sum(1 for candidate in candidates if candidate.get("source_ready") is True),
        "source_writer_allowed_count": sum(
            1 for candidate in candidates if candidate.get("source_writer_allowed") is True
        ),
        "may_write_src_count": sum(1 for candidate in candidates if candidate.get("may_write_src") is True),
        "writes_src_count": sum(1 for candidate in candidates if candidate.get("writes_src") is True),
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
    }


def _alhambra_source_body_candidate_from_bundle_preview(source_bundle_preview: dict[str, Any]) -> dict[str, Any]:
    bundle = next(
        (
            entry
            for entry in source_bundle_preview.get("bundles", []) or []
            if isinstance(entry, dict)
            and entry.get("key") == REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT
        ),
        {},
    )
    bundle_sections = bundle.get("sections") if isinstance(bundle.get("sections"), dict) else {}
    sections = {
        family: _alhambra_source_body_candidate_section(
            family=family,
            source_bundle_section=bundle_sections.get(family, {}) if isinstance(bundle_sections, dict) else {},
        )
        for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES
    }
    candidates = [
        candidate
        for section in sections.values()
        for candidate in section.get("structured_body_candidates", []) or []
        if isinstance(candidate, dict)
    ]
    family_summary = {
        family: int(section.get("artifact_count", 0))
        for family, section in sections.items()
    }
    source_ready_count = sum(1 for candidate in candidates if candidate.get("source_ready") is True)
    source_writer_allowed_count = sum(1 for candidate in candidates if candidate.get("source_writer_allowed") is True)
    may_write_src_count = sum(1 for candidate in candidates if candidate.get("may_write_src") is True)
    writes_src_count = sum(1 for candidate in candidates if candidate.get("writes_src") is True)
    blocker_summary = _alhambra_source_body_candidate_blocker_summary(candidates)
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family_count": len(sections),
        "artifact_count": len(candidates),
        "closure_contract_count": sum(int(section.get("closure_contract_count", 0)) for section in sections.values()),
        "family_summary": family_summary,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "blocker_summary": blocker_summary,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "source_body_candidate_only": True,
        "bundle_preview_input_only": True,
        "source_bundle_preview_ref": {
            "bundle_count": int(source_bundle_preview.get("bundle_count", 0)),
            "artifact_count": int(source_bundle_preview.get("artifact_count", 0)),
            "closure_contract_count": int(source_bundle_preview.get("closure_contract_count", 0)),
        },
        "source_bundle_preview_validation_errors": list(source_bundle_preview.get("validation_errors", []) or []),
        "summary": summary,
        "family_count": len(sections),
        "artifact_count": len(candidates),
        "closure_contract_count": summary["closure_contract_count"],
        "family_summary": family_summary,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "blocker_summary": blocker_summary,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "sections": sections,
        "validation_errors": [],
        "notes": [
            "Alhambra source body candidate is a no-write vertical slice over the source bundle preview.",
            "It is not source-ready, not loadable EU5 source, and not permission to write src/.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_alhambra_source_body_candidate(report)
    return report


def repeated_entity_row_alhambra_source_body_candidate_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_bundle_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_bundle_preview is None:
        source_bundle_preview = repeated_entity_row_source_bundle_preview_for_payload(payload, statuses=statuses)
    return _alhambra_source_body_candidate_from_bundle_preview(source_bundle_preview)


def _validate_alhambra_source_body_candidate_flags(
    *,
    context: str,
    value: dict[str, Any],
    errors: list[str],
) -> None:
    for flag, expected in REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_FLAGS.items():
        if value.get(flag) is not expected:
            errors.append(f"{context} missing no-write candidate flag {flag}")
    placeholder_flags = value.get("no_write_placeholder_flags")
    if not isinstance(placeholder_flags, dict):
        errors.append(f"{context} missing no-write placeholder flags")
        return
    for flag, expected in REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_FLAGS.items():
        if placeholder_flags.get(flag) is not expected:
            errors.append(f"{context} no-write placeholder flag {flag} mismatch")


def _validate_alhambra_source_body_placeholder_flags(
    *,
    context: str,
    value: Any,
    errors: list[str],
) -> None:
    if not isinstance(value, dict):
        errors.append(f"{context} missing source body placeholder")
        return
    for flag, expected in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_PLACEHOLDER_FLAGS.items():
        if value.get(flag) is not expected:
            errors.append(f"{context} source body placeholder missing no-write flag {flag}")


def validate_repeated_entity_row_alhambra_source_body_candidate(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra source body candidate pilot_key must be unique_alhambra")
    if report.get("source_body_candidate_only") is not True:
        errors.append("Alhambra source body candidate must declare source_body_candidate_only: true")
    if report.get("bundle_preview_input_only") is not True:
        errors.append("Alhambra source body candidate must declare bundle_preview_input_only: true")
    if report.get("source_bundle_preview_validation_errors"):
        errors.append("Alhambra source body candidate source bundle preview validation must be clean")

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(f"Alhambra source body candidate must not claim source_ready/verified/backend_ready at {path}")
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"Alhambra source body candidate {flag} must be false at {path}")

    if int(report.get("family_count", -1)) != len(REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES):
        errors.append("Alhambra source body candidate family_count must be 7")
    if int(report.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append("Alhambra source body candidate artifact_count must be 45")
    _validate_alhambra_source_body_candidate_flags(context="Alhambra source body candidate report", value=report, errors=errors)

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra source body candidate summary missing")
    else:
        if summary.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source body candidate summary pilot_key must be unique_alhambra")
        if int(summary.get("family_count", -1)) != len(REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES):
            errors.append("Alhambra source body candidate summary family_count must be 7")
        if int(summary.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
            errors.append("Alhambra source body candidate summary artifact_count must be 45")
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(summary.get(count_key, -1)) != 0:
                errors.append(f"Alhambra source body candidate summary {count_key} must be 0")

    sections = report.get("sections") if isinstance(report.get("sections"), dict) else {}
    missing_sections = [
        family
        for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES
        if family not in sections
    ]
    if missing_sections:
        errors.append(f"Alhambra source body candidate missing family section(s): {', '.join(missing_sections)}")

    all_candidates: list[dict[str, Any]] = []
    family_summary: dict[str, int] = {}
    for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES:
        section = sections.get(family)
        if not isinstance(section, dict):
            continue
        if section.get("family") != family:
            errors.append(f"Alhambra source body candidate section {family} family mismatch")
        if section.get("source_body_candidate_only") is not True:
            errors.append(f"Alhambra source body candidate section {family} must be candidate-only")
        if section.get("bundle_preview_input_only") is not True:
            errors.append(f"Alhambra source body candidate section {family} must be bundle-preview input only")
        _validate_alhambra_source_body_candidate_flags(
            context=f"Alhambra source body candidate section {family}",
            value=section,
            errors=errors,
        )

        candidates = section.get("structured_body_candidates") if isinstance(section.get("structured_body_candidates"), list) else []
        candidates = [candidate for candidate in candidates if isinstance(candidate, dict)]
        family_summary[family] = len(candidates)
        if int(section.get("artifact_count", -1)) != len(candidates):
            errors.append(f"Alhambra source body candidate section {family} artifact_count mismatch")
        if int(section.get("closure_contract_count", -1)) != len(candidates):
            errors.append(f"Alhambra source body candidate section {family} closure_contract_count mismatch")

        expected_refs = [candidate.get("closure_contract_ref") for candidate in candidates]
        expected_target_paths = sorted(
            {
                str(candidate.get("future_source_target_path", ""))
                for candidate in candidates
                if str(candidate.get("future_source_target_path", "")).strip()
            }
        )
        expected_validation_refs = sorted(
            {
                validation
                for candidate in candidates
                for validation in _string_refs(candidate.get("validation_refs"))
            }
        )
        expected_blockers = sorted(
            {
                blocker
                for candidate in candidates
                for blocker in _string_refs(candidate.get("unresolved_blockers"))
            }
        )
        expected_blocker_summary = _alhambra_source_body_candidate_blocker_summary(candidates)
        if section.get("closure_contract_refs") != expected_refs:
            errors.append(f"Alhambra source body candidate section {family} closure refs mismatch")
        if section.get("future_target_paths") != expected_target_paths:
            errors.append(f"Alhambra source body candidate section {family} future target paths mismatch")
        if section.get("validation_refs") != expected_validation_refs:
            errors.append(f"Alhambra source body candidate section {family} validation refs mismatch")
        if section.get("unresolved_blockers") != expected_blockers:
            errors.append(f"Alhambra source body candidate section {family} unresolved blockers mismatch")
        if section.get("blocker_summary") != expected_blocker_summary:
            errors.append(f"Alhambra source body candidate section {family} blocker summary mismatch")
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(section.get(count_key, -1)) != 0:
                errors.append(f"Alhambra source body candidate section {family} {count_key} must be 0")

        for candidate in candidates:
            artifact_kind = str(candidate.get("artifact_kind", "<unknown>"))
            context = f"Alhambra source body candidate {family} artifact {artifact_kind}"
            _validate_alhambra_source_body_candidate_flags(context=context, value=candidate, errors=errors)
            if candidate.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                errors.append(f"{context} pilot_key must be unique_alhambra")
            if candidate.get("family") != family:
                errors.append(f"{context} family mismatch")
            if not str(candidate.get("future_source_target_path", "")).startswith("src/"):
                errors.append(f"{context} missing future target path")
            if not _string_refs(candidate.get("validation_refs")):
                errors.append(f"{context} missing validation refs")
            if not _string_refs(candidate.get("unresolved_blockers")):
                errors.append(f"{context} missing unresolved blockers")
            ref = candidate.get("closure_contract_ref")
            if not isinstance(ref, dict):
                errors.append(f"{context} missing closure contract ref")
            else:
                if ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                    errors.append(f"{context} closure ref pilot must be unique_alhambra")
                if ref.get("contract_family") != family:
                    errors.append(f"{context} closure ref family mismatch")
                if ref.get("artifact_kind") != artifact_kind:
                    errors.append(f"{context} closure ref artifact mismatch")
                if ref.get("future_source_target_path") != candidate.get("future_source_target_path"):
                    errors.append(f"{context} closure ref future target path mismatch")

            body = candidate.get("structured_body_candidate")
            if not isinstance(body, dict):
                errors.append(f"{context} missing structured body candidate")
                continue
            _validate_alhambra_source_body_candidate_flags(context=f"{context} body", value=body, errors=errors)
            if body.get("body_emitted") is not False:
                errors.append(f"{context} body_emitted must be false")

            if family == "event":
                preview = body.get("source_body_preview")
                if not isinstance(preview, dict) or preview.get("kind") != "country_event_preview":
                    errors.append(f"{context} must reuse event source_body_preview")
            elif family == "localization":
                preview = body.get("source_body_preview")
                if not isinstance(preview, dict) or preview.get("kind") != "localization_key_plan_preview":
                    errors.append(f"{context} must reuse localization source_body_preview")
                elif not isinstance(preview.get("loc_key_plan"), list) or not preview.get("loc_key_plan"):
                    errors.append(f"{context} localization candidate missing loc key plan")
            elif family in {"effect", "cleanup", "trigger", "gui"}:
                _validate_alhambra_source_body_placeholder_flags(
                    context=f"{context} body",
                    value=body.get("source_body_placeholder"),
                    errors=errors,
                )
            elif family == "listener":
                _validate_alhambra_source_body_placeholder_flags(
                    context=f"{context} body",
                    value=body.get("source_body_placeholder"),
                    errors=errors,
                )
                hook_plan = body.get("on_action_hook_linkage_plan")
                if (
                    not isinstance(hook_plan, dict)
                    or hook_plan.get("linkage_only") is not True
                    or {"on_pre_winning_war", "on_ending_war"} - set(_string_refs(hook_plan.get("hooks")))
                ):
                    errors.append(f"{context} listener missing on_action hook linkage")
                trigger_linkage = body.get("selected_ritual_trigger_linkage")
                if (
                    not isinstance(trigger_linkage, dict)
                    or trigger_linkage.get("selected_ritual_only") is not True
                    or trigger_linkage.get("linkage_only") is not True
                    or trigger_linkage.get("trigger_name")
                    != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
                ):
                    errors.append(f"{context} listener missing selected ritual trigger linkage")
                war_scope_plan = body.get("war_scope_availability_persistence_plan")
                if (
                    not isinstance(war_scope_plan, dict)
                    or war_scope_plan.get("persistence_contract_only") is not True
                    or war_scope_plan.get("listener_scope_writes_allowed") is not False
                    or war_scope_plan.get("war_scope_writes_allowed") is not False
                    or {"on_pre_winning_war", "on_ending_war"}
                    - set(_string_refs(war_scope_plan.get("war_scope_available_from_hooks")))
                ):
                    errors.append(f"{context} listener missing war-scope plan")
        all_candidates.extend(candidates)

    if int(report.get("artifact_count", -1)) != len(all_candidates):
        errors.append("Alhambra source body candidate artifact_count mismatch")
    if len(all_candidates) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append(
            f"Alhambra source body candidate expected 45 artifacts, got {len(all_candidates)}"
        )
    if report.get("family_summary") != family_summary:
        errors.append("Alhambra source body candidate family_summary mismatch")
    expected_blocker_summary = _alhambra_source_body_candidate_blocker_summary(all_candidates)
    if report.get("blocker_summary") != expected_blocker_summary:
        errors.append("Alhambra source body candidate blocker_summary mismatch")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra source body candidate {count_key} must be 0")
    if summary:
        if summary.get("family_summary") != family_summary:
            errors.append("Alhambra source body candidate summary family_summary mismatch")
        if summary.get("blocker_summary") != expected_blocker_summary:
            errors.append("Alhambra source body candidate summary blocker_summary mismatch")
    return errors


def _alhambra_source_file_preview_candidate_ref(candidate: dict[str, Any]) -> dict[str, str]:
    return {
        "pilot_key": str(candidate.get("pilot_key", "")),
        "family": str(candidate.get("family", "")),
        "row_set_key": str(candidate.get("row_set_key", "")),
        "artifact_kind": str(candidate.get("artifact_kind", "")),
        "future_source_target_path": str(candidate.get("future_source_target_path", "")),
    }


def _alhambra_source_file_preview_ref_key(ref: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(ref.get("family", "")),
        str(ref.get("row_set_key", "")),
        str(ref.get("artifact_kind", "")),
        str(ref.get("future_source_target_path", "")),
    )


def _alhambra_source_file_preview_localization_boundary(
    *,
    language: str,
    target_path: str,
) -> dict[str, Any]:
    return {
        "language": language,
        "target_path": target_path,
        "required_languages": list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS),
        "language_target_paths": dict(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
        ),
        "english_target_path": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS["english"],
        "simp_chinese_target_path": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS[
            "simp_chinese"
        ],
        "language_owner": f"src/main_menu/localization/{language}",
        "separate_language_target": True,
        "missing_bilingual_coverage_allowed": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_source_file_preview_target_specs(candidate: dict[str, Any]) -> list[dict[str, str | bool]]:
    if str(candidate.get("family", "")) == "localization":
        return [
            {
                "target_path": target_path,
                "localization_language": language,
                "source_candidate_future_target_path": str(candidate.get("future_source_target_path", "")),
                "expanded_localization_target": True,
            }
            for language, target_path in REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS.items()
        ]
    return [
        {
            "target_path": str(candidate.get("future_source_target_path", "")),
            "localization_language": "",
            "source_candidate_future_target_path": str(candidate.get("future_source_target_path", "")),
            "expanded_localization_target": False,
        }
    ]


def _alhambra_source_file_preview_section(
    *,
    candidate: dict[str, Any],
    target_path: str,
    localization_language: str = "",
) -> dict[str, Any]:
    flags = _alhambra_source_body_candidate_flags()
    ref = _alhambra_source_file_preview_candidate_ref(candidate)
    section = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": str(candidate.get("family", "")),
        "artifact_kind": str(candidate.get("artifact_kind", "")),
        "row_set_key": str(candidate.get("row_set_key", "")),
        "target_path": target_path,
        "source_candidate_future_target_path": str(candidate.get("future_source_target_path", "")),
        "source_body_candidate_ref": ref,
        "closure_contract_ref": deepcopy(candidate.get("closure_contract_ref", {}) or {}),
        "validation_refs": _string_refs(candidate.get("validation_refs")),
        "required_validations": _string_refs(candidate.get("validation_refs")),
        "unresolved_blockers": _string_refs(candidate.get("unresolved_blockers")),
        "unresolved_writer_blockers": _string_refs(candidate.get("unresolved_blockers")),
        "structured_body_candidate": deepcopy(candidate.get("structured_body_candidate", {}) or {}),
        "source_body_candidate": deepcopy(candidate),
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": flags,
        **flags,
    }
    if localization_language:
        section["localization_language"] = localization_language
        section["localization_language_boundary"] = _alhambra_source_file_preview_localization_boundary(
            language=localization_language,
            target_path=target_path,
        )
    return section


def _alhambra_source_file_preview_blocker_summary(sections: list[dict[str, Any]]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for section in sections:
        for blocker in _string_refs(section.get("unresolved_blockers")):
            summary[blocker] = summary.get(blocker, 0) + 1
    return dict(sorted(summary.items()))


def _alhambra_source_file_preview_for_target(
    *,
    target_path: str,
    sections: list[dict[str, Any]],
) -> dict[str, Any]:
    families = sorted({str(section.get("family", "")) for section in sections if str(section.get("family", ""))})
    validation_refs = sorted(
        {
            validation
            for section in sections
            for validation in _string_refs(section.get("validation_refs"))
        }
    )
    unresolved_blockers = sorted(
        {
            blocker
            for section in sections
            for blocker in _string_refs(section.get("unresolved_blockers"))
        }
    )
    preview = {
        "target_path": target_path,
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "source_file_preview_only": True,
        "source_body_candidate_input_only": True,
        "families": families,
        "family_summary": _count_by_key(sections, "family"),
        "artifact_count": len(sections),
        "source_body_candidate_refs": [
            section.get("source_body_candidate_ref", {})
            for section in sections
            if isinstance(section, dict)
        ],
        "structured_body_sections": sections,
        "validation_refs": validation_refs,
        "required_validations": validation_refs,
        "unresolved_blockers": unresolved_blockers,
        "unresolved_writer_blockers": unresolved_blockers,
        "blocker_summary": _alhambra_source_file_preview_blocker_summary(sections),
        "source_ready_count": sum(1 for section in sections if section.get("source_ready") is True),
        "source_writer_allowed_count": sum(1 for section in sections if section.get("source_writer_allowed") is True),
        "may_write_src_count": sum(1 for section in sections if section.get("may_write_src") is True),
        "writes_src_count": sum(1 for section in sections if section.get("writes_src") is True),
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
    }
    localization_targets = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
    language = next((key for key, path in localization_targets.items() if path == target_path), "")
    if language:
        preview["localization_language"] = language
        preview["localization_language_boundary"] = _alhambra_source_file_preview_localization_boundary(
            language=language,
            target_path=target_path,
        )
    return preview


def _alhambra_source_file_preview_from_body_candidate(source_body_candidate: dict[str, Any]) -> dict[str, Any]:
    sections = source_body_candidate.get("sections") if isinstance(source_body_candidate.get("sections"), dict) else {}
    candidates = [
        candidate
        for family in REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES
        for candidate in (
            (sections.get(family, {}) or {}).get("structured_body_candidates", [])
            if isinstance(sections.get(family, {}), dict)
            else []
        )
        if isinstance(candidate, dict)
    ]
    source_candidate_refs: list[dict[str, Any]] = []
    seen_ref_keys: set[tuple[str, str, str, str]] = set()
    sections_by_target: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        ref = _alhambra_source_file_preview_candidate_ref(candidate)
        ref_key = _alhambra_source_file_preview_ref_key(ref)
        if ref_key not in seen_ref_keys:
            source_candidate_refs.append(ref)
            seen_ref_keys.add(ref_key)
        for target_spec in _alhambra_source_file_preview_target_specs(candidate):
            target_path = str(target_spec.get("target_path", ""))
            if not target_path:
                continue
            sections_by_target.setdefault(target_path, []).append(
                _alhambra_source_file_preview_section(
                    candidate=candidate,
                    target_path=target_path,
                    localization_language=str(target_spec.get("localization_language", "")),
                )
            )

    ordered_target_paths = [
        target_path
        for target_path in REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS
        if target_path in sections_by_target
    ]
    ordered_target_paths.extend(
        sorted(
            target_path
            for target_path in sections_by_target
            if target_path not in REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS
        )
    )
    file_previews = [
        _alhambra_source_file_preview_for_target(
            target_path=target_path,
            sections=sections_by_target[target_path],
        )
        for target_path in ordered_target_paths
    ]
    family_summary = dict(source_body_candidate.get("family_summary", {}) or {})
    source_ready_count = sum(1 for candidate in candidates if candidate.get("source_ready") is True)
    source_writer_allowed_count = sum(1 for candidate in candidates if candidate.get("source_writer_allowed") is True)
    may_write_src_count = sum(1 for candidate in candidates if candidate.get("may_write_src") is True)
    writes_src_count = sum(1 for candidate in candidates if candidate.get("writes_src") is True)
    all_file_sections = [
        section
        for preview in file_previews
        for section in preview.get("structured_body_sections", []) or []
        if isinstance(section, dict)
    ]
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "file_preview_count": len(file_previews),
        "artifact_count": len(source_candidate_refs),
        "family_count": len(family_summary),
        "family_summary": family_summary,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "source_file_preview_only": True,
        "source_body_candidate_input_only": True,
        "source_body_candidate_input_ref": {
            "pilot_key": str(source_body_candidate.get("pilot_key", "")),
            "artifact_count": int(source_body_candidate.get("artifact_count", 0)),
            "family_count": int(source_body_candidate.get("family_count", 0)),
            "validation_errors": list(source_body_candidate.get("validation_errors", []) or []),
        },
        "source_body_candidate_validation_errors": list(source_body_candidate.get("validation_errors", []) or []),
        "summary": summary,
        "file_preview_count": len(file_previews),
        "required_target_paths": list(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS),
        "localization_target_paths": dict(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
        ),
        "artifact_count": len(source_candidate_refs),
        "source_body_candidate_ref_count": len(source_candidate_refs),
        "source_body_candidate_refs": source_candidate_refs,
        "file_section_count": len(all_file_sections),
        "family_count": len(family_summary),
        "family_summary": family_summary,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "file_previews": file_previews,
        "validation_errors": [],
        "notes": [
            "Alhambra source file preview groups existing source body candidates by future target path.",
            "It expands localization into separate English and Simplified Chinese future targets.",
            "It is no-write contract evidence only and does not authorize src/ writes.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_alhambra_source_file_preview(report)
    return report


def repeated_entity_row_alhambra_source_file_preview_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_body_candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_body_candidate is None:
        source_body_candidate = repeated_entity_row_alhambra_source_body_candidate_for_payload(
            payload,
            statuses=statuses,
        )
    return _alhambra_source_file_preview_from_body_candidate(source_body_candidate)


def _validate_alhambra_source_file_preview_localization_boundary(
    *,
    context: str,
    boundary: Any,
    language: str,
    target_path: str,
    errors: list[str],
) -> None:
    if not isinstance(boundary, dict):
        errors.append(f"{context} missing localization language boundary")
        return
    expected_targets = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
    if boundary.get("language") != language:
        errors.append(f"{context} localization language boundary language mismatch")
    if boundary.get("target_path") != target_path:
        errors.append(f"{context} localization language boundary target path mismatch")
    if set(_string_refs(boundary.get("required_languages"))) != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
        errors.append(f"{context} localization language boundary missing English/Simplified Chinese split")
    if boundary.get("language_target_paths") != expected_targets:
        errors.append(f"{context} localization language boundary target paths must stay split")
    if boundary.get("english_target_path") != expected_targets["english"]:
        errors.append(f"{context} localization language boundary missing English target")
    if boundary.get("simp_chinese_target_path") != expected_targets["simp_chinese"]:
        errors.append(f"{context} localization language boundary missing Simplified Chinese target")
    if boundary.get("separate_language_target") is not True:
        errors.append(f"{context} localization language boundary must be separated by language")
    if boundary.get("missing_bilingual_coverage_allowed") is not False:
        errors.append(f"{context} localization language boundary must forbid missing bilingual coverage")
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        if boundary.get(flag) is not False:
            errors.append(f"{context} localization language boundary {flag} must be false")


def _validate_alhambra_source_file_preview_listener_section(
    *,
    context: str,
    body: dict[str, Any],
    errors: list[str],
) -> None:
    hook_plan = body.get("on_action_hook_linkage_plan")
    if (
        not isinstance(hook_plan, dict)
        or hook_plan.get("linkage_only") is not True
        or {"on_pre_winning_war", "on_ending_war"} - set(_string_refs(hook_plan.get("hooks")))
    ):
        errors.append(f"{context} listener file preview missing on_action hook linkage")
    trigger_linkage = body.get("selected_ritual_trigger_linkage")
    if (
        not isinstance(trigger_linkage, dict)
        or trigger_linkage.get("selected_ritual_only") is not True
        or trigger_linkage.get("linkage_only") is not True
        or trigger_linkage.get("trigger_name")
        != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
    ):
        errors.append(f"{context} listener file preview missing selected ritual trigger linkage")
    war_scope_plan = body.get("war_scope_availability_persistence_plan")
    if (
        not isinstance(war_scope_plan, dict)
        or war_scope_plan.get("persistence_contract_only") is not True
        or war_scope_plan.get("listener_scope_writes_allowed") is not False
        or war_scope_plan.get("war_scope_writes_allowed") is not False
        or {"on_pre_winning_war", "on_ending_war"}
        - set(_string_refs(war_scope_plan.get("war_scope_available_from_hooks")))
    ):
        errors.append(f"{context} listener file preview missing war-scope persistence plan")


def validate_repeated_entity_row_alhambra_source_file_preview(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra source file preview pilot_key must be unique_alhambra")
    if report.get("source_file_preview_only") is not True:
        errors.append("Alhambra source file preview must declare source_file_preview_only: true")
    if report.get("source_body_candidate_input_only") is not True:
        errors.append("Alhambra source file preview must derive from source body candidate input")
    if report.get("source_body_candidate_validation_errors"):
        errors.append("Alhambra source file preview source body candidate validation must be clean")
    input_ref = report.get("source_body_candidate_input_ref") if isinstance(report.get("source_body_candidate_input_ref"), dict) else {}
    if not input_ref:
        errors.append("Alhambra source file preview missing source body candidate input ref")
    else:
        if input_ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source file preview input ref pilot_key must be unique_alhambra")
        if int(input_ref.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
            errors.append("Alhambra source file preview input ref artifact_count must be 45")
        if int(input_ref.get("family_count", -1)) != len(REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES):
            errors.append("Alhambra source file preview input ref family_count must be 7")
        if input_ref.get("validation_errors"):
            errors.append("Alhambra source file preview input ref validation must be clean")

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(f"Alhambra source file preview must not claim source_ready/verified/backend_ready at {path}")
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"Alhambra source file preview {flag} must be false at {path}")

    _validate_alhambra_source_body_candidate_flags(
        context="Alhambra source file preview report",
        value=report,
        errors=errors,
    )
    if int(report.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append("Alhambra source file preview artifact_count must be 45")
    if int(report.get("family_count", -1)) != len(REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES):
        errors.append("Alhambra source file preview family_count must be 7")

    expected_target_paths = set(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS)
    file_previews = report.get("file_previews") if isinstance(report.get("file_previews"), list) else []
    if int(report.get("file_preview_count", -1)) != len(file_previews):
        errors.append("Alhambra source file preview file_preview_count mismatch")
    if int(report.get("file_preview_count", -1)) != len(expected_target_paths):
        errors.append("Alhambra source file preview file_preview_count must be 7")

    target_counts: dict[str, int] = {}
    for preview in file_previews:
        if isinstance(preview, dict):
            target_path = str(preview.get("target_path", ""))
            target_counts[target_path] = target_counts.get(target_path, 0) + 1
    duplicate_targets = sorted(target for target, count in target_counts.items() if count > 1)
    if duplicate_targets:
        errors.append(f"Alhambra source file preview duplicate target path(s): {', '.join(duplicate_targets)}")
    actual_target_paths = set(target_counts)
    missing_targets = sorted(expected_target_paths - actual_target_paths)
    extra_targets = sorted(actual_target_paths - expected_target_paths)
    if missing_targets:
        errors.append(f"Alhambra source file preview missing required target path(s): {', '.join(missing_targets)}")
    if extra_targets:
        errors.append(f"Alhambra source file preview has unexpected target path(s): {', '.join(extra_targets)}")

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra source file preview summary missing")
    else:
        if summary.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source file preview summary pilot_key must be unique_alhambra")
        if int(summary.get("file_preview_count", -1)) != len(expected_target_paths):
            errors.append("Alhambra source file preview summary file_preview_count must be 7")
        if int(summary.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
            errors.append("Alhambra source file preview summary artifact_count must be 45")
        if int(summary.get("family_count", -1)) != len(REPEATED_ENTITY_ROW_SOURCE_BUNDLE_FAMILIES):
            errors.append("Alhambra source file preview summary family_count must be 7")
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(summary.get(count_key, -1)) != 0:
                errors.append(f"Alhambra source file preview summary {count_key} must be 0")

    localization_targets = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
    localization_languages: set[str] = set()
    all_sections: list[dict[str, Any]] = []
    source_candidate_ref_keys: set[tuple[str, str, str, str]] = set()
    family_summary: dict[str, int] = {}
    for preview in file_previews:
        if not isinstance(preview, dict):
            errors.append("Alhambra source file preview file_previews item must be a mapping")
            continue
        target_path = str(preview.get("target_path", ""))
        context = f"Alhambra source file preview {target_path or '<missing-target>'}"
        _validate_alhambra_source_body_candidate_flags(context=context, value=preview, errors=errors)
        if preview.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append(f"{context} pilot_key must be unique_alhambra")
        if not target_path.startswith("src/"):
            errors.append(f"{context} target_path must be a future src/ path")
        sections = preview.get("structured_body_sections")
        if not isinstance(sections, list):
            errors.append(f"{context} missing structured body sections")
            continue
        sections = [section for section in sections if isinstance(section, dict)]
        all_sections.extend(sections)
        if int(preview.get("artifact_count", -1)) != len(sections):
            errors.append(f"{context} artifact_count mismatch")
        actual_families = sorted(
            {str(section.get("family", "")) for section in sections if str(section.get("family", ""))}
        )
        if preview.get("families") != actual_families:
            errors.append(f"{context} families mismatch")
        expected_validation_refs = sorted(
            {
                validation
                for section in sections
                for validation in _string_refs(section.get("validation_refs"))
            }
        )
        expected_blockers = sorted(
            {
                blocker
                for section in sections
                for blocker in _string_refs(section.get("unresolved_blockers"))
            }
        )
        if preview.get("validation_refs") != expected_validation_refs:
            errors.append(f"{context} validation refs mismatch")
        if preview.get("required_validations") != expected_validation_refs:
            errors.append(f"{context} required validations mismatch")
        if not expected_validation_refs:
            errors.append(f"{context} missing validation refs")
        if preview.get("unresolved_blockers") != expected_blockers:
            errors.append(f"{context} unresolved blockers mismatch")
        if preview.get("unresolved_writer_blockers") != expected_blockers:
            errors.append(f"{context} unresolved writer blockers mismatch")
        if not expected_blockers:
            errors.append(f"{context} missing unresolved blockers")
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(preview.get(count_key, -1)) != 0:
                errors.append(f"{context} {count_key} must be 0")

        if target_path in localization_targets.values():
            language = str(preview.get("localization_language", ""))
            expected_target = localization_targets.get(language)
            localization_languages.add(language)
            if expected_target != target_path:
                errors.append(f"{context} localization target path does not match language")
            if actual_families != ["localization"]:
                errors.append(f"{context} localization file preview must contain only localization sections")
            _validate_alhambra_source_file_preview_localization_boundary(
                context=context,
                boundary=preview.get("localization_language_boundary"),
                language=language,
                target_path=target_path,
                errors=errors,
            )
        elif "localization" in actual_families:
            errors.append(f"{context} localization sections must use separated language target files")

        for section in sections:
            family = str(section.get("family", ""))
            artifact_kind = str(section.get("artifact_kind", "<unknown>"))
            section_context = f"{context} {family} artifact {artifact_kind}"
            _validate_alhambra_source_body_candidate_flags(
                context=section_context,
                value=section,
                errors=errors,
            )
            if section.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                errors.append(f"{section_context} pilot_key must be unique_alhambra")
            if section.get("target_path") != target_path:
                errors.append(f"{section_context} target path mismatch")
            if not _string_refs(section.get("validation_refs")):
                errors.append(f"{section_context} missing validation refs")
            if not _string_refs(section.get("unresolved_blockers")):
                errors.append(f"{section_context} missing unresolved blockers")
            ref = section.get("source_body_candidate_ref")
            if not isinstance(ref, dict):
                errors.append(f"{section_context} missing source body candidate ref")
            else:
                if ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                    errors.append(f"{section_context} ref pilot must be unique_alhambra")
                if ref.get("family") != family:
                    errors.append(f"{section_context} ref family mismatch")
                if ref.get("artifact_kind") != artifact_kind:
                    errors.append(f"{section_context} ref artifact mismatch")
                source_candidate_ref_keys.add(_alhambra_source_file_preview_ref_key(ref))
            source_candidate = section.get("source_body_candidate")
            if not isinstance(source_candidate, dict):
                errors.append(f"{section_context} missing copied source body candidate")
            else:
                if source_candidate.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                    errors.append(f"{section_context} copied source body candidate pilot must be unique_alhambra")
                if source_candidate.get("family") != family:
                    errors.append(f"{section_context} copied source body candidate family mismatch")
            body = section.get("structured_body_candidate")
            if not isinstance(body, dict):
                errors.append(f"{section_context} missing structured body candidate")
                continue
            _validate_alhambra_source_body_candidate_flags(
                context=f"{section_context} body",
                value=body,
                errors=errors,
            )
            if body.get("body_emitted") is not False:
                errors.append(f"{section_context} body_emitted must be false")
            if family == "localization":
                language = str(section.get("localization_language", ""))
                if localization_targets.get(language) != target_path:
                    errors.append(f"{section_context} localization language target mismatch")
                _validate_alhambra_source_file_preview_localization_boundary(
                    context=section_context,
                    boundary=section.get("localization_language_boundary"),
                    language=language,
                    target_path=target_path,
                    errors=errors,
                )
                body_boundary = body.get("language_ownership_boundary")
                if (
                    not isinstance(body_boundary, dict)
                    or set(_string_refs(body_boundary.get("required_languages")))
                    != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS)
                    or not body_boundary.get("english_owner")
                    or not body_boundary.get("simp_chinese_owner")
                ):
                    errors.append(f"{section_context} localization body missing language ownership boundary")
            if family == "listener":
                _validate_alhambra_source_file_preview_listener_section(
                    context=section_context,
                    body=body,
                    errors=errors,
                )

    if localization_languages != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
        errors.append("Alhambra source file preview localization must split English and Simplified Chinese files")
    declared_refs = report.get("source_body_candidate_refs") if isinstance(report.get("source_body_candidate_refs"), list) else []
    for ref in declared_refs:
        if isinstance(ref, dict) and ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source file preview declared source ref pilot_key must be unique_alhambra")
    declared_ref_keys = {
        _alhambra_source_file_preview_ref_key(ref)
        for ref in declared_refs
        if isinstance(ref, dict)
    }
    if declared_ref_keys != source_candidate_ref_keys:
        errors.append("Alhambra source file preview source body candidate refs mismatch")
    if int(report.get("source_body_candidate_ref_count", -1)) != len(source_candidate_ref_keys):
        errors.append("Alhambra source file preview source_body_candidate_ref_count mismatch")
    if len(source_candidate_ref_keys) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append(
            f"Alhambra source file preview expected 45 unique source body artifacts, got {len(source_candidate_ref_keys)}"
        )
    for family, count in _count_by_key(
        [
            {"family": ref_key[0]}
            for ref_key in source_candidate_ref_keys
        ],
        "family",
    ).items():
        family_summary[family] = count
    if report.get("family_summary") != family_summary:
        errors.append("Alhambra source file preview family_summary mismatch")
    if summary and summary.get("family_summary") != family_summary:
        errors.append("Alhambra source file preview summary family_summary mismatch")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra source file preview {count_key} must be 0")
    return errors


def _alhambra_source_file_validation_repo_path_exists(path: str) -> bool:
    normalized = path.replace("\\", "/").strip()
    if not normalized or normalized.startswith("/") or ":" in normalized:
        return False
    relative = Path(normalized)
    if ".." in relative.parts:
        return False
    return (REPO_ROOT / relative).exists()


def _alhambra_source_file_validation_allowed_status(value: Any) -> bool:
    return (
        str(value or "").strip().lower().replace("-", "_")
        in REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_ALLOWED_STATUSES
    )


def _alhambra_source_file_validation_forbidden_status_paths(value: Any, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.strip().lower().replace("-", "_")
            child_path = f"{path}.{key_text}" if path else key_text
            if (
                normalized_key == "status"
                or normalized_key.endswith("_status")
                or normalized_key in {"evidence_status", "readiness_status", "contract_status"}
            ):
                if str(child or "").strip() and not _alhambra_source_file_validation_allowed_status(child):
                    paths.append(child_path)
            paths.extend(_alhambra_source_file_validation_forbidden_status_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_alhambra_source_file_validation_forbidden_status_paths(child, f"{path}[{index}]"))
    return paths


def _alhambra_source_file_validation_pack_ref(preview: dict[str, Any]) -> dict[str, Any]:
    return {
        "pilot_key": str(preview.get("pilot_key", "")),
        "target_path": str(preview.get("target_path", "")),
        "families": list(preview.get("families", []) or []),
        "artifact_count": int(preview.get("artifact_count", 0)),
        "validation_refs": _string_refs(preview.get("validation_refs")),
        "unresolved_blockers": _string_refs(preview.get("unresolved_blockers")),
        "source_file_preview_only": preview.get("source_file_preview_only") is True,
        "source_body_candidate_ref_count": len(
            [
                ref
                for ref in preview.get("source_body_candidate_refs", []) or []
                if isinstance(ref, dict)
            ]
        ),
    }


def _alhambra_source_file_validation_generator_candidate(
    *,
    target_path: str,
    families: list[str],
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "interface_candidate",
        "candidate": str(metadata.get("owner_candidate", "")),
        "families": list(families),
        "target_path": target_path,
        "planned_source_writer_exists": False,
        "candidate_only": True,
        "contract_only": True,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_ready": False,
        "generator_reference_paths": list(metadata.get("syntax_reference_paths", ()) or ()),
    }


def _alhambra_source_file_validation_source_target_boundary(
    *,
    preview: dict[str, Any],
    target_path: str,
    families: list[str],
) -> dict[str, Any]:
    sections = [
        section
        for section in preview.get("structured_body_sections", []) or []
        if isinstance(section, dict)
    ]
    return {
        "status": "blocked",
        "target_path": target_path,
        "families": list(families),
        "future_target_only": True,
        "source_file_preview_only": True,
        "source_file_preview_target_path": str(preview.get("target_path", "")),
        "source_candidate_future_target_paths": sorted(
            {
                str(section.get("source_candidate_future_target_path", ""))
                for section in sections
                if str(section.get("source_candidate_future_target_path", "")).strip()
            }
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_ready": False,
        "body_emitted": False,
        "boundary_summary": "preview-derived target-file evidence only; no source writer is allowed",
    }


def _alhambra_source_file_validation_requirements(preview: dict[str, Any]) -> dict[str, Any]:
    validation_refs = sorted(_string_refs(preview.get("validation_refs")))
    return {
        "status": "interface_candidate",
        "required_validations": validation_refs,
        "source_file_preview_validation_refs": validation_refs,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_ready": False,
        "validation_evidence_only": True,
    }


def _alhambra_source_file_validation_listener_linkage(preview: dict[str, Any]) -> dict[str, Any]:
    listener_section = next(
        (
            section
            for section in preview.get("structured_body_sections", []) or []
            if isinstance(section, dict) and section.get("family") == "listener"
        ),
        {},
    )
    body = listener_section.get("structured_body_candidate") if isinstance(listener_section, dict) else {}
    body = body if isinstance(body, dict) else {}
    return {
        "status": "interface_candidate",
        "on_action_hook_linkage_plan": deepcopy(body.get("on_action_hook_linkage_plan", {}) or {}),
        "selected_ritual_trigger_linkage": deepcopy(body.get("selected_ritual_trigger_linkage", {}) or {}),
        "war_scope_availability_persistence_plan": deepcopy(
            body.get("war_scope_availability_persistence_plan", {}) or {}
        ),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_ready": False,
    }


def _alhambra_source_file_validation_pack(preview: dict[str, Any]) -> dict[str, Any]:
    target_path = str(preview.get("target_path", ""))
    metadata = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA.get(target_path, {})
    families = list(preview.get("families", []) or [])
    validation_refs = sorted(_string_refs(preview.get("validation_refs")))
    unresolved_blockers = sorted(_string_refs(preview.get("unresolved_blockers")))
    pack = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "target_path": target_path,
        "evidence_status": "blocked",
        "source_file_validation_evidence_only": True,
        "source_file_preview_input_only": True,
        "families": families,
        "family_summary": dict(preview.get("family_summary", {}) or {}),
        "artifact_count": int(preview.get("artifact_count", 0)),
        "source_body_candidate_ref_count": len(
            [
                ref
                for ref in preview.get("source_body_candidate_refs", []) or []
                if isinstance(ref, dict)
            ]
        ),
        "source_body_candidate_refs": deepcopy(preview.get("source_body_candidate_refs", []) or []),
        "source_file_preview_ref": _alhambra_source_file_validation_pack_ref(preview),
        "syntax_reference_paths": list(metadata.get("syntax_reference_paths", ()) or ()),
        "generator_ownership_candidate": _alhambra_source_file_validation_generator_candidate(
            target_path=target_path,
            families=families,
            metadata=metadata,
        ),
        "source_target_boundary": _alhambra_source_file_validation_source_target_boundary(
            preview=preview,
            target_path=target_path,
            families=families,
        ),
        "validation_refs": validation_refs,
        "required_validations": validation_refs,
        "validation_requirements": _alhambra_source_file_validation_requirements(preview),
        "unresolved_blockers": unresolved_blockers,
        "unresolved_writer_blockers": unresolved_blockers,
        "blocker_summary": dict(preview.get("blocker_summary", {}) or {}),
        "source_ready_count": int(preview.get("source_ready_count", 0)),
        "source_writer_allowed_count": int(preview.get("source_writer_allowed_count", 0)),
        "may_write_src_count": int(preview.get("may_write_src_count", 0)),
        "writes_src_count": int(preview.get("writes_src_count", 0)),
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
    }
    if "localization_language" in preview:
        pack["localization_language"] = str(preview.get("localization_language", ""))
        pack["localization_language_boundary"] = deepcopy(preview.get("localization_language_boundary", {}) or {})
    if families == ["listener"]:
        pack["listener_linkage_evidence"] = _alhambra_source_file_validation_listener_linkage(preview)
    return pack


def repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_file_preview: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_file_preview is None:
        source_file_preview = repeated_entity_row_alhambra_source_file_preview_for_payload(
            payload,
            statuses=statuses,
        )
    evidence_packs = [
        _alhambra_source_file_validation_pack(preview)
        for preview in source_file_preview.get("file_previews", []) or []
        if isinstance(preview, dict)
    ]
    source_body_candidate_refs = [
        ref
        for pack in evidence_packs
        for ref in pack.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    unique_ref_keys = {
        _alhambra_source_file_preview_ref_key(ref)
        for ref in source_body_candidate_refs
    }
    source_ready_count = sum(1 for pack in evidence_packs if pack.get("source_ready") is True)
    source_writer_allowed_count = sum(1 for pack in evidence_packs if pack.get("source_writer_allowed") is True)
    may_write_src_count = sum(1 for pack in evidence_packs if pack.get("may_write_src") is True)
    writes_src_count = sum(1 for pack in evidence_packs if pack.get("writes_src") is True)
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "evidence_pack_count": len(evidence_packs),
        "artifact_count": len(unique_ref_keys),
        "file_section_count": sum(int(pack.get("artifact_count", 0)) for pack in evidence_packs),
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "source_file_validation_evidence_only": True,
        "source_file_preview_input_only": True,
        "source_file_preview_input_ref": {
            "pilot_key": str(source_file_preview.get("pilot_key", "")),
            "file_preview_count": int(source_file_preview.get("file_preview_count", 0)),
            "artifact_count": int(source_file_preview.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(source_file_preview.get("source_body_candidate_ref_count", 0)),
            "validation_errors": list(source_file_preview.get("validation_errors", []) or []),
        },
        "source_file_preview_validation_errors": list(source_file_preview.get("validation_errors", []) or []),
        "summary": summary,
        "evidence_pack_count": len(evidence_packs),
        "required_target_paths": list(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS),
        "localization_target_paths": dict(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
        ),
        "artifact_count": len(unique_ref_keys),
        "source_body_candidate_ref_count": len(unique_ref_keys),
        "file_section_count": summary["file_section_count"],
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "evidence_packs": evidence_packs,
        "validation_errors": [],
        "notes": [
            "Alhambra source-file validation evidence derives from the no-write source file preview.",
            "It records local syntax references, candidate generator ownership, target boundaries, validation requirements, and blockers.",
            "It permits only interface_candidate or blocked evidence and never authorizes src writes.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_alhambra_source_file_validation_evidence(report)
    return report


def _validate_alhambra_source_file_validation_generator_candidate(
    *,
    context: str,
    candidate: Any,
    target_path: str,
    families: list[str],
    errors: list[str],
) -> None:
    if not isinstance(candidate, dict) or not candidate:
        errors.append(f"{context} missing generator ownership candidate")
        return
    metadata = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA.get(target_path, {})
    expected_candidate = str(metadata.get("owner_candidate", ""))
    if not _alhambra_source_file_validation_allowed_status(candidate.get("status")):
        errors.append(f"{context} generator ownership candidate status must be interface_candidate or blocked")
    if candidate.get("candidate") != expected_candidate:
        errors.append(f"{context} generator ownership candidate mismatch")
    if candidate.get("families") != families:
        errors.append(f"{context} generator ownership candidate families mismatch")
    if candidate.get("planned_source_writer_exists") is not False:
        errors.append(f"{context} generator ownership candidate planned_source_writer_exists must be false")
    if candidate.get("candidate_only") is not True or candidate.get("contract_only") is not True:
        errors.append(f"{context} generator ownership candidate must be candidate-only")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src", "source_ready"):
        if candidate.get(flag) is not False:
            errors.append(f"{context} generator ownership candidate {flag} must be false")
    for path in _string_refs(candidate.get("generator_reference_paths")):
        if not _alhambra_source_file_validation_repo_path_exists(path):
            errors.append(f"{context} generator ownership candidate path does not exist: {path}")


def _validate_alhambra_source_file_validation_source_target_boundary(
    *,
    context: str,
    boundary: Any,
    target_path: str,
    families: list[str],
    errors: list[str],
) -> None:
    if not isinstance(boundary, dict) or not boundary:
        errors.append(f"{context} missing source target boundary")
        return
    if not _alhambra_source_file_validation_allowed_status(boundary.get("status")):
        errors.append(f"{context} source target boundary status must be interface_candidate or blocked")
    if boundary.get("target_path") != target_path:
        errors.append(f"{context} source target boundary target path mismatch")
    if boundary.get("families") != families:
        errors.append(f"{context} source target boundary families mismatch")
    if boundary.get("future_target_only") is not True or boundary.get("source_file_preview_only") is not True:
        errors.append(f"{context} source target boundary must stay preview-only")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src", "source_ready", "body_emitted"):
        if boundary.get(flag) is not False:
            errors.append(f"{context} source target boundary {flag} must be false")


def _validate_alhambra_source_file_validation_requirements(
    *,
    context: str,
    requirements: Any,
    expected_validations: list[str],
    errors: list[str],
) -> None:
    if not isinstance(requirements, dict) or not requirements:
        errors.append(f"{context} missing validation requirements")
        return
    if not _alhambra_source_file_validation_allowed_status(requirements.get("status")):
        errors.append(f"{context} validation requirements status must be interface_candidate or blocked")
    required_validations = sorted(_string_refs(requirements.get("required_validations")))
    if not required_validations:
        errors.append(f"{context} missing validation requirements")
    if required_validations != expected_validations:
        errors.append(f"{context} validation requirements mismatch")
    if sorted(_string_refs(requirements.get("source_file_preview_validation_refs"))) != expected_validations:
        errors.append(f"{context} validation requirements preview refs mismatch")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src", "source_ready"):
        if requirements.get(flag) is not False:
            errors.append(f"{context} validation requirements {flag} must be false")


def _validate_alhambra_source_file_validation_listener_linkage(
    *,
    context: str,
    linkage: Any,
    errors: list[str],
) -> None:
    if not isinstance(linkage, dict) or not linkage:
        errors.append(f"{context} listener target missing hook linkage, trigger linkage, or war-scope boundary")
        return
    hook_plan = linkage.get("on_action_hook_linkage_plan")
    if (
        not isinstance(hook_plan, dict)
        or hook_plan.get("linkage_only") is not True
        or {"on_pre_winning_war", "on_ending_war"} - set(_string_refs(hook_plan.get("hooks")))
    ):
        errors.append(f"{context} listener target missing hook linkage")
    trigger_linkage = linkage.get("selected_ritual_trigger_linkage")
    if (
        not isinstance(trigger_linkage, dict)
        or trigger_linkage.get("selected_ritual_only") is not True
        or trigger_linkage.get("linkage_only") is not True
        or trigger_linkage.get("trigger_name")
        != "tv_wonder_unique_alhambra_ritual_selected_ritual_listener_trigger"
    ):
        errors.append(f"{context} listener target missing selected ritual trigger linkage")
    war_scope_plan = linkage.get("war_scope_availability_persistence_plan")
    if (
        not isinstance(war_scope_plan, dict)
        or war_scope_plan.get("persistence_contract_only") is not True
        or war_scope_plan.get("listener_scope_writes_allowed") is not False
        or war_scope_plan.get("war_scope_writes_allowed") is not False
        or {"on_pre_winning_war", "on_ending_war"}
        - set(_string_refs(war_scope_plan.get("war_scope_available_from_hooks")))
    ):
        errors.append(f"{context} listener target missing war-scope boundary")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src", "source_ready"):
        if linkage.get(flag) is not False:
            errors.append(f"{context} listener linkage {flag} must be false")


def validate_repeated_entity_row_alhambra_source_file_validation_evidence(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra source file validation evidence pilot_key must be unique_alhambra")
    if report.get("source_file_validation_evidence_only") is not True:
        errors.append("Alhambra source file validation evidence must declare source_file_validation_evidence_only: true")
    if report.get("source_file_preview_input_only") is not True:
        errors.append("Alhambra source file validation evidence must derive from source file preview input")
    if report.get("source_file_preview_validation_errors"):
        errors.append("Alhambra source file validation evidence source file preview validation must be clean")
    input_ref = report.get("source_file_preview_input_ref") if isinstance(report.get("source_file_preview_input_ref"), dict) else {}
    if not input_ref:
        errors.append("Alhambra source file validation evidence missing source file preview input ref")
    else:
        if input_ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source file validation evidence input ref pilot_key must be unique_alhambra")
        if int(input_ref.get("file_preview_count", -1)) != len(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS):
            errors.append("Alhambra source file validation evidence input ref file_preview_count must be 7")
        if int(input_ref.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
            errors.append("Alhambra source file validation evidence input ref artifact_count must be 45")
        if input_ref.get("validation_errors"):
            errors.append("Alhambra source file validation evidence input ref validation must be clean")

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(
            f"Alhambra source file validation evidence must not claim source_ready/verified/backend_ready at {path}"
        )
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"Alhambra source file validation evidence {flag} must be false at {path}")
    for path in _alhambra_source_file_validation_forbidden_status_paths(report):
        errors.append(f"Alhambra source file validation evidence status must be interface_candidate or blocked at {path}")

    _validate_alhambra_source_body_candidate_flags(
        context="Alhambra source file validation evidence report",
        value=report,
        errors=errors,
    )
    expected_target_paths = set(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS)
    evidence_packs = report.get("evidence_packs") if isinstance(report.get("evidence_packs"), list) else []
    if int(report.get("evidence_pack_count", -1)) != len(evidence_packs):
        errors.append("Alhambra source file validation evidence evidence_pack_count mismatch")
    if int(report.get("evidence_pack_count", -1)) != len(expected_target_paths):
        errors.append("Alhambra source file validation evidence evidence_pack_count must be 7")
    if int(report.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append("Alhambra source file validation evidence artifact_count must be 45")

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra source file validation evidence summary missing")
    else:
        if summary.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source file validation evidence summary pilot_key must be unique_alhambra")
        if int(summary.get("evidence_pack_count", -1)) != len(expected_target_paths):
            errors.append("Alhambra source file validation evidence summary evidence_pack_count must be 7")
        if int(summary.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
            errors.append("Alhambra source file validation evidence summary artifact_count must be 45")
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(summary.get(count_key, -1)) != 0:
                errors.append(f"Alhambra source file validation evidence summary {count_key} must be 0")

    target_counts: dict[str, int] = {}
    source_ref_keys: set[tuple[str, str, str, str]] = set()
    localization_languages: set[str] = set()
    file_section_count = 0
    for pack in evidence_packs:
        if not isinstance(pack, dict):
            errors.append("Alhambra source file validation evidence pack must be a mapping")
            continue
        missing_fields = _missing_required(pack, REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_REQUIRED_FIELDS)
        target_path = str(pack.get("target_path", ""))
        context = f"Alhambra source file validation evidence {target_path or '<missing-target>'}"
        if missing_fields:
            errors.append(f"{context} missing field(s): {', '.join(missing_fields)}")
        metadata = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA.get(target_path)
        if metadata is None:
            errors.append(f"{context} has unexpected target path")
            continue
        target_counts[target_path] = target_counts.get(target_path, 0) + 1
        expected_families = list(metadata["families"])
        families = list(pack.get("families", []) or [])
        if families != expected_families:
            errors.append(f"{context} families mismatch")
        expected_artifact_count = int(metadata["artifact_count"])
        if int(pack.get("artifact_count", -1)) != expected_artifact_count:
            errors.append(f"{context} artifact_count mismatch")
        file_section_count += int(pack.get("artifact_count", 0))
        if not _alhambra_source_file_validation_allowed_status(pack.get("evidence_status")):
            errors.append(f"{context} evidence_status must be interface_candidate or blocked")
        _validate_alhambra_source_body_candidate_flags(context=context, value=pack, errors=errors)
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(pack.get(count_key, -1)) != 0:
                errors.append(f"{context} {count_key} must be 0")

        preview_ref = pack.get("source_file_preview_ref")
        if not isinstance(preview_ref, dict) or not preview_ref:
            errors.append(f"{context} missing source file preview ref")
        else:
            if preview_ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                errors.append(f"{context} source file preview ref pilot_key must be unique_alhambra")
            if preview_ref.get("target_path") != target_path:
                errors.append(f"{context} source file preview ref target mismatch")
            if preview_ref.get("families") != expected_families:
                errors.append(f"{context} source file preview ref families mismatch")
            if int(preview_ref.get("artifact_count", -1)) != expected_artifact_count:
                errors.append(f"{context} source file preview ref artifact_count mismatch")
            if preview_ref.get("source_file_preview_only") is not True:
                errors.append(f"{context} source file preview ref must stay preview-only")

        syntax_paths = _string_refs(pack.get("syntax_reference_paths"))
        if not syntax_paths:
            errors.append(f"{context} missing syntax_reference_paths")
        for path in syntax_paths:
            if not _alhambra_source_file_validation_repo_path_exists(path):
                errors.append(f"{context} syntax_reference_paths must point to existing repo files: {path}")

        _validate_alhambra_source_file_validation_generator_candidate(
            context=context,
            candidate=pack.get("generator_ownership_candidate"),
            target_path=target_path,
            families=expected_families,
            errors=errors,
        )
        _validate_alhambra_source_file_validation_source_target_boundary(
            context=context,
            boundary=pack.get("source_target_boundary"),
            target_path=target_path,
            families=expected_families,
            errors=errors,
        )
        expected_validations = sorted(_string_refs(pack.get("validation_refs") or pack.get("required_validations")))
        _validate_alhambra_source_file_validation_requirements(
            context=context,
            requirements=pack.get("validation_requirements"),
            expected_validations=expected_validations,
            errors=errors,
        )
        if not expected_validations:
            errors.append(f"{context} missing validation requirements")
        unresolved_blockers = sorted(_string_refs(pack.get("unresolved_blockers")))
        if not unresolved_blockers:
            errors.append(f"{context} unresolved blockers must not be empty while evidence is unverified")
        if sorted(_string_refs(pack.get("unresolved_writer_blockers"))) != unresolved_blockers:
            errors.append(f"{context} unresolved writer blockers mismatch")

        refs = pack.get("source_body_candidate_refs") if isinstance(pack.get("source_body_candidate_refs"), list) else []
        if int(pack.get("source_body_candidate_ref_count", -1)) != len([ref for ref in refs if isinstance(ref, dict)]):
            errors.append(f"{context} source_body_candidate_ref_count mismatch")
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            if ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                errors.append(f"{context} source body candidate ref pilot_key must be unique_alhambra")
            source_ref_keys.add(_alhambra_source_file_preview_ref_key(ref))

        localization_targets = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
        if target_path in localization_targets.values():
            language = str(pack.get("localization_language", ""))
            localization_languages.add(language)
            if localization_targets.get(language) != target_path:
                errors.append(f"{context} localization target path does not match language")
            if families != ["localization"]:
                errors.append(f"{context} localization validation evidence must contain only localization")
            _validate_alhambra_source_file_preview_localization_boundary(
                context=context,
                boundary=pack.get("localization_language_boundary"),
                language=language,
                target_path=target_path,
                errors=errors,
            )
        elif "localization" in families:
            errors.append(f"{context} localization evidence must use separated language target files")

        if families == ["listener"]:
            if int(pack.get("artifact_count", -1)) != 1:
                errors.append(f"{context} listener target artifact_count must be 1")
            _validate_alhambra_source_file_validation_listener_linkage(
                context=context,
                linkage=pack.get("listener_linkage_evidence"),
                errors=errors,
            )

    duplicate_targets = sorted(target for target, count in target_counts.items() if count > 1)
    if duplicate_targets:
        errors.append(f"Alhambra source file validation evidence duplicate target path(s): {', '.join(duplicate_targets)}")
    actual_targets = set(target_counts)
    missing_targets = sorted(expected_target_paths - actual_targets)
    extra_targets = sorted(actual_targets - expected_target_paths)
    if missing_targets:
        errors.append(
            f"Alhambra source file validation evidence missing required target path(s): {', '.join(missing_targets)}"
        )
    if extra_targets:
        errors.append(f"Alhambra source file validation evidence has unexpected target path(s): {', '.join(extra_targets)}")
    if localization_languages != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
        errors.append("Alhambra source file validation evidence localization must split English and Simplified Chinese files")
    if len(source_ref_keys) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append(
            f"Alhambra source file validation evidence expected 45 unique source body artifacts, got {len(source_ref_keys)}"
        )
    if int(report.get("source_body_candidate_ref_count", -1)) != len(source_ref_keys):
        errors.append("Alhambra source file validation evidence source_body_candidate_ref_count mismatch")
    if int(report.get("file_section_count", -1)) != file_section_count:
        errors.append("Alhambra source file validation evidence file_section_count mismatch")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra source file validation evidence {count_key} must be 0")
    if summary and int(summary.get("file_section_count", -1)) != file_section_count:
        errors.append("Alhambra source file validation evidence summary file_section_count mismatch")
    return errors


def _alhambra_source_generator_contract_allowed_status(value: Any) -> bool:
    return (
        str(value or "").strip().lower().replace("-", "_")
        in REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_GENERATOR_CONTRACT_ALLOWED_STATUSES
    )


def _alhambra_source_generator_contract_pack_ref(pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "pilot_key": str(pack.get("pilot_key", "")),
        "target_path": str(pack.get("target_path", "")),
        "families": list(pack.get("families", []) or []),
        "artifact_count": int(pack.get("artifact_count", 0)),
        "evidence_status": str(pack.get("evidence_status", "")),
        "source_file_validation_evidence_only": pack.get("source_file_validation_evidence_only") is True,
        "source_body_candidate_ref_count": int(pack.get("source_body_candidate_ref_count", 0)),
    }


def _alhambra_source_generator_contract_artifact_kinds(pack: dict[str, Any]) -> list[str]:
    return sorted(
        {
            str(ref.get("artifact_kind", ""))
            for ref in pack.get("source_body_candidate_refs", []) or []
            if isinstance(ref, dict) and str(ref.get("artifact_kind", "")).strip()
        }
    )


def _alhambra_source_generator_ref_key_dict(ref_key: tuple[str, str, str, str]) -> dict[str, str]:
    return {
        field: value
        for field, value in zip(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_REF_KEY_FIELDS,
            ref_key,
        )
    }


def _alhambra_source_generator_ref_key_tuples_from_refs(
    refs: list[dict[str, Any]],
) -> list[tuple[str, str, str, str]]:
    return sorted(
        {
            _alhambra_source_file_preview_ref_key(ref)
            for ref in refs
            if isinstance(ref, dict)
        }
    )


def _alhambra_source_generator_ref_summary_from_key_tuples(
    ref_key_tuples: list[tuple[str, str, str, str]],
) -> dict[str, Any]:
    ref_key_dicts = [
        _alhambra_source_generator_ref_key_dict(ref_key)
        for ref_key in ref_key_tuples
    ]
    return {
        "source_body_candidate_ref_count": len(ref_key_tuples),
        "artifact_kinds": sorted(
            {
                str(ref.get("artifact_kind", ""))
                for ref in ref_key_dicts
                if str(ref.get("artifact_kind", "")).strip()
            }
        ),
        "family_artifact_counts": _count_by_key(ref_key_dicts, "family"),
        "row_set_keys": sorted(
            {
                str(ref.get("row_set_key", ""))
                for ref in ref_key_dicts
                if str(ref.get("row_set_key", "")).strip()
            }
        ),
        "future_source_target_paths": sorted(
            {
                str(ref.get("future_source_target_path", ""))
                for ref in ref_key_dicts
                if str(ref.get("future_source_target_path", "")).strip()
            }
        ),
        "canonical_ref_key_tuples": ref_key_tuples,
        "canonical_ref_key_set": ref_key_dicts,
    }


def _alhambra_source_generator_contract_ref_summary(pack: dict[str, Any]) -> dict[str, Any]:
    refs = [
        ref
        for ref in pack.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    return {
        "artifact_kinds": _alhambra_source_generator_contract_artifact_kinds(pack),
        "family_artifact_counts": _count_by_key(refs, "family"),
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


def _alhambra_source_generator_ref_provenance_snapshot(pack: dict[str, Any]) -> dict[str, Any]:
    refs = [
        ref
        for ref in pack.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    ref_key_tuples = _alhambra_source_generator_ref_key_tuples_from_refs(refs)
    ref_summary = _alhambra_source_generator_ref_summary_from_key_tuples(ref_key_tuples)
    target_path = str(pack.get("target_path", ""))
    families = list(pack.get("families", []) or [])
    return {
        "provenance_snapshot_only": True,
        "snapshot_source": (
            "repeated_entity_row_alhambra_source_file_validation_evidence."
            "evidence_packs[].source_body_candidate_refs"
        ),
        "source_file_validation_evidence_only": pack.get("source_file_validation_evidence_only") is True,
        "target_path": target_path,
        "families": families,
        "artifact_count": int(pack.get("artifact_count", 0)),
        "source_body_candidate_ref_count": len(ref_key_tuples),
        "canonical_source_body_candidate_ref_key_fields": list(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_REF_KEY_FIELDS
        ),
        "canonical_source_body_candidate_ref_key_set": ref_summary["canonical_ref_key_set"],
        "artifact_kinds": ref_summary["artifact_kinds"],
        "family_artifact_counts": ref_summary["family_artifact_counts"],
        "row_set_keys": ref_summary["row_set_keys"],
        "future_source_target_paths": ref_summary["future_source_target_paths"],
        "source_file_validation_pack_ref": {
            "pilot_key": str(pack.get("pilot_key", "")),
            "target_path": target_path,
            "artifact_count": int(pack.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(pack.get("source_body_candidate_ref_count", 0)),
        },
        "contract_only": True,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_source_generator_expected_call_signature(owner_generator: str) -> str:
    return (
        f"{owner_generator}.emit_source_file_contract("
        "source_file_validation_pack: Mapping[str, Any], *, dry_run: bool = True"
        ") -> dict[str, Any]"
    )


def _alhambra_source_generator_interface_draft(
    *,
    target_path: str,
    families: list[str],
    owner_generator: str,
) -> dict[str, Any]:
    return {
        "interface_name": f"{owner_generator}.emit_source_file_contract",
        "proposed_function_name": "emit_source_file_contract",
        "owner_generator": owner_generator,
        "call_signature_draft": _alhambra_source_generator_expected_call_signature(owner_generator),
        "input_parameter": "source_file_validation_pack",
        "output_contract": "source_file_contract_artifacts",
        "target_path": target_path,
        "families": list(families),
        "generator_interface_status": "contract_drafted",
        "dry_run_required": True,
        "source_file_level_contract": True,
        "contract_only": True,
        "body_emitted": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_source_generator_input_data_shape(
    *,
    pack: dict[str, Any],
    target_path: str,
    families: list[str],
) -> dict[str, Any]:
    ref_summary = _alhambra_source_generator_contract_ref_summary(pack)
    shape: dict[str, Any] = {
        "input_source": "repeated_entity_row_alhambra_source_file_validation_evidence.evidence_packs[]",
        "input_pack_selector": {
            "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            "target_path": target_path,
        },
        "required_pack_fields": sorted(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_REQUIRED_FIELDS),
        "required_source_body_ref_fields": [
            "pilot_key",
            "family",
            "row_set_key",
            "artifact_kind",
            "future_source_target_path",
        ],
        "target_path": target_path,
        "families": list(families),
        "artifact_count": int(pack.get("artifact_count", 0)),
        "source_body_candidate_ref_count": int(pack.get("source_body_candidate_ref_count", 0)),
        **ref_summary,
        "source_file_validation_evidence_only": pack.get("source_file_validation_evidence_only") is True,
        "contract_only": True,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }
    if "localization_language" in pack:
        shape["localization_language"] = str(pack.get("localization_language", ""))
        shape["required_languages"] = list(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS)
        shape["separate_language_target"] = True
    if families == ["listener"]:
        shape["listener_linkage_required_fields"] = [
            "on_action_hook_linkage_plan",
            "selected_ritual_trigger_linkage",
            "war_scope_availability_persistence_plan",
        ]
    return shape


def _alhambra_source_generator_output_artifact_family(
    *,
    pack: dict[str, Any],
    target_path: str,
    families: list[str],
) -> dict[str, Any]:
    ref_summary = _alhambra_source_generator_contract_ref_summary(pack)
    return {
        "target_path": target_path,
        "families": list(families),
        "artifact_count": int(pack.get("artifact_count", 0)),
        "source_body_candidate_ref_count": int(pack.get("source_body_candidate_ref_count", 0)),
        **ref_summary,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "contract_only": True,
        "body_emitted": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_source_generator_no_write_contract_evidence(
    *,
    target_path: str,
    families: list[str],
    owner_generator: str,
    source_body_candidate_ref_provenance: dict[str, Any],
    pack: dict[str, Any],
    generator_interface_draft: dict[str, Any],
    input_data_shape: dict[str, Any],
    output_artifact_family: dict[str, Any],
    required_validations: list[str],
    remaining_blockers: list[str],
    source_target_boundary: dict[str, Any],
) -> dict[str, Any]:
    normalized_blockers = sorted({blocker for blocker in _string_refs(remaining_blockers) if blocker})
    return {
        "contract_evidence_only": True,
        "target_path": target_path,
        "target_paths": [target_path],
        "families": list(families),
        "owner_generator": owner_generator,
        "owner_generator_candidate": str(
            (pack.get("generator_ownership_candidate") or {}).get("candidate", owner_generator)
        ),
        "source_body_candidate_ref_provenance": deepcopy(source_body_candidate_ref_provenance),
        "generator_interface_draft": deepcopy(generator_interface_draft),
        "input_data_shape": deepcopy(input_data_shape),
        "output_artifact_family": deepcopy(output_artifact_family),
        "validation_refs": list(required_validations),
        "validation_command": REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS[0],
        "verification_commands": list(REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS),
        "source_writer_blocker_reasons": normalized_blockers,
        "source_writer_still_blocked_reason": "; ".join(normalized_blockers),
        "source_target_boundary": deepcopy(source_target_boundary),
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_source_generator_contract_for_pack(pack: dict[str, Any]) -> dict[str, Any]:
    target_path = str(pack.get("target_path", ""))
    metadata = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA.get(target_path, {})
    families = list(pack.get("families", []) or [])
    owner_generator = str(metadata.get("owner_candidate", ""))
    required_validations = sorted(_string_refs(pack.get("required_validations")))
    remaining_blockers = sorted(_string_refs(pack.get("unresolved_blockers")))
    source_target_boundary = deepcopy(pack.get("source_target_boundary", {}) or {})
    source_body_candidate_ref_provenance = _alhambra_source_generator_ref_provenance_snapshot(pack)
    generator_interface_draft = _alhambra_source_generator_interface_draft(
        target_path=target_path,
        families=families,
        owner_generator=owner_generator,
    )
    input_data_shape = _alhambra_source_generator_input_data_shape(
        pack=pack,
        target_path=target_path,
        families=families,
    )
    output_artifact_family = _alhambra_source_generator_output_artifact_family(
        pack=pack,
        target_path=target_path,
        families=families,
    )
    contract = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "target_path": target_path,
        "families": families,
        "artifact_count": int(pack.get("artifact_count", 0)),
        "evidence_pack_ref": _alhambra_source_generator_contract_pack_ref(pack),
        "source_body_candidate_ref_provenance": source_body_candidate_ref_provenance,
        "owner_generator": owner_generator,
        "generator_interface_status": "contract_drafted",
        "planned_source_writer_exists": "interface_contract_exists",
        "generator_interface_draft": generator_interface_draft,
        "input_data_shape": input_data_shape,
        "output_artifact_family": output_artifact_family,
        "verification_commands": list(REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS),
        "source_writer_blocker_reasons": remaining_blockers,
        "source_writer_still_blocked_reason": "; ".join(remaining_blockers),
        "source_target_boundary": source_target_boundary,
        "required_validations": required_validations,
        "remaining_blockers": remaining_blockers,
        "unresolved_writer_blockers": sorted(_string_refs(pack.get("unresolved_writer_blockers"))),
        "source_body_candidate_ref_count": int(pack.get("source_body_candidate_ref_count", 0)),
        "source_body_candidate_refs": deepcopy(pack.get("source_body_candidate_refs", []) or []),
        "no_write_source_writer_contract_evidence": _alhambra_source_generator_no_write_contract_evidence(
            target_path=target_path,
            families=families,
            owner_generator=owner_generator,
            source_body_candidate_ref_provenance=source_body_candidate_ref_provenance,
            pack=pack,
            generator_interface_draft=generator_interface_draft,
            input_data_shape=input_data_shape,
            output_artifact_family=output_artifact_family,
            required_validations=required_validations,
            remaining_blockers=remaining_blockers,
            source_target_boundary=source_target_boundary,
        ),
        "source_ready_count": 0,
        "source_writer_allowed_count": 0,
        "may_write_src_count": 0,
        "writes_src_count": 0,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
    }
    if "localization_language" in pack:
        contract["localization_language"] = str(pack.get("localization_language", ""))
        contract["localization_language_boundary"] = deepcopy(pack.get("localization_language_boundary", {}) or {})
    if families == ["listener"]:
        contract["listener_linkage_contract"] = deepcopy(pack.get("listener_linkage_evidence", {}) or {})
    return contract


def repeated_entity_row_alhambra_source_generator_contract_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_file_validation_evidence is None:
        source_file_validation_evidence = repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
            payload,
            statuses=statuses,
        )
    generator_contracts = [
        _alhambra_source_generator_contract_for_pack(pack)
        for pack in source_file_validation_evidence.get("evidence_packs", []) or []
        if isinstance(pack, dict)
    ]
    source_body_candidate_refs = [
        ref
        for contract in generator_contracts
        for ref in contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    unique_ref_keys = {
        _alhambra_source_file_preview_ref_key(ref)
        for ref in source_body_candidate_refs
    }
    source_ready_count = sum(1 for contract in generator_contracts if contract.get("source_ready") is True)
    source_writer_allowed_count = sum(1 for contract in generator_contracts if contract.get("source_writer_allowed") is True)
    may_write_src_count = sum(1 for contract in generator_contracts if contract.get("may_write_src") is True)
    writes_src_count = sum(1 for contract in generator_contracts if contract.get("writes_src") is True)
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "generator_contract_count": len(generator_contracts),
        "artifact_count": len(unique_ref_keys),
        "generator_interface_status_summary": _count_by_key(generator_contracts, "generator_interface_status"),
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "source_generator_contract_only": True,
        "source_file_validation_evidence_input_only": True,
        "source_file_validation_evidence_input_ref": {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        },
        "source_file_validation_evidence_validation_errors": list(
            source_file_validation_evidence.get("validation_errors", []) or []
        ),
        "summary": summary,
        "generator_contract_count": len(generator_contracts),
        "required_target_paths": list(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS),
        "localization_target_paths": dict(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
        ),
        "artifact_count": len(unique_ref_keys),
        "source_body_candidate_ref_count": len(unique_ref_keys),
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "generator_contracts": generator_contracts,
        "validation_errors": [],
        "notes": [
            "Alhambra source generator contracts derive from source-file validation evidence only.",
            "They draft generator ownership and emitter interfaces without authorizing src writes.",
            "Source-target boundaries remain blocked until a later source writer is verified.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_alhambra_source_generator_contract(
        report,
        source_file_validation_evidence=source_file_validation_evidence,
    )
    return report


def _alhambra_source_generator_contract_report_ref(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "pilot_key": str(report.get("pilot_key", "")),
        "generator_contract_count": int(report.get("generator_contract_count", 0)),
        "artifact_count": int(report.get("artifact_count", 0)),
        "source_body_candidate_ref_count": int(report.get("source_body_candidate_ref_count", 0)),
        "validation_errors": list(report.get("validation_errors", []) or []),
        "source_generator_contract_only": report.get("source_generator_contract_only") is True,
    }


def _alhambra_source_generator_contract_for_target(
    source_generator_contract: dict[str, Any],
    target_path: str,
) -> dict[str, Any]:
    for contract in source_generator_contract.get("generator_contracts", []) or []:
        if isinstance(contract, dict) and contract.get("target_path") == target_path:
            return contract
    return {}


def _alhambra_event_source_file_contract_artifact_key(ref: dict[str, Any], index: int) -> str:
    return "|".join(
        [
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_FAMILY,
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(index),
        ]
    )


def _alhambra_event_source_body_candidate_ref_key(ref: dict[str, Any]) -> dict[str, str]:
    return {
        "family": str(ref.get("family", "")),
        "row_set_key": str(ref.get("row_set_key", "")),
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "future_source_target_path": str(ref.get("future_source_target_path", "")),
    }


def _alhambra_event_source_generator_interface_contract_ref(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "pilot_key": str(contract.get("pilot_key", "")),
        "target_path": str(contract.get("target_path", "")),
        "families": list(contract.get("families", []) or []),
        "artifact_count": int(contract.get("artifact_count", 0)),
        "source_body_candidate_ref_count": int(contract.get("source_body_candidate_ref_count", 0)),
        "owner_generator": str(contract.get("owner_generator", "")),
        "generator_interface_status": str(contract.get("generator_interface_status", "")),
        "planned_source_writer_exists": str(contract.get("planned_source_writer_exists", "")),
        "source_generator_contract_only": True,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_event_source_generator_interface_prototype(
    *,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    owner_generator = str(contract.get("owner_generator", ""))
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    required_validations = sorted(_string_refs(contract.get("required_validations")))
    remaining_blockers = sorted(_string_refs(contract.get("remaining_blockers")))
    return {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "target_path": target_path,
        "owner_generator": owner_generator,
        "interface_name": f"{owner_generator}.emit_source_file_contract",
        "call_signature": _alhambra_source_generator_expected_call_signature(owner_generator),
        "input_contract": "source_generator_contract + source_file_validation_evidence_pack",
        "output_contract": "source_file_contract_artifacts",
        "output_kind": "source_file_contract_artifacts",
        "artifact_count": int(contract.get("artifact_count", 0)),
        "source_file_contract_artifact_count": int(contract.get("artifact_count", 0)),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": required_validations,
        "remaining_blockers": remaining_blockers,
        "dry_run": True,
        "dry_run_required": True,
        "source_file_level_contract": True,
        "source_generator_interface_prototype_only": True,
        "event_family_only": True,
        "memory_report_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_event_source_file_contract_artifact(
    *,
    ref: dict[str, Any],
    index: int,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    return {
        "artifact_key": _alhambra_event_source_file_contract_artifact_key(ref, index),
        "artifact_index": index,
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "row_set_key": str(ref.get("row_set_key", "")),
        "target_path": target_path,
        "future_source_target_path": str(ref.get("future_source_target_path", "")),
        "owner_generator": str(contract.get("owner_generator", "")),
        "generator_interface_status": REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_STATUS,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_file_contract_artifact_only": True,
        "source_generator_interface_prototype_only": True,
        "event_family_only": True,
        "memory_report_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "contract_only": True,
        "candidate_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_body_candidate_ref": deepcopy(ref),
        "source_body_candidate_ref_key": _alhambra_event_source_body_candidate_ref_key(ref),
        "source_body_candidate_ref_provenance": deepcopy(
            contract.get("source_body_candidate_ref_provenance", {}) or {}
        ),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "input_data_shape": deepcopy(contract.get("input_data_shape", {}) or {}),
        "output_artifact_family": deepcopy(contract.get("output_artifact_family", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": sorted(_string_refs(contract.get("required_validations"))),
        "remaining_blockers": sorted(_string_refs(contract.get("remaining_blockers"))),
        "unresolved_writer_blockers": sorted(_string_refs(contract.get("unresolved_writer_blockers"))),
        "no_write_source_writer_contract_evidence": deepcopy(
            contract.get("no_write_source_writer_contract_evidence", {}) or {}
        ),
    }


def repeated_entity_row_alhambra_event_source_generator_interface_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_file_validation_evidence is None:
        source_file_validation_evidence = repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
            payload,
            statuses=statuses,
        )
    if source_generator_contract is None:
        source_generator_contract = repeated_entity_row_alhambra_source_generator_contract_for_payload(
            payload,
            statuses=statuses,
            source_file_validation_evidence=source_file_validation_evidence,
        )
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    contract = _alhambra_source_generator_contract_for_target(source_generator_contract, target_path)
    validation_pack = next(
        (
            pack
            for pack in source_file_validation_evidence.get("evidence_packs", []) or []
            if isinstance(pack, dict) and pack.get("target_path") == target_path
        ),
        {},
    )
    source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
    refs = [
        ref
        for ref in contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    source_file_contract_artifacts = [
        _alhambra_event_source_file_contract_artifact(
            ref=ref,
            index=index,
            contract=contract,
            validation_pack=validation_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for index, ref in enumerate(refs)
    ]
    source_ready_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("source_ready") is True)
    source_writer_allowed_count = sum(
        1 for artifact in source_file_contract_artifacts if artifact.get("source_writer_allowed") is True
    )
    may_write_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("may_write_src") is True)
    writes_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("writes_src") is True)
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "target_path": target_path,
        "interface_count": 1 if contract else 0,
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "artifact_count": len(source_file_contract_artifacts),
        "output_kind": "source_file_contract_artifacts",
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "target_path": target_path,
        "source_generator_interface_prototype_only": True,
        "event_family_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "memory_report_only": True,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_generator_contract_input_only": True,
        "source_generator_contract_input_ref": source_generator_contract_ref,
        "source_generator_contract_validation_errors": list(source_generator_contract.get("validation_errors", []) or []),
        "source_file_validation_evidence_input_only": True,
        "source_file_validation_evidence_input_ref": {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        },
        "source_file_validation_evidence_validation_errors": list(
            source_file_validation_evidence.get("validation_errors", []) or []
        ),
        "summary": summary,
        "interface_count": summary["interface_count"],
        "artifact_count": len(source_file_contract_artifacts),
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "required_target_paths": [target_path],
        "source_generator_interfaces": [
            _alhambra_event_source_generator_interface_prototype(
                contract=contract,
                validation_pack=validation_pack,
                source_generator_contract_ref=source_generator_contract_ref,
            )
        ] if contract else [],
        "source_file_contract_artifacts": source_file_contract_artifacts,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "validation_errors": [],
        "notes": [
            "Alhambra event source generator interface is a no-write dry-run prototype.",
            "It emits only in-memory/report-level source_file_contract_artifacts for the event family.",
            "It binds back to external source-file validation evidence and never authorizes src writes.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_alhambra_event_source_generator_interface(
        report,
        source_generator_contract=source_generator_contract,
        source_file_validation_evidence=source_file_validation_evidence,
    )
    return report


def _alhambra_scripted_effect_cleanup_source_file_contract_artifact_key(
    ref: dict[str, Any],
    index: int,
) -> str:
    return "|".join(
        [
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_FAMILY,
            str(ref.get("family", "")),
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(index),
        ]
    )


def _alhambra_scripted_effect_cleanup_source_body_candidate_ref_key(
    ref: dict[str, Any],
) -> dict[str, str]:
    return {
        "family": str(ref.get("family", "")),
        "row_set_key": str(ref.get("row_set_key", "")),
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "future_source_target_path": str(ref.get("future_source_target_path", "")),
    }


def _alhambra_scripted_effect_cleanup_source_generator_interface_prototype(
    *,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    owner_generator = str(contract.get("owner_generator", ""))
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    target_families = list(REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_FAMILIES)
    required_validations = sorted(_string_refs(contract.get("required_validations")))
    remaining_blockers = sorted(_string_refs(contract.get("remaining_blockers")))
    return {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "families": target_families,
        "target_path": target_path,
        "owner_generator": owner_generator,
        "interface_name": f"{owner_generator}.emit_source_file_contract",
        "call_signature": _alhambra_source_generator_expected_call_signature(owner_generator),
        "input_contract": "source_generator_contract + source_file_validation_evidence_pack",
        "output_contract": "source_file_contract_artifacts",
        "output_kind": "source_file_contract_artifacts",
        "artifact_count": int(contract.get("artifact_count", 0)),
        "source_file_contract_artifact_count": int(contract.get("artifact_count", 0)),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": required_validations,
        "remaining_blockers": remaining_blockers,
        "dry_run": True,
        "dry_run_required": True,
        "source_file_level_contract": True,
        "source_generator_interface_prototype_only": True,
        "scripted_effect_cleanup_target_only": True,
        "memory_report_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
    *,
    ref: dict[str, Any],
    index: int,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    target_families = list(REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_FAMILIES)
    return {
        "artifact_key": _alhambra_scripted_effect_cleanup_source_file_contract_artifact_key(ref, index),
        "artifact_index": index,
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": str(ref.get("family", "")),
        "interface_family": REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "target_families": target_families,
        "row_set_key": str(ref.get("row_set_key", "")),
        "target_path": target_path,
        "future_source_target_path": str(ref.get("future_source_target_path", "")),
        "owner_generator": str(contract.get("owner_generator", "")),
        "generator_interface_status": (
            REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_STATUS
        ),
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_file_contract_artifact_only": True,
        "source_generator_interface_prototype_only": True,
        "scripted_effect_cleanup_target_only": True,
        "memory_report_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "contract_only": True,
        "candidate_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_body_candidate_ref": deepcopy(ref),
        "source_body_candidate_ref_key": _alhambra_scripted_effect_cleanup_source_body_candidate_ref_key(ref),
        "source_body_candidate_ref_provenance": deepcopy(
            contract.get("source_body_candidate_ref_provenance", {}) or {}
        ),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "input_data_shape": deepcopy(contract.get("input_data_shape", {}) or {}),
        "output_artifact_family": deepcopy(contract.get("output_artifact_family", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": sorted(_string_refs(contract.get("required_validations"))),
        "remaining_blockers": sorted(_string_refs(contract.get("remaining_blockers"))),
        "unresolved_writer_blockers": sorted(_string_refs(contract.get("unresolved_writer_blockers"))),
        "no_write_source_writer_contract_evidence": deepcopy(
            contract.get("no_write_source_writer_contract_evidence", {}) or {}
        ),
    }


def repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_file_validation_evidence is None:
        source_file_validation_evidence = repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
            payload,
            statuses=statuses,
        )
    if source_generator_contract is None:
        source_generator_contract = repeated_entity_row_alhambra_source_generator_contract_for_payload(
            payload,
            statuses=statuses,
            source_file_validation_evidence=source_file_validation_evidence,
        )
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    target_families = list(REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_FAMILIES)
    interface_family = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_FAMILY
    contract = _alhambra_source_generator_contract_for_target(source_generator_contract, target_path)
    validation_pack = next(
        (
            pack
            for pack in source_file_validation_evidence.get("evidence_packs", []) or []
            if isinstance(pack, dict) and pack.get("target_path") == target_path
        ),
        {},
    )
    source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
    refs = [
        ref
        for ref in contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    source_file_contract_artifacts = [
        _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
            ref=ref,
            index=index,
            contract=contract,
            validation_pack=validation_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for index, ref in enumerate(refs)
    ]
    source_ready_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("source_ready") is True)
    source_writer_allowed_count = sum(
        1 for artifact in source_file_contract_artifacts if artifact.get("source_writer_allowed") is True
    )
    may_write_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("may_write_src") is True)
    writes_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("writes_src") is True)
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": interface_family,
        "families": target_families,
        "target_path": target_path,
        "interface_count": 1 if contract else 0,
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "artifact_count": len(source_file_contract_artifacts),
        "family_artifact_counts": _count_by_key(source_file_contract_artifacts, "family"),
        "output_kind": "source_file_contract_artifacts",
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": interface_family,
        "families": target_families,
        "target_path": target_path,
        "source_generator_interface_prototype_only": True,
        "scripted_effect_cleanup_target_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "memory_report_only": True,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_generator_contract_input_only": True,
        "source_generator_contract_input_ref": source_generator_contract_ref,
        "source_generator_contract_validation_errors": list(source_generator_contract.get("validation_errors", []) or []),
        "source_file_validation_evidence_input_only": True,
        "source_file_validation_evidence_input_ref": {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        },
        "source_file_validation_evidence_validation_errors": list(
            source_file_validation_evidence.get("validation_errors", []) or []
        ),
        "summary": summary,
        "interface_count": summary["interface_count"],
        "artifact_count": len(source_file_contract_artifacts),
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "required_target_paths": [target_path],
        "source_generator_interfaces": [
            _alhambra_scripted_effect_cleanup_source_generator_interface_prototype(
                contract=contract,
                validation_pack=validation_pack,
                source_generator_contract_ref=source_generator_contract_ref,
            )
        ] if contract else [],
        "source_file_contract_artifacts": source_file_contract_artifacts,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "validation_errors": [],
        "notes": [
            "Alhambra scripted-effect/cleanup source generator interface is a no-write dry-run prototype.",
            "It emits only in-memory/report-level source_file_contract_artifacts for the shared scripted-effect target.",
            "It binds back to external source-file validation evidence and never authorizes src writes.",
        ],
    }
    report["validation_errors"] = (
        validate_repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface(
            report,
            source_generator_contract=source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
    )
    return report


def _alhambra_scripted_trigger_source_file_contract_artifact_key(
    ref: dict[str, Any],
    index: int,
) -> str:
    return "|".join(
        [
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_FAMILY,
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(index),
        ]
    )


def _alhambra_scripted_trigger_source_body_candidate_ref_key(
    ref: dict[str, Any],
) -> dict[str, str]:
    return {
        "family": str(ref.get("family", "")),
        "row_set_key": str(ref.get("row_set_key", "")),
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "future_source_target_path": str(ref.get("future_source_target_path", "")),
    }


def _alhambra_scripted_trigger_source_generator_interface_prototype(
    *,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    owner_generator = str(contract.get("owner_generator", ""))
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    required_validations = sorted(_string_refs(contract.get("required_validations")))
    remaining_blockers = sorted(_string_refs(contract.get("remaining_blockers")))
    return {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "target_path": target_path,
        "owner_generator": owner_generator,
        "interface_name": f"{owner_generator}.emit_source_file_contract",
        "call_signature": _alhambra_source_generator_expected_call_signature(owner_generator),
        "input_contract": "source_generator_contract + source_file_validation_evidence_pack",
        "output_contract": "source_file_contract_artifacts",
        "output_kind": "source_file_contract_artifacts",
        "artifact_count": int(contract.get("artifact_count", 0)),
        "source_file_contract_artifact_count": int(contract.get("artifact_count", 0)),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": required_validations,
        "remaining_blockers": remaining_blockers,
        "dry_run": True,
        "dry_run_required": True,
        "source_file_level_contract": True,
        "source_generator_interface_prototype_only": True,
        "scripted_trigger_target_only": True,
        "memory_report_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_scripted_trigger_source_file_contract_artifact(
    *,
    ref: dict[str, Any],
    index: int,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    return {
        "artifact_key": _alhambra_scripted_trigger_source_file_contract_artifact_key(ref, index),
        "artifact_index": index,
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "row_set_key": str(ref.get("row_set_key", "")),
        "target_path": target_path,
        "future_source_target_path": str(ref.get("future_source_target_path", "")),
        "owner_generator": str(contract.get("owner_generator", "")),
        "generator_interface_status": REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_STATUS,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_file_contract_artifact_only": True,
        "source_generator_interface_prototype_only": True,
        "scripted_trigger_target_only": True,
        "memory_report_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "contract_only": True,
        "candidate_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_body_candidate_ref": deepcopy(ref),
        "source_body_candidate_ref_key": _alhambra_scripted_trigger_source_body_candidate_ref_key(ref),
        "source_body_candidate_ref_provenance": deepcopy(
            contract.get("source_body_candidate_ref_provenance", {}) or {}
        ),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "input_data_shape": deepcopy(contract.get("input_data_shape", {}) or {}),
        "output_artifact_family": deepcopy(contract.get("output_artifact_family", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": sorted(_string_refs(contract.get("required_validations"))),
        "remaining_blockers": sorted(_string_refs(contract.get("remaining_blockers"))),
        "unresolved_writer_blockers": sorted(_string_refs(contract.get("unresolved_writer_blockers"))),
        "no_write_source_writer_contract_evidence": deepcopy(
            contract.get("no_write_source_writer_contract_evidence", {}) or {}
        ),
    }


def repeated_entity_row_alhambra_scripted_trigger_source_generator_interface_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_file_validation_evidence is None:
        source_file_validation_evidence = repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
            payload,
            statuses=statuses,
        )
    if source_generator_contract is None:
        source_generator_contract = repeated_entity_row_alhambra_source_generator_contract_for_payload(
            payload,
            statuses=statuses,
            source_file_validation_evidence=source_file_validation_evidence,
        )
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    interface_family = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_FAMILY
    contract = _alhambra_source_generator_contract_for_target(source_generator_contract, target_path)
    validation_pack = next(
        (
            pack
            for pack in source_file_validation_evidence.get("evidence_packs", []) or []
            if isinstance(pack, dict) and pack.get("target_path") == target_path
        ),
        {},
    )
    source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
    refs = [
        ref
        for ref in contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    source_file_contract_artifacts = [
        _alhambra_scripted_trigger_source_file_contract_artifact(
            ref=ref,
            index=index,
            contract=contract,
            validation_pack=validation_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for index, ref in enumerate(refs)
    ]
    source_ready_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("source_ready") is True)
    source_writer_allowed_count = sum(
        1 for artifact in source_file_contract_artifacts if artifact.get("source_writer_allowed") is True
    )
    may_write_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("may_write_src") is True)
    writes_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("writes_src") is True)
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": interface_family,
        "target_path": target_path,
        "interface_count": 1 if contract else 0,
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "artifact_count": len(source_file_contract_artifacts),
        "output_kind": "source_file_contract_artifacts",
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": interface_family,
        "target_path": target_path,
        "source_generator_interface_prototype_only": True,
        "scripted_trigger_target_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "memory_report_only": True,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_generator_contract_input_only": True,
        "source_generator_contract_input_ref": source_generator_contract_ref,
        "source_generator_contract_validation_errors": list(source_generator_contract.get("validation_errors", []) or []),
        "source_file_validation_evidence_input_only": True,
        "source_file_validation_evidence_input_ref": {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        },
        "source_file_validation_evidence_validation_errors": list(
            source_file_validation_evidence.get("validation_errors", []) or []
        ),
        "summary": summary,
        "interface_count": summary["interface_count"],
        "artifact_count": len(source_file_contract_artifacts),
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "required_target_paths": [target_path],
        "source_generator_interfaces": [
            _alhambra_scripted_trigger_source_generator_interface_prototype(
                contract=contract,
                validation_pack=validation_pack,
                source_generator_contract_ref=source_generator_contract_ref,
            )
        ] if contract else [],
        "source_file_contract_artifacts": source_file_contract_artifacts,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "validation_errors": [],
        "notes": [
            "Alhambra scripted-trigger source generator interface is a no-write dry-run prototype.",
            "It emits only in-memory/report-level source_file_contract_artifacts for the scripted-trigger target.",
            "It binds back to external source-file validation evidence and never authorizes src writes.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_alhambra_scripted_trigger_source_generator_interface(
        report,
        source_generator_contract=source_generator_contract,
        source_file_validation_evidence=source_file_validation_evidence,
    )
    return report


def _alhambra_localization_source_file_contract_artifact_key(
    *,
    ref: dict[str, Any],
    index: int,
    language: str,
) -> str:
    return "|".join(
        [
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_FAMILY,
            language,
            str(ref.get("row_set_key", "")),
            str(ref.get("artifact_kind", "")),
            str(index),
        ]
    )


def _alhambra_localization_source_body_candidate_ref_key(ref: dict[str, Any]) -> dict[str, str]:
    return {
        "family": str(ref.get("family", "")),
        "row_set_key": str(ref.get("row_set_key", "")),
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "future_source_target_path": str(ref.get("future_source_target_path", "")),
    }


def _alhambra_localization_source_generator_interface_prototype(
    *,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    owner_generator = str(contract.get("owner_generator", ""))
    target_path = str(contract.get("target_path", ""))
    language = str(contract.get("localization_language", ""))
    required_validations = sorted(_string_refs(contract.get("required_validations")))
    remaining_blockers = sorted(_string_refs(contract.get("remaining_blockers")))
    return {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "localization_language": language,
        "target_path": target_path,
        "owner_generator": owner_generator,
        "interface_name": f"{owner_generator}.emit_source_file_contract",
        "call_signature": _alhambra_source_generator_expected_call_signature(owner_generator),
        "input_contract": "source_generator_contract + source_file_validation_evidence_pack",
        "output_contract": "source_file_contract_artifacts",
        "output_kind": "source_file_contract_artifacts",
        "artifact_count": int(contract.get("artifact_count", 0)),
        "source_file_contract_artifact_count": int(contract.get("artifact_count", 0)),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "localization_language_boundary": deepcopy(contract.get("localization_language_boundary", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": required_validations,
        "remaining_blockers": remaining_blockers,
        "dry_run": True,
        "dry_run_required": True,
        "source_file_level_contract": True,
        "source_generator_interface_prototype_only": True,
        "localization_family_only": True,
        "memory_report_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
    }


def _alhambra_localization_source_file_contract_artifact(
    *,
    ref: dict[str, Any],
    index: int,
    contract: dict[str, Any],
    validation_pack: dict[str, Any],
    source_generator_contract_ref: dict[str, Any],
) -> dict[str, Any]:
    target_path = str(contract.get("target_path", ""))
    language = str(contract.get("localization_language", ""))
    return {
        "artifact_key": _alhambra_localization_source_file_contract_artifact_key(
            ref=ref,
            index=index,
            language=language,
        ),
        "artifact_index": index,
        "artifact_kind": str(ref.get("artifact_kind", "")),
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "localization_language": language,
        "row_set_key": str(ref.get("row_set_key", "")),
        "target_path": target_path,
        "future_source_target_path": target_path,
        "source_candidate_future_target_path": str(ref.get("future_source_target_path", "")),
        "owner_generator": str(contract.get("owner_generator", "")),
        "generator_interface_status": REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_STATUS,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_file_contract_artifact_only": True,
        "source_generator_interface_prototype_only": True,
        "localization_family_only": True,
        "memory_report_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "contract_only": True,
        "candidate_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "source_body_candidate_ref": deepcopy(ref),
        "source_body_candidate_ref_key": _alhambra_localization_source_body_candidate_ref_key(ref),
        "source_body_candidate_ref_provenance": deepcopy(
            contract.get("source_body_candidate_ref_provenance", {}) or {}
        ),
        "source_generator_contract_ref": deepcopy(source_generator_contract_ref),
        "source_file_validation_evidence_ref": _alhambra_source_generator_contract_pack_ref(validation_pack),
        "generator_interface_draft": deepcopy(contract.get("generator_interface_draft", {}) or {}),
        "localization_language_boundary": deepcopy(contract.get("localization_language_boundary", {}) or {}),
        "input_data_shape": deepcopy(contract.get("input_data_shape", {}) or {}),
        "output_artifact_family": deepcopy(contract.get("output_artifact_family", {}) or {}),
        "source_target_boundary": deepcopy(contract.get("source_target_boundary", {}) or {}),
        "required_validations": sorted(_string_refs(contract.get("required_validations"))),
        "remaining_blockers": sorted(_string_refs(contract.get("remaining_blockers"))),
        "unresolved_writer_blockers": sorted(_string_refs(contract.get("unresolved_writer_blockers"))),
        "no_write_source_writer_contract_evidence": deepcopy(
            contract.get("no_write_source_writer_contract_evidence", {}) or {}
        ),
    }


def repeated_entity_row_alhambra_localization_source_generator_interface_for_payload(
    payload: dict[str, Any],
    *,
    statuses: set[str] | None = None,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_file_validation_evidence is None:
        source_file_validation_evidence = repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
            payload,
            statuses=statuses,
        )
    if source_generator_contract is None:
        source_generator_contract = repeated_entity_row_alhambra_source_generator_contract_for_payload(
            payload,
            statuses=statuses,
            source_file_validation_evidence=source_file_validation_evidence,
        )
    target_paths = list(REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_TARGET_PATHS)
    source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
    source_generator_interfaces: list[dict[str, Any]] = []
    source_file_contract_artifacts: list[dict[str, Any]] = []
    for target_path in target_paths:
        contract = _alhambra_source_generator_contract_for_target(source_generator_contract, target_path)
        validation_pack = next(
            (
                pack
                for pack in source_file_validation_evidence.get("evidence_packs", []) or []
                if isinstance(pack, dict) and pack.get("target_path") == target_path
            ),
            {},
        )
        if not contract:
            continue
        source_generator_interfaces.append(
            _alhambra_localization_source_generator_interface_prototype(
                contract=contract,
                validation_pack=validation_pack,
                source_generator_contract_ref=source_generator_contract_ref,
            )
        )
        refs = [
            ref
            for ref in contract.get("source_body_candidate_refs", []) or []
            if isinstance(ref, dict)
        ]
        source_file_contract_artifacts.extend(
            _alhambra_localization_source_file_contract_artifact(
                ref=ref,
                index=index,
                contract=contract,
                validation_pack=validation_pack,
                source_generator_contract_ref=source_generator_contract_ref,
            )
            for index, ref in enumerate(refs)
        )

    source_ready_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("source_ready") is True)
    source_writer_allowed_count = sum(
        1 for artifact in source_file_contract_artifacts if artifact.get("source_writer_allowed") is True
    )
    may_write_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("may_write_src") is True)
    writes_src_count = sum(1 for artifact in source_file_contract_artifacts if artifact.get("writes_src") is True)
    target_artifact_counts = _count_by_key(source_file_contract_artifacts, "target_path")
    language_artifact_counts = _count_by_key(source_file_contract_artifacts, "localization_language")
    summary = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "target_paths": target_paths,
        "interface_count": len(source_generator_interfaces),
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "artifact_count": len(source_file_contract_artifacts),
        "target_artifact_counts": target_artifact_counts,
        "language_artifact_counts": language_artifact_counts,
        "output_kind": "source_file_contract_artifacts",
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
    }
    report = {
        "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
        "family": REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_FAMILY,
        "target_paths": target_paths,
        "localization_target_paths": dict(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
        ),
        "source_generator_interface_prototype_only": True,
        "localization_family_only": True,
        "dry_run": True,
        "dry_run_required": True,
        "memory_report_only": True,
        "output_kind": "source_file_contract_artifacts",
        "output_is_loadable_source": False,
        "source_generator_contract_input_only": True,
        "source_generator_contract_input_ref": source_generator_contract_ref,
        "source_generator_contract_validation_errors": list(source_generator_contract.get("validation_errors", []) or []),
        "source_file_validation_evidence_input_only": True,
        "source_file_validation_evidence_input_ref": {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        },
        "source_file_validation_evidence_validation_errors": list(
            source_file_validation_evidence.get("validation_errors", []) or []
        ),
        "summary": summary,
        "interface_count": summary["interface_count"],
        "artifact_count": len(source_file_contract_artifacts),
        "source_file_contract_artifact_count": len(source_file_contract_artifacts),
        "target_artifact_counts": target_artifact_counts,
        "language_artifact_counts": language_artifact_counts,
        "required_target_paths": target_paths,
        "source_generator_interfaces": source_generator_interfaces,
        "source_file_contract_artifacts": source_file_contract_artifacts,
        "source_ready_count": source_ready_count,
        "source_writer_allowed_count": source_writer_allowed_count,
        "may_write_src_count": may_write_src_count,
        "writes_src_count": writes_src_count,
        "candidate_only": True,
        "contract_only": True,
        "body_emitted": False,
        "source_ready": False,
        "verified": False,
        "backend_ready": False,
        "source_writer_allowed": False,
        "may_write_src": False,
        "writes_src": False,
        "no_write_boundary_flags": _repeated_row_source_bundle_no_write_boundary(),
        "no_write_placeholder_flags": _alhambra_source_body_candidate_flags(),
        "validation_errors": [],
        "notes": [
            "Alhambra localization source generator interface is a no-write dry-run prototype.",
            "It keeps English and Simplified Chinese target-file contracts separate.",
            "It emits only in-memory/report-level localization source_file_contract_artifacts.",
            "It binds each target back to external source-file validation evidence and never authorizes src writes.",
        ],
    }
    report["validation_errors"] = validate_repeated_entity_row_alhambra_localization_source_generator_interface(
        report,
        source_generator_contract=source_generator_contract,
        source_file_validation_evidence=source_file_validation_evidence,
    )
    return report


def _validate_alhambra_source_generator_contract_boundary(
    *,
    context: str,
    boundary: Any,
    target_path: str,
    families: list[str],
    errors: list[str],
) -> None:
    if not isinstance(boundary, dict) or not boundary:
        errors.append(f"{context} missing source target boundary")
        return
    if boundary.get("status") != "blocked":
        errors.append(f"{context} source target boundary must stay blocked")
    if boundary.get("target_path") != target_path:
        errors.append(f"{context} source target boundary target path mismatch")
    if boundary.get("families") != families:
        errors.append(f"{context} source target boundary families mismatch")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src", "source_ready", "body_emitted"):
        if boundary.get(flag) is not False:
            errors.append(f"{context} source target boundary {flag} must be false")


def _validate_alhambra_source_generator_interface_draft(
    *,
    context: str,
    draft: Any,
    target_path: str,
    families: list[str],
    owner_generator: str,
    errors: list[str],
) -> None:
    if not isinstance(draft, dict) or not draft:
        errors.append(f"{context} missing generator interface draft")
        return
    missing = _missing_required(
        draft,
        {
            "interface_name",
            "proposed_function_name",
            "owner_generator",
            "call_signature_draft",
            "input_parameter",
            "output_contract",
            "target_path",
            "families",
            "generator_interface_status",
            "dry_run_required",
            "source_file_level_contract",
            "contract_only",
            "body_emitted",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        },
    )
    if missing:
        errors.append(f"{context} generator interface draft missing field(s): {', '.join(missing)}")
        return
    if draft.get("owner_generator") != owner_generator:
        errors.append(f"{context} generator interface draft owner mismatch")
    expected_interface_name = f"{owner_generator}.emit_source_file_contract"
    if draft.get("interface_name") != expected_interface_name:
        errors.append(f"{context} generator interface draft interface_name mismatch")
    if draft.get("proposed_function_name") != "emit_source_file_contract":
        errors.append(f"{context} generator interface draft proposed_function_name mismatch")
    if draft.get("input_parameter") != "source_file_validation_pack":
        errors.append(f"{context} generator interface draft input_parameter mismatch")
    if draft.get("output_contract") != "source_file_contract_artifacts":
        errors.append(f"{context} generator interface draft output_contract mismatch")
    if draft.get("call_signature_draft") != _alhambra_source_generator_expected_call_signature(owner_generator):
        errors.append(f"{context} generator interface draft call_signature_draft mismatch")
    if draft.get("target_path") != target_path:
        errors.append(f"{context} generator interface draft target path mismatch")
    if draft.get("families") != families:
        errors.append(f"{context} generator interface draft families mismatch")
    if draft.get("generator_interface_status") != "contract_drafted":
        errors.append(f"{context} generator interface draft status must be contract_drafted")
    if draft.get("dry_run_required") is not True or draft.get("source_file_level_contract") is not True:
        errors.append(f"{context} generator interface draft must be source-file-level dry-run")
    for flag in ("body_emitted", "source_writer_allowed", "may_write_src", "writes_src"):
        if draft.get(flag) is not False:
            errors.append(f"{context} generator interface draft {flag} must be false")
    if draft.get("contract_only") is not True:
        errors.append(f"{context} generator interface draft must be contract-only")


def _validate_alhambra_source_generator_input_data_shape(
    *,
    context: str,
    shape: Any,
    target_path: str,
    families: list[str],
    artifact_count: int,
    source_body_candidate_ref_count: int,
    artifact_kinds: list[str],
    family_artifact_counts: dict[str, int],
    row_set_keys: list[str],
    future_source_target_paths: list[str],
    errors: list[str],
) -> None:
    if not isinstance(shape, dict) or not shape:
        errors.append(f"{context} missing input data shape")
        return
    missing = _missing_required(
        shape,
        {
            "input_source",
            "input_pack_selector",
            "required_pack_fields",
            "required_source_body_ref_fields",
            "target_path",
            "families",
            "artifact_count",
            "source_body_candidate_ref_count",
            "artifact_kinds",
            "family_artifact_counts",
            "row_set_keys",
            "future_source_target_paths",
            "source_file_validation_evidence_only",
            "contract_only",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        },
    )
    if missing:
        errors.append(f"{context} input data shape missing field(s): {', '.join(missing)}")
        return
    selector = shape.get("input_pack_selector") if isinstance(shape.get("input_pack_selector"), dict) else {}
    if selector.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append(f"{context} input data shape pilot selector mismatch")
    if selector.get("target_path") != target_path or shape.get("target_path") != target_path:
        errors.append(f"{context} input data shape target path mismatch")
    if shape.get("families") != families:
        errors.append(f"{context} input data shape families mismatch")
    if int(shape.get("artifact_count", -1)) != artifact_count:
        errors.append(f"{context} input data shape artifact_count mismatch")
    if int(shape.get("source_body_candidate_ref_count", -1)) != source_body_candidate_ref_count:
        errors.append(f"{context} input data shape source_body_candidate_ref_count mismatch")
    if sorted(_string_refs(shape.get("artifact_kinds"))) != artifact_kinds:
        errors.append(f"{context} input data shape artifact kinds mismatch")
    if shape.get("family_artifact_counts") != family_artifact_counts:
        errors.append(f"{context} input data shape family counts mismatch")
    if sorted(_string_refs(shape.get("row_set_keys"))) != row_set_keys:
        errors.append(f"{context} input data shape row set keys mismatch")
    if sorted(_string_refs(shape.get("future_source_target_paths"))) != future_source_target_paths:
        errors.append(f"{context} input data shape future source target paths mismatch")
    required_pack_fields = set(_string_refs(shape.get("required_pack_fields")))
    if not REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_REQUIRED_FIELDS <= required_pack_fields:
        errors.append(f"{context} input data shape required pack fields mismatch")
    required_ref_fields = set(_string_refs(shape.get("required_source_body_ref_fields")))
    if not {"pilot_key", "family", "row_set_key", "artifact_kind", "future_source_target_path"} <= required_ref_fields:
        errors.append(f"{context} input data shape required source body ref fields mismatch")
    if shape.get("source_file_validation_evidence_only") is not True or shape.get("contract_only") is not True:
        errors.append(f"{context} input data shape must stay validation-evidence contract-only")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src"):
        if shape.get(flag) is not False:
            errors.append(f"{context} input data shape {flag} must be false")
    localization_targets = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
    if target_path in localization_targets.values():
        language = str(shape.get("localization_language", ""))
        if localization_targets.get(language) != target_path:
            errors.append(f"{context} input data shape localization language mismatch")
        if set(_string_refs(shape.get("required_languages"))) != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
            errors.append(f"{context} input data shape localization languages mismatch")
        if shape.get("separate_language_target") is not True:
            errors.append(f"{context} input data shape localization target must stay separate")
    if families == ["listener"]:
        required_listener_fields = set(_string_refs(shape.get("listener_linkage_required_fields")))
        if not {
            "on_action_hook_linkage_plan",
            "selected_ritual_trigger_linkage",
            "war_scope_availability_persistence_plan",
        } <= required_listener_fields:
            errors.append(f"{context} input data shape missing listener linkage fields")


def _validate_alhambra_source_generator_output_artifact_family(
    *,
    context: str,
    output: Any,
    target_path: str,
    families: list[str],
    artifact_count: int,
    source_body_candidate_ref_count: int,
    artifact_kinds: list[str],
    family_artifact_counts: dict[str, int],
    row_set_keys: list[str],
    future_source_target_paths: list[str],
    errors: list[str],
) -> None:
    if not isinstance(output, dict) or not output:
        errors.append(f"{context} missing output artifact family")
        return
    missing = _missing_required(
        output,
        {
            "target_path",
            "families",
            "artifact_count",
            "source_body_candidate_ref_count",
            "artifact_kinds",
            "family_artifact_counts",
            "row_set_keys",
            "future_source_target_paths",
            "output_kind",
            "output_is_loadable_source",
            "contract_only",
            "body_emitted",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        },
    )
    if missing:
        errors.append(f"{context} output artifact family missing field(s): {', '.join(missing)}")
        return
    if output.get("target_path") != target_path:
        errors.append(f"{context} output artifact family target path mismatch")
    if output.get("families") != families:
        errors.append(f"{context} output artifact family families mismatch")
    if int(output.get("artifact_count", -1)) != artifact_count:
        errors.append(f"{context} output artifact family artifact_count mismatch")
    if int(output.get("source_body_candidate_ref_count", -1)) != source_body_candidate_ref_count:
        errors.append(f"{context} output artifact family source_body_candidate_ref_count mismatch")
    if sorted(_string_refs(output.get("artifact_kinds"))) != artifact_kinds:
        errors.append(f"{context} output artifact family artifact kinds mismatch")
    if output.get("family_artifact_counts") != family_artifact_counts:
        errors.append(f"{context} output artifact family counts mismatch")
    if sorted(_string_refs(output.get("row_set_keys"))) != row_set_keys:
        errors.append(f"{context} output artifact family row set keys mismatch")
    if sorted(_string_refs(output.get("future_source_target_paths"))) != future_source_target_paths:
        errors.append(f"{context} output artifact family future source target paths mismatch")
    if output.get("output_kind") != "source_file_contract_artifacts":
        errors.append(f"{context} output artifact family output_kind mismatch")
    if output.get("output_is_loadable_source") is not False or output.get("contract_only") is not True:
        errors.append(f"{context} output artifact family must stay contract-only and non-loadable")
    for flag in ("body_emitted", "source_writer_allowed", "may_write_src", "writes_src"):
        if output.get(flag) is not False:
            errors.append(f"{context} output artifact family {flag} must be false")


def _validate_alhambra_source_generator_ref_provenance_snapshot(
    *,
    context: str,
    snapshot: Any,
    target_path: str,
    families: list[str],
    artifact_count: int,
    errors: list[str],
) -> dict[str, Any]:
    empty_summary = _alhambra_source_generator_ref_summary_from_key_tuples([])
    if not isinstance(snapshot, dict) or not snapshot:
        errors.append(f"{context} missing source body candidate ref provenance")
        return empty_summary
    missing = _missing_required(
        snapshot,
        {
            "provenance_snapshot_only",
            "snapshot_source",
            "source_file_validation_evidence_only",
            "target_path",
            "families",
            "artifact_count",
            "source_body_candidate_ref_count",
            "canonical_source_body_candidate_ref_key_fields",
            "canonical_source_body_candidate_ref_key_set",
            "artifact_kinds",
            "family_artifact_counts",
            "row_set_keys",
            "future_source_target_paths",
            "source_file_validation_pack_ref",
            "contract_only",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        },
    )
    if missing:
        errors.append(f"{context} source body candidate ref provenance missing field(s): {', '.join(missing)}")
        return empty_summary
    if snapshot.get("provenance_snapshot_only") is not True:
        errors.append(f"{context} source body candidate ref provenance must be snapshot-only")
    if snapshot.get("source_file_validation_evidence_only") is not True:
        errors.append(f"{context} source body candidate ref provenance must derive from validation evidence")
    if snapshot.get("target_path") != target_path:
        errors.append(f"{context} source body candidate ref provenance target path mismatch")
    if snapshot.get("families") != families:
        errors.append(f"{context} source body candidate ref provenance families mismatch")
    if int(snapshot.get("artifact_count", -1)) != artifact_count:
        errors.append(f"{context} source body candidate ref provenance artifact_count mismatch")
    if snapshot.get("canonical_source_body_candidate_ref_key_fields") != list(
        REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_REF_KEY_FIELDS
    ):
        errors.append(f"{context} source body candidate ref provenance key fields mismatch")

    raw_key_set = snapshot.get("canonical_source_body_candidate_ref_key_set")
    if not isinstance(raw_key_set, list) or not raw_key_set:
        errors.append(f"{context} source body candidate ref provenance key set missing")
        return empty_summary
    ref_key_tuples = _alhambra_source_generator_ref_key_tuples_from_refs(
        [ref for ref in raw_key_set if isinstance(ref, dict)]
    )
    ref_summary = _alhambra_source_generator_ref_summary_from_key_tuples(ref_key_tuples)
    if int(snapshot.get("source_body_candidate_ref_count", -1)) != ref_summary["source_body_candidate_ref_count"]:
        errors.append(f"{context} source body candidate ref provenance ref count mismatch")
    if ref_summary["source_body_candidate_ref_count"] != artifact_count:
        errors.append(f"{context} source body candidate ref provenance key set must match artifact_count")
    if sorted(_string_refs(snapshot.get("artifact_kinds"))) != ref_summary["artifact_kinds"]:
        errors.append(f"{context} source body candidate ref provenance artifact kinds mismatch")
    if snapshot.get("family_artifact_counts") != ref_summary["family_artifact_counts"]:
        errors.append(f"{context} source body candidate ref provenance family counts mismatch")
    if sorted(_string_refs(snapshot.get("row_set_keys"))) != ref_summary["row_set_keys"]:
        errors.append(f"{context} source body candidate ref provenance row set keys mismatch")
    if sorted(_string_refs(snapshot.get("future_source_target_paths"))) != ref_summary["future_source_target_paths"]:
        errors.append(f"{context} source body candidate ref provenance future source target paths mismatch")
    pack_ref = snapshot.get("source_file_validation_pack_ref")
    if not isinstance(pack_ref, dict):
        errors.append(f"{context} source body candidate ref provenance missing validation pack ref")
    else:
        if pack_ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append(f"{context} source body candidate ref provenance pack ref pilot mismatch")
        if pack_ref.get("target_path") != target_path:
            errors.append(f"{context} source body candidate ref provenance pack ref target mismatch")
        if int(pack_ref.get("artifact_count", -1)) != artifact_count:
            errors.append(f"{context} source body candidate ref provenance pack ref artifact_count mismatch")
        if int(pack_ref.get("source_body_candidate_ref_count", -1)) != artifact_count:
            errors.append(f"{context} source body candidate ref provenance pack ref source ref count mismatch")
    if snapshot.get("contract_only") is not True:
        errors.append(f"{context} source body candidate ref provenance must be contract-only")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src"):
        if snapshot.get(flag) is not False:
            errors.append(f"{context} source body candidate ref provenance {flag} must be false")
    return ref_summary


def _validate_alhambra_source_generator_no_write_contract_evidence(
    *,
    context: str,
    evidence: Any,
    target_path: str,
    families: list[str],
    owner_generator: str,
    source_body_candidate_ref_provenance: dict[str, Any],
    required_validations: list[str],
    remaining_blockers: list[str],
    source_target_boundary: dict[str, Any],
    generator_interface_draft: dict[str, Any],
    input_data_shape: dict[str, Any],
    output_artifact_family: dict[str, Any],
    errors: list[str],
) -> None:
    if not isinstance(evidence, dict) or not evidence:
        errors.append(f"{context} missing no-write source-writer contract evidence")
        return
    missing = _missing_required(
        evidence,
        {
            "contract_evidence_only",
            "target_path",
            "target_paths",
            "families",
            "owner_generator",
            "owner_generator_candidate",
            "source_body_candidate_ref_provenance",
            "generator_interface_draft",
            "input_data_shape",
            "output_artifact_family",
            "validation_refs",
            "validation_command",
            "verification_commands",
            "source_writer_blocker_reasons",
            "source_writer_still_blocked_reason",
            "source_target_boundary",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        },
    )
    if missing:
        errors.append(f"{context} no-write source-writer contract evidence missing field(s): {', '.join(missing)}")
        return
    if evidence.get("contract_evidence_only") is not True:
        errors.append(f"{context} no-write source-writer contract evidence must be contract-only")
    if evidence.get("target_path") != target_path or evidence.get("target_paths") != [target_path]:
        errors.append(f"{context} no-write source-writer contract evidence target path mismatch")
    if evidence.get("families") != families:
        errors.append(f"{context} no-write source-writer contract evidence families mismatch")
    if evidence.get("owner_generator") != owner_generator:
        errors.append(f"{context} no-write source-writer contract evidence owner mismatch")
    if evidence.get("source_body_candidate_ref_provenance") != source_body_candidate_ref_provenance:
        errors.append(f"{context} no-write source-writer contract evidence provenance mismatch")
    if evidence.get("generator_interface_draft") != generator_interface_draft:
        errors.append(f"{context} no-write source-writer contract evidence interface draft mismatch")
    if evidence.get("input_data_shape") != input_data_shape:
        errors.append(f"{context} no-write source-writer contract evidence input data shape mismatch")
    if evidence.get("output_artifact_family") != output_artifact_family:
        errors.append(f"{context} no-write source-writer contract evidence output artifact family mismatch")
    if sorted(_string_refs(evidence.get("validation_refs"))) != required_validations:
        errors.append(f"{context} no-write source-writer contract evidence validation refs mismatch")
    if tuple(_string_refs(evidence.get("verification_commands"))) != REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS:
        errors.append(f"{context} no-write source-writer contract evidence verification commands mismatch")
    if evidence.get("validation_command") != REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS[0]:
        errors.append(f"{context} no-write source-writer contract evidence validation command mismatch")
    if sorted(_string_refs(evidence.get("source_writer_blocker_reasons"))) != remaining_blockers:
        errors.append(f"{context} no-write source-writer contract evidence blocker reasons mismatch")
    if not str(evidence.get("source_writer_still_blocked_reason", "")).strip():
        errors.append(f"{context} no-write source-writer contract evidence missing still-blocked reason")
    if evidence.get("source_target_boundary") != source_target_boundary:
        errors.append(f"{context} no-write source-writer contract evidence source-target boundary mismatch")
    for flag in ("source_writer_allowed", "may_write_src", "writes_src"):
        if evidence.get(flag) is not False:
            errors.append(f"{context} no-write source-writer contract evidence {flag} must be false")


def _alhambra_source_generator_external_validation_evidence_pack_index(
    source_file_validation_evidence: Any,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    if not isinstance(source_file_validation_evidence, dict):
        errors.append("Alhambra source generator contract external source-file validation evidence must be a mapping")
        return {}
    evidence_errors = validate_repeated_entity_row_alhambra_source_file_validation_evidence(
        source_file_validation_evidence
    )
    if evidence_errors:
        errors.append("Alhambra source generator contract external source-file validation evidence must be clean")
    pack_index: dict[str, dict[str, Any]] = {}
    for pack in source_file_validation_evidence.get("evidence_packs", []) or []:
        if not isinstance(pack, dict):
            continue
        target_path = str(pack.get("target_path", ""))
        if not target_path:
            continue
        if target_path in pack_index:
            errors.append(
                "Alhambra source generator contract external source-file validation evidence duplicate target "
                f"{target_path}"
            )
            continue
        pack_index[target_path] = pack
    return pack_index


def _validate_alhambra_source_generator_external_evidence_binding(
    *,
    context: str,
    contract: dict[str, Any],
    external_pack: dict[str, Any],
    target_path: str,
    families: list[str],
    owner_generator: str,
    errors: list[str],
) -> None:
    if external_pack.get("target_path") != target_path:
        errors.append(f"{context} external validation evidence target path mismatch")
    if list(external_pack.get("families", []) or []) != families:
        errors.append(f"{context} external validation evidence families mismatch")

    expected_ref_key_tuples = _alhambra_source_generator_ref_key_tuples_from_refs(
        [
            ref
            for ref in external_pack.get("source_body_candidate_refs", []) or []
            if isinstance(ref, dict)
        ]
    )
    contract_ref_key_tuples = _alhambra_source_generator_ref_key_tuples_from_refs(
        [
            ref
            for ref in contract.get("source_body_candidate_refs", []) or []
            if isinstance(ref, dict)
        ]
    )
    if contract_ref_key_tuples != expected_ref_key_tuples:
        errors.append(f"{context} source body candidate refs external validation evidence mismatch")

    expected_provenance = _alhambra_source_generator_ref_provenance_snapshot(external_pack)
    if contract.get("source_body_candidate_ref_provenance") != expected_provenance:
        errors.append(f"{context} source body candidate ref provenance external validation evidence mismatch")
    if contract.get("evidence_pack_ref") != _alhambra_source_generator_contract_pack_ref(external_pack):
        errors.append(f"{context} evidence_pack_ref external validation evidence mismatch")

    expected_input_shape = _alhambra_source_generator_input_data_shape(
        pack=external_pack,
        target_path=target_path,
        families=families,
    )
    if contract.get("input_data_shape") != expected_input_shape:
        errors.append(f"{context} input data shape external validation evidence mismatch")

    expected_output_family = _alhambra_source_generator_output_artifact_family(
        pack=external_pack,
        target_path=target_path,
        families=families,
    )
    if contract.get("output_artifact_family") != expected_output_family:
        errors.append(f"{context} output artifact family external validation evidence mismatch")

    expected_source_target_boundary = deepcopy(external_pack.get("source_target_boundary", {}) or {})
    if contract.get("source_target_boundary") != expected_source_target_boundary:
        errors.append(f"{context} source target boundary external validation evidence mismatch")

    expected_required_validations = sorted(_string_refs(external_pack.get("required_validations")))
    if sorted(_string_refs(contract.get("required_validations"))) != expected_required_validations:
        errors.append(f"{context} required validations external validation evidence mismatch")

    expected_remaining_blockers = sorted(_string_refs(external_pack.get("unresolved_blockers")))
    if sorted(_string_refs(contract.get("remaining_blockers"))) != expected_remaining_blockers:
        errors.append(f"{context} remaining blockers external validation evidence mismatch")
    if sorted(_string_refs(contract.get("unresolved_writer_blockers"))) != sorted(
        _string_refs(external_pack.get("unresolved_writer_blockers"))
    ):
        errors.append(f"{context} unresolved writer blockers external validation evidence mismatch")
    if sorted(_string_refs(contract.get("source_writer_blocker_reasons"))) != expected_remaining_blockers:
        errors.append(f"{context} source writer blocker reasons external validation evidence mismatch")

    expected_interface_draft = _alhambra_source_generator_interface_draft(
        target_path=target_path,
        families=families,
        owner_generator=owner_generator,
    )
    expected_no_write_evidence = _alhambra_source_generator_no_write_contract_evidence(
        target_path=target_path,
        families=families,
        owner_generator=owner_generator,
        source_body_candidate_ref_provenance=expected_provenance,
        pack=external_pack,
        generator_interface_draft=expected_interface_draft,
        input_data_shape=expected_input_shape,
        output_artifact_family=expected_output_family,
        required_validations=expected_required_validations,
        remaining_blockers=expected_remaining_blockers,
        source_target_boundary=expected_source_target_boundary,
    )
    if contract.get("no_write_source_writer_contract_evidence") != expected_no_write_evidence:
        errors.append(f"{context} no-write source-writer contract evidence external validation evidence mismatch")


def validate_repeated_entity_row_alhambra_source_generator_contract(
    report: dict[str, Any],
    *,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra source generator contract pilot_key must be unique_alhambra")
    if report.get("source_generator_contract_only") is not True:
        errors.append("Alhambra source generator contract must declare source_generator_contract_only: true")
    if report.get("source_file_validation_evidence_input_only") is not True:
        errors.append("Alhambra source generator contract must derive from source-file validation evidence input")
    if report.get("source_file_validation_evidence_validation_errors"):
        errors.append("Alhambra source generator contract source-file validation evidence must be clean")
    input_ref = (
        report.get("source_file_validation_evidence_input_ref")
        if isinstance(report.get("source_file_validation_evidence_input_ref"), dict)
        else {}
    )
    if not input_ref:
        errors.append("Alhambra source generator contract missing source-file validation evidence input ref")
    else:
        if input_ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source generator contract input ref pilot_key must be unique_alhambra")
        if int(input_ref.get("evidence_pack_count", -1)) != len(
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS
        ):
            errors.append("Alhambra source generator contract input ref evidence_pack_count must be 7")
        if int(input_ref.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
            errors.append("Alhambra source generator contract input ref artifact_count must be 45")
        if input_ref.get("validation_errors"):
            errors.append("Alhambra source generator contract input ref validation must be clean")
    external_validation_packs_by_target: dict[str, dict[str, Any]] | None = None
    if source_file_validation_evidence is not None:
        external_validation_packs_by_target = _alhambra_source_generator_external_validation_evidence_pack_index(
            source_file_validation_evidence,
            errors,
        )
        if isinstance(source_file_validation_evidence, dict):
            expected_input_ref = {
                "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
                "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
                "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
                "source_body_candidate_ref_count": int(
                    source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
                ),
                "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
            }
            if input_ref and input_ref != expected_input_ref:
                errors.append(
                    "Alhambra source generator contract input ref external validation evidence mismatch"
                )

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(f"Alhambra source generator contract must not claim source_ready/verified/backend_ready at {path}")
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"Alhambra source generator contract {flag} must be false at {path}")

    _validate_alhambra_source_body_candidate_flags(
        context="Alhambra source generator contract report",
        value=report,
        errors=errors,
    )

    expected_target_paths = set(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_REQUIRED_TARGET_PATHS)
    generator_contracts = (
        report.get("generator_contracts") if isinstance(report.get("generator_contracts"), list) else []
    )
    if int(report.get("generator_contract_count", -1)) != len(generator_contracts):
        errors.append("Alhambra source generator contract generator_contract_count mismatch")
    if int(report.get("generator_contract_count", -1)) != len(expected_target_paths):
        errors.append("Alhambra source generator contract generator_contract_count must be 7")
    if int(report.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append("Alhambra source generator contract artifact_count must be 45")

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra source generator contract summary missing")
    else:
        if summary.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append("Alhambra source generator contract summary pilot_key must be unique_alhambra")
        if int(summary.get("generator_contract_count", -1)) != len(expected_target_paths):
            errors.append("Alhambra source generator contract summary generator_contract_count must be 7")
        if int(summary.get("artifact_count", -1)) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
            errors.append("Alhambra source generator contract summary artifact_count must be 45")
        expected_status_summary = _count_by_key(
            [
                contract
                for contract in generator_contracts
                if isinstance(contract, dict)
            ],
            "generator_interface_status",
        )
        if summary.get("generator_interface_status_summary") != expected_status_summary:
            errors.append("Alhambra source generator contract summary status mismatch")
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(summary.get(count_key, -1)) != 0:
                errors.append(f"Alhambra source generator contract summary {count_key} must be 0")

    target_counts: dict[str, int] = {}
    source_ref_keys: set[tuple[str, str, str, str]] = set()
    localization_languages: set[str] = set()
    for contract in generator_contracts:
        if not isinstance(contract, dict):
            errors.append("Alhambra source generator contract entry must be a mapping")
            continue
        missing_fields = _missing_required(
            contract,
            REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_GENERATOR_CONTRACT_REQUIRED_FIELDS,
        )
        target_path = str(contract.get("target_path", ""))
        context = f"Alhambra source generator contract {target_path or '<missing-target>'}"
        if missing_fields:
            errors.append(f"{context} missing field(s): {', '.join(missing_fields)}")
        metadata = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA.get(target_path)
        if metadata is None:
            errors.append(f"{context} has unexpected target path")
            continue
        target_counts[target_path] = target_counts.get(target_path, 0) + 1
        expected_families = list(metadata["families"])
        families = list(contract.get("families", []) or [])
        if families != expected_families:
            errors.append(f"{context} families mismatch")
        expected_artifact_count = int(metadata["artifact_count"])
        if int(contract.get("artifact_count", -1)) != expected_artifact_count:
            errors.append(f"{context} artifact_count mismatch")
        if not _alhambra_source_generator_contract_allowed_status(contract.get("generator_interface_status")):
            errors.append(f"{context} generator_interface_status must be contract_drafted or blocked")
        expected_owner = str(metadata.get("owner_candidate", ""))
        if contract.get("owner_generator") != expected_owner:
            errors.append(f"{context} owner_generator mismatch")
        if contract.get("planned_source_writer_exists") != "interface_contract_exists":
            errors.append(f"{context} planned_source_writer_exists must be interface_contract_exists")
        external_pack = (
            external_validation_packs_by_target.get(target_path)
            if external_validation_packs_by_target is not None
            else None
        )
        if external_validation_packs_by_target is not None and external_pack is None:
            errors.append(f"{context} missing external source-file validation evidence pack")

        refs = contract.get("source_body_candidate_refs") if isinstance(contract.get("source_body_candidate_refs"), list) else []
        structured_refs = [
            ref
            for ref in refs
            if isinstance(ref, dict)
        ]
        provenance_summary = _validate_alhambra_source_generator_ref_provenance_snapshot(
            context=context,
            snapshot=contract.get("source_body_candidate_ref_provenance"),
            target_path=target_path,
            families=expected_families,
            artifact_count=expected_artifact_count,
            errors=errors,
        )
        contract_ref_key_tuples = _alhambra_source_generator_ref_key_tuples_from_refs(structured_refs)
        if contract_ref_key_tuples != provenance_summary["canonical_ref_key_tuples"]:
            errors.append(f"{context} source body candidate refs provenance mismatch")
        required_validations = sorted(_string_refs(contract.get("required_validations")))
        remaining_blockers = sorted(_string_refs(contract.get("remaining_blockers")))
        source_target_boundary = (
            contract.get("source_target_boundary") if isinstance(contract.get("source_target_boundary"), dict) else {}
        )

        _validate_alhambra_source_generator_interface_draft(
            context=context,
            draft=contract.get("generator_interface_draft"),
            target_path=target_path,
            families=expected_families,
            owner_generator=expected_owner,
            errors=errors,
        )
        _validate_alhambra_source_generator_input_data_shape(
            context=context,
            shape=contract.get("input_data_shape"),
            target_path=target_path,
            families=expected_families,
            artifact_count=expected_artifact_count,
            source_body_candidate_ref_count=provenance_summary["source_body_candidate_ref_count"],
            artifact_kinds=provenance_summary["artifact_kinds"],
            family_artifact_counts=provenance_summary["family_artifact_counts"],
            row_set_keys=provenance_summary["row_set_keys"],
            future_source_target_paths=provenance_summary["future_source_target_paths"],
            errors=errors,
        )
        _validate_alhambra_source_generator_output_artifact_family(
            context=context,
            output=contract.get("output_artifact_family"),
            target_path=target_path,
            families=expected_families,
            artifact_count=expected_artifact_count,
            source_body_candidate_ref_count=provenance_summary["source_body_candidate_ref_count"],
            artifact_kinds=provenance_summary["artifact_kinds"],
            family_artifact_counts=provenance_summary["family_artifact_counts"],
            row_set_keys=provenance_summary["row_set_keys"],
            future_source_target_paths=provenance_summary["future_source_target_paths"],
            errors=errors,
        )
        _validate_alhambra_source_body_candidate_flags(context=context, value=contract, errors=errors)
        for flag in ("source_ready", "verified", "backend_ready", "source_writer_allowed", "may_write_src", "writes_src"):
            if contract.get(flag) is not False:
                errors.append(f"{context} {flag} must be false")
        for count_key in (
            "source_ready_count",
            "source_writer_allowed_count",
            "may_write_src_count",
            "writes_src_count",
        ):
            if int(contract.get(count_key, -1)) != 0:
                errors.append(f"{context} {count_key} must be 0")

        evidence_ref = contract.get("evidence_pack_ref")
        if not isinstance(evidence_ref, dict) or not evidence_ref:
            errors.append(f"{context} missing evidence_pack_ref")
        else:
            if evidence_ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                errors.append(f"{context} evidence_pack_ref pilot_key must be unique_alhambra")
            if evidence_ref.get("target_path") != target_path:
                errors.append(f"{context} evidence_pack_ref target mismatch")
            if evidence_ref.get("families") != expected_families:
                errors.append(f"{context} evidence_pack_ref families mismatch")
            if int(evidence_ref.get("artifact_count", -1)) != expected_artifact_count:
                errors.append(f"{context} evidence_pack_ref artifact_count mismatch")
            if evidence_ref.get("source_file_validation_evidence_only") is not True:
                errors.append(f"{context} evidence_pack_ref must derive from validation evidence")

        _validate_alhambra_source_generator_contract_boundary(
            context=context,
            boundary=source_target_boundary,
            target_path=target_path,
            families=expected_families,
            errors=errors,
        )

        if not required_validations:
            errors.append(f"{context} required_validations must not be empty")
        if not remaining_blockers:
            errors.append(f"{context} remaining_blockers must not be empty while source target boundary is blocked")
        if sorted(_string_refs(contract.get("unresolved_writer_blockers"))) != remaining_blockers:
            errors.append(f"{context} unresolved writer blockers mismatch")
        if sorted(_string_refs(contract.get("source_writer_blocker_reasons"))) != remaining_blockers:
            errors.append(f"{context} source writer blocker reasons mismatch")
        if not str(contract.get("source_writer_still_blocked_reason", "")).strip():
            errors.append(f"{context} missing source writer still-blocked reason")
        if tuple(_string_refs(contract.get("verification_commands"))) != REPEATED_ENTITY_ROW_NO_WRITE_SOURCE_WRITER_VERIFICATION_COMMANDS:
            errors.append(f"{context} verification commands mismatch")
        _validate_alhambra_source_generator_no_write_contract_evidence(
            context=context,
            evidence=contract.get("no_write_source_writer_contract_evidence"),
            target_path=target_path,
            families=expected_families,
            owner_generator=expected_owner,
            source_body_candidate_ref_provenance=contract.get("source_body_candidate_ref_provenance"),
            required_validations=required_validations,
            remaining_blockers=remaining_blockers,
            source_target_boundary=source_target_boundary,
            generator_interface_draft=contract.get("generator_interface_draft"),
            input_data_shape=contract.get("input_data_shape"),
            output_artifact_family=contract.get("output_artifact_family"),
            errors=errors,
        )
        if external_pack is not None:
            _validate_alhambra_source_generator_external_evidence_binding(
                context=context,
                contract=contract,
                external_pack=external_pack,
                target_path=target_path,
                families=expected_families,
                owner_generator=expected_owner,
                errors=errors,
            )

        if int(contract.get("source_body_candidate_ref_count", -1)) != len(structured_refs):
            errors.append(f"{context} source_body_candidate_ref_count mismatch")
        for ref in refs:
            if not isinstance(ref, dict):
                continue
            if ref.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
                errors.append(f"{context} source body candidate ref pilot_key must be unique_alhambra")
        source_ref_keys.update(provenance_summary["canonical_ref_key_tuples"])

        localization_targets = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
        if target_path in localization_targets.values():
            language = str(contract.get("localization_language", ""))
            localization_languages.add(language)
            if localization_targets.get(language) != target_path:
                errors.append(f"{context} localization target path does not match language")
            if families != ["localization"]:
                errors.append(f"{context} localization generator contract must contain only localization")
            _validate_alhambra_source_file_preview_localization_boundary(
                context=context,
                boundary=contract.get("localization_language_boundary"),
                language=language,
                target_path=target_path,
                errors=errors,
            )
        elif "localization" in families:
            errors.append(f"{context} localization generator contract must use separated language target files")

        if families == ["listener"]:
            if int(contract.get("artifact_count", -1)) != 1:
                errors.append(f"{context} listener target artifact_count must be 1")
            _validate_alhambra_source_file_validation_listener_linkage(
                context=context,
                linkage=contract.get("listener_linkage_contract"),
                errors=errors,
            )

    duplicate_targets = sorted(target for target, count in target_counts.items() if count > 1)
    if duplicate_targets:
        errors.append(f"Alhambra source generator contract duplicate target path(s): {', '.join(duplicate_targets)}")
    actual_targets = set(target_counts)
    missing_targets = sorted(expected_target_paths - actual_targets)
    extra_targets = sorted(actual_targets - expected_target_paths)
    if missing_targets:
        errors.append(f"Alhambra source generator contract missing required target path(s): {', '.join(missing_targets)}")
    if extra_targets:
        errors.append(f"Alhambra source generator contract has unexpected target path(s): {', '.join(extra_targets)}")
    if external_validation_packs_by_target is not None and actual_targets != set(external_validation_packs_by_target):
        errors.append("Alhambra source generator contract target paths external validation evidence mismatch")
    if localization_languages != set(REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS):
        errors.append("Alhambra source generator contract localization must split English and Simplified Chinese files")
    if len(source_ref_keys) != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_ARTIFACT_COUNT:
        errors.append(f"Alhambra source generator contract expected 45 unique source body artifacts, got {len(source_ref_keys)}")
    if int(report.get("source_body_candidate_ref_count", -1)) != len(source_ref_keys):
        errors.append("Alhambra source generator contract source_body_candidate_ref_count mismatch")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra source generator contract {count_key} must be 0")
    return errors


def validate_repeated_entity_row_alhambra_event_source_generator_interface(
    report: dict[str, Any],
    *,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    expected_family = REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_FAMILY
    expected_artifact_count = int(
        REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA[target_path]["artifact_count"]
    )

    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra event source generator interface pilot_key must be unique_alhambra")
    if report.get("family") != expected_family:
        errors.append("Alhambra event source generator interface family must be event")
    if report.get("target_path") != target_path:
        errors.append("Alhambra event source generator interface target_path mismatch")
    if report.get("source_generator_interface_prototype_only") is not True:
        errors.append("Alhambra event source generator interface must declare prototype-only")
    if report.get("event_family_only") is not True:
        errors.append("Alhambra event source generator interface must be event-family-only")
    if report.get("dry_run") is not True or report.get("dry_run_required") is not True:
        errors.append("Alhambra event source generator interface must be dry-run")
    if report.get("memory_report_only") is not True:
        errors.append("Alhambra event source generator interface must be memory/report-only")
    if report.get("output_kind") != "source_file_contract_artifacts":
        errors.append("Alhambra event source generator interface output_kind must be source_file_contract_artifacts")
    if report.get("output_is_loadable_source") is not False:
        errors.append("Alhambra event source generator interface output must not be loadable source")
    if report.get("source_generator_contract_input_only") is not True:
        errors.append("Alhambra event source generator interface must derive from source generator contract input")
    if report.get("source_file_validation_evidence_input_only") is not True:
        errors.append("Alhambra event source generator interface must derive from source-file validation evidence input")
    if report.get("source_generator_contract_validation_errors"):
        errors.append("Alhambra event source generator interface source generator contract input must be clean")
    if report.get("source_file_validation_evidence_validation_errors"):
        errors.append("Alhambra event source generator interface source-file validation evidence input must be clean")

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(
            "Alhambra event source generator interface must not claim source_ready/verified/backend_ready "
            f"at {path}"
        )
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"Alhambra event source generator interface {flag} must be false at {path}")
    _validate_alhambra_source_body_candidate_flags(
        context="Alhambra event source generator interface report",
        value=report,
        errors=errors,
    )

    if source_file_validation_evidence is None:
        errors.append(
            "Alhambra event source generator interface requires external source-file validation evidence"
        )
        external_pack: dict[str, Any] = {}
    else:
        evidence_errors = validate_repeated_entity_row_alhambra_source_file_validation_evidence(
            source_file_validation_evidence
        )
        if evidence_errors:
            errors.append(
                "Alhambra event source generator interface external source-file validation evidence must be clean"
            )
        expected_evidence_input_ref = {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        }
        if report.get("source_file_validation_evidence_input_ref") != expected_evidence_input_ref:
            errors.append(
                "Alhambra event source generator interface source-file validation evidence input ref mismatch"
            )
        external_pack = next(
            (
                pack
                for pack in source_file_validation_evidence.get("evidence_packs", []) or []
                if isinstance(pack, dict) and pack.get("target_path") == target_path
            ),
            {},
        )
        if not external_pack:
            errors.append(
                "Alhambra event source generator interface missing external event source-file validation pack"
            )

    if source_generator_contract is None:
        errors.append("Alhambra event source generator interface requires source generator contract input")
        expected_contract: dict[str, Any] = {}
        source_generator_contract_ref: dict[str, Any] = {}
    else:
        contract_errors = validate_repeated_entity_row_alhambra_source_generator_contract(
            source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if contract_errors:
            errors.append(
                "Alhambra event source generator interface source generator contract input must bind cleanly"
            )
        source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
        if report.get("source_generator_contract_input_ref") != source_generator_contract_ref:
            errors.append(
                "Alhambra event source generator interface source generator contract input ref mismatch"
            )
        expected_contract = (
            _alhambra_source_generator_contract_for_pack(external_pack)
            if external_pack
            else _alhambra_source_generator_contract_for_target(source_generator_contract, target_path)
        )
        if not expected_contract:
            errors.append("Alhambra event source generator interface missing event source generator contract")

    expected_pack_ref = _alhambra_source_generator_contract_pack_ref(external_pack) if external_pack else {}
    expected_refs = [
        ref
        for ref in expected_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    expected_artifacts = [
        _alhambra_event_source_file_contract_artifact(
            ref=ref,
            index=index,
            contract=expected_contract,
            validation_pack=external_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for index, ref in enumerate(expected_refs)
    ] if expected_contract and external_pack else []
    expected_interface = (
        _alhambra_event_source_generator_interface_prototype(
            contract=expected_contract,
            validation_pack=external_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        if expected_contract and external_pack
        else {}
    )

    artifacts = report.get("source_file_contract_artifacts")
    if not isinstance(artifacts, list):
        errors.append("Alhambra event source generator interface source_file_contract_artifacts must be a list")
        artifacts = []
    interfaces = report.get("source_generator_interfaces")
    if not isinstance(interfaces, list):
        errors.append("Alhambra event source generator interface source_generator_interfaces must be a list")
        interfaces = []

    if int(report.get("interface_count", -1)) != len(interfaces):
        errors.append("Alhambra event source generator interface interface_count mismatch")
    if int(report.get("interface_count", -1)) != 1:
        errors.append("Alhambra event source generator interface interface_count must be 1")
    if int(report.get("artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra event source generator interface artifact_count mismatch")
    if int(report.get("source_file_contract_artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra event source generator interface artifact count mismatch")
    if int(report.get("artifact_count", -1)) != expected_artifact_count:
        errors.append("Alhambra event source generator interface artifact_count must be 8")
    if report.get("required_target_paths") != [target_path]:
        errors.append("Alhambra event source generator interface required target paths must contain only event target")

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra event source generator interface summary missing")
    else:
        expected_summary = {
            "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            "family": expected_family,
            "target_path": target_path,
            "interface_count": 1,
            "source_file_contract_artifact_count": len(artifacts),
            "artifact_count": len(artifacts),
            "output_kind": "source_file_contract_artifacts",
            "source_ready_count": 0,
            "source_writer_allowed_count": 0,
            "may_write_src_count": 0,
            "writes_src_count": 0,
        }
        if summary != expected_summary:
            errors.append("Alhambra event source generator interface summary mismatch")

    if len(interfaces) != 1:
        errors.append("Alhambra event source generator interface must expose exactly one event interface")
    elif interfaces and isinstance(interfaces[0], dict):
        interface = interfaces[0]
        missing = _missing_required(
            interface,
            REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(
                "Alhambra event source generator interface prototype missing field(s): "
                + ", ".join(missing)
            )
        elif expected_interface and interface != expected_interface:
            errors.append(
                "Alhambra event source generator interface prototype external validation evidence mismatch"
            )
    else:
        errors.append("Alhambra event source generator interface prototype must be a mapping")

    actual_ref_keys: set[tuple[str, str, str, str]] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append("Alhambra event source generator interface artifact must be a mapping")
            continue
        context = f"Alhambra event source generator interface artifact {index}"
        missing = _missing_required(
            artifact,
            REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(f"{context} missing field(s): {', '.join(missing)}")
            continue
        if artifact.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append(f"{context} pilot_key must be unique_alhambra")
        if artifact.get("family") != expected_family:
            errors.append(f"{context} family must be event")
        if artifact.get("target_path") != target_path:
            errors.append(f"{context} target_path mismatch")
        if artifact.get("future_source_target_path") != target_path:
            errors.append(f"{context} future_source_target_path mismatch")
        if artifact.get("generator_interface_status") != REPEATED_ENTITY_ROW_ALHAMBRA_EVENT_SOURCE_GENERATOR_INTERFACE_STATUS:
            errors.append(f"{context} generator_interface_status mismatch")
        if artifact.get("output_kind") != "source_file_contract_artifacts":
            errors.append(f"{context} output_kind must be source_file_contract_artifacts")
        if artifact.get("output_is_loadable_source") is not False:
            errors.append(f"{context} output must not be loadable source")
        if artifact.get("source_file_contract_artifact_only") is not True:
            errors.append(f"{context} must be source-file contract artifact only")
        if artifact.get("source_generator_interface_prototype_only") is not True:
            errors.append(f"{context} must be interface-prototype-only")
        if artifact.get("event_family_only") is not True:
            errors.append(f"{context} must be event-family-only")
        if artifact.get("memory_report_only") is not True:
            errors.append(f"{context} must be memory/report-only")
        if artifact.get("dry_run") is not True or artifact.get("dry_run_required") is not True:
            errors.append(f"{context} must be dry-run")
        if artifact.get("contract_only") is not True or artifact.get("candidate_only") is not True:
            errors.append(f"{context} must be contract/candidate-only")
        for flag in ("body_emitted", "source_ready", "verified", "backend_ready", "source_writer_allowed", "may_write_src", "writes_src"):
            if artifact.get(flag) is not False:
                errors.append(f"{context} {flag} must be false")
        ref = artifact.get("source_body_candidate_ref") if isinstance(artifact.get("source_body_candidate_ref"), dict) else {}
        ref_key = _alhambra_source_file_preview_ref_key(ref)
        actual_ref_keys.add(ref_key)
        if artifact.get("source_body_candidate_ref_key") != _alhambra_event_source_body_candidate_ref_key(ref):
            errors.append(f"{context} source body candidate ref key mismatch")
        if artifact.get("source_generator_contract_ref") != source_generator_contract_ref:
            errors.append(f"{context} source generator contract ref mismatch")
        if artifact.get("source_file_validation_evidence_ref") != expected_pack_ref:
            errors.append(f"{context} source-file validation evidence ref mismatch")
        if expected_artifacts and index < len(expected_artifacts) and artifact != expected_artifacts[index]:
            errors.append(f"{context} external validation evidence mismatch")

    expected_ref_keys = {
        _alhambra_source_file_preview_ref_key(ref)
        for ref in expected_refs
    }
    if actual_ref_keys != expected_ref_keys:
        errors.append("Alhambra event source generator interface source body refs external validation evidence mismatch")
    if len(actual_ref_keys) != expected_artifact_count:
        errors.append(
            f"Alhambra event source generator interface expected 8 unique source file contract artifacts, got {len(actual_ref_keys)}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra event source generator interface {count_key} must be 0")
    return errors


def validate_repeated_entity_row_alhambra_scripted_trigger_source_generator_interface(
    report: dict[str, Any],
    *,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    expected_family = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_FAMILY
    expected_artifact_count = int(
        REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA[target_path]["artifact_count"]
    )

    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra scripted-trigger source generator interface pilot_key must be unique_alhambra")
    if report.get("family") != expected_family:
        errors.append("Alhambra scripted-trigger source generator interface family must be trigger")
    if report.get("target_path") != target_path:
        errors.append("Alhambra scripted-trigger source generator interface target_path mismatch")
    if report.get("source_generator_interface_prototype_only") is not True:
        errors.append("Alhambra scripted-trigger source generator interface must declare prototype-only")
    if report.get("scripted_trigger_target_only") is not True:
        errors.append("Alhambra scripted-trigger source generator interface must be scripted-trigger-target-only")
    if report.get("dry_run") is not True or report.get("dry_run_required") is not True:
        errors.append("Alhambra scripted-trigger source generator interface must be dry-run")
    if report.get("memory_report_only") is not True:
        errors.append("Alhambra scripted-trigger source generator interface must be memory/report-only")
    if report.get("output_kind") != "source_file_contract_artifacts":
        errors.append(
            "Alhambra scripted-trigger source generator interface output_kind must be "
            "source_file_contract_artifacts"
        )
    if report.get("output_is_loadable_source") is not False:
        errors.append("Alhambra scripted-trigger source generator interface output must not be loadable source")
    if report.get("source_generator_contract_input_only") is not True:
        errors.append(
            "Alhambra scripted-trigger source generator interface must derive from source generator contract input"
        )
    if report.get("source_file_validation_evidence_input_only") is not True:
        errors.append(
            "Alhambra scripted-trigger source generator interface must derive from source-file validation evidence input"
        )
    if report.get("source_generator_contract_validation_errors"):
        errors.append("Alhambra scripted-trigger source generator interface source generator contract input must be clean")
    if report.get("source_file_validation_evidence_validation_errors"):
        errors.append(
            "Alhambra scripted-trigger source generator interface source-file validation evidence input must be clean"
        )

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(
            "Alhambra scripted-trigger source generator interface must not claim "
            f"source_ready/verified/backend_ready at {path}"
        )
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"Alhambra scripted-trigger source generator interface {flag} must be false at {path}")
    _validate_alhambra_source_body_candidate_flags(
        context="Alhambra scripted-trigger source generator interface report",
        value=report,
        errors=errors,
    )

    if source_file_validation_evidence is None:
        errors.append(
            "Alhambra scripted-trigger source generator interface requires external source-file validation evidence"
        )
        external_pack: dict[str, Any] = {}
    else:
        evidence_errors = validate_repeated_entity_row_alhambra_source_file_validation_evidence(
            source_file_validation_evidence
        )
        if evidence_errors:
            errors.append(
                "Alhambra scripted-trigger source generator interface external source-file validation evidence must be clean"
            )
        expected_evidence_input_ref = {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        }
        if report.get("source_file_validation_evidence_input_ref") != expected_evidence_input_ref:
            errors.append(
                "Alhambra scripted-trigger source generator interface source-file validation evidence input ref mismatch"
            )
        external_pack = next(
            (
                pack
                for pack in source_file_validation_evidence.get("evidence_packs", []) or []
                if isinstance(pack, dict) and pack.get("target_path") == target_path
            ),
            {},
        )
        if not external_pack:
            errors.append(
                "Alhambra scripted-trigger source generator interface missing external scripted-trigger source-file validation pack"
            )
        elif list(external_pack.get("families", []) or []) != [expected_family]:
            errors.append(
                "Alhambra scripted-trigger source generator interface external validation evidence families mismatch"
            )

    if source_generator_contract is None:
        errors.append("Alhambra scripted-trigger source generator interface requires source generator contract input")
        expected_contract: dict[str, Any] = {}
        source_generator_contract_ref: dict[str, Any] = {}
    else:
        contract_errors = validate_repeated_entity_row_alhambra_source_generator_contract(
            source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if contract_errors:
            errors.append(
                "Alhambra scripted-trigger source generator interface source generator contract input must bind cleanly"
            )
        source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
        if report.get("source_generator_contract_input_ref") != source_generator_contract_ref:
            errors.append(
                "Alhambra scripted-trigger source generator interface source generator contract input ref mismatch"
            )
        expected_contract = (
            _alhambra_source_generator_contract_for_pack(external_pack)
            if external_pack
            else _alhambra_source_generator_contract_for_target(source_generator_contract, target_path)
        )
        if not expected_contract:
            errors.append(
                "Alhambra scripted-trigger source generator interface missing scripted-trigger source generator contract"
            )

    expected_pack_ref = _alhambra_source_generator_contract_pack_ref(external_pack) if external_pack else {}
    expected_refs = [
        ref
        for ref in expected_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    expected_artifacts = [
        _alhambra_scripted_trigger_source_file_contract_artifact(
            ref=ref,
            index=index,
            contract=expected_contract,
            validation_pack=external_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for index, ref in enumerate(expected_refs)
    ] if expected_contract and external_pack else []
    expected_interface = (
        _alhambra_scripted_trigger_source_generator_interface_prototype(
            contract=expected_contract,
            validation_pack=external_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        if expected_contract and external_pack
        else {}
    )

    artifacts = report.get("source_file_contract_artifacts")
    if not isinstance(artifacts, list):
        errors.append(
            "Alhambra scripted-trigger source generator interface source_file_contract_artifacts must be a list"
        )
        artifacts = []
    interfaces = report.get("source_generator_interfaces")
    if not isinstance(interfaces, list):
        errors.append("Alhambra scripted-trigger source generator interface source_generator_interfaces must be a list")
        interfaces = []

    if int(report.get("interface_count", -1)) != len(interfaces):
        errors.append("Alhambra scripted-trigger source generator interface interface_count mismatch")
    if int(report.get("interface_count", -1)) != 1:
        errors.append("Alhambra scripted-trigger source generator interface interface_count must be 1")
    if int(report.get("artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra scripted-trigger source generator interface artifact_count mismatch")
    if int(report.get("source_file_contract_artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra scripted-trigger source generator interface artifact count mismatch")
    if int(report.get("artifact_count", -1)) != expected_artifact_count:
        errors.append("Alhambra scripted-trigger source generator interface artifact_count must be 6")
    if report.get("required_target_paths") != [target_path]:
        errors.append(
            "Alhambra scripted-trigger source generator interface required target paths must contain only scripted-trigger target"
        )

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra scripted-trigger source generator interface summary missing")
    else:
        expected_summary = {
            "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            "family": expected_family,
            "target_path": target_path,
            "interface_count": 1,
            "source_file_contract_artifact_count": len(artifacts),
            "artifact_count": len(artifacts),
            "output_kind": "source_file_contract_artifacts",
            "source_ready_count": 0,
            "source_writer_allowed_count": 0,
            "may_write_src_count": 0,
            "writes_src_count": 0,
        }
        if summary != expected_summary:
            errors.append("Alhambra scripted-trigger source generator interface summary mismatch")

    if len(interfaces) != 1:
        errors.append("Alhambra scripted-trigger source generator interface must expose exactly one interface")
    elif interfaces and isinstance(interfaces[0], dict):
        interface = interfaces[0]
        missing = _missing_required(
            interface,
            REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(
                "Alhambra scripted-trigger source generator interface prototype missing field(s): "
                + ", ".join(missing)
            )
        elif expected_interface and interface != expected_interface:
            errors.append(
                "Alhambra scripted-trigger source generator interface prototype external validation evidence mismatch"
            )
    else:
        errors.append("Alhambra scripted-trigger source generator interface prototype must be a mapping")

    actual_ref_keys: set[tuple[str, str, str, str]] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append("Alhambra scripted-trigger source generator interface artifact must be a mapping")
            continue
        context = f"Alhambra scripted-trigger source generator interface artifact {index}"
        missing = _missing_required(
            artifact,
            REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(f"{context} missing field(s): {', '.join(missing)}")
            continue
        if artifact.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append(f"{context} pilot_key must be unique_alhambra")
        if artifact.get("family") != expected_family:
            errors.append(f"{context} family must be trigger")
        if artifact.get("target_path") != target_path:
            errors.append(f"{context} target_path mismatch")
        if artifact.get("future_source_target_path") != target_path:
            errors.append(f"{context} future_source_target_path mismatch")
        if (
            artifact.get("generator_interface_status")
            != REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_TRIGGER_SOURCE_GENERATOR_INTERFACE_STATUS
        ):
            errors.append(f"{context} generator_interface_status mismatch")
        if artifact.get("output_kind") != "source_file_contract_artifacts":
            errors.append(f"{context} output_kind must be source_file_contract_artifacts")
        if artifact.get("output_is_loadable_source") is not False:
            errors.append(f"{context} output must not be loadable source")
        if artifact.get("source_file_contract_artifact_only") is not True:
            errors.append(f"{context} must be source-file contract artifact only")
        if artifact.get("source_generator_interface_prototype_only") is not True:
            errors.append(f"{context} must be interface-prototype-only")
        if artifact.get("scripted_trigger_target_only") is not True:
            errors.append(f"{context} must be scripted-trigger-target-only")
        if artifact.get("memory_report_only") is not True:
            errors.append(f"{context} must be memory/report-only")
        if artifact.get("dry_run") is not True or artifact.get("dry_run_required") is not True:
            errors.append(f"{context} must be dry-run")
        if artifact.get("contract_only") is not True or artifact.get("candidate_only") is not True:
            errors.append(f"{context} must be contract/candidate-only")
        for flag in (
            "body_emitted",
            "source_ready",
            "verified",
            "backend_ready",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        ):
            if artifact.get(flag) is not False:
                errors.append(f"{context} {flag} must be false")
        ref = artifact.get("source_body_candidate_ref") if isinstance(artifact.get("source_body_candidate_ref"), dict) else {}
        ref_key = _alhambra_source_file_preview_ref_key(ref)
        actual_ref_keys.add(ref_key)
        if artifact.get("source_body_candidate_ref_key") != _alhambra_scripted_trigger_source_body_candidate_ref_key(ref):
            errors.append(f"{context} source body candidate ref key mismatch")
        if artifact.get("source_generator_contract_ref") != source_generator_contract_ref:
            errors.append(f"{context} source generator contract ref mismatch")
        if artifact.get("source_file_validation_evidence_ref") != expected_pack_ref:
            errors.append(f"{context} source-file validation evidence ref mismatch")
        if expected_artifacts and index < len(expected_artifacts) and artifact != expected_artifacts[index]:
            errors.append(f"{context} external validation evidence mismatch")

    expected_ref_keys = {
        _alhambra_source_file_preview_ref_key(ref)
        for ref in expected_refs
    }
    if actual_ref_keys != expected_ref_keys:
        errors.append(
            "Alhambra scripted-trigger source generator interface source body refs external validation evidence mismatch"
        )
    if len(actual_ref_keys) != expected_artifact_count:
        errors.append(
            "Alhambra scripted-trigger source generator interface expected 6 unique source file contract "
            f"artifacts, got {len(actual_ref_keys)}"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra scripted-trigger source generator interface {count_key} must be 0")
    return errors


def validate_repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface(
    report: dict[str, Any],
    *,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    target_path = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_PATH
    expected_family = REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_FAMILY
    expected_target_families = list(
        REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_TARGET_FAMILIES
    )
    expected_artifact_count = int(
        REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA[target_path]["artifact_count"]
    )

    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra scripted-effect/cleanup source generator interface pilot_key must be unique_alhambra")
    if report.get("family") != expected_family:
        errors.append("Alhambra scripted-effect/cleanup source generator interface family must be scripted_effect_cleanup")
    if report.get("families") != expected_target_families:
        errors.append("Alhambra scripted-effect/cleanup source generator interface families mismatch")
    if report.get("target_path") != target_path:
        errors.append("Alhambra scripted-effect/cleanup source generator interface target_path mismatch")
    if report.get("source_generator_interface_prototype_only") is not True:
        errors.append("Alhambra scripted-effect/cleanup source generator interface must declare prototype-only")
    if report.get("scripted_effect_cleanup_target_only") is not True:
        errors.append("Alhambra scripted-effect/cleanup source generator interface must be scripted-effect/cleanup-target-only")
    if report.get("dry_run") is not True or report.get("dry_run_required") is not True:
        errors.append("Alhambra scripted-effect/cleanup source generator interface must be dry-run")
    if report.get("memory_report_only") is not True:
        errors.append("Alhambra scripted-effect/cleanup source generator interface must be memory/report-only")
    if report.get("output_kind") != "source_file_contract_artifacts":
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface output_kind must be "
            "source_file_contract_artifacts"
        )
    if report.get("output_is_loadable_source") is not False:
        errors.append("Alhambra scripted-effect/cleanup source generator interface output must not be loadable source")
    if report.get("source_generator_contract_input_only") is not True:
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface must derive from source generator contract input"
        )
    if report.get("source_file_validation_evidence_input_only") is not True:
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface must derive from source-file validation evidence input"
        )
    if report.get("source_generator_contract_validation_errors"):
        errors.append("Alhambra scripted-effect/cleanup source generator interface source generator contract input must be clean")
    if report.get("source_file_validation_evidence_validation_errors"):
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface source-file validation evidence input must be clean"
        )

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface must not claim "
            f"source_ready/verified/backend_ready at {path}"
        )
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(
                f"Alhambra scripted-effect/cleanup source generator interface {flag} must be false at {path}"
            )
    _validate_alhambra_source_body_candidate_flags(
        context="Alhambra scripted-effect/cleanup source generator interface report",
        value=report,
        errors=errors,
    )

    if source_file_validation_evidence is None:
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface requires external source-file validation evidence"
        )
        external_pack: dict[str, Any] = {}
    else:
        evidence_errors = validate_repeated_entity_row_alhambra_source_file_validation_evidence(
            source_file_validation_evidence
        )
        if evidence_errors:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface external source-file validation evidence must be clean"
            )
        expected_evidence_input_ref = {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        }
        if report.get("source_file_validation_evidence_input_ref") != expected_evidence_input_ref:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface source-file validation evidence input ref mismatch"
            )
        external_pack = next(
            (
                pack
                for pack in source_file_validation_evidence.get("evidence_packs", []) or []
                if isinstance(pack, dict) and pack.get("target_path") == target_path
            ),
            {},
        )
        if not external_pack:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface missing external scripted-effect/cleanup source-file validation pack"
            )
        elif list(external_pack.get("families", []) or []) != expected_target_families:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface external validation evidence families mismatch"
            )

    if source_generator_contract is None:
        errors.append("Alhambra scripted-effect/cleanup source generator interface requires source generator contract input")
        expected_contract: dict[str, Any] = {}
        source_generator_contract_ref: dict[str, Any] = {}
    else:
        contract_errors = validate_repeated_entity_row_alhambra_source_generator_contract(
            source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if contract_errors:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface source generator contract input must bind cleanly"
            )
        source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
        if report.get("source_generator_contract_input_ref") != source_generator_contract_ref:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface source generator contract input ref mismatch"
            )
        expected_contract = (
            _alhambra_source_generator_contract_for_pack(external_pack)
            if external_pack
            else _alhambra_source_generator_contract_for_target(source_generator_contract, target_path)
        )
        if not expected_contract:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface missing scripted-effect/cleanup source generator contract"
            )

    expected_pack_ref = _alhambra_source_generator_contract_pack_ref(external_pack) if external_pack else {}
    expected_refs = [
        ref
        for ref in expected_contract.get("source_body_candidate_refs", []) or []
        if isinstance(ref, dict)
    ]
    expected_artifacts = [
        _alhambra_scripted_effect_cleanup_source_file_contract_artifact(
            ref=ref,
            index=index,
            contract=expected_contract,
            validation_pack=external_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for index, ref in enumerate(expected_refs)
    ] if expected_contract and external_pack else []
    expected_interface = (
        _alhambra_scripted_effect_cleanup_source_generator_interface_prototype(
            contract=expected_contract,
            validation_pack=external_pack,
            source_generator_contract_ref=source_generator_contract_ref,
        )
        if expected_contract and external_pack
        else {}
    )

    artifacts = report.get("source_file_contract_artifacts")
    if not isinstance(artifacts, list):
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface source_file_contract_artifacts must be a list"
        )
        artifacts = []
    interfaces = report.get("source_generator_interfaces")
    if not isinstance(interfaces, list):
        errors.append("Alhambra scripted-effect/cleanup source generator interface source_generator_interfaces must be a list")
        interfaces = []

    if int(report.get("interface_count", -1)) != len(interfaces):
        errors.append("Alhambra scripted-effect/cleanup source generator interface interface_count mismatch")
    if int(report.get("interface_count", -1)) != 1:
        errors.append("Alhambra scripted-effect/cleanup source generator interface interface_count must be 1")
    if int(report.get("artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra scripted-effect/cleanup source generator interface artifact_count mismatch")
    if int(report.get("source_file_contract_artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra scripted-effect/cleanup source generator interface artifact count mismatch")
    if int(report.get("artifact_count", -1)) != expected_artifact_count:
        errors.append("Alhambra scripted-effect/cleanup source generator interface artifact_count must be 18")
    if report.get("required_target_paths") != [target_path]:
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface required target paths must contain only scripted-effect target"
        )

    actual_family_artifact_counts = _count_by_key(artifacts, "family")
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra scripted-effect/cleanup source generator interface summary missing")
    else:
        expected_summary = {
            "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            "family": expected_family,
            "families": expected_target_families,
            "target_path": target_path,
            "interface_count": 1,
            "source_file_contract_artifact_count": len(artifacts),
            "artifact_count": len(artifacts),
            "family_artifact_counts": actual_family_artifact_counts,
            "output_kind": "source_file_contract_artifacts",
            "source_ready_count": 0,
            "source_writer_allowed_count": 0,
            "may_write_src_count": 0,
            "writes_src_count": 0,
        }
        if summary != expected_summary:
            errors.append("Alhambra scripted-effect/cleanup source generator interface summary mismatch")

    if len(interfaces) != 1:
        errors.append("Alhambra scripted-effect/cleanup source generator interface must expose exactly one interface")
    elif interfaces and isinstance(interfaces[0], dict):
        interface = interfaces[0]
        missing = _missing_required(
            interface,
            REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface prototype missing field(s): "
                + ", ".join(missing)
            )
        elif expected_interface and interface != expected_interface:
            errors.append(
                "Alhambra scripted-effect/cleanup source generator interface prototype external validation evidence mismatch"
            )
    else:
        errors.append("Alhambra scripted-effect/cleanup source generator interface prototype must be a mapping")

    actual_ref_keys: set[tuple[str, str, str, str]] = set()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append("Alhambra scripted-effect/cleanup source generator interface artifact must be a mapping")
            continue
        context = f"Alhambra scripted-effect/cleanup source generator interface artifact {index}"
        missing = _missing_required(
            artifact,
            REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(f"{context} missing field(s): {', '.join(missing)}")
            continue
        if artifact.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append(f"{context} pilot_key must be unique_alhambra")
        if artifact.get("interface_family") != expected_family:
            errors.append(f"{context} interface_family must be scripted_effect_cleanup")
        if artifact.get("family") not in expected_target_families:
            errors.append(f"{context} family must be effect or cleanup")
        if artifact.get("target_families") != expected_target_families:
            errors.append(f"{context} target families mismatch")
        if artifact.get("target_path") != target_path:
            errors.append(f"{context} target_path mismatch")
        if artifact.get("future_source_target_path") != target_path:
            errors.append(f"{context} future_source_target_path mismatch")
        if (
            artifact.get("generator_interface_status")
            != REPEATED_ENTITY_ROW_ALHAMBRA_SCRIPTED_EFFECT_CLEANUP_SOURCE_GENERATOR_INTERFACE_STATUS
        ):
            errors.append(f"{context} generator_interface_status mismatch")
        if artifact.get("output_kind") != "source_file_contract_artifacts":
            errors.append(f"{context} output_kind must be source_file_contract_artifacts")
        if artifact.get("output_is_loadable_source") is not False:
            errors.append(f"{context} output must not be loadable source")
        if artifact.get("source_file_contract_artifact_only") is not True:
            errors.append(f"{context} must be source-file contract artifact only")
        if artifact.get("source_generator_interface_prototype_only") is not True:
            errors.append(f"{context} must be interface-prototype-only")
        if artifact.get("scripted_effect_cleanup_target_only") is not True:
            errors.append(f"{context} must be scripted-effect/cleanup-target-only")
        if artifact.get("memory_report_only") is not True:
            errors.append(f"{context} must be memory/report-only")
        if artifact.get("dry_run") is not True or artifact.get("dry_run_required") is not True:
            errors.append(f"{context} must be dry-run")
        if artifact.get("contract_only") is not True or artifact.get("candidate_only") is not True:
            errors.append(f"{context} must be contract/candidate-only")
        for flag in (
            "body_emitted",
            "source_ready",
            "verified",
            "backend_ready",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        ):
            if artifact.get(flag) is not False:
                errors.append(f"{context} {flag} must be false")
        ref = artifact.get("source_body_candidate_ref") if isinstance(artifact.get("source_body_candidate_ref"), dict) else {}
        ref_key = _alhambra_source_file_preview_ref_key(ref)
        actual_ref_keys.add(ref_key)
        if artifact.get("family") != str(ref.get("family", "")):
            errors.append(f"{context} family must match source body candidate ref")
        if artifact.get("source_body_candidate_ref_key") != _alhambra_scripted_effect_cleanup_source_body_candidate_ref_key(ref):
            errors.append(f"{context} source body candidate ref key mismatch")
        if artifact.get("source_generator_contract_ref") != source_generator_contract_ref:
            errors.append(f"{context} source generator contract ref mismatch")
        if artifact.get("source_file_validation_evidence_ref") != expected_pack_ref:
            errors.append(f"{context} source-file validation evidence ref mismatch")
        if expected_artifacts and index < len(expected_artifacts) and artifact != expected_artifacts[index]:
            errors.append(f"{context} external validation evidence mismatch")

    expected_ref_keys = {
        _alhambra_source_file_preview_ref_key(ref)
        for ref in expected_refs
    }
    if actual_ref_keys != expected_ref_keys:
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface source body refs external validation evidence mismatch"
        )
    if len(actual_ref_keys) != expected_artifact_count:
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface expected 18 unique source file contract "
            f"artifacts, got {len(actual_ref_keys)}"
        )
    expected_family_artifact_counts = _count_by_key(expected_refs, "family")
    if expected_refs and actual_family_artifact_counts != expected_family_artifact_counts:
        errors.append(
            "Alhambra scripted-effect/cleanup source generator interface family counts external validation evidence mismatch"
        )
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra scripted-effect/cleanup source generator interface {count_key} must be 0")
    return errors


def validate_repeated_entity_row_alhambra_localization_source_generator_interface(
    report: dict[str, Any],
    *,
    source_generator_contract: dict[str, Any] | None = None,
    source_file_validation_evidence: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    target_paths = list(REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_TARGET_PATHS)
    expected_family = REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_FAMILY
    expected_artifact_count_per_target = {
        target_path: int(REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_VALIDATION_TARGET_METADATA[target_path]["artifact_count"])
        for target_path in target_paths
    }
    expected_total_artifact_count = sum(expected_artifact_count_per_target.values())
    localization_targets = REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_FILE_PREVIEW_LOCALIZATION_TARGET_PATHS
    expected_language_by_target = {
        target_path: language
        for language, target_path in localization_targets.items()
    }

    if report.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
        errors.append("Alhambra localization source generator interface pilot_key must be unique_alhambra")
    if report.get("family") != expected_family:
        errors.append("Alhambra localization source generator interface family must be localization")
    if report.get("target_paths") != target_paths:
        errors.append("Alhambra localization source generator interface target_paths mismatch")
    if report.get("required_target_paths") != target_paths:
        errors.append("Alhambra localization source generator interface required target paths must stay language split")
    if report.get("localization_target_paths") != localization_targets:
        errors.append("Alhambra localization source generator interface localization target paths must stay split")
    if report.get("source_generator_interface_prototype_only") is not True:
        errors.append("Alhambra localization source generator interface must declare prototype-only")
    if report.get("localization_family_only") is not True:
        errors.append("Alhambra localization source generator interface must be localization-family-only")
    if report.get("dry_run") is not True or report.get("dry_run_required") is not True:
        errors.append("Alhambra localization source generator interface must be dry-run")
    if report.get("memory_report_only") is not True:
        errors.append("Alhambra localization source generator interface must be memory/report-only")
    if report.get("output_kind") != "source_file_contract_artifacts":
        errors.append(
            "Alhambra localization source generator interface output_kind must be source_file_contract_artifacts"
        )
    if report.get("output_is_loadable_source") is not False:
        errors.append("Alhambra localization source generator interface output must not be loadable source")
    if report.get("source_generator_contract_input_only") is not True:
        errors.append("Alhambra localization source generator interface must derive from source generator contract input")
    if report.get("source_file_validation_evidence_input_only") is not True:
        errors.append(
            "Alhambra localization source generator interface must derive from source-file validation evidence input"
        )
    if report.get("source_generator_contract_validation_errors"):
        errors.append("Alhambra localization source generator interface source generator contract input must be clean")
    if report.get("source_file_validation_evidence_validation_errors"):
        errors.append(
            "Alhambra localization source generator interface source-file validation evidence input must be clean"
        )

    for path in _source_bundle_forbidden_ready_paths(report):
        errors.append(
            "Alhambra localization source generator interface must not claim "
            f"source_ready/verified/backend_ready at {path}"
        )
    for flag in ("may_write_src", "writes_src", "source_writer_allowed"):
        for path in _source_bundle_true_flag_paths(report, flag):
            errors.append(f"Alhambra localization source generator interface {flag} must be false at {path}")
    _validate_alhambra_source_body_candidate_flags(
        context="Alhambra localization source generator interface report",
        value=report,
        errors=errors,
    )

    external_packs_by_target: dict[str, dict[str, Any]] = {}
    if source_file_validation_evidence is None:
        errors.append(
            "Alhambra localization source generator interface requires external source-file validation evidence"
        )
    else:
        evidence_errors = validate_repeated_entity_row_alhambra_source_file_validation_evidence(
            source_file_validation_evidence
        )
        if evidence_errors:
            errors.append(
                "Alhambra localization source generator interface external source-file validation evidence must be clean"
            )
        expected_evidence_input_ref = {
            "pilot_key": str(source_file_validation_evidence.get("pilot_key", "")),
            "evidence_pack_count": int(source_file_validation_evidence.get("evidence_pack_count", 0)),
            "artifact_count": int(source_file_validation_evidence.get("artifact_count", 0)),
            "source_body_candidate_ref_count": int(
                source_file_validation_evidence.get("source_body_candidate_ref_count", 0)
            ),
            "validation_errors": list(source_file_validation_evidence.get("validation_errors", []) or []),
        }
        if report.get("source_file_validation_evidence_input_ref") != expected_evidence_input_ref:
            errors.append(
                "Alhambra localization source generator interface source-file validation evidence input ref mismatch"
            )
        for pack in source_file_validation_evidence.get("evidence_packs", []) or []:
            if isinstance(pack, dict) and pack.get("target_path") in target_paths:
                target_path = str(pack.get("target_path", ""))
                if target_path in external_packs_by_target:
                    errors.append(
                        "Alhambra localization source generator interface duplicate external source-file "
                        f"validation pack for {target_path}"
                    )
                external_packs_by_target[target_path] = pack
        for target_path in target_paths:
            pack = external_packs_by_target.get(target_path, {})
            if not pack:
                errors.append(
                    "Alhambra localization source generator interface missing external localization "
                    f"source-file validation pack for {target_path}"
                )
                continue
            if list(pack.get("families", []) or []) != [expected_family]:
                errors.append(
                    "Alhambra localization source generator interface external validation evidence families mismatch"
                )
            language = str(pack.get("localization_language", ""))
            if expected_language_by_target.get(target_path) != language:
                errors.append(
                    "Alhambra localization source generator interface external validation evidence language mismatch"
                )

    source_generator_contract_ref: dict[str, Any] = {}
    expected_contracts_by_target: dict[str, dict[str, Any]] = {}
    if source_generator_contract is None:
        errors.append("Alhambra localization source generator interface requires source generator contract input")
    else:
        contract_errors = validate_repeated_entity_row_alhambra_source_generator_contract(
            source_generator_contract,
            source_file_validation_evidence=source_file_validation_evidence,
        )
        if contract_errors:
            errors.append(
                "Alhambra localization source generator interface source generator contract input must bind cleanly"
            )
        source_generator_contract_ref = _alhambra_source_generator_contract_report_ref(source_generator_contract)
        if report.get("source_generator_contract_input_ref") != source_generator_contract_ref:
            errors.append(
                "Alhambra localization source generator interface source generator contract input ref mismatch"
            )

    for target_path in target_paths:
        external_pack = external_packs_by_target.get(target_path, {})
        if external_pack:
            expected_contracts_by_target[target_path] = _alhambra_source_generator_contract_for_pack(external_pack)
        elif source_generator_contract is not None:
            expected_contracts_by_target[target_path] = _alhambra_source_generator_contract_for_target(
                source_generator_contract,
                target_path,
            )
        if not expected_contracts_by_target.get(target_path):
            errors.append(
                "Alhambra localization source generator interface missing localization source generator contract "
                f"for {target_path}"
            )

    expected_interfaces = [
        _alhambra_localization_source_generator_interface_prototype(
            contract=expected_contracts_by_target[target_path],
            validation_pack=external_packs_by_target[target_path],
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for target_path in target_paths
        if target_path in expected_contracts_by_target and target_path in external_packs_by_target
    ]
    expected_artifacts = [
        _alhambra_localization_source_file_contract_artifact(
            ref=ref,
            index=index,
            contract=expected_contracts_by_target[target_path],
            validation_pack=external_packs_by_target[target_path],
            source_generator_contract_ref=source_generator_contract_ref,
        )
        for target_path in target_paths
        if target_path in expected_contracts_by_target and target_path in external_packs_by_target
        for index, ref in enumerate(
            [
                ref
                for ref in expected_contracts_by_target[target_path].get("source_body_candidate_refs", []) or []
                if isinstance(ref, dict)
            ]
        )
    ]

    artifacts = report.get("source_file_contract_artifacts")
    if not isinstance(artifacts, list):
        errors.append(
            "Alhambra localization source generator interface source_file_contract_artifacts must be a list"
        )
        artifacts = []
    interfaces = report.get("source_generator_interfaces")
    if not isinstance(interfaces, list):
        errors.append(
            "Alhambra localization source generator interface source_generator_interfaces must be a list"
        )
        interfaces = []

    if int(report.get("interface_count", -1)) != len(interfaces):
        errors.append("Alhambra localization source generator interface interface_count mismatch")
    if int(report.get("interface_count", -1)) != len(target_paths):
        errors.append("Alhambra localization source generator interface interface_count must be 2")
    if int(report.get("artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra localization source generator interface artifact_count mismatch")
    if int(report.get("source_file_contract_artifact_count", -1)) != len(artifacts):
        errors.append("Alhambra localization source generator interface artifact count mismatch")
    if int(report.get("artifact_count", -1)) != expected_total_artifact_count:
        errors.append("Alhambra localization source generator interface artifact_count must be 20")

    actual_target_artifact_counts = _count_by_key(artifacts, "target_path")
    actual_language_artifact_counts = _count_by_key(artifacts, "localization_language")
    if report.get("target_artifact_counts") != actual_target_artifact_counts:
        errors.append("Alhambra localization source generator interface target artifact counts mismatch")
    if report.get("language_artifact_counts") != actual_language_artifact_counts:
        errors.append("Alhambra localization source generator interface language artifact counts mismatch")
    for target_path, expected_count in expected_artifact_count_per_target.items():
        if actual_target_artifact_counts.get(target_path) != expected_count:
            errors.append(
                "Alhambra localization source generator interface must emit 10 report-only artifacts per target"
            )
    for language in REPEATED_ENTITY_ROW_SOURCE_PREVIEW_LANGUAGE_KEYS:
        target_path = localization_targets[language]
        if actual_language_artifact_counts.get(language) != expected_artifact_count_per_target[target_path]:
            errors.append(
                "Alhambra localization source generator interface must emit 10 report-only artifacts per language"
            )

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    if not summary:
        errors.append("Alhambra localization source generator interface summary missing")
    else:
        expected_summary = {
            "pilot_key": REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT,
            "family": expected_family,
            "target_paths": target_paths,
            "interface_count": len(target_paths),
            "source_file_contract_artifact_count": len(artifacts),
            "artifact_count": len(artifacts),
            "target_artifact_counts": actual_target_artifact_counts,
            "language_artifact_counts": actual_language_artifact_counts,
            "output_kind": "source_file_contract_artifacts",
            "source_ready_count": 0,
            "source_writer_allowed_count": 0,
            "may_write_src_count": 0,
            "writes_src_count": 0,
        }
        if summary != expected_summary:
            errors.append("Alhambra localization source generator interface summary mismatch")

    if len(interfaces) != len(target_paths):
        errors.append("Alhambra localization source generator interface must expose one interface per language target")
    elif expected_interfaces and interfaces != expected_interfaces:
        errors.append(
            "Alhambra localization source generator interface prototype external validation evidence mismatch"
        )
    for index, interface in enumerate(interfaces):
        if not isinstance(interface, dict):
            errors.append("Alhambra localization source generator interface prototype must be a mapping")
            continue
        context = f"Alhambra localization source generator interface prototype {index}"
        missing = _missing_required(
            interface,
            REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(f"{context} missing field(s): {', '.join(missing)}")
            continue
        target_path = str(interface.get("target_path", ""))
        language = str(interface.get("localization_language", ""))
        if target_path not in target_paths:
            errors.append(f"{context} unexpected target path")
        if expected_language_by_target.get(target_path) != language:
            errors.append(f"{context} localization language mismatch")
        if interface.get("family") != expected_family:
            errors.append(f"{context} family must be localization")
        if interface.get("localization_family_only") is not True:
            errors.append(f"{context} must be localization-family-only")
        if interface.get("source_file_validation_evidence_ref") != (
            _alhambra_source_generator_contract_pack_ref(external_packs_by_target.get(target_path, {}))
            if external_packs_by_target.get(target_path)
            else {}
        ):
            errors.append(f"{context} source-file validation evidence ref mismatch")
        _validate_alhambra_source_file_preview_localization_boundary(
            context=context,
            boundary=interface.get("localization_language_boundary"),
            language=language,
            target_path=target_path,
            errors=errors,
        )

    actual_artifact_keys_by_target: dict[str, set[tuple[str, str, str, str]]] = {
        target_path: set()
        for target_path in target_paths
    }
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            errors.append("Alhambra localization source generator interface artifact must be a mapping")
            continue
        context = f"Alhambra localization source generator interface artifact {index}"
        missing = _missing_required(
            artifact,
            REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_FILE_CONTRACT_ARTIFACT_REQUIRED_FIELDS,
        )
        if missing:
            errors.append(f"{context} missing field(s): {', '.join(missing)}")
            continue
        target_path = str(artifact.get("target_path", ""))
        language = str(artifact.get("localization_language", ""))
        if target_path not in target_paths:
            errors.append(f"{context} unexpected target_path")
        if expected_language_by_target.get(target_path) != language:
            errors.append(f"{context} localization language mismatch")
        if artifact.get("pilot_key") != REPEATED_ENTITY_ROW_ALHAMBRA_SOURCE_BODY_CANDIDATE_PILOT:
            errors.append(f"{context} pilot_key must be unique_alhambra")
        if artifact.get("family") != expected_family:
            errors.append(f"{context} family must be localization")
        if artifact.get("future_source_target_path") != target_path:
            errors.append(f"{context} future_source_target_path must match language target")
        if (
            artifact.get("generator_interface_status")
            != REPEATED_ENTITY_ROW_ALHAMBRA_LOCALIZATION_SOURCE_GENERATOR_INTERFACE_STATUS
        ):
            errors.append(f"{context} generator_interface_status mismatch")
        if artifact.get("output_kind") != "source_file_contract_artifacts":
            errors.append(f"{context} output_kind must be source_file_contract_artifacts")
        if artifact.get("output_is_loadable_source") is not False:
            errors.append(f"{context} output must not be loadable source")
        if artifact.get("source_file_contract_artifact_only") is not True:
            errors.append(f"{context} must be source-file contract artifact only")
        if artifact.get("source_generator_interface_prototype_only") is not True:
            errors.append(f"{context} must be interface-prototype-only")
        if artifact.get("localization_family_only") is not True:
            errors.append(f"{context} must be localization-family-only")
        if artifact.get("memory_report_only") is not True:
            errors.append(f"{context} must be memory/report-only")
        if artifact.get("dry_run") is not True or artifact.get("dry_run_required") is not True:
            errors.append(f"{context} must be dry-run")
        if artifact.get("contract_only") is not True or artifact.get("candidate_only") is not True:
            errors.append(f"{context} must be contract/candidate-only")
        for flag in (
            "body_emitted",
            "source_ready",
            "verified",
            "backend_ready",
            "source_writer_allowed",
            "may_write_src",
            "writes_src",
        ):
            if artifact.get(flag) is not False:
                errors.append(f"{context} {flag} must be false")
        ref = (
            artifact.get("source_body_candidate_ref")
            if isinstance(artifact.get("source_body_candidate_ref"), dict)
            else {}
        )
        ref_key = _alhambra_source_file_preview_ref_key(ref)
        if target_path in actual_artifact_keys_by_target:
            actual_artifact_keys_by_target[target_path].add(ref_key)
        if artifact.get("source_candidate_future_target_path") != str(ref.get("future_source_target_path", "")):
            errors.append(f"{context} source candidate future target path mismatch")
        if artifact.get("source_body_candidate_ref_key") != _alhambra_localization_source_body_candidate_ref_key(ref):
            errors.append(f"{context} source body candidate ref key mismatch")
        if artifact.get("source_generator_contract_ref") != source_generator_contract_ref:
            errors.append(f"{context} source generator contract ref mismatch")
        expected_pack_ref = (
            _alhambra_source_generator_contract_pack_ref(external_packs_by_target.get(target_path, {}))
            if external_packs_by_target.get(target_path)
            else {}
        )
        if artifact.get("source_file_validation_evidence_ref") != expected_pack_ref:
            errors.append(f"{context} source-file validation evidence ref mismatch")
        expected_contract = expected_contracts_by_target.get(target_path, {})
        if expected_contract:
            if artifact.get("source_body_candidate_ref_provenance") != expected_contract.get(
                "source_body_candidate_ref_provenance"
            ):
                errors.append(f"{context} source body candidate ref provenance mismatch")
            if artifact.get("no_write_source_writer_contract_evidence") != expected_contract.get(
                "no_write_source_writer_contract_evidence"
            ):
                errors.append(f"{context} no-write source writer evidence mismatch")
        _validate_alhambra_source_file_preview_localization_boundary(
            context=context,
            boundary=artifact.get("localization_language_boundary"),
            language=language,
            target_path=target_path,
            errors=errors,
        )
        if expected_artifacts and index < len(expected_artifacts) and artifact != expected_artifacts[index]:
            errors.append(f"{context} external validation evidence mismatch")

    for target_path in target_paths:
        expected_refs = [
            ref
            for ref in expected_contracts_by_target.get(target_path, {}).get("source_body_candidate_refs", []) or []
            if isinstance(ref, dict)
        ]
        expected_ref_keys = {
            _alhambra_source_file_preview_ref_key(ref)
            for ref in expected_refs
        }
        actual_ref_keys = actual_artifact_keys_by_target.get(target_path, set())
        if actual_ref_keys != expected_ref_keys:
            errors.append(
                "Alhambra localization source generator interface source body refs external validation evidence "
                f"mismatch for {target_path}"
            )
        expected_count = expected_artifact_count_per_target[target_path]
        if len(actual_ref_keys) != expected_count:
            errors.append(
                "Alhambra localization source generator interface expected 10 unique source file contract "
                f"artifacts for {target_path}, got {len(actual_ref_keys)}"
            )
    if expected_artifacts and artifacts != expected_artifacts:
        errors.append("Alhambra localization source generator interface artifacts external validation evidence mismatch")
    for count_key in (
        "source_ready_count",
        "source_writer_allowed_count",
        "may_write_src_count",
        "writes_src_count",
    ):
        if int(report.get(count_key, -1)) != 0:
            errors.append(f"Alhambra localization source generator interface {count_key} must be 0")
    return errors


def _design_matrix_index(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = matrix.get("unique_wonders", []) if isinstance(matrix, dict) else []
    return {
        str(entry["wonder_key"]): entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("wonder_key")
    }


def _lower_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_lower_text(child) for child in value.values())
    if isinstance(value, list):
        return " ".join(_lower_text(child) for child in value)
    return str(value or "").lower()


def _tracked_entity_type_tokens(entry: dict[str, Any]) -> set[str]:
    design_ir = entry.get("design_ir")
    if not isinstance(design_ir, dict):
        return set()
    tokens: set[str] = set()
    for tracked in design_ir.get("tracked_entity_sets", []) or []:
        if not isinstance(tracked, dict):
            continue
        for field in ("key", "entity_type"):
            tokens.add(_lower_text(tracked.get(field)))
    return set(" ".join(tokens).split())


def _design_ir_projection_notes(entry: dict[str, Any]) -> str:
    design_ir = entry.get("design_ir")
    if not isinstance(design_ir, dict):
        return ""
    return _lower_text(design_ir.get("projection_notes"))


PROJECTION_STRATEGY_TOKENS = {
    "compress",
    "compression",
    "flatten",
    "preserve",
    "projection",
    "replace",
    "retain",
    "summarize",
}


def _projection_strategy_text(entry: dict[str, Any]) -> str:
    node_graph = entry.get("node_graph") if isinstance(entry.get("node_graph"), dict) else {}
    return _lower_text(
        [
            _design_ir_projection_notes(entry),
            node_graph.get("projection_notes"),
            node_graph.get("summary"),
            node_graph.get("graph_shape"),
            node_graph.get("mechanic_signature"),
        ]
    )


def _has_projection_strategy(value: str) -> bool:
    return any(token in value for token in PROJECTION_STRATEGY_TOKENS)


def _tracked_named_entity_count(design_ir: dict[str, Any]) -> int:
    count = 0
    for tracked in design_ir.get("tracked_entity_sets", []) or []:
        if not isinstance(tracked, dict):
            continue
        entities = tracked.get("entities")
        if not isinstance(entities, list):
            continue
        for entity in entities:
            if isinstance(entity, dict) and any(entity.get(field) for field in ("key", "display_name", "name")):
                count += 1
            elif isinstance(entity, str) and entity.strip():
                count += 1
    return count


def _has_nested_key(value: Any, keys: set[str]) -> bool:
    if isinstance(value, dict):
        return any(str(key) in keys or _has_nested_key(child, keys) for key, child in value.items())
    if isinstance(value, list):
        return any(_has_nested_key(child, keys) for child in value)
    return False


def _ui_model_declares_repeated_or_per_entity_status(ui_model: Any) -> bool:
    if _has_nested_key(ui_model, {"repeated_rows", "per_entity_status"}):
        return True
    text = _lower_text(ui_model)
    if "repeated" in text and "rows" in text:
        return True
    return any(
        token in text
        for token in (
            "repeated row",
            "repeated rows",
            "per-entity status",
            "per entity status",
            "one row per",
        )
    )


def _matrix_entry_expects_named_routes(matrix_entry: dict[str, Any]) -> bool:
    ui_values = set(_string_refs(matrix_entry.get("expected_ui_model")))
    text = _lower_text(
        [
            matrix_entry.get("proposed_core_mechanic"),
            matrix_entry.get("player_agency_model"),
            matrix_entry.get("risk_or_failure_branch"),
            matrix_entry.get("uniqueness_notes"),
            matrix_entry.get("primary_cadence_type"),
            matrix_entry.get("secondary_cadence_type"),
        ]
    )
    return "route_map" in ui_values and any(token in text for token in ("route", "lane", "convoy", "mediterranean"))


def anti_flattening_warnings_for_payload(
    payload: dict[str, Any],
    *,
    design_matrix: dict[str, Any] | None = None,
) -> list[str]:
    matrix = design_matrix if design_matrix is not None else load_optional_yaml(DESIGN_MATRIX_FILE)
    matrix_by_key = _design_matrix_index(matrix)
    warnings: list[str] = []
    for entry in payload.get("unique_wonders", []) or []:
        if not isinstance(entry, dict):
            continue
        identity = entry.get("identity") or {}
        key = str(identity.get("key", ""))
        status = str(identity.get("status", ""))
        if not key or status in STUB_STATUSES:
            continue
        matrix_entry = matrix_by_key.get(key)
        design_ir = entry.get("design_ir") if isinstance(entry.get("design_ir"), dict) else None
        tracked_tokens = _tracked_entity_type_tokens(entry)
        if matrix_entry and _matrix_entry_expects_named_routes(matrix_entry) and "route" not in tracked_tokens:
            warnings.append(f"{key}: matrix expects route_map/named routes, but design_ir does not declare a tracked route set")
        if matrix_entry and _has_content(matrix_entry.get("risk_or_failure_branch")):
            if design_ir is not None and not _has_content(design_ir.get("risk_branches")):
                warnings.append(f"{key}: matrix risk_or_failure_branch exists, but design_ir.risk_branches is empty")
        notes = _lower_text((matrix_entry or {}).get("uniqueness_notes"))
        specific_terms = {
            "mediterranean": "route",
            "sea lane": "route",
            "public debt": "debt",
            "pledge": "pledge",
            "manuscript": "manuscript",
            "teacher network": "teacher",
        }
        if design_ir is not None:
            design_text = _lower_text(design_ir)
            missing_specific = [
                source
                for source, expected in specific_terms.items()
                if source in notes and expected not in design_text
            ]
            if missing_specific:
                warnings.append(
                    f"{key}: uniqueness_notes mention {', '.join(missing_specific)}, but design_ir does not preserve that interface"
                )
            named_entity_count = _tracked_named_entity_count(design_ir)
            if named_entity_count > 5 and not _has_projection_strategy(_projection_strategy_text(entry)):
                warnings.append(
                    f"{key}: design_ir.tracked_entity_sets declares {named_entity_count} named entities, but projection_notes/node_graph do not explain projection strategy"
                )
            if _ui_model_declares_repeated_or_per_entity_status(design_ir.get("ui_feedback_model")):
                projection_notes = _design_ir_projection_notes(entry)
                if not any(token in projection_notes for token in ("row", "rows", "status", "projection", "compress", "compression")):
                    warnings.append(
                        f"{key}: design_ir.ui_feedback_model declares repeated rows or per-entity status, but projection_notes do not explain row/status projection"
                    )
        implementation_notes = entry.get("implementation_notes") or {}
        has_manual_evidence = str(implementation_notes.get("implementation_source", "")).strip() not in {"", "none"}
        node_graph = entry.get("node_graph") or {}
        has_runtime_or_nodes = _has_content(node_graph.get("runtime_variables")) or _has_content(node_graph.get("nodes"))
        if design_ir is not None and has_manual_evidence and has_runtime_or_nodes:
            projection_notes = _design_ir_projection_notes(entry)
            if not any(
                token in projection_notes
                for token in ("preserve", "retain", "replace", "drop", "abandon", "compress", "flatten", "projection", "manual")
            ):
                warnings.append(
                    f"{key}: manual implementation evidence exists, but design_ir.projection_notes does not explain preservation/projection"
                )
    return warnings


def _contract_error_count(errors: list[str], contract_name: str) -> int:
    return sum(1 for error in errors if contract_name in error)


def validate_spec_payload(
    payload: dict[str, Any],
    *,
    wonders: list[dict[str, Any]] | None = None,
    localization: dict[str, str] | None = None,
    occupied_event_ids: set[int] | None = None,
    require_all_wonders: bool = True,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_template_registry(template_registry) if template_registry is not None else validate_template_registry())
    errors.extend(
        validate_capability_registry(capability_registry)
        if capability_registry is not None
        else validate_capability_registry()
    )
    errors.extend(
        validate_archetype_registry(archetype_registry, capability_registry=capability_registry)
        if archetype_registry is not None
        else validate_archetype_registry(capability_registry=capability_registry)
    )
    wonders = wonders if wonders is not None else load_unique_wonders()
    wonder_by_key = wonder_index(wonders)
    entries = payload.get("unique_wonders", []) or []
    if not isinstance(entries, list):
        return ["unique_wonders must be a list"]

    seen_keys: set[str] = set()
    seen_event_ids: dict[int, str] = {}
    loc = localization if localization is not None else loc_english()
    loc_keys = loc_key_inventory(localization)

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("unique_wonders entries must be mappings")
            continue
        identity = entry.get("identity", {})
        if not isinstance(identity, dict):
            errors.append("entry identity must be a mapping")
            continue
        key = str(identity.get("key", ""))
        if not key:
            errors.append("entry identity.key is required")
            continue
        if key in seen_keys:
            errors.append(f"{key}: duplicate spec entry")
            continue
        seen_keys.add(key)

        wonder = wonder_by_key.get(key)
        if wonder is None:
            errors.append(f"{key}: not present in data/unique_wonders.yaml")
            continue
        for field in ("id", "base_key", "location"):
            if identity.get(field) != wonder.get(field):
                errors.append(_issue(entry, f"identity.{field} must match data/unique_wonders.yaml"))
        status = str(identity.get("status", ""))
        if status not in ALLOWED_STATUSES:
            errors.append(_issue(entry, f"identity.status '{status}' is unsupported"))
            continue

        requires_design_ir = _is_status_requiring_design_ir(status)
        errors.extend(_validate_design_ir(entry, required=requires_design_ir))
        errors.extend(
            _validate_compiler_gap_ledger(
                entry,
                required=requires_design_ir,
                template_registry=template_registry,
                capability_registry=capability_registry,
            )
        )
        unresolved_gaps = unresolved_compiler_gap_rows(entry)
        if status in CODEGEN_ELIGIBLE_STATUSES and unresolved_gaps:
            primitives = ", ".join(str(row.get("primitive", "<unknown>")) for row in unresolved_gaps)
            errors.append(_issue(entry, f"source-codegen-ready status has unresolved compiler gap(s): {primitives}"))
        if status in CODEGEN_ELIGIBLE_STATUSES:
            ledger = entry.get("compiler_gap_ledger", [])
            non_backend_ready = [
                row
                for row in ledger
                if isinstance(row, dict) and row.get("verification_status") != "backend_ready"
            ]
            if non_backend_ready:
                primitives = ", ".join(str(row.get("primitive", "<unknown>")) for row in non_backend_ready)
                errors.append(_issue(entry, f"source-codegen-ready status has compiler gap row(s) not backend_ready: {primitives}"))

        entry_event_ids = event_ids_in_entry(entry)
        for event_id in entry_event_ids:
            if event_id <= 0:
                errors.append(_issue(entry, f"event id {event_id} must be positive"))
            if event_id >= 10000:
                errors.append(_issue(entry, f"event id {event_id} must be < 10000"))
            if event_id in seen_event_ids:
                errors.append(_issue(entry, f"event id {event_id} duplicates {seen_event_ids[event_id]}"))
            seen_event_ids[event_id] = key
            if occupied_event_ids is not None and status in CODEGEN_ELIGIBLE_STATUSES and event_id in occupied_event_ids:
                errors.append(_issue(entry, f"event id {event_id} collides with an occupied Engineering Department event id"))

        node_graph = entry.get("node_graph", {})
        if not isinstance(node_graph, dict):
            errors.append(_issue(entry, "node_graph must be a mapping"))
            node_graph = {}
        archetypes = node_graph.get("archetypes")
        if archetypes is not None:
            if not isinstance(archetypes, list):
                errors.append(_issue(entry, "node_graph.archetypes must be a list"))
            else:
                archetype_index = archetype_registry_index(archetype_registry)
                for archetype in _string_refs(archetypes):
                    if archetype not in archetype_index and not _is_custom_archetype(archetype):
                        errors.append(_issue(entry, f"node_graph.archetypes unknown archetype {archetype!r}"))
        listeners = node_graph.get("listeners", [])
        if listeners is None:
            listeners = []
        if not isinstance(listeners, list):
            errors.append(_issue(entry, "node_graph.listeners must be a list"))
        else:
            for listener in listeners:
                if listener not in SUPPORTED_LISTENERS:
                    errors.append(_issue(entry, f"unsupported listener {listener!r}"))

        if status not in IMPLEMENTED_STATUSES:
            continue

        nodes = node_graph.get("nodes", []) if isinstance(node_graph, dict) else []
        if not isinstance(nodes, list):
            errors.append(_issue(entry, "node_graph.nodes must be a list"))
            continue
        entry_event_id_set = set(entry_event_ids)
        visible_nodes = [node for node in nodes if isinstance(node, dict) and node.get("player_visible")]
        if len(visible_nodes) < 3:
            errors.append(_issue(entry, "needs at least 3 player-visible ritual nodes"))
        if len(entry_event_ids) < 3:
            errors.append(_issue(entry, "needs at least 3 explicit event ids"))
        if not any(isinstance(node, dict) and node.get("failure_or_retry") for node in nodes):
            errors.append(_issue(entry, "needs at least one failure/retry path"))
        if not str(node_graph.get("historical_mechanic", "")).strip():
            errors.append(_issue(entry, "node_graph.historical_mechanic is required"))
        if status in SEMANTIC_GRAPH_STATUSES:
            errors.extend(
                _validate_codegen_node_graph(
                    entry,
                    node_graph,
                    entry_event_id_set,
                    loc_keys,
                    template_registry,
                    capability_registry,
                    archetype_registry,
                    require_generation=status in CODEGEN_ELIGIBLE_STATUSES,
                )
            )
            errors.extend(validate_codegen_ui_bindings(entry, localization=localization))
        else:
            for node in nodes:
                if not isinstance(node, dict) or "event_id" not in node:
                    continue
                if int(node["event_id"]) not in entry_event_id_set:
                    errors.append(_issue(entry, f"node {node.get('key', '<unknown>')} references undeclared event id {node['event_id']}"))

        runtime_prefix = str(identity.get("runtime_prefix", ""))
        runtime_variables = declared_runtime_variables(entry)
        for variable in runtime_variables:
            if not str(variable).startswith(runtime_prefix):
                errors.append(_issue(entry, f"runtime variable {variable} must start with {runtime_prefix}"))

        components = ((entry.get("ui_model") or {}).get("components") or [])
        if not components:
            errors.append(_issue(entry, "ui_model.components must not be empty"))
        for component in components:
            ctype = component.get("type") if isinstance(component, dict) else None
            if ctype not in SUPPORTED_UI_COMPONENTS:
                errors.append(_issue(entry, f"unsupported ui component type {ctype!r}"))
            if isinstance(component, dict):
                for field in UI_VARIABLE_FIELDS:
                    variable = component.get(field)
                    if variable and str(variable) not in runtime_variables:
                        errors.append(_issue(entry, f"ui component {component.get('key', ctype)} uses undeclared runtime variable {variable}"))

        rewards = entry.get("rewards", {})
        for channel in REQUIRED_REWARD_CHANNELS:
            reward = rewards.get(channel) if isinstance(rewards, dict) else None
            if not isinstance(reward, dict) or reward.get("status") in {None, "pending"}:
                errors.append(_issue(entry, f"reward channel {channel} is missing or pending"))

        loc_event_rows = ((entry.get("localization") or {}).get("event_keys") or [])
        if len(loc_event_rows) < 3:
            errors.append(_issue(entry, "localization.event_keys needs at least 3 event rows"))
        desc_chars = 0
        for row in loc_event_rows:
            if not isinstance(row, dict):
                continue
            for loc_key in [row.get("title_key"), row.get("desc_key"), *(row.get("option_keys") or [])]:
                if loc_key and loc_key not in loc_keys:
                    errors.append(_issue(entry, f"missing English localization key {loc_key}"))
            desc_key = row.get("desc_key")
            if desc_key in loc:
                desc_chars += len(str(loc[desc_key]))
            row_event_id = row.get("event_id")
            if row_event_id is not None:
                try:
                    normalized_row_event_id = int(row_event_id)
                except (TypeError, ValueError):
                    errors.append(_issue(entry, f"localization row has invalid event id {row_event_id!r}"))
                else:
                    if normalized_row_event_id not in entry_event_id_set:
                        errors.append(_issue(entry, f"localization row references undeclared event id {row_event_id}"))
        if desc_chars < 400:
            errors.append(_issue(entry, "event description text is too thin; need at least 400 English characters"))

        for note in (entry.get("implementation_notes") or {}).get("needs_verification", []) or []:
            if str(note).strip() and status in {"implementation_ready", "harness_generated"}:
                errors.append(_issue(entry, f"unverified implementation note remains: {note}"))

    if require_all_wonders:
        missing_specs = sorted(set(wonder_by_key) - seen_keys)
        extra_specs = sorted(seen_keys - set(wonder_by_key))
        if missing_specs:
            errors.append("Missing ritual spec entries: " + ", ".join(missing_specs))
        if extra_specs:
            errors.append("Unknown ritual spec entries: " + ", ".join(extra_specs))

    return errors


def validate_unique_ritual_specs_for_repo() -> list[str]:
    if not SPEC_FILE.exists():
        return [f"{SPEC_FILE.relative_to(REPO_ROOT)} is missing; run scripts/gen_unique_wonder_ritual_specs.py"]
    try:
        payload = load_spec_data()
        return validate_spec_payload(payload, occupied_event_ids=collect_occupied_engineering_event_ids())
    except Exception as exc:  # validate.py should report, not crash
        return [f"{SPEC_FILE.relative_to(REPO_ROOT)} could not be validated: {exc}"]


def audit_summary(
    *,
    wonders: list[dict[str, Any]] | None = None,
    designs: dict[str, Any] | None = None,
    design_matrix: dict[str, Any] | None = None,
    prompts: dict[str, Any] | None = None,
    specs: dict[str, Any] | None = None,
    localization: dict[str, str] | None = None,
    template_registry: dict[str, Any] | None = None,
    capability_registry: dict[str, Any] | None = None,
    archetype_registry: dict[str, Any] | None = None,
    repeated_entity_row_preflight: dict[str, Any] | None = None,
    repeated_entity_row_source_plan: dict[str, Any] | None = None,
    repeated_entity_row_source_preview: dict[str, Any] | None = None,
    repeated_entity_row_source_writer_readiness: dict[str, Any] | None = None,
    repeated_entity_row_source_bundle_preview: dict[str, Any] | None = None,
    repeated_entity_row_alhambra_source_generator_contract: dict[str, Any] | None = None,
    repeated_entity_row_alhambra_event_source_generator_interface: dict[str, Any] | None = None,
    repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface: dict[str, Any] | None = None,
    repeated_entity_row_alhambra_scripted_trigger_source_generator_interface: dict[str, Any] | None = None,
    repeated_entity_row_alhambra_localization_source_generator_interface: dict[str, Any] | None = None,
) -> dict[str, Any]:
    wonders = wonders if wonders is not None else load_unique_wonders()
    wonder_keys = {str(wonder["key"]) for wonder in wonders}
    designs = designs if designs is not None else load_optional_yaml(DESIGN_FILE)
    design_matrix = design_matrix if design_matrix is not None else load_optional_yaml(DESIGN_MATRIX_FILE)
    prompts = prompts if prompts is not None else load_optional_yaml(PROMPTS_FILE)
    specs = specs if specs is not None else load_spec_data()
    loc = localization if localization is not None else loc_english()
    template_registry = template_registry if template_registry is not None else load_template_registry()
    capability_registry = capability_registry if capability_registry is not None else load_capability_registry()
    archetype_registry = archetype_registry if archetype_registry is not None else load_archetype_registry()
    template_registry_errors = validate_template_registry(template_registry)
    capability_registry_errors = validate_capability_registry(capability_registry)
    archetype_registry_errors = validate_archetype_registry(
        archetype_registry,
        capability_registry=capability_registry,
    )

    design_index = list_index(designs)
    prompt_index = list_index(prompts)
    spec_index = list_index(specs)
    spec_errors = validate_spec_payload(
        specs,
        wonders=wonders,
        localization=loc,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    graph_validation_errors = graph_validation_errors_for_payload(
        specs,
        localization=loc,
        template_registry=template_registry,
        capability_registry=capability_registry,
        archetype_registry=archetype_registry,
    )
    lifecycle_summary = graph_lifecycle_summary_for_payload(specs)
    codegen_tier_summary = codegen_tier_summary_for_payload(specs, template_registry=template_registry)
    capability_coverage_summary = capability_coverage_summary_for_payload(specs)
    archetype_coverage_summary = archetype_coverage_summary_for_payload(specs)
    node_kind_summary = node_kind_summary_for_payload(specs)
    if repeated_entity_row_preflight is None:
        repeated_entity_row_preflight = repeated_entity_row_preflight_for_payload(specs)
    if repeated_entity_row_source_plan is None:
        repeated_entity_row_source_plan = repeated_entity_row_source_plan_for_payload(specs)
    if repeated_entity_row_source_preview is None:
        repeated_entity_row_source_preview = repeated_entity_row_source_preview_for_payload(
            specs,
            source_plan=repeated_entity_row_source_plan,
        )
    if repeated_entity_row_source_writer_readiness is None:
        repeated_entity_row_source_writer_readiness = repeated_entity_row_source_writer_readiness_for_payload(
            specs,
            source_plan=repeated_entity_row_source_plan,
            source_preview=repeated_entity_row_source_preview,
        )
    if repeated_entity_row_source_bundle_preview is None:
        repeated_entity_row_source_bundle_preview = repeated_entity_row_source_bundle_preview_for_payload(
            specs,
            source_writer_readiness=repeated_entity_row_source_writer_readiness,
        )
    alhambra_source_file_validation_evidence: dict[str, Any] | None = None
    if repeated_entity_row_alhambra_source_generator_contract is None:
        alhambra_source_body_candidate = repeated_entity_row_alhambra_source_body_candidate_for_payload(
            specs,
            source_bundle_preview=repeated_entity_row_source_bundle_preview,
        )
        alhambra_source_file_preview = repeated_entity_row_alhambra_source_file_preview_for_payload(
            specs,
            source_body_candidate=alhambra_source_body_candidate,
        )
        alhambra_source_file_validation_evidence = (
            repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
                specs,
                source_file_preview=alhambra_source_file_preview,
            )
        )
        repeated_entity_row_alhambra_source_generator_contract = (
            repeated_entity_row_alhambra_source_generator_contract_for_payload(
                specs,
                source_file_validation_evidence=alhambra_source_file_validation_evidence,
            )
        )
    if repeated_entity_row_alhambra_event_source_generator_interface is None:
        if alhambra_source_file_validation_evidence is None:
            alhambra_source_body_candidate = repeated_entity_row_alhambra_source_body_candidate_for_payload(
                specs,
                source_bundle_preview=repeated_entity_row_source_bundle_preview,
            )
            alhambra_source_file_preview = repeated_entity_row_alhambra_source_file_preview_for_payload(
                specs,
                source_body_candidate=alhambra_source_body_candidate,
            )
            alhambra_source_file_validation_evidence = (
                repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
                    specs,
                    source_file_preview=alhambra_source_file_preview,
                )
            )
        repeated_entity_row_alhambra_event_source_generator_interface = (
            repeated_entity_row_alhambra_event_source_generator_interface_for_payload(
                specs,
                source_generator_contract=repeated_entity_row_alhambra_source_generator_contract,
                source_file_validation_evidence=alhambra_source_file_validation_evidence,
            )
        )
    if repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface is None:
        if alhambra_source_file_validation_evidence is None:
            alhambra_source_body_candidate = repeated_entity_row_alhambra_source_body_candidate_for_payload(
                specs,
                source_bundle_preview=repeated_entity_row_source_bundle_preview,
            )
            alhambra_source_file_preview = repeated_entity_row_alhambra_source_file_preview_for_payload(
                specs,
                source_body_candidate=alhambra_source_body_candidate,
            )
            alhambra_source_file_validation_evidence = (
                repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
                    specs,
                    source_file_preview=alhambra_source_file_preview,
                )
            )
        repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface = (
            repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface_for_payload(
                specs,
                source_generator_contract=repeated_entity_row_alhambra_source_generator_contract,
                source_file_validation_evidence=alhambra_source_file_validation_evidence,
            )
        )
    if repeated_entity_row_alhambra_scripted_trigger_source_generator_interface is None:
        if alhambra_source_file_validation_evidence is None:
            alhambra_source_body_candidate = repeated_entity_row_alhambra_source_body_candidate_for_payload(
                specs,
                source_bundle_preview=repeated_entity_row_source_bundle_preview,
            )
            alhambra_source_file_preview = repeated_entity_row_alhambra_source_file_preview_for_payload(
                specs,
                source_body_candidate=alhambra_source_body_candidate,
            )
            alhambra_source_file_validation_evidence = (
                repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
                    specs,
                    source_file_preview=alhambra_source_file_preview,
                )
            )
        repeated_entity_row_alhambra_scripted_trigger_source_generator_interface = (
            repeated_entity_row_alhambra_scripted_trigger_source_generator_interface_for_payload(
                specs,
                source_generator_contract=repeated_entity_row_alhambra_source_generator_contract,
                source_file_validation_evidence=alhambra_source_file_validation_evidence,
            )
        )
    if repeated_entity_row_alhambra_localization_source_generator_interface is None:
        if alhambra_source_file_validation_evidence is None:
            alhambra_source_body_candidate = repeated_entity_row_alhambra_source_body_candidate_for_payload(
                specs,
                source_bundle_preview=repeated_entity_row_source_bundle_preview,
            )
            alhambra_source_file_preview = repeated_entity_row_alhambra_source_file_preview_for_payload(
                specs,
                source_body_candidate=alhambra_source_body_candidate,
            )
            alhambra_source_file_validation_evidence = (
                repeated_entity_row_alhambra_source_file_validation_evidence_for_payload(
                    specs,
                    source_file_preview=alhambra_source_file_preview,
                )
            )
        repeated_entity_row_alhambra_localization_source_generator_interface = (
            repeated_entity_row_alhambra_localization_source_generator_interface_for_payload(
                specs,
                source_generator_contract=repeated_entity_row_alhambra_source_generator_contract,
                source_file_validation_evidence=alhambra_source_file_validation_evidence,
            )
        )
    anti_flattening_warnings = anti_flattening_warnings_for_payload(
        specs,
        design_matrix=design_matrix,
    )

    implemented = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") in IMPLEMENTED_STATUSES
    ]
    implemented_parity = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") == "implemented_parity"
    ]
    design_complete = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") == "design_complete"
    ]
    compiler_mapped = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") == "compiler_mapped"
    ]
    evidence_verified = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") == "evidence_verified"
    ]
    source_codegen_ready = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") == "source_codegen_ready"
    ]
    implementation_ready = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") == "implementation_ready"
    ]
    harness_generated = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") == "harness_generated"
    ]
    stubs = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") in STUB_STATUSES
    ]
    codegen_supported: list[str] = []
    codegen_blocked: list[str] = []
    unsupported_templates: set[str] = set()
    for key, entry in spec_index.items():
        status = (entry.get("identity") or {}).get("status")
        if status not in CODEGEN_ELIGIBLE_STATUSES:
            continue
        support_errors = codegen_support_errors(
            entry,
            template_registry=template_registry,
            capability_registry=capability_registry,
            archetype_registry=archetype_registry,
        )
        unsupported_templates.update(
            template
            for template in templates_used_by_entry(entry)
            if template not in template_registry_index(template_registry)
        )
        if support_errors:
            codegen_blocked.append(key)
        else:
            codegen_supported.append(key)
    loc_missing = [
        key
        for key in sorted(wonder_keys)
        if f"tv_engineering_department.500.d_{key}" not in loc
        or f"tv_engineering_department.600.d_{key}" not in loc
    ]
    return {
        "unique_wonders": len(wonders),
        "designs": len(design_index),
        "prompts": len(prompt_index),
        "specs": len(spec_index),
        "implemented_specs": len(implemented),
        "implemented_parity_count": len(implemented_parity),
        "design_complete_count": len(design_complete),
        "compiler_mapped_count": len(compiler_mapped),
        "evidence_verified_count": len(evidence_verified),
        "source_codegen_ready_count": len(source_codegen_ready),
        "implementation_ready_count": len(implementation_ready),
        "harness_generated_count": len(harness_generated),
        "stub_specs": len(stubs),
        "codegen_supported_count": len(codegen_supported),
        "codegen_blocked_count": len(codegen_blocked),
        "codegen_tier_summary": codegen_tier_summary,
        "capability_coverage_summary": capability_coverage_summary,
        "archetype_coverage_summary": archetype_coverage_summary,
        "node_kind_summary": node_kind_summary,
        "repeated_entity_row_preflight": repeated_entity_row_preflight,
        "repeated_entity_row_source_plan": repeated_entity_row_source_plan,
        "repeated_entity_row_source_preview": repeated_entity_row_source_preview,
        "repeated_entity_row_source_writer_readiness": repeated_entity_row_source_writer_readiness,
        "repeated_entity_row_source_bundle_preview": repeated_entity_row_source_bundle_preview,
        "repeated_entity_row_alhambra_source_generator_contract": repeated_entity_row_alhambra_source_generator_contract,
        "repeated_entity_row_alhambra_event_source_generator_interface": (
            repeated_entity_row_alhambra_event_source_generator_interface
        ),
        "repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface": (
            repeated_entity_row_alhambra_scripted_effect_cleanup_source_generator_interface
        ),
        "repeated_entity_row_alhambra_scripted_trigger_source_generator_interface": (
            repeated_entity_row_alhambra_scripted_trigger_source_generator_interface
        ),
        "repeated_entity_row_alhambra_localization_source_generator_interface": (
            repeated_entity_row_alhambra_localization_source_generator_interface
        ),
        "unsupported_templates": sorted(unsupported_templates),
        "template_registry_errors": template_registry_errors,
        "capability_registry_errors": capability_registry_errors,
        "archetype_registry_errors": archetype_registry_errors,
        "graph_reachable_count": lifecycle_summary["graph_reachable_count"],
        "graph_unreachable_count": lifecycle_summary["graph_unreachable_count"],
        "lifecycle_error_count": lifecycle_summary["lifecycle_error_count"],
        "archetype_contract_error_count": _contract_error_count(spec_errors, "archetype"),
        "listener_contract_error_count": _contract_error_count(spec_errors, "listener_contract"),
        "scope_contract_error_count": _contract_error_count(spec_errors, "scope_contract"),
        "graph_validation_errors": graph_validation_errors,
        "anti_flattening_warnings": anti_flattening_warnings,
        "missing_designs": sorted(wonder_keys - set(design_index)),
        "placeholder_designs": sorted(
            key
            for key, entry in design_index.items()
            if entry.get("status") == "needs_design"
        ),
        "missing_prompts": sorted(wonder_keys - set(prompt_index)),
        "missing_specs": sorted(wonder_keys - set(spec_index)),
        "missing_finalization_or_world_news_loc": loc_missing,
        "spec_errors": spec_errors,
        "occupied_engineering_event_ids": len(collect_occupied_engineering_event_ids()),
    }
