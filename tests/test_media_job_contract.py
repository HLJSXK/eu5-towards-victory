from __future__ import annotations

import threading
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from towards_victory_editor_web.services.tooling import (
    JobManager, ToolPlan, ToolRegistry, ToolResult, ToolSpec, read_plan_inputs,
)


class JsonTool:
    spec = ToolSpec(
        "test.json", "JSON test tool", "test", "test",
        resource_ids=("editor.wonder_crop",), artifact_formats=("json",),
    )

    def __init__(self, root):
        self.root = root
        self.source = root / "source.txt"
        self.output = root / "output.json"
        self.action = lambda context: self.output.write_text('{"ok": true}')
        self.optional = ()

    def validate(self, options):
        if options:
            raise ValueError("no options are accepted")
        return {}

    @contextmanager
    def prepare(self, options):
        _, snapshots = read_plan_inputs(
            (self.source,), lambda: None, repo_root=self.root, optional=self.optional,
        )

        def run(context):
            self.action(context)
            return ToolResult(message="done")

        yield ToolPlan(snapshots, (self.output,), run)


@pytest.fixture
def job_env(tmp_path):
    tool = JsonTool(tmp_path)
    tool.source.write_text("source")
    registry = ToolRegistry()
    registry.register(tool)
    manager = JobManager(registry, tmp_path)
    yield tool, manager
    manager.shutdown()


def execute(tool, manager):
    job = manager.submit(tool.spec.id, {})
    manager.shutdown()
    return manager.get(job.id).payload()


def test_job_reports_resource_snapshot_and_declared_artifact(job_env):
    tool, manager = job_env
    job = execute(tool, manager)
    assert job["status"] == "succeeded"
    assert job["resource_ids"] == ["editor.wonder_crop"]
    assert job["artifact_formats"] == ["json"]
    assert job["source_snapshots"][0]["path"] == "source.txt"
    assert job["declared_outputs"] == ["output.json"]
    assert job["artifacts"][0]["path"] == "output.json"
    assert job["artifacts"][0]["changed"] is True
    assert job["metadata"]["output_validation"][0]["valid"] is True


@pytest.mark.parametrize("failure", ["source_changed", "exception", "cancelled"])
def test_failed_or_cancelled_job_preserves_written_artifacts(job_env, failure):
    tool, manager = job_env

    def action(context):
        tool.output.write_text('{"partial": true}')
        tool.source.write_text("changed")
        if failure == "exception":
            raise RuntimeError("generator stopped")
        if failure == "cancelled":
            manager.cancel(context.job_id)

    tool.action = action
    job = execute(tool, manager)
    assert job["status"] == ("cancelled" if failure == "cancelled" else "failed")
    assert job["returncode"] == (130 if failure == "cancelled" else 1)
    assert job["artifacts"][0]["path"] == "output.json"
    assert job["artifacts"][0]["changed"] is True
    assert job["outputs_may_be_partial"] is True
    assert "no rollback" in job["lines"][-1]
    expected = {"source_changed": "Declared inputs changed", "exception": "generator stopped", "cancelled": "Cancellation requested"}
    assert expected[failure] in job["error"]


def test_missing_declared_output_fails_and_unrelated_files_are_not_artifacts(job_env):
    tool, manager = job_env
    tool.action = lambda context: (tool.root / "unrelated.txt").write_text("another writer")
    job = execute(tool, manager)
    assert job["status"] == "failed"
    assert job["missing_outputs"] == ["output.json"]
    assert job["artifacts"] == []
    assert "Missing declared outputs" in job["error"]


def test_unrelated_file_change_does_not_fail_valid_job(job_env):
    tool, manager = job_env

    def action(context):
        tool.output.write_text('{}')
        (tool.root / "unrelated.txt").write_text("another writer")

    tool.action = action
    job = execute(tool, manager)
    assert job["status"] == "succeeded"
    assert [item["path"] for item in job["artifacts"]] == ["output.json"]


def test_missing_declared_input_fails_before_writes(job_env):
    tool, manager = job_env
    tool.source.unlink()
    job = execute(tool, manager)
    assert job["status"] == "failed"
    assert "Missing declared input" in job["error"]
    assert not tool.output.exists()


