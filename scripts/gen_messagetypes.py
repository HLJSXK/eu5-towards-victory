"""
gen_messagetypes.py — Generate per-root full-copy messagetypes.txt files.

``messagetypes.txt`` is a winner-takes-all singleton. Standalone roots keep
only their own message types so they load cleanly by themselves. The main mod
keeps the TV+Engineering union and must be sorted after Engineering Department
when both are enabled.
"""
import sys
import pathlib
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.victory_tree_node_codegen import action_name as tree_action_name
from scripts.victory_tree_node_codegen import flatten_nodes as tree_flatten_nodes
from scripts.victory_tree_node_codegen import load_data as load_tree_variant_data
from scripts.victory_task_codegen import PATH_IDS as VICTORY_TASK_PATH_IDS
from scripts.victory_task_codegen import SLOTS as VICTORY_TASK_SLOTS
from scripts.victory_task_codegen import action_name as victory_task_action_name
from scripts.victory_task_codegen import refresh_action_name as victory_task_refresh_action_name

VANILLA = ROOT / "reference_game_files/game/main_menu/gui/messagetypes.txt"
MAIN_OUT = ROOT / "src/main_menu/gui/messagetypes.txt"
ENGINEERING_OUT = ROOT / "src_engineering_department/main_menu/gui/messagetypes.txt"
COURT_OUT = ROOT / "src_court_positions/main_menu/gui/messagetypes.txt"
VICTORY_PATHS = ROOT / "data/victory_paths.yaml"
IO_ESTABLISHMENT = ROOT / "data/io_establishment.yaml"
COURT_POSITIONS = ROOT / "data/court_positions.yaml"

MONOPOLY_SLOT_COUNT = 2
INTELLIGENCE_ROW_COUNT = 10
COURT_POSITION_ROLE_ACTION_COUNT = 3

