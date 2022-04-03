import os
from typing import Optional, Tuple, List

from dotenv import load_dotenv
from fastapi import APIRouter, Header, Response, HTTPException

from src.models.raid_data import RaidSeedData
from src.utils.seed_data_fs_interface import (
    SortOrder,
    get_sorted_seed_data,
    get_seed_data_by_recency,
    _dump_seed_data
)

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')

router = APIRouter(
    prefix="/raw_seeds",
    # tags=["raw seeds"],
    responses={404: {"description": "Not found"}},
)


@router.get("/all_seeds")
async def sorted_seeds(sort_order: Optional[SortOrder] = SortOrder.DESCENDING) -> Tuple[RaidSeedData]:
    return get_sorted_seed_data(sort_order=sort_order)


@router.get("/seed")
async def seed_by_recency(offset_weeks: Optional[int] = 0) -> RaidSeedData:
    payload = get_seed_data_by_recency(offset=offset_weeks)

    if payload is None:
        raise HTTPException(status_code=400, detail="Offset too large")

    return payload


@router.post("/{filename}")
async def sorted_seeds(filename: str, data: List[RaidSeedData], secret: Optional[str] = Header(None)):
    if not secret or secret != ENV_AUTH_SECRET:
        raise HTTPException(
            status_code=401,
            detail=f"You are not authorized to make this request."
        )

    try:
        result = _dump_seed_data(filename=filename, data=data)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong when interfacing with the filesystem."
        )

    if result is False:
        raise HTTPException(
            status_code=400,
            detail=f"File {filename} already exists on the server."
        )

    return Response(content="Success")
