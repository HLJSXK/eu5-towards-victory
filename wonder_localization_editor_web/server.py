from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .service import GENERATED_WONDER_IMAGES_DIR, WONDER_IMAGE_URL_PREFIX, WonderLocalizationService

PACKAGE_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_ROOT / "static"
service = WonderLocalizationService()


class SaveWonderRequest(BaseModel):
    values: dict[str, dict[str, str]] = Field(default_factory=dict)
    mechanics: dict[str, Any] = Field(default_factory=dict)
    regenerate: bool = True


class WonderDraftRequest(BaseModel):
    wonder_id: int
    values: dict[str, dict[str, str]] = Field(default_factory=dict)
    mechanics: dict[str, Any] = Field(default_factory=dict)


class SaveWondersRequest(BaseModel):
    wonders: list[WonderDraftRequest] = Field(default_factory=list)
    current_wonder_id: int | None = None
    regenerate: bool = True


class SaveRitualPromptRequest(BaseModel):
    prompt: str = ""


def create_app() -> FastAPI:
    app = FastAPI(
        title="Wonder Localization Editor Web",
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
            return service.save_wonder(
                wonder_id,
                request.values,
                mechanics_values=request.mechanics,
                regenerate=request.regenerate,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/api/wonders/save")
    def save_wonders(request: SaveWondersRequest) -> dict:
        try:
            return service.save_wonders(
                {
                    draft.wonder_id: {
                        "values": draft.values,
                        "mechanics": draft.mechanics,
                    }
                    for draft in request.wonders
                },
                current_wonder_id=request.current_wonder_id,
                regenerate=request.regenerate,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    @app.post("/api/ritual-prompts/{wonder_id}")
    def save_ritual_prompt(wonder_id: int, request: SaveRitualPromptRequest) -> dict:
        try:
            return service.save_unique_ritual_prompt(wonder_id, request.prompt)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount(
        WONDER_IMAGE_URL_PREFIX,
        StaticFiles(directory=GENERATED_WONDER_IMAGES_DIR, check_dir=False),
        name="wonder-images",
    )
    return app


app = create_app()
