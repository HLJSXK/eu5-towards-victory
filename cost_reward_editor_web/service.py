from __future__ import annotations

import sys
import threading
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.wonder_mechanics.io import REPO_ROOT, load_yaml, save_yaml_document

DATA_FILE = REPO_ROOT / "data" / "cost_reward_units.yaml"
DATA_REL = "data/cost_reward_units.yaml"

# The five foundational categories this catalog is organized into. Each is its own top-level
# YAML list, independent of any single mechanic's data (see the file's own header comment).
# The first three are one-shot units (magnitude only, always positive) — there is no separate
# "cost" category: a cost is simply the negative of the matching reward value, applied by
# whichever system consumes it. The last two are persistent per-level modifier units: real EU5
# modifier keys extracted from the wonder system's own data, which can legitimately be negative
# (e.g. a cost-reduction modifier is beneficial as a negative number).
CATEGORY_DEFS = (
    {"key": "country_reward", "label_en": "Country-level Reward", "label_zh": "国家级奖励"},
    {"key": "local_reward", "label_en": "Local-level Reward", "label_zh": "本地级奖励"},
    {"key": "character_reward", "label_en": "Character-level Reward", "label_zh": "角色级奖励"},
    {"key": "country_modifier", "label_en": "Country-level Modifier (per level)", "label_zh": "国家级 Modifier（每级）"},
    {"key": "local_modifier", "label_en": "Local-level Modifier (per level)", "label_zh": "本地级 Modifier（每级）"},
)
CATEGORY_KEYS = tuple(category["key"] for category in CATEGORY_DEFS)
MODIFIER_CATEGORY_KEYS = ("country_modifier", "local_modifier")


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


class CostRewardEditorService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._log_lines: list[str] = []
        self.data: dict = load_yaml(DATA_FILE)

    def reload_from_disk(self) -> None:
        self.data = load_yaml(DATA_FILE)

    def _append_log(self, text: str) -> None:
        self._log_lines.append(text)
        del self._log_lines[:-4000]

    def bootstrap_payload(self) -> dict:
        groups = []
        for category in CATEGORY_DEFS:
            tokens = [dict(token) for token in self.data.get(category["key"], [])]
            groups.append({**category, "tokens": tokens})
        return {
            "groups": groups,
            "log": "".join(self._log_lines[-200:]),
        }

    def save_tokens(self, edits: dict[str, dict[str, dict[str, Any]]]) -> dict:
        with self._lock:
            for category_key in CATEGORY_KEYS:
                category_edits = edits.get(category_key) or {}
                if not category_edits:
                    continue
                tokens = self.data.get(category_key, [])
                by_id = {token["id"]: token for token in tokens}
                for token_id, fields in category_edits.items():
                    if token_id not in by_id:
                        raise KeyError(f"Unknown unit id in {category_key}: {token_id}")
                    token = by_id[token_id]
                    if "value" in fields:
                        value = _parse_scalar(fields["value"])
                        if value == 0:
                            raise ValueError(f"{category_key}.{token_id}.value must not be zero")
                        if category_key not in MODIFIER_CATEGORY_KEYS and value <= 0:
                            raise ValueError(f"{category_key}.{token_id}.value must be a positive number")
                        token["value"] = value

            save_yaml_document(DATA_FILE, self.data, preserve_leading_comments=True)
            self._append_log(f"[save] Wrote {DATA_REL}\n")

            self.reload_from_disk()
            return self.bootstrap_payload()


def build_check_report() -> list[str]:
    try:
        data = load_yaml(DATA_FILE)
    except Exception as exc:  # noqa: BLE001
        return [f"[FAIL] Could not load {DATA_REL}: {exc}"]

    lines: list[str] = []
    total = 0
    for category_key in CATEGORY_KEYS:
        for token in data.get(category_key, []):
            total += 1
            token_id = token.get("id", "?")
            value = token.get("value")
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value == 0:
                lines.append(f"[FAIL] {category_key}.{token_id}: value must be a nonzero number, got {value!r}")
            elif category_key not in MODIFIER_CATEGORY_KEYS and value <= 0:
                lines.append(f"[FAIL] {category_key}.{token_id}: value must be a positive number, got {value!r}")

    if not lines:
        lines.append(f"[OK] {DATA_REL}: {total} units validated across {len(CATEGORY_KEYS)} categories.")
    return lines
