#!/usr/bin/env python3
"""Run the Editor/Web test suites.

Default (fast) tier: parallel pytest without ``slow`` tests, Node unit tests and
the Web ``--check``, all started together. ``--full`` adds the slow tests (the
real Wonder generator chain) and the Chrome acceptance run.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent

PYTEST_FILES = (
    "tests/test_cost_reward_resource_contract.py",
    "tests/test_victory_tree_resource_contract.py",
    "tests/test_wonder_resource_contract.py",
    "tests/test_wonder_field_preview.py",
    "tests/test_wonder_payload_loading.py",
    "tests/test_cropper_resource_contract.py",
    "tests/test_media_job_contract.py",
    "tests/test_media_cancellation.py",
    "tests/test_media_plans.py",
    "tests/test_operation_log_contract.py",
    "tests/test_editor_file_transactions.py",
    "tests/test_generation_plan.py",
    "tests/test_validation_api.py",
    "tests/test_localization_resource_contract.py",
)
NODE_FILES = (
    "tests/api.cjs",
    "tests/resource_state.cjs",
    "tests/media_job_polling.cjs",
    "tests/cropper_resource_state.cjs",
    "tests/wonder_resource_state.cjs",
    "tests/shared_display.cjs",
    "tests/wonder_values.cjs",
    "tests/wonder_rituals.cjs",
    "tests/wonder_drafts.cjs",
    "tests/wonder_panels.cjs",
    "tests/validation_panel.cjs",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--full", action="store_true", help="also run slow pytest tests and the Chrome acceptance")
    parser.add_argument("--workers", default="auto", help="pytest-xdist worker count (default: auto)")
    args = parser.parse_args()

    python = sys.executable
    # Some tests require basetemp inside the repository; give each run its own directory.
    basetemp = REPO_ROOT / f".pytest-editor-{os.getpid()}"
    log_dir = REPO_ROOT / f".pytest-editor-{os.getpid()}-logs"  # pytest empties basetemp itself
    env = {**os.environ, "EU5_PYTHON": python}
    commands = {
        # worksteal rebalances the few 15-20 s tests that the default batching piles onto one worker.
        "pytest": [python, "-m", "pytest", "-q", "-n", args.workers, "--dist", "worksteal", "--basetemp", str(basetemp),
                   "-p", "no:cacheprovider", *(() if args.full else ("-m", "not slow")), *PYTEST_FILES],
        "node": ["node", "--test", *NODE_FILES],
        "web-check": [python, "-m", "towards_victory_editor_web", "--check"],
    }
    if args.full:
        commands["chrome"] = ["node", "tests/resource_state_browser.cjs"]

    started = time.perf_counter()
    log_dir.mkdir()
    # Files, not pipes: an undrained pipe would block a suite while another is awaited.
    logs = {name: (log_dir / f"{name}.log").open("w+", encoding="utf-8", errors="replace") for name in commands}
    processes = {
        name: subprocess.Popen(command, cwd=REPO_ROOT, env=env, stdout=logs[name], stderr=subprocess.STDOUT)
        for name, command in commands.items()
    }
    failed = []
    try:
        for name, process in processes.items():
            process.wait()
            elapsed = time.perf_counter() - started
            logs[name].seek(0)
            output = logs[name].read()
            status = "ok" if process.returncode == 0 else f"FAILED ({process.returncode})"
            tail = output.strip().splitlines()[-1:] if process.returncode == 0 else output.strip().splitlines()[-40:]
            print(f"=== {name}: {status}, finished at {elapsed:.1f}s")
            print("\n".join(tail))
            if process.returncode:
                failed.append(name)
    finally:
        for process in processes.values():
            if process.poll() is None:
                process.kill()
        for log in logs.values():
            log.close()
        shutil.rmtree(basetemp, ignore_errors=True)
        shutil.rmtree(log_dir, ignore_errors=True)
    print(f"=== total {time.perf_counter() - started:.1f}s; {'failed: ' + ', '.join(failed) if failed else 'all passed'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
