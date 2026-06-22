#!/usr/bin/env python3
"""Small in-memory tests for the unique wonder ritual Harness quality gates."""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from gen_unique_wonder_ritual_code import (  # noqa: E402
    CodegenError,
    generate_fragments_for_payload,
)
from wonder_unique_ritual_harness import validate_spec_payload  # noqa: E402


WONDER = {
    "id": 999,
    "key": "unique_test_wonder",
    "base_key": "great_lighthouse",
    "location": "testopolis",
}

NODE_KEYS = ["opening", "materials", "monthly_gate", "retry_choice", "final_prep", "reward"]
TEMPLATES = [
    "sequential_event_chain",
    "branch_retry_event",
    "monthly_progress_gate",
    "simple_progress_track_ui_binding",
    "final_reward_dispatch_stub",
]


def event_row(event_id: int, node_key: str, *, retry: bool = False) -> dict:
    options = [f"event.{event_id}.a"]
    if retry:
        options.append(f"event.{event_id}.b")
    return {
        "event_id": event_id,
        "title_key": f"event.{event_id}.t",
        "desc_key": f"event.{event_id}.d",
        "option_keys": options,
        "node_key": node_key,
    }


def node(
    key: str,
    event_id: int,
    *,
    kind: str = "event",
    reads: list[str] | None = None,
    writes: list[str] | None = None,
    next_nodes: list[str] | None = None,
    failure_or_retry: bool = False,
    retry_target: str | None = None,
) -> dict:
    return {
        "key": key,
        "kind": kind,
        "event_id": event_id,
        "player_visible": True,
        "historical_anchor": f"anchor_{key}",
        "enter_condition": f"{key}_enter_check",
        "completion_condition": f"{key}_complete_check",
        "failure_or_retry": failure_or_retry,
        "retry_target": retry_target,
        "next_nodes": next_nodes or [],
        "writes": writes or [],
        "reads": reads or [],
        "ui_state": {"variable_refs": reads or writes or []},
        "loc_refs": [f"node.{key}.label"],
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
        "event_ids": [
            {"id": 1001, "key": "opening"},
            {"id": 1002, "key": "materials"},
            {"id": 1003, "key": "monthly_gate"},
            {"id": 1004, "key": "retry_choice"},
            {"id": 1005, "key": "final_prep"},
            {"id": 1006, "key": "reward"},
        ],
        "node_graph": {
            "model": "state_machine_dsl_v1",
            "historical_mechanic": "A visible historical testing mechanic with sequential steps and retry.",
            "listeners": ["monthly"],
            "summary": "Test summary.",
            "variables": [
                {
                    "name": "tv_wonder_test_stage",
                    "scope": "country",
                    "type": "number",
                    "initial_value": 0,
                    "writer_nodes": ["opening", "materials", "retry_choice", "reward"],
                    "reader_nodes": NODE_KEYS,
                    "cleanup": "project_state_clear",
                },
                {
                    "name": "tv_wonder_test_progress",
                    "scope": "country",
                    "type": "number",
                    "initial_value": 0,
                    "writer_nodes": ["monthly_gate"],
                    "reader_nodes": ["monthly_gate", "retry_choice", "final_prep", "reward"],
                    "cleanup": "project_state_clear",
                },
            ],
            "nodes": [
                node("opening", 1001, writes=["tv_wonder_test_stage"], next_nodes=["materials"]),
                node(
                    "materials",
                    1002,
                    reads=["tv_wonder_test_stage"],
                    writes=["tv_wonder_test_stage"],
                    next_nodes=["monthly_gate"],
                ),
                node(
                    "monthly_gate",
                    1003,
                    kind="monthly_progress_gate",
                    reads=["tv_wonder_test_stage", "tv_wonder_test_progress"],
                    writes=["tv_wonder_test_progress"],
                    next_nodes=["retry_choice"],
                ),
                node(
                    "retry_choice",
                    1004,
                    kind="retry_event",
                    reads=["tv_wonder_test_progress"],
                    writes=["tv_wonder_test_stage"],
                    next_nodes=["final_prep"],
                    failure_or_retry=True,
                    retry_target="materials",
                ),
                node(
                    "final_prep",
                    1005,
                    reads=["tv_wonder_test_stage", "tv_wonder_test_progress"],
                    writes=["tv_wonder_test_stage"],
                    next_nodes=["reward"],
                ),
                node(
                    "reward",
                    1006,
                    kind="final_reward_dispatch",
                    reads=["tv_wonder_test_stage"],
                    writes=["tv_wonder_test_stage"],
                ),
            ],
            "edges": [
                {"from": "opening", "to": "materials", "condition": "always", "effect": "advance", "label_key": "edge.opening.materials"},
                {"from": "materials", "to": "monthly_gate", "condition": "always", "effect": "advance", "label_key": "edge.materials.monthly"},
                {"from": "monthly_gate", "to": "retry_choice", "condition": "progress_met", "effect": "advance", "label_key": "edge.monthly.retry"},
                {"from": "retry_choice", "to": "materials", "condition": "retry", "effect": "retry", "label_key": "edge.retry.materials"},
                {"from": "retry_choice", "to": "final_prep", "condition": "accepted", "effect": "advance", "label_key": "edge.retry.final"},
                {"from": "final_prep", "to": "reward", "condition": "always", "effect": "advance", "label_key": "edge.final.reward"},
            ],
            "actions": [
                {
                    "key": "start_chain",
                    "kind": "generator_template",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "sequential_event_chain",
                },
                {
                    "key": "retry_branch",
                    "kind": "generator_template",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "branch_retry_event",
                },
                {
                    "key": "monthly_gate",
                    "kind": "generator_template",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "monthly_progress_gate",
                },
                {
                    "key": "ui_progress",
                    "kind": "generator_template",
                    "scope": "gui_fragment",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "simple_progress_track_ui_binding",
                },
                {
                    "key": "reward_dispatch",
                    "kind": "reward_dispatch_stub",
                    "scope": "country",
                    "verified_interface": "harness_v1_intermediate_fragment",
                    "generator_template": "final_reward_dispatch_stub",
                },
            ],
            "checks": [
                {
                    "key": "stage_ready",
                    "kind": "generator_template",
                    "generator_template": "sequential_event_chain",
                    "tooltip_key": "check.stage_ready",
                },
                {
                    "key": "monthly_ready",
                    "kind": "generator_template",
                    "generator_template": "monthly_progress_gate",
                    "tooltip_key": "check.monthly_ready",
                },
            ],
        },
        "ui_model": {
            "components": [{"type": "progress_track", "key": "progress", "value_variable": "tv_wonder_test_progress"}],
            "bindings": [
                {
                    "key": "progress_binding",
                    "component_key": "progress",
                    "variable_refs": ["tv_wonder_test_stage", "tv_wonder_test_progress"],
                    "node_refs": ["monthly_gate", "reward"],
                    "loc_refs": ["ui.progress.label"],
                }
            ],
        },
        "generation": {
            "status": "ready_for_dry_run",
            "target_files": ["data/generated_fragments/unique_wonder_rituals/unique_test_wonder_ritual_codegen.md"],
            "verified_templates": TEMPLATES,
            "blocked_templates": [],
            "dry_run_notes": "In-memory fixture only.",
        },
        "rewards": {
            "permanent_country_modifier": {"status": "implemented", "description": "A country reward."},
            "local_building_reward": {"status": "implemented", "description": "A local reward."},
            "one_time_reward": {"status": "implemented", "description": "A one-time reward."},
        },
        "localization": {
            "event_keys": [
                event_row(1001, "opening"),
                event_row(1002, "materials"),
                event_row(1003, "monthly_gate"),
                event_row(1004, "retry_choice", retry=True),
                event_row(1005, "final_prep"),
                event_row(1006, "reward"),
            ]
        },
        "implementation_notes": {"needs_verification": []},
    }


