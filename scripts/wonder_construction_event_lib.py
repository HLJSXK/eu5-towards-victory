"""Shared data builders for generated Wonder Construction random events."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = REPO_ROOT / "data" / "wonder_construction_events.yaml"
T = "\t"


EVENT_KIND_WEIGHTS = {
    "gain_engineering_2": 1,
    "gain_engineering_1": 5,
    "trade_noneng_for_eng": 5,
    "swing_engineering_1": 5,
    "choose_eng_or_noneng_loss": 5,
    "lose_noneng_1": 5,
    "lose_noneng_2": 1,
    "engineer_gain_engineering_2": 5,
    "engineer_gain_engineering_1": 5,
    "engineer_swing_engineering_1": 5,
    "engineer_lose_noneng_1": 5,
    "engineer_lose_noneng_2": 5,
}

KIND_OUTCOMES = {
    "gain_engineering_2": "good",
    "gain_engineering_1": "good",
    "trade_noneng_for_eng": "neutral",
    "swing_engineering_1": "neutral",
    "choose_eng_or_noneng_loss": "bad",
    "lose_noneng_1": "bad",
    "lose_noneng_2": "bad",
    "engineer_gain_engineering_2": "good",
    "engineer_gain_engineering_1": "good",
    "engineer_swing_engineering_1": "neutral",
    "engineer_lose_noneng_1": "bad",
    "engineer_lose_noneng_2": "bad",
}

KIND_TITLE = {
    "gain_engineering_2": {
        "en": "{eng_effect} Windfall",
        "zh": "{eng_effect}激增",
    },
    "gain_engineering_1": {
        "en": "{eng_effect} Improves",
        "zh": "{eng_effect}改善",
    },
    "trade_noneng_for_eng": {
        "en": "{eng_effect} for {noneng}",
        "zh": "以{noneng}换取{eng_effect}",
    },
    "swing_engineering_1": {
        "en": "Uncertain {eng_effect}",
        "zh": "{eng_effect}波动",
    },
    "choose_eng_or_noneng_loss": {
        "en": "{eng_effect} or {noneng}",
        "zh": "{eng_effect}或{noneng}",
    },
    "lose_noneng_1": {
        "en": "{noneng} Strain",
        "zh": "{noneng}受压",
    },
    "lose_noneng_2": {
        "en": "{noneng} Crisis",
        "zh": "{noneng}危机",
    },
    "engineer_gain_engineering_2": {
        "en": "Engineer's {eng_effect} Breakthrough",
        "zh": "大工程师带来{eng_effect}突破",
    },
    "engineer_gain_engineering_1": {
        "en": "Engineer's {eng_effect} Method",
        "zh": "大工程师改善{eng_effect}",
    },
    "engineer_swing_engineering_1": {
        "en": "Engineer's Risk on {eng_effect}",
        "zh": "大工程师冒险处理{eng_effect}",
    },
    "engineer_lose_noneng_1": {
        "en": "Engineer's {noneng} Oversight",
        "zh": "大工程师忽视{noneng}",
    },
    "engineer_lose_noneng_2": {
        "en": "Engineer's {noneng} Failure",
        "zh": "大工程师导致{noneng}失败",
    },
}

KIND_DESC = {
    "gain_engineering_2": {
        "en": (
            "A rare convergence of practical minds and favorable conditions has given the wonder works a sudden advantage. "
            "What looked like a routine month has turned into a useful surge of {eng}. Foremen write cleaner schedules, "
            "clerks find room in the accounts, and the site carries itself with the dangerous confidence of a project that "
            "has briefly outrun its doubts."
        ),
        "zh": (
            "一次少见的顺利月份降临在奇观工地上。原本只是照常核算的工序，忽然在{eng}方面打开了余地。"
            "工头的日程更清楚，书记的账册更宽松，选址上的人们也短暂相信这项工程并非只会吞噬命令与耐心。"
        ),
    },
    "gain_engineering_1": {
        "en": (
            "The work crews have found a modest but real improvement in {eng}. It is not dramatic enough for court poets, "
            "but the people who count carts, mark stone, and argue over scaffolds know its worth. The great project advances "
            "because a hundred small frictions have been filed down."
        ),
        "zh": (
            "工地在{eng}方面取得了一项不算惊人但确实有用的改善。它不足以让宫廷诗人动笔，却足以让数车、量石、"
            "争论脚手架的人松一口气。奇观正是靠这些细小阻力被磨平而继续向前。"
        ),
    },
    "trade_noneng_for_eng": {
        "en": (
            "The Engineering Department can convert a political and material inconvenience into progress on {eng}, but the "
            "price will be paid in {noneng}. The proposal is practical, slightly graceless, and therefore very tempting. "
            "The alternative is to let the month pass without disturbing the realm further."
        ),
        "zh": (
            "工程部门提出了一项务实而不甚优雅的办法：以{noneng}为代价，换取{eng}上的进展。"
            "账面说得通，现场也确实需要，但这笔交换会在工程之外留下痕迹。另一种选择是让这个月平静过去。"
        ),
    },
    "swing_engineering_1": {
        "en": (
            "A new decision around {eng} has produced results that nobody is quite ready to name. The same shortcut could save "
            "the project a month or cost it one; the same improvisation could become a method or a warning. The site waits for "
            "the verdict with all the dignity of people standing near expensive unfinished stone."
        ),
        "zh": (
            "围绕{eng}的一项临场决定带来了难以预判的结果。同一条捷径可能节省一个月，也可能赔掉一个月；"
            "同一种权宜可能成为方法，也可能成为教训。昂贵而未完成的石料旁，所有人都在等待答案。"
        ),
    },
    "choose_eng_or_noneng_loss": {
        "en": (
            "The month has presented the builders with an unpleasant accounting choice. Either the project absorbs a loss in "
            "{eng}, or the realm outside the fences pays through {noneng}. There is no clean option, only the familiar art of "
            "choosing where the bruise will be least visible."
        ),
        "zh": (
            "这个月把一个令人不快的账目选择推到了建筑者面前：要么让工程在{eng}上受损，要么让围栏之外的国家以"
            "{noneng}承受代价。没有哪一个选择干净，只有把淤青放在哪里更不显眼。"
        ),
    },
    "lose_noneng_1": {
        "en": (
            "The wonder has leaned harder on the country than expected. The cost appears first as pressure on {noneng}, then "
            "as whispers that every magnificent monument casts a practical shadow. The works continue, but the realm has been "
            "reminded that grandeur never sends only one bill."
        ),
        "zh": (
            "奇观工程对国家施加的压力比预想更重，首先显现在{noneng}上。随后，人们又开始低声谈论："
            "任何宏伟纪念碑都会投下实际的阴影。工程仍在继续，但国家已经记起壮丽从不会只寄来一张账单。"
        ),
    },
    "lose_noneng_2": {
        "en": (
            "A harsher disruption has spilled out from the construction site and struck {noneng}. Officials can explain the "
            "sequence, but explanations do not repair the damage. For now the wonder remains standing only in promise, while "
            "the country pays for the promise in advance."
        ),
        "zh": (
            "一场更严厉的扰动从工地溢出，重重击中了{noneng}。官员们能够解释事情如何发生，但解释并不能修复损失。"
            "奇观此刻仍只存在于承诺之中，而国家已经提前为承诺付款。"
        ),
    },
    "engineer_gain_engineering_2": {
        "en": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName] has imposed an unusually elegant solution on the works. "
            "The result is a sharp improvement in {eng}, and even the skeptical foremen have stopped calling it luck.\\n\\n"
            "#G This event occurred because the current [tv_great_engineer|E] has effective military ability above 80.#!"
        ),
        "zh": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName]为工程强行理出了一套罕见而漂亮的方案，"
            "使{eng}大幅改善。连最怀疑的工头也暂时不再把这称作运气。\\n\\n"
            "#G 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力高于80。#!"
        ),
    },
    "engineer_gain_engineering_1": {
        "en": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName] has corrected a stubborn problem in the works. "
            "The improvement to {eng} is not miraculous, but it has the satisfying shape of competence applied at the right "
            "moment.\\n\\n#G This event occurred because the current [tv_great_engineer|E] has effective military ability above 50.#!"
        ),
        "zh": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName]修正了工地上一项顽固问题，使{eng}得到改善。"
            "这并非奇迹，却很像称职之人在正确时刻施加了正确压力。\\n\\n"
            "#G 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力高于50。#!"
        ),
    },
    "engineer_swing_engineering_1": {
        "en": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName] has chosen a bold answer to a problem in {eng}. "
            "The decision may prove inspired or merely expensive, and the site will learn which soon enough.\\n\\n"
            "#Y This event occurred because the current [tv_great_engineer|E] has effective military ability between 20 and 80.#!"
        ),
        "zh": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName]对{eng}上的问题采取了大胆方案。"
            "它可能显得高明，也可能只是昂贵；工地很快就会知道答案。\\n\\n"
            "#Y 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力处于20到80之间。#!"
        ),
    },
    "engineer_lose_noneng_1": {
        "en": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName] has kept eyes fixed on the geometry of the monument and "
            "missed the pressure gathering around {noneng}. The project survives the oversight, but the country must absorb it.\\n\\n"
            "#R This event occurred because the current [tv_great_engineer|E] has effective military ability below 50.#!"
        ),
        "zh": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName]把注意力牢牢放在纪念碑的形制上，却忽略了"
            "{noneng}方面逐渐积累的压力。项目能承受这次疏忽，国家也不得不承受。\\n\\n"
            "#R 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力低于50。#!"
        ),
    },
    "engineer_lose_noneng_2": {
        "en": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName] has allowed a preventable failure to travel beyond the site "
            "and damage {noneng}. The mistake is not large enough to end the wonder, which may be the cruelest part of it.\\n\\n"
            "#R This event occurred because the current [tv_great_engineer|E] has effective military ability below 20.#!"
        ),
        "zh": (
            "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName]让一场本可避免的失误越过工地边界，损害了"
            "{noneng}。错误尚不足以终止奇观，这或许正是最残酷之处。\\n\\n"
            "#R 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力低于20。#!"
        ),
    },
}

KIND_OPTIONS = {
    "gain_engineering_2": {
        "a": {"en": "Use this rare opening.", "zh": "抓住这次难得机会。"},
    },
    "gain_engineering_1": {
        "a": {"en": "A useful improvement.", "zh": "一项有用改进。"},
    },
    "trade_noneng_for_eng": {
        "a": {"en": "Make the exchange.", "zh": "接受这笔交换。"},
        "b": {"en": "Leave the matter alone.", "zh": "让事情维持原状。"},
    },
    "swing_engineering_1": {
        "a": {"en": "Let the site decide.", "zh": "让工地给出答案。"},
    },
    "choose_eng_or_noneng_loss": {
        "a": {"en": "Let the project absorb it.", "zh": "让工程承受代价。"},
        "b": {"en": "Shift the cost outward.", "zh": "把代价转移出去。"},
    },
    "lose_noneng_1": {
        "a": {"en": "The country will bear it.", "zh": "国家会承受它。"},
    },
    "lose_noneng_2": {
        "a": {"en": "This will be remembered.", "zh": "这会被记住。"},
    },
    "engineer_gain_engineering_2": {
        "a": {"en": "Brilliant work.", "zh": "卓越的工作。"},
    },
    "engineer_gain_engineering_1": {
        "a": {"en": "Good engineering.", "zh": "不错的工程判断。"},
    },
    "engineer_swing_engineering_1": {
        "a": {"en": "Trust the engineer's gamble.", "zh": "相信工程师的冒险。"},
    },
    "engineer_lose_noneng_1": {
        "a": {"en": "Correct what can be corrected.", "zh": "能补救的就补救。"},
    },
    "engineer_lose_noneng_2": {
        "a": {"en": "An ugly lesson.", "zh": "一堂难看的教训。"},
    },
}

EN_ENGINEERING_TITLE_FLAVOR = {
    "domestic_support": {
        "gain2_title": "The Streets Applaud the Site",
        "gain1_title": "Street Talk Turns",
        "swing_title": "Opinion at the Scaffold Wavers",
        "engineer_gain2_title": "[tv_great_engineer|E] Wins the Street",
        "engineer_gain1_title": "[tv_great_engineer|E] Calms the Rumor",
        "engineer_swing_title": "[tv_great_engineer|E] Courts the Crowd",
        "trade_title": "Public Backing",
        "choice_title": "Public Doubt",
    },
    "scale_competence": {
        "gain2_title": "A Wider Line on the Earth",
        "gain1_title": "The Measure Is Corrected",
        "swing_title": "The Plan Outgrows the Page",
        "engineer_gain2_title": "[tv_great_engineer|E] Redraws the Grand Line",
        "engineer_gain1_title": "[tv_great_engineer|E] Sets the Measure",
        "engineer_swing_title": "[tv_great_engineer|E] Enlarges the Plan",
        "trade_title": "A Broader Design",
        "choice_title": "A Narrower Monument",
    },
    "organization_competence": {
        "gain2_title": "Names and Orders Fall Into Place",
        "gain1_title": "The Yard Learns Its Rhythm",
        "swing_title": "Orders Change Under the Awning",
        "engineer_gain2_title": "[tv_great_engineer|E] Rebuilds the Schedule",
        "engineer_gain1_title": "[tv_great_engineer|E] Straightens the Rolls",
        "engineer_swing_title": "[tv_great_engineer|E] Rewrites the Shift",
        "trade_title": "Sharper Orders",
        "choice_title": "Muddled Rosters",
    },
    "logistics_competence": {
        "gain2_title": "Roads and Carts Find Their Rhythm",
        "gain1_title": "Ruts Find a Better Road",
        "swing_title": "The Route Turns Through Mud",
        "engineer_gain2_title": "[tv_great_engineer|E] Opens the Road",
        "engineer_gain1_title": "[tv_great_engineer|E] Clears the Convoy",
        "engineer_swing_title": "[tv_great_engineer|E] Takes the Risky Road",
        "trade_title": "A Clearer Road",
        "choice_title": "Delayed Convoys",
    },
    "materials_stockpile": {
        "gain2_title": "Storehouses Full by Morning",
        "gain1_title": "The Yard Finds Surplus",
        "swing_title": "Abacuses at the Storehouse Door",
        "engineer_gain2_title": "[tv_great_engineer|E] Expands the Storeyards",
        "engineer_gain1_title": "[tv_great_engineer|E] Revives the Stores",
        "engineer_swing_title": "[tv_great_engineer|E] Recounts the Stock",
        "trade_title": "Fuller Stores",
        "choice_title": "Thinning Piles",
    },
    "construction_progress": {
        "gain2_title": "Stone Rises Past the Mark",
        "gain1_title": "Hammers Draw Completion Near",
        "swing_title": "A New Method Hangs in the Air",
        "engineer_gain2_title": "[tv_great_engineer|E] Drives the Main Works",
        "engineer_gain1_title": "[tv_great_engineer|E] Fits the Critical Joint",
        "engineer_swing_title": "[tv_great_engineer|E] Tests a Faster Method",
        "trade_title": "A Sudden Advance",
        "choice_title": "Lost Progress",
    },
}

EN_NON_ENGINEERING_TITLE_FLAVOR = {
    "gold": {
        "trade_title": "Treasury Doors Open",
        "choice_title": "Silver Runs Thin",
        "strain_title": "A New Gap in the Treasury",
        "crisis_title": "Silence at the Treasury Door",
        "engineer_loss1_title": "[tv_great_engineer|E] Miscounts the Coin",
        "engineer_loss2_title": "[tv_great_engineer|E] Breaks the Ledger",
    },
    "legitimacy": {
        "trade_title": "Royal Authority Is Pledged",
        "choice_title": "Mandate Wears Thin",
        "strain_title": "Dust on the Royal Seal",
        "crisis_title": "Mandate Cracks Before the Site",
        "engineer_loss1_title": "[tv_great_engineer|E] Forgets the Court",
        "engineer_loss2_title": "[tv_great_engineer|E] Wounds the Crown",
    },
    "stability": {
        "trade_title": "Villages Give Way",
        "choice_title": "Order Loosens",
        "strain_title": "Quiet Towns Are Disturbed",
        "crisis_title": "Order Splinters in the Levy",
        "engineer_loss1_title": "[tv_great_engineer|E] Misreads the Villages",
        "engineer_loss2_title": "[tv_great_engineer|E] Unsettles the Country",
    },
    "prestige": {
        "trade_title": "Reputation Is Spent",
        "choice_title": "Prestige Gathers Dust",
        "strain_title": "The Court Loses Color",
        "crisis_title": "Honor Falters in Public",
        "engineer_loss1_title": "[tv_great_engineer|E] Speaks Too Soon",
        "engineer_loss2_title": "[tv_great_engineer|E] Makes a Spectacle",
    },
    "nobles_satisfaction": {
        "trade_title": "Noble Patience Is Borrowed",
        "choice_title": "Noble Murmurs",
        "strain_title": "Cold Words at Noble Tables",
        "crisis_title": "Noble Patience Is Chiseled Through",
        "engineer_loss1_title": "[tv_great_engineer|E] Slights the Nobles",
        "engineer_loss2_title": "[tv_great_engineer|E] Angers the Houses",
    },
    "clergy_satisfaction": {
        "trade_title": "The Altars Are Asked to Yield",
        "choice_title": "Clerical Unease",
        "strain_title": "Frowns Before the Altar",
        "crisis_title": "Patience Runs Out in the Vestry",
        "engineer_loss1_title": "[tv_great_engineer|E] Disturbs the Calendar",
        "engineer_loss2_title": "[tv_great_engineer|E] Offends the Clergy",
    },
    "burghers_satisfaction": {
        "trade_title": "The Market Lends Its Streets",
        "choice_title": "Merchant Complaints",
        "strain_title": "Thinner Ledgers in the Market",
        "crisis_title": "Anger Reaches the Streets",
        "engineer_loss1_title": "[tv_great_engineer|E] Blocks the Market",
        "engineer_loss2_title": "[tv_great_engineer|E] Provokes the Burghers",
    },
    "peasants_satisfaction": {
        "trade_title": "Village Shoulders Are Borrowed",
        "choice_title": "Tired Villages",
        "strain_title": "Heavier Backs in the Villages",
        "crisis_title": "Rural Anger Will Not Stay Quiet",
        "engineer_loss1_title": "[tv_great_engineer|E] Underestimates the Villages",
        "engineer_loss2_title": "[tv_great_engineer|E] Breaks the Villages",
    },
    "site_development": {
        "trade_title": "The Site Gives Stone and Space",
        "choice_title": "The Site Is Hollowed",
        "strain_title": "The Site Gives Up Its Streets",
        "crisis_title": "The Site Falls Back",
        "engineer_loss1_title": "[tv_great_engineer|E] Cuts the Wrong Streets",
        "engineer_loss2_title": "[tv_great_engineer|E] Injures the Site",
    },
    "site_prosperity": {
        "trade_title": "Local Trade Is Bent Toward the Works",
        "choice_title": "The Site Cools",
        "strain_title": "The Site Grows Quieter",
        "crisis_title": "The Site's Prosperity Is Smothered",
        "engineer_loss1_title": "[tv_great_engineer|E] Crowds the Site's Livelihoods",
        "engineer_loss2_title": "[tv_great_engineer|E] Snuffs Out the Site's Markets",
    },
    "capital_development": {
        "trade_title": "Capital Works Are Reassigned",
        "choice_title": "The Capital Gives Up Its Frame",
        "strain_title": "Capital Projects Make Way",
        "crisis_title": "The Capital Pays in Stone",
        "engineer_loss1_title": "[tv_great_engineer|E] Misuses the Capital",
        "engineer_loss2_title": "[tv_great_engineer|E] Hollows the Capital's Plans",
    },
    "capital_prosperity": {
        "trade_title": "The Capital's Markets Are Turned",
        "choice_title": "The Capital Cools",
        "strain_title": "Quieter Streets in the Capital",
        "crisis_title": "The Royal City's Trade Is Pressed Low",
        "engineer_loss1_title": "[tv_great_engineer|E] Disturbs the Royal City",
        "engineer_loss2_title": "[tv_great_engineer|E] Dims the Capital's Prosperity",
    },
    "site_laborers": {
        "trade_title": "Labor Is Driven Harder",
        "choice_title": "Laborers Fall",
        "strain_title": "Names Added to the Injury Roll",
        "crisis_title": "Sweat Crosses Into Blood",
        "engineer_loss1_title": "[tv_great_engineer|E] Misjudges the Labor Limit",
        "engineer_loss2_title": "[tv_great_engineer|E] Causes Casualties",
    },
}

ENGINEERING_CONCEPT_REF_EN = {
    "domestic_support": "[tv_wonder_domestic_support|E]",
    "scale_competence": "[tv_wonder_scale_competence|E]",
    "organization_competence": "[tv_wonder_organization_competence|E]",
    "logistics_competence": "[tv_wonder_logistics_competence|E]",
    "materials_stockpile": "[tv_wonder_materials|E]",
    "construction_progress": "[tv_wonder_construction|E] progress",
}

NON_ENGINEERING_CONCEPT_REF_EN = {
    "gold": "[gold|E]",
    "legitimacy": "[legitimacy|E]",
    "stability": "[stability|E]",
    "prestige": "[prestige|E]",
    "nobles_satisfaction": "[estate_satisfaction|E] among the nobles",
    "clergy_satisfaction": "[estate_satisfaction|E] among the clergy",
    "burghers_satisfaction": "[estate_satisfaction|E] among the burghers",
    "peasants_satisfaction": "[estate_satisfaction|E] among the peasants",
    "site_development": "[development|E] at the site",
    "site_prosperity": "[prosperity|E] at the site",
    "capital_development": "[development|E] in the capital",
    "capital_prosperity": "[prosperity|E] in the capital",
    "site_laborers": "the laboring [population|E] at the site",
}

EN_CONCEPT_REPLACEMENTS = [
    ("Engineering Department", "[tv_engineering_department|E]"),
]

ZH_CONCEPT_REPLACEMENTS = [
    ("国内支持度", "[tv_wonder_domestic_support|E]"),
    ("规模适性", "[tv_wonder_scale_competence|E]"),
    ("组织适性", "[tv_wonder_organization_competence|E]"),
    ("物流适性", "[tv_wonder_logistics_competence|E]"),
    ("物资储备", "[tv_wonder_materials|E]"),
    ("建设进度", "[tv_wonder_construction|E]进度"),
    ("大工程师", "[tv_great_engineer|E]"),
    ("稳定度", "[stability|E]"),
    ("正统性", "[legitimacy|E]"),
    ("威望", "[prestige|E]"),
    ("发展度", "[development|E]"),
    ("繁荣度", "[prosperity|E]"),
    ("贵族阶层满意度", "贵族的[estate_satisfaction|E]"),
    ("教士阶层满意度", "教士的[estate_satisfaction|E]"),
    ("市民阶层满意度", "市民的[estate_satisfaction|E]"),
    ("平民阶层满意度", "平民的[estate_satisfaction|E]"),
    ("国库资金", "[gold|E]"),
]

ENGINEER_SCOPE_ZH = "[SCOPE.sCharacter('tv_wonder_event_engineer').GetShortName]"
ENGINEER_NOTE_80_ZH = "#G 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力高于80。#!"
ENGINEER_NOTE_50_ZH = "#G 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力高于50。#!"
ENGINEER_NOTE_SWING_ZH = "#Y 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力处于20到80之间。#!"
ENGINEER_NOTE_BAD_50_ZH = "#R 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力低于50。#!"
ENGINEER_NOTE_BAD_20_ZH = "#R 该事件出现是因为当前[tv_great_engineer|E]的等效军事能力低于20。#!"

ZH_ENGINEERING_FLAVOR = {
    "domestic_support": {
        "short": "民心",
        "gain2_title": "街巷为工地喝彩",
        "gain1_title": "民议稍向工地",
        "swing_title": "脚手架旁的人心摇摆",
        "engineer_gain2_title": "大工程师说服街市",
        "engineer_gain1_title": "大工程师安定民议",
        "engineer_swing_title": "大工程师押注公议",
        "trade_title": "民心归拢",
        "choice_title": "民望收缩",
        "trade_need": "民众的耐心和乡绅的背书",
        "trade_result": "街巷开始把工程称作国家的体面",
        "choice_pressure": "围观者的赞叹正变得迟疑，工地外的闲谈已经学会计算每一车石料",
        "choice_loss": "布告会失去光泽，支持者也会把声音压低",
        "option_gain2": "让这股拥护顺势灌入工地。",
        "option_gain1": "把新得的耐心登记下来。",
        "option_swing": "让民议在工棚外自行落定。",
        "option_engineer_gain2": "把这场说服写进工程日志。",
        "option_engineer_gain1": "让工程师继续稳住人心。",
        "option_engineer_swing": "押上工程师的公众判断。",
        "gain2_desc": (
            "布告还没贴满，工地外的茶肆已经先把这项工程说成国家的荣光。行会愿意多派熟手，"
            "乡绅愿意少问几句账目，连原本只看热闹的人也开始替石料车让路。国内支持度被一车车可见的秩序推高，"
            "奇观第一次像是属于围栏外的所有人。"
        ),
        "gain1_desc": (
            "几名原本皱眉的地方头面人物愿意在名册上添下姓名，市场里的抱怨也少了些锋芒。"
            "这不是举国欢呼，却足以让工地少听见几句冷话。国内支持度向前挪了一步，"
            "而大型工程有时正需要这样的半步。"
        ),
        "swing_desc": (
            "一次仓促安排的开放参观把工地推到众人眼前。有人看见秩序，有人只看见泥水和征发；"
            "同一排脚手架在不同嘴里变成荣光或浪费。国内支持度会向哪边倾斜，"
            "要等街巷把今日见闻嚼碎之后才知道。"
        ),
        "engineer_gain2_desc": (
            f"{ENGINEER_SCOPE_ZH}没有只谈石料，而是亲自向行会、乡绅和工头解释奇观的用途。"
            "一场原本可能散成争吵的集会被压成了赞同，国内支持度因此猛然上扬。\\n\\n"
            f"{ENGINEER_NOTE_80_ZH}"
        ),
        "engineer_gain1_desc": (
            f"{ENGINEER_SCOPE_ZH}补上了工地与民众之间最刺耳的几处误会。"
            "传令更清楚，征调更有分寸，国内支持度也随之稳稳抬升。\\n\\n"
            f"{ENGINEER_NOTE_50_ZH}"
        ),
        "engineer_swing_desc": (
            f"{ENGINEER_SCOPE_ZH}决定把一项尚未完工的阶段成果展示给众人。"
            "这可能换来信任，也可能把未完成的瑕疵暴露得太早；国内支持度正在等待街巷裁决。\\n\\n"
            f"{ENGINEER_NOTE_SWING_ZH}"
        ),
    },
    "scale_competence": {
        "short": "尺度",
        "gain2_title": "宏图重新合上地平",
        "gain1_title": "尺规修正宏愿",
        "swing_title": "尺度在图纸边缘摇晃",
        "engineer_gain2_title": "大工程师重定宏图",
        "engineer_gain1_title": "大工程师校准尺度",
        "engineer_swing_title": "大工程师放大蓝图",
        "trade_title": "宏图舒展",
        "choice_title": "尺度折损",
        "trade_need": "更宽的基址、更多的测量日和更大胆的结构余量",
        "trade_result": "图纸上的庞大轮廓不再显得像狂想",
        "choice_pressure": "测量绳拉到尽头，立柱间距却仍在逼迫匠师承认旧图过于保守",
        "choice_loss": "宏图会被削去锋芒，后世看到的奇观也会矮上一截",
        "option_gain2": "让扩展后的图纸立刻盖印。",
        "option_gain1": "按新的尺规修订工程图。",
        "option_swing": "让测量绳再向外拉一次。",
        "option_engineer_gain2": "批准这份更大胆的总图。",
        "option_engineer_gain1": "采纳工程师的尺度修正。",
        "option_engineer_swing": "让工程师赌一赌更大的轮廓。",
        "gain2_desc": (
            "测量队在晨雾中重拉基线，发现原本被视为边界的坡地其实能承受更宏大的展开。"
            "新图纸把道路、台阶和主轴连成一口气，规模适性骤然提高。"
            "这不是把奇观画大那么简单，而是让大变得可信。"
        ),
        "gain1_desc": (
            "一处尴尬的转角被重新丈量，几段过紧的通道也被移到更顺手的位置。"
            "规模适性因此得到改善，宏图少了一些勉强，多了一些能落在土地上的重量。"
            "工地没有欢呼，只是许多人同时点了点头。"
        ),
        "swing_desc": (
            "匠师们提出要放宽某段布局，以免未来的主殿显得局促。"
            "若判断正确，规模适性会因此受益；若判断错误，更多空地只会让未完成的部分显得更刺眼。"
            "每一寸扩张都在询问国家到底想留下多大的影子。"
        ),
        "engineer_gain2_desc": (
            f"{ENGINEER_SCOPE_ZH}把旧图摊在泥地上，亲手划掉了几条让人困惑的轴线。"
            "新的尺度安排让宏愿与地形重新咬合，规模适性大幅提升。\\n\\n"
            f"{ENGINEER_NOTE_80_ZH}"
        ),
        "engineer_gain1_desc": (
            f"{ENGINEER_SCOPE_ZH}发现总图里一处迟早会拖慢全局的收束，并在施工前将它校正。"
            "规模适性因此更稳，工程也少了一份未来的尴尬。\\n\\n"
            f"{ENGINEER_NOTE_50_ZH}"
        ),
        "engineer_swing_desc": (
            f"{ENGINEER_SCOPE_ZH}坚持把一段设计放大到原先无人敢签字的程度。"
            "它可能让奇观获得配得上野心的尺度，也可能让工程背上过大的身躯。\\n\\n"
            f"{ENGINEER_NOTE_SWING_ZH}"
        ),
    },
    "organization_competence": {
        "short": "组织",
        "gain2_title": "名册与号令归位",
        "gain1_title": "工棚秩序理清",
        "swing_title": "号令在雨棚下改口",
        "engineer_gain2_title": "大工程师重排工序",
        "engineer_gain1_title": "大工程师理顺名册",
        "engineer_swing_title": "大工程师改写排班",
        "trade_title": "号令整肃",
        "choice_title": "排班混乱",
        "trade_need": "更清楚的名册、轮班和责任界线",
        "trade_result": "工棚里的命令终于能按同一种节拍传下去",
        "choice_pressure": "同一批工匠被两份命令叫走，材料堆旁的争吵也开始盖过锤声",
        "choice_loss": "名册会重新长出涂改和空缺，工头也会各自为政",
        "option_gain2": "把新名册分发到每座工棚。",
        "option_gain1": "让工头们照此排班。",
        "option_swing": "让这套临时号令跑满一日。",
        "option_engineer_gain2": "让工程师的排程成为新规。",
        "option_engineer_gain1": "按工程师的名册重新点人。",
        "option_engineer_swing": "用工程师的新排班赌一轮。",
        "gain2_desc": (
            "一夜之间，工棚门口的旧名册被换成按工种、时辰和责任划开的新册。"
            "石匠不再等木匠让路，书记也终于知道每一车灰浆该算在哪一段。"
            "组织适性的跃升像一道不显眼的梁，把原本松散的工地托了起来。"
        ),
        "gain1_desc": (
            "几个总被遗漏的小组被重新纳入排班，工具领取和夜间守卫也有了清楚的交接。"
            "组织适性因此改善。它不会让石头自己升起，却能让抬石头的人少走冤枉路。"
        ),
        "swing_desc": (
            "为了赶上某个关键节点，工头们临时打乱了原有排班。"
            "如果新顺序成立，组织适性会有所提高；如果它只是纸上秩序，工棚明早就会被互相寻找的人塞满。"
            "命令发出时总显得简单，执行时才显出牙齿。"
        ),
        "engineer_gain2_desc": (
            f"{ENGINEER_SCOPE_ZH}用半日时间拆开了整个工地的排程，再把它按真正的先后关系装回去。"
            "工棚里的等待和互相推诿突然少了许多，组织适性随之大幅改善。\\n\\n"
            f"{ENGINEER_NOTE_80_ZH}"
        ),
        "engineer_gain1_desc": (
            f"{ENGINEER_SCOPE_ZH}在名册中找到了几处长期无人承认的空白。"
            "补上责任人之后，组织适性稳步提高，连书记的墨水都少浪费了一些。\\n\\n"
            f"{ENGINEER_NOTE_50_ZH}"
        ),
        "engineer_swing_desc": (
            f"{ENGINEER_SCOPE_ZH}下令把三支熟练队伍临时拆散，分插到最拖后的工段。"
            "这可能立刻治好堵点，也可能让所有人都忘了原本该听谁的。\\n\\n"
            f"{ENGINEER_NOTE_SWING_ZH}"
        ),
    },
    "logistics_competence": {
        "short": "转运",
        "gain2_title": "道路与车队合拍",
        "gain1_title": "车辙找到新路",
        "swing_title": "运道在泥水间改线",
        "engineer_gain2_title": "大工程师打开运道",
        "engineer_gain1_title": "大工程师疏通车队",
        "engineer_swing_title": "大工程师改走险路",
        "trade_title": "运道畅通",
        "choice_title": "车队迟滞",
        "trade_need": "桥、仓、驿路和车队之间更可靠的衔接",
        "trade_result": "石料和木材能按工地真正需要的速度抵达",
        "choice_pressure": "雨后的车辙陷得太深，码头上的货堆又一次比工地的耐心更高",
        "choice_loss": "车队会继续误点，工匠也会继续等着看空车回来",
        "option_gain2": "把新运道纳入正式线路。",
        "option_gain1": "让车队按这条路试行。",
        "option_swing": "让货车跟着新标桩走。",
        "option_engineer_gain2": "照工程师的线路调度车马。",
        "option_engineer_gain1": "按工程师的办法疏通转运。",
        "option_engineer_swing": "准许工程师改走这条险路。",
        "gain2_desc": (
            "雨停之后，斥候在旧路旁找到一条能避开泥沼的高地车道。"
            "临时桥板、驿站和堆料点被迅速串联起来，物流适性猛然提高。"
            "工地第一次听见车轮声像一支守时的队伍，而不是一串借口。"
        ),
        "gain1_desc": (
            "一段绕远的石料路线被改短，码头到仓棚之间也添了更清楚的交接。"
            "物流适性因此改善。少几次空等，少几车翻覆，奇观就多一点像会准时到来的东西。"
        ),
        "swing_desc": (
            "车队主管建议改走一条更短却更难维护的线路。"
            "若路基撑得住，物流适性会因此上涨；若撑不住，省下的时辰会被泥水连本带利讨回。"
            "每一道车辙都像在替工程投票。"
        ),
        "engineer_gain2_desc": (
            f"{ENGINEER_SCOPE_ZH}亲自沿着运道走了一遍，随后把桥板、驿夫和仓位重新排成一张清楚的网。"
            "物流适性大幅提升，工地终于能预先知道明日会到什么。\\n\\n"
            f"{ENGINEER_NOTE_80_ZH}"
        ),
        "engineer_gain1_desc": (
            f"{ENGINEER_SCOPE_ZH}找出了车队总在同一处误时的原因，并把那里改成真正的交接点。"
            "物流适性随之改善，抱怨声至少少了一种。\\n\\n"
            f"{ENGINEER_NOTE_50_ZH}"
        ),
        "engineer_swing_desc": (
            f"{ENGINEER_SCOPE_ZH}命令转运队伍绕开拥堵官道，改走一条尚未完全压实的新路。"
            "这条路可能成为捷径，也可能成为下一封坏消息的开头。\\n\\n"
            f"{ENGINEER_NOTE_SWING_ZH}"
        ),
    },
    "materials_stockpile": {
        "short": "储料",
        "gain2_title": "仓廪满过清晨",
        "gain1_title": "料场多出余裕",
        "swing_title": "仓门前的算盘声",
        "engineer_gain2_title": "大工程师扩充料仓",
        "engineer_gain1_title": "大工程师盘活储料",
        "engineer_swing_title": "大工程师重估库存",
        "trade_title": "仓储充盈",
        "choice_title": "料堆见底",
        "trade_need": "更多石材、木料、灰浆和能遮雨的仓棚",
        "trade_result": "料场终于不再贴着最低线呼吸",
        "choice_pressure": "石材堆的阴影一日比一日短，仓吏却还在等待下一批车队",
        "choice_loss": "仓棚会继续空出令人心慌的角落",
        "option_gain2": "把多出的材料立刻入账。",
        "option_gain1": "把这批余料妥善封存。",
        "option_swing": "照新的库存估算开仓。",
        "option_engineer_gain2": "让工程师扩建临时料仓。",
        "option_engineer_gain1": "按工程师的清单重新配料。",
        "option_engineer_swing": "相信工程师的库存重算。",
        "gain2_desc": (
            "几批早被视为误期的石材同时抵达，木梁也在雨前被推进了遮棚。"
            "仓吏的算盘响了整整一个上午，最后给出一个令人难得安心的数字。"
            "物资储备大幅增加，工地终于能把目光从明日转向下月。"
        ),
        "gain1_desc": (
            "旧料堆中被清出一批仍可使用的石块，新到的木材也比预期干燥。"
            "物资储备因此改善。它不像胜利那样耀眼，却像仓门上的新锁一样令人安心。"
        ),
        "swing_desc": (
            "仓吏提出按新的损耗率提前释放部分材料，以免工段闲置。"
            "若估算准确，物资储备的使用会更有效；若估算过于乐观，料场很快会露出空地。"
            "每一次开仓都带着一点赌性。"
        ),
        "engineer_gain2_desc": (
            f"{ENGINEER_SCOPE_ZH}把散落在各处的材料清单合成一份真正可用的库存图。"
            "被遗忘的石料、可替换的木梁和新的遮棚位置一起出现，物资储备大幅提升。\\n\\n"
            f"{ENGINEER_NOTE_80_ZH}"
        ),
        "engineer_gain1_desc": (
            f"{ENGINEER_SCOPE_ZH}纠正了仓吏沿用许久的损耗估算，把还能使用的材料从废料名册里救了出来。"
            "物资储备因此得到改善。\\n\\n"
            f"{ENGINEER_NOTE_50_ZH}"
        ),
        "engineer_swing_desc": (
            f"{ENGINEER_SCOPE_ZH}要求提前调用一批原本留作备用的材料。"
            "这可能让本月施工顺畅许多，也可能让下一次缺料来得更响。\\n\\n"
            f"{ENGINEER_NOTE_SWING_ZH}"
        ),
    },
    "construction_progress": {
        "short": "工段",
        "gain2_title": "石层越过标线",
        "gain1_title": "锤声推近完工",
        "swing_title": "新工法悬在半空",
        "engineer_gain2_title": "大工程师推进主工段",
        "engineer_gain1_title": "大工程师补上关键榫口",
        "engineer_swing_title": "大工程师试行新工法",
        "trade_title": "工程突进",
        "choice_title": "进度回落",
        "trade_need": "当前部件上更密集的工序、更长的白昼和更少的等待",
        "trade_result": "未完成的部件越过了昨日谁也不敢保证的标线",
        "choice_pressure": "脚手架已经搭好，熟手也在场，可每一次停顿都像在把完工日往后推",
        "choice_loss": "当前部件会少一段本该属于今日的高度",
        "option_gain2": "让下一层石块紧跟上去。",
        "option_gain1": "把这段进展钉进日程。",
        "option_swing": "让新工法在当前部件上试一次。",
        "option_engineer_gain2": "照工程师的节奏推进主工段。",
        "option_engineer_gain1": "让工程师补上这处关键榫口。",
        "option_engineer_swing": "允许工程师试行这套新工法。",
        "gain2_desc": (
            "天色尚早，工头就在标线旁发现今日的石层已经超过预定高度。"
            "临时调整的脚手架没有塌，吊具也没有误时，建设进度因此大幅推进。"
            "在奇观工地上，这样的日子少得足以让人不敢高声庆祝。"
        ),
        "gain1_desc": (
            "一处拖延许久的榫口终于合上，后续工段得以接上锤声。"
            "建设进度向前推进了一截。它不是传奇，只是许多手臂在同一刻终于没有互相等待。"
        ),
        "swing_desc": (
            "匠师建议用一套更快的搭接办法处理当前部件。"
            "若它成功，建设进度会明显受益；若它失败，返工会把节省的时间吞回去。"
            "未完成的石面沉默地等着这次判断。"
        ),
        "engineer_gain2_desc": (
            f"{ENGINEER_SCOPE_ZH}把最熟练的几支队伍集中到当前部件，并亲自重新安排吊装顺序。"
            "石层越过旧标线，建设进度大幅推进。\\n\\n"
            f"{ENGINEER_NOTE_80_ZH}"
        ),
        "engineer_gain1_desc": (
            f"{ENGINEER_SCOPE_ZH}在一处反复卡住的连接点上做出修正，使后续工段重新接续。"
            "建设进度因此稳步提升。\\n\\n"
            f"{ENGINEER_NOTE_50_ZH}"
        ),
        "engineer_swing_desc": (
            f"{ENGINEER_SCOPE_ZH}决定在当前部件上试行一套更快但容错更低的工法。"
            "成功时它会像灵感，失败时它会像傲慢。\\n\\n"
            f"{ENGINEER_NOTE_SWING_ZH}"
        ),
    },
}

ZH_NON_ENGINEERING_FLAVOR = {
    "gold": {
        "short": "国库",
        "trade_title": "国库拨款",
        "choice_title": "银箱吃紧",
        "strain_title": "国库添上新缺口",
        "crisis_title": "金库门前的沉默",
        "engineer_loss1_title": "大工程师漏算库银",
        "engineer_loss2_title": "大工程师拖垮账册",
        "trade_scene": "司库打开预备金箱，把原本留给军饷、赈济和宫廷修缮的硬币拨往工地",
        "trade_after": "空出的账格会被每个有眼睛的官员看见",
        "choice_pressure": "国库已经为本季度的各项开销列满注脚，任何额外支出都要从别处拔钉",
        "choice_loss": "钱箱会发出比反对声更清楚的回响",
        "decline_option": "把国库铁锁重新扣上",
        "spend_option": "打开国库暗格",
        "loss1_desc": (
            "工程继续向前，但国库账页比往常薄了一截。司库能解释每一笔支出，却无法让空出的栏位重新生钱。"
            "奇观还没立起，国家已经先学会为它垫付耐心。"
        ),
        "loss2_desc": (
            "这次不再只是普通超支。几项早已承诺的拨款被迫后移，金库门前的沉默比任何责问都难听。"
            "官员们把原因写得很整齐，可整齐的字迹补不上国库资金的裂口。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}把吊装和石料算得分毫不差，却低估了每一次临时采购会怎样啃食国库。"
            "账册还能勉强合上，只是合上时声音很重。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}批准了一连串本可避免的急购，把国库推到不得不补洞的境地。"
            "工地没有停下，账册却替它摔了一跤。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "让司库先把缺口缝起来。",
        "option_loss2": "记下这场昂贵的沉默。",
        "option_engineer_loss1": "叫工程师重新看账。",
        "option_engineer_loss2": "让这笔烂账成为训诫。",
    },
    "legitimacy": {
        "short": "正统",
        "trade_title": "王命背书",
        "choice_title": "名分受损",
        "strain_title": "王命染上灰尘",
        "crisis_title": "名分在工地前裂开",
        "engineer_loss1_title": "大工程师轻慢名分",
        "engineer_loss2_title": "大工程师折损王命",
        "trade_scene": "宫廷愿意把君主的名义压在工程布告上，让反对者暂时不敢把抱怨说得太响",
        "trade_after": "被动用的威仪很难完全收回",
        "choice_pressure": "王命若为一处工段反复背书，名分本身也会被拖进泥水里",
        "choice_loss": "正统性会在每一道催工诏令后变薄",
        "decline_option": "别让王命替工棚担保",
        "spend_option": "以王命为工程背书",
        "loss1_desc": (
            "几道催工文书以君主名义发出，却没有得到同样庄重的结果。朝臣仍然服从，语气却多了一点计算。"
            "正统性不是崩塌，只是在奇观阴影下蒙了一层灰。"
        ),
        "loss2_desc": (
            "一场围绕工程的争执被迫抬到王座之前，名分因此成了施工耗材。"
            "当君主的威仪被拿来解释石料迟到，正统性的裂口便很难再被称作小事。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}把宫廷礼制当成可以挪动的脚手架，却忘了名分一旦拆动就会留下痕迹。"
            "工程保住了节奏，正统性却被磨薄。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}让一项工程命令越过了礼制能承受的界线。"
            "工地得到了一时方便，王命却替这份方便付出沉重代价。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "让宫廷尽快修补礼数。",
        "option_loss2": "这道裂缝会被史官看见。",
        "option_engineer_loss1": "提醒工程师敬畏名分。",
        "option_engineer_loss2": "把王命从工地泥水里抬出来。",
    },
    "stability": {
        "short": "安宁",
        "trade_title": "扰动乡里",
        "choice_title": "秩序松动",
        "strain_title": "地方安宁受扰",
        "crisis_title": "秩序在征发中破声",
        "engineer_loss1_title": "大工程师误触安宁",
        "engineer_loss2_title": "大工程师搅乱地方",
        "trade_scene": "地方官同意加快征调人手和车辆，让原本安静的乡里为工程让出道路",
        "trade_after": "被惊动的日常秩序不会立刻恢复原状",
        "choice_pressure": "地方已经被频繁的征调和传令搅得心神不宁，再多一步就会有人把怨气说出口",
        "choice_loss": "稳定度会在看似普通的命令之间松动",
        "decline_option": "不要再惊动乡里",
        "spend_option": "让地方秩序为工程让路",
        "loss1_desc": (
            "额外征调打乱了几处市镇的平常节奏，抱怨先在酒馆里出现，随后才进入官员的耳朵。"
            "稳定度受到冲击，工程也因此显得比石头更重。"
        ),
        "loss2_desc": (
            "几地同时出现延误、争执和拒役，地方秩序被工程牵出一串裂响。"
            "官员们仍能压住局面，却无法否认稳定度已经为奇观付出一笔硬账。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}只看见调度表上的空格，却没有看见村镇日常能承受多少扰动。"
            "工地得到了人手，稳定度却被拉扯了一下。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}连续改变征调安排，使地方官还没解释完上一道命令就收到下一道。"
            "安宁被搅碎，稳定度也随之下跌。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "先把地方怨气压下去。",
        "option_loss2": "让巡吏去收拾回声。",
        "option_engineer_loss1": "让工程师听一听地方官。",
        "option_engineer_loss2": "把混乱从排程里剔除。",
    },
    "prestige": {
        "short": "声名",
        "trade_title": "透支声名",
        "choice_title": "威望蒙尘",
        "strain_title": "宫廷声望失色",
        "crisis_title": "威望在众目下折损",
        "engineer_loss1_title": "大工程师误伤声望",
        "engineer_loss2_title": "大工程师毁了体面",
        "trade_scene": "宫廷愿意把已经积累的声名借给工地，用典礼、宣告和夸饰遮住几处现实缺口",
        "trade_after": "夸下的词句会反过来要求结果",
        "choice_pressure": "若工程继续把宏伟挂在嘴边却拿不出相称进展，宫廷威望就会成为被嘲笑的靶子",
        "choice_loss": "威望会在每一次过早的宣告后褪色",
        "decline_option": "别把声望再押上去",
        "spend_option": "拿宫廷声名替工程开路",
        "loss1_desc": (
            "一次本该显示气派的工程展示只让来宾看见了未完成的尴尬。"
            "威望受到轻微折损，宫廷仍然体面，只是笑声来得比掌声更快。"
        ),
        "loss2_desc": (
            "关于工地失误的消息传得太快，远方使节听到的版本甚至比现场更锋利。"
            "威望被公开磨损，奇观还未完成，已经先替国家招来一场难看的审视。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}过早宣布了一项尚未稳固的成果。"
            "当细节被追问时，工程还能解释，威望却先红了脸。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}把一场施工失误变成了公开笑柄。"
            "石头可以重砌，威望却不能用同一把凿子修好。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "把失色的体面擦一擦。",
        "option_loss2": "这份羞辱要有人记账。",
        "option_engineer_loss1": "让工程师少说多做。",
        "option_engineer_loss2": "先把宫廷脸面救回来。",
    },
    "nobles_satisfaction": {
        "short": "贵族",
        "trade_title": "借用贵族耐性",
        "choice_title": "贵族怨言",
        "strain_title": "贵族席间传出冷语",
        "crisis_title": "贵族耐心被凿穿",
        "engineer_loss1_title": "大工程师怠慢贵族",
        "engineer_loss2_title": "大工程师激怒贵族",
        "trade_scene": "数家显贵同意把车马、佃户和名义借给工地，只是他们的微笑比契约更薄",
        "trade_after": "宴席上的沉默会记住这次让步",
        "choice_pressure": "贵族已经觉得工程拿走了太多车马和面子，再要一次就会从冷淡变成怨恨",
        "choice_loss": "贵族阶层满意度会在礼貌的沉默里下降",
        "decline_option": "别再试探贵族耐性",
        "spend_option": "借贵族的车马与面子",
        "loss1_desc": (
            "几位贵族把原本答应的协助照常送到，却在席间把话说得很凉。"
            "贵族阶层满意度受损，工地得到的帮助也因此带上了欠债的味道。"
        ),
        "loss2_desc": (
            "工程征用越过了某些显贵能忍受的界线，抱怨开始从私人书信流向公开场合。"
            "贵族阶层满意度明显下跌，奇观的每一块石头都像压在一张纹章上。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}安排车马时忘了给几家贵族留下体面。"
            "物资到了，脸色也到了，贵族阶层满意度随之受损。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}把贵族的让步当成理所当然，直到他们决定用冷硬的礼貌回应。"
            "工程仍有车马，国家却少了贵族的好脸色。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "派人去贵族席间解释。",
        "option_loss2": "这杯冷酒先饮下去。",
        "option_engineer_loss1": "让工程师补上礼数。",
        "option_engineer_loss2": "去安抚那些被轻慢的纹章。",
    },
    "clergy_satisfaction": {
        "short": "教士",
        "trade_title": "动用教士宽容",
        "choice_title": "祭坛不悦",
        "strain_title": "祭坛前的眉头",
        "crisis_title": "教士耐心告罄",
        "engineer_loss1_title": "大工程师触犯祭坛",
        "engineer_loss2_title": "大工程师冒犯教士",
        "trade_scene": "教士们同意缩短若干仪式、让出若干地产便利和祝祷时辰，好让工程赶上安排",
        "trade_after": "祭坛旁的低语会问这一切是否过于世俗",
        "choice_pressure": "教士已经觉得奇观把神圣用作施工借口，再多一步就会让讲坛发出责备",
        "choice_loss": "教士阶层满意度会在祈祷声里冷下去",
        "decline_option": "别让祭坛继续让步",
        "spend_option": "请教士为工地让出时辰",
        "loss1_desc": (
            "几场仪式因工程安排被迫简化，讲坛上的语气随之变得谨慎而冷。"
            "教士阶层满意度下降，奇观在神圣名义下多了一层不安。"
        ),
        "loss2_desc": (
            "一项施工决定被教士视为对礼仪的公开冒犯。"
            "解释可以送到修院，却无法让被冒犯者立刻点头；教士阶层满意度遭到重创。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}把祭日当成普通日程来排，直到教士们用沉默提醒工地并非万事皆可调度。"
            "教士阶层满意度因此受损。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}在不合时宜的地点开工，让祭坛旁的人把锤声听成冒犯。"
            "工程抢到了一日，教士阶层满意度却失去许多。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "向祭坛送去迟来的歉意。",
        "option_loss2": "让神职者先把怒意说完。",
        "option_engineer_loss1": "让工程师记住祭历。",
        "option_engineer_loss2": "把工地从祭坛前退开。",
    },
    "burghers_satisfaction": {
        "short": "市民",
        "trade_title": "占用市民便利",
        "choice_title": "商街怨声",
        "strain_title": "商街账本变薄",
        "crisis_title": "市民怒气上街",
        "engineer_loss1_title": "大工程师压住商街",
        "engineer_loss2_title": "大工程师惹恼市民",
        "trade_scene": "城镇商人同意让仓库、码头和信用暂时偏向工地，哪怕市场因此少了几分顺滑",
        "trade_after": "账房会把这份不便逐笔记下",
        "choice_pressure": "市民已经为封路、征车和临时仓储让出太多便利，商街的笑脸快维持不住",
        "choice_loss": "市民阶层满意度会在账本边缘被削薄",
        "decline_option": "别再挤压商街",
        "spend_option": "让商街替工地周转",
        "loss1_desc": (
            "几处市场因工程调度改道，商人们照常营业，却把算盘拨得格外响。"
            "市民阶层满意度下降，工地从商街借来的便利开始计息。"
        ),
        "loss2_desc": (
            "临时征用仓库和码头的命令引发了公开抱怨，商街终于不愿只在账房里生气。"
            "市民阶层满意度大幅受损，工程的影子压到了每一张柜台上。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}为了赶料，要求商街连续几日替工地让路。"
            "货物到了，市民阶层满意度却被堵在路口。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}把商人的仓库视为工地附属，直到市民决定用公开怨声追回界线。"
            "这次误判让市民阶层满意度狠狠下跌。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "向商街许诺补偿。",
        "option_loss2": "先让市场重新开门。",
        "option_engineer_loss1": "让工程师给商人让出路来。",
        "option_engineer_loss2": "把仓库钥匙还给市民。",
    },
    "peasants_satisfaction": {
        "short": "平民",
        "trade_title": "借走乡民余力",
        "choice_title": "村社疲惫",
        "strain_title": "村社肩背发沉",
        "crisis_title": "平民怨气压不住",
        "engineer_loss1_title": "大工程师低估乡里",
        "engineer_loss2_title": "大工程师压垮村社",
        "trade_scene": "乡村被要求多出劳役、车驾和粮秣，地方官保证这只是临时安排",
        "trade_after": "田埂上的疲惫不会因为文书写着临时就消失",
        "choice_pressure": "平民已经在农时和工役之间来回奔走，再加一层负担就会让沉默变成怨声",
        "choice_loss": "平民阶层满意度会在田垄之间掉落",
        "decline_option": "别再抽走乡民余力",
        "spend_option": "让村社再撑一程",
        "loss1_desc": (
            "劳役名单又向乡里伸出一截，村社照办，却把怨气藏进晚饭后的沉默里。"
            "平民阶层满意度下降，奇观的宏伟在田垄上显得格外遥远。"
        ),
        "loss2_desc": (
            "一轮过重的征调撞上农时，村社的忍耐终于破出声来。"
            "平民阶层满意度明显受损，工地得到的每一双手都带着被迫离开的影子。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}在排程上看见的是可用人手，在村社里留下的却是缺席的父兄。"
            "平民阶层满意度因此受损。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}把劳役推过了乡里能承受的边界。"
            "工地多了人，村社少了耐心，平民阶层满意度随之重挫。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "让地方官去听村社诉苦。",
        "option_loss2": "这份怨气会沿田埂传开。",
        "option_engineer_loss1": "让工程师重新数一数农时。",
        "option_engineer_loss2": "把劳役从乡里肩上卸下一些。",
    },
    "site_development": {
        "short": "工址发展",
        "trade_title": "拆用工址积累",
        "choice_title": "工址被掏空",
        "strain_title": "工址街区让出骨肉",
        "crisis_title": "工址发展倒退",
        "engineer_loss1_title": "大工程师拆错街区",
        "engineer_loss2_title": "大工程师伤及工址",
        "trade_scene": "建设地点周边的既有设施被拆改、征用和改道，好给奇观腾出更顺手的空间",
        "trade_after": "当地原本积累的便利会留下缺口",
        "choice_pressure": "工址周边能拆能改的地方越来越少，再动一刀就会伤到当地自己的生计",
        "choice_loss": "建设地点发展度会被工程从脚下掏走一块",
        "decline_option": "别再拆用工址街区",
        "spend_option": "拆改工址既有设施",
        "loss1_desc": (
            "几处原本服务当地的设施被改作工程用途，居民仍能生活，却明显绕了更远的路。"
            "建设地点发展度受损，奇观开始从自己的地基周围取肉。"
        ),
        "loss2_desc": (
            "为了工地便利，一片原本繁忙的街区被强行拆改到失去原有功能。"
            "建设地点发展度明显下降，未来的奇观将站在一块被它自己削瘦的土地上。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}把一处看似碍事的街区划入拆改范围，却低估了它对当地日常的支撑。"
            "建设地点发展度因此受损。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}为赶工拆掉了太多工址周边的骨架。"
            "奇观得到空间，当地发展却被硬生生削下一层。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "先修补工址周边的空洞。",
        "option_loss2": "这块地会记住拆痕。",
        "option_engineer_loss1": "让工程师重新画拆改线。",
        "option_engineer_loss2": "停止继续啃食工址。",
    },
    "site_prosperity": {
        "short": "工址繁荣",
        "trade_title": "抽走工址生意",
        "choice_title": "工址繁荣降温",
        "strain_title": "工址市声变低",
        "crisis_title": "工址繁荣被压熄",
        "engineer_loss1_title": "大工程师扰乱工址生计",
        "engineer_loss2_title": "大工程师熄了工址市声",
        "trade_scene": "当地的客栈、作坊和集市被要求优先服务工地，原本流动的生意被引向同一个巨口",
        "trade_after": "被抽走的市声不会立刻回到街角",
        "choice_pressure": "工址附近的生意已经被工程吞下太多，再继续抽调会让繁荣本身开始退潮",
        "choice_loss": "建设地点繁荣度会在看似热闹的工棚旁降温",
        "decline_option": "让工址生意喘口气",
        "spend_option": "把当地生意转向工地",
        "loss1_desc": (
            "工地带来了人潮，却也把当地原本多样的生意挤成单一的供给线。"
            "建设地点繁荣度下降，街市仍然喧闹，却不再像从前那样自由流动。"
        ),
        "loss2_desc": (
            "连续的封路、征用和优先供应让工址周边的正常交易冷了下来。"
            "建设地点繁荣度遭到重击，奇观的阴影第一次盖过了街市的烟火气。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}把当地所有便利都视作工程供应链的一部分。"
            "工地更顺了，建设地点繁荣度却被挤得发皱。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}连续改变道路和供给安排，使工址周边的生意无处落脚。"
            "繁荣被施工声压低，损失已经无法装作寻常。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "让街市重新流动起来。",
        "option_loss2": "别让工地吞完整座街市。",
        "option_engineer_loss1": "让工程师给生意留路。",
        "option_engineer_loss2": "把市声从锤声下救出来。",
    },
    "capital_development": {
        "short": "首都发展",
        "trade_title": "挪用首都积累",
        "choice_title": "首都骨架受削",
        "strain_title": "首都工程被迫让路",
        "crisis_title": "首都发展替奇观买单",
        "engineer_loss1_title": "大工程师误拆首都余裕",
        "engineer_loss2_title": "大工程师掏空首都安排",
        "trade_scene": "首都几项原定修缮和扩建被暂缓，熟练工匠与材料转而支援奇观",
        "trade_after": "宫城与街区会记住被推迟的承诺",
        "choice_pressure": "首都自己的工程已经多次让路，再抽调一次就会把城市的骨架削得太明显",
        "choice_loss": "首都发展度会替奇观承担看得见的缺口",
        "decline_option": "别再挪走首都积累",
        "spend_option": "让首都工程暂且让路",
        "loss1_desc": (
            "首都几处原本排定的修缮被推迟，工匠和材料流向远处或城郊的奇观工地。"
            "首都发展度受损，中心之城第一次显得像在为自己的荣光节衣缩食。"
        ),
        "loss2_desc": (
            "一轮过重的抽调让首都街区的实际建设停摆，连宫廷也难以假装这只是临时挪用。"
            "首都发展度明显下降，奇观的账单被送到了王国心脏。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}从首都调走一批关键匠人时，没有意识到他们原本支撑着多少既定工程。"
            "首都发展度因此受损。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}把首都的修缮安排拆成了奇观的备用零件。"
            "工地暂时顺利，首都发展却被掏出一个清楚的洞。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "让首都先把缺口遮住。",
        "option_loss2": "王城也会记账。",
        "option_engineer_loss1": "让工程师归还首都匠人。",
        "option_engineer_loss2": "停止拆解首都的未来。",
    },
    "capital_prosperity": {
        "short": "首都繁荣",
        "trade_title": "借首都商气",
        "choice_title": "首都繁荣失温",
        "strain_title": "首都街市变冷",
        "crisis_title": "王城市声被压低",
        "engineer_loss1_title": "大工程师扰乱王城市声",
        "engineer_loss2_title": "大工程师压熄首都繁荣",
        "trade_scene": "首都市场的信用、仓储和人流被工程吸走一部分，最繁华的街道也为远处的石头腾出余裕",
        "trade_after": "王城市声会短暂低下去",
        "choice_pressure": "首都商路已经被工程借走太多周转，再继续抽取会让繁荣在街角失温",
        "choice_loss": "首都繁荣度会在最亮的橱窗后暗下去",
        "decline_option": "别再抽走王城市声",
        "spend_option": "把首都商气引向工地",
        "loss1_desc": (
            "首都市场仍旧拥挤，但几条原本最灵活的商路被工程调度牵住。"
            "首都繁荣度下降，繁华没有消失，只是被迫放慢了呼吸。"
        ),
        "loss2_desc": (
            "连续抽调仓储、车马和信用之后，首都街市明显冷了下来。"
            "首都繁荣度受到重创，王城第一次像是在替一座尚未完工的纪念碑禁声。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}为了让材料准时到达，强行改写了首都几条重要商路的节奏。"
            "工地听见车轮声，王城却少了市声。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}连续从首都市场抽走周转能力，让繁荣像火盆一样被人掀开。"
            "奇观的供应稳住了，首都繁荣度却明显下跌。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "让王城商路重新呼吸。",
        "option_loss2": "这阵冷清太过刺眼。",
        "option_engineer_loss1": "让工程师放过几条商路。",
        "option_engineer_loss2": "把市声还给首都。",
    },
    "site_laborers": {
        "short": "劳工",
        "trade_title": "压上劳工筋骨",
        "choice_title": "劳工倒下",
        "strain_title": "工地伤亡添名",
        "crisis_title": "劳工血汗越过界线",
        "engineer_loss1_title": "大工程师误判劳役极限",
        "engineer_loss2_title": "大工程师酿成伤亡",
        "trade_scene": "工头要求劳工延长班次，把休息、替换和安全余量一并压缩到最窄",
        "trade_after": "疲惫的身体会把代价记得比账册更准",
        "choice_pressure": "劳工已经在石尘和绳索下撑到极限，再赶一步就会有人倒在奇观的影子里",
        "choice_loss": "建设地点劳工会用伤亡替工程付款",
        "decline_option": "别再压榨劳工筋骨",
        "spend_option": "让劳工再撑一轮",
        "loss1_desc": (
            "几处工段为了赶时辰压缩了休息，伤病名单随即多出一些本可避免的姓名。"
            "建设地点劳工遭受损失，工地的进度表第一次显得像一张冷硬的判词。"
        ),
        "loss2_desc": (
            "一次过度赶工造成了严重伤亡，血和石粉一起留在未完成的部件旁。"
            "建设地点劳工付出惨痛代价，任何关于宏伟的词句都暂时说不出口。"
        ),
        "engineer_loss1_desc": (
            f"{ENGINEER_SCOPE_ZH}把劳工当作排程上可以延展的线，却忘了人的筋骨不会按墨线弯曲。"
            "伤病增加，建设地点劳工为这次误判付出代价。\\n\\n"
            f"{ENGINEER_NOTE_BAD_50_ZH}"
        ),
        "engineer_loss2_desc": (
            f"{ENGINEER_SCOPE_ZH}批准了一次过于凶狠的赶工，结果让伤亡越过了所有人能轻描淡写的界线。"
            "奇观继续沉默地上升，劳工却倒在它脚下。\\n\\n"
            f"{ENGINEER_NOTE_BAD_20_ZH}"
        ),
        "option_loss1": "先把伤者抬离工段。",
        "option_loss2": "这不是能被石粉盖住的事。",
        "option_engineer_loss1": "让工程师重新计算人的极限。",
        "option_engineer_loss2": "停止这场带血的赶工。",
    },
}


def zh_engineering_flavor(token: dict) -> dict:
    return ZH_ENGINEERING_FLAVOR[token["id"]]


def zh_non_engineering_flavor(token: dict) -> dict:
    return ZH_NON_ENGINEERING_FLAVOR[token["id"]]


def apply_zh_concept_format(text: str) -> str:
    for old, new in ZH_CONCEPT_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def apply_en_concept_format(text: str) -> str:
    for old, new in EN_CONCEPT_REPLACEMENTS:
        text = text.replace(old, new)
    return text


def en_engineering_title_flavor(token: dict) -> dict:
    return EN_ENGINEERING_TITLE_FLAVOR[token["id"]]


def en_non_engineering_title_flavor(token: dict) -> dict:
    return EN_NON_ENGINEERING_TITLE_FLAVOR[token["id"]]


def format_title_en(event: dict) -> str:
    kind = event["kind"]
    eng = en_engineering_title_flavor(event["eng"]) if event.get("eng") else None
    noneng = en_non_engineering_title_flavor(event["noneng"]) if event.get("noneng") else None

    if kind == "gain_engineering_2":
        core = eng["gain2_title"]
    elif kind == "gain_engineering_1":
        core = eng["gain1_title"]
    elif kind == "trade_noneng_for_eng":
        core = f"{noneng['trade_title']} for {eng['trade_title']}"
    elif kind == "swing_engineering_1":
        core = eng["swing_title"]
    elif kind == "choose_eng_or_noneng_loss":
        core = f"{eng['choice_title']} or {noneng['choice_title']}"
    elif kind == "lose_noneng_1":
        core = noneng["strain_title"]
    elif kind == "lose_noneng_2":
        core = noneng["crisis_title"]
    elif kind == "engineer_gain_engineering_2":
        core = eng["engineer_gain2_title"]
    elif kind == "engineer_gain_engineering_1":
        core = eng["engineer_gain1_title"]
    elif kind == "engineer_swing_engineering_1":
        core = eng["engineer_swing_title"]
    elif kind == "engineer_lose_noneng_1":
        core = noneng["engineer_loss1_title"]
    elif kind == "engineer_lose_noneng_2":
        core = noneng["engineer_loss2_title"]
    else:
        raise ValueError(f"Unhandled wonder event kind: {kind}")
    return f"[tv_wonder_construction|E]：{core}"


def format_title_zh(event: dict) -> str:
    kind = event["kind"]
    eng = zh_engineering_flavor(event["eng"]) if event.get("eng") else None
    noneng = zh_non_engineering_flavor(event["noneng"]) if event.get("noneng") else None

    if kind == "gain_engineering_2":
        core = eng["gain2_title"]
    elif kind == "gain_engineering_1":
        core = eng["gain1_title"]
    elif kind == "trade_noneng_for_eng":
        core = f"{noneng['trade_title']}，换{eng['trade_title']}"
    elif kind == "swing_engineering_1":
        core = eng["swing_title"]
    elif kind == "choose_eng_or_noneng_loss":
        core = f"{eng['choice_title']}，还是{noneng['choice_title']}"
    elif kind == "lose_noneng_1":
        core = noneng["strain_title"]
    elif kind == "lose_noneng_2":
        core = noneng["crisis_title"]
    elif kind == "engineer_gain_engineering_2":
        core = eng["engineer_gain2_title"]
    elif kind == "engineer_gain_engineering_1":
        core = eng["engineer_gain1_title"]
    elif kind == "engineer_swing_engineering_1":
        core = eng["engineer_swing_title"]
    elif kind == "engineer_lose_noneng_1":
        core = noneng["engineer_loss1_title"]
    elif kind == "engineer_lose_noneng_2":
        core = noneng["engineer_loss2_title"]
    else:
        raise ValueError(f"Unhandled wonder event kind: {kind}")
    return apply_zh_concept_format(f"[tv_wonder_construction|E]：{core}")


def format_desc_zh(event: dict) -> str:
    kind = event["kind"]
    eng = zh_engineering_flavor(event["eng"]) if event.get("eng") else None
    noneng = zh_non_engineering_flavor(event["noneng"]) if event.get("noneng") else None

    if kind == "gain_engineering_2":
        return eng["gain2_desc"]
    if kind == "gain_engineering_1":
        return eng["gain1_desc"]
    if kind == "trade_noneng_for_eng":
        return (
            f"{noneng['trade_scene']}。工程部门趁这阵并不体面的余裕，把{eng['trade_need']}推进到图纸和工棚之间。"
            f"{eng['trade_result']}，但{noneng['trade_after']}。这不是没有代价的聪明，"
            "只是把代价放到了当下最容易被承受的位置。"
        )
    if kind == "swing_engineering_1":
        return eng["swing_desc"]
    if kind == "choose_eng_or_noneng_loss":
        return (
            f"{eng['choice_pressure']}，同时{noneng['choice_pressure']}。"
            f"若让工程自己吞下这口气，{eng['choice_loss']}；若把压力推出围栏，{noneng['choice_loss']}。"
            "参事们都能说明两边为何必要，却没有人能把账页变干净。"
        )
    if kind == "lose_noneng_1":
        return noneng["loss1_desc"]
    if kind == "lose_noneng_2":
        return noneng["loss2_desc"]
    if kind == "engineer_gain_engineering_2":
        return eng["engineer_gain2_desc"]
    if kind == "engineer_gain_engineering_1":
        return eng["engineer_gain1_desc"]
    if kind == "engineer_swing_engineering_1":
        return eng["engineer_swing_desc"]
    if kind == "engineer_lose_noneng_1":
        return noneng["engineer_loss1_desc"]
    if kind == "engineer_lose_noneng_2":
        return noneng["engineer_loss2_desc"]
    raise ValueError(f"Unhandled wonder event kind: {kind}")


def option_loc_zh(event: dict, suffix: str) -> str:
    kind = event["kind"]
    eng = zh_engineering_flavor(event["eng"]) if event.get("eng") else None
    noneng = zh_non_engineering_flavor(event["noneng"]) if event.get("noneng") else None

    if kind == "gain_engineering_2":
        return eng["option_gain2"]
    if kind == "gain_engineering_1":
        return eng["option_gain1"]
    if kind == "trade_noneng_for_eng":
        if suffix == "a":
            return f"{noneng['spend_option']}，换来{eng['short']}上的余裕。"
        return f"{noneng['decline_option']}，让{eng['short']}慢慢积累。"
    if kind == "swing_engineering_1":
        return eng["option_swing"]
    if kind == "choose_eng_or_noneng_loss":
        if suffix == "a":
            return f"让{eng['short']}先退一步，免得{noneng['short']}被拖下水。"
        return f"保住{eng['short']}，把压力推给{noneng['short']}。"
    if kind == "lose_noneng_1":
        return noneng["option_loss1"]
    if kind == "lose_noneng_2":
        return noneng["option_loss2"]
    if kind == "engineer_gain_engineering_2":
        return eng["option_engineer_gain2"]
    if kind == "engineer_gain_engineering_1":
        return eng["option_engineer_gain1"]
    if kind == "engineer_swing_engineering_1":
        return eng["option_engineer_swing"]
    if kind == "engineer_lose_noneng_1":
        return noneng["option_engineer_loss1"]
    if kind == "engineer_lose_noneng_2":
        return noneng["option_engineer_loss2"]
    raise ValueError(f"Unhandled wonder event kind: {kind}")


def load_data() -> dict:
    with DATA_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def eng_name(token: dict, lang: str) -> str:
    return token["loc"]["en_effect" if lang == "en" else "zh_effect"]


def noneng_name(token: dict, lang: str) -> str:
    return token["loc"][lang]


def event_weight(kind: str, eng: dict | None = None, noneng: dict | None = None) -> int:
    weight = EVENT_KIND_WEIGHTS[kind]
    if eng is not None:
        weight *= eng["weight"]
    if noneng is not None:
        weight *= noneng["weight"]
    return weight


def build_events(data: dict) -> list[dict]:
    events: list[dict] = []
    event_id = int(data["event_id_start"])
    eng_tokens = data["engineering_tokens"]
    noneng_tokens = data["non_engineering_tokens"]

    def add(kind: str, eng: dict | None = None, noneng: dict | None = None) -> None:
        nonlocal event_id
        events.append(
            {
                "id": event_id,
                "kind": kind,
                "eng": eng,
                "noneng": noneng,
                "outcome": KIND_OUTCOMES[kind],
                "weight": event_weight(kind, eng, noneng),
            }
        )
        event_id += 1

    for eng in eng_tokens:
        add("gain_engineering_2", eng=eng)
    for eng in eng_tokens:
        add("gain_engineering_1", eng=eng)
    for eng in eng_tokens:
        for noneng in noneng_tokens:
            add("trade_noneng_for_eng", eng=eng, noneng=noneng)
    for eng in eng_tokens:
        add("swing_engineering_1", eng=eng)
    for eng in eng_tokens:
        for noneng in noneng_tokens:
            add("choose_eng_or_noneng_loss", eng=eng, noneng=noneng)
    for noneng in noneng_tokens:
        add("lose_noneng_1", noneng=noneng)
    for noneng in noneng_tokens:
        add("lose_noneng_2", noneng=noneng)
    for eng in eng_tokens:
        add("engineer_gain_engineering_2", eng=eng)
    for eng in eng_tokens:
        add("engineer_gain_engineering_1", eng=eng)
    for eng in eng_tokens:
        add("engineer_swing_engineering_1", eng=eng)
    for noneng in noneng_tokens:
        add("engineer_lose_noneng_1", noneng=noneng)
    for noneng in noneng_tokens:
        add("engineer_lose_noneng_2", noneng=noneng)
    return events


def format_title(event: dict, lang: str) -> str:
    if lang == "zh":
        return format_title_zh(event)
    if lang == "en":
        return format_title_en(event)
    template = KIND_TITLE[event["kind"]][lang]
    eng = eng_name(event["eng"], lang) if event.get("eng") else ""
    noneng = noneng_name(event["noneng"], lang) if event.get("noneng") else ""
    core = template.format(eng=eng, eng_effect=eng, noneng=noneng)
    return f"奇观建设：{core}"


def format_desc(event: dict, lang: str) -> str:
    if lang == "zh":
        return apply_zh_concept_format(format_desc_zh(event))
    template = KIND_DESC[event["kind"]][lang]
    eng = ENGINEERING_CONCEPT_REF_EN[event["eng"]["id"]] if lang == "en" and event.get("eng") else eng_name(event["eng"], lang) if event.get("eng") else ""
    noneng = NON_ENGINEERING_CONCEPT_REF_EN[event["noneng"]["id"]] if lang == "en" and event.get("noneng") else noneng_name(event["noneng"], lang) if event.get("noneng") else ""
    return apply_en_concept_format(template.format(eng=eng, noneng=noneng))


def option_loc(event_or_kind: dict | str, suffix: str, lang: str) -> str:
    if isinstance(event_or_kind, dict):
        if lang == "zh":
            return apply_zh_concept_format(option_loc_zh(event_or_kind, suffix))
        kind = event_or_kind["kind"]
    else:
        kind = event_or_kind
    return KIND_OPTIONS[kind][suffix][lang]


def indent_lines(text: str, level: int) -> str:
    return "\n".join((T * level + line if line.strip() else "") for line in text.rstrip().splitlines())


def render_header(script: str, data: str, extra: str = "") -> str:
    suffix = f"\n{extra.rstrip()}\n" if extra else "\n"
    return (
        f"# @Generated by {script}\n"
        f"#   Data:    {data}\n"
        f"#   Regen:   conda run --no-capture-output -n eu5 python {script}\n"
        "# Do not edit directly - modify the data file and re-run the generator.\n"
        f"{suffix}"
    )
