from __future__ import annotations

import subprocess
import threading
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    write_localization_updates,
)
from scripts.wonder_mechanics_lib import (
    ceremony_modifier_for_style,
    ceremony_styles,
    final_building_for_style,
    load_all_wonder_mechanics_data,
    load_manual_game_concept_ids,
    mechanic_key,
    ritual_blessing_modifier_name,
    ritual_burden_modifier_name,
)

LANGUAGES = ("english", "simp_chinese")
LANGUAGE_LABELS = {
    "english": "English",
    "simp_chinese": "简体中文",
}
LANGUAGE_DATA_KEYS = {
    "english": "en",
    "simp_chinese": "zh",
}
ROMAN_NUMERALS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
}
GENERATED_LOC_FILES = {
    "english": REPO_ROOT / "src" / "main_menu" / "localization" / "english" / "tv_engineering_department_wonder_mechanics_l_english.yml",
    "simp_chinese": REPO_ROOT / "src" / "main_menu" / "localization" / "simp_chinese" / "tv_engineering_department_wonder_mechanics_l_simp_chinese.yml",
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
    "scripts/main_menu/localization/english/gen_tv_engineering_department_wonder_mechanics_l_english.py",
    "scripts/main_menu/localization/simp_chinese/gen_tv_engineering_department_wonder_mechanics_l_simp_chinese.py",
)


@dataclass(slots=True)
class FieldSpec:
    key: str
    label: str
    group: str
    language: str
    source_kind: str
    file_path: Path
    original_value: str
    height: int = 3

    def to_api_dict(self) -> dict[str, Any]:
        origin_label = "数据源" if self.source_kind == "generated" else "手工文件"
        return {
            "key": self.key,
            "label": self.label,
            "group": self.group,
            "language": self.language,
            "source_kind": self.source_kind,
            "origin_label": origin_label,
            "original_value": self.original_value,
            "value": self.original_value,
            "height": self.height,
        }


