from __future__ import annotations

from contextlib import contextmanager
import sqlite3
import threading

import pytest
from fastapi.testclient import TestClient

from towards_victory_editor_web.services.operation_store import OperationStore
from towards_victory_editor_web.services.platform import (
    OperationCancelled, OperationLog, ResourceBusyError, resource_operation, run_operation,
)


def test_operation_log_reports_shared_success_lifecycle() -> None:
    operation = OperationLog("resource_commit", ("editor.wonder", "editor.cost_reward"))

    operation.start()
    operation.event("candidate prepared")
    operation.succeed()
    payload = operation.payload()

    assert payload["id"] == operation.id
    assert payload["kind"] == "resource_commit"
    assert payload["status"] == "succeeded"
    assert payload["resource_ids"] == ["editor.cost_reward", "editor.wonder"]
    assert payload["error"] is None
    assert payload["started_at"] is not None
    assert payload["finished_at"] is not None
    assert [event["message"] for event in payload["events"]] == [
        "started", "candidate prepared", "succeeded",
    ]


def test_operation_log_cancel_request_is_visible_before_terminal_state() -> None:
    operation = OperationLog("media_job", ("editor.wonder_crop",))

    operation.start()
    operation.request_cancel()
    assert operation.payload()["status"] == "cancelling"
    assert operation.payload()["cancel_requested"] is True

    operation.cancel()
    payload = operation.payload()
    assert payload["status"] == "cancelled"
    assert payload["error"] == "Cancellation requested"


@pytest.mark.parametrize("terminal", ["succeeded", "failed", "cancelled"])
def test_terminal_operation_cannot_be_restarted_or_overwritten(terminal) -> None:
    operation = OperationLog("media_job")
    operation.start()
    if terminal == "succeeded":
        operation.succeed()
    elif terminal == "failed":
        operation.fail("original failure")
    else:
        operation.cancel()
    finished = operation.payload()

    operation.start()
    operation.request_cancel()
    operation.succeed()
    operation.fail("later failure")
    operation.cancel("later cancellation")

    assert operation.payload() == finished


def test_executor_busy_resource_releases_locks_without_starting() -> None:
    operation = OperationLog("resource_commit", ("test.first", "test.second"))
    calls = []
    with resource_operation(("test.second",)):
        with pytest.raises(ResourceBusyError) as caught:
            run_operation(operation, lambda: calls.append("write"))
        with resource_operation(("test.first",), blocking=False):
            pass

    assert not calls
    assert caught.value.operation == operation.payload()
    assert operation.payload()["started_at"] is None
    assert operation.payload()["status"] == "failed"
    assert len(operation.payload()["events"]) == 1


def test_executor_waits_for_cleanup_and_preserves_original_failure() -> None:
    operation = OperationLog("resource_commit", ("test.cleanup",))
    failure = ValueError("cleanup failed")

    @contextmanager
    def transaction():
        yield
        assert operation.payload()["status"] == "running"
        raise failure

    def execute():
        with transaction():
            return "candidate result"

    with pytest.raises(ValueError) as caught:
        run_operation(operation, execute)
    assert caught.value is failure
    assert failure.operation == operation.payload()
    assert failure.operation["status"] == "failed"
    with resource_operation(("test.cleanup",), blocking=False):
        pass


@pytest.mark.parametrize("fail_after_cancel", [False, True])
def test_executor_cancellation_wins_over_result_or_error(fail_after_cancel) -> None:
    operation = OperationLog("media_job", ("test.cancel",))

    def execute():
        operation.request_cancel()
        if fail_after_cancel:
            raise ValueError("stale input")
        return "done"

    with pytest.raises(OperationCancelled) as caught:
        run_operation(operation, execute)
    assert caught.value.operation == operation.payload()
    assert operation.payload()["status"] == "cancelled"
    assert operation.payload()["error"] == "Cancellation requested"
    with resource_operation(("test.cancel",), blocking=False):
        pass


def test_executor_cannot_repeat_side_effects_for_an_operation() -> None:
    operation = OperationLog("resource_commit")
    calls = []
    assert run_operation(operation, lambda: calls.append("write") or "result") == "result"
    completed = operation.payload()
    with pytest.raises(RuntimeError, match="only be executed once"):
        run_operation(operation, lambda: calls.append("second write"))
    operation.request_cancel()
    assert operation.payload() == completed
    assert calls == ["write"]


def test_executor_records_error_diagnostics_before_terminal_publication() -> None:
    operation = OperationLog("media_job")
    observed = []

    def execute():
        raise ValueError("generator failed")

    def record_failure(error):
        observed.append((str(error), operation.payload()["status"]))

    with pytest.raises(ValueError):
        run_operation(operation, execute, on_error=record_failure)
    assert observed == [("generator failed", "running")]
    assert operation.payload()["status"] == "failed"


def test_executor_observer_failure_still_publishes_terminal_state() -> None:
    operation = OperationLog("media_job")

    def record_failure(_error):
        raise RuntimeError("diagnostic observer failed")

    with pytest.raises(RuntimeError, match="diagnostic observer failed"):
        run_operation(
            operation,
            lambda: (_ for _ in ()).throw(ValueError("generator failed")),
            on_error=record_failure,
        )

    payload = operation.payload()
    assert payload["status"] == "failed"
    assert payload["error"] == "generator failed"
    assert payload["finished_at"] is not None


