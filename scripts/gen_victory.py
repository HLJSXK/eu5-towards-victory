#!/usr/bin/env python3
r"""Generate all Towards Victory game files from data/victory_paths.yaml.

Usage:
    C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\gen_victory.py        # write files
    C:\Users\Hades\anaconda3\envs\eu5\python.exe scripts\gen_victory.py --dry  # preview only

1对1原则: Each YAML field maps to one piece of output. Complex EU5 script bodies
are stored verbatim in the YAML; this generator inserts them unchanged. It is a
template filler, not a code reasoner.

Generated files (do NOT hand-edit):
  src/in_game/common/scripted_triggers/towards_victory_triggers.txt
  src/in_game/common/scripted_effects/towards_victory_effects.txt
  src/in_game/common/static_modifiers/towards_victory_modifiers.txt
  src/in_game/common/situations/towards_victory_situations.txt
  src/in_game/common/on_action/towards_victory_yearly.txt
  src/in_game/events/towards_victory_{id}_events.txt  (×6)
  src/main_menu/localization/english/towards_victory_l_english.yml
  src/main_menu/localization/simp_chinese/towards_victory_l_simp_chinese.yml
"""
import sys
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: conda install -n eu5 pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent.parent
MANAGED_SANDBOX_PYTHON = r"C:\Users\Hades\anaconda3\envs\eu5\python.exe"
SRC = ROOT / "src"
DATA_YAML = ROOT / "data" / "victory_paths.yaml"
ESTABLISHMENT_YAML = ROOT / "data" / "io_establishment.yaml"
IO_LEADERS_YAML = ROOT / "data" / "io_leaders.yaml"
PULSE_REGISTRY_YAML = ROOT / "data" / "pulse_registry.yaml"

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def indent(text: str, n: int = 1) -> str:
    """Prepend n tabs to every non-empty line."""
    prefix = "\t" * n
    lines = text.rstrip("\n").split("\n")
    return "\n".join(prefix + ln if ln.strip() else ln for ln in lines)


def write_file(path: Path, content: str, dry: bool) -> None:
    """Write UTF-8 BOM file, or print to stdout in dry mode."""
    if dry:
        print(f"\n{'='*72}")
        print(f"=== {path.relative_to(ROOT)}")
        print(f"{'='*72}")
        print(content[:2000])
        if len(content) > 2000:
            print(f"... [{len(content)-2000} more chars]")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8-sig")
        print(f"  wrote {path.relative_to(ROOT)}")


def reward_options(milestone: dict) -> list[dict]:
    """Return the three reward options for a milestone."""
    options = milestone["reward_options"]
    if len(options) != 3:
        raise ValueError(f"Milestone {milestone.get('n')} must define exactly 3 reward_options")
    return options


def reward_modifier_id(pid: str, n: int, choice: int) -> str:
    return f"tv_{pid}_m{n}_reward_{choice}_bonus"


COMMON_IO_CHIEF_ROLE_VAR = "tv_io_chief_role"


def monthly_country_pulse_event_delay_days(data: dict) -> int:
    return int(data.get("_pulse_settings", {}).get("monthly_country_pulse_event_delay_days", 1))


def monthly_country_pulse_event(data: dict, event_id: str) -> str:
    delay = monthly_country_pulse_event_delay_days(data)
    return f"trigger_event_non_silently = {{ id = {event_id} days = {delay} }}"


def establishment_step1_event_id(est: dict) -> int:
    return 100 + int(est["event_id"])


def establishment_step2_event_id(est: dict) -> int:
    return 200 + int(est["event_id"])


def establishment_paths(data: dict) -> list[dict]:
    return data.get("_io_establishment", {}).get("paths", [])


def leader_by_id(data: dict) -> dict[str, dict]:
    return {leader["id"]: leader for leader in data.get("_io_leaders", {}).get("ios", [])}


def path_by_id(data: dict) -> dict[str, dict]:
    return {path["id"]: path for path in data["paths"]}


def establishment_by_id(data: dict) -> dict[str, dict]:
    return {path["id"]: path for path in establishment_paths(data)}


def establishment_data_for_path(data: dict, pid: str) -> dict | None:
    return establishment_by_id(data).get(pid)


def loc_text(obj: dict, lang: str) -> str:
    return obj["en" if lang == "en" else "zh"]


def _snippet_lines(text: str, level: int = 0) -> list[str]:
    prefix = "\t" * level
    return [prefix + line.rstrip() if line.strip() else "" for line in text.rstrip().splitlines()]


def _ai_creation_requirement_lines(est: dict, level: int) -> list[str]:
    requirement = est.get("ai_creation_requirement_body", "").strip()
    if not requirement:
        return []
    prefix = "\t" * level
    lines = [
        f"{prefix}OR = {{",
        f"{prefix}\tis_ai = no",
    ]
    lines.extend(_snippet_lines(requirement, level + 1))
    lines.append(f"{prefix}}}")
    return lines


def _creation_requirement_lines(est: dict, level: int) -> list[str]:
    requirement = est.get("creation_requirement_body", "").strip()
    if not requirement:
        return []
    return _snippet_lines(requirement, level)


def _leader_extra_effect_lines(leader: dict, key: str, level: int) -> list[str]:
    effect = leader.get(key, "").rstrip()
    if not effect:
        return []
    return _snippet_lines(effect, level)


def _clear_current_leader_role_lines(leader: dict, level: int) -> list[str]:
    prefix = "\t" * level
    title_mod = leader.get("title_modifier", "")
    lines = [
        f"{prefix}if = {{",
        f"{prefix}\tlimit = {{ has_variable = {leader['leader_var']} }}",
        f"{prefix}\tvar:{leader['leader_var']} ?= {{",
        f"{prefix}\t\tremove_variable = {COMMON_IO_CHIEF_ROLE_VAR}",
    ]
    if title_mod:
        lines.append(f"{prefix}\t\tremove_character_modifier = {title_mod}")
    lines.extend([
        f"{prefix}\t}}",
        f"{prefix}}}",
    ])
    return lines


def _set_new_leader_role_lines(leader: dict, level: int, target_scope: str = "scope:target") -> list[str]:
    prefix = "\t" * level
    title_mod = leader.get("title_modifier", "")
    lines = [
        f"{prefix}{target_scope} = {{",
        f"{prefix}\tset_variable = {{ name = {COMMON_IO_CHIEF_ROLE_VAR} value = 1 }}",
    ]
    if title_mod:
        lines.append(f"{prefix}\tadd_character_modifier = {{ modifier = {title_mod} years = -1 mode = add_and_extend }}")
    lines.append(f"{prefix}}}")
    return lines


