"""Dome of the Rock (unique_dome_of_the_rock) ritual content.

Implements data/unique_wonder_ritual_specs.yaml's `design_ir.tracked_entity_sets`
with full per-entity fidelity via the shared entity-ritual engine
(scripts/unique_wonder_ritual_content/_entity_ritual.py): 5 named sanctuary
access groups and 5 named custody duties, each with its own status variable,
real Jerusalem site-control eligibility trigger, its own GUI row, and a
reward scaled by how many entities settle favorably.

Event IDs 1662-1669 allocated via scripts/allocate_unique_wonder_ritual_event_ids.py
(fresh, non-colliding with the retired data/repeated_row_pilot_wonders.yaml block
1000-1003/1658-1661 and the spec's own 1004-1007 node_graph, both of which this
module replaces).
"""
from . import _entity_ritual as engine

WONDER_ID = 103
WONDER_KEY = "unique_dome_of_the_rock"
NAME_SLUG = "dome_of_the_rock"
RUNTIME_PREFIX = "tv_wonder_dome_of_the_rock"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_dome_of_the_rock_cropped.dds"
LOCATION = "jerusalem"

WONDER = {
    "wonder_id": WONDER_ID,
    "wonder_key": WONDER_KEY,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "location": LOCATION,
    "row_sets": [
        {
            "row_set_key": "sanctuary_access_groups",
            "label_en": "Sanctuary Access Covenant",
            "label_zh": "圣所门禁盟约",
            "favorable_weight": 60,
            "entities": [
                {"key": "gate_wardens", "en": "Platform Gate Wardens", "zh": "圣殿平台门卫"},
                {"key": "religious_jurists", "en": "State-Faith Jurists", "zh": "国教法学家"},
                {"key": "pilgrim_caravans", "en": "Visiting Pilgrim Groups", "zh": "来访朝圣团"},
                {"key": "local_notables", "en": "Jerusalem Local Notables", "zh": "耶路撒冷本地贤达"},
                {"key": "supervised_witnesses", "en": "Supervised Intercommunal Witnesses", "zh": "受监督的跨教派见证人"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1662,
                    "en_title": "Wardens at the Golden Threshold",
                    "en_desc": "The commissioner gathers the platform gate wardens, the state-faith jurists, visiting pilgrim groups, Jerusalem's local notables, and a panel of supervised intercommunal witnesses before the access covenant can be read aloud.",
                    "zh_title": "金色门槛前的门卫",
                    "zh_desc": "专员召集圣殿平台门卫、国教法学家、来访朝圣团、耶路撒冷本地贤达，以及一组受监督的跨教派见证人，随后才能当众宣读门禁盟约。",
                    "option_a_en": "Open the covenant reading.",
                    "option_a_zh": "开始宣读盟约。",
                },
                "update": {
                    "event_id": 1663,
                    "en_title": "Weighing the Access Compact",
                    "en_desc": "Each party is measured in turn: the wardens for discipline, the jurists for proclamation, the pilgrims for patience, the notables for standing, and the witnesses for impartiality. Some accept the compact readily; others make their reservations known.",
                    "zh_title": "衡量门禁契约",
                    "zh_desc": "各方依次受到评估：门卫看纪律，法学家看宣示，朝圣者看耐心，贤达看声望，见证人看公正。有些欣然接受契约，有些则表明保留意见。",
                    "option_a_en": "Record how each party responds.",
                    "option_a_zh": "记录各方的反应。",
                },
                "retry": {
                    "event_id": 1664,
                    "en_title": "The Compact Is Tested",
                    "en_desc": "Guard overreach at the gates, a pilgrim group's suspicion of favoritism, or a witness panel's doubt about impartiality threatens to unravel the covenant before it is sealed.",
                    "zh_title": "契约受到考验",
                    "zh_desc": "门前守卫的越权行为、朝圣团对偏袒的怀疑，或见证团对公正性的疑虑，都可能在盟约封印之前使其瓦解。",
                    "option_a_en": "Reopen talks and seek reconciliation.",
                    "option_b_en": "Accept a narrower, safer proclamation.",
                    "option_a_zh": "重开谈判，寻求和解。",
                    "option_b_zh": "接受更保守、更安全的宣告。",
                },
                "resolve": {
                    "event_id": 1665,
                    "en_title": "The Access Covenant Is Sealed",
                    "en_desc": "The custody covenant is sealed on the platform: gate wardens, jurists, pilgrims, notables, and witnesses each take their place under the recognized order of the sanctuary.",
                    "zh_title": "门禁盟约封印",
                    "zh_desc": "监护盟约在圣殿平台上封印：门卫、法学家、朝圣者、贤达与见证人各自在受认可的圣所秩序下就位。",
                    "option_a_en": "Seal the covenant.",
                    "option_a_zh": "封印盟约。",
                },
            },
        },
        {
            "row_set_key": "custody_duties",
            "label_en": "Custody Duties",
            "label_zh": "职守托付",
            "favorable_weight": 60,
            "entities": [
                {"key": "gate_keys", "en": "Gate Keys And Watch Lists", "zh": "门钥与值守名册"},
                {"key": "cisterns", "en": "Cisterns And Water Carriers", "zh": "蓄水池与运水人"},
                {"key": "lamps", "en": "Dome Lamps And Inscriptions", "zh": "穹顶灯盏与铭文"},
                {"key": "endowment_deeds", "en": "Endowment Deeds And Scribes", "zh": "瓦克夫契据与书吏"},
                {"key": "pilgrim_routes", "en": "Guarded Pilgrim Routes", "zh": "受护朝圣路线"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1666,
                    "en_title": "The Duties of the Platform",
                    "en_desc": "Before the sanctuary can be trusted to its custodians, the gate keys and watch lists, the cisterns and water carriers, the dome lamps and inscriptions, the endowment deeds and scribes, and the guarded pilgrim routes must all be entrusted to named keepers.",
                    "zh_title": "圣殿平台的职守",
                    "zh_desc": "在圣所可以托付给监护人之前，门钥与值守名册、蓄水池与运水人、穹顶灯盏与铭文、瓦克夫契据与书吏，以及受护朝圣路线，都必须托付给专职的看守人。",
                    "option_a_en": "Begin entrusting the duties.",
                    "option_a_zh": "开始托付职守。",
                },
                "update": {
                    "event_id": 1667,
                    "en_title": "Entrusting the Sanctuary's Labor",
                    "en_desc": "Keepers are assigned to each duty. Some prove reliable at once; others draw complaints of neglect, corruption, or delay before their charge is confirmed.",
                    "zh_title": "托付圣所的劳作",
                    "zh_desc": "每项职守都分派了看守人。有些立即证明可靠，另一些则在其职责被确认前招致玩忽职守、贪腐或延误的指控。",
                    "option_a_en": "Record how each duty is discharged.",
                    "option_a_zh": "记录每项职守的履行情况。",
                },
                "retry": {
                    "event_id": 1668,
                    "en_title": "A Duty Neglected",
                    "en_desc": "A neglected cistern, a lamp left unlit, or a scribe's mishandled deed makes custody look like plunder rather than stewardship unless it is corrected.",
                    "zh_title": "一项被忽视的职守",
                    "zh_desc": "一处荒废的蓄水池、一盏未点燃的灯，或一名书吏经手不当的契据，若不加以纠正，都会让监护看起来像掠夺而非守护。",
                    "option_a_en": "Discipline the keeper and re-entrust the duty.",
                    "option_b_en": "Quietly narrow that duty's scope instead.",
                    "option_a_zh": "惩处看守人并重新托付职守。",
                    "option_b_zh": "转而悄悄缩减该职守的范围。",
                },
                "resolve": {
                    "event_id": 1669,
                    "en_title": "The Custody Duties Are Entrusted",
                    "en_desc": "Gate keys, cisterns, lamps, endowment deeds, and pilgrim routes are all entrusted to keepers whose discipline is now a matter of public record.",
                    "zh_title": "职守托付完成",
                    "zh_desc": "门钥、蓄水池、灯盏、瓦克夫契据与朝圣路线，如今都已托付给纪律有据可查的看守人。",
                    "option_a_en": "Confirm the custody arrangement.",
                    "option_a_zh": "确认职守安排。",
                },
            },
        },
    ],
    "good_threshold": 8,
    "fair_threshold": 5,
    "reward": {
        "good": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_dome_of_the_rock_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 15"],
        },
        "fair": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_dome_of_the_rock_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 8"],
        },
        "poor": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_dome_of_the_rock_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 3"],
        },
    },
    "modifier_bundles": {
        "tv_wonder_dome_of_the_rock_ritual_reward_modifier": {"tolerance_own": 1.5, "diplomatic_reputation": 2},
        "tv_wonder_dome_of_the_rock_ritual_reward_modifier_lesser": {"tolerance_own": 0.5},
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
