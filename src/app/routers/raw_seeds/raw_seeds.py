from typing import Optional, Tuple

from fastapi import APIRouter, HTTPException, status

from src.PATHS import RAW_SEEDS_DIR
from src.models.raid_data import RaidRawSeedData
from src.utils.SortOrder import SortOrder
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.seed_data_fs_interface import (
    get_sorted_seed_data,
    get_seed_data_by_recency
)

router = APIRouter(
    prefix="/raw_seeds",
    tags=["raid seeds"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


@router.get("/all_seeds")
async def sorted_seeds(sort_order: Optional[SortOrder] = SortOrder.DESCENDING) -> Tuple[RaidRawSeedData]:
    return get_sorted_seed_data(dir_path=RAW_SEEDS_DIR, sort_order=sort_order)


@router.get("/most_recent")
async def seed_by_recency(offset_weeks: Optional[int] = 0) -> RaidRawSeedData:
    payload = get_seed_data_by_recency(dir_path=RAW_SEEDS_DIR, offset=offset_weeks)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offset too large")

    return payload