HEADER = (
    "# @Generated by scripts/gen_victory.py\n"
    "#   Data:    data/victory_paths.yaml + data/io_establishment.yaml + data/io_leaders.yaml + data/pulse_registry.yaml\n"
    "#   Regen:   conda run --no-capture-output -n eu5 python scripts/gen_victory.py\n"
    "# Do not edit directly — modify the data file and re-run the generator.\n"
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. TRIGGERS
# ─────────────────────────────────────────────────────────────────────────────

def gen_triggers(data: dict) -> str:
    lines = [HEADER, ""]
    for path in data["paths"]:
        pid = path["id"]
        PID = pid.upper()
        score_var = path["score_var"]
        lines.append(f"# {'─'*70}")
        lines.append(f"# {PID} VICTORY MILESTONES")
        lines.append(f"# {'─'*70}")
        lines.append("")
        for m in path["milestones"]:
            n = m["n"]
            threshold = m["threshold"]
            lines.append(f"tv_{pid}_milestone_{n} = {{")
            lines.append(f"\tcustom_tooltip = {{")
            lines.append(f"\t\ttext = TV_{PID}_VICTORY_ENABLED_TT")
            lines.append(f"\t\thas_variable = tv_{pid}_victory_enabled")
            lines.append(f"\t}}")
            if threshold > 0:
                lines.append(f"\tcustom_tooltip = {{")
                lines.append(f"\t\ttext = TV_{PID}_M{n}_TRIGGER_DESC")
                lines.append(f"\t\thas_variable = {score_var}")
                lines.append(f"\t\tvar:{score_var} >= {threshold}")
                lines.append(f"\t}}")
            if m.get("extra_trigger_block"):
                lines.append(indent(m["extra_trigger_block"].rstrip(), 1))
            lines.append(f"}}")
        lines.append("")
        lines.append("")
    if establishment_paths(data):
        lines.append("# " + "鈹€"*70)
        lines.append("# IO ESTABLISHMENT")
        lines.append("# " + "鈹€"*70)
        lines.append("")
        for est in establishment_paths(data):
            pid = est["id"]
            PID = pid.upper()
            building = est["headquarters"]["building"]
            build_check_lines = [
                "custom_tooltip = {",
                f"\ttext = TV_{PID}_ESTABLISHMENT_STEP2_REQUIREMENT",
                "\towner ?= scope:actor",
                "\tis_capital = yes",
                f"\tlocation_and_owner_can_build = {{ building_type = {building} }}",
                f"\tNOT = {{ has_building = building_type:{building} }}",
                "\tNOT = {",
                "\t\tany_buildings_in_location = {",
                f"\t\t\tbuilding_type = building_type:{building}",
                "\t\t\tbuilding_levels_under_construction >= 1",
                "\t\t}",
                "\t}",
                "}",
            ]
            lines.append(f"tv_{pid}_establishment_basic_requirement = {{")
            lines.append(indent(est["basic_requirement_body"].rstrip(), 1))
            lines.append("}")
            lines.append("")
            lines.append(f"tv_{pid}_headquarters_can_build_in_location = {{")
            lines.extend(_snippet_lines("\n".join(build_check_lines), 1))
            lines.append("}")
            lines.append("")
            lines.append(f"tv_{pid}_headquarters_can_build_in_capital = {{")
            lines.append("\tcustom_tooltip = {")
            lines.append(f"\t\ttext = TV_{PID}_ESTABLISHMENT_STEP2_REQUIREMENT")
            lines.append("\t\tcapital ?= {")
            lines.append("\t\t\tis_capital = yes")
            lines.append(f"\t\t\tlocation_and_owner_can_build = {{ building_type = {building} }}")
            lines.append(f"\t\t\tNOT = {{ has_building = building_type:{building} }}")
            lines.append("\t\t\tNOT = {")
            lines.append("\t\t\t\tany_buildings_in_location = {")
            lines.append(f"\t\t\t\t\tbuilding_type = building_type:{building}")
            lines.append("\t\t\t\t\tbuilding_levels_under_construction >= 1")
            lines.append("\t\t\t\t}")
            lines.append("\t\t\t}")
            lines.append("\t\t}")
            lines.append("\t}")
            lines.append("}")
            lines.append("")
            lines.append(f"tv_{pid}_establishment_basic_done = {{")
            lines.append("\tcustom_tooltip = {")
            lines.append(f"\t\ttext = TV_{PID}_ESTABLISHMENT_STEP1_DONE_TT")
            lines.append(f"\t\thas_variable = tv_{pid}_establishment_basic_done")
            lines.append("\t}")
            lines.append("}")
            lines.append("")
            lines.append(f"tv_{pid}_establishment_headquarters_done = {{")
            lines.append("\tcustom_tooltip = {")
            lines.append(f"\t\ttext = TV_{PID}_ESTABLISHMENT_STEP2_DONE_TT")
            lines.append(f"\t\tcapital ?= {{ has_building_with_at_least_one_level = {building} }}")
            lines.append("\t}")
            lines.append("}")
            lines.append("")
            lines.append(f"tv_{pid}_establishment_ready_to_appoint = {{")
            lines.append(f"\ttv_{pid}_establishment_basic_done = yes")
            lines.append(f"\ttv_{pid}_establishment_headquarters_done = yes")
            lines.append(f"\tNOT = {{ has_variable = tv_{pid}_victory_enabled }}")
            lines.extend(_creation_requirement_lines(est, 1))
            lines.extend(_ai_creation_requirement_lines(est, 1))
            lines.append("}")
            lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 2. EFFECTS
# ─────────────────────────────────────────────────────────────────────────────

def gen_establishment_effects(data: dict) -> str:
    est_paths = establishment_paths(data)
    if not est_paths:
        return ""

    leaders = leader_by_id(data)
    lines: list[str] = []

    lines.append("# " + "鈺?"*71)
    lines.append("# SECTION: IO ESTABLISHMENT CREATE HELPERS")
    lines.append("# " + "鈺?"*71)
    lines.append("")

    lines.extend([
        "tv_arts_exhibition_create_effect = {",
        "\tsave_scope_as = tv_arts_exhibition_founder",
        "\tif = {",
        "\t\tlimit = {",
        "\t\t\tcustom_tooltip = {",
        "\t\t\t\ttext = TV_HAS_VARIABLE_NOT_SET_TT",
        "\t\t\t\tNOT = { has_variable = tv_arts_exhibition_member }",
        "\t\t\t}",
        "\t\t}",
        "\t\tset_variable = { name = tv_arts_exhibition_member value = 1 }",
        "\t}",
        "\tif = {",
        "\t\tlimit = {",
        "\t\t\tNOT = {",
        "\t\t\t\tany_international_organizations_member_of = {",
        "\t\t\t\t\tinternational_organization_type = international_organization_type:tv_arts_exhibition",
        "\t\t\t\t\tleader_country ?= scope:tv_arts_exhibition_founder",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t}",
        "\t\tcreate_international_organization = {",
        "\t\t\ttype = international_organization_type:tv_arts_exhibition",
        "\t\t\tadd_country_to_international_organization = prev",
        "\t\t\tset_leader_country = prev",
        "\t\t}",
        "\t}",
        "}",
        "",
        "tv_academy_of_sciences_create_effect = {",
        "\tsave_scope_as = tv_academy_of_sciences_founder",
        "\tif = {",
        "\t\tlimit = {",
        "\t\t\tcustom_tooltip = {",
        "\t\t\t\ttext = TV_HAS_VARIABLE_NOT_SET_TT",
        "\t\t\t\tNOT = { has_variable = tv_academy_io_member }",
        "\t\t\t}",
        "\t\t}",
        "\t\tset_variable = { name = tv_academy_io_member value = 1 }",
        "\t\tset_variable = { name = tv_research_phase value = 0 }",
        "\t\tset_variable = { name = tv_research_interest value = 0 }",
        "\t\tset_variable = { name = tv_research_b_done value = 0 }",
        "\t\tset_variable = { name = tv_rm_subprocess_a value = 0 }",
        "\t\tset_variable = { name = tv_rm_subprocess_b value = 0 }",
        "\t\tset_variable = { name = tv_rm_subprocess_c value = 0 }",
        "\t\tset_variable = { name = tv_rm_subprocess_d_ready value = 0 }",
        "\t\tset_variable = { name = tv_med_progress value = 0 }",
        "\t\tset_variable = { name = tv_med_disp_adm value = 0 }",
        "\t\tset_variable = { name = tv_med_disp_dip value = 0 }",
        "\t\tset_variable = { name = tv_med_disp_mil value = 0 }",
        "\t\tset_variable = { name = tv_academy_philosophy_current value = 1 }",
        "\t\tset_variable = { name = tv_academy_philosophy_phase value = 0 }",
        "\t\tset_variable = { name = tv_academy_debate_initial_progress_pending value = 1 }",
        "\t\ttv_academy_philosophy_initialize_timeline_effect = yes",
        "\t}",
        "\tif = {",
        "\t\tlimit = {",
        "\t\t\tNOT = {",
        "\t\t\t\tany_international_organizations_member_of = {",
        "\t\t\t\t\tinternational_organization_type = international_organization_type:tv_academy_of_sciences",
        "\t\t\t\t\tleader_country ?= scope:tv_academy_of_sciences_founder",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t}",
        "\t\tcreate_international_organization = {",
        "\t\t\ttype = international_organization_type:tv_academy_of_sciences",
        "\t\t\thidden_effect = {",
        "\t\t\t\tadd_country_to_international_organization = prev",
        "\t\t\t\tset_leader_country = prev",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "\tif = {",
        "\t\tlimit = { has_variable = tv_academy_debate_initial_progress_pending }",
        "\t\ttv_academy_debate_set_local_progress_effect = { value = 50 }",
        "\t\tremove_variable = tv_academy_debate_initial_progress_pending",
        "\t}",
        "}",
        "",
    ])

    lines.append("# " + "鈺?"*71)
    lines.append("# SECTION: IO ESTABLISHMENT ROUTINE")
    lines.append("# " + "鈺?"*71)
    lines.append("")

    lines.append("tv_io_establishment_monthly_pulse_effect = {")
    lines.append("\ttv_io_establishment_mark_basic_requirements_effect = yes")
    lines.append("\ttv_io_establishment_refresh_headquarters_cache_effect = yes")
    lines.append("}")
    lines.append("")

    lines.append("tv_io_establishment_mark_basic_requirements_effect = {")
    for est in est_paths:
        pid = est["id"]
        lines.append("\tif = {")
        lines.append("\t\tlimit = {")
        lines.append(f"\t\t\tNOT = {{ has_variable = tv_{pid}_establishment_basic_done }}")
        lines.append(f"\t\t\tNOT = {{ has_variable = tv_{pid}_victory_enabled }}")
        lines.append("\t\t}")
        if pid == "conquest":
            lines.append("\t\ttv_update_conquest_score_effect = yes")
        lines.append("\t\tif = {")
        lines.append(f"\t\t\tlimit = {{ tv_{pid}_establishment_basic_requirement = yes }}")
        lines.append(f"\t\t\tset_variable = {{ name = tv_{pid}_establishment_basic_done value = 1 }}")
        lines.append("\t\t\tif = {")
        lines.append("\t\t\t\tlimit = { is_ai = no }")
        lines.append(f"\t\t\t\t{monthly_country_pulse_event(data, f'tv_io_establishment.{establishment_step1_event_id(est)}')}")
        lines.append("\t\t\t}")
        lines.append("\t\t}")
        lines.append("\t}")
    lines.append("}")
    lines.append("")

    lines.append("tv_io_establishment_refresh_headquarters_cache_effect = {")
    for est in est_paths:
        pid = est["id"]
        lines.append("\tif = {")
        lines.append(f"\t\tlimit = {{ tv_{pid}_establishment_headquarters_done = yes }}")
        lines.append(f"\t\tset_variable = {{ name = tv_{pid}_establishment_headquarters_done value = 1 }}")
        lines.append("\t}")
        lines.append("\telse = {")
        lines.append(f"\t\tremove_variable = tv_{pid}_establishment_headquarters_done")
        lines.append("\t}")
    lines.append("}")
    lines.append("")

    lines.append("tv_io_establishment_validate_enabled_routes_on_game_load_effect = {")
    lines.append("\tevery_country = {")
    lines.append("\t\tlimit = {")
    lines.append("\t\t\tOR = {")
    for est in est_paths:
        pid = est["id"]
        lines.append(f"\t\t\t\thas_variable = tv_{pid}_victory_enabled")
    lines.append("\t\t\t}")
    lines.append("\t\t}")
    for est in est_paths:
        pid = est["id"]
        leader = leaders[est["leader_id"]]
        io_type = leader["io_type"]
        lines.append("\t\tif = {")
        lines.append("\t\t\tlimit = {")
        lines.append(f"\t\t\t\thas_variable = tv_{pid}_victory_enabled")
        lines.append("\t\t\t\tNOT = {")
        lines.append("\t\t\t\t\tany_international_organizations_member_of = {")
        lines.append(f"\t\t\t\t\t\tinternational_organization_type = international_organization_type:{io_type}")
        lines.append("\t\t\t\t\t}")
        lines.append("\t\t\t\t}")
        lines.append("\t\t\t}")
        lines.append(f"\t\t\tremove_variable = tv_{pid}_victory_enabled")
        lines.append("\t\t}")
    lines.append("\t\ttv_update_all_progress_pct_effect = yes")
    lines.append("\t}")
    lines.append("}")
    lines.append("")

    for est in est_paths:
        pid = est["id"]
        leader = leaders[est["leader_id"]]
        lines.append(f"tv_establish_{pid}_io_effect = {{")
        lines.append("\tif = {")
        lines.append("\t\tlimit = {")
        lines.append("\t\t\texists = scope:target")
        lines.append("\t\t\tscope:target = { is_alive = yes }")
        lines.append(f"\t\t\ttv_{pid}_establishment_ready_to_appoint = yes")
        lines.append("\t\t}")
        lines.append(f"\t\t{est['create_effect']} = yes")
        lines.extend(_clear_current_leader_role_lines(leader, 2))
        lines.append(f"\t\tset_variable = {{ name = {leader['leader_var']} value = scope:target }}")
        lines.extend(_leader_extra_effect_lines(leader, "on_appoint_effect", 2))
        lines.extend(_set_new_leader_role_lines(leader, 2))
        lines.append(f"\t\tset_variable = {{ name = tv_{pid}_victory_enabled value = 1 }}")
        lines.append(f"\t\tset_variable = {{ name = tv_{pid}_establishment_headquarters_done value = 1 }}")
        event_id = "tv_io_establishment." + str(int(est["event_id"]))
        lines.append(f"\t\t{monthly_country_pulse_event(data, event_id)}")
        lines.append(f"\t\ttv_check_{pid}_milestones_effect = yes")
        lines.append("\t\ttv_update_all_progress_pct_effect = yes")
        lines.append("\t}")
        lines.append("}")
        lines.append("")

    return "\n".join(lines)


