"""
gen_messagetypes.py — Generate both mods' full-copy messagetypes.txt files.
Copies vanilla and writes two full-copy outputs: an Engineering Department
subset and the main mod's strict superset. The declared main -> Engineering
Department dependency guarantees the superset wins when both mods are loaded.
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

VANILLA = ROOT / "reference_game_files/game/main_menu/gui/messagetypes.txt"
MAIN_OUT = ROOT / "src/main_menu/gui/messagetypes.txt"
ENGINEERING_OUT = ROOT / "src_engineering_department/main_menu/gui/messagetypes.txt"
ENGINEERING_GENERIC_ACTIONS_DIR = ROOT / "src_engineering_department/in_game/common/generic_actions"
VICTORY_PATHS = ROOT / "data/victory_paths.yaml"
IO_ESTABLISHMENT = ROOT / "data/io_establishment.yaml"

MONOPOLY_SLOT_COUNT = 2
INTELLIGENCE_ROW_COUNT = 10

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
        victory_task_action_name(path_id, slot)
        for path_id in VICTORY_TASK_PATH_IDS
        for slot in VICTORY_TASK_SLOTS
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

TV_ENTRIES = """
# ── Towards Victory — Generic Action Message Types ───────────────────────────

PERFORM_tv_send_artist_abroad_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = society
}

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


def engineering_action_ids() -> list[str]:
    """Read the standalone mod's top-level generic action ids."""
    action_re = re.compile(r"^([a-z][A-Za-z0-9_]*)\s*=\s*\{", re.MULTILINE)
    actions: set[str] = set()
    for path in sorted(ENGINEERING_GENERIC_ACTIONS_DIR.glob("*.txt")):
        actions.update(action_re.findall(path.read_text(encoding="utf-8-sig")))
    if not actions:
        raise ValueError(f"No Engineering Department generic actions found in {ENGINEERING_GENERIC_ACTIONS_DIR}")
    return sorted(actions)


def extract_message_type_block(text: str, message_type: str) -> str:
    match = re.search(rf"(?m)^{re.escape(message_type)}\s*=\s*\{{", text)
    if match is None:
        raise ValueError(f"Missing message type block for {message_type}")
    brace_start = text.find("{", match.start())
    depth = 0
    for index in range(brace_start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[match.start():index + 1]
    raise ValueError(f"Unterminated message type block for {message_type}")


def engineering_message_entries(all_entries: str) -> str:
    """Filter the main superset down to the standalone mod's action blocks."""
    blocks = ["\n# Engineering Department - Generic Action Message Types\n"]
    for action in engineering_action_ids():
        blocks.append(extract_message_type_block(all_entries, f"PERFORM_{action}_ACTION"))
    return "\n\n".join(blocks) + "\n"

vanilla_bytes = VANILLA.read_bytes()
# strip BOM if present
if vanilla_bytes.startswith(b'\xef\xbb\xbf'):
    vanilla_bytes = vanilla_bytes[3:]

combined_entries = (
    TV_ENTRIES
    + hagia_assignment_message_entries()
    + trade_monopoly_message_entries()
    + victory_reward_message_entries()
    + victory_tree_node_message_entries()
    + victory_task_message_entries()
    + io_establishment_message_entries()
)
engineering_entries = engineering_message_entries(combined_entries)
for output, entries in (
    (MAIN_OUT, combined_entries),
    (ENGINEERING_OUT, engineering_entries),
):
    output.parent.mkdir(parents=True, exist_ok=True)
    combined = b'\xef\xbb\xbf' + vanilla_bytes + entries.encode("utf-8")
    output.write_bytes(combined)
    print(f"[OK] Written {output.relative_to(ROOT)} ({len(combined)} bytes)")

