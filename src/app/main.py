from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from src.domain.seed_data_repository import SeedDataRepository
from src.stage import Stage

from .routers import api

DESCRIPTION = """
    Provides access to raid seed data for the mobile game Tap Titans 2.
    You can get raw (unmodified) seeds and enhanced (with useful extra information) seeds."""


def create_app(*, stage: Stage, seed_data_repo: SeedDataRepository):
    app = FastAPI(title=f"TT2 Raid Data API | {stage.value}",
                  version="0.1.0",
                  description=DESCRIPTION,
                  swagger_ui_parameters={
                      "defaultModelsExpandDepth": -1,
                      "tryItOutEnabled": stage == Stage.PRODUCTION
                  })

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse("/docs")

    app.include_router(api.create_router(seed_data_repo=seed_data_repo))

    return app
