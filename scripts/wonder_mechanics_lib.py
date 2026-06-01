import sys
from copy import deepcopy
from pathlib import Path
import re

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
WONDERS_FILE = REPO_ROOT / "data" / "wonders.yaml"
MECHANICS_FILE = REPO_ROOT / "data" / "wonder_mechanics.yaml"
UNIQUE_WONDERS_FILE = REPO_ROOT / "data" / "unique_wonders.yaml"
GENERIC_WONDER_IMAGE_PROMPTS_FILE = REPO_ROOT / "data" / "wonder_image_prompts.yaml"
MANUAL_TV_GAME_CONCEPTS_FILE = REPO_ROOT / "src" / "main_menu" / "common" / "game_concepts" / "tv_game_concepts.txt"
ALL_WONDER_MIN_ID = 1
ALL_WONDER_MAX_ID = 40
UNIQUE_WONDER_MIN_ID = 101
UNIQUE_WONDER_MAX_ID = 140
WONDER_MECHANICS_MIN_ID = ALL_WONDER_MIN_ID
WONDER_MECHANICS_MAX_ID = UNIQUE_WONDER_MAX_ID
PARTS = ["foundation", "body", "function", "decoration"]
GAME_CONCEPT_DECL_RE = re.compile(r"^([A-Za-z0-9_]+)\s*=\s*\{$")
ROMAN_NUMERALS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
}
SUPPORTED_RITUAL_COST_TYPES = {None, "artwork", "scaled_gold", "prestige"}
SUPPORTED_UNIQUE_RITUAL_MODES = {"immediate", "timed", "auxiliary_building"}
SUPPORTED_RITUAL_LISTENERS = {"monthly", "ruler_death", "pre_winning_war", "ending_war"}
SITE_RULES_SECTION = "site_rules"


class WonderYamlDumper(yaml.SafeDumper):
    pass


