"""Bank of Saint George (unique_bank_of_saint_george) ritual content.

Bespoke rewrite: the previous version routed through the shared generic
`_entity_ritual` engine (opening/update/retry/resolve stages, identical
random_list 60/40 + 80/20 rolls reused across every wonder that used the
engine), which is exactly the design-homogenization failure
`scripts/audit_unique_wonder_ritual_mechanic_similarity.py` flags (see
docs/guides/Unique_Wonder_Ritual_Harness.md).

This version implements the wonder's own `design_ir`/`mechanic_signature` in
`data/unique_wonder_ritual_specs.yaml` (`instant_but_branching` cadence, the
`public_credit_charter_retry` archetype): the player chooses one of three
founding charters (creditor privilege / crown supervision / open merchant
access). Each charter *deterministically* decides which 2 of 6 public-credit
pledges become distrusted (no dice), then a single credit-incident event
offers a real choice: guarantee the distrusted pledges with treasury gold, or
narrow the ledger to the proven streams for free. No `random_list` is used
anywhere in this ritual.

GUI rendering reuses `_entity_ritual.append_gui`'s row/status-chip widgets
(pure rendering, not the flattened mechanic) by feeding it a row-set shape
matching this module's own variable naming.
"""
from . import _entity_ritual as engine
from ._entity_ritual import DASH, NAMESPACE, T

WONDER_ID = 122
WONDER_KEY = "unique_bank_of_saint_george"
NAME_SLUG = "bank_of_saint_george"
RUNTIME_PREFIX = "tv_wonder_bank_of_saint_george"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_bank_of_saint_george_cropped.dds"
LOCATION = "genoa"

STATUS_PENDING = 0
STATUS_FAVORABLE = 1
STATUS_CONTESTED = 2
STATUS_NARROWED = 3

OPENING_EVENT_ID = 1670
CHARTER_EVENT_ID = 1671
INCIDENT_EVENT_ID = 1672
REWARD_EVENT_ID = 1673

CHARTER_OPTIONS = [
    {"key": "creditor_privilege", "en": "Creditor Privilege Charter", "zh": "债权人特权宪章"},
    {"key": "crown_supervision", "en": "Crown Supervision Charter", "zh": "王室监管宪章"},
    {"key": "open_merchant_access", "en": "Open Merchant Access Charter", "zh": "商人开放准入宪章"},
]
PLEDGES = [
    {"key": "old_war_debts", "en": "Old War Debts", "zh": "旧战债"},
    {"key": "customs_dues", "en": "Customs Dues", "zh": "关税"},
    {"key": "salt_tax", "en": "Salt Tax", "zh": "盐税"},
    {"key": "port_tolls", "en": "Port Tolls", "zh": "港口通行税"},
    {"key": "coin_assays", "en": "Coin Assays", "zh": "货币成色检验"},
    {"key": "archive_volumes", "en": "Archive Volumes", "zh": "档案卷宗"},
]

# Which 2 of 6 pledges the chosen charter puts at risk -- a fixed,
# deterministic mapping (no dice).
CHARTERS = {
    "creditor_privilege": {"value": 1, "at_risk": ["old_war_debts", "coin_assays"]},
    "crown_supervision": {"value": 2, "at_risk": ["customs_dues", "salt_tax"]},
    "open_merchant_access": {"value": 3, "at_risk": ["port_tolls", "archive_volumes"]},
}
CHARTER_ORDER = ["creditor_privilege", "crown_supervision", "open_merchant_access"]

WONDER = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "modifier_bundles": {
        "tv_wonder_bank_of_saint_george_ritual_reward_modifier": {"minting_income_factor": 0.15, "tax_income_efficiency": 0.1},
        "tv_wonder_bank_of_saint_george_ritual_reward_modifier_lesser": {"minting_income_factor": 0.05},
    },
}

GUI_WONDER_SHAPE = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "row_sets": [
        {"row_set_key": "charter", "entities": CHARTER_OPTIONS},
        {"row_set_key": "pledge", "entities": PLEDGES},
    ],
}

KEY_PREFIX = f"TV_ENGINEERING_{NAME_SLUG.upper()}"


def _charter_var(key: str) -> str:
    return f"{RUNTIME_PREFIX}_charter_{key}_status"


def _pledge_var(key: str) -> str:
    return f"{RUNTIME_PREFIX}_pledge_{key}_status"


def _stage_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_stage"


def _pending_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_pending_event"


