"""Bank of Saint George (unique_bank_of_saint_george) ritual content.

Second bespoke rewrite. The first bespoke rewrite (2026-07) replaced the
shared `_entity_ritual` engine with a hand-written "choose 1 of 3 founding
charters -> the charter deterministically marks 2 of 6 public-credit pledges
`distrusted` -> one credit-incident event offers guarantee-with-gold vs
narrow-for-free -> reward scaled by favorable-pledge count" mechanic. That
shape is exactly what `scripts/audit_unique_wonder_ritual_mechanic_similarity.py`
flagged as a *new* homogenized template: it scored `combined_ratio` 0.48-0.71
against Dome of the Rock and St. Peter's Basilica even with all dice removed
and all variables renamed, because "choice -> deterministic branch marking a
fixed subset of entities at risk -> one retry/incident event offering
pay-to-fully-resolve vs accept-narrower-for-free -> threshold reward" is
itself a template (see docs/knowledge/risk_cards/wonders.md rule 13).

This rewrite drops that shape entirely and instead models what actually made
the historical Casa di San Giorgio distinctive: it was not a one-shot
political negotiation, it was a *funded, amortizing public debt* — a running
principal that accrues interest and is paid down by pledged tax revenue over
years, racing toward zero before a restructuring deadline. Concretely:

  1. Opening event (1670): convene the compere assembly. Single option, gated
     by `owns = location:genoa` (site control), starts the state machine.
  2. Charter event (1671): the player picks one of 3 founding charters. Unlike
     the previous version, the charter choice does not flag any entity as
     "distrusted" — it sets the *numeric parameters* of a real amortization
     schedule (starting principal, a fixed monthly interest fraction, a fixed
     monthly pledge paydown, and a one-time chartering cost paid in gold).
  3. Amortization (stage 2, no dedicated event): every month, while the
     ritual is active, `tv_wonder_bank_of_saint_george_ritual_monthly_progress_effect`
     (the same shared dispatcher name the on_action pulse already calls)
     accrues interest onto the outstanding principal
     (`change_variable = { name = principal add = { value = var:principal
     multiply = var:interest_rate } } }`, verified pattern — see
     `western_schism.txt:257-261`) and subtracts the fixed monthly pledge.
     This is genuinely arithmetic and genuinely time-extended: dozens of
     months pass with no event at all while the ledger runs, exactly the
     "monetary balance racing toward a target over years" shape the debt
     institution is actually known for, rather than one instant negotiation.
  4. Ledger Assembly event (1672) is a *recurring* checkpoint (every 12
     elapsed months while stage 2 is running, tracked by a
     `next_review_month` variable, not a one-shot retry). It offers three
     real options, not a binary pay/accept: prepay a lump sum with treasury
     gold (fastest), permanently requisition more pledged revenue (no gold
     cost, but a lasting commitment), or hold steady (no change). This can
     fire zero, one, or many times over a single ritual's run — there is no
     fixed "one retry then done" structure.
  5. Completion is autonomous, not player-confirmed: the monthly effect
     itself detects `principal <= 0` (paid off) or `elapsed_months >= 96`
     (8-year restructuring deadline) and picks one of 4 outcome tiers keyed
     on *how fast* the debt was retired (or whether it wasn't, before the
     deadline). Reward event (1673) just presents the already-decided
     outcome; the decision axis is elapsed time, not a favorable-entity
     count, which is the axis the audit flagged as reused across all three
     rewritten wonders.

No `random_list` anywhere. No per-entity status enum. No "mark N of M
entities as distrusted" branch. The only thing this shares with the previous
version is the founding-charter framing (kept because it is the historically
correct hook) and the general "opening -> branch -> running state -> reward"
shared plumbing every Engineering Department ritual must use (stage var +
pending-event guard + `tv_wonder_complete_active_ritual_effect`).

Deviation from `data/unique_wonder_ritual_specs.yaml`'s
`unique_bank_of_saint_george` entry: that spec's `node_graph` (entry node
`bank_opening` -> `bank_charter_branch` -> `bank_credit_incident` retry loop
-> `bank_reward`, cadence_type `instant_but_branching`) is precisely the
generic branch-then-incident shape being retired here — it is the design
source that led to the homogenization in the first place, since the same
`instant_but_branching` / "charter marks entities at risk, one incident event
resolves it" shape was independently given to Dome of the Rock and St.
Peter's Basilica too. This module keeps the spec's historical anchor (public
credit, pledged revenue, coin trust, merchant/crown/creditor charter framing)
and its 4 pre-allocated event IDs, but replaces `cadence_type:
instant_but_branching` with a genuinely multi-year amortization loop
(`monthly_institutionalization`-shaped, driven through the existing
`*_ritual_monthly_progress_effect` dispatcher already wired into
`tv_engineering_department_ritual_monthly_pulse`), and replaces the single
retry/incident node with a recurring, 3-option assembly checkpoint plus an
autonomous time-tiered completion, per the explicit instruction to deviate
from a spec whose own node_graph is the thing causing the homogenization.
"""
from . import _entity_ritual as engine
from ._entity_ritual import DASH, NAMESPACE, T

