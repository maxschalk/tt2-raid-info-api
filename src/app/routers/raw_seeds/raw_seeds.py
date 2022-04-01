from fastapi import APIRouter

router = APIRouter(
    prefix="/raw_seeds",
    tags=["raw_seeds"],
    responses={404: {"description": "Not found"}},
)


@router.get("/seed")
async def most_recent_seed():
    return {"message": "Hello World"}


@router.get("/seed/{offset}")
async def most_recent_seed(offset: int):
    return {"message": "Hello World"}
