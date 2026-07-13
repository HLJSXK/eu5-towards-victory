"""Canonical id/loc-key catalog for Engineering Department suitability rows.

Shared by the wonder-index effects generator (writes condition/weight variable
maps) and the engineering department GUI generator (reads the same ids back
via dynamic GUI expressions). Ids are stable and must never be reassigned once
shipped, since the GUI resolves loc keys by concatenating the numeric id.
"""

from decimal import Decimal, InvalidOperation

CONDITION_LOC_KEYS: dict[str, str] = {
    "topography_mountains": "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_MOUNTAINS",
    "topography_plateau": "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_PLATEAU",
    "topography_hills": "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_HILLS",
    "vegetation_forest": "TV_ENGINEERING_SUITABILITY_CONDITION_VEGETATION_FOREST",
    "vegetation_woods": "TV_ENGINEERING_SUITABILITY_CONDITION_VEGETATION_WOODS",
    "vegetation_forest_or_woods": "TV_ENGINEERING_SUITABILITY_CONDITION_VEGETATION_FOREST_OR_WOODS",
    "rank_rural": "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_RURAL",
    "rank_city": "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_CITY",
    "rank_megalopolis": "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_MEGALOPOLIS",
    "neighbor_city": "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_CITY",
    "neighbor_town": "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_TOWN",
    "has_monastery": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_MONASTERY",
    "has_cathedral": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_CATHEDRAL",
    "dominant_religion_owner": "TV_ENGINEERING_SUITABILITY_CONDITION_DOMINANT_RELIGION_OWNER",
    "has_bridge_infrastructure": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_BRIDGE_INFRASTRUCTURE",
    "neighbor_bridge_opening": "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_BRIDGE_OPENING",
    "waterway_or_port": "TV_ENGINEERING_SUITABILITY_CONDITION_WATERWAY_OR_PORT",
    "is_port": "TV_ENGINEERING_SUITABILITY_CONDITION_IS_PORT",
    "fort_level": "TV_ENGINEERING_SUITABILITY_CONDITION_FORT_LEVEL",
    "urban_rank": "TV_ENGINEERING_SUITABILITY_CONDITION_URBAN_RANK",
    "is_capital": "TV_ENGINEERING_SUITABILITY_CONDITION_IS_CAPITAL",
    "raw_coin_metal": "TV_ENGINEERING_SUITABILITY_CONDITION_RAW_COIN_METAL",
    "has_armory": "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_ARMORY",
}

SOURCE_LOC_KEYS: dict[str, str] = {
    "development": "TV_ENGINEERING_SUITABILITY_SOURCE_DEVELOPMENT",
    "total_building_levels": "TV_ENGINEERING_SUITABILITY_SOURCE_TOTAL_BUILDING_LEVELS",
    "harbor_suitability": "TV_ENGINEERING_SUITABILITY_SOURCE_HARBOR_SUITABILITY",
    "free_building_levels": "TV_ENGINEERING_SUITABILITY_SOURCE_FREE_BUILDING_LEVELS",
    "average_location_literacy": "TV_ENGINEERING_SUITABILITY_SOURCE_AVERAGE_LOCATION_LITERACY",
}

# Stable numeric id assignment: 0 is a reserved sentinel meaning "no condition
# in this slot". Conditions take ids 1..len(CONDITION_LOC_KEYS), sources
# continue immediately after. Never renumber existing entries; append new
# condition/source keys at the end of their respective dict above.
CONDITION_IDS: dict[str, int] = {key: index for index, key in enumerate(CONDITION_LOC_KEYS, start=1)}
SOURCE_IDS: dict[str, int] = {
    key: index for index, key in enumerate(SOURCE_LOC_KEYS, start=len(CONDITION_IDS) + 1)
}

# Combined row -> id lookup, keyed the same way suitability_knowledge_for_wonder
# rows are keyed ("condition" for condition_bonus rows, "source" for scaled_bonus rows).
ROW_KEY_TO_ID: dict[str, int] = {**CONDITION_IDS, **SOURCE_IDS}

# Combined id -> numeric-suffixed loc key, used by the GUI loc generator.
ID_TO_NUMBERED_LOC_KEY: dict[int, str] = {
    row_id: f"TV_ENGINEERING_SUITABILITY_CONDITION_ID_{row_id}" for row_id in ROW_KEY_TO_ID.values()
}

# id -> the original named loc key, so the loc generator can copy existing text.
ID_TO_SOURCE_LOC_KEY: dict[int, str] = {
    **{CONDITION_IDS[key]: loc_key for key, loc_key in CONDITION_LOC_KEYS.items()},
    **{SOURCE_IDS[key]: loc_key for key, loc_key in SOURCE_LOC_KEYS.items()},
}


def suitability_row_condition_id(row: dict[str, str]) -> int:
    key = row["condition"] if row["type"] == "condition_bonus" else row["source"]
    return ROW_KEY_TO_ID[key]


def suitability_row_weight(row: dict[str, str]) -> Decimal:
    if row["type"] == "condition_bonus":
        return Decimal(str(row["value"]))
    try:
        return Decimal(str(row["max"])) * Decimal(str(row["multiplier"]))
    except (InvalidOperation, KeyError, ValueError):
        return Decimal(str(row["multiplier"]))


def format_weight_literal(value: Decimal) -> str:
    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"
