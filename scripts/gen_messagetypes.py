"""
gen_messagetypes.py — Generate src/main_menu/gui/messagetypes.txt
Copies the vanilla messagetypes.txt and appends Towards Victory entries.
Run after updating vanilla game files or adding new generic actions.
"""
import sys
import pathlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

ROOT = pathlib.Path(__file__).parent.parent
VANILLA = ROOT / "reference_game_files/game/main_menu/gui/messagetypes.txt"
OUT = ROOT / "src/main_menu/gui/messagetypes.txt"
TRADE_GOODS = ROOT / "data/trade_league_goods.yaml"

DISPLAY_ROW_COUNT = 10

TRADE_MONOPOLY_ACTIONS = [
    "tv_trade_previous_monopoly_page",
    "tv_trade_next_monopoly_page",
    *(f"tv_trade_select_monopoly_row_{row}" for row in range(1, DISPLAY_ROW_COUNT + 1)),
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

PERFORM_tv_wonder_select_construction_site_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_build_labor_camp_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_build_material_dispatch_point_ACTION={
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

PERFORM_tv_wonder_perform_royal_sacrifice_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_meditation_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_confirm_divine_investiture_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_request_emissary_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_triumph_parade_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_civic_festival_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_hold_golden_auction_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_confirm_fleet_review_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_free_trade_festival_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_ancestor_festival_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_dedicate_quiet_land_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_light_eternal_flame_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_navigator_guild_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_complete_long_watch_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_water_festival_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_complete_waterwheel_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_swear_miners_rights_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_confirm_royal_mint_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_deep_drainage_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_star_catalog_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_confirm_nautical_almanac_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_eclipse_proclamation_ACTION={
	log=yes
	onmap=no
	popup=no
	idle=no
	option=yes
	pausepopup=no
	message_category = society
}

PERFORM_tv_wonder_start_embassy_quarter_ACTION={
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

WE_PERFORM_tv_seek_diplomatic_support_ACTION={
\tlog=yes
\tonmap=no
\tpopup=no
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
}

ACTION_tv_seek_diplomatic_support_PERFORMED_ON_US={
\tlog=yes
\tonmap=no
\tpopup=yes
\tidle=no
\toption=yes
\tpausepopup=no
\tmessage_category = diplomacy
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
    with TRADE_GOODS.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)
    goods = data["goods"]
    seen = {}
    for category in data["categories"]:
        if not category["goods"]:
            raise ValueError(f"Trade League monopoly category {category['id']} has no goods")
        for good in category["goods"]:
            if good in seen:
                raise ValueError(
                    f"Trade League monopoly good {good} is in both {seen[good]} and {category['id']}"
                )
            seen[good] = category["id"]
    missing = [good for good in goods if good not in seen]
    extra = [good for good in seen if good not in goods]
    if missing:
        raise ValueError(f"Trade League monopoly goods missing categories: {', '.join(missing)}")
    if extra:
        raise ValueError(f"Trade League monopoly categories list unknown goods: {', '.join(extra)}")
    blocks = ["\n# ---- Generated Trade League monopoly controls ----\n"]
    for category in data["categories"]:
        action = category["action"]
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

vanilla_bytes = VANILLA.read_bytes()
# strip BOM if present
if vanilla_bytes.startswith(b'\xef\xbb\xbf'):
    vanilla_bytes = vanilla_bytes[3:]

combined_entries = TV_ENTRIES + trade_monopoly_message_entries()
combined = b'\xef\xbb\xbf' + vanilla_bytes + combined_entries.encode("utf-8")
OUT.write_bytes(combined)
print(f"[OK] Written {OUT.relative_to(ROOT)} ({len(combined)} bytes)")