def _represent_yaml_string(dumper: yaml.SafeDumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


WonderYamlDumper.add_representer(str, _represent_yaml_string)


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml_document(payload: object) -> str:
    return yaml.dump(
        payload,
        Dumper=WonderYamlDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )


def load_wonders_source_data(path: Path = WONDERS_FILE) -> dict:
    return load_yaml(path) or {}


def load_mechanics_source_data(path: Path = MECHANICS_FILE) -> dict:
    return load_yaml(path) or {}


def load_unique_wonders_source_data(path: Path = UNIQUE_WONDERS_FILE) -> dict:
    if not path.exists():
        return {"unique_wonders": []}
    return load_yaml(path) or {"unique_wonders": []}


def leading_comment_block(text: str) -> str:
    lines = text.splitlines()
    captured: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            captured.append(line.rstrip())
            continue
        break
    return "\n".join(captured).rstrip()


def save_yaml_document(path: Path, payload: object, *, preserve_leading_comments: bool = False) -> None:
    header = ""
    if preserve_leading_comments and path.exists():
        header = leading_comment_block(path.read_text(encoding="utf-8"))

    body = dump_yaml_document(payload).rstrip() + "\n"
    if header:
        path.write_text(f"{header}\n{body}", encoding="utf-8")
    else:
        path.write_text(body, encoding="utf-8")


def load_generic_wonder_image_prompts(path: Path = GENERIC_WONDER_IMAGE_PROMPTS_FILE) -> dict[str, str]:
    if not path.exists():
        return {}

    raw = load_yaml(path) or {}
    prompts = raw.get("generic_wonder_image_prompts", {})
    if not isinstance(prompts, dict):
        raise ValueError("generic_wonder_image_prompts must be a mapping")

    normalized: dict[str, str] = {}
    for key, prompt in prompts.items():
        normalized_key = str(key).strip()
        normalized_prompt = str(prompt).strip()
        if not normalized_key:
            raise ValueError("Wonder image prompt keys cannot be empty")
        if not normalized_prompt:
            raise ValueError(f"Wonder image prompt for {normalized_key} cannot be empty")
        normalized[normalized_key] = normalized_prompt
    return normalized


def load_manual_game_concept_ids(path: Path = MANUAL_TV_GAME_CONCEPTS_FILE) -> set[str]:
    if not path.exists():
        return set()

    concept_ids: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        match = GAME_CONCEPT_DECL_RE.match(raw_line.strip())
        if match:
            concept_ids.add(match.group(1))
    return concept_ids


def normalize_final_buildings(wonder: dict) -> dict:
    normalized = deepcopy(wonder)
    normalized["final_buildings"] = {
        int(style): building
        for style, building in normalized["final_buildings"].items()
    }
    normalized.setdefault("is_unique", False)
    normalized.setdefault("base_key", normalized["key"])
    normalized.setdefault("mechanic_key", normalized["base_key"])
    normalized.setdefault("base_effect_multiplier", 1)
    return normalized


def mechanic_key(wonder: dict) -> str:
    return wonder.get("mechanic_key", wonder.get("base_key", wonder["key"]))


def ceremony_styles(wonder: dict) -> list[int]:
    return sorted(int(style) for style in wonder["final_buildings"])


def normalize_loc_map(value: object, *, default: str = "") -> dict[str, str]:
    if value is None:
        return {"en": default, "zh": default}
    if isinstance(value, str):
        return {"en": value, "zh": value}
    if not isinstance(value, dict):
        raise TypeError(f"Expected localized text map or string, got {type(value)!r}")
    return {
        "en": str(value.get("en", default)),
        "zh": str(value.get("zh", default)),
    }


def normalize_script_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip("\n")
    return text


def normalize_string_list(value: object, *, default: list[str] | None = None) -> list[str]:
    if value is None:
        items = list(default or [])
    elif isinstance(value, str):
        items = [value]
    elif isinstance(value, list):
        items = [str(item) for item in value]
    else:
        raise TypeError(f"Expected string or list of strings, got {type(value)!r}")

    normalized: list[str] = []
    for item in items:
        if item not in normalized:
            normalized.append(item)
    return normalized


def indent_script_block(script: str | None, indent: int) -> list[str]:
    if not script:
        return []
    prefix = "\t" * indent
    lines: list[str] = []
    for raw_line in script.splitlines():
        if raw_line.strip():
            lines.append(f"{prefix}{raw_line.rstrip()}")
        else:
            lines.append("")
    return lines


def ritual_has_custom_completion_trigger(ritual: dict) -> bool:
    return bool(ritual.get("completion_trigger_script", ""))


def ritual_listens_to(ritual: dict, listener: str) -> bool:
    return listener in ritual.get("listeners", [])


def ritual_uses_deferred_completion(ritual: dict) -> bool:
    return ritual.get("mode") != "immediate" or ritual_has_custom_completion_trigger(ritual) or bool(ritual.get("listeners", []))


def normalize_unique_ritual(wonder: dict) -> dict:
    raw = deepcopy(wonder.get("ritual") or wonder.get("ceremony") or {})
    if not raw:
        raise ValueError(f"Unique wonder {wonder['key']} is missing ritual data")

    mode = raw.get("mode")
    if mode is None:
        if "timed" in raw:
            mode = "timed"
        elif "auxiliary_building" in raw:
            mode = "auxiliary_building"
        else:
            mode = "immediate"
    if mode not in SUPPORTED_UNIQUE_RITUAL_MODES:
        raise ValueError(f"Unsupported unique ritual mode for {wonder['key']}: {mode}")

    cost_type = raw.get("cost_type")
    if cost_type not in SUPPORTED_RITUAL_COST_TYPES:
        raise ValueError(f"Unsupported unique ritual cost_type for {wonder['key']}: {cost_type}")

    timed = deepcopy(raw.get("timed") or {})
    auxiliary_building = deepcopy(raw.get("auxiliary_building") or {})
    listeners = normalize_string_list(raw.get("listeners"), default=["monthly"] if mode == "timed" else [])
    for listener in listeners:
        if listener not in SUPPORTED_RITUAL_LISTENERS:
            raise ValueError(f"Unsupported unique ritual listener for {wonder['key']}: {listener}")

    snapshot_effect_script = normalize_script_text(raw.get("snapshot_effect_script"))
    progress_effect_script = normalize_script_text(raw.get("progress_effect_script"))
    completion_trigger_script = normalize_script_text(raw.get("completion_trigger_script"))
    runtime_variables = normalize_string_list(raw.get("runtime_variables"))

    if mode == "immediate" and (listeners or snapshot_effect_script or progress_effect_script) and not completion_trigger_script:
        raise ValueError(
            f"Immediate unique ritual {wonder['key']} needs completion_trigger_script when it uses listeners or runtime progress hooks"
        )

    if mode == "auxiliary_building" and "local_modifier" in raw and "local_modifier" not in auxiliary_building:
        auxiliary_building["local_modifier"] = deepcopy(raw["local_modifier"])

    ritual = {
        "key": raw.get("key", f"{wonder['key']}_ritual"),
        "loc": normalize_loc_map(raw.get("loc"), default=wonder["loc"]["en"]),
        "effect": normalize_loc_map(raw.get("effect"), default=""),
        "active_text": normalize_loc_map(raw.get("active_text"), default=""),
        "completion_text": normalize_loc_map(raw.get("completion_text"), default=""),
        "mode": mode,
        "cost_type": cost_type,
        "listeners": listeners,
        "runtime_variables": runtime_variables,
        "country_modifier": deepcopy(raw.get("country_modifier", raw.get("modifiers", {}))),
        "reward": deepcopy(raw.get("reward", [])),
        "confirmation_trigger_script": normalize_script_text(raw.get("confirmation_trigger_script")),
        "start_effect_script": normalize_script_text(raw.get("start_effect_script")),
        "snapshot_effect_script": snapshot_effect_script,
        "progress_effect_script": progress_effect_script,
        "completion_trigger_script": completion_trigger_script,
        "completion_effect_script": normalize_script_text(raw.get("completion_effect_script")),
        "timed": {
            "years": int(timed.get("years", 1)),
            "burden_modifier": deepcopy(timed.get("burden_modifier", {})),
            "blessing_modifier": deepcopy(timed.get("blessing_modifier", {})),
        },
        "auxiliary_building": {
            "local_modifier": deepcopy(auxiliary_building.get("local_modifier", {})),
            "maintenance": auxiliary_building.get("maintenance"),
            "build_time": auxiliary_building.get("build_time"),
            "construction_demand": auxiliary_building.get("construction_demand"),
            "price": auxiliary_building.get("price"),
            "attributes": deepcopy(auxiliary_building.get("attributes", {})),
            "max_levels": int(auxiliary_building.get("max_levels", 1)),
        },
    }
    return ritual


def unique_ritual(wonder: dict) -> dict:
    if not wonder.get("is_unique"):
        raise ValueError(f"{wonder['key']} is not a unique wonder")
    return wonder["ritual"]


def ritual_plan_for_style(wonder: dict, mechanics: dict, style: int) -> dict:
    if wonder.get("is_unique"):
        if style != 1:
            raise ValueError(f"Unique wonder {wonder['key']} only supports style 1 ritual plans")
        return unique_ritual(wonder)

    ritual = generic_ritual_for_wonder(mechanics, wonder)
    if style == 1:
        return {
            "mode": "timed",
            "cost_type": None,
            "listeners": ["monthly"],
            "runtime_variables": [],
            "country_modifier": {},
            "reward": [],
            "confirmation_trigger_script": "",
            "start_effect_script": "",
            "snapshot_effect_script": "",
            "progress_effect_script": "",
            "completion_trigger_script": "",
            "completion_effect_script": "",
            "timed": {
                "years": 1,
                "burden_modifier": {},
                "blessing_modifier": deepcopy(ritual["style_1"]["country_modifier"]),
            },
            "auxiliary_building": {
                "local_modifier": {},
                "maintenance": None,
                "build_time": None,
                "construction_demand": None,
                "price": None,
                "attributes": {},
                "max_levels": 1,
            },
        }
    if style == 2:
        return {
            "mode": "auxiliary_building",
            "cost_type": None,
            "listeners": [],
            "runtime_variables": [],
            "country_modifier": {},
            "reward": [],
            "confirmation_trigger_script": "",
            "start_effect_script": "",
            "snapshot_effect_script": "",
            "progress_effect_script": "",
            "completion_trigger_script": "",
            "completion_effect_script": "",
            "timed": {
                "years": 1,
                "burden_modifier": {},
                "blessing_modifier": {},
            },
            "auxiliary_building": {
                "local_modifier": deepcopy(ritual["style_2"]["local_modifier"]),
                "maintenance": None,
                "build_time": None,
                "construction_demand": None,
                "price": None,
                "attributes": {},
                "max_levels": 1,
            },
        }
    if style == 3:
        return {
            "mode": "immediate",
            "cost_type": ritual["style_3"]["cost_type"],
            "listeners": [],
            "runtime_variables": [],
            "country_modifier": {},
            "reward": deepcopy(ritual["style_3"]["reward"]),
            "confirmation_trigger_script": "",
            "start_effect_script": "",
            "snapshot_effect_script": "",
            "progress_effect_script": "",
            "completion_trigger_script": "",
            "completion_effect_script": "",
            "timed": {
                "years": 1,
                "burden_modifier": {},
                "blessing_modifier": {},
            },
            "auxiliary_building": {
                "local_modifier": {},
                "maintenance": None,
                "build_time": None,
                "construction_demand": None,
                "price": None,
                "attributes": {},
                "max_levels": 1,
            },
        }
    raise ValueError(f"Unsupported ritual style for {wonder['key']}: {style}")


def load_wonder_data(
    min_id: int = ALL_WONDER_MIN_ID,
    max_id: int = ALL_WONDER_MAX_ID,
    *,
    require_designs: bool = True,
    require_buildings: bool = True,
    require_base_modifiers: bool = True,
) -> tuple[list[dict], dict]:
    wonders_data = load_wonders_source_data()
    mechanics = load_mechanics_source_data()
    wonders = [
        normalize_final_buildings(wonder)
        for wonder in wonders_data["wonders"]
        if min_id <= int(wonder["id"]) <= max_id
    ]
    for wonder in wonders:
        key = wonder["key"]
        if require_designs and key not in mechanics["designs"]:
            raise ValueError(f"Missing design data for {key}")
        if require_buildings and key not in mechanics["buildings"]:
            raise ValueError(f"Missing building data for {key}")
        if require_base_modifiers and key not in mechanics["base_modifiers"]:
            raise ValueError(f"Missing base modifier data for {key}")
    return wonders, mechanics


def load_generic_wonder_mechanics_data() -> tuple[list[dict], dict]:
    wonders, mechanics = load_wonder_data(
        ALL_WONDER_MIN_ID,
        ALL_WONDER_MAX_ID,
        require_designs=False,
        require_buildings=True,
        require_base_modifiers=True,
    )
    generic_rituals = mechanics.get("generic_rituals", {})
    for wonder in wonders:
        if wonder["key"] not in generic_rituals:
            raise ValueError(f"Missing generic ritual data for {wonder['key']}")
    return wonders, mechanics


def load_unique_wonders() -> list[dict]:
    if not UNIQUE_WONDERS_FILE.exists():
        return []
    wonders_data = load_wonders_source_data()
    mechanics = load_mechanics_source_data()
    unique_data = load_unique_wonders_source_data()
    base_by_key = {
        wonder["key"]: normalize_final_buildings(wonder)
        for wonder in wonders_data["wonders"]
    }
    unique_wonders: list[dict] = []
    for raw in unique_data.get("unique_wonders", []):
        base_key = raw["base_key"]
        if base_key not in base_by_key:
            raise ValueError(f"Unknown base wonder for unique wonder {raw['key']}: {base_key}")
        if base_key not in mechanics["buildings"]:
            raise ValueError(f"Missing building data for base wonder {base_key}")
        if base_key not in mechanics["base_modifiers"]:
            raise ValueError(f"Missing base modifier data for base wonder {base_key}")
        base = deepcopy(base_by_key[base_key])
        key = raw["key"]
        merged = {
            **base,
            **raw,
            "is_unique": True,
            "base_key": base_key,
            "mechanic_key": base_key,
            "fixed_location": raw["location"],
            "base_effect_multiplier": raw.get("base_effect_multiplier", 2),
            "final_buildings": raw.get(
                "final_buildings",
                {1: raw.get("final_building", f"tv_wonder_{key}_inaugurated")},
            ),
        }
        normalized = normalize_final_buildings(merged)
        normalized["ritual"] = normalize_unique_ritual(normalized)
        if ceremony_styles(normalized) != [1]:
            raise ValueError(f"Unique wonder {key} must currently expose exactly one ceremony style")
        unique_wonders.append(normalized)
    return unique_wonders


def load_all_wonder_mechanics_data(*, include_unique: bool = True) -> tuple[list[dict], dict]:
    wonders, mechanics = load_generic_wonder_mechanics_data()
    if include_unique:
        wonders.extend(load_unique_wonders())
    return wonders, mechanics


def load_generic_wonder_mechanics() -> tuple[list[dict], dict]:
    return load_generic_wonder_mechanics_data()


def load_all_wonder_mechanics(*, include_unique: bool = True) -> tuple[list[dict], dict]:
    return load_all_wonder_mechanics_data(include_unique=include_unique)


def legacy_site_trigger_lines(key: str, indent: int = 1) -> list[str]:
    prefix = "\t" * indent
    lines: list[str] = []
    if key in {"sacred_mountain", "giant_observatory", "mountain_terrace_network"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\ttopography = mountains",
            f"{prefix}\ttopography = plateau",
            f"{prefix}\ttopography = hills",
            f"{prefix}}}",
        ])
    elif key in {"triumphal_axis", "city_expansion_project"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\tlocation_rank ?= location_rank:city",
            f"{prefix}\tlocation_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    elif key in {"great_port", "great_lighthouse", "national_shipyard", "coastal_beacon_network", "maritime_trade_station_network"}:
        lines.append(f"{prefix}is_port = yes")
    elif key == "giant_necropolis":
        lines.append(f"{prefix}location_rank ?= location_rank:rural_settlement")
    elif key in {"hydraulic_workshop", "river_extension"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\thas_river = yes",
            f"{prefix}\tis_adjacent_to_lake = yes",
            f"{prefix}}}",
        ])
    elif key == "mining_city":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\traw_material = goods:iron",
            f"{prefix}\traw_material = goods:copper",
            f"{prefix}\traw_material = goods:tin",
            f"{prefix}\traw_material = goods:lead",
            f"{prefix}\traw_material = goods:silver",
            f"{prefix}\traw_material = goods:goods_gold",
            f"{prefix}}}",
        ])
    elif key in {"palace_of_nations", "library_of_nation"}:
        lines.append(f"{prefix}is_capital = yes")
    elif key in {
        "university_city",
        "star_fortress_city",
        "giant_armory",
        "war_college_system",
        "great_clock_bell_system",
        "grand_theater_festival_district",
        "guild_alliance",
        "giant_workshop_complex",
    }:
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:rural_settlement }}")
    elif key == "sky_dome_grand_temple":
        lines.append(f"{prefix}dominant_religion = owner.religion")
    elif key == "giant_tower_temple":
        lines.append(f"{prefix}always = yes")
    elif key == "great_wall":
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:city }}")
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:megalopolis }}")
    elif key in {"large_canal_system", "giant_dam_project", "canal_hub_city"}:
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\thas_river = yes",
            f"{prefix}\tis_adjacent_to_lake = yes",
            f"{prefix}\tis_port = yes",
            f"{prefix}}}",
        ])
        if key == "canal_hub_city":
            lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:rural_settlement }}")
    elif key in {"royal_granary_system", "imperial_post_road_network", "law_code_stele_project"}:
        lines.append(f"{prefix}always = yes")
    elif key == "frontier_colonization_belt":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\tlocation_rank ?= location_rank:rural_settlement",
            f"{prefix}\ttopography = hills",
            f"{prefix}}}",
        ])
    elif key == "knightly_fortress_order":
        lines.append(f"{prefix}NOT = {{ location_rank ?= location_rank:rural_settlement }}")
    elif key == "royal_art_district":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\tis_capital = yes",
            f"{prefix}\tlocation_rank ?= location_rank:city",
            f"{prefix}\tlocation_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    elif key == "world_embassy_quarter":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\tis_capital = yes",
            f"{prefix}\tNOT = {{ location_rank ?= location_rank:rural_settlement }}",
            f"{prefix}}}",
        ])
    elif key == "world_market":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\tis_port = yes",
            f"{prefix}\tlocation_rank ?= location_rank:city",
            f"{prefix}\tlocation_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    elif key == "royal_mint_system":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\tlocation_rank ?= location_rank:city",
            f"{prefix}\tlocation_rank ?= location_rank:megalopolis",
            f"{prefix}\traw_material = goods:goods_gold",
            f"{prefix}\traw_material = goods:silver",
            f"{prefix}\traw_material = goods:copper",
            f"{prefix}}}",
        ])
    elif key == "world_monument_group":
        lines.extend([
            f"{prefix}OR = {{",
            f"{prefix}\tis_capital = yes",
            f"{prefix}\tlocation_rank ?= location_rank:city",
            f"{prefix}\tlocation_rank ?= location_rank:megalopolis",
            f"{prefix}}}",
        ])
    else:
        raise ValueError(f"No site trigger mapping for {key}")
    return lines


