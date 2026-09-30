from __future__ import annotations

import contextlib
import hashlib
import io
import json
import struct
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ContextManager, Iterable, Protocol

from .platform import ConflictError, FileSnapshot, repo_relative_path, resource_operation, snapshot_files


class ToolCancelled(RuntimeError):
    """Raised by a handler when a cooperative cancellation was requested."""


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
class Artifact:
    path: str
    role: str
    size: int
    sha256: str
    changed: bool

    def payload(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "role": self.role,
            "size": self.size,
            "sha256": self.sha256,
            "changed": self.changed,
        }


@dataclass(frozen=True)
class ToolResult:
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


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
    def __init__(self, job_id: str, repo_root: Path, emit: Callable[[str], None]) -> None:
        self.job_id = job_id
        self.repo_root = repo_root
        self._emit = emit
        self._cancel = threading.Event()

    def log(self, message: str) -> None:
        self._emit(str(message).rstrip("\r\n"))

    def request_cancel(self) -> None:
        self._cancel.set()

    def check_cancelled(self) -> None:
        if self._cancel.is_set():
            raise ToolCancelled("Cancellation requested")


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


def _relative(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def _snapshot(paths: Iterable[Path]) -> dict[Path, tuple[int, str]]:
    result: dict[Path, tuple[int, str]] = {}
    for path in paths:
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            continue
        result[path.resolve()] = (len(data), hashlib.sha256(data).hexdigest())
    return result


def collect_artifacts(repo_root, before, after) -> tuple[Artifact, ...]:
    artifacts = []
    for path in sorted(set(before) | set(after), key=str):
        current = after.get(path)
        if current is None:
            artifacts.append(Artifact(_relative(repo_root, path), "deleted", 0, "missing", True))
        else:
            artifacts.append(Artifact(_relative(repo_root, path), "output", *current, before.get(path) != current))
    return tuple(artifacts)


def validate_artifact_contract(
    repo_root: Path,
    artifacts: Iterable[Artifact],
    allowed_formats: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Validate the file-level contracts shared by all media tools."""
    allowed = {str(value).lower().lstrip(".") for value in allowed_formats}
    reports: list[dict[str, Any]] = []
    for artifact in artifacts:
        if artifact.role == "deleted":
            continue
        path = (repo_root / artifact.path).resolve()
        suffix = path.suffix.lower()
        report: dict[str, Any] = {"path": artifact.path, "format": suffix.lstrip(".") or "file", "valid": True}
        try:
            if allowed and suffix.lstrip(".") not in allowed:
                raise ValueError(
                    f"format {suffix.lstrip('.') or 'file'} is not declared by {artifact.role} contract"
                )
            data = path.read_bytes()
            if suffix == ".png":
                if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise ValueError("invalid PNG signature")
                report["width"] = int.from_bytes(data[16:20], "big")
                report["height"] = int.from_bytes(data[20:24], "big")
            elif suffix == ".dds":
                if len(data) < 128 or not data.startswith(b"DDS "):
                    raise ValueError("invalid DDS header")
                report["height"], report["width"] = struct.unpack_from("<II", data, 12)
                fourcc = data[84:88].decode("ascii", errors="replace").strip("\x00")
                if fourcc not in {"DXT1", "DXT5"}:
                    raise ValueError(f"unsupported DDS format {fourcc!r}")
                report["dds_format"] = fourcc
            elif suffix == ".json":
                json.loads(data.decode("utf-8-sig"))
            elif suffix in {".jpg", ".jpeg"} and not data.startswith(b"\xff\xd8"):
                raise ValueError("invalid JPEG signature")
        except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
            report["valid"] = False
            report["error"] = str(exc)
        reports.append(report)
    return reports


class Job:
    def __init__(self, job_id: str, handler: ToolHandler, options: dict[str, Any], repo_root: Path) -> None:
        self.id = job_id
        self.handler = handler
        self.options = options
        self.repo_root = repo_root
        self.status = "queued"
        self.lines: list[str] = []
        self.returncode: int | None = None
        self.error: str | None = None
        self.message = ""
        self.metadata: dict[str, Any] = {}
        self.artifacts: tuple[Artifact, ...] = ()
        self.source_snapshots: list[dict[str, Any]] = []
        self.declared_outputs: list[str] = []
        self.missing_outputs: list[str] = []
        self.outputs_may_be_partial = False
        self.created_at = time.time()
        self.finished_at: float | None = None
        self.context = ToolContext(job_id, repo_root, self._append)

    def _append(self, line: str) -> None:
        self.lines.append(line)
        del self.lines[:-500]

    def payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tool": self.handler.spec.id,
            "status": self.status,
            "options": self.options,
            "lines": self.lines[-300:],
            "returncode": self.returncode,
            "error": self.error,
            "message": self.message,
            "metadata": self.metadata,
            "resource_ids": list(self.handler.spec.resource_ids),
            "artifact_formats": list(self.handler.spec.artifact_formats),
            "source_snapshots": self.source_snapshots,
            "declared_outputs": self.declared_outputs,
            "missing_outputs": self.missing_outputs,
            "outputs_may_be_partial": self.outputs_may_be_partial,
            "artifacts": [artifact.payload() for artifact in self.artifacts],
            "created_at": self.created_at,
            "finished_at": self.finished_at,
        }


class JobManager:
    def __init__(self, registry: ToolRegistry, repo_root: Path) -> None:
        self.registry = registry
        self.repo_root = repo_root
        self._jobs: dict[str, Job] = {}
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="tv-tool")
        self._execution_lock = threading.RLock()

    def submit(self, tool_id: str, options: dict[str, Any]) -> Job:
        handler = self.registry.get(tool_id)
        normalized = handler.validate(options)
        job = Job(uuid.uuid4().hex[:12], handler, normalized, self.repo_root)
        with self._lock:
            self._jobs[job.id] = job
        self._executor.submit(self._run, job)
        return job

    def get(self, job_id: str) -> Job:
        with self._lock:
            try:
                return self._jobs[job_id]
            except KeyError as exc:
                raise KeyError(f"Unknown job: {job_id}") from exc

    def cancel(self, job_id: str) -> Job:
        job = self.get(job_id)
        with self._lock:
            if job.status in {"queued", "running"}:
                job.status = "cancelling"
                job.context.request_cancel()
        return job

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)

    def _run(self, job: Job) -> None:
        try:
            with self._execution_lock, resource_operation(job.handler.spec.resource_ids, blocking=False):
                job.context.check_cancelled()
                with self._lock:
                    job.status = "running"
                with capture_script_output(job.context), job.handler.prepare(job.options) as plan:
                    outputs = tuple(dict.fromkeys(path.resolve() for path in (*plan.outputs, *plan.optional_outputs)))
                    for path in outputs:
                        repo_relative_path(path, self.repo_root)
                    job.source_snapshots = [vars(item) for item in plan.inputs]
                    job.declared_outputs = [_relative(self.repo_root, path) for path in outputs]
                    inputs = tuple(self.repo_root / item.path for item in plan.inputs)
                    job.context.check_cancelled()
                    if snapshot_files(inputs, repo_root=self.repo_root) != plan.inputs:
                        raise ConflictError("Declared inputs changed before job execution")
                    before = _snapshot(outputs)
                    try:
                        result = plan.run(job.context)
                        job.message = result.message
                        job.metadata = dict(result.metadata)
                    finally:
                        # Preserve the real disk outcome even if run() raises or is cancelled.
                        after = _snapshot(outputs)
                        job.artifacts = collect_artifacts(self.repo_root, before, after)
                        job.missing_outputs = [
                            _relative(self.repo_root, path) for path in plan.outputs
                            if path.resolve() not in after
                        ]
                        job.metadata["output_validation"] = validate_artifact_contract(
                            self.repo_root, job.artifacts, job.handler.spec.artifact_formats
                        )
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
                    with self._lock:
                        job.context.check_cancelled()
                        job.status = "succeeded"
                        job.returncode = 0
        except Exception as exc:  # surfaced through the job API, including partial writes
            with self._lock:
                try:
                    job.context.check_cancelled()
                except ToolCancelled as cancelled:
                    exc = cancelled
                job.error = str(exc)
                job.outputs_may_be_partial = any(artifact.changed for artifact in job.artifacts)
                job.status = "cancelled" if isinstance(exc, ToolCancelled) else "failed"
                job.returncode = 130 if job.status == "cancelled" else 1
                job.context.log(f"{job.status}: {exc}")
                if job.outputs_may_be_partial:
                    job.context.log("Output files were changed on disk; no rollback was performed.")
        finally:
            job.finished_at = time.time()


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
