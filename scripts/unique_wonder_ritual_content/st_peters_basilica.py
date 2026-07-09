"""St. Peter's Basilica (unique_st_peters_basilica) ritual content.

Bespoke rewrite: the previous version routed through the shared generic
`_entity_ritual` engine (opening/update/retry/resolve stages, identical
random_list 60/40 + 80/20 rolls reused across every wonder that used the
engine), which `scripts/audit_unique_wonder_ritual_mechanic_similarity.py`
flags as design homogenization (see docs/guides/Unique_Wonder_Ritual_Harness.md).
Its own docstring candidly noted this was "a scoped simplification" of the
spec's `actor_assignment` cadence, punted because a live 5-way simultaneous
character selector isn't proven anywhere in this codebase.

This version still does not invent an unverified multi-character selector
(that remains a real, larger follow-up requiring new `generic_actions`
surface area and its own Step 2/3 verification pass). Instead it uses the
design's own documented fallback for the `sacred_official_character_selector`
compiler-gap row in `data/unique_wonder_ritual_specs.yaml`: "Represent the
official as a semantic role variable while keeping candidate rows in
design_ir." The player *chooses* which sacred official to install (a real,
non-random decision, unlike the old dice-roll engine), and that choice
deterministically decides which one of the five apostolic service duties
becomes the office's scandal (each role has its own, distinct weak duty), then
a real choice: correct it at a prestige cost, or overlook it for free. No
`random_list` is used anywhere in this ritual.

GUI rendering reuses `_entity_ritual.append_gui`'s row/status-chip widgets
(pure rendering, not the flattened mechanic) by feeding it a row-set shape
matching this module's own variable naming.
"""
from . import _entity_ritual as engine
from ._entity_ritual import DASH, NAMESPACE, T

WONDER_ID = 112
WONDER_KEY = "unique_st_peters_basilica"
NAME_SLUG = "st_peters_basilica"
RUNTIME_PREFIX = "tv_wonder_st_peters_basilica"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_st_peters_basilica_cropped.dds"
LOCATION = "rome"

STATUS_PENDING = 0
STATUS_FAVORABLE = 1
STATUS_CONTESTED = 2
STATUS_NARROWED = 3

OPENING_EVENT_ID = 1678
ASSIGNMENT_EVENT_ID = 1679
SCANDAL_EVENT_ID = 1680
REWARD_EVENT_ID = 1681

ROLES = [
    {"key": "cardinal_administrator", "en": "Cardinal Administrator", "zh": "枢机总务"},
    {"key": "diocesan_bishop", "en": "Diocesan Bishop", "zh": "教区主教"},
    {"key": "relic_custodian", "en": "Relic Custodian", "zh": "圣物监护人"},
    {"key": "alms_prefect", "en": "Alms Prefect", "zh": "施赈长官"},
    {"key": "artist_canon", "en": "Artist Canon", "zh": "艺匠咏礼司铎"},
]
DUTIES = [
    {"key": "relic_inventory", "en": "Relic Inventory", "zh": "圣物清册"},
    {"key": "alms_ledger", "en": "Alms Ledger", "zh": "施赈账簿"},
    {"key": "pilgrim_threshold", "en": "Pilgrim Threshold", "zh": "朝圣门槛"},
    {"key": "choir_offices", "en": "Choir Offices", "zh": "唱诗职务"},
    {"key": "chapel_patronage", "en": "Chapel Patronage", "zh": "小圣堂赞助"},
]

