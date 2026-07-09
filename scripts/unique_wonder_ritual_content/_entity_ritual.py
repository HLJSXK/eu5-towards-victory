"""Shared "entity ritual" rendering engine.

Used by dome_of_the_rock.py, bank_of_saint_george.py, st_peters_basilica.py,
and alhambra.py: each of those wonders' data/unique_wonder_ritual_specs.yaml
`design_ir.tracked_entity_sets` names several individually-tracked entities per
row set (e.g. 5 named access groups, 6 named credit pledges). This engine gives
every named entity its own status variable, its own real eligibility trigger
(site control, not `always = yes`), its own GUI checklist/incident_log row, and
a real reward effect at the resolve stage scaled by how many entities landed in
a favorable state — replacing the generic
`started/progress/branch/completed/failed/reset/state` aggregate-only stub that
scripts/gen_repeated_row_pilot_wonders.py produced for these wonders.

Per-entity status values (persistent int variable, one per entity):
    0 = pending      (not yet rolled)
    1 = favorable     (accepted / entrusted / secured — the good outcome)
    2 = contested      (objects / disputed / threatened — the risk outcome)
    3 = narrowed      (locked to a reduced but stable settlement)

Each row set moves through 4 stages, matching the existing pilot-wonder shape:
    opening  -> initializes every entity to `pending`
    update   -> rolls every entity to `favorable` or `contested`
                (weighted by `favorable_weight`), inside hidden_effect since the
                roll has no useful visible tooltip
    retry    -> two-option branch on any `contested` entity: reconcile
                (re-roll contested entities at better odds) or narrow
                (lock remaining contested entities to `narrowed`, ending retries)
    resolve  -> real reward effect, branched by how many entities are
                `favorable` (bounded literal thresholds, safe for option tooltips
                since they only re-read already-committed persistent state)
"""
from wonder_mechanics.render import monthly_country_pulse_event

T = "\t"
NAMESPACE = "tv_engineering_department"
OPTION_LETTERS = "abcdefghijklmnopqrstuvwxyz"
DASH = "-" * 46

STATUS_PENDING = 0
STATUS_FAVORABLE = 1
STATUS_CONTESTED = 2
STATUS_NARROWED = 3

WONDER_DISPLAY_NAMES = {
    "alhambra": {
        "english": "Alhambra",
        "simp_chinese": "\u963f\u5c14\u7f55\u5e03\u62c9\u5bab",
    },
    "dome_of_the_rock": {
        "english": "Dome of the Rock",
        "simp_chinese": "\u5706\u9876\u6e05\u771f\u5bfa",
    },
    "bank_of_saint_george": {
        "english": "Bank of Saint George",
        "simp_chinese": "\u5723\u4e54\u6cbb\u94f6\u884c",
    },
    "st_peters_basilica": {
        "english": "St. Peter's Basilica",
        "simp_chinese": "\u5723\u5f7c\u5f97\u5927\u6559\u5802",
    },
}


def row_prefix(runtime_prefix: str, row_set_key: str) -> str:
    return f"{runtime_prefix}_{row_set_key}"


def entity_status_var(runtime_prefix: str, row_set_key: str, entity_key: str) -> str:
    return f"{row_prefix(runtime_prefix, row_set_key)}_{entity_key}_status"


def favorable_count_var(runtime_prefix: str, row_set_key: str) -> str:
    return f"{row_prefix(runtime_prefix, row_set_key)}_favorable_count"


def narrowed_var(runtime_prefix: str, row_set_key: str) -> str:
    return f"{row_prefix(runtime_prefix, row_set_key)}_narrowed"


def site_control_trigger_name(runtime_prefix: str) -> str:
    return f"{runtime_prefix}_site_control_trigger"


def locked_trigger_name(runtime_prefix: str) -> str:
    return f"{runtime_prefix}_active_trigger"


def ritual_row_set_index_var(runtime_prefix: str) -> str:
    return f"{runtime_prefix}_ritual_row_set_index"


def ritual_phase_var(runtime_prefix: str) -> str:
    return f"{runtime_prefix}_ritual_phase"


def ritual_pending_event_var(runtime_prefix: str) -> str:
    return f"{runtime_prefix}_ritual_pending_event"


def ritual_completed_var(name_slug: str) -> str:
    return f"tv_wonder_{name_slug}_ritual_completed"