def test_executor_observer_runs_without_operation_lock() -> None:
    operation = OperationLog("media_job")
    observer_started = threading.Event()
    release_observer = threading.Event()
    cancel_completed = threading.Event()

    def record_failure(_error):
        observer_started.set()
        assert release_observer.wait(2)

    def request_cancel():
        assert observer_started.wait(2)
        operation.request_cancel()
        cancel_completed.set()

    errors = []

    def run():
        try:
            run_operation(
                operation,
                lambda: (_ for _ in ()).throw(ValueError("generator failed")),
                on_error=record_failure,
            )
        except Exception as error:
            errors.append(error)

    runner = threading.Thread(target=run)
    runner.start()
    assert observer_started.wait(2)
    requester = threading.Thread(target=request_cancel)
    requester.start()
    try:
        assert cancel_completed.wait(2)
    finally:
        release_observer.set()
        requester.join(timeout=2)
        runner.join(timeout=2)
    assert not requester.is_alive()
    assert not runner.is_alive()
    assert len(errors) == 1 and isinstance(errors[0], ValueError)
    assert operation.payload()["status"] == "failed"


def test_operation_store_queries_snapshots_after_reopen(tmp_path) -> None:
    path = tmp_path / "operations.sqlite3"
    store = OperationStore(path)
    completed = OperationLog("resource_commit", ("editor.wonder",), store=store)
    run_operation(completed, lambda: completed.event("saved") or "done")
    failed = OperationLog("media_job", store=store)
    with pytest.raises(ValueError, match="generator failed"):
        run_operation(failed, lambda: (_ for _ in ()).throw(ValueError("generator failed")))

    assert store.get(completed.id) == completed.payload()
    assert store.get(failed.id) == failed.payload()
    assert [item["id"] for item in store.recent(kind="media_job")] == [failed.id]
    assert [item["id"] for item in store.recent(status="succeeded")] == [completed.id]
    assert "events" not in store.recent(limit=1)[0]
    store.close()

    reopened = OperationStore(path)
    try:
        assert reopened.get(completed.id) == completed.payload()
        assert reopened.get(failed.id) == failed.payload()
        with pytest.raises(KeyError, match="Unknown operation"):
            reopened.get("missing")
    finally:
        reopened.close()


def test_reopen_marks_unfinished_operations_interrupted_without_replaying(tmp_path) -> None:
    path = tmp_path / "operations.sqlite3"
    store = OperationStore(path)
    queued = OperationLog("media_job", store=store)
    running = OperationLog("resource_commit", store=store)
    running.start()
    cancelling = OperationLog("media_job", store=store)
    cancelling.request_cancel()
    completed = OperationLog("media_job", store=store)
    completed.start()
    completed.succeed()
    store.close()

    reopened = OperationStore(path)
    try:
        for operation in (queued, running, cancelling):
            payload = reopened.get(operation.id)
            assert payload["status"] == "failed"
            assert payload["error"] == OperationStore.INTERRUPTED_ERROR
            assert payload["finished_at"] is not None
            assert payload["events"][-1]["message"] == OperationStore.INTERRUPTED_ERROR
        assert reopened.get(queued.id)["started_at"] is None
        assert reopened.get(running.id)["started_at"] is not None
        assert reopened.get(cancelling.id)["cancel_requested"] is True
        assert reopened.get(completed.id) == completed.payload()
    finally:
        reopened.close()


def test_persistence_failure_is_visible_without_changing_commit_outcome(tmp_path, monkeypatch) -> None:
    store = OperationStore(tmp_path / "operations.sqlite3")
    operation = OperationLog("resource_commit", store=store)

    def reject_save(_payload):
        raise sqlite3.OperationalError("disk unavailable")

    monkeypatch.setattr(store, "save", reject_save)
    try:
        assert run_operation(operation, lambda: "saved") == "saved"
        assert operation.payload()["status"] == "succeeded"
        assert "disk unavailable" in operation.payload()["persistence_error"]
    finally:
        store.close()


def test_operation_query_api_returns_full_record_and_recent_summary(tmp_path) -> None:
    from towards_victory_editor_web.server import create_app

    store = OperationStore(tmp_path / "operations.sqlite3")
    operation = OperationLog("query_contract_test", store=store)
    run_operation(operation, lambda: "done")
    try:
        with TestClient(create_app(store)) as client:
            detail = client.get(f"/api/operations/{operation.id}")
            recent = client.get("/api/operations", params={"kind": "query_contract_test", "limit": 1})
            missing = client.get("/api/operations/missing")
    finally:
        store.close()

    assert detail.status_code == 200
    assert detail.json() == operation.payload()
    assert recent.status_code == 200
    assert recent.json()["operations"] == [
        {key: value for key, value in operation.payload().items() if key != "events"}
    ]
    assert missing.status_code == 404


def test_lifespan_restores_shared_operation_store_references(tmp_path) -> None:
    from towards_victory_editor_web import server

    store = OperationStore(tmp_path / "operations.sqlite3")
    previous_cropper_store = server.cropper.operation_store
    previous_jobs_store = server.jobs.operation_store
    try:
        with TestClient(server.create_app(store)):
            assert server.cropper.operation_store is store
            assert server.jobs.operation_store is store
        assert server.cropper.operation_store is previous_cropper_store
        assert server.jobs.operation_store is previous_jobs_store
    finally:
        store.close()


def test_operation_events_are_throttled_but_lifecycle_transitions_persisted(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(OperationLog, "EVENT_PERSIST_INTERVAL", 3600.0)
    store = OperationStore(tmp_path / "operations.sqlite3")
    writes = []
    original_save = store.save
    store.save = lambda payload: (writes.append(payload), original_save(payload))[1]
    try:
        operation = OperationLog("media_job", store=store)
        assert len(writes) == 1
        for index in range(10):
            operation.event(f"generator output {index}")
        assert len(writes) == 1
        operation.start()
        assert len(writes) == 2
        operation.succeed()
        assert len(writes) == 3
    finally:
        store.close()
