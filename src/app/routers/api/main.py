from fastapi import APIRouter

from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from ...routers.v0 import main as v0

router = APIRouter(
    prefix="/api",
    tags=[],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)

router.include_router(v0.router)


@router.get("/", include_in_schema=False)
async def welcome():
    return {
        "message": "Welcome to the TT2 Raid Seed API! You can find the docs at /docs."
    }