def gen_effects(data: dict) -> str:
    paths = data["paths"]
    lines = [HEADER, ""]

    # Section 1: dispatcher
    lines.append("# " + "═"*71)
    lines.append("# SECTION 1: TOP-LEVEL DISPATCHER")
    lines.append("# " + "═"*71)
    lines.append("")
    lines.append("tv_check_all_milestones_effect = {")
    for p in paths:
        lines.append(f"\ttv_check_{p['id']}_milestones_effect = yes")
    lines.append("}")
    lines.append("")

    # Section 1.5+: score updaters (skip paths with null body)
    for p in paths:
        if not p.get("score_updater_body"):
            continue
        pid = p["id"]
        lines.append("# " + "═"*71)
        lines.append(f"# SECTION: {pid.upper()} SCORE UPDATER")
        lines.append("# " + "═"*71)
        lines.append("")
        lines.append(f"tv_update_{pid}_score_effect = {{")
        lines.append(indent(p["score_updater_body"].rstrip()))
        lines.append("}")
        lines.append("")

    establishment_effects = gen_establishment_effects(data)
    if establishment_effects:
        lines.append(establishment_effects)
        lines.append("")

    # Section 2: milestone checkers
    lines.append("# " + "═"*71)
    lines.append("# SECTION 2: PER-PATH MILESTONE CHECKERS")
    lines.append("# Guards via var:tv_*_milestone < N prevent re-triggering after grant.")
    lines.append("# " + "═"*71)
    lines.append("")
    for p in paths:
        pid = p["id"]
        score_var = p["score_var"]
        lines.append(f"# ── {pid.capitalize()} Victory {'─'*50}")
        lines.append(f"tv_check_{pid}_milestones_effect = {{")
        if p.get("call_updater_in_checker"):
            lines.append(f"\ttv_update_{pid}_score_effect = yes")
        if p.get("score_var_init_in_checker"):
            lines.append(f"\t# Initialise score variable on first call")
            lines.append(f"\tif = {{")
            lines.append(f"\t\tlimit = {{")
            lines.append(f"\t\t\tcustom_tooltip = {{")
            lines.append(f"\t\t\t\ttext = TV_HAS_VARIABLE_NOT_SET_TT")
            lines.append(f"\t\t\t\tNOT = {{ has_variable = {score_var} }}")
            lines.append(f"\t\t\t}}")
            lines.append(f"\t\t}}")
            lines.append(f"\t\tset_variable = {{ name = {score_var} value = 0 }}")
            lines.append(f"\t}}")
        lines.append(f"\t# Initialise on first call (guards against missing variable)")
        lines.append(f"\tif = {{")
        lines.append(f"\t\tlimit = {{")
        lines.append(f"\t\t\tcustom_tooltip = {{")
        lines.append(f"\t\t\t\ttext = TV_HAS_VARIABLE_NOT_SET_TT")
        lines.append(f"\t\t\t\tNOT = {{ has_variable = tv_{pid}_milestone }}")
        lines.append(f"\t\t\t}}")
        lines.append(f"\t\t}}")
        lines.append(f"\t\tset_variable = {{ name = tv_{pid}_milestone value = 0 }}")
        lines.append(f"\t}}")
        for m in p["milestones"]:
            n = m["n"]
            lines.append(f"\tif = {{")
            lines.append(f"\t\tlimit = {{")
            lines.append(f"\t\t\tvar:tv_{pid}_milestone < {n}")
            lines.append(f"\t\t\ttv_{pid}_milestone_{n} = yes")
            lines.append(f"\t\t}}")
            lines.append(f"\t\tset_variable = {{ name = tv_{pid}_milestone value = {n} }}")
            lines.append(f"\t\t{monthly_country_pulse_event(data, f'tv_{pid}.{n}')}")
            lines.append(f"\t}}")
        lines.append("}")
        lines.append("")

    # Section 3: progress pct
    lines.append("# " + "═"*71)
    lines.append("# SECTION 3: PROGRESS PERCENTAGE UPDATER")
    lines.append("# Stores tv_*_progress_pct in [0, 100] for each path (used by GUI bars).")
    lines.append("# " + "═"*71)
    lines.append("")
    lines.append("tv_update_all_progress_pct_effect = {")
    for p in paths:
        pid = p["id"]
        lines.append(f"\tset_variable = {{ name = tv_{pid}_progress_pct value = 0 }}")
        if p.get("progress_pct_body"):
            lines.append(f"\tif = {{")
            lines.append(f"\t\tlimit = {{ has_variable = tv_{pid}_victory_enabled }}")
            lines.append(indent(p["progress_pct_body"].rstrip(), 2))
            lines.append(f"\t}}")
            lines.append("")
    lines.append("}")
    lines.append("")

    # Section 4: unlock and reward selection effects
    lines.append("# " + "═"*71)
    lines.append("# SECTION 4: MILESTONE UNLOCK AND REWARD SELECTION EFFECTS")
    lines.append("# Events call tv_unlock_* for non-modifier side effects only.")
    lines.append("# Generic actions call tv_select_*_reward_effect; removal is hidden, current grant is visible.")
    lines.append("# " + "═"*71)
    lines.append("")
    for p in paths:
        pid = p["id"]
        lines.append(f"# {pid.capitalize()} Victory")
        for m in p["milestones"]:
            n = m["n"]
            choice_var = f"tv_{pid}_m{n}_reward_choice"
            lines.append(f"tv_unlock_{pid}_milestone_{n} = {{")
            if m.get("unlock_body"):
                lines.append(indent(m["unlock_body"].rstrip()))
            else:
                lines.append("\t# No unlock-only side effects for this milestone.")
            lines.append(f"}}")
            lines.append("")
            lines.append(f"tv_select_{pid}_m{n}_reward_effect = {{")
            lines.append(f"\tif = {{")
            lines.append(f"\t\tlimit = {{")
            lines.append(f"\t\t\tcustom_tooltip = {{")
            lines.append(f"\t\t\t\ttext = TV_HAS_{pid.upper()}_MILESTONE_TT")
            lines.append(f"\t\t\t\thas_variable = tv_{pid}_milestone")
            lines.append(f"\t\t\t}}")
            lines.append(f"\t\t\tvar:tv_{pid}_milestone ?= {{ this >= {n} }}")
            lines.append(f"\t\t\tNOT = {{ var:{choice_var} ?= $choice$ }}")
            lines.append(f"\t\t}}")
            lines.append(f"\t\thidden_effect = {{")
            for choice in range(1, 4):
                lines.append(f"\t\t\tremove_country_modifier = {reward_modifier_id(pid, n, choice)}")
            lines.append(f"\t\t}}")
            lines.append(f"\t\tset_variable = {{ name = {choice_var} value = $choice$ }}")
            for choice in range(1, 4):
                branch = "if" if choice == 1 else "else_if"
                lines.append(f"\t\t{branch} = {{")
                lines.append(f"\t\t\tlimit = {{ var:{choice_var} = {choice} }}")
                lines.append(f"\t\t\tadd_country_modifier = {{ modifier = {reward_modifier_id(pid, n, choice)} days = -1 }}")
                lines.append(f"\t\t}}")
            lines.append(f"\t}}")
            lines.append(f"}}")
            lines.append("")
        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 3. MODIFIERS
