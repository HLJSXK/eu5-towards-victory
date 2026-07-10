"""Dome of the Rock (unique_dome_of_the_rock) ritual content.

Second bespoke rewrite. The first bespoke rewrite (2026-07) replaced the shared
`_entity_ritual` engine with a player-chosen "access compact" that
*deterministically* flagged 2 of 5 access groups and 1 of 5 custody duties as
contested, followed by one settlement event offering "reconcile at a prestige
cost" vs. "accept a narrower outcome for free", with a reward scaled by a
favorable-count threshold. `scripts/audit_unique_wonder_ritual_mechanic_similarity.py`
found that shape scored `combined_ratio` 0.48-0.71 against Bank of Saint
George and St. Peter's Basilica even after their own independent rewrites,
because all three still followed the same underlying narrative template:
"choice -> deterministic branch marking a fixed subset of tracked entities
'at risk' -> one retry/incident event offering 'pay a cost to fully resolve'
vs. 'accept a narrower outcome for free' -> threshold-scaled reward" (see
docs/knowledge/risk_cards/wonders.md rule 13).

This version is structurally different: it is time-extended and systemic
rather than a one-shot opening-choice-then-incident chain, reflecting the
real Haram al-Sharif's long history of *rotating, shared, negotiated*
custodianship among distinct communities rather than a single settlement.
The ritual runs a fixed six-term "Custody Calendar" spanning roughly two
years of in-game time:

  * Every term, the player actively *assigns* which of three permanent
    custodian communities (the Nusaybah guardian family, the Waqf endowment
    council, and the garrison's platform watch) holds custody for that term.
    This is a repeated real decision across time, not a single deterministic
    branch computed from an opening choice.
  * Repeating the same community builds `continuity` (administrative memory)
    but costs `concord` (perceived favoritism); rotating to a different
    community grants `concord` but does not build `continuity`. This is a
    genuine ongoing trade-off between two independently accumulating state
    tracks, not a fixed subset of entities getting marked "contested" by a
    lookup table.
  * Every term also asks a separate, recurring resource question -- fund the
    endowment's physical upkeep at a prestige cost, or let it lapse -- which
    accumulates a third independent `endowment_health` track over the full
    six-term span. This is a resource-management cadence repeated across
    time, not a single retry event offering "pay to fully resolve vs. accept
    a lesser outcome for free" after a one-time risk reveal.
  * The final reward is scaled by the combined `concord + continuity +
    endowment_health` score accumulated across all six terms, not by a
    favorable/contested count of a fixed tracked-entity set.

Per data/unique_wonder_ritual_specs.yaml's `unique_dome_of_the_rock` entry,
the design_ir names `sanctuary_access_groups` and `custody_duties` as tracked
entity sets and mentions `opposition_pressure` / `site_evidence_status`
variables. This rewrite intentionally does not implement those as literal
per-entity status trackers: the design's own `mechanic_signature` and
`cadence_signature` ask for something that proves custody through *time and
restraint*, not through resolving a fixed list of named stakeholders once.
The three communities here (guardian family / endowment council / garrison
watch) are a compressed, permanent cast standing in for the design's access
groups and custody duties, and `concord` stands in for `opposition_pressure`
as a continuously-accumulating pressure track rather than a per-entity
enum. This keeps the historically distinctive shape (shared, rotating,
negotiated custody over an extended period) while avoiding both dice
(`random_list` was already absent) and the flagged deterministic-branch
retry template.

GUI rendering is bespoke (not `_entity_ritual.append_gui`): the state here is
three continuous accumulator tracks plus a per-community service-count
ledger, not a repeated-entity-row checklist, so a checklist/incident-log
widget shape would not fit.
"""
from . import _entity_ritual as engine
from ._entity_ritual import DASH, NAMESPACE, T

WONDER_ID = 103
WONDER_KEY = "unique_dome_of_the_rock"
NAME_SLUG = "dome_of_the_rock"
RUNTIME_PREFIX = "tv_wonder_dome_of_the_rock"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_dome_of_the_rock_cropped.dds"
LOCATION = "jerusalem"