# ---------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------

def _row_init_effect(wonder: dict, row_set: dict) -> list[str]:
    runtime_prefix = wonder["runtime_prefix"]
    prefix = row_prefix(runtime_prefix, row_set["row_set_key"])
    lines = [f"# -- {prefix}_row_init_effect {DASH}", f"{prefix}_row_init_effect = {{"]
    for entity in row_set["entities"]:
        var = entity_status_var(runtime_prefix, row_set["row_set_key"], entity["key"])
        lines.append(f"{T}set_variable = {{ name = {var} value = {STATUS_PENDING} }}")
    lines.append(f"{T}set_variable = {{ name = {favorable_count_var(runtime_prefix, row_set['row_set_key'])} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {narrowed_var(runtime_prefix, row_set['row_set_key'])} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {prefix}_started value = 1 }}")
    lines.append(f"{T}set_variable = {{ name = {ritual_phase_var(runtime_prefix)} value = 1 }}")
    lines.append(f"{T}remove_variable = {ritual_pending_event_var(runtime_prefix)}")
    lines.append("}")
    return lines


def _row_state_write_effect(wonder: dict, row_set: dict) -> list[str]:
    runtime_prefix = wonder["runtime_prefix"]
    row_set_key = row_set["row_set_key"]
    prefix = row_prefix(runtime_prefix, row_set_key)
    weight = int(row_set.get("favorable_weight", 65))
    lines = [f"# -- {prefix}_row_state_write_effect {DASH}", f"{prefix}_row_state_write_effect = {{"]
    lines.append(f"{T}hidden_effect = {{")
    for entity in row_set["entities"]:
        var = entity_status_var(runtime_prefix, row_set_key, entity["key"])
        lines.append(f"{T}{T}random_list = {{")
        lines.append(f"{T}{T}{T}{weight} = {{ set_variable = {{ name = {var} value = {STATUS_FAVORABLE} }} }}")
        lines.append(f"{T}{T}{T}{100 - weight} = {{ set_variable = {{ name = {var} value = {STATUS_CONTESTED} }} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}{prefix}_aggregate_refresh_effect = yes")
    lines.append(f"{T}{T}set_variable = {{ name = {ritual_phase_var(runtime_prefix)} value = 2 }}")
    lines.append(f"{T}{T}remove_variable = {ritual_pending_event_var(runtime_prefix)}")
    lines.append(f"{T}}}")
    lines.append("}")
    return lines


def _aggregate_refresh_effect(wonder: dict, row_set: dict) -> list[str]:
    runtime_prefix = wonder["runtime_prefix"]
    row_set_key = row_set["row_set_key"]
    prefix = row_prefix(runtime_prefix, row_set_key)
    lines = [f"# -- {prefix}_aggregate_refresh_effect {DASH}", f"{prefix}_aggregate_refresh_effect = {{"]
    lines.append(f"{T}set_variable = {{ name = {favorable_count_var(runtime_prefix, row_set_key)} value = 0 }}")
    for entity in row_set["entities"]:
        var = entity_status_var(runtime_prefix, row_set_key, entity["key"])
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ var:{var} ?= {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {favorable_count_var(runtime_prefix, row_set_key)} add = 1 }}")
        lines.append(f"{T}}}")
    lines.append("}")
    return lines


def _branch_write_effect(wonder: dict, row_set: dict) -> list[str]:
    runtime_prefix = wonder["runtime_prefix"]
    row_set_key = row_set["row_set_key"]
    prefix = row_prefix(runtime_prefix, row_set_key)
    lines = [f"# -- {prefix}_reconcile_effect {DASH}", f"{prefix}_reconcile_effect = {{"]
    lines.append(f"{T}hidden_effect = {{")
    for entity in row_set["entities"]:
        var = entity_status_var(runtime_prefix, row_set_key, entity["key"])
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{var} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}random_list = {{")
        lines.append(f"{T}{T}{T}{T}80 = {{ set_variable = {{ name = {var} value = {STATUS_FAVORABLE} }} }}")
        lines.append(f"{T}{T}{T}{T}20 = {{ set_variable = {{ name = {var} value = {STATUS_CONTESTED} }} }}")
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}{prefix}_aggregate_refresh_effect = yes")
    lines.append(f"{T}{T}set_variable = {{ name = {ritual_phase_var(runtime_prefix)} value = 2 }}")
    lines.append(f"{T}{T}remove_variable = {ritual_pending_event_var(runtime_prefix)}")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")
    lines.append(f"# -- {prefix}_narrow_effect {DASH}")
    lines.append(f"{prefix}_narrow_effect = {{")
    lines.append(f"{T}hidden_effect = {{")
    for entity in row_set["entities"]:
        var = entity_status_var(runtime_prefix, row_set_key, entity["key"])
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{var} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {var} value = {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = {narrowed_var(runtime_prefix, row_set_key)} value = 1 }}")
    lines.append(f"{T}{T}{prefix}_aggregate_refresh_effect = yes")
    lines.append(f"{T}{T}set_variable = {{ name = {ritual_phase_var(runtime_prefix)} value = 2 }}")
    lines.append(f"{T}{T}remove_variable = {ritual_pending_event_var(runtime_prefix)}")
    lines.append(f"{T}}}")
    lines.append("}")
    return lines


