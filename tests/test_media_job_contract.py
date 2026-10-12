from __future__ import annotations

import threading
from contextlib import contextmanager
from pathlib import Path

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
        self.action = lambda context: context.stage_path(self.output).write_text('{"ok": true}')
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
            self.context = context
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


def wait_for_jobs(manager):
    for future in list(manager._futures.values()):
        future.result(timeout=15)


def test_cli_check_exits_nonzero_when_a_subcheck_fails(monkeypatch, capsys):
    import sys

    from towards_victory_editor_web import __main__ as web_main
    from towards_victory_editor_web.services import media
    from towards_victory_editor_web.services.cropper import cropper

    monkeypatch.setattr(sys, "argv", ["towards_victory_editor_web", "--check"])
    monkeypatch.setattr(
        web_main,
        "safe_check",
        lambda name, _check: [f"[FAIL] {name}: injected check failure"]
        if name == "victory_tree" else [f"[PASS] {name}"],
    )
    monkeypatch.setattr(media, "bootstrap_payload", lambda: {"tools": []})
    monkeypatch.setattr(media.registry, "payload", lambda: [])
    monkeypatch.setattr(cropper, "tasks", [])

    with pytest.raises(SystemExit) as error:
        web_main.main()

    assert error.value.code == 1
    assert "[FAIL] victory_tree" in capsys.readouterr().out


def execute(tool, manager):
    job = manager.submit(tool.spec.id, {})
    wait_for_jobs(manager)
    manager.shutdown()
    return manager.get(job.id)


def test_shutdown_cancels_running_waiting_and_queued_jobs_and_persists_all(job_env):
    tool, manager = job_env
    started = threading.Event()
    attempts = []
    def action(context):
        attempts.append(context.job_id)
        started.set()
        context.wait(10)
        pytest.fail("running job was not cancelled")
    tool.action = action
    first = manager.submit(tool.spec.id, {})
    assert started.wait(5)
    others = [manager.submit(tool.spec.id, {}) for _ in range(5)]
    manager.shutdown()
    assert attempts == [first.id]
    for job in [first, *others]:
        payload = manager.get(job.id)
        assert payload["operation"]["status"] == "cancelled"
        assert payload["operation"]["finished_at"] is not None
        assert payload["operation"].get("persistence_error") is None
        assert manager.operation_store.get(job.id)["status"] == "cancelled"
    assert manager._futures == {}
    assert all(job.operation.started_at is None for job in others)
    with pytest.raises(RuntimeError, match="closed"):
        manager.submit(tool.spec.id, {})
    assert len(manager.operation_store.recent()) == 6
    assert not tool.output.exists()


def test_submit_racing_with_shutdown_cannot_leave_a_queued_record(job_env, monkeypatch):
    tool, manager = job_env
    submitting, release, closing, closed = (threading.Event() for _ in range(4))
    submit = manager._executor.submit
    def blocked_submit(*args):
        submitting.set()
        assert release.wait(5)
        return submit(*args)
    monkeypatch.setattr(manager._executor, "submit", blocked_submit)
    tool.action = lambda context: context.wait(10)
    submitted, errors = [], []
    def submit_job():
        try:
            submitted.append(manager.submit(tool.spec.id, {}))
        except Exception as error:
            errors.append(error)
    def shutdown():
        closing.set()
        manager.shutdown()
        closed.set()
    submit_thread = threading.Thread(target=submit_job)
    close_thread = threading.Thread(target=shutdown)
    submit_thread.start()
    try:
        assert submitting.wait(5)
        close_thread.start()
        assert closing.wait(5)
        assert not closed.is_set()
    finally:
        release.set()
        submit_thread.join(5)
        close_thread.join(5)
    assert closed.is_set()
    assert not errors
    assert len(submitted) == 1
    assert manager.get(submitted[0].id)["operation"]["status"] == "cancelled"
    assert manager.operation_store.get(submitted[0].id)["status"] == "cancelled"


def test_shutdown_during_validation_rejects_without_registering_job(job_env, monkeypatch):
    tool, manager = job_env
    validate = tool.validate
    def close_during_validation(options):
        normalized = validate(options)
        manager.shutdown()
        return normalized
    monkeypatch.setattr(tool, "validate", close_during_validation)
    with pytest.raises(RuntimeError, match="closed"):
        manager.submit(tool.spec.id, {})
    assert manager.operation_store.recent() == []