def test_busy_resource_fails_job_before_writes(job_env):
    from towards_victory_editor_web.services.platform import resource_operation

    tool, manager = job_env
    with resource_operation(("editor.wonder_crop",)):
        job = execute(tool, manager)
    assert job["status"] == "failed"
    assert "Resource busy" in job["error"]
    assert not tool.output.exists()


def test_input_change_during_preparation_is_rejected(job_env):
    from towards_victory_editor_web.services.platform import ConflictError

    tool, _ = job_env
    with pytest.raises(ConflictError, match="during job preparation"):
        read_plan_inputs((tool.source,), lambda: tool.source.write_text("changed"), repo_root=tool.root)


def test_optional_input_appearing_during_execution_is_a_conflict(job_env):
    tool, manager = job_env
    tool.source.unlink()
    tool.optional = (tool.source,)

    def action(context):
        tool.source.write_text("new config")
        tool.output.write_text('{}')

    tool.action = action
    job = execute(tool, manager)
    assert job["status"] == "failed"
    assert job["source_snapshots"][0]["sha256"] == "missing"
    assert "Declared inputs changed" in job["error"]


@pytest.mark.parametrize("extension,content,error", [
    ("txt", "wrong format", "not declared"),
    ("json", "not JSON", "Output validation failed"),
])
def test_invalid_artifact_retains_manifest(job_env, extension, content, error):
    tool, manager = job_env
    tool.output = tool.root / f"output.{extension}"
    tool.action = lambda context: tool.output.write_text(content)
    job = execute(tool, manager)
    assert job["status"] == "failed"
    assert error in job["error"]
    assert job["artifacts"][0]["path"] == tool.output.name
    assert job["metadata"]["output_validation"][0]["valid"] is False


def test_unchanged_output_is_validated_and_reported(job_env):
    tool, manager = job_env
    tool.output.write_text('{}')
    tool.action = lambda context: None
    job = execute(tool, manager)
    assert job["status"] == "succeeded"
    assert job["artifacts"][0]["changed"] is False


def test_deleted_output_is_recorded_after_failure(job_env):
    tool, manager = job_env
    tool.output.write_text('{}')
    tool.action = lambda context: tool.output.unlink()
    job = execute(tool, manager)
    assert job["status"] == "failed"
    assert job["missing_outputs"] == ["output.json"]
    assert job["artifacts"][0]["role"] == "deleted"
    assert job["outputs_may_be_partial"] is True


def test_http_job_contract_and_crop_commit_conflict(job_env, monkeypatch):
    from towards_victory_editor_web import server
    from towards_victory_editor_web.services.cropper import CropperService

    tool, manager = job_env
    cropper = CropperService(tasks=[], data_path=tool.root / "crops.json", repo_root=tool.root)
    monkeypatch.setattr(server, "jobs", manager)
    monkeypatch.setattr(server, "cropper", cropper)
    started, finish = threading.Event(), threading.Event()

    def action(context):
        started.set()
        assert finish.wait(5), "test did not release generator"
        tool.output.write_text('{}')

    tool.action = action
    with TestClient(server.create_app()) as client:
        resource = client.get("/api/resources/editor.wonder_crop").json()
        base = {item["path"]: item["sha256"] for item in resource["change_set"]["base"]}
        submitted = client.post("/api/jobs", json={"tool": tool.spec.id, "options": {}})
        assert submitted.status_code == 200
        assert started.wait(5)
        try:
            job_id = submitted.json()["id"]
            running = client.get(f"/api/jobs/{job_id}").json()
            assert running["resource_ids"] == ["editor.wonder_crop"]
            assert running["source_snapshots"][0]["path"] == "source.txt"
            assert running["declared_outputs"] == ["output.json"]
            conflict = client.post("/api/resources/editor.wonder_crop/commit", json={"base": base, "edits": {}})
            assert conflict.status_code == 409
            assert "Resource busy" in conflict.json()["detail"]
            assert not cropper.data_path.exists()
        finally:
            finish.set()
            manager.shutdown()
        completed = client.get(f"/api/jobs/{job_id}").json()
        assert completed["status"] == "succeeded"
        assert completed["artifacts"][0]["path"] == "output.json"
        assert client.post("/api/resources/editor.wonder_crop/commit", json={"base": base, "edits": {}}).status_code == 200
