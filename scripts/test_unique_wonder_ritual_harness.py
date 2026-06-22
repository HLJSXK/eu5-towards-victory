#!/usr/bin/env python3
"""Small in-memory tests for the unique wonder ritual Harness quality gates."""

import sys
from copy import deepcopy
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from wonder_unique_ritual_harness import validate_spec_payload  # noqa: E402


WONDER = {
    "id": 999,
    "key": "unique_test_wonder",
    "base_key": "great_lighthouse",
    "location": "testopolis",
}


def valid_entry() -> dict:
    return {
        "identity": {
            "id": 999,
            "key": "unique_test_wonder",
            "base_key": "great_lighthouse",
            "location": "testopolis",
            "runtime_prefix": "tv_wonder_test",
            "status": "implementation_ready",
        },
        "event_ids": [{"id": 1001, "key": "a"}, {"id": 1002, "key": "b"}, {"id": 1003, "key": "c"}],
        "node_graph": {
            "model": "node_graph",
            "historical_mechanic": "A visible historical testing mechanic.",
            "listeners": ["monthly"],
            "summary": "Test summary.",
            "runtime_variables": ["tv_wonder_test_stage"],
            "nodes": [
                {"key": "a", "event_id": 1001, "player_visible": True, "failure_or_retry": False},
                {"key": "b", "event_id": 1002, "player_visible": True, "failure_or_retry": True},
                {"key": "c", "event_id": 1003, "player_visible": True, "failure_or_retry": False},
            ],
        },
        "ui_model": {"components": [{"type": "progress_track", "key": "test", "value_variable": "tv_wonder_test_stage"}]},
        "rewards": {
            "permanent_country_modifier": {"status": "implemented", "description": "A country reward."},
            "local_building_reward": {"status": "implemented", "description": "A local reward."},
            "one_time_reward": {"status": "implemented", "description": "A one-time reward."},
        },
        "localization": {
            "event_keys": [
                {
                    "event_id": 1001,
                    "title_key": "event.1001.t",
                    "desc_key": "event.1001.d",
                    "option_keys": ["event.1001.a"],
                },
                {
                    "event_id": 1002,
                    "title_key": "event.1002.t",
                    "desc_key": "event.1002.d",
                    "option_keys": ["event.1002.a", "event.1002.b"],
                },
                {
                    "event_id": 1003,
                    "title_key": "event.1003.t",
                    "desc_key": "event.1003.d",
                    "option_keys": ["event.1003.a"],
                },
            ]
        },
        "implementation_notes": {"needs_verification": []},
    }


def loc() -> dict[str, str]:
    long_text = "This event description is intentionally long enough to satisfy the ritual text density gate. " * 2
    return {
        "event.1001.t": "A",
        "event.1001.d": long_text,
        "event.1001.a": "Go",
        "event.1002.t": "B",
        "event.1002.d": long_text,
        "event.1002.a": "Pay",
        "event.1002.b": "Retry",
        "event.1003.t": "C",
        "event.1003.d": long_text,
        "event.1003.a": "Finish",
    }


def assert_has_error(
    name: str,
    entry: dict,
    needle: str,
    *,
    localization: dict[str, str] | None = None,
    occupied_event_ids: set[int] | None = None,
) -> None:
    errors = validate_spec_payload(
        {"unique_wonders": [entry]},
        wonders=[WONDER],
        localization=localization or loc(),
        occupied_event_ids=occupied_event_ids,
        require_all_wonders=True,
    )
    if not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected error containing {needle!r}, got {errors}")


def main() -> None:
    good_errors = validate_spec_payload(
        {"unique_wonders": [valid_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if good_errors:
        raise AssertionError(f"valid entry unexpectedly failed: {good_errors}")

    duplicate = valid_entry()
    duplicate["event_ids"][2]["id"] = 1002
    assert_has_error("duplicate event id", duplicate, "duplicates")

    missing_reward = valid_entry()
    missing_reward["rewards"]["one_time_reward"]["status"] = "pending"
    assert_has_error("missing reward", missing_reward, "one_time_reward")

    short_text = valid_entry()
    short_loc = loc()
    short_loc["event.1001.d"] = "Short."
    short_loc["event.1002.d"] = "Short."
    short_loc["event.1003.d"] = "Short."
    assert_has_error("short text", short_text, "too thin", localization=short_loc)

    one_event = valid_entry()
    one_event["event_ids"] = one_event["event_ids"][:1]
    one_event["node_graph"]["nodes"] = one_event["node_graph"]["nodes"][:1]
    assert_has_error("one-event ritual", one_event, "3 player-visible ritual nodes")

    bad_runtime = valid_entry()
    bad_runtime["node_graph"]["runtime_variables"] = ["tv_other_stage"]
    assert_has_error("runtime prefix", bad_runtime, "must start with tv_wonder_test")

    undeclared_runtime = valid_entry()
    undeclared_runtime["ui_model"]["components"][0]["value_variable"] = "tv_wonder_test_missing"
    assert_has_error("undeclared runtime variable", undeclared_runtime, "undeclared runtime variable")

    unsupported_listener = valid_entry()
    unsupported_listener["node_graph"]["listeners"] = ["unsupported_listener"]
    assert_has_error("unsupported listener", unsupported_listener, "unsupported listener")

    occupied_event_id = valid_entry()
    assert_has_error(
        "occupied event id",
        occupied_event_id,
        "collides with an occupied Engineering Department event id",
        occupied_event_ids={1002},
    )

    unverified = valid_entry()
    unverified["implementation_notes"]["needs_verification"] = ["modifier_key"]
    assert_has_error("unverified implementation", unverified, "unverified implementation note")

    print("[OK] Unique wonder ritual Harness quality-gate tests passed.")


if __name__ == "__main__":
    main()
