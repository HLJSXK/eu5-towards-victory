from __future__ import annotations

import argparse
import threading
import webbrowser
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from .service import build_check_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the web-based Engineering Department wonder localization editor.")
    parser.add_argument("--check", action="store_true", help="load data and localization files, then exit without starting the web app")
    parser.add_argument("--host", default="127.0.0.1", help="host interface for the web server")
    parser.add_argument("--port", type=int, default=8765, help="port for the web server")
    parser.add_argument("--no-browser", action="store_true", help="start the server without opening a browser tab")
    parser.add_argument("--reload", action="store_true", help="enable uvicorn auto-reload")
    args = parser.parse_args()

    if args.check:
        for line in build_check_report():
            print(line)
        return

    try:
        import fastapi  # noqa: F401
        import uvicorn
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: uvicorn/fastapi.\n"
            "Install them in the eu5 environment first, for example:\n"
            "conda run --no-capture-output -n eu5 python -m pip install -r wonder_localization_editor_web/requirements.txt"
        ) from exc

    url = f"http://{args.host}:{args.port}/"
    if not args.no_browser and args.host in {"127.0.0.1", "localhost"}:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    print(f"Wonder Localization Editor Web running at {url}")
    uvicorn.run("wonder_localization_editor_web.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
