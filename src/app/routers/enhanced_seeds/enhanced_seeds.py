from typing import Optional, Tuple, List

from fastapi import APIRouter, HTTPException, status

from src.PATHS import ENHANCED_SEEDS_DIR
from src.models.raid_data import RaidRawSeedData
from src.utils.SortOrder import SortOrder
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.seed_data_fs_interface import (
    get_sorted_seed_data,
    get_seed_data_by_recency
)

router = APIRouter(
    prefix="/enhanced_seeds",
    tags=["raid seeds"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


@router.get("/all")
async def sorted_seeds(sort_order: Optional[SortOrder] = SortOrder.DESCENDING) -> Tuple[List[RaidRawSeedData]]:
    return get_sorted_seed_data(dir_path=ENHANCED_SEEDS_DIR, sort_order=sort_order)


@router.get("/most_recent")
async def seed_by_recency(offset_weeks: Optional[int] = 0) -> List[RaidRawSeedData]:
    payload = get_seed_data_by_recency(dir_path=ENHANCED_SEEDS_DIR, offset_weeks=offset_weeks)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offset too large")

    return payload
