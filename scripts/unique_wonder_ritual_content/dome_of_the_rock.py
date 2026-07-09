"""Dome of the Rock (unique_dome_of_the_rock) ritual content.

Bespoke rewrite: the previous version routed through the shared generic
`_entity_ritual` engine (opening/update/retry/resolve stages, identical
random_list 60/40 + 80/20 rolls reused across every wonder that used the
engine) with no player choice at all before the dice rolled. That is exactly
the design-homogenization failure `scripts/audit_unique_wonder_ritual_mechanic_similarity.py`
flags (see docs/guides/Unique_Wonder_Ritual_Harness.md).

This version implements the wonder's own `design_ir`/`mechanic_signature` in
`data/unique_wonder_ritual_specs.yaml` (`event_driven` cadence, custom
`sanctuary_custody_compact` archetype): the player chooses one of three
access compacts (guard discipline / jurist proclamation / witnessed
tolerance). Each compact *deterministically* decides which 2 of 5 sanctuary
access groups and which 1 of 5 custody duties become contested/disputed
(no dice), then a settlement event offers a real choice: reconcile them to
full recognition at a prestige cost, or accept a narrower, free settlement.
No `random_list` is used anywhere in this ritual.

GUI rendering reuses `_entity_ritual.append_gui`'s row/status-chip widgets
(pure rendering, not the flattened mechanic) by feeding it a row-set shape
matching this module's own variable naming.
"""
from . import _entity_ritual as engine
from ._entity_ritual import DASH, NAMESPACE, T

WONDER_ID = 103
WONDER_KEY = "unique_dome_of_the_rock"
NAME_SLUG = "dome_of_the_rock"
RUNTIME_PREFIX = "tv_wonder_dome_of_the_rock"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_dome_of_the_rock_cropped.dds"
LOCATION = "jerusalem"

STATUS_PENDING = 0
STATUS_FAVORABLE = 1
STATUS_CONTESTED = 2
STATUS_NARROWED = 3

OPENING_EVENT_ID = 1662
COMPACT_EVENT_ID = 1663
SETTLEMENT_EVENT_ID = 1664
REWARD_EVENT_ID = 1665

ACCESS_GROUPS = [
    {"key": "gate_wardens", "en": "Platform Gate Wardens", "zh": "圣殿平台门卫"},
    {"key": "religious_jurists", "en": "State-Faith Jurists", "zh": "国教法学家"},
    {"key": "pilgrim_caravans", "en": "Visiting Pilgrim Groups", "zh": "来访朝圣团"},
    {"key": "local_notables", "en": "Jerusalem Local Notables", "zh": "耶路撒冷本地贤达"},
    {"key": "supervised_witnesses", "en": "Supervised Intercommunal Witnesses", "zh": "受监督的跨教派见证人"},
]
CUSTODY_DUTIES = [
    {"key": "gate_keys", "en": "Gate Keys And Watch Lists", "zh": "门钥与值守名册"},
    {"key": "cisterns", "en": "Cisterns And Water Carriers", "zh": "蓄水池与运水人"},
    {"key": "lamps", "en": "Dome Lamps And Inscriptions", "zh": "穹顶灯盏与铭文"},
    {"key": "endowment_deeds", "en": "Endowment Deeds And Scribes", "zh": "瓦克夫契据与书吏"},
    {"key": "pilgrim_routes", "en": "Guarded Pilgrim Routes", "zh": "受护朝圣路线"},
]

# Which access group(s)/custody duty become contested/disputed under each
# compact -- a fixed, deterministic mapping (no dice). Every compact leaves
# exactly 2 access groups contested and 1 custody duty disputed.
COMPACTS = {
    "guard_discipline": {
        "value": 1,
        "en": "Guard Discipline",
        "zh": "卫队纪律",
        "contested_access": ["pilgrim_caravans", "local_notables"],
        "disputed_duty": "pilgrim_routes",
    },
    "jurist_proclamation": {
        "value": 2,
        "en": "Jurist Proclamation",
        "zh": "法学家宣示",
        "contested_access": ["gate_wardens", "supervised_witnesses"],
        "disputed_duty": "endowment_deeds",
    },
    "witnessed_tolerance": {
        "value": 3,
        "en": "Witnessed Tolerance",
        "zh": "见证下的宽容",
        "contested_access": ["religious_jurists", "gate_wardens"],
        "disputed_duty": "gate_keys",
    },
}
COMPACT_ORDER = ["guard_discipline", "jurist_proclamation", "witnessed_tolerance"]

