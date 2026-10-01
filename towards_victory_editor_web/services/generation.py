"""Prepared generator DAGs and a synchronous, artifact-aware command runner.

The caller owns the file transaction; this runner records attempted disk results
before raising, so rollback does not erase the diagnosis.
"""
from __future__ import annotations

import math
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from .artifacts import collect_artifacts, snapshot_artifacts, validate_artifact_contract
from .platform import generated_outputs_by_script, repo_relative_path


@dataclass(frozen=True)
class GeneratorSpec:
    script: str
    depends_on: tuple[str, ...] = ()
    # Direct file inputs used for dependency edges (e.g. merged GUI fragments).
    # This is not a complete transitive Python/data import graph.
    inputs: tuple[str, ...] = ()
    extra_outputs: tuple[str, ...] = ()
    timeout_seconds: float = 120


@dataclass(frozen=True)
class GenerationStep:
    spec: GeneratorSpec
    outputs: tuple[Path, ...]


@dataclass(frozen=True)
class GenerationPlan:
    repo_root: Path
    steps: tuple[GenerationStep, ...]

    @property
    def outputs(self) -> tuple[Path, ...]:
        return tuple(dict.fromkeys(path for step in self.steps for path in step.outputs))

    def payload(self) -> dict:
        return {
            "steps": [
                {
                    "id": step.spec.script,
                    "script": step.spec.script,
                    "depends_on": list(step.spec.depends_on),
                    "inputs": list(step.spec.inputs),
                    "outputs": [repo_relative_path(path, self.repo_root) for path in step.outputs],
                    "timeout_seconds": step.spec.timeout_seconds,
                }
                for step in self.steps
            ],
            "outputs": [repo_relative_path(path, self.repo_root) for path in self.outputs],
        }


class GenerationError(RuntimeError):
    def __init__(self, message: str, report: dict) -> None:
        self.report = report
        super().__init__(message)


def _order_generators(
    catalog: dict[str, GeneratorSpec], roots: Iterable[str],
) -> tuple[list[str], dict[str, set[str]]]:
    """Topologically order roots and their upstream closure."""
    ordered: list[str] = []
    visiting = set()
    ancestors: dict[str, set[str]] = {}

    def visit(script: str) -> None:
        if script in visiting:
            raise ValueError(f"Generator dependency cycle: {script}")
        if script in ancestors:
            return
        if script not in catalog:
            raise ValueError(f"Unknown generator dependency: {script}")
        visiting.add(script)
        dependencies = set()
        for dependency in catalog[script].depends_on:
            visit(dependency)
            dependencies.update((dependency, *ancestors[dependency]))
        visiting.remove(script)
        ancestors[script] = dependencies
        ordered.append(script)

    for script in roots:
        visit(script)
    return ordered, ancestors


def build_generation_plan(
    specs: Iterable[GeneratorSpec], roots: Iterable[str], *, repo_root: Path,
) -> GenerationPlan:
    """Plan roots, their upstream dependencies, and every downstream consumer.

    A generator joins the plan when it depends on a planned generator or reads
    one of its outputs, so a partial plan cannot leave a merge step stale.
    """
    catalog = {}
    for spec in specs:
        if spec.script in catalog:
            raise ValueError(f"Duplicate generator: {spec.script}")
        catalog[spec.script] = spec
    selected = list(dict.fromkeys(roots))
    while True:
        ordered, ancestors = _order_generators(catalog, selected)
        outputs = generated_outputs_by_script(
            ordered, repo_root=repo_root,
            extra_outputs={script: catalog[script].extra_outputs for script in ordered},
        )
        produced = {path for script in ordered for path in outputs[script]}
        dependents = [
            spec.script for spec in catalog.values()
            if spec.script not in ancestors and (
                any(dependency in ancestors for dependency in spec.depends_on)
                or any((repo_root / source).resolve() in produced for source in spec.inputs)
            )
        ]
        if not dependents:
            break
        selected.extend(dependents)
    writers: dict[Path, list[str]] = {}
    for script in ordered:
        if not math.isfinite(catalog[script].timeout_seconds) or catalog[script].timeout_seconds <= 0:
            raise ValueError(f"Generator timeout must be finite and positive: {script}")
        path = repo_root / script
        repo_relative_path(path, repo_root)
        if not path.is_file():
            raise ValueError(f"Missing generator script: {script}")
        for path in outputs[script]:
            previous = writers.setdefault(path, [])
            if any(writer not in ancestors[script] for writer in previous):
                raise ValueError(f"Unordered generators write the same output: {path}")
            previous.append(script)
    for script in ordered:
        for source in catalog[script].inputs:
            path = (repo_root / source).resolve()
            repo_relative_path(path, repo_root)
            producers = [writer for writer in writers.get(path, ()) if writer != script]
            # A shared in-place output can also have downstream writers.
            upstream = [writer for writer in producers if writer in ancestors[script]]
            if producers and not upstream and path not in outputs[script]:
                raise ValueError(f"Missing dependency for {script} input: {source}")
            if not upstream and not path.is_file():
                raise ValueError(f"Missing generator input for {script}: {source}")
    return GenerationPlan(repo_root, tuple(GenerationStep(catalog[script], outputs[script]) for script in ordered))


