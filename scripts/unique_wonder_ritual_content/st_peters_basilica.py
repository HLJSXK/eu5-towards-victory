"""St. Peter's Basilica (unique_st_peters_basilica) ritual content.

Second bespoke rewrite. The first bespoke rewrite (2026-07) replaced the shared
`_entity_ritual` engine with a hand-written mechanic: the player picked 1 of 5
"sacred official roles", which deterministically flagged 1 of 5 "apostolic
service duties" as that office's scandal, then a single retry event offered
"correct at a prestige cost" vs. "overlook for free", with a reward scaled by
the final favorable-duty count. `scripts/audit_unique_wonder_ritual_mechanic_similarity.py`
flagged that shape (choice -> deterministic branch marking a fixed subset of
tracked entities "at risk" -> one retry event offering pay-to-fully-resolve vs.
accept-for-free-at-a-lesser-tier -> threshold-scaled reward) as homogenized
with Dome of the Rock and Bank of Saint George (`combined_ratio` 0.48-0.71),
even after dice and variable names were removed. See
`docs/knowledge/risk_cards/wonders.md` rule 13.

This version is a different shape entirely: institutional succession over
time, not a single appointment-then-incident chain. St. Peter's is not one
office-holder facing one scandal; it is a seat that outlives every
office-holder, refilled across successive tenures. The ritual runs the
Archpriest's chair through `TENURE_TOTAL` (3) tenures. Each tenure is opened
by choosing a *manner of succession* (papal appointment, chapter election, or
dynastic coadjutor) from a fixed 3-way menu; that choice sets the *rate* at
which a single continuous "Apostolic Authority" score accrues every month for
the length of the tenure (`TENURE_DURATION_MONTHS`, 6), with no player action
during that accrual window. When a tenure's duration elapses, the same 3-way
menu fires again for the *next* tenure -- and each mode also applies its own
carry-over multiplier to the authority already accumulated (continuity,
factional loss, or compounding patronage) plus its own one-time cost (none,
prestige, or clergy-estate resentment). After the third tenure's duration
elapses, the office is sealed permanently and the final reward tier is read
from the accumulated authority score.

This differs from the flagged template in every axis the audit checks: there
is no fixed subset of tracked entities marked "at risk" by a deterministic
branch (there is one continuous scalar, not a marked checklist); there is no
retry/incident event offering "pay to fully fix vs. accept a narrower version
for free" (every choice is the same freely-repeated 3-way succession-manner
menu, not a binary correction dichotomy); and the time structure is a
multi-cycle institutional loop with real monthly accrual windows, not a single
linear open -> assign -> incident -> reward chain. The reward-tier threshold on
a final accumulated score is the one structural element kept from many other
mechanics in this mod (and is not itself the flagged shape -- the flagged
shape is the whole choice/branch/retry/reward sequence, not "a reward that
reads a final number").

This still does not build the design spec's unproven "live 5-way simultaneous
character selector" for `sacred_official_character_selector`
(`data/unique_wonder_ritual_specs.yaml`, key `unique_st_peters_basilica`) --
that remains real, larger follow-up work requiring new `generic_actions`
surface area and its own Step 2/3 verification pass, exactly as the previous
rewrite's docstring noted. Instead, per the spec's own documented fallback for
that primitive ("Represent the official as a semantic role variable"), the
office-holder's manner of installation is a semantic mode variable
(`tv_wonder_st_peters_basilica_succession_mode`), not a named character. The
`sacred_official_candidates` / `apostolic_service_duties` tracked-entity rows
from the spec's `design_ir` are intentionally not reused here: those rows are
exactly the shape that produced the flagged homogenization, and the succession
mode is this rewrite's own three-way selector standing in their place.
"""
NAMESPACE = "tv_engineering_department"
T = "\t"
DASH = "-" * 74

WONDER_ID = 112
WONDER_KEY = "unique_st_peters_basilica"
NAME_SLUG = "st_peters_basilica"
RUNTIME_PREFIX = "tv_wonder_st_peters_basilica"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_st_peters_basilica_cropped.dds"
LOCATION = "rome"

STAGE_OPENING = 0
STAGE_AWAITING_INSTALLATION = 1
STAGE_TENURE_ACTIVE = 2
STAGE_TRANSITION_PENDING = 3
STAGE_CONSECRATION_PENDING = 4

