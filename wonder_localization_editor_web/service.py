from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.wonder_localization_lib import (
    REPO_ROOT,
    WONDER_LOCALIZATION_FILE,
    load_engineering_department_suffix_map,
    load_localization_map,
    load_wonder_localization_data,
    normalize_editor_text,
    save_wonder_localization_data,
)
from scripts.wonder_mechanics_lib import (
    MECHANICS_FILE,
    SUPPORTED_RITUAL_COST_TYPES,
    SUPPORTED_RITUAL_LISTENERS,
    SUPPORTED_UNIQUE_RITUAL_MODES,
    UNIQUE_WONDERS_FILE,
    WONDERS_FILE,
    authored_final_building_local_modifiers,
    ceremony_modifier_for_style,
    ceremony_styles,
    dump_yaml_document,
    final_building_for_style,
    load_all_wonder_mechanics_data,
    load_mechanics_source_data,
    load_unique_wonders_source_data,
    load_wonders_source_data,
    loc_line,
    mechanic_key,
    normalize_unique_ritual,
    render_header,
    ritual_blessing_modifier_name,
    ritual_burden_modifier_name,
    save_yaml_document,
    site_preference_script_for_key,
    site_trigger_script_for_key,
    suitability_knowledge_for_key,
)

LANGUAGES = ("english", "simp_chinese")
LANGUAGE_LABELS = {
    "english": "English",
    "simp_chinese": "Simplified Chinese",
}
WONDER_SIZE_LABELS = {
    "small": "Small",
    "medium": "Medium",
    "large": "Large",
}
WONDER_SIZE_OPTIONS = [
    {"value": size, "label": label}
    for size, label in WONDER_SIZE_LABELS.items()
]
ROMAN_NUMERALS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
}
WONDER_LOCALIZATION_DATA_REL = "data/wonder_localization.yaml"
GENERATED_LOC_DATA_REL = "data/wonders.yaml + data/wonder_mechanics.yaml + data/unique_wonders.yaml + data/wonder_localization.yaml"
WONDER_EDITOR_CATALOG_FILE = REPO_ROOT / "data" / "wonder_editor_catalog.yaml"
MODIFIER_LOCALIZATION_INDEX_FILE = REPO_ROOT / "data" / "index" / "modifier_localization.json"
GENERATED_WONDER_IMAGES_DIR = REPO_ROOT / "data" / "generated_wonders"
WONDER_IMAGE_URL_PREFIX = "/wonder-images"
GENERATED_LOC_FILES = {
    "english": REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_engineering_department_wonder_mechanics_l_english.yml",
    "simp_chinese": REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_wonder_mechanics_l_simp_chinese.yml",
}
GENERATED_LOC_SCRIPT_REL = {
    "english": "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
    "simp_chinese": "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py",
}
MANUAL_CONCEPT_FILES = {
    "english": REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_game_concepts_l_english.yml",
    "simp_chinese": REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_game_concepts_l_simp_chinese.yml",
}
MANUAL_ENGINEERING_FILES = {
    "english": REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_engineering_department_l_english.yml",
    "simp_chinese": REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_l_simp_chinese.yml",
}
REGEN_SCRIPTS = (
    GENERATED_LOC_SCRIPT_REL["english"],
    GENERATED_LOC_SCRIPT_REL["simp_chinese"],
)
WONDER_DATA_REGEN_SCRIPTS = (
    "scripts/in_game/common/building_types/gen_tv_wonder_module_buildings.py",
    "scripts/in_game/common/building_types/gen_tv_engineering_department_wonder_mechanics_buildings.py",
    "scripts/in_game/common/static_modifiers/gen_tv_engineering_department_wonder_mechanics_modifiers.py",
    "scripts/in_game/common/generic_actions/gen_tv_engineering_department_wonder_mechanics_actions.py",
    "scripts/in_game/common/scripted_triggers/gen_tv_engineering_department_wonder_mechanics_triggers.py",
    "scripts/in_game/common/scripted_effects/gen_tv_wonder_module_effects.py",
    "scripts/in_game/common/scripted_effects/gen_tv_engineering_department_wonder_mechanics_effects.py",
    "scripts/main_menu/common/game_concepts/gen_tv_engineering_department_wonder_mechanics_concepts.py",
    GENERATED_LOC_SCRIPT_REL["english"],
    GENERATED_LOC_SCRIPT_REL["simp_chinese"],
    "scripts/in_game/gui/panels/organization/gen_tv_engineering_department_wonder_mechanics_gui.py",
    "scripts/in_game/gui/panels/organization/merge_tv_engineering_department_wonder_mechanics_gui.py",
    "scripts/in_game/gui/gen_location_window.py",
)
CONCEPT_FILE = REPO_ROOT / "src" / "main_menu" / "common" / "game_concepts" / "tv_engineering_department_wonder_mechanics_concepts.txt"
CONCEPT_SCRIPT_REL = "scripts/main_menu/common/game_concepts/gen_tv_engineering_department_wonder_mechanics_concepts.py"
CONCEPT_ICONS = {
    "infrastructure_category": "gfx/interface/icons/location_icons/new/prosperity.dds",
    "military_category": "gfx/interface/icons/flat_icons/tabicons/military.dds",
    "cultural_category": "gfx/interface/icons/flat_icons/cultural_influence.dds",
    "government_category": "gfx/interface/icons/flat_icons/diplomatic_reputation.dds",
}
ESTATE_POWER_BY_POP_TYPE = {
    "clergy": "local_clergy_estate_power",
    "nobles": "local_nobles_estate_power",
    "burghers": "local_burghers_estate_power",
    "laborers": "local_peasants_estate_power",
    "soldiers": "local_crown_estate_power",
}
GENERIC_STYLE_2_DERIVED_TITLE = "Auto-applied estate power"
GENERIC_STYLE_2_DERIVED_HELP_TEXT = (
    "The auxiliary building generator always adds this +0.5 local estate power effect "
    "for the wonder's pop_type on top of the editable local modifiers."
)
INDEX_LANGUAGE_BY_EDITOR_LANGUAGE = {
    "english": "en",
    "simp_chinese": "zh",
}
REFERENCE_LOC_DIR_BY_EDITOR_LANGUAGE = {
    "english": REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "localization" / "english",
    "simp_chinese": REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "localization" / "simp_chinese",
}
OPTION_LOC_LINE_RE = re.compile(r'^\s*([A-Za-z0-9_.-]+):(?:\d+)?\s+"(.*)"\s*$')
REWARD_LABEL_CANDIDATES = {
    "all_estate_satisfaction": ("estate_satisfaction", "game_concept_estate_satisfaction"),
    "estate_satisfaction": ("estate_satisfaction", "game_concept_estate_satisfaction"),
    "ruler_adm": ("administration", "game_concept_administration", "adm"),
    "ruler_dip": ("diplomacy", "game_concept_diplomacy", "dip"),
    "ruler_mil": ("military", "game_concept_military", "mil"),
    "site_prosperity": ("prosperity", "game_concept_prosperity"),
}
REWARD_FALLBACK_LABELS = {
    "all_estate_satisfaction": "All Estate Satisfaction",
    "estate_satisfaction": "Estate Satisfaction",
    "ruler_adm": "Ruler Administrative Skill",
    "ruler_dip": "Ruler Diplomatic Skill",
    "ruler_mil": "Ruler Military Skill",
    "site_prosperity": "Site Prosperity",
    "yearly_gold": "Yearly Gold",
    "yearly_manpower": "Yearly Manpower",
    "yearly_sailors": "Yearly Sailors",
}
COMMON_LOCALIZATION_KEYS = (
    "tv_wonder_confirm_ceremony",
    "tv_wonder_confirm_ceremony_desc",
    "tv_wonder_confirm_ceremony_scaled_gold",
    "tv_wonder_confirm_ceremony_scaled_gold_desc",
    "tv_wonder_confirm_ceremony_prestige",
    "tv_wonder_confirm_ceremony_prestige_desc",
    "tv_wonder_ritual_style_3_scaled_gold_price",
    "tv_wonder_ritual_style_3_prestige_price",
    "tv_wonder_ritual_annex_small_price",
    "tv_wonder_ritual_annex_medium_price",
    "tv_wonder_ritual_annex_large_price",
    "MODIFIER_TYPE_NAME_tv_wonder_ritual_style_3_scaled_gold_price_cost_modifier",
    "MODIFIER_TYPE_DESC_tv_wonder_ritual_style_3_scaled_gold_price_cost_modifier",
    "MODIFIER_TYPE_NAME_tv_wonder_ritual_style_3_prestige_price_cost_modifier",
    "MODIFIER_TYPE_DESC_tv_wonder_ritual_style_3_prestige_price_cost_modifier",
    "MODIFIER_TYPE_NAME_tv_wonder_ritual_annex_small_price_cost_modifier",
    "MODIFIER_TYPE_DESC_tv_wonder_ritual_annex_small_price_cost_modifier",
    "MODIFIER_TYPE_NAME_tv_wonder_ritual_annex_medium_price_cost_modifier",
    "MODIFIER_TYPE_DESC_tv_wonder_ritual_annex_medium_price_cost_modifier",
    "MODIFIER_TYPE_NAME_tv_wonder_ritual_annex_large_price_cost_modifier",
    "MODIFIER_TYPE_DESC_tv_wonder_ritual_annex_large_price_cost_modifier",
    "PERFORM_tv_wonder_confirm_ceremony_ACTION_SETUP",
    "PERFORM_tv_wonder_confirm_ceremony_ACTION_LOG",
    "PERFORM_tv_wonder_confirm_ceremony_ACTION_MAP",
    "PERFORM_tv_wonder_confirm_ceremony_scaled_gold_ACTION_SETUP",
    "PERFORM_tv_wonder_confirm_ceremony_scaled_gold_ACTION_LOG",
    "PERFORM_tv_wonder_confirm_ceremony_scaled_gold_ACTION_MAP",
    "PERFORM_tv_wonder_confirm_ceremony_prestige_ACTION_SETUP",
    "PERFORM_tv_wonder_confirm_ceremony_prestige_ACTION_LOG",
    "PERFORM_tv_wonder_confirm_ceremony_prestige_ACTION_MAP",
    "TV_ENGINEERING_SUITABILITY_KNOWLEDGE_TITLE",
    "TV_ENGINEERING_SUITABILITY_LOCATION_CONDITIONS_TITLE",
    "TV_ENGINEERING_SUITABILITY_CONDITIONS_TITLE",
    "TV_ENGINEERING_SUITABILITY_ROW_HIDDEN",
    "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_MOUNTAINS",
    "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_PLATEAU",
    "TV_ENGINEERING_SUITABILITY_CONDITION_TOPOGRAPHY_HILLS",
    "TV_ENGINEERING_SUITABILITY_CONDITION_VEGETATION_FOREST",
    "TV_ENGINEERING_SUITABILITY_CONDITION_VEGETATION_WOODS",
    "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_RURAL",
    "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_CITY",
    "TV_ENGINEERING_SUITABILITY_CONDITION_RANK_MEGALOPOLIS",
    "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_CITY",
    "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_TOWN",
    "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_MONASTERY",
    "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_CATHEDRAL",
    "TV_ENGINEERING_SUITABILITY_CONDITION_DOMINANT_RELIGION_OWNER",
    "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_BRIDGE_INFRASTRUCTURE",
    "TV_ENGINEERING_SUITABILITY_CONDITION_NEIGHBOR_BRIDGE_OPENING",
    "TV_ENGINEERING_SUITABILITY_CONDITION_WATERWAY_OR_PORT",
    "TV_ENGINEERING_SUITABILITY_CONDITION_IS_PORT",
    "TV_ENGINEERING_SUITABILITY_CONDITION_FORT_LEVEL",
    "TV_ENGINEERING_SUITABILITY_CONDITION_URBAN_RANK",
    "TV_ENGINEERING_SUITABILITY_CONDITION_IS_CAPITAL",
    "TV_ENGINEERING_SUITABILITY_CONDITION_RAW_COIN_METAL",
    "TV_ENGINEERING_SUITABILITY_CONDITION_HAS_ARMORY",
    "TV_ENGINEERING_SUITABILITY_SOURCE_DEVELOPMENT",
    "TV_ENGINEERING_SUITABILITY_SOURCE_TOTAL_BUILDING_LEVELS",
    "TV_ENGINEERING_SUITABILITY_SOURCE_HARBOR_SUITABILITY",
    "TV_ENGINEERING_SUITABILITY_SOURCE_AVERAGE_LOCATION_LITERACY",
)