def _cleanup_write_effect(wonder: dict, row_set: dict) -> list[str]:
    runtime_prefix = wonder["runtime_prefix"]
    row_set_key = row_set["row_set_key"]
    prefix = row_prefix(runtime_prefix, row_set_key)
    lines = [f"# -- {prefix}_cleanup_write_effect {DASH}", f"{prefix}_cleanup_write_effect = {{"]
    for entity in row_set["entities"]:
        lines.append(f"{T}remove_variable = {entity_status_var(runtime_prefix, row_set_key, entity['key'])}")
    lines.append(f"{T}remove_variable = {favorable_count_var(runtime_prefix, row_set_key)}")
    lines.append(f"{T}remove_variable = {narrowed_var(runtime_prefix, row_set_key)}")
    lines.append(f"{T}remove_variable = {prefix}_started")
    lines.append(f"{T}remove_variable = {prefix}_completed")
    lines.append("}")
    return lines


def _completion_effect(wonder: dict, row_set: dict) -> list[str]:
    runtime_prefix = wonder["runtime_prefix"]
    prefix = row_prefix(runtime_prefix, row_set["row_set_key"])
    lines = [f"# -- {prefix}_completion_effect {DASH}", f"{prefix}_completion_effect = {{"]
    lines.append(f"{T}set_variable = {{ name = {prefix}_completed value = 1 }}")
    lines.append(f"{T}set_variable = {{ name = {ritual_phase_var(runtime_prefix)} value = 3 }}")
    lines.append(f"{T}remove_variable = {ritual_pending_event_var(runtime_prefix)}")
    lines.append("}")
    return lines


def append_effects(wonder: dict, lines: list[str]) -> None:
    for row_set in wonder["row_sets"]:
        lines.append("")
        lines.extend(_row_init_effect(wonder, row_set))
        lines.append("")
        lines.extend(_row_state_write_effect(wonder, row_set))
        lines.append("")
        lines.extend(_aggregate_refresh_effect(wonder, row_set))
        lines.append("")
        lines.extend(_branch_write_effect(wonder, row_set))
        lines.append("")
        lines.extend(_cleanup_write_effect(wonder, row_set))
        lines.append("")
        lines.extend(_completion_effect(wonder, row_set))
    wonder["extra_effects_hook"](lines) if wonder.get("extra_effects_hook") else None
    lines.append("")
    lines.extend(_resolve_reward_effect(wonder))
    lines.append("")
    lines.extend(_monthly_progress_effect(wonder))
    lines.append("")
    lines.extend(_start_effect(wonder))


