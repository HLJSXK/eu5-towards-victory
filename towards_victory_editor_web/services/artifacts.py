"""File-level artifact contracts shared by jobs and editor generation plans."""

from __future__ import annotations

import hashlib
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def _validate_script(data: bytes, path: Path) -> None:
    """Check encoding and delimiters, leaving Jomini semantics to domain checks."""
    if {"common", "events", "gui"}.intersection(path.parts[:-1]) and not data.startswith(b"\xef\xbb\xbf"):
        raise ValueError("game scripts under common/, events/ or gui/ require UTF-8 BOM")
    text = data.decode("utf-8-sig")
    if not text.strip() or "\x00" in text:
        raise ValueError("empty or binary script output")
    depth = 0
    quoted = escaped = comment = False
    line = 1
    for char in text:
        if char == "\n":
            line += 1
            comment = False
        if comment:
            continue
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == "#":
            comment = True
        elif char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                raise ValueError(f"unexpected closing brace at line {line}")
    if quoted or depth:
        raise ValueError(f"unterminated string or block at line {line}")


def _validate_localization(data: bytes, path: Path) -> None:
    if not data.startswith(b"\xef\xbb\xbf"):
        raise ValueError("localization requires UTF-8 BOM")
    lines = [line.strip() for line in data.decode("utf-8-sig").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    if not lines or not re.fullmatch(r"l_[a-z_]+:", lines[0]):
        raise ValueError("missing localization language header")
    if "_l_" in path.stem and lines[0] != "l_" + path.stem.rsplit("_l_", 1)[1] + ":":
        raise ValueError("localization language does not match filename")
    keys = set()
    for line in lines[1:]:
        # EU5 localization permits literal interior quotes (e.g. vanilla
        # government_l_english.yml). Check the physical outer quotes,
        # not JSON/YAML string escaping rules.
        match = re.fullmatch(r'([^\s:]+):\d*\s*".*"\s*(?:#.*)?', line)
        if not match:
            raise ValueError(f"malformed localization entry: {line[:120]}")
        if match[1] in keys:
            raise ValueError(f"duplicate localization key: {match[1]}")
        keys.add(match[1])
    if not keys:
        raise ValueError("localization has no entries")


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


def artifact_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def snapshot_artifacts(paths: Iterable[Path]) -> dict[Path, tuple[int, str]]:
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
            artifacts.append(Artifact(artifact_path(repo_root, path), "deleted", 0, "missing", True))
        else:
            artifacts.append(Artifact(artifact_path(repo_root, path), "output", *current, before.get(path) != current))
    return tuple(artifacts)


def validate_artifact_contract(
    repo_root: Path,
    artifacts: Iterable[Artifact],
    allowed_formats: Iterable[str] = (),
) -> list[dict[str, Any]]:
    """Validate declared media formats and generated script/localization files."""
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
            elif suffix == ".yml":
                _validate_localization(data, path)
            elif suffix in {".txt", ".gui"}:
                _validate_script(data, Path(artifact.path))
            elif suffix in {".jpg", ".jpeg"} and not data.startswith(b"\xff\xd8"):
                raise ValueError("invalid JPEG signature")
        except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
            report["valid"] = False
            report["error"] = str(exc)
        reports.append(report)
    return reports
