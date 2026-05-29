import json
import sys
from copy import deepcopy
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_mechanics_lib import (  # noqa: E402
    ceremony_styles,
    generic_ritual_for_wonder,
    load_generic_wonder_mechanics_data,
    load_unique_wonders,
    mechanic_key,
    unique_ritual,
)

OUT_FILE = REPO_ROOT / "data" / "wonder_effects.json"

SIZE_LABELS = {
    "small": "小型",
    "medium": "中型",
    "large": "大型",
}

ESTATE_LABELS = {
    "burghers_estate": "市民阶层",
    "clergy_estate": "教士阶层",
    "nobles_estate": "贵族阶层",
    "peasants_estate": "平民阶层",
}

RESEARCH_PROGRESS_LABELS = {
    "research_progress_mild_bonus": 5,
    "research_progress_severe_bonus": 10,
    "research_progress_extreme_bonus": 15,
}

MODIFIER_LABELS = {
    "army_movement_speed": ("行军速度", "percent"),
    "clergy_estate_target_satisfaction": ("教士满意度均衡点", "percent"),
    "diplomatic_reputation": ("外交声誉", "flat_int"),
    "fort_level": ("要塞等级", "flat_int"),
    "global_crown_estate_power": ("全国王室阶层力量", "percent"),
    "global_distance_from_capital_speed_propagation": ("全国距首都传播速度", "percent"),
    "global_garrison_size_modifier": ("全国驻军规模", "percent"),
    "global_manpower_modifier": ("全国人力", "percent"),
    "global_monthly_prosperity": ("每月全国繁荣度", "flat_decimal"),
    "global_pop_conversion_speed_modifier": ("全国人口皈依速度", "percent"),
    "global_production_efficiency": ("全国生产效率", "percent"),
    "global_raw_material_output": ("全国原料产出", "percent"),
    "harbor_suitability": ("港口适宜度", "percent"),
    "land_morale_modifier": ("陆军士气", "percent"),
    "local_burghers_estate_power": ("本地市民阶层力量", "percent"),
    "local_clergy_estate_power": ("本地教士阶层力量", "percent"),
    "local_clergy_max_literacy": ("本地教士最大识字率", "flat_int"),
    "local_crown_estate_power": ("本地王室阶层力量", "percent"),
    "local_cultural_influence": ("本地文化影响", "flat_decimal"),
    "local_cultural_tradition": ("本地文化传统", "flat_decimal"),
    "local_defensive": ("本地防御", "percent"),
    "local_distance_from_capital_speed_propagation": ("本地距首都传播速度", "percent"),
    "local_garrison_size": ("本地驻军规模", "flat_int"),
    "local_manpower_modifier": ("本地人力", "percent"),
    "local_max_control": ("本地最大控制力", "percent"),
    "local_max_literacy": ("本地最大识字率", "flat_int"),
    "local_max_rgo_size_modifier": ("本地原料产出上限", "percent"),
    "local_migration_attraction": ("本地迁入吸引力", "flat_int"),
    "local_monthly_development_modifier": ("本地月发展度", "percent"),
    "local_monthly_literacy": ("本地月识字率", "flat_decimal"),
    "local_nobles_estate_power": ("本地贵族阶层力量", "percent"),
    "local_peasants_estate_power": ("本地平民阶层力量", "percent"),
    "local_pop_assimilation_speed": ("本地人口同化速度", "percent"),
    "local_pop_conversion_speed": ("本地人口皈依速度", "percent"),
    "local_pop_promotion_speed": ("本地人口晋升速度", "percent"),
    "local_production_efficiency": ("本地生产效率", "percent"),
    "local_raw_material_output": ("本地原料产出", "percent"),
    "local_ship_build_speed": ("本地造船速度", "percent"),
    "local_trade_center_power": ("本地贸易中心力量", "percent"),
    "local_unrest": ("本地叛乱度", "percent"),
    "max_ships_built_at_same_time": ("同时建造船只上限", "flat_int"),
    "minting_income_factor": ("铸币收入", "percent"),
    "monthly_legitimacy": ("每月正统性", "flat_decimal"),
    "monthly_prestige": ("每月威望", "flat_decimal"),
    "monthly_towards_centralization": ("每月中央集权倾向", "flat_decimal"),
    "naval_morale_modifier": ("海军士气", "percent"),
    "naval_range": ("海军范围", "flat_int"),
    "peasants_estate_target_satisfaction": ("平民满意度均衡点", "percent"),
    "research_speed": ("研究速度", "percent"),
    "ship_build_speed": ("造船速度", "percent"),
    "siege_ability": ("攻城能力", "percent"),
    "stability_investment": ("稳定度投资成本", "percent"),
    "tax_income_efficiency": ("税收收入效率", "percent"),
    "tolerance_own": ("正统信仰容忍", "flat_int"),
    "trade_income": ("贸易收入", "percent"),
    "trade_range": ("贸易范围", "flat_int"),
}