def _resolve_reward_effect(wonder: dict) -> list[str]:
    """One resolve-reward effect covering every row set: real, branch-scaled
    permanent country modifier + one-time reward, using literal thresholds
    over each row set's already-committed favorable_count (safe under the
    Events risk card: no same-chain scratch-variable reads)."""
    reward = wonder["reward"]
    lines = [f"# -- tv_wonder_{wonder['name_slug']}_ritual_grant_reward_effect {DASH}"]
    lines.append(f"tv_wonder_{wonder['name_slug']}_ritual_grant_reward_effect = {{")

    total_entities = sum(len(rs["entities"]) for rs in wonder["row_sets"])
    lines.append(f"{T}set_variable = {{ name = tv_wonder_{wonder['name_slug']}_ritual_total_favorable value = 0 }}")
    for row_set in wonder["row_sets"]:
        lines.append(
            f"{T}change_variable = {{ name = tv_wonder_{wonder['name_slug']}_ritual_total_favorable "
            f"add = var:{favorable_count_var(wonder['runtime_prefix'], row_set['row_set_key'])} }}"
        )

    good_threshold = wonder.get("good_threshold", max(1, round(total_entities * 0.8)))
    fair_threshold = wonder.get("fair_threshold", max(1, round(total_entities * 0.5)))

    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_{wonder['name_slug']}_ritual_total_favorable >= {good_threshold} }}")
    for effect_line in reward["good"]["modifier_effects"]:
        lines.append(f"{T}{T}{effect_line}")
    for effect_line in reward["good"]["one_time_effects"]:
        lines.append(f"{T}{T}{effect_line}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:tv_wonder_{wonder['name_slug']}_ritual_total_favorable >= {fair_threshold} }}")
    for effect_line in reward["fair"]["modifier_effects"]:
        lines.append(f"{T}{T}{effect_line}")
    for effect_line in reward["fair"]["one_time_effects"]:
        lines.append(f"{T}{T}{effect_line}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    for effect_line in reward["poor"]["modifier_effects"]:
        lines.append(f"{T}{T}{effect_line}")
    for effect_line in reward["poor"]["one_time_effects"]:
        lines.append(f"{T}{T}{effect_line}")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = tv_wonder_{wonder['name_slug']}_ritual_total_favorable")
    for row_set in wonder["row_sets"]:
        lines.append(f"{T}{row_prefix(wonder['runtime_prefix'], row_set['row_set_key'])}_cleanup_write_effect = yes")
    lines.append(f"{T}remove_variable = {ritual_row_set_index_var(wonder['runtime_prefix'])}")
    lines.append(f"{T}remove_variable = {ritual_phase_var(wonder['runtime_prefix'])}")
    lines.append(f"{T}remove_variable = {ritual_pending_event_var(wonder['runtime_prefix'])}")
    lines.append(f"{T}set_variable = {{ name = {ritual_completed_var(wonder['name_slug'])} value = 1 }}")
    lines.append(f"{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append("}")
    return lines


def _start_effect(wonder: dict) -> list[str]:
    runtime_prefix = wonder["runtime_prefix"]
    lines = [f"# -- tv_wonder_{wonder['name_slug']}_ritual_start_effect {DASH}"]
    lines.append(f"tv_wonder_{wonder['name_slug']}_ritual_start_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {ritual_row_set_index_var(runtime_prefix)} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {ritual_phase_var(runtime_prefix)} value = 0 }}")
    lines.append(f"{T}remove_variable = {ritual_pending_event_var(runtime_prefix)}")
    lines.append("}")
    return lines


def _monthly_progress_effect(wonder: dict) -> list[str]:
    """Fires the next event in sequence for the wonder-level row_set_index /
    phase state machine (0 = fire opening, 1 = fire update, 2 = fire retry if
    a contested entity remains else fire resolve, 3 = advance to the next row
    set). Mirrors the verified tv_wonder_hagia_monthly_progress_effect /
    tv_wonder_pharos_roll_route_effect dispatch pattern."""
    runtime_prefix = wonder["runtime_prefix"]
    row_sets = wonder["row_sets"]
    lines = [f"# -- tv_wonder_{wonder['name_slug']}_ritual_monthly_progress_effect {DASH}"]
    lines.append(f"tv_wonder_{wonder['name_slug']}_ritual_monthly_progress_effect = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{locked_trigger_name(runtime_prefix)} = yes")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = {ritual_pending_event_var(runtime_prefix)} }}")
    lines.append(f"{T}{T}}}")
    for index, row_set in enumerate(row_sets):
        prefix = row_prefix(runtime_prefix, row_set["row_set_key"])
        stages = row_set["stages"]
        head = "if" if index == 0 else "else_if"
        lines.append(f"{T}{T}{head} = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{ritual_row_set_index_var(runtime_prefix)} ?= {index} }}")
        opening_limit = f"var:{ritual_phase_var(runtime_prefix)} ?= 0"
        if index == 0 and wonder.get("gate_trigger"):
            opening_limit = f"var:{ritual_phase_var(runtime_prefix)} ?= 0 {wonder['gate_trigger']} = yes"
        lines.append(f"{T}{T}{T}if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ {opening_limit} }}")
        lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {ritual_pending_event_var(runtime_prefix)} value = 1 }}")
        lines.append(f"{T}{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{stages['opening']['event_id']} days = 1 }}")
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}else_if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ var:{ritual_phase_var(runtime_prefix)} ?= 1 }}")
        lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {ritual_pending_event_var(runtime_prefix)} value = 1 }}")
        lines.append(f"{T}{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{stages['update']['event_id']} days = 1 }}")
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}else_if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ var:{ritual_phase_var(runtime_prefix)} ?= 2 }}")
        lines.append(f"{T}{T}{T}{T}if = {{")
        lines.append(f"{T}{T}{T}{T}{T}limit = {{ {prefix}_has_contested_entity_trigger = yes }}")
        lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {ritual_pending_event_var(runtime_prefix)} value = 1 }}")
        lines.append(f"{T}{T}{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{stages['retry']['event_id']} days = 1 }}")
        lines.append(f"{T}{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}{T}else = {{")
        lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {ritual_pending_event_var(runtime_prefix)} value = 1 }}")
        lines.append(f"{T}{T}{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{stages['resolve']['event_id']} days = 1 }}")
        lines.append(f"{T}{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}{T}else_if = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ var:{ritual_phase_var(runtime_prefix)} ?= 3 }}")
        lines.append(f"{T}{T}{T}{T}change_variable = {{ name = {ritual_row_set_index_var(runtime_prefix)} add = 1 }}")
        lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {ritual_phase_var(runtime_prefix)} value = 0 }}")
        lines.append(f"{T}{T}{T}}}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")
    return lines


