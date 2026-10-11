"""Wonder source paths, input groups and ritual source loading."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from scripts_engineering_department.wonder_localization_lib import (
    REPO_ROOT,
    WONDER_LOCALIZATION_FILE,
)
from scripts_engineering_department.wonder_mechanics.io import (
    UNIQUE_WONDERS_FILE,
    WONDERS_FILE,
    WONDER_BASE_MODIFIERS_FILE,
    WONDER_FINAL_BUILDINGS_FILE,
    WONDER_GENERIC_RITUALS_FILE,
    WONDER_MECHANICS_DATA_REL,
    WONDER_SITE_RULES_FILE,
)

from ..platform import repo_relative_path
from ..wonder_generation import WONDER_SOURCE_GROUPS


WONDER_LOCALIZATION_DATA_REL = "data/wonder_localization.yaml"
GENERATED_LOC_DATA_REL = f"data/wonders.yaml + {WONDER_MECHANICS_DATA_REL} + data/unique_wonders.yaml + data/wonder_localization.yaml"
UNIQUE_RITUAL_DESIGNS_REL = "data/unique_wonder_ritual_designs.yaml"
UNIQUE_RITUAL_DESIGNS_ZH_REL = "data/unique_wonder_ritual_designs_zh.yaml"
UNIQUE_RITUAL_PROMPTS_REL = "data/unique_wonder_ritual_prompts.yaml"
UNIQUE_RITUAL_DESIGNS_FILE = REPO_ROOT / UNIQUE_RITUAL_DESIGNS_REL
UNIQUE_RITUAL_DESIGNS_ZH_FILE = REPO_ROOT / UNIQUE_RITUAL_DESIGNS_ZH_REL
UNIQUE_RITUAL_PROMPTS_FILE = REPO_ROOT / UNIQUE_RITUAL_PROMPTS_REL


def wonder_source_paths() -> tuple[Path, ...]:
    """Return source paths from the current module constants.

    Tests and local editor instances can redirect the repository data files;
    deriving this tuple at use time keeps the resource contract aligned with
    those redirected paths.
    """
    return (
        WONDER_LOCALIZATION_FILE,
        WONDER_FINAL_BUILDINGS_FILE,
        WONDER_GENERIC_RITUALS_FILE,
        WONDER_BASE_MODIFIERS_FILE,
        WONDER_SITE_RULES_FILE,
        WONDERS_FILE,
        UNIQUE_WONDERS_FILE,
        UNIQUE_RITUAL_PROMPTS_FILE,
    )


def wonder_source_rels() -> tuple[str, ...]:
    return tuple(
        repo_relative_path(path, REPO_ROOT)
        for path in wonder_source_paths()
    )


def wonder_input_groups(files: dict[Path, bytes]) -> set[str]:
    return {
        WONDER_SOURCE_GROUPS[repo_relative_path(path, REPO_ROOT)]
        for path in files
        if repo_relative_path(path, REPO_ROOT) in WONDER_SOURCE_GROUPS
    }


WONDER_EDITOR_CATALOG_FILE = REPO_ROOT / "data" / "wonder_editor_catalog.yaml"
MODIFIER_LOCALIZATION_INDEX_FILE = REPO_ROOT / "data" / "index" / "modifier_localization.json"
GENERATED_WONDER_IMAGES_DIR = REPO_ROOT / "assets" / "generated_wonders"
WONDER_IMAGE_URL_PREFIX = "/wonder-images"
GENERATED_LOC_FILES = {
    "english": REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "english" / "tv_engineering_department_wonder_mechanics_l_english.yml",
    "simp_chinese": REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_wonder_mechanics_l_simp_chinese.yml",
}
MANUAL_CONCEPT_FILES = {
    "english": REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "english" / "tv_engineering_department_game_concepts_l_english.yml",
    "simp_chinese": REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_game_concepts_l_simp_chinese.yml",
}
MANUAL_ENGINEERING_FILES = {
    "english": REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "english" / "tv_engineering_department_l_english.yml",
    "simp_chinese": REPO_ROOT / "src_engineering_department" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_l_simp_chinese.yml",
}
CONCEPT_FILE = REPO_ROOT / "src_engineering_department" / "main_menu" / "common" / "game_concepts" / "tv_engineering_department_wonder_mechanics_concepts.txt"
CONCEPT_SCRIPT_REL = "scripts_engineering_department/main_menu/common/game_concepts/gen_tv_engineering_department_wonder_mechanics_concepts.py"
REFERENCE_LOC_DIR_BY_EDITOR_LANGUAGE = {
    "english": REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "localization" / "english",
    "simp_chinese": REPO_ROOT / "reference_game_files" / "game" / "main_menu" / "localization" / "simp_chinese",
}


def load_unique_ritual_designs_data(path: Path = UNIQUE_RITUAL_DESIGNS_FILE) -> dict[str, Any]:
    if not path.exists():
        return {"metadata": {}, "unique_wonders": []}
    payload = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a mapping")
    unique_wonders = payload.get("unique_wonders", [])
    if not isinstance(unique_wonders, list):
        raise TypeError(f"{path}.unique_wonders must be a list")
    return payload


def load_unique_ritual_design_translations_data(path: Path = UNIQUE_RITUAL_DESIGNS_ZH_FILE) -> dict[str, Any]:
    if not path.exists():
        return {"metadata": {}, "unique_wonders": []}
    payload = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a mapping")
    unique_wonders = payload.get("unique_wonders", [])
    if not isinstance(unique_wonders, list):
        raise TypeError(f"{path}.unique_wonders must be a list")
    return payload


def unique_ritual_design_translation_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for entry in data.get("unique_wonders", []):
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("key", "")).strip()
        ritual_design_zh = entry.get("ritual_design_zh")
        if key and isinstance(ritual_design_zh, dict):
            index[key] = entry
    return index


def default_unique_ritual_prompts_data() -> dict[str, Any]:
    return {
        "metadata": {
            "purpose": "AI prompts for implementing unique wonder rituals from the design-only ritual source.",
            "source_data": UNIQUE_RITUAL_DESIGNS_REL,
            "generated_game_code": False,
            "design_policy": (
                "This file stores user-authored AI prompts only. It is not consumed by game-code "
                "generators until a later implementation pass defines an explicit schema."
            ),
        },
        "unique_wonders": [],
    }


def load_unique_ritual_prompts_data(path: Path = UNIQUE_RITUAL_PROMPTS_FILE) -> dict[str, Any]:
    if not path.exists():
        return default_unique_ritual_prompts_data()
    payload = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a mapping")
    payload.setdefault("metadata", default_unique_ritual_prompts_data()["metadata"])
    unique_wonders = payload.setdefault("unique_wonders", [])
    if not isinstance(unique_wonders, list):
        raise TypeError(f"{path}.unique_wonders must be a list")
    return payload


def unique_ritual_prompt_index(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for entry in data.get("unique_wonders", []):
        if not isinstance(entry, dict):
            continue
        key = str(entry.get("key", "")).strip()
        if key:
            index[key] = entry
    return index


def validate_unique_ritual_designs(wonders: list[dict[str, Any]], designs_data: dict[str, Any]) -> None:
    wonders_by_id = {int(wonder["id"]): wonder for wonder in wonders}
    seen_ids: set[int] = set()
    seen_keys: set[str] = set()
    for index, entry in enumerate(designs_data.get("unique_wonders", [])):
        source = f"{UNIQUE_RITUAL_DESIGNS_REL}.unique_wonders[{index}]"
        if not isinstance(entry, dict) or type(entry.get("id")) is not int or not isinstance(entry.get("key"), str):
            raise RuntimeError(f"{source} must have an integer id and string key")
        wonder_id, key = entry["id"], entry["key"]
        wonder = wonders_by_id.get(wonder_id)
        if wonder is None or not wonder.get("is_unique") or wonder["key"] != key:
            raise RuntimeError(f"{source} id/key does not match a unique wonder: {wonder_id}/{key}")
        if wonder_id in seen_ids or key in seen_keys:
            raise RuntimeError(f"{source} duplicates ritual design id/key: {wonder_id}/{key}")
        seen_ids.add(wonder_id)
        seen_keys.add(key)


def get_unique_wonder_source(unique_wonders_data: dict[str, Any], wonder_key: str) -> dict[str, Any]:
    for wonder in unique_wonders_data.get("unique_wonders", []):
        if wonder.get("key") == wonder_key:
            return wonder
    raise KeyError(f"Unknown unique wonder key: {wonder_key}")