def test_job_reports_resource_snapshot_and_declared_artifact(job_env):
    tool, manager = job_env
    job = execute(tool, manager)
    assert job["operation"]["status"] == "succeeded"
    assert {"id", "status", "error", "resource_ids", "operation_id", "created_at", "finished_at"}.isdisjoint(job)
    assert job["operation"]["started_at"] is not None
    assert manager.operation_store.get(job["operation"]["id"]) == job["operation"]
    assert job["operation"]["resource_ids"] == ["editor.wonder_crop"]
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
    job_id = completed["operation"]["id"]
    store.close()
    restarted_store = OperationStore(tmp_path / "operations.sqlite3")
    restarted = JobManager(ToolRegistry(), tmp_path, restarted_store)
    try:
        queried = restarted.get(job_id)
        assert queried["operation"]["status"] == "succeeded"
        assert queried["tool"] == tool.spec.id
        assert queried["lines"] == []
        assert queried["artifacts"] == completed["artifacts"]
        assert restarted.get(job_id, after_line=queried["line_cursor"])["lines"] == []
    finally:
        restarted.shutdown()
        restarted_store.close()


@pytest.mark.usefixtures("without_wonder_service")
def test_lifespan_cancels_job_before_closing_owned_store(job_env, monkeypatch):
    from towards_victory_editor_web import server

    tool, manager = job_env
    started = threading.Event()
    def action(context):
        started.set()
        context.wait(10)
        pytest.fail("shutdown did not cancel the running job")
    tool.action = action
    monkeypatch.setattr(server, "registry", manager.registry)
    monkeypatch.setattr(server, "PACKAGE_ROOT", tool.root / "web")
    store_path = tool.root / "lifespan.sqlite3"
    app = server.create_app(operation_store_path=store_path)
    with TestClient(app) as client:
        submitted = client.post("/api/jobs", json={"tool": tool.spec.id, "options": {}})
        assert submitted.status_code == 200
        assert started.wait(5)
        job_id = submitted.json()["operation"]["id"]
        first_manager = app.state.jobs
    reopened = OperationStore(store_path)
    try:
        persisted = reopened.get(job_id)
        assert persisted["status"] == "cancelled"
        assert not persisted.get("interrupted")
        assert "persistence_error" not in persisted
    finally:
        reopened.close()
    with TestClient(app):
        assert app.state.jobs is not first_manager
        assert app.state.jobs.get(job_id)["operation"]["status"] == "cancelled"


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

    assert failed["operation"]["status"] == "failed"
    assert "Tool result from test.json must be JSON serializable" in failed["operation"]["error"]
    assert "persistence_error" not in failed["operation"]
    assert failed["message"] == ""
    assert list(failed["metadata"]) == ["output_validation"]
    assert failed["metadata"]["output_validation"][0]["valid"] is True
    assert failed["artifacts"][0]["path"] == "output.json"
    assert failed["outputs_may_be_partial"] is False
    operation, details = manager.operation_store.get_with_details(failed["operation"]["id"])
    assert operation == failed["operation"]
    assert details["metadata"] == failed["metadata"]
    assert details["lines"] == failed["lines"]

    manager.operation_store.close()
    reopened = OperationStore(manager.operation_store.path)
    archived = JobManager(ToolRegistry(), tool.root, reopened)
    try:
        assert archived.get(failed["operation"]["id"]) == failed
        assert "interrupted" not in reopened.get(failed["operation"]["id"])
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

    assert completed["operation"]["status"] == "succeeded"
    assert completed["metadata"]["output"] == {"path": "output.json"}
    operation, details = manager.operation_store.get_with_details(completed["operation"]["id"])
    assert operation == completed["operation"]
    assert details["metadata"] == completed["metadata"]


