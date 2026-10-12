"""Sequential, registered generator runs in an isolated repository copy."""

from __future__ import annotations

import copy
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from scripts_engineering_department.wonder_mechanics._core import load_yaml

from .artifacts import collect_artifacts, snapshot_artifacts, validate_artifact_contract
from .operation_store import OperationStore
from .platform import (
    ConflictError, OperationLog, RollbackError, atomic_write_files, file_transaction,
    repo_relative_path, run_operation, snapshot_files,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
STEP_TIMEOUT_SECONDS = 120
OUTPUT_TAIL_LIMIT = 4096
REGISTRY_PATH = "data/generated_files.yaml"
EXCLUDED_NAMES = {
    ".git", ".editor_state", ".agents", ".codex", ".claude", ".vscode",
    ".pytest_cache", "__pycache__", "node_modules",
}
WRITE_VIOLATION = "Unregistered write outside staging"
STAGED_RUNNER = r'''
import os
import runpy
import sys
from pathlib import Path

root = Path.cwd().resolve()
script = Path(sys.argv[1])
sys.argv = [str(script)]
sys.path.insert(0, str(script.parent))

def guard(event, arguments):
    paths = ()
    if event == "open":
        path, mode, flags = arguments
        if isinstance(path, int) or not (flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
            return
        paths = (path,)
    elif event in {"os.rename", "os.replace"}:
        paths = arguments[:2]
    elif event in {"os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.utime", "os.truncate"}:
        paths = arguments[:1]
    elif event in {"os.symlink", "os.link", "subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn"}:
        raise PermissionError("Unregistered write outside staging: " + event)
    for path in paths:
        if isinstance(path, int) or not Path(os.fsdecode(path)).resolve().is_relative_to(root):
            raise PermissionError("Unregistered write outside staging: " + str(path))

sys.addaudithook(guard)
runpy.run_path(str(script), run_name="__main__")
'''


class GeneratorRunError(RuntimeError):
    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.report: dict[str, Any] = {}


def _excluded(name: str) -> bool:
    return name in EXCLUDED_NAMES or name.startswith(".pytest-")


def _reject_link(path: Path) -> None:
    attributes = path.lstat()
    if path.is_symlink() or getattr(attributes, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        raise ValueError(f"Repository links are not allowed: {path}")


def _relative_path(root: Path, value: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError(f"Invalid repository path: {value!r}")
    normalized = value.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    if PureWindowsPath(value).drive or normalized.startswith("/") or ".." in parts or any(_excluded(part) for part in parts):
        raise ValueError(f"Invalid repository path: {value}")
    path = root
    for part in parts:
        path /= part
        if path.exists() or path.is_symlink():
            _reject_link(path)
    return repo_relative_path(path, root)


def _tree_snapshot(root: Path) -> dict[Path, tuple[int, str]]:
    paths = []
    def fail(error: OSError) -> None:
        raise error
    for directory, directories, files in os.walk(root, onerror=fail):
        for name in (*directories, *files):
            _reject_link(Path(directory) / name)
        paths.extend(Path(directory) / name for name in files)
    return snapshot_artifacts(paths)


def _copy_ignore(directory: str, names: list[str]) -> list[str]:
    ignored = [name for name in names if _excluded(name)]
    for name in set(names) - set(ignored):
        _reject_link(Path(directory) / name)
    return ignored


def _resource_ids(outputs: list[str]) -> tuple[str, ...]:
    resources = set()
    for output in outputs:
        lowered = output.lower()
        if "/localization/" in lowered:
            resources.add("editor.localization")
        if "wonder" in lowered or "engineering_department" in lowered:
            resources.update(("editor.wonder", "editor.cost_reward"))
        if "victory" in lowered:
            resources.update(("editor.victory_tree", "editor.cost_reward"))
        if "cost_reward" in lowered or "task_pool" in lowered:
            resources.add("editor.cost_reward")
        if "image_crops" in lowered or "wonder" in lowered and Path(output).suffix.lower() in {".png", ".dds", ".jpg", ".jpeg"}:
            resources.add("editor.wonder_crop")
    return tuple(sorted(resources))


class GeneratorRunService:
    def __init__(self, operation_store: OperationStore | None = None, *, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or REPO_ROOT).resolve()
        self.operation_store = operation_store

    def generators(self) -> list[dict[str, Any]]:
        catalog: dict[str, dict[str, Any]] = {}
        for entry in load_yaml(self.repo_root / REGISTRY_PATH)["generated"]:
            script = _relative_path(self.repo_root, entry["script"])
            parts = PurePosixPath(script).parts
            if len(parts) < 2 or not (parts[0] == "scripts" or parts[0].startswith("scripts_")) or not script.endswith(".py"):
                raise ValueError(f"Invalid registered generator: {script}")
            if not (self.repo_root / script).is_file():
                raise ValueError(f"Missing registered generator: {script}")
            generator = catalog.setdefault(script, {
                "script": script, "root": "src" + parts[0][len("scripts"):],
                "domain": "/".join(parts[1:-1]) or Path(script).stem.removeprefix("gen_"),
                "data_inputs": set(), "outputs": set(),
            })
            generator["outputs"].add(_relative_path(self.repo_root, entry["output"]))
            for source in str(entry.get("data", "")).split(" + "):
                source = source.split(" (", 1)[0].strip()
                if source:
                    generator["data_inputs"].add(_relative_path(self.repo_root, source))
        return sorted(({
            **generator, "data_inputs": sorted(generator["data_inputs"]), "outputs": sorted(generator["outputs"]),
        } for generator in catalog.values()), key=lambda item: (item["root"], item["domain"], item["script"]))

    def _select(self, scripts: list[str]) -> list[dict[str, Any]]:
        if not scripts or len(set(scripts)) != len(scripts):
            raise ValueError("scripts must be a non-empty list without duplicates")
        catalog = {item["script"]: item for item in self.generators()}
        unknown = [script for script in scripts if script not in catalog]
        if unknown:
            raise ValueError("Unknown generators: " + ", ".join(unknown))
        selected = [catalog[script] for script in scripts]
        owners: dict[Path, str] = {}
        for generator in selected:
            for output in generator["outputs"]:
                path = (self.repo_root / output).resolve()
                for previous, owner in owners.items():
                    if path == previous or path in previous.parents or previous in path.parents:
                        raise ValueError(f"Intersecting outputs: {output} ({owner}, {generator['script']}; {repo_relative_path(previous, self.repo_root)})")
                owners[path] = generator["script"]
        return selected

    def _tracked_snapshot(self, selected: list[dict[str, Any]]) -> tuple:
        paths = {self.repo_root / REGISTRY_PATH}
        for generator in selected:
            paths.add(self.repo_root / generator["script"])
            paths.update(self.repo_root / output for output in generator["outputs"])
            for source in generator["data_inputs"]:
                if not any(character in source for character in "*?["):
                    paths.add(self.repo_root / source)
                for path in self.repo_root.glob(source):
                    paths.update(path.rglob("*") if path.is_dir() else (path,))
        files = [path for path in paths if not path.is_dir()]
        return snapshot_files(sorted(files), repo_root=self.repo_root)

    def run(self, scripts: list[str], dry_run: bool = False) -> dict[str, Any]:
        selected = self._select(scripts)
        outputs = [output for generator in selected for output in generator["outputs"]]
        details: dict[str, Any] = {
            "results": [{"script": script, "status": "skipped", "exit_code": None, "duration_ms": 0, "output_tail": ""} for script in scripts],
            "artifacts": [], "rollback": {"status": "not_needed", "errors": []},
        }
        operation = OperationLog(
            "generator_run", _resource_ids(outputs), store=self.operation_store,
            snapshot_details=lambda: copy.deepcopy(details),
        )

        def execute() -> None:
            if dry_run:
                return
            tracked_before = self._tracked_snapshot(selected)
            formal_paths = [self.repo_root / output for output in outputs]
            before = snapshot_artifacts(formal_paths)
            with tempfile.TemporaryDirectory(prefix="tv-generators-") as temporary:
                staging = Path(temporary) / "repo"
                shutil.copytree(self.repo_root, staging, ignore=_copy_ignore)
                if self._tracked_snapshot(selected) != tracked_before:
                    raise ConflictError("Registered generator inputs or outputs changed during staging")
                staged_before = _tree_snapshot(staging)
                for generator, result in zip(selected, details["results"]):
                    step_before = staged_before
                    started = time.monotonic()
                    operation.event(f"Running {generator['script']}")
                    try:
                        try:
                            process = subprocess.run(
                                [sys.executable, "-B", "-u", "-c", STAGED_RUNNER, str(staging / generator["script"])], cwd=staging,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(staging)},
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace", check=False,
                                timeout=STEP_TIMEOUT_SECONDS,
                            )
                        except subprocess.TimeoutExpired as exc:
                            result["status"] = "timed_out"
                            captured = exc.stdout or ""
                            if isinstance(captured, bytes):
                                captured = captured.decode("utf-8", errors="replace")
                            result["output_tail"] = captured[-OUTPUT_TAIL_LIMIT:]
                            raise GeneratorRunError(f"{generator['script']} timed out after {STEP_TIMEOUT_SECONDS:g}s", 504) from exc
                        result.update(exit_code=process.returncode, output_tail=process.stdout[-OUTPUT_TAIL_LIMIT:])
                        if process.returncode and WRITE_VIOLATION in result["output_tail"]:
                            raise GeneratorRunError(result["output_tail"], 400)
                        staged_before = _tree_snapshot(staging)
                        allowed = {staging / output for output in generator["outputs"]}
                        extras = [repo_relative_path(path, staging) for path in set(step_before) | set(staged_before)
                                  if step_before.get(path) != staged_before.get(path) and path not in allowed]
                        if extras:
                            raise GeneratorRunError("Unregistered artifacts: " + ", ".join(sorted(extras)), 400)
                        if process.returncode:
                            raise GeneratorRunError(f"{generator['script']} exited with {process.returncode}")
                        missing = [output for output in generator["outputs"]
                                   if staging / output not in staged_before and staging / output not in step_before]
                        if missing:
                            raise GeneratorRunError("Missing registered outputs: " + ", ".join(missing), 400)
                        artifacts = collect_artifacts(staging, {path: step_before[path] for path in allowed if path in step_before},
                                                      {path: staged_before[path] for path in allowed if path in staged_before})
                        failures = [item for item in validate_artifact_contract(staging, artifacts) if not item["valid"]]
                        if failures:
                            raise GeneratorRunError("File-level artifact validation failed: " + "; ".join(
                                f"{item['path']}: {item['error']}" for item in failures), 400)
                        result["status"] = "succeeded"
                    except Exception:
                        if result["status"] != "timed_out":
                            result["status"] = "failed"
                        raise
                    finally:
                        result["duration_ms"] = round((time.monotonic() - started) * 1000)
                        operation.checkpoint()
                after = {self.repo_root / output: staged_before[staging / output] for output in outputs if staging / output in staged_before}
                details["artifacts"] = [{"path": artifact.path, "size": artifact.size,
                                         "sha256": artifact.sha256, "changed": artifact.changed}
                                        for artifact in collect_artifacts(self.repo_root, before, after)]
                if self._tracked_snapshot(selected) != tracked_before:
                    raise ConflictError("Registered generator inputs or outputs changed before publication")
                try:
                    with file_transaction(formal_paths, reload=lambda: None):
                        atomic_write_files({path: (staging / path.relative_to(self.repo_root)).read_bytes()
                                            for path in after if before.get(path) != after[path]})
                        for path in set(before) - set(after):
                            path.unlink()
                except Exception as exc:
                    details["rollback"] = {"status": "failed" if isinstance(exc, RollbackError) else "completed",
                                           "errors": exc.errors if isinstance(exc, RollbackError) else []}
                    raise

        try:
            run_operation(operation, execute)
        except Exception as exc:
            error = exc if isinstance(exc, GeneratorRunError) else GeneratorRunError(str(exc), 409 if isinstance(exc, ConflictError) else 500)
            error.report = {"operation_id": operation.id, "operation": operation.payload(), **copy.deepcopy(details)}
            if error is exc:
                raise
            raise error from exc
        return {"operation_id": operation.id, "operation": operation.payload(), **copy.deepcopy(details)}


def build_check_report() -> list[str]:
    generators = GeneratorRunService().generators()
    groups = Counter((item["root"], item["domain"]) for item in generators)
    return [f"[PASS] runnable generators: {len(generators)}", *[
        f"[PASS] generators {root}/{domain}: {count}" for (root, domain), count in sorted(groups.items())
    ]]
