import os
from typing import List, Tuple

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.seed_data_fs_interface import (fs_get_seed_data_by_recency,
                                        fs_get_seed_filename_by_recency,
                                        fs_get_sorted_seed_data)
from src.utils.get_seeds_dir_path import get_seeds_dir_path
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.sort_order import SortOrder

router = APIRouter(
    prefix="/seeds",
    tags=["raid seeds"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


@router.get("/{seed_type}")
async def get_all_seeds_sorted(
        seed_type: SeedType,
        sort_order: SortOrder = SortOrder.ASCENDING
) -> Tuple[List[RaidSeedData]]:
    dir_path = get_seeds_dir_path(seed_type=seed_type)

    return fs_get_sorted_seed_data(dir_path=dir_path, sort_order=sort_order)


@router.get("/{seed_type}/recent")
async def get_seed_by_recency(seed_type: SeedType,
                              offset_weeks: int = 0,
                              *,
                              download: bool = False) -> List[RaidSeedData]:
    dir_path = get_seeds_dir_path(seed_type=seed_type)

    if download:
        filename = fs_get_seed_filename_by_recency(dir_path=dir_path,
                                                   offset_weeks=offset_weeks)

        filename = os.path.basename(filename)

        return RedirectResponse(
            f"/api/v0/admin/seed_file/{seed_type.value}/{filename}")

    payload = fs_get_seed_data_by_recency(dir_path=dir_path,
                                          offset_weeks=offset_weeks)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Offset too large")

    return payload
