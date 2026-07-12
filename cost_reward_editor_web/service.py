from __future__ import annotations

import sys
import threading
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.wonder_mechanics.io import REPO_ROOT, load_yaml, save_yaml_document

DATA_FILE = REPO_ROOT / "data" / "cost_reward_units.yaml"
DATA_REL = "data/cost_reward_units.yaml"

TASK_POOL_FILE = REPO_ROOT / "data" / "task_pool.yaml"
TASK_POOL_REL = "data/task_pool.yaml"

# The five foundational categories this catalog is organized into. Each is its own top-level
# YAML list, independent of any single mechanic's data (see the file's own header comment).
# The first three are one-shot units (magnitude only, always positive) — there is no separate
# "cost" category: a cost is simply the negative of the matching reward value, applied by
# whichever system consumes it. The last two are persistent modifier units: numeric entries are
# per-level values and country_modifier may also contain unscaled boolean unlocks. Numeric values
# can legitimately be negative (e.g. a cost-reduction modifier is beneficial as a negative number).
CATEGORY_DEFS = (
    {"key": "country_reward", "label_en": "Country-level Reward", "label_zh": "国家级奖励"},
    {"key": "local_reward", "label_en": "Local-level Reward", "label_zh": "本地级奖励"},
    {"key": "character_reward", "label_en": "Character-level Reward", "label_zh": "角色级奖励"},
    {"key": "country_modifier", "label_en": "Country-level Modifier / Unlock", "label_zh": "国家级 Modifier / 解锁"},
    {"key": "local_modifier", "label_en": "Local-level Modifier (per level)", "label_zh": "本地级 Modifier（每级）"},
)
CATEGORY_KEYS = tuple(category["key"] for category in CATEGORY_DEFS)
MODIFIER_CATEGORY_KEYS = ("country_modifier", "local_modifier")

# The two task-pool families (see docs/design/Cost_Reward_Unit_Concepts.md section 6). Neither
# stores a reward; each stores only what must happen / what must be reached and how the engine
# detects it. Sibling catalog to cost_reward_units.yaml, same independence convention, own file.
TASK_CATEGORY_DEFS = (
    {"key": "on_action_task", "label_en": "On_action Task", "label_zh": "on_action 型任务"},
    {"key": "trigger_task", "label_en": "Trigger Task", "label_zh": "Trigger 型任务"},
)
TASK_CATEGORY_KEYS = tuple(category["key"] for category in TASK_CATEGORY_DEFS)
TRIGGER_COMPARISONS = ("gte", "lte", "boolean")


def _parse_scalar(raw: Any) -> float:
    if isinstance(raw, bool):
        raise ValueError(f"Not a number: {raw!r}")
    if isinstance(raw, (int, float)):
        return raw
    text = str(raw).strip()
    try:
        value = float(text)
    except ValueError as exc:
        raise ValueError(f"Not a number: {raw!r}") from exc
    if value.is_integer():
        return int(value)
    return value


def _parse_bool(raw: Any) -> bool:
    if isinstance(raw, bool):
        return raw
    text = str(raw).strip().lower()
    if text in {"true", "1", "yes", "on"}:
        return True
    if text in {"false", "0", "no", "off", ""}:
        return False
    raise ValueError(f"Not a boolean: {raw!r}")