def test_job_polling_returns_only_new_lines_and_keeps_lifecycle_events(job_env):
    tool, manager = job_env

    def action(context):
        context.log("first line")
        context.log("second line")
        context.stage_path(tool.output).write_text('{}')

    tool.action = action
    job = manager.submit(tool.spec.id, {})
    wait_for_jobs(manager)
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
        context.stage_path(tool.output).write_text('{}')

    tool.action = action
    job = manager.submit(tool.spec.id, {})
    wait_for_jobs(manager)
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
        context.stage_path(tool.output).write_text('{"partial": true}')
        tool.source.write_text("changed")
        if failure == "exception":
            raise RuntimeError("generator stopped")
        if failure == "cancelled":
            manager.cancel(context.job_id)

    tool.action = action
    job = execute(tool, manager)
    assert job["operation"]["status"] == ("cancelled" if failure == "cancelled" else "failed")
    assert "operation_id" not in job
    assert job["returncode"] == (130 if failure == "cancelled" else 1)
    assert job["artifacts"][0]["path"] == "output.json"
    assert job["artifacts"][0]["changed"] is True
    assert job["outputs_may_be_partial"] is False
    assert job["formal_output_changes"] == []
    assert not tool.output.exists()
    expected = {"source_changed": "Declared inputs changed", "exception": "generator stopped", "cancelled": "Cancellation requested"}
    assert expected[failure] in job["operation"]["error"]


def test_missing_declared_output_fails_and_unrelated_files_are_not_artifacts(job_env):
    tool, manager = job_env
    tool.action = lambda context: (tool.root / "unrelated.txt").write_text("another writer")
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert job["missing_outputs"] == ["output.json"]
    assert job["artifacts"] == []
    assert "Missing declared outputs" in job["operation"]["error"]


def test_unrelated_file_changes_are_not_scanned_or_attributed_to_job(job_env, monkeypatch):
    tool, manager = job_env
    tool.output = tool.root / "images" / "output.json"
    tool.output.parent.mkdir()
    unrelated = (tool.root / "unrelated.txt", tool.output.parent / "unrelated.txt")
    for path in unrelated:
        path.write_text("before")
    read_bytes = Path.read_bytes
    rglob = Path.rglob

    def read_declared_only(path):
        assert path not in unrelated, f"read unrelated file: {path}"
        return read_bytes(path)

    def scan_job_staging_only(path, pattern):
        assert path.parent == tool.root / ".editor_state", f"scanned outside job staging: {path}"
        return rglob(path, pattern)

    monkeypatch.setattr(Path, "read_bytes", read_declared_only)
    monkeypatch.setattr(Path, "rglob", scan_job_staging_only)

    def action(context):
        context.stage_path(tool.output).write_text('{}')
        for path in unrelated:
            path.write_text("another writer")
        (tool.root / "__pycache__").mkdir()
        (tool.root / "__pycache__" / "unrelated.pyc").write_bytes(b"cache")

    tool.action = action
    job = execute(tool, manager)
    assert job["operation"]["status"] == "succeeded"
    assert [item["path"] for item in job["artifacts"]] == ["images/output.json"]
    assert job["formal_output_changes"] == []
    assert job["outputs_may_be_partial"] is False
    assert job["lines"] == []


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("outcome", ["return", "exception", "cancel"])
def test_direct_formal_writes_are_rejected_and_reported(job_env, existing, outcome):
    tool, manager = job_env
    if existing:
        tool.output.write_bytes(b'{"before": true}')

    def action(context):
        tool.output.write_bytes(b'{"outside_staging": true}')
        if outcome == "exception":
            raise RuntimeError("generator failed")
        if outcome == "cancel":
            context.request_cancel()

    tool.action = action
    job = execute(tool, manager)
    assert job["operation"]["status"] == ("cancelled" if outcome == "cancel" else "failed")
    assert job["formal_output_changes"] == ["output.json"]
    assert job["outputs_may_be_partial"] is True
    if outcome == "return":
        assert "Formal outputs changed outside staging" in job["operation"]["error"]
    assert any("writer unknown, review files: output.json" in line for line in job["lines"])
    # No compatibility copy into staging and no restoration over another writer.
    assert tool.output.read_bytes() == b'{"outside_staging": true}'
    restarted = JobManager(ToolRegistry(), tool.root, manager.operation_store)
    try:
        assert restarted.get(job["operation"]["id"]) == job
    finally:
        restarted.shutdown()


