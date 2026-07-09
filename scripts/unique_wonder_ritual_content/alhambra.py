"""Alhambra (unique_alhambra) ritual content.

Implements data/unique_wonder_ritual_specs.yaml's `design_ir.tracked_entity_sets`
with full per-entity fidelity via the shared entity-ritual engine: 6 named
treaty clauses and 5 named palace-risk points, each with its own status
variable, its own GUI row, and a reward scaled by how many entities settle
favorably.

This is also the only one of the 6 wonders whose spec declares a real
`pre_winning_war` / `ending_war` listener_contract (node `alhambra_war_validation`):
the treaty court cannot open until a war in which the sponsor holds Granada has
been won or ended. That is implemented here as a real war-validation gate
(`tv_wonder_alhambra_war_validated_trigger`), set by a dedicated on_action bridge
(src/in_game/common/on_action/tv_wonder_unique_alhambra_ritual_on_actions.txt)
following the exact `tv_engineering_department_ritual_on_pre_winning_war` /
`_on_ending_war` pattern already proven in
src/in_game/common/on_action/tv_engineering_department_on_action.txt, gating the
treaty_clause_register row set's opening event.

Event IDs 1686-1693 allocated via scripts/allocate_unique_wonder_ritual_event_ids.py.
This replaces the mechanically-generated, unrelated 7309-7316 skeleton produced by
`gen_unique_wonder_ritual_code.py --write-alhambra-source`, and wires the ritual
into data/unique_wonders.yaml (previously an empty flat-modifier placeholder).
"""
from . import _entity_ritual as engine

WONDER_ID = 106
WONDER_KEY = "unique_alhambra"
NAME_SLUG = "alhambra"
RUNTIME_PREFIX = "tv_wonder_alhambra"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_alhambra_cropped.dds"
LOCATION = "granada"

GATE_TRIGGER = "tv_wonder_alhambra_war_validated_trigger"


def _append_extra_triggers(lines: list[str]) -> None:
    lines.append("")
    lines.append(f"# -- {GATE_TRIGGER} {engine.DASH}")
    lines.append(f"{GATE_TRIGGER} = {{")
    lines.append(f"{engine.T}has_variable = tv_wonder_alhambra_war_validation")
    lines.append(f"{engine.T}var:tv_wonder_alhambra_war_validation ?= 1")
    lines.append("}")