@dataclass(slots=True)
class FieldSpec:
    key: str
    label: str
    group: str
    language: str
    file_path: Path
    original_value: str
    height: int = 3
    source_kind: str = "canonical"

    def to_api_dict(self) -> dict[str, Any]:
        origin_label = {
            "canonical": "Canonical source",
        }.get(self.source_kind, self.source_kind)
        return {
            "key": self.key,
            "label": self.label,
            "group": self.group,
            "language": self.language,
            "source_kind": self.source_kind,
            "origin_label": origin_label,
            "original_value": self.original_value,
            "value": self.original_value,
            "field_type": "text",
            "height": self.height,
            "options": [],
            "help_text": "",
        }


@dataclass(slots=True)
class MechanicsFieldSpec:
    key: str
    label: str
    group: str
    source_kind: str
    file_path: Path
    original_value: str
    field_type: str
    target_kind: str
    target_key: str
    target_parent_key: str = ""
    height: int = 3
    options: list[dict[str, Any]] = field(default_factory=list)
    help_text: str = ""
    source_path: str = ""
    target_path: str = ""
    structured_value: Any | None = None
    editable: bool = True
    prototype_key: str = ""

    def to_api_dict(self) -> dict[str, Any]:
        origin_label = {
            "shared": "Shared mechanics source",
            "generic": "Generic wonder source",
            "unique": "Unique wonder source",
        }.get(self.source_kind, self.source_kind)
        if not self.editable and self.prototype_key:
            origin_label = "Inherited from prototype"
        return {
            "key": self.key,
            "label": self.label,
            "group": self.group,
            "source_kind": self.source_kind,
            "origin_label": origin_label,
            "original_value": self.original_value,
            "value": self.original_value,
            "field_type": self.field_type,
            "target_kind": self.target_kind,
            "target_key": self.target_key,
            "target_parent_key": self.target_parent_key,
            "height": self.height,
            "options": list(self.options),
            "help_text": self.help_text,
            "source_path": self.source_path or str(self.file_path.relative_to(REPO_ROOT)),
            "target_path": self.target_path,
            "structured_value": deepcopy(self.structured_value),
            "editable": self.editable,
            "prototype_key": self.prototype_key,
        }


def serialize_yaml_editor_value(value: object) -> str:
    return dump_yaml_document(value).rstrip()


def normalize_multiline_editor_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def parse_yaml_editor_value(raw_value: str, *, expected_type: type) -> object:
    text = raw_value.strip()
    if not text:
        raise ValueError(f"Expected {expected_type.__name__} YAML value, got empty input")
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML value: {exc}") from exc
    if not isinstance(value, expected_type):
        raise ValueError(f"Expected {expected_type.__name__}, got {type(value).__name__}")
    return value


def normalize_text_file(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def serialize_structured_editor_value(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def parse_structured_editor_value(raw_value: object, *, context: str) -> object:
    if isinstance(raw_value, str):
        text = raw_value.strip()
        if not text:
            raise ValueError(f"{context} cannot be empty")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{context} is not valid editor JSON: {exc}") from exc
    return deepcopy(raw_value)


def stringify_editor_scalar(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value)


def parse_editor_scalar(raw_value: object) -> object:
    if isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool):
        return raw_value
    text = str(raw_value).strip()
    if not text:
        raise ValueError("Scalar value cannot be empty")
    if text.lower() == "yes":
        return True
    if text.lower() == "no":
        return False
    try:
        if any(marker in text for marker in (".", "e", "E")):
            number = float(text)
            if number.is_integer() and "." not in text and "e" not in text.lower():
                return int(number)
            return number
        return int(text)
    except ValueError:
        return text


def wonder_size_label(size: object) -> str:
    return WONDER_SIZE_LABELS.get(str(size), str(size))


def normalize_editor_wonder_size(raw_value: object, *, context: str) -> str:
    size = str(raw_value).strip()
    if size not in WONDER_SIZE_LABELS:
        supported = ", ".join(WONDER_SIZE_LABELS)
        raise ValueError(f"{context} must be one of: {supported}")
    return size


def modifier_rows_from_mapping(mapping: dict[str, object]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for modifier, value in mapping.items():
        rows.append(
            {
                "modifier": str(modifier),
                "value": stringify_editor_scalar(value),
            }
        )
    return rows


def scale_numeric_mapping(mapping: dict[str, object], multiplier: int | float) -> dict[str, object]:
    if multiplier == 1:
        return dict(mapping)
    scaled: dict[str, object] = {}
    for modifier, value in mapping.items():
        if isinstance(value, (int, float)):
            scaled[modifier] = value * multiplier
        else:
            scaled[modifier] = value
    return scaled


def mapping_from_modifier_rows(raw_value: object, *, context: str) -> dict[str, object]:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"{context}.rows must be a list")
    mapping: dict[str, object] = {}
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.rows[{index}] must be an object")
        modifier = str(row.get("modifier", "")).strip()
        value = str(row.get("value", "")).strip()
        if not modifier and not value:
            continue
        if not modifier:
            raise ValueError(f"{context}.rows[{index}] is missing modifier")
        if not value:
            raise ValueError(f"{context}.rows[{index}] is missing value")
        if modifier in mapping:
            raise ValueError(f"Duplicate modifier {modifier!r} in {context}")
        mapping[modifier] = parse_editor_scalar(value)
    return mapping


def reward_rows_from_list(reward: list[object]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in reward:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "type": str(item.get("type", "")).strip(),
                "value": stringify_editor_scalar(item.get("value", "")),
            }
        )
    return rows


def reward_list_from_rows(raw_value: object, *, context: str) -> list[dict[str, object]]:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"{context}.rows must be a list")
    reward: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.rows[{index}] must be an object")
        reward_type = str(row.get("type", "")).strip()
        value = str(row.get("value", "")).strip()
        if not reward_type and not value:
            continue
        if not reward_type:
            raise ValueError(f"{context}.rows[{index}] is missing reward type")
        if not value:
            raise ValueError(f"{context}.rows[{index}] is missing reward value")
        reward.append(
            {
                "type": reward_type,
                "value": parse_editor_scalar(value),
            }
        )
    return reward


def string_rows_from_list(items: list[str]) -> list[dict[str, str]]:
    return [{"value": item} for item in items]


def list_from_string_rows(raw_value: object, *, context: str) -> list[str]:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"{context}.rows must be a list")
    values: list[str] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.rows[{index}] must be an object")
        value = str(row.get("value", "")).strip()
        if not value:
            continue
        if value in values:
            raise ValueError(f"Duplicate value {value!r} in {context}")
        values.append(value)
    return values


def build_modifier_editor_state(
    mapping: dict[str, object],
    *,
    modifier_scope: str,
    options: list[dict[str, Any]],
    derived_mapping: dict[str, object] | None = None,
    derived_title: str = "",
    derived_help_text: str = "",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "modifier_scope": modifier_scope,
        "rows": modifier_rows_from_mapping(mapping),
        "options": list(options),
    }
    if derived_mapping:
        payload["derived_rows"] = modifier_rows_from_mapping(derived_mapping)
        payload["derived_title"] = derived_title or "Auto-applied modifiers"
        if derived_help_text:
            payload["derived_help_text"] = derived_help_text
    return payload


def generic_style_2_derived_modifier_mapping(wonder: dict[str, Any]) -> dict[str, object]:
    modifier = ESTATE_POWER_BY_POP_TYPE.get(str(wonder.get("pop_type", "")).strip())
    if not modifier:
        return {}
    return {modifier: 0.5}


def build_reward_editor_state(
    *,
    rows: list[dict[str, str]],
    options: list[dict[str, Any]],
    cost_type: str | None = None,
    cost_options: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "rows": rows,
        "options": list(options),
    }
    if cost_options is not None:
        payload["cost_type"] = cost_type
        payload["cost_options"] = list(cost_options)
    return payload


def _optional_editor_text(value: object) -> str | None:
    text = normalize_multiline_editor_text(str(value))
    return text or None


def build_unique_ritual_editor_state(
    ritual: dict[str, Any],
    *,
    country_modifier_options: list[dict[str, Any]],
    local_modifier_options: list[dict[str, Any]],
    reward_type_options: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "key": ritual.get("key", ""),
        "mode": ritual.get("mode"),
        "mode_options": [{"value": mode, "label": mode} for mode in sorted(SUPPORTED_UNIQUE_RITUAL_MODES)],
        "cost_type": ritual.get("cost_type"),
        "cost_options": [
            {"value": "", "label": "None"},
            *[
                {"value": cost_type, "label": cost_type}
                for cost_type in sorted(option for option in SUPPORTED_RITUAL_COST_TYPES if option is not None)
            ],
        ],
        "listeners": {
            "rows": string_rows_from_list(list(ritual.get("listeners", []))),
            "options": [{"value": listener, "label": listener} for listener in sorted(SUPPORTED_RITUAL_LISTENERS)],
        },
        "runtime_variables": {
            "rows": string_rows_from_list(list(ritual.get("runtime_variables", []))),
        },
        "country_modifier": build_modifier_editor_state(
            ritual.get("country_modifier", {}),
            modifier_scope="country",
            options=country_modifier_options,
        ),
        "reward": build_reward_editor_state(
            rows=reward_rows_from_list(list(ritual.get("reward", []))),
            options=reward_type_options,
        ),
        "confirmation_trigger_script": ritual.get("confirmation_trigger_script", ""),
        "start_effect_script": ritual.get("start_effect_script", ""),
        "snapshot_effect_script": ritual.get("snapshot_effect_script", ""),
        "progress_effect_script": ritual.get("progress_effect_script", ""),
        "completion_trigger_script": ritual.get("completion_trigger_script", ""),
        "completion_effect_script": ritual.get("completion_effect_script", ""),
        "timed": {
            "years": ritual.get("timed", {}).get("years", 1),
            "burden_modifier": build_modifier_editor_state(
                ritual.get("timed", {}).get("burden_modifier", {}),
                modifier_scope="country",
                options=country_modifier_options,
            ),
            "blessing_modifier": build_modifier_editor_state(
                ritual.get("timed", {}).get("blessing_modifier", {}),
                modifier_scope="country",
                options=country_modifier_options,
            ),
        },
        "auxiliary_building": {
            "local_modifier": build_modifier_editor_state(
                ritual.get("auxiliary_building", {}).get("local_modifier", {}),
                modifier_scope="local",
                options=local_modifier_options,
            ),
            "maintenance": ritual.get("auxiliary_building", {}).get("maintenance") or "",
            "build_time": ritual.get("auxiliary_building", {}).get("build_time") or "",
            "construction_demand": ritual.get("auxiliary_building", {}).get("construction_demand") or "",
            "price": ritual.get("auxiliary_building", {}).get("price") or "",
            "attributes": {
                "rows": modifier_rows_from_mapping(ritual.get("auxiliary_building", {}).get("attributes", {})),
            },
            "max_levels": ritual.get("auxiliary_building", {}).get("max_levels", 1),
        },
    }


