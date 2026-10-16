from __future__ import annotations

import copy
import hashlib
import re
import threading
from pathlib import Path
from typing import Any

from scripts_engineering_department.wonder_mechanics.io import REPO_ROOT, load_yaml

from .generator_runs import GeneratorRunService
from .operation_store import OperationStore
from .platform import (
    ConflictError,
    OperationLog,
    assert_resource_base,
    atomic_write_files,
    file_transaction,
    load_yaml_snapshots,
    run_operation,
    snapshot_files,
    yaml_bytes,
)


RESOURCE_ID = "editor.victory_paths"
SCHEMA_VERSION = 1
PATHS_FILE = REPO_ROOT / "data" / "victory_paths.yaml"
TASKS_FILE = REPO_ROOT / "data" / "victory_path_tasks.yaml"
PATHS_REL = "data/victory_paths.yaml"
TASKS_REL = "data/victory_path_tasks.yaml"
SOURCE_RELS = (PATHS_REL, TASKS_REL)

PATH_FIELDS = frozenset(
    {
        "id",
        "score_var",
        "gui",
        "call_updater_in_checker",
        "call_updater_on_situation_start",
        "score_var_init_in_checker",
        "score_updater_body",
        "progress_pct_body",
        "extra_loc_keys",
        "loc",
        "milestones",
    }
)
GUI_FIELDS = frozenset({"order", "tab_label", "icon", "progress_style"})
MILESTONE_FIELDS = frozenset(
    {
        "n",
        "is_short_term",
        "is_long_term",
        "threshold",
        "extra_trigger_block",
        "reward_options",
        "unlock_body",
        "loc",
    }
)
TASK_GROUP_FIELDS = frozenset({"label", "color", "tasks"})

_PATH_ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_TASK_FIELDS = frozenset(
    {
        "id",
        "key",
        "type",
        "metric",
        "thresholds",
        "icon",
        "update",
        "appearance",
        "completion",
        "failure",
        "custom_tooltip",
        "loc",
        "requirement",
        "institution",
        "callback",
        "building",
        "capital_only",
        "price",
        "goods",
        "event_id",
        "global_once",
    }
)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_bool(value: Any) -> bool:
    return isinstance(value, bool)


def _copy(value: Any) -> Any:
    return copy.deepcopy(value)


def _normalise_path(value: str) -> str:
    return value.replace("\\", "/")


