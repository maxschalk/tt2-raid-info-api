import json
import os.path
from enum import Enum
from os import listdir
from os.path import isfile, join
from typing import Tuple, Optional, Iterator, List

from fastapi.encoders import jsonable_encoder

from src.PATHS import RAW_SEEDS_DIR
from src.models.raid_data import RaidSeedData


class SortOrder(Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


def _seed_path_generator() -> Iterator[str]:
    for filepath in listdir(RAW_SEEDS_DIR):
        if isfile(join(RAW_SEEDS_DIR, filepath)):
            yield filepath


def _get_all_seed_paths() -> Tuple[str]:
    return tuple(_seed_path_generator())


def _get_sorted_seed_paths(*, sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:
    def sort_key(filepath: str):
        *_, date = filepath.split('_')
        return date

    return tuple(
        sorted(
            _seed_path_generator(),
            key=sort_key,
            reverse=(sort_order == SortOrder.DESCENDING)
        )
    )


def _load_seed_data(*, filepath: str) -> RaidSeedData:
    if not os.path.isabs(filepath):
        filepath = join(RAW_SEEDS_DIR, filepath)

    with open(filepath, 'r') as file:
        return json.load(file)


def _dump_seed_data(*, filename: str, data: List[RaidSeedData]) -> bool:
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    filepath = join(RAW_SEEDS_DIR, filename)

    if os.path.exists(filepath):
        return False

    with open(filepath, 'w') as file:
        json.dump(jsonable_encoder(data), file)

    return True


def get_all_seed_data() -> tuple[RaidSeedData]:
    return tuple(
        _load_seed_data(filepath=filepath)
        for filepath
        in _get_all_seed_paths()
    )


def get_sorted_seed_data(*, sort_order: SortOrder = SortOrder.ASCENDING) -> tuple[RaidSeedData]:
    return tuple(
        _load_seed_data(filepath=filepath)
        for filepath
        in _get_sorted_seed_paths(sort_order=sort_order)
    )


def get_seed_data_by_recency(*, offset: int = 0) -> Optional[RaidSeedData]:
    offset = abs(offset)

    most_recent_filepaths = _get_sorted_seed_paths(sort_order=SortOrder.DESCENDING)

    if offset >= len(most_recent_filepaths):
        return None

    selected_filepath = most_recent_filepaths[offset]

    return _load_seed_data(filepath=selected_filepath)


def get_most_recent_seed_data() -> RaidSeedData:
    return get_seed_data_by_recency(offset=0)