TENURE_TOTAL = 3
TENURE_DURATION_MONTHS = 6

OPENING_EVENT_ID = 1678
INSTALLATION_EVENT_ID = 1679
REWARD_EVENT_ID = 1680

REWARD_TIER_HIGH = 65
REWARD_TIER_MID = 45

# Each succession manner sets this tenure's monthly authority accrual rate,
# the multiplier applied to authority already accumulated when this manner is
# chosen (continuity, factional loss, or compounding patronage), and the
# one-time cost of installing it. No dice anywhere in this ritual.
MODES = [
    {
        "key": "appointment",
        "value": 1,
        "en": "Papal Appointment",
        "zh": "教皇任命",
        "accrual": 3,
        "carry_multiply": 1.0,
        "cost_kind": "none",
    },
    {
        "key": "election",
        "value": 2,
        "en": "Chapter Election",
        "zh": "教士团选举",
        "accrual": 5,
        "carry_multiply": 0.8,
        "cost_kind": "prestige",
        "cost_value": -2,
    },
    {
        "key": "dynastic",
        "value": 3,
        "en": "Dynastic Coadjutor",
        "zh": "世袭助祭",
        "accrual": 4,
        "carry_multiply": 1.15,
        "cost_kind": "clergy_satisfaction",
        "cost_value": -0.03,
    },
]

WONDER = {
    "wonder_id": WONDER_ID,
    "name_slug": NAME_SLUG,
    "modifier_bundles": {
        "tv_wonder_st_peters_basilica_ritual_reward_modifier": {"tolerance_own": 1.5, "clergy_estate_target_satisfaction": 0.1},
        "tv_wonder_st_peters_basilica_ritual_reward_modifier_lesser": {"tolerance_own": 0.5},
    },
}

KEY_PREFIX = f"TV_ENGINEERING_{NAME_SLUG.upper()}"


def _stage_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_stage"


def _pending_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_pending_event"


def _completed_var() -> str:
    return f"{RUNTIME_PREFIX}_ritual_completed"


def _tenure_index_var() -> str:
    return f"{RUNTIME_PREFIX}_tenure_index"


def _tenure_months_var() -> str:
    return f"{RUNTIME_PREFIX}_tenure_months"


def _authority_var() -> str:
    return f"{RUNTIME_PREFIX}_authority"


def _mode_var() -> str:
    return f"{RUNTIME_PREFIX}_succession_mode"


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
    lines.append(f"# -- {RUNTIME_PREFIX}_authority_strong_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_authority_strong_trigger = {{")
    lines.append(f"{T}has_variable = {_authority_var()}")
    lines.append(f"{T}var:{_authority_var()} >= {REWARD_TIER_HIGH}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_final_tenure_risk_trigger {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_final_tenure_risk_trigger = {{")
    lines.append(f"{T}AND = {{")
    lines.append(f"{T}{T}has_variable = {_tenure_index_var()}")
    lines.append(f"{T}{T}has_variable = {_authority_var()}")
    lines.append(f"{T}{T}var:{_tenure_index_var()} >= {TENURE_TOTAL - 1}")
    lines.append(f"{T}{T}var:{_authority_var()} < {REWARD_TIER_MID}")
    lines.append(f"{T}}}")
    lines.append("}")


# ---------------------------------------------------------------------------
# effects
# ---------------------------------------------------------------------------

def _mode_install_cost_lines(mode: dict) -> list[str]:
    cost_kind = mode["cost_kind"]
    if cost_kind == "none":
        return []
    if cost_kind == "prestige":
        return [f"{T}add_prestige = {mode['cost_value']}"]
    if cost_kind == "clergy_satisfaction":
        return [
            f"{T}if = {{",
            f"{T}{T}limit = {{ country_has_estate = estate_type:clergy_estate }}",
            f"{T}{T}add_estate_satisfaction = {{ type = estate_type:clergy_estate value = {mode['cost_value']} }}",
            f"{T}}}",
        ]
    raise ValueError(f"unknown cost_kind {cost_kind!r}")


