from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .services.cost_reward import CostRewardEditorService
from .services.generation import GenerationError
from .services.platform import RollbackError
from .services.victory_tree import GENERATED_PREVIEWS_DIR, TREE_PREVIEW_URL_PREFIX, VictoryTreePlannerService
from .services.wonder_localization import (
    GENERATED_WONDER_IMAGES_DIR,
    WONDER_IMAGE_URL_PREFIX,
    WonderLocalizationService,
)
from .services.cropper import cropper
from .services.media import bootstrap_payload as media_bootstrap
from .services.media import registry
from .services.media import jobs
from .services.platform import ConflictError

PACKAGE_ROOT = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_ROOT / "static"


class SaveCostRewardRequest(BaseModel):
    edits: dict[str, dict[str, dict[str, Any]]] = Field(default_factory=dict)
    base: dict[str, str] = Field(default_factory=dict)


class SaveVictoryTreeRequest(BaseModel):
    edits: dict[str, dict[str, dict[str, Any]]] = Field(default_factory=dict)
    base: dict[str, str] = Field(default_factory=dict)


class WonderDraftRequest(BaseModel):
    wonder_id: int
    values: dict[str, dict[str, str]] = Field(default_factory=dict)
    mechanics: dict[str, Any] = Field(default_factory=dict)


class WonderResourceRequest(BaseModel):
    wonders: list[WonderDraftRequest] = Field(default_factory=list)
    current_wonder_id: int | None = None
    regenerate: bool = True
    base: dict[str, str] = Field(default_factory=dict)


class SaveRitualPromptRequest(BaseModel):
    prompt: str = ""


class JobRequest(BaseModel):
    tool: str
    options: dict[str, Any] = Field(default_factory=dict)