# ---------------------------------------------------------------------------
# triggers
# ---------------------------------------------------------------------------

def append_triggers(wonder: dict, lines: list[str]) -> None:
    runtime_prefix = wonder["runtime_prefix"]
    lines.append("")
    lines.append(f"# -- {site_control_trigger_name(runtime_prefix)} {DASH}")
    lines.append(f"{site_control_trigger_name(runtime_prefix)} = {{")
    lines.append(f"{T}owns = location:{wonder['location']}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {locked_trigger_name(runtime_prefix)} {DASH}")
    lines.append(f"{locked_trigger_name(runtime_prefix)} = {{")
    lines.append(f"{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}var:tv_wonder_locked ?= {wonder['wonder_id']}")
    lines.append(f"{T}has_variable = tv_wonder_ritual_in_progress")
    lines.append("}")

    for row_set in wonder["row_sets"]:
        prefix = row_prefix(runtime_prefix, row_set["row_set_key"])

        lines.append("")
        lines.append(f"# -- {prefix}_row_completion_trigger {DASH}")
        lines.append(f"{prefix}_row_completion_trigger = {{")
        lines.append(f"{T}has_variable = {prefix}_completed")
        lines.append(f"{T}var:{prefix}_completed ?= 1")
        lines.append("}")

        lines.append("")
        lines.append(f"# -- {prefix}_eligibility_trigger {DASH}")
        lines.append(f"{prefix}_eligibility_trigger = {{")
        lines.append(f"{T}{locked_trigger_name(runtime_prefix)} = yes")
        lines.append(f"{T}{site_control_trigger_name(runtime_prefix)} = yes")
        if wonder.get("gate_trigger") and row_set is wonder["row_sets"][0]:
            lines.append(f"{T}{wonder['gate_trigger']} = yes")
        lines.append("}")

        lines.append("")
        lines.append(f"# -- {prefix}_has_contested_entity_trigger {DASH}")
        lines.append(f"{prefix}_has_contested_entity_trigger = {{")
        lines.append(f"{T}OR = {{")
        for entity in row_set["entities"]:
            var = entity_status_var(runtime_prefix, row_set["row_set_key"], entity["key"])
            lines.append(f"{T}{T}var:{var} ?= {STATUS_CONTESTED}")
        lines.append(f"{T}}}")
        lines.append("}")

        for entity in row_set["entities"]:
            var = entity_status_var(runtime_prefix, row_set["row_set_key"], entity["key"])
            lines.append("")
            lines.append(f"# -- {var}_favorable_trigger {DASH}")
            lines.append(f"{var}_favorable_trigger = {{")
            lines.append(f"{T}var:{var} ?= {STATUS_FAVORABLE}")
            lines.append("}")

    if wonder.get("extra_triggers_hook"):
        wonder["extra_triggers_hook"](lines)


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------