class WonderLocalizationService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._log_fragments: list[str] = []
        self.wonders: list[dict[str, Any]] = []
        self.mechanics: dict[str, Any] = {}
        self.manual_concepts: set[str] = set()
        self.event_suffixes: dict[int, str] = {}
        self.localization_data: dict[str, dict[str, str]] = {}
        self.localization_values: dict[Path, dict[str, str]] = {}
        self.manual_concept_loc_keys: set[str] = set()
        self.reload_from_disk()
        self._append_log("[server] Wonder Localization Editor Web 已就绪\n")

    @property
    def log_text(self) -> str:
        return "".join(self._log_fragments)

    def _append_log(self, text: str) -> None:
        self._log_fragments.append(text)
        if len(self._log_fragments) > 400:
            self._log_fragments = self._log_fragments[-400:]

    def reload_from_disk(self) -> None:
        with self._lock:
            self.wonders, self.mechanics = load_all_wonder_mechanics_data()
            self.wonders = sorted(self.wonders, key=lambda item: int(item["id"]))
            self.manual_concepts = load_manual_game_concept_ids()
            self.event_suffixes = load_engineering_department_suffix_map()
            self._load_localization_values()

    def bootstrap_payload(self) -> dict[str, Any]:
        with self._lock:
            wonders = self.list_wonders()
            first_wonder_id = wonders[0]["id"] if wonders else None
            return {
                "title": "Towards Victory 奇观本地化编辑器",
                "status": "就绪",
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
                    wonder.get("loc", {}).get("en", ""),
                    wonder.get("loc", {}).get("zh", ""),
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
            return {
                "summary": self._wonder_summary(wonder),
                "meta": self._wonder_meta(wonder),
                "languages": self._serialize_specs(specs),
                "status": f"已载入 {wonder['key']}",
            }

    def reload_wonder_payload(self, wonder_id: int) -> dict[str, Any]:
        self.reload_from_disk()
        payload = self.get_wonder_payload(wonder_id)
        if payload is None:
            raise KeyError(f"Unknown wonder id: {wonder_id}")
        payload["status"] = f"已重新加载 {payload['summary']['key']}"
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
        *,
        regenerate: bool = True,
    ) -> dict[str, Any]:
        with self._lock:
            wonder = self._get_wonder(wonder_id)
            specs = self._build_specs_for_wonder(wonder)
            manual_updates: dict[Path, dict[str, str]] = {}
            localization_updates: dict[str, dict[str, str]] = {language: {} for language in LANGUAGES}
            incoming_values = values_by_language or {}

            for language, language_specs in specs.items():
                language_values = incoming_values.get(language, {})
                for spec in language_specs:
                    value = normalize_editor_text(str(language_values.get(spec.key, spec.original_value)))
                    if value == spec.original_value:
                        continue
                    if spec.source_kind == "manual":
                        manual_updates.setdefault(spec.file_path, {})[spec.key] = value
                    else:
                        localization_updates[language][spec.key] = value

            changed_files: list[str] = []
            try:
                for path, updates in manual_updates.items():
                    if write_localization_updates(path, updates):
                        changed_files.append(str(path.relative_to(REPO_ROOT)))

                if any(localization_updates[language] for language in LANGUAGES):
                    self.localization_data = load_wonder_localization_data()
                    for language, updates in localization_updates.items():
                        if not updates:
                            continue
                        language_values = self.localization_data.setdefault(language, {})
                        language_values.update(updates)
                    save_wonder_localization_data(self.localization_data)
                    changed_files.append(str(WONDER_LOCALIZATION_FILE.relative_to(REPO_ROOT)))

                if regenerate:
                    self._run_generators()

                self.reload_from_disk()
                payload = self.get_wonder_payload(wonder_id)
                if payload is None:
                    raise KeyError(f"Unknown wonder id after reload: {wonder_id}")

                if changed_files:
                    status = f"已保存：{', '.join(changed_files)}"
                elif regenerate:
                    status = "已重新生成，没有新的编辑"
                else:
                    status = "没有新的编辑"

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
                raise exc

    def _load_localization_values(self) -> None:
        paths = set(GENERATED_LOC_FILES.values()) | set(MANUAL_CONCEPT_FILES.values()) | set(MANUAL_ENGINEERING_FILES.values())
        self.localization_values = {path: load_localization_map(path) for path in paths}
        self.localization_data = load_wonder_localization_data()
        for language, path in GENERATED_LOC_FILES.items():
            merged = dict(self.localization_values.get(path, {}))
            merged.update(self.localization_data.get(language, {}))
            self.localization_values[path] = merged
        self.manual_concept_loc_keys = self._load_manual_concept_loc_keys()

    def _load_manual_concept_loc_keys(self) -> set[str]:
        keys: set[str] = set()
        for path in MANUAL_CONCEPT_FILES.values():
            for key in self.localization_values.get(path, {}):
                if key.startswith("game_concept_"):
                    keys.add(key)
        return keys

    def _get_wonder(self, wonder_id: int) -> dict[str, Any]:
        for wonder in self.wonders:
            if int(wonder["id"]) == int(wonder_id):
                return wonder
        raise KeyError(f"Unknown wonder id: {wonder_id}")

    def _wonder_summary(self, wonder: dict[str, Any]) -> dict[str, Any]:
        kind_label = "独特" if wonder.get("is_unique") else "通用"
        return {
            "id": int(wonder["id"]),
            "key": wonder["key"],
            "concept": wonder["concept"],
            "is_unique": bool(wonder.get("is_unique")),
            "kind_label": kind_label,
            "name_en": wonder.get("loc", {}).get("en", ""),
            "name_zh": wonder.get("loc", {}).get("zh", ""),
            "display_name": f"{wonder.get('loc', {}).get('zh', '')} / {wonder.get('loc', {}).get('en', '')}",
        }

    def _wonder_meta(self, wonder: dict[str, Any]) -> dict[str, Any]:
        meta = {
            "id": int(wonder["id"]),
            "key": wonder["key"],
            "concept": wonder["concept"],
            "name_en": wonder.get("loc", {}).get("en", ""),
            "name_zh": wonder.get("loc", {}).get("zh", ""),
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

    def _build_specs_for_wonder(self, wonder: dict[str, Any]) -> dict[str, list[FieldSpec]]:
        specs = {language: [] for language in LANGUAGES}
        code = wonder["key"].upper()
        concept_key = f"game_concept_{wonder['concept']}"
        concept_desc_key = f"{concept_key}_desc"
        is_manual_concept = concept_key in self.manual_concept_loc_keys
        design = self.mechanics.get("designs", {}).get(mechanic_key(wonder), {})

        for language in LANGUAGES:
            generated_file = GENERATED_LOC_FILES[language]
            concept_file = MANUAL_CONCEPT_FILES[language] if is_manual_concept else generated_file
            concept_source = "manual" if is_manual_concept else "generated"
            self._add_field(specs, language, concept_source, concept_file, "基础文本", "概念名称", concept_key, height=2)
            self._add_field(specs, language, concept_source, concept_file, "基础文本", "概念描述", concept_desc_key, height=5)

            self._add_generated(specs, language, "工程提案", "提案简介", f"TV_ENGINEERING_PROPOSAL_{code}_TEXT", height=3)
            self._add_generated(specs, language, "工程提案", "续建提案", f"TV_ENGINEERING_PROPOSAL_RESUME_{code}_TEXT", height=3)
            self._add_generated(specs, language, "工程提案", "扩建提案", f"TV_ENGINEERING_PROPOSAL_EXPAND_{code}_TEXT", height=3)
            self._add_generated(specs, language, "工程提案", "锁定后的说明", f"TV_ENGINEERING_LOCKED_{code}_TEXT", height=2)
            self._add_generated(specs, language, "工程提案", "提案按钮", f"TV_ENGINEERING_PROPOSAL_BUTTON_{code}", height=2)
            self._add_generated(specs, language, "工程提案", "锁定 tooltip", f"TV_WONDER_LOCK_{code}_TT", height=2)

            self._add_generated(specs, language, "奇观与构件", "奇观建筑名称", f"tv_wonder_{wonder['key']}", height=2)
            self._add_generated(specs, language, "奇观与构件", "奇观建筑描述", f"tv_wonder_{wonder['key']}_desc", height=3)
            for part, label in (
                ("foundation", "地基构件"),
                ("body", "主体构件"),
                ("function", "功能构件"),
                ("decoration", "封顶装饰构件"),
            ):
                self._add_generated(specs, language, "奇观与构件", f"{label}名称", f"tv_wonder_{wonder['key']}_{part}", height=2)
                self._add_generated(specs, language, "奇观与构件", f"{label}描述", f"tv_wonder_{wonder['key']}_{part}_desc", height=3)
            if not wonder.get("is_unique"):
                self._add_generated(specs, language, "奇观与构件", "仪式附属建筑名称", f"tv_wonder_{wonder['key']}_ritual_annex", height=2)
                self._add_generated(specs, language, "奇观与构件", "仪式附属建筑描述", f"tv_wonder_{wonder['key']}_ritual_annex_desc", height=3)

            for level in range(1, 7):
                self._add_generated(
                    specs,
                    language,
                    "修正名",
                    f"等级 {ROMAN_NUMERALS[level]} 修正名",
                    f"STATIC_MODIFIER_NAME_tv_wonder_{wonder['key']}_level_{level}",
                    height=2,
                )
            if not wonder.get("is_unique"):
                self._add_generated(
                    specs,
                    language,
                    "修正名",
                    "一号仪式负担修正名",
                    f"STATIC_MODIFIER_NAME_{ritual_burden_modifier_name(wonder)}",
                    height=2,
                )
                self._add_generated(
                    specs,
                    language,
                    "修正名",
                    "一号仪式祝福修正名",
                    f"STATIC_MODIFIER_NAME_{ritual_blessing_modifier_name(wonder)}",
                    height=2,
                )

            for style in ceremony_styles(wonder):
                branch_name = self._branch_name(wonder, design, style, language)
                building = final_building_for_style(wonder, style)
                ceremony_key = building.removeprefix("tv_wonder_").upper()
                label_prefix = f"仪式 {style}：{branch_name}"
                self._add_generated(specs, language, "仪式分支", f"{label_prefix} 最终建筑名", building, height=2)
                self._add_generated(specs, language, "仪式分支", f"{label_prefix} 最终建筑描述", f"{building}_desc", height=3)
                ceremony_modifier = ceremony_modifier_for_style(wonder, self.mechanics, style)
                if ceremony_modifier is not None:
                    self._add_generated(
                        specs,
                        language,
                        "仪式分支",
                        f"{label_prefix} 修正名",
                        f"STATIC_MODIFIER_NAME_{ceremony_modifier[0]}",
                        height=2,
                    )
                self._add_generated(
                    specs,
                    language,
                    "仪式分支",
                    f"{label_prefix} 按钮",
                    f"TV_ENGINEERING_CEREMONY_{ceremony_key}_BUTTON",
                    height=2,
                )
                self._add_generated(
                    specs,
                    language,
                    "仪式分支",
                    f"{label_prefix} 执行/进行中文字",
                    f"TV_ENGINEERING_ACTIVE_RITUAL_{code}_{style}",
                    height=3,
                )

            if wonder.get("is_unique"):
                self._add_generated(
                    specs,
                    language,
                    "事件文本",
                    "独特奇观落成事件正文",
                    f"tv_engineering_department.500.d_{wonder['key']}",
                    height=6,
                )
            else:
                suffix = self.event_suffixes.get(int(wonder["id"]))
                if suffix:
                    for style in ceremony_styles(wonder):
                        branch_name = self._branch_name(wonder, design, style, language)
                        self._add_generated(
                            specs,
                            language,
                            "事件文本",
                            f"通用奇观落成事件正文 {style}：{branch_name}",
                            f"tv_engineering_department.500.d_{suffix}_{style}",
                            height=6,
                        )
                    self._add_generated(
                        specs,
                        language,
                        "事件文本",
                        "世界新闻事件正文",
                        f"tv_engineering_department.600.d_{suffix}",
                        height=6,
                    )

        return specs

    def _branch_name(self, wonder: dict[str, Any], design: dict[str, Any], style: int, language: str) -> str:
        data_key = LANGUAGE_DATA_KEYS[language]
        if wonder.get("is_unique"):
            ritual = wonder.get("ritual", {})
            return ritual.get("loc", {}).get(data_key, f"Style {style}")
        branch = design.get("branches", {}).get(style, {})
        return branch.get(data_key, branch.get("en", f"Style {style}"))

    def _field_exists(self, path: Path, key: str) -> bool:
        return key in self.localization_values.get(path, {})

    def _add_generated(
        self,
        specs: dict[str, list[FieldSpec]],
        language: str,
        group: str,
        label: str,
        key: str,
        *,
        height: int = 3,
    ) -> None:
        self._add_field(specs, language, "generated", GENERATED_LOC_FILES[language], group, label, key, height=height)

    def _add_field(
        self,
        specs: dict[str, list[FieldSpec]],
        language: str,
        source_kind: str,
        file_path: Path,
        group: str,
        label: str,
        key: str,
        *,
        height: int = 3,
    ) -> None:
        original_value = self.localization_values.get(file_path, {}).get(key, "")
        specs[language].append(
            FieldSpec(
                key=key,
                label=label,
                group=group,
                language=language,
                source_kind=source_kind,
                file_path=file_path,
                original_value=original_value,
                height=height,
            )
        )

    def _run_generators(self) -> None:
        self._append_log("\n[regen] 开始重新生成奇观本地化...\n")
        for script in REGEN_SCRIPTS:
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
                self._append_log(f"[regen] 失败：{script} 退出码 {result.returncode}\n")
                raise RuntimeError(f"{script} 退出码 {result.returncode}。详情见日志。")
        self._append_log("[regen] 完成\n")


def build_check_report() -> list[str]:
    wonders, _mechanics = load_all_wonder_mechanics_data()
    manual_concepts = load_manual_game_concept_ids()
    localization_data = load_wonder_localization_data()
    concept_loc_keys = set()
    for path in MANUAL_CONCEPT_FILES.values():
        concept_loc_keys.update(key for key in load_localization_map(path) if key.startswith("game_concept_"))
    suffixes = load_engineering_department_suffix_map()
    generated_keys = sum(len(load_localization_map(path)) for path in GENERATED_LOC_FILES.values())
    source_keys = sum(len(values) for values in localization_data.values())
    manual_keys = sum(len(load_localization_map(path)) for path in set(MANUAL_CONCEPT_FILES.values()) | set(MANUAL_ENGINEERING_FILES.values()))
    return [
        f"Loaded {len(wonders)} wonders",
        f"Concept declarations: {len(manual_concepts)}",
        f"Manual concept localization keys: {len(concept_loc_keys)}",
        f"Engineering event suffix mappings: {len(suffixes)}",
        f"Wonder localization source keys: {source_keys}",
        f"Generated localization keys parsed: {generated_keys}",
        f"Manual localization keys parsed: {manual_keys}",
    ]
