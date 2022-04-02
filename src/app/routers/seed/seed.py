from typing import Optional

from fastapi import APIRouter

from src.utils import selectors
from src.utils.fetch_seed_data import get_seed_data_by_recency

router = APIRouter(
    prefix="/seed",
    # tags=["selected_seeds"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{tier}/{level}")
async def sorted_seeds(tier: int, level: int, offset_weeks: Optional[int] = 0):
    seed_data = get_seed_data_by_recency(offset=offset_weeks)

    selectors_and_validators = (
        (selectors.raid_tier, lambda x: x == tier),
        (selectors.raid_level, lambda x: x == level),
    )

    return selectors.select_first_by(
        data=seed_data,
        selectors_and_validators=selectors_and_validators,
    )