@pytest.mark.parametrize("fails", [False, True])
def test_staging_intermediates_do_not_mark_formal_outputs_partial(job_env, fails):
    tool, manager = job_env
    def action(context):
        output = context.stage_path(tool.output)
        output.write_bytes(b'{}')
        output.with_name("intermediate.bin").write_bytes(b"intermediate")
        if fails:
            raise RuntimeError("generator failed")

    tool.action = action
    job = execute(tool, manager)
    assert job["operation"]["status"] == ("failed" if fails else "succeeded")
    assert job["staging_extra_files"] == ["staging/intermediate.bin"]
    assert job["formal_output_changes"] == []
    assert job["outputs_may_be_partial"] is False
    assert not (tool.root / "intermediate.bin").exists()
    assert list((tool.root / ".editor_state").iterdir()) == []
    assert all("Undeclared" not in line for line in job["lines"])


def test_missing_declared_input_fails_before_writes(job_env):
    tool, manager = job_env
    tool.source.unlink()
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert "Missing declared input" in job["operation"]["error"]
    assert not tool.output.exists()


def test_busy_resource_fails_job_before_writes(job_env):
    from towards_victory_editor_web.services.platform import resource_operation

    tool, manager = job_env
    with resource_operation(("editor.wonder_crop",)):
        job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert job["operation"]["started_at"] is None
    assert "Resource busy" in job["operation"]["error"]
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
        assert payload["operation"]["status"] == "queued"
        assert payload["operation"]["started_at"] is None
        assert payload["operation"]["events"] == []
        if cancel:
            manager.cancel(job.id)
            payload = job.payload()
            assert payload["operation"]["status"] == "cancelling"
    wait_for_jobs(manager)
    manager.shutdown()
    payload = job.payload()
    assert payload["operation"]["status"] == ("cancelled" if cancel else "succeeded")
    assert (payload["operation"]["started_at"] is None) == cancel
    assert tool.output.exists() != cancel


@pytest.mark.parametrize("cancel,cleanup_fails", [(False, False), (False, True), (True, False), (True, True)])
def test_job_finishes_only_after_handler_cleanup(job_env, monkeypatch, cancel, cleanup_fails):
    from towards_victory_editor_web.services.platform import resource_operation

    tool, manager = job_env
    tool.output.write_text('{"original": true}')
    original_output = tool.output.read_bytes()
    cleanup_started, finish_cleanup = threading.Event(), threading.Event()
    prepare = tool.prepare

    @contextmanager
    def prepare_with_cleanup(options):
        with prepare(options) as plan:
            yield plan
            cleanup_started.set()
            tool.context.stage_path(tool.output).write_text('{"cleanup": true}')
            assert finish_cleanup.wait(5), "test did not release cleanup"
            if cleanup_fails:
                raise RuntimeError("cleanup failed")

    monkeypatch.setattr(tool, "prepare", prepare_with_cleanup)
    job = manager.submit(tool.spec.id, {})
    try:
        assert cleanup_started.wait(5)
        running = job.payload()
        assert running["operation"]["status"] == "running"
        assert running["returncode"] is None
        assert running["operation"]["finished_at"] is None
        if cancel:
            manager.cancel(job.id)
            cancelling = job.payload()
            manager.cancel(job.id)
            assert cancelling["operation"]["status"] == "cancelling"
            assert job.payload()["operation"] == cancelling["operation"]
    finally:
        finish_cleanup.set()
        wait_for_jobs(manager)
        manager.shutdown()

    completed = job.payload()
    expected = "cancelled" if cancel else "failed" if cleanup_fails else "succeeded"
    assert completed["operation"]["status"] == expected
    assert completed["operation"]["error"] == ("Cancellation requested" if cancel else "cleanup failed" if cleanup_fails else None)
    assert completed["returncode"] == {"succeeded": 0, "failed": 1, "cancelled": 130}[expected]
    assert completed["operation"]["finished_at"] is not None
    assert completed["outputs_may_be_partial"] is False
    if expected == "succeeded":
        assert tool.output.read_bytes() != original_output
    else:
        assert tool.output.read_bytes() == original_output
    manager.cancel(job.id)
    assert job.payload() == completed
    with resource_operation(tool.spec.resource_ids, blocking=False):
        pass


@pytest.mark.parametrize("cleanup_change", ["invalid_output", "input_change"])
def test_job_validates_files_after_handler_cleanup(job_env, monkeypatch, cleanup_change):
    tool, manager = job_env
    tool.output.write_bytes(b'{"original": true}')
    before = tool.output.read_bytes()
    prepare = tool.prepare

    @contextmanager
    def prepare_with_cleanup(options):
        with prepare(options) as plan:
            yield plan
            if cleanup_change == "invalid_output":
                tool.context.stage_path(tool.output).write_bytes(b"not JSON")
            else:
                tool.source.write_text("changed in cleanup")

    monkeypatch.setattr(tool, "prepare", prepare_with_cleanup)
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    expected = "Output validation failed" if cleanup_change == "invalid_output" else "Declared inputs changed"
    assert expected in job["operation"]["error"]
    assert tool.output.read_bytes() == before


