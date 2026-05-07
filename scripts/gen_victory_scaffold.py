#!/usr/bin/env python3
"""Generate all Towards Victory scaffold source files.

Generates: situations, triggers, effects, modifiers, on_action, GUI, localization.
All milestone condition / reward content is left as documented stubs — fill in later.

Usage:
    conda run -n eu5 python scripts/gen_victory_scaffold.py
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"

# ─────────────────────────────────────────────────────────────────────────────
# Configuration — drives all file generation.
# Each path has 5 milestones: 1, 2, V1 (short-term), 4, V2 (long-term).
# ─────────────────────────────────────────────────────────────────────────────

PATHS = [
    {
        "id": "conquest",
        "name_en": "Conquest Victory",
        "name_zh": "征服胜利",
        "desc_en": "Dominate the world through territorial expansion.",
        "flavor_en": '"The greatest happiness is to vanquish your enemies." — Genghis Khan',
        "progress_var": "tv_conquest_progress_pct",
        "milestone_var": "tv_conquest_milestone",
        "icon": "tv_conquest",
        "bar_style": "progress_bar_blue_alt",
        "milestones": [
            {
                "n": 1, "label": "1", "short": False, "long": False,
                "threshold_hint": "~150 owned locations",
                "meaning_en": "A nation of modest reach. ~150 owned locations.",
                "meaning_zh": "TODO",
                "reward_hint": "combat capability (manpower_recovery_speed, land_morale)",
            },
            {
                "n": 2, "label": "2", "short": False, "long": False,
                "threshold_hint": "~350 owned locations",
                "meaning_en": "A substantial empire. ~350 owned locations.",
                "meaning_zh": "TODO",
                "reward_hint": "logistics (supply, attrition reduction)",
            },
            {
                "n": 3, "label": "V1", "short": True, "long": False,
                "threshold_hint": "~600 owned locations",
                "meaning_en": "Territorial supremacy secured. Short-term Victory. ~600 owned locations.",
                "meaning_zh": "TODO",
                "reward_hint": "governance (admin efficiency, unrest reduction)",
            },
            {
                "n": 4, "label": "4", "short": False, "long": False,
                "threshold_hint": "~1100 owned locations",
                "meaning_en": "An empire spanning continents. ~1100 owned locations.",
                "meaning_zh": "TODO",
                "reward_hint": "administration at scale (autonomy reduction, corruption)",
            },
            {
                "n": 5, "label": "V2", "short": False, "long": True,
                "threshold_hint": "~1600 owned locations",
                "meaning_en": "Undisputed world empire. Long-term Victory. ~1600 owned locations.",
                "meaning_zh": "TODO",
                "reward_hint": "grand legacy (prestige cap, manpower cap)",
            },
        ],
    },
    {
        "id": "prosperity",
        "name_en": "Prosperity Victory",
        "name_zh": "繁荣胜利",
        "desc_en": "Build a thriving nation through domestic development.",
        "flavor_en": '"Prosperity is the fruit of labour." — Thucydides',
        "progress_var": "tv_prosperity_progress_pct",
        "milestone_var": "tv_prosperity_milestone",
        "icon": "tv_prosperity",
        "bar_style": "progress_bar_green_alt",
        "milestones": [
            {
                "n": 1, "label": "1", "short": False, "long": False,
                "threshold_hint": "Composite development score threshold 1",
                "meaning_en": "A growing nation — early domestic prosperity.",
                "meaning_zh": "TODO",
                "reward_hint": "domestic production bonus, tax income",
            },
            {
                "n": 2, "label": "2", "short": False, "long": False,
                "threshold_hint": "Composite development score threshold 2",
                "meaning_en": "A flourishing nation — sustained domestic investment.",
                "meaning_zh": "TODO",
                "reward_hint": "pop growth, building cost reduction",
            },
            {
                "n": 3, "label": "V1", "short": True, "long": False,
                "threshold_hint": "Composite development score threshold 3",
                "meaning_en": "A prosperous heartland. Short-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "development cost reduction",
            },
            {
                "n": 4, "label": "4", "short": False, "long": False,
                "threshold_hint": "Composite development score threshold 4 (high)",
                "meaning_en": "An advanced nation — the envy of neighbours.",
                "meaning_zh": "TODO",
                "reward_hint": "construction speed, educated pop bonus",
            },
            {
                "n": 5, "label": "V2", "short": False, "long": True,
                "threshold_hint": "Composite development score threshold 5 (very high)",
                "meaning_en": "The most developed nation on earth. Long-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "permanent construction speed, population cap bonus",
            },
        ],
    },
    {
        "id": "trade",
        "name_en": "Trade Victory",
        "name_zh": "贸易胜利",
        "desc_en": "Build an empire of commerce and maritime power.",
        "flavor_en": '"Venice does not make war; Venice makes money."',
        "progress_var": "tv_trade_progress_pct",
        "milestone_var": "tv_trade_milestone",
        "icon": "tv_trade",
        "bar_style": "progress_bar_goldish",
        "milestones": [
            {
                "n": 1, "label": "1", "short": False, "long": False,
                "threshold_hint": "Trade income share threshold 1",
                "meaning_en": "A merchant of note — commanding a trade node.",
                "meaning_zh": "TODO",
                "reward_hint": "merchant power, trade node influence",
            },
            {
                "n": 2, "label": "2", "short": False, "long": False,
                "threshold_hint": "Dominating multiple trade nodes",
                "meaning_en": "A maritime power — dominating multiple nodes.",
                "meaning_zh": "TODO",
                "reward_hint": "light ships, merchant count",
            },
            {
                "n": 3, "label": "V1", "short": True, "long": False,
                "threshold_hint": "Major trade empire threshold",
                "meaning_en": "A major trade empire. Short-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "trade efficiency",
            },
            {
                "n": 4, "label": "4", "short": False, "long": False,
                "threshold_hint": "Near-monopoly on key nodes",
                "meaning_en": "Near-monopoly control of key trade arteries.",
                "meaning_zh": "TODO",
                "reward_hint": "trade steering bonus",
            },
            {
                "n": 5, "label": "V2", "short": False, "long": True,
                "threshold_hint": "Trade hegemon threshold",
                "meaning_en": "Undisputed trade hegemon. Long-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "permanent trade income multiplier, merchant count",
            },
        ],
    },
    {
        "id": "diplomatic",
        "name_en": "Diplomatic Victory",
        "name_zh": "外交胜利",
        "desc_en": "Accumulate influence through alliances, treaties, and statecraft.",
        "flavor_en": '"An army is of little use where reason fails."',
        "progress_var": "tv_diplomatic_progress_pct",
        "milestone_var": "tv_diplomatic_milestone",
        "icon": "tv_diplomatic",
        "bar_style": "progress_bar_blue_alt",
        "milestones": [
            {
                "n": 1, "label": "1", "short": False, "long": False,
                "threshold_hint": "tv_diplomatic_victory_points >= 50",
                "meaning_en": "50 Diplomatic Victory Points. A respected voice in affairs.",
                "meaning_zh": "TODO",
                "reward_hint": "diplomatic reputation, opinion bonus",
            },
            {
                "n": 2, "label": "2", "short": False, "long": False,
                "threshold_hint": "tv_diplomatic_victory_points >= 120",
                "meaning_en": "120 DVP. A reliable ally and guarantor of peace.",
                "meaning_zh": "TODO",
                "reward_hint": "alliance reliability, defensive bonuses",
            },
            {
                "n": 3, "label": "V1", "short": True, "long": False,
                "threshold_hint": "tv_diplomatic_victory_points >= 220",
                "meaning_en": "220 DVP. A power of first diplomatic rank. Short-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "diplomatic range, claim fabrication speed",
            },
            {
                "n": 4, "label": "4", "short": False, "long": False,
                "threshold_hint": "tv_diplomatic_victory_points >= 380",
                "meaning_en": "380 DVP. The arbiter of international order.",
                "meaning_zh": "TODO",
                "reward_hint": "diplomatic immunity, vassal bonuses",
            },
            {
                "n": 5, "label": "V2", "short": False, "long": True,
                "threshold_hint": "tv_diplomatic_victory_points >= 580",
                "meaning_en": "580 DVP. Undisputed diplomatic hegemon. Long-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "permanent casus belli defense, prestige",
            },
        ],
    },
    {
        "id": "cultural",
        "name_en": "Cultural Victory",
        "name_zh": "文化胜利",
        "desc_en": "Achieve pre-eminence through art, court, and the spread of culture.",
        "flavor_en": '"Art is the signature of civilisations."',
        "progress_var": "tv_cultural_progress_pct",
        "milestone_var": "tv_cultural_milestone",
        "icon": "tv_cultural",
        "bar_style": "progress_bar_green_alt",
        "milestones": [
            {
                "n": 1, "label": "1", "short": False, "long": False,
                "threshold_hint": "tv_cultural_influence_points >= 50",
                "meaning_en": "50 Cultural Influence Points. A patron of the arts.",
                "meaning_zh": "TODO",
                "reward_hint": "court attraction, ideas cost reduction",
            },
            {
                "n": 2, "label": "2", "short": False, "long": False,
                "threshold_hint": "tv_cultural_influence_points >= 120",
                "meaning_en": "120 CIP. A celebrated cultural power.",
                "meaning_zh": "TODO",
                "reward_hint": "diplomat effectiveness, cultural prestige",
            },
            {
                "n": 3, "label": "V1", "short": True, "long": False,
                "threshold_hint": "tv_cultural_influence_points >= 220",
                "meaning_en": "220 CIP. A centre of Renaissance brilliance. Short-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "artifact find chance, court income",
            },
            {
                "n": 4, "label": "4", "short": False, "long": False,
                "threshold_hint": "tv_cultural_influence_points >= 380",
                "meaning_en": "380 CIP. Culture radiates from your court across the world.",
                "meaning_zh": "TODO",
                "reward_hint": "cultural spread multiplier, missionary strength",
            },
            {
                "n": 5, "label": "V2", "short": False, "long": True,
                "threshold_hint": "tv_cultural_influence_points >= 580",
                "meaning_en": "580 CIP. The greatest cultural legacy in history. Long-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "permanent cultural spread multiplier, prestige cap",
            },
        ],
    },
    {
        "id": "science",
        "name_en": "Scientific Victory",
        "name_zh": "科技胜利",
        "desc_en": "Lead the world through technological advancement into the industrial age.",
        "flavor_en": '"Science is the great antidote to superstition." — Adam Smith',
        "progress_var": "tv_science_progress_pct",
        "milestone_var": "tv_science_milestone",
        "icon": "tv_science",
        "bar_style": "progress_bar_blue_green_alt",
        "milestones": [
            {
                "n": 1, "label": "1", "short": False, "long": False,
                "threshold_hint": "tv_science_score — Age 1-2 era threshold",
                "meaning_en": "Early scientific curiosity. Age 1-2 technology score.",
                "meaning_zh": "TODO",
                "reward_hint": "research speed bonus",
            },
            {
                "n": 2, "label": "2", "short": False, "long": False,
                "threshold_hint": "tv_science_score — Age 3 era threshold",
                "meaning_en": "A nation of scholars. Age 3 technology score.",
                "meaning_zh": "TODO",
                "reward_hint": "technology spread, military effectiveness",
            },
            {
                "n": 3, "label": "V1", "short": True, "long": False,
                "threshold_hint": "tv_science_score — Age 4 era threshold",
                "meaning_en": "Scientific pre-eminence. Age 4 technology score. Short-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "institution spread speed, educated pop growth",
            },
            {
                "n": 4, "label": "4", "short": False, "long": False,
                "threshold_hint": "tv_science_score — High Age 4 threshold",
                "meaning_en": "The world's foremost scientific nation.",
                "meaning_zh": "TODO",
                "reward_hint": "scientific institution bonus, production bonus",
            },
            {
                "n": 5, "label": "V2", "short": False, "long": True,
                "threshold_hint": "tv_science_score — Age 5 (steam/industrial) threshold",
                "meaning_en": "The Industrial Revolution achieved. Long-term Victory.",
                "meaning_zh": "TODO",
                "reward_hint": "permanent production bonus, army modernization",
            },
        ],
    },
]

# Labels for milestone circles in GUI — loc keys map to these display strings
MILESTONE_LOC = {
    1: ("TV_MILESTONE_1_LABEL", "1"),
    2: ("TV_MILESTONE_2_LABEL", "2"),
    3: ("TV_MILESTONE_V1_LABEL", "V1"),
    4: ("TV_MILESTONE_4_LABEL", "4"),
    5: ("TV_MILESTONE_V2_LABEL", "V2"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def write_file(path: Path, content: str, bom: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoding = "utf-8-sig" if bom else "utf-8"
    with open(path, "w", encoding=encoding, newline="\n") as fh:
        fh.write(content)
    print(f"  wrote  {path.relative_to(ROOT)}")


def _milestone_circle_block(path: dict, m: dict, indent: str) -> list[str]:
    """Return lines for one milestone circle blockoverride."""
    pid = path["id"]
    n = m["n"]
    mv = path["milestone_var"]
    loc_key, label_str = MILESTONE_LOC[n]

    if m["long"]:
        block_name = "milestone_v2_circle"
        size = "38 38"
        bg = "bg_circle_piechart_big"
    elif m["short"]:
        block_name = "milestone_v1_circle"
        size = "34 34"
        bg = "bg_circle_piechart_big"
    else:
        block_name = f"milestone_{n}_circle"
        size = "30 30"
        bg = "bg_circle_piechart"

    # Verification — Step 3, Reference: treaty_of_tordesillas.gui:138, declare_war_lateralview.gui:109
    # EqualTo_float(FixedPointToFloat(...GetValue), '(float)1.0') / GreaterThanOrEqualTo_CFixedPoint(...)
    # Country.MakeScope is the correct chain in situation panels (western_schism.gui:43, no GetPlayerCountry)
    vis_expr = (
        f"[GreaterThanOrEqualTo_CFixedPoint("
        f"Country.MakeScope.GetVariable('{mv}').GetValue, '(CFixedPoint){n}.0')]"
    )

    i = indent
    return [
        f'{i}blockoverride "{block_name}" {{',
        f'{i}\twidget = {{',
        f'{i}\t\tsize = {{ {size} }}',
        f'{i}\t\tparentanchor = vcenter',
        f'{i}\t\tusing = {bg}',
        f'{i}\t\t# Gold glow overlay — visible when {mv} >= {n}',
        f'{i}\t\ticon = {{',
        f'{i}\t\t\tvisible = "{vis_expr}"',
        f'{i}\t\t\tparentanchor = center',
        f'{i}\t\t\tsize = {{ 100% 100% }}',
        f'{i}\t\t\ttexture = "gfx/interface/component_tiles/selected_glow.dds"',
        f'{i}\t\t\tusing = color_new_gold',
        f'{i}\t\t\talpha = 0.75',
        f'{i}\t\t}}',
        f'{i}\t\ttext_single = {{',
        f'{i}\t\t\tparentanchor = center',
        f'{i}\t\t\tsize = {{ 100% 100% }}',
        f'{i}\t\t\tautoresize = no',
        f'{i}\t\t\talign = center|nobaseline',
        f'{i}\t\t\ttext = "{loc_key}"',
        f'{i}\t\t}}',
        f'{i}\t\ttooltipwidget = {{ using = tv_{pid}_milestone_{n}_tooltip }}',
        f'{i}\t}}',
        f'{i}}}',
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Generator functions
# ─────────────────────────────────────────────────────────────────────────────

def gen_situation() -> None:
    content = """\
