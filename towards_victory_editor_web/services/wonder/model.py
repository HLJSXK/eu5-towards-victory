"""Wonder edit application and queries."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
from urllib.parse import quote

from scripts_engineering_department.wonder_localization_lib import normalize_editor_text
from scripts_engineering_department.wonder_mechanics.rituals import (
    SUPPORTED_RITUAL_COST_TYPES,
    normalize_unique_ceremony,
    normalize_unique_ritual,
)

from . import sources
from .field_types import serialize_mechanics_specs, serialize_specs
from .fields import build_mechanics_specs_for_wonder, build_specs_for_wonder
from .localization import LANGUAGES, localization_value, wonder_name_key
from .options import reference_option_catalogs
from .site_rules import render_preference_script_from_state, render_trigger_script_from_state
from .sources import (
    default_unique_ritual_prompts_data,
    get_unique_wonder_source,
    unique_ritual_design_translation_index,
    unique_ritual_prompt_index,
)
from .values import (
    mapping_from_modifier_rows,
    normalize_editor_wonder_size,
    normalize_multiline_editor_text,
    parse_structured_editor_value,
    parse_unique_initial_level,
    parse_yaml_editor_value,
    reward_list_from_rows,
    unique_ceremony_from_editor_state,
    unique_ritual_from_editor_state,
    wonder_size_label,
)


RITUAL_DESIGN_FIELD_LABELS = {
    "title": "标题",
    "historical_flavor": "历史氛围",
    "mode": "模式",
    "duration": "持续时间",
    "listeners": "监听器",
    "confirmation_logic": "确认逻辑",
    "start_logic": "启动逻辑",
    "progress_logic": "推进逻辑",
    "completion_logic": "完成逻辑",
    "failure_or_timeout_logic": "失败或超时逻辑",
    "implementation_mapping": "实现映射",
    "confirmation_trigger_script": "确认触发脚本",
    "start_effect_script": "启动效果脚本",
    "snapshot_effect_script": "快照效果脚本",
    "progress_effect_script": "推进效果脚本",
    "completion_trigger_script": "完成触发脚本",
    "completion_effect_script": "完成效果脚本",
    "intended_rewards": "预期奖励",
    "permanent_country_modifier": "永久国家修正",
    "local_building_reward": "本地建筑奖励",
    "one_time_reward": "一次性奖励",
    "notes": "备注",
}


class WonderModel:
    """Apply Wonder edits and query summaries, details and ritual designs."""

    def option_catalog_payload(self) -> dict[str, Any]:
        with self._lock:
            return {"version": self._option_catalog_version, "catalogs": self._option_catalogs}

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
            specs = build_specs_for_wonder(
                wonder, mechanics=self.mechanics, event_suffixes=self.event_suffixes,
                localization_data=self.localization_data,
            )
            mechanics_specs = build_mechanics_specs_for_wonder(
                wonder, mechanics=self.mechanics, mechanics_data=self.mechanics_data,
                unique_wonders_data=self.unique_wonders_data,
                generic_options=self._generic_wonder_options() if wonder.get("is_unique") else [],
                option_catalogs=self._option_catalogs,
            )
            payload = {
                "summary": self._wonder_summary(wonder),
                "meta": self._wonder_meta(wonder),
                "languages": serialize_specs(specs),
                "mechanics": serialize_mechanics_specs(mechanics_specs),
                "ritual_design": self._unique_ritual_design_for_wonder(wonder),
                "ritual_prompt": self._unique_ritual_prompt_for_wonder(wonder),
                "status": f"Loaded {wonder['key']}",
                "catalog_version": self._option_catalog_version,
            }
            reference_option_catalogs(payload["mechanics"], self._option_catalogs)
            return payload

    def _apply_wonder_edits(
        self,
        wonder_id: int,
        values_by_language: dict[str, dict[str, str]] | None,
        mechanics_values: dict[str, Any] | None = None,
    ) -> dict[str, bool]:
        wonder = self._get_wonder(wonder_id)
        specs = build_specs_for_wonder(
            wonder, mechanics=self.mechanics, event_suffixes=self.event_suffixes,
            localization_data=self.localization_data,
        )
        mechanics_specs = build_mechanics_specs_for_wonder(
            wonder, mechanics=self.mechanics, mechanics_data=self.mechanics_data,
            unique_wonders_data=self.unique_wonders_data,
            generic_options=self._generic_wonder_options() if wonder.get("is_unique") else [],
            option_catalogs=self._option_catalogs,
        )
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
                "unique_ceremony_editor",
                "site_trigger_template",
                "site_preference_template",
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
                entry = get_unique_wonder_source(self.unique_wonders_data, spec.target_key)
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
                entry = get_unique_wonder_source(self.unique_wonders_data, spec.target_key)
                entry["location"] = value
                unique_file_changed = True
                continue

            if spec.target_kind == "unique_initial_level":
                parsed = parse_unique_initial_level(value, context=spec.key)
                entry = get_unique_wonder_source(self.unique_wonders_data, spec.target_key)
                entry["initial_level"] = parsed
                unique_file_changed = True
                continue

            if spec.target_kind == "unique_ritual":
                if spec.field_type == "unique_ritual_editor":
                    parsed = unique_ritual_from_editor_state(value, context=spec.key)
                else:
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                entry = get_unique_wonder_source(self.unique_wonders_data, spec.target_key)
                updated_entry = dict(entry)
                updated_entry["ritual"] = parsed
                updated_entry["ritual"] = normalize_unique_ritual(updated_entry)
                entry["ritual"] = updated_entry["ritual"]
                unique_file_changed = True
                continue

            if spec.target_kind == "unique_ceremony":
                if spec.field_type == "unique_ceremony_editor":
                    parsed = unique_ceremony_from_editor_state(value, context=spec.key)
                else:
                    parsed = parse_yaml_editor_value(value, expected_type=dict)
                entry = get_unique_wonder_source(self.unique_wonders_data, spec.target_key)
                updated_entry = dict(entry)
                updated_entry["ceremony"] = parsed
                entry["ceremony"] = normalize_unique_ceremony(updated_entry)
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

    def _apply_ritual_prompt_edit(self, wonder_id: int, prompt: str) -> bool:
        wonder = self._get_wonder(wonder_id)
        if not wonder.get("is_unique"):
            raise ValueError(f"{wonder['key']} is not a unique wonder")

        normalized_prompt = normalize_multiline_editor_text(str(prompt))
        current_prompt = str(
            unique_ritual_prompt_index(self.unique_ritual_prompts_data)
            .get(wonder["key"], {})
            .get("prompt", "")
        )
        if normalized_prompt == current_prompt:
            return False

        prompt_entries = [
            deepcopy(entry)
            for entry in self.unique_ritual_prompts_data.get("unique_wonders", [])
            if isinstance(entry, dict) and str(entry.get("key", "")).strip() != wonder["key"]
        ]
        if normalized_prompt:
            design = self._unique_ritual_design_for_wonder(wonder) or {}
            ritual_design = design.get("ritual_design", {}) if isinstance(design, dict) else {}
            prompt_entries.append(
                {
                    "id": int(wonder["id"]),
                    "key": wonder["key"],
                    "base_key": wonder.get("base_key", ""),
                    "location": wonder.get("location", ""),
                    "ritual_title": ritual_design.get("title", ""),
                    "prompt": normalized_prompt,
                }
            )
        prompt_entries.sort(key=lambda entry: int(entry.get("id", 0)))
        data = deepcopy(self.unique_ritual_prompts_data or default_unique_ritual_prompts_data())
        data["unique_wonders"] = prompt_entries
        self.unique_ritual_prompts_data = data
        return True

    def _unique_ritual_design_by_key(self, wonder_key: str) -> dict[str, Any] | None:
        for entry in self.unique_ritual_designs_data.get("unique_wonders", []):
            if isinstance(entry, dict) and entry.get("key") == wonder_key:
                return entry
        return None

    def _unique_ritual_prompt_for_wonder(self, wonder: dict[str, Any]) -> dict[str, Any] | None:
        if not wonder.get("is_unique"):
            return None
        entry = unique_ritual_prompt_index(self.unique_ritual_prompts_data).get(wonder["key"], {})
        return {
            "source_path": sources.UNIQUE_RITUAL_PROMPTS_REL,
            "prompt": str(entry.get("prompt", "")),
            "exists": bool(entry.get("prompt")),
        }

    def _attach_unique_ritual_translation(self, payload: dict[str, Any]) -> None:
        translation = unique_ritual_design_translation_index(self.unique_ritual_design_translations_data).get(
            str(payload.get("key", ""))
        )
        payload["translation_source_path"] = sources.UNIQUE_RITUAL_DESIGNS_ZH_REL
        if not translation:
            return
        ritual_design_zh = translation.get("ritual_design_zh")
        if isinstance(ritual_design_zh, dict):
            payload["ritual_design_zh"] = deepcopy(ritual_design_zh)

    def _unique_ritual_design_for_wonder(self, wonder: dict[str, Any]) -> dict[str, Any] | None:
        if not wonder.get("is_unique"):
            return None
        entry = self._unique_ritual_design_by_key(wonder["key"])
        if entry is None:
            return None
        payload = deepcopy(entry)
        summary = self._wonder_summary(wonder)
        payload["name_en"] = summary["name_en"]
        payload["name_zh"] = summary["name_zh"]
        payload["display_name"] = summary["display_name"]
        payload["source_path"] = sources.UNIQUE_RITUAL_DESIGNS_REL
        payload["field_labels"] = dict(RITUAL_DESIGN_FIELD_LABELS)
        self._attach_unique_ritual_translation(payload)
        return payload

    def ritual_design_catalog_payload(self) -> dict[str, Any]:
        with self._lock:
            entries = []
            translations = unique_ritual_design_translation_index(self.unique_ritual_design_translations_data)
            for entry in self.unique_ritual_designs_data.get("unique_wonders", []):
                wonder = self._get_wonder(entry["id"])
                summary = self._wonder_summary(wonder)
                ritual = entry.get("ritual_design") or {}
                translated = translations.get(str(entry.get("key", "")), {}).get("ritual_design_zh") or {}
                fields = ("title", "mode", "listeners")
                item = {
                    "id": entry["id"],
                    "key": entry["key"],
                    "display_name": summary["display_name"],
                    "ritual_design": {key: deepcopy(ritual[key]) for key in fields if key in ritual},
                }
                if translated:
                    item["ritual_design_zh"] = {key: deepcopy(translated[key]) for key in fields if key in translated}
                entries.append(item)
            entries.sort(key=lambda item: item["id"])
            return {
                "source_path": sources.UNIQUE_RITUAL_DESIGNS_REL,
                "translation_source_path": sources.UNIQUE_RITUAL_DESIGNS_ZH_REL,
                "prompt_source_path": sources.UNIQUE_RITUAL_PROMPTS_REL,
                "field_labels": dict(RITUAL_DESIGN_FIELD_LABELS),
                "count": len(entries),
                "wonders": entries,
            }

    def ritual_design_payload(self, wonder_id: int) -> dict[str, Any]:
        with self._lock:
            wonder = self._get_wonder(wonder_id)
            if not wonder.get("is_unique"):
                raise ValueError(f"{wonder['key']} is not a unique wonder")
            payload = self._unique_ritual_design_for_wonder(wonder)
            if payload is None:
                raise KeyError(f"No ritual design for wonder id: {wonder_id}")
            return payload

    def _get_wonder(self, wonder_id: int) -> dict[str, Any]:
        for wonder in self.wonders:
            if int(wonder["id"]) == int(wonder_id):
                return wonder
        raise KeyError(f"Unknown wonder id: {wonder_id}")

    def _unique_initial_level(self, wonder: dict[str, Any]) -> int:
        if not wonder.get("is_unique"):
            return 0
        unique_key = str(wonder["key"])
        entry = get_unique_wonder_source(self.unique_wonders_data, unique_key)
        return parse_unique_initial_level(
            entry.get("initial_level"),
            context=f"unique_wonders[{unique_key}].initial_level",
        )

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
        return localization_value(self.localization_data, language, wonder_name_key(wonder))

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

        image_path = sources.GENERATED_WONDER_IMAGES_DIR / filename
        exists = image_path.is_file()
        return {
            "stem": Path(filename).stem,
            "filename": filename,
            "path": f"assets/generated_wonders/{filename}",
            "url": f"{sources.WONDER_IMAGE_URL_PREFIX}/{quote(filename)}" if exists else None,
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
            "initial_level": self._unique_initial_level(wonder),
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
            "initial_level": self._unique_initial_level(wonder),
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