@pytest.mark.parametrize("rollback_fails", [False, True])
def test_publication_failure_restores_files_or_retains_backups(job_env, monkeypatch, rollback_fails):
    from towards_victory_editor_web.services import tooling

    tool, manager = job_env
    outputs = (tool.output, tool.root / "new.json", tool.root / "last.json")
    original = b'{"original": true}'
    outputs[0].write_bytes(original)
    outputs[2].write_bytes(original)
    unrelated_tmp = tool.root / "unrelated.tmp"
    unrelated_tmp.write_text("keep")
    prepare = tool.prepare

    @contextmanager
    def prepare_multiple(options):
        with prepare(options) as plan:
            def run(context):
                for output in outputs:
                    context.stage_path(output).write_bytes(b'{"new": true}')
                return ToolResult()
            yield ToolPlan(plan.inputs, outputs, run)

    replace = tooling.os.replace
    def fail_last(source, target):
        if target == outputs[2]:
            raise OSError("publication failed")
        replace(source, target)

    copy = tooling.shutil.copy2
    def copy_with_locked_output(source, target):
        if rollback_fails and ".backup" in source.parts and target == outputs[0]:
            raise PermissionError("output is locked")
        return copy(source, target)

    monkeypatch.setattr(tool, "prepare", prepare_multiple)
    monkeypatch.setattr(tooling.os, "replace", fail_last)
    monkeypatch.setattr(tooling.shutil, "copy2", copy_with_locked_output)
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert ("output is locked" if rollback_fails else "publication failed") in job["operation"]["error"]
    assert "publication failed" in job["operation"]["error"]
    if rollback_fails:
        assert "Rollback incomplete" in job["operation"]["error"]
    assert outputs[2].read_bytes() == original
    assert not outputs[1].exists()
    assert job["outputs_may_be_partial"] == rollback_fails
    assert job["publication_rollback_failed"] == rollback_fails
    assert list(tool.root.glob("*.tmp")) == [unrelated_tmp]
    if rollback_fails:
        assert outputs[0].read_bytes() == b'{"new": true}'
        retained, = (tool.root / ".editor_state").iterdir()
        assert (retained / ".backup" / outputs[0].name).read_bytes() == original
        assert any("retained backups at" in line for line in job["lines"])
    else:
        assert outputs[0].read_bytes() == original
        assert list((tool.root / ".editor_state").iterdir()) == []
    restarted = JobManager(ToolRegistry(), tool.root, manager.operation_store)
    try:
        assert restarted.get(job["operation"]["id"]) == job
    finally:
        restarted.shutdown()


def test_cancellation_during_publication_keeps_rollback_diagnostics(job_env, monkeypatch):
    from towards_victory_editor_web.services import tooling

    tool, manager = job_env
    outputs = (tool.output, tool.root / "last.json")
    for output in outputs:
        output.write_text('{"old":true}')
    contexts = []

    @contextmanager
    def prepare(options):
        def run(context):
            contexts.append(context)
            for output in outputs:
                context.stage_path(output).write_text('{"new":true}')
            return ToolResult()
        yield ToolPlan((), outputs, run)

    replace = tooling.os.replace
    def cancel_then_fail(source, target):
        if target == outputs[1]:
            contexts[0].operation.request_cancel()
            raise OSError("publication failed")
        replace(source, target)

    copy = tooling.shutil.copy2
    def locked_restore(source, target):
        if ".backup" in source.parts and target == outputs[0]:
            raise PermissionError("restore blocked")
        return copy(source, target)

    monkeypatch.setattr(tool, "prepare", prepare)
    monkeypatch.setattr(tooling.os, "replace", cancel_then_fail)
    monkeypatch.setattr(tooling.shutil, "copy2", locked_restore)
    job = execute(tool, manager)
    assert job["operation"]["status"] == "cancelled"
    assert job["publication_rollback_failed"] is True
    for text in (job["operation"]["error"], "\n".join(job["lines"])):
        assert "Cancellation requested" in text
        assert "publication failed" in text
        assert "Rollback incomplete" in text and "restore blocked" in text
    stored, _ = manager.operation_store.get_with_details(job["operation"]["id"])
    assert "restore blocked" in stored["error"]


