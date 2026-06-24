"""
Generate generated Simplified Chinese localization for Trade League monopoly controls.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_FILE = REPO_ROOT / "data" / "trade_league_goods.yaml"
OUT_FILE = (
    REPO_ROOT
    / "src"
    / "main_menu"
    / "localization"
    / "simp_chinese"
    / "tv_trade_league_monopoly_l_simp_chinese.yml"
)

VIRTUAL_ACTION_COST_PCT = 5
EMBARGO_COST_PCT = 30
MONOPOLY_SLOT_COUNT = 2
INTELLIGENCE_ROW_COUNT = 10


def good_name(good: str) -> str:
    return f"${good}$"


def perform_entries(action: str) -> list[tuple[str, str]]:
    return [
        (f"PERFORM_{action}_ACTION_SETUP", "当我们使用贸易联盟垄断控制时。"),
        (f"PERFORM_{action}_ACTION_LOG", "我们使用了一项贸易联盟垄断控制。"),
        (f"PERFORM_{action}_ACTION_MAP", ""),
    ]


def fixed_action_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = [
        ("tv_trade_select_monopoly_slot_desc", "显示此垄断槽商品的详情。"),
        ("TV_TRADE_LEAGUE_EMPTY_MONOPOLY_SLOT", "没有商品在该槽位达到25%垄断潜力。"),
        ("TV_TRADE_LEAGUE_MONOPOLY_POTENTIAL", "有垄断潜力"),
        ("TV_TRADE_LEAGUE_LOW_MONOPOLY", "低垄断"),
        ("TV_TRADE_LEAGUE_HIGH_MONOPOLY", "高垄断"),
        ("TV_TRADE_LEAGUE_COMPLETE_MONOPOLY", "完全垄断"),
        ("TV_TRADE_LEAGUE_ORIGIN_MONOPOLY", "原产垄断"),
        ("TV_TRADE_LEAGUE_TRANSIT_MONOPOLY", "中转垄断"),
        ("TV_TRADE_LEAGUE_CONSUMER_MONOPOLY", "消费垄断"),
        ("tv_trade_previous_intelligence_page", "上一页"),
        ("tv_trade_previous_intelligence_page_desc", "显示上一页情报。"),
        ("tv_trade_next_intelligence_page", "下一页"),
        ("tv_trade_next_intelligence_page_desc", "显示下一页情报。"),
        ("tv_trade_select_intelligence_row_desc", "显示此市场的情报详情。"),
        ("tv_trade_start_intelligence_network", "建立情报网"),
        ("tv_trade_start_intelligence_network_desc", "派遣大商人在所选市场建立情报网。"),
        ("tv_trade_cancel_intelligence_network", "取消情报网"),
        ("tv_trade_cancel_intelligence_network_desc", "停止当前贸易联盟情报网建设。"),
        ("tv_trade_start_chain", "建立贸易链"),
        ("tv_trade_start_chain_desc", "派遣大商人在两个市场之间建立远距离贸易链。"),
        ("tv_trade_cancel_chain", "取消贸易链"),
        ("tv_trade_cancel_chain_desc", "停止维护当前贸易联盟贸易链。"),
        ("tv_trade_set_selected_virtual_demand", "虚构需求"),
        ("tv_trade_set_selected_virtual_demand_desc", "分配垄断水平，在选定市场创造当前商品的临时需求。"),
        ("tv_trade_increase_selected_virtual_demand", "增加虚构需求"),
        ("tv_trade_increase_selected_virtual_demand_desc", f"为当前商品的虚构需求额外使用{VIRTUAL_ACTION_COST_PCT}%垄断水平。"),
        ("tv_trade_decrease_selected_virtual_demand", "减少虚构需求"),
        ("tv_trade_decrease_selected_virtual_demand_desc", f"从当前商品的虚构需求释放{VIRTUAL_ACTION_COST_PCT}%垄断水平。"),
        ("tv_trade_cancel_selected_virtual_demand", "取消虚构需求"),
        ("tv_trade_cancel_selected_virtual_demand_desc", "移除当前商品的虚构需求行动。"),
        ("tv_trade_set_selected_virtual_supply", "虚构生产"),
        ("tv_trade_set_selected_virtual_supply_desc", "分配垄断水平，在选定市场创造当前商品的临时生产。"),
        ("tv_trade_increase_selected_virtual_supply", "增加虚构生产"),
        ("tv_trade_increase_selected_virtual_supply_desc", f"为当前商品的虚构生产额外使用{VIRTUAL_ACTION_COST_PCT}%垄断水平。"),
        ("tv_trade_decrease_selected_virtual_supply", "减少虚构生产"),
        ("tv_trade_decrease_selected_virtual_supply_desc", f"从当前商品的虚构生产释放{VIRTUAL_ACTION_COST_PCT}%垄断水平。"),
        ("tv_trade_cancel_selected_virtual_supply", "取消虚构生产"),
        ("tv_trade_cancel_selected_virtual_supply_desc", "移除当前商品的虚构生产行动。"),
        ("tv_trade_set_selected_embargo", "禁运"),
        ("tv_trade_set_selected_embargo_desc", f"消耗{EMBARGO_COST_PCT}%垄断水平，使一个国家在选定市场获得-50贸易优势。"),
        ("tv_trade_cancel_selected_embargo", "取消禁运"),
        ("tv_trade_cancel_selected_embargo_desc", "移除当前商品的禁运行动。"),
        ("tv_trade_select_chain_origin_market", "选择起点市场"),
        ("tv_trade_select_chain_destination_market", "选择终点市场"),
        ("tv_trade_no_chain_origin_market_available", "@trigger_no! 没有贸易范围内的[market|E]可用。"),
        ("tv_trade_no_chain_destination_market_available", "@trigger_no! 没有贸易范围内的远距离[market|E]可用。"),
    ]
    for slot in range(1, MONOPOLY_SLOT_COUNT + 1):
        entries.append((f"tv_trade_select_monopoly_slot_{slot}", f"选择垄断槽{slot}"))
        entries.append((f"tv_trade_select_monopoly_slot_{slot}_desc", "显示此垄断槽商品的详情。"))
    for row in range(1, INTELLIGENCE_ROW_COUNT + 1):
        entries.append((f"tv_trade_select_intelligence_row_{row}", "选择市场"))
        entries.append((f"tv_trade_select_intelligence_row_{row}_desc", "显示此市场的情报详情。"))
    actions = [
        *(f"tv_trade_select_monopoly_slot_{slot}" for slot in range(1, MONOPOLY_SLOT_COUNT + 1)),
        "tv_trade_previous_intelligence_page",
        "tv_trade_next_intelligence_page",
        *(f"tv_trade_select_intelligence_row_{row}" for row in range(1, INTELLIGENCE_ROW_COUNT + 1)),
        "tv_trade_start_intelligence_network",
        "tv_trade_cancel_intelligence_network",
        "tv_trade_start_chain",
        "tv_trade_cancel_chain",
        "tv_trade_set_selected_virtual_demand",
        "tv_trade_increase_selected_virtual_demand",
        "tv_trade_decrease_selected_virtual_demand",
        "tv_trade_cancel_selected_virtual_demand",
        "tv_trade_set_selected_virtual_supply",
        "tv_trade_increase_selected_virtual_supply",
        "tv_trade_decrease_selected_virtual_supply",
        "tv_trade_cancel_selected_virtual_supply",
        "tv_trade_set_selected_embargo",
        "tv_trade_cancel_selected_embargo",
    ]
    for action in actions:
        entries.extend(perform_entries(action))
    return entries


def demand_modifier_entries(good: str) -> list[tuple[str, str]]:
    name = good_name(good)
    return [(f"tv_trade_virtual_demand_{good}", f"贸易联盟虚构需求：{name}")]


def generate(data: dict) -> bytes:
    lines = [
        "l_simp_chinese:",
        "# @Generated by scripts/main_menu/localization/simp_chinese/gen_tv_trade_league_monopoly_l_simp_chinese.py",
        "#   Data:    data/trade_league_goods.yaml",
        "#   Regen:   conda run --no-capture-output -n eu5 python scripts/main_menu/localization/simp_chinese/gen_tv_trade_league_monopoly_l_simp_chinese.py",
        "# Do not edit directly - modify the data file and re-run the generator.",
        "",
    ]
    for key, value in fixed_action_entries():
        escaped = value.replace('"', '\\"')
        lines.append(f' {key}: "{escaped}"')
    for good in data["goods"]:
        for key, value in demand_modifier_entries(good):
            escaped = value.replace('"', '\\"')
            lines.append(f' {key}: "{escaped}"')
    text = "\n".join(lines) + "\n"
    return b"\xef\xbb\xbf" + text.encode("utf-8")


def main() -> None:
    with DATA_FILE.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    OUT_FILE.write_bytes(generate(data))
    print(f"Written: {OUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
