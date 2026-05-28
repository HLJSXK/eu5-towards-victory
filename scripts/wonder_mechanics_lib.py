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
    return load_wonder_data(
        ALL_WONDER_MIN_ID,
        ALL_WONDER_MAX_ID,
        require_designs=False,
        require_buildings=True,
        require_base_modifiers=True,
    )


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
        unique_wonders.append(normalize_final_buildings(merged))
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
        return f"tv_wonder_{wonder['key']}_ceremony_modifier", wonder.get("ceremony", {}).get("modifiers", {})
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
