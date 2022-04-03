from typing import Optional

from fastapi import APIRouter, HTTPException

from src.models.raid_data import RaidSeedData
from src.utils import selectors
from src.utils.seed_data_fs_interface import get_seed_data_by_recency

router = APIRouter(
    prefix="/raid_info",
    # tags=["selected_seeds"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{tier}/{level}")
async def raid_info_by_tier_level(tier: int, level: int, offset_weeks: Optional[int] = 0) -> RaidSeedData:
    seed_data = get_seed_data_by_recency(offset=offset_weeks)

    selectors_and_validators = (
        (selectors.raid_tier, lambda x: x == tier),
        (selectors.raid_level, lambda x: x == level),
    )

    payload = selectors.select_first_by(
        data=seed_data,
        selectors_and_validators=selectors_and_validators,
    )

    if payload is None:
        raise HTTPException(status_code=400, detail=f"No raid raid_info found for raid level {tier}-{level}")

    return payload