# Ritual stage machine driven by the monthly dispatcher.
STAGE_OPENING = 0
STAGE_TERM_WAIT = 1
STAGE_UPKEEP_WAIT = 2
STAGE_SEALING_WAIT = 3

OPENING_EVENT_ID = 1662
ASSIGNMENT_EVENT_ID = 1663
UPKEEP_EVENT_ID = 1664
SEALING_EVENT_ID = 1665

TOTAL_TERMS = 6
TERM_LENGTH_MONTHS = 4

# Fixed, permanent cast of custodian communities. Every term the player
# assigns custody of the sanctuary to exactly one of these three -- there is
# no dice roll and no deterministic lookup marking any of them "contested";
# each term's assignment is a live player decision.
COMMUNITIES = [
    {"key": "guardian_family", "value": 1, "en": "Nusaybah Guardian Family", "zh": "努赛贝守门世家"},
    {"key": "waqf_council", "value": 2, "en": "Waqf Endowment Council", "zh": "瓦克夫捐产议事会"},
    {"key": "garrison_watch", "value": 3, "en": "Garrison Platform Watch", "zh": "卫戍平台警戒队"},
]

WONDER = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "modifier_bundles": {
        "tv_wonder_dome_of_the_rock_ritual_reward_modifier": {"tolerance_own": 1.5, "diplomatic_reputation": 2},
        "tv_wonder_dome_of_the_rock_ritual_reward_modifier_lesser": {"tolerance_own": 0.5},
    },
}

KEY_PREFIX = f"TV_ENGINEERING_{NAME_SLUG.upper()}"


def _stage_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_stage"


def _term_index_var() -> str:
    return f"{RUNTIME_PREFIX}_term_index"


def _cooldown_var() -> str:
    return f"{RUNTIME_PREFIX}_term_cooldown_months"


def _previous_holder_var() -> str:
    return f"{RUNTIME_PREFIX}_previous_holder"


def _concord_var() -> str:
    return f"{RUNTIME_PREFIX}_concord"


def _continuity_var() -> str:
    return f"{RUNTIME_PREFIX}_continuity"


def _endowment_var() -> str:
    return f"{RUNTIME_PREFIX}_endowment_health"


def _service_var(community_key: str) -> str:
    return f"{RUNTIME_PREFIX}_service_{community_key}"


def _combined_score_var() -> str:
    return f"{RUNTIME_PREFIX}_combined_score"


def _pending_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_pending_event"


def _completed_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_completed"


# ---------------------------------------------------------------------------
# triggers
# ---------------------------------------------------------------------------

