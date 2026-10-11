"""Localized Wonder option catalogs and payload catalog references."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from scripts_engineering_department.wonder_mechanics.rituals import (
    CEREMONY_COST_CATALOGS,
    STYLE_3_REWARD_EFFECTS,
    load_cost_reward_unit_entries,
    load_cost_reward_units,
)

from . import sources
from .localization import LANGUAGES


INDEX_LANGUAGE_BY_EDITOR_LANGUAGE = {
    "english": "en",
    "simp_chinese": "zh",
}
OPTION_LOC_LINE_RE = re.compile(r'^\s*([A-Za-z0-9_.-]+):(?:\d+)?\s+"(.*)"\s*$')
REWARD_LABEL_CANDIDATES = {
    "all_estate_satisfaction": ("estate_satisfaction", "game_concept_estate_satisfaction"),
    "celestial_authority": ("celestial_authority", "game_concept_celestial_authority"),
    "estate_satisfaction": ("estate_satisfaction", "game_concept_estate_satisfaction"),
    "imperial_authority": ("imperial_authority", "game_concept_imperial_authority"),
    "papal_authority": ("papal_authority", "game_concept_papal_authority"),
    "religious_influence": ("religious_influence", "game_concept_religious_influence"),
    "ruler_adm": ("administration", "game_concept_administration", "adm"),
    "ruler_dip": ("diplomacy", "game_concept_diplomacy", "dip"),
    "ruler_mil": ("military", "game_concept_military", "mil"),
    "scaled_gold": ("gold", "game_concept_gold"),
    "site_control": ("control", "game_concept_control"),
    "site_development": ("development", "game_concept_development"),
    "site_prosperity": ("prosperity", "game_concept_prosperity"),
    "site_raw_material_workers": ("raw_material", "game_concept_raw_material"),
}
REWARD_FALLBACK_LABELS = {
    "all_estate_satisfaction": "All Estate Satisfaction",
    "celestial_authority": "Celestial Authority",
    "estate_satisfaction": "Estate Satisfaction",
    "imperial_authority": "Imperial Authority",
    "papal_authority": "Papal Authority",
    "religious_influence": "Religious Influence",
    "ruler_adm": "Ruler Administrative Skill",
    "ruler_dip": "Ruler Diplomatic Skill",
    "ruler_mil": "Ruler Military Skill",
    "scaled_gold": "Scaled Gold",
    "site_control": "Site Control",
    "site_development": "Site Development",
    "site_prosperity": "Site Prosperity",
    "site_raw_material_workers": "Site Raw Material Workers",
    "yearly_gold": "Yearly Gold",
    "yearly_manpower": "Yearly Manpower",
    "yearly_sailors": "Yearly Sailors",
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


def _cost_reward_unit_labels(entry: dict[str, Any], fallback: str) -> dict[str, str]:
    labels = entry.get("loc", {}) if isinstance(entry, dict) else {}
    if not isinstance(labels, dict):
        labels = {}
    english = _scrub_option_markup(labels.get("en") or fallback)
    simp_chinese = _scrub_option_markup(labels.get("zh") or english)
    return {
        "english": english or fallback,
        "simp_chinese": simp_chinese or english or fallback,
    }


def _cost_reward_unit_entry_index(catalogs: dict[str, list[dict[str, Any]]], catalog: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for entry in catalogs.get(catalog, []):
        if not isinstance(entry, dict):
            continue
        entry_id = str(entry.get("id", "")).strip()
        if not entry_id:
            continue
        indexed[entry_id] = {**entry, "_catalog": catalog}
    return indexed


def _cost_reward_unit_option_source(catalog: str, entry_id: str) -> str:
    return f"data/cost_reward_units.yaml:{catalog}.{entry_id}"


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


def _parse_reference_loc_value(raw_value: str) -> str:
    return raw_value.replace(r"\"", '"').replace(r"\n", "\n")


def _load_reference_localization_subset(language: str, wanted_keys: set[str]) -> dict[str, str]:
    root = sources.REFERENCE_LOC_DIR_BY_EDITOR_LANGUAGE[language]
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


def _catalog_string_values(raw_value: object) -> set[str]:
    if not isinstance(raw_value, list):
        return set()
    return {str(item).strip() for item in raw_value if str(item).strip()}


def _load_wonder_editor_catalog() -> dict[str, Any]:
    if not sources.WONDER_EDITOR_CATALOG_FILE.exists():
        return {}
    payload = yaml.safe_load(sources.WONDER_EDITOR_CATALOG_FILE.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(payload, dict):
        return {}
    return payload


def ceremony_stage_cost_options() -> list[dict[str, Any]]:
    """Options for the ceremony cost row editor. The dropdown value remains
    'catalog:id'; displayed/searchable labels come from data/cost_reward_units.yaml."""
    catalogs = load_cost_reward_units()
    entries = load_cost_reward_unit_entries()
    options: list[dict[str, Any]] = []
    for catalog in CEREMONY_COST_CATALOGS:
        entry_index = _cost_reward_unit_entry_index(entries, catalog)
        for entry_id in sorted(catalogs.get(catalog, {})):
            entry = entry_index.get(entry_id, {})
            fallback = entry_id.replace("_", " ").strip().title()
            labels = _cost_reward_unit_labels(entry, fallback)
            option_source = _cost_reward_unit_option_source(catalog, entry_id)
            options.append(
                {
                    "value": f"{catalog}:{entry_id}",
                    "label": f"[{catalog}] {labels['simp_chinese']}",
                    "key_label": f"{catalog}:{entry_id}",
                    "localized_label": f"[{catalog}] {labels['simp_chinese']}",
                    "label_en": f"[{catalog}] {labels['english']}",
                    "label_zh": f"[{catalog}] {labels['simp_chinese']}",
                    "search_text": " ".join(
                        part
                        for part in (
                            catalog,
                            entry_id,
                            labels["english"],
                            labels["simp_chinese"],
                            str(entry.get("value", "")),
                            option_source,
                        )
                        if part
                    ).lower(),
                    "source": option_source,
                }
            )
    return options


def _modifier_options(
    values: set[str],
    modifier_index: dict[str, Any],
    unit_entries: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    unit_entries = unit_entries or {}
    options: list[dict[str, Any]] = []
    for value in sorted(values):
        index_entry = modifier_index.get(value, {})
        if not isinstance(index_entry, dict):
            index_entry = {}
        fallback = _prettify_option_key(value)
        labels = _localized_pair_from_index_entry(index_entry, "name", fallback)
        descriptions = _localized_pair_from_index_entry(index_entry, "description", "")
        unit_entry = unit_entries.get(value)
        source = ""
        extra = {
            key: index_entry[key]
            for key in ("value_kind", "decimals", "category", "color")
            if key in index_entry
        }
        if unit_entry:
            unit_labels = _cost_reward_unit_labels(unit_entry, fallback)
            if labels["english"] == fallback and labels["simp_chinese"] == fallback:
                labels = unit_labels
            else:
                labels = {
                    language: labels.get(language) or unit_labels[language]
                    for language in LANGUAGES
                }
            catalog = str(unit_entry.get("_catalog", "")).strip()
            if catalog:
                source = _cost_reward_unit_option_source(catalog, value)
                extra["catalog"] = catalog
            if "value" in unit_entry:
                extra["default_value"] = unit_entry["value"]
        options.append(_localized_option(value, labels, descriptions=descriptions, source=source, extra=extra))
    return options


def _reward_options(
    reward_types: set[str],
    reward_sources: dict[str, str],
    unit_entries: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    unit_entries = unit_entries or {}
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
        unit_entry = unit_entries.get(reward_type)
        extra: dict[str, Any] = {}
        if unit_entry:
            labels = _cost_reward_unit_labels(unit_entry, fallback)
            catalog = str(unit_entry.get("_catalog", "")).strip()
            unit_source = _cost_reward_unit_option_source(catalog, reward_type) if catalog else ""
            if catalog:
                extra["catalog"] = catalog
            if "value" in unit_entry:
                extra["default_value"] = unit_entry["value"]
            if source and unit_source:
                source = f"{source} ({unit_source})"
            elif unit_source:
                source = unit_source
        else:
            labels = {}
            for language in LANGUAGES:
                labels[language] = ""
                for candidate in candidate_map[reward_type]:
                    value = loc_values[language].get(candidate)
                    if value:
                        labels[language] = value
                        break
                if not labels[language]:
                    labels[language] = fallback
        options.append(_localized_option(reward_type, labels, source=source, extra=extra))
    return options


def modifier_option_catalog(
    mechanics_data: dict[str, Any],
    unique_wonders_data: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    country_modifiers: set[str] = set()
    local_modifiers: set[str] = set()
    reward_types: set[str] = set()
    editor_catalog = _load_wonder_editor_catalog()
    modifier_index = _load_json_index(sources.MODIFIER_LOCALIZATION_INDEX_FILE, "modifiers")
    reward_sources = {
        str(key): str(value)
        for key, value in (editor_catalog.get("style_3_reward_sources", {}) or {}).items()
    }
    for reward_type, spec in STYLE_3_REWARD_EFFECTS.items():
        reward_sources.setdefault(reward_type, str(spec.get("effect", "")))

    unit_catalogs = load_cost_reward_unit_entries()
    country_modifier_units = _cost_reward_unit_entry_index(unit_catalogs, "country_modifier")
    local_modifier_units = _cost_reward_unit_entry_index(unit_catalogs, "local_modifier")
    reward_unit_entries: dict[str, dict[str, Any]] = {}
    for catalog in ("country_reward", "local_reward", "character_reward"):
        reward_unit_entries.update(_cost_reward_unit_entry_index(unit_catalogs, catalog))

    country_modifiers.update(country_modifier_units)
    local_modifiers.update(local_modifier_units)
    reward_types.update(reward_unit_entries)

    cost_reward_unit_types = editor_catalog.get("cost_reward_unit_types", {})
    if isinstance(cost_reward_unit_types, dict):
        country_modifiers.update(_catalog_string_values(cost_reward_unit_types.get("country_modifier", [])))
        local_modifiers.update(_catalog_string_values(cost_reward_unit_types.get("local_modifier", [])))
        for catalog in ("country_reward", "local_reward", "character_reward"):
            reward_types.update(_catalog_string_values(cost_reward_unit_types.get(catalog, [])))

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
            reward_types.update(
                str(item.get("type", "")).strip()
                for item in style_3.get("reward", [])
                if isinstance(item, dict) and str(item.get("type", "")).strip()
            )

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
            reward_types.update(
                str(item.get("type", "")).strip()
                for item in reward
                if isinstance(item, dict) and str(item.get("type", "")).strip()
            )
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
        _modifier_options(country_modifiers, modifier_index, country_modifier_units),
        _modifier_options(local_modifiers, modifier_index, local_modifier_units),
        _reward_options(reward_types, reward_sources, reward_unit_entries),
    )


def reference_option_catalogs(value: object, catalogs: dict[str, list[dict[str, Any]]]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, list) and (key == "options" or key.endswith("_options")):
                for catalog_id, options in catalogs.items():
                    if item == options:
                        value[key] = {"catalog_ref": catalog_id}
                        break
            else:
                reference_option_catalogs(item, catalogs)
    elif isinstance(value, list):
        for item in value:
            reference_option_catalogs(item, catalogs)