def _charter_branch_var() -> str:
    return f"{RUNTIME_PREFIX}_charter_branch"


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
    lines.append(f"# -- {RUNTIME_PREFIX}_eligibility_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_eligibility_trigger = {{")
    lines.append(f"{T}{RUNTIME_PREFIX}_active_trigger = yes")
    lines.append(f"{T}{RUNTIME_PREFIX}_site_control_trigger = yes")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_has_distrusted_pledge_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_has_distrusted_pledge_trigger = {{")
    lines.append(f"{T}OR = {{")
    for pledge in PLEDGES:
        lines.append(f"{T}{T}var:{_pledge_var(pledge['key'])} ?= {STATUS_CONTESTED}")
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
    for option in CHARTER_OPTIONS:
        value = STATUS_FAVORABLE if option["key"] == charter_key else STATUS_NARROWED
        lines.append(f"{T}set_variable = {{ name = {_charter_var(option['key'])} value = {value} }}")
    for pledge in PLEDGES:
        value = STATUS_CONTESTED if pledge["key"] in charter["at_risk"] else STATUS_FAVORABLE
        lines.append(f"{T}set_variable = {{ name = {_pledge_var(pledge['key'])} value = {value} }}")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 2 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")
    return lines


def append_effects(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_start_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_start_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_charter_branch_var()} value = 0 }}")
    for option in CHARTER_OPTIONS:
        lines.append(f"{T}set_variable = {{ name = {_charter_var(option['key'])} value = {STATUS_PENDING} }}")
    for pledge in PLEDGES:
        lines.append(f"{T}set_variable = {{ name = {_pledge_var(pledge['key'])} value = {STATUS_PENDING} }}")
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
    lines.append(f"# -- {RUNTIME_PREFIX}_incident_guarantee_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_incident_guarantee_effect = {{")
    lines.append(f"{T}hidden_effect = {{")
    for pledge in PLEDGES:
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{_pledge_var(pledge['key'])} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {_pledge_var(pledge['key'])} value = {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = -3 }}")
    lines.append(f"{T}{T}set_variable = {{ name = {_stage_var()} value = 3 }}")
    lines.append(f"{T}{T}remove_variable = {_pending_var()}")
    lines.append(f"{T}}}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_incident_narrow_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_incident_narrow_effect = {{")
    lines.append(f"{T}hidden_effect = {{")
    for pledge in PLEDGES:
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{_pledge_var(pledge['key'])} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {_pledge_var(pledge['key'])} value = {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = {_stage_var()} value = 3 }}")
    lines.append(f"{T}{T}remove_variable = {_pending_var()}")
    lines.append(f"{T}}}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_grant_reward_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_grant_reward_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable value = 0 }}")
    for pledge in PLEDGES:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_pledge_var(pledge['key'])} ?= {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 2 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_pledge_var(pledge['key'])} ?= {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 1 }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{RUNTIME_PREFIX}_ritual_total_favorable >= 12 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 5 }}")
    lines.append(f"{T}{T}add_prestige = 5")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:{RUNTIME_PREFIX}_ritual_total_favorable >= 8 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 3 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}change_gold_effect = {{ scale = 1 }}")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {RUNTIME_PREFIX}_ritual_total_favorable")
    lines.append(f"{T}remove_variable = {_stage_var()}")
    lines.append(f"{T}remove_variable = {_charter_branch_var()}")
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
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{INCIDENT_EVENT_ID} days = 1 }}")
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
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_eligibility_trigger = yes }}")
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

    lines.append(f"# -- {NAMESPACE}.{INCIDENT_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{INCIDENT_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{INCIDENT_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{INCIDENT_EVENT_ID}.d")
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{INCIDENT_EVENT_ID}.a")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_has_distrusted_pledge_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_incident_guarantee_effect = yes")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{INCIDENT_EVENT_ID}.b")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_has_distrusted_pledge_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_incident_narrow_effect = yes")
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
            "t": "The Ledger Oath of San Giorgio",
            "d": "The doge's officers, merchant creditors, notaries, mint masters, and customs farmers gather around the ledger oath. Before it can be sworn, one of three founding charters must be chosen.",
            "a": "Open the ledger oath.",
        },
        CHARTER_EVENT_ID: {
            "t": "Creditors, Crown, or Common Market",
            "d": "Creditor Privilege favors the war creditors, but risks the old debts and the coin assays. Crown Supervision favors royal officers, but risks the customs dues and the salt tax. Open Merchant Access favors the wider trading public, but risks the port tolls and the archive volumes.",
            "a": "Creditor Privilege Charter.",
            "b": "Crown Supervision Charter.",
            "c": "Open Merchant Access Charter.",
        },
        INCIDENT_EVENT_ID: {
            "t": "The First Test of Trust",
            "d": "The pledges put at risk by the chosen charter now fall into doubt. The treasury can guarantee them outright, or the ledger can be narrowed to the streams that were never in question.",
            "a": "Guarantee them with treasury reserves. (-3 treasury)",
            "b": "Narrow the ledger to the proven streams.",
        },
        REWARD_EVENT_ID: {
            "t": "San Giorgio's Seal",
            "d": "The founding charter is sealed. Creditors, crown officers, and merchants alike now recognize San Giorgio's authority over debts, taxes, and coin trust.",
            "a": "Seal the founding charter.",
        },
    },
    "simp_chinese": {
        OPENING_EVENT_ID: {
            "t": "圣乔治的账簿誓言",
            "d": "总督的官员、商人债权人、公证人、铸币官与关税承包人齐聚账簿誓言之前。在誓言宣读之前，必须先选定三份创立宪章之一。",
            "a": "开启账簿誓言。",
        },
        CHARTER_EVENT_ID: {
            "t": "债权人、王室或公开市场",
            "d": "债权人特权偏重战争债权人，但会使旧战债与货币成色检验陷入风险。王室监管偏重王室官员，但会使关税与盐税陷入风险。商人开放准入偏重更广泛的贸易公众，但会使港口通行税与档案卷宗陷入风险。",
            "a": "债权人特权宪章。",
            "b": "王室监管宪章。",
            "c": "商人开放准入宪章。",
        },
        INCIDENT_EVENT_ID: {
            "t": "信任的初次考验",
            "d": "被所选宪章置于风险中的抵押品如今陷入疑云。国库可以直接为其担保，也可以将账簿缩减至从未受质疑的收入来源。",
            "a": "以国库储备作担保。（国库 -3）",
            "b": "将账簿缩减至已验证的收入来源。",
        },
        REWARD_EVENT_ID: {
            "t": "圣乔治的印信",
            "d": "创立宪章已经封印。债权人、王室官员与商人如今都承认圣乔治银行对债务、税收与货币信用的权威。",
            "a": "封印创立宪章。",
        },
    },
}