def _option(event_id: int, letter: str, effect_lines: list[str], trigger_line: str | None = None) -> list[str]:
    lines = [f"{T}option = {{", f"{T}{T}name = {NAMESPACE}.{event_id}.{letter}"]
    if trigger_line:
        lines.append(f"{T}{T}trigger = {{ {trigger_line} }}")
    for effect_line in effect_lines:
        lines.append(f"{T}{T}{effect_line}")
    lines.append(f"{T}}}")
    return lines


def build_events_body(wonder: dict) -> list[str]:
    lines: list[str] = []
    for row_set in wonder["row_sets"]:
        prefix = row_prefix(wonder["runtime_prefix"], row_set["row_set_key"])
        stages = row_set["stages"]

        opening = stages["opening"]
        eid = opening["event_id"]
        lines.append(f"# -- {NAMESPACE}.{eid} {DASH}")
        lines.append(f"{NAMESPACE}.{eid} = {{")
        lines.append(f"{T}type = country_event")
        lines.append(f"{T}title = {NAMESPACE}.{eid}.t")
        lines.append(f"{T}desc = {NAMESPACE}.{eid}.d")
        lines.append(f"{T}outcome = neutral")
        lines.append("")
        lines.extend(_option(eid, "a", [f"{prefix}_row_init_effect = yes"], trigger_line=f"{prefix}_eligibility_trigger = yes"))
        lines.append("}")
        lines.append("")

        update = stages["update"]
        eid = update["event_id"]
        lines.append(f"# -- {NAMESPACE}.{eid} {DASH}")
        lines.append(f"{NAMESPACE}.{eid} = {{")
        lines.append(f"{T}type = country_event")
        lines.append(f"{T}title = {NAMESPACE}.{eid}.t")
        lines.append(f"{T}desc = {NAMESPACE}.{eid}.d")
        lines.append(f"{T}outcome = neutral")
        lines.append("")
        lines.extend(_option(eid, "a", [f"{prefix}_row_state_write_effect = yes"], trigger_line=f"{prefix}_eligibility_trigger = yes"))
        lines.append("}")
        lines.append("")

        retry = stages["retry"]
        eid = retry["event_id"]
        lines.append(f"# -- {NAMESPACE}.{eid} {DASH}")
        lines.append(f"{NAMESPACE}.{eid} = {{")
        lines.append(f"{T}type = country_event")
        lines.append(f"{T}title = {NAMESPACE}.{eid}.t")
        lines.append(f"{T}desc = {NAMESPACE}.{eid}.d")
        lines.append(f"{T}outcome = neutral")
        lines.append("")
        lines.extend(_option(eid, "a", [f"{prefix}_reconcile_effect = yes"], trigger_line=f"{prefix}_has_contested_entity_trigger = yes"))
        lines.append("")
        lines.extend(_option(eid, "b", [f"{prefix}_narrow_effect = yes"], trigger_line=f"{prefix}_has_contested_entity_trigger = yes"))
        lines.append("}")
        lines.append("")

        resolve = stages["resolve"]
        eid = resolve["event_id"]
        lines.append(f"# -- {NAMESPACE}.{eid} {DASH}")
        lines.append(f"{NAMESPACE}.{eid} = {{")
        lines.append(f"{T}type = country_event")
        lines.append(f"{T}title = {NAMESPACE}.{eid}.t")
        lines.append(f"{T}desc = {NAMESPACE}.{eid}.d")
        lines.append(f"{T}outcome = good")
        lines.append("")
        resolve_effects = [f"{prefix}_completion_effect = yes"]
        if row_set is wonder["row_sets"][-1]:
            resolve_effects.append(f"tv_wonder_{wonder['name_slug']}_ritual_grant_reward_effect = yes")
        lines.extend(_option(eid, "a", resolve_effects))
        lines.append("}")
        lines.append("")

    if wonder.get("extra_events_hook"):
        wonder["extra_events_hook"](lines)

    return lines


# ---------------------------------------------------------------------------
# localization
# ---------------------------------------------------------------------------