WONDER = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "modifier_bundles": {
        "tv_wonder_dome_of_the_rock_ritual_reward_modifier": {"tolerance_own": 1.5, "diplomatic_reputation": 2},
        "tv_wonder_dome_of_the_rock_ritual_reward_modifier_lesser": {"tolerance_own": 0.5},
    },
}

# Shape consumed only by `_entity_ritual.append_gui` for widget rendering;
# its variable-naming convention (`<runtime_prefix>_<row_set_key>_<entity>_status`)
# matches this module's ACCESS_/DUTY_ status variables exactly.
GUI_WONDER_SHAPE = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "row_sets": [
        {"row_set_key": "access", "entities": ACCESS_GROUPS},
        {"row_set_key": "duty", "entities": CUSTODY_DUTIES},
    ],
}

KEY_PREFIX = f"TV_ENGINEERING_{NAME_SLUG.upper()}"


def _access_var(key: str) -> str:
    return f"{RUNTIME_PREFIX}_access_{key}_status"


def _duty_var(key: str) -> str:
    return f"{RUNTIME_PREFIX}_duty_{key}_status"


def _stage_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_stage"


def _pending_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_pending_event"


def _compact_var() -> str:
    return f"{RUNTIME_PREFIX}_compact_choice"


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
    lines.append(f"# -- {RUNTIME_PREFIX}_has_contested_entity_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_has_contested_entity_trigger = {{")
    lines.append(f"{T}OR = {{")
    for group in ACCESS_GROUPS:
        lines.append(f"{T}{T}var:{_access_var(group['key'])} ?= {STATUS_CONTESTED}")
    for duty in CUSTODY_DUTIES:
        lines.append(f"{T}{T}var:{_duty_var(duty['key'])} ?= {STATUS_CONTESTED}")
    lines.append(f"{T}}}")
    lines.append("}")


# ---------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------