# ─────────────────────────────────────────────────────────────────────────────

def gen_modifiers(data: dict) -> str:
    lines = [HEADER, ""]
    for path in data["paths"]:
        pid = path["id"]
        lines.append(f"# {'─'*70}")
        lines.append(f"# {pid.upper()} VICTORY MODIFIERS")
        lines.append(f"# {'─'*70}")
        lines.append("")
        for m in path["milestones"]:
            n = m["n"]
            for choice, reward in enumerate(reward_options(m), start=1):
                lines.append(f"{reward_modifier_id(pid, n, choice)} = {{")
                for key, val in reward["modifier"].items():
                    lines.append(f"\t{key} = {val}")
                lines.append("}")
                lines.append("")
        lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 4. SITUATIONS (static template)
# ─────────────────────────────────────────────────────────────────────────────

SITUATIONS_TEMPLATE = """\
{header}

tv_victory_situation = {{
\tmonthly_spawn_chance = monthly_spawn_chance_unique

\tcan_start = {{
\t\talways = yes
\t}}

\tcan_end = {{
\t\talways = no    # Permanent situation — never ends naturally
\t}}

\tvisible = {{
\t\talways = yes
\t}}

\ton_start = {{
\t\t# Initialise the AI yearly pulse counter on the situation scope
\t\tset_variable = {{ name = tv_ai_pulse_counter value = 0 }}
\t\t# Full initial scan of every country -- seeds per-path progress variables for leaderboard
\t\tevery_country = {{
\t\t\tif = {{
\t\t\t\tlimit = {{ NOT = {{ has_variable = tv_victory_selected_path }} }}
\t\t\t\tset_variable = {{ name = tv_victory_selected_path value = 0 }}
\t\t\t}}
\t\t\ttv_check_all_milestones_effect = yes
\t\t\ttv_update_all_progress_pct_effect = yes
\t\t}}
\t\t# Build initial leaderboard ranking immediately
\t\ttv_update_leaderboard_effect = yes
\t}}

\ton_monthly = {{
\t\thidden_effect = {{
\t\t\t# ── PLAYER MILESTONE CHECKS (every month) ────────────────────────────────
\t\t\tevery_country = {{
\t\t\t\tlimit = {{
\t\t\t\t\tis_ai = no
\t\t\t\t}}
\t\t\t\ttv_check_all_milestones_effect = yes
\t\t\t\ttv_update_all_progress_pct_effect = yes
\t\t\t}}

\t\t\t# ── AI MILESTONE CHECKS (every 12 months, via counter) ────────────────────
\t\t\tchange_variable = {{ name = tv_ai_pulse_counter add = 1 }}
\t\t\tif = {{
\t\t\t\tlimit = {{ var:tv_ai_pulse_counter >= 12 }}
\t\t\t\tset_variable = {{ name = tv_ai_pulse_counter value = 0 }}
\t\t\t\t# Yearly prosperity score update for ALL countries (expensive every_owned_location iteration)
\t\t\t\tevery_country = {{
\t\t\t\t\ttv_update_prosperity_score_effect = yes
\t\t\t\t}}
\t\t\t\tevery_country = {{
\t\t\t\t\tlimit = {{
\t\t\t\t\t\tis_ai = yes
\t\t\t\t\t}}
\t\t\t\t\ttv_check_all_milestones_effect = yes
\t\t\t\t\ttv_update_all_progress_pct_effect = yes
\t\t\t\t}}
\t\t\t}}
\t\t}}
\t}}

\ton_ended = {{
\t\t# Should never fire — tv_victory_situation is permanent
\t}}
}}

tv_academy_world_debate_situation = {{
\tmonthly_spawn_chance = monthly_spawn_chance_unique

\tcan_start = {{
\t\talways = yes
\t}}

\tcan_end = {{
\t\talways = no
\t}}

\tvisible = {{
\t\thas_variable = tv_academy_world_debate_participant
\t}}

\ton_start = {{
\t\ttv_academy_world_debate_initialize_effect = yes
\t}}

\ton_monthly = {{
\t\thidden_effect = {{
\t\t\ttv_academy_world_debate_monthly_effect = yes
\t\t}}
\t}}

\ton_ended = {{
\t}}
}}
"""

