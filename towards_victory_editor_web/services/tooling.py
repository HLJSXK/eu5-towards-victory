from __future__ import annotations

import contextlib
import copy
import io
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ContextManager, Iterable, Protocol

from .artifacts import (
    Artifact, artifact_path, collect_artifacts, snapshot_artifacts, validate_artifact_contract,
)
from .operation_store import OperationStore
from .platform import (
    ConflictError,
    FileSnapshot,
    OperationCancelled,
    OperationLog,
    repo_relative_path,
    run_operation,
    snapshot_files,
)


@dataclass(frozen=True)
class ToolOption:
    key: str
    label: str
    kind: str
    default: Any = None
    required: bool = False
    choices: tuple[str, ...] = ()
    description: str = ""

    def payload(self) -> dict[str, Any]:
        value = {
            "key": self.key,
            "label": self.label,
            "kind": self.kind,
            "default": self.default,
            "required": self.required,
            "description": self.description,
        }
        if self.choices:
            value["choices"] = list(self.choices)
        return value


@dataclass(frozen=True)
class ToolSpec:
    id: str
    label: str
    description: str
    group: str
    options: tuple[ToolOption, ...] = ()
    interactive: bool = False
    # Resources identify the editor contract a generator consumes.  Keeping
    # this on the tool spec lets the catalog and every job report the same
    # dependency without importing a domain service into the job runner.
    resource_ids: tuple[str, ...] = ()
    # Formats are a small, declarative contract for the artifacts a tool may
    # produce. Each prepared invocation supplies concrete output paths.
    artifact_formats: tuple[str, ...] = ()

    def payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "group": self.group,
            "interactive": self.interactive,
            "options": [option.payload() for option in self.options],
            "resource_ids": list(self.resource_ids),
            "artifact_formats": list(self.artifact_formats),
        }


def normalize_declared_options(spec: ToolSpec, options: dict[str, Any]) -> dict[str, Any]:
    """Apply the same option contract to every runnable tool."""
    if not isinstance(options, dict):
        raise ValueError("options must be an object")
    declared = {option.key: option for option in spec.options}
    unknown = sorted(set(options) - set(declared))
    if unknown:
        raise ValueError(f"Unknown option(s) for {spec.id}: {', '.join(unknown)}")
    normalized: dict[str, Any] = {}
    for key, option in declared.items():
        value = options.get(key, option.default)
        if value is None:
            if option.required:
                raise ValueError(f"Missing required option: {key}")
            continue
        if option.kind == "boolean":
            if not isinstance(value, bool):
                raise ValueError(f"{key} must be a boolean")
        elif option.kind == "integer":
            if isinstance(value, bool):
                raise ValueError(f"{key} must be an integer")
            try:
                value = int(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{key} must be an integer") from exc
        elif option.kind == "paths":
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                raise ValueError(f"{key} must be a list of paths")
        elif not isinstance(value, str):
            raise ValueError(f"{key} must be text")
        if option.choices and value not in option.choices:
            raise ValueError(f"{key} must be one of: {', '.join(option.choices)}")
        normalized[key] = value
    return normalized


@dataclass(frozen=True)
class ToolResult:
    """Result fields must be JSON serializable before publication."""

    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


def _json_snapshot(value: dict[str, Any], *, label: str) -> dict[str, Any]:
    """Validate the tool boundary and detach the published JSON tree."""
    try:
        return json.loads(json.dumps(value, allow_nan=False))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be JSON serializable: {exc}") from exc


@dataclass(frozen=True)
class ToolPlan:
    """One resolved invocation; declarations and execution share this state."""

    inputs: tuple[FileSnapshot, ...]
    outputs: tuple[Path, ...]
    run: Callable[["ToolContext"], ToolResult]
    optional_outputs: tuple[Path, ...] = ()


def read_plan_inputs(
    paths: Iterable[Path], loader: Callable[[], Any], *,
    repo_root: Path, optional: Iterable[Path] = (),
) -> tuple[Any, tuple[FileSnapshot, ...]]:
    """Track absent optional files too, and reject changes during preparation."""
    paths = tuple(paths)
    optional = set(optional)
    before = snapshot_files(paths, repo_root=repo_root)
    for path, snapshot in zip(paths, before):
        if snapshot.sha256 == "missing" and path not in optional:
            raise FileNotFoundError(f"Missing declared input: {snapshot.path}")
    value = loader()
    if before != snapshot_files(paths, repo_root=repo_root):
        raise ConflictError("Declared inputs changed during job preparation")
    return value, before


class ToolHandler(Protocol):
    spec: ToolSpec

    def validate(self, options: dict[str, Any]) -> dict[str, Any]: ...

    def prepare(self, options: dict[str, Any]) -> ContextManager[ToolPlan]: ...


class ToolContext:
    def __init__(
        self,
        job_id: str,
        repo_root: Path,
        emit: Callable[[str], None],
        operation: OperationLog,
    ) -> None:
        self.job_id = job_id
        self.repo_root = repo_root
        self._emit = emit
        self.operation = operation

    def log(self, message: str) -> None:
        message = str(message).rstrip("\r\n")
        self._emit(message)

    def request_cancel(self) -> None:
        self.operation.request_cancel()

    def check_cancelled(self) -> None:
        self.operation.check_cancelled()


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}
        self._specs: dict[str, ToolSpec] = {}

    def register(self, handler: ToolHandler) -> None:
        if handler.spec.id in self._specs:
            raise ValueError(f"Duplicate tool id: {handler.spec.id}")
        self._handlers[handler.spec.id] = handler
        self._specs[handler.spec.id] = handler.spec

    def register_spec(self, spec: ToolSpec) -> None:
        if spec.id in self._specs:
            raise ValueError(f"Duplicate tool id: {spec.id}")
        self._specs[spec.id] = spec

    def get(self, tool_id: str) -> ToolHandler:
        try:
            return self._handlers[tool_id]
        except KeyError as exc:
            raise ValueError(f"Unknown tool: {tool_id}") from exc

    def all(self) -> tuple[ToolHandler, ...]:
        return tuple(self._handlers.values())

    def payload(self, *, interactive: bool | None = None) -> list[dict[str, Any]]:
        return [
            spec.payload()
            for spec in self._specs.values()
            if interactive is None or spec.interactive == interactive
        ]