def append_triggers(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_site_control_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_site_control_trigger = {{")
    lines.append(f"{T}owns = location:{LOCATION}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_active_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_active_trigger = {{")
    lines.append(f"{T}has_variable = tv_wonder_locked")
    lines.append(f"{T}var:tv_wonder_locked ?= {WONDER_ID}")
    lines.append(f"{T}has_variable = tv_wonder_ritual_in_progress")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_calendar_strained_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_calendar_strained_trigger = {{")
    lines.append(f"{T}OR = {{")
    lines.append(f"{T}{T}AND = {{ has_variable = {_concord_var()}  var:{_concord_var()} <= 30 }}")
    lines.append(f"{T}{T}AND = {{ has_variable = {_continuity_var()}  var:{_continuity_var()} <= 30 }}")
    lines.append(f"{T}{T}AND = {{ has_variable = {_endowment_var()}  var:{_endowment_var()} <= 20 }}")
    lines.append(f"{T}}}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_endowment_critical_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_endowment_critical_trigger = {{")
    lines.append(f"{T}has_variable = {_endowment_var()}")
    lines.append(f"{T}var:{_endowment_var()} <= 20")
    lines.append("}")


# ---------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------

def _assign_effect(community: dict) -> list[str]:
    effect_name = f"{RUNTIME_PREFIX}_assign_{community['key']}_effect"
    lines = [f"# -- {effect_name} {DASH}", f"{effect_name} = {{"]
    lines.append(f"{T}change_variable = {{ name = {_service_var(community['key'])} add = 1 }}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_previous_holder_var()} ?= {community['value']} }}")
    lines.append(f"{T}{T}change_variable = {{ name = {_concord_var()} add = -1 }}")
    lines.append(f"{T}{T}change_variable = {{ name = {_continuity_var()} add = 2 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}change_variable = {{ name = {_concord_var()} add = 3 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}clamp_variable = {{ name = {_concord_var()} min = 0 max = 100 }}")
    lines.append(f"{T}clamp_variable = {{ name = {_continuity_var()} min = 0 max = 100 }}")
    lines.append(f"{T}set_variable = {{ name = {_previous_holder_var()} value = {community['value']} }}")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = {STAGE_UPKEEP_WAIT} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")
    return lines


def _upkeep_effect(fund: bool) -> list[str]:
    key = "fund" if fund else "defer"
    effect_name = f"{RUNTIME_PREFIX}_upkeep_{key}_effect"
    lines = [f"# -- {effect_name} {DASH}", f"{effect_name} = {{"]
    if fund:
        lines.append(f"{T}change_variable = {{ name = {_endowment_var()} add = 15 }}")
        lines.append(f"{T}add_prestige = -2")
    else:
        lines.append(f"{T}change_variable = {{ name = {_endowment_var()} add = -10 }}")
    lines.append(f"{T}clamp_variable = {{ name = {_endowment_var()} min = 0 max = 100 }}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_term_index_var()} >= {TOTAL_TERMS} }}")
    lines.append(f"{T}{T}set_variable = {{ name = {_stage_var()} value = {STAGE_SEALING_WAIT} }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}change_variable = {{ name = {_term_index_var()} add = 1 }}")
    lines.append(f"{T}{T}set_variable = {{ name = {_cooldown_var()} value = {TERM_LENGTH_MONTHS} }}")
    lines.append(f"{T}{T}set_variable = {{ name = {_stage_var()} value = {STAGE_TERM_WAIT} }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")
    return lines


def append_effects(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_start_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_start_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = {STAGE_OPENING} }}")
    lines.append(f"{T}set_variable = {{ name = {_term_index_var()} value = 1 }}")
    lines.append(f"{T}set_variable = {{ name = {_cooldown_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_previous_holder_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_concord_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_continuity_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_endowment_var()} value = 50 }}")
    for community in COMMUNITIES:
        lines.append(f"{T}set_variable = {{ name = {_service_var(community['key'])} value = 0 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_opening_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_opening_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = {STAGE_TERM_WAIT} }}")
    lines.append(f"{T}set_variable = {{ name = {_cooldown_var()} value = 0 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    for community in COMMUNITIES:
        lines.append("")
        lines.extend(_assign_effect(community))

    lines.append("")
    lines.extend(_upkeep_effect(True))
    lines.append("")
    lines.extend(_upkeep_effect(False))

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_grant_reward_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_grant_reward_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_combined_score_var()} value = 0 }}")
    lines.append(f"{T}change_variable = {{ name = {_combined_score_var()} add = var:{_concord_var()} }}")
    lines.append(f"{T}change_variable = {{ name = {_combined_score_var()} add = var:{_continuity_var()} }}")
    lines.append(f"{T}change_variable = {{ name = {_combined_score_var()} add = var:{_endowment_var()} }}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_combined_score_var()} >= 220 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 15")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_combined_score_var()} >= 150 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 8")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 3")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {_combined_score_var()}")
    lines.append(f"{T}remove_variable = {_stage_var()}")
    lines.append(f"{T}remove_variable = {_term_index_var()}")
    lines.append(f"{T}remove_variable = {_cooldown_var()}")
    lines.append(f"{T}remove_variable = {_previous_holder_var()}")
    lines.append(f"{T}remove_variable = {_concord_var()}")
    lines.append(f"{T}remove_variable = {_continuity_var()}")
    lines.append(f"{T}remove_variable = {_endowment_var()}")
    for community in COMMUNITIES:
        lines.append(f"{T}remove_variable = {_service_var(community['key'])}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append(f"{T}set_variable = {{ name = {_completed_var()} value = 1 }}")
    lines.append(f"{T}tv_wonder_complete_active_ritual_effect = yes")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_monthly_progress_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_monthly_progress_effect = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{")
    lines.append(f"{T}{T}{T}{RUNTIME_PREFIX}_active_trigger = yes")
    lines.append(f"{T}{T}{T}NOT = {{ has_variable = {_pending_var()} }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_OPENING} {RUNTIME_PREFIX}_site_control_trigger = yes }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{OPENING_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_TERM_WAIT} }}")
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ var:{_cooldown_var()} >= 1 }}")
    lines.append(f"{T}{T}{T}{T}change_variable = {{ name = {_cooldown_var()} add = -1 }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}else = {{")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{ASSIGNMENT_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_UPKEEP_WAIT} }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{UPKEEP_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_SEALING_WAIT} }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{SEALING_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append("}")


# ---------------------------------------------------------------------------
# events
# ---------------------------------------------------------------------------

def build_events_body() -> list[str]:
    lines: list[str] = []

    lines.append(f"# -- {NAMESPACE}.{OPENING_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{OPENING_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{OPENING_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{OPENING_EVENT_ID}.d")
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{OPENING_EVENT_ID}.a")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_active_trigger = yes {RUNTIME_PREFIX}_site_control_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_opening_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{ASSIGNMENT_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{ASSIGNMENT_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{ASSIGNMENT_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{ASSIGNMENT_EVENT_ID}.d")
    lines.append(f"{T}triggered_desc = {{")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_calendar_strained_trigger = yes }}")
    lines.append(f"{T}{T}desc = {NAMESPACE}.{ASSIGNMENT_EVENT_ID}.strained.d")
    lines.append(f"{T}}}")
    lines.append(f"{T}outcome = neutral")
    for letter, community in zip("abc", COMMUNITIES):
        lines.append("")
        lines.append(f"{T}option = {{")
        lines.append(f"{T}{T}name = {NAMESPACE}.{ASSIGNMENT_EVENT_ID}.{letter}")
        lines.append(f"{T}{T}{RUNTIME_PREFIX}_assign_{community['key']}_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{UPKEEP_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{UPKEEP_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{UPKEEP_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{UPKEEP_EVENT_ID}.d")
    lines.append(f"{T}triggered_desc = {{")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_endowment_critical_trigger = yes }}")
    lines.append(f"{T}{T}desc = {NAMESPACE}.{UPKEEP_EVENT_ID}.critical.d")
    lines.append(f"{T}}}")
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{UPKEEP_EVENT_ID}.a")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_upkeep_fund_effect = yes")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{UPKEEP_EVENT_ID}.b")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_upkeep_defer_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{SEALING_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{SEALING_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{SEALING_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{SEALING_EVENT_ID}.d")
    lines.append(f"{T}outcome = positive")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{SEALING_EVENT_ID}.a")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_ritual_grant_reward_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")

    return lines


