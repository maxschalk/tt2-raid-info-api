import os
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Response, Header

from src.models.raid_data import RaidSeedData
from src.utils import selectors
from src.utils.seed_data_fs_interface import get_seed_data_by_recency, _dump_seed_data

load_dotenv()

ENV_AUTH_SECRET = os.getenv('AUTH_SECRET')

router = APIRouter(
    prefix="/seed",
    # tags=["selected_seeds"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{tier}/{level}")
async def selected_seed(tier: int, level: int, offset_weeks: Optional[int] = 0) -> RaidSeedData:
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
        raise HTTPException(status_code=400, detail=f"No raid seed found for raid level {tier}-{level}")

    return payload


@router.post("/{filename}")
async def sorted_seeds(filename: str, data: List[RaidSeedData], auth_secret: Optional[str] = Header(None)):
    if not auth_secret or auth_secret != ENV_AUTH_SECRET:
        raise HTTPException(
            status_code=401,
            detail=f"You are not authorized to make this request."
        )

    try:
        result = _dump_seed_data(filename=filename, data=data)
    except IndexError:
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong when interfacing with the filesystem."
        )

    if result is False:
        raise HTTPException(
            status_code=400,
            detail=f"File {filename} already exists on the server."
        )

    return Response(content="Success")
