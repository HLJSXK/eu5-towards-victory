#!/usr/bin/env python3
"""Regression checks for scripts/ai_context.py routing."""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import ai_context  # noqa: E402


def route_ids(context: dict) -> set[str]:
    return {entry["id"] for entry in context["domains"]}


def card_paths(context: dict) -> set[str]:
    return {entry["path"] for entry in context["cards"]}


def alert_ids(context: dict) -> set[str]:
    return {entry["id"] for entry in context["alerts"]}


def build(files: list[str]) -> dict:
    return ai_context.build_context(files, ai_context.load_routes())


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    building_file = "src_engineering_department/in_game/common/building_types/tv_engineering_department_wonder_mechanics_buildings.txt"
    ctx = build([building_file])
    assert_true("wonders" in route_ids(ctx), "wonder building file should route to wonders")
    assert_true("wonder_buildings" in route_ids(ctx), "wonder building file should route to wonder_buildings")
    assert_true("object_on_built" in alert_ids(ctx), "on_built should produce immediate alert")
    assert_true("docs/knowledge/risk_cards/object_on_built.md" in card_paths(ctx), "on_built card should be required")

    workflow_ctx = build(["scripts/ai_context.py", "CLAUDE.md"])
    assert_true("ai_workflow" in route_ids(workflow_ctx), "workflow files should route to ai_workflow")
    assert_true("variable_map" not in route_ids(workflow_ctx), "workflow prose should not trigger variable_map routing")

    loc_ctx = build(["src/main_menu/localization/english/towards_victory_l_english.yml"])
    assert_true("localization" in route_ids(loc_ctx), "localization path should route to localization")

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        ai_context.print_markdown(ctx, full=False)
    default_output = buffer.getvalue()
    assert_true("## Immediate Risk Alerts" in default_output, "default output should include alerts")
    assert_true("## Risk Card:" not in default_output, "default output should not inline full cards")

    json.dumps(ctx, ensure_ascii=False)
    print("[OK] ai_context routing checks passed.")


if __name__ == "__main__":
    main()