# ---------------------------------------------------------------------------
# localization
# ---------------------------------------------------------------------------

_EVENTS_TEXT = {
    "english": {
        OPENING_EVENT_ID: {
            "t": "A Calendar of Shared Custody",
            "d": "The commissioner proposes something the sanctuary has never had under this reign: a fixed calendar of shared custody. Rather than settling access once and for all, the Nusaybah guardian family, the Waqf endowment council, and the garrison's platform watch will each hold the keys in turn, across six terms spanning several years, with the sponsor's own record of fairness and upkeep becoming the true measure of the covenant.",
            "options": {
                "a": "Open the calendar of shared custody.",
            },
        },
        ASSIGNMENT_EVENT_ID: {
            "t": "The Term Falls Due",
            "d": "A term of the custody calendar has come due. The keys, the watch-lists, and the standing before pilgrims must pass to whichever party the sponsor names for this term. Rotating custody preserves the appearance of impartial rule, but returning the same party to office builds administrative memory the sanctuary can rely on.",
            "strained_d": "The record so far has not been kind: fairness, continuity, or the endowment's own upkeep -- one or more of the calendar's three measures is already faltering, and this term's choice will not undo that on its own.",
            "options": {
                "a": "Entrust this term to the Nusaybah Guardian Family.",
                "b": "Entrust this term to the Waqf Endowment Council.",
                "c": "Entrust this term to the Garrison Platform Watch.",
            },
        },
        UPKEEP_EVENT_ID: {
            "t": "Funding the Term's Upkeep",
            "d": "The lamps, cisterns, and gate timbers of the platform need constant tending, and this term's custodian has presented the bill. The sponsor may commit personal prestige to see the endowment funded in full, or let this term's maintenance lapse and let the fabric of the sanctuary wear a little more.",
            "critical_d": "The endowment's fabric is now in visibly poor repair -- lamps unlit, cisterns fouled, gate timbers rotting. Another lapsed term risks real damage to the platform itself.",
            "options": {
                "a": "Commit prestige to fund the endowment in full. (-2 prestige)",
                "b": "Let this term's maintenance lapse.",
            },
        },
        SEALING_EVENT_ID: {
            "t": "The Calendar Is Completed",
            "d": "Six terms have passed, and the custody calendar is complete. The record now stands: how often custody rotated fairly, how often the same hands kept it steady, and how well the platform's fabric was kept -- that record, not any single day's proclamation, is what history will call the Dome's true custody.",
            "options": {
                "a": "Seal the completed calendar.",
            },
        },
    },
    "simp_chinese": {
        OPENING_EVENT_ID: {
            "t": "共享监护的历法",
            "d": "专员提议这座圣所在本朝从未有过的安排：一份固定的共享监护历法。此举并非一次性地敲定门禁，而是让努赛贝守门世家、瓦克夫捐产议事会与卫戍平台警戒队依次执掌钥匙，历经六个任期、跨越数年，赞助者自身在公正与维护上的记录才是这份盟约真正的度量。",
            "options": {
                "a": "开启共享监护历法。",
            },
        },
        ASSIGNMENT_EVENT_ID: {
            "t": "任期已至",
            "d": "监护历法的一个任期已经到期。钥匙、值守名册与在朝圣者面前的地位，必须移交给赞助者为本任期指定的一方——轮换监护能保持公正统治的形象，而让同一方连任则能积累圣所可以倚仗的行政经验。",
            "strained_d": "迄今为止的记录并不乐观：公正、延续性或基金会自身的维护——历法三项度量中至少有一项已经出现问题，本任期的选择本身并不能就此扭转局面。",
            "options": {
                "a": "本任期交由努赛贝守门世家执掌。",
                "b": "本任期交由瓦克夫捐产议事会执掌。",
                "c": "本任期交由卫戍平台警戒队执掌。",
            },
        },
        UPKEEP_EVENT_ID: {
            "t": "任期维护经费",
            "d": "平台上的灯盏、蓄水池与门扉木构需要持续维护，本任期的监护人已呈上账目。赞助者可投入个人声望以全额资助基金会，也可让本任期的维护搁置，任由圣所构造多耗损一分。",
            "critical_d": "基金会的构造如今已明显破败——灯盏不亮，蓄水池污浊，门扉木构朽坏。再搁置一个任期恐将令平台本身遭受实质损害。",
            "options": {
                "a": "投入声望，全额资助基金会。（声望 -2）",
                "b": "让本任期的维护搁置。",
            },
        },
        SEALING_EVENT_ID: {
            "t": "历法圆满",
            "d": "六个任期已经过去，监护历法圆满完成。记录已经写定：监护轮换是否公正、同一方连任是否带来了稳定、平台构造是否维护得当——正是这份记录，而非某一日的宣告，才是历史将会承认的圆顶真正监护。",
            "options": {
                "a": "封印圆满的历法。",
            },
        },
    },
}


