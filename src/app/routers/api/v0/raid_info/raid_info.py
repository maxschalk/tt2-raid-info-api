from fastapi import APIRouter, HTTPException, status
from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.seed_data_fs_interface import fs_get_seed_data_by_recency
from src.utils import selectors
from src.utils.get_seeds_dir_path import get_seeds_dir_path
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND

router = APIRouter(
    prefix="/raid_info",
    tags=["raid info"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


@router.get("/{seed_type}/{tier}/{level}")
async def raid_info_by_tier_level(seed_type: SeedType,
                                  tier: int,
                                  level: int,
                                  offset_weeks: int = 0) -> RaidSeedData:
    dir_path = get_seeds_dir_path(seed_type=seed_type)

    seed_data = fs_get_seed_data_by_recency(dir_path=dir_path,
                                            offset_weeks=offset_weeks)

    if seed_data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Offset too large")

    selectors_and_validators = (
        (selectors.raid_tier, lambda x: x == tier),
        (selectors.raid_level, lambda x: x == level),
    )

    payload = selectors.select_first_by(
        data=seed_data,
        selectors_and_validators=selectors_and_validators,
    )

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No raid info found for raid level {tier}-{level}")

    return payload
