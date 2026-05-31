import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from wonder_localization_lib import (
    REPO_ROOT,
    WONDER_LOCALIZATION_FILE,
    load_engineering_department_suffix_map,
    load_localization_map,
    load_wonder_localization_data,
    normalize_editor_text,
    save_wonder_localization_data,
    write_localization_updates,
)
from wonder_mechanics_lib import (
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


@dataclass(slots=True)
class FieldWidget:
    spec: FieldSpec
    widget: tk.Text


class ScrollableFrame(ttk.Frame):
    def __init__(self, master: tk.Widget) -> None:
        super().__init__(master)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.interior = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.interior.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_frame_configure(self, _event: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def clear(self) -> None:
        for child in self.interior.winfo_children():
            child.destroy()


class WonderLocalizationEditor:
    def __init__(self) -> None:
        self.wonders, self.mechanics = load_all_wonder_mechanics_data()
        self.wonders = sorted(self.wonders, key=lambda item: int(item["id"]))
        self.manual_concepts = load_manual_game_concept_ids()
        self.event_suffixes = load_engineering_department_suffix_map()
        self.localization_data = load_wonder_localization_data()
        self.localization_values: dict[Path, dict[str, str]] = {}
        self._load_localization_values()

        self.current_wonder: dict | None = None
        self.current_specs: dict[str, list[FieldSpec]] = {language: [] for language in LANGUAGES}
        self.field_widgets: list[FieldWidget] = []
        self.wonder_by_iid: dict[str, dict] = {}
        self._updating_tree = False

        self.root = tk.Tk()
        self.root.title("Towards Victory 奇观本地化编辑器")
        self.root.geometry("1380x900")
        self.root.minsize(1100, 720)
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="就绪")
        self.meta_var = tk.StringVar(value="")
        self._build_ui()
        self._populate_wonder_tree()
        self._select_first_wonder()

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

    def _build_ui(self) -> None:
        root_frame = ttk.Frame(self.root, padding=8)
        root_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        paned = ttk.Panedwindow(root_frame, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky="nsew")
        root_frame.grid_rowconfigure(0, weight=1)
        root_frame.grid_columnconfigure(0, weight=1)

        left = ttk.Frame(paned, padding=(0, 0, 8, 0))
        right = ttk.Frame(paned)
        paned.add(left, weight=1)
        paned.add(right, weight=5)

        ttk.Label(left, text="选择奇观").grid(row=0, column=0, sticky="w")
        search = ttk.Entry(left, textvariable=self.search_var)
        search.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.search_var.trace_add("write", lambda *_args: self._populate_wonder_tree())

        columns = ("id", "type", "name")
        self.wonder_tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse", height=24)
        self.wonder_tree.heading("id", text="ID")
        self.wonder_tree.heading("type", text="类型")
        self.wonder_tree.heading("name", text="名称")
        self.wonder_tree.column("id", width=52, stretch=False, anchor="e")
        self.wonder_tree.column("type", width=58, stretch=False, anchor="center")
        self.wonder_tree.column("name", width=260, stretch=True)
        tree_scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.wonder_tree.yview)
        self.wonder_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.wonder_tree.grid(row=2, column=0, sticky="nsew")
        tree_scrollbar.grid(row=2, column=1, sticky="ns")
        self.wonder_tree.bind("<<TreeviewSelect>>", self._on_wonder_selected)
        left.grid_rowconfigure(2, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ttk.Label(right, textvariable=self.meta_var, wraplength=980, justify="left").grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.notebook = ttk.Notebook(right)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.language_frames: dict[str, ScrollableFrame] = {}
        for language in LANGUAGES:
            frame = ScrollableFrame(self.notebook)
            self.language_frames[language] = frame
            self.notebook.add(frame, text=LANGUAGE_LABELS[language])

        log_frame = ttk.Frame(self.notebook)
        self.log_text = tk.Text(log_frame, wrap="word", height=12, state="disabled")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.notebook.add(log_frame, text="日志")

        button_frame = ttk.Frame(right)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(button_frame, text="保存并重新生成", command=self._save_and_regenerate).grid(row=0, column=0, sticky="w")
        ttk.Button(button_frame, text="重新加载文件", command=self._reload_current_wonder).grid(row=0, column=1, sticky="w", padx=(8, 0))
        ttk.Label(button_frame, textvariable=self.status_var).grid(row=0, column=2, sticky="e", padx=(16, 0))
        button_frame.grid_columnconfigure(2, weight=1)

    def _populate_wonder_tree(self) -> None:
        previous_id = str(self.current_wonder["id"]) if self.current_wonder else None
        filter_text = self.search_var.get().strip().lower()
        self._updating_tree = True
        try:
            for item in self.wonder_tree.get_children():
                self.wonder_tree.delete(item)
            self.wonder_by_iid.clear()

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
                if filter_text and filter_text not in haystack:
                    continue

                iid = str(wonder["id"])
                self.wonder_by_iid[iid] = wonder
                kind = "独特" if wonder.get("is_unique") else "通用"
                name = f"{wonder.get('loc', {}).get('zh', '')} / {wonder.get('loc', {}).get('en', '')}"
                self.wonder_tree.insert("", "end", iid=iid, values=(wonder["id"], kind, name))

            if previous_id in self.wonder_by_iid:
                self.wonder_tree.selection_set(previous_id)
                self.wonder_tree.focus(previous_id)
        finally:
            self._updating_tree = False

    def _select_first_wonder(self) -> None:
        children = self.wonder_tree.get_children()
        if not children:
            return
        first = children[0]
        self.wonder_tree.selection_set(first)
        self.wonder_tree.focus(first)
        self._load_wonder(self.wonder_by_iid[first])

    def _on_wonder_selected(self, _event: tk.Event) -> None:
        if self._updating_tree:
            return
        selection = self.wonder_tree.selection()
        if not selection:
            return
        iid = selection[0]
        wonder = self.wonder_by_iid.get(iid)
        if wonder is None:
            return
        if self.current_wonder is not None and int(self.current_wonder["id"]) == int(wonder["id"]):
            return
        if not self._confirm_save_before_switch():
            self._restore_current_tree_selection()
            return
        self._load_wonder(wonder)

    def _restore_current_tree_selection(self) -> None:
        if self.current_wonder is None:
            return
        iid = str(self.current_wonder["id"])
        if iid not in self.wonder_by_iid:
            return
        self._updating_tree = True
        try:
            self.wonder_tree.selection_set(iid)
            self.wonder_tree.focus(iid)
        finally:
            self._updating_tree = False

    def _confirm_save_before_switch(self) -> bool:
        if not self._has_unsaved_changes():
            return True
        answer = messagebox.askyesnocancel(
            "未保存更改",
            "当前奇观有未保存的本地化修改。是否保存并重新生成后再切换？",
        )
        if answer is None:
            return False
        if answer is False:
            return True
        return self._save_current_wonder(regenerate=True)

    def _load_wonder(self, wonder: dict) -> None:
        self.current_wonder = wonder
        self.current_specs = self._build_specs_for_wonder(wonder)
        self._render_current_wonder()
        base_info = f"，原型 {wonder['base_key']}" if wonder.get("is_unique") else ""
        location = f"，地点 {wonder.get('location')}" if wonder.get("is_unique") else ""
        self.meta_var.set(
            f"ID {wonder['id']} · {wonder['key']} · {wonder['loc']['zh']} / {wonder['loc']['en']} · "
            f"concept={wonder['concept']}{base_info}{location}"
        )
        self.status_var.set(f"已载入 {wonder['key']}")

    def _render_current_wonder(self) -> None:
        self.field_widgets.clear()
        for language, frame in self.language_frames.items():
            frame.clear()
            specs = self.current_specs.get(language, [])
            row = 0
            current_group: str | None = None
            for spec in specs:
                if spec.group != current_group:
                    current_group = spec.group
                    heading = ttk.Label(frame.interior, text=current_group, font=("", 10, "bold"))
                    heading.grid(row=row, column=0, sticky="ew", pady=(10 if row else 0, 4))
                    row += 1

                origin = "数据源" if spec.source_kind == "generated" else "手工文件"
                label_text = f"{spec.label}  [{spec.key}]  ({origin})"
                ttk.Label(frame.interior, text=label_text, wraplength=980, justify="left").grid(row=row, column=0, sticky="ew", pady=(2, 2))
                row += 1

                text = tk.Text(frame.interior, height=spec.height, wrap="word", undo=True)
                text.insert("1.0", spec.original_value)
                text.grid(row=row, column=0, sticky="ew", pady=(0, 6))
                frame.interior.grid_columnconfigure(0, weight=1)
                self.field_widgets.append(FieldWidget(spec=spec, widget=text))
                row += 1

    def _build_specs_for_wonder(self, wonder: dict) -> dict[str, list[FieldSpec]]:
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
                        self._add_field(
                            specs,
                            language,
                            "manual",
                            MANUAL_ENGINEERING_FILES[language],
                            "事件文本",
                            f"通用奇观落成事件正文 {style}：{branch_name}",
                            f"tv_engineering_department.500.d_{suffix}_{style}",
                            height=6,
                        )
                    world_news_key = f"tv_engineering_department.600.d_{suffix}"
                    if self._field_exists(language, MANUAL_ENGINEERING_FILES[language], world_news_key):
                        self._add_field(
                            specs,
                            language,
                            "manual",
                            MANUAL_ENGINEERING_FILES[language],
                            "事件文本",
                            "世界新闻事件正文",
                            world_news_key,
                            height=6,
                        )

        return specs

    def _branch_name(self, wonder: dict, design: dict, style: int, language: str) -> str:
        data_key = LANGUAGE_DATA_KEYS[language]
        if wonder.get("is_unique"):
            ritual = wonder.get("ritual", {})
            return ritual.get("loc", {}).get(data_key, f"Style {style}")
        branch = design.get("branches", {}).get(style, {})
        return branch.get(data_key, branch.get("en", f"Style {style}"))

    def _field_exists(self, language: str, path: Path, key: str) -> bool:
        return key in self.localization_values.get(path, {})

    def _add_generated(self, specs: dict[str, list[FieldSpec]], language: str, group: str, label: str, key: str, *, height: int = 3) -> None:
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

    def _get_widget_value(self, widget: tk.Text) -> str:
        return normalize_editor_text(widget.get("1.0", "end-1c"))

    def _has_unsaved_changes(self) -> bool:
        for field in self.field_widgets:
            if self._get_widget_value(field.widget) != field.spec.original_value:
                return True
        return False

    def _collect_changes(self) -> tuple[dict[Path, dict[str, str]], dict[str, dict[str, str]]]:
        manual_updates: dict[Path, dict[str, str]] = {}
        localization_updates: dict[str, dict[str, str]] = {language: {} for language in LANGUAGES}
        for field in self.field_widgets:
            value = self._get_widget_value(field.widget)
            if value == field.spec.original_value:
                continue
            if field.spec.source_kind == "manual":
                manual_updates.setdefault(field.spec.file_path, {})[field.spec.key] = value
            else:
                localization_updates[field.spec.language][field.spec.key] = value
        return manual_updates, localization_updates

    def _save_and_regenerate(self) -> None:
        self._save_current_wonder(regenerate=True)

    def _save_current_wonder(self, *, regenerate: bool) -> bool:
        if self.current_wonder is None:
            return True

        manual_updates, localization_updates = self._collect_changes()
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
                if not self._run_generators():
                    return False

            self._load_localization_values()
            current_id = int(self.current_wonder["id"])
            self._load_wonder(next(wonder for wonder in self.wonders if int(wonder["id"]) == current_id))
            if changed_files:
                self.status_var.set(f"已保存：{', '.join(changed_files)}")
            elif regenerate:
                self.status_var.set("已重新生成，没有新的编辑")
            else:
                self.status_var.set("没有新的编辑")
            return True
        except Exception as exc:
            messagebox.showerror("保存失败", str(exc))
            self._append_log(f"[ERROR] {exc}\n")
            return False

    def _reload_current_wonder(self) -> None:
        if self._has_unsaved_changes() and not messagebox.askyesno("重新加载", "放弃当前未保存编辑并重新读取文件吗？"):
            return
        self._load_localization_values()
        if self.current_wonder is not None:
            current_id = int(self.current_wonder["id"])
            self._load_wonder(next(wonder for wonder in self.wonders if int(wonder["id"]) == current_id))

    def _run_generators(self) -> bool:
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
                messagebox.showerror("重新生成失败", f"{script} 退出码 {result.returncode}。详情见日志。")
                self.status_var.set("重新生成失败")
                return False
        self._append_log("[regen] 完成\n")
        return True

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def run(self) -> None:
        self.root.mainloop()


def run_check() -> None:
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
    print(f"Loaded {len(wonders)} wonders")
    print(f"Concept declarations: {len(manual_concepts)}")
    print(f"Manual concept localization keys: {len(concept_loc_keys)}")
    print(f"Engineering event suffix mappings: {len(suffixes)}")
    print(f"Wonder localization source keys: {source_keys}")
    print(f"Generated localization keys parsed: {generated_keys}")
    print(f"Manual localization keys parsed: {manual_keys}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Edit Engineering Department wonder localization.")
    parser.add_argument("--check", action="store_true", help="load data and localization files, then exit without opening the GUI")
    args = parser.parse_args()

    if args.check:
        run_check()
        return

    WonderLocalizationEditor().run()


if __name__ == "__main__":
    main()