def legacy_site_preference_lines(key: str, indent: int = 2) -> list[str]:
    prefix = "\t" * indent
    lines: list[str] = []

    def bonus(value: str | int | float) -> None:
        lines.append(f"{prefix}tv_wonder_change_all_survey_competence_target_effect = {{ value = {value} }}")

    if key == "sacred_mountain":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = hills }} }}")
        bonus(0)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ vegetation = forest }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ vegetation = woods }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key in {"triumphal_axis", "palace_of_nations"}:
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.2 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:megalopolis }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key in {"great_port", "great_lighthouse"}:
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.modifier:harbor_suitability }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 1 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 25 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "giant_necropolis":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = hills }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ any_neighbor_location = {{ tv_wonder_location_is_city_trigger = yes }} }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ any_neighbor_location = {{ tv_wonder_location_is_town_trigger = yes }} }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key == "hydraulic_workshop":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.total_building_levels }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.25 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "city_expansion_project":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.total_building_levels }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.25 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:megalopolis }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "mining_city":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.2 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:rural_settlement }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "giant_observatory":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.average_location_literacy }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "university_city":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:city }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:megalopolis }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.average_location_literacy }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.2 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key in {"sky_dome_grand_temple", "giant_tower_temple"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:monastery }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:cathedral }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ dominant_religion = owner.religion }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
    elif key == "river_extension":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:bridge_infrastructure }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ any_neighbor_location = {{ has_building = building_type:tv_wonder_bridge_opening }} }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "national_shipyard":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.modifier:harbor_suitability }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 1 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 15 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "star_fortress_city":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ modifier:fort_level > 0 }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ location_rank ?= location_rank:city location_rank ?= location_rank:megalopolis }} }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key == "great_wall":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ modifier:fort_level > 0 }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:rural_settlement }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key == "giant_armory":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ has_building = building_type:armory }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ location_rank ?= location_rank:city location_rank ?= location_rank:megalopolis }} }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.15 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key == "library_of_nation":
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.15 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:city }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:megalopolis }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    elif key in {"large_canal_system", "giant_dam_project", "canal_hub_city"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ has_river = yes is_adjacent_to_lake = yes is_port = yes }} }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
        if key == "canal_hub_city":
            lines.append(f"{prefix}if = {{")
            lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ location_rank ?= location_rank:city location_rank ?= location_rank:megalopolis }} }} }}")
            bonus(5)
            lines.append(f"{prefix}}}")
    elif key == "mountain_terrace_network":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = plateau }} }}")
        bonus(7.5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}else_if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = hills }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
    elif key in {"royal_granary_system", "frontier_colonization_belt"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ location_rank ?= location_rank:rural_settlement }} }}")
        bonus(10 if key == "frontier_colonization_belt" else 5)
        lines.append(f"{prefix}}}")
    elif key in {"coastal_beacon_network", "maritime_trade_station_network"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ is_port = yes }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
    elif key == "knightly_fortress_order":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ modifier:fort_level > 0 }} }}")
        bonus(5)
        lines.append(f"{prefix}}}")
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ topography = mountains }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")
    elif key == "royal_mint_system":
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ OR = {{ raw_material = goods:goods_gold raw_material = goods:silver raw_material = goods:copper }} }} }}")
        bonus(15)
        lines.append(f"{prefix}}}")
    elif key in {"royal_art_district", "world_embassy_quarter", "law_code_stele_project", "world_monument_group"}:
        lines.append(f"{prefix}if = {{")
        lines.append(f"{prefix}\tlimit = {{ var:tv_wonder_survey_site ?= {{ is_capital = yes }} }}")
        bonus(10)
        lines.append(f"{prefix}}}")

    if key not in {
        "sacred_mountain",
        "triumphal_axis",
        "great_port",
        "giant_necropolis",
        "great_lighthouse",
        "hydraulic_workshop",
        "city_expansion_project",
        "mining_city",
        "giant_observatory",
        "palace_of_nations",
        "university_city",
        "sky_dome_grand_temple",
        "giant_tower_temple",
        "river_extension",
        "national_shipyard",
        "star_fortress_city",
        "great_wall",
        "giant_armory",
        "library_of_nation",
        "mountain_terrace_network",
        "coastal_beacon_network",
        "maritime_trade_station_network",
    }:
        lines.append(f"{prefix}set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.development }}")
        lines.append(f"{prefix}clamp_variable = {{ name = tv_wonder_site_preference_bonus min = 0 max = 100 }}")
        lines.append(f"{prefix}change_variable = {{ name = tv_wonder_site_preference_bonus multiply = 0.1 }}")
        bonus("var:tv_wonder_site_preference_bonus")
        lines.append(f"{prefix}remove_variable = tv_wonder_site_preference_bonus")
    return lines