WONDER = {
    "wonder_id": WONDER_ID,
    "wonder_key": WONDER_KEY,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "location": LOCATION,
    "gate_trigger": GATE_TRIGGER,
    "extra_triggers_hook": _append_extra_triggers,
    "row_sets": [
        {
            "row_set_key": "treaty_clause_register",
            "label_en": "Treaty Of Capitulation",
            "label_zh": "投降条约",
            "favorable_weight": 60,
            "entities": [
                {"key": "symbolic_keys", "en": "Symbolic Keys Of Granada", "zh": "格拉纳达的象征性钥匙"},
                {"key": "protected_households", "en": "Protected Households And Elites", "zh": "受保护的家户与显贵"},
                {"key": "artisan_rosters", "en": "Artisans And Palace Workshops", "zh": "工匠与宫廷作坊"},
                {"key": "acequia_water", "en": "Acequia Water And Courts", "zh": "灌渠水权与法庭"},
                {"key": "safe_conducts", "en": "Safe-Conduct Passes", "zh": "安全通行证"},
                {"key": "foreign_copies", "en": "Foreign Treaty Copies", "zh": "外邦条约副本"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1686,
                    "en_title": "The Treaty Court Opens",
                    "en_desc": "With the war over Granada now won or ended, the treaty court can finally open. The symbolic keys, the protected households and elites, the artisan rosters, the acequia water courts, the safe-conduct passes, and the foreign treaty copies are all laid before the sponsor for capitulation terms.",
                    "zh_title": "投降法庭开启",
                    "zh_desc": "围绕格拉纳达的战争已经胜利或结束，投降法庭终于得以开启。象征性钥匙、受保护的家户与显贵、工匠与宫廷作坊、灌渠水权与法庭、安全通行证，以及外邦条约副本，全部呈交赞助者以议定投降条款。",
                    "option_a_en": "Open the treaty court.",
                    "option_a_zh": "开启投降法庭。",
                },
                "update": {
                    "event_id": 1687,
                    "en_title": "The Clauses Are Read",
                    "en_desc": "Each clause is read and tested: the keys as a symbol of surrender, the households against reprisal, the artisans against flight, the acequia courts against sabotage, the safe conducts against banditry, and the foreign copies against forgery.",
                    "zh_title": "条款宣读",
                    "zh_desc": "每一条条款都被宣读并接受检验：钥匙作为投降的象征，家户不受报复，工匠不致逃散，灌渠法庭不受破坏，安全通行证不受匪患侵扰，外邦副本不被伪造。",
                    "option_a_en": "Read the treaty clauses aloud.",
                    "option_a_zh": "当众宣读条约条款。",
                },
                "retry": {
                    "event_id": 1688,
                    "en_title": "A Clause Is Challenged",
                    "en_desc": "A dishonored safe conduct, a raided workshop, or a disputed acequia court threatens to unravel the treaty before it is witnessed by foreign courts.",
                    "zh_title": "条款受到挑战",
                    "zh_desc": "一份被背弃的安全通行证、一处遭劫掠的作坊，或一场有争议的灌渠诉讼，都可能在条约被外邦宫廷见证之前使其瓦解。",
                    "option_a_en": "Press for mercy and reconciliation.",
                    "option_b_en": "Accept a narrower, harder settlement.",
                    "option_a_zh": "力求宽仁与和解。",
                    "option_b_zh": "接受更严苛、更狭窄的和议。",
                },
                "resolve": {
                    "event_id": 1689,
                    "en_title": "The Treaty Is Witnessed",
                    "en_desc": "The keys, households, artisans, acequia courts, safe conducts, and foreign copies are all accounted for. The Treaty of Capitulation is witnessed and sealed.",
                    "zh_title": "条约获得见证",
                    "zh_desc": "钥匙、家户、工匠、灌渠法庭、安全通行证与外邦副本均已清点完毕。投降条约获得见证并封印。",
                    "option_a_en": "Seal the treaty.",
                    "option_a_zh": "封印条约。",
                },
            },
        },
        {
            "row_set_key": "palace_risk_points",
            "label_en": "Palace Security",
            "label_zh": "宫廷安防",
            "favorable_weight": 60,
            "entities": [
                {"key": "gate_of_justice", "en": "Gate Of Justice", "zh": "正义之门"},
                {"key": "hall_of_ambassadors", "en": "Hall Of Ambassadors", "zh": "使节大厅"},
                {"key": "court_of_lions", "en": "Court Of The Lions", "zh": "狮子庭院"},
                {"key": "water_channels", "en": "Palace Water Channels", "zh": "宫廷水渠"},
                {"key": "vega_overlook", "en": "Walls Overlooking The Vega", "zh": "俯瞰韦加平原的城墙"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1690,
                    "en_title": "Securing the Red Fortress",
                    "en_desc": "Before the palace can be trusted to the new order, the Gate of Justice, the Hall of Ambassadors, the Court of the Lions, the palace water channels, and the walls overlooking the vega must all be secured.",
                    "zh_title": "确保红堡的安全",
                    "zh_desc": "在宫殿可以托付给新秩序之前，正义之门、使节大厅、狮子庭院、宫廷水渠，以及俯瞰韦加平原的城墙，都必须确保安全。",
                    "option_a_en": "Begin securing the palace.",
                    "option_a_zh": "开始确保宫殿安全。",
                },
                "update": {
                    "event_id": 1691,
                    "en_title": "The Palace Guard Reports",
                    "en_desc": "Each point is inspected: the Gate of Justice for crowd control, the Hall of Ambassadors for intrigue, the Court of the Lions for symbolic damage, the water channels for sabotage, and the vega walls for raiders.",
                    "zh_title": "宫廷卫队呈报",
                    "zh_desc": "每处要点都受到检查：正义之门看人群管控，使节大厅看阴谋，狮子庭院看象征性损毁，水渠看破坏，韦加城墙看袭掠者。",
                    "option_a_en": "Receive the palace guard's report.",
                    "option_a_zh": "接收宫廷卫队的呈报。",
                },
                "retry": {
                    "event_id": 1692,
                    "en_title": "Overreach At The Gate",
                    "en_desc": "Heavy-handed guards at the Gate of Justice, a plundered chamber in the Hall of Ambassadors, or a raid on the vega threatens to turn stewardship into occupation.",
                    "zh_title": "城门前的越权行为",
                    "zh_desc": "正义之门前卫兵的强硬手段、使节大厅内一间遭劫掠的厅室，或韦加平原上的一次袭掠，都可能使守护变成占领。",
                    "option_a_en": "Rein in the guards and make amends.",
                    "option_b_en": "Accept harsher, narrower occupation terms.",
                    "option_a_zh": "约束卫兵并作出补偿。",
                    "option_b_zh": "接受更严苛、更狭窄的占领条款。",
                },
                "resolve": {
                    "event_id": 1693,
                    "en_title": "The Red Fortress Is Secured",
                    "en_desc": "The Gate of Justice, the Hall of Ambassadors, the Court of the Lions, the water channels, and the vega walls are all secured under the new order.",
                    "zh_title": "红堡确保安全",
                    "zh_desc": "正义之门、使节大厅、狮子庭院、水渠与韦加城墙，全部在新秩序下确保安全。",
                    "option_a_en": "Confirm the palace is secure.",
                    "option_a_zh": "确认宫殿安全无虞。",
                },
            },
        },
    ],
    "good_threshold": 8,
    "fair_threshold": 5,
    "reward": {
        "good": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_alhambra_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 12"],
        },
        "fair": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_alhambra_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 6"],
        },
        "poor": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_alhambra_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["add_prestige = 2"],
        },
    },
    "modifier_bundles": {
        "tv_wonder_alhambra_ritual_reward_modifier": {"monthly_prestige": 0.12, "diplomatic_reputation": 2},
        "tv_wonder_alhambra_ritual_reward_modifier_lesser": {"monthly_prestige": 0.08, "diplomatic_reputation": 1},
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


def build_on_action_body() -> list[str]:
    """Alhambra-only war-validation bridge: root scope is the country the
    on_action fires for (matches the verified
    tv_engineering_department_ritual_on_pre_winning_war / _on_ending_war
    pattern in src/in_game/common/on_action/tv_engineering_department_on_action.txt),
    so no scope:winner/scope:loser lookup is needed — root simply must hold
    Granada while its Alhambra ritual is in progress."""
    T = engine.T
    trigger_lines = [
        f"{T}has_variable = tv_wonder_locked",
        f"{T}var:tv_wonder_locked ?= {WONDER_ID}",
        f"{T}has_variable = tv_wonder_ritual_in_progress",
        f"{T}{engine.site_control_trigger_name(RUNTIME_PREFIX)} = yes",
    ]
    lines: list[str] = []
    for on_action_name in (
        "tv_wonder_unique_alhambra_ritual_on_pre_winning_war",
        "tv_wonder_unique_alhambra_ritual_on_ending_war",
    ):
        lines.append(f"{on_action_name} = {{")
        lines.append(f"{T}trigger = {{")
        lines.extend(trigger_lines)
        lines.append(f"{T}}}")
        lines.append(f"{T}effect = {{")
        lines.append(f"{T}{T}hidden_effect = {{")
        lines.append(f"{T}{T}{T}set_variable = {{ name = tv_wonder_alhambra_war_validation value = 1 }}")
        lines.append(f"{T}{T}}}")
        lines.append(f"{T}}}")
        lines.append("}")
        lines.append("")
    return lines