def unique_ritual_from_editor_state(raw_value: object, *, context: str) -> dict[str, Any]:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")

    mode = str(payload.get("mode", "")).strip()
    if mode not in SUPPORTED_UNIQUE_RITUAL_MODES:
        raise ValueError(f"{context}.mode must be one of: {', '.join(sorted(SUPPORTED_UNIQUE_RITUAL_MODES))}")

    cost_type_value = payload.get("cost_type", "")
    cost_type_raw = "" if cost_type_value is None else str(cost_type_value).strip()
    cost_type = cost_type_raw or None
    if cost_type not in SUPPORTED_RITUAL_COST_TYPES:
        supported = ", ".join(sorted(option for option in SUPPORTED_RITUAL_COST_TYPES if option is not None))
        raise ValueError(f"{context}.cost_type must be empty or one of: {supported}")

    listeners = list_from_string_rows(payload.get("listeners", {}), context=f"{context}.listeners")
    for listener in listeners:
        if listener not in SUPPORTED_RITUAL_LISTENERS:
            raise ValueError(f"Unsupported listener {listener!r} in {context}.listeners")

    runtime_variables = list_from_string_rows(payload.get("runtime_variables", {}), context=f"{context}.runtime_variables")
    country_modifier = mapping_from_modifier_rows(payload.get("country_modifier", {}), context=f"{context}.country_modifier")
    reward = reward_list_from_rows(payload.get("reward", {}), context=f"{context}.reward")

    timed = payload.get("timed", {})
    if not isinstance(timed, dict):
        raise ValueError(f"{context}.timed must be an object")
    timed_years = parse_editor_scalar(timed.get("years", 1))
    if not isinstance(timed_years, int) or isinstance(timed_years, bool) or timed_years < 1:
        raise ValueError(f"{context}.timed.years must be an integer >= 1")
    burden_modifier = mapping_from_modifier_rows(timed.get("burden_modifier", {}), context=f"{context}.timed.burden_modifier")
    blessing_modifier = mapping_from_modifier_rows(timed.get("blessing_modifier", {}), context=f"{context}.timed.blessing_modifier")

    auxiliary = payload.get("auxiliary_building", {})
    if not isinstance(auxiliary, dict):
        raise ValueError(f"{context}.auxiliary_building must be an object")
    local_modifier = mapping_from_modifier_rows(auxiliary.get("local_modifier", {}), context=f"{context}.auxiliary_building.local_modifier")
    attributes = mapping_from_modifier_rows(auxiliary.get("attributes", {}), context=f"{context}.auxiliary_building.attributes")
    max_levels = parse_editor_scalar(auxiliary.get("max_levels", 1))
    if not isinstance(max_levels, int) or isinstance(max_levels, bool) or max_levels < 1:
        raise ValueError(f"{context}.auxiliary_building.max_levels must be an integer >= 1")

    return {
        "key": str(payload.get("key", "")).strip() or "ritual",
        "mode": mode,
        "cost_type": cost_type,
        "listeners": listeners,
        "runtime_variables": runtime_variables,
        "country_modifier": country_modifier,
        "reward": reward,
        "confirmation_trigger_script": normalize_multiline_editor_text(str(payload.get("confirmation_trigger_script", ""))),
        "start_effect_script": normalize_multiline_editor_text(str(payload.get("start_effect_script", ""))),
        "snapshot_effect_script": normalize_multiline_editor_text(str(payload.get("snapshot_effect_script", ""))),
        "progress_effect_script": normalize_multiline_editor_text(str(payload.get("progress_effect_script", ""))),
        "completion_trigger_script": normalize_multiline_editor_text(str(payload.get("completion_trigger_script", ""))),
        "completion_effect_script": normalize_multiline_editor_text(str(payload.get("completion_effect_script", ""))),
        "timed": {
            "years": timed_years,
            "burden_modifier": burden_modifier,
            "blessing_modifier": blessing_modifier,
        },
        "auxiliary_building": {
            "local_modifier": local_modifier,
            "maintenance": _optional_editor_text(auxiliary.get("maintenance", "")),
            "build_time": _optional_editor_text(auxiliary.get("build_time", "")),
            "construction_demand": _optional_editor_text(auxiliary.get("construction_demand", "")),
            "price": _optional_editor_text(auxiliary.get("price", "")),
            "attributes": attributes,
            "max_levels": max_levels,
        },
    }


def _prettify_option_key(value: object) -> str:
    return str(value).replace("_", " ").strip().title()


def _scrub_option_markup(value: object) -> str:
    text = str(value or "")

    def concept_replacement(match: re.Match[str]) -> str:
        return _prettify_option_key(match.group(1))

    text = re.sub(r"\[([^|\]]+)\|[A-Za-z]+\]", concept_replacement, text)
    text = re.sub(r"@([A-Za-z0-9_]+)!", "", text)
    text = re.sub(r"#\w+\s*", "", text).replace("#!", "")
    return " ".join(text.split())


def _best_localized_label(labels: dict[str, str], fallback: str) -> str:
    for language in ("simp_chinese", "english"):
        label = _scrub_option_markup(labels.get(language, ""))
        if label:
            return label
    return fallback