def site_rule_config(mechanics: dict, key: str) -> dict:
    return mechanics.get(SITE_RULES_SECTION, {}).get(key, {}) or {}


def site_trigger_script_for_key(mechanics: dict, key: str) -> str:
    override = normalize_script_text(site_rule_config(mechanics, key).get("trigger_script"))
    if override:
        return override
    return "\n".join(legacy_site_trigger_lines(key, 0)).strip()


def site_preference_script_for_key(mechanics: dict, key: str) -> str:
    override = normalize_script_text(site_rule_config(mechanics, key).get("preference_script"))
    if override:
        return override
    return "\n".join(legacy_site_preference_lines(key, 0)).strip()


def site_trigger_lines_for_wonder(mechanics: dict, wonder: dict, indent: int = 1) -> list[str]:
    key = mechanic_key(wonder)
    override = normalize_script_text(site_rule_config(mechanics, key).get("trigger_script"))
    if override:
        return indent_script_block(override, indent)
    return legacy_site_trigger_lines(key, indent)


def site_preference_lines_for_wonder(mechanics: dict, wonder: dict, indent: int = 2) -> list[str]:
    key = mechanic_key(wonder)
    override = normalize_script_text(site_rule_config(mechanics, key).get("preference_script"))
    if override:
        return indent_script_block(override, indent)
    return legacy_site_preference_lines(key, indent)


