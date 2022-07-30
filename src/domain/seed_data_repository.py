from __future__ import annotations

from abc import ABC, abstractmethod
from ast import Tuple
from typing import List, Optional

from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder


class SeedDuplicateError(Exception):
    pass


class SeedNotFoundError(Exception):
    pass


class SeedDataRepository(ABC):

    @abstractmethod
    def list_seed_identifiers(
            self,
            *,
            seed_type: SeedType = SeedType.RAW,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:
        pass

    @abstractmethod
    def get_seed_identifier_by_week_offset(
            self,
            *,
            seed_type: SeedType = SeedType.RAW,
            offset_weeks: int = 0) -> Optional[str]:
        pass

    @abstractmethod
    def get_seed_by_identifier(self,
                               *,
                               identifier: str,
                               seed_type: SeedType = SeedType.RAW
                               ) -> Optional[List[RaidSeedData]]:
        pass

    @abstractmethod
    def get_seed_by_week_offset(
        self,
        *,
        seed_type: SeedType = SeedType.RAW,
        offset_weeks: int = 0,
    ) -> Optional[List[RaidSeedData]]:
        pass

    @abstractmethod
    def list_seeds(
        self,
        *,
        seed_type: SeedType = SeedType.RAW,
        sort_order: SortOrder = SortOrder.ASCENDING
    ) -> List[List[RaidSeedData]]:
        pass

    @abstractmethod
    def save_seed(self, *, identifier: str, seed_type: SeedType,
                  data: List[RaidSeedData]) -> None:
        pass

    @abstractmethod
    def save_seeds(
            self, *, items: Tuple[Tuple[str, SeedType,
                                        List[RaidSeedData]]]) -> None:
        pass

    @abstractmethod
    def delete_seed(self, *, identifier: str, seed_type: SeedType) -> None:
        pass

    @abstractmethod
    def delete_seeds(self, *, items: Tuple[Tuple[str, SeedType]]) -> None:
        pass
