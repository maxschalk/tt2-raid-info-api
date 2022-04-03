from fastapi import APIRouter

from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from ...routers import admin, raw_seeds, raid_info

router = APIRouter(
    prefix="/api/v0",
    tags=[],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)

router.include_router(admin.router)

router.include_router(raw_seeds.router)

router.include_router(raid_info.router)


@router.get("/")
async def most_recent_seed():
    #  TODO Link docs
    return {"message": "Welcome to the TT2 Raid Seed API v0"}