def _choose_mode_effect(mode: dict) -> list[str]:
    effect_name = f"{RUNTIME_PREFIX}_choose_{mode['key']}_effect"
    lines = [f"# -- {effect_name} {DASH}", f"{effect_name} = {{"]
    # Carry the authority already banked into the incoming tenure. At the
    # very first installation this is a harmless multiply of 0; at every
    # later transition it is the continuity/loss/compounding tax of the
    # manner just chosen for the new tenure.
    lines.append(f"{T}change_variable = {{ name = {_authority_var()} multiply = {mode['carry_multiply']} }}")
    lines.append(f"{T}set_variable = {{ name = {_mode_var()} value = {mode['value']} }}")
    lines.extend(_mode_install_cost_lines(mode))
    lines.append(f"{T}change_variable = {{ name = {_tenure_index_var()} add = 1 }}")
    lines.append(f"{T}set_variable = {{ name = {_tenure_months_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = {STAGE_TENURE_ACTIVE} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")
    return lines


def append_effects(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_start_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_start_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = {STAGE_OPENING} }}")
    lines.append(f"{T}set_variable = {{ name = {_tenure_index_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_tenure_months_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_authority_var()} value = 0 }}")
    lines.append(f"{T}set_variable = {{ name = {_mode_var()} value = 0 }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_opening_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_opening_effect = {{")
    lines.append(f"{T}set_variable = {{ name = {_stage_var()} value = {STAGE_AWAITING_INSTALLATION} }}")
    lines.append(f"{T}remove_variable = {_pending_var()}")
    lines.append("}")

    for mode in MODES:
        lines.append("")
        lines.extend(_choose_mode_effect(mode))

    lines.append("")
    lines.append(f"# -- {RUNTIME_PREFIX}_ritual_grant_reward_effect {DASH}")
    lines.append(f"{RUNTIME_PREFIX}_ritual_grant_reward_effect = {{")
    lines.append(f"{T}if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_authority_var()} >= {REWARD_TIER_HIGH} }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 14")
    lines.append(f"{T}{T}if = {{")
    lines.append(f"{T}{T}{T}limit = {{ country_has_estate = estate_type:clergy_estate }}")
    lines.append(f"{T}{T}{T}add_estate_satisfaction = {{ type = estate_type:clergy_estate value = 0.05 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}}}")
    lines.append(f"{T}else_if = {{")
    lines.append(f"{T}{T}limit = {{ var:{_authority_var()} >= {REWARD_TIER_MID} }}")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 7")
    lines.append(f"{T}}}")
    lines.append(f"{T}else = {{")
    lines.append(f"{T}{T}add_country_modifier = {{ modifier = {RUNTIME_PREFIX}_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }}")
    lines.append(f"{T}{T}add_prestige = 2")
    lines.append(f"{T}}}")
    lines.append(f"{T}remove_variable = {_authority_var()}")
    lines.append(f"{T}remove_variable = {_mode_var()}")
    lines.append(f"{T}remove_variable = {_tenure_index_var()}")
    lines.append(f"{T}remove_variable = {_tenure_months_var()}")
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
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_OPENING} {RUNTIME_PREFIX}_site_control_trigger = yes }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{OPENING_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_AWAITING_INSTALLATION} }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{INSTALLATION_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_TENURE_ACTIVE} }}")
    lines.append(f"{T}{T}{T}change_variable = {{ name = {_tenure_months_var()} add = 1 }}")
    for mode in MODES:
        conditional = "if" if mode is MODES[0] else "else_if"
        lines.append(f"{T}{T}{T}{conditional} = {{")
        lines.append(f"{T}{T}{T}{T}limit = {{ var:{_mode_var()} ?= {mode['value']} }}")
        lines.append(f"{T}{T}{T}{T}change_variable = {{ name = {_authority_var()} add = {mode['accrual']} }}")
        lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}limit = {{ var:{_tenure_months_var()} >= {TENURE_DURATION_MONTHS} }}")
    lines.append(f"{T}{T}{T}{T}if = {{")
    lines.append(f"{T}{T}{T}{T}{T}limit = {{ var:{_tenure_index_var()} >= {TENURE_TOTAL} }}")
    lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {_stage_var()} value = {STAGE_CONSECRATION_PENDING} }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}{T}else = {{")
    lines.append(f"{T}{T}{T}{T}{T}set_variable = {{ name = {_stage_var()} value = {STAGE_TRANSITION_PENDING} }}")
    lines.append(f"{T}{T}{T}{T}}}")
    lines.append(f"{T}{T}{T}}}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_TRANSITION_PENDING} }}")
    lines.append(f"{T}{T}{T}set_variable = {{ name = {_pending_var()} value = 1 }}")
    lines.append(f"{T}{T}{T}trigger_event_non_silently = {{ id = {NAMESPACE}.{INSTALLATION_EVENT_ID} days = 1 }}")
    lines.append(f"{T}{T}}}")
    lines.append(f"{T}{T}else_if = {{")
    lines.append(f"{T}{T}{T}limit = {{ var:{_stage_var()} ?= {STAGE_CONSECRATION_PENDING} }}")
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

    lines.append(f"# -- {NAMESPACE}.{INSTALLATION_EVENT_ID} {DASH}")
    lines.append(f"{NAMESPACE}.{INSTALLATION_EVENT_ID} = {{")
    lines.append(f"{T}type = country_event")
    lines.append(f"{T}title = {NAMESPACE}.{INSTALLATION_EVENT_ID}.t")
    lines.append(f"{T}desc = {NAMESPACE}.{INSTALLATION_EVENT_ID}.d")
    lines.append(f"{T}triggered_desc = {{")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_authority_strong_trigger = yes }}")
    lines.append(f"{T}{T}desc = {NAMESPACE}.{INSTALLATION_EVENT_ID}.strong.d")
    lines.append(f"{T}}}")
    lines.append(f"{T}triggered_desc = {{")
    lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_final_tenure_risk_trigger = yes }}")
    lines.append(f"{T}{T}desc = {NAMESPACE}.{INSTALLATION_EVENT_ID}.final_risk.d")
    lines.append(f"{T}}}")
    lines.append(f"{T}outcome = neutral")
    for letter, mode in zip("abc", MODES):
        lines.append("")
        lines.append(f"{T}option = {{")
        lines.append(f"{T}{T}name = {NAMESPACE}.{INSTALLATION_EVENT_ID}.{letter}")
        lines.append(f"{T}{T}trigger = {{ {RUNTIME_PREFIX}_active_trigger = yes {RUNTIME_PREFIX}_site_control_trigger = yes }}")
        lines.append(f"{T}{T}{RUNTIME_PREFIX}_choose_{mode['key']}_effect = yes")
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
            "t": "The Chair Falls Vacant",
            "d": "The tomb's threshold, high altar, and treasury stand ready, but the chair of the Archpriest has stood empty since the last tenure ended. The basilica cannot be dedicated to a living institution until the office is filled and, in time, refilled again.",
            "options": {"a": "Open the succession."},
        },
        INSTALLATION_EVENT_ID: {
            "t": "Filling the Chair",
            "d": "Whenever the chair falls vacant, Rome must again decide how the office's standing passes to the next hand. A papal appointment keeps the office steady and unremarkable. A vote of the chapter's canons wins zeal and pace, at a political price and some loss of what came before. A kinsman installed as coadjutor compounds the office's authority fastest of all, at the cost of the clergy's goodwill.",
            "strong_d": "The chair's standing already commands wide recognition. Whoever fills it next inherits an office at the height of its authority, for better or worse.",
            "final_risk_d": "This is the last tenure before the office is sealed, and its standing so far has been modest at best. Whoever is named now carries the last real chance to lift the chair's authority before it is judged.",
            "options": {
                "a": "Appoint the Archpriest by papal decree.",
                "b": "Elect the Archpriest through the canons' chapter. (-2 prestige)",
                "c": "Install a kinsman as coadjutor. (Clergy estate satisfaction cost)",
            },
        },
        REWARD_EVENT_ID: {
            "t": "The Unbroken Chair",
            "d": "Three tenures of the Archpriest's chair have passed, each shaped by how its authority was handed to the next. What the office accumulated across appointment, election, and patronage alike is now sealed into the basilica's permanent standing.",
            "options": {"a": "Seal the apostolic succession."},
        },
    },
    "simp_chinese": {
        OPENING_EVENT_ID: {
            "t": "圣座空缺",
            "d": "圣墓门槛、高坛与圣库均已备妥，但自上一任总铎的任期结束以来，总铎之位一直空缺。在此职位被填补、并在日后一再重新填补之前，大教堂无法被奉献给一个真正运作的机构。",
            "options": {"a": "开启继任程序。"},
        },
        INSTALLATION_EVENT_ID: {
            "t": "圣座的填补",
            "d": "每当圣座空缺，罗马都必须再次决定该职位的威望要如何交到下一任手中。教皇任命使职位保持稳固而平淡。教士团投票选举带来热忱与更快的积累，但需付出政治代价，且会损耗此前积累的部分威望。任命一位族人为助祭则能以最快速度增益职位权柄，但会损耗神职人员的善意。",
            "strong_d": "圣座的威望已然广受认可。无论谁接掌此职，都将继承一个正处于权柄巅峰的职位——无论这是福是祸。",
            "final_risk_d": "这是圣座封印之前的最后一任，而迄今其威望至多平平。此刻的任命，将是在最终定论之前提升圣座权柄的最后真正机会。",
            "options": {
                "a": "以教皇诏令任命总铎。",
                "b": "通过教士团选举总铎。（声望 -2）",
                "c": "任命一位族人为助祭。（神职阶层满意度代价）",
            },
        },
        REWARD_EVENT_ID: {
            "t": "不曾断绝的圣座",
            "d": "总铎之位已历经三任，每一次交接的方式都塑造了其权柄的走向。无论经由任命、选举还是任人唯亲所积累的一切，如今都已被封存于大教堂的永久地位之中。",
            "options": {"a": "封印使徒的继任。"},
        },
    },
}