def _compact_choice_effect(compact_key: str) -> list[str]:
    compact = COMPACTS[compact_key]
    effect_name = f"{RUNTIME_PREFIX}_choose_{compact_key}_effect"
    lines = [f"# -- {effect_name} {DASH}", f"{effect_name} = {{"]
    lines.append(f"{T}set_variable = {{ name = {_compact_var()} value = {compact['value']} }}")
    for group in ACCESS_GROUPS:
        value = STATUS_CONTESTED if group["key"] in compact["contested_access"] else STATUS_FAVORABLE
        lines.append(f"{T}set_variable = {{ name = {_access_var(group['key'])} value = {value} }}")
    for duty in CUSTODY_DUTIES:
        value = STATUS_CONTESTED if duty["key"] == compact["disputed_duty"] else STATUS_FAVORABLE
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
    lines.append(f"{T}set_variable = {{ name = {_compact_var()} value = 0 }}")
    for group in ACCESS_GROUPS:
        lines.append(f"{T}set_variable = {{ name = {_access_var(group['key'])} value = {STATUS_PENDING} }}")
    for duty in CUSTODY_DUTIES:
        lines.append(f"{T}set_variable = {{ name = {_duty_var(duty['key'])} value = {STATUS_PENDING} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_opening_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_opening_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = 1 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    for compact_key in COMPACT_ORDER:
        lines.append("")
        lines.extend(_compact_choice_effect(compact_key))

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_settlement_reconcile_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_settlement_reconcile_effect = {{")
    lines.append(f"{T}hidden_effect = {{")
    for group in ACCESS_GROUPS:
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{_access_var(group['key'])} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {_access_var(group['key'])} value = {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}}}")
    for duty in CUSTODY_DUTIES:
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
    lines.append(f"# -- {RUNTIME_PREFIX}_settlement_narrow_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_settlement_narrow_effect = {{")
    lines.append(f"{T}hidden_effect = {{")
    for group in ACCESS_GROUPS:
        lines.append(f"{T}{T}if = {{")
        lines.append(f"{T}{T}{T}limit = {{ var:{_access_var(group['key'])} ?= {STATUS_CONTESTED} }}")
        lines.append(f"{T}{T}{T}set_variable = {{ name = {_access_var(group['key'])} value = {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}}}")
    for duty in CUSTODY_DUTIES:
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
    for group in ACCESS_GROUPS:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_access_var(group['key'])} ?= {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 2 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_access_var(group['key'])} ?= {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 1 }}")
        lines.append(f"{T}}}")
    for duty in CUSTODY_DUTIES:
        lines.append(f"{T}if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_duty_var(duty['key'])} ?= {STATUS_FAVORABLE} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 2 }}")
        lines.append(f"{T}}}")
        lines.append(f"{T}else_if = {{")
        lines.append(f"{T}{T}limit = {{ var:{_duty_var(duty['key'])} ?= {STATUS_NARROWED} }}")
        lines.append(f"{T}{T}change_variable = {{ name = {RUNTIME_PREFIX}_ritual_total_favorable add = 1 }}")
        lines.append(f"{T}}}")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{RUNTIME_PREFIX}_ritual_total_favorable >= 20 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 15")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:{RUNTIME_PREFIX}_ritual_total_favorable >= 15 }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 8")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 3")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {RUNTIME_PREFIX}_ritual_total_favorable")
    lines.append(f"{T}remove_variable = {_stage_var()}")
    lines.append(f"{T}remove_variable = {_compact_var()}")
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
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{COMPACT_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= 2 }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{SETTLEMENT_EVENT_ID} days = 1 }}")
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

    lines.append(f"# -- {NAMESPACE}.{COMPACT_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{COMPACT_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{COMPACT_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{COMPACT_EVENT_ID}.d")
    lines.append(f"{T}outcome = neutral")
    for letter, compact_key in zip("abc", COMPACT_ORDER):
        lines.append("")
        lines.append(f"{T}option = {{")
        lines.append(f"{T}{T}name = {NAMESPACE}.{COMPACT_EVENT_ID}.{letter}")
        lines.append(f"{T}{T}{RUNTIME_PREFIX}_choose_{compact_key}_effect = yes")
        lines.append(f"{T}}}")
    lines.append("}")
    lines.append("")

    lines.append(f"# -- {NAMESPACE}.{SETTLEMENT_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{SETTLEMENT_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{SETTLEMENT_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{SETTLEMENT_EVENT_ID}.d")
    lines.append(f"{T}outcome = neutral")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{SETTLEMENT_EVENT_ID}.a")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_has_contested_entity_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_settlement_reconcile_effect = yes")
    lines.append(f"{T}}}")
    lines.append("")
    lines.append(f"{T}option = {{")
    lines.append(f"{T}{T}name = {NAMESPACE}.{SETTLEMENT_EVENT_ID}.b")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_has_contested_entity_trigger = yes }}")
    lines.append(f"{T}{T}{RUNTIME_PREFIX}_settlement_narrow_effect = yes")
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
            "t": "Wardens at the Golden Threshold",
            "d": "The commissioner gathers the platform gate wardens, the state-faith jurists, visiting pilgrim groups, Jerusalem's local notables, and a panel of supervised intercommunal witnesses. Before the access covenant can be read aloud, one of three compacts must be chosen to govern it.",
            "a": "Open the covenant reading.",
        },
        COMPACT_EVENT_ID: {
            "t": "Choosing the Access Compact",
            "d": "Guard discipline favors strict order but risks alienating pilgrims and local notables. Jurist proclamation favors public legal clarity but risks the gate wardens and the intercommunal witnesses. Witnessed tolerance favors broad recognition but risks the jurists and the gate wardens.",
            "a": "Guard Discipline: strict order at the gates.",
            "b": "Jurist Proclamation: public legal clarity.",
            "c": "Witnessed Tolerance: broad, witnessed access.",
        },
        SETTLEMENT_EVENT_ID: {
            "t": "The Compact Is Tested",
            "d": "The parties and duties left unsettled by the chosen compact now press their objections. The covenant can still be sealed in full, at a cost to the commissioner's standing, or accepted as a narrower and safer proclamation.",
            "a": "Add jurist oversight and seal full recognition. (-3 prestige)",
            "b": "Accept a narrower, safer proclamation.",
        },
        REWARD_EVENT_ID: {
            "t": "The Access Covenant Is Sealed",
            "d": "The custody covenant is sealed on the platform: gate wardens, jurists, pilgrims, notables, and witnesses each take their place under the recognized order of the sanctuary, and the entrusted duties pass to named keepers.",
            "a": "Seal the covenant.",
        },
    },
    "simp_chinese": {
        OPENING_EVENT_ID: {
            "t": "金色门槛前的门卫",
            "d": "专员召集圣殿平台门卫、国教法学家、来访朝圣团、耶路撒冷本地贤达，以及一组受监督的跨教派见证人。在门禁盟约当众宣读之前，必须先选定三份契约之一来治理它。",
            "a": "开始宣读盟约。",
        },
        COMPACT_EVENT_ID: {
            "t": "选择门禁契约",
            "d": "卫队纪律偏重严格秩序，但可能疏远朝圣者与本地贤达。法学家宣示偏重公开的法理清晰，但可能触怒门卫与跨教派见证人。见证下的宽容偏重广泛认可，但可能触怒法学家与门卫。",
            "a": "卫队纪律：门前的严格秩序。",
            "b": "法学家宣示：公开的法理清晰。",
            "c": "见证下的宽容：广泛的、有见证的门禁。",
        },
        SETTLEMENT_EVENT_ID: {
            "t": "契约受到考验",
            "d": "未被所选契约安抚的各方与职守如今提出异议。盟约仍可完全封印，但需付出声望代价；亦可接受更保守、更安全的宣告。",
            "a": "增派法学家监督，完全封印盟约。（声望 -3）",
            "b": "接受更保守、更安全的宣告。",
        },
        REWARD_EVENT_ID: {
            "t": "门禁盟约封印",
            "d": "监护盟约在圣殿平台上封印：门卫、法学家、朝圣者、贤达与见证人各自在受认可的圣所秩序下就位，受托的职守也已交付专职看守人。",
            "a": "封印盟约。",
        },
    },
}

