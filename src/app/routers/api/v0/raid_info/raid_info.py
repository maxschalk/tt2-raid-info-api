from fastapi import APIRouter, HTTPException, status
from src.domain.seed_data_repository import SeedDataRepository
from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.utils import selectors


def _factory_raid_info_by_tier_level(*, repo: SeedDataRepository):

    async def raid_info_by_tier_level(seed_type: SeedType,
                                      tier: int,
                                      level: int,
                                      offset_weeks: int = 0) -> RaidSeedData:

        seed_data = repo.get_seed_by_week_offset(offset_weeks=offset_weeks,
                                                 seed_type=seed_type)

        if seed_data is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No raid seed found for {offset_weeks=}")

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

    return raid_info_by_tier_level


def create_router(seed_data_repo: SeedDataRepository):

    router = APIRouter(
        prefix="/raid_info",
        tags=["Raid Info"],
    )

    router.add_api_route(
        path="/{seed_type}/{tier}/{level}",
        methods=["get"],
        endpoint=_factory_raid_info_by_tier_level(repo=seed_data_repo),
        response_model=RaidSeedData,
        summary="Individual raid level info",
        description="Select the data for a single raid level by tier and level"
    )

    return router