def _source_base(base: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(base, dict):
        raise ValueError("base must be an object")
    sources = base.get("sources")
    if not isinstance(sources, list):
        raise ValueError("base.sources must be a list")
    result: dict[str, str] = {}
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("base.sources entries must be objects")
        path = source.get("path")
        digest = source.get("sha256")
        if not isinstance(path, str) or _normalise_path(path) not in SOURCE_RELS:
            raise ValueError(f"path_out_of_bounds: {path!r}")
        if not isinstance(digest, str) or not digest:
            raise ValueError(f"Invalid base sha256 for {path!r}")
        result[_normalise_path(path)] = digest
    if set(result) != set(SOURCE_RELS):
        raise ValueError("base.sources must contain exactly the two victory path sources")
    return result


def _source_payload(snapshots: tuple) -> list[dict[str, Any]]:
    return [
        {"path": snapshot.path, "sha256": snapshot.sha256, "size": snapshot.size}
        for snapshot in snapshots
    ]


def _error(code: str, path: str, message: str) -> dict[str, str]:
    return {"code": code, "path": path, "message": message}


def _diff_values(before: Any, after: Any, path: str, output: list[dict[str, Any]], source: str) -> None:
    if isinstance(before, dict) and isinstance(after, dict):
        keys = list(dict.fromkeys([*before.keys(), *after.keys()]))
        for key in keys:
            child = f"{path}.{key}" if path else str(key)
            if key not in before:
                output.append({"path": source, "field": child, "before": None, "after": _copy(after[key])})
            elif key not in after:
                output.append({"path": source, "field": child, "before": _copy(before[key]), "after": None})
            else:
                _diff_values(before[key], after[key], child, output, source)
        return
    if isinstance(before, list) and isinstance(after, list):
        for index in range(max(len(before), len(after))):
            child = f"{path}[{index}]"
            if index >= len(before):
                output.append({"path": source, "field": child, "before": None, "after": _copy(after[index])})
            elif index >= len(after):
                output.append({"path": source, "field": child, "before": _copy(before[index]), "after": None})
            else:
                _diff_values(before[index], after[index], child, output, source)
        return
    if before != after:
        output.append({"path": source, "field": path, "before": _copy(before), "after": _copy(after)})


class VictoryPathsEditorService:
    def __init__(
        self,
        operation_store: OperationStore | None = None,
        *,
        generator_service: GeneratorRunService | None = None,
    ) -> None:
        self.operation_store = operation_store
        self.generator_service = generator_service or GeneratorRunService(operation_store, repo_root=REPO_ROOT)
        self._lock = threading.Lock()
        self._known_victory_modifiers: set[str] = set()
        self.reload_from_disk()

    def reload_from_disk(self) -> None:
        documents, snapshots = load_yaml_snapshots((PATHS_FILE, TASKS_FILE), repo_root=REPO_ROOT)
        self.paths_data = documents[PATHS_FILE]
        self.tasks_data = documents[TASKS_FILE]
        self._base = snapshots
        self._known_victory_modifiers.update(self._modifier_keys(self.paths_data))

    @staticmethod
    def _modifier_keys(paths_data: dict[str, Any]) -> set[str]:
        keys: set[str] = set()
        for path in paths_data.get("paths", []) if isinstance(paths_data, dict) else []:
            for milestone in path.get("milestones", []) if isinstance(path, dict) else []:
                for option in milestone.get("reward_options", []) if isinstance(milestone, dict) else []:
                    modifier = option.get("modifier") if isinstance(option, dict) else None
                    if isinstance(modifier, dict):
                        keys.update(str(key) for key in modifier)
                    elif isinstance(modifier, str):
                        keys.add(modifier)
        return keys

    def _reward_catalog_ids(self) -> set[str]:
        try:
            catalog = load_yaml(REPO_ROOT / "data" / "cost_reward_units.yaml")
        except (OSError, TypeError, ValueError):
            return set()
        return {
            str(item["id"])
            for values in catalog.values()
            if isinstance(values, list)
            for item in values
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }

    @staticmethod
    def _modifier_schema_ids() -> set[str]:
        roots = (
            REPO_ROOT / ".eu5-base" / "reference_game_files" / "game" / "main_menu" / "common" / "modifier_type_definitions",
            REPO_ROOT / ".eu5-base" / "reference_mods_variants" / "eu5-towards-victory",
        )
        result: set[str] = set()
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*.txt"):
                try:
                    text = path.read_text(encoding="utf-8-sig", errors="ignore")
                except OSError:
                    continue
                result.update(re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)\s*=\s*\{", text))
        return result

    def _document_from_sources(self, paths_data: dict[str, Any], tasks_data: dict[str, Any]) -> dict[str, Any]:
        task_groups = tasks_data.get("paths", {})
        paths = []
        for path in paths_data.get("paths", []):
            path_id = path["id"]
            group = task_groups.get(path_id, {})
            merged = _copy(path)
            merged["tasks"] = {
                "label": _copy(group.get("label")),
                "color": _copy(group.get("color")),
                "items": [
                    {
                        "task_id": task.get("id"),
                        "source": {"path_id": path_id, "task_index": index},
                        "fields": {
                            key: _copy(value)
                            for key, value in task.items()
                            if key != "id"
                        },
                    }
                    for index, task in enumerate(group.get("tasks", []))
                ],
            }
            paths.append(merged)
        national = tasks_data.get("national_special", {})
        return {
            "shared": _copy(paths_data.get("shared")),
            "paths": paths,
            "on_actions": _copy(paths_data.get("on_actions")),
            "national_special": {
                "tasks": [
                    {
                        "task_id": task.get("id"),
                        "source": {"path_id": "national_special", "task_index": index},
                        "fields": {
                            key: _copy(value)
                            for key, value in task.items()
                            if key != "id"
                        },
                    }
                    for index, task in enumerate(national.get("tasks", []))
                ]
            },
        }

    @staticmethod
    def _task_group_from_view(value: Any, path_id: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError(f"paths[{path_id}].tasks must be an object")
        if set(value) - {"label", "color", "items"}:
            unknown = sorted(set(value) - {"label", "color", "items"})
            raise ValueError(f"Unknown task group field for {path_id}: {', '.join(unknown)}")
        items = value.get("items")
        if not isinstance(items, list):
            raise ValueError(f"paths[{path_id}].tasks.items must be a list")
        tasks = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"paths[{path_id}].tasks.items[{index}] must be an object")
            if set(item) - {"task_id", "source", "fields"}:
                unknown = sorted(set(item) - {"task_id", "source", "fields"})
                raise ValueError(f"Unknown task view field for {path_id}[{index}]: {', '.join(unknown)}")
            task_id = item.get("task_id")
            fields = item.get("fields")
            source = item.get("source")
            if not isinstance(task_id, int) or isinstance(task_id, bool):
                raise ValueError(f"paths[{path_id}].tasks.items[{index}].task_id must be an integer")
            if not isinstance(fields, dict):
                raise ValueError(f"paths[{path_id}].tasks.items[{index}].fields must be an object")
            if not isinstance(source, dict) or source.get("path_id") != path_id or source.get("task_index") != index:
                raise ValueError(f"paths[{path_id}].tasks.items[{index}].source is immutable")
            task = _copy(fields)
            task["id"] = task_id
            tasks.append(task)
        return {
            "label": _copy(value.get("label")),
            "color": _copy(value.get("color")),
            "tasks": tasks,
        }

    def _sources_from_document(self, document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        if not isinstance(document, dict):
            raise ValueError("document must be an object")
        required = {"shared", "paths", "on_actions", "national_special"}
        missing = sorted(required - set(document))
        unknown = sorted(set(document) - required)
        if missing:
            raise ValueError("document is missing: " + ", ".join(missing))
        if unknown:
            raise ValueError("Unknown document field: " + ", ".join(unknown))
        paths = document["paths"]
        if not isinstance(paths, list):
            raise ValueError("document.paths must be a list")
        path_sources = []
        task_sources: dict[str, Any] = {}
        for index, merged in enumerate(paths):
            if not isinstance(merged, dict):
                raise ValueError(f"document.paths[{index}] must be an object")
            if "id" not in merged:
                raise ValueError(f"document.paths[{index}] is missing id")
            path = {key: _copy(value) for key, value in merged.items() if key != "tasks"}
            if "tasks" not in merged:
                raise ValueError(f"document.paths[{index}] is missing tasks")
            task_sources[merged["id"]] = self._task_group_from_view(merged["tasks"], str(merged["id"]))
            path_sources.append(path)
        national = document["national_special"]
        if not isinstance(national, dict) or set(national) != {"tasks"}:
            raise ValueError("national_special must contain only tasks")
        national_group = self._task_group_from_view(
            {"label": None, "color": None, "items": national["tasks"]}, "national_special"
        )
        shared = _copy(document["shared"])
        labels = shared.get("milestone_labels") if isinstance(shared, dict) else None
        if isinstance(labels, dict):
            shared["milestone_labels"] = {
                int(key) if str(key) in {"1", "2", "3", "4", "5"} else key: value
                for key, value in labels.items()
            }
        return (
            {"shared": shared, "paths": path_sources, "on_actions": _copy(document["on_actions"])},
            {"version": self.tasks_data.get("version"), "paths": task_sources, "national_special": {"tasks": national_group["tasks"]}},
        )

    @staticmethod
    def _validate_bilingual(value: Any, path: str, errors: list[dict[str, str]]) -> None:
        keys = {str(key) for key in value} if isinstance(value, dict) else set()
        if keys != {"en", "zh"}:
            errors.append(_error("bilingual_required", path, "A complete en/zh mapping is required."))
            return
        if not all(isinstance(value.get(lang), str) for lang in ("en", "zh")):
            errors.append(_error("invalid_text", path, "English and Chinese values must be strings."))

    @classmethod
    def _validate_localized_value(cls, value: Any, path: str, errors: list[dict[str, str]]) -> None:
        if not isinstance(value, dict):
            errors.append(_error("bilingual_required", path, "A complete en/zh mapping is required."))
            return
        keys = {str(key) for key in value}
        if keys == {"en", "zh"}:
            cls._validate_bilingual(value, path, errors)
            return
        for key, child in value.items():
            cls._validate_localized_value(child, f"{path}.{key}", errors)

    def _validate_documents(
        self,
        paths_data: dict[str, Any],
        tasks_data: dict[str, Any],
        *,
        check_references: bool = True,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        errors: list[dict[str, str]] = []
        warnings: list[dict[str, str]] = []
        if not isinstance(paths_data, dict):
            return [_error("invalid_document", "victory_paths", "The victory paths source must be a mapping.")], warnings
        if set(paths_data) != {"shared", "paths", "on_actions"}:
            errors.append(_error("unknown_field", "victory_paths", "Top-level fields must be shared, paths and on_actions."))
        shared = paths_data.get("shared")
        if not isinstance(shared, dict):
            errors.append(_error("required_field", "shared", "shared must be a mapping."))
        else:
            expected_shared = {
                "situation_name",
                "situation_desc",
                "situation_title",
                "tooltip_conditions_header",
                "tooltip_rewards_header",
                "milestone_labels",
            }
            if set(shared) != expected_shared:
                errors.append(_error("unknown_field", "shared", "shared fields do not match the current schema."))
            for key in expected_shared - {"milestone_labels"}:
                if key in shared:
                    self._validate_bilingual(shared[key], f"shared.{key}", errors)
            labels = shared.get("milestone_labels")
            label_keys = {str(key) for key in labels} if isinstance(labels, dict) else set()
            if not isinstance(labels, dict) or label_keys != {"1", "2", "3", "4", "5"}:
                errors.append(_error("invalid_milestone_labels", "shared.milestone_labels", "Labels for 1..5 are required."))
            elif not all(isinstance(value, str) for value in labels.values()):
                errors.append(_error("invalid_text", "shared.milestone_labels", "Milestone labels must be strings."))

        paths = paths_data.get("paths")
        if not isinstance(paths, list):
            errors.append(_error("required_field", "paths", "paths must be a list."))
            paths = []
        path_ids: list[str] = []
        for index, path in enumerate(paths):
            prefix = f"paths[{index}]"
            if not isinstance(path, dict):
                errors.append(_error("invalid_path", prefix, "Each path must be a mapping."))
                continue
            unknown = sorted(set(path) - PATH_FIELDS)
            if unknown:
                errors.append(_error("unknown_field", prefix, "Unknown fields: " + ", ".join(unknown)))
            path_id = path.get("id")
            if not isinstance(path_id, str) or not _PATH_ID_RE.fullmatch(path_id):
                errors.append(_error("invalid_path_id", f"{prefix}.id", "Path id must match [a-z][a-z0-9_]*."))
            elif path_id in path_ids:
                errors.append(_error("duplicate_path_id", f"{prefix}.id", "Path ids must be unique."))
            else:
                path_ids.append(path_id)
            for required in ("id", "score_var", "gui", "call_updater_in_checker", "score_var_init_in_checker", "loc", "milestones"):
                if required not in path:
                    errors.append(_error("required_field", f"{prefix}.{required}", "Required field is missing."))
            for bool_key in ("call_updater_in_checker", "call_updater_on_situation_start", "score_var_init_in_checker"):
                if bool_key in path and path[bool_key] is not None and not _is_bool(path[bool_key]) and path[bool_key] != "player_only":
                    errors.append(_error("invalid_boolean", f"{prefix}.{bool_key}", "Value must be true or false."))
            gui = path.get("gui")
            if isinstance(gui, dict):
                if set(gui) != GUI_FIELDS:
                    errors.append(_error("unknown_field", f"{prefix}.gui", "GUI fields do not match the current schema."))
                if not isinstance(gui.get("order"), int) or isinstance(gui.get("order"), bool) or gui.get("order", -1) < 0:
                    errors.append(_error("invalid_order", f"{prefix}.gui.order", "Order must be a non-negative integer."))
                self._validate_bilingual(gui.get("tab_label"), f"{prefix}.gui.tab_label", errors)
                for key in ("icon", "progress_style"):
                    if not isinstance(gui.get(key), str) or not gui.get(key):
                        errors.append(_error("invalid_text", f"{prefix}.gui.{key}", "Value must be a non-empty string."))
            loc = path.get("loc")
            if not isinstance(loc, dict):
                errors.append(_error("required_field", f"{prefix}.loc", "Path localization must be a mapping."))
            else:
                for key, value in loc.items():
                    self._validate_localized_value(value, f"{prefix}.loc.{key}", errors)
            milestones = path.get("milestones")
            if not isinstance(milestones, list) or len(milestones) != 5:
                errors.append(_error("invalid_milestones", f"{prefix}.milestones", "Exactly five milestones are required."))
                milestones = milestones if isinstance(milestones, list) else []
            seen_n: list[int] = []
            for milestone_index, milestone in enumerate(milestones):
                mpath = f"{prefix}.milestones[{milestone_index}]"
                if not isinstance(milestone, dict):
                    errors.append(_error("invalid_milestone", mpath, "Milestone must be a mapping."))
                    continue
                unknown_m = sorted(set(milestone) - MILESTONE_FIELDS)
                if unknown_m:
                    errors.append(_error("unknown_field", mpath, "Unknown fields: " + ", ".join(unknown_m)))
                number = milestone.get("n")
                if not isinstance(number, int) or isinstance(number, bool) or number not in range(1, 6) or number in seen_n:
                    errors.append(_error("invalid_milestone_number", f"{mpath}.n", "Milestone n must be unique and in 1..5."))
                else:
                    seen_n.append(number)
                for bool_key in ("is_short_term", "is_long_term"):
                    if not _is_bool(milestone.get(bool_key)):
                        errors.append(_error("invalid_boolean", f"{mpath}.{bool_key}", "Value must be true or false."))
                if milestone.get("is_short_term") and milestone.get("is_long_term"):
                    errors.append(_error("invalid_milestone_flags", mpath, "A milestone cannot be both short-term and long-term."))
                if not _is_number(milestone.get("threshold")) or milestone.get("threshold", -1) < 0:
                    errors.append(_error("invalid_threshold", f"{mpath}.threshold", "Threshold must be a non-negative number."))
                options = milestone.get("reward_options")
                if not isinstance(options, list) or len(options) != 3:
                    errors.append(_error("invalid_reward_options", f"{mpath}.reward_options", "Exactly three reward options are required."))
                    options = options if isinstance(options, list) else []
                for option_index, option in enumerate(options):
                    opath = f"{mpath}.reward_options[{option_index}]"
                    if not isinstance(option, dict) or set(option) != {"modifier"}:
                        errors.append(_error("invalid_reward_option", opath, "Reward option must contain modifier only."))
                        continue
                    modifier = option["modifier"]
                    if not isinstance(modifier, (dict, str)) or isinstance(modifier, dict) and not modifier:
                        errors.append(_error("invalid_reward_modifier", f"{opath}.modifier", "Modifier must be a non-empty mapping or key."))
                    if isinstance(modifier, dict):
                        for key, value in modifier.items():
                            if not isinstance(key, str) or not _is_number(value):
                                errors.append(_error("invalid_reward_modifier", f"{opath}.modifier", "Modifier keys and values are invalid."))
                for key in ("loc",):
                    value = milestone.get(key)
                    if not isinstance(value, dict):
                        errors.append(_error("required_field", f"{mpath}.{key}", "Localization must be a mapping."))
                    else:
                        for loc_key, loc_value in value.items():
                            self._validate_localized_value(loc_value, f"{mpath}.{key}.{loc_key}", errors)
                for body_key in ("extra_trigger_block", "unlock_body"):
                    if milestone.get(body_key) is not None and not isinstance(milestone.get(body_key), str):
                        errors.append(_error("invalid_script_body", f"{mpath}.{body_key}", "Script body must be text or null."))
            if seen_n and sorted(seen_n) != [1, 2, 3, 4, 5]:
                errors.append(_error("invalid_milestone_sequence", f"{prefix}.milestones", "Milestones must be numbered 1..5."))

        tasks_paths = tasks_data.get("paths") if isinstance(tasks_data, dict) else None
        if not isinstance(tasks_data, dict) or set(tasks_data) != {"version", "paths", "national_special"}:
            errors.append(_error("unknown_field", "victory_path_tasks", "Top-level fields must be version, paths and national_special."))
        if not isinstance(tasks_data.get("version"), int) or isinstance(tasks_data.get("version"), bool):
            errors.append(_error("invalid_version", "victory_path_tasks.version", "Version must be an integer."))
        if not isinstance(tasks_paths, dict):
            errors.append(_error("required_field", "victory_path_tasks.paths", "Task paths must be a mapping."))
            tasks_paths = {}
        if set(tasks_paths) != set(path_ids):
            errors.append(_error("path_pairing", "victory_path_tasks.paths", "Task path ids must match victory path ids exactly."))
        all_task_ids: set[int] = set()
        for path_id, group in tasks_paths.items():
            prefix = f"tasks.paths.{path_id}"
            if not isinstance(group, dict) or set(group) != TASK_GROUP_FIELDS:
                errors.append(_error("invalid_task_group", prefix, "Task group fields must be label, color and tasks."))
                continue
            self._validate_bilingual(group.get("label"), f"{prefix}.label", errors)
            color = group.get("color")
            if not isinstance(color, dict) or set(color) != {"r", "g", "b"} or not all(_is_number(color.get(channel)) and 0 <= color[channel] <= 1 for channel in ("r", "g", "b")):
                errors.append(_error("invalid_color", f"{prefix}.color", "Color must contain numeric r/g/b values in 0..1."))
            task_list = group.get("tasks")
            if not isinstance(task_list, list):
                errors.append(_error("invalid_tasks", f"{prefix}.tasks", "Tasks must be a list."))
                continue
            for task_index, task in enumerate(task_list):
                tpath = f"{prefix}.tasks[{task_index}]"
                if not isinstance(task, dict):
                    errors.append(_error("invalid_task", tpath, "Task must be a mapping."))
                    continue
                unknown_task = sorted(set(task) - _TASK_FIELDS)
                if unknown_task:
                    errors.append(_error("unknown_field", tpath, "Unknown fields: " + ", ".join(unknown_task)))
                task_id = task.get("id")
                if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id in all_task_ids:
                    errors.append(_error("invalid_task_id", f"{tpath}.id", "Task ids must be unique integers."))
                else:
                    all_task_ids.add(task_id)
                if not isinstance(task.get("key"), str) or not task.get("key"):
                    errors.append(_error("invalid_task_key", f"{tpath}.key", "Task key must be a non-empty string."))
                if task.get("type") not in {"fixed", "target"}:
                    errors.append(_error("invalid_task_type", f"{tpath}.type", "Task type must be fixed or target."))
                if task.get("type") == "fixed":
                    thresholds = task.get("thresholds")
                    if not isinstance(thresholds, list) or not thresholds or any(not _is_number(value) for value in thresholds) or any(a >= b for a, b in zip(thresholds, thresholds[1:])):
                        errors.append(_error("invalid_task_thresholds", f"{tpath}.thresholds", "Fixed task thresholds must increase."))
                if not _is_bool(task.get("custom_tooltip")):
                    errors.append(_error("invalid_boolean", f"{tpath}.custom_tooltip", "Value must be true or false."))
                for key in ("loc", "requirement"):
                    self._validate_bilingual(task.get(key), f"{tpath}.{key}", errors)
        national = tasks_data.get("national_special") if isinstance(tasks_data, dict) else None
        if not isinstance(national, dict) or set(national) != {"tasks"} or not isinstance(national.get("tasks"), list):
            errors.append(_error("invalid_national_special", "national_special.tasks", "National special tasks must be a list."))

        if check_references:
            catalog_ids = self._reward_catalog_ids() | self._modifier_schema_ids()
            for modifier in self._modifier_keys(paths_data):
                if modifier not in catalog_ids and modifier not in self._known_victory_modifiers:
                    errors.append(_error("invalid_reward_reference", "reward_options.modifier", f"Unknown reward modifier reference: {modifier}."))
        return errors, warnings

    def _references(self, paths_data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        catalog_ids = self._reward_catalog_ids() | self._modifier_schema_ids()
        seen: set[str] = set()
        rewards = []
        for key in self._modifier_keys(paths_data):
            if key in seen:
                continue
            seen.add(key)
            resolved = key in catalog_ids or key in self._known_victory_modifiers
            rewards.append(
                {
                    "key": key,
                    "resolved": resolved,
                    "source_resource": "editor.cost_reward" if key in self._reward_catalog_ids() else "game_modifier_schema",
                    "editable": False,
                    "editable_here": False,
                }
            )
        return {"rewards": rewards, "tasks": []}

    def _generation_plan(self, *, source_changed: bool) -> dict[str, Any]:
        errors: list[dict[str, str]] = []
        try:
            generators = self.generator_service.generators()
        except Exception as exc:  # noqa: BLE001
            errors.append(_error("generation_registry_incomplete", "generation", str(exc)))
            generators = []
        selected = []
        sources = set(SOURCE_RELS)
        for generator in generators:
            inputs = {_normalise_path(str(value)) for value in generator.get("data_inputs", [])}
            if sources.intersection(inputs):
                selected.append(generator)
        owners: dict[str, str] = {}
        outputs: set[str] = set()
        for generator in selected:
            script = generator.get("script")
            declared = generator.get("outputs")
            if not isinstance(script, str) or not script:
                errors.append(_error("generation_registry_incomplete", "generation", "A matched generator is missing script."))
                continue
            if not isinstance(declared, list) or not declared:
                errors.append(_error("generation_registry_incomplete", script, "A matched generator has no outputs."))
                continue
            for output in declared:
                output = _normalise_path(str(output))
                if output in owners and owners[output] != script:
                    errors.append(_error("generation_output_conflict", output, f"Output is declared by both {owners[output]} and {script}."))
                owners[output] = script
                outputs.add(output)
        if source_changed and not selected:
            errors.append(_error("generation_registry_incomplete", "generation", "No registered generator declares a victory path source."))
        registry_complete = not errors
        return {
            "required": bool(source_changed and selected),
            "registry_complete": registry_complete,
            "generators": [generator["script"] for generator in selected if isinstance(generator.get("script"), str)],
            "outputs": sorted(outputs),
            "steps": [
                {"script": generator["script"], "outputs": sorted(generator.get("outputs", []))}
                for generator in selected
                if isinstance(generator.get("script"), str)
            ],
            "errors": errors,
        }

    def _registry_plan_is_complete(self, plan: dict[str, Any]) -> bool:
        return bool(plan["registry_complete"] and plan["generators"] and plan["outputs"])

    def _payload(self, *, generation: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "resource_id": RESOURCE_ID,
            "schema_version": SCHEMA_VERSION,
            "sources": _source_payload(self._base),
            "document": self._document_from_sources(self.paths_data, self.tasks_data),
            "references": self._references(self.paths_data),
            "generation": generation or self._generation_plan(source_changed=False),
            "read_only_outputs": True,
            "constraints": {
                "yaml_write_boundary": "Preserves BOM, leading comment block and newline style; body comments are not retained and key order is not guaranteed for untouched keys.",
                "task_catalogue": "Source tasks are a catalogue; the generated runtime assigns them to three slots and no synthetic slot field is written back.",
            },
        }

    def load_resource(self) -> dict[str, Any]:
        with self._lock:
            self.reload_from_disk()
            return self._payload()

    def _prepare(self, document: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, str]], list[dict[str, str]]]:
        candidate_paths, candidate_tasks = self._sources_from_document(document)
        errors, warnings = self._validate_documents(candidate_paths, candidate_tasks)
        return candidate_paths, candidate_tasks, errors, warnings

    def _base_assert(self, base: dict[str, Any]) -> None:
        current = snapshot_files((PATHS_FILE, TASKS_FILE), repo_root=REPO_ROOT)
        assert_resource_base(_source_base(base), self._base, current)

    def _candidate_report(self, document: dict[str, Any]) -> dict[str, Any]:
        candidate_paths, candidate_tasks, errors, warnings = self._prepare(document)
        source_changed = candidate_paths != self.paths_data or candidate_tasks != self.tasks_data
        generation = self._generation_plan(source_changed=source_changed)
        errors = [*errors, *generation["errors"]]
        return {
            "candidate_paths": candidate_paths,
            "candidate_tasks": candidate_tasks,
            "source_changed": source_changed,
            "errors": errors,
            "warnings": warnings,
            "generation": generation,
            "document": document,
        }

    def validate_document(self, document: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            report = self._candidate_report(document)
            return {
                "resource_id": RESOURCE_ID,
                "valid": not report["errors"],
                "errors": report["errors"],
                "warnings": report["warnings"],
                "written_paths": SOURCE_RELS if report["source_changed"] else [],
                "references": self._references(report["candidate_paths"]),
                "generation": report["generation"],
            }

    def preview_document(self, document: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self._base_assert(base)
            report = self._candidate_report(document)
            candidate_bytes = {
                PATHS_FILE: yaml_bytes(PATHS_FILE, report["candidate_paths"]),
                TASKS_FILE: yaml_bytes(TASKS_FILE, report["candidate_tasks"]),
            }
            current_bytes = {PATHS_FILE: PATHS_FILE.read_bytes(), TASKS_FILE: TASKS_FILE.read_bytes()}
            after_snapshots = snapshot_files((PATHS_FILE, TASKS_FILE), repo_root=REPO_ROOT)
            diff: list[dict[str, Any]] = []
            _diff_values(self.paths_data, report["candidate_paths"], "", diff, PATHS_REL)
            _diff_values(self.tasks_data, report["candidate_tasks"], "", diff, TASKS_REL)
            source_diffs = []
            for path, rel in ((PATHS_FILE, PATHS_REL), (TASKS_FILE, TASKS_REL)):
                before = current_bytes[path]
                after = candidate_bytes[path]
                source_diffs.append(
                    {
                        "path": rel,
                        "changed": before != after,
                        "before_sha256": next(item.sha256 for item in after_snapshots if item.path == rel),
                        "after_sha256": hashlib.sha256(after).hexdigest(),
                    }
                )
            generation = report["generation"]
            return {
                "resource_id": RESOURCE_ID,
                "ready": not report["errors"],
                "validation": {"errors": report["errors"], "warnings": report["warnings"]},
                "diff": {"sources": source_diffs, "fields": diff},
                "written_paths": [item["path"] for item in source_diffs if item["changed"]],
                "references": self._references(report["candidate_paths"]),
                "generation": generation,
            }

    def commit_document(self, document: dict[str, Any], base: dict[str, Any], message: str | None = None) -> dict[str, Any]:
        with self._lock:
            self._base_assert(base)
            report = self._candidate_report(document)
            if report["errors"]:
                raise ValueError("Victory paths validation failed: " + "; ".join(item["message"] for item in report["errors"]))
            candidate_bytes = {
                PATHS_FILE: yaml_bytes(PATHS_FILE, report["candidate_paths"]),
                TASKS_FILE: yaml_bytes(TASKS_FILE, report["candidate_tasks"]),
            }
            current_bytes = {PATHS_FILE: PATHS_FILE.read_bytes(), TASKS_FILE: TASKS_FILE.read_bytes()}
            source_files = {path: content for path, content in candidate_bytes.items() if content != current_bytes[path]}
            details: dict[str, Any] = {
                "resource_id": RESOURCE_ID,
                "written_paths": [],
                "generation": {
                    "status": "not_required",
                    "generators": report["generation"]["generators"],
                    "outputs": report["generation"]["outputs"],
                    "artifacts": [],
                },
                "rollback": {"status": "not_needed", "errors": []},
            }
            operation = OperationLog(
                "resource_commit", (RESOURCE_ID,), store=self.operation_store,
                snapshot_details=lambda: copy.deepcopy(details),
            )

            def execute() -> dict[str, Any]:
                try:
                    outputs = tuple(REPO_ROOT / output for output in report["generation"]["outputs"])
                    with file_transaction((*source_files, *outputs), reload=self.reload_from_disk):
                        atomic_write_files(source_files)
                        if report["generation"]["required"]:
                            generation_result = self.generator_service.run(report["generation"]["generators"])
                            details["generation"] = {
                                "status": "succeeded",
                                "generators": report["generation"]["generators"],
                                "outputs": report["generation"]["outputs"],
                                "artifacts": generation_result.get("artifacts", []),
                            }
                        self.reload_from_disk()
                except Exception as exc:
                    details["rollback"] = {
                        "status": "failed" if getattr(exc, "errors", None) else "completed",
                        "errors": list(getattr(exc, "errors", [])),
                    }
                    raise
                details["written_paths"] = [path.relative_to(REPO_ROOT).as_posix() for path in source_files]
                details["written_paths"].extend(
                    artifact["path"] for artifact in details["generation"]["artifacts"] if artifact["changed"]
                )
                details["written_paths"] = list(dict.fromkeys(details["written_paths"]))
                return self._payload(generation=report["generation"]) | {
                    "operation_id": operation.id,
                    "status": "succeeded",
                    "written_paths": details["written_paths"],
                    "generation": details["generation"],
                    "rollback": details["rollback"],
                    "base": {"sources": _source_payload(self._base)},
                    "message": message,
                }

            try:
                result = run_operation(operation, execute)
            except Exception as exc:
                if hasattr(exc, "report") and isinstance(exc.report, dict):
                    exc.report["resource_id"] = RESOURCE_ID
                    exc.report["written_paths"] = details["written_paths"]
                    exc.report["rollback"] = details["rollback"]
                raise
            return {**result, "operation": operation.payload()}