# Towards Victory — Situation definitions
# Generated by scripts/gen_victory_scaffold.py
# Framework: do not hand-edit structural sections; fill in TODO stubs in place.

tv_victory_situation = {
\tmonthly_spawn_chance = monthly_spawn_chance_unique

\tcan_start = {
\t\tgame_is_initialized = yes
\t}

\tcan_end = {
\t\talways = no    # Permanent situation — never ends naturally
\t}

\tvisible = {
\t\talways = yes
\t}

\ton_start = {
\t\t# Initialise the AI yearly pulse counter on the situation scope
\t\tset_variable = { name = tv_ai_pulse_counter value = 0 }
\t}

\ton_monthly = {
\t\thidden_effect = {
\t\t\t# ── PLAYER MILESTONE CHECKS (every month) ────────────────────────────────
\t\t\t# Verification — Step 3: is_ai = no confirmed country-scope trigger
\t\t\t# Reference: parliament_agendas/00_common.txt (potential = { is_ai = no })
\t\t\tevery_country = {
\t\t\t\tlimit = {
\t\t\t\t\tis_ai = no
\t\t\t\t}
\t\t\t\ttv_check_all_milestones_effect = yes
\t\t\t\ttv_update_all_progress_pct_effect = yes
\t\t\t}

\t\t\t# ── AI MILESTONE CHECKS (every 12 months, via counter) ────────────────────
\t\t\t# Verification — Step 3: is_ai = yes confirmed country-scope trigger
\t\t\t# Reference: subject_interaction_events.txt, hre.txt, privateers.txt
\t\t\tchange_variable = { name = tv_ai_pulse_counter add = 1 }
\t\t\tif = {
\t\t\t\tlimit = { var:tv_ai_pulse_counter >= 12 }
\t\t\t\tset_variable = { name = tv_ai_pulse_counter value = 0 }
\t\t\t\tevery_country = {
\t\t\t\t\tlimit = {
\t\t\t\t\t\tis_ai = yes
\t\t\t\t\t}
\t\t\t\t\ttv_check_all_milestones_effect = yes
\t\t\t\t\ttv_update_all_progress_pct_effect = yes
\t\t\t\t}
\t\t\t}
\t\t}
\t}

\ton_ended = {
\t\t# Should never fire — tv_victory_situation is permanent
\t}
}
"""
    write_file(SRC / "in_game/common/situations/towards_victory_situations.txt", content)


def gen_triggers() -> None:
    lines: list[str] = [
        "# Towards Victory — Milestone trigger definitions",
        "# Generated by scripts/gen_victory_scaffold.py",
        "# All 30 triggers are stubs (always = no). Fill in actual conditions path by path.",
        "# Consult reference_game_files/game/main_menu/common/modifier_type_definitions/",
        "# and reference_game_files/game/in_game/common/scripted_triggers/ for patterns.",
        "",
    ]
    for path in PATHS:
        pid = path["id"]
        lines += [
            f"# {'─' * 70}",
            f"# {path['name_en'].upper()} MILESTONES",
            f"# {'─' * 70}",
            "",
        ]
        for m in path["milestones"]:
            n = m["n"]
            label = (
                "Short-term Victory" if m["short"] else
                "Long-term Victory" if m["long"] else
                f"Milestone {n}"
            )
            lines += [
                f"tv_{pid}_milestone_{n} = {{",
                f"\t# TODO: {path['name_en']} — {label}",
                f"\t# Threshold hint: {m['threshold_hint']}",
                f"\t# Step 2/3 verification required before implementing",
                f"\talways = no",
                f"}}",
                "",
            ]
        lines.append("")

    write_file(
        SRC / "in_game/common/scripted_triggers/towards_victory_triggers.txt",
        "\n".join(lines),
    )


def gen_effects() -> None:
    lines: list[str] = [
        "# Towards Victory — Scripted effect definitions",
        "# Generated by scripts/gen_victory_scaffold.py",
        "",
        "# ═══════════════════════════════════════════════════════════════════════════",
        "# SECTION 1: TOP-LEVEL DISPATCHER",
        "# ═══════════════════════════════════════════════════════════════════════════",
        "",
        "tv_check_all_milestones_effect = {",
    ]
    for path in PATHS:
        lines.append(f"\ttv_check_{path['id']}_milestones_effect = yes")
    lines += ["}", ""]

    # Per-path milestone checkers
    lines += [
        "# ═══════════════════════════════════════════════════════════════════════════",
        "# SECTION 2: PER-PATH MILESTONE CHECKERS",
        "# Guards via var:tv_*_milestone < N prevent re-triggering after grant.",
        "# ═══════════════════════════════════════════════════════════════════════════",
        "",
    ]
    for path in PATHS:
        pid = path["id"]
        mv = path["milestone_var"]
        lines += [
            f"# ── {path['name_en']} ──────────────────────────────────────────────────────",
            f"tv_check_{pid}_milestones_effect = {{",
            f"\t# Initialise on first call (guards against missing variable)",
            f"\tif = {{",
            f"\t\tlimit = {{ NOT = {{ has_variable = {mv} }} }}",
            f"\t\tset_variable = {{ name = {mv} value = 0 }}",
            f"\t}}",
        ]
        for m in path["milestones"]:
            n = m["n"]
            ev = f"tv.{pid}.{n}"
            lines += [
                f"\tif = {{",
                f"\t\tlimit = {{",
                f"\t\t\tvar:{mv} < {n}",
                f"\t\t\ttv_{pid}_milestone_{n} = yes",
                f"\t\t}}",
                f"\t\tset_variable = {{ name = {mv} value = {n} }}",
                f"\t\ttrigger_event_non_silently = {ev}",
                f"\t}}",
            ]
        lines += ["}", ""]

    # Progress pct updater
    lines += [
        "# ═══════════════════════════════════════════════════════════════════════════",
        "# SECTION 3: PROGRESS PERCENTAGE UPDATER",
        "# Stores tv_*_progress_pct in [0.0, 1.0] for each path (used by GUI bars).",
        "# Called monthly for players, yearly for AI — must be cheap to evaluate.",
        "# ═══════════════════════════════════════════════════════════════════════════",
        "",
        "tv_update_all_progress_pct_effect = {",
    ]
    for path in PATHS:
        pid = path["id"]
        pv = path["progress_var"]
        v2_hint = next(m["threshold_hint"] for m in path["milestones"] if m["long"])
        lines += [
            f"\t# ── {path['name_en']} ────────────────────────────────────────────────────",
            f"\t# TODO: compute 0.0-1.0 progress fraction for {pid} path",
            f"\t# Formula: {pv} = raw_metric / v2_threshold",
            f"\t# V2 threshold hint: {v2_hint}",
            f"\t# Pattern:",
            f"\t#   set_variable = {{ name = {pv} value = <raw_metric_accessor> }}",
            f"\t#   change_variable = {{ name = {pv} divide = <v2_threshold_literal> }}",
            f"\t#   if = {{ limit = {{ var:{pv} > 1 }} set_variable = {{ name = {pv} value = 1 }} }}",
            "",
        ]
    lines += ["}", ""]

    # Grant (reward) effects
    lines += [
        "# ═══════════════════════════════════════════════════════════════════════════",
        "# SECTION 4: MILESTONE REWARD EFFECTS",
        "# Called from events tv.<path>.<n> after the milestone is first reached.",
        "# Each effect applies the permanent static modifier for that milestone.",
        "# ═══════════════════════════════════════════════════════════════════════════",
        "",
    ]
    for path in PATHS:
        pid = path["id"]
        lines.append(f"# {path['name_en']}")
        for m in path["milestones"]:
            n = m["n"]
            mod = f"tv_{pid}_m{n}_bonus"
            label = (
                "Short-term Victory reward" if m["short"] else
                "Long-term Victory reward" if m["long"] else
                f"Milestone {n} reward"
            )
            lines += [
                f"tv_grant_{pid}_milestone_{n} = {{",
                f"\t# TODO: {path['name_en']} — {label}",
                f"\t# Design intent: {m['reward_hint']}",
                f"\t# add_country_modifier = {{ name = {mod} }}",
                f"}}",
                "",
            ]
        lines.append("")

    write_file(
        SRC / "in_game/common/scripted_effects/towards_victory_effects.txt",
        "\n".join(lines),
    )


def gen_modifiers() -> None:
    lines: list[str] = [
        "# Towards Victory — Static modifier definitions (permanent milestone rewards)",
        "# Generated by scripts/gen_victory_scaffold.py",
        "# All 30 modifiers are stubs. Fill in actual modifier effects path by path.",
        "#",
        "# Before adding modifier effect keys, verify names against:",
        "#   reference_game_files/game/main_menu/common/modifier_type_definitions/",
        "# Country-scoped modifiers only. Location-scoped modifiers require TRY_REPLACE",
        "# in src/main_menu/common/static_modifiers/ per EU5 engine requirements.",
        "",
    ]
    for path in PATHS:
        pid = path["id"]
        lines += [
            f"# {'─' * 70}",
            f"# {path['name_en'].upper()} MODIFIERS",
            f"# {'─' * 70}",
            "",
        ]
        for m in path["milestones"]:
            n = m["n"]
            label = (
                "Short-term Victory reward" if m["short"] else
                "Long-term Victory reward" if m["long"] else
                f"Milestone {n} reward"
            )
            lines += [
                f"tv_{pid}_m{n}_bonus = {{",
                f"\t# TODO: {path['name_en']} — {label} (~{2 if m['short'] or m['long'] else 1} Advance equivalent)",
                f"\t# Design intent: {m['reward_hint']}",
                f"\t# Verify modifier key names in modifier_type_definitions/ before adding values",
                f"}}",
                "",
            ]
        lines.append("")

    write_file(
        SRC / "in_game/common/static_modifiers/towards_victory_modifiers.txt",
        "\n".join(lines),
    )


def gen_on_action() -> None:
    content = """\
