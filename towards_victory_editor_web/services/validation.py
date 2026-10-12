from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATION_TIMEOUT_SECONDS = 180
OUTPUT_TAIL_LIMIT = 4096
MOD_ROOT_NAMES = ("src", "src_engineering_department", "src_court_positions", "src_eureka")
VALIDATED_SUFFIXES = {".txt", ".gui", ".yml", ".yaml", ".md", ".py"}
UTF8_BOM = b"\xef\xbb\xbf"


class ValidationExecutionError(RuntimeError):
    def __init__(self, message: str, status_code: int, output_tail: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.output_tail = output_tail


def _output_tail(stdout: str | bytes | None, stderr: str | bytes | None) -> str:
    parts = [
        output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output
        for output in (stdout, stderr) if output
    ]
    return "\n".join(parts)[-OUTPUT_TAIL_LIMIT:]


def _allowed_root(name: str) -> bool:
    return name == "data" or name.startswith(("src", "scripts"))


def _diagnostic(issue: dict[str, Any]) -> dict[str, Any]:
    diagnostic = dict(issue)
    diagnostic["rule"] = str(issue.get("rule", "unknown"))
    message = issue.get("message") or issue.get("raw")
    if message is None:
        message = f"Bad: {issue.get('bad', '')} -> {issue.get('fix', '')}"
    diagnostic["message"] = str(message)
    if diagnostic["rule"] == "localization":
        diagnostic["message"] = f"[LOC] {message}"
    if "file" in diagnostic:
        diagnostic["file"] = str(diagnostic["file"]).replace("\\", "/")
    return diagnostic


class ValidationService:
    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or REPO_ROOT).resolve()

    def _check_resolved_path(self, path: Path) -> None:
        try:
            relative = path.resolve().relative_to(self.repo_root)
        except (OSError, RuntimeError, ValueError) as exc:
            raise ValueError(f"Validation path escapes the repository: {path}") from exc
        if not relative.parts or not _allowed_root(relative.parts[0]):
            raise ValueError(f"Validation path is outside data/, src*/ or scripts*/: {path}")

    def _check_tree(self, path: Path) -> None:
        self._check_resolved_path(path)
        if path.is_dir():
            for descendant in path.rglob("*"):
                self._check_resolved_path(descendant)

    def _target(self, name: str) -> str:
        normalized = name.replace("\\", "/")
        relative = PurePosixPath(normalized)
        if (
            not normalized or "\x00" in normalized or ":" in normalized
            or relative.is_absolute() or PureWindowsPath(name).drive
            or ".." in relative.parts or not relative.parts
            or not _allowed_root(relative.parts[0])
        ):
            raise ValueError(f"Expected a repository-relative path under data/, src*/ or scripts*/: {name}")
        self._check_tree(self.repo_root / relative)
        return relative.as_posix()

    def _bom_candidates(self, targets: list[str], changed: bool) -> dict[Path, str]:
        roots = (
            [self.repo_root / name for name in MOD_ROOT_NAMES]
            if changed or not targets else [self.repo_root / target for target in targets]
        )
        candidates: dict[Path, str] = {}
        for root in roots:
            direct_file = root.is_file()
            paths = [root] if direct_file else root.rglob("*")
            for path in paths:
                if not path.is_file() or not direct_file and path.suffix not in VALIDATED_SUFFIXES:
                    continue
                if path.relative_to(self.repo_root).parts[0] not in MOD_ROOT_NAMES:
                    continue
                self._check_resolved_path(path)
                raw = path.read_bytes()
                if not raw.startswith(UTF8_BOM):
                    candidates[path] = hashlib.sha256(raw).hexdigest()
        return candidates

    def run(
        self,
        files: list[str] | None = None,
        changed: bool | None = None,
        fix: bool = False,
        *,
        allow_fix: bool = False,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        if fix and not allow_fix:
            raise ValueError("fix:true is only available to local callers")
        targets = [self._target(name) for name in files or []]
        use_changed = changed if changed is not None else not targets
        for name in MOD_ROOT_NAMES:
            self._check_tree(self.repo_root / name)
        script = self.repo_root / "scripts" / "validate.py"
        self._check_resolved_path(script)
        command = [sys.executable, str(script), "--ai-report", *targets]
        if use_changed:
            command.append("--changed")
        if fix:
            command.append("--fix")
        candidates = self._bom_candidates(targets, use_changed) if fix else {}
        try:
            result = subprocess.run(
                command, cwd=self.repo_root, capture_output=True, text=True,
                encoding="utf-8", errors="replace", check=False, shell=False,
                timeout=VALIDATION_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValidationExecutionError(
                "Validation timed out after 180 seconds", 504,
                _output_tail(exc.stdout, exc.stderr),
            ) from exc
        except OSError as exc:
            raise ValidationExecutionError(f"Could not start validator: {exc}", 500, "") from exc
        output_tail = _output_tail(result.stdout, result.stderr)
        try:
            report = json.loads(result.stdout)
            if (
                not isinstance(report, dict) or type(report.get("pass")) is not bool
                or type(report.get("files_checked")) is not int or report["files_checked"] < 0
                or any(
                    not isinstance(report.get(key), list)
                    or any(not isinstance(issue, dict) for issue in report[key])
                    for key in ("errors", "warnings")
                )
                or result.returncode != (0 if report["pass"] else 1)
            ):
                raise ValueError("Invalid validation report")
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValidationExecutionError("Validator did not return a valid JSON report", 500, output_tail) from exc
        fixed = []
        for path, before_hash in candidates.items():
            if not path.is_file():
                continue
            self._check_resolved_path(path)
            raw = path.read_bytes()
            if raw.startswith(UTF8_BOM) and hashlib.sha256(raw[len(UTF8_BOM):]).hexdigest() == before_hash:
                fixed.append(path.relative_to(self.repo_root).as_posix())
        return {
            "pass": report["pass"],
            "errors": [_diagnostic(issue) for issue in report["errors"]],
            "warnings": [_diagnostic(issue) for issue in report["warnings"]],
            "files_checked": report["files_checked"],
            "command": command,
            "duration_ms": round((time.perf_counter() - started) * 1000),
            "fixed": sorted(fixed),
        }
