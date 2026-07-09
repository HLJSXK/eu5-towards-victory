"""Bank of Saint George (unique_bank_of_saint_george) ritual content.

Implements data/unique_wonder_ritual_specs.yaml's `design_ir.tracked_entity_sets`
with full per-entity fidelity via the shared entity-ritual engine: 3 named
charter branches and 6 named public-credit pledges, each with its own status
variable, real Genoa site-control eligibility trigger, its own GUI row, and a
reward scaled by how many entities settle favorably.

Event IDs 1670-1677 allocated via scripts/allocate_unique_wonder_ritual_event_ids.py.
"""
from . import _entity_ritual as engine

WONDER_ID = 122
WONDER_KEY = "unique_bank_of_saint_george"
NAME_SLUG = "bank_of_saint_george"
RUNTIME_PREFIX = "tv_wonder_bank_of_saint_george"
IMAGE = "gfx/interface/icons/towards_victory/wonders/tv_wonder_unique_bank_of_saint_george_cropped.dds"
LOCATION = "genoa"

WONDER = {
    "wonder_id": WONDER_ID,
    "wonder_key": WONDER_KEY,
    "name_slug": NAME_SLUG,
    "runtime_prefix": RUNTIME_PREFIX,
    "location": LOCATION,
    "row_sets": [
        {
            "row_set_key": "charter_options",
            "label_en": "Founding Charter",
            "label_zh": "创立宪章",
            "favorable_weight": 60,
            "entities": [
                {"key": "creditor_privilege", "en": "Creditor Privilege Charter", "zh": "债权人特权宪章"},
                {"key": "crown_supervision", "en": "Crown Supervision Charter", "zh": "王室监管宪章"},
                {"key": "open_merchant_access", "en": "Open Merchant Access Charter", "zh": "商人开放准入宪章"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1670,
                    "en_title": "The Ledger Oath of San Giorgio",
                    "en_desc": "The doge's officers, merchant creditors, notaries, mint masters, and customs farmers gather around the ledger oath. Three charters are drafted for the founders to weigh: creditor privilege, crown supervision, and open merchant access.",
                    "zh_title": "圣乔治的账簿誓言",
                    "zh_desc": "总督的官员、商人债权人、公证人、铸币官与关税承包人齐聚账簿誓言之前。三份宪章草案供创立者权衡：债权人特权、王室监管与商人开放准入。",
                    "option_a_en": "Open the ledger oath.",
                    "option_a_zh": "开启账簿誓言。",
                },
                "update": {
                    "event_id": 1671,
                    "en_title": "Creditors, Crown, or Common Market",
                    "en_desc": "Each charter is tested against the council's trust: the Creditor Privilege Charter for the war creditors, the Crown Supervision Charter for royal officers, and the Open Merchant Access Charter for the wider trading public.",
                    "zh_title": "债权人、王室或公开市场",
                    "zh_desc": "每份宪章都要接受议事会信任度的检验：债权人特权宪章面向战争债权人，王室监管宪章面向王室官员，商人开放准入宪章面向更广泛的贸易公众。",
                    "option_a_en": "Weigh the council's trust in each charter.",
                    "option_a_zh": "衡量议事会对每份宪章的信任。",
                },
                "retry": {
                    "event_id": 1672,
                    "en_title": "The First Test of Trust",
                    "en_desc": "Creditor overreach, crown distrust, or open-market default pressure threatens to discredit a charter before the bank's seal can be trusted.",
                    "zh_title": "信任的初次考验",
                    "zh_desc": "债权人越权、王室的不信任，或公开市场的违约压力，都可能在银行的印信获得信任之前使某份宪章蒙上污点。",
                    "option_a_en": "Curb the overreach and renegotiate.",
                    "option_b_en": "Stand by the charter and absorb the cost.",
                    "option_a_zh": "遏制越权并重新协商。",
                    "option_b_zh": "坚持宪章原案并承担代价。",
                },
                "resolve": {
                    "event_id": 1673,
                    "en_title": "San Giorgio's Seal",
                    "en_desc": "The founding charters are sealed. Creditors, crown officers, and merchants alike now recognize San Giorgio's authority over debts, taxes, and coin trust.",
                    "zh_title": "圣乔治的印信",
                    "zh_desc": "创立宪章已经封印。债权人、王室官员与商人如今都承认圣乔治银行对债务、税收与货币信用的权威。",
                    "option_a_en": "Seal the founding charters.",
                    "option_a_zh": "封印创立宪章。",
                },
            },
        },
        {
            "row_set_key": "public_credit_pledges",
            "label_en": "Public Credit Pledges",
            "label_zh": "公共信用抵押",
            "favorable_weight": 60,
            "entities": [
                {"key": "old_war_debts", "en": "Old War Debts", "zh": "旧战债"},
                {"key": "customs_dues", "en": "Customs Dues", "zh": "关税"},
                {"key": "salt_tax", "en": "Salt Tax", "zh": "盐税"},
                {"key": "port_tolls", "en": "Port Tolls", "zh": "港口通行税"},
                {"key": "coin_assays", "en": "Coin Assays", "zh": "货币成色检验"},
                {"key": "archive_volumes", "en": "Archive Volumes", "zh": "档案卷宗"},
            ],
            "stages": {
                "opening": {
                    "event_id": 1674,
                    "en_title": "The Pledge Rolls Are Opened",
                    "en_desc": "The old war debts, customs dues, salt tax, port tolls, coin assays, and archive volumes are all opened for pledge before the public ledger can be trusted.",
                    "zh_title": "抵押名册开启",
                    "zh_desc": "旧战债、关税、盐税、港口通行税、货币成色检验与档案卷宗，全部开放供抵押登记，随后公共账簿方可取信于人。",
                    "option_a_en": "Open the pledge rolls.",
                    "option_a_zh": "开启抵押名册。",
                },
                "update": {
                    "event_id": 1675,
                    "en_title": "Debts, Duties, and the Archive Vault",
                    "en_desc": "Each pledge is weighed for trust: the old war debts against past defaults, the customs dues and salt tax against smuggling, the port tolls against harbor traffic, the coin assays against clipped currency, and the archive volumes against fire and rot.",
                    "zh_title": "债务、税捐与档案库",
                    "zh_desc": "每项抵押都要接受信用的衡量：旧战债对照过往违约记录，关税与盐税对照走私风险，港口通行税对照港口流量，货币成色检验对照剪边货币，档案卷宗对照火灾与虫蛀。",
                    "option_a_en": "Weigh the trust of each pledge.",
                    "option_a_zh": "衡量每项抵押的信用。",
                },
                "retry": {
                    "event_id": 1676,
                    "en_title": "A Pledge Falls Into Doubt",
                    "en_desc": "A defaulted debt, a smuggled cargo, or a rotted archive volume threatens to make one of the pledges worthless before the ledger is honored.",
                    "zh_title": "一项抵押陷入疑云",
                    "zh_desc": "一笔违约的债务、一批走私货物，或一卷腐坏的档案，都可能使某项抵押在账簿获得兑现之前变得一文不值。",
                    "option_a_en": "Guarantee it with treasury reserves.",
                    "option_b_en": "Narrow the ledger to proven streams only.",
                    "option_a_zh": "以国库储备作担保。",
                    "option_b_zh": "将账簿范围缩减至已验证的收入来源。",
                },
                "resolve": {
                    "event_id": 1677,
                    "en_title": "The Ledger Is Honored",
                    "en_desc": "Old war debts, customs dues, salt tax, port tolls, coin assays, and archive volumes are all pledged into a ledger the public now trusts.",
                    "zh_title": "账簿获得兑现",
                    "zh_desc": "旧战债、关税、盐税、港口通行税、货币成色检验与档案卷宗，全部抵押进入如今受公众信任的账簿。",
                    "option_a_en": "Honor the ledger.",
                    "option_a_zh": "兑现账簿。",
                },
            },
        },
    ],
    "good_threshold": 7,
    "fair_threshold": 4,
    "reward": {
        "good": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_bank_of_saint_george_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["change_gold_effect = { scale = 5 }", "add_prestige = 5"],
        },
        "fair": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_bank_of_saint_george_ritual_reward_modifier years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["change_gold_effect = { scale = 3 }"],
        },
        "poor": {
            "modifier_effects": [
                "add_country_modifier = { modifier = tv_wonder_bank_of_saint_george_ritual_reward_modifier_lesser years = -1 mode = add_and_extend }",
            ],
            "one_time_effects": ["change_gold_effect = { scale = 1 }"],
        },
    },
    "modifier_bundles": {
        "tv_wonder_bank_of_saint_george_ritual_reward_modifier": {"minting_income_factor": 0.15, "tax_income_efficiency": 0.1},
        "tv_wonder_bank_of_saint_george_ritual_reward_modifier_lesser": {"minting_income_factor": 0.05},
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
