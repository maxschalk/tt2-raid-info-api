from typing import Optional, Tuple

from fastapi import APIRouter, HTTPException

from src.models.raid_data import RaidSeedData
from src.utils.seed_data_fs_interface import (
    SortOrder,
    get_sorted_seed_data,
    get_seed_data_by_recency
)

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