_STATUS_WORDS = {
    "pending": ("Awaiting review", "尚待核验"),
    "favorable": ("Recognized", "获得认可"),
    "contested": ("Contested", "争议中"),
    "narrowed": ("Narrowed settlement", "缩减定案"),
}


def build_localization(language: str) -> list[str]:
    lang_index = 0 if language == "english" else 1
    lines: list[str] = []

    for event_id in (OPENING_EVENT_ID, COMPACT_EVENT_ID, SETTLEMENT_EVENT_ID, REWARD_EVENT_ID):
        text = _EVENTS_TEXT[language][event_id]
        lines.append(f' {NAMESPACE}.{event_id}.t:0 "{text["t"]}"')
        lines.append(f' {NAMESPACE}.{event_id}.d:0 "{text["d"]}"')
        for letter in ("a", "b", "c"):
            if letter in text:
                lines.append(f' {NAMESPACE}.{event_id}.{letter}:0 "{text[letter]}"')

    for status_key, words in _STATUS_WORDS.items():
        lines.append(f' {KEY_PREFIX}_STATUS_{status_key.upper()}:0 "{words[lang_index]}"')

    labels = {"access": ("Sanctuary Access Groups", "圣所门禁各方"), "duty": ("Custody Duties", "职守托付")}
    for rs_key, words in labels.items():
        lines.append(f' {KEY_PREFIX}_{rs_key.upper()}_LABEL:0 "{words[lang_index]}"')

    name_field = "en" if language == "english" else "zh"
    for group in ACCESS_GROUPS:
        lines.append(f' {KEY_PREFIX}_ACCESS_{group["key"].upper()}:0 "{group[name_field]}"')
    for duty in CUSTODY_DUTIES:
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
