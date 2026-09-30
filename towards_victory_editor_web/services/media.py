"""Unified tool registry and job API used by the FastAPI application."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .media_tools import registry
from .tooling import JobManager, ToolSpec

REPO_ROOT = Path(__file__).resolve().parents[2]
jobs = JobManager(registry, REPO_ROOT)

registry.register_spec(ToolSpec(
    "editor.cost_reward",
    "Cost / reward editor",
    "Edit cost, reward, modifier, and task-pool data.",
    "editor",
    interactive=True,
))
registry.register_spec(ToolSpec(
    "editor.victory_tree",
    "Victory tree planner",
    "Arrange victory tree nodes and save their normalized positions.",
    "editor",
    interactive=True,
))
registry.register_spec(ToolSpec(
    "editor.wonder",
    "Wonder localization editor",
    "Edit wonder localization and mechanics data.",
    "editor",
    interactive=True,
))
registry.register_spec(ToolSpec(
    "editor.wonder_crop",
    "Wonder image cropper",
    "Edit source image crops used by the wonder DDS rebuild job.",
    "editor",
    interactive=True,
))


def bootstrap_payload() -> dict[str, Any]:
    return {
        "tools": registry.payload(interactive=False),
        "config": {
            "historical_inputs": [
                str(path.relative_to(REPO_ROOT)).replace("\\", "/")
                for path in sorted((REPO_ROOT / "assets" / "historical").glob("*"))
                if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
            ]
        },
    }