class CostRewardEditorService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._log_lines: list[str] = []
        self.data: dict = load_yaml(DATA_FILE)
        self.task_data: dict = load_yaml(TASK_POOL_FILE)

    def reload_from_disk(self) -> None:
        self.data = load_yaml(DATA_FILE)
        self.task_data = load_yaml(TASK_POOL_FILE)

    def _append_log(self, text: str) -> None:
        self._log_lines.append(text)
        del self._log_lines[:-4000]

    def bootstrap_payload(self) -> dict:
        groups = []
        for category in CATEGORY_DEFS:
            tokens = [dict(token) for token in self.data.get(category["key"], [])]
            groups.append({**category, "tokens": tokens})
        for category in TASK_CATEGORY_DEFS:
            tokens = [dict(token) for token in self.task_data.get(category["key"], [])]
            groups.append({**category, "tokens": tokens})
        return {
            "groups": groups,
            "log": "".join(self._log_lines[-200:]),
        }

    def _apply_reward_modifier_edits(self, category_key: str, edits: dict[str, dict[str, Any]]) -> None:
        tokens = self.data.get(category_key, [])
        by_id = {token["id"]: token for token in tokens}
        for token_id, fields in edits.items():
            if token_id not in by_id:
                raise KeyError(f"Unknown unit id in {category_key}: {token_id}")
            token = by_id[token_id]
            if "value" in fields:
                if isinstance(token.get("value"), bool):
                    if category_key != "country_modifier":
                        raise ValueError(f"{category_key}.{token_id}.value cannot be a boolean unlock")
                    value = _parse_bool(fields["value"])
                else:
                    value = _parse_scalar(fields["value"])
                    if value == 0:
                        raise ValueError(f"{category_key}.{token_id}.value must not be zero")
                    if category_key not in MODIFIER_CATEGORY_KEYS and value <= 0:
                        raise ValueError(f"{category_key}.{token_id}.value must be a positive number")
                token["value"] = value

    def _apply_on_action_task_edits(self, edits: dict[str, dict[str, Any]]) -> None:
        tokens = self.task_data.get("on_action_task", [])
        by_id = {token["id"]: token for token in tokens}
        for token_id, fields in edits.items():
            if token_id not in by_id:
                raise KeyError(f"Unknown task id in on_action_task: {token_id}")
            token = by_id[token_id]
            if "wired" in fields:
                token["wired"] = _parse_bool(fields["wired"])
            if "completion_note" in fields:
                note = str(fields["completion_note"]).strip()
                if not note:
                    raise ValueError(f"on_action_task.{token_id}.completion_note must not be empty")
                token["completion_note"] = note

    def _apply_trigger_task_edits(self, edits: dict[str, dict[str, Any]]) -> None:
        tokens = self.task_data.get("trigger_task", [])
        by_id = {token["id"]: token for token in tokens}
        for token_id, fields in edits.items():
            if token_id not in by_id:
                raise KeyError(f"Unknown task id in trigger_task: {token_id}")
            token = by_id[token_id]
            if "comparison" in fields:
                comparison = str(fields["comparison"]).strip()
                if comparison not in TRIGGER_COMPARISONS:
                    raise ValueError(
                        f"trigger_task.{token_id}.comparison must be one of {', '.join(TRIGGER_COMPARISONS)}"
                    )
                token["comparison"] = comparison
            if "representative_threshold" in fields:
                raw = fields["representative_threshold"]
                if raw is None or (isinstance(raw, str) and raw.strip() == ""):
                    token["representative_threshold"] = None
                else:
                    token["representative_threshold"] = _parse_scalar(raw)

            is_boolean = token.get("comparison") == "boolean"
            has_threshold = token.get("representative_threshold") is not None
            if is_boolean and has_threshold:
                raise ValueError(
                    f"trigger_task.{token_id}: representative_threshold must be null when comparison is boolean"
                )
            if not is_boolean and not has_threshold:
                raise ValueError(
                    f"trigger_task.{token_id}: representative_threshold is required unless comparison is boolean"
                )

    def save_tokens(self, edits: dict[str, dict[str, dict[str, Any]]]) -> dict:
        with self._lock:
            touched_cost_reward = False
            touched_task_pool = False

            for category_key in CATEGORY_KEYS:
                category_edits = edits.get(category_key) or {}
                if not category_edits:
                    continue
                self._apply_reward_modifier_edits(category_key, category_edits)
                touched_cost_reward = True

            on_action_edits = edits.get("on_action_task") or {}
            if on_action_edits:
                self._apply_on_action_task_edits(on_action_edits)
                touched_task_pool = True

            trigger_edits = edits.get("trigger_task") or {}
            if trigger_edits:
                self._apply_trigger_task_edits(trigger_edits)
                touched_task_pool = True

            if touched_cost_reward:
                save_yaml_document(DATA_FILE, self.data, preserve_leading_comments=True)
                self._append_log(f"[save] Wrote {DATA_REL}\n")
            if touched_task_pool:
                save_yaml_document(TASK_POOL_FILE, self.task_data, preserve_leading_comments=True)
                self._append_log(f"[save] Wrote {TASK_POOL_REL}\n")

            self.reload_from_disk()
            return self.bootstrap_payload()


