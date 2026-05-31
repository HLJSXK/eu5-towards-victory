from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .service import WonderLocalizationService

PACKAGE_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_ROOT / "static"
service = WonderLocalizationService()


class SaveWonderRequest(BaseModel):
    values: dict[str, dict[str, str]] = Field(default_factory=dict)
    regenerate: bool = True


def create_app() -> FastAPI:
    app = FastAPI(
        title="Wonder Localization Editor Web",
        docs_url=None,
        redoc_url=None,
    )

    @app.get("/")
    def root() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/bootstrap")
    def bootstrap() -> dict:
        return service.bootstrap_payload()

    @app.get("/api/wonders/{wonder_id}")
    def get_wonder(wonder_id: int) -> dict:
        try:
            payload = service.get_wonder_payload(wonder_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        if payload is None:
            raise HTTPException(status_code=404, detail=f"Unknown wonder id: {wonder_id}")
        return payload

    @app.post("/api/wonders/{wonder_id}/reload")
    def reload_wonder(wonder_id: int) -> dict:
        try:
            return service.reload_wonder_payload(wonder_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/api/wonders/{wonder_id}/save")
    def save_wonder(wonder_id: int, request: SaveWonderRequest) -> dict:
        try:
            return service.save_wonder(wonder_id, request.values, regenerate=request.regenerate)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()

