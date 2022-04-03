import json
import os.path
from os import listdir
from os.path import isfile, join
from typing import Tuple, Optional, Iterator, List

from fastapi.encoders import jsonable_encoder

from src.PATHS import RAW_SEEDS_DIR
from src.models.raid_data import RaidRawSeedData
from src.utils.SortOrder import SortOrder


def _seed_path_generator(*, dir_path: str) -> Iterator[str]:
    for filename in listdir(dir_path):
        if isfile(join(RAW_SEEDS_DIR, filename)):
            yield filename


def get_all_seed_filenames(*, dir_path: str) -> Tuple[str]:
    return tuple(_seed_path_generator(dir_path=dir_path))


def get_sorted_seed_filenames(*, dir_path: str, sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:
    def sort_key(filepath: str):
        *_, date = filepath.split('_')
        return date

    return tuple(
        sorted(
            _seed_path_generator(dir_path=dir_path),
            key=sort_key,
            reverse=(sort_order == SortOrder.DESCENDING)
        )
    )


def load_seed_data(*, filepath: str) -> RaidRawSeedData:
    if not os.path.isabs(filepath):
        filepath = join(RAW_SEEDS_DIR, filepath)

    with open(filepath, 'r') as file:
        return json.load(file)


def dump_seed_data(*, filename: str, data: List[RaidRawSeedData]) -> bool:
    filepath = join(RAW_SEEDS_DIR, filename)

    if os.path.exists(filepath):
        return False

    with open(filepath, 'w') as file:
        json.dump(jsonable_encoder(data), file)

    return True


def get_all_seed_data(*, dir_path: str, ) -> tuple[RaidRawSeedData]:
    return tuple(
        load_seed_data(filepath=filepath)
        for filepath
        in get_all_seed_filenames(dir_path=dir_path)
    )


def get_sorted_seed_data(*, dir_path: str, sort_order: SortOrder = SortOrder.ASCENDING) -> tuple[RaidRawSeedData]:
    return tuple(
        load_seed_data(filepath=filepath)
        for filepath
        in get_sorted_seed_filenames(dir_path=dir_path, sort_order=sort_order)
    )


def get_seed_data_by_recency(*, dir_path: str, offset: int = 0) -> Optional[RaidRawSeedData]:
    offset = abs(offset)

    most_recent_filepaths = get_sorted_seed_filenames(dir_path=dir_path, sort_order=SortOrder.DESCENDING)

    if offset >= len(most_recent_filepaths):
        return None

    selected_filepath = most_recent_filepaths[offset]

    return load_seed_data(filepath=selected_filepath)


def get_most_recent_seed_data(*, dir_path: str) -> RaidRawSeedData:
    return get_seed_data_by_recency(dir_path=dir_path, offset=0)
