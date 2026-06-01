from __future__ import annotations

import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
    UNIQUE_WONDERS_FILE,
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
)

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
WONDER_LOCALIZATION_DATA_REL = "data/wonder_localization.yaml"
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
    options: list[dict[str, str]] = field(default_factory=list)
    help_text: str = ""

    def to_api_dict(self) -> dict[str, Any]:
        origin_label = {
            "shared": "Shared mechanics source",
            "unique": "Unique wonder source",
        }.get(self.source_kind, self.source_kind)
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
    for line in render_header(GENERATED_LOC_SCRIPT_REL[language], WONDER_LOCALIZATION_DATA_REL):
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

    def save_wonder(
        self,
        wonder_id: int,
        values_by_language: dict[str, dict[str, str]] | None,
        mechanics_values: dict[str, str] | None = None,
        *,
        regenerate: bool = True,
    ) -> dict[str, Any]:
        with self._lock:
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

            mechanics_file_changed = False
            unique_file_changed = False
            for spec in mechanics_specs:
                value = normalize_multiline_editor_text(str(incoming_mechanics.get(spec.key, spec.original_value)))
                if value == spec.original_value:
                    continue

                if spec.target_kind == "site_rule":
                    if not value:
                        raise ValueError(f"{spec.key} cannot be empty")
                    self.mechanics_data["site_rules"][spec.target_key][spec.target_parent_key] = value
                    mechanics_file_changed = True
                    continue

                if spec.target_kind == "base_modifiers":
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                    self.mechanics_data.setdefault("base_modifiers", {})[spec.target_key] = parsed
                    mechanics_file_changed = True
                    continue

                if spec.target_kind == "generic_ritual":
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                    self.mechanics_data.setdefault("generic_rituals", {}).setdefault(spec.target_key, {})[spec.target_parent_key] = parsed
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
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                    entry = self._get_unique_wonder_source(spec.target_key)
                    updated_entry = dict(entry)
                    updated_entry["ritual"] = parsed
                    updated_entry["ritual"] = normalize_unique_ritual(updated_entry)
                    entry["ritual"] = updated_entry["ritual"]
                    unique_file_changed = True
                    continue

                raise ValueError(f"Unsupported mechanics target kind: {spec.target_kind}")

            changed_files: list[str] = []
            try:
                if any(localization_updates[language] for language in LANGUAGES):
                    for language, updates in localization_updates.items():
                        if not updates:
                            continue
                        self.localization_data[language].update(updates)
                    validate_canonical_localization_data(
                        self.wonders,
                        self.mechanics,
                        self.event_suffixes,
                        self.localization_data,
                    )
                    save_wonder_localization_data(self.localization_data)
                    changed_files.append(str(WONDER_LOCALIZATION_FILE.relative_to(REPO_ROOT)))

                if mechanics_file_changed:
                    save_yaml_document(MECHANICS_FILE, self.mechanics_data)
                    changed_files.append(str(MECHANICS_FILE.relative_to(REPO_ROOT)))

                if unique_file_changed:
                    save_yaml_document(UNIQUE_WONDERS_FILE, self.unique_wonders_data, preserve_leading_comments=True)
                    changed_files.append(str(UNIQUE_WONDERS_FILE.relative_to(REPO_ROOT)))

                if regenerate:
                    if mechanics_file_changed or unique_file_changed:
                        self._run_generators(WONDER_DATA_REGEN_SCRIPTS)
                    elif any(localization_updates[language] for language in LANGUAGES):
                        self._run_generators(REGEN_SCRIPTS)

                self.reload_from_disk()
                payload = self.get_wonder_payload(wonder_id)
                if payload is None:
                    raise KeyError(f"Unknown wonder id after reload: {wonder_id}")

                if changed_files:
                    status = f"Saved: {', '.join(changed_files)}"
                elif regenerate:
                    status = "Regenerated without source edits"
                else:
                    status = "No changes"

                payload["status"] = status
                return {
                    "status": status,
                    "changed_files": changed_files,
                    "wonders": self.list_wonders(),
                    "wonder": payload,
                    "log_text": self.log_text,
                }
            except Exception as exc:
                self._append_log(f"[error] {exc}\n")
                raise

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

    def _wonder_name(self, wonder: dict[str, Any], language: str) -> str:
        return self._localization_value(language, wonder_name_key(wonder))

    def _wonder_summary(self, wonder: dict[str, Any]) -> dict[str, Any]:
        kind_label = "Unique" if wonder.get("is_unique") else "Generic"
        name_en = self._wonder_name(wonder, "english")
        name_zh = self._wonder_name(wonder, "simp_chinese")
        return {
            "id": int(wonder["id"]),
            "key": wonder["key"],
            "concept": wonder["concept"],
            "is_unique": bool(wonder.get("is_unique")),
            "kind_label": kind_label,
            "name_en": name_en,
            "name_zh": name_zh,
            "display_name": f"{name_zh} / {name_en}",
        }

    def _wonder_meta(self, wonder: dict[str, Any]) -> dict[str, Any]:
        meta = {
            "id": int(wonder["id"]),
            "key": wonder["key"],
            "concept": wonder["concept"],
            "name_en": self._wonder_name(wonder, "english"),
            "name_zh": self._wonder_name(wonder, "simp_chinese"),
            "is_unique": bool(wonder.get("is_unique")),
        }
        if wonder.get("is_unique"):
            meta["base_key"] = wonder.get("base_key")
            meta["location"] = wonder.get("location")
        return meta

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

        self._add_mechanics_spec(
            specs,
            group="Site Rules",
            label="Build trigger script",
            key=f"mechanics.site_trigger.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=MECHANICS_FILE,
            original_value=site_trigger_script_for_key(self.mechanics_data, prototype_key),
            field_type="script",
            target_kind="site_rule",
            target_key=prototype_key,
            target_parent_key="trigger_script",
            height=8,
            help_text="Edits data/wonder_mechanics.yaml site_rules.trigger_script for the mechanic prototype.",
        )
        self._add_mechanics_spec(
            specs,
            group="Site Rules",
            label="Preference script",
            key=f"mechanics.site_preference.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=MECHANICS_FILE,
            original_value=site_preference_script_for_key(self.mechanics_data, prototype_key),
            field_type="script",
            target_kind="site_rule",
            target_key=prototype_key,
            target_parent_key="preference_script",
            height=12,
            help_text="Edits data/wonder_mechanics.yaml site_rules.preference_script for the mechanic prototype.",
        )
        self._add_mechanics_spec(
            specs,
            group="Base Modifiers",
            label="Per-level base modifiers",
            key=f"mechanics.base_modifiers.{wonder['key']}",
            source_kind=shared_source_kind,
            file_path=MECHANICS_FILE,
            original_value=serialize_yaml_editor_value(self.mechanics_data.get("base_modifiers", {}).get(prototype_key, {})),
            field_type="yaml",
            target_kind="base_modifiers",
            target_key=prototype_key,
            height=8,
            help_text="Edits data/wonder_mechanics.yaml base_modifiers for the mechanic prototype.",
        )

        if wonder.get("is_unique"):
            unique_key = wonder["key"]
            unique_entry = self._get_unique_wonder_source(unique_key)
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
            )
            self._add_mechanics_spec(
                specs,
                group="Unique Wonder",
                label="Ritual definition",
                key=f"mechanics.unique_ritual.{unique_key}",
                source_kind="unique",
                file_path=UNIQUE_WONDERS_FILE,
                original_value=serialize_yaml_editor_value(unique_entry["ritual"]),
                field_type="yaml",
                target_kind="unique_ritual",
                target_key=unique_key,
                height=14,
                help_text="Edits data/unique_wonders.yaml ritual. Legacy ceremony aliases are not supported.",
            )
            return specs

        generic_ritual = self.mechanics_data.get("generic_rituals", {}).get(wonder["key"], {})
        for style in (1, 2, 3):
            self._add_mechanics_spec(
                specs,
                group="Generic Ritual",
                label=f"Style {style} ritual config",
                key=f"mechanics.generic_ritual.{wonder['key']}.style_{style}",
                source_kind="shared",
                file_path=MECHANICS_FILE,
                original_value=serialize_yaml_editor_value(generic_ritual.get(f"style_{style}", {})),
                field_type="yaml",
                target_kind="generic_ritual",
                target_key=wonder["key"],
                target_parent_key=f"style_{style}",
                height=8,
                help_text="Edits data/wonder_mechanics.yaml generic_rituals.",
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
        options: list[dict[str, str]] | None = None,
        help_text: str = "",
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
            )
        )

    def _build_specs_for_wonder(self, wonder: dict[str, Any]) -> dict[str, list[FieldSpec]]:
        specs = {language: [] for language in LANGUAGES}
        code = wonder["key"].upper()

        for language in LANGUAGES:
            self._add_localization_field(specs, language, "Concept", "Concept name", concept_key_for_wonder(wonder), height=2)
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
    actual_concepts = normalize_text_file(CONCEPT_FILE.read_text(encoding="utf-8"))
    if actual_concepts != expected_concepts:
        raise ValueError(f"{CONCEPT_FILE} is not synchronized with wonder source data")

    return [
        f"Validated {len(wonders)} wonders against canonical source {WONDER_LOCALIZATION_FILE.relative_to(REPO_ROOT)}",
        f"Required canonical localization keys: {len(required_keys)}",
        f"Generated localization files match canonical output: {len(GENERATED_LOC_FILES)}",
        f"Concept generator output matches wonder source: {CONCEPT_FILE.relative_to(REPO_ROOT)}",
        f"Checked manual localization overlap across {len(manual_loc_paths)} files",
    ]
