from typing import Optional, Tuple, List

from fastapi import APIRouter, HTTPException, status

from src.PATHS import RAW_SEEDS_DIR, ENHANCED_SEEDS_DIR
from src.models.raid_data import RaidRawSeedData
from src.utils.SeedType import SeedType
from src.utils.SortOrder import SortOrder
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.seed_data_fs_interface import (
    get_sorted_seed_data,
    get_seed_data_by_recency
)

router = APIRouter(
    prefix="/seeds",
    tags=["raid seeds"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


def get_seeds_dir_path(seed_type: SeedType):
    return RAW_SEEDS_DIR if seed_type == SeedType.RAW else ENHANCED_SEEDS_DIR


@router.get("/all/{seed_type}")
async def sorted_seeds(
        seed_type: SeedType,
        sort_order: Optional[SortOrder] = SortOrder.DESCENDING
) -> Tuple[List[RaidRawSeedData]]:
    dir_path = get_seeds_dir_path(seed_type=seed_type)

    return get_sorted_seed_data(dir_path=dir_path, sort_order=sort_order)


@router.get("/most_recent/{seed_type}")
async def seed_by_recency(
        seed_type: SeedType,
        offset_weeks: Optional[int] = 0
) -> List[RaidRawSeedData]:
    dir_path = get_seeds_dir_path(seed_type=seed_type)

    payload = get_seed_data_by_recency(dir_path=dir_path, offset_weeks=offset_weeks)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offset too large"
        )

    return payload