def loc() -> dict[str, str]:
    long_text = "This event description is intentionally long enough to satisfy the ritual text density gate. " * 2
    data: dict[str, str] = {}
    for event_id in range(1001, 1007):
        data[f"event.{event_id}.t"] = f"Title {event_id}"
        data[f"event.{event_id}.d"] = long_text
        data[f"event.{event_id}.a"] = "Continue"
        data[f"event.{event_id}.b"] = "Retry"
    for key in NODE_KEYS:
        data[f"node.{key}.label"] = key
    for key in (
        "edge.opening.materials",
        "edge.materials.monthly",
        "edge.monthly.retry",
        "edge.retry.materials",
        "edge.retry.final",
        "edge.final.reward",
        "check.stage_ready",
        "check.monthly_ready",
        "ui.progress.label",
    ):
        data[key] = key
    return data


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


def assert_codegen_error(name: str, entry: dict, needle: str) -> None:
    try:
        generate_fragments_for_payload(
            {"unique_wonders": [entry]},
            wonder_keys={"unique_test_wonder"},
        )
    except CodegenError as exc:
        if needle not in str(exc):
            raise AssertionError(f"{name}: expected codegen error containing {needle!r}, got {exc}") from exc
        return
    raise AssertionError(f"{name}: expected CodegenError containing {needle!r}")