def build_localization(language: str) -> list[str]:
    lang_index = 0 if language == "english" else 1
    lines: list[str] = []

    for event_id in (OPENING_EVENT_ID, INSTALLATION_EVENT_ID, REWARD_EVENT_ID):
        text = _EVENTS_TEXT[language][event_id]
        lines.append(f' {NAMESPACE}.{event_id}.t:0 "{text["t"]}"')
        lines.append(f' {NAMESPACE}.{event_id}.d:0 "{text["d"]}"')
        if "strong_d" in text:
            lines.append(f' {NAMESPACE}.{event_id}.strong.d:0 "{text["strong_d"]}"')
        if "final_risk_d" in text:
            lines.append(f' {NAMESPACE}.{event_id}.final_risk.d:0 "{text["final_risk_d"]}"')
        options = text["options"]
        for letter in ("a", "b", "c"):
            if letter in options:
                lines.append(f' {NAMESPACE}.{event_id}.{letter}:0 "{options[letter]}"')

    panel_labels = {
        f"{KEY_PREFIX}_PANEL_TITLE": ("The Archpriest's Chair", "总铎圣座"),
        f"{KEY_PREFIX}_TENURE_LABEL": ("Tenure", "任期"),
        f"{KEY_PREFIX}_AUTHORITY_LABEL": ("Apostolic Authority", "使徒权柄"),
    }
    for key, words in panel_labels.items():
        lines.append(f' {key}:0 "{words[lang_index]}"')

    name_field = "en" if language == "english" else "zh"
    for mode in MODES:
        lines.append(f' {KEY_PREFIX}_MODE_{mode["key"].upper()}:0 "{mode[name_field]}"')

    modifier_labels = {
        "tv_wonder_st_peters_basilica_ritual_reward_modifier": ("Apostolic Succession Sealed", "使徒继任封印"),
        "tv_wonder_st_peters_basilica_ritual_reward_modifier_lesser": ("Apostolic Succession Sealed (Lesser)", "使徒继任封印（次等）"),
    }
    for modifier_name, words in modifier_labels.items():
        lines.append(f' STATIC_MODIFIER_NAME_{modifier_name}:0 "{words[lang_index]}"')

    return lines


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    eq = helpers["eq"]
    player_var = helpers["player_var"]
    fold_bool = helpers["fold_bool"]
    active_ritual_visible = helpers["active_ritual_visible"]

    prefix = T * indent
    card_visible = fold_bool(
        "And",
        [
            active_ritual_visible(),
            f"{player_var('tv_wonder_locked')}.IsSet",
            eq("tv_wonder_locked", WONDER_ID),
        ],
    )
    tenure_var = player_var(_tenure_index_var())
    months_var = player_var(_tenure_months_var())
    authority_var = player_var(_authority_var())

    lines.append(f"{prefix}widget = {{")
    lines.append(f'{prefix}{T}visible = "[{card_visible}]"')
    lines.append(f"{prefix}{T}layoutpolicy_horizontal = expanding")
    lines.append(f"{prefix}{T}size = {{ 462 118 }}")
    lines.append(f"{prefix}{T}using = bg_text_mask_container_dark_blue")
    lines.append("")
    lines.append(f"{prefix}{T}vbox = {{")
    lines.append(f"{prefix}{T}{T}margin = {{ 8 7 }}")
    lines.append(f"{prefix}{T}{T}ignoreinvisible = yes")
    lines.append(f"{prefix}{T}{T}spacing = 4")
    lines.append(f'{prefix}{T}{T}text_single = {{ text = "{KEY_PREFIX}_PANEL_TITLE" align = nobaseline|left }}')

    lines.append(f"{prefix}{T}{T}hbox = {{")
    lines.append(f"{prefix}{T}{T}{T}spacing = 6")
    lines.append(f'{prefix}{T}{T}{T}text_single = {{ text = "{KEY_PREFIX}_TENURE_LABEL" size = {{ 90 20 }} align = nobaseline|left }}')
    lines.append(f"{prefix}{T}{T}{T}text_single = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}visible = "[{tenure_var}.IsSet]"')
    lines.append(f'{prefix}{T}{T}{T}{T}raw_text = "[{tenure_var}.GetValue|0]/{TENURE_TOTAL}"')
    lines.append(f"{prefix}{T}{T}{T}{T}size = {{ 60 20 }}")
    lines.append(f"{prefix}{T}{T}{T}{T}align = nobaseline|left")
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}}}")

    lines.append(f"{prefix}{T}{T}widget = {{")
    lines.append(f"{prefix}{T}{T}{T}size = {{ 100% 16 }}")
    lines.append(f"{prefix}{T}{T}{T}progressbar = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}visible = "[{months_var}.IsSet]"')
    lines.append(f"{prefix}{T}{T}{T}{T}size = {{ 100% 16 }}")
    lines.append(f"{prefix}{T}{T}{T}{T}using = progress_bar_goldish")
    lines.append(f"{prefix}{T}{T}{T}{T}min = 0")
    lines.append(f"{prefix}{T}{T}{T}{T}max = {TENURE_DURATION_MONTHS}")
    lines.append(f'{prefix}{T}{T}{T}{T}value = "[{months_var}.GetValue]"')
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}}}")

    for mode in MODES:
        mode_visible = fold_bool("And", [f"{player_var(_mode_var())}.IsSet", eq(_mode_var(), mode["value"])])
        lines.append(f"{prefix}{T}{T}text_single = {{")
        lines.append(f'{prefix}{T}{T}{T}visible = "[{mode_visible}]"')
        lines.append(f'{prefix}{T}{T}{T}text = "{KEY_PREFIX}_MODE_{mode["key"].upper()}"')
        lines.append(f"{prefix}{T}{T}{T}align = nobaseline|left")
        lines.append(f"{prefix}{T}{T}}}")

    lines.append(f"{prefix}{T}{T}hbox = {{")
    lines.append(f"{prefix}{T}{T}{T}spacing = 6")
    lines.append(f'{prefix}{T}{T}{T}text_single = {{ text = "{KEY_PREFIX}_AUTHORITY_LABEL" size = {{ 140 20 }} align = nobaseline|left }}')
    lines.append(f"{prefix}{T}{T}{T}text_single = {{")
    lines.append(f'{prefix}{T}{T}{T}{T}visible = "[{authority_var}.IsSet]"')
    lines.append(f'{prefix}{T}{T}{T}{T}raw_text = "[{authority_var}.GetValue|0]"')
    lines.append(f"{prefix}{T}{T}{T}{T}align = nobaseline|left")
    lines.append(f"{prefix}{T}{T}{T}}}")
    lines.append(f"{prefix}{T}{T}}}")

    lines.append(f"{prefix}{T}}}")
    lines.append(f"{prefix}}}")