WONDER_ID = 122
WONDER_KEY = "unique_bank_of_saint_george"
NAME_SLUG = "bank_of_saint_george"
RUNTIME_PREFIX = "tv_wonder_bank_of_saint_george"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_bank_of_saint_george_cropped.dds"
LOCATION = "genoa"

OPENING_EVENT_ID = 1670
CHARTER_EVENT_ID = 1671
ASSEMBLY_EVENT_ID = 1672
REWARD_EVENT_ID = 1673

# The amortization schedule. Each charter sets the *numeric* parameters of a
# running funded-debt principal -- no entity is marked "at risk"; the choice
# is about how fast and how expensively the debt gets consolidated.
CHARTERS = {
    "conservative_sinking_fund": {
        "value": 1,
        "en": "Conservative Sinking Fund Charter",
        "zh": "保守偿债基金宪章",
        "principal_start": 80,
        "interest_rate": 0.02,
        "monthly_pledge": 6,
        "charter_cost_scale": -2,
    },
    "balanced_compere": {
        "value": 2,
        "en": "Balanced Compere Charter",
        "zh": "均衡公债宪章",
        "principal_start": 110,
        "interest_rate": 0.025,
        "monthly_pledge": 9,
        "charter_cost_scale": -4,
    },
    "aggressive_consolidation": {
        "value": 3,
        "en": "Aggressive Consolidation Charter",
        "zh": "激进整合宪章",
        "principal_start": 150,
        "interest_rate": 0.03,
        "monthly_pledge": 14,
        "charter_cost_scale": -7,
    },
}
CHARTER_ORDER = ["conservative_sinking_fund", "balanced_compere", "aggressive_consolidation"]

MAX_MONTHS = 96
REVIEW_INTERVAL_MONTHS = 12
TIER_FAST_MONTHS = 24
TIER_MEDIUM_MONTHS = 60

ASSEMBLY_PREPAY_GOLD_SCALE = -5
ASSEMBLY_PREPAY_PRINCIPAL_REDUCTION = 15
ASSEMBLY_REQUISITION_PLEDGE_INCREASE = 2

WONDER = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "modifier_bundles": {
        "tv_wonder_bank_of_saint_george_ritual_reward_modifier": {"minting_income_factor": 0.15, "tax_income_efficiency": 0.1},
        "tv_wonder_bank_of_saint_george_ritual_reward_modifier_partial": {"minting_income_factor": 0.09, "tax_income_efficiency": 0.06},
        "tv_wonder_bank_of_saint_george_ritual_reward_modifier_lesser": {"minting_income_factor": 0.04},
    },
}

KEY_PREFIX = f"TV_ENGINEERING_{NAME_SLUG.upper()}"


def _stage_var() -> str:
    return f"{RUNTIME_PREFIX}_stage"


def _pending_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_pending_event"


def _completed_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_completed"


def _charter_branch_var() -> str:
    return f"{RUNTIME_PREFIX}_charter_branch"


def _principal_var() -> str:
    return f"{RUNTIME_PREFIX}_principal"