class CropResourceRequest(BaseModel):
    edits: dict[str, dict[str, Any] | None] = Field(default_factory=dict)
    base: dict[str, str] = Field(default_factory=dict)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Towards Victory Editor Web",
        docs_url=None,
        redoc_url=None,
    )

    # Shared exception-handling boundary, replacing the identical
    # try/except KeyError->404 / ValueError->400 / RuntimeError->500 / Exception->500
    # block that used to be repeated in every editor route.
    def error_response(request, exc: Exception, status_code: int) -> JSONResponse:
        content = {"detail": str(exc)}
        original = exc.original if isinstance(exc, RollbackError) else exc
        if isinstance(original, GenerationError):
            content["generation"] = original.report
        if (
            request.url.path == "/api/resources/editor.wonder"
            or request.url.path.startswith("/api/resources/editor.wonder/")
        ) and wonder_service is not None:
            content["log_text"] = wonder_service.log_text
        return JSONResponse(status_code=status_code, content=content)

    @app.exception_handler(KeyError)
    async def _handle_key_error(request, exc: KeyError):
        return error_response(request, exc, 404)

    @app.exception_handler(ValueError)
    async def _handle_value_error(request, exc: ValueError):
        return error_response(request, exc, 400)

    @app.exception_handler(RuntimeError)
    async def _handle_runtime_error(request, exc: RuntimeError):
        return error_response(request, exc, 500)

    @app.exception_handler(ConflictError)
    async def _handle_conflict_error(request, exc: ConflictError):
        return error_response(request, exc, 409)

    @app.exception_handler(Exception)
    async def _handle_generic_error(request, exc: Exception):
        return error_response(request, exc, 500)

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

    @app.get("/api/resources/editor.cost_reward")
    def cost_reward_resource() -> dict:
        return cost_reward_service.load_resource()

    @app.post("/api/resources/editor.cost_reward/validate")
    def cost_reward_validate(request: SaveCostRewardRequest) -> dict:
        return cost_reward_service.validate_edits(request.edits)

    @app.post("/api/resources/editor.cost_reward/preview")
    def cost_reward_preview(request: SaveCostRewardRequest) -> dict:
        report = cost_reward_service.preview_edits(request.edits, request.base)
        return {"resource": cost_reward_service.resource_descriptor().payload(), **report}

    @app.post("/api/resources/editor.cost_reward/commit")
    def cost_reward_commit(request: SaveCostRewardRequest) -> dict:
        return cost_reward_service.save_tokens(request.edits, request.base)

    # --- Victory tree planner --------------------------------------------------
    victory_tree_service = VictoryTreePlannerService()

    @app.get("/api/resources/editor.victory_tree")
    def victory_tree_resource() -> dict:
        return victory_tree_service.load_resource()

    @app.post("/api/resources/editor.victory_tree/validate")
    def victory_tree_validate(request: SaveVictoryTreeRequest) -> dict:
        return victory_tree_service.validate_edits(request.edits)

    @app.post("/api/resources/editor.victory_tree/preview")
    def victory_tree_preview(request: SaveVictoryTreeRequest) -> dict:
        report = victory_tree_service.preview_edits(request.edits, request.base)
        return {"resource": victory_tree_service.resource_descriptor().payload(), **report}

    @app.post("/api/resources/editor.victory_tree/commit")
    def victory_tree_commit(request: SaveVictoryTreeRequest) -> dict:
        return victory_tree_service.save_positions(request.edits, request.base)

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

    @app.get("/api/wonder-localization/catalog")
    def wonder_catalog() -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.option_catalog_payload()

    # --- Unified Wonder resource --------------------------------------------
    @app.get("/api/resources/editor.wonder")
    def wonder_resource() -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.load_resource()

    @app.post("/api/resources/editor.wonder/validate")
    def wonder_resource_validate(request: WonderResourceRequest) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        drafts = {
            draft.wonder_id: {"values": draft.values, "mechanics": draft.mechanics}
            for draft in request.wonders
        }
        return wonder_service.validate_resource_edits(drafts)

    @app.post("/api/resources/editor.wonder/preview")
    def wonder_resource_preview(request: WonderResourceRequest) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        drafts = {
            draft.wonder_id: {"values": draft.values, "mechanics": draft.mechanics}
            for draft in request.wonders
        }
        report = wonder_service.preview_resource_edits(drafts, request.base, regenerate=request.regenerate)
        return {"resource": wonder_service.resource_descriptor().payload(), **report}

    @app.post("/api/resources/editor.wonder/commit")
    def wonder_resource_commit(request: WonderResourceRequest) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        drafts = {
            draft.wonder_id: {"values": draft.values, "mechanics": draft.mechanics}
            for draft in request.wonders
        }
        return wonder_service.commit_resource(
            drafts,
            request.base,
            current_wonder_id=request.current_wonder_id,
            regenerate=request.regenerate,
        )

    @app.get("/api/wonder-localization/ritual-designs")
    def ritual_design_catalog() -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.ritual_design_catalog_payload()

    @app.get("/api/wonder-localization/ritual-designs/{wonder_id}")
    def ritual_design_get(wonder_id: int) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        return wonder_service.ritual_design_payload(wonder_id)

    @app.get("/api/wonder-localization/wonders/{wonder_id}")
    def wonder_get(wonder_id: int) -> dict:
        if wonder_service is None:
            return JSONResponse(status_code=503, content={"detail": wonder_load_error})
        payload = wonder_service.get_wonder_payload(wonder_id)
        if payload is None:
            return JSONResponse(status_code=404, content={"detail": f"Unknown wonder id: {wonder_id}"})
        return payload

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

    # --- Unified media workspace ---------------------------------------------
    @app.get("/api/tools")
    def tools_bootstrap() -> dict[str, Any]:
        return {
            "tools": registry.payload(),
            **{key: value for key, value in media_bootstrap().items() if key != "tools"},
        }

    @app.get("/api/media/bootstrap")
    def media_tools_bootstrap() -> dict[str, Any]:
        return media_bootstrap()

    @app.post("/api/jobs")
    def create_job(request: JobRequest) -> dict[str, Any]:
        return jobs.submit(request.tool, request.options).payload()

    @app.get("/api/jobs/{job_id}")
    def get_job(job_id: str) -> dict[str, Any]:
        return jobs.get(job_id).payload()

    @app.post("/api/jobs/{job_id}/cancel")
    def cancel_job(job_id: str) -> dict[str, Any]:
        return jobs.cancel(job_id).payload()

    @app.get("/api/resources/editor.wonder_crop")
    def cropper_resource() -> dict[str, Any]:
        return cropper.load_resource()

    @app.post("/api/resources/editor.wonder_crop/validate")
    def cropper_validate(request: CropResourceRequest) -> dict[str, Any]:
        return cropper.validate_edits(request.edits)

    @app.post("/api/resources/editor.wonder_crop/preview")
    def cropper_preview(request: CropResourceRequest) -> dict[str, Any]:
        return cropper.preview_edits(request.edits, request.base)

    @app.post("/api/resources/editor.wonder_crop/commit")
    def cropper_commit(request: CropResourceRequest) -> dict[str, Any]:
        return cropper.commit_edits(request.edits, request.base)

    @app.get("/api/cropper/image/{index}")
    def cropper_image(index: int) -> FileResponse:
        task = cropper._task(index)
        return FileResponse(task.png_path)

    return app


app = create_app()