def gen_situation(data: dict) -> str:
    return SITUATIONS_TEMPLATE.format(header=HEADER.rstrip())


# ─────────────────────────────────────────────────────────────────────────────
# 5. ON-ACTIONS
# ─────────────────────────────────────────────────────────────────────────────

def gen_on_actions(data: dict) -> str:
    lines = [HEADER, ""]
    lines.append("# Supplemental on_action hooks for Towards Victory")
    lines.append("# Diplomatic and Cultural point accumulation hooks.")
    lines.append("# Parent hook bridge registration lives in tv_pulse_bridges.txt.")
    lines.append("")
    if establishment_paths(data):
        lines.append("tv_io_establishment_monthly_pulse = {")
        lines.append("\teffect = {")
        lines.append("\t\ttv_io_establishment_monthly_pulse_effect = yes")
        lines.append("\t}")
        lines.append("}")
        lines.append("")
        lines.append("# Registered under on_game_load by tv_pulse_bridges.txt.")
        lines.append("tv_io_establishment_save_load_validation = {")
        lines.append("\teffect = {")
        lines.append("\t\thidden_effect = {")
        lines.append("\t\t\ttv_io_establishment_validate_enabled_routes_on_game_load_effect = yes")
        lines.append("\t\t}")
        lines.append("\t}")
        lines.append("}")
        lines.append("")
    for hook in data.get("on_actions", []):
        hook_name = hook["hook"]
        callback = hook.get("callback", f"tv_{hook_name}_callback")
        lines.append(f"# Registered under {hook_name} by tv_pulse_bridges.txt.")
        lines.append(f"{callback} = {{")
        lines.append(f"\teffect = {{")
        lines.append(indent(hook["effect_body"].rstrip(), 2))
        lines.append(f"\t}}")
        lines.append(f"}}")
        lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 6. EVENTS (one file per path)
# ─────────────────────────────────────────────────────────────────────────────