def loc_key(event_id: int, suffix: str) -> str:
    return f"{NAMESPACE}.{event_id}.{suffix}"


def _display_name_from_slug(name_slug: str) -> str:
    return " ".join(part.capitalize() for part in name_slug.split("_"))


def _modifier_display_name(wonder: dict, modifier_name: str, language: str) -> str:
    names = WONDER_DISPLAY_NAMES.get(wonder["name_slug"], {})
    base_name = names.get(language) or names.get("english") or _display_name_from_slug(wonder["name_slug"])
    is_lesser = modifier_name.endswith("_lesser")
    if language == "english":
        suffix = " (Lesser)" if is_lesser else ""
        return f"{base_name} Ritual Reward{suffix}"
    lesser = "\u6b21\u7ea7" if is_lesser else ""
    return f"{base_name}{lesser}\u4eea\u5f0f\u5956\u52b1"


def build_localization(wonder: dict, language: str) -> list[str]:
    """Returns ' KEY:0 "text"' lines (no header/wrapper) for one language."""
    title_field = "en_title" if language == "english" else "zh_title"
    desc_field = "en_desc" if language == "english" else "zh_desc"
    name_field = "en" if language == "english" else "zh"
    lines: list[str] = []

    for row_set in wonder["row_sets"]:
        for stage_key in ("opening", "update", "retry", "resolve"):
            stage = row_set["stages"][stage_key]
            eid = stage["event_id"]
            lines.append(f' {loc_key(eid, "t")}:0 "{stage[title_field]}"')
            lines.append(f' {loc_key(eid, "d")}:0 "{stage[desc_field]}"')
            if stage_key == "retry":
                lines.append(f' {loc_key(eid, "a")}:0 "{stage["option_a_" + ("en" if language == "english" else "zh")]}"')
                lines.append(f' {loc_key(eid, "b")}:0 "{stage["option_b_" + ("en" if language == "english" else "zh")]}"')
            else:
                lines.append(f' {loc_key(eid, "a")}:0 "{stage["option_a_" + ("en" if language == "english" else "zh")]}"')

    # GUI panel text: row-set label + per-entity name + status words.
    key_prefix = f"TV_ENGINEERING_{wonder['name_slug'].upper()}"
    status_words = {
        "pending": ("Awaiting review", "尚待核验"),
        "favorable": ("Favorable", "顺遂"),
        "contested": ("Contested", "争议中"),
        "narrowed": ("Narrowed settlement", "缩减定案"),
    }
    lang_index = 0 if language == "english" else 1
    for status_key, words in status_words.items():
        lines.append(f' {key_prefix}_STATUS_{status_key.upper()}:0 "{words[lang_index]}"')
    for row_set in wonder["row_sets"]:
        rs_key = row_set["row_set_key"]
        rs_label = row_set[f"label_{name_field}"]
        lines.append(f' {key_prefix}_{rs_key.upper()}_LABEL:0 "{rs_label}"')
        for entity in row_set["entities"]:
            entity_label = entity[name_field]
            lines.append(f' {key_prefix}_{rs_key.upper()}_{entity["key"].upper()}:0 "{entity_label}"')

    for modifier_name in wonder.get("modifier_bundles", {}):
        label = _modifier_display_name(wonder, modifier_name, language)
        lines.append(f' STATIC_MODIFIER_NAME_{modifier_name}:0 "{label}"')

    if wonder.get("extra_localization_hook"):
        wonder["extra_localization_hook"](lines, language)

    return lines


# ---------------------------------------------------------------------------
# GUI (checklist / incident_log rows, real per entity)
# ---------------------------------------------------------------------------

CARD_WIDTH = 462
ROW_HEIGHT = 24