def main() -> None:
    good_errors = validate_spec_payload(
        {"unique_wonders": [valid_entry()]},
        wonders=[WONDER],
        localization=loc(),
        require_all_wonders=True,
    )
    if good_errors:
        raise AssertionError(f"valid entry unexpectedly failed: {good_errors}")

    result = generate_fragments_for_payload(
        {"unique_wonders": [valid_entry()]},
        wonder_keys={"unique_test_wonder"},
    )
    generated_text = result["generated"][0]["text"]
    for expected in (
        "## Event Skeleton",
        "## Variable Table",
        "## UI Binding Summary",
        "## Reward Dispatch Stub",
        "tv_engineering_department.1006",
    ):
        if expected not in generated_text:
            raise AssertionError(f"codegen dry-run missing {expected!r}")

    duplicate = valid_entry()
    duplicate["event_ids"][2]["id"] = 1002
    assert_has_error("duplicate event id", duplicate, "duplicates")

    missing_reward = valid_entry()
    missing_reward["rewards"]["one_time_reward"]["status"] = "pending"
    assert_has_error("missing reward", missing_reward, "one_time_reward")

    short_text = valid_entry()
    short_loc = loc()
    for event_id in range(1001, 1007):
        short_loc[f"event.{event_id}.d"] = "Short."
    assert_has_error("short text", short_text, "too thin", localization=short_loc)

    one_event = valid_entry()
    one_event["event_ids"] = one_event["event_ids"][:1]
    one_event["node_graph"]["nodes"] = one_event["node_graph"]["nodes"][:1]
    assert_has_error("one-event ritual", one_event, "3 player-visible ritual nodes")

    bad_runtime = valid_entry()
    bad_runtime["node_graph"]["variables"][0]["name"] = "tv_other_stage"
    assert_has_error("runtime prefix", bad_runtime, "must start with tv_wonder_test")

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

    edge_missing_node = valid_entry()
    edge_missing_node["node_graph"]["edges"][0]["to"] = "missing"
    assert_has_error("edge missing node", edge_missing_node, "edge to references undeclared node missing")

    node_undeclared_read = valid_entry()
    node_undeclared_read["node_graph"]["nodes"][0]["reads"] = ["tv_wonder_test_missing"]
    assert_has_error("node undeclared read", node_undeclared_read, "reads undeclared variable tv_wonder_test_missing")

    binding_undeclared_variable = valid_entry()
    binding_undeclared_variable["ui_model"]["bindings"][0]["variable_refs"].append("tv_wonder_test_missing")
    assert_has_error(
        "binding undeclared variable",
        binding_undeclared_variable,
        "ui binding progress_binding references undeclared variable tv_wonder_test_missing",
    )

    missing_retry_target = valid_entry()
    missing_retry_target["node_graph"]["nodes"][3]["retry_target"] = "missing"
    assert_has_error("missing retry target", missing_retry_target, "retry_target references undeclared node missing")

    harness_generated_without_targets = valid_entry()
    harness_generated_without_targets["identity"]["status"] = "harness_generated"
    harness_generated_without_targets["generation"]["target_files"] = []
    assert_has_error(
        "harness generated target files",
        harness_generated_without_targets,
        "harness_generated must declare generation.target_files",
    )

    unsupported_node_kind = valid_entry()
    unsupported_node_kind["node_graph"]["nodes"][0]["kind"] = "unsupported_node"
    assert_has_error("unsupported node kind", unsupported_node_kind, "unsupported kind 'unsupported_node'")

    unsupported_action_kind = valid_entry()
    unsupported_action_kind["node_graph"]["actions"][0]["kind"] = "unsupported_action"
    assert_has_error("unsupported action kind", unsupported_action_kind, "unsupported kind 'unsupported_action'")

    unsupported_check_kind = valid_entry()
    unsupported_check_kind["node_graph"]["checks"][0]["kind"] = "unsupported_check"
    assert_has_error("unsupported check kind", unsupported_check_kind, "unsupported kind 'unsupported_check'")

    unverified = valid_entry()
    unverified["implementation_notes"]["needs_verification"] = ["modifier_key"]
    assert_has_error("unverified implementation", unverified, "unverified implementation note")

    unverified_token = valid_entry()
    unverified_token["generation"]["dry_run_notes"] = "needs_verification"
    assert_has_error("needs verification token", unverified_token, "cannot contain needs_verification")

    explicit_stub = valid_entry()
    explicit_stub["identity"]["status"] = "stub"
    assert_codegen_error("explicit stub codegen", explicit_stub, "cannot be generated by Harness codegen")

    print("[OK] Unique wonder ritual Harness quality-gate tests passed.")


if __name__ == "__main__":
    main()