# Each role's own weak duty -- a fixed, deterministic mapping (no dice): the
# administrator's bureaucratic distance from alms honesty, the bishop's
# disciplinarian neglect of the choir, the custodian's obsession with relics
# at the pilgrims' expense, the prefect's patronage favoritism, and the
# canon's artistic focus neglecting the relic bookkeeping.
ROLES_TABLE = {
    "cardinal_administrator": {"value": 1, "weak_duty": "alms_ledger"},
    "diocesan_bishop": {"value": 2, "weak_duty": "choir_offices"},
    "relic_custodian": {"value": 3, "weak_duty": "pilgrim_threshold"},
    "alms_prefect": {"value": 4, "weak_duty": "chapel_patronage"},
    "artist_canon": {"value": 5, "weak_duty": "relic_inventory"},
}
ROLE_ORDER = ["cardinal_administrator", "diocesan_bishop", "relic_custodian", "alms_prefect", "artist_canon"]

WONDER = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "modifier_bundles": {
        "tv_wonder_st_peters_basilica_ritual_reward_modifier": {"tolerance_own": 1.5, "clergy_estate_target_satisfaction": 0.1},
        "tv_wonder_st_peters_basilica_ritual_reward_modifier_lesser": {"tolerance_own": 0.5},
    },
}

GUI_WONDER_SHAPE = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "row_sets": [
        {"row_set_key": "role", "entities": ROLES},
        {"row_set_key": "duty", "entities": DUTIES},
    ],
}

KEY_PREFIX = f"TV_ENGINEERING_{NAME_SLUG.upper()}"


def _role_var(key: str) -> str:
    return f"{RUNTIME_PREFIX}_role_{key}_status"


def _duty_var(key: str) -> str:
    return f"{RUNTIME_PREFIX}_duty_{key}_status"


def _stage_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_stage"


def _pending_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_pending_event"


def _assigned_role_var() -> str:
    return f"{RUNTIME_PREFIX}_assigned_role"


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
    lines.append(f"# -- {RUNTIME_PREFIX}_has_scandal_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_has_scandal_trigger = {{")
    lines.append(f"{T}OR = {{")
    for duty in DUTIES:
        lines.append(f"{T}{T}var:{_duty_var(duty['key'])} ?= {STATUS_CONTESTED}")
    lines.append(f"{T}}}")
    lines.append("}")


# ---------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------

def _role_choice_effect(role_key: str) -> list[str]:
    role = ROLES_TABLE[role_key]
    effect_name = f"{RUNTIME_PREFIX}_choose_{role_key}_effect"
    lines = [f"# -- {effect_name} {DASH}", f"{effect_name} = {{"]
    lines.append(f"{T}set_variable = {{ name = {_assigned_role_var()} value = {role['value']} }}")
    for candidate in ROLES:
        value = STATUS_FAVORABLE if candidate["key"] == role_key else STATUS_NARROWED
        lines.append(f"{T}set_variable = {{ name = {_role_var(candidate['key'])} value = {value} }}")
    for duty in DUTIES:
        value = STATUS_CONTESTED if duty["key"] == role["weak_duty"] else STATUS_FAVORABLE
        lines.append(f"{T}set_variable = {{ name = {_duty_var(duty['key'])} value = {value} }}")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 2 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")
    return lines


