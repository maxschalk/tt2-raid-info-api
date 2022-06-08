import operator
from typing import List, Tuple

import pytest
import requests
from dotenv import load_dotenv

from src.models.SeedType import SeedType
from src.models.SortOrder import SortOrder
from src.models.Stage import Stage
from src.models.raid_data import RaidRawSeedData
from test.utils.assert_deep_equals import assert_deep_equals
from test.utils.make_request import make_request_sync

load_dotenv()

BASE_PATH_ADMIN = "admin"
BASE_PATH_SEEDS = "seeds"
BASE_PATH_RAID_INFO = "raid_info"


def test_stage(stage: Stage):
    if stage == Stage.PRODUCTION:
        pytest.skip(allow_module_level=True)


# TEST ADMIN


def admin_get_all_filenames_base(
        stage: Stage,
        posted_seeds: List[Tuple[str, RaidRawSeedData]],
        seed_type: SeedType,
        sort_order: SortOrder = None
):
    qs = "" if sort_order is None else f"?sort_order={sort_order.value}"

    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_ADMIN}/all_seed_filenames/{seed_type.value}{qs}",
        stage=stage,
        parse_response=False
    )

    assert response.status_code == 200

    filenames = response.json()

    assert all(type(filename) is str for filename in filenames)

    filenames_iter = iter(filenames)

    if sort_order in {None, SortOrder.ASCENDING}:
        op = operator.le
    else:
        op = operator.ge

    prev = next(filenames_iter)

    for filename in filenames_iter:
        assert op(prev, filename)

        prev = filename

    assert all(filename in filenames for filename, _ in posted_seeds)


def test_admin_get_all_filenames(stage: Stage, posted_seeds: List[Tuple[str, RaidRawSeedData]]):
    for seed_type in (SeedType.RAW, SeedType.ENHANCED):
        for sort_order in (None, SortOrder.ASCENDING, SortOrder.DESCENDING):
            admin_get_all_filenames_base(stage, posted_seeds, seed_type, sort_order)


# TEST SEEDS


def test_seeds_all_raw_contains_posted_seeds(
        stage: Stage,
        posted_seeds: List[Tuple[str, RaidRawSeedData]],
):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_SEEDS}/all/{SeedType.RAW.value}",
        stage=stage,
        parse_response=False
    )

    assert response.status_code == 200

    server_seeds = response.json()

    test_seeds = list(map(lambda t: t[1], posted_seeds))

    for posted_seed, server_seed in zip(test_seeds, server_seeds):
        assert_deep_equals(posted_seed, server_seed)


def test_seeds_most_recent_raw_contains_posted_seed(stage: Stage, posted_seeds: List[RaidRawSeedData]):
    all_filenames = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
        stage=stage,
    )

    files_count = len(all_filenames)

    for i, (_, posted_seed) in enumerate(posted_seeds):
        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_SEEDS}/most_recent/raw?offset_weeks={files_count - 1 - i}",
            stage=stage,
            parse_response=False
        )

        assert response.status_code == 200

        server_seed = response.json()

        assert_deep_equals(posted_seed, server_seed)

# TEST RAID INFO
