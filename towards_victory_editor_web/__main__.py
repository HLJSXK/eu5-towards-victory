from __future__ import annotations

import argparse
import threading
import webbrowser
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from .services.common import safe_check


def _run_combined_check() -> None:
    from .services.cost_reward import build_check_report as cost_reward_check
    from .services.victory_tree import build_check_report as victory_tree_check
    from .services.wonder_localization import build_check_report as wonder_localization_check

    tools = [
        ("cost_reward", cost_reward_check),
        ("victory_tree", victory_tree_check),
        ("wonder_localization", wonder_localization_check),
    ]
    for name, check_fn in tools:
        print(f"=== {name} ===")
        for line in safe_check(name, check_fn):
            print(line)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the merged Towards Victory editor web app (cost/reward, victory tree, wonder localization)."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="run all three tools' data validation checks, then exit without starting the web app",
    )
    parser.add_argument("--host", default="127.0.0.1", help="host interface for the web server")
    parser.add_argument("--port", type=int, default=8760, help="port for the web server")
    parser.add_argument("--no-browser", action="store_true", help="start the server without opening a browser tab")
    parser.add_argument("--reload", action="store_true", help="enable uvicorn auto-reload")
    args = parser.parse_args()

    if args.check:
        _run_combined_check()
        return

    try:
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: uvicorn/fastapi.\n"
            "Install them in the eu5 environment first, for example:\n"
            "conda run --no-capture-output -n eu5 python -m pip install -r towards_victory_editor_web/requirements.txt"
        ) from exc

    url = f"http://{args.host}:{args.port}/"
    if not args.no_browser and args.host in {"127.0.0.1", "localhost"}:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    print(f"Towards Victory Editor Web running at {url}")
    uvicorn.run("towards_victory_editor_web.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
