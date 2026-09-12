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


def audit_ids(context: dict) -> set[str]:
    return {entry["id"] for entry in context.get("cross_surface_audits", [])}


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

    eureka_file = "src_eureka/in_game/gui/advances_lateralview.gui"
    eureka_ctx = build([eureka_file])
    assert_true("eureka" in {item["id"] for item in eureka_ctx["subprojects"]}, "Eureka files should activate Eureka overview")
    assert_true("docs/knowledge/PROJECT_OVERVIEW.md" in {item["path"] for item in eureka_ctx["reads"]}, "project overview should always be required")
    assert_true("docs/knowledge/subprojects/eureka.md" in {item["path"] for item in eureka_ctx["reads"]}, "Eureka overview should be required")
    assert_true("docs/knowledge/eureka_gui_maintenance.md" in {item["path"] for item in eureka_ctx["reads"]}, "Eureka GUI maintenance map should be required")
    assert_true("eureka_advance_surfaces" in route_ids(build([eureka_file])), "Advance surface filename route should fire")
    eureka_audits = eureka_ctx.get("cross_surface_audits", [])
    assert_true("eureka_advance_surfaces" in audit_ids(eureka_ctx), "Advance surface route should emit a mandatory cross-surface audit")
    audit_paths = {path for audit in eureka_audits for path in audit.get("paths", [])}
    assert_true("src_eureka/in_game/gui/technology_lateralview.gui" in audit_paths, "Advance audit must include technology_lateralview.gui")
    assert_true("src_eureka/in_game/gui/advances_lateralview.gui" in audit_paths, "Advance audit must include advances_lateralview.gui")
    assert_true(eureka_ctx["ownership"] == [{"path": eureka_file, "owner": "scripts_eureka/patch_gui_progress.py", "reason": "Eureka GUI outputs are regenerated from vanilla files by the checked-in patcher"}], "Eureka GUI output should identify its patch generator")

    eureka_backend_file = "src_eureka/in_game/common/advances/tv_eureka_guilds.txt"
    backend_ctx = build([eureka_backend_file])
    assert_true("eureka_advance_surfaces" in audit_ids(backend_ctx), "Any Eureka backend change should emit the Advance cross-surface audit")
    assert_true("eureka_advance_backend" in route_ids(backend_ctx), "Eureka Advance backend files should route to the dedicated backend domain")

    keyword_ctx = ai_context.build_context(["scripts_eureka/patch_gui_progress.py"], ai_context.load_routes(), ["Advance", "research"])
    assert_true("eureka_advance_concept" in route_ids(keyword_ctx), "Advance/research keywords should route the full Eureka concept")
    assert_true("docs/knowledge/risk_cards/eureka_advance_surfaces.md" in card_paths(keyword_ctx), "Advance concept card should be required")
    engineering_ctx = build(["src_engineering_department/in_game/common/building_types/tv_engineering_department_wonder_mechanics_buildings.txt"])
    assert_true({item["id"] for item in engineering_ctx["subprojects"]} == {"engineering_department"}, "generated data sources must not activate unrelated main subproject")
    wonder_data_ctx = build(["data/wonders.yaml"])
    assert_true("main_mod" not in {item["id"] for item in wonder_data_ctx["subprojects"]}, "shared wonder data must not be claimed by main mod")

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        ai_context.print_markdown(ctx, full=False)
    default_output = buffer.getvalue()
    assert_true("## Immediate Risk Alerts" in default_output, "default output should include alerts")
    eureka_buffer = io.StringIO()
    with redirect_stdout(eureka_buffer):
        ai_context.print_markdown(eureka_ctx, full=False)
    eureka_output = eureka_buffer.getvalue()
    assert_true("## Required Cross-Surface Audits" in eureka_output, "default output should include cross-surface audit instructions")
    assert_true("## Risk Card:" not in default_output, "default output should not inline full cards")

    json.dumps(ctx, ensure_ascii=False)
    print("[OK] ai_context routing checks passed.")


if __name__ == "__main__":
    main()