def _principal_start_var() -> str:
    return f"{RUNTIME_PREFIX}_principal_start"


def _interest_rate_var() -> str:
    return f"{RUNTIME_PREFIX}_interest_rate"


def _monthly_pledge_var() -> str:
    return f"{RUNTIME_PREFIX}_monthly_pledge"


def _elapsed_months_var() -> str:
    return f"{RUNTIME_PREFIX}_elapsed_months"


def _next_review_month_var() -> str:
    return f"{RUNTIME_PREFIX}_next_review_month"


def _outcome_tier_var() -> str:
    return f"{RUNTIME_PREFIX}_outcome_tier"


def _progress_pct_var() -> str:
    return f"{RUNTIME_PREFIX}_progress_pct"


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
    lines.append(f"# -- {RUNTIME_PREFIX}_debt_outstanding_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_debt_outstanding_trigger = {{")
    lines.append(f"{T}has_variable = {_principal_var()}")
    lines.append(f"{T}var:{_principal_var()} > 0")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_amortization_race_close_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_amortization_race_close_trigger = {{")
    lines.append(f"{T}AND = {{")
    lines.append(f"{T}{T}has_variable = {_elapsed_months_var()}")
    lines.append(f"{T}{T}has_variable = {_principal_var()}")
    lines.append(f"{T}{T}var:{_elapsed_months_var()} >= {MAX_MONTHS - REVIEW_INTERVAL_MONTHS}")
    lines.append(f"{T}{T}var:{_principal_var()} > 0")
    lines.append(f"{T}}}")
    lines.append("}")


# ---------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------

def _charter_choice_effect(charter_key: str) -> list[str]:
    charter = CHARTERS[charter_key]
    effect_name = f"{RUNTIME_PREFIX}_choose_{charter_key}_effect"
    lines = [f"# -- {effect_name} {DASH}", f"{effect_name} = {{"]
    lines.append(f"{T}set_variable = {{ name = {_charter_branch_var()} value = {charter['value']} }}")
    lines.append(f"{T}set_variable = {{ name = {_principal_start_var()} value = {charter['principal_start']} }}")
    lines.append(f"{T}set_variable = {{ name = {_principal_var()} value = {charter['principal_start']} }}")
    lines.append(f"{T}set_variable = {{ name = {_interest_rate_var()} value = {charter['interest_rate']} }}")
    lines.append(f"{T}set_variable = {{ name = {_monthly_pledge_var()} value = {charter['monthly_pledge']} }}")
    lines.append(f"{T}set_variable = {{ name = {_elapsed_months_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_next_review_month_var()} value = {REVIEW_INTERVAL_MONTHS} }}")
    lines.append(f"{T}set_variable = {{ name = {_progress_pct_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 2 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append(f"{T}change_gold_effect = {{ scale = {charter['charter_cost_scale']} }}")
    lines.append("}")
    return lines


def append_effects(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_start_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_start_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 0 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_opening_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_opening_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 1 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    for charter_key in CHARTER_ORDER:
        lines.append("")
        lines.extend(_charter_choice_effect(charter_key))

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_assembly_prepay_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_assembly_prepay_effect = {{")
    lines.append(f"{T}change_gold_effect = {{ scale = {ASSEMBLY_PREPAY_GOLD_SCALE} }}")
    lines.append(f"{T}change_variable = {{ name = {_principal_var()} subtract = {ASSEMBLY_PREPAY_PRINCIPAL_REDUCTION} }}")
    lines.append(f"{T}change_variable = {{ name = {_next_review_month_var()} add = {REVIEW_INTERVAL_MONTHS} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_assembly_requisition_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_assembly_requisition_effect = {{")
    lines.append(f"{T}change_variable = {{ name = {_monthly_pledge_var()} add = {ASSEMBLY_REQUISITION_PLEDGE_INCREASE} }}")
    lines.append(f"{T}change_variable = {{ name = {_next_review_month_var()} add = {REVIEW_INTERVAL_MONTHS} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_assembly_hold_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_assembly_hold_effect = {{")
    lines.append(f"{T}change_variable = {{ name = {_next_review_month_var()} add = {REVIEW_INTERVAL_MONTHS} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_grant_reward_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_grant_reward_effect = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_outcome_tier_var()} ?= 1 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 5 }}")
    lines.append(f"{T}{T}add_prestige = 5")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_outcome_tier_var()} ?= 2 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_partial years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 3 }}")
    lines.append(f"{T}{T}add_prestige = 2")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_outcome_tier_var()} ?= 3 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 1 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = -2")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {_charter_branch_var()}")
    lines.append(f"{T}remove_variable = {_principal_var()}")
    lines.append(f"{T}remove_variable = {_principal_start_var()}")
    lines.append(f"{T}remove_variable = {_interest_rate_var()}")
    lines.append(f"{T}remove_variable = {_monthly_pledge_var()}")
    lines.append(f"{T}remove_variable = {_elapsed_months_var()}")
    lines.append(f"{T}remove_variable = {_next_review_month_var()}")
    lines.append(f"{T}remove_variable = {_outcome_tier_var()}")
    lines.append(f"{T}remove_variable = {_progress_pct_var()}")
    lines.append(f"{T}remove_variable = {_stage_var()}")
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
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= 0 {RUNTIME_PREFIX}_site_control_trigger = yes }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{OPENING_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= 1 }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{CHARTER_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= 2 }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {RUNTIME_PREFIX}_interest_accrual value = var:{_principal_var()} }}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_interest_accrual multiply = var:{_interest_rate_var()} }}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = {_principal_var()} add = var:{RUNTIME_PREFIX}_interest_accrual }}")
    lines.append(f"{T}{T}{T}remove_variable = {RUNTIME_PREFIX}_interest_accrual")
    lines.append(f"{T}{T}{T}change_variable = {{ name = {_principal_var()} subtract = var:{_monthly_pledge_var()} }}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = {_elapsed_months_var()} add = 1 }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_progress_pct_var()} value = var:{_elapsed_months_var()} }}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = {_progress_pct_var()} multiply = 100 }}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = {_progress_pct_var()} divide = {MAX_MONTHS} }}")
    lines.append(f"{T}{T}{T}clamp_variable = {{ name = {_progress_pct_var()} min = 0 max = 100 }}")
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ OR = {{ var:{_principal_var()} <= 0  var:{_elapsed_months_var()} >= {MAX_MONTHS} }} }}")
    lines.append(f"{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ var:{_principal_var()} <= 0  var:{_elapsed_months_var()} <= {TIER_FAST_MONTHS} }}")
    lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {_outcome_tier_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ var:{_principal_var()} <= 0  var:{_elapsed_months_var()} <= {TIER_MEDIUM_MONTHS} }}")
    lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {_outcome_tier_var()} value = 2 }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ var:{_principal_var()} <= 0 }}")
    lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {_outcome_tier_var()} value = 3 }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}else = {{")
    lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {_outcome_tier_var()} value = 4 }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {_stage_var()} value = 3 }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ var:{_elapsed_months_var()} >= var:{_next_review_month_var()} }}")
    lines.append(f"{T}{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{ASSEMBLY_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= 3 }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{REWARD_EVENT_ID} days = 1 }}")
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

    lines.append(f"# -- {NAMESPACE}.{CHARTER_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{CHARTER_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{CHARTER_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{CHARTER_EVENT_ID}.d")
    lines.append(f"{T}outcome = neutral")
    for letter, charter_key in zip("abc", CHARTER_ORDER):
        lines.append("")
        lines.append(f"{T}option = {{")
        lines.append(f"{T}{T}name = {NAMESPACE}.{CHARTER_EVENT_ID}.{letter}")
        lines.append(f"{T}{T}{RUNTIME_PREFIX}_choose_{charter_key}_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{ASSEMBLY_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{ASSEMBLY_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{ASSEMBLY_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{ASSEMBLY_EVENT_ID}.d")
    lines.append(f"{T}triggered_desc = {{")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_amortization_race_close_trigger = yes }}")
    lines.append(f"{T}{T}desc = {NAMESPACE}.{ASSEMBLY_EVENT_ID}.race_close.d")
    lines.append(f"{T}}}")
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{ASSEMBLY_EVENT_ID}.a")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_debt_outstanding_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_assembly_prepay_effect = yes")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{ASSEMBLY_EVENT_ID}.b")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_debt_outstanding_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_assembly_requisition_effect = yes")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{ASSEMBLY_EVENT_ID}.c")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_assembly_hold_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{REWARD_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{REWARD_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{REWARD_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{REWARD_EVENT_ID}.d")
    lines.append(f"{T}outcome = positive")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{REWARD_EVENT_ID}.a")
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
            "t": "The Compere Ledger Convenes",
            "d": "The doge's officers, Anziani, merchant creditors, notaries, mint masters, and customs farmers gather to found a funded public debt: a single compere ledger, backed by pledged revenue, that will pay itself down over years rather than remain a floating obligation forever.",
            "options": {
                "a": "Convene the compere assembly.",
            },
        },
        CHARTER_EVENT_ID: {
            "t": "The Founding Charter",
            "d": "Three charters would fund the consolidated debt differently. The Conservative Sinking Fund borrows least and grows slowest, but is cheapest to found and safest to service. The Balanced Compere borrows more at a middling pace. The Aggressive Consolidation borrows heavily to retire old obligations at once, at a steep founding cost and a heavier monthly service burden.",
            "options": {
                "a": "Conservative Sinking Fund Charter. (-2 treasury; smaller debt, modest pledge, patient schedule.)",
                "b": "Balanced Compere Charter. (-4 treasury; moderate debt and pledge.)",
                "c": "Aggressive Consolidation Charter. (-7 treasury; largest debt, heaviest pledge, fastest possible payoff.)",
            },
        },
        ASSEMBLY_EVENT_ID: {
            "t": "The Ledger Assembly Convenes",
            "d": "As the compere ledger runs its course, the assembly of creditors and officers periodically reviews its pace. The debt can be pushed toward faster retirement, or left to its charter's own schedule.",
            "race_close_d": "The restructuring deadline is now close, and the ledger is still not clear. Without a decisive push, the compere debt risks being forced into restructuring rather than retired on the assembly's own terms.",
            "options": {
                "a": "Advance a lump sum from the treasury to retire debt early. (-5 treasury)",
                "b": "Requisition additional pledged revenue permanently.",
                "c": "Maintain steady administration; change nothing.",
            },
        },
        REWARD_EVENT_ID: {
            "t": "The Seal of San Giorgio",
            "d": "Whether retired ahead of schedule, on schedule, after long patience, or restructured at the deadline, the compere ledger is sealed. San Giorgio's authority over Genoa's public credit, pledged revenue, and coin trust is now permanent.",
            "options": {
                "a": "Seal the compere ledger.",
            },
        },
    },
    "simp_chinese": {
        OPENING_EVENT_ID: {
            "t": "公债账簿的召集",
            "d": "总督的官员、长老会、商人债权人、公证人、铸币官与关税承包人齐聚一堂，筹建一份有资金支持的公共债务：一份由抵押收入担保的统一公债账簿，将在数年间自行偿清，而非永远悬而未决。",
            "options": {
                "a": "召集公债会议。",
            },
        },
        CHARTER_EVENT_ID: {
            "t": "创立宪章",
            "d": "三份宪章将以不同方式为整合后的债务提供资金。保守偿债基金借贷最少、增长最慢，但创立成本最低、偿还也最稳妥。均衡公债以中等速度借贷更多。激进整合大举借贷以一次性偿清旧债，创立成本高昂，每月偿付负担也更重。",
            "options": {
                "a": "保守偿债基金宪章。（国库 -2；债务较小、抵押较少、进度从容。）",
                "b": "均衡公债宪章。（国库 -4；债务与抵押适中。）",
                "c": "激进整合宪章。（国库 -7；债务最大、抵押最重，但偿清速度最快。）",
            },
        },
        ASSEMBLY_EVENT_ID: {
            "t": "账簿会议的召集",
            "d": "随着公债账簿逐步推进，债权人与官员组成的会议会定期审视其进度。债务可以被推动更快偿清，也可以按宪章原定的节奏自行运行。",
            "race_close_d": "重组期限已经临近，账簿仍未清偿完毕。若不果断推动，这份公债恐将被迫按期重组，而非按会议自身的条件偿清。",
            "options": {
                "a": "从国库拨付一笔款项以提前偿还债务。（国库 -5）",
                "b": "永久性地征调更多抵押收入。",
                "c": "维持现状，不作改变。",
            },
        },
        REWARD_EVENT_ID: {
            "t": "圣乔治的印信",
            "d": "无论是提前偿清、按期偿清、历经长久耐心偿清，还是在期限届满时被迫重组，公债账簿如今都已封印。圣乔治对热那亚公共信贷、抵押收入与货币信用的权威由此永久确立。",
            "options": {
                "a": "封印公债账簿。",
            },
        },
    },
}