def append_effects(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_start_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_start_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_assigned_role_var()} value = 0 }}")
    for role in ROLES:
        lines.append(f"{T}set_variable = {{ name = {_role_var(role['key'])} value = {STATUS_PENDING} }}")
    for duty in DUTIES:
        lines.append(f"{T}set_variable = {{ name = {_duty_var(duty['key'])} value = {STATUS_PENDING} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_opening_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_opening_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 1 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    for role_key in ROLE_ORDER:
        lines.append("")
        lines.extend(_role_choice_effect(role_key))

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_scandal_correct_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_scandal_correct_effect = {{")
    lines.append(f"{T}hidden_effect = {{")
    for duty in DUTIES:
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{_duty_var(duty['key'])} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {_duty_var(duty['key'])} value = {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}add_prestige = -3")
    lines.append(f"{T}{T}set_variable = {{ name = {_stage_var()} value = 3 }}")
    lines.append(f"{T}{T}remove_variable = {_pending_var()}")
    lines.append(f"{T}}}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_scandal_overlook_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_scandal_overlook_effect = {{")
    lines.append(f"{T}hidden_effect = {{")
    for duty in DUTIES:
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{_duty_var(duty['key'])} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {_duty_var(duty['key'])} value = {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}set_variable = {{ name = {_stage_var()} value = 3 }}")
    lines.append(f"{T}{T}remove_variable = {_pending_var()}")
    lines.append(f"{T}}}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_grant_reward_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_grant_reward_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable value = 0 }}")
    for duty in DUTIES:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_duty_var(duty['key'])} ?= {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 2 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_duty_var(duty['key'])} ?= {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 1 }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{RUNTIME_PREFIX}_ritual_total_favorable >= 10 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 12")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ country_has_estate = estate_type:clergy_estate }}")
    lines.append(f"{T}{T}{T}add_estate_satisfaction = {{ type = estate_type:clergy_estate value = 0.05 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:{RUNTIME_PREFIX}_ritual_total_favorable >= 9 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 6")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 2")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {RUNTIME_PREFIX}_ritual_total_favorable")
    lines.append(f"{T}remove_variable = {_stage_var()}")
    lines.append(f"{T}remove_variable = {_assigned_role_var()}")
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
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{ASSIGNMENT_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= 2 }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{SCANDAL_EVENT_ID} days = 1 }}")
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

    lines.append(f"# -- {NAMESPACE}.{ASSIGNMENT_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{ASSIGNMENT_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{ASSIGNMENT_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{ASSIGNMENT_EVENT_ID}.d")
    lines.append(f"{T}outcome = neutral")
    for letter, role_key in zip("abcde", ROLE_ORDER):
        lines.append("")
        lines.append(f"{T}option = {{")
        lines.append(f"{T}{T}name = {NAMESPACE}.{ASSIGNMENT_EVENT_ID}.{letter}")
        lines.append(f"{T}{T}{RUNTIME_PREFIX}_choose_{role_key}_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{SCANDAL_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{SCANDAL_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{SCANDAL_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{SCANDAL_EVENT_ID}.d")
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{SCANDAL_EVENT_ID}.a")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_has_scandal_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_scandal_correct_effect = yes")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{SCANDAL_EVENT_ID}.b")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_has_scandal_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_scandal_overlook_effect = yes")
    lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{REWARD_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{REWARD_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{REWARD_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{REWARD_EVENT_ID}.d")
    lines.append(f"{T}outcome = good")
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
            "t": "A Keeper for Peter's Tomb",
            "d": "The basilica doors, high altar, relic inventories, pilgrim hostels, and alms ledgers are prepared, but the threshold cannot open until a sacred official is named to keep the apostolic tomb.",
            "a": "Prepare to name the official.",
        },
        ASSIGNMENT_EVENT_ID: {
            "t": "The Keys Are Offered",
            "d": "A Cardinal Administrator brings ledgers but risks the alms accounts. A Diocesan Bishop brings discipline but risks the choir offices. A Relic Custodian brings devotion but risks the pilgrim threshold. An Alms Prefect brings charity but risks chapel patronage. An Artist Canon brings splendor but risks the relic inventory.",
            "a": "Install the Cardinal Administrator.",
            "b": "Install the Diocesan Bishop.",
            "c": "Install the Relic Custodian.",
            "d": "Install the Alms Prefect.",
            "e": "Install the Artist Canon.",
        },
        SCANDAL_EVENT_ID: {
            "t": "The First Scandal",
            "d": "The office's own weakness has produced its first dispute. It can still be corrected in full, at a cost to the sponsor's own standing, or quietly overlooked for a narrower dedication.",
            "a": "Investigate and discipline the office. (-3 prestige)",
            "b": "Overlook it for a narrower dedication.",
        },
        REWARD_EVENT_ID: {
            "t": "The Apostolic Threshold Sealed",
            "d": "The sacred official is confirmed in office, the apostolic service duties are all in order, and the threshold opens under recognized clergy obligation.",
            "a": "Seal the apostolic threshold.",
        },
    },
    "simp_chinese": {
        OPENING_EVENT_ID: {
            "t": "为彼得墓寻找监护人",
            "d": "大教堂的门扉、高坛、圣物清册、朝圣客栈与施赈账簿均已备妥，但在一位圣职人员被任命看守使徒墓之前，门槛无法开启。",
            "a": "准备任命圣职人员。",
        },
        ASSIGNMENT_EVENT_ID: {
            "t": "钥匙的授予",
            "d": "枢机总务带来账目管理，但会使施赈账目陷入风险。教区主教带来教规纪律，但会使唱诗职务陷入风险。圣物监护人带来虔诚，但会使朝圣门槛陷入风险。施赈长官带来慈善，但会使小圣堂赞助陷入风险。艺匠咏礼司铎带来华彩，但会使圣物清册陷入风险。",
            "a": "任命枢机总务。",
            "b": "任命教区主教。",
            "c": "任命圣物监护人。",
            "d": "任命施赈长官。",
            "e": "任命艺匠咏礼司铎。",
        },
        SCANDAL_EVENT_ID: {
            "t": "首次丑闻",
            "d": "该圣职自身的弱点已经引发了首次争议。仍可完全纠正，但需付出赞助者自身声望的代价；亦可悄然不予追究，转而举行较小规模的奉献礼。",
            "a": "调查并惩处该圣职。（声望 -3）",
            "b": "不予追究，举行较小规模的奉献礼。",
        },
        REWARD_EVENT_ID: {
            "t": "使徒门槛封印",
            "d": "圣职人员已在职位上获得确认，使徒职责均已就绪，门槛在获得承认的神职义务下开启。",
            "a": "封印使徒门槛。",
        },
    },
}