def gen_events(path: dict) -> str:
    pid = path["id"]
    lines = [
        HEADER,
        f"# Towards Victory — {pid.capitalize()} milestone events",
        "",
        f"namespace = tv_{pid}",
        "",
    ]
    for m in path["milestones"]:
        n = m["n"]
        lines.append(f"tv_{pid}.{n} = {{")
        lines.append(f"\ttype = country_event")
        lines.append(f"\ttitle = tv_{pid}.{n}.t")
        lines.append(f"\tdesc = tv_{pid}.{n}.d")
        lines.append(f"\toutcome = neutral")
        lines.append(f"\toption = {{")
        lines.append(f"\t\tname = tv_{pid}.{n}.a")
        lines.append(f"\t\ttv_unlock_{pid}_milestone_{n} = yes")
        lines.append(f"\t}}")
        lines.append(f"}}")
        lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 7. LOCALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def gen_establishment_events(data: dict) -> str:
    lines = [
        HEADER,
        "# Towards Victory IO establishment events",
        "",
        "namespace = tv_io_establishment",
        "",
    ]
    for est in establishment_paths(data):
        pid = est["id"]
        building = est["headquarters"]["building"]
        step1_event_id = establishment_step1_event_id(est)
        step2_event_id = establishment_step2_event_id(est)
        event_id = int(est["event_id"])
        lines.append(f"tv_io_establishment.{step1_event_id} = {{")
        lines.append("\ttype = country_event")
        lines.append(f"\ttitle = tv_io_establishment.{step1_event_id}.t")
        lines.append(f"\tdesc = tv_io_establishment.{step1_event_id}.d")
        lines.append("\toutcome = neutral")
        lines.append("\ttrigger = {")
        lines.append(f"\t\ttv_{pid}_establishment_basic_done = yes")
        lines.append(f"\t\tNOT = {{ tv_{pid}_establishment_headquarters_done = yes }}")
        lines.append(f"\t\tNOT = {{ has_variable = tv_{pid}_victory_enabled }}")
        lines.append("\t}")
        lines.append("\toption = {")
        lines.append(f"\t\tname = tv_io_establishment.{step1_event_id}.a")
        lines.append("\t}")
        lines.append("\toption = {")
        lines.append(f"\t\tname = tv_io_establishment.{step1_event_id}.b")
        lines.append(f"\t\ttrigger = {{ tv_{pid}_headquarters_can_build_in_capital = yes }}")
        lines.append("\t\tif = {")
        lines.append(f"\t\t\tlimit = {{ tv_{pid}_headquarters_can_build_in_capital = yes }}")
        lines.append("\t\t\tcapital ?= {")
        lines.append(f"\t\t\t\tconstruct_building = {{ building_type = building_type:{building} }}")
        lines.append("\t\t\t}")
        lines.append("\t\t}")
        lines.append("\t}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_io_establishment.{step2_event_id} = {{")
        lines.append("\ttype = country_event")
        lines.append(f"\ttitle = tv_io_establishment.{step2_event_id}.t")
        lines.append(f"\tdesc = tv_io_establishment.{step2_event_id}.d")
        lines.append("\toutcome = neutral")
        lines.append("\ttrigger = {")
        lines.append(f"\t\ttv_{pid}_establishment_ready_to_appoint = yes")
        lines.append("\t}")
        lines.append("\toption = {")
        lines.append(f"\t\tname = tv_io_establishment.{step2_event_id}.a")
        lines.append("\t}")
        lines.append("}")
        lines.append("")

        lines.append(f"tv_io_establishment.{event_id} = {{")
        lines.append("\ttype = country_event")
        lines.append(f"\ttitle = tv_io_establishment.{event_id}.t")
        lines.append(f"\tdesc = tv_io_establishment.{event_id}.d")
        lines.append("\toutcome = neutral")
        lines.append("\toption = {")
        lines.append(f"\t\tname = tv_io_establishment.{event_id}.a")
        lines.append("\t}")
        lines.append("}")
        lines.append("")
    return "\n".join(lines)