def build_localization(language: str) -> list[str]:
    lang_index = 0 if language == "english" else 1
    name_field = "en" if language == "english" else "zh"
    lines: list[str] = []

    for event_id in (OPENING_EVENT_ID, CHARTER_EVENT_ID, ASSEMBLY_EVENT_ID, REWARD_EVENT_ID):
        text = _EVENTS_TEXT[language][event_id]
        lines.append(f' {NAMESPACE}.{event_id}.t:0 "{text["t"]}"')
        lines.append(f' {NAMESPACE}.{event_id}.d:0 "{text["d"]}"')
        if "race_close_d" in text:
            lines.append(f' {NAMESPACE}.{event_id}.race_close.d:0 "{text["race_close_d"]}"')
        for letter, option_text in text["options"].items():
            lines.append(f' {NAMESPACE}.{event_id}.{letter}:0 "{option_text}"')

    label_words = ("Bank of Saint George — Funded Debt", "圣乔治银行——公债基金")
    lines.append(f' {KEY_PREFIX}_LABEL:0 "{label_words[lang_index]}"')

    for charter_key in CHARTER_ORDER:
        charter = CHARTERS[charter_key]
        lines.append(f' {KEY_PREFIX}_CHARTER_{charter_key.upper()}:0 "{charter[name_field]}"')

    for modifier_name in WONDER["modifier_bundles"]:
        label = engine._modifier_display_name(WONDER, modifier_name, language)
        lines.append(f' STATIC_MODIFIER_NAME_{modifier_name}:0 "{label}"')

    return lines


