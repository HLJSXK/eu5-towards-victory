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
    from .services.media import bootstrap_payload, registry
    from .services.cropper import cropper

    tools = [
        ("cost_reward", cost_reward_check),
        ("victory_tree", victory_tree_check),
        ("wonder_localization", wonder_localization_check),
    ]
    for name, check_fn in tools:
        print(f"=== {name} ===")
        for line in safe_check(name, check_fn):
            print(line)
    print("=== media ===")
    payload = bootstrap_payload()
    print(f"[PASS] registered tools: {len(registry.payload())} ({len(payload['tools'])} runnable media tools)")
    print(f"[PASS] cropper images discovered: {len(cropper.tasks)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the unified Towards Victory web workspace (editors, media generators, and wonder cropper)."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="run editor checks and unified media discovery checks, then exit",
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
            "C:\\Users\\Hades\\anaconda3\\envs\\eu5\\python.exe -m pip install -r towards_victory_editor_web/requirements.txt"
        ) from exc

    url = f"http://{args.host}:{args.port}/"
    if not args.no_browser and args.host in {"127.0.0.1", "localhost"}:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    print(f"Towards Victory Editor Web running at {url}")
    uvicorn.run("towards_victory_editor_web.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