class Job:
    def __init__(
        self, handler: ToolHandler, options: dict[str, Any], repo_root: Path,
        operation_store: OperationStore | None = None,
    ) -> None:
        self.handler = handler
        self.options = options
        self.repo_root = repo_root
        self.lines: list[str] = []
        self._line_cursor = 0
        self._details_lock = threading.RLock()
        self.message = ""
        self.metadata: dict[str, Any] = {}
        self.artifacts: tuple[Artifact, ...] = ()
        self.source_snapshots: list[dict[str, Any]] = []
        self.declared_outputs: list[str] = []
        self.missing_outputs: list[str] = []
        self.operation = OperationLog(
            "media_job", handler.spec.resource_ids, store=operation_store,
            snapshot_details=self._snapshot_details,
        )
        self.id = self.operation.id
        self.context = ToolContext(self.id, repo_root, self._append, self.operation)

    def _append(self, line: str) -> None:
        with self._details_lock:
            self.lines.append(line)
            self._line_cursor += 1
            del self.lines[:-500]
        # Never acquire the operation lock while holding the details lock:
        # lifecycle checkpoints take them in the opposite order.
        self.operation.checkpoint(force=False)

    def payload(self, after_line: int | None = None) -> dict[str, Any]:
        operation, details = self.operation.payload_with_details()
        return job_payload(operation, details, after_line=after_line)

    def _snapshot_details(self) -> dict[str, Any]:
        with self._details_lock:
            return copy.deepcopy({
                "tool": self.handler.spec.id,
                "options": self.options,
                "lines": self.lines,
                "line_cursor": self._line_cursor,
                "message": self.message,
                "metadata": self.metadata,
                "artifact_formats": list(self.handler.spec.artifact_formats),
                "source_snapshots": self.source_snapshots,
                "declared_outputs": self.declared_outputs,
                "missing_outputs": self.missing_outputs,
                "artifacts": [artifact.payload() for artifact in self.artifacts],
            })


def job_payload(
    operation: dict[str, Any], details: dict[str, Any], *, after_line: int | None = None
) -> dict[str, Any]:
    """Use one read protocol for live jobs and durable, read-only checkpoints."""
    cursor = details["line_cursor"]
    retained_start = cursor - len(details["lines"])
    reset = after_line is None or after_line < retained_start or after_line > cursor
    start = max(retained_start, cursor - 300) if reset else after_line
    return {
        **details,
        "id": operation["id"],
        "status": operation["status"],
        "lines": details["lines"][start - retained_start:],
        "lines_reset": reset,
        "returncode": {"succeeded": 0, "failed": 1, "cancelled": 130}.get(operation["status"]),
        "error": operation["error"],
        "resource_ids": operation["resource_ids"],
        "outputs_may_be_partial": operation["status"] in {"failed", "cancelled"} and (
            any(artifact["changed"] for artifact in details["artifacts"])
            or (operation.get("interrupted", False) and operation["started_at"] is not None)
        ),
        "operation_id": operation["id"],
        "operation": operation,
        "created_at": operation["created_at"],
        "finished_at": operation["finished_at"],
    }


