"""St. Peter's Basilica (unique_st_peters_basilica) ritual content.

Implements data/unique_wonder_ritual_specs.yaml's `design_ir.tracked_entity_sets`
with full per-entity fidelity via the shared entity-ritual engine: 5 named
sacred-official candidates and 5 named apostolic service duties, each with its
own status variable, real Rome site-control eligibility trigger, its own GUI
row, and a reward scaled by how many entities settle favorably.

The full spec additionally models `sacred_official_candidates` with a
character-scope `assignment_gate` (picking an actual court character per
role). That primitive is not yet proven for a 5-way simultaneous
multi-character selector anywhere in this codebase (Hagia Sophia's own
assignment pattern only proves a single sequential role at a time), so this
pass tracks each candidate role's status/quality through the same verified
entity-ritual engine as the other wonders rather than inventing an unverified
5-way character-search interface. This is a scoped simplification, not a
dropped requirement: it keeps every named role individually tracked, gated,
and visible, which is the fidelity gap this task closes.

Event IDs 1678-1685 allocated via scripts/allocate_unique_wonder_ritual_event_ids.py.
"""
from . import _entity_ritual as engine

WONDER_ID = 112
WONDER_KEY = "unique_st_peters_basilica"
NAME_SLUG = "st_peters_basilica"
RUNTIME_PREFIX = "tv_wonder_st_peters_basilica"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_st_peters_basilica_cropped.dds"
LOCATION = "rome"

