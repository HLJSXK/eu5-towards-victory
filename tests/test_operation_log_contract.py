from __future__ import annotations

from contextlib import contextmanager
import threading

import pytest

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
