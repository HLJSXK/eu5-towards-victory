from __future__ import annotations

import threading
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from towards_victory_editor_web.services.tooling import (
    JobManager, ToolPlan, ToolRegistry, ToolResult, ToolSpec, read_plan_inputs,
)
from towards_victory_editor_web.services.operation_store import OperationStore


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
        self.result = ToolResult(message="done")

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
            return self.result

        yield ToolPlan(snapshots, (self.output,), run)


@pytest.fixture
def job_env(tmp_path):
    tool = JsonTool(tmp_path)
    tool.source.write_text("source")
    registry = ToolRegistry()
    registry.register(tool)
    store = OperationStore(tmp_path / "operations.sqlite3")
    manager = JobManager(registry, tmp_path, store)
    yield tool, manager
    manager.shutdown()
    store.close()


def execute(tool, manager):
    job = manager.submit(tool.spec.id, {})
    manager.shutdown()
    return manager.get(job.id)


def test_job_reports_resource_snapshot_and_declared_artifact(job_env):
    tool, manager = job_env
    job = execute(tool, manager)
    assert job["status"] == "succeeded"
    assert job["operation_id"] == job["operation"]["id"]
    assert job["operation"]["status"] == job["status"]
    assert job["operation"]["started_at"] is not None
    assert manager.operation_store.get(job["operation_id"]) == job["operation"]
    assert job["resource_ids"] == ["editor.wonder_crop"]
    assert job["artifact_formats"] == ["json"]
    assert job["source_snapshots"][0]["path"] == "source.txt"
    assert job["declared_outputs"] == ["output.json"]
    assert job["artifacts"][0]["path"] == "output.json"
    assert job["artifacts"][0]["changed"] is True
    assert job["metadata"]["output_validation"][0]["valid"] is True


def test_completed_job_details_are_queryable_after_manager_restart(tmp_path):
    tool = JsonTool(tmp_path)
    tool.source.write_text("source")
    registry = ToolRegistry()
    registry.register(tool)
    store = OperationStore(tmp_path / "operations.sqlite3")
    manager = JobManager(registry, tmp_path, store)
    completed = execute(tool, manager)
    job_id = completed["id"]
    store.close()
    restarted_store = OperationStore(tmp_path / "operations.sqlite3")
    restarted = JobManager(ToolRegistry(), tmp_path, restarted_store)
    try:
        queried = restarted.get(job_id)
        assert queried["status"] == "succeeded"
        assert queried["tool"] == tool.spec.id
        assert queried["lines"] == []
        assert queried["artifacts"] == completed["artifacts"]
        assert restarted.get(job_id, after_line=queried["line_cursor"])["lines"] == []
    finally:
        restarted.shutdown()
        restarted_store.close()


@pytest.mark.parametrize("invalid", ["path", "circular", "nonfinite", "message"])
def test_invalid_tool_result_keeps_terminal_diagnostic_and_artifacts(job_env, invalid):
    tool, manager = job_env
    metadata = {"output": {"path": tool.output}}
    message = "done"
    if invalid == "circular":
        metadata = {}
        metadata["self"] = metadata
    elif invalid == "nonfinite":
        metadata = {"progress": float("nan")}
    elif invalid == "message":
        metadata = {}
        message = tool.output
    tool.result = ToolResult(message=message, metadata=metadata)

    failed = execute(tool, manager)

    assert failed["status"] == "failed"
    assert "Tool result from test.json must be JSON serializable" in failed["error"]
    assert "persistence_error" not in failed["operation"]
    assert failed["message"] == ""
    assert list(failed["metadata"]) == ["output_validation"]
    assert failed["metadata"]["output_validation"][0]["valid"] is True
    assert failed["artifacts"][0]["path"] == "output.json"
    assert failed["outputs_may_be_partial"] is True
    operation, details = manager.operation_store.get_with_details(failed["id"])
    assert operation == failed["operation"]
    assert details["metadata"] == failed["metadata"]
    assert details["lines"] == failed["lines"]

    reopened = OperationStore(manager.operation_store.path)
    archived = JobManager(ToolRegistry(), tool.root, reopened)
    try:
        assert archived.get(failed["id"]) == failed
        assert "interrupted" not in reopened.get(failed["id"])
    finally:
        archived.shutdown()
        reopened.close()


