import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts_engineering_department"))

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


def loc_simp_chinese(data: dict[str, Any] | None = None) -> dict[str, str]:
    payload = data if data is not None else load_optional_yaml(LOCALIZATION_FILE)
    return dict((payload.get("wonder_localization") or {}).get("simp_chinese") or {})


def loc_for_language(language: str, data: dict[str, Any] | None = None) -> dict[str, str]:
    if language == "english":
        return loc_english(data)
    if language == "simp_chinese":
        return loc_simp_chinese(data)
    raise ValueError(f"Unsupported localization language: {language}")


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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_triggers emits tv_wonder_pharos_alexandria_hostile_privateers_trigger and tv_wonder_pharos_alexandria_hostile_privateers_at_least_<count>_trigger with any_privateer_in_area",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_effects emits tv_wonder_pharos_clear_privateers_effect with every_privateer_in_area and change_privateer_power = -0.4",
                "scripts_engineering_department/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event ids 7301-7303 call tv_wonder_pharos_clear_privateers_effect; 7304 calls tv_wonder_pharos_enter_stage_2_effect",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:PHAROS_ROUTE_KEYS defines constantinople, venice, genoa, malta, tunis, palermo, candia, and gibraltar",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:PHAROS_ROUTE_IDS assigns stable route ids 1-8 for tv_wonder_pharos_active_route",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_triggers emits per-route triggers for every PHAROS_ROUTE_KEYS entry",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_route_row reads tv_wonder_pharos_route_<route>_location and tv_wonder_pharos_route_<route>_owner",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_stage_2_card loops PHAROS_ROUTE_KEYS and appends pharos_route_row for every route",
                "src_engineering_department/in_game/gui/panels/organization/tv_engineering_department.gui:Pharos generated rows call GetLocation.GetName and GetCountry.GetNameWithFlag from route variables",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_set_route_projection_lines writes tv_wonder_pharos_route_<route>_location, _owner, and _status",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_status_visible reads tv_wonder_pharos_route_<route>_status in GUI visibility expressions",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_selected_route_completion_lines writes tv_wonder_pharos_route_<route>_passed for completed rows",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_roll_route_effect uses random_list branches filtered by tv_wonder_pharos_route_<route>_pending_trigger",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_select_route_lines writes tv_wonder_pharos_active_route, tv_wonder_pharos_active_route_id, tv_wonder_pharos_event_route_location, and tv_wonder_pharos_event_route_owner",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_evaluate_selected_route_effect dispatches selected routes to event ids 7305, 7306, or 7307",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_triggers emits tv_wonder_pharos_route_<route>_controlled_trigger with owns = location:<route>",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_complete_selected_controlled_route_effect sets tv_wonder_pharos_active_route_status = 1",
                "scripts_engineering_department/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event id 7305 calls tv_wonder_pharos_complete_selected_controlled_route_effect",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:append_pharos_triggers emits tv_wonder_pharos_route_<route>_basing_trigger with gives_fleet_basing_rights_to and receives_fleet_basing_rights_from",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_complete_selected_basing_route_effect sets tv_wonder_pharos_active_route_status = 2",
                "scripts_engineering_department/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event id 7306 calls tv_wonder_pharos_complete_selected_basing_route_effect",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_evaluate_selected_route_effect dispatches owned foreign route scopes to event id 7307 when no control or basing pass exists",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_create_selected_route_basing_effect creates bidirectional relation_type:fleet_basing_rights with scope:tv_wonder_pharos_event_route_owner",
                "scripts_engineering_department/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event id 7307 charges change_gold_effect and calls tv_wonder_pharos_create_selected_route_basing_effect",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_refresh_threat_effect writes tv_wonder_pharos_privateer_threat_pct from hostile privateer count thresholds",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_stage_1_card renders pharos_piechart bound to tv_wonder_pharos_privateer_threat_pct",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:events 7301-7303 clear privateers and refresh display before event 7304 enters route stage",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_refresh_route_progress_effect counts tv_wonder_pharos_route_<route>_passed and clamps tv_wonder_pharos_route_progress to 0-8",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:tv_wonder_pharos_maybe_finish_routes_effect checks tv_wonder_pharos_route_progress >= PHAROS_ROUTE_COUNT and schedules event id 7308",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_stage_2_card renders pharos_piechart and x/8 raw_text from tv_wonder_pharos_route_progress",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_route_row builds one fixed-height row with route location, owner, and Control/Basing/Unheld status labels",
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_stage_2_card iterates PHAROS_ROUTE_KEYS and emits eight pharos_route_row blocks",
                "src_engineering_department/in_game/gui/panels/organization/tv_engineering_department.gui:generated Pharos block contains per-route rows for constantinople, venice, genoa, malta, tunis, palermo, candia, and gibraltar",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py:pharos_stage_1_card and pharos_stage_2_card render separate progress piecharts for threat and route count",
                "scripts_engineering_department/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py:event ids 7301-7303 and 7307 provide the incident-like player-facing choices",
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
                "scripts_engineering_department/wonder_unique_rituals/pharos.py provides existing manual generation patterns for route rows, selectors, triggers, and effects",
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
            "implementation_source": "scripts_engineering_department/wonder_unique_rituals/pharos.py + scripts/in_game/events/gen_tv_wonder_unique_pharos_lighthouse_ritual_events.py",
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
            "implementation_source": "scripts_engineering_department/wonder_unique_rituals/hagia.py + scripts/in_game/events/gen_tv_wonder_unique_hagia_sophia_ritual_events.py",
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
            "generated_by": "scripts_engineering_department/gen_unique_wonder_ritual_specs.py",
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
        root / "src_engineering_department" / "in_game",
        root / "scripts_engineering_department" / "in_game",
        root / "scripts_engineering_department" / "wonder_unique_rituals",
        root / "data" / "wonder_localization.yaml",
    ]
    alhambra_generated_event_target = "src_engineering_department/in_game/events/tv_wonder_unique_alhambra_ritual_events.txt"
    ids: set[int] = set()
    for base in roots:
        paths = [base] if base.is_file() else list(base.rglob("*")) if base.exists() else []
        for path in paths:
            if not path.is_file() or path.suffix not in {".txt", ".py", ".yml", ".yaml"}:
                continue
            try:
                rel_path = path.relative_to(root).as_posix()
            except ValueError:
                rel_path = path.as_posix()
            if rel_path == alhambra_generated_event_target:
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
