from fastapi import APIRouter
from src.domain.seed_data_repository import SeedDataRepository
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND

from . import admin, raid_info, seeds


def create_router(seed_data_repo: SeedDataRepository):
    router = APIRouter(
        prefix="/v0",
        tags=[],
        responses=RESPONSE_STANDARD_NOT_FOUND,
    )

    router.include_router(admin.create_router(seed_data_repo=seed_data_repo))

    router.include_router(seeds.create_router(seed_data_repo=seed_data_repo))

    router.include_router(
        raid_info.create_router(seed_data_repo=seed_data_repo))

    @router.get("/", include_in_schema=False)
    async def welcome():
        return {
            "message":
            "Welcome to the TT2 Raid Seed API v0! You can find the docs at /docs."
        }

    return router
