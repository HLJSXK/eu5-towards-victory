"""Paired EN/ZH localization edits through the existing resource platform."""

from __future__ import annotations

import hashlib
import re
import threading
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from scripts_engineering_department.wonder_mechanics.io import REPO_ROOT

from .operation_store import OperationStore
from .platform import (
    ChangeSet,
    ConflictError,
    FileSnapshot,
    OperationLog,
    ResourceDescriptor,
    assert_resource_base,
    atomic_write_files,
    file_transaction,
    run_operation,
    snapshot_files,
    source_text_bytes,
)

LANGUAGES = ("english", "simp_chinese")
REGISTRY = "data/generated_files.yaml"
KEY_PATTERN = re.compile(r"[A-Za-z0-9_.-]+")
HEADER_PATTERN = re.compile(r"l_([a-z_]+):\s*")
ENTRY_PATTERN = re.compile(r'^\s+([A-Za-z0-9_.-]+):\d*\s*"(.*)"\s*(?:#.*)?$')


@dataclass(frozen=True)
class LocalizationFile:
    language: str
    values: dict[str, str]
    raw: bytes


def _parse_file(path: str, raw: bytes) -> LocalizationFile:
    language = None
    values: dict[str, str] = {}
    for line_number, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if language is None:
            header = HEADER_PATTERN.fullmatch(stripped)
            if header is None:
                raise ValueError(f"Missing localization language header: {path}:{line_number}")
            language = header[1]
            if not path.endswith(f"_l_{language}.yml") or language not in PurePosixPath(path).parts:
                raise ValueError(f"Localization language does not match path: {path}")
            continue
        entry = ENTRY_PATTERN.fullmatch(line)
        if entry is None or "\x00" in line:
            raise ValueError(f"Malformed localization entry: {path}:{line_number}")
        key, value = entry.groups()
        if key in values:
            raise ValueError(f"Duplicate localization key {key!r}: {path}:{line_number}")
        values[key] = value
    if language is None:
        raise ValueError(f"Missing localization language header: {path}")
    return LocalizationFile(language, values, raw)


def _counterparts(path: str, language: str) -> dict[str, str]:
    parts = list(PurePosixPath(path).parts)
    language_index = parts.index("localization") + 1
    if parts[language_index] != language:
        raise ValueError(f"Localization language directory does not match header: {path}")
    stem = parts[-1][:-len(f"_l_{language}.yml")]
    result = {}
    for target in LANGUAGES:
        target_parts = parts.copy()
        target_parts[language_index] = target
        target_parts[-1] = f"{stem}_l_{target}.yml"
        result[target] = PurePosixPath(*target_parts).as_posix()
    return result


