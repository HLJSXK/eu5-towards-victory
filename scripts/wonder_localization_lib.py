import ast
import re
import sys
from pathlib import Path

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
WONDER_LOCALIZATION_FILE = REPO_ROOT / "data" / "wonder_localization.yaml"
ENGINEERING_DEPARTMENT_EVENTS_FILE = REPO_ROOT / "src" / "in_game" / "events" / "tv_engineering_department_events.txt"
LANGUAGES = ("english", "simp_chinese")

LOCALIZATION_LINE_RE = re.compile(r'^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.-]+):(?P<version>0)?\s+(?P<value>"(?:[^"\\]|\\.)*")\s*$')
ENGINEERING_DEPARTMENT_500_ID_RE = re.compile(r"var:tv_wonder_locked \?= (?P<id>\d+)")
ENGINEERING_DEPARTMENT_500_DESC_RE = re.compile(r"desc = tv_engineering_department\.500\.d_(?P<suffix>[A-Za-z0-9_]+?)(?:_(?P<style>\d+))?$")


def normalize_editor_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ").strip()


def escape_localization_value(value: str) -> str:
    normalized = normalize_editor_text(value)
    return normalized.replace("\\", "\\\\").replace('"', '\\"')


def parse_localization_value(raw_value: str) -> str:
    try:
        return ast.literal_eval(raw_value)
    except Exception:
        return raw_value[1:-1].replace(r"\"", '"').replace(r"\\", "\\")


def load_localization_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        match = LOCALIZATION_LINE_RE.match(raw_line)
        if match is None:
            continue
        key = match.group("key")
        values[key] = parse_localization_value(match.group("value"))
    return values


def write_localization_updates(path: Path, updates: dict[str, str], *, append_missing: bool = True) -> bool:
    if not updates:
        return False

    if path.exists():
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    else:
        lines = []

    changed = False
    seen_keys: set[str] = set()
    rewritten: list[str] = []
    for raw_line in lines:
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
    if missing_keys and append_missing:
        if rewritten and rewritten[-1].strip():
            rewritten.append("")
        for key in missing_keys:
            rewritten.append(f' {key}:0 "{escape_localization_value(updates[key])}"')
        changed = True

    if not changed:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rewritten).rstrip() + "\n", encoding="utf-8-sig")
    return True


def load_wonder_localization_data() -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {language: {} for language in LANGUAGES}
    if not WONDER_LOCALIZATION_FILE.exists():
        return result

    raw = yaml.safe_load(WONDER_LOCALIZATION_FILE.read_text(encoding="utf-8"))
    if not raw:
        return result

    localization = raw.get("wonder_localization", {})
    for language in result:
        language_values = localization.get(language, {}) or {}
        result[language] = {str(key): str(value) for key, value in language_values.items()}
    return result


def save_wonder_localization_data(localization: dict[str, dict[str, str]]) -> None:
    payload = {
        "wonder_localization": {
            language: dict(localization.get(language, {}))
            for language in LANGUAGES
        },
    }
    WONDER_LOCALIZATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    WONDER_LOCALIZATION_FILE.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )


def apply_localization_values(text: str, localization: dict[str, str]) -> str:
    if not localization:
        return text

    rewritten: list[str] = []
    for raw_line in text.splitlines():
        match = LOCALIZATION_LINE_RE.match(raw_line)
        if match is None:
            rewritten.append(raw_line)
            continue

        key = match.group("key")
        if key not in localization:
            rewritten.append(raw_line)
            continue

        prefix = match.group("indent")
        version = match.group("version") or ""
        rewritten.append(f'{prefix}{key}:{version} "{escape_localization_value(localization[key])}"')
    return "\n".join(rewritten).rstrip() + "\n"


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
