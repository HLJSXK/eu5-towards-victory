"""Shared code generation for the three-slot Victory Path task system.

The canonical catalogue is ``data/victory_path_tasks.yaml``.  Thin 1:1
generators under ``scripts/in_game`` and ``scripts/main_menu`` call the
functions in this module so generated-file ownership remains explicit.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "victory_path_tasks.yaml"
VANILLA_PRICES = REPO_ROOT / "reference_game_files/game/in_game/events/economy/prices.txt"
VANILLA_IO_EFFECTS = (
    REPO_ROOT
    / "reference_game_files/game/in_game/common/scripted_effects/international_organization_effects.txt"
)
VANILLA_INSTITUTION_DIR = REPO_ROOT / "reference_game_files/game/in_game/common/institution"
FONT_ICONS = REPO_ROOT / "reference_game_files/game/main_menu/gui/shared/font_icons.gui"

PATH_IDS = ("conquest", "prosperity", "trade", "diplomatic", "cultural", "science")
SLOTS = (1, 2, 3)
PATH_ID_PREFIX = {path_id: index for index, path_id in enumerate(PATH_IDS, 1)}


def _top_level_ids(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8-sig")
    return set(re.findall(r"(?m)^([a-z][a-z0-9_]*)\s*=\s*\{", text))


def validate_data(data: dict) -> None:
    if set(data.get("paths", {})) != set(PATH_IDS):
        raise ValueError(f"Victory task paths must be exactly {PATH_IDS}")
    if data.get("national_special", {}).get("tasks"):
        raise ValueError("National-special task pool must remain empty in this release")

    ids: set[int] = set()
    keys: set[tuple[str, str]] = set()
    for path_id in PATH_IDS:
        prefix = PATH_ID_PREFIX[path_id]
        for task in data["paths"][path_id]["tasks"]:
            task_id = task.get("id")
            if not isinstance(task_id, int) or task_id in ids:
                raise ValueError(f"Victory task id must be a unique integer: {task_id!r}")
            ids.add(task_id)
            if task_id // 1000 != prefix:
                raise ValueError(f"Task {task_id} is outside the {path_id} x000 ID segment")
            if prefix * 1000 + 200 <= task_id <= prefix * 1000 + 299:
                raise ValueError(f"Task {task_id} uses the reserved {prefix}2xx national-special segment")
            keyed = (path_id, task["key"])
            if keyed in keys:
                raise ValueError(f"Duplicate Victory task key: {path_id}/{task['key']}")
            keys.add(keyed)
            if task["type"] not in {"fixed", "target"}:
                raise ValueError(f"Unsupported task type on {task_id}: {task['type']}")
            if task["type"] == "fixed":
                thresholds = task.get("thresholds", [])
                if not thresholds or any(a >= b for a, b in zip(thresholds, thresholds[1:])):
                    raise ValueError(f"Fixed task {task_id} thresholds must be strictly increasing")

    artworks = next(task for task in data["paths"]["cultural"]["tasks"] if task["id"] == 5001)
    if artworks["thresholds"] != list(range(10, 201, 10)):
        raise ValueError("Artwork-count thresholds must be 10, 20, ..., 200")

    vanilla_institutions: set[str] = set()
    for path in VANILLA_INSTITUTION_DIR.glob("*.txt"):
        if path.name != "readme.txt":
            vanilla_institutions.update(_top_level_ids(path))
    task_institutions = {
        task["institution"]
        for task in data["paths"]["science"]["tasks"]
        if task.get("institution")
    }
    if task_institutions != vanilla_institutions:
        missing = sorted(vanilla_institutions - task_institutions)
        extra = sorted(task_institutions - vanilla_institutions)
        raise ValueError(f"Institution task list mismatch; missing={missing}, extra={extra}")

    font_icon_text = FONT_ICONS.read_text(encoding="utf-8-sig")
    font_icons = set(re.findall(r"(?m)^\s*icon\s*=\s*([A-Za-z0-9_]+)\s*$", font_icon_text))
    task_icons = {task["icon"] for task in all_tasks(data)} | {"trigger_fail", "trigger_yes"}
    missing_icons = sorted(task_icons - font_icons)
    if missing_icons:
        raise ValueError(f"Victory task inline icons missing from font_icons.gui: {missing_icons}")


def load_data() -> dict:
    data = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8"))
    validate_data(data)
    return data


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8-sig")


def all_tasks(data: dict) -> list[dict]:
    result: list[dict] = []
    for path_id in PATH_IDS:
        for task in data["paths"][path_id]["tasks"]:
            result.append({**task, "path": path_id})
    return result


def tasks_for_path(data: dict, path_id: str) -> list[dict]:
    return [{**task, "path": path_id} for task in data["paths"][path_id]["tasks"]]


def header(script: str, description: str, extra_data: str = "") -> str:
    data_line = "data/victory_path_tasks.yaml"
    if extra_data:
        data_line += " + " + extra_data
    return (
        f"# @Generated by {script}\n"
        f"#   Data:    {data_line}\n"
        f"#   Regen:   conda run --no-capture-output -n eu5 python {script}\n"
        "# Do not edit directly - modify the data/generator and re-run it.\n"
        f"# {description}\n"
    )


def slot_prefix(path_id: str, slot: int) -> str:
    return f"tv_{path_id}_task_slot_{slot}"


def metric_var(metric: str) -> str:
    return f"tv_victory_task_metric_{metric}"


def claimed_var(task: dict) -> str:
    suffix = "claimed_index" if task["type"] == "fixed" else "claimed"
    return f"tv_victory_task_{task['id']}_{suffix}"


def task_condition_name(task: dict) -> str:
    return f"tv_victory_task_{task['id']}_current_condition"


def candidate_name(task: dict) -> str:
    return f"tv_victory_task_{task['id']}_candidate"


def refresh_effect(path_id: str, slot: int) -> str:
    return f"tv_victory_path_tasks_refresh_{path_id}_slot_{slot}_effect"


def assign_effect(path_id: str, slot: int) -> str:
    return f"tv_victory_path_tasks_assign_{path_id}_slot_{slot}_effect"


def refill_empty_effect(path_id: str) -> str:
    return f"tv_victory_path_tasks_refill_empty_{path_id}_slots_effect"


def update_effect(path_id: str, slot: int) -> str:
    return f"tv_victory_path_tasks_update_{path_id}_slot_{slot}_effect"


def claim_effect(path_id: str, slot: int) -> str:
    return f"tv_victory_path_tasks_claim_{path_id}_slot_{slot}_effect"


def action_name(path_id: str, slot: int) -> str:
    return f"tv_victory_claim_{path_id}_task_slot_{slot}"


def emit(lines: list[str], level: int = 0, text: str = "") -> None:
    lines.append("\t" * level + text if text else "")


CANDIDATE_METRICS_PREPARED_FLAG = "tv_victory_task_candidate_metrics_prepared"


def uses_monthly_pulse(task: dict) -> bool:
    # Capital building totals have no reliable generic building-completed owner
    # callback, so task 2105 deliberately retains its monthly fallback.
    return task["update"] == "monthly" or task["id"] == 2105


SCALAR_METRICS = {
    "total_locations": "num_locations_owned_or_owned_by_subjects_or_below",
    "owned_locations": "num_locations",
    "tax_base": "country_tax_base",
    "population": "total_population",
    "average_control_pct": "average_control",
    "trade_income": "monthly_trade_income",
    "diplomatic_reputation": "modifier:diplomatic_reputation",
    "artworks": "num_works_of_art",
    "cultural_tradition": "culture.cultural_tradition",
    "cultural_influence": "culture.cultural_influence",
    "science_score": "var:tv_science_score",
}


def _metric_effect(metric: str) -> list[str]:
    """Country-scope effect body that refreshes one cached metric variable."""
    var = metric_var(metric)
    if metric in SCALAR_METRICS:
        value = SCALAR_METRICS[metric]
        lines = [f"set_variable = {{ name = {var} value = {value} }}"]
        if metric == "average_control_pct":
            lines.append(f"change_variable = {{ name = {var} multiply = 100 }}")
        return lines

    if metric == "colonial_locations":
        return [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "every_subject_or_below = {",
            "\tlimit = { is_colonial_subject = yes }",
            "\tscope:tv_victory_task_metric_owner = {",
            f"\t\tchange_variable = {{ name = {var} add = prev.num_locations }}",
            "\t}",
            "}",
        ]

    if metric in {"average_development", "average_prosperity_pct"}:
        value = "development" if metric == "average_development" else "prosperity"
        lines = [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "every_owned_location = {",
            f"\tscope:tv_victory_task_metric_owner = {{ change_variable = {{ name = {var} add = prev.{value} }} }}",
            "}",
            "if = {",
            "\tlimit = { num_locations > 0 }",
            f"\tchange_variable = {{ name = {var} divide = num_locations }}",
            "}",
        ]
        if metric == "average_prosperity_pct":
            lines.append(f"change_variable = {{ name = {var} multiply = 100 }}")
        return lines

    if metric == "dominant_markets":
        return [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "every_market_with_merchants = {",
            "\tlimit = { most_powerful_merchant = scope:tv_victory_task_metric_owner }",
            f"\tscope:tv_victory_task_metric_owner = {{ change_variable = {{ name = {var} add = 1 }} }}",
            "}",
        ]

    if metric == "alliance_level":
        return [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "every_international_organizations_member_of = {",
            "\tlimit = { international_organization_type = international_organization_type:tv_diplomatic_alliance }",
            f"\tif = {{ limit = {{ var:tv_alliance_tier > scope:tv_victory_task_metric_owner.var:{var} }} scope:tv_victory_task_metric_owner = {{ set_variable = {{ name = {var} value = prev.var:tv_alliance_tier }} }} }}",
            "}",
        ]

    if metric == "num_allies":
        return [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "every_known_country = {",
            "\tlimit = { is_allied_with = { target = scope:tv_victory_task_metric_owner } }",
            f"\tscope:tv_victory_task_metric_owner = {{ change_variable = {{ name = {var} add = 1 }} }}",
            "}",
        ]

    if metric == "best_art_quality_pct":
        return [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "ordered_work_of_art_in_country = {",
            "\torder_by = art_quality",
            "\tmax = 1",
            f"\tscope:tv_victory_task_metric_owner = {{ set_variable = {{ name = {var} value = prev.art_quality }} }}",
            "}",
        ]

    if metric == "best_artist_skill_pct":
        return [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "ordered_artist = {",
            "\tlimit = { is_alive = yes }",
            "\torder_by = artist_skill",
            "\tmax = 1",
            f"\tscope:tv_victory_task_metric_owner = {{ set_variable = {{ name = {var} value = prev.artist_skill }} }}",
            "}",
            f"change_variable = {{ name = {var} multiply = 100 }}",
        ]

    if metric == "exhibition_influence":
        return [
            f"set_variable = {{ name = {var} value = 0 }}",
            "save_scope_as = tv_victory_task_metric_owner",
            "every_international_organizations_member_of = {",
            "\tlimit = {",
            "\t\tinternational_organization_type = international_organization_type:tv_arts_exhibition",
            "\t\tleader_country = scope:tv_victory_task_metric_owner",
            "\t}",
            f"\tscope:tv_victory_task_metric_owner = {{ set_variable = {{ name = {var} value = prev.var:tv_arts_intl_influence }} }}",
            "}",
        ]

    raise KeyError(f"Unsupported Victory task metric: {metric}")


def _target_condition_body(task: dict) -> list[str]:
    key = task["completion"]
    if key.startswith("callback") or key == "callback":
        return ["always = no"]
    if key == "institution_embraced":
        return [f"has_embraced_institution = institution:{task['institution']}"]
    conditions: dict[str, list[str]] = {
        "unite_culture": [
            "NOT = {",
            "\tany_location_in_the_world = {",
            "\t\tdominant_culture = root.culture",
            "\t\tNOT = { owner = root }",
            "\t}",
            "}",
        ],
        # The culture-group scope is snapshotted into the active slot at assignment.
        "unite_culture_group": ["always = no"],
        "unite_capital_area": ["capital.area = { NOT = { any_location_in_area = { NOT = { owner = root } } } }"],
        "unite_capital_region": ["capital.region = { NOT = { any_location_in_region = { NOT = { owner = root } } } }"],
        "unite_capital_subcontinent": ["capital.sub_continent = { NOT = { any_location_in_sub_continent = { NOT = { owner = root } } } }"],
        "unite_capital_continent": ["capital.continent = { NOT = { any_location_in_continent = { NOT = { owner = root } } } }"],
        "colonial_empire": [
            "any_subject_or_below = { is_colonial_subject = yes capital.sub_continent = sub_continent:north_america }",
            "any_subject_or_below = { is_colonial_subject = yes capital.sub_continent = sub_continent:south_america }",
            "any_subject_or_below = { is_colonial_subject = yes capital.continent = continent:africa }",
            "any_subject_or_below = { is_colonial_subject = yes capital.continent = continent:asia }",
        ],
        "independent_market": ["capital = { market = { location = root.capital } }"],
        "capital_town": ["capital = { OR = { location_rank = location_rank:town location_rank = location_rank:city location_rank = location_rank:megalopolis } }"],
        "capital_city": ["capital = { OR = { location_rank = location_rank:city location_rank = location_rank:megalopolis } }"],
        "capital_megalopolis": ["capital = { location_rank = location_rank:megalopolis }"],
        "capital_buildings_100": ["capital = { num_buildings >= 100 }"],
        "three_allies": [f"var:{metric_var('num_allies')} ?= {{ this >= 3 }}"],
        "strong_ally": [
            "any_known_country = {",
            "\tis_allied_with = { target = root }",
            "\trelative_military_strength = { target = root value > 0.5 }",
            "}",
        ],
        "hre_emperor": ["any_international_organizations_member_of = { international_organization_type = international_organization_type:hre leader_country = root }"],
        "italian_wars_victor": ["OR = { has_italian_league_won_the_italian_wars = yes has_foreign_league_won_the_italian_wars = yes }"],
        "chinese_emperor": ["any_international_organizations_member_of = { international_organization_type = international_organization_type:middle_kingdom leader_country = root }"],
        "senior_union_partner": ["union ?= { country_is_senior_partner = { country = root } }"],
        "survived_black_death": ["NOT = { is_situation_active = situation:black_death }", "has_variable = had_black_death"],
    }
    if key not in conditions:
        raise KeyError(f"Unsupported target condition: {key} ({task['id']})")
    return conditions[key]


def _appearance_body(task: dict) -> list[str]:
    key = task["appearance"]
    if key in {"default", "not_currently_complete", "next_threshold_above_current"}:
        return ["always = yes"]
    chain: dict[str, list[str]] = {
        "united_culture_and_not_complete": [
            f"{task_condition_name({'id': 1101})} = yes",
            "culture = { has_any_culture_group = yes }",
        ],
        "united_area_and_not_complete": [f"{task_condition_name({'id': 1103})} = yes"],
        "united_region_and_not_complete": [f"{task_condition_name({'id': 1104})} = yes"],
        "united_subcontinent_and_not_complete": [f"{task_condition_name({'id': 1105})} = yes"],
        "has_colonial_subject_and_not_complete": ["any_subject_or_below = { is_colonial_subject = yes }"],
        "capital_is_town": ["capital = { location_rank = location_rank:town }"],
        "capital_is_city": ["capital = { location_rank = location_rank:city }"],
        "triangle_trade_foothold": ["capital.market ?= { location.continent = continent:europe has_merchant = root most_powerful_merchant = root }"],
        "european_capital": ["capital.continent = continent:europe"],
        "coffee_event_basics": ["current_year >= 1500", "capital.continent = continent:europe", "religion.group = religion_group:christian"],
        "spice_trade_foothold": ["capital.continent = continent:europe", "num_of_ports >= 10"],
        "felt_hat_basics": ["current_year >= 1600", "capital.continent = continent:europe"],
        "standing_navy_basics": ["current_year >= 1600", "has_markets = yes"],
        "bronze_cannon_basics": ["has_advance = artillery_institution_advance", "current_age = age_4_reformation"],
        "old_world_market": ["capital_in_old_world_trigger = yes", "has_markets = yes"],
        "tobacco_basics": ["capital_in_old_world_trigger = yes", "has_markets = yes", "OR = { religion.group = religion_group:christian religion.group = religion_group:muslim }"],
        "has_rival": ["any_country = { is_rival_of = root }"],
        "hre_monarchy_not_emperor": ["government_type = government_type:monarchy", "any_international_organizations_member_of = { international_organization_type = international_organization_type:hre }"],
        "italian_wars_member": ["is_situation_active = situation:italian_wars", "is_member_of_any_italian_wars_league = yes"],
        "chinese_culture_group": ["culture = { has_culture_group = culture_group:chinese_group }"],
        "monarchy_not_senior_partner": ["government_type = government_type:monarchy"],
        "looted_art_before": ["has_variable = tv_victory_task_5101_claimed"],
        "local_exhibition_before": ["has_variable = tv_victory_task_5103_claimed"],
        "rating_2_before": ["has_variable = tv_victory_task_5104_claimed"],
        "rating_3_before": ["has_variable = tv_victory_task_5105_claimed"],
        "black_death_active": ["is_situation_active = situation:black_death"],
    }
    if key == "institution_not_embraced":
        return [f"NOT = {{ has_embraced_institution = institution:{task['institution']} }}"]
    if key not in chain:
        raise KeyError(f"Unsupported appearance condition: {key} ({task['id']})")
    return chain[key]


def _fixed_threshold_eligible_lines(task: dict, threshold: int | float, index: int) -> list[str]:
    return [
        f"NOT = {{ var:{claimed_var(task)} ?= {{ this >= {index} }} }}",
        f"var:{metric_var(task['metric'])} ?= {{ this < {threshold} }}",
    ]


def generate_triggers(data: dict, script: str) -> str:
    lines = [header(script, "Task candidate, completion and GUI display triggers."), ""]
    tasks = all_tasks(data)

    emit(lines, 0, "# Target-state triggers")
    for task in tasks:
        if task["type"] != "target":
            continue
        emit(lines, 0, f"{task_condition_name(task)} = {{")
        for raw in _target_condition_body(task):
            emit(lines, 1, raw)
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "# Candidate triggers; slot de-duplication is added by each refresh router.")
    for task in tasks:
        emit(lines, 0, f"{candidate_name(task)} = {{")
        emit(lines, 1, "is_human = yes")
        if task["type"] == "fixed":
            emit(lines, 1, "OR = {")
            for index, threshold in enumerate(task["thresholds"], 1):
                emit(lines, 2, "AND = {")
                for raw in _fixed_threshold_eligible_lines(task, threshold, index):
                    emit(lines, 3, raw)
                emit(lines, 2, "}")
            emit(lines, 1, "}")
        else:
            emit(lines, 1, f"NOT = {{ has_variable = {claimed_var(task)} }}")
            if task.get("global_once"):
                emit(lines, 1, f"NOT = {{ has_global_variable = tv_victory_task_price_{task['event_id']}_triggered }}")
            for raw in _appearance_body(task):
                emit(lines, 1, raw)
            if task["completion"] not in {"callback", "callback_quality_80", "callback_rating_2", "callback_rating_3", "callback_rating_4"}:
                emit(lines, 1, f"NOT = {{ {task_condition_name(task)} = yes }}")
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "# Empty national-special framework. Future x2xx tasks plug into these routers.")
    emit(lines, 0, "tv_victory_path_task_national_special_historical_tag_eligible = {")
    emit(lines, 1, "has_or_had_tag = $tag$")
    emit(lines, 0, "}")
    emit(lines)
    for path_id in PATH_IDS:
        for slot in SLOTS:
            emit(lines, 0, f"tv_{path_id}_task_slot_{slot}_has_national_special_candidate = {{ always = no }}")
    emit(lines)

    emit(lines, 0, "# Fixed GUI-facing slot triggers. Each route dispatches by the slot's stable task ID.")
    for path_id in PATH_IDS:
        path_tasks = tasks_for_path(data, path_id)
        for slot in SLOTS:
            prefix = slot_prefix(path_id, slot)
            emit(lines, 0, f"{prefix}_display_trigger = {{")
            emit(lines, 1, "switch = {")
            emit(lines, 2, f"trigger = var:{prefix}_id")
            emit(lines, 2, "0 = {")
            emit(lines, 3, "custom_tooltip = { text = TV_VICTORY_TASK_NO_AVAILABLE_REQUIREMENT always = no }")
            emit(lines, 2, "}")
            for task in path_tasks:
                emit(lines, 2, f"{task['id']} = {{")
                emit(lines, 3, "custom_tooltip = {")
                emit(lines, 4, f"text = TV_VICTORY_TASK_{task['id']}_{path_id.upper()}_{slot}_REQUIREMENT")
                emit(lines, 4, "OR = {")
                emit(lines, 5, f"has_variable = {prefix}_complete")
                if task["type"] == "fixed":
                    emit(lines, 5, f"var:{metric_var(task['metric'])} ?= {{ this >= var:{prefix}_target }}")
                elif task["completion"] == "unite_culture_group":
                    emit(lines, 5, f"var:{prefix}_culture_group ?= {{")
                    emit(lines, 6, "NOT = {")
                    emit(lines, 7, "any_location_in_the_world = {")
                    emit(lines, 8, "dominant_culture = { any_culture_group = { this = root.var:" + prefix + "_culture_group } }")
                    emit(lines, 8, "NOT = { owner = root }")
                    emit(lines, 7, "}")
                    emit(lines, 6, "}")
                    emit(lines, 5, "}")
                elif task["completion"].startswith("callback") or task["completion"] == "callback":
                    emit(lines, 5, "always = no")
                else:
                    emit(lines, 5, f"{task_condition_name(task)} = yes")
                emit(lines, 4, "}")
                emit(lines, 3, "}")
                emit(lines, 2, "}")
            emit(lines, 1, "}")
            emit(lines, 0, "}")
            emit(lines)
    return "\n".join(lines)


def _emit_metric_effects(lines: list[str], data: dict) -> None:
    metrics = sorted({task["metric"] for task in all_tasks(data) if task["type"] == "fixed"} | {"num_allies"})
    for metric in metrics:
        emit(lines, 0, f"tv_victory_task_refresh_metric_{metric}_effect = {{")
        for raw in _metric_effect(metric):
            emit(lines, 1, raw)
        emit(lines, 0, "}")
        emit(lines)


def _emit_candidate_metric_refreshes(lines: list[str], data: dict, path_id: str, level: int) -> None:
    """Refresh candidate metrics once, skipping permanently exhausted families."""
    requirements: dict[str, list[str]] = {}
    for task in tasks_for_path(data, path_id):
        if task["type"] == "fixed":
            requirements.setdefault(task["metric"], []).append(
                f"NOT = {{ var:{claimed_var(task)} ?= {{ this >= {len(task['thresholds'])} }} }}"
            )
        elif task["completion"] == "three_allies":
            requirements.setdefault("num_allies", []).append(
                f"NOT = {{ has_variable = {claimed_var(task)} }}"
            )

    for metric, metric_requirements in sorted(requirements.items()):
        emit(lines, level, "if = {")
        emit(lines, level + 1, "limit = {")
        if len(metric_requirements) == 1:
            emit(lines, level + 2, metric_requirements[0])
        else:
            emit(lines, level + 2, "OR = {")
            for requirement in metric_requirements:
                emit(lines, level + 3, requirement)
            emit(lines, level + 2, "}")
        emit(lines, level + 1, "}")
        emit(lines, level + 1, f"tv_victory_task_refresh_metric_{metric}_effect = yes")
        emit(lines, level, "}")


def _emit_clear_slot(
    lines: list[str], level: int, prefix: str, *, include_culture_group: bool
) -> None:
    suffixes = ("target", "target_index", "progress_pct", "complete")
    if include_culture_group:
        suffixes += ("culture_group",)
    for suffix in suffixes:
        emit(lines, level, f"remove_variable = {prefix}_{suffix}")
    emit(lines, level, f"set_variable = {{ name = {prefix}_id value = 0 }}")
    emit(lines, level, f"set_variable = {{ name = {prefix}_target value = 0 }}")
    emit(lines, level, f"set_variable = {{ name = {prefix}_target_index value = 0 }}")
    emit(lines, level, f"set_variable = {{ name = {prefix}_progress_pct value = 0 }}")


def _emit_assign_task(lines: list[str], level: int, task: dict, path_id: str, slot: int) -> None:
    prefix = slot_prefix(path_id, slot)
    if task["type"] == "fixed":
        for idx, threshold in enumerate(task["thresholds"], 1):
            keyword = "if" if idx == 1 else "else_if"
            emit(lines, level, f"{keyword} = {{")
            emit(lines, level + 1, "limit = {")
            for raw in _fixed_threshold_eligible_lines(task, threshold, idx):
                emit(lines, level + 2, raw)
            emit(lines, level + 1, "}")
            emit(lines, level + 1, f"set_variable = {{ name = {prefix}_id value = {task['id']} }}")
            emit(lines, level + 1, f"set_variable = {{ name = {prefix}_target value = {threshold} }}")
            emit(lines, level + 1, f"set_variable = {{ name = {prefix}_target_index value = {idx} }}")
            emit(lines, level, "}")
    else:
        emit(lines, level, f"set_variable = {{ name = {prefix}_id value = {task['id']} }}")
        if task["completion"] == "unite_culture_group":
            emit(lines, level, "save_scope_as = tv_victory_task_culture_group_owner")
            emit(lines, level, "culture = {")
            emit(lines, level + 1, "every_culture_group = {")
            emit(lines, level + 2, "scope:tv_victory_task_culture_group_owner = {")
            emit(lines, level + 3, "if = {")
            emit(lines, level + 4, f"limit = {{ NOT = {{ has_variable = {prefix}_culture_group }} }}")
            emit(lines, level + 4, f"set_variable = {{ name = {prefix}_culture_group value = prev }}")
            emit(lines, level + 3, "}")
            emit(lines, level + 2, "}")
            emit(lines, level + 1, "}")
            emit(lines, level, "}")


def _emit_slot_update(lines: list[str], data: dict, path_id: str, slot: int) -> None:
    prefix = slot_prefix(path_id, slot)
    path_tasks = sorted(tasks_for_path(data, path_id), key=lambda task: not uses_monthly_pulse(task))
    emit(lines, 0, f"{update_effect(path_id, slot)} = {{")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ has_variable = {prefix}_complete }}")
    emit(lines, 2, f"set_variable = {{ name = {prefix}_progress_pct value = 100 }}")
    emit(lines, 1, "}")
    for task in path_tasks:
        emit(lines, 1, "else_if = {")
        emit(lines, 2, f"limit = {{ var:{prefix}_id ?= {task['id']} }}")
        if task["type"] == "fixed":
            metric = task["metric"]
            emit(lines, 2, "if = {")
            emit(lines, 3, f"limit = {{ NOT = {{ has_variable = {CANDIDATE_METRICS_PREPARED_FLAG} }} }}")
            emit(lines, 3, f"tv_victory_task_refresh_metric_{metric}_effect = yes")
            emit(lines, 2, "}")
            emit(lines, 2, f"set_variable = {{ name = {prefix}_progress_pct value = var:{metric_var(metric)} }}")
            emit(lines, 2, f"change_variable = {{ name = {prefix}_progress_pct divide = var:{prefix}_target }}")
            emit(lines, 2, f"change_variable = {{ name = {prefix}_progress_pct multiply = 100 }}")
            emit(lines, 2, "if = {")
            emit(lines, 3, f"limit = {{ var:{prefix}_progress_pct < 0 }}")
            emit(lines, 3, f"set_variable = {{ name = {prefix}_progress_pct value = 0 }}")
            emit(lines, 2, "}")
            emit(lines, 2, "if = {")
            emit(lines, 3, f"limit = {{ var:{prefix}_progress_pct > 100 }}")
            emit(lines, 3, f"set_variable = {{ name = {prefix}_progress_pct value = 100 }}")
            emit(lines, 2, "}")
            emit(lines, 2, "if = {")
            emit(lines, 3, f"limit = {{ var:{metric_var(metric)} ?= {{ this >= var:{prefix}_target }} }}")
            emit(lines, 3, f"set_variable = {{ name = {prefix}_complete value = 1 }}")
            emit(lines, 3, f"set_variable = {{ name = {prefix}_progress_pct value = 100 }}")
            emit(lines, 2, "}")
        elif task["completion"] == "three_allies":
            emit(lines, 2, "if = {")
            emit(lines, 3, f"limit = {{ NOT = {{ has_variable = {CANDIDATE_METRICS_PREPARED_FLAG} }} }}")
            emit(lines, 3, "tv_victory_task_refresh_metric_num_allies_effect = yes")
            emit(lines, 2, "}")
            emit(lines, 2, f"if = {{ limit = {{ {task_condition_name(task)} = yes }} set_variable = {{ name = {prefix}_complete value = 1 }} set_variable = {{ name = {prefix}_progress_pct value = 100 }} }}")
        elif task["completion"] == "unite_culture_group":
            emit(lines, 2, f"if = {{ limit = {{ {prefix}_display_trigger = yes }} set_variable = {{ name = {prefix}_complete value = 1 }} set_variable = {{ name = {prefix}_progress_pct value = 100 }} }}")
        elif task["failure"] == "italian_wars_ended_without_victory":
            emit(lines, 2, "if = {")
            emit(lines, 3, "limit = { NOT = { is_situation_active = situation:italian_wars } }")
            emit(lines, 3, f"if = {{ limit = {{ {task_condition_name(task)} = yes }} set_variable = {{ name = {prefix}_complete value = 1 }} set_variable = {{ name = {prefix}_progress_pct value = 100 }} }}")
            emit(lines, 3, f"else = {{ {refresh_effect(path_id, slot)} = yes }}")
            emit(lines, 2, "}")
        elif task["failure"] == "black_death_ended_without_exposure":
            emit(lines, 2, "if = {")
            emit(lines, 3, "limit = { NOT = { is_situation_active = situation:black_death } }")
            emit(lines, 3, f"if = {{ limit = {{ {task_condition_name(task)} = yes }} set_variable = {{ name = {prefix}_complete value = 1 }} set_variable = {{ name = {prefix}_progress_pct value = 100 }} }}")
            emit(lines, 3, f"else = {{ {refresh_effect(path_id, slot)} = yes }}")
            emit(lines, 2, "}")
        elif task["completion"].startswith("callback") or task["completion"] == "callback":
            emit(lines, 2, f"set_variable = {{ name = {prefix}_progress_pct value = 0 }}")
        else:
            emit(lines, 2, "if = {")
            emit(lines, 3, f"limit = {{ {task_condition_name(task)} = yes }}")
            emit(lines, 3, f"set_variable = {{ name = {prefix}_complete value = 1 }}")
            emit(lines, 3, f"set_variable = {{ name = {prefix}_progress_pct value = 100 }}")
            emit(lines, 2, "}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def _emit_assign_slot(lines: list[str], data: dict, path_id: str, slot: int) -> None:
    prefix = slot_prefix(path_id, slot)
    path_tasks = tasks_for_path(data, path_id)
    has_culture_group_task = any(
        task["completion"] == "unite_culture_group" for task in path_tasks
    )
    other_slots = [s for s in SLOTS if s != slot]
    emit(lines, 0, f"{assign_effect(path_id, slot)} = {{")
    _emit_clear_slot(
        lines, 1, prefix, include_culture_group=has_culture_group_task
    )
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ tv_{path_id}_task_slot_{slot}_has_national_special_candidate = yes }}")
    emit(lines, 2, "# Reserved national-special priority branch; no candidates this release.")
    emit(lines, 1, "}")
    emit(lines, 1, "else = {")
    emit(lines, 2, "random_list = {")
    for task in path_tasks:
        emit(lines, 3, "1 = {")
        emit(lines, 4, "trigger = {")
        emit(lines, 5, f"{candidate_name(task)} = yes")
        for other in other_slots:
            emit(lines, 5, f"NOT = {{ var:{slot_prefix(path_id, other)}_id ?= {task['id']} }}")
        emit(lines, 4, "}")
        _emit_assign_task(lines, 4, task, path_id, slot)
        emit(lines, 3, "}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ var:{prefix}_id ?= {{ this > 0 }} }}")
    emit(lines, 2, f"{update_effect(path_id, slot)} = yes")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def _emit_refresh_slot(lines: list[str], data: dict, path_id: str, slot: int) -> None:
    emit(lines, 0, f"{refresh_effect(path_id, slot)} = {{")
    emit(lines, 1, "if = {")
    emit(lines, 2, f"limit = {{ is_human = yes has_variable = tv_{path_id}_victory_enabled }}")
    _emit_candidate_metric_refreshes(lines, data, path_id, 2)
    emit(lines, 2, f"set_variable = {{ name = {CANDIDATE_METRICS_PREPARED_FLAG} value = 1 }}")
    emit(lines, 2, f"{assign_effect(path_id, slot)} = yes")
    emit(lines, 2, f"remove_variable = {CANDIDATE_METRICS_PREPARED_FLAG}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def _emit_refill_empty_slots(lines: list[str], data: dict, path_id: str) -> None:
    """Fill route slots with one metric pass and stop after the first miss."""
    emit(lines, 0, f"{refill_empty_effect(path_id)} = {{")
    _emit_candidate_metric_refreshes(lines, data, path_id, 1)
    emit(lines, 1, f"set_variable = {{ name = {CANDIDATE_METRICS_PREPARED_FLAG} value = 1 }}")
    for slot in SLOTS:
        prefix = slot_prefix(path_id, slot)
        emit(lines, 1, "if = {")
        emit(lines, 2, "limit = {")
        emit(lines, 3, f"var:{prefix}_id ?= 0")
        for previous_slot in SLOTS:
            if previous_slot >= slot:
                break
            emit(lines, 3, f"NOT = {{ var:{slot_prefix(path_id, previous_slot)}_id ?= 0 }}")
        emit(lines, 2, "}")
        emit(lines, 2, f"{assign_effect(path_id, slot)} = yes")
        emit(lines, 1, "}")
    emit(lines, 1, f"remove_variable = {CANDIDATE_METRICS_PREPARED_FLAG}")
    emit(lines, 0, "}")
    emit(lines)


def _emit_mark_task_complete(lines: list[str], data: dict, task: dict, *, extra_limit: Iterable[str] = ()) -> None:
    path_id = task["path"]
    name = f"tv_victory_task_mark_{task['id']}_complete_effect"
    emit(lines, 0, f"{name} = {{")
    for slot in SLOTS:
        prefix = slot_prefix(path_id, slot)
        emit(lines, 1, "if = {")
        emit(lines, 2, "limit = {")
        emit(lines, 3, f"var:{prefix}_id ?= {task['id']}")
        for raw in extra_limit:
            emit(lines, 3, raw)
        emit(lines, 2, "}")
        emit(lines, 2, f"set_variable = {{ name = {prefix}_complete value = 1 }}")
        emit(lines, 2, f"set_variable = {{ name = {prefix}_progress_pct value = 100 }}")
        emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def _emit_callbacks(lines: list[str], data: dict) -> None:
    tasks = all_tasks(data)
    for task in tasks:
        if task["type"] == "target":
            _emit_mark_task_complete(lines, data, task)

    callback_groups: dict[str, list[dict]] = {}
    for task in tasks:
        callback = task.get("callback")
        if callback:
            callback_groups.setdefault(callback, []).append(task)

    for callback, group in callback_groups.items():
        emit(lines, 0, f"tv_victory_task_callback_{callback}_effect = {{")
        for task in group:
            if task["completion"].startswith("callback_rating_"):
                rating = task["completion"].rsplit("_", 1)[1]
                emit(lines, 1, f"if = {{ limit = {{ var:tv_local_exhibition_last_rating ?= {{ this >= {rating} }} }} tv_victory_task_mark_{task['id']}_complete_effect = yes }}")
            else:
                emit(lines, 1, f"tv_victory_task_mark_{task['id']}_complete_effect = yes")
        emit(lines, 0, "}")
        emit(lines)

    emit(lines, 0, "tv_victory_task_work_of_art_looted_callback_effect = {")
    emit(lines, 1, "tv_victory_task_mark_5101_complete_effect = yes")
    emit(lines, 1, "if = { limit = { root.art_quality >= 80 } tv_victory_task_mark_5102_complete_effect = yes }")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_victory_task_join_war_callback_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = { any_country = { is_rival_of = root is_at_war_with = root } }")
    emit(lines, 2, "tv_victory_task_mark_4103_complete_effect = yes")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_victory_task_italian_wars_ended_callback_effect = {")
    emit(lines, 1, "every_country = {")
    emit(lines, 2, "limit = { is_human = yes }")
    emit(lines, 2, "if = {")
    emit(lines, 3, "limit = {")
    emit(lines, 4, "OR = {")
    for io_id in (
        "italian_league_1",
        "italian_league_2",
        "italian_league_3",
        "foreign_league_balkan",
        "foreign_league_france",
        "foreign_league_hre",
        "foreign_league_iberia",
    ):
        emit(lines, 5, "AND = {")
        emit(lines, 6, f"is_member_of_international_organization = international_organization:{io_id}")
        emit(lines, 6, f"international_organization:{io_id} ?= {{ total_locations_owned >= 200 }}")
        emit(lines, 5, "}")
    emit(lines, 4, "}")
    emit(lines, 3, "}")
    emit(lines, 3, "tv_victory_task_mark_4105_complete_effect = yes")
    emit(lines, 2, "}")
    emit(lines, 2, "else = {")
    for slot in SLOTS:
        prefix = slot_prefix("diplomatic", slot)
        emit(lines, 3, f"if = {{ limit = {{ var:{prefix}_id ?= 4105 }} {refresh_effect('diplomatic', slot)} = yes }}")
    emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    for task in tasks:
        if task.get("building"):
            emit(lines, 0, f"tv_victory_task_build_{task['building']}_callback_effect = {{")
            emit(lines, 1, f"tv_victory_task_mark_{task['id']}_complete_effect = yes")
            emit(lines, 0, "}")
            emit(lines)

    price_tasks = {int(t["event_id"]): t for t in tasks if t.get("event_id") is not None}
    for event_id, task in sorted(price_tasks.items()):
        emit(lines, 0, f"tv_victory_task_prices_{event_id}_callback_effect = {{")
        if task.get("global_once"):
            global_var = f"tv_victory_task_price_{event_id}_triggered"
            emit(lines, 1, "if = {")
            emit(lines, 2, f"limit = {{ NOT = {{ has_global_variable = {global_var} }} }}")
            emit(lines, 2, f"set_global_variable = {{ name = {global_var} value = 1 }}")
            emit(lines, 2, "every_country = {")
            emit(lines, 3, "limit = { is_human = yes }")
            emit(lines, 3, "if = {")
            emit(lines, 4, "limit = { this = root }")
            emit(lines, 4, f"tv_victory_task_mark_{task['id']}_complete_effect = yes")
            emit(lines, 3, "}")
            emit(lines, 3, "else = {")
            for slot in SLOTS:
                prefix = slot_prefix("trade", slot)
                emit(lines, 4, f"if = {{ limit = {{ var:{prefix}_id ?= {task['id']} }} {refresh_effect('trade', slot)} = yes }}")
            emit(lines, 3, "}")
            emit(lines, 2, "}")
            emit(lines, 1, "}")
        else:
            emit(lines, 1, f"tv_victory_task_mark_{task['id']}_complete_effect = yes")
        emit(lines, 0, "}")
        emit(lines)


def _emit_claim(lines: list[str], data: dict, path_id: str, slot: int) -> None:
    prefix = slot_prefix(path_id, slot)
    emit(lines, 0, f"{claim_effect(path_id, slot)} = {{")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = {")
    emit(lines, 3, "is_human = yes")
    emit(lines, 3, f"has_variable = {prefix}_complete")
    emit(lines, 3, f"var:{prefix}_id ?= {{ this > 0 }}")
    emit(lines, 2, "}")
    emit(lines, 2, f"change_variable = {{ name = tv_{path_id}_tree_points add = 1 }}")
    for task in tasks_for_path(data, path_id):
        emit(lines, 2, "if = {")
        emit(lines, 3, f"limit = {{ var:{prefix}_id ?= {task['id']} }}")
        if task["type"] == "fixed":
            emit(lines, 3, f"set_variable = {{ name = {claimed_var(task)} value = var:{prefix}_target_index }}")
        else:
            emit(lines, 3, f"set_variable = {{ name = {claimed_var(task)} value = 1 }}")
        emit(lines, 2, "}")
    emit(lines, 2, f"{refresh_effect(path_id, slot)} = yes")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)


def generate_effects(data: dict, script: str) -> str:
    lines = [
        header(
            script,
            "Task metrics, assignment, updates, callbacks and claiming.",
            "reference_game_files/.../international_organization_effects.txt",
        ),
        "",
    ]
    _emit_metric_effects(lines, data)

    for path_id in PATH_IDS:
        path_tasks = tasks_for_path(data, path_id)
        has_culture_group_task = any(
            task["completion"] == "unite_culture_group" for task in path_tasks
        )
        for slot in SLOTS:
            _emit_slot_update(lines, data, path_id, slot)
        for slot in SLOTS:
            _emit_assign_slot(lines, data, path_id, slot)
        for slot in SLOTS:
            _emit_refresh_slot(lines, data, path_id, slot)
        _emit_refill_empty_slots(lines, data, path_id)
        emit(lines, 0, f"tv_victory_path_tasks_refresh_all_{path_id}_effect = {{")
        emit(lines, 1, "if = {")
        emit(lines, 2, f"limit = {{ is_human = yes has_variable = tv_{path_id}_victory_enabled }}")
        for slot in SLOTS:
            _emit_clear_slot(
                lines,
                2,
                slot_prefix(path_id, slot),
                include_culture_group=has_culture_group_task,
            )
        _emit_candidate_metric_refreshes(lines, data, path_id, 2)
        emit(lines, 2, f"set_variable = {{ name = {CANDIDATE_METRICS_PREPARED_FLAG} value = 1 }}")
        for slot in SLOTS:
            if slot == SLOTS[0]:
                emit(lines, 2, f"{assign_effect(path_id, slot)} = yes")
                continue
            emit(lines, 2, "if = {")
            emit(lines, 3, "limit = {")
            for previous_slot in SLOTS:
                if previous_slot >= slot:
                    break
                emit(lines, 4, f"NOT = {{ var:{slot_prefix(path_id, previous_slot)}_id ?= 0 }}")
            emit(lines, 3, "}")
            emit(lines, 3, f"{assign_effect(path_id, slot)} = yes")
            emit(lines, 2, "}")
        emit(lines, 2, f"remove_variable = {CANDIDATE_METRICS_PREPARED_FLAG}")
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)
        emit(lines, 0, f"tv_victory_path_tasks_initialize_{path_id}_effect = {{")
        emit(lines, 1, "if = {")
        emit(lines, 2, "limit = { is_human = yes }")
        emit(lines, 2, f"set_variable = {{ name = tv_{path_id}_tree_points value = 0 }}")
        emit(lines, 2, f"tv_victory_path_tasks_refresh_all_{path_id}_effect = yes")
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)
        for slot in SLOTS:
            _emit_claim(lines, data, path_id, slot)

    _emit_callbacks(lines, data)

    emit(lines, 0, "tv_victory_path_tasks_monthly_pulse_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = { is_human = yes }")
    for path_id in PATH_IDS:
        emit(lines, 2, f"if = {{ limit = {{ has_variable = tv_{path_id}_victory_enabled }}")
        monthly_ids = [task["id"] for task in tasks_for_path(data, path_id) if uses_monthly_pulse(task)]
        for slot in SLOTS:
            prefix = slot_prefix(path_id, slot)
            if monthly_ids:
                emit(lines, 3, "if = {")
                emit(lines, 4, "limit = {")
                emit(lines, 5, "OR = {")
                for task_id in monthly_ids:
                    emit(lines, 6, f"var:{prefix}_id ?= {task_id}")
                emit(lines, 5, "}")
                emit(lines, 4, "}")
                emit(lines, 4, f"{update_effect(path_id, slot)} = yes")
                emit(lines, 3, "}")
        emit(lines, 3, "if = {")
        emit(lines, 4, "limit = {")
        emit(lines, 5, "OR = {")
        for slot in SLOTS:
            emit(lines, 6, f"var:{slot_prefix(path_id, slot)}_id ?= 0")
        emit(lines, 5, "}")
        emit(lines, 4, "}")
        emit(lines, 4, f"{refill_empty_effect(path_id)} = yes")
        emit(lines, 3, "}")
        emit(lines, 2, "}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_victory_path_tasks_yearly_pulse_effect = {")
    emit(lines, 1, "if = {")
    emit(lines, 2, "limit = { is_human = yes has_variable = tv_science_victory_enabled }")
    for slot in SLOTS:
        prefix = slot_prefix("science", slot)
        emit(lines, 2, f"if = {{ limit = {{ var:{prefix}_id ?= 6001 }} {update_effect('science', slot)} = yes }}")
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_victory_path_tasks_location_owner_changed_effect = {")
    for path_id in ("conquest", "prosperity"):
        for slot in SLOTS:
            emit(lines, 1, f"if = {{ limit = {{ has_variable = tv_{path_id}_victory_enabled }} {update_effect(path_id, slot)} = yes }}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_victory_path_tasks_cultural_state_changed_effect = {")
    for slot in SLOTS:
        emit(lines, 1, f"if = {{ limit = {{ has_variable = tv_cultural_victory_enabled }} {update_effect('cultural', slot)} = yes }}")
    emit(lines, 0, "}")
    emit(lines)

    emit(lines, 0, "tv_victory_path_tasks_diplomatic_state_changed_effect = {")
    for slot in SLOTS:
        emit(lines, 1, f"if = {{ limit = {{ has_variable = tv_diplomatic_victory_enabled }} {update_effect('diplomatic', slot)} = yes }}")
    emit(lines, 0, "}")
    emit(lines)

    # The vanilla situation destroys every Italian Wars league at the end of
    # on_ended.  Resolve the active task immediately before that destruction,
    # while winning-league membership is still queryable, then preserve the
    # remainder of the vanilla helper byte-for-byte.
    vanilla_destroy = _extract_top_level_block(
        VANILLA_IO_EFFECTS.read_text(encoding="utf-8-sig"),
        "destroy_all_italian_leagues",
    )
    opening = "destroy_all_italian_leagues = {"
    if not vanilla_destroy.startswith(opening):
        raise ValueError("Vanilla destroy_all_italian_leagues shape changed")
    override = vanilla_destroy.replace(
        opening,
        "REPLACE:" + opening + "\n\ttv_victory_task_italian_wars_ended_callback_effect = yes",
        1,
    )
    emit(lines, 0, "# Same-ID vanilla helper override: append task resolution before league destruction.")
    lines.extend(override.splitlines())
    emit(lines)
    return "\n".join(lines)


def generate_actions(data: dict, script: str) -> str:
    lines = [header(script, "Eighteen player-only click-to-claim slot actions."), ""]
    for path_id in PATH_IDS:
        for slot in SLOTS:
            prefix = slot_prefix(path_id, slot)
            name = action_name(path_id, slot)
            emit(lines, 0, f"{name} = {{")
            emit(lines, 1, "type = owncountry")
            emit(lines, 1, "show_message = no")
            emit(lines, 1, "ai_tick = never")
            emit(lines, 1, "automation_tick = never")
            emit(lines, 1, "potential = { scope:actor = { is_human = yes has_variable = tv_" + path_id + "_victory_enabled var:" + prefix + "_id ?= { this > 0 } } }")
            emit(lines, 1, f"allow = {{ scope:actor = {{ has_variable = {prefix}_complete }} }}")
            emit(lines, 1, "effect = {")
            emit(lines, 2, "scope:actor = {")
            emit(lines, 3, "hidden_effect = {")
            emit(lines, 4, f"{claim_effect(path_id, slot)} = yes")
            emit(lines, 3, "}")
            emit(lines, 2, "}")
            emit(lines, 1, "}")
            emit(lines, 1, "ai_will_do = { add = -100 }")
            emit(lines, 0, "}")
            emit(lines)
    return "\n".join(lines)


def generate_ai_list(data: dict, script: str) -> str:
    lines = [header(script, "Registers all task actions as ineligible for AI automation."), ""]
    emit(lines, 0, "tv_victory_path_task_actions_list = {")
    emit(lines, 1, "potential = { always = no }")
    emit(lines, 1, "actions = {")
    for path_id in PATH_IDS:
        for slot in SLOTS:
            emit(lines, 2, action_name(path_id, slot))
    emit(lines, 1, "}")
    emit(lines, 0, "}")
    emit(lines)
    return "\n".join(lines)


def generate_customizable_localization(data: dict, script: str) -> str:
    lines = [header(script, "Dynamic inline task icon/name routing by slot ID."), ""]
    for path_id in PATH_IDS:
        path_tasks = tasks_for_path(data, path_id)
        for slot in SLOTS:
            prefix = slot_prefix(path_id, slot)
            for suffix in ("icon", "name"):
                emit(lines, 0, f"{prefix}_{suffix} = {{")
                emit(lines, 1, "type = country")
                emit(lines, 1, "text = {")
                emit(lines, 2, f"trigger = {{ var:{prefix}_id ?= 0 }}")
                emit(lines, 2, f"localization_key = TV_VICTORY_TASK_NO_AVAILABLE_{suffix.upper()}")
                emit(lines, 1, "}")
                for task in path_tasks:
                    emit(lines, 1, "text = {")
                    emit(lines, 2, f"trigger = {{ var:{prefix}_id ?= {task['id']} }}")
                    emit(lines, 2, f"localization_key = TV_VICTORY_TASK_{task['id']}_{suffix.upper()}")
                    emit(lines, 1, "}")
                emit(lines, 0, "}")
                emit(lines)
    return "\n".join(lines)


def generate_on_actions(data: dict, script: str) -> str:
    lines = [header(script, "Named callback on_actions registered through data/pulse_registry.yaml."), ""]

    def block(name: str, body: Iterable[str]) -> None:
        emit(lines, 0, f"{name} = {{")
        emit(lines, 1, "effect = {")
        for raw in body:
            emit(lines, 2, raw)
        emit(lines, 1, "}")
        emit(lines, 0, "}")
        emit(lines)

    block("tv_victory_path_tasks_monthly_pulse", [
        "tv_victory_path_tasks_monthly_pulse_effect = yes",
    ])
    block("tv_victory_path_tasks_yearly_pulse", [
        "tv_victory_path_tasks_yearly_pulse_effect = yes",
    ])

    block("tv_victory_path_tasks_on_location_changed_owner", [
        "scope:loser ?= { tv_victory_path_tasks_location_owner_changed_effect = yes }",
        "scope:winner ?= { tv_victory_path_tasks_location_owner_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_location_changed_rank", [
        "owner ?= { tv_victory_path_tasks_location_owner_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_subject_created", [
        "scope:overlord ?= { tv_victory_path_tasks_location_owner_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_transfer_subject", [
        "scope:overlord ?= { tv_victory_path_tasks_location_owner_changed_effect = yes }",
        "scope:former_overlord ?= { tv_victory_path_tasks_location_owner_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_institution_embraced", [
        "root ?= { tv_victory_path_tasks_update_science_slot_1_effect = yes tv_victory_path_tasks_update_science_slot_2_effect = yes tv_victory_path_tasks_update_science_slot_3_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_work_of_art_created", [
        "owner ?= { tv_victory_path_tasks_cultural_state_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_work_of_art_destroyed", [
        "owner ?= { tv_victory_path_tasks_cultural_state_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_work_of_art_looted", [
        "scope:target.owner ?= { tv_victory_task_work_of_art_looted_callback_effect = yes tv_victory_path_tasks_cultural_state_changed_effect = yes }",
        "scope:location.owner ?= { tv_victory_path_tasks_cultural_state_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_join_war", [
        "root ?= { tv_victory_task_join_war_callback_effect = yes tv_victory_path_tasks_diplomatic_state_changed_effect = yes }",
    ])
    block("tv_victory_path_tasks_on_io_leader_changed", [
        "root ?= { tv_victory_path_tasks_diplomatic_state_changed_effect = yes }",
        "scope:old_ruler ?= { tv_victory_path_tasks_diplomatic_state_changed_effect = yes }",
    ])
    return "\n".join(lines)


def _extract_top_level_block(text: str, key: str) -> str:
    match = re.search(rf"(?m)^\s*(?:REPLACE:)?{re.escape(key)}\s*=\s*\{{", text)
    if not match:
        raise ValueError(f"Top-level block not found: {key}")
    start = match.start()
    brace = text.find("{", match.start(), match.end())
    depth = 0
    in_string = False
    escaped = False
    for index in range(brace, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1].strip()
    raise ValueError(f"Unterminated top-level block: {key}")


def _as_replace_block(block: str, key: str) -> str:
    opening = f"{key} = {{"
    if not block.startswith(opening):
        raise ValueError(f"Top-level block shape changed: {key}")
    return block.replace(opening, f"REPLACE:{opening}", 1)


def generate_price_events(data: dict, script: str) -> str:
    source = VANILLA_PRICES.read_text(encoding="utf-8-sig")
    event_ids = sorted(int(t["event_id"]) for t in all_tasks(data) if t.get("event_id") is not None)
    blocks: list[str] = []
    for event_id in event_ids:
        block = _extract_top_level_block(source, f"prices.{event_id}")
        if event_id == 30:
            old = "\t\treligion.group = religion_group:christian\n\t\treligion.group = religion_group:muslim"
            new = "\t\tOR = {\n\t\t\treligion.group = religion_group:christian\n\t\t\treligion.group = religion_group:muslim\n\t\t}"
            if old not in block:
                raise ValueError("prices.30 religion condition shape changed")
            block = block.replace(old, new, 1)
        insertion = f"\n\timmediate = {{\n\t\ttv_victory_task_prices_{event_id}_callback_effect = yes\n\t}}\n"
        marker = "\n\timage = "
        if marker not in block:
            raise ValueError(f"prices.{event_id} has no image insertion marker")
        block = block.replace(marker, insertion + marker, 1)
        blocks.append(block)
    return header(script, "Early-loaded vanilla price event patches with task callbacks.", "reference_game_files/.../prices.txt") + "\nnamespace = prices\n\n" + "\n\n".join(blocks) + "\n"


def generate_building_overrides(_data: dict, script: str) -> str:
    blocks: list[str] = []
    for building in ("university", "library"):
        callback = (
            f"INJECT:{building} = {{\n"
            "\ton_construction_ended = {\n"
            "\t\thidden_effect = {\n"
            f"\t\t\towner ?= {{ tv_victory_task_build_{building}_callback_effect = yes }}\n"
            "\t\t}\n"
            "\t}\n"
            "}"
        )
        blocks.append(callback)
    return header(script, "Minimal Library/University construction-callback injections.") + "\n" + "\n\n".join(blocks) + "\n"


def _yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def generate_localization(data: dict, script: str, *, language: str) -> str:
    zh = language == "simp_chinese"
    lang_key = "l_simp_chinese" if zh else "l_english"
    lines = [
        f"# @Generated by {script}",
        "#   Data:    data/victory_path_tasks.yaml",
        f"#   Regen:   conda run --no-capture-output -n eu5 python {script}",
        "# Do not edit directly - modify the data/generator and re-run it.",
        "",
        f"{lang_key}:",
    ]
    no_available = "无可用任务" if zh else "No Available Task"
    no_requirement = "当前没有满足出现条件的任务；系统将在月度脉冲中重试。" if zh else "No task currently satisfies the appearance rules; this slot retries on the monthly pulse."
    lines.append(f" TV_VICTORY_TASK_NO_AVAILABLE_ICON: {_yaml_quote('@trigger_fail!')}")
    lines.append(f" TV_VICTORY_TASK_NO_AVAILABLE_NAME: {_yaml_quote('@trigger_fail! ' + no_available)}")
    lines.append(f" TV_VICTORY_TASK_NO_AVAILABLE_REQUIREMENT: {_yaml_quote(no_requirement)}")
    lines.append(f" TV_VICTORY_TASK_CLAIM_HINT: {_yaml_quote('左键点击领取：对应路线节点进度 +1。' if zh else 'Left-click to claim: +1 node progress for this Victory Path.')}")
    for task in all_tasks(data):
        title = task["loc"]["zh" if zh else "en"]
        requirement = task["requirement"]["zh" if zh else "en"]
        icon = f"@{task['icon']}!"
        lines.append(f" TV_VICTORY_TASK_{task['id']}_ICON: {_yaml_quote(icon)}")
        lines.append(f" TV_VICTORY_TASK_{task['id']}_NAME: {_yaml_quote(icon + ' ' + title)}")
        for slot in SLOTS:
            path_id = task["path"]
            if task["type"] == "fixed":
                target_expr = f"[ROOT.GetVariable('{slot_prefix(path_id, slot)}_target').GetValue|0]"
                text = f"{requirement} 目标：#Y {target_expr}#!。" if zh else f"{requirement} Target: #Y {target_expr}#!."
            else:
                text = requirement
            lines.append(f" TV_VICTORY_TASK_{task['id']}_{path_id.upper()}_{slot}_REQUIREMENT: {_yaml_quote(text)}")
    for path_id in PATH_IDS:
        for slot in SLOTS:
            name = action_name(path_id, slot)
            title = "领取胜利之路任务" if zh else "Claim Victory Path Task"
            desc = "完成任务后获得该路线1点节点解锁进度，并刷新此槽位。" if zh else "Gain exactly 1 node-unlock point for this path, then refresh this slot."
            lines.append(f" {name}: {_yaml_quote(title)}")
            lines.append(f" {name}_desc: {_yaml_quote(desc)}")
    message_setup = "当我们领取一个胜利之路任务时。" if zh else "When we claim a Victory Path task."
    message_log = "我们领取了一个胜利之路任务。" if zh else "We claimed a Victory Path task."
    for path_id in PATH_IDS:
        for slot in SLOTS:
            name = action_name(path_id, slot)
            lines.append(f" PERFORM_{name}_ACTION_SETUP: {_yaml_quote(message_setup)}")
            lines.append(f" PERFORM_{name}_ACTION_LOG: {_yaml_quote(message_log)}")
            lines.append(f" PERFORM_{name}_ACTION_MAP: {_yaml_quote('')}")
    return "\n".join(lines) + "\n"