def build_localization(language: str) -> list[str]:
    lang_index = 0 if language == "english" else 1
    lines: list[str] = []

    for event_id in (OPENING_EVENT_ID, ASSIGNMENT_EVENT_ID, UPKEEP_EVENT_ID, SEALING_EVENT_ID):
        text = _EVENTS_TEXT[language][event_id]
        lines.append(f' {NAMESPACE}.{event_id}.t:0 "{text["t"]}"')
        lines.append(f' {NAMESPACE}.{event_id}.d:0 "{text["d"]}"')
        if "critical_d" in text:
            lines.append(f' {NAMESPACE}.{event_id}.critical.d:0 "{text["critical_d"]}"')
        if "strained_d" in text:
            lines.append(f' {NAMESPACE}.{event_id}.strained.d:0 "{text["strained_d"]}"')
        for letter, option_text in text["options"].items():
            lines.append(f' {NAMESPACE}.{event_id}.{letter}:0 "{option_text}"')

    lines.append(f' {KEY_PREFIX}_CARD_TITLE:0 "{"Custody Calendar" if language == "english" else "监护历法"}"')
    lines.append(f' {KEY_PREFIX}_TERM_LABEL:0 "{"Term" if language == "english" else "任期"}"')
    lines.append(f' {KEY_PREFIX}_CONCORD_LABEL:0 "{"Concord" if language == "english" else "共识"}"')
    lines.append(f' {KEY_PREFIX}_CONTINUITY_LABEL:0 "{"Continuity" if language == "english" else "延续性"}"')
    lines.append(f' {KEY_PREFIX}_ENDOWMENT_LABEL:0 "{"Endowment Health" if language == "english" else "基金会状况"}"')

    name_field = "en" if language == "english" else "zh"
    for community in COMMUNITIES:
        lines.append(f' {KEY_PREFIX}_COMMUNITY_{community["key"].upper()}:0 "{community[name_field]}"')

    for modifier_name in WONDER["modifier_bundles"]:
        label = engine._modifier_display_name(WONDER, modifier_name, language)
        lines.append(f' STATIC_MODIFIER_NAME_{modifier_name}:0 "{label}"')

    return lines


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

