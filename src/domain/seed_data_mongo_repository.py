from typing import List, Optional, Tuple

from src.domain.seed_data_repository import SeedDataRepository
from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder


class SeedDataMongoRepository(SeedDataRepository):

    def list_seed_identifiers(
            self: SeedDataRepository,
            *,
            seed_type: SeedType = SeedType.RAW,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:

        raise NotImplementedError

    def get_seed_identifier_by_week_offset(
            self: SeedDataRepository,
            *,
            offset_weeks: int = 0) -> Optional[str]:

        raise NotImplementedError

    def get_seed_by_identifier(
            self: SeedDataRepository,
            *,
            identifier: str,
            seed_type: SeedType = SeedType.RAW
    ) -> Optional[List[RaidSeedData]]:

        raise NotImplementedError

    def get_seed_by_week_offset(
            self: SeedDataRepository,
            *,
            offset_weeks: int = 0,
            seed_type: SeedType = SeedType.RAW
    ) -> Optional[List[RaidSeedData]]:
        raise NotImplementedError

    def list_seeds(
        self: SeedDataRepository,
        *,
        seed_type: SeedType = SeedType.RAW,
        sort_order: SortOrder = SortOrder.ASCENDING
    ) -> Tuple[List[RaidSeedData]]:

        raise NotImplementedError

    def save_seed(self: SeedDataRepository,
                  *,
                  identifier: str,
                  data: List[RaidSeedData],
                  seed_type: SeedType = SeedType.RAW) -> bool:

        raise NotImplementedError

    def delete_seed(self: SeedDataRepository,
                    *,
                    identifier: str,
                    seed_type: SeedType = SeedType.RAW) -> None:

        raise NotImplementedError
