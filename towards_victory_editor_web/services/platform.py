"""Small platform contracts shared by editor adapters.

The web workspace edits repository files directly, so the platform boundary
needs explicit source descriptors and an atomic commit primitive before more
editors are migrated.
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
import sys
import tempfile
import threading
import time
import uuid
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, ContextManager, Iterable, Iterator, TypeVar

from scripts_engineering_department.wonder_mechanics._core import StrictWonderYamlLoader, load_yaml
from .operation_store import OperationStore


class ConflictError(RuntimeError):
    """Raised when a resource changed after the editor loaded its draft."""

    code = "resource_changed"


class ResourceBusyError(ConflictError):
    """Raised when another operation currently holds a resource lock."""

    code = "resource_busy"


class OperationCancelled(RuntimeError):
    """Cooperative cancellation shared by operation runners and handlers."""


class OperationLog:
    """Shared lifecycle record for resource commits and media jobs.

    The record stays small and keeps domain logs and artifact reports separate.
    A configured store snapshots each visible transition for later queries.
    """

    MAX_EVENTS = 500
    EVENT_PERSIST_INTERVAL = 0.5
    EVENT_PERSIST_BATCH = 50
    TERMINAL_STATUSES = frozenset({"succeeded", "failed", "cancelled"})

    def __init__(
        self, kind: str, resource_ids: Iterable[str] = (), *, store: OperationStore | None = None,
        snapshot_details: Callable[[], dict[str, object]] | None = None,
    ) -> None:
        self.id = uuid.uuid4().hex
        self.kind = kind
        self.resource_ids = tuple(sorted(set(resource_ids)))
        self.status = "queued"
        self.error: str | None = None
        self.cancel_requested = False
        self._cancel_event = threading.Event()
        self.created_at = time.time()
        self.started_at: float | None = None
        self.finished_at: float | None = None
        self._events: list[dict[str, object]] = []
        self._lock = threading.RLock()
        self._execution_claimed = False
        self._store = store
        self._snapshot_details = snapshot_details
        self.persistence_error: str | None = None
        self._last_persist_at = 0.0
        self._events_since_persist = 0
        self._persist_locked()

    def event(self, message: str, *, level: str = "info", force_persist: bool = False) -> None:
        with self._lock:
            self._events.append({"at": time.time(), "level": level, "message": str(message)})
            del self._events[:-self.MAX_EVENTS]
            self._events_since_persist += 1
            self._persist_locked(force=force_persist)

    def start(self) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            if self.started_at is None:
                self.started_at = time.time()
            self.status = "running"
            self.event("started", force_persist=True)

    def request_cancel(self) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES or self.cancel_requested:
                return
            self.cancel_requested = True
            self._cancel_event.set()
            if self.status in {"queued", "running"}:
                self.status = "cancelling"
            self.event("cancellation requested", level="warning", force_persist=True)

    def check_cancelled(self) -> None:
        with self._lock:
            if self.cancel_requested:
                raise OperationCancelled("Cancellation requested")

    def wait(self, seconds: float) -> None:
        self._cancel_event.wait(seconds)
        self.check_cancelled()

    def succeed(self) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            self.status = "succeeded"
            self.finished_at = time.time()
            self.event("succeeded", force_persist=True)

    def fail(self, error: object) -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            self.status = "failed"
            self.error = str(error)
            self.finished_at = time.time()
            self.event(self.error, level="error", force_persist=True)

    def cancel(self, error: object = "Cancellation requested") -> None:
        with self._lock:
            if self.status in self.TERMINAL_STATUSES:
                return
            self.cancel_requested = True
            self._cancel_event.set()
            self.status = "cancelled"
            self.error = str(error)
            self.finished_at = time.time()
            self.event(self.error, level="warning", force_persist=True)

    def payload(self) -> dict[str, object]:
        with self._lock:
            return self._payload_locked()

    def checkpoint(self, *, force: bool = True) -> None:
        """Persist changed domain details without duplicating them in events."""
        with self._lock:
            self._events_since_persist += 1
            self._persist_locked(force=force)

    def payload_with_details(self) -> tuple[dict[str, object], dict[str, object]]:
        with self._lock:
            if self._snapshot_details is None:
                raise RuntimeError("Operation has no domain details")
            return self._payload_locked(), self._snapshot_details()

    def _payload_locked(self) -> dict[str, object]:
        payload: dict[str, object] = {
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
        if self.persistence_error is not None:
            payload["persistence_error"] = self.persistence_error
        return payload

    def _persist_locked(self, *, force: bool = True) -> None:
        if self._store is None:
            return
        now = time.time()
        if (
            not force
            and self._events_since_persist < self.EVENT_PERSIST_BATCH
            and now - self._last_persist_at < self.EVENT_PERSIST_INTERVAL
        ):
            return
        try:
            if self._snapshot_details is None:
                self._store.save(self._payload_locked())
            else:
                self._store.save(self._payload_locked(), details=self._snapshot_details())
            self._last_persist_at = now
            self._events_since_persist = 0
        except (OSError, sqlite3.Error) as exc:
            # A diagnostic-store failure must not turn a completed file commit
            # into an apparent failed commit after its transaction has ended.
            self._last_persist_at = now
            self._events_since_persist = 0
            self.persistence_error = f"{type(exc).__name__}: {exc}"


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


OperationResult = TypeVar("OperationResult")


def run_operation(
    operation: OperationLog,
    execute: Callable[[], OperationResult],
    *,
    execution_lock: ContextManager | None = None,
    on_error: Callable[[Exception], None] | None = None,
) -> OperationResult:
    """Run a commit or job under the same resource and lifecycle boundary.

    Scheduling remains with the caller. An optional execution lock serializes
    media work without marking jobs running while they wait. Domain callbacks
    own validation, transactions and cleanup; all must finish before success.
    The error observer records domain diagnostics before terminal publication.
    ``on_error`` runs without the operation lock and must remain lightweight;
    its failure does not prevent the operation from reaching a terminal state.
    """
    with operation._lock:
        if operation._execution_claimed or operation.status not in {"queued", "cancelling"}:
            raise RuntimeError("An operation can only be executed once")
        operation._execution_claimed = True
    try:
        with execution_lock if execution_lock is not None else nullcontext():
            operation.check_cancelled()
            with resource_operation(operation.resource_ids, blocking=False):
                with operation._lock:
                    operation.check_cancelled()
                    operation.start()
                result = execute()
                # Cancellation and completion share a lock so a late request
                # cannot leave the operation cancelling after successful work.
                with operation._lock:
                    operation.succeed()
                return result
    except Exception as exc:
        with operation._lock:
            error = exc
            if operation.cancel_requested and not isinstance(error, OperationCancelled):
                # Cancellation decides the terminal status, but an incomplete
                # rollback must stay visible: files may need manual recovery.
                detail = f"; {exc}" if isinstance(exc, RollbackError) else ""
                error = OperationCancelled(f"Cancellation requested{detail}")
        try:
            if on_error is not None:
                on_error(error)
        except Exception as observer_error:
            diagnostic = f"on_error failed: {type(observer_error).__name__}: {observer_error}"
            error.add_note(diagnostic)
            operation.event(diagnostic, level="error")
        finally:
            # Keep diagnostics ahead of the terminal event, while guaranteeing
            # that a faulty observer cannot leave polling stuck in running.
            if isinstance(error, OperationCancelled):
                operation.cancel(error)
            else:
                operation.fail(error)
            error.operation = operation.payload()
        if error is not exc:
            raise error from exc
        raise


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


_input_recorders = threading.local()


def _record_file_inputs(event: str, args: tuple) -> None:
    recorder = getattr(_input_recorders, "current", None)
    if recorder is None or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
        return
    if event == "open":
        recorder[0].add(os.fsdecode(args[0]))
    elif event == "os.scandir":
        recorder[1].add(os.fsdecode(args[0]))


sys.addaudithook(_record_file_inputs)


@dataclass(frozen=True)
class InputFingerprint:
    """Stat-level identity of every file opened and directory scanned by one load."""

    files: tuple[tuple[str, int, int] | tuple[str, None, None], ...]
    directories: tuple[tuple[str, tuple[str, ...] | None], ...]

    @classmethod
    def capture(cls, files: Iterable[str], directories: Iterable[str]) -> "InputFingerprint":
        def stat(path: str):
            try:
                result = os.stat(path)
            except OSError:
                return (path, None, None)
            return (path, result.st_mtime_ns, result.st_size)

        def listing(path: str):
            try:
                return (path, tuple(sorted(os.listdir(path))))
            except OSError:
                return (path, None)

        return cls(tuple(stat(path) for path in sorted(set(files))),
                   tuple(listing(path) for path in sorted(set(directories))))

    def current(self) -> "InputFingerprint":
        return self.capture((item[0] for item in self.files), (item[0] for item in self.directories))


@contextmanager
def record_file_inputs(always: Iterable[Path] = ()) -> Iterator[list[InputFingerprint]]:
    """Record files this thread opens; yields a list that receives the fingerprint.

    Paths in ``always`` are included even when a load only checks for their
    existence, so a source created after the load is still detected.
    """
    previous = getattr(_input_recorders, "current", None)
    recorder = ({os.fspath(path) for path in always}, set())
    _input_recorders.current = recorder
    result: list[InputFingerprint] = []
    try:
        yield result
    finally:
        _input_recorders.current = previous
    result.append(InputFingerprint.capture(*recorder))


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