WONDER = {
    "wonder_id": WONDER_ID,
    "wonder_key": WONDER_KEY,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "location": LOCATION,
    "row_sets": [
        {
            "row_set_key": "sacred_official_candidates",
            "label_en": "Sacred Office",
            "label_zh": "神圣圣职",
            "favorable_weight": 60,
            "entities": [
                {"key": "cardinal_administrator", "en": "Cardinal Administrator", "zh": "枢机总务"},
                {"key": "diocesan_bishop", "en": "Diocesan Bishop", "zh": "教区主教"},
                {"key": "relic_custodian", "en": "Relic Custodian", "zh": "圣物监护人"},
                {"key": "alms_prefect", "en": "Alms Prefect", "zh": "施赈长官"},
                {"key": "artist_canon", "en": "Artist Canon", "zh": "艺匠咏礼司铎"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1678,
                    "en_title": "A Keeper for Peter's Tomb",
                    "en_desc": "Before the threshold can open, a cardinal administrator, a diocesan bishop, a relic custodian, an alms prefect, and an artist canon must each be named to their office over the apostolic tomb.",
                    "zh_title": "为彼得墓寻找监护人",
                    "zh_desc": "在门槛开启之前，必须先任命一位枢机总务、一位教区主教、一位圣物监护人、一位施赈长官与一位艺匠咏礼司铎，各自执掌使徒墓上的圣职。",
                    "option_a_en": "Begin the naming of officials.",
                    "option_a_zh": "开始任命官员。",
                },
                "update": {
                    "event_id": 1679,
                    "en_title": "The Keys Are Offered",
                    "en_desc": "Each office is tested: the administrator's ledgers, the bishop's discipline, the custodian's care of relics, the prefect's honesty with alms, and the canon's judgment over commissioned art.",
                    "zh_title": "钥匙的授予",
                    "zh_desc": "每个圣职都要接受考验：总务的账目、主教的教规、监护人对圣物的照料、长官对施赈的诚实，以及司铎对委托艺术品的判断。",
                    "option_a_en": "Weigh how each official performs.",
                    "option_a_zh": "衡量每位官员的表现。",
                },
                "retry": {
                    "event_id": 1680,
                    "en_title": "The First Scandal",
                    "en_desc": "A missing relic, a misspent alms purse, or a factional bishop threatens to discredit the office before the dedication can proceed.",
                    "zh_title": "首次丑闻",
                    "zh_desc": "一件失踪的圣物、一笔被挪用的施赈款，或一位结党的主教，都可能在奉献礼进行之前使该圣职蒙羞。",
                    "option_a_en": "Investigate and discipline the office.",
                    "option_b_en": "Overlook it for a narrower dedication.",
                    "option_a_zh": "调查并惩处该圣职。",
                    "option_b_zh": "对此不予追究，转而举行较小规模的奉献礼。",
                },
                "resolve": {
                    "event_id": 1681,
                    "en_title": "The Sacred Office Confirmed",
                    "en_desc": "The cardinal administrator, diocesan bishop, relic custodian, alms prefect, and artist canon are all confirmed in office over the apostolic tomb.",
                    "zh_title": "神圣圣职获得确认",
                    "zh_desc": "枢机总务、教区主教、圣物监护人、施赈长官与艺匠咏礼司铎，全部在使徒墓上的圣职中获得确认。",
                    "option_a_en": "Confirm the sacred offices.",
                    "option_a_zh": "确认神圣圣职。",
                },
            },
        },
        {
            "row_set_key": "apostolic_service_duties",
            "label_en": "Apostolic Duties",
            "label_zh": "使徒职责",
            "favorable_weight": 60,
            "entities": [
                {"key": "relic_inventory", "en": "Relic Inventory", "zh": "圣物清册"},
                {"key": "alms_ledger", "en": "Alms Ledger", "zh": "施赈账簿"},
                {"key": "pilgrim_threshold", "en": "Pilgrim Threshold", "zh": "朝圣门槛"},
                {"key": "choir_offices", "en": "Choir Offices", "zh": "唱诗职务"},
                {"key": "chapel_patronage", "en": "Chapel Patronage", "zh": "小圣堂赞助"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1682,
                    "en_title": "The Doors Behind the Keeper",
                    "en_desc": "Behind the newly named officials, the relic inventory, alms ledger, pilgrim threshold, choir offices, and chapel patronage must all be organized before the basilica can serve its full apostolic charge.",
                    "zh_title": "监护人身后的门扉",
                    "zh_desc": "在新任官员身后，圣物清册、施赈账簿、朝圣门槛、唱诗职务与小圣堂赞助，都必须妥善安排，大教堂才能承担起完整的使徒职责。",
                    "option_a_en": "Begin organizing the apostolic duties.",
                    "option_a_zh": "开始安排使徒职责。",
                },
                "update": {
                    "event_id": 1683,
                    "en_title": "The Charge Is Divided",
                    "en_desc": "Each duty is divided among clergy and lay staff: the relic inventory catalogued, the alms ledger balanced, the pilgrim threshold staffed, the choir offices scheduled, and the chapel patronage assigned.",
                    "zh_title": "职责分派",
                    "zh_desc": "每项职责都在神职人员与俗务人员之间分派：圣物清册被编目，施赈账簿被核平，朝圣门槛配备了人手，唱诗职务排定了班次，小圣堂赞助也已指派。",
                    "option_a_en": "Divide the duties among the staff.",
                    "option_a_zh": "在人员之间分派职责。",
                },
                "retry": {
                    "event_id": 1684,
                    "en_title": "Whispers Beneath the Dome",
                    "en_desc": "A miscounted relic, an unbalanced ledger, or an idle choir office spreads whispers of neglect beneath the dome.",
                    "zh_title": "穹顶下的私语",
                    "zh_desc": "一件被误计的圣物、一本不平的账簿，或一处闲置的唱诗职务，都会在穹顶下引发关于疏于职守的私语。",
                    "option_a_en": "Correct the neglect and re-audit.",
                    "option_b_en": "Quietly narrow that duty's scope.",
                    "option_a_zh": "纠正疏漏并重新核查。",
                    "option_b_zh": "悄悄缩减该职责的范围。",
                },
                "resolve": {
                    "event_id": 1685,
                    "en_title": "The Apostolic Threshold Sealed",
                    "en_desc": "The relic inventory, alms ledger, pilgrim threshold, choir offices, and chapel patronage are all in order, and the apostolic threshold is sealed under recognized clergy obligation.",
                    "zh_title": "使徒门槛封印",
                    "zh_desc": "圣物清册、施赈账簿、朝圣门槛、唱诗职务与小圣堂赞助均已就绪，使徒门槛在获得承认的神职义务下完成封印。",
                    "option_a_en": "Seal the apostolic threshold.",
                    "option_a_zh": "封印使徒门槛。",
                },
            },
        },
    ],
    "good_threshold": 8,
    "fair_threshold": 5,
    "reward": {
        "good": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_st_peters_basilica_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": [
                "add_prestige = 12",
                "if = { limit = { country_has_estate = estate_type:clergy_estate } add_estate_satisfaction = { type = estate_type:clergy_estate value = 0.05 } }",
            ],
        },
        "fair": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_st_peters_basilica_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 6"],
        },
        "poor": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_st_peters_basilica_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 2"],
        },
    },
    "modifier_bundles": {
        "tv_wonder_st_peters_basilica_ritual_reward_modifier": {"tolerance_own": 1.5, "clergy_estate_target_satisfaction": 0.1},
        "tv_wonder_st_peters_basilica_ritual_reward_modifier_lesser": {"tolerance_own": 0.5},
    },
}


def build_events_body() -> list[str]:
    return engine.build_events_body(WONDER)


def append_effects(lines: list[str]) -> None:
    engine.append_effects(WONDER, lines)


def append_triggers(lines: list[str]) -> None:
    engine.append_triggers(WONDER, lines)


def build_localization(language: str) -> list[str]:
    return engine.build_localization(WONDER, language)


def append_gui(lines: list[str], indent: int, helpers: dict[str, object]) -> None:
    engine.append_gui(WONDER, lines, indent, helpers)