def test_stage_path_rejects_undeclared_outputs_before_and_after_setup(tmp_path):
    from towards_victory_editor_web.services.platform import OperationLog
    from towards_victory_editor_web.services.tooling import ToolContext

    context = ToolContext("strict-staging", tmp_path, lambda line: None, OperationLog("media_job"))
    output = tmp_path / "out" / "declared.json"
    with pytest.raises(ValueError, match="not a declared job output"):
        context.stage_path(output)
    context.set_staging(tmp_path / ".editor_state" / "test-staging", (output,))
    with pytest.raises(ValueError, match="not a declared job output"):
        context.stage_path(output.with_name("undeclared.json"))
    assert context.stage_path(output).parent.is_dir()


@pytest.mark.parametrize("rollback_fails", [False, True])
def test_last_moment_publication_conflict_restores_prior_replacements(job_env, monkeypatch, rollback_fails):
    from towards_victory_editor_web.services import tooling

    tool, manager = job_env
    outputs = (tool.output, tool.root / "last.json")
    for output in outputs:
        output.write_text('{"old":true}')

    @contextmanager
    def prepare(options):
        def run(context):
            for output in outputs:
                context.stage_path(output).write_text('{"new":true}')
            return ToolResult()
        yield ToolPlan((), outputs, run)

    copy = tooling.shutil.copy2
    def change_during_copy(source, target):
        if rollback_fails and ".backup" in source.parts and target == outputs[0]:
            raise PermissionError("restore blocked")
        result = copy(source, target)
        if target.name.startswith("last.json.") and target.suffix == ".tmp":
            outputs[1].write_text('{"external":true}')
        return result

    monkeypatch.setattr(tool, "prepare", prepare)
    monkeypatch.setattr(tooling.shutil, "copy2", change_during_copy)
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert "changed before publication" in job["operation"]["error"]
    assert outputs[0].read_text() == ('{"new":true}' if rollback_fails else '{"old":true}')
    assert outputs[1].read_text() == '{"external":true}'
    assert job["formal_output_changes"] == ["last.json"]
    assert job["outputs_may_be_partial"] is True
    if rollback_fails:
        assert "Rollback incomplete" in job["operation"]["error"]
        assert "restore blocked" in job["operation"]["error"]
    _, details = manager.operation_store.get_with_details(job["operation"]["id"])
    assert details["formal_output_changes"] == ["last.json"]


@pytest.mark.parametrize("fails", [False, True])
def test_optional_png_deleted_in_staging_is_deleted_only_on_success(job_env, monkeypatch, fails):
    tool, manager = job_env
    png = tool.root / "kept.png"
    png.write_bytes(b"original PNG")

    @contextmanager
    def prepare(options):
        def run(context):
            context.stage_path(tool.output).write_text('{}')
            context.stage_path(png).unlink()
            if fails:
                raise RuntimeError("generation failed")
            return ToolResult()
        yield ToolPlan((), (tool.output,), run, optional_outputs=(png,))

    monkeypatch.setattr(tool, "prepare", prepare)
    job = execute(tool, manager)
    assert job["operation"]["status"] == ("failed" if fails else "succeeded"), job["operation"]["error"]
    deleted = [item["path"] for item in job["artifacts"] if item["role"] == "deleted"]
    if fails:
        assert png.read_bytes() == b"original PNG"
        assert deleted == []
    else:
        # A stale PNG left beside regenerated outputs would be preferred as
        # the source by later rebuilds, so the handler's deletion is published.
        assert not png.exists()
        assert deleted == ["kept.png"]
    _, details = manager.operation_store.get_with_details(job["operation"]["id"])
    assert details["artifacts"] == job["artifacts"]