@pytest.mark.parametrize("invalid", ["path", "circular"])
def test_invalid_normalized_options_are_rejected_before_creating_job(job_env, monkeypatch, invalid):
    tool, manager = job_env
    options = {"source": tool.source}
    if invalid == "circular":
        options = {}
        options["self"] = options
    monkeypatch.setattr(tool, "validate", lambda _options: options)

    with pytest.raises(ValueError, match="Tool options for test.json must be JSON serializable"):
        manager.submit(tool.spec.id, {})

    assert manager.operation_store.recent() == []
    assert not tool.output.exists()


def test_tool_result_is_detached_before_handler_cleanup(job_env, monkeypatch):
    tool, manager = job_env
    metadata = {"output": {"path": "output.json"}}
    tool.result = ToolResult(message="done", metadata=metadata)
    prepare = tool.prepare

    @contextmanager
    def prepare_with_cleanup(options):
        with prepare(options) as plan:
            yield plan
            # A handler-owned object must not mutate the published JSON snapshot.
            metadata["output"]["path"] = tool.output

    monkeypatch.setattr(tool, "prepare", prepare_with_cleanup)

    completed = execute(tool, manager)

    assert completed["status"] == "succeeded"
    assert completed["metadata"]["output"] == {"path": "output.json"}
    operation, details = manager.operation_store.get_with_details(completed["id"])
    assert operation == completed["operation"]
    assert details["metadata"] == completed["metadata"]


def test_job_polling_returns_only_new_lines_and_keeps_lifecycle_events(job_env):
    tool, manager = job_env

    def action(context):
        context.log("first line")
        context.log("second line")
        tool.output.write_text('{}')

    tool.action = action
    job = manager.submit(tool.spec.id, {})
    manager.shutdown()
    full = job.payload()
    assert full["lines"] == ["first line", "second line"]
    assert full["lines_reset"] is True
    assert full["line_cursor"] == 2
    assert job.payload(after_line=1)["lines"] == ["second line"]
    assert job.payload(after_line=2)["lines"] == []
    assert job.payload(after_line=2)["lines_reset"] is False
    assert [event["message"] for event in full["operation"]["events"]] == ["started", "succeeded"]


def test_job_polling_resets_when_cursor_falls_out_of_retained_window(job_env):
    tool, manager = job_env

    def action(context):
        for index in range(510):
            context.log(f"line {index}")
        tool.output.write_text('{}')

    tool.action = action
    job = manager.submit(tool.spec.id, {})
    manager.shutdown()
    payload = job.payload(after_line=0)
    assert payload["lines_reset"] is True
    assert payload["line_cursor"] == 510
    assert len(payload["lines"]) == 300
    assert payload["lines"][0] == "line 210"
    assert payload["lines"][-1] == "line 509"
    assert job.payload(after_line=509)["lines"] == ["line 509"]


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
    assert job["operation_id"] == job["operation"]["id"]
    assert job["operation"]["status"] == job["status"]
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
    assert job["operation"]["status"] == "failed"
    assert job["operation"]["started_at"] is None
    assert "Resource busy" in job["error"]
    assert not tool.output.exists()


@pytest.mark.parametrize("cancel", [False, True])
def test_waiting_for_execution_lock_does_not_start_operation(job_env, monkeypatch, cancel):
    tool, manager = job_env
    execution_lock = manager._execution_lock
    waiting = threading.Event()

    @contextmanager
    def observed_lock():
        waiting.set()
        with execution_lock:
            yield

    monkeypatch.setattr(manager, "_execution_lock", observed_lock())
    with execution_lock:
        job = manager.submit(tool.spec.id, {})
        assert waiting.wait(5), "worker did not reach the execution lock"
        payload = job.payload()
        assert payload["status"] == payload["operation"]["status"] == "queued"
        assert payload["operation"]["started_at"] is None
        assert payload["operation"]["events"] == []
        if cancel:
            manager.cancel(job.id)
            payload = job.payload()
            assert payload["status"] == payload["operation"]["status"] == "cancelling"
    manager.shutdown()
    payload = job.payload()
    assert payload["status"] == payload["operation"]["status"] == ("cancelled" if cancel else "succeeded")
    assert (payload["operation"]["started_at"] is None) == cancel
    assert tool.output.exists() != cancel


