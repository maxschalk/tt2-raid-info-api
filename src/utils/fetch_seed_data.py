import json
import os.path

from typing import Tuple, Dict, Iterator
from os import listdir
from os.path import isfile, join
from enum import Enum

from src.PATHS import DATA_DIR

JSON_DATA_TYPES = str | int | float | dict | list | bool | None


class SortOrder(Enum):
    ASCENDING = 0
    DESCENDING = 1


def seed_path_generator() -> Iterator[str]:
    for filepath in listdir(DATA_DIR):
        if isfile(join(DATA_DIR, filepath)):
            yield filepath


def get_all_seed_paths() -> Tuple[str]:
    return tuple(seed_path_generator())


def get_sorted_seed_paths(*, sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:
    def sort_key(filepath: str):
        *_, date = filepath.split('_')
        return date

    return tuple(
        sorted(
            seed_path_generator(),
            key=sort_key,
            reverse=(sort_order == SortOrder.DESCENDING)
        )
    )


def load_seed_data(*, filepath: str) -> JSON_DATA_TYPES:
    if not os.path.isabs(filepath):
        filepath = join(DATA_DIR, filepath)

    with open(filepath, 'r') as file:
        return json.load(file)


def get_all_seed_data() -> tuple[JSON_DATA_TYPES]:
    return tuple(
        load_seed_data(filepath=filepath)
        for filepath
        in get_all_seed_paths()
    )


def get_sorted_seed_data(*, sort_order: SortOrder = SortOrder.ASCENDING) -> tuple[JSON_DATA_TYPES]:
    return tuple(
        load_seed_data(filepath=filepath)
        for filepath
        in get_sorted_seed_paths(sort_order=sort_order)
    )


def get_seed_data_by_recency(*, offset: int = 0) -> Dict:
    offset = abs(offset)

    most_recent_filepaths = get_sorted_seed_paths(sort_order=SortOrder.DESCENDING)

    selected_filepath = most_recent_filepaths[offset]

    return load_seed_data(filepath=selected_filepath)


def get_most_recent_seed_data() -> Dict:
    return get_seed_data_by_recency(offset=0)


print(get_most_recent_seed_data())