def _entity_row(wonder: dict, row_set: dict, entity: dict, indent: int, helpers: dict[str, object]) -> list[str]:
    prefix = T * indent
    runtime_prefix = wonder["runtime_prefix"]
    var = entity_status_var(runtime_prefix, row_set["row_set_key"], entity["key"])
    key_prefix = f"TV_ENGINEERING_{wonder['name_slug'].upper()}"
    label_key = f"{key_prefix}_{row_set['row_set_key'].upper()}_{entity['key'].upper()}"

    var_is_set = helpers["var_is_set"]
    eq = helpers["eq"]
    fold_bool = helpers["fold_bool"]

    def status_chip(status_value: int, text_key: str, texture: str, alpha: str) -> list[str]:
        visible = f"And({var_is_set(var)}, {eq(var, status_value)})"
        return [
            f"{prefix}{T}widget = {{",
            f'{prefix}{T}{T}visible = "[{visible}]"',
            f"{prefix}{T}{T}size = {{ 118 20 }}",
            f"{prefix}{T}{T}alwaystransparent = yes",
            f"{prefix}{T}{T}background = {{ using = {texture} alpha = {alpha} }}",
            f'{prefix}{T}{T}text_single = {{ text = "{text_key}" size = {{ 100% 100% }} fontsize = 11 align = center|nobaseline }}',
            f"{prefix}{T}}}",
        ]

    pending_visible = f"Not({var_is_set(var)})"
    lines = [
        f"{prefix}hbox = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {CARD_WIDTH - 16} {ROW_HEIGHT} }}",
        f"{prefix}{T}spacing = 8",
        f"{prefix}{T}ignoreinvisible = yes",
        f'{prefix}{T}text_single = {{ text = "{label_key}" size = {{ 322 22 }} max_width = 322 fontsize = 12 align = nobaseline|left }}',
    ]
    lines.extend(status_chip(STATUS_FAVORABLE, f"{key_prefix}_STATUS_FAVORABLE", "color_market_green_texture", "0.30"))
    lines.extend(status_chip(STATUS_CONTESTED, f"{key_prefix}_STATUS_CONTESTED", "color_mid_red_texture", "0.30"))
    lines.extend(status_chip(STATUS_NARROWED, f"{key_prefix}_STATUS_NARROWED", "color_yellow_texture", "0.30"))
    lines.extend(
        [
            f"{prefix}{T}widget = {{",
            f'{prefix}{T}{T}visible = "[{pending_visible}]"',
            f"{prefix}{T}{T}size = {{ 118 20 }}",
            f"{prefix}{T}{T}alwaystransparent = yes",
            f"{prefix}{T}{T}background = {{ using = color_yellow_texture alpha = 0.12 }}",
            f'{prefix}{T}{T}text_single = {{ text = "{key_prefix}_STATUS_PENDING" size = {{ 100% 100% }} fontsize = 11 align = center|nobaseline }}',
            f"{prefix}{T}}}",
        ]
    )
    lines.append(f"{prefix}}}")
    return lines


def append_gui(wonder: dict, lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    globals().update(helpers)
    prefix_t = T * indent
    key_prefix = f"TV_ENGINEERING_{wonder['name_slug'].upper()}"
    locked_expr = f"And({helpers['player_var']('tv_wonder_locked')}.IsSet, {helpers['eq']('tv_wonder_locked', wonder['wonder_id'])})"
    card_visible = f"And({helpers['active_ritual_visible']()}, {locked_expr})"

    card_height = 40 + sum(24 * (1 + len(rs["entities"])) for rs in wonder["row_sets"])
    lines.append(f"{prefix_t}widget = {{")
    lines.append(f'{prefix_t}{T}visible = "[{card_visible}]"')
    lines.append(f"{prefix_t}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix_t}{T}layoutpolicy_vertical = fixed")
    lines.append(f"{prefix_t}{T}size = {{ {CARD_WIDTH} {card_height} }}")
    lines.append(f"{prefix_t}{T}using = bg_text_mask_container_dark_blue")
    lines.append(f"{prefix_t}{T}vbox = {{")
    lines.append(f"{prefix_t}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix_t}{T}{T}margin = {{ 8 8 }}")
    lines.append(f"{prefix_t}{T}{T}spacing = 4")
    lines.append(f"{prefix_t}{T}{T}ignoreinvisible = yes")

    for row_set in wonder["row_sets"]:
        rs_key = row_set["row_set_key"]
        lines.append(
            f'{prefix_t}{T}{T}text_single = {{ text = "{key_prefix}_{rs_key.upper()}_LABEL" size = {{ {CARD_WIDTH - 16} 22 }} max_width = {CARD_WIDTH - 16} fontsize = 13 align = nobaseline|left }}'
        )
        for entity in row_set["entities"]:
            lines.extend(_entity_row(wonder, row_set, entity, indent + 2, helpers))

    lines.append(f"{prefix_t}{T}}}")
    lines.append(f"{prefix_t}}}")
