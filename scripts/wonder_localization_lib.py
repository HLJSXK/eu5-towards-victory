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
        load_all_wonder_mechanics_data,
        ritual_auxiliary_building,
        ritual_auxiliary_display_modifier_name,
        ritual_plan_for_style,
    )
except ModuleNotFoundError:
    from wonder_mechanics_lib import (
        ceremony_styles,
        load_all_wonder_mechanics_data,
        ritual_auxiliary_building,
        ritual_auxiliary_display_modifier_name,
        ritual_plan_for_style,
    )

REPO_ROOT = Path(__file__).resolve().parents[1]
WONDER_LOCALIZATION_FILE = REPO_ROOT / "data" / "wonder_localization.yaml"
ENGINEERING_DEPARTMENT_EVENTS_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_engineering_department_events.txt"
LANGUAGES = ("english", "simp_chinese")
WONDER_NAME_PREFIX = "tv_wonder_"
CONCEPT_NAME_PREFIX = "game_concept_"

LOCALIZATION_LINE_RE = re.compile(r'^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.-]+):(?P<version>0)?\s+(?P<value>"(?:[^"\\]|\\.)*")\s*$')
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


def wonder_name_key(wonder: dict[str, Any]) -> str:
    return f"{WONDER_NAME_PREFIX}{wonder['key']}"


def concept_name_key(wonder: dict[str, Any]) -> str:
    return f"{CONCEPT_NAME_PREFIX}{wonder['concept']}"


def _wonder_concept_pairs() -> list[tuple[str, str]]:
    wonders, _ = load_all_wonder_mechanics_data()
    return [(wonder_name_key(wonder), concept_name_key(wonder)) for wonder in wonders]


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
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or LOCALIZATION_HEADER_RE.match(stripped):
            continue
        match = LOCALIZATION_LINE_RE.match(raw_line)
        if match is None:
            raise ValueError(f"Unparseable localization line in {path}:{line_number}: {raw_line}")
        key = match.group("key")
        if key in values:
            raise ValueError(f"Duplicate localization key {key!r} in {path}:{line_number}")
        values[key] = parse_localization_value(match.group("value"))
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