def run_generation(plan: GenerationPlan, *, log: Callable[[str], None]) -> dict:
    report = {
        "operation_id": uuid.uuid4().hex,
        "status": "running",
        "plan": plan.payload(),
        "steps": [{"id": step.spec.script, "status": "pending"} for step in plan.steps],
        "artifacts": [], "missing_outputs": [], "output_validation": [],
    }
    before = snapshot_artifacts(plan.outputs)

    def collect_report() -> None:
        after = snapshot_artifacts(plan.outputs)
        artifacts = collect_artifacts(plan.repo_root, before, after)
        report["artifacts"] = [artifact.payload() for artifact in artifacts]
        report["missing_outputs"] = [repo_relative_path(path, plan.repo_root)
                                     for path in plan.outputs if path not in after]
        report["output_validation"] = validate_artifact_contract(plan.repo_root, artifacts, ("txt", "gui", "yml"))

    log(f"\n[regen {report['operation_id']}] Starting {len(plan.steps)} generators\n")
    try:
        for step, result in zip(plan.steps, report["steps"]):
            started = time.monotonic()
            result["status"] = "running"
            try:
                for source in step.spec.inputs:
                    if not (plan.repo_root / source).is_file():
                        raise RuntimeError(f"Missing generator input: {source}")
                command = [sys.executable, step.spec.script]
                log(f"$ {' '.join(command)}\n")
                try:
                    process = subprocess.run(
                        command, cwd=plan.repo_root, text=True, encoding="utf-8", errors="replace",
                        capture_output=True, check=False, timeout=step.spec.timeout_seconds,
                    )
                except subprocess.TimeoutExpired as exc:
                    # run() kills and waits for the child before raising. Recovery
                    # can then restore files without the timed-out writer racing it.
                    for output in (exc.stdout, exc.stderr):
                        if output:
                            log(output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output)
                    result["timed_out"] = True
                    raise RuntimeError(
                        f"{step.spec.script} timed out after {step.spec.timeout_seconds:g}s. See log for details."
                    ) from exc
                result["returncode"] = process.returncode
                if process.stdout:
                    log(process.stdout)
                if process.stderr:
                    log(process.stderr)
                after = snapshot_artifacts(step.outputs)
                result["missing_outputs"] = [repo_relative_path(path, plan.repo_root)
                                             for path in step.outputs if path not in after]
                artifacts = collect_artifacts(plan.repo_root, {}, after)
                result["output_validation"] = validate_artifact_contract(plan.repo_root, artifacts, ("txt", "gui", "yml"))
                if process.returncode:
                    raise RuntimeError(f"{step.spec.script} exited with {process.returncode}. See log for details.")
                if result["missing_outputs"]:
                    raise RuntimeError("Missing declared outputs: " + ", ".join(result["missing_outputs"]))
                failures = [item for item in result["output_validation"] if not item["valid"]]
                if failures:
                    raise RuntimeError("Output validation failed: " + "; ".join(
                        f"{item['path']}: {item['error']}" for item in failures))
                result["status"] = "succeeded"
            except Exception as exc:
                result.update(status="failed", error=str(exc))
                raise
            finally:
                result["duration_seconds"] = round(time.monotonic() - started, 3)
        # A later merge can change an earlier output; also validate the final set.
        collect_report()
        failures = [item for item in report["output_validation"] if not item["valid"]]
        if report["missing_outputs"] or failures:
            raise RuntimeError("Final output validation failed: " + "; ".join(
                [*report["missing_outputs"], *(f"{item['path']}: {item['error']}" for item in failures)]))
        report["status"] = "succeeded"
        log("[regen] Complete\n")
    except Exception as exc:
        report.update(status="failed", error=str(exc))
        for result in report["steps"]:
            if result["status"] == "pending":
                result["status"] = "skipped"
        try:
            collect_report()
        except Exception as collection_error:
            # Disk/permission errors in diagnostics must not hide the execution error.
            report["collection_error"] = str(collection_error)
        raise GenerationError(str(exc), report) from exc
    return report