@pytest.mark.parametrize("cancel,cleanup_fails", [(False, False), (False, True), (True, False), (True, True)])
def test_job_finishes_only_after_handler_cleanup(job_env, monkeypatch, cancel, cleanup_fails):
    from towards_victory_editor_web.services.platform import resource_operation

    tool, manager = job_env
    cleanup_started, finish_cleanup = threading.Event(), threading.Event()
    prepare = tool.prepare

    @contextmanager
    def prepare_with_cleanup(options):
        with prepare(options) as plan:
            yield plan
            cleanup_started.set()
            assert finish_cleanup.wait(5), "test did not release cleanup"
            if cleanup_fails:
                raise RuntimeError("cleanup failed")

    monkeypatch.setattr(tool, "prepare", prepare_with_cleanup)
    job = manager.submit(tool.spec.id, {})
    try:
        assert cleanup_started.wait(5)
        running = job.payload()
        assert running["status"] == running["operation"]["status"] == "running"
        assert running["returncode"] is None
        assert running["finished_at"] is running["operation"]["finished_at"] is None
        if cancel:
            manager.cancel(job.id)
            cancelling = job.payload()
            manager.cancel(job.id)
            assert cancelling["status"] == "cancelling"
            assert job.payload()["operation"] == cancelling["operation"]
    finally:
        finish_cleanup.set()
        manager.shutdown()

    completed = job.payload()
    expected = "cancelled" if cancel else "failed" if cleanup_fails else "succeeded"
    assert completed["status"] == completed["operation"]["status"] == expected
    assert completed["error"] == completed["operation"]["error"]
    assert completed["error"] == ("Cancellation requested" if cancel else "cleanup failed" if cleanup_fails else None)
    assert completed["returncode"] == {"succeeded": 0, "failed": 1, "cancelled": 130}[expected]
    assert completed["created_at"] == completed["operation"]["created_at"]
    assert completed["finished_at"] == completed["operation"]["finished_at"]
    assert completed["finished_at"] is not None
    assert completed["outputs_may_be_partial"] == (expected != "succeeded")
    manager.cancel(job.id)
    assert job.payload() == completed
    with resource_operation(tool.spec.resource_ids, blocking=False):
        pass


def test_cancelled_queued_job_does_not_try_to_acquire_busy_resource(job_env):
    from towards_victory_editor_web.services.platform import resource_operation

    tool, manager = job_env
    with resource_operation(tool.spec.resource_ids):
        with manager._execution_lock:
            job = manager.submit(tool.spec.id, {})
            manager.cancel(job.id)
        manager.shutdown()
    payload = job.payload()
    assert payload["status"] == "cancelled"
    assert payload["operation"]["started_at"] is None
    assert payload["error"] == "Cancellation requested"
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
            assert conflict.json()["code"] == "resource_busy"
            assert conflict.json()["operation"]["status"] == "failed"
            assert conflict.json()["operation_id"] != running["operation_id"]
            assert not cropper.data_path.exists()
        finally:
            finish.set()
            manager.shutdown()
        completed = client.get(f"/api/jobs/{job_id}").json()
        assert completed["status"] == "succeeded"
        assert completed["artifacts"][0]["path"] == "output.json"
        assert client.get(f"/api/jobs/{job_id}?after_line={completed['line_cursor']}").json()["lines"] == []
        assert client.get(f"/api/jobs/{job_id}?after_line=-1").status_code == 422
        assert client.post("/api/resources/editor.wonder_crop/commit", json={"base": base, "edits": {}}).status_code == 200
