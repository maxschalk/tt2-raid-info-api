import json
import os.path
from os import listdir
from os.path import isfile, join
from typing import Iterator, List, Optional, Tuple

from fastapi.encoders import jsonable_encoder
from src.models.raid_data import RaidSeedData
from src.models.SortOrder import SortOrder
from src.PATHS import RAW_SEEDS_DIR


def _seed_path_generator(*, dir_path: str) -> Iterator[str]:
    for filename in listdir(dir_path):
        if isfile(join(dir_path, filename)):
            yield filename


def get_all_seed_filenames(*, dir_path: str) -> Tuple[str]:
    return tuple(_seed_path_generator(dir_path=dir_path))


def get_sorted_seed_filenames(*, dir_path: str, sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:
    return tuple(
        sorted(
            _seed_path_generator(dir_path=dir_path),
            reverse=(sort_order == SortOrder.DESCENDING)
        )
    )


def load_seed_data(*, filepath: str) -> List[RaidSeedData]:
    with open(filepath, 'r') as file:
        return json.load(file)


def dump_seed_data(*, filepath: str, data: List[RaidSeedData]) -> bool:
    if os.path.exists(filepath):
        return False

    with open(filepath, 'w') as file:
        json.dump(jsonable_encoder(data), file)

    return True


def get_all_seed_data(*, dir_path: str) -> tuple[List[RaidSeedData]]:
    return tuple(
        load_seed_data(filepath=os.path.join(dir_path, filepath))
        for filepath
        in get_all_seed_filenames(dir_path=dir_path)
    )


def fs_get_sorted_seed_data(*, dir_path: str, sort_order: SortOrder = SortOrder.ASCENDING) -> tuple[List[RaidSeedData]]:
    return tuple(
        load_seed_data(filepath=os.path.join(dir_path, filepath))
        for filepath
        in get_sorted_seed_filenames(dir_path=dir_path, sort_order=sort_order)
    )


def fs_get_seed_data_by_recency(*, dir_path: str, offset_weeks: int = 0) -> Optional[List[RaidSeedData]]:
    offset_weeks = abs(offset_weeks)

    most_recent_filepaths = get_sorted_seed_filenames(
        dir_path=dir_path, sort_order=SortOrder.DESCENDING
    )

    if offset_weeks >= len(most_recent_filepaths):
        return None

    selected_filepath = os.path.join(
        dir_path, most_recent_filepaths[offset_weeks]
    )

    return load_seed_data(filepath=selected_filepath)


def get_most_recent_seed_data(*, dir_path: str) -> List[RaidSeedData]:
    return fs_get_seed_data_by_recency(dir_path=dir_path, offset_weeks=0)


def delete_raw_seed_file(*, filename: str) -> bool:
    file_path = os.path.join(RAW_SEEDS_DIR, filename)

    if not os.path.exists(file_path):
        return False

    try:
        os.remove(file_path)
    except OSError:
        return False

    return True