def render_header(script_rel: str, data_rel: str = "data/wonders.yaml + data/wonder_mechanics.yaml + data/unique_wonders.yaml") -> list[str]:
    return [
        f"# @Generated by {script_rel}",
        f"#   Data:    {data_rel}",
        f"#   Regen:   conda run --no-capture-output -n eu5 python {script_rel}",
        "# Do not edit directly - modify the data file and re-run the generator.",
        "",
    ]


def upper_key(key: str) -> str:
    return key.upper()


def q(text: str) -> str:
    return text.replace('"', '\\"')


def all_final_buildings(wonders: list[dict]) -> list[str]:
    buildings: list[str] = []
    for wonder in wonders:
        for building in wonder["final_buildings"].values():
            if building not in buildings:
                buildings.append(building)
    return buildings


def loc_line(key: str, value: str) -> str:
    return f' {key}:0 "{q(value)}"'


def level_static_modifier_loc(concept: str, level: int) -> str:
    numeral = ROMAN_NUMERALS.get(level)
    if numeral is None:
        raise ValueError(f"Unsupported wonder level for localization: {level}")
    return f"[{concept}|E] {numeral}"


def final_building_for_style(wonder: dict, style: int) -> str:
    if style in wonder["final_buildings"]:
        return wonder["final_buildings"][style]
    if str(style) in wonder["final_buildings"]:
        return wonder["final_buildings"][str(style)]
    raise KeyError(f"{wonder['key']} has no final building for ceremony style {style}")


