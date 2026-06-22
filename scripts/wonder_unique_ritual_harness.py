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

SPEC_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_specs.yaml"
DESIGN_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_designs.yaml"
PROMPTS_FILE = REPO_ROOT / "data" / "unique_wonder_ritual_prompts.yaml"
LOCALIZATION_FILE = REPO_ROOT / "data" / "wonder_localization.yaml"

IMPLEMENTED_STATUSES = {"implemented_parity", "implementation_ready", "harness_generated"}
STUB_STATUSES = {"stub", "needs_design"}
ALLOWED_STATUSES = IMPLEMENTED_STATUSES | STUB_STATUSES
SUPPORTED_UI_COMPONENTS = {
    "checklist",
    "route_map",
    "actor_slots",
    "material_stockpile",
    "incident_log",
    "progress_track",
}
SUPPORTED_LISTENERS = {"monthly", "ruler_death", "pre_winning_war", "ending_war"}
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
EVENT_ID_PATTERN = re.compile(r"\btv_engineering_department\.([0-9]+)\b")


def load_unique_wonders() -> list[dict[str, Any]]:
    return list(load_unique_wonders_source_data().get("unique_wonders", []))


def load_optional_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return load_yaml(path)


def load_spec_data(path: Path = SPEC_FILE) -> dict[str, Any]:
    return load_optional_yaml(path) or {"metadata": {}, "unique_wonders": []}


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
    entries = []
    for wonder in wonders:
        key = str(wonder["key"])
        default_entry = default_spec_for_wonder(wonder)
        entry = deepcopy(existing_by_key.get(key)) if key in existing_by_key else deepcopy(default_entry)
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
                "implementation_ready": "Authored spec has passed Harness quality gates and may be generated.",
                "harness_generated": "Generated implementation is owned by the Harness node-graph generator.",
            },
            "quality_contract": {
                "minimum_player_visible_nodes": 3,
                "minimum_event_count": 3,
                "required_reward_channels": list(REQUIRED_REWARD_CHANNELS),
                "required_ui_components": list(sorted(SUPPORTED_UI_COMPONENTS)),
                "event_id_rule": "Every event id must be explicit, unique within this file, and < 10000.",
            },
            "ai_prompt_contract": {
                "batch_size": "1-5 unique wonders per authoring pass",
                "required_output_sections": [
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


def validate_spec_payload(
    payload: dict[str, Any],
    *,
    wonders: list[dict[str, Any]] | None = None,
    localization: dict[str, str] | None = None,
    occupied_event_ids: set[int] | None = None,
    require_all_wonders: bool = True,
) -> list[str]:
    errors: list[str] = []
    wonders = wonders if wonders is not None else load_unique_wonders()
    wonder_by_key = wonder_index(wonders)
    entries = payload.get("unique_wonders", []) or []
    if not isinstance(entries, list):
        return ["unique_wonders must be a list"]

    seen_keys: set[str] = set()
    seen_event_ids: dict[int, str] = {}
    loc = localization if localization is not None else loc_english()

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

        entry_event_ids = event_ids_in_entry(entry)
        for event_id in entry_event_ids:
            if event_id <= 0:
                errors.append(_issue(entry, f"event id {event_id} must be positive"))
            if event_id >= 10000:
                errors.append(_issue(entry, f"event id {event_id} must be < 10000"))
            if event_id in seen_event_ids:
                errors.append(_issue(entry, f"event id {event_id} duplicates {seen_event_ids[event_id]}"))
            seen_event_ids[event_id] = key
            if (
                occupied_event_ids is not None
                and status == "implementation_ready"
                and event_id in occupied_event_ids
            ):
                errors.append(_issue(entry, f"event id {event_id} collides with an occupied Engineering Department event id"))

        node_graph = entry.get("node_graph", {})
        if not isinstance(node_graph, dict):
            errors.append(_issue(entry, "node_graph must be a mapping"))
            node_graph = {}
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
        for node in nodes:
            if not isinstance(node, dict) or "event_id" not in node:
                continue
            if int(node["event_id"]) not in entry_event_id_set:
                errors.append(_issue(entry, f"node {node.get('key', '<unknown>')} references undeclared event id {node['event_id']}"))

        runtime_prefix = str(identity.get("runtime_prefix", ""))
        runtime_variables = set(str(variable) for variable in node_graph.get("runtime_variables", []) or [])
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
                if loc_key and loc_key not in loc:
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


def audit_summary() -> dict[str, Any]:
    wonders = load_unique_wonders()
    wonder_keys = {str(wonder["key"]) for wonder in wonders}
    designs = load_optional_yaml(DESIGN_FILE)
    prompts = load_optional_yaml(PROMPTS_FILE)
    specs = load_spec_data()
    loc = loc_english()

    design_index = list_index(designs)
    prompt_index = list_index(prompts)
    spec_index = list_index(specs)
    spec_errors = validate_spec_payload(specs, wonders=wonders, localization=loc)

    implemented = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") in IMPLEMENTED_STATUSES
    ]
    stubs = [
        key
        for key, entry in spec_index.items()
        if (entry.get("identity") or {}).get("status") in STUB_STATUSES
    ]
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
        "stub_specs": len(stubs),
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
