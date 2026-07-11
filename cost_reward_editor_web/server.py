from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .service import CostRewardEditorService

PACKAGE_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_ROOT / "static"
service = CostRewardEditorService()


class SaveTokensRequest(BaseModel):
    edits: dict[str, dict[str, dict[str, Any]]] = Field(default_factory=dict)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cost/Reward & Modifier & Task Pool Unit Editor Web",
        docs_url=None,
        redoc_url=None,
    )

    @app.middleware("http")
    async def no_cache_editor_static(request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
        return response

    @app.get("/")
    def root() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/bootstrap")
    def bootstrap() -> dict:
        return service.bootstrap_payload()

    @app.post("/api/save")
    def save(request: SaveTokensRequest) -> dict:
        try:
            return service.save_tokens(request.edits)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