def _localized_option(
    value: str,
    labels: dict[str, str] | None = None,
    *,
    descriptions: dict[str, str] | None = None,
    source: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    labels = labels or {}
    descriptions = descriptions or {}
    fallback = _prettify_option_key(value)
    label_en = _scrub_option_markup(labels.get("english") or fallback)
    label_zh = _scrub_option_markup(labels.get("simp_chinese") or label_en)
    description_en = _scrub_option_markup(descriptions.get("english", ""))
    description_zh = _scrub_option_markup(descriptions.get("simp_chinese", ""))
    localized_label = _best_localized_label(
        {
            "english": label_en,
            "simp_chinese": label_zh,
        },
        fallback,
    )
    search_parts = [
        value,
        localized_label,
        label_en,
        label_zh,
        description_en,
        description_zh,
        source,
    ]
    option: dict[str, Any] = {
        "value": value,
        "label": localized_label,
        "key_label": value,
        "localized_label": localized_label,
        "label_en": label_en,
        "label_zh": label_zh,
        "description_en": description_en,
        "description_zh": description_zh,
        "search_text": " ".join(part for part in search_parts if part).lower(),
    }
    if source:
        option["source"] = source
    if extra:
        option.update(extra)
    return option


def _load_json_index(path: Path, root_key: str) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    records = payload.get(root_key, {})
    return records if isinstance(records, dict) else {}


def _localized_pair_from_index_entry(entry: dict[str, Any], field_name: str, fallback: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    for language in LANGUAGES:
        index_language = INDEX_LANGUAGE_BY_EDITOR_LANGUAGE[language]
        language_entry = entry.get(index_language, {}) if isinstance(entry, dict) else {}
        value = language_entry.get(field_name) if isinstance(language_entry, dict) else None
        labels[language] = _scrub_option_markup(value or fallback)
    return labels


def _modifier_options(values: set[str], modifier_index: dict[str, Any]) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for value in sorted(values):
        entry = modifier_index.get(value, {})
        if not isinstance(entry, dict):
            entry = {}
        fallback = _prettify_option_key(value)
        labels = _localized_pair_from_index_entry(entry, "name", fallback)
        descriptions = _localized_pair_from_index_entry(entry, "description", "")
        extra = {
            key: entry[key]
            for key in ("value_kind", "decimals", "category", "color")
            if key in entry
        }
        options.append(_localized_option(value, labels, descriptions=descriptions, extra=extra))
    return options


def _parse_reference_loc_value(raw_value: str) -> str:
    return raw_value.replace(r"\"", '"').replace(r"\n", "\n")


def _load_reference_localization_subset(language: str, wanted_keys: set[str]) -> dict[str, str]:
    root = REFERENCE_LOC_DIR_BY_EDITOR_LANGUAGE[language]
    if not wanted_keys or not root.exists():
        return {}
    remaining = set(wanted_keys)
    values: dict[str, str] = {}
    for path in sorted(root.rglob("*.yml")):
        try:
            lines = path.read_text(encoding="utf-8-sig").splitlines()
        except UnicodeDecodeError:
            continue
        for line in lines:
            match = OPTION_LOC_LINE_RE.match(line)
            if match is None:
                continue
            key = match.group(1)
            if key not in remaining:
                continue
            values[key] = _parse_reference_loc_value(match.group(2))
            remaining.remove(key)
        if not remaining:
            break
    return values


def _reward_label_candidates(reward_type: str, source: str = "") -> list[str]:
    candidates: list[str] = []
    for candidate in REWARD_LABEL_CANDIDATES.get(reward_type, ()):
        candidates.append(candidate)
    candidates.extend([reward_type, f"game_concept_{reward_type}"])
    if reward_type.startswith("yearly_"):
        base = reward_type.removeprefix("yearly_")
        candidates.extend([base, f"game_concept_{base}"])
    if source.startswith("add_"):
        source_base = source.removeprefix("add_")
        candidates.extend([source_base, f"game_concept_{source_base}"])
    seen: set[str] = set()
    unique: list[str] = []
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            unique.append(candidate)
    return unique


def _reward_options(reward_types: set[str], reward_sources: dict[str, str]) -> list[dict[str, Any]]:
    candidate_map = {
        reward_type: _reward_label_candidates(reward_type, reward_sources.get(reward_type, ""))
        for reward_type in reward_types
    }
    wanted_keys = {candidate for candidates in candidate_map.values() for candidate in candidates}
    loc_values = {
        language: _load_reference_localization_subset(language, wanted_keys)
        for language in LANGUAGES
    }
    options: list[dict[str, Any]] = []
    for reward_type in sorted(reward_types):
        source = reward_sources.get(reward_type, "")
        fallback = REWARD_FALLBACK_LABELS.get(reward_type, _prettify_option_key(reward_type))
        labels: dict[str, str] = {}
        for language in LANGUAGES:
            labels[language] = ""
            for candidate in candidate_map[reward_type]:
                value = loc_values[language].get(candidate)
                if value:
                    labels[language] = value
                    break
            if not labels[language]:
                labels[language] = fallback
        options.append(_localized_option(reward_type, labels, source=source))
    return options


def _catalog_string_values(raw_value: object) -> set[str]:
    if not isinstance(raw_value, list):
        return set()
    return {str(item).strip() for item in raw_value if str(item).strip()}


def _load_wonder_editor_catalog() -> dict[str, Any]:
    if not WONDER_EDITOR_CATALOG_FILE.exists():
        return {}
    payload = yaml.safe_load(WONDER_EDITOR_CATALOG_FILE.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _modifier_option_catalog(
    mechanics_data: dict[str, Any],
    unique_wonders_data: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    country_modifiers: set[str] = set()
    local_modifiers: set[str] = set()
    reward_types: set[str] = set()
    editor_catalog = _load_wonder_editor_catalog()
    modifier_index = _load_json_index(MODIFIER_LOCALIZATION_INDEX_FILE, "modifiers")
    reward_sources = {
        str(key): str(value)
        for key, value in (editor_catalog.get("style_3_reward_sources", {}) or {}).items()
    }
    catalog_modifier_types = editor_catalog.get("modifier_types", {})
    if isinstance(catalog_modifier_types, dict):
        country_modifiers.update(_catalog_string_values(catalog_modifier_types.get("country", [])))
        local_modifiers.update(_catalog_string_values(catalog_modifier_types.get("local", [])))
    reward_types.update(_catalog_string_values(editor_catalog.get("style_3_reward_types", [])))

    for mapping in mechanics_data.get("base_modifiers", {}).values():
        if isinstance(mapping, dict):
            country_modifiers.update(str(key) for key in mapping)

    for building in mechanics_data.get("buildings", {}).values():
        if not isinstance(building, dict):
            continue
        local_mapping = building.get("final_local", {})
        if isinstance(local_mapping, dict):
            local_modifiers.update(str(key) for key in local_mapping)

    for ritual in mechanics_data.get("generic_rituals", {}).values():
        if not isinstance(ritual, dict):
            continue
        style_1 = ritual.get("style_1", {})
        if isinstance(style_1, dict):
            country_modifier = style_1.get("country_modifier", {})
            if isinstance(country_modifier, dict):
                country_modifiers.update(str(key) for key in country_modifier)
        style_2 = ritual.get("style_2", {})
        if isinstance(style_2, dict):
            local_modifier = style_2.get("local_modifier", {})
            if isinstance(local_modifier, dict):
                local_modifiers.update(str(key) for key in local_modifier)
        style_3 = ritual.get("style_3", {})
        if isinstance(style_3, dict):
            reward_types.update(str(item.get("type", "")).strip() for item in style_3.get("reward", []) if isinstance(item, dict) and str(item.get("type", "")).strip())

    for modifier in mechanics_data.get("ceremony_modifiers", {}).values():
        if isinstance(modifier, dict):
            country_modifiers.update(str(key) for key in modifier)

    for wonder in unique_wonders_data.get("unique_wonders", []):
        if not isinstance(wonder, dict):
            continue
        entry = wonder.get("ritual", {})
        if not isinstance(entry, dict):
            continue
        country_modifier = entry.get("country_modifier", {})
        if isinstance(country_modifier, dict):
            country_modifiers.update(str(key) for key in country_modifier)
        reward = entry.get("reward", [])
        if isinstance(reward, list):
            reward_types.update(str(item.get("type", "")).strip() for item in reward if isinstance(item, dict) and str(item.get("type", "")).strip())
        timed = entry.get("timed", {})
        if isinstance(timed, dict):
            burden_modifier = timed.get("burden_modifier", {})
            if isinstance(burden_modifier, dict):
                country_modifiers.update(str(key) for key in burden_modifier)
            blessing_modifier = timed.get("blessing_modifier", {})
            if isinstance(blessing_modifier, dict):
                country_modifiers.update(str(key) for key in blessing_modifier)
        auxiliary = entry.get("auxiliary_building", {})
        if isinstance(auxiliary, dict):
            local_modifier = auxiliary.get("local_modifier", {})
            if isinstance(local_modifier, dict):
                local_modifiers.update(str(key) for key in local_modifier)

    if not country_modifiers:
        country_modifiers.add("monthly_prestige")
    if not local_modifiers:
        local_modifiers.add("local_production_efficiency")
    if not reward_types:
        reward_types.update({"prestige", "gold"})
    return (
        _modifier_options(country_modifiers, modifier_index),
        _modifier_options(local_modifiers, modifier_index),
        _reward_options(reward_types, reward_sources),
    )


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


TRIGGER_SET_RE = re.compile(
    r"^set_variable = \{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site\.([A-Za-z0-9_:]+) \}$"
)
TRIGGER_CLAMP_RE = re.compile(
    r"^clamp_variable = \{ name = tv_wonder_site_preference_bonus min = ([^ ]+) max = ([^ ]+) \}$"
)
TRIGGER_MULTIPLY_RE = re.compile(
    r"^change_variable = \{ name = tv_wonder_site_preference_bonus multiply = ([^ ]+) \}$"
)
PREFERENCE_RULE_RE = re.compile(
    r"^(if|else_if) = \{ limit = \{ var:tv_wonder_survey_site \?= \{ (.+?) \} \} tv_wonder_change_all_survey_competence_target_effect = \{ value = (.+?) \} \}$"
)


def split_top_level_statements(script: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    balance = 0
    for raw_line in normalize_multiline_editor_text(script).splitlines():
        stripped = raw_line.rstrip()
        if not stripped and not current:
            continue
        current.append(stripped)
        balance += stripped.count("{") - stripped.count("}")
        if balance == 0 and current:
            statements.append("\n".join(current).strip())
            current = []
    if current:
        raise ValueError(f"Unbalanced script block: {script}")
    return statements


def parse_trigger_builder_state(script: str) -> dict[str, Any]:
    normalized = normalize_multiline_editor_text(script)
    try:
        any_of: list[str] = []
        all_of: list[str] = []
        for statement in split_top_level_statements(normalized):
            statement_lines = statement.splitlines()
            if normalize_inline_script(statement) == "always = yes":
                continue
            if statement.startswith("OR = {"):
                if len(statement_lines) < 3:
                    raise ValueError(f"Malformed OR statement: {statement}")
                for line in statement_lines[1:-1]:
                    condition_id = TRIGGER_CONDITION_SCRIPT_TO_ID.get(normalize_inline_script(line))
                    if condition_id is None:
                        raise ValueError(f"Unknown trigger condition: {line}")
                    any_of.append(condition_id)
            else:
                condition_id = TRIGGER_CONDITION_SCRIPT_TO_ID.get(normalize_inline_script(statement))
                if condition_id is None:
                    raise ValueError(f"Unknown trigger condition: {statement}")
                if condition_id.startswith("not_"):
                    all_of.append(condition_id)
                else:
                    any_of.append(condition_id)
        signature = _trigger_signature(any_of, all_of)
        template_id = TRIGGER_PRESET_SIGNATURE_TO_ID.get(signature, "current_variant")
        return {
            "template_id": template_id,
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in TRIGGER_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(TRIGGER_TEMPLATE_PRESETS),
            "condition_options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            "any_of": {
                "rows": [_site_value_row(value) for value in any_of],
                "options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            },
            "all_of": {
                "rows": [_site_value_row(value) for value in all_of],
                "options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            },
            "raw_script": normalized,
        }
    except Exception:
        return {
            "template_id": "custom_script",
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in TRIGGER_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(TRIGGER_TEMPLATE_PRESETS),
            "condition_options": deepcopy(TRIGGER_CONDITION_OPTIONS),
            "any_of": {"rows": [], "options": deepcopy(TRIGGER_CONDITION_OPTIONS)},
            "all_of": {"rows": [], "options": deepcopy(TRIGGER_CONDITION_OPTIONS)},
            "raw_script": normalized,
        }


def render_trigger_script_from_state(raw_value: object, *, context: str) -> str:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    if payload.get("template_id") == "custom_script":
        script = normalize_multiline_editor_text(str(payload.get("raw_script", "")))
        if not script:
            raise ValueError(f"{context}.raw_script cannot be empty")
        return script
    any_of = list_from_string_rows(payload.get("any_of", {}), context=f"{context}.any_of")
    all_of = list_from_string_rows(payload.get("all_of", {}), context=f"{context}.all_of")
    lines: list[str] = []
    for item in any_of + all_of:
        if item not in TRIGGER_CONDITION_BY_ID:
            raise ValueError(f"Unknown trigger condition {item!r} in {context}")
    if any_of:
        if len(any_of) == 1:
            lines.append(TRIGGER_CONDITION_BY_ID[any_of[0]]["script"])
        else:
            lines.append("OR = {")
            lines.extend(f"\t{TRIGGER_CONDITION_BY_ID[item]['script']}" for item in any_of)
            lines.append("}")
    lines.extend(TRIGGER_CONDITION_BY_ID[item]["script"] for item in all_of)
    if not lines:
        return "always = yes"
    return "\n".join(lines)


def parse_preference_builder_state(script: str) -> dict[str, Any]:
    normalized = normalize_multiline_editor_text(script)
    try:
        bonus_rules: list[dict[str, str]] = []
        scaled_rules: list[dict[str, str]] = []
        statements = [normalize_inline_script(statement) for statement in split_top_level_statements(normalized)]
        index = 0
        while index < len(statements):
            statement = statements[index]
            match = PREFERENCE_RULE_RE.match(statement)
            if match:
                branch, condition_script, value = match.groups()
                condition_id = PREFERENCE_CONDITION_SCRIPT_TO_ID.get(normalize_inline_script(condition_script))
                if condition_id is None:
                    raise ValueError(f"Unknown preference condition: {condition_script}")
                bonus_rules.append(_bonus_rule(branch, condition_id, value))
                index += 1
                continue

            if index + 4 < len(statements):
                set_match = TRIGGER_SET_RE.match(statement)
                clamp_match = TRIGGER_CLAMP_RE.match(statements[index + 1])
                multiply_match = TRIGGER_MULTIPLY_RE.match(statements[index + 2])
                if (
                    set_match
                    and clamp_match
                    and multiply_match
                    and statements[index + 3]
                    == "tv_wonder_change_all_survey_competence_target_effect = { value = var:tv_wonder_site_preference_bonus }"
                    and statements[index + 4] == "remove_variable = tv_wonder_site_preference_bonus"
                ):
                    source_id = PREFERENCE_SCALE_SOURCE_PATH_TO_ID.get(set_match.group(1))
                    if source_id is None:
                        raise ValueError(f"Unknown scale source: {set_match.group(1)}")
                    scaled_rules.append(
                        _scaled_rule(source_id, clamp_match.group(1), clamp_match.group(2), multiply_match.group(1))
                    )
                    index += 5
                    continue

            if statement == "remove_variable = tv_wonder_site_preference_bonus":
                index += 1
                continue

            if index + 3 < len(statements):
                set_match = TRIGGER_SET_RE.match(statement)
                clamp_match = TRIGGER_CLAMP_RE.match(statements[index + 1])
                multiply_match = TRIGGER_MULTIPLY_RE.match(statements[index + 2])
                if (
                    set_match
                    and clamp_match
                    and multiply_match
                    and statements[index + 3]
                    == "tv_wonder_change_all_survey_competence_target_effect = { value = var:tv_wonder_site_preference_bonus }"
                ):
                    source_id = PREFERENCE_SCALE_SOURCE_PATH_TO_ID.get(set_match.group(1))
                    if source_id is None:
                        raise ValueError(f"Unknown scale source: {set_match.group(1)}")
                    scaled_rules.append(
                        _scaled_rule(source_id, clamp_match.group(1), clamp_match.group(2), multiply_match.group(1))
                    )
                    index += 4
                    continue

            raise ValueError(f"Unknown preference statement: {statement}")

        signature = _preference_signature(bonus_rules, scaled_rules)
        template_id = PREFERENCE_PRESET_SIGNATURE_TO_ID.get(signature, "current_variant")
        return {
            "template_id": template_id,
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in PREFERENCE_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(PREFERENCE_TEMPLATE_PRESETS),
            "condition_options": deepcopy(PREFERENCE_CONDITION_OPTIONS),
            "branch_options": deepcopy(PREFERENCE_BRANCH_OPTIONS),
            "scale_source_options": deepcopy(PREFERENCE_SCALE_SOURCE_OPTIONS),
            "bonus_rules": {"rows": deepcopy(bonus_rules)},
            "scaled_rules": {"rows": deepcopy(scaled_rules)},
            "raw_script": normalized,
        }
    except Exception:
        return {
            "template_id": "custom_script",
            "template_options": [
                {"value": "current_variant", "label": "Current structured variant"},
                *[{"value": item["id"], "label": item["label"]} for item in PREFERENCE_TEMPLATE_PRESETS],
                {"value": "custom_script", "label": "Custom script"},
            ],
            "presets": deepcopy(PREFERENCE_TEMPLATE_PRESETS),
            "condition_options": deepcopy(PREFERENCE_CONDITION_OPTIONS),
            "branch_options": deepcopy(PREFERENCE_BRANCH_OPTIONS),
            "scale_source_options": deepcopy(PREFERENCE_SCALE_SOURCE_OPTIONS),
            "bonus_rules": {"rows": []},
            "scaled_rules": {"rows": []},
            "raw_script": normalized,
        }


def render_preference_script_from_state(raw_value: object, *, context: str) -> str:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    if payload.get("template_id") == "custom_script":
        script = normalize_multiline_editor_text(str(payload.get("raw_script", "")))
        if not script:
            raise ValueError(f"{context}.raw_script cannot be empty")
        return script

    bonus_rows = payload.get("bonus_rules", {}).get("rows", [])
    scaled_rows = payload.get("scaled_rules", {}).get("rows", [])
    if not isinstance(bonus_rows, list) or not isinstance(scaled_rows, list):
        raise ValueError(f"{context} rows must be lists")

    lines: list[str] = []
    for index, row in enumerate(bonus_rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.bonus_rules.rows[{index}] must be an object")
        branch = str(row.get("branch", "if")).strip() or "if"
        condition = str(row.get("condition", "")).strip()
        value = str(row.get("value", "")).strip()
        if not condition and not value:
            continue
        if branch not in {"if", "else_if"}:
            raise ValueError(f"{context}.bonus_rules.rows[{index}] has invalid branch {branch!r}")
        if condition not in PREFERENCE_CONDITION_BY_ID:
            raise ValueError(f"{context}.bonus_rules.rows[{index}] has unknown condition {condition!r}")
        if not value:
            raise ValueError(f"{context}.bonus_rules.rows[{index}] is missing value")
        condition_script = PREFERENCE_CONDITION_BY_ID[condition]["script"]
        lines.extend(
            [
                f"{branch} = {{",
                f"\tlimit = {{ var:tv_wonder_survey_site ?= {{ {condition_script} }} }}",
                f"\ttv_wonder_change_all_survey_competence_target_effect = {{ value = {value} }}",
                "}",
            ]
        )

    rendered_scaled = False
    for index, row in enumerate(scaled_rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.scaled_rules.rows[{index}] must be an object")
        source = str(row.get("source", "")).strip()
        minimum = str(row.get("min", "")).strip()
        maximum = str(row.get("max", "")).strip()
        multiplier = str(row.get("multiplier", "")).strip()
        if not source and not minimum and not maximum and not multiplier:
            continue
        if source not in PREFERENCE_SCALE_SOURCE_BY_ID:
            raise ValueError(f"{context}.scaled_rules.rows[{index}] has unknown source {source!r}")
        if not minimum or not maximum or not multiplier:
            raise ValueError(f"{context}.scaled_rules.rows[{index}] must define min, max, and multiplier")
        source_path = PREFERENCE_SCALE_SOURCE_BY_ID[source]["path"]
        lines.extend(
            [
                f"set_variable = {{ name = tv_wonder_site_preference_bonus value = var:tv_wonder_survey_site.{source_path} }}",
                f"clamp_variable = {{ name = tv_wonder_site_preference_bonus min = {minimum} max = {maximum} }}",
                f"change_variable = {{ name = tv_wonder_site_preference_bonus multiply = {multiplier} }}",
                "tv_wonder_change_all_survey_competence_target_effect = { value = var:tv_wonder_site_preference_bonus }",
            ]
        )
        rendered_scaled = True

    if rendered_scaled:
        lines.append("remove_variable = tv_wonder_site_preference_bonus")

    if not lines:
        raise ValueError(f"{context} must define at least one rule")
    return "\n".join(lines)


def build_suitability_knowledge_editor_state(rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "row_type_options": [
            {"value": "condition_bonus", "label": "Condition bonus"},
            {"value": "scaled_bonus", "label": "Scaled bonus"},
        ],
        "condition_options": deepcopy(PREFERENCE_CONDITION_OPTIONS),
        "scale_source_options": deepcopy(PREFERENCE_SCALE_SOURCE_OPTIONS),
        "rows": deepcopy(rows),
    }


def suitability_knowledge_from_editor_state(raw_value: object, *, context: str) -> list[dict[str, str]]:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"{context}.rows must be a list")

    normalized: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.rows[{index}] must be an object")
        row_type = str(row.get("type", "")).strip()
        if row_type == "condition_bonus":
            condition = str(row.get("condition", "")).strip()
            value = str(row.get("value", "")).strip()
            if condition not in PREFERENCE_CONDITION_BY_ID:
                raise ValueError(f"{context}.rows[{index}] has unknown condition {condition!r}")
            if not value:
                raise ValueError(f"{context}.rows[{index}] is missing value")
            normalized.append({"type": row_type, "condition": condition, "value": value})
            continue
        if row_type == "scaled_bonus":
            source = str(row.get("source", "")).strip()
            minimum = str(row.get("min", "")).strip()
            maximum = str(row.get("max", "")).strip()
            multiplier = str(row.get("multiplier", "")).strip()
            if source not in PREFERENCE_SCALE_SOURCE_BY_ID:
                raise ValueError(f"{context}.rows[{index}] has unknown source {source!r}")
            if not minimum or not maximum or not multiplier:
                raise ValueError(f"{context}.rows[{index}] must define min, max, and multiplier")
            normalized.append(
                {
                    "type": row_type,
                    "source": source,
                    "min": minimum,
                    "max": maximum,
                    "multiplier": multiplier,
                }
            )
            continue
        raise ValueError(f"{context}.rows[{index}] has unsupported type {row_type!r}")
    if not normalized:
        raise ValueError(f"{context}.rows must define at least one suitability row")
    return normalized


def concept_key_for_wonder(wonder: dict[str, Any]) -> str:
    return f"game_concept_{wonder['concept']}"


def wonder_name_key(wonder: dict[str, Any]) -> str:
    return f"tv_wonder_{wonder['key']}"


def branch_button_key(building: str) -> str:
    ceremony_key = building.removeprefix("tv_wonder_").upper()
    return f"TV_ENGINEERING_CEREMONY_{ceremony_key}_BUTTON"


def active_ritual_key(wonder: dict[str, Any], style: int) -> str:
    return f"TV_ENGINEERING_ACTIVE_RITUAL_{wonder['key'].upper()}_{style}"


def event_desc_key(wonder: dict[str, Any], suffixes: dict[int, str], style: int | None = None) -> str | None:
    if wonder.get("is_unique"):
        return f"tv_engineering_department.500.d_{wonder['key']}"
    suffix = suffixes.get(int(wonder["id"]))
    if suffix is None:
        return None
    if style is None:
        return f"tv_engineering_department.600.d_{suffix}"
    return f"tv_engineering_department.500.d_{suffix}_{style}"


def required_localization_keys_for_wonder(
    wonder: dict[str, Any],
    mechanics: dict[str, Any],
    suffixes: dict[int, str],
) -> set[str]:
    code = wonder["key"].upper()
    keys = {
        concept_key_for_wonder(wonder),
        f"{concept_key_for_wonder(wonder)}_desc",
        f"TV_ENGINEERING_PROPOSAL_{code}_TEXT",
        f"TV_ENGINEERING_PROPOSAL_RESUME_{code}_TEXT",
        f"TV_ENGINEERING_PROPOSAL_EXPAND_{code}_TEXT",
        f"TV_ENGINEERING_LOCKED_{code}_TEXT",
        f"TV_ENGINEERING_PROPOSAL_BUTTON_{code}",
        f"TV_WONDER_LOCK_{code}_TT",
        wonder_name_key(wonder),
        f"{wonder_name_key(wonder)}_desc",
    }

    for part in ("foundation", "body", "function", "decoration"):
        keys.add(f"{wonder_name_key(wonder)}_{part}")
        keys.add(f"{wonder_name_key(wonder)}_{part}_desc")

    for level in range(1, 7):
        keys.add(f"STATIC_MODIFIER_NAME_{wonder_name_key(wonder)}_level_{level}")

    if not wonder.get("is_unique"):
        keys.add(f"{wonder_name_key(wonder)}_ritual_annex")
        keys.add(f"{wonder_name_key(wonder)}_ritual_annex_desc")
        keys.add(f"STATIC_MODIFIER_NAME_{ritual_burden_modifier_name(wonder)}")
        keys.add(f"STATIC_MODIFIER_NAME_{ritual_blessing_modifier_name(wonder)}")

    for style in ceremony_styles(wonder):
        building = final_building_for_style(wonder, style)
        keys.add(building)
        keys.add(f"{building}_desc")
        keys.add(branch_button_key(building))
        keys.add(active_ritual_key(wonder, style))
        ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
        if ceremony_modifier is not None:
            keys.add(f"STATIC_MODIFIER_NAME_{ceremony_modifier[0]}")
        wonder_event_key = event_desc_key(wonder, suffixes, style if not wonder.get("is_unique") else None)
        if wonder_event_key is not None:
            keys.add(wonder_event_key)

    if not wonder.get("is_unique"):
        world_news_key = event_desc_key(wonder, suffixes, None)
        if world_news_key is not None:
            keys.add(world_news_key)

    return keys


def required_canonical_localization_keys(
    wonders: list[dict[str, Any]],
    mechanics: dict[str, Any],
    suffixes: dict[int, str],
) -> set[str]:
    keys = set(COMMON_LOCALIZATION_KEYS)
    for wonder in wonders:
        keys.update(required_localization_keys_for_wonder(wonder, mechanics, suffixes))
    return keys


def validate_canonical_localization_data(
    wonders: list[dict[str, Any]],
    mechanics: dict[str, Any],
    suffixes: dict[int, str],
    localization_data: dict[str, dict[str, str]],
) -> set[str]:
    english_keys = set(localization_data["english"])
    chinese_keys = set(localization_data["simp_chinese"])

    missing_in_chinese = sorted(english_keys - chinese_keys)
    if missing_in_chinese:
        preview = ", ".join(missing_in_chinese[:10])
        raise ValueError(
            f"Missing Simplified Chinese localization keys in {WONDER_LOCALIZATION_FILE}: {preview}"
        )

    missing_in_english = sorted(chinese_keys - english_keys)
    if missing_in_english:
        preview = ", ".join(missing_in_english[:10])
        raise ValueError(
            f"Missing English localization keys in {WONDER_LOCALIZATION_FILE}: {preview}"
        )

    required_keys = required_canonical_localization_keys(wonders, mechanics, suffixes)
    missing_required = sorted(required_keys - english_keys)
    if missing_required:
        preview = ", ".join(missing_required[:10])
        raise KeyError(
            f"Missing required canonical localization keys in {WONDER_LOCALIZATION_FILE}: {preview}"
        )

    return required_keys


def render_expected_localization_output(language: str, localization_data: dict[str, dict[str, str]]) -> str:
    header = f"l_{language}:"
    lines = [header]
    for line in render_header(GENERATED_LOC_SCRIPT_REL[language], GENERATED_LOC_DATA_REL):
        lines.append(f" {line}")
    for key, value in localization_data[language].items():
        lines.append(loc_line(key, value))
    return "\n".join(lines).rstrip() + "\n"


def render_expected_concepts_output(wonders: list[dict[str, Any]]) -> str:
    lines = render_header(CONCEPT_SCRIPT_REL)
    for wonder in wonders:
        texture = CONCEPT_ICONS.get(wonder["category"], CONCEPT_ICONS["infrastructure_category"])
        lines.extend(
            [
                f"{wonder['concept']} = {{",
                f'\ttexture = "{texture}"',
                "}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


class WonderLocalizationService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._log_fragments: list[str] = []
        self.wonders: list[dict[str, Any]] = []
        self.mechanics: dict[str, Any] = {}
        self.wonders_data: dict[str, Any] = {}
        self.mechanics_data: dict[str, Any] = {}
        self.unique_wonders_data: dict[str, Any] = {}
        self.event_suffixes: dict[int, str] = {}
        self.localization_data: dict[str, dict[str, str]] = {}
        self.country_modifier_options: list[dict[str, Any]] = []
        self.local_modifier_options: list[dict[str, Any]] = []
        self.reward_type_options: list[dict[str, Any]] = []
        self.reload_from_disk()
        self._append_log("[server] Wonder Localization Editor ready\n")

    @property
    def log_text(self) -> str:
        return "".join(self._log_fragments)

    def _append_log(self, text: str) -> None:
        self._log_fragments.append(text)
        if len(self._log_fragments) > 400:
            self._log_fragments = self._log_fragments[-400:]

    def reload_from_disk(self) -> None:
        with self._lock:
            self.wonders_data = load_wonders_source_data()
            self.mechanics_data = load_mechanics_source_data()
            self.unique_wonders_data = load_unique_wonders_source_data()
            self.wonders, self.mechanics = load_all_wonder_mechanics_data()
            self.wonders = sorted(self.wonders, key=lambda item: int(item["id"]))
            self.event_suffixes = load_engineering_department_suffix_map()
            self.localization_data = load_wonder_localization_data()
            (
                self.country_modifier_options,
                self.local_modifier_options,
                self.reward_type_options,
            ) = _modifier_option_catalog(self.mechanics_data, self.unique_wonders_data)
            validate_canonical_localization_data(
                self.wonders,
                self.mechanics,
                self.event_suffixes,
                self.localization_data,
            )

    def bootstrap_payload(self) -> dict[str, Any]:
        with self._lock:
            wonders = self.list_wonders()
            first_wonder_id = wonders[0]["id"] if wonders else None
            return {
                "title": "Towards Victory Wonder Editor",
                "status": "Ready",
                "wonders": wonders,
                "current_wonder": self.get_wonder_payload(first_wonder_id) if first_wonder_id is not None else None,
                "log_text": self.log_text,
            }

    def list_wonders(self, filter_text: str = "") -> list[dict[str, Any]]:
        normalized_filter = filter_text.strip().lower()
        wonders: list[dict[str, Any]] = []
        for wonder in self.wonders:
            haystack = " ".join(
                [
                    str(wonder["id"]),
                    wonder["key"],
                    wonder["concept"],
                    wonder.get("base_key", ""),
                    wonder.get("size", ""),
                    wonder_size_label(wonder.get("size", "")),
                    self._wonder_name(wonder, "english"),
                    self._wonder_name(wonder, "simp_chinese"),
                ]
            ).lower()
            if normalized_filter and normalized_filter not in haystack:
                continue
            wonders.append(self._wonder_summary(wonder))
        return wonders

    def get_wonder_payload(self, wonder_id: int | None) -> dict[str, Any] | None:
        with self._lock:
            if wonder_id is None:
                return None
            wonder = self._get_wonder(wonder_id)
            specs = self._build_specs_for_wonder(wonder)
            mechanics_specs = self._build_mechanics_specs_for_wonder(wonder)
            return {
                "summary": self._wonder_summary(wonder),
                "meta": self._wonder_meta(wonder),
                "languages": self._serialize_specs(specs),
                "mechanics": self._serialize_mechanics_specs(mechanics_specs),
                "status": f"Loaded {wonder['key']}",
            }

    def reload_wonder_payload(self, wonder_id: int) -> dict[str, Any]:
        self.reload_from_disk()
        payload = self.get_wonder_payload(wonder_id)
        if payload is None:
            raise KeyError(f"Unknown wonder id: {wonder_id}")
        payload["status"] = f"Reloaded {payload['summary']['key']}"
        return {
            "status": payload["status"],
            "wonder": payload,
            "wonders": self.list_wonders(),
            "log_text": self.log_text,
        }

    def _apply_wonder_edits(
        self,
        wonder_id: int,
        values_by_language: dict[str, dict[str, str]] | None,
        mechanics_values: dict[str, Any] | None = None,
    ) -> dict[str, bool]:
        wonder = self._get_wonder(wonder_id)
        specs = self._build_specs_for_wonder(wonder)
        mechanics_specs = self._build_mechanics_specs_for_wonder(wonder)
        localization_updates: dict[str, dict[str, str]] = {language: {} for language in LANGUAGES}
        incoming_values = values_by_language or {}
        incoming_mechanics = mechanics_values or {}

        for language, language_specs in specs.items():
            language_values = incoming_values.get(language, {})
            for spec in language_specs:
                value = normalize_editor_text(str(language_values.get(spec.key, spec.original_value)))
                if value == spec.original_value:
                    continue
                localization_updates[language][spec.key] = value

        wonders_file_changed = False
        mechanics_file_changed = False
        unique_file_changed = False
        for spec in mechanics_specs:
            raw_value = incoming_mechanics.get(spec.key, spec.original_value)
            if spec.field_type in {
                "modifier_table",
                "reward_editor",
                "unique_ritual_editor",
                "site_trigger_template",
                "site_preference_template",
                "suitability_knowledge_editor",
            }:
                value = str(raw_value)
            else:
                value = normalize_multiline_editor_text(str(raw_value))
            if value == spec.original_value:
                continue
            if not spec.editable:
                continue

            if spec.target_kind == "site_rule":
                if spec.field_type == "site_trigger_template":
                    rendered_script = render_trigger_script_from_state(value, context=spec.key)
                elif spec.field_type == "site_preference_template":
                    rendered_script = render_preference_script_from_state(value, context=spec.key)
                elif spec.field_type == "suitability_knowledge_editor":
                    self.mechanics_data["site_rules"][spec.target_key][spec.target_parent_key] = (
                        suitability_knowledge_from_editor_state(value, context=spec.key)
                    )
                    mechanics_file_changed = True
                    continue
                else:
                    rendered_script = value
                if not rendered_script:
                    raise ValueError(f"{spec.key} cannot be empty")
                self.mechanics_data["site_rules"][spec.target_key][spec.target_parent_key] = rendered_script
                mechanics_file_changed = True
                continue

            if spec.target_kind == "generic_size":
                size = normalize_editor_wonder_size(value, context=spec.key)
                entry = self._get_generic_wonder_source(spec.target_key)
                entry["size"] = size
                wonders_file_changed = True
                continue

            if spec.target_kind == "unique_prototype":
                if not value:
                    raise ValueError(f"{spec.key} cannot be empty")
                self._get_generic_wonder_by_key(value)
                entry = self._get_unique_wonder_source(spec.target_key)
                entry["base_key"] = value
                entry["mechanic_key"] = value
                unique_file_changed = True
                continue

            if spec.target_kind == "building_local":
                if spec.field_type == "modifier_table":
                    parsed = mapping_from_modifier_rows(value, context=spec.key)
                else:
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                self.mechanics_data.setdefault("buildings", {}).setdefault(spec.target_key, {})[
                    spec.target_parent_key
                ] = parsed
                mechanics_file_changed = True
                continue

            if spec.target_kind == "base_modifiers":
                if spec.field_type == "modifier_table":
                    parsed = mapping_from_modifier_rows(value, context=spec.key)
                else:
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                self.mechanics_data.setdefault("base_modifiers", {})[spec.target_key] = parsed
                mechanics_file_changed = True
                continue

            if spec.target_kind == "generic_ritual":
                if spec.field_type == "modifier_table":
                    parsed_modifier = mapping_from_modifier_rows(value, context=spec.key)
                    modifier_field = "country_modifier" if spec.target_parent_key == "style_1" else "local_modifier"
                    parsed = {modifier_field: parsed_modifier}
                elif spec.field_type == "reward_editor":
                    payload = parse_structured_editor_value(value, context=spec.key)
                    if not isinstance(payload, dict):
                        raise ValueError(f"{spec.key} must be an object")
                    cost_type_value = payload.get("cost_type", "")
                    cost_type_raw = "" if cost_type_value is None else str(cost_type_value).strip()
                    cost_type = cost_type_raw or None
                    if cost_type not in SUPPORTED_RITUAL_COST_TYPES:
                        supported = ", ".join(sorted(option for option in SUPPORTED_RITUAL_COST_TYPES if option is not None))
                        raise ValueError(f"{spec.key}.cost_type must be empty or one of: {supported}")
                    parsed = {
                        "cost_type": cost_type,
                        "reward": reward_list_from_rows(value, context=f"{spec.key}.reward"),
                    }
                else:
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                self.mechanics_data.setdefault("generic_rituals", {}).setdefault(spec.target_key, {})[
                    spec.target_parent_key
                ] = parsed
                mechanics_file_changed = True
                continue

            if spec.target_kind == "unique_location":
                if not value:
                    raise ValueError(f"{spec.key} cannot be empty")
                entry = self._get_unique_wonder_source(spec.target_key)
                entry["location"] = value
                unique_file_changed = True
                continue

            if spec.target_kind == "unique_ritual":
                if spec.field_type == "unique_ritual_editor":
                    parsed = unique_ritual_from_editor_state(value, context=spec.key)
                else:
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                entry = self._get_unique_wonder_source(spec.target_key)
                updated_entry = dict(entry)
                updated_entry["ritual"] = parsed
                updated_entry["ritual"] = normalize_unique_ritual(updated_entry)
                entry["ritual"] = updated_entry["ritual"]
                unique_file_changed = True
                continue

            raise ValueError(f"Unsupported mechanics target kind: {spec.target_kind}")

        localization_file_changed = any(localization_updates[language] for language in LANGUAGES)
        if localization_file_changed:
            for language, updates in localization_updates.items():
                if not updates:
                    continue
                self.localization_data[language].update(updates)

        return {
            "localization": localization_file_changed,
            "mechanics": mechanics_file_changed,
            "wonders": wonders_file_changed,
            "unique": unique_file_changed,
        }

    def save_wonders(
        self,
        drafts_by_wonder_id: dict[int, dict[str, Any]],
        *,
        current_wonder_id: int | None = None,
        regenerate: bool = True,
    ) -> dict[str, Any]:
        with self._lock:
            changed = {
                "localization": False,
                "mechanics": False,
                "wonders": False,
                "unique": False,
            }
            changed_wonder_ids: list[int] = []
            try:
                for wonder_id, draft in sorted(drafts_by_wonder_id.items(), key=lambda item: int(item[0])):
                    page_changes = self._apply_wonder_edits(
                        int(wonder_id),
                        draft.get("values", {}),
                        draft.get("mechanics", {}),
                    )
                    if any(page_changes.values()):
                        changed_wonder_ids.append(int(wonder_id))
                    for key, value in page_changes.items():
                        changed[key] = changed[key] or value

                changed_files: list[str] = []
                if changed["localization"]:
                    validate_canonical_localization_data(
                        self.wonders,
                        self.mechanics,
                        self.event_suffixes,
                        self.localization_data,
                    )
                    save_wonder_localization_data(self.localization_data)
                    changed_files.append(str(WONDER_LOCALIZATION_FILE.relative_to(REPO_ROOT)))

                if changed["mechanics"]:
                    save_yaml_document(MECHANICS_FILE, self.mechanics_data)
                    changed_files.append(str(MECHANICS_FILE.relative_to(REPO_ROOT)))

                if changed["wonders"]:
                    save_yaml_document(WONDERS_FILE, self.wonders_data)
                    changed_files.append(str(WONDERS_FILE.relative_to(REPO_ROOT)))

                if changed["unique"]:
                    save_yaml_document(UNIQUE_WONDERS_FILE, self.unique_wonders_data, preserve_leading_comments=True)
                    changed_files.append(str(UNIQUE_WONDERS_FILE.relative_to(REPO_ROOT)))

                if regenerate:
                    if changed["wonders"] or changed["mechanics"] or changed["unique"]:
                        self._run_generators(WONDER_DATA_REGEN_SCRIPTS)
                    elif changed["localization"]:
                        self._run_generators(REGEN_SCRIPTS)

                self.reload_from_disk()
                target_wonder_id = current_wonder_id
                if target_wonder_id is None and drafts_by_wonder_id:
                    target_wonder_id = int(next(iter(drafts_by_wonder_id)))
                payload = self.get_wonder_payload(target_wonder_id) if target_wonder_id is not None else None
                if payload is None and target_wonder_id is not None:
                    raise KeyError(f"Unknown wonder id after reload: {target_wonder_id}")

                if changed_files:
                    page_count = len(changed_wonder_ids)
                    status = f"Saved {page_count} page{'s' if page_count != 1 else ''}: {', '.join(changed_files)}"
                else:
                    status = "No changes"

                if payload is not None:
                    payload["status"] = status
                return {
                    "status": status,
                    "changed_files": changed_files,
                    "changed_wonder_ids": changed_wonder_ids,
                    "wonders": self.list_wonders(),
                    "wonder": payload,
                    "log_text": self.log_text,
                }
            except Exception as exc:
                self._append_log(f"[error] {exc}\n")
                self.reload_from_disk()
                raise

    def save_wonder(
        self,
        wonder_id: int,
        values_by_language: dict[str, dict[str, str]] | None,
        mechanics_values: dict[str, Any] | None = None,
        *,
        regenerate: bool = True,
    ) -> dict[str, Any]:
        return self.save_wonders(
            {
                int(wonder_id): {
                    "values": values_by_language or {},
                    "mechanics": mechanics_values or {},
                }
            },
            current_wonder_id=wonder_id,
            regenerate=regenerate,
        )

    def _localization_value(self, language: str, key: str) -> str:
        if language not in self.localization_data:
            raise KeyError(f"Missing language {language} in {WONDER_LOCALIZATION_FILE}")
        language_values = self.localization_data[language]
        if key not in language_values:
            raise KeyError(f"Missing canonical localization key {key} in {WONDER_LOCALIZATION_FILE} ({language})")
        return language_values[key]

    def _get_wonder(self, wonder_id: int) -> dict[str, Any]:
        for wonder in self.wonders:
            if int(wonder["id"]) == int(wonder_id):
                return wonder
        raise KeyError(f"Unknown wonder id: {wonder_id}")

    def _get_unique_wonder_source(self, wonder_key: str) -> dict[str, Any]:
        for wonder in self.unique_wonders_data.get("unique_wonders", []):
            if wonder.get("key") == wonder_key:
                return wonder
        raise KeyError(f"Unknown unique wonder key: {wonder_key}")

    def _get_generic_wonder_source(self, wonder_key: str) -> dict[str, Any]:
        for wonder in self.wonders_data.get("wonders", []):
            if wonder.get("key") == wonder_key:
                return wonder
        raise KeyError(f"Unknown generic wonder key: {wonder_key}")

    def _get_generic_wonder_by_key(self, wonder_key: str) -> dict[str, Any]:
        for wonder in self.wonders:
            if not wonder.get("is_unique") and wonder.get("key") == wonder_key:
                return wonder
        raise KeyError(f"Unknown generic wonder key: {wonder_key}")

    def _wonder_name(self, wonder: dict[str, Any], language: str) -> str:
        return self._localization_value(language, wonder_name_key(wonder))

    def _wonder_image_info(self, wonder: dict[str, Any]) -> dict[str, Any]:
        raw_stem = str(wonder.get("image") or f"tv_wonder_{wonder['key']}").strip()
        filename = raw_stem if raw_stem.lower().endswith(".png") else f"{raw_stem}.png"
        if not filename or Path(filename).name != filename:
            return {
                "stem": raw_stem,
                "filename": filename,
                "path": "",
                "url": None,
                "exists": False,
            }

        image_path = GENERATED_WONDER_IMAGES_DIR / filename
        exists = image_path.is_file()
        return {
            "stem": Path(filename).stem,
            "filename": filename,
            "path": f"data/generated_wonders/{filename}",
            "url": f"{WONDER_IMAGE_URL_PREFIX}/{quote(filename)}" if exists else None,
            "exists": exists,
        }

    def _wonder_summary(self, wonder: dict[str, Any]) -> dict[str, Any]:
        kind_label = "Unique" if wonder.get("is_unique") else "Generic"
        name_en = self._wonder_name(wonder, "english")
        name_zh = self._wonder_name(wonder, "simp_chinese")
        size = str(wonder.get("size", ""))
        return {
            "id": int(wonder["id"]),
            "key": wonder["key"],
            "concept": wonder["concept"],
            "is_unique": bool(wonder.get("is_unique")),
            "kind_label": kind_label,
            "size": size,
            "size_label": wonder_size_label(size),
            "name_en": name_en,
            "name_zh": name_zh,
            "display_name": f"{name_zh} / {name_en}",
            "image": self._wonder_image_info(wonder),
        }

    def _wonder_meta(self, wonder: dict[str, Any]) -> dict[str, Any]:
        meta = {
            "id": int(wonder["id"]),
            "key": wonder["key"],
            "concept": wonder["concept"],
            "name_en": self._wonder_name(wonder, "english"),
            "name_zh": self._wonder_name(wonder, "simp_chinese"),
            "is_unique": bool(wonder.get("is_unique")),
            "size": str(wonder.get("size", "")),
            "size_label": wonder_size_label(wonder.get("size", "")),
            "image": self._wonder_image_info(wonder),
        }
        if wonder.get("is_unique"):
            meta["base_key"] = wonder.get("base_key")
            meta["mechanic_key"] = wonder.get("mechanic_key")
            meta["base_effect_multiplier"] = wonder.get("base_effect_multiplier", 1)
            meta["location"] = wonder.get("location")
        return meta

    def _generic_wonder_options(self) -> list[dict[str, str]]:
        options: list[dict[str, str]] = []
        for wonder in self.wonders:
            if wonder.get("is_unique"):
                continue
            options.append(
                {
                    "value": wonder["key"],
                    "label": self._wonder_summary(wonder)["display_name"],
                }
            )
        return options

    def _serialize_specs(self, specs: dict[str, list[FieldSpec]]) -> dict[str, dict[str, Any]]:
        payload: dict[str, dict[str, Any]] = {}
        for language in LANGUAGES:
            sections: list[dict[str, Any]] = []
            current_group: str | None = None
            current_fields: list[dict[str, Any]] = []
            for spec in specs.get(language, []):
                if spec.group != current_group:
                    if current_group is not None:
                        sections.append({"group": current_group, "fields": current_fields})
                    current_group = spec.group
                    current_fields = []
                current_fields.append(spec.to_api_dict())
            if current_group is not None:
                sections.append({"group": current_group, "fields": current_fields})
            payload[language] = {
                "label": LANGUAGE_LABELS[language],
                "sections": sections,
            }
        return payload

    def _serialize_mechanics_specs(self, specs: list[MechanicsFieldSpec]) -> dict[str, Any]:
        sections: list[dict[str, Any]] = []
        current_group: str | None = None
        current_fields: list[dict[str, Any]] = []
        for spec in specs:
            if spec.group != current_group:
                if current_group is not None:
                    sections.append({"group": current_group, "fields": current_fields})
                current_group = spec.group
                current_fields = []
            current_fields.append(spec.to_api_dict())
        if current_group is not None:
            sections.append({"group": current_group, "fields": current_fields})
        return {
            "label": "Mechanics",
            "sections": sections,
        }

    def _build_mechanics_specs_for_wonder(self, wonder: dict[str, Any]) -> list[MechanicsFieldSpec]:
        specs: list[MechanicsFieldSpec] = []
        prototype_key = mechanic_key(wonder)
        shared_source_kind = "shared"
        inherits_from_prototype = bool(wonder.get("is_unique"))
        base_effect_multiplier = wonder.get("base_effect_multiplier", 1)
        site_help_text = (
            "Inherited from the prototype. Use the prototype selector to change this rule set; edit the prototype wonder to modify the script."
            if inherits_from_prototype
            else "Choose a site-condition template, then adjust the allowed condition atoms instead of editing the raw trigger script directly."
        )
        preference_help_text = (
            "Inherited from the prototype. Use the prototype selector to change this rule set; edit the prototype wonder to modify the script."
            if inherits_from_prototype
            else "Choose a preference template, then edit condition bonus rows and scaled bonus rows without hand-writing script blocks."
        )
        suitability_help_text = (
            "Inherited from the prototype. These rows are revealed to the player one completed survey at a time."
            if inherits_from_prototype
            else "Player-visible suitability rows. Keep the order aligned with the semantic clues you want surveys to reveal."
        )
        base_modifier_help_text = (
            (
                f"Inherited from the prototype. Displayed values already apply this unique wonder's x{base_effect_multiplier} "
                "base-effect multiplier; edit the prototype wonder to modify the underlying modifier list."
            )
            if inherits_from_prototype
            else "Structured editor for data/wonder_mechanics.yaml base_modifiers entries."
        )
        base_modifier_mapping = self.mechanics_data.get("base_modifiers", {}).get(prototype_key, {})
        displayed_base_modifier_mapping = (
            scale_numeric_mapping(base_modifier_mapping, base_effect_multiplier)
            if inherits_from_prototype
            else base_modifier_mapping
        )
        building_design = self.mechanics_data.get("buildings", {}).get(prototype_key, {})
        final_local_mapping = building_design.get("final_local", {})
        displayed_final_building_local_mapping = (
            authored_final_building_local_modifiers(wonder, self.mechanics)
            if inherits_from_prototype
            else {}
        )

        if not inherits_from_prototype:
            self._add_mechanics_spec(
                specs,
                group="Core Data",
                label="Wonder size",
                key=f"mechanics.generic_size.{wonder['key']}",
                source_kind="generic",
                file_path=WONDERS_FILE,
                original_value=str(wonder["size"]),
                field_type="select",
                target_kind="generic_size",
                target_key=wonder["key"],
                height=1,
                options=WONDER_SIZE_OPTIONS,
                help_text="Small, medium, or large. Unique wonders inherit this value from their prototype wonder.",
                target_path=f"wonders[{wonder['key']}].size",
            )

        self._add_mechanics_spec(
            specs,
            group="Site Rules",
            label="Build condition template",
            key=f"mechanics.site_trigger.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=MECHANICS_FILE,
            original_value=serialize_structured_editor_value(
                parse_trigger_builder_state(site_trigger_script_for_key(self.mechanics_data, prototype_key))
            ),
            field_type="site_trigger_template",
            target_kind="site_rule",
            target_key=prototype_key,
            target_parent_key="trigger_script",
            height=10,
            help_text=site_help_text,
            target_path=f"site_rules.{prototype_key}.trigger_script",
            structured_value=parse_trigger_builder_state(site_trigger_script_for_key(self.mechanics_data, prototype_key)),
            editable=not inherits_from_prototype,
            prototype_key=prototype_key if inherits_from_prototype else "",
        )
        self._add_mechanics_spec(
            specs,
            group="Site Rules",
            label="Survey preference template",
            key=f"mechanics.site_preference.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=MECHANICS_FILE,
            original_value=serialize_structured_editor_value(
                parse_preference_builder_state(site_preference_script_for_key(self.mechanics_data, prototype_key))
            ),
            field_type="site_preference_template",
            target_kind="site_rule",
            target_key=prototype_key,
            target_parent_key="preference_script",
            height=14,
            help_text=preference_help_text,
            target_path=f"site_rules.{prototype_key}.preference_script",
            structured_value=parse_preference_builder_state(site_preference_script_for_key(self.mechanics_data, prototype_key)),
            editable=not inherits_from_prototype,
            prototype_key=prototype_key if inherits_from_prototype else "",
        )
        suitability_rows = suitability_knowledge_for_key(self.mechanics_data, prototype_key)
        self._add_mechanics_spec(
            specs,
            group="Site Rules",
            label="Player suitability knowledge rows",
            key=f"mechanics.suitability_knowledge.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=MECHANICS_FILE,
            original_value=serialize_structured_editor_value(
                build_suitability_knowledge_editor_state(suitability_rows)
            ),
            field_type="suitability_knowledge_editor",
            target_kind="site_rule",
            target_key=prototype_key,
            target_parent_key="suitability_knowledge",
            height=12,
            help_text=suitability_help_text,
            target_path=f"site_rules.{prototype_key}.suitability_knowledge",
            structured_value=build_suitability_knowledge_editor_state(suitability_rows),
            editable=not inherits_from_prototype,
            prototype_key=prototype_key if inherits_from_prototype else "",
        )

        if inherits_from_prototype:
            inherited_local_state = build_modifier_editor_state(
                displayed_final_building_local_mapping,
                modifier_scope="local",
                options=self.local_modifier_options,
            )
            self._add_mechanics_spec(
                specs,
                group="Final Building Local Effects",
                label="Inherited doubled local effects",
                key=f"mechanics.building_local.inherited.{wonder['key']}",
                source_kind=shared_source_kind,
                file_path=MECHANICS_FILE,
                original_value=serialize_structured_editor_value(inherited_local_state),
                field_type="modifier_table",
                target_kind="building_local",
                target_key=prototype_key,
                target_parent_key="final_local",
                height=10,
                help_text=(
                    f"Inherited from prototype. Displayed values already apply this unique wonder's x{base_effect_multiplier} "
                    "multiplier to the prototype's authored final_local package; edit the prototype wonder to modify the source."
                ),
                target_path=f"buildings.{prototype_key}.final_local",
                structured_value=inherited_local_state,
                editable=False,
                prototype_key=prototype_key,
            )
        else:
            final_local_state = build_modifier_editor_state(
                final_local_mapping,
                modifier_scope="local",
                options=self.local_modifier_options,
            )
            self._add_mechanics_spec(
                specs,
                group="Final Building Local Effects",
                label="Shared final local effects",
                key=f"mechanics.building_local.{wonder['key']}.final_local",
                source_kind=shared_source_kind,
                file_path=MECHANICS_FILE,
                original_value=serialize_structured_editor_value(final_local_state),
                field_type="modifier_table",
                target_kind="building_local",
                target_key=prototype_key,
                target_parent_key="final_local",
                height=10,
                help_text="Shared local effects applied identically to all three final-building branches.",
                target_path=f"buildings.{prototype_key}.final_local",
                structured_value=final_local_state,
            )
        self._add_mechanics_spec(
            specs,
            group="Base Modifiers",
            label="Per-level base modifiers",
            key=f"mechanics.base_modifiers.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=MECHANICS_FILE,
            original_value=serialize_structured_editor_value(
                build_modifier_editor_state(
                    displayed_base_modifier_mapping,
                    modifier_scope="country",
                    options=self.country_modifier_options,
                )
            ),
            field_type="modifier_table",
            target_kind="base_modifiers",
            target_key=prototype_key,
            height=10,
            help_text=base_modifier_help_text,
            target_path=f"base_modifiers.{prototype_key}",
            structured_value=build_modifier_editor_state(
                displayed_base_modifier_mapping,
                modifier_scope="country",
                options=self.country_modifier_options,
            ),
            editable=not inherits_from_prototype,
            prototype_key=prototype_key if inherits_from_prototype else "",
        )

        if wonder.get("is_unique"):
            unique_key = wonder["key"]
            unique_entry = self._get_unique_wonder_source(unique_key)
            self._add_mechanics_spec(
                specs,
                group="Unique Wonder",
                label="Prototype wonder",
                key=f"mechanics.unique_prototype.{unique_key}",
                source_kind="unique",
                file_path=UNIQUE_WONDERS_FILE,
                original_value=str(unique_entry["base_key"]),
                field_type="select",
                target_kind="unique_prototype",
                target_key=unique_key,
                height=1,
                options=self._generic_wonder_options(),
                help_text="Choose which generic wonder this unique wonder inherits its site rules and base modifiers from.",
                target_path=f"unique_wonders[{unique_key}].base_key",
            )
            self._add_mechanics_spec(
                specs,
                group="Unique Wonder",
                label="Fixed location",
                key=f"mechanics.unique_location.{unique_key}",
                source_kind="unique",
                file_path=UNIQUE_WONDERS_FILE,
                original_value=str(unique_entry["location"]),
                field_type="text",
                target_kind="unique_location",
                target_key=unique_key,
                height=2,
                help_text="Edits data/unique_wonders.yaml location.",
                target_path=f"unique_wonders[{unique_key}].location",
            )
            self._add_mechanics_spec(
                specs,
                group="Unique Wonder",
                label="Ritual plan",
                key=f"mechanics.unique_ritual.{unique_key}",
                source_kind="unique",
                file_path=UNIQUE_WONDERS_FILE,
                original_value=serialize_structured_editor_value(
                    build_unique_ritual_editor_state(
                        unique_entry["ritual"],
                        country_modifier_options=self.country_modifier_options,
                        local_modifier_options=self.local_modifier_options,
                        reward_type_options=self.reward_type_options,
                    )
                ),
                field_type="unique_ritual_editor",
                target_kind="unique_ritual",
                target_key=unique_key,
                height=18,
                help_text="Structured editor for data/unique_wonders.yaml ritual. Advanced script hooks stay visible but no longer require editing a whole YAML block.",
                target_path=f"unique_wonders[{unique_key}].ritual",
                structured_value=build_unique_ritual_editor_state(
                    unique_entry["ritual"],
                    country_modifier_options=self.country_modifier_options,
                    local_modifier_options=self.local_modifier_options,
                    reward_type_options=self.reward_type_options,
                ),
            )
            return specs

        generic_ritual = self.mechanics_data.get("generic_rituals", {}).get(wonder["key"], {})
        style_1 = generic_ritual.get("style_1", {})
        style_2 = generic_ritual.get("style_2", {})
        style_3 = generic_ritual.get("style_3", {})

        self._add_mechanics_spec(
            specs,
            group="Generic Ritual",
            label="Style 1 country modifiers",
            key=f"mechanics.generic_ritual.{wonder['key']}.style_1",
            source_kind="shared",
            file_path=MECHANICS_FILE,
            original_value=serialize_structured_editor_value(
                build_modifier_editor_state(
                    style_1.get("country_modifier", {}),
                    modifier_scope="country",
                    options=self.country_modifier_options,
                )
            ),
            field_type="modifier_table",
            target_kind="generic_ritual",
            target_key=wonder["key"],
            target_parent_key="style_1",
            height=10,
            help_text="Structured editor for generic ritual style 1 country modifiers.",
            target_path=f"generic_rituals.{wonder['key']}.style_1.country_modifier",
            structured_value=build_modifier_editor_state(
                style_1.get("country_modifier", {}),
                modifier_scope="country",
                options=self.country_modifier_options,
            ),
        )
        style_2_editor_state = build_modifier_editor_state(
            style_2.get("local_modifier", {}),
            modifier_scope="local",
            options=self.local_modifier_options,
            derived_mapping=generic_style_2_derived_modifier_mapping(wonder),
            derived_title=GENERIC_STYLE_2_DERIVED_TITLE,
            derived_help_text=GENERIC_STYLE_2_DERIVED_HELP_TEXT,
        )
        self._add_mechanics_spec(
            specs,
            group="Generic Ritual",
            label="Style 2 local modifiers",
            key=f"mechanics.generic_ritual.{wonder['key']}.style_2",
            source_kind="shared",
            file_path=MECHANICS_FILE,
            original_value=serialize_structured_editor_value(style_2_editor_state),
            field_type="modifier_table",
            target_kind="generic_ritual",
            target_key=wonder["key"],
            target_parent_key="style_2",
            height=10,
            help_text="Structured editor for generic ritual style 2 local modifiers. The read-only section below shows the estate power that the building generator adds automatically.",
            target_path=f"generic_rituals.{wonder['key']}.style_2.local_modifier",
            structured_value=style_2_editor_state,
        )
        self._add_mechanics_spec(
            specs,
            group="Generic Ritual",
            label="Style 3 reward package",
            key=f"mechanics.generic_ritual.{wonder['key']}.style_3",
            source_kind="shared",
            file_path=MECHANICS_FILE,
            original_value=serialize_structured_editor_value(
                build_reward_editor_state(
                    rows=reward_rows_from_list(style_3.get("reward", [])),
                    options=self.reward_type_options,
                    cost_type=style_3.get("cost_type"),
                    cost_options=[
                        {"value": "", "label": "None"},
                        *[
                            {"value": cost_type, "label": cost_type}
                            for cost_type in sorted(option for option in SUPPORTED_RITUAL_COST_TYPES if option is not None)
                        ],
                    ],
                )
            ),
            field_type="reward_editor",
            target_kind="generic_ritual",
            target_key=wonder["key"],
            target_parent_key="style_3",
            height=10,
            help_text="Structured editor for style 3 cost type and one-time rewards.",
            target_path=f"generic_rituals.{wonder['key']}.style_3",
            structured_value=build_reward_editor_state(
                rows=reward_rows_from_list(style_3.get("reward", [])),
                options=self.reward_type_options,
                cost_type=style_3.get("cost_type"),
                cost_options=[
                    {"value": "", "label": "None"},
                    *[
                        {"value": cost_type, "label": cost_type}
                        for cost_type in sorted(option for option in SUPPORTED_RITUAL_COST_TYPES if option is not None)
                    ],
                ],
            ),
        )
        return specs

    def _add_mechanics_spec(
        self,
        specs: list[MechanicsFieldSpec],
        *,
        group: str,
        label: str,
        key: str,
        source_kind: str,
        file_path: Path,
        original_value: str,
        field_type: str,
        target_kind: str,
        target_key: str,
        target_parent_key: str = "",
        height: int = 3,
        options: list[dict[str, Any]] | None = None,
        help_text: str = "",
        target_path: str = "",
        structured_value: Any | None = None,
        editable: bool = True,
        prototype_key: str = "",
    ) -> None:
        specs.append(
            MechanicsFieldSpec(
                key=key,
                label=label,
                group=group,
                source_kind=source_kind,
                file_path=file_path,
                original_value=original_value,
                field_type=field_type,
                target_kind=target_kind,
                target_key=target_key,
                target_parent_key=target_parent_key,
                height=height,
                options=list(options or []),
                help_text=help_text,
                source_path=str(file_path.relative_to(REPO_ROOT)),
                target_path=target_path,
                structured_value=structured_value,
                editable=editable,
                prototype_key=prototype_key,
            )
        )

    def _build_specs_for_wonder(self, wonder: dict[str, Any]) -> dict[str, list[FieldSpec]]:
        specs = {language: [] for language in LANGUAGES}
        code = wonder["key"].upper()

        for language in LANGUAGES:
            self._add_localization_field(specs, language, "Concept", "Concept description", f"{concept_key_for_wonder(wonder)}_desc", height=5)

            self._add_localization_field(specs, language, "Proposal", "Proposal brief", f"TV_ENGINEERING_PROPOSAL_{code}_TEXT", height=3)
            self._add_localization_field(specs, language, "Proposal", "Resume proposal", f"TV_ENGINEERING_PROPOSAL_RESUME_{code}_TEXT", height=3)
            self._add_localization_field(specs, language, "Proposal", "Expand proposal", f"TV_ENGINEERING_PROPOSAL_EXPAND_{code}_TEXT", height=3)
            self._add_localization_field(specs, language, "Proposal", "Locked text", f"TV_ENGINEERING_LOCKED_{code}_TEXT", height=2)
            self._add_localization_field(specs, language, "Proposal", "Proposal button", f"TV_ENGINEERING_PROPOSAL_BUTTON_{code}", height=2)
            self._add_localization_field(specs, language, "Proposal", "Lock tooltip", f"TV_WONDER_LOCK_{code}_TT", height=2)

            self._add_localization_field(specs, language, "Wonder", "Wonder name", wonder_name_key(wonder), height=2)
            self._add_localization_field(specs, language, "Wonder", "Wonder description", f"{wonder_name_key(wonder)}_desc", height=3)
            for part, label in (
                ("foundation", "Foundation module"),
                ("body", "Main structure module"),
                ("function", "Functional module"),
                ("decoration", "Crowning module"),
            ):
                self._add_localization_field(specs, language, "Wonder", f"{label} name", f"{wonder_name_key(wonder)}_{part}", height=2)
                self._add_localization_field(specs, language, "Wonder", f"{label} description", f"{wonder_name_key(wonder)}_{part}_desc", height=3)

            if not wonder.get("is_unique"):
                self._add_localization_field(specs, language, "Wonder", "Ritual annex name", f"{wonder_name_key(wonder)}_ritual_annex", height=2)
                self._add_localization_field(specs, language, "Wonder", "Ritual annex description", f"{wonder_name_key(wonder)}_ritual_annex_desc", height=3)

            for level in range(1, 7):
                self._add_localization_field(
                    specs,
                    language,
                    "Modifiers",
                    f"Level {ROMAN_NUMERALS[level]} static modifier",
                    f"STATIC_MODIFIER_NAME_{wonder_name_key(wonder)}_level_{level}",
                    height=2,
                )

            if not wonder.get("is_unique"):
                self._add_localization_field(
                    specs,
                    language,
                    "Modifiers",
                    "Ritual burden modifier",
                    f"STATIC_MODIFIER_NAME_{ritual_burden_modifier_name(wonder)}",
                    height=2,
                )
                self._add_localization_field(
                    specs,
                    language,
                    "Modifiers",
                    "Ritual blessing modifier",
                    f"STATIC_MODIFIER_NAME_{ritual_blessing_modifier_name(wonder)}",
                    height=2,
                )

            for style in ceremony_styles(wonder):
                branch_name = self._branch_name(wonder, style, language)
                building = final_building_for_style(wonder, style)
                label_prefix = f"Style {style}: {branch_name}"
                self._add_localization_field(specs, language, "Branches", f"{label_prefix} final building name", building, height=2)
                self._add_localization_field(specs, language, "Branches", f"{label_prefix} final building description", f"{building}_desc", height=3)
                ceremony_modifier = ceremony_modifier_for_style(wonder, self.mechanics, style)
                if ceremony_modifier is not None:
                    self._add_localization_field(
                        specs,
                        language,
                        "Branches",
                        f"{label_prefix} modifier name",
                        f"STATIC_MODIFIER_NAME_{ceremony_modifier[0]}",
                        height=2,
                    )
                self._add_localization_field(
                    specs,
                    language,
                    "Branches",
                    f"{label_prefix} button",
                    branch_button_key(building),
                    height=2,
                )
                self._add_localization_field(
                    specs,
                    language,
                    "Branches",
                    f"{label_prefix} active ritual text",
                    active_ritual_key(wonder, style),
                    height=3,
                )

            if wonder.get("is_unique"):
                self._add_localization_field(
                    specs,
                    language,
                    "Events",
                    "Wonder completion event",
                    event_desc_key(wonder, self.event_suffixes),
                    height=6,
                )
            else:
                suffix = self.event_suffixes.get(int(wonder["id"]))
                if suffix is not None:
                    for style in ceremony_styles(wonder):
                        branch_name = self._branch_name(wonder, style, language)
                        self._add_localization_field(
                            specs,
                            language,
                            "Events",
                            f"Completion event style {style}: {branch_name}",
                            event_desc_key(wonder, self.event_suffixes, style),
                            height=6,
                        )
                    self._add_localization_field(
                        specs,
                        language,
                        "Events",
                        "World news event",
                        event_desc_key(wonder, self.event_suffixes, None),
                        height=6,
                    )

        return specs

    def _branch_name(self, wonder: dict[str, Any], style: int, language: str) -> str:
        building = final_building_for_style(wonder, style)
        return self._localization_value(language, branch_button_key(building))

    def _add_localization_field(
        self,
        specs: dict[str, list[FieldSpec]],
        language: str,
        group: str,
        label: str,
        key: str | None,
        *,
        height: int = 3,
    ) -> None:
        if key is None:
            raise KeyError(f"Missing generated localization key for {label}")
        specs[language].append(
            FieldSpec(
                key=key,
                label=label,
                group=group,
                language=language,
                file_path=WONDER_LOCALIZATION_FILE,
                original_value=self._localization_value(language, key),
                height=height,
            )
        )

    def _run_generators(self, scripts: tuple[str, ...] = REGEN_SCRIPTS) -> None:
        self._append_log("\n[regen] Starting wonder generation\n")
        for script in scripts:
            command = [
                "conda",
                "run",
                "--no-capture-output",
                "-n",
                "eu5",
                "python",
                script,
            ]
            self._append_log(f"$ {' '.join(command)}\n")
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            if result.stdout:
                self._append_log(result.stdout)
            if result.stderr:
                self._append_log(result.stderr)
            if result.returncode != 0:
                self._append_log(f"[regen] Failed: {script} exited with {result.returncode}\n")
                raise RuntimeError(f"{script} exited with {result.returncode}. See log for details.")
        self._append_log("[regen] Complete\n")


def build_check_report() -> list[str]:
    wonders, mechanics = load_all_wonder_mechanics_data()
    localization_data = load_wonder_localization_data()
    suffixes = load_engineering_department_suffix_map()
    required_keys = validate_canonical_localization_data(wonders, mechanics, suffixes, localization_data)

    for language, path in GENERATED_LOC_FILES.items():
        generated_map = load_localization_map(path)
        canonical_map = localization_data[language]
        if generated_map != canonical_map:
            missing = sorted(set(canonical_map) - set(generated_map))
            extra = sorted(set(generated_map) - set(canonical_map))
            mismatched = sorted(
                key
                for key in set(generated_map) & set(canonical_map)
                if generated_map[key] != canonical_map[key]
            )
            details: list[str] = []
            if missing:
                details.append(f"missing keys: {', '.join(missing[:10])}")
            if extra:
                details.append(f"extra keys: {', '.join(extra[:10])}")
            if mismatched:
                details.append(f"value mismatches: {', '.join(mismatched[:10])}")
            raise ValueError(f"{path} does not match canonical localization ({'; '.join(details)})")

        actual_text = normalize_text_file(path.read_text(encoding="utf-8-sig"))
        expected_text = render_expected_localization_output(language, localization_data)
        if actual_text != expected_text:
            raise ValueError(f"{path} is not rendered from the canonical localization source exactly")

    manual_loc_paths = sorted(set(MANUAL_CONCEPT_FILES.values()) | set(MANUAL_ENGINEERING_FILES.values()))
    for path in manual_loc_paths:
        manual_keys = set(load_localization_map(path))
        overlap = sorted(manual_keys & required_keys)
        if overlap:
            preview = ", ".join(overlap[:10])
            raise ValueError(f"Manual localization file duplicates canonical wonder keys: {path} -> {preview}")

    expected_concepts = render_expected_concepts_output(wonders)
    actual_concepts = normalize_text_file(CONCEPT_FILE.read_text(encoding="utf-8-sig"))
    if actual_concepts != expected_concepts:
        raise ValueError(f"{CONCEPT_FILE} is not synchronized with wonder source data")

    return [
        f"Validated {len(wonders)} wonders against canonical source {WONDER_LOCALIZATION_FILE.relative_to(REPO_ROOT)}",
        f"Required canonical localization keys: {len(required_keys)}",
        f"Generated localization files match canonical output: {len(GENERATED_LOC_FILES)}",
        f"Concept generator output matches wonder source: {CONCEPT_FILE.relative_to(REPO_ROOT)}",
        f"Checked manual localization overlap across {len(manual_loc_paths)} files",
    ]