def signed_number(value: float | int) -> str:
    if isinstance(value, float):
        text = f"{value:.3f}".rstrip("0").rstrip(".")
    else:
        text = str(value)
    if text.startswith("-"):
        return text
    return f"+{text}"


def ensure_sentence(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    if stripped[-1] in "。！？.!?":
        return stripped
    return f"{stripped}。"


def join_fragments(fragments: list[str]) -> str:
    return "".join(ensure_sentence(fragment) for fragment in fragments if fragment.strip())


def format_modifier(key: str, value: float | int) -> str:
    label, kind = MODIFIER_LABELS.get(key, (key, "raw"))
    if kind == "percent":
        display_value = value * 100 if abs(value) <= 1 else value
        return f"{signed_number(display_value)}% {label}"
    if kind == "flat_int":
        return f"{signed_number(value)} {label}"
    if kind == "flat_decimal":
        return f"{signed_number(value)} {label}"
    return f"{signed_number(value)} {label}"


def format_modifiers(modifiers: dict[str, float | int]) -> str:
    return "、".join(format_modifier(key, value) for key, value in modifiers.items())


def burden_modifiers(blessing: dict[str, float | int]) -> dict[str, float | int]:
    return {key: value * -2 for key, value in blessing.items()}


def estate_power_key(pop_type: str) -> str:
    return {
        "burghers": "local_burghers_estate_power",
        "clergy": "local_clergy_estate_power",
        "laborers": "local_peasants_estate_power",
        "nobles": "local_nobles_estate_power",
        "soldiers": "local_crown_estate_power",
    }[pop_type]


def format_reward(entry: dict[str, object]) -> str:
    effect_type = entry["type"]
    if effect_type == "stability":
        return f"{signed_number(entry['value'])} 稳定度"
    if effect_type == "prestige":
        return f"{signed_number(entry['value'])} 威望"
    if effect_type == "legitimacy":
        return f"{signed_number(entry['value'])} 正统性"
    if effect_type == "gold":
        return f"{signed_number(entry['value'])} 金钱"
    if effect_type == "manpower":
        return f"{signed_number(entry['value'])} 人力"
    if effect_type == "research_progress":
        return f"+{RESEARCH_PROGRESS_LABELS[str(entry['value'])]} 研究进度"
    if effect_type == "ruler_adm":
        return f"统治者 {signed_number(entry['value'])} 行政"
    if effect_type == "ruler_dip":
        return f"统治者 {signed_number(entry['value'])} 外交"
    if effect_type == "ruler_mil":
        return f"统治者 {signed_number(entry['value'])} 军事"
    if effect_type == "site_prosperity":
        return f"{signed_number(entry['value'])} 本地繁荣度"
    if effect_type == "estate_satisfaction":
        estate = ESTATE_LABELS[str(entry["estate"])]
        return f"{signed_number(entry['value'] * 100)}% {estate}满意度"
    raise ValueError(f"Unsupported ritual reward effect type: {effect_type}")


def cost_label(cost_type: str | None) -> str:
    return {
        None: "",
        "artwork": "1 件艺术品",
        "scaled_gold": "`scaled_gold = 5`",
        "prestige": "50 威望",
    }[cost_type]


def cost_requirement_text(cost_type: str | None) -> str:
    if cost_type is None:
        return ""
    return {
        "artwork": "需消耗 1 件艺术品",
        "scaled_gold": "需支付 `scaled_gold = 5`",
        "prestige": "需支付 50 威望",
    }[cost_type]


def generic_completion_text(style: int, ritual: dict[str, object]) -> str:
    cost_type = ritual["style_3"]["cost_type"]  # type: ignore[index]
    if style == 1:
        return "确认后进入为期 1 年的国家仪式负担；到期后自动落成并转为永久祝福。"
    if style == 2:
        return "确认后在奇观地点建造专属仪式附属建筑；建筑完工时自动落成。"
    if cost_type == "artwork":
        return "确认后消耗 1 件艺术品并立即落成。"
    if cost_type == "scaled_gold":
        return "确认后支付 `scaled_gold = 5` 并立即落成。"
    if cost_type == "prestige":
        return "确认后支付 50 威望并立即落成。"
    raise ValueError(f"Unsupported ritual cost type: {cost_type}")


def generic_effect_text(wonder: dict[str, object], mechanics: dict[str, object], style: int) -> str:
    ritual = generic_ritual_for_wonder(mechanics, wonder)
    if style == 1:
        blessing = ritual["style_1"]["country_modifier"]
        burden = burden_modifiers(blessing)
        return (
            f"开始后：{format_modifiers(burden)}，持续 1 年；"
            f"结束后：永久 {format_modifiers(blessing)}。"
        )
    if style == 2:
        local_modifiers = deepcopy(ritual["style_2"]["local_modifier"])
        estate_key = estate_power_key(str(wonder["pop_type"]))
        local_modifiers[estate_key] = local_modifiers.get(estate_key, 0) + 0.5
        return f"附属建筑提供 {format_modifiers(local_modifiers)}。"
    rewards = [format_reward(entry) for entry in ritual["style_3"]["reward"]]
    return "获得 " + "、".join(rewards) + "。"


def generic_wonder_entry(wonder: dict[str, object], mechanics: dict[str, object]) -> dict[str, object]:
    design = mechanics["designs"][mechanic_key(wonder)]
    ritual = generic_ritual_for_wonder(mechanics, wonder)
    branches = []
    for style in ceremony_styles(wonder):
        branch = design["branches"][style]
        branches.append(
            {
                "分支": branch["zh"],
                "完成方式": generic_completion_text(style, ritual),
                "仪式类型": {
                    1: "一年国家仪式",
                    2: "附属建筑仪式",
                    3: {
                        "artwork": "装饰仪式（艺术品）",
                        "scaled_gold": "装饰仪式（资金）",
                        "prestige": "装饰仪式（威望）",
                    }[ritual["style_3"]["cost_type"]],
                }[style],
                "额外效果": generic_effect_text(wonder, mechanics, style),
            }
        )
    return {
        "key": wonder["key"],
        "名称": wonder["loc"]["zh"],
        "英文名": wonder["loc"]["en"],
        "状态": "已实现",
        "规模": SIZE_LABELS[str(wonder["size"])],
        "代码对照": {
            "concept": wonder["concept"],
            "最终建筑": list(wonder["final_buildings"].values()),
        },
        "基础效果": design["base_effect"],
        "选址限制": design["site"],
        "测绘偏好": design["preference"],
        "仪式": branches,
        "备注": "",
    }


def unique_ritual_type(ritual: dict[str, object]) -> str:
    base = {
        "immediate": "独特即时仪式",
        "timed": "独特计时仪式",
        "auxiliary_building": "独特附属建筑仪式",
    }[str(ritual["mode"])]
    if ritual["cost_type"] is None:
        return base
    return f"{base}（{cost_label(str(ritual['cost_type']))}）"


def unique_completion_text(ritual: dict[str, object]) -> str:
    prefix = "建成后自动锁定该独特仪式；"
    cost_text = cost_requirement_text(ritual["cost_type"])
    mode = str(ritual["mode"])
    if mode == "immediate":
        body = "确认后立即结算仪式效果并完成最终落成"
    elif mode == "timed":
        years = ritual["timed"]["years"]
        body = f"确认后进入为期 {years} 年的仪式阶段，结束后结算仪式效果并完成最终落成"
    elif mode == "auxiliary_building":
        body = "确认后在奇观地点开建专属仪式附属建筑，建筑完工时结算仪式效果并完成最终落成"
    else:
        raise ValueError(f"Unsupported unique ritual mode: {mode}")
    if cost_text:
        body = f"{cost_text}，{body}"
    return prefix + body + "。"


def unique_script_notes(ritual: dict[str, object]) -> list[str]:
    notes: list[str] = []
    if ritual["confirmation_trigger_script"]:
        notes.append("自定义确认条件")
    if ritual["start_effect_script"]:
        notes.append("自定义开始效果")
    if ritual["completion_effect_script"]:
        notes.append("自定义完成效果")
    return notes


def unique_effect_text(ritual: dict[str, object]) -> str:
    fragments: list[str] = []

    effect_text = str(ritual["effect"]["zh"]).strip()
    if effect_text:
        fragments.append(effect_text)

    mode = str(ritual["mode"])
    if mode == "timed":
        years = ritual["timed"]["years"]
        burden = ritual["timed"]["burden_modifier"]
        blessing = ritual["timed"]["blessing_modifier"]
        timed_parts: list[str] = []
        if burden:
            timed_parts.append(f"开始后：{format_modifiers(burden)}，持续 {years} 年")
        else:
            timed_parts.append(f"仪式持续 {years} 年")
        if blessing:
            timed_parts.append(f"结束后：永久 {format_modifiers(blessing)}")
        fragments.append("；".join(timed_parts))

    if mode == "auxiliary_building":
        local_modifiers = ritual["auxiliary_building"]["local_modifier"]
        if local_modifiers:
            fragments.append(f"附属建筑提供 {format_modifiers(local_modifiers)}")

    country_modifier = ritual["country_modifier"]
    if country_modifier:
        fragments.append(f"最终国家修正：{format_modifiers(country_modifier)}")

    rewards = ritual["reward"]
    if rewards:
        fragments.append("奖励：" + "、".join(format_reward(entry) for entry in rewards))

    script_notes = unique_script_notes(ritual)
    if script_notes:
        fragments.append("自定义钩子：" + "、".join(script_notes))

    if not fragments:
        return "暂无额外效果说明。"
    return join_fragments(fragments)


def unique_branch_entry(wonder: dict[str, object]) -> dict[str, object]:
    ritual = unique_ritual(wonder)
    branch = {
        "分支": ritual["loc"]["zh"],
        "仪式类型": unique_ritual_type(ritual),
        "完成方式": unique_completion_text(ritual),
        "额外效果": unique_effect_text(ritual),
    }
    active_text = str(ritual["active_text"]["zh"]).strip()
    completion_text = str(ritual["completion_text"]["zh"]).strip()
    if active_text:
        branch["进行中文本"] = active_text
    if completion_text:
        branch["完成文本"] = completion_text
    return branch


def unique_entry(wonder: dict[str, object], mechanics: dict[str, object]) -> dict[str, object]:
    design = mechanics["designs"][mechanic_key(wonder)]
    return {
        "key": wonder["key"],
        "名称": wonder["loc"]["zh"],
        "英文名": wonder["loc"]["en"],
        "状态": "已实现",
        "规模": SIZE_LABELS[str(wonder["size"])],
        "代码对照": {
            "concept": wonder["concept"],
            "base_key": wonder["base_key"],
            "最终建筑": list(wonder["final_buildings"].values()),
        },
        "基础效果": (
            f"国家级基础效果沿用原型奇观 {wonder['base_key']} 并乘以 "
            f"{wonder['base_effect_multiplier']}；本地建筑效果、规模与基础分支结构继承原型。"
        ),
        "选址限制": (
            f"固定历史地点：{wonder['fixed_location']}。"
            f"除固定地点外，仍继承原型奇观的选址规则：{design['site']}"
        ),
        "测绘偏好": "固定历史地点；测绘开始时额外 +100 规模称职度、+20 物流称职度、+20 组织称职度。",
        "仪式": [unique_branch_entry(wonder)],
        "备注": (
            "接受独特奇观提案时额外 +50 初始国内支持；建成后仍自动锁定唯一分支，"
            "但该分支现在由统一的 `ritual` 结构驱动，可自由组合模式、成本、国家修正、奖励、文本和脚本钩子。"
        ),
    }


def build_document() -> dict[str, object]:
    generic_wonders, mechanics = load_generic_wonder_mechanics_data()
    unique_wonders = load_unique_wonders()

    generic_entries = [generic_wonder_entry(wonder, mechanics) for wonder in generic_wonders]
    unique_entries = [unique_entry(wonder, mechanics) for wonder in unique_wonders]

    return {
        "说明": (
            "这个文件由 `scripts/gen_wonder_effects_reference.py` 根据 "
            "`data/wonders.yaml`、`data/wonder_mechanics.yaml` 和 "
            "`data/unique_wonders.yaml` 自动回写，用自然语言保存当前奇观设计状态，"
            "方便后续补充、平衡和 AI 对照。它不直接参与脚本生成链。"
        ),
        "维护约定": [
            "若需修改奇观设计，请优先改源数据后重新生成本文件。",
            "key 用于和代码、变量、建筑名对照，尽量不要随意改。",
            "效果字段优先写成人能读懂的一句话；必要时再补充代码名。",
            "未设计完的内容保留空字符串或“待补”。",
            "百分比按玩家看到的写法填写，例如 +20%、-10%。",
        ],
        "同步命令": "conda run --no-capture-output -n eu5 python scripts/gen_wonder_effects_reference.py",
        "通用规则": {
            "等级": "奇观最高 6 级。奇观等级取决于四个部分均已达到的最高单元数；例如四部分为 1/2/3/1 时，实际奇观等级为 1。",
            "建设部分": [
                "基础建设",
                "主体结构",
                "功能实现",
                "封顶与装饰",
            ],
            "规模": {
                "小型": "每个建设单元需要 100000 总建设进度。",
                "中型": "每个建设单元需要 200000 总建设进度。",
                "大型": "每个建设单元需要 300000 总建设进度。",
            },
            "测绘": "测绘结果包括规模称职度、物流称职度、组织称职度，范围 0~100。结果由奇观偏好、随机测绘、月度事件和首席工程师行政能力共同决定。",
            "仪式": (
                "39 个通用奇观都使用统一三类仪式框架：分支 1 是 1 年国家仪式负担并在结束后转为永久祝福，"
                "分支 2 是在奇观地点建造专属仪式附属建筑并在完工时落成，"
                "分支 3 是支付固定装饰成本（1 件艺术品、`scaled_gold = 5` 或 50 威望）后立即落成。"
                "独特奇观则在建成后自动锁定唯一分支，但该分支现在也走统一 `ritual` 结构，"
                "可按 `mode` 设计为 `immediate`、`timed` 或 `auxiliary_building`，"
                "并可叠加成本、国家修正、奖励、进行中文本、完成文本与自定义脚本。"
            ),
            "独特奇观": (
                "独特奇观使用固定历史地点，接受提案时额外 +50 初始国内支持，"
                "测绘开始时额外 +100 规模称职度、+20 物流称职度、+20 组织称职度，"
                "且国家级基础效果按原型乘以 2。"
            ),
        },
        "奇观": generic_entries,
        "独特奇观": unique_entries,
    }


def main() -> None:
    OUT_FILE.write_text(json.dumps(build_document(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