def gen_localization(data: dict, lang: str) -> str:
    """Generate l_{lang}.yml content. lang is 'en' or 'zh'."""
    shared = data["shared"]
    lines = [
        f"l_{'english' if lang == 'en' else 'simp_chinese'}:",
        "# @Generated by scripts/gen_victory.py",
        "#   Data:    data/victory_paths.yaml + data/io_establishment.yaml + data/io_leaders.yaml",
        "#   Regen:   conda run --no-capture-output -n eu5 python scripts/gen_victory.py",
        "# Do not edit directly — modify the data file and re-run the generator.",
    ]

    def kv(key: str, val: str, version: bool = False) -> str:
        if (
            key.startswith("tv_no_")
            and key.endswith("_headquarters_location_available")
            and not val.startswith("@trigger_no!")
        ):
            val = f"@trigger_no! {val}"
        escaped = val.replace('"', '\\"')
        if version:
            return f' {key}:0 "{escaped}"'
        return f' {key}: "{escaped}"'

    def action_message_loc(action: str, setup: str, log: str) -> None:
        lines.append(kv(f"PERFORM_{action}_ACTION_SETUP", setup))
        lines.append(kv(f"PERFORM_{action}_ACTION_LOG", log))
        lines.append(kv(f"PERFORM_{action}_ACTION_MAP", ""))

    def reward_label(choice: int) -> str:
        if lang == "en":
            return ("I", "II", "III")[choice - 1]
        return ("\u4e00", "\u4e8c", "\u4e09")[choice - 1]

    def reward_name(title: str, choice: int) -> str:
        if lang == "en":
            return f"{title} - Reward {reward_label(choice)}"
        return f"{title} - \u5956\u52b1{reward_label(choice)}"

    # Shared situation keys
    lines.append(" # ── Situation ──────────────────────────────────────────────────────────────")
    lines.append(kv("tv_victory_situation", shared["situation_name"][lang]))
    lines.append(kv("tv_victory_situation_desc", shared["situation_desc"][lang]))
    lines.append(kv("TV_VICTORY_SITUATION_TITLE", shared["situation_title"][lang]))
    lines.append(kv("TV_VICTORY_REWARD_1_LABEL", "I" if lang == "en" else "一"))
    lines.append(kv("TV_VICTORY_REWARD_2_LABEL", "II" if lang == "en" else "二"))
    lines.append(kv("TV_VICTORY_REWARD_3_LABEL", "III" if lang == "en" else "三"))
    lines.append(kv("TV_VICTORY_LOCKED_REWARD", "Locked" if lang == "en" else "未解锁"))
    lines.append("")
    lines.append(" # ── Shared milestone circle labels ─────────────────────────────────────────")
    for n, label in shared["milestone_labels"].items():
        key = "TV_MILESTONE_V1_LABEL" if n == 3 else ("TV_MILESTONE_V2_LABEL" if n == 5 else f"TV_MILESTONE_{n}_LABEL")
        lines.append(kv(key, label))
    lines.append("")
    lines.append(" # ── Shared tooltip section headers ─────────────────────────────────────────")
    lines.append(kv("TV_TOOLTIP_CONDITIONS_HEADER", shared["tooltip_conditions_header"][lang]))
    lines.append(kv("TV_TOOLTIP_REWARDS_HEADER", shared["tooltip_rewards_header"][lang]))

    est_paths = sorted(establishment_paths(data), key=lambda est: int(est.get("order", 0)))
    if est_paths:
        if lang == "en":
            shared_est_loc = {
                "TV_ESTABLISHMENT_STEP1_TITLE": "Step 1: Meet Basic Requirements",
                "TV_ESTABLISHMENT_STEP2_TITLE": "Step 2: Build Organization Headquarters",
                "TV_ESTABLISHMENT_STEP3_TITLE": "Step 3: Appoint Chief",
                "TV_ESTABLISHMENT_APPOINT_CHIEF_BUTTON": "Appoint Chief",
                "TV_ESTABLISHMENT_APPOINT_CHIEF_UNAVAILABLE": "No eligible chief candidate is available.",
                "tv_io_headquarters_price": "Organization Headquarters",
                "MODIFIER_TYPE_NAME_tv_io_headquarters_price_cost_modifier": "$tv_io_headquarters_price$ Cost",
                "MODIFIER_TYPE_DESC_tv_io_headquarters_price_cost_modifier": "Modifies the gold construction cost of $tv_io_headquarters_price$ buildings.",
                "TV_IO_HEADQUARTERS_EVENT_OPTION": "Excellent.",
                "TV_IO_ESTABLISHMENT_GUIDE_PANEL_OPTION": "Open the situation panel.",
                "TV_IO_ESTABLISHMENT_GUIDE_BUILD_OPTION": "Begin construction in the capital.",
                "TV_IO_ESTABLISHMENT_GUIDE_APPOINT_OPTION": "Open the situation panel.",
            }
        else:
            shared_est_loc = {
                "TV_ESTABLISHMENT_STEP1_TITLE": "步骤1：满足基本要求",
                "TV_ESTABLISHMENT_STEP2_TITLE": "步骤2：建造组织首府",
                "TV_ESTABLISHMENT_STEP3_TITLE": "步骤3：任命首席",
                "TV_ESTABLISHMENT_APPOINT_CHIEF_BUTTON": "任命首席",
                "TV_ESTABLISHMENT_APPOINT_CHIEF_UNAVAILABLE": "没有符合条件的首席候选人。",
                "tv_io_headquarters_price": "组织首府",
                "MODIFIER_TYPE_NAME_tv_io_headquarters_price_cost_modifier": "$tv_io_headquarters_price$花费",
                "MODIFIER_TYPE_DESC_tv_io_headquarters_price_cost_modifier": "修正$tv_io_headquarters_price$的金币建设花费。",
                "TV_IO_HEADQUARTERS_EVENT_OPTION": "很好。",
                "TV_IO_ESTABLISHMENT_GUIDE_PANEL_OPTION": "打开局势面板。",
                "TV_IO_ESTABLISHMENT_GUIDE_BUILD_OPTION": "在首都开始建造。",
                "TV_IO_ESTABLISHMENT_GUIDE_APPOINT_OPTION": "打开局势面板。",
            }
        lines.append("")
        lines.append(" # ---- IO establishment ----")
        for key, value in shared_est_loc.items():
            lines.append(kv(key, value))
        for est in est_paths:
            pid = est["id"]
            PID = pid.upper()
            route_name = loc_text(est["route_name"], lang)
            io_name = loc_text(est["io_name"], lang)
            hq = est["headquarters"]
            building = hq["building"]
            building_name = loc_text(hq["name"], lang)
            title = f"Establish {io_name}" if lang == "en" else f"建立{io_name}"
            victory_enabled_tt = (
                f"{route_name} Victory progress is unlocked."
                if lang == "en"
                else f"{route_name}胜利进度已解锁。"
            )
            step1_done = (
                f"Complete the basic requirement for establishing {io_name}."
                if lang == "en"
                else f"完成建立{io_name}的基本要求。"
            )
            step2_done = (
                f"Build {building_name} in the capital."
                if lang == "en"
                else f"在首都建成{building_name}。"
            )
            building_desc = (
                f"The capital headquarters of {io_name}, built to coordinate the realm's {route_name} Victory institutions."
                if lang == "en"
                else f"{io_name}的首都机构，用于统筹国家的{route_name}胜利组织。"
            )
            build_action = f"Build {building_name}" if lang == "en" else f"建造{building_name}"
            build_desc = loc_text(est["loc"]["step2_text"], lang)
            appoint_desc = loc_text(est["loc"]["step3_text"], lang)
            lines.append("")
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_TITLE", title))
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_STEP1_TEXT", loc_text(est["loc"]["step1_text"], lang)))
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_STEP2_TEXT", build_desc))
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_STEP3_TEXT", appoint_desc))
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_STEP1_REQUIREMENT", loc_text(est["loc"]["step1_text"], lang)))
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_STEP2_REQUIREMENT", build_desc))
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_STEP1_DONE_TT", step1_done))
            lines.append(kv(f"TV_{PID}_ESTABLISHMENT_STEP2_DONE_TT", step2_done))
            lines.append(kv(f"TV_{PID}_VICTORY_ENABLED_TT", victory_enabled_tt))
            lines.append(kv(building, building_name))
            lines.append(kv(f"{building}_desc", building_desc))
            lines.append(kv(f"{building}_maintenance", f"{building_name} Maintenance" if lang == "en" else f"{building_name}维护"))
            lines.append(kv(hq["construction_demand"], f"{building_name} Construction" if lang == "en" else f"{building_name}建设"))
            lines.append(kv(f"tv_build_{pid}_headquarters", build_action))
            lines.append(kv(f"tv_build_{pid}_headquarters_desc", build_desc))
            lines.append(kv(f"tv_select_{pid}_headquarters_location", "Select Capital" if lang == "en" else "选择首都"))
            lines.append(kv(
                f"tv_no_{pid}_headquarters_location_available",
                "No valid capital location is available." if lang == "en" else "没有可用的首都地点。",
            ))
            action_message_loc(
                f"tv_build_{pid}_headquarters",
                f"When we begin building {building_name}." if lang == "en" else f"当我们开始建造{building_name}时。",
                f"We began building {building_name}." if lang == "en" else f"我们开始建造{building_name}。",
            )
            lines.append(kv(f"tv_establish_{pid}_io", shared_est_loc["TV_ESTABLISHMENT_APPOINT_CHIEF_BUTTON"]))
            lines.append(kv(f"tv_establish_{pid}_io_desc", appoint_desc))
            action_message_loc(
                f"tv_establish_{pid}_io",
                f"When we appoint the first chief of {io_name}." if lang == "en" else f"当我们任命{io_name}的首任首席时。",
                f"We appointed the first chief of {io_name}." if lang == "en" else f"我们任命了{io_name}的首任首席。",
            )
            event_id = int(est["event_id"])
            step1_event_id = establishment_step1_event_id(est)
            step2_event_id = establishment_step2_event_id(est)
            step1_event_title = (
                f"{route_name} Victory: Headquarters Ready"
                if lang == "en"
                else f"{route_name}胜利：可以建设首府"
            )
            step1_event_desc = (
                f"The basic requirement for {route_name} Victory is complete. Open the Towards Victory situation panel to begin the next step, or start building {building_name} in the capital directly from this event."
                if lang == "en"
                else f"{route_name}胜利的基本要求已经完成。你可以打开\"胜利之路\"局势面板继续下一步，也可以直接通过本事件在首都开始建造{building_name}。"
            )
            step2_event_title = (
                f"{building_name} Completed"
                if lang == "en"
                else f"{building_name}已经建成"
            )
            step2_event_desc = (
                f"{building_name} is complete. Open the Towards Victory situation panel and appoint a chief to establish {io_name}."
                if lang == "en"
                else f"{building_name}已经建成。请打开\"胜利之路\"局势面板，任命首席以建立{io_name}。"
            )
            lines.append(kv(f"tv_io_establishment.{step1_event_id}.t", step1_event_title))
            lines.append(kv(f"tv_io_establishment.{step1_event_id}.d", step1_event_desc))
            lines.append(kv(f"tv_io_establishment.{step1_event_id}.a", shared_est_loc["TV_IO_ESTABLISHMENT_GUIDE_PANEL_OPTION"]))
            lines.append(kv(f"tv_io_establishment.{step1_event_id}.b", shared_est_loc["TV_IO_ESTABLISHMENT_GUIDE_BUILD_OPTION"]))
            lines.append(kv(f"tv_io_establishment.{step2_event_id}.t", step2_event_title))
            lines.append(kv(f"tv_io_establishment.{step2_event_id}.d", step2_event_desc))
            lines.append(kv(f"tv_io_establishment.{step2_event_id}.a", shared_est_loc["TV_IO_ESTABLISHMENT_GUIDE_APPOINT_OPTION"]))
            lines.append(kv(f"tv_io_establishment.{event_id}.t", f"{io_name} Established" if lang == "en" else f"{io_name}已建立"))
            lines.append(kv(f"tv_io_establishment.{event_id}.d", loc_text(est["loc"]["event_desc"], lang)))
            lines.append(kv(f"tv_io_establishment.{event_id}.a", shared_est_loc["TV_IO_HEADQUARTERS_EVENT_OPTION"]))

    for path in data["paths"]:
        pid = path["id"]
        PID = pid.upper()
        ploc = path["loc"]

        lines.append("")
        lines.append(f" # ── {pid.capitalize()} Victory ──────────────────────────────────────────────────────────")
        lines.append(kv(f"TV_{PID}_TAB_LABEL", path["gui"]["tab_label"][lang]))
        lines.append(kv(f"TV_{PID}_TITLE", ploc["title"][lang]))
        lines.append(kv(f"TV_{PID}_DESCRIPTION", ploc["description"][lang]))
        lines.append(kv(f"TV_{PID}_FLAVOR", ploc["flavor"][lang]))
        lines.append(kv(f"TV_{PID}_OVERVIEW_TITLE", ploc["overview_card"]["title"][lang]))
        lines.append(kv(f"TV_{PID}_OVERVIEW_PLAYSTYLE", ploc["overview_card"]["playstyle"][lang]))
        lines.append(kv(f"TV_{PID}_OVERVIEW_FORMULA", ploc["overview_card"]["formula"][lang]))
        lines.append(kv(f"tv_victory_select_path_{pid}", path["gui"]["tab_label"][lang]))
        lines.append(kv(
            f"tv_victory_select_path_{pid}_desc",
            (f"Show the {ploc['title'][lang]} page." if lang == "en" else f"显示{ploc['title'][lang]}页面。"),
        ))
        action_message_loc(
            f"tv_victory_select_path_{pid}",
            "When we switch victory path pages." if lang == "en" else "当我们切换胜利之路页面时。",
            "We switched the victory path page." if lang == "en" else "我们切换了胜利之路页面。",
        )
        lines.append("")
        for m in path["milestones"]:
            n = m["n"]
            mloc = m["loc"]
            lines.append(kv(f"TV_{PID}_M{n}_TITLE", mloc["title"][lang]))
            lines.append(kv(f"TV_{PID}_M{n}_MEANING", mloc["meaning"][lang]))
            lines.append(kv(f"TV_{PID}_M{n}_TRIGGER_DESC", mloc["trigger_desc"][lang]))
            if mloc.get("extra_trigger_desc") and mloc["extra_trigger_desc"].get(lang):
                lines.append(kv(f"TV_{PID}_M{n}_EXTRA_TRIGGER_DESC", mloc["extra_trigger_desc"][lang]))
            for choice in range(1, 4):
                modifier = reward_modifier_id(pid, n, choice)
                reward_title = reward_name(mloc["title"][lang], choice)
                reward_desc = (
                    f"Select reward {reward_label(choice)}: [GetModifier('{modifier}').GetDesc]"
                    if lang == "en"
                    else f"\u9009\u62e9\u5956\u52b1{reward_label(choice)}\uff1a[GetModifier('{modifier}').GetDesc]"
                )
                lines.append(kv(f"tv_victory_select_{pid}_m{n}_reward_{choice}", reward_title))
                lines.append(kv(f"tv_victory_select_{pid}_m{n}_reward_{choice}_desc", reward_desc))
                action_message_loc(
                    f"tv_victory_select_{pid}_m{n}_reward_{choice}",
                    "When we select a victory milestone reward."
                    if lang == "en"
                    else "当我们选择胜利里程碑奖励时。",
                    "We selected a victory milestone reward."
                    if lang == "en"
                    else "我们选择了一项胜利里程碑奖励。",
                )
        lines.append("")
        # Events
        lines.append(f" # ── {pid.capitalize()} Victory Events ───────────────────────────────────────────────")
        for m in path["milestones"]:
            n = m["n"]
            mloc = m["loc"]
            lines.append(kv(f"tv_{pid}.{n}.t", mloc["event_title"][lang]))
            lines.append(kv(f"tv_{pid}.{n}.d", mloc["event_desc"][lang]))
            lines.append(kv(f"tv_{pid}.{n}.a", mloc["event_option"][lang]))
        lines.append("")
        # Extra loc keys
        for ekl in path.get("extra_loc_keys", []):
            lines.append(kv(ekl["key"], ekl[lang], version=ekl.get("has_version_suffix", False)))

    # Progress display strings (version-suffixed :0)
    lines.append("")
    lines.append(" # ── Progress bar tooltips — current score display ───────────────────────────")
    for path in data["paths"]:
        pid = path["id"]
        PID = pid.upper()
        lines.append(kv(f"TV_{PID}_PROGRESS_DISPLAY", path["loc"]["progress_display"][lang], version=True))

    # Static modifier names
    lines.append("")
    lines.append(" # ── Static Modifier Names (shown in modifier tooltips) ─────────────────────")
    for path in data["paths"]:
        pid = path["id"]
        for m in path["milestones"]:
            n = m["n"]
            for choice in range(1, 4):
                lines.append(kv(
                    f"STATIC_MODIFIER_NAME_{reward_modifier_id(pid, n, choice)}",
                    reward_name(m["loc"]["title"][lang], choice),
                ))

    lines.append("")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Towards Victory game files from victory_paths.yaml")
    parser.add_argument("--dry", action="store_true", help="Print output to stdout, do not write files")
    args = parser.parse_args()

    data = yaml.safe_load(DATA_YAML.read_text(encoding="utf-8"))
    data["_io_establishment"] = yaml.safe_load(ESTABLISHMENT_YAML.read_text(encoding="utf-8"))
    data["_io_leaders"] = yaml.safe_load(IO_LEADERS_YAML.read_text(encoding="utf-8"))
    pulse_registry = yaml.safe_load(PULSE_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
    data["_pulse_settings"] = pulse_registry.get("settings", {})

    dry = args.dry
    if not dry:
        print("Generating Towards Victory files...")

    # 1. Triggers
    write_file(
        SRC / "in_game/common/scripted_triggers/towards_victory_triggers.txt",
        gen_triggers(data), dry,
    )

    # 2. Effects
    write_file(
        SRC / "in_game/common/scripted_effects/towards_victory_effects.txt",
        gen_effects(data), dry,
    )

    # 3. Modifiers
    write_file(
        SRC / "in_game/common/static_modifiers/towards_victory_modifiers.txt",
        gen_modifiers(data), dry,
    )

    # 4. Situations
    write_file(
        SRC / "in_game/common/situations/towards_victory_situations.txt",
        gen_situation(data), dry,
    )

    # 5. On-actions
    write_file(
        SRC / "in_game/common/on_action/towards_victory_yearly.txt",
        gen_on_actions(data), dry,
    )

    # 6. Events (one file per path)
    for path in data["paths"]:
        pid = path["id"]
        write_file(
            SRC / f"in_game/events/towards_victory_{pid}_events.txt",
            gen_events(path), dry,
        )
    write_file(
        SRC / "in_game/events/tv_io_establishment_events.txt",
        gen_establishment_events(data), dry,
    )

    # 7. Localization
    write_file(
        SRC / "main_menu/localization/english/towards_victory_l_english.yml",
        gen_localization(data, "en"), dry,
    )
    write_file(
        SRC / "main_menu/localization/simp_chinese/towards_victory_l_simp_chinese.yml",
        gen_localization(data, "zh"), dry,
    )

    if not dry:
        print(f"Done. Run: {MANAGED_SANDBOX_PYTHON} scripts\\validate.py")


if __name__ == "__main__":
    main()
