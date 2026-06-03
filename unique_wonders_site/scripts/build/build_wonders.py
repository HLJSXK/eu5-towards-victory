#!/usr/bin/env python
"""Build the frontend data file for the unique wonders atlas."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.wonder_localization_lib import load_wonder_localization_data, wonder_name_key
from scripts.wonder_mechanics_lib import (
    authored_final_building_local_modifiers,
    ceremony_modifier_for_style,
    load_all_wonder_mechanics_data,
    mechanic_key,
    scale_numeric_modifier_mapping,
)

SITE_ROOT = REPO_ROOT / "unique_wonders_site"
DEFAULT_LOCATIONS_INDEX = (
    REPO_ROOT
    / "reference_mods"
    / "national_destinies_site"
    / "dist"
    / "data"
    / "locations_index.json"
)
DEFAULT_REFERENCE_LOC = (
    REPO_ROOT
    / "reference_mods"
    / "national_destinies_site"
    / "dist"
    / "data"
    / "loc.json"
)
DEFAULT_OUT = SITE_ROOT / "dist" / "data" / "unique_wonders.json"

LANGUAGES = ("en", "zh")
SOURCE_LANGUAGE = {
    "en": "english",
    "zh": "simp_chinese",
}

SIZE_LABELS = {
    "small": {"en": "Small", "zh": "小型"},
    "medium": {"en": "Medium", "zh": "中型"},
    "large": {"en": "Large", "zh": "大型"},
}

CATEGORY_LABELS = {
    "cultural_category": {"en": "Cultural", "zh": "文化"},
    "government_category": {"en": "Government", "zh": "政务"},
    "infrastructure_category": {"en": "Infrastructure", "zh": "基建"},
    "military_category": {"en": "Military", "zh": "军事"},
    "religious_category": {"en": "Religious", "zh": "宗教"},
    "commerce_category": {"en": "Commerce", "zh": "商业"},
    "industry_category": {"en": "Industry", "zh": "产业"},
}


def prettify(key: str) -> str:
    return str(key).replace("_", " ").strip().title()


def scrub_markup(text: str) -> str:
    """Flatten common EU5 loc markup for a web-only plain text atlas."""
    text = str(text or "")
    text = re.sub(r"\[([^|\]]+)\|[A-Za-z]+\]", lambda match: prettify(match.group(1)), text)
    text = re.sub(r"@([A-Za-z0-9_]+)!", "", text)
    text = re.sub(r"#\w+\s*", "", text).replace("#!", "")
    return " ".join(text.split())


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required JSON file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def localization_value(
    loc_data: dict[str, dict[str, str]],
    key: str,
    *,
    language: str,
    fallback: str | None = None,
) -> str:
    source_language = SOURCE_LANGUAGE[language]
    value = loc_data.get(source_language, {}).get(key)
    if value is None and fallback is not None:
        value = fallback
    if value is None:
        value = prettify(key)
    return scrub_markup(value)


def localized_pair(
    loc_data: dict[str, dict[str, str]],
    key: str,
    *,
    fallback: str | None = None,
) -> dict[str, str]:
    return {
        lang: localization_value(loc_data, key, language=lang, fallback=fallback)
        for lang in LANGUAGES
    }


def reference_loc_pair(reference_loc: dict[str, str], key: str) -> dict[str, str]:
    english = scrub_markup(reference_loc.get(key) or prettify(key))
    return {"en": english, "zh": english}


def scalar_value(value: object) -> object:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if value is None:
        return None
    return str(value)


def rows_from_mapping(mapping: dict[str, object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, value in mapping.items():
        rows.append({"key": str(key), "value": scalar_value(value)})
    return rows


def rows_from_rewards(rewards: list[object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for raw in rewards:
        if not isinstance(raw, dict):
            continue
        reward_type = str(raw.get("type", "")).strip()
        if not reward_type:
            continue
        rows.append({"key": reward_type, "value": scalar_value(raw.get("value"))})
    return rows


def effect_section(
    section_id: str,
    title_en: str,
    title_zh: str,
    rows: list[dict[str, object]],
    *,
    scope: str,
    value_label_en: str = "Value",
    value_label_zh: str = "数值",
    meta: dict[str, object] | None = None,
) -> dict[str, object] | None:
    normalized_meta = meta or {}
    if not rows and not normalized_meta:
        return None
    return {
        "id": section_id,
        "title": {"en": title_en, "zh": title_zh},
        "scope": scope,
        "value_label": {"en": value_label_en, "zh": value_label_zh},
        "rows": rows,
        "meta": normalized_meta,
    }


def localized_label(labels: dict[str, dict[str, str]], key: str) -> dict[str, str]:
    if key in labels:
        return dict(labels[key])
    pretty = prettify(key)
    return {"en": pretty, "zh": pretty}


def build_record(
    wonder: dict[str, Any],
    *,
    base_wonders: dict[str, dict[str, Any]],
    mechanics: dict[str, Any],
    loc_data: dict[str, dict[str, str]],
    locations_index: dict[str, Any],
    reference_loc: dict[str, str],
) -> dict[str, object]:
    location_key = str(wonder["location"])
    location_info = locations_index.get(location_key)
    if not isinstance(location_info, dict):
        raise KeyError(f"Unique wonder {wonder['key']} references unknown location {location_key}")

    base_key = mechanic_key(wonder)
    base_wonder = base_wonders[base_key]
    name_key = wonder_name_key(wonder)
    final_building = next(iter(wonder["final_buildings"].values()))

    base_modifiers = mechanics.get("base_modifiers", {}).get(base_key, {})
    displayed_base_modifiers = scale_numeric_modifier_mapping(
        base_modifiers,
        wonder.get("base_effect_multiplier", 1),
    )
    final_local_modifiers = authored_final_building_local_modifiers(wonder, mechanics)

    effects: list[dict[str, object]] = []
    for section in (
        effect_section(
            "final_local",
            "Inherited final local effects",
            "继承的最终建筑本地效果",
            rows_from_mapping(final_local_modifiers),
            scope="local",
        ),
        effect_section(
            "base_modifiers",
            "Per-level country effects",
            "每级国家效果",
            rows_from_mapping(displayed_base_modifiers),
            scope="country",
        ),
    ):
        if section is not None:
            effects.append(section)

    ritual = wonder["ritual"]
    ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, 1)
    ceremony_meta: dict[str, object] = {}
    if ceremony_modifier is not None:
        ceremony_meta["source"] = ceremony_modifier[0]
    section = effect_section(
        "ritual_country_modifier",
        "Ritual country modifiers",
        "仪式国家修正",
        rows_from_mapping(ritual.get("country_modifier", {})),
        scope="country",
        meta=ceremony_meta,
    )
    if section is not None:
        effects.append(section)

    section = effect_section(
        "ritual_rewards",
        "Ritual rewards",
        "仪式奖励",
        rows_from_rewards(ritual.get("reward", [])),
        scope="reward",
        value_label_en="Amount",
        value_label_zh="数量",
    )
    if section is not None:
        effects.append(section)

    timed = ritual.get("timed", {})
    if isinstance(timed, dict):
        section = effect_section(
            "timed_burden",
            "Timed burden modifiers",
            "限时负担修正",
            rows_from_mapping(timed.get("burden_modifier", {})),
            scope="country",
            meta={"years": timed.get("years", 1)} if timed.get("burden_modifier") else None,
        )
        if section is not None:
            effects.append(section)
        section = effect_section(
            "timed_blessing",
            "Timed blessing modifiers",
            "限时祝福修正",
            rows_from_mapping(timed.get("blessing_modifier", {})),
            scope="country",
            meta={"years": timed.get("years", 1)} if timed.get("blessing_modifier") else None,
        )
        if section is not None:
            effects.append(section)

    auxiliary = ritual.get("auxiliary_building", {})
    if isinstance(auxiliary, dict):
        auxiliary_meta = {
            key: value
            for key, value in {
                "maintenance": auxiliary.get("maintenance"),
                "build_time": auxiliary.get("build_time"),
                "construction_demand": auxiliary.get("construction_demand"),
                "price": auxiliary.get("price"),
                "max_levels": auxiliary.get("max_levels"),
            }.items()
            if value not in (None, "", {})
        }
        section = effect_section(
            "auxiliary_local",
            "Auxiliary local modifiers",
            "附属建筑本地修正",
            rows_from_mapping(auxiliary.get("local_modifier", {})),
            scope="local",
            meta=auxiliary_meta,
        )
        if section is not None:
            effects.append(section)
        section = effect_section(
            "auxiliary_attributes",
            "Auxiliary attributes",
            "附属建筑属性",
            rows_from_mapping(auxiliary.get("attributes", {})),
            scope="attribute",
        )
        if section is not None:
            effects.append(section)

    return {
        "id": wonder["id"],
        "key": wonder["key"],
        "name": localized_pair(loc_data, final_building, fallback=loc_data["english"].get(name_key)),
        "description": localized_pair(
            loc_data,
            f"{final_building}_desc",
            fallback=loc_data["english"].get(f"{name_key}_desc", ""),
        ),
        "base_key": base_key,
        "base_name": localized_pair(loc_data, wonder_name_key(base_wonder)),
        "size": wonder["size"],
        "size_label": localized_label(SIZE_LABELS, wonder["size"]),
        "category": wonder["category"],
        "category_label": localized_label(CATEGORY_LABELS, wonder["category"]),
        "location_key": location_key,
        "location_name": reference_loc_pair(reference_loc, location_key),
        "centroid": location_info["centroid"],
        "bbox": location_info["bbox"],
        "image": wonder.get("image") or f"tv_wonder_{wonder['key']}",
        "construction_requirements": [],
        "effects": effects,
    }


def build_payload(locations_index_path: Path, reference_loc_path: Path) -> dict[str, object]:
    all_wonders, mechanics = load_all_wonder_mechanics_data(include_unique=True)
    loc_data = load_wonder_localization_data()
    locations_index = load_json(locations_index_path).get("locations", {})
    if not isinstance(locations_index, dict):
        raise TypeError(f"{locations_index_path}.locations must be an object")

    reference_loc_payload = load_json(reference_loc_path) if reference_loc_path.exists() else {}
    reference_loc = reference_loc_payload.get("strings", {})
    if not isinstance(reference_loc, dict):
        reference_loc = {}

    base_wonders = {
        wonder["key"]: wonder
        for wonder in all_wonders
        if not wonder.get("is_unique")
    }
    unique_wonders = [
        wonder
        for wonder in all_wonders
        if wonder.get("is_unique")
    ]
    unique_wonders.sort(key=lambda item: int(item["id"]))

    records = [
        build_record(
            wonder,
            base_wonders=base_wonders,
            mechanics=mechanics,
            loc_data=loc_data,
            locations_index=locations_index,
            reference_loc=reference_loc,
        )
        for wonder in unique_wonders
    ]

    return {
        "version": 1,
        "wonders": records,
        "counts": {
            "unique_wonders": len(records),
            "missing_locations": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locations-index", type=Path, default=DEFAULT_LOCATIONS_INDEX)
    parser.add_argument("--reference-loc", type=Path, default=DEFAULT_REFERENCE_LOC)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    payload = build_payload(args.locations_index, args.reference_loc)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {args.out.relative_to(REPO_ROOT)} "
        f"({payload['counts']['unique_wonders']} unique wonders)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