def wonder_image_name(wonder: dict) -> str:
    return str(wonder.get("image") or f"tv_wonder_{wonder['key']}")


def wonder_image_prompt(wonder: dict, generic_prompts: dict[str, str] | None = None) -> str:
    prompt = str(wonder.get("prompt") or "").strip()
    if prompt:
        return prompt

    prompts = generic_prompts or {}
    if wonder.get("is_unique"):
        raise ValueError(f"Unique wonder {wonder['key']} is missing an image prompt")

    prompt = str(prompts.get(wonder["key"]) or "").strip()
    if not prompt:
        raise ValueError(f"Generic wonder {wonder['key']} is missing an image prompt")
    return prompt


def load_wonder_image_tasks(*, include_unique: bool = True) -> list[dict]:
    wonders, _ = load_all_wonder_mechanics_data(include_unique=include_unique)
    generic_prompts = load_generic_wonder_image_prompts()
    generic_keys = {wonder["key"] for wonder in wonders if not wonder.get("is_unique")}

    missing_generic_prompts = sorted(key for key in generic_keys if key not in generic_prompts)
    if missing_generic_prompts:
        raise ValueError(
            "Missing generic wonder image prompts for: "
            + ", ".join(missing_generic_prompts)
        )

    extra_generic_prompts = sorted(key for key in generic_prompts if key not in generic_keys)
    if extra_generic_prompts:
        raise ValueError(
            "Unknown generic wonder image prompt keys: "
            + ", ".join(extra_generic_prompts)
        )

    tasks: list[dict] = []
    for wonder in wonders:
        tasks.append(
            {
                "id": int(wonder["id"]),
                "key": wonder["key"],
                "name": wonder_image_name(wonder),
                "prompt": wonder_image_prompt(wonder, generic_prompts),
                "is_unique": bool(wonder.get("is_unique")),
            }
        )
    return tasks


