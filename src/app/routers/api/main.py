from fastapi import APIRouter
from src.domain.seed_data_repository import SeedDataRepository
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND

from . import v0


def create_router(seed_data_repo: SeedDataRepository):
    router = APIRouter(
        prefix="/api",
        tags=[],
        responses=RESPONSE_STANDARD_NOT_FOUND,
    )

    router.include_router(v0.create_router(seed_data_repo=seed_data_repo))

    @router.get("/", include_in_schema=False)
    async def root():
        return {
            "message":
            "Welcome to the TT2 Raid Seed API! You can find the docs at /docs."
        }

    return router