class LocalizationEditorService:
    def __init__(self, operation_store: OperationStore | None = None, *, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or REPO_ROOT).resolve()
        self.operation_store = operation_store
        self._lock = threading.RLock()
        self._documents: dict[str, LocalizationFile] = {}
        self._generated: dict[str, list[str]] = {}
        self._base: tuple[FileSnapshot, ...] = ()

    def _discover_paths(self) -> list[Path]:
        result = set()
        for root in sorted(self.repo_root.glob("src*")):
            if not root.is_dir():
                continue
            for path in root.glob("**/localization/**/*.yml"):
                if not path.is_file():
                    continue
                try:
                    path.resolve().relative_to(root.resolve())
                    path.resolve().relative_to(self.repo_root)
                except ValueError as exc:
                    raise ValueError(f"Localization path escapes mod root: {path}") from exc
                result.add(path)
        return sorted(result)

    def reload_from_disk(self) -> None:
        registry_raw = (self.repo_root / REGISTRY).read_bytes()
        registry = yaml.safe_load(registry_raw.decode("utf-8-sig"))
        generated = {
            str(entry["output"]).replace("\\", "/"): [part.strip() for part in str(entry["data"]).split("+")]
            for entry in registry["generated"]
        }
        documents = {}
        snapshots = []
        for path in self._discover_paths():
            relative = path.relative_to(self.repo_root).as_posix()
            raw = path.read_bytes()
            document = _parse_file(relative, raw)
            _counterparts(relative, document.language)
            documents[relative] = document
            snapshots.append(FileSnapshot(relative, hashlib.sha256(raw).hexdigest(), len(raw)))
        snapshots.append(FileSnapshot(REGISTRY, hashlib.sha256(registry_raw).hexdigest(), len(registry_raw)))
        self._documents, self._generated, self._base = documents, generated, tuple(snapshots)

    def resource_descriptor(self) -> ResourceDescriptor:
        return ResourceDescriptor(
            "editor.localization", "localization", "Localization", tuple(item.path for item in self._base)
        )

    def _resource(self) -> dict[str, Any]:
        return {
            **self.resource_descriptor().payload(),
            "discovery": {
                "glob": "src*/**/localization/**/*.yml",
                "generated_registry": REGISTRY,
                "generated_policy": "read_only; edit the registered data source instead",
                "writable_languages": list(LANGUAGES),
            },
        }

    def _read_only(self, path: str) -> tuple[bool, str, list[str]]:
        document = self._documents[path]
        counterparts = _counterparts(path, document.language)
        owners = sorted({owner for target in {path, *counterparts.values()} for owner in self._generated.get(target, [])})
        if any(target in self._generated for target in {path, *counterparts.values()}):
            return True, "Generated localization; edit source data: " + ", ".join(owners), owners
        if document.language not in LANGUAGES:
            return True, "Only english and simp_chinese are editable in this resource", []
        return False, "", []

    def _missing(self, values: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
        pairs = {
            _counterparts(path, document.language)["english"]: _counterparts(path, document.language)
            for path, document in self._documents.items()
            if document.language in LANGUAGES and not self._read_only(path)[0]
        }
        missing = []
        for counterparts in pairs.values():
            for target, source in (("simp_chinese", "english"), ("english", "simp_chinese")):
                keys = sorted(set(values.get(counterparts[source], {})) - set(values.get(counterparts[target], {})))
                if keys:
                    missing.append({"path": counterparts[target], "keys": keys})
        return sorted(missing, key=lambda entry: entry["path"])

    def _draft(self, values: dict[str, dict[str, str]]) -> dict[str, Any]:
        roots: dict[str, list[dict[str, Any]]] = {}
        for path, document in self._documents.items():
            read_only, reason, source_data = self._read_only(path)
            languages = {
                language: [{"key": key, "value": value} for key, value in values.get(target, {}).items()]
                for language, target in _counterparts(path, document.language).items()
            }
            if document.language not in LANGUAGES:
                languages[document.language] = [{"key": key, "value": value} for key, value in values[path].items()]
            item = {"path": path, "read_only": read_only, "languages": languages}
            if read_only:
                item["read_only_reason"] = reason
            if source_data:
                item["source_data"] = source_data
            roots.setdefault(PurePosixPath(path).parts[0], []).append(item)
        return {
            "roots": [{"root": root, "files": files} for root, files in sorted(roots.items())],
            "missing_translations": self._missing(values),
        }

    def _payload(self, values: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
        if values is None:
            values = {path: document.values for path, document in self._documents.items()}
        return {
            "resource": self._resource(),
            "draft": self._draft(values),
            "change_set": ChangeSet("editor.localization", tuple(item.path for item in self._base), self._base).payload(),
        }

    def load_resource(self) -> dict[str, Any]:
        with self._lock:
            self.reload_from_disk()
            return self._payload()

    def _assert_base(self, base: dict[str, str] | None) -> None:
        paths = (*self._discover_paths(), self.repo_root / REGISTRY)
        current = snapshot_files(paths, repo_root=self.repo_root)
        assert_resource_base(base, self._base, current)
        if {item.path for item in current} != {item.path for item in self._base}:
            raise ConflictError("Localization file list changed since load")

    def _candidate(self, edits: dict[str, Any]) -> tuple[dict[str, dict[str, str]], list[dict[str, Any]]]:
        if not isinstance(edits, dict):
            raise ValueError("edits must be an object")
        values = {path: dict(document.values) for path, document in self._documents.items()}
        assigned = set()
        for path, changes in edits.items():
            if path not in self._documents:
                raise ValueError(f"Unknown localization file: {path}")
            read_only, reason, _ = self._read_only(path)
            if read_only:
                raise ValueError(f"read_only localization file {path}: {reason}")
            if not isinstance(changes, dict):
                raise ValueError(f"Edits for {path} must be an object")
            counterparts = _counterparts(path, self._documents[path].language)
            if any(target not in values for target in counterparts.values()):
                raise ValueError(f"Missing paired localization file: {path}")
            for key, fields in changes.items():
                if not isinstance(key, str) or KEY_PATTERN.fullmatch(key) is None:
                    raise ValueError(f"Invalid localization key: {key}")
                existed = any(key in self._documents[target].values for target in counterparts.values())
                if fields is None:
                    if not existed:
                        raise ValueError(f"Unknown localization key: {key}")
                    fields = dict.fromkeys(LANGUAGES)
                else:
                    if not isinstance(fields, dict) or not fields or set(fields) - set(LANGUAGES):
                        raise ValueError(f"Invalid language fields for {key}")
                    if not existed and set(fields) != set(LANGUAGES):
                        raise ValueError(f"New key {key} requires both english and simp_chinese values")
                    for value in fields.values():
                        if not isinstance(value, str) or any(char in value for char in ("\r", "\n", "\x00")):
                            raise ValueError(f"Value for {key} must be a string without physical CR/LF or NUL")
                for language, value in fields.items():
                    target = counterparts[language]
                    identity = (target, key)
                    if identity in assigned:
                        raise ValueError(f"Duplicate localization edit: {target}: {key}")
                    assigned.add(identity)
                    if value is None:
                        values[target].pop(key, None)
                    else:
                        values[target][key] = value
        owners = {}
        for path, entries in values.items():
            language = self._documents[path].language
            for key in entries:
                identity = (PurePosixPath(path).parts[0], language, key)
                if identity in owners:
                    raise ValueError(f"Duplicate localization key {key!r}: {owners[identity]}, {path}")
                owners[identity] = path
        diff = []
        for path, entries in values.items():
            before = self._documents[path].values
            for key in sorted(set(before) | set(entries)):
                if (key in before, before.get(key)) != (key in entries, entries.get(key)):
                    diff.append({
                        "path": path, "key": key, "language": self._documents[path].language,
                        "field": "value", "before": before.get(key), "after": entries.get(key),
                        "before_present": key in before, "after_present": key in entries,
                    })
        return values, diff

    def _validation(self, values: dict[str, dict[str, str]]) -> dict[str, Any]:
        missing = self._missing(values)
        return {
            "valid": not missing,
            "errors": [f"{entry['path']}: missing translation keys: {', '.join(entry['keys'])}" for entry in missing],
            "missing_translations": missing,
        }

    def validate_edits(self, edits: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self.reload_from_disk()
            values, _ = self._candidate(edits)
            return {"resource": self._resource(), **self._validation(values)}

    def preview_edits(self, edits: dict[str, Any], base: dict[str, str] | None = None) -> dict[str, Any]:
        with self._lock:
            self.reload_from_disk()
            self._assert_base(base)
            values, diff = self._candidate(edits)
            return {**self._payload(values), **self._validation(values), "diff": diff}

    def commit_edits(self, edits: dict[str, Any], base: dict[str, str] | None = None) -> dict[str, Any]:
        operation = OperationLog("commit", ("editor.localization",), store=self.operation_store)

        def commit() -> dict[str, Any]:
            self.reload_from_disk()
            self._assert_base(base)
            values, diff = self._candidate(edits)
            validation = self._validation(values)
            if not validation["valid"]:
                raise ValueError("; ".join(validation["errors"]))
            files = {}
            for relative in sorted({entry["path"] for entry in diff}):
                document = self._documents[relative]
                body = f"l_{document.language}:\n" + "\n".join(
                    f' {key}: "{value}"' for key, value in values[relative].items()
                )
                path = self.repo_root / relative
                content = source_text_bytes(path, body)
                _parse_file(relative, content)
                files[path] = content
            self._assert_base(base)
            with file_transaction(files, reload=self.reload_from_disk):
                atomic_write_files(files)
                self.reload_from_disk()
                result = self._payload()
            return {**result, "written_paths": [path.relative_to(self.repo_root).as_posix() for path in files]}

        result = run_operation(operation, commit, execution_lock=self._lock)
        return {**result, "operation_id": operation.id, "operation": operation.payload()}


def build_check_report() -> list[str]:
    service = LocalizationEditorService()
    payload = service.load_resource()
    validation = service.validate_edits({})
    lines = []
    for root in payload["draft"]["roots"]:
        files = root["files"]
        manual = [item for item in files if item["path"] not in service._generated]
        editable = [item for item in files if not item["read_only"]]
        pairs = {
            _counterparts(item["path"], service._documents[item["path"]].language)["english"]
            for item in editable
        }
        counts = {
            language: sum(len(service._documents[item["path"]].values) for item in editable
                          if service._documents[item["path"]].language == language)
            for language in LANGUAGES
        }
        missing = sum(len(entry["keys"]) for entry in validation["missing_translations"]
                      if PurePosixPath(entry["path"]).parts[0] == root["root"])
        lines.append(
            f"[{'FAIL' if missing else 'PASS'}] {root['root']}: hand-authored files={len(manual)}, "
            f"editable EN/ZH files={len(editable)}, bilingual groups={len(pairs)}, "
            f"EN keys={counts['english']}, ZH keys={counts['simp_chinese']}, missing keys={missing}"
        )
    lines.extend(f"[FAIL] {error}" for error in validation["errors"])
    return lines
