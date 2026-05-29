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
MANUAL_TV_GAME_CONCEPTS_FILE = REPO_ROOT / "src" / "main_menu" / "common" / "game_concepts" / "tv_game_concepts.txt"
ALL_WONDER_MIN_ID = 1
ALL_WONDER_MAX_ID = 39
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


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


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
    wonders_data = load_yaml(WONDERS_FILE)
    mechanics = load_yaml(MECHANICS_FILE)
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
    wonders_data = load_yaml(WONDERS_FILE)
    mechanics = load_yaml(MECHANICS_FILE)
    unique_data = load_yaml(UNIQUE_WONDERS_FILE)
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