_STATUS_WORDS = {
    "pending": ("Awaiting review", "尚待核验"),
    "favorable": ("Trusted", "获得信任"),
    "contested": ("Distrusted", "受质疑"),
    "narrowed": ("Not chosen / narrowed", "未选定或已缩减"),
}


def build_localization(language: str) -> list[str]:
    lang_index = 0 if language == "english" else 1
    lines: list[str] = []

    for event_id in (OPENING_EVENT_ID, CHARTER_EVENT_ID, INCIDENT_EVENT_ID, REWARD_EVENT_ID):
        text = _EVENTS_TEXT[language][event_id]
        lines.append(f' {NAMESPACE}.{event_id}.t:0 "{text["t"]}"')
        lines.append(f' {NAMESPACE}.{event_id}.d:0 "{text["d"]}"')
        for letter in ("a", "b", "c"):
            if letter in text:
                lines.append(f' {NAMESPACE}.{event_id}.{letter}:0 "{text[letter]}"')

    for status_key, words in _STATUS_WORDS.items():
        lines.append(f' {KEY_PREFIX}_STATUS_{status_key.upper()}:0 "{words[lang_index]}"')

    labels = {"charter": ("Founding Charter", "创立宪章"), "pledge": ("Public Credit Pledges", "公共信用抵押")}
    for rs_key, words in labels.items():
        lines.append(f' {KEY_PREFIX}_{rs_key.upper()}_LABEL:0 "{words[lang_index]}"')

    name_field = "en" if language == "english" else "zh"
    for option in CHARTER_OPTIONS:
        lines.append(f' {KEY_PREFIX}_CHARTER_{option["key"].upper()}:0 "{option[name_field]}"')
    for pledge in PLEDGES:
        lines.append(f' {KEY_PREFIX}_PLEDGE_{pledge["key"].upper()}:0 "{pledge[name_field]}"')

    for modifier_name in WONDER["modifier_bundles"]:
        label = engine._modifier_display_name(WONDER, modifier_name, language)
        lines.append(f' STATIC_MODIFIER_NAME_{modifier_name}:0 "{label}"')

    return lines


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    engine.append_gui(GUI_WONDER_SHAPE, lines, indent, helpers)