# ---------------------------------------------------------------------------
# GUI (bespoke: a numeric amortization card, not a repeated-entity checklist)
# ---------------------------------------------------------------------------

CARD_WIDTH = 462
CARD_HEIGHT = 108


def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    prefix = T * indent
    eq = helpers["eq"]
    var_is_set = helpers["var_is_set"]
    player_var = helpers["player_var"]
    fold_bool = helpers["fold_bool"]
    active_ritual_visible = helpers["active_ritual_visible"]

    charter_branch_var = _charter_branch_var()
    progress_var = _progress_pct_var()
    elapsed_var = _elapsed_months_var()

    locked_expr = fold_bool("And", [var_is_set("tv_wonder_locked"), eq("tv_wonder_locked", WONDER_ID)])
    card_visible = fold_bool("And", [active_ritual_visible(), locked_expr])
    progress_bar_width = CARD_WIDTH - 16 - 20 - 66

    lines.append(f"{prefix}widget = {{")
    lines.append(f'{prefix}{T}visible = "[{card_visible}]"')
    lines.append(f"{prefix}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}layoutpolicy_vertical = fixed")
    lines.append(f"{prefix}{T}size = {{ {CARD_WIDTH} {CARD_HEIGHT} }}")
    lines.append(f"{prefix}{T}using = bg_text_mask_container_dark_blue")
    lines.append(f"{prefix}{T}vbox = {{")
    lines.append(f"{prefix}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}{T}margin = {{ 8 8 }}")
    lines.append(f"{prefix}{T}{T}spacing = 4")
    lines.append(f"{prefix}{T}{T}ignoreinvisible = yes")
    lines.append(
        f'{prefix}{T}{T}text_single = {{ text = "{KEY_PREFIX}_LABEL" size = {{ {CARD_WIDTH - 16} 22 }} '
        f"max_width = {CARD_WIDTH - 16} fontsize = 13 align = nobaseline|left }}"
    )

    for charter_key in CHARTER_ORDER:
        charter = CHARTERS[charter_key]
        charter_visible = fold_bool("And", [var_is_set(charter_branch_var), eq(charter_branch_var, charter["value"])])
        lines.append(f"{prefix}{T}{T}text_single = {{")
        lines.append(f'{prefix}{T}{T}{T}visible = "[{charter_visible}]"')
        lines.append(f'{prefix}{T}{T}{T}text = "{KEY_PREFIX}_CHARTER_{charter_key.upper()}"')
        lines.append(f"{prefix}{T}{T}{T}size = {{ {CARD_WIDTH - 16} 20 }}")
        lines.append(f"{prefix}{T}{T}{T}max_width = {CARD_WIDTH - 16}")
        lines.append(f"{prefix}{T}{T}{T}fontsize = 12")
        lines.append(f"{prefix}{T}{T}{T}align = nobaseline|left")
        lines.append(f"{prefix}{T}{T}}}")

    lines.append(f"{prefix}{T}{T}hbox = {{")
    lines.append(f"{prefix}{T}{T}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}{T}{T}spacing = 6")
    lines.append(f'{prefix}{T}{T}{T}text_single = {{ raw_text = "@gold!" size = {{ 20 24 }} fontsize = 16 align = center|nobaseline }}')
    lines.append(f"{prefix}{T}{T}{T}widget = {{")
    lines.append(f"{prefix}{T}{T}{T}{T}size = {{ {progress_bar_width} 24 }}")
    lines.append(f"{prefix}{T}{T}{T}{T}progressbar = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}{T}visible = "[{var_is_set(progress_var)}]"')
    lines.append(f"{prefix}{T}{T}{T}{T}{T}size = {{ {progress_bar_width} 16 }}")
    lines.append(f"{prefix}{T}{T}{T}{T}{T}using = progress_bar_goldish")
    lines.append(f"{prefix}{T}{T}{T}{T}{T}min = 0")
    lines.append(f"{prefix}{T}{T}{T}{T}{T}max = 100")
    lines.append(f'{prefix}{T}{T}{T}{T}{T}value = "[{player_var(progress_var)}.GetValue]"')
    lines.append(f"{prefix}{T}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}{T}{T}progressbar = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}{T}visible = "[Not({var_is_set(progress_var)})]"')
    lines.append(f"{prefix}{T}{T}{T}{T}{T}size = {{ {progress_bar_width} 16 }}")
    lines.append(f"{prefix}{T}{T}{T}{T}{T}using = progress_bar_goldish")
    lines.append(f"{prefix}{T}{T}{T}{T}{T}min = 0")
    lines.append(f"{prefix}{T}{T}{T}{T}{T}max = 100")
    lines.append(f"{prefix}{T}{T}{T}{T}{T}value = 0")
    lines.append(f"{prefix}{T}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}{T}text_single = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}visible = "[{var_is_set(elapsed_var)}]"')
    lines.append(f"{prefix}{T}{T}{T}{T}size = {{ 60 24 }}")
    lines.append(f'{prefix}{T}{T}{T}{T}raw_text = "[{player_var(elapsed_var)}.GetValue|0]/{MAX_MONTHS}"')
    lines.append(f"{prefix}{T}{T}{T}{T}align = nobaseline|right")
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}{T}text_single = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}visible = "[Not({var_is_set(elapsed_var)})]"')
    lines.append(f"{prefix}{T}{T}{T}{T}size = {{ 60 24 }}")
    lines.append(f'{prefix}{T}{T}{T}{T}raw_text = "0/{MAX_MONTHS}"')
    lines.append(f"{prefix}{T}{T}{T}{T}align = nobaseline|right")
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}}}")

    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
