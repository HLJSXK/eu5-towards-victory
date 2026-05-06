#!/usr/bin/env python3
"""Patch all Diplomatic Victory stubs in-place.

Run: conda run -n eu5 python scripts/gen_diplomatic_victory.py
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
_ok = 0
_err = 0


def patch(path: Path, old: str, new: str, label: str, enc: str = "utf-8-sig") -> None:
    global _ok, _err
    text = path.read_text(encoding=enc)
    if old not in text:
        print(f"[ERR] {label}: old text not found in {path.name}")
        _err += 1
        return
    path.write_text(text.replace(old, new, 1), encoding=enc)
    print(f"[OK]  {label}")
    _ok += 1


def append_to(path: Path, addition: str, label: str, enc: str = "utf-8-sig") -> None:
    global _ok
    existing = path.read_text(encoding=enc)
    path.write_text(existing + addition, encoding=enc)
    print(f"[OK]  {label}")
    _ok += 1


# ── File paths ────────────────────────────────────────────────────────────────

TRIGGERS    = REPO / "src/in_game/common/scripted_triggers/towards_victory_triggers.txt"
EFFECTS     = REPO / "src/in_game/common/scripted_effects/towards_victory_effects.txt"
MODIFIERS   = REPO / "src/in_game/common/static_modifiers/towards_victory_modifiers.txt"
EVENTS      = REPO / "src/in_game/events/towards_victory_events.txt"
ON_ACTION   = REPO / "src/in_game/common/on_action/towards_victory_yearly.txt"
LOC_EN      = REPO / "src/main_menu/localization/english/towards_victory_l_english.yml"
LOC_ZH      = REPO / "src/main_menu/localization/simp_chinese/towards_victory_l_simp_chinese.yml"

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 1-5: TRIGGERS — replace always = no stubs
# ══════════════════════════════════════════════════════════════════════════════

patch(TRIGGERS,
    old=(
        "tv_diplomatic_milestone_1 = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 1\n"
        "\t# Threshold hint: tv_diplomatic_victory_points >= 50\n"
        "\t# Step 2/3 verification required before implementing\n"
        "\talways = no\n"
        "}"
    ),
    new=(
        "tv_diplomatic_milestone_1 = {\n"
        "\thas_variable = tv_diplomatic_victory_points\n"
        "\tvar:tv_diplomatic_victory_points >= 50\n"
        "}"
    ),
    label="triggers: milestone 1",
)

patch(TRIGGERS,
    old=(
        "tv_diplomatic_milestone_2 = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 2\n"
        "\t# Threshold hint: tv_diplomatic_victory_points >= 120\n"
        "\t# Step 2/3 verification required before implementing\n"
        "\talways = no\n"
        "}"
    ),
    new=(
        "tv_diplomatic_milestone_2 = {\n"
        "\thas_variable = tv_diplomatic_victory_points\n"
        "\tvar:tv_diplomatic_victory_points >= 120\n"
        "}"
    ),
    label="triggers: milestone 2",
)

patch(TRIGGERS,
    old=(
        "tv_diplomatic_milestone_3 = {\n"
        "\t# TODO: Diplomatic Victory — Short-term Victory\n"
        "\t# Threshold hint: tv_diplomatic_victory_points >= 220\n"
        "\t# Step 2/3 verification required before implementing\n"
        "\talways = no\n"
        "}"
    ),
    new=(
        "tv_diplomatic_milestone_3 = {\n"
        "\thas_variable = tv_diplomatic_victory_points\n"
        "\tvar:tv_diplomatic_victory_points >= 220\n"
        "}"
    ),
    label="triggers: milestone 3",
)

patch(TRIGGERS,
    old=(
        "tv_diplomatic_milestone_4 = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 4\n"
        "\t# Threshold hint: tv_diplomatic_victory_points >= 380\n"
        "\t# Step 2/3 verification required before implementing\n"
        "\talways = no\n"
        "}"
    ),
    new=(
        "tv_diplomatic_milestone_4 = {\n"
        "\thas_variable = tv_diplomatic_victory_points\n"
        "\tvar:tv_diplomatic_victory_points >= 380\n"
        "}"
    ),
    label="triggers: milestone 4",
)

patch(TRIGGERS,
    old=(
        "tv_diplomatic_milestone_5 = {\n"
        "\t# TODO: Diplomatic Victory — Long-term Victory\n"
        "\t# Threshold hint: tv_diplomatic_victory_points >= 580\n"
        "\t# Step 2/3 verification required before implementing\n"
        "\talways = no\n"
        "}"
    ),
    new=(
        "tv_diplomatic_milestone_5 = {\n"
        "\thas_variable = tv_diplomatic_victory_points\n"
        "\tvar:tv_diplomatic_victory_points >= 580\n"
        "}"
    ),
    label="triggers: milestone 5",
)

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 6: EFFECTS — add DVP variable init inside milestone checker
# ══════════════════════════════════════════════════════════════════════════════

patch(EFFECTS,
    old=(
        "tv_check_diplomatic_milestones_effect = {\n"
        "\t# Initialise on first call (guards against missing variable)\n"
        "\tif = {\n"
        "\t\tlimit = { NOT = { has_variable = tv_diplomatic_milestone } }\n"
        "\t\tset_variable = { name = tv_diplomatic_milestone value = 0 }\n"
        "\t}"
    ),
    new=(
        "tv_check_diplomatic_milestones_effect = {\n"
        "\t# Initialise on first call (guards against missing variable)\n"
        "\tif = {\n"
        "\t\tlimit = { NOT = { has_variable = tv_diplomatic_victory_points } }\n"
        "\t\tset_variable = { name = tv_diplomatic_victory_points value = 0 }\n"
        "\t}\n"
        "\tif = {\n"
        "\t\tlimit = { NOT = { has_variable = tv_diplomatic_milestone } }\n"
        "\t\tset_variable = { name = tv_diplomatic_milestone value = 0 }\n"
        "\t}"
    ),
    label="effects: DVP variable init in checker",
)

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 7: EFFECTS — progress pct for diplomatic path
# ══════════════════════════════════════════════════════════════════════════════

patch(EFFECTS,
    old=(
        "\t# TODO: compute 0.0-1.0 progress fraction for diplomatic path\n"
        "\t# Formula: tv_diplomatic_progress_pct = raw_metric / v2_threshold\n"
        "\t# V2 threshold hint: tv_diplomatic_victory_points >= 580\n"
        "\t# Pattern:\n"
        "\t#   set_variable = { name = tv_diplomatic_progress_pct value = <raw_metric_accessor> }\n"
        "\t#   change_variable = { name = tv_diplomatic_progress_pct divide = <v2_threshold_literal> }\n"
        "\t#   if = { limit = { var:tv_diplomatic_progress_pct > 1 } set_variable = { name = tv_diplomatic_progress_pct value = 1 } }"
    ),
    new=(
        "\tif = {\n"
        "\t\tlimit = { has_variable = tv_diplomatic_victory_points }\n"
        "\t\tset_variable = { name = tv_diplomatic_progress_pct value = var:tv_diplomatic_victory_points }\n"
        "\t\tchange_variable = { name = tv_diplomatic_progress_pct divide = 580 }\n"
        "\t\tif = { limit = { var:tv_diplomatic_progress_pct > 1 } set_variable = { name = tv_diplomatic_progress_pct value = 1 } }\n"
        "\t}"
    ),
    label="effects: progress pct for diplomatic",
)

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 8-12: EFFECTS — 5 reward effects
# ══════════════════════════════════════════════════════════════════════════════

patch(EFFECTS,
    old=(
        "tv_grant_diplomatic_milestone_1 = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 1 reward\n"
        "\t# Design intent: diplomatic reputation, opinion bonus\n"
        "\t# add_country_modifier = { name = tv_diplomatic_m1_bonus }\n"
        "}"
    ),
    new=(
        "tv_grant_diplomatic_milestone_1 = {\n"
        "\tadd_country_modifier = { modifier = tv_diplomatic_m1_bonus days = -1 }\n"
        "}"
    ),
    label="effects: grant diplomatic milestone 1",
)

patch(EFFECTS,
    old=(
        "tv_grant_diplomatic_milestone_2 = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 2 reward\n"
        "\t# Design intent: alliance reliability, defensive bonuses\n"
        "\t# add_country_modifier = { name = tv_diplomatic_m2_bonus }\n"
        "}"
    ),
    new=(
        "tv_grant_diplomatic_milestone_2 = {\n"
        "\tadd_country_modifier = { modifier = tv_diplomatic_m2_bonus days = -1 }\n"
        "}"
    ),
    label="effects: grant diplomatic milestone 2",
)

patch(EFFECTS,
    old=(
        "tv_grant_diplomatic_milestone_3 = {\n"
        "\t# TODO: Diplomatic Victory — Short-term Victory reward\n"
        "\t# Design intent: diplomatic range, claim fabrication speed\n"
        "\t# add_country_modifier = { name = tv_diplomatic_m3_bonus }\n"
        "}"
    ),
    new=(
        "tv_grant_diplomatic_milestone_3 = {\n"
        "\tadd_country_modifier = { modifier = tv_diplomatic_m3_bonus days = -1 }\n"
        "}"
    ),
    label="effects: grant diplomatic milestone 3",
)

patch(EFFECTS,
    old=(
        "tv_grant_diplomatic_milestone_4 = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 4 reward\n"
        "\t# Design intent: diplomatic immunity, vassal bonuses\n"
        "\t# add_country_modifier = { name = tv_diplomatic_m4_bonus }\n"
        "}"
    ),
    new=(
        "tv_grant_diplomatic_milestone_4 = {\n"
        "\tadd_country_modifier = { modifier = tv_diplomatic_m4_bonus days = -1 }\n"
        "}"
    ),
    label="effects: grant diplomatic milestone 4",
)

patch(EFFECTS,
    old=(
        "tv_grant_diplomatic_milestone_5 = {\n"
        "\t# TODO: Diplomatic Victory — Long-term Victory reward\n"
        "\t# Design intent: permanent casus belli defense, prestige\n"
        "\t# add_country_modifier = { name = tv_diplomatic_m5_bonus }\n"
        "}"
    ),
    new=(
        "tv_grant_diplomatic_milestone_5 = {\n"
        "\tadd_country_modifier = { modifier = tv_diplomatic_m5_bonus days = -1 }\n"
        "}"
    ),
    label="effects: grant diplomatic milestone 5",
)

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 13-17: MODIFIERS — fill 5 empty diplomatic bonus blocks
# Verification — Step 2, Reference: 00_modifier_types.txt
#   diplomatic_reputation, diplomatic_capacity, diplomatic_range_modifier,
#   honoring_alliance_call_cost_modifier, subject_opinions, subject_loyalty,
#   monthly_prestige all confirmed present.
# ══════════════════════════════════════════════════════════════════════════════

patch(MODIFIERS,
    old=(
        "tv_diplomatic_m1_bonus = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 1 reward (~1 Advance equivalent)\n"
        "\t# Design intent: diplomatic reputation, opinion bonus\n"
        "\t# Verify modifier key names in modifier_type_definitions/ before adding values\n"
        "}"
    ),
    new=(
        "tv_diplomatic_m1_bonus = {\n"
        "\tdiplomatic_reputation = 1\n"
        "\tdiplomatic_capacity = 1\n"
        "}"
    ),
    label="modifiers: tv_diplomatic_m1_bonus",
)

patch(MODIFIERS,
    old=(
        "tv_diplomatic_m2_bonus = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 2 reward (~1 Advance equivalent)\n"
        "\t# Design intent: alliance reliability, defensive bonuses\n"
        "\t# Verify modifier key names in modifier_type_definitions/ before adding values\n"
        "}"
    ),
    new=(
        "tv_diplomatic_m2_bonus = {\n"
        "\thonoring_alliance_call_cost_modifier = -0.10\n"
        "\tsubject_opinions = 5\n"
        "}"
    ),
    label="modifiers: tv_diplomatic_m2_bonus",
)

patch(MODIFIERS,
    old=(
        "tv_diplomatic_m3_bonus = {\n"
        "\t# TODO: Diplomatic Victory — Short-term Victory reward (~2 Advance equivalent)\n"
        "\t# Design intent: diplomatic range, claim fabrication speed\n"
        "\t# Verify modifier key names in modifier_type_definitions/ before adding values\n"
        "}"
    ),
    new=(
        "tv_diplomatic_m3_bonus = {\n"
        "\tdiplomatic_range_modifier = 0.20\n"
        "\tdiplomatic_reputation = 1\n"
        "}"
    ),
    label="modifiers: tv_diplomatic_m3_bonus",
)

patch(MODIFIERS,
    old=(
        "tv_diplomatic_m4_bonus = {\n"
        "\t# TODO: Diplomatic Victory — Milestone 4 reward (~1 Advance equivalent)\n"
        "\t# Design intent: diplomatic immunity, vassal bonuses\n"
        "\t# Verify modifier key names in modifier_type_definitions/ before adding values\n"
        "}"
    ),
    new=(
        "tv_diplomatic_m4_bonus = {\n"
        "\tsubject_loyalty = 5\n"
        "\tdiplomatic_capacity = 2\n"
        "}"
    ),
    label="modifiers: tv_diplomatic_m4_bonus",
)

patch(MODIFIERS,
    old=(
        "tv_diplomatic_m5_bonus = {\n"
        "\t# TODO: Diplomatic Victory — Long-term Victory reward (~2 Advance equivalent)\n"
        "\t# Design intent: permanent casus belli defense, prestige\n"
        "\t# Verify modifier key names in modifier_type_definitions/ before adding values\n"
        "}"
    ),
    new=(
        "tv_diplomatic_m5_bonus = {\n"
        "\tmonthly_prestige = 0.25\n"
        "\tdiplomatic_reputation = 1\n"
        "}"
    ),
    label="modifiers: tv_diplomatic_m5_bonus",
)

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 18: EVENTS — append diplomatic events section
# ══════════════════════════════════════════════════════════════════════════════

_DIPLOMATIC_EVENTS = (
    "\n"
    "# ──────────"
    "──────────"
    "──────────"
    "──────────"
    "──────────"
    "──────────"
    "──────────\n"
    "# DIPLOMATIC VICTORY EVENTS\n"
    "# ──────────"
    "──────────"
    "──────────"
    "──────────"
    "──────────"
    "──────────"
    "──────────\n"
    "\n"
    "tv.diplomatic.1 = {\n"
    "\ttype = country_event\n"
    "\ttitle = tv.diplomatic.1.t\n"
    "\tdesc = tv.diplomatic.1.d\n"
    "\toption = {\n"
    "\t\tname = tv.diplomatic.1.a\n"
    "\t\ttv_grant_diplomatic_milestone_1 = yes\n"
    "\t}\n"
    "}\n"
    "\n"
    "tv.diplomatic.2 = {\n"
    "\ttype = country_event\n"
    "\ttitle = tv.diplomatic.2.t\n"
    "\tdesc = tv.diplomatic.2.d\n"
    "\toption = {\n"
    "\t\tname = tv.diplomatic.2.a\n"
    "\t\ttv_grant_diplomatic_milestone_2 = yes\n"
    "\t}\n"
    "}\n"
    "\n"
    "tv.diplomatic.3 = {\n"
    "\ttype = country_event\n"
    "\ttitle = tv.diplomatic.3.t\n"
    "\tdesc = tv.diplomatic.3.d\n"
    "\toption = {\n"
    "\t\tname = tv.diplomatic.3.a\n"
    "\t\ttv_grant_diplomatic_milestone_3 = yes\n"
    "\t}\n"
    "}\n"
    "\n"
    "tv.diplomatic.4 = {\n"
    "\ttype = country_event\n"
    "\ttitle = tv.diplomatic.4.t\n"
    "\tdesc = tv.diplomatic.4.d\n"
    "\toption = {\n"
    "\t\tname = tv.diplomatic.4.a\n"
    "\t\ttv_grant_diplomatic_milestone_4 = yes\n"
    "\t}\n"
    "}\n"
    "\n"
    "tv.diplomatic.5 = {\n"
    "\ttype = country_event\n"
    "\ttitle = tv.diplomatic.5.t\n"
    "\tdesc = tv.diplomatic.5.d\n"
    "\toption = {\n"
    "\t\tname = tv.diplomatic.5.a\n"
    "\t\ttv_grant_diplomatic_milestone_5 = yes\n"
    "\t}\n"
    "}\n"
)

append_to(EVENTS, _DIPLOMATIC_EVENTS, label="events: append tv.diplomatic.1-5")

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 19: ON_ACTION — replace DVP TODO comment block with actual hooks
# Scope verification — Step 3, Reference: _hardcoded.txt
#   on_royal_marriage:4410 — scope:actor (sender country), scope:recipient (receiver country)
#   on_winning_war:1068    — scope:winner (winning country)
# ══════════════════════════════════════════════════════════════════════════════

patch(ON_ACTION,
    old=(
        "# ── DIPLOMATIC VICTORY POINTS (tv_diplomatic_victory_points) ──────────────────\n"
        "# Sources:\n"
        "#   +5  DVP: forming a defensive alliance with a major power\n"
        "#   +2  DVP: becoming guarantor of another nation\n"
        "#   +10 DVP: successfully mediating a peace treaty\n"
        "#   +5  DVP: winning a vote in an international organisation\n"
        "#   +3  DVP: concluding a royal marriage with a ruling dynasty\n"
        "#   +5  DVP: surviving a war as a weaker nation (favorable peace as defender)\n"
        "#\n"
        "# TODO: add on_action hooks below once source event names are verified (Step 2/3).\n"
        "# Pattern example:\n"
        "#   on_defensive_war_won = {\n"
        "#       effect = {\n"
        "#           # Award DVP to countries that defended successfully\n"
        "#       }\n"
        "#   }\n"
        "#"
    ),
    new=(
        "# ── DIPLOMATIC VICTORY POINTS (tv_diplomatic_victory_points) ──────────────────\n"
        "# +3 DVP: royal marriage (both parties)\n"
        "# +5 DVP: winning a war (winner)\n"
        "\n"
        "on_royal_marriage = {\n"
        "\teffect = {\n"
        "\t\tscope:actor = {\n"
        "\t\t\tif = {\n"
        "\t\t\t\tlimit = { NOT = { has_variable = tv_diplomatic_victory_points } }\n"
        "\t\t\t\tset_variable = { name = tv_diplomatic_victory_points value = 0 }\n"
        "\t\t\t}\n"
        "\t\t\tchange_variable = { name = tv_diplomatic_victory_points add = 3 }\n"
        "\t\t}\n"
        "\t\tscope:recipient = {\n"
        "\t\t\tif = {\n"
        "\t\t\t\tlimit = { NOT = { has_variable = tv_diplomatic_victory_points } }\n"
        "\t\t\t\tset_variable = { name = tv_diplomatic_victory_points value = 0 }\n"
        "\t\t\t}\n"
        "\t\t\tchange_variable = { name = tv_diplomatic_victory_points add = 3 }\n"
        "\t\t}\n"
        "\t}\n"
        "}\n"
        "\n"
        "on_winning_war = {\n"
        "\teffect = {\n"
        "\t\tscope:winner = {\n"
        "\t\t\tif = {\n"
        "\t\t\t\tlimit = { NOT = { has_variable = tv_diplomatic_victory_points } }\n"
        "\t\t\t\tset_variable = { name = tv_diplomatic_victory_points value = 0 }\n"
        "\t\t\t}\n"
        "\t\t\tchange_variable = { name = tv_diplomatic_victory_points add = 5 }\n"
        "\t\t}\n"
        "\t}\n"
        "}\n"
        "#"
    ),
    label="on_action: DVP hooks (royal_marriage + winning_war)",
)

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 20: ENGLISH LOCALIZATION — fill CONDITIONS and REWARDS for M1-M5
# ══════════════════════════════════════════════════════════════════════════════

patch(LOC_EN,
    old=(
        ' TV_DIPLOMATIC_M1_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M1_REWARDS: ""'
    ),
    new=(
        ' TV_DIPLOMATIC_M1_CONDITIONS: "Accumulate 50 Diplomatic Victory Points (DVP).'\
        ' Earned from royal marriages (+3 DVP) and winning wars (+5 DVP)."\n'
        ' TV_DIPLOMATIC_M1_REWARDS: "+1 Diplomatic Reputation\\n+1 Diplomatic Capacity"'
    ),
    label="loc EN: diplomatic M1 conditions/rewards",
)

patch(LOC_EN,
    old=(
        ' TV_DIPLOMATIC_M2_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M2_REWARDS: ""'
    ),
    new=(
        ' TV_DIPLOMATIC_M2_CONDITIONS: "Accumulate 120 DVP."\n'
        ' TV_DIPLOMATIC_M2_REWARDS: "-10% Alliance Call Cost\\n+5 Subject Opinion"'
    ),
    label="loc EN: diplomatic M2 conditions/rewards",
)

patch(LOC_EN,
    old=(
        ' TV_DIPLOMATIC_M3_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M3_REWARDS: ""'
    ),
    new=(
        ' TV_DIPLOMATIC_M3_CONDITIONS: "Accumulate 220 DVP. Short-term Victory."\n'
        ' TV_DIPLOMATIC_M3_REWARDS: "+20% Diplomatic Range\\n+1 Diplomatic Reputation"'
    ),
    label="loc EN: diplomatic M3 conditions/rewards",
)

patch(LOC_EN,
    old=(
        ' TV_DIPLOMATIC_M4_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M4_REWARDS: ""'
    ),
    new=(
        ' TV_DIPLOMATIC_M4_CONDITIONS: "Accumulate 380 DVP."\n'
        ' TV_DIPLOMATIC_M4_REWARDS: "+5 Subject Loyalty\\n+2 Diplomatic Capacity"'
    ),
    label="loc EN: diplomatic M4 conditions/rewards",
)

patch(LOC_EN,
    old=(
        ' TV_DIPLOMATIC_M5_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M5_REWARDS: ""'
    ),
    new=(
        ' TV_DIPLOMATIC_M5_CONDITIONS: "Accumulate 580 DVP. Long-term Victory."\n'
        ' TV_DIPLOMATIC_M5_REWARDS: "+0.25 Monthly Prestige\\n+1 Diplomatic Reputation"'
    ),
    label="loc EN: diplomatic M5 conditions/rewards",
)

# PATCH 21: Append diplomatic event localization keys (English)

_LOC_EN_EVENTS = (
    "\n"
    " # ── Diplomatic Victory Events ─────────────────────────────────────────\n"
    ' tv.diplomatic.1.t: "A Voice Among Nations"\n'
    ' tv.diplomatic.1.d: "Our patient diplomacy has begun to bear fruit.'
    " Through alliances and royal bonds, our nation is earning a place"
    ' at the table of great powers."\n'
    ' tv.diplomatic.1.a: "Let our word carry weight."\n'
    ' tv.diplomatic.2.t: "A Reliable Ally"\n'
    ' tv.diplomatic.2.d: "Nations seek us out as guarantors and partners.'
    " Our willingness to honour our commitments has built a reputation"
    ' that money cannot buy."\n'
    ' tv.diplomatic.2.a: "Our word is our bond."\n'
    ' tv.diplomatic.3.t: "A Power of the First Rank — Short-term Victory"\n'
    ' tv.diplomatic.3.d: "Our diplomatic reach extends across continents.'
    " Treaties bear our seal, and ambassadors from distant courts seek"
    ' our counsel. We have achieved a short-term diplomatic victory."\n'
    ' tv.diplomatic.3.a: "The world listens when we speak."\n'
    ' tv.diplomatic.4.t: "Arbiter of Nations"\n'
    ' tv.diplomatic.4.d: "No quarrel between princes is settled without'
    " our consent. Our subjects are loyal, our allies numerous, and our"
    ' influence unmatched in this age."\n'
    ' tv.diplomatic.4.a: "We shall keep the peace of the world."\n'
    ' tv.diplomatic.5.t: "Long-term Victory — Diplomatic Hegemon"\n'
    ' tv.diplomatic.5.d: "Five hundred and eighty points of diplomatic'
    " achievement. No nation in history has woven so vast a web of"
    " alliances, marriages, and mutual guarantees. Our legacy is written"
    ' not in conquest but in the peace we preserved."\n'
    ' tv.diplomatic.5.a: "Our name shall be synonymous with statecraft."\n'
)

append_to(LOC_EN, _LOC_EN_EVENTS, label="loc EN: append diplomatic event strings")

# ══════════════════════════════════════════════════════════════════════════════
# PATCH 22: CHINESE LOCALIZATION — replace diplomatic stub block
# ══════════════════════════════════════════════════════════════════════════════

patch(LOC_ZH,
    old=(
        ' TV_DIPLOMATIC_DESCRIPTION: "TODO"\n'
        ' TV_DIPLOMATIC_FLAVOR: "TODO"\n'
        "\n"
        ' TV_DIPLOMATIC_M1_TITLE: "TODO"\n'
        ' TV_DIPLOMATIC_M1_MEANING: "TODO"\n'
        ' TV_DIPLOMATIC_M1_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M1_REWARDS: ""\n'
        ' TV_DIPLOMATIC_M2_TITLE: "TODO"\n'
        ' TV_DIPLOMATIC_M2_MEANING: "TODO"\n'
        ' TV_DIPLOMATIC_M2_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M2_REWARDS: ""\n'
        ' TV_DIPLOMATIC_M3_TITLE: "TODO"\n'
        ' TV_DIPLOMATIC_M3_MEANING: "TODO"\n'
        ' TV_DIPLOMATIC_M3_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M3_REWARDS: ""\n'
        ' TV_DIPLOMATIC_M4_TITLE: "TODO"\n'
        ' TV_DIPLOMATIC_M4_MEANING: "TODO"\n'
        ' TV_DIPLOMATIC_M4_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M4_REWARDS: ""\n'
        ' TV_DIPLOMATIC_M5_TITLE: "TODO"\n'
        ' TV_DIPLOMATIC_M5_MEANING: "TODO"\n'
        ' TV_DIPLOMATIC_M5_CONDITIONS: ""\n'
        ' TV_DIPLOMATIC_M5_REWARDS: ""'
    ),
    new=(
        ' TV_DIPLOMATIC_DESCRIPTION: "通过同盟、条约和外交手段积累影响力。"\n'
        ' TV_DIPLOMATIC_FLAVOR: “\\”在理性失败之处，军随谓少用。\\””\n'
        "\n"
        ' TV_DIPLOMATIC_M1_TITLE: "外交胜利 — 里程碑一"\n'
        ' TV_DIPLOMATIC_M1_MEANING: "50 外交胜利点。在国际事务中占有一席之地。"\n'
        ' TV_DIPLOMATIC_M1_CONDITIONS: "积累50外交胜利点（DVP）。通过联姻（+3 DVP）或赞利战争（+5 DVP）获得。"\n'
        ' TV_DIPLOMATIC_M1_REWARDS: "+1 外交声望\\n+1 外交容量"\n'
        ' TV_DIPLOMATIC_M2_TITLE: "外交胜利 — 里程碑二"\n'
        ' TV_DIPLOMATIC_M2_MEANING: "120 DVP。可靠的盟友与和平居间人。"\n'
        ' TV_DIPLOMATIC_M2_CONDITIONS: "积累120 DVP。"\n'
        ' TV_DIPLOMATIC_M2_REWARDS: "-10% 履行盟约费用\\n+5 属国好感度"\n'
        ' TV_DIPLOMATIC_M3_TITLE: "外交胜利 — 短期胜利"\n'
        ' TV_DIPLOMATIC_M3_MEANING: "220 DVP。一流外交大国。短期胜利。"\n'
        ' TV_DIPLOMATIC_M3_CONDITIONS: "积累220 DVP。短期胜利。"\n'
        ' TV_DIPLOMATIC_M3_REWARDS: "+20% 外交范围\\n+1 外交声望"\n'
        ' TV_DIPLOMATIC_M4_TITLE: "外交胜利 — 里程碑四"\n'
        ' TV_DIPLOMATIC_M4_MEANING: "380 DVP。国际秩序的仲裁人。"\n'
        ' TV_DIPLOMATIC_M4_CONDITIONS: "积累380 DVP。"\n'
        ' TV_DIPLOMATIC_M4_REWARDS: "+5 属国忠诚度\\n+2 外交容量"\n'
        ' TV_DIPLOMATIC_M5_TITLE: "外交胜利 — 长期胜利"\n'
        ' TV_DIPLOMATIC_M5_MEANING: "580 DVP。无可争议的外交霸主。长期胜利。"\n'
        ' TV_DIPLOMATIC_M5_CONDITIONS: "积累580 DVP。长期胜利。"\n'
        ' TV_DIPLOMATIC_M5_REWARDS: "+0.25 每月声望\\n+1 外交声望"'
    ),
    label="loc ZH: fill diplomatic section",
)

# PATCH 23: Append diplomatic event localization keys (Chinese)

_LOC_ZH_EVENTS = (
    "\n"
    " # ── 外交胜利事件 ──────────────────────────────────────\n"
    ' tv.diplomatic.1.t: "外交展露头角"\n'
    ' tv.diplomatic.1.d: "我们耐心的外交已开始结果。通过同盟与联姻，我国正在赢得一席之地。"\n'
    ' tv.diplomatic.1.a: "让我们的话语具有分量。"\n'
    ' tv.diplomatic.2.t: "可靠的盟友"\n'
    ' tv.diplomatic.2.d: "各国將我们视为促成和平的保证人与合作伙伴。我们履行承诺的意愿已席建了金钱买不到的声望。"\n'
    ' tv.diplomatic.2.a: "我们以診言为盟。"\n'
    ' tv.diplomatic.3.t: "一流外交大国 — 短期胜利"\n'
    ' tv.diplomatic.3.d: "我们的外交触角已覆盖大陆。条约盖有我们的印签，远方庭院的使节俬岔1我们的廣语。我们已取得短期外交胜利。"\n'
    ' tv.diplomatic.3.a: "世界在我们说话时会值岗刀傅。"\n'
    ' tv.diplomatic.4.t: "万国仲裁人"\n'
    ' tv.diplomatic.4.d: "没有任何小国纷争可绕过我们的同意而得到解决。我们的属国忠诚，盟友众多，在这个时代影响无可匹敌。"\n'
    ' tv.diplomatic.4.a: "我们将维护世界和平。"\n'
    ' tv.diplomatic.5.t: "长期胜利 — 外交霸主"\n'
    ' tv.diplomatic.5.d: "五百八十分外交胜利点。史上从未有任何国家编织过如此广大的同盟、联姻与互保网络。我们的功勣不写于征服，而写于我们保卫的和平。"\n'
    ' tv.diplomatic.5.a: "我们的名字将与外交艺术永远共存。"\n'
)

append_to(LOC_ZH, _LOC_ZH_EVENTS, label="loc ZH: append diplomatic event strings")

# ══════════════════════════════════════════════════════════════════════════════

print(f"\n{_ok} patches applied, {_err} errors.")
if _err:
    sys.exit(1)
print("Next: conda run -n eu5 python scripts/validate.py --changed")