# Towards Victory — Supplemental on_action hooks
# Generated by scripts/gen_victory_scaffold.py
#
# Primary milestone checking is handled by tv_victory_situation.on_monthly.
# This file provides POINT ACCUMULATION hooks for Diplomatic and Cultural paths,
# tied to specific in-game events.
#
# ── DIPLOMATIC VICTORY POINTS (tv_diplomatic_victory_points) ──────────────────
# Sources:
#   +5  DVP: forming a defensive alliance with a major power
#   +2  DVP: becoming guarantor of another nation
#   +10 DVP: successfully mediating a peace treaty
#   +5  DVP: winning a vote in an international organisation
#   +3  DVP: concluding a royal marriage with a ruling dynasty
#   +5  DVP: surviving a war as a weaker nation (favorable peace as defender)
#
# TODO: add on_action hooks below once source event names are verified (Step 2/3).
# Pattern example:
#   on_defensive_war_won = {
#       effect = {
#           # Award DVP to countries that defended successfully
#       }
#   }
#
# ── CULTURAL INFLUENCE POINTS (tv_cultural_influence_points) ──────────────────
# Sources:
#   +10 CIP per artifact owned (checked monthly, once per artifact per month)
#   +3  CIP per cultural spread event where this country is the origin
#   +5  CIP per era with court spending above threshold
#
# TODO: add monthly artifact CIP check via monthly_country_pulse or equivalent.
# Step 2/3: verify on_action name and artifact ownership trigger before implementing.
#
# ── SCIENTIFIC SCORE (tv_science_score) ──────────────────────────────────────
# Weighted technology count (recomputed in tv_update_all_progress_pct_effect):
#   Age 1-2 technologies: weight x1
#   Age 3 technologies:   weight x2
#   Age 4 technologies:   weight x3
#   Age 5 technologies (steam/industrial): weight x5
#
# TODO: implement scoring formula inside tv_update_all_progress_pct_effect.
"""
    write_file(SRC / "in_game/common/on_action/towards_victory_yearly.txt", content)


def gen_localization_en() -> None:
    lines: list[str] = [
        "l_english:",
        " # ── Situation ──────────────────────────────────────────────────────────────────",
        ' tv_victory_situation: "Towards Victory"',
        ' tv_victory_situation_desc: "Track your progress across six distinct victory paths."',
        ' TV_VICTORY_SITUATION_TITLE: "Victory Progress"',
        "",
        " # ── Shared milestone circle labels ─────────────────────────────────────────────",
        ' TV_MILESTONE_1_LABEL: "1"',
        ' TV_MILESTONE_2_LABEL: "2"',
        ' TV_MILESTONE_V1_LABEL: "V1"',
        ' TV_MILESTONE_4_LABEL: "4"',
        ' TV_MILESTONE_V2_LABEL: "V2"',
        "",
        " # ── Shared tooltip section headers ─────────────────────────────────────────────",
        ' TV_TOOLTIP_CONDITIONS_HEADER: "Required Conditions"',
        ' TV_TOOLTIP_REWARDS_HEADER: "Milestone Reward"',
        "",
    ]
    for path in PATHS:
        pid = path["id"].upper()
        lines += [
            f" # ── {path['name_en']} ─────────────────────────────────────────────────────────",
            f' TV_{pid}_TITLE: "{path["name_en"]}"',
            f' TV_{pid}_DESCRIPTION: "{path["desc_en"]}"',
            f' TV_{pid}_FLAVOR: "{path["flavor_en"]}"',
            "",
        ]
        for m in path["milestones"]:
            n = m["n"]
            label = (
                "Short-term Victory" if m["short"] else
                "Long-term Victory" if m["long"] else
                f"Milestone {n}"
            )
            lines += [
                f' TV_{pid}_M{n}_TITLE: "{path["name_en"]} — {label}"',
                f' TV_{pid}_M{n}_MEANING: "{m["meaning_en"]}"',
                f' TV_{pid}_M{n}_CONDITIONS: ""',
                f' TV_{pid}_M{n}_REWARDS: ""',
            ]
        lines.append("")

    write_file(
        SRC / "main_menu/localization/english/towards_victory_l_english.yml",
        "\n".join(lines),
        bom=True,
    )


def gen_localization_zh() -> None:
    ZH: dict[str, str] = {
        "conquest":   "征服胜利",
        "prosperity": "繁荣胜利",
        "trade":      "贸易胜利",
        "diplomatic": "外交胜利",
        "cultural":   "文化胜利",
        "science":    "科技胜利",
    }
    lines: list[str] = [
        "l_simp_chinese:",
        " # ── 局势 ──────────────────────────────────────────────────────────────────────",
        ' tv_victory_situation: "胜利条件"',
        ' tv_victory_situation_desc: "追踪您在六条胜利路径上的进度。"',
        ' TV_VICTORY_SITUATION_TITLE: "胜利进度"',
        "",
        " # ── 共用里程碑圆形标签 ──────────────────────────────────────────────────────────",
        ' TV_MILESTONE_1_LABEL: "1"',
        ' TV_MILESTONE_2_LABEL: "2"',
        ' TV_MILESTONE_V1_LABEL: "V1"',
        ' TV_MILESTONE_4_LABEL: "4"',
        ' TV_MILESTONE_V2_LABEL: "V2"',
        "",
        " # ── 共用提示标题 ────────────────────────────────────────────────────────────────",
        ' TV_TOOLTIP_CONDITIONS_HEADER: "达成条件"',
        ' TV_TOOLTIP_REWARDS_HEADER: "里程碑奖励"',
        "",
    ]
    for path in PATHS:
        pid = path["id"].upper()
        zh_name = ZH.get(path["id"], path["name_en"])
        lines += [
            f" # ── {zh_name} ──────────────────────────────────────────────────────────────────",
            f' TV_{pid}_TITLE: "{zh_name}"',
            f' TV_{pid}_DESCRIPTION: "TODO"',
            f' TV_{pid}_FLAVOR: "TODO"',
            "",
        ]
        for m in path["milestones"]:
            n = m["n"]
            lines += [
                f' TV_{pid}_M{n}_TITLE: "TODO"',
                f' TV_{pid}_M{n}_MEANING: "{m["meaning_zh"]}"',
                f' TV_{pid}_M{n}_CONDITIONS: ""',
                f' TV_{pid}_M{n}_REWARDS: ""',
            ]
        lines.append("")

    write_file(
        SRC / "main_menu/localization/simp_chinese/towards_victory_l_simp_chinese.yml",
        "\n".join(lines),
        bom=True,
    )


def gen_gui() -> None:  # noqa: PLR0912 (acceptable complexity for a generator)
    out: list[str] = []

    # ── File header ──────────────────────────────────────────────────────────
    out += [
        "# Towards Victory — Victory Progress Situation Panel",
        "# Generated by scripts/gen_victory_scaffold.py",
        "#",
        "# Verification — Step 2, Reference: cards.gui:1118",
        "#   situation_card_common extends card_common with bg_card_header_01 header.",
        "#   Valid blockoverride targets on card_common:",
        "#     header_size, header_decor_templates, common_header_back_decor,",
        "#     common_header_extra_left, common_header, common_header_extra_right,",
        "#     card_common_bottom_margin, common_bottom_content",
        "#",
        "# GUI file name MUST match the situation identifier: tv_victory_situation",
        "",
    ]

    # ── types block ──────────────────────────────────────────────────────────
    out += [
        "types TVVictoryTypes {",
        "",
        "\t# tv_victory_row — reusable row template for one victory path.",
        "\t# Parameterised via block overrides per instance (6 total):",
        "\t#   row_progress_value   : progressbar value expression",
        "\t#   row_progress_style   : progressbar texture template",
        "\t#   path_icon_circle     : large victory-type icon circle (44x44)",
        "\t#   milestone_1_circle   : M1 circle (30x30)",
        "\t#   milestone_2_circle   : M2 circle (30x30)",
        "\t#   milestone_v1_circle  : V1 Short-term Victory circle (34x34, special)",
        "\t#   milestone_4_circle   : M4 circle (30x30)",
        "\t#   milestone_v2_circle  : V2 Long-term Victory circle (38x38, special)",
        "\ttype tv_victory_row = widget {",
        "\t\tsize = { -1 52 }",
        "",
        "\t\t# Subtle row background for visual separation between paths",
        "\t\tbackground = {",
        '\t\t\ttexture = "gfx/interface/component_tiles/tile_light.dds"',
        "\t\t\talpha = 0.08",
        "\t\t\tspriteType = CorneredStretched",
        "\t\t\tspriteborder = { 4 4 }",
        "\t\t}",
        "",
        "\t\t# ── Layer 1: progress bar (rendered first — behind marker circles) ──────",
        "\t\tprogressbar = {",
        "\t\t\tparentanchor = vcenter",
        "\t\t\tsize = { 100% 14 }",
        '\t\t\tblock "row_progress_value" { value = 0 }',
        '\t\t\tblock "row_progress_style" { using = progress_bar_blue_alt }',
        "\t\t}",
        "",
        "\t\t# ── Layer 2: icon + milestone circles (rendered on top of bar) ──────────",
        "\t\thbox = {",
        "\t\t\tsize = { -1 100% }",
        "\t\t\tlayoutpolicy_horizontal = expanding",
        "",
        "\t\t\t# Victory-type icon (44x44, overlaps bar start)",
        '\t\t\tblock "path_icon_circle" { }',
        "\t\t\texpand = { }",
        "\t\t\t# Milestone 1 (30x30, ~20% of bar width)",
        '\t\t\tblock "milestone_1_circle" { }',
        "\t\t\texpand = { }",
        "\t\t\t# Milestone 2 (30x30, ~40%)",
        '\t\t\tblock "milestone_2_circle" { }',
        "\t\t\texpand = { }",
        "\t\t\t# V1 Short-term Victory (34x34, ~60%, special gold frame)",
        '\t\t\tblock "milestone_v1_circle" { }',
        "\t\t\texpand = { }",
        "\t\t\t# Milestone 4 (30x30, ~80%)",
        '\t\t\tblock "milestone_4_circle" { }',
        "\t\t\texpand = { }",
        "\t\t\t# V2 Long-term Victory (38x38, ~100%, special gold frame)",
        '\t\t\tblock "milestone_v2_circle" { }',
        "\t\t}",
        "\t}",
        "}",
        "",
    ]

    # ── Icon tooltip templates (6) ────────────────────────────────────────────
    out += [
        "# ══════════════════════════════════════════════════════════════════════════",
        "# VICTORY TYPE ICON TOOLTIPS (6 total)",
        "# Shows: short description of the victory path + flavor text.",
        "# ══════════════════════════════════════════════════════════════════════════",
        "",
    ]
    for path in PATHS:
        pid = path["id"]
        PID = pid.upper()
        out += [
            f"template tv_{pid}_icon_tooltip {{",
            f"\tContextualTooltipType = {{",
            f'\t\tblockoverride "title_text" {{ text = "TV_{PID}_TITLE" }}',
            f'\t\tblockoverride "title_icon_texture" {{',
            f'\t\t\ttexture = "gfx/interface/icons/situations/{path["icon"]}.dds"',
            f'\t\t}}',
            f'\t\tblockoverride "concept_link" {{ text = "[situation|E]" }}',
            f'\t\tblockoverride "tooltip_content" {{',
            f'\t\t\tTooltipTextBlock = {{',
            f'\t\t\t\tblockoverride "text" {{ text = "TV_{PID}_DESCRIPTION" }}',
            f'\t\t\t}}',
            f'\t\t\tTooltipFlavorTextBlock = {{',
            f'\t\t\t\tblockoverride "text" {{ text = "TV_{PID}_FLAVOR" }}',
            f'\t\t\t}}',
            f'\t\t}}',
            f'\t}}',
            f'}}',
            f'',
        ]

    # ── Milestone tooltip templates (30) ──────────────────────────────────────
    out += [
        "# ══════════════════════════════════════════════════════════════════════════",
        "# MILESTONE TOOLTIPS (30 total — 6 paths x 5 milestones)",
        "# 3-panel design:",
        "#   Panel 1: what this milestone position means (plain description)",
        "#   Panel 2: conditions to reach it (standard requirements list display)",
        "#   Panel 3: rewards upon achievement (standard modifier pair display)",
        "# ══════════════════════════════════════════════════════════════════════════",
        "",
    ]
    for path in PATHS:
        pid = path["id"]
        PID = pid.upper()
        out.append(f"# ── {path['name_en']} milestones ──────────────────────────────────────────────")
        out.append("")
        for m in path["milestones"]:
            n = m["n"]
            out += [
                f"template tv_{pid}_milestone_{n}_tooltip {{",
                f"\tContextualTooltipType = {{",
                f'\t\tblockoverride "title_text" {{ text = "TV_{PID}_M{n}_TITLE" }}',
                f'\t\tblockoverride "tooltip_content" {{',
                f'',
                f'\t\t\t# ── Panel 1: what this milestone position means ────────────────────',
                f'\t\t\tTooltipTextBlock = {{',
                f'\t\t\t\tblockoverride "text" {{ text = "TV_{PID}_M{n}_MEANING" }}',
                f'\t\t\t}}',
                f'',
                f'\t\t\t# Visual separator between panels',
                f'\t\t\twidget = {{ size = {{ -1 1 }} background = {{ using = color_gold  alpha = 0.3 }} }}',
                f'',
                f'\t\t\t# ── Panel 2: conditions to reach this milestone ────────────────────',
                f'\t\t\t# Standard requirements list — green/red coloring from engine evaluation.',
                f'\t\t\t# textcontext expression requires Step 2/3 verification once trigger is defined.',
                f'\t\t\t# Candidate (Country.MakeScope verified; Step 3 ref: western_schism.gui:43): "[Country.MakeScope.GetScript(\'tv_{pid}_milestone_{n}\')]"',
                f'\t\t\tTooltipScrolledRequirementsList = {{',
                f'\t\t\t\tblockoverride "block_title" {{ text = "TV_TOOLTIP_CONDITIONS_HEADER" }}',
                f'\t\t\t\ttextcontext = "TV_{PID}_M{n}_CONDITIONS"',
                f'\t\t\t}}',
                f'',
                f'\t\t\t# Visual separator between panels',
                f'\t\t\twidget = {{ size = {{ -1 1 }} background = {{ using = color_gold  alpha = 0.3 }} }}',
                f'',
                f'\t\t\t# ── Panel 3: rewards upon reaching this milestone ──────────────────',
                f'\t\t\t# Standard modifier pair list.',
                f'\t\t\t# Update textcontext once tv_{pid}_m{n}_bonus modifier is defined.',
                f'\t\t\tTooltipStringPairList = {{',
                f'\t\t\t\tblockoverride "block_title" {{ text = "TV_TOOLTIP_REWARDS_HEADER" }}',
                f'\t\t\t\ttextcontext = "TV_{PID}_M{n}_REWARDS"',
                f'\t\t\t}}',
                f'',
                f'\t\t}}',
                f'\t}}',
                f'}}',
                f'',
            ]

    # ── Main situation panel ──────────────────────────────────────────────────
    out += [
        "# ══════════════════════════════════════════════════════════════════════════",
        "# MAIN SITUATION PANEL",
        "# situation_card_common root widget — displays when player opens this situation.",
        "# Header title is automatically sourced from tv_victory_situation loc key.",
        "# ══════════════════════════════════════════════════════════════════════════",
        "",
        "situation_card_common = {",
        "",
        '\tblockoverride "common_bottom_content" {',
        "\t\tvbox = {",
        "\t\t\tlayoutpolicy_horizontal = expanding",
        "\t\t\tspacing = 6",
        "\t\t\tmargin = { 8 8 }",
        "",
    ]

    for path in PATHS:
        pid = path["id"]
        PID = pid.upper()
        pv = path["progress_var"]
        i = "\t\t\t"  # indent for inside vbox

        out += [
            f"{i}# ── {path['name_en']} row ────────────────────────────────────────────────────",
            f"{i}tv_victory_row = {{",
            f'{i}\tblockoverride "row_progress_value" {{',
            # Verification — Step 3: Country.MakeScope is correct in situation panels;
            # GetPlayerCountry does not exist. Reference: western_schism.gui:43
            f"{i}\t\tvalue = \"[Country.MakeScope.GetVariable('{pv}').GetValue]\"",
            f"{i}\t}}",
            f'{i}\tblockoverride "row_progress_style" {{',
            f"{i}\t\tusing = {path['bar_style']}",
            f"{i}\t}}",
            f'{i}\tblockoverride "path_icon_circle" {{',
            f"{i}\t\twidget = {{",
            f"{i}\t\t\tsize = {{ 44 44 }}",
            f"{i}\t\t\tparentanchor = vcenter",
            f"{i}\t\t\tusing = bg_circle_piechart_big",
            f"{i}\t\t\ticon = {{",
            f"{i}\t\t\t\tparentanchor = center",
            f"{i}\t\t\t\tsize = {{ 70% 70% }}",
            f"{i}\t\t\t\ttexture = \"gfx/interface/icons/situations/{path['icon']}.dds\"",
            f"{i}\t\t\t}}",
            f"{i}\t\t\ttooltipwidget = {{ using = tv_{pid}_icon_tooltip }}",
            f"{i}\t\t}}",
            f"{i}\t}}",
        ]

        for m in path["milestones"]:
            out += _milestone_circle_block(path, m, f"{i}\t")

        out += [
            f"{i}}}",
            "",
        ]

    out += [
        "\t\t}",
        "\t}",
        "}",
        "",
    ]

    write_file(
        SRC / "in_game/gui/panels/situation/tv_victory_situation.gui",
        "\n".join(out),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Towards Victory — generating scaffold files...")
    print()
    gen_situation()
    gen_triggers()
    gen_effects()
    gen_modifiers()
    gen_on_action()
    gen_localization_en()
    gen_localization_zh()
    gen_gui()
    print()
    print("Done. Next steps:")
    print("  1. conda run -n eu5 python scripts/validate.py --changed")
    print("  2. Perform Step 2/3 verification for the 5 flagged TODOs in tv_victory_situation.gui")
    print("  3. Fill in milestone trigger content in towards_victory_triggers.txt")


if __name__ == "__main__":
    main()
