from typing import Tuple, List

from fastapi import APIRouter, HTTPException, status

from src.PATHS import RAW_SEEDS_DIR, ENHANCED_SEEDS_DIR
from src.models.SeedType import SeedType
from src.models.SortOrder import SortOrder
from src.models.raid_data import RaidSeedData
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.seed_data_fs_interface import (
    fs_get_sorted_seed_data,
    fs_get_seed_data_by_recency
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
        sort_order: SortOrder = SortOrder.ASCENDING
) -> Tuple[List[RaidSeedData]]:
    dir_path = get_seeds_dir_path(seed_type=seed_type)

    return fs_get_sorted_seed_data(dir_path=dir_path, sort_order=sort_order)


@router.get("/most_recent/{seed_type}")
async def seed_by_recency(
        seed_type: SeedType,
        offset_weeks: int = 0
) -> List[RaidSeedData]:
    dir_path = get_seeds_dir_path(seed_type=seed_type)

    payload = fs_get_seed_data_by_recency(dir_path=dir_path, offset_weeks=offset_weeks)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offset too large"
        )

    return payload
