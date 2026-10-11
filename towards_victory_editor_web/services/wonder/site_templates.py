"""Site condition atoms, preference presets and template signatures."""
from __future__ import annotations

import json

from .values import normalize_multiline_editor_text


def normalize_inline_script(text: str) -> str:
    return " ".join(normalize_multiline_editor_text(text).split())


def _site_value_row(value: str) -> dict[str, str]:
    return {"value": value}


def _bonus_rule(branch: str, condition: str, value: str | int | float) -> dict[str, str]:
    return {
        "branch": branch,
        "condition": condition,
        "value": str(value),
    }


def _scaled_rule(source: str, minimum: str | int | float, maximum: str | int | float, multiplier: str | int | float) -> dict[str, str]:
    return {
        "source": source,
        "min": str(minimum),
        "max": str(maximum),
        "multiplier": str(multiplier),
    }


TRIGGER_CONDITION_OPTIONS = [
    {"value": "is_port", "label": "Port location", "script": "is_port = yes"},
    {"value": "is_capital", "label": "Capital location", "script": "is_capital = yes"},
    {
        "value": "not_capital_continent",
        "label": "Different continent from capital",
        "script": "AND = { has_owner = yes NOT = { continent = owner.capital.continent } }",
    },
    {"value": "has_river", "label": "Has river", "script": "has_river = yes"},
    {"value": "adjacent_lake", "label": "Adjacent to lake", "script": "is_adjacent_to_lake = yes"},
    {
        "value": "dominant_religion_owner",
        "label": "Dominant religion matches owner",
        "script": "dominant_religion = owner.religion",
    },
    {"value": "topography_mountains", "label": "Topography: mountains", "script": "topography = mountains"},
    {"value": "topography_plateau", "label": "Topography: plateau", "script": "topography = plateau"},
    {"value": "topography_hills", "label": "Topography: hills", "script": "topography = hills"},
    {"value": "rank_rural", "label": "Rank: rural settlement", "script": "location_rank ?= location_rank:rural_settlement"},
    {"value": "rank_city", "label": "Rank: city", "script": "location_rank ?= location_rank:city"},
    {"value": "rank_megalopolis", "label": "Rank: megalopolis", "script": "location_rank ?= location_rank:megalopolis"},
    {
        "value": "not_rural",
        "label": "Not rural settlement",
        "script": "NOT = { location_rank ?= location_rank:rural_settlement }",
    },
    {"value": "not_city", "label": "Not city", "script": "NOT = { location_rank ?= location_rank:city }"},
    {
        "value": "not_megalopolis",
        "label": "Not megalopolis",
        "script": "NOT = { location_rank ?= location_rank:megalopolis }",
    },
    {"value": "raw_iron", "label": "Raw material: iron", "script": "raw_material = goods:iron"},
    {"value": "raw_copper", "label": "Raw material: copper", "script": "raw_material = goods:copper"},
    {"value": "raw_tin", "label": "Raw material: tin", "script": "raw_material = goods:tin"},
    {"value": "raw_lead", "label": "Raw material: lead", "script": "raw_material = goods:lead"},
    {"value": "raw_silver", "label": "Raw material: silver", "script": "raw_material = goods:silver"},
    {"value": "raw_gold", "label": "Raw material: gold", "script": "raw_material = goods:goods_gold"},
]
TRIGGER_CONDITION_BY_ID = {item["value"]: item for item in TRIGGER_CONDITION_OPTIONS}
TRIGGER_CONDITION_SCRIPT_TO_ID = {
    normalize_inline_script(item["script"]): item["value"] for item in TRIGGER_CONDITION_OPTIONS
}
TRIGGER_TEMPLATE_PRESETS = [
    {"id": "always", "label": "No site restriction", "any_of": [], "all_of": []},
    {
        "id": "mountain_plateau_hills",
        "label": "Mountains / plateau / hills",
        "any_of": ["topography_mountains", "topography_plateau", "topography_hills"],
        "all_of": [],
    },
    {
        "id": "city_or_megalopolis",
        "label": "City or megalopolis",
        "any_of": ["rank_city", "rank_megalopolis"],
        "all_of": [],
    },
    {"id": "port_only", "label": "Port only", "any_of": ["is_port"], "all_of": []},
    {"id": "rural_only", "label": "Rural settlement only", "any_of": ["rank_rural"], "all_of": []},
    {
        "id": "river_or_lake",
        "label": "River or adjacent lake",
        "any_of": ["has_river", "adjacent_lake"],
        "all_of": [],
    },
    {
        "id": "mineral_site",
        "label": "Mineral-producing site",
        "any_of": ["raw_iron", "raw_copper", "raw_tin", "raw_lead", "raw_silver", "raw_gold"],
        "all_of": [],
    },
    {"id": "capital_only", "label": "Capital only", "any_of": ["is_capital"], "all_of": []},
    {
        "id": "different_continent_from_capital",
        "label": "Different continent from capital",
        "any_of": [],
        "all_of": ["not_capital_continent"],
    },
    {"id": "non_rural", "label": "Non-rural site", "any_of": [], "all_of": ["not_rural"]},
    {
        "id": "owner_religion_majority",
        "label": "Owner religion majority",
        "any_of": ["dominant_religion_owner"],
        "all_of": [],
    },
    {
        "id": "not_city_or_megalopolis",
        "label": "Not city and not megalopolis",
        "any_of": [],
        "all_of": ["not_city", "not_megalopolis"],
    },
    {
        "id": "waterway_or_port",
        "label": "River / lake / port",
        "any_of": ["has_river", "adjacent_lake", "is_port"],
        "all_of": [],
    },
    {
        "id": "waterway_or_port_non_rural",
        "label": "River / lake / port and non-rural",
        "any_of": ["has_river", "adjacent_lake", "is_port"],
        "all_of": ["not_rural"],
    },
    {
        "id": "rural_or_hills",
        "label": "Rural settlement or hills",
        "any_of": ["rank_rural", "topography_hills"],
        "all_of": [],
    },
    {
        "id": "capital_or_city_or_megalopolis",
        "label": "Capital / city / megalopolis",
        "any_of": ["is_capital", "rank_city", "rank_megalopolis"],
        "all_of": [],
    },
    {
        "id": "capital_or_non_rural",
        "label": "Capital or non-rural",
        "any_of": ["is_capital", "not_rural"],
        "all_of": [],
    },
    {
        "id": "port_or_city_or_megalopolis",
        "label": "Port / city / megalopolis",
        "any_of": ["is_port", "rank_city", "rank_megalopolis"],
        "all_of": [],
    },
    {
        "id": "city_megalopolis_or_coin_metal",
        "label": "City / megalopolis / gold / silver / copper",
        "any_of": ["rank_city", "rank_megalopolis", "raw_gold", "raw_silver", "raw_copper"],
        "all_of": [],
    },
]
TRIGGER_PRESET_BY_ID = {item["id"]: item for item in TRIGGER_TEMPLATE_PRESETS}
PREFERENCE_CONDITION_OPTIONS = [
    {"value": "topography_mountains", "label": "Topography: mountains", "script": "topography = mountains"},
    {"value": "topography_plateau", "label": "Topography: plateau", "script": "topography = plateau"},
    {"value": "topography_hills", "label": "Topography: hills", "script": "topography = hills"},
    {"value": "vegetation_forest", "label": "Vegetation: forest", "script": "vegetation = forest"},
    {"value": "vegetation_woods", "label": "Vegetation: woods", "script": "vegetation = woods"},
    {
        "value": "vegetation_forest_or_woods",
        "label": "Vegetation: forest or woods",
        "script": "OR = { vegetation = forest vegetation = woods }",
    },
    {"value": "rank_rural", "label": "Rank: rural settlement", "script": "location_rank ?= location_rank:rural_settlement"},
    {"value": "rank_city", "label": "Rank: city", "script": "location_rank ?= location_rank:city"},
    {"value": "rank_megalopolis", "label": "Rank: megalopolis", "script": "location_rank ?= location_rank:megalopolis"},
    {
        "value": "neighbor_city",
        "label": "Adjacent to city",
        "script": "any_neighbor_location = { tv_wonder_location_is_city_trigger = yes }",
    },
    {
        "value": "neighbor_town",
        "label": "Adjacent to town",
        "script": "any_neighbor_location = { tv_wonder_location_is_town_trigger = yes }",
    },
    {
        "value": "has_monastery",
        "label": "Has monastery",
        "script": "has_building = building_type:monastery",
    },
    {
        "value": "has_cathedral",
        "label": "Has cathedral",
        "script": "has_building = building_type:cathedral",
    },
    {
        "value": "dominant_religion_owner",
        "label": "Dominant religion matches owner",
        "script": "dominant_religion = owner.religion",
    },
    {
        "value": "has_bridge_infrastructure",
        "label": "Has bridge infrastructure",
        "script": "has_building = building_type:bridge_infrastructure",
    },
    {
        "value": "neighbor_bridge_opening",
        "label": "Adjacent to River Extension",
        "script": "any_neighbor_location = { has_building = building_type:tv_wonder_bridge_opening }",
    },
    {
        "value": "waterway_or_port",
        "label": "River / lake / port",
        "script": "OR = { has_river = yes is_adjacent_to_lake = yes is_port = yes }",
    },
    {"value": "is_port", "label": "Port location", "script": "is_port = yes"},
    {"value": "fort_level", "label": "Has fort level", "script": "modifier:fort_level > 0"},
    {
        "value": "urban_rank",
        "label": "City or megalopolis",
        "script": "OR = { location_rank ?= location_rank:city location_rank ?= location_rank:megalopolis }",
    },
    {"value": "is_capital", "label": "Capital location", "script": "is_capital = yes"},
    {
        "value": "raw_coin_metal",
        "label": "Gold / silver / copper",
        "script": "OR = { raw_material = goods:goods_gold raw_material = goods:silver raw_material = goods:copper }",
    },
    {"value": "has_armory", "label": "Has armory", "script": "has_building = building_type:armory"},
]
PREFERENCE_CONDITION_BY_ID = {item["value"]: item for item in PREFERENCE_CONDITION_OPTIONS}
PREFERENCE_CONDITION_SCRIPT_TO_ID = {
    normalize_inline_script(item["script"]): item["value"] for item in PREFERENCE_CONDITION_OPTIONS
}
PREFERENCE_BRANCH_OPTIONS = [
    {"value": "if", "label": "if"},
    {"value": "else_if", "label": "else_if"},
]
PREFERENCE_SCALE_SOURCE_OPTIONS = [
    {
        "value": "development",
        "label": "Development",
        "path": "development",
        "default_min": "0",
        "default_max": "100",
        "default_multiplier": "0.1",
    },
    {
        "value": "total_building_levels",
        "label": "Total building levels",
        "path": "total_building_levels",
        "default_min": "0",
        "default_max": "100",
        "default_multiplier": "0.25",
    },
    {
        "value": "harbor_suitability",
        "label": "Harbor suitability",
        "path": "modifier:harbor_suitability",
        "default_min": "0",
        "default_max": "1",
        "default_multiplier": "25",
    },
    {
        "value": "free_building_levels",
        "label": "Supported building levels",
        "path": "modifier:free_building_levels",
        "default_min": "0",
        "default_max": "200",
        "default_multiplier": "0.1",
    },
    {
        "value": "average_location_literacy",
        "label": "Average literacy",
        "path": "average_location_literacy",
        "default_min": "0",
        "default_max": "100",
        "default_multiplier": "0.1",
    },
]
PREFERENCE_SCALE_SOURCE_BY_ID = {item["value"]: item for item in PREFERENCE_SCALE_SOURCE_OPTIONS}
PREFERENCE_SCALE_SOURCE_PATH_TO_ID = {item["path"]: item["value"] for item in PREFERENCE_SCALE_SOURCE_OPTIONS}
PREFERENCE_TEMPLATE_PRESETS = [
    {
        "id": "mountain_vegetation_chain",
        "label": "Mountain / vegetation chain",
        "bonus_rules": [
            _bonus_rule("if", "topography_mountains", 15),
            _bonus_rule("else_if", "topography_plateau", 7.5),
            _bonus_rule("else_if", "topography_hills", 0),
            _bonus_rule("if", "vegetation_forest", 10),
            _bonus_rule("else_if", "vegetation_woods", 5),
        ],
        "scaled_rules": [],
    },
    {
        "id": "development_020_megalopolis_5",
        "label": "Development scale + megalopolis bonus",
        "bonus_rules": [_bonus_rule("if", "rank_megalopolis", 5)],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.2)],
    },
    {
        "id": "harbor_25_scale",
        "label": "Harbor suitability scale",
        "bonus_rules": [],
        "scaled_rules": [_scaled_rule("harbor_suitability", 0, 1, 25)],
    },
    {
        "id": "hills_with_neighbor_settlement",
        "label": "Hills + neighboring settlement",
        "bonus_rules": [
            _bonus_rule("if", "topography_hills", 15),
            _bonus_rule("if", "neighbor_city", 10),
            _bonus_rule("else_if", "neighbor_town", 5),
        ],
        "scaled_rules": [],
    },
    {
        "id": "building_levels_025",
        "label": "Total building levels scale",
        "bonus_rules": [],
        "scaled_rules": [_scaled_rule("total_building_levels", 0, 100, 0.25)],
    },
    {
        "id": "development_020_rural_5",
        "label": "Development scale + rural bonus",
        "bonus_rules": [_bonus_rule("if", "rank_rural", 5)],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.2)],
    },
    {
        "id": "mountain_literacy_scale",
        "label": "Mountain / plateau + literacy scale",
        "bonus_rules": [
            _bonus_rule("if", "topography_mountains", 15),
            _bonus_rule("else_if", "topography_plateau", 7.5),
        ],
        "scaled_rules": [_scaled_rule("average_location_literacy", 0, 100, 0.1)],
    },
    {
        "id": "urban_literacy_scale",
        "label": "Urban rank + literacy scale",
        "bonus_rules": [
            _bonus_rule("if", "rank_city", 5),
            _bonus_rule("else_if", "rank_megalopolis", 5),
        ],
        "scaled_rules": [_scaled_rule("average_location_literacy", 0, 100, 0.2)],
    },
    {
        "id": "religious_buildings_and_share",
        "label": "Religious buildings + religion share",
        "bonus_rules": [
            _bonus_rule("if", "has_monastery", 5),
            _bonus_rule("if", "has_cathedral", 5),
            _bonus_rule("if", "dominant_religion_owner", 15),
        ],
        "scaled_rules": [],
    },
    {
        "id": "development_bridge_network",
        "label": "Development scale + bridge network",
        "bonus_rules": [
            _bonus_rule("if", "has_bridge_infrastructure", 5),
            _bonus_rule("if", "neighbor_bridge_opening", 10),
        ],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "harbor_15_plus_development",
        "label": "Harbor scale + development scale",
        "bonus_rules": [],
        "scaled_rules": [
            _scaled_rule("harbor_suitability", 0, 1, 15),
            _scaled_rule("development", 0, 100, 0.1),
        ],
    },
    {
        "id": "fortified_mountain_urban",
        "label": "Mountain / plateau + fort + urban",
        "bonus_rules": [
            _bonus_rule("if", "topography_mountains", 15),
            _bonus_rule("else_if", "topography_plateau", 7.5),
            _bonus_rule("if", "fort_level", 5),
            _bonus_rule("if", "urban_rank", 5),
        ],
        "scaled_rules": [],
    },
    {
        "id": "fortified_mountain_rural",
        "label": "Mountain / plateau + fort + rural",
        "bonus_rules": [
            _bonus_rule("if", "topography_mountains", 15),
            _bonus_rule("else_if", "topography_plateau", 7.5),
            _bonus_rule("if", "fort_level", 5),
            _bonus_rule("if", "rank_rural", 5),
        ],
        "scaled_rules": [],
    },
    {
        "id": "armory_urban_development",
        "label": "Armory + urban + development scale",
        "bonus_rules": [
            _bonus_rule("if", "has_armory", 5),
            _bonus_rule("if", "urban_rank", 5),
        ],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.15)],
    },
    {
        "id": "development_015_city_5_megalopolis_10",
        "label": "Development scale + city/megalopolis bonus",
        "bonus_rules": [
            _bonus_rule("if", "rank_city", 5),
            _bonus_rule("else_if", "rank_megalopolis", 10),
        ],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.15)],
    },
    {
        "id": "waterway_development",
        "label": "Waterway bonus + development scale",
        "bonus_rules": [_bonus_rule("if", "waterway_or_port", 10)],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "mountain_plateau_hills_chain",
        "label": "Mountains / plateau / hills chain",
        "bonus_rules": [
            _bonus_rule("if", "topography_mountains", 15),
            _bonus_rule("else_if", "topography_plateau", 7.5),
            _bonus_rule("else_if", "topography_hills", 5),
        ],
        "scaled_rules": [],
    },
    {
        "id": "rural_development",
        "label": "Rural bonus + development scale",
        "bonus_rules": [_bonus_rule("if", "rank_rural", 5)],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "development_010",
        "label": "Development scale only",
        "bonus_rules": [],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "waterway_urban_development",
        "label": "Waterway + urban + development scale",
        "bonus_rules": [
            _bonus_rule("if", "waterway_or_port", 10),
            _bonus_rule("if", "urban_rank", 5),
        ],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "rural_10_plus_development",
        "label": "Rural + development scale (strong)",
        "bonus_rules": [_bonus_rule("if", "rank_rural", 10)],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "port_15_flat",
        "label": "Port flat bonus",
        "bonus_rules": [_bonus_rule("if", "is_port", 15)],
        "scaled_rules": [],
    },
    {
        "id": "fort_mountains_development",
        "label": "Fort + mountains + development scale",
        "bonus_rules": [
            _bonus_rule("if", "fort_level", 5),
            _bonus_rule("if", "topography_mountains", 10),
        ],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "capital_development",
        "label": "Capital bonus + development scale",
        "bonus_rules": [_bonus_rule("if", "is_capital", 10)],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "coin_metal_development",
        "label": "Coin metal bonus + development scale",
        "bonus_rules": [_bonus_rule("if", "raw_coin_metal", 15)],
        "scaled_rules": [_scaled_rule("development", 0, 100, 0.1)],
    },
    {
        "id": "building_levels_025_megalopolis_5",
        "label": "Building levels scale + megalopolis bonus",
        "bonus_rules": [_bonus_rule("if", "rank_megalopolis", 5)],
        "scaled_rules": [_scaled_rule("total_building_levels", 0, 100, 0.25)],
    },
]
PREFERENCE_PRESET_BY_ID = {item["id"]: item for item in PREFERENCE_TEMPLATE_PRESETS}


def _trigger_signature(any_of: list[str], all_of: list[str]) -> str:
    return json.dumps({"any_of": any_of, "all_of": all_of}, ensure_ascii=False)


TRIGGER_PRESET_SIGNATURE_TO_ID = {
    _trigger_signature(item["any_of"], item["all_of"]): item["id"] for item in TRIGGER_TEMPLATE_PRESETS
}


def _preference_signature(bonus_rules: list[dict[str, str]], scaled_rules: list[dict[str, str]]) -> str:
    return json.dumps({"bonus_rules": bonus_rules, "scaled_rules": scaled_rules}, ensure_ascii=False, sort_keys=True)


PREFERENCE_PRESET_SIGNATURE_TO_ID = {
    _preference_signature(item["bonus_rules"], item["scaled_rules"]): item["id"] for item in PREFERENCE_TEMPLATE_PRESETS
}
