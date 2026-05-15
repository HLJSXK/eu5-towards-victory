"""
gen_messagetypes.py — Generate src/main_menu/gui/messagetypes.txt
Copies the vanilla messagetypes.txt and appends Towards Victory entries.
Run after updating vanilla game files or adding new generic actions.
"""
import sys
import pathlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).parent.parent
VANILLA = ROOT / "reference_game_files/game/main_menu/gui/messagetypes.txt"
OUT = ROOT / "src/main_menu/gui/messagetypes.txt"

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

PERFORM_tv_treat_character_ACTION={
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
"""

vanilla_bytes = VANILLA.read_bytes()
# strip BOM if present
if vanilla_bytes.startswith(b'\xef\xbb\xbf'):
    vanilla_bytes = vanilla_bytes[3:]

combined = b'\xef\xbb\xbf' + vanilla_bytes + TV_ENTRIES.encode("utf-8")
OUT.write_bytes(combined)
print(f"[OK] Written {OUT.relative_to(ROOT)} ({len(combined)} bytes)")
