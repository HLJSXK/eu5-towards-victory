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

from scripts.wonder_localization_lib import (
    concept_desc_key,
    load_wonder_localization_data,
    wonder_name_key,
)
from scripts.wonder_mechanics_lib import (
    authored_final_building_local_modifiers,
    ceremony_modifier_for_style,
    ceremony_styles,
    final_building_for_style,
    load_all_wonder_mechanics_data,
    mechanic_key,
    ritual_plan_for_style,
    scale_numeric_modifier_mapping,
    site_trigger_script_for_key,
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
DEFAULT_MODIFIER_LOCALIZATION_INDEX = REPO_ROOT / "data" / "index" / "modifier_localization.json"
DEFAULT_TRIGGER_LOCALIZATION_INDEX = REPO_ROOT / "data" / "index" / "trigger_localization.json"
WONDER_IMAGE_SOURCE_ROOT = REPO_ROOT / "data" / "generated_wonders"
DIST_WONDER_IMAGE_ROOT = Path("images") / "wonders"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

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

KIND_LABELS = {
    "generic": {"en": "Generic", "zh": "\u901a\u7528"},
    "unique": {"en": "Unique", "zh": "\u72ec\u7279"},
}

GENERIC_LOCATION_LABEL = {
    "en": "No fixed map location",
    "zh": "\u65e0\u56fa\u5b9a\u5730\u56fe\u4f4d\u7f6e",
}

CONCEPT_LABELS = {
    "building": {"en": "Building", "zh": "建筑"},
    "buildings": {"en": "Buildings", "zh": "建筑"},
    "capital": {"en": "Capital", "zh": "首都"},
    "country": {"en": "Country", "zh": "国家"},
    "development": {"en": "Development", "zh": "发展度"},
    "dominant_religion": {"en": "Dominant Religion", "zh": "优势宗教"},
    "location": {"en": "Location", "zh": "地点"},
    "locations": {"en": "Locations", "zh": "地点"},
    "location_rank": {"en": "Location Rank", "zh": "地点等级"},
    "owned": {"en": "Owned", "zh": "治下"},
    "population": {"en": "Population", "zh": "人口"},
    "pops": {"en": "Pops", "zh": "人口"},
    "proximity": {"en": "Proximity", "zh": "邻近度"},
    "religion": {"en": "Religion", "zh": "宗教"},
    "topography": {"en": "Topography", "zh": "地形"},
    "vegetation": {"en": "Vegetation", "zh": "植被"},
}

TOKEN_LABELS = {
    "location_rank:rural_settlement": {"en": "Rural Settlement", "zh": "乡村定居点"},
    "location_rank:town": {"en": "Town", "zh": "城镇"},
    "location_rank:city": {"en": "City", "zh": "城市"},
    "location_rank:megalopolis": {"en": "Megalopolis", "zh": "巨型都市"},
    "goods:iron": {"en": "Iron", "zh": "铁"},
    "goods:copper": {"en": "Copper", "zh": "铜"},
    "goods:tin": {"en": "Tin", "zh": "锡"},
    "goods:lead": {"en": "Lead", "zh": "铅"},
    "goods:silver": {"en": "Silver", "zh": "白银"},
    "goods:goods_gold": {"en": "Gold", "zh": "黄金"},
    "building_type:monastery": {"en": "Monastery", "zh": "修道院"},
    "building_type:cathedral": {"en": "Cathedral", "zh": "主教座堂"},
    "building_type:bridge_infrastructure": {"en": "Bridge Infrastructure", "zh": "桥梁基础设施"},
    "building_type:armory": {"en": "Armory", "zh": "军械库"},
    "mountains": {"en": "Mountains", "zh": "山地"},
    "plateau": {"en": "Plateau", "zh": "高原"},
    "hills": {"en": "Hills", "zh": "丘陵"},
    "forest": {"en": "Forest", "zh": "森林"},
    "woods": {"en": "Woods", "zh": "林地"},
    "owner.religion": {"en": "Owner's Religion", "zh": "拥有者宗教"},
}

BOOLEAN_TRIGGER_LABELS = {
    "is_capital": {
        False: {"en": "Is NOT a Capital", "zh": "不是首都"},
        True: {"en": "Is a Capital", "zh": "是首都"},
    },
}

SCOPE_TOKEN_LABELS = {
    "en": {
        r"\[COUNTRY\.GetName\]": "this Country",
        r"\[LOCATION\.GetName\]": "this Location",
    },
    "zh": {
        r"\[COUNTRY\.GetName\]": "该国家",
        r"\[LOCATION\.GetName\]": "该地点",
    },
}

TRIGGER_VALUE_REPLACEMENTS = (
    r"\$NAME(?:\|[A-Za-z0-9+=%._-]+)?\$",
    r"\$TOPOGRAPHY(?:\|[A-Za-z0-9+=%._-]+)?\$",
    r"\$VEGETATION(?:\|[A-Za-z0-9+=%._-]+)?\$",
    r"\$ENUM(?:\|[A-Za-z0-9+=%._-]+)?\$",
    r"\[TARGET_LOCATION_RANK\.GetName\]",
    r"\[TARGET_GOODS\.GetName\]",
    r"\[TARGET_RELIGION\.GetName\]",
    r"\[TARGET_BUILDING_TYPE\.GetName\]",
    r"\[TOPOGRAPHY\.GetName\]",
)


def prettify(key: str) -> str:
    return str(key).replace("_", " ").strip().title()


def scrub_markup(text: str, language: str | None = None) -> str:
    """Flatten common EU5 loc markup for a web-only plain text atlas."""
    text = str(text or "")

    def concept_replacement(match: re.Match[str]) -> str:
        concept = match.group(1)
        labels = CONCEPT_LABELS.get(concept)
        if labels and language in labels:
            return labels[language]
        return prettify(concept)

    text = re.sub(r"\[([^|\]]+)\|[A-Za-z]+\]", concept_replacement, text)
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


def load_index_payload(path: Path, root_key: str) -> dict[str, Any]:
    payload = load_json(path)
    records = payload.get(root_key, {})
    if not isinstance(records, dict):
        raise TypeError(f"{path}.{root_key} must be an object")
    return records


def wonder_image_source(image_id: str) -> Path | None:
    for extension in IMAGE_EXTENSIONS:
        candidate = WONDER_IMAGE_SOURCE_ROOT / f"{image_id}{extension}"
        if candidate.exists():
            return candidate
    return None


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
    return scrub_markup(value, language)


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


def token_label_pair(token: object) -> dict[str, str]:
    raw = str(token or "").strip()
    if raw in TOKEN_LABELS:
        return dict(TOKEN_LABELS[raw])
    if ":" in raw:
        raw = raw.split(":", 1)[1]
    return {"en": prettify(raw), "zh": prettify(raw)}


def indexed_text_pair(
    entry: dict[str, Any] | None,
    field: str,
    *,
    fallback: str,
) -> dict[str, str]:
    result: dict[str, str] = {}
    for language in LANGUAGES:
        language_entry = entry.get(language, {}) if isinstance(entry, dict) else {}
        value = language_entry.get(field) if isinstance(language_entry, dict) else None
        result[language] = scrub_markup(value or fallback, language)
    return result


def substitute_trigger_value(text: str, value: object, language: str) -> str:
    value_label = token_label_pair(value)[language]
    result = str(text or "")
    for pattern in TRIGGER_VALUE_REPLACEMENTS:
        result = re.sub(pattern, value_label, result)
    for pattern, replacement in SCOPE_TOKEN_LABELS[language].items():
        result = re.sub(pattern, replacement, result)
    return result


def trigger_lookup_candidates(key: str) -> list[str]:
    return [
        key,
        f"{key}_equal",
        f"location_{key}_equal",
        f"none_{key}_equal",
        f"{key}_this_equal",
        f"location_has_{key}",
    ]


def trigger_index_entry(trigger_index: dict[str, Any], key: str) -> dict[str, Any] | None:
    for candidate in trigger_lookup_candidates(key):
        entry = trigger_index.get(candidate)
        if isinstance(entry, dict):
            return entry
    return None


def scalar_value(value: object) -> object:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() == "yes":
        return True
    if text.lower() == "no":
        return False
    try:
        if any(marker in text for marker in (".", "e", "E")):
            return float(text)
        return int(text)
    except ValueError:
        return text


def annotate_modifier_row(
    row: dict[str, object],
    modifier_index: dict[str, Any],
) -> dict[str, object]:
    key = str(row["key"])
    entry = modifier_index.get(key, {})
    if not isinstance(entry, dict):
        entry = {}
    annotated = dict(row)
    annotated["label"] = indexed_text_pair(entry, "name", fallback=prettify(key))
    description = indexed_text_pair(entry, "description", fallback="")
    if any(description.values()):
        annotated["description"] = description
    for field in ("value_kind", "decimals", "category", "color"):
        if field in entry:
            annotated[field] = entry[field]
    return annotated


def rows_from_mapping(
    mapping: dict[str, object],
    *,
    modifier_index: dict[str, Any],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for key, value in mapping.items():
        rows.append(
            annotate_modifier_row(
                {"key": str(key), "value": scalar_value(value)},
                modifier_index,
            )
        )
    return rows


def rows_from_rewards(rewards: list[object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for raw in rewards:
        if not isinstance(raw, dict):
            continue
        reward_type = str(raw.get("type", "")).strip()
        if not reward_type:
            continue
        rows.append(
            {
                "key": reward_type,
                "label": {"en": prettify(reward_type), "zh": prettify(reward_type)},
                "value": scalar_value(raw.get("value")),
            }
        )
    return rows


SCRIPT_OPERATORS = {"?=", "=", ">=", "<=", ">", "<"}
SCRIPT_TOKEN_RE = re.compile(r"\{|\}|>=|<=|\?=|=|>|<|[^\s{}=<>]+")


def split_top_level_statements(script: str) -> list[str]:
    statements: list[str] = []
    cleaned = "\n".join(line.split("#", 1)[0] for line in str(script or "").splitlines())
    tokens = SCRIPT_TOKEN_RE.findall(cleaned)
    index = 0
    while index < len(tokens):
        if tokens[index] == "}":
            break
        if index + 1 >= len(tokens) or tokens[index + 1] not in SCRIPT_OPERATORS:
            statements.append(tokens[index])
            index += 1
            continue

        key = tokens[index]
        operator = tokens[index + 1]
        if index + 2 < len(tokens) and tokens[index + 2] == "{":
            index += 3
            depth = 1
            block_tokens: list[str] = []
            while index < len(tokens) and depth > 0:
                token = tokens[index]
                if token == "{":
                    depth += 1
                    block_tokens.append(token)
                elif token == "}":
                    depth -= 1
                    if depth > 0:
                        block_tokens.append(token)
                else:
                    block_tokens.append(token)
                index += 1
            statements.append(f"{key} {operator} {{ {' '.join(block_tokens)} }}")
            continue

        value = tokens[index + 2] if index + 2 < len(tokens) else ""
        statements.append(f"{key} {operator} {value}".strip())
        index += 3
    return statements


def inner_block(statement: str) -> str:
    start = statement.find("{")
    end = statement.rfind("}")
    if start < 0 or end < start:
        return ""
    return statement[start + 1:end].strip()


TRIGGER_STATEMENT_RE = re.compile(r"^([A-Za-z0-9_:.]+)\s*(\?=|=|>=|<=|>|<)\s*(.+)$")


def parse_trigger_statement(
    statement: str,
    *,
    logic: str,
    negated: bool,
    trigger_index: dict[str, Any],
    modifier_index: dict[str, Any],
) -> list[dict[str, object]]:
    normalized = " ".join(str(statement or "").split())
    if not normalized:
        return []
    normalized_upper = normalized.upper()
    if normalized_upper.startswith("OR = {"):
        rows: list[dict[str, object]] = []
        for child in split_top_level_statements(inner_block(statement)):
            rows.extend(
                parse_trigger_statement(
                    child,
                    logic="any",
                    negated=negated,
                    trigger_index=trigger_index,
                    modifier_index=modifier_index,
                )
        )
        return rows
    if normalized_upper.startswith("NOT = {"):
        rows = []
        for child in split_top_level_statements(inner_block(statement)):
            rows.extend(
                parse_trigger_statement(
                    child,
                    logic=logic,
                    negated=not negated,
                    trigger_index=trigger_index,
                    modifier_index=modifier_index,
                )
            )
        return rows

    match = TRIGGER_STATEMENT_RE.match(normalized)
    if not match:
        return [
            {
                "key": normalized,
                "label": {"en": normalized, "zh": normalized},
                "logic": logic,
                "negated": negated,
            }
        ]

    raw_key, operator, raw_value = match.groups()
    value = scalar_value(raw_value)
    if value is False:
        negated = not negated
    row: dict[str, object] = {
        "key": raw_key,
        "operator": operator,
        "value": value,
        "logic": logic,
        "negated": negated,
    }
    if raw_key.startswith("modifier:"):
        modifier_key = raw_key.split(":", 1)[1]
        row["key"] = modifier_key
        row["source"] = "modifier"
        return [annotate_modifier_row(row, modifier_index)]

    if isinstance(value, bool) and raw_key in BOOLEAN_TRIGGER_LABELS:
        row["label"] = dict(BOOLEAN_TRIGGER_LABELS[raw_key][not negated])
        row.pop("value", None)
        return [row]

    lookup_key = raw_key
    entry = trigger_index_entry(trigger_index, lookup_key)
    fallback = prettify(lookup_key)
    label: dict[str, str] = {}
    for language in LANGUAGES:
        language_entry = entry.get(language, {}) if isinstance(entry, dict) else {}
        variant = "not" if negated else "text"
        text = (
            language_entry.get(variant) or language_entry.get("text")
            if isinstance(language_entry, dict)
            else None
        )
        label[language] = scrub_markup(
            substitute_trigger_value(text or fallback, raw_value, language),
            language,
        )
    row["label"] = label
    if value in (True, False, "yes", "no"):
        row.pop("value", None)
    return [row]


def rows_from_trigger_script(
    script: str,
    *,
    trigger_index: dict[str, Any],
    modifier_index: dict[str, Any],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for statement in split_top_level_statements(script):
        if " ".join(statement.split()) == "always = yes":
            continue
        rows.extend(
            parse_trigger_statement(
                statement,
                logic="all",
                negated=False,
                trigger_index=trigger_index,
                modifier_index=modifier_index,
            )
        )
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


def effect_section_with_title(
    section_id: str,
    title: dict[str, str],
    rows: list[dict[str, object]],
    *,
    scope: str,
    value_label_en: str = "Value",
    value_label_zh: str = "\u6570\u503c",
    meta: dict[str, object] | None = None,
) -> dict[str, object] | None:
    normalized_meta = meta or {}
    if not rows and not normalized_meta:
        return None
    return {
        "id": section_id,
        "title": dict(title),
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


def append_ritual_plan_sections(
    effects: list[dict[str, object]],
    *,
    wonder: dict[str, Any],
    mechanics: dict[str, Any],
    loc_data: dict[str, dict[str, str]],
    modifier_index: dict[str, Any],
    style: int,
) -> None:
    ritual = ritual_plan_for_style(wonder, mechanics, style)
    title = localized_pair(loc_data, final_building_for_style(wonder, style))
    ceremony_modifier = ceremony_modifier_for_style(wonder, mechanics, style)
    ceremony_meta: dict[str, object] = {"style": style}
    if ceremony_modifier is not None:
        ceremony_meta["source"] = ceremony_modifier[0]

    for section in (
        effect_section_with_title(
            f"style_{style}_country_modifier",
            title,
            rows_from_mapping(ritual.get("country_modifier", {}), modifier_index=modifier_index),
            scope="country",
            meta=ceremony_meta,
        ),
        effect_section_with_title(
            f"style_{style}_rewards",
            title,
            rows_from_rewards(ritual.get("reward", [])),
            scope="reward",
            value_label_en="Amount",
            value_label_zh="\u6570\u91cf",
            meta={"style": style, "cost_type": ritual.get("cost_type")}
            if ritual.get("reward")
            else None,
        ),
    ):
        if section is not None:
            effects.append(section)

    timed = ritual.get("timed", {})
    if isinstance(timed, dict):
        for suffix, rows_key in (
            ("timed_burden", "burden_modifier"),
            ("timed_blessing", "blessing_modifier"),
        ):
            rows = rows_from_mapping(timed.get(rows_key, {}), modifier_index=modifier_index)
            section = effect_section_with_title(
                f"style_{style}_{suffix}",
                title,
                rows,
                scope="country",
                meta={"style": style, "years": timed.get("years", 1)} if rows else None,
            )
            if section is not None:
                effects.append(section)

    auxiliary = ritual.get("auxiliary_building", {})
    if isinstance(auxiliary, dict):
        auxiliary_meta = {
            key: value
            for key, value in {
                "style": style,
                "maintenance": auxiliary.get("maintenance"),
                "build_time": auxiliary.get("build_time"),
                "construction_demand": auxiliary.get("construction_demand"),
                "price": auxiliary.get("price"),
                "max_levels": auxiliary.get("max_levels"),
            }.items()
            if value not in (None, "", {})
        }
        section = effect_section_with_title(
            f"style_{style}_auxiliary_local",
            title,
            rows_from_mapping(auxiliary.get("local_modifier", {}), modifier_index=modifier_index),
            scope="local",
            meta=auxiliary_meta,
        )
        if section is not None:
            effects.append(section)


def build_record(
    wonder: dict[str, Any],
    *,
    base_wonders: dict[str, dict[str, Any]],
    mechanics: dict[str, Any],
    loc_data: dict[str, dict[str, str]],
    locations_index: dict[str, Any],
    reference_loc: dict[str, str],
    modifier_index: dict[str, Any],
    trigger_index: dict[str, Any],
) -> dict[str, object]:
    is_unique = bool(wonder.get("is_unique"))
    kind = "unique" if is_unique else "generic"
    location_key = ""
    location_name = dict(GENERIC_LOCATION_LABEL)
    location_info: dict[str, Any] | None = None
    if is_unique:
        location_key = str(wonder["location"])
        raw_location_info = locations_index.get(location_key)
        if not isinstance(raw_location_info, dict):
            raise KeyError(f"Unique wonder {wonder['key']} references unknown location {location_key}")
        location_info = raw_location_info
        location_name = reference_loc_pair(reference_loc, location_key)

    base_key = mechanic_key(wonder)
    base_wonder = base_wonders[base_key]
    name_key = wonder_name_key(wonder)
    final_building = next(iter(wonder["final_buildings"].values()))
    if "ritual" not in wonder:
        wonder = dict(wonder)
        wonder["ritual"] = ritual_plan_for_style(wonder, mechanics, 1)
    record_name_key = final_building if is_unique else name_key
    record_desc_key = f"{final_building}_desc" if is_unique else concept_desc_key(wonder)

    base_modifiers = mechanics.get("base_modifiers", {}).get(base_key, {})
    displayed_base_modifiers = scale_numeric_modifier_mapping(
        base_modifiers,
        wonder.get("base_effect_multiplier", 1),
    )
    final_local_modifiers = authored_final_building_local_modifiers(wonder, mechanics)
    image_id = str(wonder.get("image") or f"tv_wonder_{wonder['key']}")
    image_source = wonder_image_source(image_id)
    image_path = (
        (DIST_WONDER_IMAGE_ROOT / image_source.name).as_posix()
        if image_source is not None
        else ""
    )

    effects: list[dict[str, object]] = []
    for section in (
        effect_section(
            "final_local",
            "Inherited final local effects",
            "继承的最终建筑本地效果",
            rows_from_mapping(final_local_modifiers, modifier_index=modifier_index),
            scope="local",
        ),
        effect_section(
            "base_modifiers",
            "Per-level country effects",
            "每级国家效果",
            rows_from_mapping(displayed_base_modifiers, modifier_index=modifier_index),
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
        rows_from_mapping(ritual.get("country_modifier", {}), modifier_index=modifier_index),
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
            rows_from_mapping(timed.get("burden_modifier", {}), modifier_index=modifier_index),
            scope="country",
            meta={"years": timed.get("years", 1)} if timed.get("burden_modifier") else None,
        )
        if section is not None:
            effects.append(section)
        section = effect_section(
            "timed_blessing",
            "Timed blessing modifiers",
            "限时祝福修正",
            rows_from_mapping(timed.get("blessing_modifier", {}), modifier_index=modifier_index),
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
            rows_from_mapping(auxiliary.get("local_modifier", {}), modifier_index=modifier_index),
            scope="local",
            meta=auxiliary_meta,
        )
        if section is not None:
            effects.append(section)
        section = effect_section(
            "auxiliary_attributes",
            "Auxiliary attributes",
            "附属建筑属性",
            rows_from_mapping(auxiliary.get("attributes", {}), modifier_index=modifier_index),
            scope="attribute",
        )
        if section is not None:
            effects.append(section)

    if not is_unique:
        for style in ceremony_styles(wonder):
            if style == 1:
                continue
            append_ritual_plan_sections(
                effects,
                wonder=wonder,
                mechanics=mechanics,
                loc_data=loc_data,
                modifier_index=modifier_index,
                style=style,
            )

    return {
        "id": wonder["id"],
        "key": wonder["key"],
        "kind": kind,
        "kind_label": localized_label(KIND_LABELS, kind),
        "is_unique": is_unique,
        "has_map_marker": is_unique,
        "name": localized_pair(loc_data, record_name_key, fallback=loc_data["english"].get(name_key)),
        "description": localized_pair(
            loc_data,
            record_desc_key,
            fallback=loc_data["english"].get(f"{name_key}_desc", ""),
        ),
        "base_key": base_key,
        "base_name": localized_pair(loc_data, wonder_name_key(base_wonder)),
        "size": wonder["size"],
        "size_label": localized_label(SIZE_LABELS, wonder["size"]),
        "category": wonder["category"],
        "category_label": localized_label(CATEGORY_LABELS, wonder["category"]),
        "location_key": location_key,
        "location_name": location_name,
        "centroid": location_info["centroid"] if location_info is not None else None,
        "bbox": location_info["bbox"] if location_info is not None else None,
        "image": image_id,
        "image_path": image_path,
        "image_exists": image_source is not None,
        "construction_requirements": rows_from_trigger_script(
            site_trigger_script_for_key(mechanics, base_key),
            trigger_index=trigger_index,
            modifier_index=modifier_index,
        ),
        "effects": effects,
    }


def build_payload(
    locations_index_path: Path,
    reference_loc_path: Path,
    modifier_localization_index_path: Path,
    trigger_localization_index_path: Path,
) -> dict[str, object]:
    all_wonders, mechanics = load_all_wonder_mechanics_data(include_unique=True)
    loc_data = load_wonder_localization_data()
    locations_index = load_json(locations_index_path).get("locations", {})
    if not isinstance(locations_index, dict):
        raise TypeError(f"{locations_index_path}.locations must be an object")

    reference_loc_payload = load_json(reference_loc_path) if reference_loc_path.exists() else {}
    reference_loc = reference_loc_payload.get("strings", {})
    if not isinstance(reference_loc, dict):
        reference_loc = {}
    modifier_index = load_index_payload(modifier_localization_index_path, "modifiers")
    trigger_index = load_index_payload(trigger_localization_index_path, "triggers")

    base_wonders = {
        wonder["key"]: wonder
        for wonder in all_wonders
        if not wonder.get("is_unique")
    }
    generic_wonders = [
        wonder
        for wonder in all_wonders
        if not wonder.get("is_unique")
    ]
    unique_wonders = [
        wonder
        for wonder in all_wonders
        if wonder.get("is_unique")
    ]
    generic_wonders.sort(key=lambda item: int(item["id"]))
    unique_wonders.sort(key=lambda item: int(item["id"]))

    records = [
        build_record(
            wonder,
            base_wonders=base_wonders,
            mechanics=mechanics,
            loc_data=loc_data,
            locations_index=locations_index,
            reference_loc=reference_loc,
            modifier_index=modifier_index,
            trigger_index=trigger_index,
        )
        for wonder in [*generic_wonders, *unique_wonders]
    ]

    return {
        "version": 2,
        "wonders": records,
        "counts": {
            "generic_wonders": len(generic_wonders),
            "unique_wonders": len(unique_wonders),
            "total_wonders": len(records),
            "missing_locations": 0,
            "missing_images": sum(1 for record in records if not record.get("image_exists")),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locations-index", type=Path, default=DEFAULT_LOCATIONS_INDEX)
    parser.add_argument("--reference-loc", type=Path, default=DEFAULT_REFERENCE_LOC)
    parser.add_argument(
        "--modifier-localization-index",
        type=Path,
        default=DEFAULT_MODIFIER_LOCALIZATION_INDEX,
    )
    parser.add_argument(
        "--trigger-localization-index",
        type=Path,
        default=DEFAULT_TRIGGER_LOCALIZATION_INDEX,
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    payload = build_payload(
        args.locations_index,
        args.reference_loc,
        args.modifier_localization_index,
        args.trigger_localization_index,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {args.out.relative_to(REPO_ROOT)} "
        f"({payload['counts']['generic_wonders']} generic, "
        f"{payload['counts']['unique_wonders']} unique wonders)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
