"""Small platform contracts shared by editor adapters.

The web workspace edits repository files directly, so the platform boundary
needs explicit source descriptors and an atomic commit primitive before more
editors are migrated.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


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
        data = path.read_bytes()
        resolved = path.resolve()
        display_path = str(resolved)
        if repo_root is not None:
            try:
                display_path = str(resolved.relative_to(repo_root.resolve())).replace("\\", "/")
            except ValueError:
                pass
        snapshots.append(FileSnapshot(display_path, hashlib.sha256(data).hexdigest(), len(data)))
    return tuple(snapshots)


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


def yaml_bytes(path: Path, payload: object) -> bytes:
    """Serialize a YAML document while preserving its leading comments/encoding."""
    import codecs

    from scripts_engineering_department.wonder_mechanics.io import dump_yaml_document
    from scripts_engineering_department.wonder_mechanics._core import leading_comment_block

    header = ""
    has_bom = False
    if path.exists():
        raw = path.read_bytes()
        has_bom = raw.startswith(codecs.BOM_UTF8)
        text = raw.decode("utf-8-sig")
        header = leading_comment_block(text)
    body = dump_yaml_document(payload).rstrip() + "\n"
    text = f"{header}\n{body}" if header else body
    return text.encode("utf-8-sig" if has_bom else "utf-8")
