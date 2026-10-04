from __future__ import annotations

import pytest

from towards_victory_editor_web.services.platform import OperationLog


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