CARD_WIDTH = 462


def _stat_row(indent: int, label_key: str, var_name: str, helpers: dict[str, object]) -> list[str]:
    prefix = T * indent
    player_var = helpers["player_var"]
    var_expr = player_var(var_name)
    lines = [
        f"{prefix}hbox = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {CARD_WIDTH - 16} 20 }}",
        f"{prefix}{T}spacing = 6",
        f'{prefix}{T}text_single = {{ text = "{label_key}" size = {{ 120 20 }} fontsize = 12 align = nobaseline|left }}',
        f"{prefix}{T}widget = {{",
        f"{prefix}{T}{T}size = {{ 260 16 }}",
        f"{prefix}{T}{T}progressbar = {{",
        f'{prefix}{T}{T}{T}visible = "[{var_expr}.IsSet]"',
        f"{prefix}{T}{T}{T}size = {{ 260 16 }}",
        f"{prefix}{T}{T}{T}using = progress_bar_goldish",
        f"{prefix}{T}{T}{T}min = 0",
        f"{prefix}{T}{T}{T}max = 100",
        f'{prefix}{T}{T}{T}value = "[{var_expr}.GetValue]"',
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}{T}progressbar = {{",
        f'{prefix}{T}{T}{T}visible = "[Not({var_expr}.IsSet)]"',
        f"{prefix}{T}{T}{T}size = {{ 260 16 }}",
        f"{prefix}{T}{T}{T}using = progress_bar_goldish",
        f"{prefix}{T}{T}{T}min = 0",
        f"{prefix}{T}{T}{T}max = 100",
        f"{prefix}{T}{T}{T}value = 0",
        f"{prefix}{T}{T}}}",
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]
    return lines


def _service_row(indent: int, community: dict, helpers: dict[str, object]) -> list[str]:
    prefix = T * indent
    player_var = helpers["player_var"]
    var_expr = player_var(_service_var(community["key"]))
    label_key = f"{KEY_PREFIX}_COMMUNITY_{community['key'].upper()}"
    lines = [
        f"{prefix}hbox = {{",
        f"{prefix}{T}layoutpolicy_horizontal = expanding",
        f"{prefix}{T}layoutpolicy_vertical = fixed",
        f"{prefix}{T}size = {{ {CARD_WIDTH - 16} 18 }}",
        f"{prefix}{T}spacing = 6",
        f'{prefix}{T}text_single = {{ text = "{label_key}" size = {{ 320 18 }} max_width = 320 fontsize = 11 align = nobaseline|left }}',
        f"{prefix}{T}text_single = {{",
        f'{prefix}{T}{T}visible = "[{var_expr}.IsSet]"',
        f'{prefix}{T}{T}raw_text = "[{var_expr}.GetValue|0]"',
        f"{prefix}{T}{T}fontsize = 11",
        f"{prefix}{T}{T}align = nobaseline|right",
        f"{prefix}{T}}}",
        f"{prefix}{T}text_single = {{",
        f'{prefix}{T}{T}visible = "[Not({var_expr}.IsSet)]"',
        f'{prefix}{T}{T}raw_text = "0"',
        f"{prefix}{T}{T}fontsize = 11",
        f"{prefix}{T}{T}align = nobaseline|right",
        f"{prefix}{T}}}",
        f"{prefix}}}",
    ]
    return lines


def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    prefix = T * indent
    eq = helpers["eq"]
    player_var = helpers["player_var"]
    active_ritual_visible = helpers["active_ritual_visible"]

    locked_expr = f"And({player_var('tv_wonder_locked')}.IsSet, {eq('tv_wonder_locked', WONDER_ID)})"
    card_visible = f"And({active_ritual_visible()}, {locked_expr})"
    card_height = 20 + 22 + 3 * 22 + len(COMMUNITIES) * 20 + 14 + 4 * 7

    lines.append(f"{prefix}widget = {{")
    lines.append(f'{prefix}{T}visible = "[{card_visible}]"')
    lines.append(f"{prefix}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}layoutpolicy_vertical = fixed")
    lines.append(f"{prefix}{T}size = {{ {CARD_WIDTH} {card_height} }}")
    lines.append(f"{prefix}{T}using = bg_text_mask_container_dark_blue")
    lines.append("")
    lines.append(f"{prefix}{T}vbox = {{")
    lines.append(f"{prefix}{T}{T}margin = {{ 8 7 }}")
    lines.append(f"{prefix}{T}{T}ignoreinvisible = yes")
    lines.append(f"{prefix}{T}{T}spacing = 4")
    lines.append(f'{prefix}{T}{T}text_single = {{ text = "{KEY_PREFIX}_CARD_TITLE" fontsize = 16 align = nobaseline|left }}')

    term_expr = player_var(_term_index_var())
    lines.append(f"{prefix}{T}{T}hbox = {{")
    lines.append(f"{prefix}{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}{T}{T}spacing = 6")
    lines.append(f'{prefix}{T}{T}{T}text_single = {{ text = "{KEY_PREFIX}_TERM_LABEL" size = {{ 120 20 }} fontsize = 12 align = nobaseline|left }}')
    lines.append(f"{prefix}{T}{T}{T}text_single = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}visible = "[{term_expr}.IsSet]"')
    lines.append(f'{prefix}{T}{T}{T}{T}raw_text = "[{term_expr}.GetValue|0]/{TOTAL_TERMS}"')
    lines.append(f"{prefix}{T}{T}{T}{T}fontsize = 12")
    lines.append(f"{prefix}{T}{T}{T}{T}align = nobaseline|right")
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}{T}text_single = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}visible = "[Not({term_expr}.IsSet)]"')
    lines.append(f'{prefix}{T}{T}{T}{T}raw_text = "0/{TOTAL_TERMS}"')
    lines.append(f"{prefix}{T}{T}{T}{T}fontsize = 12")
    lines.append(f"{prefix}{T}{T}{T}{T}align = nobaseline|right")
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}}}")

    lines.extend(_stat_row(indent + 2, f"{KEY_PREFIX}_CONCORD_LABEL", _concord_var(), helpers))
    lines.extend(_stat_row(indent + 2, f"{KEY_PREFIX}_CONTINUITY_LABEL", _continuity_var(), helpers))
    lines.extend(_stat_row(indent + 2, f"{KEY_PREFIX}_ENDOWMENT_LABEL", _endowment_var(), helpers))

    for community in COMMUNITIES:
        lines.extend(_service_row(indent + 2, community, helpers))

    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