def final_building_maintenance(wonder: dict, building_design: dict, building: str) -> str:
    return building_design.get("final_maintenance", {}).get(building, building_design.get("maintenance", wonder["maintenance"]))


def ceremony_modifier_for_building(wonder: dict, mechanics: dict, building: str) -> tuple[str, dict] | None:
    if wonder.get("is_unique"):
        modifier_data = unique_ritual(wonder).get("country_modifier", {})
        if not modifier_data:
            return None
        return f"tv_wonder_{wonder['key']}_ceremony_modifier", modifier_data
    modifier_name = mechanics.get("ceremony_modifier_names", {}).get(wonder["key"], {}).get(building, f"{building}_modifier")
    ceremony_modifiers = mechanics.get("ceremony_modifiers", {})
    if modifier_name in ceremony_modifiers:
        return modifier_name, ceremony_modifiers[modifier_name]
    if building in ceremony_modifiers:
        return modifier_name, ceremony_modifiers[building]
    return None


def ceremony_modifier_for_style(wonder: dict, mechanics: dict, style: int) -> tuple[str, dict] | None:
    if style not in wonder["final_buildings"] and str(style) not in wonder["final_buildings"]:
        return None
    return ceremony_modifier_for_building(wonder, mechanics, final_building_for_style(wonder, style))


def generic_ritual_for_wonder(mechanics: dict, wonder: dict) -> dict:
    return mechanics["generic_rituals"][wonder["key"]]


def ritual_auxiliary_building(wonder: dict) -> str:
    return f"tv_wonder_{wonder['key']}_ritual_annex"


def ritual_burden_modifier_name(wonder: dict) -> str:
    if wonder.get("is_unique"):
        return f"tv_wonder_{wonder['key']}_ritual_burden_modifier"
    return f"tv_wonder_{wonder['key']}_ritual_burden_modifier"


def ritual_blessing_modifier_name(wonder: dict) -> str:
    if wonder.get("is_unique"):
        return f"tv_wonder_{wonder['key']}_ritual_blessing_modifier"
    return f"tv_wonder_{wonder['key']}_ritual_blessing_modifier"