def _check_cost_reward(data: dict) -> list[str]:
    lines: list[str] = []
    total = 0
    for category_key in CATEGORY_KEYS:
        for token in data.get(category_key, []):
            total += 1
            token_id = token.get("id", "?")
            value = token.get("value")
            if isinstance(value, bool):
                if category_key != "country_modifier":
                    lines.append(f"[FAIL] {category_key}.{token_id}: boolean unlocks are only valid for country_modifier")
                continue
            if not isinstance(value, (int, float)) or value == 0:
                lines.append(f"[FAIL] {category_key}.{token_id}: value must be a nonzero number, got {value!r}")
            elif category_key not in MODIFIER_CATEGORY_KEYS and value <= 0:
                lines.append(f"[FAIL] {category_key}.{token_id}: value must be a positive number, got {value!r}")

    if not lines:
        lines.append(f"[OK] {DATA_REL}: {total} units validated across {len(CATEGORY_KEYS)} categories.")
    return lines


def _check_task_pool(data: dict) -> list[str]:
    lines: list[str] = []
    total = 0

    for token in data.get("on_action_task", []):
        total += 1
        token_id = token.get("id", "?")
        if not isinstance(token.get("wired"), bool):
            lines.append(f"[FAIL] on_action_task.{token_id}: wired must be a boolean, got {token.get('wired')!r}")
        note = token.get("completion_note")
        if not isinstance(note, str) or not note.strip():
            lines.append(f"[FAIL] on_action_task.{token_id}: completion_note must be a non-empty string")

    for token in data.get("trigger_task", []):
        total += 1
        token_id = token.get("id", "?")
        comparison = token.get("comparison")
        threshold = token.get("representative_threshold")
        if comparison not in TRIGGER_COMPARISONS:
            lines.append(
                f"[FAIL] trigger_task.{token_id}: comparison must be one of {', '.join(TRIGGER_COMPARISONS)}, "
                f"got {comparison!r}"
            )
            continue
        is_boolean = comparison == "boolean"
        has_threshold = threshold is not None
        if is_boolean and has_threshold:
            lines.append(f"[FAIL] trigger_task.{token_id}: representative_threshold must be null when comparison is boolean")
        if not is_boolean and not has_threshold:
            lines.append(f"[FAIL] trigger_task.{token_id}: representative_threshold is required unless comparison is boolean")

    if not lines:
        lines.append(f"[OK] {TASK_POOL_REL}: {total} tasks validated across {len(TASK_CATEGORY_KEYS)} categories.")
    return lines


def build_check_report() -> list[str]:
    lines: list[str] = []

    try:
        data = load_yaml(DATA_FILE)
    except Exception as exc:  # noqa: BLE001
        lines.append(f"[FAIL] Could not load {DATA_REL}: {exc}")
    else:
        lines.extend(_check_cost_reward(data))

    try:
        task_data = load_yaml(TASK_POOL_FILE)
    except Exception as exc:  # noqa: BLE001
        lines.append(f"[FAIL] Could not load {TASK_POOL_REL}: {exc}")
    else:
        lines.extend(_check_task_pool(task_data))

    return lines
