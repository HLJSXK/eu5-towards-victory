from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .services.cost_reward import CostRewardEditorService
from .services.victory_tree import GENERATED_PREVIEWS_DIR, TREE_PREVIEW_URL_PREFIX, VictoryTreePlannerService
from .services.wonder_localization import (
    GENERATED_WONDER_IMAGES_DIR,
    WONDER_IMAGE_URL_PREFIX,
    WonderLocalizationService,
)

PACKAGE_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_ROOT / "static"


class SaveCostRewardRequest(BaseModel):
    edits: dict[str, dict[str, dict[str, Any]]] = Field(default_factory=dict)


class SaveVictoryTreeRequest(BaseModel):
    edits: dict[str, dict[str, dict[str, Any]]] = Field(default_factory=dict)


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
        title="Towards Victory Editor Web",
        docs_url=None,
        redoc_url=None,
    )

    # Shared exception-handling boundary, replacing the identical
    # try/except KeyError->404 / ValueError->400 / RuntimeError->500 / Exception->500
    # block that used to be repeated in every route of all three standalone tools.
    @app.exception_handler(KeyError)
    async def _handle_key_error(request, exc: KeyError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def _handle_value_error(request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(RuntimeError)
    async def _handle_runtime_error(request, exc: RuntimeError):
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def _handle_generic_error(request, exc: Exception):
        return JSONResponse(status_code=500, content={"detail": str(exc)})

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

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # --- Cost / Reward editor -------------------------------------------------
    cost_reward_service = CostRewardEditorService()

    @app.get("/api/cost-reward/bootstrap")
    def cost_reward_bootstrap() -> dict:
        return cost_reward_service.bootstrap_payload()

    @app.post("/api/cost-reward/save")
    def cost_reward_save(request: SaveCostRewardRequest) -> dict:
        return cost_reward_service.save_tokens(request.edits)

    # --- Victory tree planner --------------------------------------------------
    victory_tree_service = VictoryTreePlannerService()

    @app.get("/api/victory-tree/bootstrap")
    def victory_tree_bootstrap() -> dict:
        return victory_tree_service.bootstrap_payload()

    @app.post("/api/victory-tree/save")
    def victory_tree_save(request: SaveVictoryTreeRequest) -> dict:
        return victory_tree_service.save_positions(request.edits)

    app.mount(
        TREE_PREVIEW_URL_PREFIX,
        StaticFiles(directory=GENERATED_PREVIEWS_DIR, check_dir=False),
        name="tree-previews",
    )

    # --- Wonder localization editor --------------------------------------------
    # Isolated construction: this service's __init__ eagerly validates
    # data/wonder_localization.yaml and raises if required zh-CN keys are missing.
    # A data bug here must not take down the cost-reward/victory-tree tabs too.
    wonder_service: WonderLocalizationService | None = None
    wonder_load_error: str | None = None
    try:
        wonder_service = WonderLocalizationService()
    except Exception as exc:  # noqa: BLE001
        wonder_load_error = str(exc)

    @app.get("/api/wonder-localization/bootstrap")
    def wonder_bootstrap() -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.bootstrap_payload()

    @app.get("/api/wonder-localization/wonders/{wonder_id}")
    def wonder_get(wonder_id: int) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        payload = wonder_service.get_wonder_payload(wonder_id)
        if payload is None:
            return JSONResponse(status_code=404, content={"detail": f"Unknown wonder id: {wonder_id}"})
        return payload

    @app.post("/api/wonder-localization/wonders/{wonder_id}/reload")
    def wonder_reload(wonder_id: int) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.reload_wonder_payload(wonder_id)

    @app.post("/api/wonder-localization/wonders/{wonder_id}/save")
    def wonder_save_one(wonder_id: int, request: SaveWonderRequest) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.save_wonder(
            wonder_id,
            request.values,
            mechanics_values=request.mechanics,
            regenerate=request.regenerate,
        )

    @app.post("/api/wonder-localization/wonders/save")
    def wonder_save_many(request: SaveWondersRequest) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.save_wonders(
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

    @app.post("/api/wonder-localization/ritual-prompts/{wonder_id}")
    def wonder_save_ritual_prompt(wonder_id: int, request: SaveRitualPromptRequest) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.save_unique_ritual_prompt(wonder_id, request.prompt)

    app.mount(
        WONDER_IMAGE_URL_PREFIX,
        StaticFiles(directory=GENERATED_WONDER_IMAGES_DIR, check_dir=False),
        name="wonder-images",
    )

    return app


app = create_app()
