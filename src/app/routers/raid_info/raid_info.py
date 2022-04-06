from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src.PATHS import RAW_SEEDS_DIR, ENHANCED_SEEDS_DIR
from src.models.raid_data import RaidRawSeedData
from src.utils import selectors
from src.utils.responses import RESPONSE_STANDARD_NOT_FOUND
from src.utils.seed_data_fs_interface import get_seed_data_by_recency

router = APIRouter(
    prefix="/raid_info",
    tags=["raid info"],
    responses=RESPONSE_STANDARD_NOT_FOUND,
)


def raid_info_by_tier_level_base(dir_path: str,
                                 tier: int,
                                 level: int,
                                 offset_weeks: Optional[int] = 0
                                 ) -> RaidRawSeedData:
    seed_data = get_seed_data_by_recency(dir_path=dir_path, offset_weeks=offset_weeks)

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
            detail=f"No raid raid_info found for raid level {tier}-{level}"
        )

    return payload


@router.get("/{tier}/{level}")
async def raid_info_by_tier_level(tier: int, level: int, offset_weeks: Optional[int] = 0) -> RaidRawSeedData:
    return raid_info_by_tier_level_base(dir_path=RAW_SEEDS_DIR, tier=tier, level=level, offset_weeks=offset_weeks)


@router.get("/enhanced/{tier}/{level}")
async def raid_info_by_tier_level_enhanced(tier: int, level: int, offset_weeks: Optional[int] = 0) -> RaidRawSeedData:
    return raid_info_by_tier_level_base(dir_path=ENHANCED_SEEDS_DIR, tier=tier, level=level, offset_weeks=offset_weeks)