class JobManager:
    def __init__(
        self, registry: ToolRegistry, repo_root: Path,
        operation_store: OperationStore | None = None,
    ) -> None:
        self.registry = registry
        self.repo_root = repo_root
        self.operation_store = operation_store
        self._jobs: dict[str, Job] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="tv-tool")
        self._execution_lock = threading.RLock()

    def submit(self, tool_id: str, options: dict[str, Any]) -> Job:
        handler = self.registry.get(tool_id)
        normalized = _json_snapshot(
            handler.validate(options), label=f"Tool options for {handler.spec.id}"
        )
        job = Job(handler, normalized, self.repo_root, self.operation_store)
        with self._lock:
            self._prune_expired_locked()
            self._jobs[job.id] = job
        self._executor.submit(self._run, job)
        return job

    def get(self, job_id: str, after_line: int | None = None) -> dict[str, Any]:
        with self._lock:
            self._prune_expired_locked()
            job = self._jobs.get(job_id)
        if job is not None:
            return job.payload(after_line=after_line)
        if self.operation_store is not None:
            try:
                operation, details = self.operation_store.get_with_details(job_id)
            except KeyError:
                pass
            else:
                if operation["kind"] == "media_job":
                    return job_payload(operation, details, after_line=after_line)
        raise KeyError(f"Unknown job: {job_id}")

    def cancel(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            self._prune_expired_locked()
            job = self._jobs.get(job_id)
        if job is not None:
            job.context.request_cancel()
        # Archived jobs are terminal: cancellation is an idempotent read, not
        # reconstruction of a handler or a request to resume execution.
        return self.get(job_id)

    def _prune_expired_locked(self) -> None:
        retention = (self.operation_store.retention_seconds if self.operation_store is not None
                     else OperationStore.DEFAULT_RETENTION_DAYS * 86400)
        cutoff = time.time() - retention
        expired = []
        for job_id, job in self._jobs.items():
            operation = job.operation.payload()
            if (operation["status"] in OperationLog.TERMINAL_STATUSES
                    and operation["finished_at"] < cutoff):
                expired.append(job_id)
        for job_id in expired:
            del self._jobs[job_id]

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)

    def _run(self, job: Job) -> None:
        def execute() -> None:
            with capture_script_output(job.context), job.handler.prepare(job.options) as plan:
                outputs = tuple(dict.fromkeys(path.resolve() for path in (*plan.outputs, *plan.optional_outputs)))
                for path in outputs:
                    repo_relative_path(path, self.repo_root)
                with job._details_lock:
                    job.source_snapshots = [vars(item) for item in plan.inputs]
                    job.declared_outputs = [artifact_path(self.repo_root, path) for path in outputs]
                job.operation.checkpoint()
                inputs = tuple(self.repo_root / item.path for item in plan.inputs)
                job.context.check_cancelled()
                if snapshot_files(inputs, repo_root=self.repo_root) != plan.inputs:
                    raise ConflictError("Declared inputs changed before job execution")
                before = snapshot_artifacts(outputs)
                try:
                    result = plan.run(job.context)
                    result_snapshot = _json_snapshot(
                        {"message": result.message, "metadata": dict(result.metadata)},
                        label=f"Tool result from {job.handler.spec.id}",
                    )
                    with job._details_lock:
                        job.message = result_snapshot["message"]
                        job.metadata = result_snapshot["metadata"]
                finally:
                    # Preserve the real disk outcome even if run() raises or is cancelled.
                    after = snapshot_artifacts(outputs)
                    artifacts = collect_artifacts(self.repo_root, before, after)
                    missing_outputs = [
                        artifact_path(self.repo_root, path) for path in plan.outputs
                        if path.resolve() not in after
                    ]
                    validation = validate_artifact_contract(
                        self.repo_root, artifacts, job.handler.spec.artifact_formats
                    )
                    with job._details_lock:
                        job.artifacts = artifacts
                        job.missing_outputs = missing_outputs
                        job.metadata["output_validation"] = validation
                    job.operation.checkpoint()
                # Cancellation wins over stale-input / missing-output diagnostics.
                job.context.check_cancelled()
                # DDS-only conversions intentionally transform their input in place.
                immutable = tuple(item for item in plan.inputs if (self.repo_root / item.path).resolve() not in outputs)
                if snapshot_files((self.repo_root / item.path for item in immutable), repo_root=self.repo_root) != immutable:
                    raise ConflictError("Declared inputs changed during job execution; outputs may be stale")
                if job.missing_outputs:
                    raise RuntimeError("Missing declared outputs: " + ", ".join(job.missing_outputs))
                failures = [item for item in job.metadata["output_validation"] if not item["valid"]]
                if failures:
                    raise RuntimeError("Output validation failed: " + "; ".join(
                        f"{item['path']}: {item['error']}" for item in failures
                    ))

        def record_failure(exc: Exception) -> None:
            status = "cancelled" if isinstance(exc, OperationCancelled) else "failed"
            job._append(f"{status}: {exc}")
            if any(artifact.changed for artifact in job.artifacts):
                job.context.log("Output files were changed on disk; no rollback was performed.")

        try:
            run_operation(job.operation, execute, execution_lock=self._execution_lock, on_error=record_failure)
        except Exception:
            # The executor has recorded the failure; expose it through polling.
            pass


class CapturedOutput(io.TextIOBase):
    def __init__(self, context: ToolContext, stream_name: str) -> None:
        super().__init__()
        self.context = context
        self.stream_name = stream_name

    def write(self, text: str) -> int:
        for line in text.splitlines():
            if line:
                self.context.log(line)
        return len(text)

    def flush(self) -> None:
        return None


@contextlib.contextmanager
def capture_script_output(context: ToolContext):
    stdout = CapturedOutput(context, "stdout")
    stderr = CapturedOutput(context, "stderr")
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        yield
