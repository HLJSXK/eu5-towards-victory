import ast
import re
import sys
from pathlib import Path
from typing import Any

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from scripts.wonder_mechanics_lib import (
        ceremony_styles,
        final_building_for_style,
        level_static_modifier_loc,
        load_all_wonder_mechanics_data,
        ritual_auxiliary_building,
        ritual_auxiliary_display_modifier_name,
        ritual_blessing_modifier_name,
        ritual_plan_for_style,
        wonder_auto_base_modifier_name,
        unique_ceremony_modifier_name,
        wonder_static_display_modifier_name,
        wonder_static_local_display_modifier_name,
    )
except ModuleNotFoundError:
    from wonder_mechanics_lib import (
        ceremony_styles,
        final_building_for_style,
        level_static_modifier_loc,
        load_all_wonder_mechanics_data,
        ritual_auxiliary_building,
        ritual_auxiliary_display_modifier_name,
        ritual_blessing_modifier_name,
        ritual_plan_for_style,
        wonder_auto_base_modifier_name,
        unique_ceremony_modifier_name,
        wonder_static_display_modifier_name,
        wonder_static_local_display_modifier_name,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
WONDER_LOCALIZATION_FILE = REPO_ROOT / "data" / "wonder_localization.yaml"
ENGINEERING_DEPARTMENT_EVENTS_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_engineering_department_events.txt"
LANGUAGES = ("english", "simp_chinese")
WONDER_NAME_PREFIX = "tv_wonder_"
CONCEPT_NAME_PREFIX = "game_concept_"
WONDER_DISPLAY_CONCEPT_PREFIX = "tv_wonder_display_"
WONDER_IMAGE_CONCEPT_PREFIX = "tv_wonder_display_image_"
WONDER_FULL_IMAGE_CONCEPT_PREFIX = "tv_wonder_display_full_image_"
WONDER_RITUAL_DISPLAY_CONCEPT_PREFIX = "tv_wonder_display_"
ENGINEERING_PREVIEW_LOCATION_TEXT_PREFIX = "TV_ENGINEERING_WONDER_PREVIEW_LOCATION_TEXT_"

LOCALIZATION_LINE_RE = re.compile(r'^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.-]+):(?P<version>0)?\s+(?P<value>"(?:[^"\\]|\\.)*")\s*$')
LOCALIZATION_LINE_START_RE = re.compile(r'^\s*(?P<key>[A-Za-z0-9_.-]+):(?P<version>0)?\s+(?P<value_start>".*)$')
LOCALIZATION_HEADER_RE = re.compile(r"^l_[A-Za-z_]+:\s*$")
ENGINEERING_DEPARTMENT_500_ID_RE = re.compile(r"var:tv_wonder_locked \?= (?P<id>\d+)")
ENGINEERING_DEPARTMENT_500_DESC_RE = re.compile(r"desc = tv_engineering_department\.500\.d_(?P<suffix>[A-Za-z0-9_]+?)(?:_(?P<style>\d+))?$")


class StrictWonderLocalizationLoader(yaml.SafeLoader):
    pass


def _construct_yaml_mapping_no_duplicates(
    loader: StrictWonderLocalizationLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict:
    mapping: dict = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            source_name = getattr(loader, "source_name", "<yaml>")
            raise ValueError(f"Duplicate key {key!r} in {source_name}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictWonderLocalizationLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_yaml_mapping_no_duplicates,
)


def normalize_editor_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ").strip()


def escape_localization_value(value: str) -> str:
    normalized = normalize_editor_text(value)
    return normalized.replace("\\", "\\\\").replace('"', '\\"')


def parse_localization_value(raw_value: str) -> str:
    try:
        return ast.literal_eval(raw_value)
    except Exception as exc:
        raise ValueError(f"Invalid localization string literal: {raw_value}") from exc


def is_complete_localization_value(raw_value: str) -> bool:
    if not raw_value.startswith('"'):
        return False
    escaped = False
    closing_index: int | None = None
    for index, character in enumerate(raw_value[1:], start=1):
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == '"':
            closing_index = index
    return closing_index is not None and not raw_value[closing_index + 1 :].strip()


def parse_complete_localization_value(raw_value: str) -> str | None:
    if not is_complete_localization_value(raw_value):
        return None
    value = parse_localization_value(raw_value.replace("\n", "\\n"))
    if not isinstance(value, str):
        raise ValueError(f"Localization value must be a string literal: {raw_value}")
    return value


def wonder_name_key(wonder: dict[str, Any]) -> str:
    return f"{WONDER_NAME_PREFIX}{wonder['key']}"


def concept_name_key(wonder: dict[str, Any]) -> str:
    return f"{CONCEPT_NAME_PREFIX}{wonder['concept']}"


def _wonder_concept_pairs() -> list[tuple[str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    return [(wonder_name_key(wonder), concept_name_key(wonder)) for wonder in wonders]


def image_route_concept_key(wonder: dict[str, Any]) -> str:
    return f"{CONCEPT_NAME_PREFIX}{WONDER_IMAGE_CONCEPT_PREFIX}{wonder['id']}"


def image_route_concept_desc_key(wonder: dict[str, Any]) -> str:
    return f"{image_route_concept_key(wonder)}_desc"


def full_image_route_concept_key(wonder: dict[str, Any]) -> str:
    return f"{CONCEPT_NAME_PREFIX}{WONDER_FULL_IMAGE_CONCEPT_PREFIX}{wonder['id']}"


def full_image_route_concept_desc_key(wonder: dict[str, Any]) -> str:
    return f"{full_image_route_concept_key(wonder)}_desc"


def display_route_concept_key(wonder: dict[str, Any]) -> str:
    return f"{CONCEPT_NAME_PREFIX}{WONDER_DISPLAY_CONCEPT_PREFIX}{wonder['id']}"


def display_route_concept_desc_key(wonder: dict[str, Any]) -> str:
    return f"{display_route_concept_key(wonder)}_desc"


def ritual_display_route_concept_key(wonder: dict[str, Any], style: int) -> str:
    return f"{CONCEPT_NAME_PREFIX}{WONDER_RITUAL_DISPLAY_CONCEPT_PREFIX}{wonder['id']}_ritual_{style}"


def ritual_display_route_concept_desc_key(wonder: dict[str, Any], style: int) -> str:
    return f"{ritual_display_route_concept_key(wonder, style)}_desc"


def ceremony_name_key(wonder: dict[str, Any], style: int) -> str:
    building = final_building_for_style(wonder, style)
    return f"TV_ENGINEERING_CEREMONY_{building.removeprefix('tv_wonder_').upper()}_BUTTON"


def concept_desc_key(wonder: dict[str, Any]) -> str:
    return f"{concept_name_key(wonder)}_desc"


def _wonder_display_route_pairs() -> list[tuple[str, str, str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    return [
        (
            concept_name_key(wonder),
            concept_desc_key(wonder),
            display_route_concept_key(wonder),
            display_route_concept_desc_key(wonder),
        )
        for wonder in wonders
    ]


def _wonder_image_route_pairs() -> list[tuple[str, str, str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    return [
        (
            concept_name_key(wonder),
            concept_desc_key(wonder),
            image_route_concept_key(wonder),
            image_route_concept_desc_key(wonder),
        )
        for wonder in wonders
    ]


def _wonder_full_image_route_pairs() -> list[tuple[str, str, str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    return [
        (
            concept_name_key(wonder),
            concept_desc_key(wonder),
            full_image_route_concept_key(wonder),
            full_image_route_concept_desc_key(wonder),
        )
        for wonder in wonders
    ]


def _wonder_ritual_display_route_pairs() -> list[tuple[str, str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    return [
        (
            ceremony_name_key(wonder, style),
            ritual_display_route_concept_key(wonder, style),
            ritual_display_route_concept_desc_key(wonder, style),
        )
        for wonder in wonders
        for style in ceremony_styles(wonder)
    ]


def _engineering_gui_text_route_pairs() -> list[tuple[str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    pairs: list[tuple[str, str]] = []
    for wonder in wonders:
        key = str(wonder["key"]).upper()
        wonder_id = int(wonder["id"])
        pairs.extend(
            [
                (f"TV_ENGINEERING_PROPOSAL_{key}_TEXT", f"TV_ENGINEERING_PROPOSAL_TEXT_{wonder_id}"),
                (f"TV_ENGINEERING_PROPOSAL_RESUME_{key}_TEXT", f"TV_ENGINEERING_PROPOSAL_RESUME_TEXT_{wonder_id}"),
                (f"TV_ENGINEERING_PROPOSAL_EXPAND_{key}_TEXT", f"TV_ENGINEERING_PROPOSAL_EXPAND_TEXT_{wonder_id}"),
                (f"TV_ENGINEERING_LOCKED_{key}_TEXT", f"TV_ENGINEERING_LOCKED_TEXT_{wonder_id}"),
            ]
        )
    return pairs


def preview_location_text_key(wonder: dict[str, Any]) -> str:
    return f"{ENGINEERING_PREVIEW_LOCATION_TEXT_PREFIX}{int(wonder['id'])}"


def _engineering_preview_location_text_values() -> list[tuple[str, str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    values: list[tuple[str, str, str]] = []
    for wonder in wonders:
        key = preview_location_text_key(wonder)
        if wonder.get("is_unique"):
            location = wonder.get("location")
            if not location:
                raise KeyError(f"Unique wonder {wonder['key']!r} is missing its fixed location")
            english = (
                "@location! This is a unique [tv_wonder_construction|E] that can be built at "
                f"[ShowLocationName('{location}')], its fixed [location|E]"
            )
            simp_chinese = (
                "@location! 这是一个[tv_wonder_construction|E]独特奇观，可以建造在"
                f"[ShowLocationName('{location}')]这一[location|E]"
            )
        else:
            english = (
                "@location! This is a generic [tv_wonder_construction|E] that can be built "
                "across multiple eligible [location|E] sites"
            )
            simp_chinese = (
                "@location! 这是一个[tv_wonder_construction|E]通用奇观，可以建造在多个符合条件的[location|E]"
            )
        values.append((key, english, simp_chinese))
    return values


def _auto_base_modifier_values() -> list[tuple[str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    values: list[tuple[str, str]] = []
    for wonder in wonders:
        for level in range(1, 7):
            values.append(
                (
                    f"AUTO_MODIFIER_NAME_{wonder_auto_base_modifier_name(wonder, level)}",
                    level_static_modifier_loc(wonder["concept"], level),
                )
            )
    return values


def _static_base_modifier_values() -> list[tuple[str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    values: list[tuple[str, str]] = []
    for wonder in wonders:
        for level in range(1, 7):
            value = level_static_modifier_loc(wonder["concept"], level)
            values.append((f"STATIC_MODIFIER_NAME_{wonder_static_display_modifier_name(wonder, level)}", value))
            values.append((f"STATIC_MODIFIER_NAME_{wonder_static_local_display_modifier_name(wonder, level)}", value))
    return values


def _ritual_static_modifier_keys() -> list[str]:
    wonders, mechanics = load_all_wonder_mechanics_data()
    keys: list[str] = []
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            if wonder.get("is_unique"):
                if ritual_plan.get("country_modifier", {}):
                    keys.append(f"STATIC_MODIFIER_NAME_{unique_ceremony_modifier_name(wonder)}")
                continue
            if ritual_plan["mode"] != "timed":
                continue
            if ritual_plan.get("timed", {}).get("blessing_modifier", {}):
                keys.append(f"STATIC_MODIFIER_NAME_{ritual_blessing_modifier_name(wonder)}")
    return keys


def _auxiliary_display_modifier_pairs() -> list[tuple[str, str]]:
    wonders, mechanics = load_all_wonder_mechanics_data()
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for wonder in wonders:
        for style in ceremony_styles(wonder):
            ritual_plan = ritual_plan_for_style(wonder, mechanics, style)
            if ritual_plan["mode"] != "auxiliary_building":
                continue
            modifier_loc_key = f"STATIC_MODIFIER_NAME_{ritual_auxiliary_display_modifier_name(wonder)}"
            if modifier_loc_key in seen:
                continue
            seen.add(modifier_loc_key)
            pairs.append((ritual_auxiliary_building(wonder), modifier_loc_key))
    return pairs


def expand_wonder_localization_data(localization: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    expanded = {language: dict(values) for language, values in localization.items()}
    for wonder_name, concept_name in _wonder_concept_pairs():
        for language in LANGUAGES:
            language_values = expanded[language]
            if wonder_name not in language_values:
                raise KeyError(f"Missing wonder localization key {wonder_name!r} in {WONDER_LOCALIZATION_FILE} ({language})")
            language_values[concept_name] = language_values[wonder_name]
    for concept_name, concept_desc, route_concept, route_concept_desc in _wonder_image_route_pairs():
        for language in LANGUAGES:
            language_values = expanded[language]
            if concept_name not in language_values:
                raise KeyError(f"Missing wonder concept localization key {concept_name!r} in {WONDER_LOCALIZATION_FILE} ({language})")
            if concept_desc not in language_values:
                raise KeyError(f"Missing wonder concept localization key {concept_desc!r} in {WONDER_LOCALIZATION_FILE} ({language})")
            language_values[route_concept] = language_values[concept_name]
            language_values[route_concept_desc] = language_values[concept_desc]
    for concept_name, concept_desc, route_concept, route_concept_desc in _wonder_full_image_route_pairs():
        for language in LANGUAGES:
            language_values = expanded[language]
            if concept_name not in language_values:
                raise KeyError(f"Missing wonder concept localization key {concept_name!r} in {WONDER_LOCALIZATION_FILE} ({language})")
            if concept_desc not in language_values:
                raise KeyError(f"Missing wonder concept localization key {concept_desc!r} in {WONDER_LOCALIZATION_FILE} ({language})")
            language_values[route_concept] = language_values[concept_name]
            language_values[route_concept_desc] = language_values[concept_desc]
    for concept_name, concept_desc, route_concept, route_concept_desc in _wonder_display_route_pairs():
        for language in LANGUAGES:
            language_values = expanded[language]
            if concept_name not in language_values:
                raise KeyError(f"Missing wonder concept localization key {concept_name!r} in {WONDER_LOCALIZATION_FILE} ({language})")
            if concept_desc not in language_values:
                raise KeyError(f"Missing wonder concept localization key {concept_desc!r} in {WONDER_LOCALIZATION_FILE} ({language})")
            language_values[route_concept] = language_values[concept_name]
            language_values[route_concept_desc] = language_values[concept_desc]
    for source_key, route_key in _engineering_gui_text_route_pairs():
        for language in LANGUAGES:
            language_values = expanded[language]
            if source_key not in language_values:
                raise KeyError(
                    f"Missing engineering GUI localization key {source_key!r} in "
                    f"{WONDER_LOCALIZATION_FILE} ({language})"
                )
            language_values[route_key] = language_values[source_key]
    for route_key, english, simp_chinese in _engineering_preview_location_text_values():
        expanded["english"][route_key] = english
        expanded["simp_chinese"][route_key] = simp_chinese
    for source_key, route_concept, route_concept_desc in _wonder_ritual_display_route_pairs():
        for language in LANGUAGES:
            language_values = expanded[language]
            if source_key not in language_values:
                raise KeyError(
                    f"Missing wonder ritual localization key {source_key!r} in "
                    f"{WONDER_LOCALIZATION_FILE} ({language})"
                )
            language_values[route_concept] = language_values[source_key]
            language_values[route_concept_desc] = language_values[source_key]
    for auto_modifier_loc_key, auto_value in _auto_base_modifier_values():
        for language in LANGUAGES:
            expanded[language][auto_modifier_loc_key] = auto_value
    for static_modifier_loc_key, static_value in _static_base_modifier_values():
        for language in LANGUAGES:
            expanded[language][static_modifier_loc_key] = static_value
    for static_modifier_loc_key in _ritual_static_modifier_keys():
        for language in LANGUAGES:
            language_values = expanded[language]
            if static_modifier_loc_key not in language_values:
                raise KeyError(
                    f"Missing wonder ritual static modifier localization key {static_modifier_loc_key!r} in "
                    f"{WONDER_LOCALIZATION_FILE} ({language})"
                )
    for building_name, modifier_loc_key in _auxiliary_display_modifier_pairs():
        for language in LANGUAGES:
            language_values = expanded[language]
            if building_name not in language_values:
                raise KeyError(
                    f"Missing auxiliary building localization key {building_name!r} in "
                    f"{WONDER_LOCALIZATION_FILE} ({language})"
                )
            language_values[modifier_loc_key] = language_values[building_name]
    return expanded


def collapse_wonder_localization_data(localization: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    collapsed = {language: dict(values) for language, values in localization.items()}
    for _, concept_name in _wonder_concept_pairs():
        for language in LANGUAGES:
            collapsed[language].pop(concept_name, None)
    for _, _, route_concept, route_concept_desc in _wonder_image_route_pairs():
        for language in LANGUAGES:
            collapsed[language].pop(route_concept, None)
            collapsed[language].pop(route_concept_desc, None)
    for _, _, route_concept, route_concept_desc in _wonder_full_image_route_pairs():
        for language in LANGUAGES:
            collapsed[language].pop(route_concept, None)
            collapsed[language].pop(route_concept_desc, None)
    for _, _, route_concept, route_concept_desc in _wonder_display_route_pairs():
        for language in LANGUAGES:
            collapsed[language].pop(route_concept, None)
            collapsed[language].pop(route_concept_desc, None)
    for _, route_key in _engineering_gui_text_route_pairs():
        for language in LANGUAGES:
            collapsed[language].pop(route_key, None)
    for route_key, _, _ in _engineering_preview_location_text_values():
        for language in LANGUAGES:
            collapsed[language].pop(route_key, None)
    for _, route_concept, route_concept_desc in _wonder_ritual_display_route_pairs():
        for language in LANGUAGES:
            collapsed[language].pop(route_concept, None)
            collapsed[language].pop(route_concept_desc, None)
    for auto_modifier_loc_key, _ in _auto_base_modifier_values():
        for language in LANGUAGES:
            collapsed[language].pop(auto_modifier_loc_key, None)
    for static_modifier_loc_key, _ in _static_base_modifier_values():
        for language in LANGUAGES:
            collapsed[language].pop(static_modifier_loc_key, None)
    for _, modifier_loc_key in _auxiliary_display_modifier_pairs():
        for language in LANGUAGES:
            collapsed[language].pop(modifier_loc_key, None)
    return collapsed


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing YAML source file: {path}")
    loader = StrictWonderLocalizationLoader(path.read_text(encoding="utf-8"))
    loader.source_name = str(path)
    try:
        data = loader.get_single_data()
    finally:
        loader.dispose()
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a top-level mapping")
    return data


def load_localization_map(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Missing localization file: {path}")
    values: dict[str, str] = {}
    pending_key: str | None = None
    pending_value_lines: list[str] = []
    pending_start_line = 0
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if pending_key is not None:
            pending_value_lines.append(raw_line)
            parsed_value = parse_complete_localization_value("\n".join(pending_value_lines))
            if parsed_value is None:
                continue
            values[pending_key] = parsed_value
            pending_key = None
            pending_value_lines = []
            pending_start_line = 0
            continue

        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or LOCALIZATION_HEADER_RE.match(stripped):
            continue
        match = LOCALIZATION_LINE_RE.match(raw_line)
        if match is not None:
            key = match.group("key")
            if key in values:
                raise ValueError(f"Duplicate localization key {key!r} in {path}:{line_number}")
            values[key] = parse_localization_value(match.group("value"))
            continue

        start_match = LOCALIZATION_LINE_START_RE.match(raw_line)
        if start_match is None:
            raise ValueError(f"Unparseable localization line in {path}:{line_number}: {raw_line}")
        key = start_match.group("key")
        if key in values:
            raise ValueError(f"Duplicate localization key {key!r} in {path}:{line_number}")
        pending_key = key
        pending_value_lines = [start_match.group("value_start")]
        pending_start_line = line_number
    if pending_key is not None:
        raise ValueError(f"Unterminated localization string for key {pending_key!r} in {path}:{pending_start_line}")
    return values


def write_localization_updates(path: Path, updates: dict[str, str], *, append_missing: bool = False) -> bool:
    if not updates:
        return False
    if not path.exists():
        raise FileNotFoundError(f"Missing localization file: {path}")

    lines = path.read_text(encoding="utf-8-sig").splitlines()

    changed = False
    seen_keys: set[str] = set()
    rewritten: list[str] = []
    for line_number, raw_line in enumerate(lines, start=1):
        match = LOCALIZATION_LINE_RE.match(raw_line)
        if match is None:
            rewritten.append(raw_line.rstrip("\r"))
            continue

        key = match.group("key")
        if key not in updates:
            rewritten.append(raw_line.rstrip("\r"))
            continue

        seen_keys.add(key)
        new_value = escape_localization_value(updates[key])
        prefix = match.group("indent")
        version = match.group("version") or ""
        rewritten.append(f'{prefix}{key}:{version} "{new_value}"')
        if parse_localization_value(match.group("value")) != updates[key]:
            changed = True

    missing_keys = [key for key in updates if key not in seen_keys]
    if missing_keys:
        if append_missing:
            raise RuntimeError("append_missing compatibility mode has been removed")
        raise KeyError(f"Missing localization keys in {path}: {', '.join(missing_keys)}")

    if not changed:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rewritten).rstrip() + "\n", encoding="utf-8-sig")
    return True


def load_wonder_localization_data() -> dict[str, dict[str, str]]:
    raw = load_yaml(WONDER_LOCALIZATION_FILE)
    if "wonder_localization" not in raw:
        raise KeyError(f"Missing wonder_localization root in {WONDER_LOCALIZATION_FILE}")
    localization = raw["wonder_localization"]
    if not isinstance(localization, dict):
        raise TypeError(f"{WONDER_LOCALIZATION_FILE}.wonder_localization must be a mapping")
    extra_languages = sorted(set(localization) - set(LANGUAGES))
    if extra_languages:
        raise ValueError(f"Unexpected language sections in {WONDER_LOCALIZATION_FILE}: {', '.join(extra_languages)}")
    result: dict[str, dict[str, str]] = {}
    for language in LANGUAGES:
        if language not in localization:
            raise KeyError(f"Missing language section {language} in {WONDER_LOCALIZATION_FILE}")
        language_values = localization[language]
        if not isinstance(language_values, dict):
            raise TypeError(f"{WONDER_LOCALIZATION_FILE}.wonder_localization.{language} must be a mapping")
        normalized: dict[str, str] = {}
        for key, value in language_values.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f"Invalid localization key in {WONDER_LOCALIZATION_FILE}.{language}: {key!r}")
            if not isinstance(value, str):
                raise TypeError(
                    f"Localization value for {language}.{key} in {WONDER_LOCALIZATION_FILE} must be a string, "
                    f"got {type(value).__name__}"
                )
            normalized[key] = value
        result[language] = normalized
    return expand_wonder_localization_data(result)


def save_wonder_localization_data(localization: dict[str, dict[str, str]]) -> None:
    canonical = collapse_wonder_localization_data(localization)
    payload = {
        "wonder_localization": {
            language: dict(canonical[language])
            for language in LANGUAGES
        },
    }
    WONDER_LOCALIZATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    WONDER_LOCALIZATION_FILE.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )


def apply_localization_values(text: str, localization: dict[str, str]) -> str:
    raise RuntimeError("Localization overlay mode has been removed; write canonical values to data/wonder_localization.yaml")


def load_engineering_department_suffix_map() -> dict[int, str]:
    if not ENGINEERING_DEPARTMENT_EVENTS_FILE.exists():
        return {}

    suffixes: dict[int, str] = {}
    current_id: int | None = None
    for raw_line in ENGINEERING_DEPARTMENT_EVENTS_FILE.read_text(encoding="utf-8-sig").splitlines():
        id_match = ENGINEERING_DEPARTMENT_500_ID_RE.search(raw_line)
        if id_match is not None:
            current_id = int(id_match.group("id"))
            continue

        if current_id is None:
            continue

        desc_match = ENGINEERING_DEPARTMENT_500_DESC_RE.search(raw_line)
        if desc_match is None:
            continue

        suffixes.setdefault(current_id, desc_match.group("suffix"))

    return suffixes
