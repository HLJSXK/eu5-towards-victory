"""Conversions between Wonder source values and structured editor values."""
from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

import yaml

from scripts_engineering_department.wonder_mechanics.io import dump_yaml_document
from scripts_engineering_department.wonder_mechanics.rituals import (
    CEREMONY_STAGE_COUNT,
    SUPPORTED_RITUAL_COST_TYPES,
    SUPPORTED_RITUAL_LISTENERS,
    SUPPORTED_UNIQUE_RITUAL_MODES,
    ceremony_cost_computed_value,
)


WONDER_SIZE_LABELS = {
    "small": "Small",
    "medium": "Medium",
    "large": "Large",
}
WONDER_SIZE_OPTIONS = [
    {"value": size, "label": label}
    for size, label in WONDER_SIZE_LABELS.items()
]
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
    return json.dumps(without_editor_options(payload), ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def without_editor_options(value: object) -> object:
    """Reserve options and *_options for UI lists, never edited source data."""
    if isinstance(value, dict):
        return {
            key: without_editor_options(item)
            for key, item in value.items()
            if key != "options" and not key.endswith("_options")
        }
    if isinstance(value, list):
        return [without_editor_options(item) for item in value]
    return value


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


def parse_unique_initial_level(raw_value: object, *, context: str) -> int:
    parsed = parse_editor_scalar(raw_value)
    if not isinstance(parsed, int) or isinstance(parsed, bool):
        raise ValueError(f"{context} must be an integer from 0 to 6")
    if parsed < 0 or parsed > 6:
        raise ValueError(f"{context} must be an integer from 0 to 6")
    return parsed


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


def ceremony_cost_rows_from_list(cost: list[object]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in cost:
        if not isinstance(item, dict):
            continue
        catalog = str(item.get("catalog", "")).strip()
        entry_id = str(item.get("type", "")).strip()
        composite = f"{catalog}:{entry_id}" if catalog else entry_id
        rows.append(
            {
                "type": composite,
                "value": stringify_editor_scalar(item.get("value", "")),
            }
        )
    return rows


def ceremony_cost_list_from_rows(raw_value: object, *, context: str, stage_index: int) -> list[dict[str, object]]:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"{context}.rows must be a list")
    cost: list[dict[str, object]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"{context}.rows[{index}] must be an object")
        composite = str(row.get("type", "")).strip()
        if not composite:
            continue
        if ":" not in composite:
            raise ValueError(f"{context}.rows[{index}] cost type must be 'catalog:id', got {composite!r}")
        catalog, _, entry_id = composite.partition(":")
        cost.append(
            {
                "catalog": catalog,
                "type": entry_id,
                # Always recomputed from the catalog + stage parity — never trust a
                # user-edited value cell, since the schema no longer allows hand-picked
                # magnitudes (see docs/knowledge/risk_cards/wonders.md rule 20).
                "value": ceremony_cost_computed_value(catalog, entry_id, stage_index),
            }
        )
    return cost


def build_unique_ceremony_editor_state(
    ceremony: dict[str, Any],
    *,
    cost_type_options: list[dict[str, str]],
) -> dict[str, Any]:
    stages = ceremony.get("stages", [])
    return {
        "stage_count": CEREMONY_STAGE_COUNT,
        "stages": [
            {
                "title_en": stage.get("title_en", ""),
                "title_zh": stage.get("title_zh", ""),
                "desc_en": stage.get("desc_en", ""),
                "desc_zh": stage.get("desc_zh", ""),
                "icon": stage.get("icon", ""),
                "icon_rationale": stage.get("icon_rationale", ""),
                "cost": {
                    "rows": ceremony_cost_rows_from_list(list(stage.get("cost", []))),
                    "options": list(cost_type_options),
                },
                "option_pay_en": stage.get("option_pay_en", ""),
                "option_pay_zh": stage.get("option_pay_zh", ""),
                "option_decline_en": stage.get("option_decline_en", ""),
                "option_decline_zh": stage.get("option_decline_zh", ""),
            }
            for stage in stages
        ],
    }


def unique_ceremony_from_editor_state(raw_value: object, *, context: str) -> dict[str, Any]:
    payload = parse_structured_editor_value(raw_value, context=context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context} must be an object")

    stages = payload.get("stages", [])
    if not isinstance(stages, list):
        raise ValueError(f"{context}.stages must be a list")

    normalized_stages: list[dict[str, Any]] = []
    for index, stage in enumerate(stages, start=1):
        if not isinstance(stage, dict):
            raise ValueError(f"{context}.stages[{index}] must be an object")
        normalized_stages.append(
            {
                "title_en": normalize_multiline_editor_text(str(stage.get("title_en", ""))),
                "title_zh": normalize_multiline_editor_text(str(stage.get("title_zh", ""))),
                "desc_en": normalize_multiline_editor_text(str(stage.get("desc_en", ""))),
                "desc_zh": normalize_multiline_editor_text(str(stage.get("desc_zh", ""))),
                "icon": str(stage.get("icon", "")).strip(),
                "icon_rationale": normalize_multiline_editor_text(str(stage.get("icon_rationale", ""))),
                "cost": ceremony_cost_list_from_rows(
                    stage.get("cost", {}),
                    context=f"{context}.stages[{index}].cost",
                    stage_index=index,
                ),
                "option_pay_en": normalize_multiline_editor_text(str(stage.get("option_pay_en", ""))),
                "option_pay_zh": normalize_multiline_editor_text(str(stage.get("option_pay_zh", ""))),
                "option_decline_en": normalize_multiline_editor_text(str(stage.get("option_decline_en", ""))),
                "option_decline_zh": normalize_multiline_editor_text(str(stage.get("option_decline_zh", ""))),
            }
        )
    return {"stages": normalized_stages}
