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
from typing import Any, Callable, Iterable, Protocol


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

    def payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "group": self.group,
            "interactive": self.interactive,
            "options": [option.payload() for option in self.options],
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
    output_paths: tuple[Path, ...] = ()


class ToolHandler(Protocol):
    spec: ToolSpec

    def validate(self, options: dict[str, Any]) -> dict[str, Any]: ...

    def roots(self, options: dict[str, Any]) -> tuple[Path, ...]: ...

    def run(self, options: dict[str, Any], context: "ToolContext") -> ToolResult: ...


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
    for root in paths:
        if not root.exists():
            continue
        candidates = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
        for path in candidates:
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            result[path.resolve()] = (path.stat().st_size, digest.hexdigest())
    return result


def collect_artifacts(repo_root: Path, before: dict[Path, tuple[int, str]], after: dict[Path, tuple[int, str]], output_paths: Iterable[Path]) -> tuple[Artifact, ...]:
    explicit = {path.resolve() for path in output_paths}
    changed = set(before) | set(after) | explicit
    artifacts: list[Artifact] = []
    for path in sorted(changed, key=str):
        current = after.get(path)
        if current is None:
            continue
        previous = before.get(path)
        if previous == current and path not in explicit:
            continue
        role = "output" if path in explicit else "changed"
        artifacts.append(Artifact(_relative(repo_root, path), role, current[0], current[1], previous != current))
    return tuple(artifacts)


def validate_artifact_contract(repo_root: Path, artifacts: Iterable[Artifact]) -> list[dict[str, Any]]:
    """Validate the file-level contracts shared by all media tools."""
    reports: list[dict[str, Any]] = []
    for artifact in artifacts:
        path = (repo_root / artifact.path).resolve()
        suffix = path.suffix.lower()
        report: dict[str, Any] = {"path": artifact.path, "format": suffix.lstrip(".") or "file", "valid": True}
        try:
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
            raise RuntimeError(f"Output validation failed for {artifact.path}: {exc}") from exc
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

    def _run(self, job: Job) -> None:
        with self._lock:
            if job.status != "queued":
                job.status = "cancelled"
                job.finished_at = time.time()
                return
            job.status = "running"
        try:
            with self._execution_lock:
                before = _snapshot(job.handler.roots(job.options))
                result = job.handler.run(job.options, job.context)
                after = _snapshot(job.handler.roots(job.options))
            job.context.check_cancelled()
            job.message = result.message
            job.metadata = result.metadata
            job.artifacts = collect_artifacts(self.repo_root, before, after, result.output_paths)
            job.metadata["output_validation"] = validate_artifact_contract(self.repo_root, job.artifacts)
            with self._lock:
                job.status = "succeeded"
                job.returncode = 0
        except ToolCancelled as exc:
            job.error = str(exc)
            with self._lock:
                job.status = "cancelled"
                job.returncode = 130
        except Exception as exc:  # noqa: BLE001 - surfaced through the job API.
            job.error = str(exc)
            with self._lock:
                job.status = "failed"
                job.returncode = 1
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
