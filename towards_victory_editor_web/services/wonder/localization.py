"""Canonical localization keys, validation and generated-output checks."""
from __future__ import annotations

import sys
from typing import Any

from scripts_engineering_department.wonder_localization_lib import (
    engineering_department_wonder_mechanics_localization_map,
    load_engineering_department_suffix_map,
    load_localization_map,
    load_wonder_localization_data,
)
from scripts_engineering_department.wonder_mechanics.io import load_all_wonder_mechanics_data
from scripts_engineering_department.wonder_mechanics.naming import (
    final_building_for_style,
    wonder_static_display_modifier_name,
    wonder_static_local_display_modifier_name,
)
from scripts_engineering_department.wonder_mechanics.render import loc_line, render_header
from scripts_engineering_department.wonder_mechanics.rituals import (
    ceremony_styles,
    ritual_blessing_modifier_name,
    ritual_burden_modifier_name,
    ritual_plan_for_style,
    unique_ceremony_modifier_name,
)
from scripts_engineering_department.wonder_mechanics.suitability_conditions import ID_TO_NUMBERED_LOC_KEY

from . import sources
from ..wonder_generation import LOCALIZATION_SCRIPTS
from .values import normalize_text_file


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


LANGUAGES = ("english", "simp_chinese")
LANGUAGE_LABELS = {
    "english": "English",
    "simp_chinese": "Simplified Chinese",
}
ROMAN_NUMERALS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
}
CONCEPT_ICONS = {
    "infrastructure_category": "gfx/interface/icons/location_icons/new/prosperity.dds",
    "military_category": "gfx/interface/icons/flat_icons/tabicons/military.dds",
    "cultural_category": "gfx/interface/icons/flat_icons/cultural_influence.dds",
    "government_category": "gfx/interface/icons/flat_icons/diplomatic_reputation.dds",
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
)


def ceremony_modifier_for_style(wonder: dict[str, Any], mechanics: dict[str, Any], style: int) -> tuple[str, dict] | None:
    if not wonder.get("is_unique"):
        return None
    modifiers = ritual_plan_for_style(wonder, mechanics, style).get("country_modifier", {})
    if not modifiers:
        return None
    return unique_ceremony_modifier_name(wonder), modifiers


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
        keys.add(f"STATIC_MODIFIER_NAME_{wonder_static_display_modifier_name(wonder, level)}")
        keys.add(f"STATIC_MODIFIER_NAME_{wonder_static_local_display_modifier_name(wonder, level)}")

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
    keys.update(ID_TO_NUMBERED_LOC_KEY.values())
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
    required_keys = required_canonical_localization_keys(wonders, mechanics, suffixes)

    missing_in_chinese = sorted(required_keys - chinese_keys)
    if missing_in_chinese:
        preview = ", ".join(missing_in_chinese[:10])
        raise ValueError(
            f"Missing Simplified Chinese localization keys in {sources.WONDER_LOCALIZATION_FILE}: {preview}"
        )

    missing_in_english = sorted(required_keys - english_keys)
    if missing_in_english:
        preview = ", ".join(missing_in_english[:10])
        raise ValueError(
            f"Missing English localization keys in {sources.WONDER_LOCALIZATION_FILE}: {preview}"
        )

    return required_keys


def render_expected_localization_output(language: str, localization_data: dict[str, dict[str, str]]) -> str:
    header = f"l_{language}:"
    lines = [header]
    for line in render_header(LOCALIZATION_SCRIPTS[language], sources.GENERATED_LOC_DATA_REL):
        lines.append(f" {line}")
    for key, value in generated_localization_map(language, localization_data).items():
        lines.append(loc_line(key, value))
    return "\n".join(lines).rstrip() + "\n"


def generated_localization_map(language: str, localization_data: dict[str, dict[str, str]]) -> dict[str, str]:
    return engineering_department_wonder_mechanics_localization_map(language, localization_data[language])


def render_expected_concepts_output(wonders: list[dict[str, Any]]) -> str:
    from scripts_engineering_department.main_menu.common.game_concepts.gen_tv_engineering_department_wonder_mechanics_concepts import (
        generate,
    )

    return generate()


def build_check_report() -> list[str]:
    wonders, mechanics = load_all_wonder_mechanics_data()
    localization_data = load_wonder_localization_data()
    suffixes = load_engineering_department_suffix_map()
    required_keys = validate_canonical_localization_data(wonders, mechanics, suffixes, localization_data)

    for language, path in sources.GENERATED_LOC_FILES.items():
        generated_map = load_localization_map(path)
        canonical_map = generated_localization_map(language, localization_data)
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

    manual_loc_paths = sorted(set(sources.MANUAL_CONCEPT_FILES.values()) | set(sources.MANUAL_ENGINEERING_FILES.values()))
    for path in manual_loc_paths:
        manual_keys = set(load_localization_map(path))
        overlap = sorted(manual_keys & required_keys)
        if overlap:
            preview = ", ".join(overlap[:10])
            raise ValueError(f"Manual localization file duplicates canonical wonder keys: {path} -> {preview}")

    expected_concepts = render_expected_concepts_output(wonders)
    actual_concepts = normalize_text_file(sources.CONCEPT_FILE.read_text(encoding="utf-8-sig"))
    if actual_concepts != expected_concepts:
        raise ValueError(f"{sources.CONCEPT_FILE} is not synchronized with wonder source data")

    return [
        f"Validated {len(wonders)} wonders against canonical source {sources.WONDER_LOCALIZATION_FILE.relative_to(sources.REPO_ROOT)}",
        f"Required canonical localization keys: {len(required_keys)}",
        f"Generated localization files match canonical output: {len(sources.GENERATED_LOC_FILES)}",
        f"Concept generator output matches wonder source: {sources.CONCEPT_FILE.relative_to(sources.REPO_ROOT)}",
        f"Checked manual localization overlap across {len(manual_loc_paths)} files",
    ]


def localization_value(localization_data: dict[str, dict[str, str]], language: str, key: str) -> str:
    if language not in localization_data:
        raise KeyError(f"Missing language {language} in {sources.WONDER_LOCALIZATION_FILE}")
    language_values = localization_data[language]
    if key not in language_values:
        raise KeyError(f"Missing canonical localization key {key} in {sources.WONDER_LOCALIZATION_FILE} ({language})")
    return language_values[key]
