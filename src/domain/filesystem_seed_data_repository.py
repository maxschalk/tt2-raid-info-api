import json
from pathlib import Path
from typing import Any, Iterator, Optional, Tuple, Union

from fastapi.encoders import jsonable_encoder
from src.domain.seed_data_repository import SeedDataRepository
from src.model.raid_data import RaidSeed
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder


def _filepath_generator(*, dir_path: Path) -> Iterator[Path]:
    yield from filter(Path.is_file, dir_path.iterdir())


def _load_from_json_file(*, filepath: Path) -> RaidSeed:
    with open(filepath, mode='r', encoding='utf-8') as file:
        return json.load(file)


def _save_to_json_file(*, filepath: Path, data: Any) -> bool:
    with open(filepath, mode='w', encoding='utf-8') as file:
        json.dump(jsonable_encoder(data), file)

    return True


class FSSeedDataRepository(SeedDataRepository):

    def __init__(self, *, base_path: Union[str, Path]) -> None:
        super().__init__()

        self.base_path = Path(base_path)

        self.dir_raw: Path = self.base_path / SeedType.RAW.value
        self.dir_enhanced: Path = self.base_path / SeedType.ENHANCED.value

    def list_seed_identifiers(
            self,
            *,
            seed_type: SeedType = SeedType.RAW,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:

        dir_path = self.base_path / seed_type.value

        path_iterator = _filepath_generator(dir_path=dir_path)

        id_iterator = map(lambda path: path.stem, path_iterator)

        reverse = sort_order == SortOrder.DESCENDING

        return tuple(sorted(id_iterator, reverse=reverse))

    def get_seed_identifier_by_week_offset(
            self,
            *,
            seed_type: SeedType = SeedType.RAW,
            offset_weeks: int = 0) -> Optional[str]:

        ids = self.list_seed_identifiers(seed_type=seed_type,
                                         sort_order=SortOrder.DESCENDING)

        offset_weeks = abs(offset_weeks)

        try:
            return ids[offset_weeks]
        except IndexError:
            return None

    def get_seed_by_identifier(
            self,
            *,
            identifier: str,
            seed_type: SeedType = SeedType.RAW) -> Optional[RaidSeed]:

        filepath = self.base_path / seed_type.value / f"{identifier}.json"

        if not filepath.is_file():
            return None

        return _load_from_json_file(filepath=filepath)

    def get_seed_by_week_offset(
        self,
        *,
        seed_type: SeedType = SeedType.RAW,
        offset_weeks: int = 0,
    ) -> Optional[RaidSeed]:

        identifier = self.get_seed_identifier_by_week_offset(
            offset_weeks=offset_weeks)

        return self.get_seed_by_identifier(identifier=identifier,
                                           seed_type=seed_type)

    def list_seeds(
            self,
            *,
            seed_type: SeedType = SeedType.RAW,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[RaidSeed]:

        identifiers = self.list_seed_identifiers(sort_order=sort_order)

        dir_path = self.base_path / seed_type.value

        def load_by_id(identifier: str):
            path = dir_path / f"{identifier}.json"
            return _load_from_json_file(filepath=path)

        return tuple(map(load_by_id, identifiers))

    def save_seed(self,
                  *,
                  identifier: str,
                  seed_type: SeedType = SeedType.RAW,
                  data: RaidSeed) -> bool:

        filepath = self.base_path / seed_type.value / f"{identifier}.json"

        if filepath.exists():
            return False

        return _save_to_json_file(filepath=filepath, data=data)

    def save_seeds(self, *, items: Tuple[Tuple[str, SeedType,
                                               RaidSeed]]) -> bool:

        def save_item(item: Tuple[str, SeedType, RaidSeed]) -> bool:

            identifier, seed_type, data = item

            return self.save_seed(identifier=identifier,
                                  seed_type=seed_type,
                                  data=data)

        return all(list(map(save_item, items)))

    def delete_seed(self,
                    *,
                    identifier: str,
                    seed_type: SeedType = SeedType.RAW) -> bool:

        filepath = self.base_path / seed_type.value / f"{identifier}.json"

        try:
            filepath.unlink()
            return True
        except FileNotFoundError:
            return False

    def delete_seeds(self, *, items: Tuple[Tuple[str, SeedType]]) -> bool:

        def delete_item(item: Tuple[str, SeedType]) -> bool:

            identifier, seed_type = item

            return self.delete_seed(identifier=identifier, seed_type=seed_type)

        return all(list(map(delete_item, items)))
