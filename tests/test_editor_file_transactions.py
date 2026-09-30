from pathlib import Path

import pytest
import yaml

from towards_victory_editor_web.services import platform


def test_rollback_attempts_every_path_and_reload_despite_multiple_failures(tmp_path, monkeypatch):
    locked_source = tmp_path / "locked.yaml"
    artifact = tmp_path / "artifact.txt"
    locked_new = tmp_path / "locked_new.txt"
    new = tmp_path / "new.txt"
    locked_source.write_bytes(b"old source")
    artifact.write_bytes(b"old artifact")
    original_write = platform.atomic_write_files
    original_unlink = Path.unlink
    attempts = []

    def restore(files):
        attempts.extend(files)
        if locked_source in files:
            raise PermissionError("source locked")
        original_write(files)

    def unlink(path, **kwargs):
        if path == locked_new:
            raise PermissionError("new file locked")
        return original_unlink(path, **kwargs)

    def reload():
        attempts.append("reload")
        raise ValueError("invalid partial source")

    monkeypatch.setattr(platform, "atomic_write_files", restore)
    monkeypatch.setattr(Path, "unlink", unlink)
    original_error = RuntimeError("generator X exited with 1")
    with pytest.raises(platform.RollbackError) as error:
        with platform.file_transaction((locked_source, artifact, locked_new, new), reload=reload):
            for path in (locked_source, artifact, locked_new, new):
                path.write_bytes(b"new content")
            raise original_error

    assert error.value.__cause__ is original_error
    assert "generator X exited with 1" in str(error.value)
    assert "source locked" in str(error.value)
    assert "new file locked" in str(error.value)
    assert "invalid partial source" in str(error.value)
    assert len(error.value.errors) == 3
    assert artifact.read_bytes() == b"old artifact"
    assert not new.exists()
    assert attempts == [locked_source, artifact, "reload"]


def test_rollback_leaves_unchanged_files_and_mtimes_alone(tmp_path, monkeypatch):
    unchanged = tmp_path / "unchanged.txt"
    changed = tmp_path / "changed.txt"
    absent = tmp_path / "absent.txt"
    unchanged.write_bytes(b"same")
    changed.write_bytes(b"old")
    before = unchanged.stat()
    writes = []
    original_write = platform.atomic_write_files

    def write(files):
        writes.extend(files)
        original_write(files)

    monkeypatch.setattr(platform, "atomic_write_files", write)
    with pytest.raises(RuntimeError, match="failed"):
        with platform.file_transaction((unchanged, changed, absent), reload=lambda: None):
            changed.write_bytes(b"new")
            raise RuntimeError("failed")
    assert writes == [changed]
    assert unchanged.stat().st_mtime_ns == before.st_mtime_ns
    assert unchanged.stat().st_ino == before.st_ino
    assert not absent.exists()


def test_registry_selects_only_planned_scripts_and_rejects_missing_registration(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    registry = data / "generated_files.yaml"
    registry.write_text(yaml.safe_dump({"generated": [
        {"script": "loc.py", "output": "loc.yml"},
        {"script": "loc.py", "output": "added.yml"},
        {"script": "mechanics.py", "output": "mechanics.txt"},
    ]}))
    assert platform.generated_outputs_by_script(("loc.py",), repo_root=tmp_path) == {
        "loc.py": (tmp_path / "loc.yml", tmp_path / "added.yml"),
    }
    assert platform.generated_outputs_by_script(
        ("merge.py", "merge2.py"), repo_root=tmp_path,
        extra_outputs={"merge.py": ("shared.gui",), "merge2.py": ("shared.gui",)},
    ) == {"merge.py": (tmp_path / "shared.gui",), "merge2.py": (tmp_path / "shared.gui",)}
    with pytest.raises(ValueError, match="No registered outputs.*unknown.py"):
        platform.generated_outputs_by_script(("unknown.py",), repo_root=tmp_path)
    registry.unlink()
    assert platform.generated_outputs_by_script((), repo_root=tmp_path) == {}


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
@pytest.mark.parametrize("bom", [b"", b"\xef\xbb\xbf"])
def test_yaml_bytes_preserves_newlines_bom_and_header(tmp_path, newline, bom):
    path = tmp_path / "source.yaml"
    path.write_bytes(bom + f"# Header{newline}key: old{newline}".encode())
    content = platform.yaml_bytes(path, {"key": "new"})
    assert content == bom + f"# Header{newline}key: new{newline}".encode()
