from __future__ import annotations

from abc import ABC, abstractmethod
from ast import Tuple
from typing import List, Optional

from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder


class SeedDataRepository(ABC):

    @abstractmethod
    def list_seed_identifiers(
            self: SeedDataRepository,
            *,
            seed_type: SeedType = SeedType.RAW,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:
        pass

    @abstractmethod
    def get_seed_identifier_by_week_offset(
            self: SeedDataRepository,
            *,
            offset_weeks: int = 0) -> Optional[str]:
        pass

    @abstractmethod
    def get_seed_by_identifier(
            self: SeedDataRepository,
            *,
            identifier: str,
            seed_type: SeedType = SeedType.RAW
    ) -> Optional[List[RaidSeedData]]:
        pass

    @abstractmethod
    def get_seed_by_week_offset(
            self: SeedDataRepository,
            *,
            offset_weeks: int = 0,
            seed_type: SeedType = SeedType.RAW
    ) -> Optional[List[RaidSeedData]]:
        pass

    @abstractmethod
    def list_seeds(
        self: SeedDataRepository,
        *,
        seed_type: SeedType = SeedType.RAW,
        sort_order: SortOrder = SortOrder.ASCENDING
    ) -> List[List[RaidSeedData]]:
        pass

    @abstractmethod
    def save_seed(self: SeedDataRepository,
                  *,
                  identifier: str,
                  data: List[RaidSeedData],
                  seed_type: SeedType = SeedType.RAW) -> bool:
        pass

    @abstractmethod
    def delete_seed(self: SeedDataRepository,
                    *,
                    identifier: str,
                    seed_type: SeedType = SeedType.RAW) -> None:
        pass