def test_cancelled_queued_job_does_not_try_to_acquire_busy_resource(job_env):
    from towards_victory_editor_web.services.platform import resource_operation

    tool, manager = job_env
    with resource_operation(tool.spec.resource_ids):
        with manager._execution_lock:
            job = manager.submit(tool.spec.id, {})
            manager.cancel(job.id)
        wait_for_jobs(manager)
    manager.shutdown()
    payload = job.payload()
    assert payload["operation"]["status"] == "cancelled"
    assert payload["operation"]["started_at"] is None
    assert payload["operation"]["error"] == "Cancellation requested"
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
        context.stage_path(tool.output).write_text('{}')

    tool.action = action
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert job["source_snapshots"][0]["sha256"] == "missing"
    assert "Declared inputs changed" in job["operation"]["error"]


@pytest.mark.parametrize("extension,content,error", [
    ("txt", "wrong format", "not declared"),
    ("json", "not JSON", "Output validation failed"),
])
def test_invalid_artifact_retains_manifest(job_env, extension, content, error):
    tool, manager = job_env
    tool.output = tool.root / f"output.{extension}"
    tool.action = lambda context: context.stage_path(tool.output).write_text(content)
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert error in job["operation"]["error"]
    assert job["artifacts"][0]["path"] == tool.output.name
    assert job["metadata"]["output_validation"][0]["valid"] is False


def test_unchanged_output_is_validated_and_reported(job_env):
    tool, manager = job_env
    tool.output.write_text('{}')
    tool.action = lambda context: None
    job = execute(tool, manager)
    assert job["operation"]["status"] == "succeeded"
    assert job["artifacts"][0]["changed"] is False


def test_missing_staged_output_does_not_report_formal_deletion(job_env):
    tool, manager = job_env
    tool.output.write_text('{}')
    tool.action = lambda context: context.stage_path(tool.output).unlink()
    job = execute(tool, manager)
    assert job["operation"]["status"] == "failed"
    assert job["missing_outputs"] == ["output.json"]
    assert job["artifacts"] == []
    assert tool.output.read_text() == '{}'
    assert job["outputs_may_be_partial"] is False


@pytest.mark.usefixtures("without_wonder_service")
def test_http_job_contract_and_crop_commit_conflict(job_env, monkeypatch):
    from towards_victory_editor_web import server
    from towards_victory_editor_web.services.cropper import CropperService

    tool, manager = job_env
    cropper = CropperService(tasks=[], data_path=tool.root / "crops.json", repo_root=tool.root)
    monkeypatch.setattr(server, "registry", manager.registry)
    monkeypatch.setattr(server, "PACKAGE_ROOT", tool.root / "web")
    monkeypatch.setattr(server, "cropper", cropper)
    started, finish = threading.Event(), threading.Event()

    def action(context):
        started.set()
        assert finish.wait(5), "test did not release generator"
        context.stage_path(tool.output).write_text('{}')

    tool.action = action
    with TestClient(server.create_app()) as client:
        resource = client.get("/api/resources/editor.wonder_crop").json()
        base = {item["path"]: item["sha256"] for item in resource["change_set"]["base"]}
        submitted = client.post("/api/jobs", json={"tool": tool.spec.id, "options": {}})
        assert submitted.status_code == 200
        assert started.wait(5)
        try:
            job_id = submitted.json()["operation"]["id"]
            running = client.get(f"/api/jobs/{job_id}").json()
            assert running["operation"]["resource_ids"] == ["editor.wonder_crop"]
            assert running["source_snapshots"][0]["path"] == "source.txt"
            assert running["declared_outputs"] == ["output.json"]
            conflict = client.post("/api/resources/editor.wonder_crop/commit", json={"base": base, "edits": {}})
            assert conflict.status_code == 409
            assert "Resource busy" in conflict.json()["detail"]
            assert conflict.json()["code"] == "resource_busy"
            assert conflict.json()["operation"]["status"] == "failed"
            assert conflict.json()["operation_id"] != running["operation"]["id"]
            assert not cropper.data_path.exists()
        finally:
            finish.set()
            wait_for_jobs(client.app.state.jobs)
        completed = client.get(f"/api/jobs/{job_id}").json()
        assert completed["operation"]["status"] == "succeeded"
        assert completed["artifacts"][0]["path"] == "output.json"
        assert client.get(f"/api/jobs/{job_id}?after_line={completed['line_cursor']}").json()["lines"] == []
        assert client.get(f"/api/jobs/{job_id}?after_line=-1").status_code == 422
        assert client.post("/api/resources/editor.wonder_crop/commit", json={"base": base, "edits": {}}).status_code == 200
