from typing import List, Tuple

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from src.domain.seed_data_repository import SeedDataRepository
from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder


def _factory_get_all_seeds(*, repo: SeedDataRepository):

    async def get_all_seeds_sorted(
        seed_type: SeedType,
        sort_order: SortOrder = SortOrder.ASCENDING
    ) -> Tuple[List[RaidSeedData]]:

        return repo.list_seeds(seed_type=seed_type, sort_order=sort_order)

    return get_all_seeds_sorted


def _factory_get_seed_by_recency(*, repo: SeedDataRepository):

    async def get_seed_by_recency(
            seed_type: SeedType,
            offset_weeks: int = 0,
            *,
            download: bool = False) -> List[RaidSeedData]:

        if download:
            identifier = repo.get_seed_identifier_by_week_offset(
                offset_weeks=offset_weeks)

            return RedirectResponse(
                f"/api/v0/admin/seed/{seed_type.value}/{identifier}")

        data = repo.get_seed_by_week_offset(offset_weeks=offset_weeks)

        if data is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"No seed found for {offset_weeks=}")

        return data

    return get_seed_by_recency


def create_router(seed_data_repo: SeedDataRepository):

    router = APIRouter(
        prefix="/seeds",
        tags=["Raid Seeds"],
    )

    router.add_api_route(path="/{seed_type}",
                         methods=["get"],
                         endpoint=_factory_get_all_seeds(repo=seed_data_repo))

    router.add_api_route(
        path="/{seed_type}/recent",
        methods=["get"],
        endpoint=_factory_get_seed_by_recency(repo=seed_data_repo))

    return router
