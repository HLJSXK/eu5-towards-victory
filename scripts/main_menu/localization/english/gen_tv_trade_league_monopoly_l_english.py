"""
Generate generated English localization for Trade League monopoly controls.
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
    / "english"
    / "tv_trade_league_monopoly_l_english.yml"
)

VIRTUAL_ACTION_COST_PCT = 5
EMBARGO_COST_PCT = 30
MONOPOLY_SLOT_COUNT = 2
INTELLIGENCE_ROW_COUNT = 10


def good_name(good: str) -> str:
    return f"${good}$"


def perform_entries(action: str) -> list[tuple[str, str]]:
    return [
        (f"PERFORM_{action}_ACTION_SETUP", "When we use a Trade League monopoly control."),
        (f"PERFORM_{action}_ACTION_LOG", "We used a Trade League monopoly control."),
        (f"PERFORM_{action}_ACTION_MAP", ""),
    ]


def fixed_action_entries() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = [
        ("tv_trade_select_monopoly_slot_desc", "Show monopoly details for this commodity slot."),
        ("TV_TRADE_LEAGUE_EMPTY_MONOPOLY_SLOT", "No commodity has at least 25% monopoly potential for this slot."),
        ("TV_TRADE_LEAGUE_MONOPOLY_POTENTIAL", "Monopoly Potential"),
        ("TV_TRADE_LEAGUE_LOW_MONOPOLY", "Low Monopoly"),
        ("TV_TRADE_LEAGUE_HIGH_MONOPOLY", "High Monopoly"),
        ("TV_TRADE_LEAGUE_COMPLETE_MONOPOLY", "Complete Monopoly"),
        ("TV_TRADE_LEAGUE_ORIGIN_MONOPOLY", "Origin Monopoly"),
        ("TV_TRADE_LEAGUE_TRANSIT_MONOPOLY", "Transit Monopoly"),
        ("TV_TRADE_LEAGUE_CONSUMER_MONOPOLY", "Consumer Monopoly"),
        ("tv_trade_previous_intelligence_page", "Previous Page"),
        ("tv_trade_previous_intelligence_page_desc", "Show the previous intelligence page."),
        ("tv_trade_next_intelligence_page", "Next Page"),
        ("tv_trade_next_intelligence_page_desc", "Show the next intelligence page."),
        ("tv_trade_select_intelligence_row_desc", "Show intelligence details for this market."),
        ("tv_trade_start_intelligence_network", "Build Intelligence Network"),
        ("tv_trade_start_intelligence_network_desc", "Assign the Grand Merchant to build an intelligence network in the selected market."),
        ("tv_trade_cancel_intelligence_network", "Cancel Intelligence Network"),
        ("tv_trade_cancel_intelligence_network_desc", "Stop building the active Trade League intelligence network."),
        ("tv_trade_start_chain", "Establish Trade Chain"),
        (
            "tv_trade_start_chain_desc",
            "Assign the Grand Merchant to establish a long-distance trade chain between two markets.",
        ),
        ("tv_trade_cancel_chain", "Cancel Trade Chain"),
        ("tv_trade_cancel_chain_desc", "Stop maintaining the active Trade League trade chain."),
        ("tv_trade_set_selected_virtual_demand", "Virtual Demand"),
        (
            "tv_trade_set_selected_virtual_demand_desc",
            "Allocate monopoly level to create temporary demand for the selected commodity in a selected market.",
        ),
        ("tv_trade_increase_selected_virtual_demand", "Increase Virtual Demand"),
        (
            "tv_trade_increase_selected_virtual_demand_desc",
            f"Use {VIRTUAL_ACTION_COST_PCT}% more monopoly level on virtual demand for the selected commodity.",
        ),
        ("tv_trade_decrease_selected_virtual_demand", "Decrease Virtual Demand"),
        (
            "tv_trade_decrease_selected_virtual_demand_desc",
            f"Release {VIRTUAL_ACTION_COST_PCT}% monopoly level from virtual demand for the selected commodity.",
        ),
        ("tv_trade_cancel_selected_virtual_demand", "Cancel Virtual Demand"),
        ("tv_trade_cancel_selected_virtual_demand_desc", "Remove the virtual demand action for the selected commodity."),
        ("tv_trade_set_selected_virtual_supply", "Virtual Production"),
        (
            "tv_trade_set_selected_virtual_supply_desc",
            "Allocate monopoly level to create temporary production for the selected commodity in a selected market.",
        ),
        ("tv_trade_increase_selected_virtual_supply", "Increase Virtual Production"),
        (
            "tv_trade_increase_selected_virtual_supply_desc",
            f"Use {VIRTUAL_ACTION_COST_PCT}% more monopoly level on virtual production for the selected commodity.",
        ),
        ("tv_trade_decrease_selected_virtual_supply", "Decrease Virtual Production"),
        (
            "tv_trade_decrease_selected_virtual_supply_desc",
            f"Release {VIRTUAL_ACTION_COST_PCT}% monopoly level from virtual production for the selected commodity.",
        ),
        ("tv_trade_cancel_selected_virtual_supply", "Cancel Virtual Production"),
        ("tv_trade_cancel_selected_virtual_supply_desc", "Remove the virtual production action for the selected commodity."),
        ("tv_trade_set_selected_embargo", "Embargo"),
        (
            "tv_trade_set_selected_embargo_desc",
            f"Spend {EMBARGO_COST_PCT}% monopoly level to give a country -50 trade advantage in a selected market.",
        ),
        ("tv_trade_cancel_selected_embargo", "Cancel Embargo"),
        ("tv_trade_cancel_selected_embargo_desc", "Remove the embargo action for the selected commodity."),
        ("tv_trade_select_chain_origin_market", "Select Origin Market"),
        ("tv_trade_select_chain_destination_market", "Select Destination Market"),
        ("tv_trade_no_chain_origin_market_available", "@trigger_no! No [market|E] in trade range is available."),
        (
            "tv_trade_no_chain_destination_market_available",
            "@trigger_no! No distant [market|E] in trade range is available.",
        ),
    ]
    for slot in range(1, MONOPOLY_SLOT_COUNT + 1):
        entries.append((f"tv_trade_select_monopoly_slot_{slot}", f"Select Monopoly Slot {slot}"))
        entries.append((f"tv_trade_select_monopoly_slot_{slot}_desc", "Show monopoly details for this commodity slot."))
    for row in range(1, INTELLIGENCE_ROW_COUNT + 1):
        entries.append((f"tv_trade_select_intelligence_row_{row}", "Select Market"))
        entries.append((f"tv_trade_select_intelligence_row_{row}_desc", "Show intelligence details for this market."))
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
    return [(f"tv_trade_virtual_demand_{good}", f"Trade League Virtual Demand: {name}")]


def generate(data: dict) -> bytes:
    lines = [
        "l_english:",
        "# @Generated by scripts/main_menu/localization/english/gen_tv_trade_league_monopoly_l_english.py",
        "#   Data:    data/trade_league_goods.yaml",
        "#   Regen:   conda run --no-capture-output -n eu5 python scripts/main_menu/localization/english/gen_tv_trade_league_monopoly_l_english.py",
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