TRADE_MONOPOLY_ACTIONS = [
    *(f"tv_trade_select_monopoly_slot_{slot}" for slot in range(1, MONOPOLY_SLOT_COUNT + 1)),
    "tv_trade_previous_intelligence_page",
    "tv_trade_next_intelligence_page",
    *(f"tv_trade_select_intelligence_row_{row}" for row in range(1, INTELLIGENCE_ROW_COUNT + 1)),
    "tv_trade_start_intelligence_network",
    "tv_trade_cancel_intelligence_network",
    "tv_trade_add_chain_node",
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

HAGIA_ASSIGNMENT_ACTIONS = [
    f"tv_wonder_hagia_assign_step_{step}"
    for step in range(1, 9)
]


def victory_reward_action_ids() -> list[str]:
    with VICTORY_PATHS.open(encoding="utf-8-sig") as file:
        data = yaml.safe_load(file)
    paths = sorted(data["paths"], key=lambda path: int(path["gui"]["order"]))
    actions: list[str] = []
    for path in paths:
        actions.append(f"tv_victory_select_path_{path['id']}")
    for path in paths:
        pid = path["id"]
        for milestone in path["milestones"]:
            n = int(milestone["n"])
            for choice in range(1, 4):
                actions.append(f"tv_victory_select_{pid}_m{n}_reward_{choice}")
    return actions


def victory_tree_node_action_ids() -> list[str]:
    data = load_tree_variant_data()
    actions: list[str] = []
    for path in data["paths"]:
        pid = path["id"]
        for node in tree_flatten_nodes(path):
            actions.append(tree_action_name(pid, node["id"]))
    return actions


def victory_task_action_ids() -> list[str]:
    return [
        action
        for path_id in VICTORY_TASK_PATH_IDS
        for slot in VICTORY_TASK_SLOTS
        for action in (
            victory_task_action_name(path_id, slot),
            victory_task_refresh_action_name(path_id, slot),
        )
    ]


def io_establishment_action_ids() -> list[str]:
    with IO_ESTABLISHMENT.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    actions: list[str] = []
    for path in sorted(data["paths"], key=lambda item: int(item.get("order", 0))):
        pid = path["id"]
        actions.append(f"tv_build_{pid}_headquarters")
        actions.append(f"tv_establish_{pid}_io")
    return actions


def court_position_action_ids() -> list[str]:
    with COURT_POSITIONS.open(encoding="utf-8-sig") as file:
        data = yaml.safe_load(file)
    actions: list[str] = []
    for position in data["positions"]:
        pid = position["id"]
        actions.extend((
            f"tv_court_appoint_{pid}",
            f"tv_court_replace_{pid}",
            f"tv_court_dismiss_{pid}",
        ))
        actions.extend(f"tv_court_{pid}_select_action_{index}" for index in range(1, COURT_POSITION_ROLE_ACTION_COUNT + 1))
    return actions


ACTION_DECL_RE = re.compile(r"(?m)^([a-z][A-Za-z0-9_]*)\s*=\s*\{")
MESSAGE_BLOCK_RE = re.compile(r"(?ms)^([A-Z][A-Za-z0-9_]*)\s*=\s*\{\n.*?\n\}\s*")


def action_ids_under(*dirs: pathlib.Path) -> set[str]:
    actions: set[str] = set()
    for directory in dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.txt")):
            actions.update(ACTION_DECL_RE.findall(path.read_text(encoding="utf-8-sig")))
    return actions


MAIN_ACTION_IDS = action_ids_under(
    ROOT / "src/in_game/common/generic_actions",
    ROOT / "src/in_game/common/country_interactions",
)
ENGINEERING_ACTION_IDS = action_ids_under(
    ROOT / "src_engineering_department/in_game/common/generic_actions",
    ROOT / "src_engineering_department/in_game/common/country_interactions",
)
COURT_ACTION_IDS = action_ids_under(
    ROOT / "src_court_positions/in_game/common/generic_actions",
    ROOT / "src_court_positions/in_game/common/country_interactions",
)
MAIN_WINNER_ACTION_IDS = MAIN_ACTION_IDS | ENGINEERING_ACTION_IDS


def message_action_id(message_type: str) -> str | None:
    if message_type.startswith("PERFORM_") and message_type.endswith("_ACTION"):
        return message_type.removeprefix("PERFORM_").removesuffix("_ACTION")
    if message_type.startswith("WE_PERFORM_") and message_type.endswith("_ACTION"):
        return message_type.removeprefix("WE_PERFORM_").removesuffix("_ACTION")
    if message_type.startswith("ACTION_") and message_type.endswith("_PERFORMED_ON_US_TARGET"):
        return message_type.removeprefix("ACTION_").removesuffix("_PERFORMED_ON_US_TARGET")
    if message_type.startswith("ACTION_") and message_type.endswith("_PERFORMED_ON_US"):
        return message_type.removeprefix("ACTION_").removesuffix("_PERFORMED_ON_US")
    return None


def filtered_static_message_entries(action_ids: set[str]) -> str:
    blocks: list[str] = []
    for match in MESSAGE_BLOCK_RE.finditer(TV_ENTRIES):
        action = message_action_id(match.group(1))
        if action in action_ids:
            blocks.append(match.group(0).rstrip())
    if not blocks:
        return ""
    return "\n# ---- Root-filtered TV controls ----\n\n" + "\n\n".join(blocks) + "\n"

TV_ENTRIES = """
# ── Towards Victory — Generic Action Message Types ───────────────────────────

PERFORM_tv_host_domestic_exhibition_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_add_artworks_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_royal_visit_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_radical_art_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_expand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_sell_art_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_recruit_artists_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_invite_foreign_artist_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_designate_treasure_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_local_exhibition_live_creation_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_start_arts_exchange_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_invite_domestic_arts_exchange_artist_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_invite_foreign_arts_exchange_artist_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_appoint_arts_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_remove_arts_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_change_arts_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_appoint_alliance_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_remove_alliance_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_change_alliance_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_appoint_academy_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_remove_academy_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_change_academy_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_appoint_engineering_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_remove_engineering_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_change_engineering_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_appoint_trade_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_remove_trade_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_change_trade_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_wonder_accept_proposal_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_select_proposal_slot_1_ACTION={
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_select_proposal_slot_2_ACTION={
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_select_proposal_slot_3_ACTION={
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_refute_proposal_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_bribe_proposal_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_accept_nobles_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_refute_nobles_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_bribe_nobles_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_accept_burghers_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_refute_burghers_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_bribe_burghers_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_accept_clergy_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_refute_clergy_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_bribe_clergy_demand_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_end_debate_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_abandon_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_start_survey_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_rerun_survey_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_wonder_select_construction_site_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_begin_foundation_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_begin_body_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_begin_function_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_begin_decoration_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_finish_construction_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_choose_ceremony_style_1_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_choose_ceremony_style_2_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_choose_ceremony_style_3_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_confirm_ceremony_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_confirm_ceremony_scaled_gold_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_confirm_ceremony_prestige_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}




















































PERFORM_tv_request_research_target_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_abandon_research_target_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_start_concentrated_research_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_pause_concentrated_research_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_treat_character_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_start_meditation_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_stop_meditation_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_train_grand_general_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_plan_offensive_strategy_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = military
}

PERFORM_tv_plan_defensive_strategy_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = military
}

PERFORM_tv_abort_war_plan_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = military
}

PERFORM_tv_change_war_plan_target_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = military
}

PERFORM_tv_appoint_conquest_general_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_remove_conquest_general_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_change_conquest_general_leader_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_reinitialize_mod_ACTION={
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = government
}

PERFORM_tv_appoint_governor_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_auto_assign_governors_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_enable_governor_automation_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_disable_governor_automation_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_remove_governor_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

PERFORM_tv_change_governor_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

WE_PERFORM_tv_invite_to_diplomatic_alliance_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

ACTION_tv_invite_to_diplomatic_alliance_PERFORMED_ON_US={
\tlog=yes
\tonmap=no
\tpopup=yes
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

WE_PERFORM_tv_invite_to_trade_league_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

ACTION_tv_invite_to_trade_league_PERFORMED_ON_US={
\tlog=yes
\tonmap=no
\tpopup=yes
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_expel_diplomatic_alliance_member_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_alliance_sublime_empire_subjugate_member_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_alliance_cultural_union_enforce_culture_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_alliance_religious_congress_enforce_religion_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

PERFORM_tv_expel_trade_league_member_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}
"""


def trade_monopoly_message_entries() -> str:
    blocks = ["\n# ---- Generated Trade League monopoly controls ----\n"]
    for action in TRADE_MONOPOLY_ACTIONS:
        blocks.append(
            f"""PERFORM_{action}_ACTION={{
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = economy
}}
"""
        )
    return "\n".join(blocks)


def hagia_assignment_message_entries() -> str:
    blocks = ["\n# ---- Generated Hagia Sophia ritual assignment controls ----\n"]
    for action in HAGIA_ASSIGNMENT_ACTIONS:
        blocks.append(
            f"""PERFORM_{action}_ACTION={{
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}}
"""
        )
    return "\n".join(blocks)


def victory_reward_message_entries() -> str:
    blocks = ["\n# ---- Generated victory path UI controls ----\n"]
    for action in victory_reward_action_ids():
        blocks.append(
            f"""PERFORM_{action}_ACTION={{
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = government
}}
"""
        )
    return "\n".join(blocks)


def victory_tree_node_message_entries() -> str:
    blocks = ["\n# ---- Generated Victory Path Tree node unlock controls ----\n"]
    for action in victory_tree_node_action_ids():
        blocks.append(
            f"""PERFORM_{action}_ACTION={{
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = government
}}
"""
        )
    return "\n".join(blocks)


def victory_task_message_entries() -> str:
    blocks = ["\n# ---- Generated Victory Path task claim controls ----\n"]
    for action in victory_task_action_ids():
        blocks.append(
            f"""PERFORM_{action}_ACTION={{
\tlog=no
\tonmap=no
\tpopup=no
\tidle=no
\toption=no
\tpausepopup=no
\tmessage_category = government
}}
"""
        )
    return "\n".join(blocks)


def io_establishment_message_entries() -> str:
    blocks = ["\n# ---- Generated IO establishment controls ----\n"]
    for action in io_establishment_action_ids():
        blocks.append(
            f"""PERFORM_{action}_ACTION={{
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = government
}}
"""
        )
    return "\n".join(blocks)


def court_position_message_entries() -> str:
    blocks = ["\n# ---- Generated Court Positions controls ----\n"]
    for action in court_position_action_ids():
        blocks.append(
            f"""PERFORM_{action}_ACTION={{
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}}
"""
        )
    return "\n".join(blocks)


vanilla_bytes = VANILLA.read_bytes()
# strip BOM if present
if vanilla_bytes.startswith(b'\xef\xbb\xbf'):
    vanilla_bytes = vanilla_bytes[3:]

main_entries = (
    filtered_static_message_entries(MAIN_WINNER_ACTION_IDS)
    + hagia_assignment_message_entries()
    + trade_monopoly_message_entries()
    + victory_reward_message_entries()
    + victory_tree_node_message_entries()
    + victory_task_message_entries()
    + io_establishment_message_entries()
)
engineering_entries = (
    filtered_static_message_entries(ENGINEERING_ACTION_IDS)
    + hagia_assignment_message_entries()
)
court_entries = court_position_message_entries()

for output, entries in (
    (MAIN_OUT, main_entries),
    (ENGINEERING_OUT, engineering_entries),
    (COURT_OUT, court_entries),
):
    output.parent.mkdir(parents=True, exist_ok=True)
    combined = b'\xef\xbb\xbf' + vanilla_bytes + entries.encode("utf-8")
    output.write_bytes(combined)
    print(f"[OK] Written {output.relative_to(ROOT)} ({len(combined)} bytes)")

