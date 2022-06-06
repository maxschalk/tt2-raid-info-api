from fastapi import APIRouter

from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from . import seeds, admin, raid_info

router = APIRouter(
    prefix="/v0",
    tags=[],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)

router.include_router(admin.router)

router.include_router(seeds.router)

router.include_router(raid_info.router)


@router.get("/", include_in_schema=False)
async def welcome():
    return {
        "message": "Welcome to the TT2 Raid Seed API v0! You can find the docs at /docs."
    }