_STATUS_WORDS = {
    "pending": ("Not yet named", "尚未任命"),
    "favorable": ("In good standing", "履职良好"),
    "contested": ("Under scandal", "陷入丑闻"),
    "narrowed": ("Not chosen / overlooked", "未选定或已不予追究"),
}


def build_localization(language: str) -> list[str]:
    lang_index = 0 if language == "english" else 1
    lines: list[str] = []

    for event_id in (OPENING_EVENT_ID, ASSIGNMENT_EVENT_ID, SCANDAL_EVENT_ID, REWARD_EVENT_ID):
        text = _EVENTS_TEXT[language][event_id]
        lines.append(f' {NAMESPACE}.{event_id}.t:0 "{text["t"]}"')
        lines.append(f' {NAMESPACE}.{event_id}.d:0 "{text["d"]}"')
        for letter in ("a", "b", "c", "d", "e"):
            if letter in text:
                lines.append(f' {NAMESPACE}.{event_id}.{letter}:0 "{text[letter]}"')

    for status_key, words in _STATUS_WORDS.items():
        lines.append(f' {KEY_PREFIX}_STATUS_{status_key.upper()}:0 "{words[lang_index]}"')

    labels = {"role": ("Sacred Office", "神圣圣职"), "duty": ("Apostolic Duties", "使徒职责")}
    for rs_key, words in labels.items():
        lines.append(f' {KEY_PREFIX}_{rs_key.upper()}_LABEL:0 "{words[lang_index]}"')

    name_field = "en" if language == "english" else "zh"
    for role in ROLES:
        lines.append(f' {KEY_PREFIX}_ROLE_{role["key"].upper()}:0 "{role[name_field]}"')
    for duty in DUTIES:
        lines.append(f' {KEY_PREFIX}_DUTY_{duty["key"].upper()}:0 "{duty[name_field]}"')

    for modifier_name in WONDER["modifier_bundles"]:
        label = engine._modifier_display_name(WONDER, modifier_name, language)
        lines.append(f' STATIC_MODIFIER_NAME_{modifier_name}:0 "{label}"')

    return lines


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    engine.append_gui(GUI_WONDER_SHAPE, lines, indent, helpers)
