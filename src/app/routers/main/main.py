from fastapi import APIRouter

from ...routers import raw_seeds, seed

router = APIRouter(
    prefix="/api/v0",
    tags=[],
    responses={404: {"description": "Not found"}},
)

router.include_router(raw_seeds.router)

router.include_router(seed.router)


@router.get("/")
async def most_recent_seed():
    #  TODO Link docs
    return {"message": "Welcome to the TT2 Raid Seed API v0"}
