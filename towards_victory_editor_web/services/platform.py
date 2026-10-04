"""Small platform contracts shared by editor adapters.

The web workspace edits repository files directly, so the platform boundary
needs explicit source descriptors and an atomic commit primitive before more
editors are migrated.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator

from scripts_engineering_department.wonder_mechanics._core import StrictWonderYamlLoader, load_yaml


class ConflictError(RuntimeError):
    """Raised when a resource changed after the editor loaded its draft."""

    code = "resource_changed"


class ResourceBusyError(ConflictError):
    """Raised when another operation currently holds a resource lock."""

    code = "resource_busy"


class OperationLog:
    """Shared lifecycle record for resource commits and media jobs.

    The record is deliberately small and in-memory.  It gives synchronous
    commits and asynchronous jobs the same observable state contract while
    keeping the existing domain logs and artifact reports intact.
    """

    MAX_EVENTS = 500
    TERMINAL_STATUSES = frozenset({"succeeded", "failed", "cancelled"})

    def __init__(self, kind: str, resource_ids: Iterable[str] = ()) -> None:
        self.id = uuid.uuid4().hex
        self.kind = kind
        self.resource_ids = tuple(sorted(set(resource_ids)))
        self.status = "queued"
        self.error: str | None = None
        self.cancel_requested = False
        self.created_at = time.time()
        self.started_at: float | None = None
        self.finished_at: float | None = None
        self._events: list[dict[str, object]] = []
        self._lock = threading.RLock()

    @property
    def operation_id(self) -> str:
        return self.id

    def event(self, message: str, *, level: str = "info") -> None:
        with self._lock:
            self._events.append({"at": time.time(), "level": level, "message": str(message)})
            del self._events[:-self.MAX_EVENTS]

    def start(self) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            if self.started_at is None:
                self.started_at = time.time()
            self.status = "cancelling" if self.cancel_requested else "running"
            self.event("started")

    def request_cancel(self) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            self.cancel_requested = True
            if self.status in {"queued", "running"}:
                self.status = "cancelling"
            self.event("cancellation requested", level="warning")

    def succeed(self) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            self.status = "succeeded"
            self.finished_at = time.time()
            self.event("succeeded")

    def fail(self, error: object) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            self.status = "failed"
            self.error = str(error)
            self.finished_at = time.time()
            self.event(self.error, level="error")

    def cancel(self, error: object = "Cancellation requested") -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            self.cancel_requested = True
            self.status = "cancelled"
            self.error = str(error)
            self.finished_at = time.time()
            self.event(self.error, level="warning")

    def payload(self) -> dict[str, object]:
        with self._lock:
            return {
                "id": self.id,
                "operation_id": self.id,
                "kind": self.kind,
                "status": self.status,
                "resource_ids": list(self.resource_ids),
                "events": list(self._events),
                "error": self.error,
                "cancel_requested": self.cancel_requested,
                "created_at": self.created_at,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
            }


_resource_locks: dict[str, threading.Lock] = {}
_resource_locks_guard = threading.Lock()


@contextmanager
def resource_operation(resource_ids: Iterable[str], *, blocking: bool = True) -> Iterator[None]:
    """Coordinate writers and generators in this single-process workspace."""
    acquired = []
    try:
        for resource_id in sorted(set(resource_ids)):
            with _resource_locks_guard:
                lock = _resource_locks.setdefault(resource_id, threading.Lock())
            if not lock.acquire(blocking=blocking):
                raise ResourceBusyError(f"Resource busy: {resource_id}; retry after the current operation finishes")
            acquired.append(lock)
        yield
    finally:
        for lock in reversed(acquired):
            lock.release()


class RollbackError(RuntimeError):
    """Keep the operation error and every recovery failure visible together."""

    def __init__(self, original: Exception, errors: list[str]) -> None:
        self.original = original
        self.errors = errors
        super().__init__(f"{original}\nRollback incomplete:\n" + "\n".join(errors))


def repo_relative_path(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


@dataclass(frozen=True)
class ResourceDescriptor:
    id: str
    kind: str
    label: str
    source_paths: tuple[str, ...]
    generator_ids: tuple[str, ...] = ()

    def payload(self) -> dict[str, object]:
        return {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "source_paths": list(self.source_paths),
            "generator_ids": list(self.generator_ids),
        }


@dataclass(frozen=True)
class FileSnapshot:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True)
class ChangeSet:
    resource_id: str
    files: tuple[str, ...]
    base: tuple[FileSnapshot, ...]

    def payload(self) -> dict[str, object]:
        return {
            "resource_id": self.resource_id,
            "files": list(self.files),
            "base": [
                {"path": item.path, "sha256": item.sha256, "size": item.size}
                for item in self.base
            ],
        }


def snapshot_files(paths: Iterable[Path], *, repo_root: Path | None = None) -> tuple[FileSnapshot, ...]:
    snapshots: list[FileSnapshot] = []
    for path in paths:
        resolved = path.resolve()
        display_path = str(resolved)
        if repo_root is not None:
            try:
                display_path = repo_relative_path(resolved, repo_root)
            except ValueError:
                pass
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            snapshots.append(FileSnapshot(display_path, "missing", 0))
        else:
            snapshots.append(FileSnapshot(display_path, hashlib.sha256(data).hexdigest(), len(data)))
    return tuple(snapshots)


def load_yaml_snapshots(
    paths: Iterable[Path], *, repo_root: Path, optional: Iterable[Path] = ()
) -> tuple[dict[Path, dict | None], tuple[FileSnapshot, ...]]:
    """Parse and hash each YAML source from the same read."""
    optional_paths = set(optional)
    documents: dict[Path, dict | None] = {}
    snapshots: list[FileSnapshot] = []
    for path in paths:
        display_path = repo_relative_path(path, repo_root)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            if path not in optional_paths:
                raise
            documents[path] = None
            snapshots.append(FileSnapshot(display_path, "missing", 0))
            continue
        loader = StrictWonderYamlLoader(raw.decode("utf-8"))
        loader.source_name = str(path)
        try:
            document = loader.get_single_data()
        finally:
            loader.dispose()
        if not isinstance(document, dict):
            raise TypeError(f"{path} must contain a top-level mapping")
        documents[path] = document
        snapshots.append(FileSnapshot(display_path, hashlib.sha256(raw).hexdigest(), len(raw)))
    return documents, tuple(snapshots)


def assert_resource_base(
    base: dict[str, str] | None,
    loaded: tuple[FileSnapshot, ...],
    current: tuple[FileSnapshot, ...],
) -> None:
    expected = {item.path: item.sha256 for item in loaded}
    if set(base or {}) != set(expected):
        raise ValueError("base must include snapshots for all resource files")
    actual = {item.path: item.sha256 for item in current}
    for path, digest in expected.items():
        if base[path] != digest or actual.get(path) != digest:
            raise ConflictError(f"Resource changed since load: {path}")


def atomic_write_files(files: dict[Path, bytes]) -> None:
    """Write all files through a staged directory, then replace them.

    Replacement across unrelated filesystem entries cannot be made globally
    atomic by POSIX. Staging all bytes first prevents partial serialization and
    keeps the failure boundary before the first target replacement.
    """
    temporary: list[tuple[Path, Path]] = []
    try:
        for target, content in files.items():
            target = target.resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
            temporary_path = Path(name)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
            except Exception:
                temporary_path.unlink(missing_ok=True)
                raise
            temporary.append((temporary_path, target))
        for temporary_path, target in temporary:
            mode = target.stat().st_mode & 0o777 if target.exists() else 0o644
            os.chmod(temporary_path, mode)
            os.replace(temporary_path, target)
    finally:
        for temporary_path, _ in temporary:
            temporary_path.unlink(missing_ok=True)


def snapshot_file_contents(paths: Iterable[Path]) -> dict[Path, bytes | None]:
    snapshots: dict[Path, bytes | None] = {}
    for path in paths:
        try:
            snapshots[path] = path.read_bytes()
        except FileNotFoundError:
            snapshots[path] = None
    return snapshots


def restore_file_contents(snapshots: dict[Path, bytes | None]) -> list[str]:
    """Restore each changed file independently, attempting all paths on failure."""
    errors: list[str] = []
    for path, original in snapshots.items():
        try:
            try:
                current = path.read_bytes()
            except FileNotFoundError:
                current = None
            if current == original:
                continue
            if original is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write_files({path: original})
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    return errors


@contextmanager
def file_transaction(paths: Iterable[Path], *, reload: Callable[[], None]) -> Iterator[None]:
    """Recover registered files and reload state after any operation failure."""
    snapshots = snapshot_file_contents(paths)
    try:
        yield
    except Exception as exc:
        errors = restore_file_contents(snapshots)
        try:
            reload()
        except Exception as reload_error:
            errors.append(f"Reload failed: {reload_error}")
        if errors:
            raise RollbackError(exc, errors) from exc
        raise


def generated_outputs_by_script(
    scripts: Iterable[str],
    *,
    repo_root: Path,
    extra_outputs: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, tuple[Path, ...]]:
    """Read the output registry once for a prepared generation plan."""
    scripts = tuple(scripts)
    if not scripts:
        return {}
    by_script: dict[str, list[str]] = {}
    for entry in load_yaml(repo_root / "data/generated_files.yaml")["generated"]:
        by_script.setdefault(entry["script"], []).append(entry["output"])
    for script, outputs in (extra_outputs or {}).items():
        by_script.setdefault(script, []).extend(outputs)
    result: dict[str, tuple[Path, ...]] = {}
    for script in scripts:
        if not by_script.get(script):
            raise ValueError(f"No registered outputs for generator: {script}")
        paths: dict[Path, None] = {}
        for output in by_script[script]:
            path = (repo_root / output).resolve()
            repo_relative_path(path, repo_root)  # Reject outputs outside the repository.
            paths[path] = None
        result[script] = tuple(paths)
    return result


def source_text_bytes(path: Path, body: str) -> bytes:
    """Preserve a source document's leading comments, BOM and newline style."""
    import codecs
    import re

    from scripts_engineering_department.wonder_mechanics._core import leading_comment_block

    header = ""
    has_bom = False
    newline = "\n"
    if path.exists():
        raw = path.read_bytes()
        has_bom = raw.startswith(codecs.BOM_UTF8)
        first_newline = re.search(rb"\r\n|\n|\r", raw)
        if first_newline:
            newline = first_newline.group().decode("ascii")
        text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        header = leading_comment_block(text)
    body = body.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"
    text = f"{header}\n{body}" if header else body
    return text.replace("\n", newline).encode("utf-8-sig" if has_bom else "utf-8")


def yaml_bytes(path: Path, payload: object) -> bytes:
    from scripts_engineering_department.wonder_mechanics.io import dump_yaml_document

    return source_text_bytes(path, dump_yaml_document(payload))
