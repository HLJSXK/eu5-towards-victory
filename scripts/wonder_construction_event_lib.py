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
    template = KIND_TITLE[event["kind"]][lang]
    eng = eng_name(event["eng"], lang) if event.get("eng") else ""
    noneng = noneng_name(event["noneng"], lang) if event.get("noneng") else ""
    core = template.format(eng=eng, eng_effect=eng, noneng=noneng)
    if lang == "en":
        return f"Wonder Construction: {core}"
    return f"奇观建设：{core}"


def format_desc(event: dict, lang: str) -> str:
    template = KIND_DESC[event["kind"]][lang]
    eng = eng_name(event["eng"], lang).lower() if lang == "en" and event.get("eng") else eng_name(event["eng"], lang) if event.get("eng") else ""
    noneng = noneng_name(event["noneng"], lang) if event.get("noneng") else ""
    return template.format(eng=eng, noneng=noneng)


def option_loc(kind: str, suffix: str, lang: str) -> str:
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
