import asyncio
import operator
from test.utils.assert_deep_equals import assert_deep_equals
from test.utils.make_request import make_request_async, make_request_sync
from typing import List, Tuple

import aiohttp
import pytest
import requests
from dotenv import load_dotenv
from pydantic import ValidationError
from src.models.raid_data import RaidSeedDataEnhanced, RaidSeedDataRaw
from src.models.SeedType import SeedType
from src.models.SortOrder import SortOrder
from src.models.Stage import Stage
from src.utils import selectors

load_dotenv()

BASE_PATH_ADMIN = "admin"
BASE_PATH_SEEDS = "seeds"
BASE_PATH_RAID_INFO = "raid_info"


def test_validate_stage(stage: Stage):
    if stage == Stage.PRODUCTION:
        pytest.skip(allow_module_level=True)


# TEST ADMIN


def admin_get_all_filenames_base(
        stage: Stage,
        posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
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

    if sort_order in {None, SortOrder.ASCENDING}:
        op = operator.le
    else:
        op = operator.ge

    assert all(op(a, b) for a, b in zip(filenames, filenames[1:]))

    assert all(filename in filenames for filename, _ in posted_seeds)


def test_admin_get_all_filenames(stage: Stage, posted_seeds: List[Tuple[str, RaidSeedDataRaw]]):
    for seed_type in SeedType:
        for sort_order in (None, *SortOrder):
            admin_get_all_filenames_base(
                stage, posted_seeds, seed_type, sort_order)


def test_admin_download_file(
        stage: Stage,
        posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
):
    for filename, posted_seed in posted_seeds:
        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_ADMIN}/seed_file/{SeedType.RAW.value}/{filename}",
            stage=stage,
            parse_response=False
        )

        assert response.status_code == 200

        data = response.json()

        assert_deep_equals(posted_seed, data)


# TEST SEEDS


def test_seeds_all_raw_contains_posted_seeds(
        stage: Stage,
        posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_SEEDS}/{SeedType.RAW.value}/all",
        stage=stage,
        parse_response=False
    )

    assert response.status_code == 200

    server_seeds = response.json()

    test_seeds = list(map(lambda t: t[1], posted_seeds))

    for posted_seed, server_seed in zip(test_seeds, server_seeds):
        assert_deep_equals(posted_seed, server_seed)


def test_seeds_most_recent_raw_contains_posted_seed(stage: Stage, posted_seeds: List[RaidSeedDataRaw]):
    all_filenames = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
        stage=stage,
    )

    files_count = len(all_filenames)

    for i, (_, posted_seed) in enumerate(posted_seeds):
        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_SEEDS}/{SeedType.RAW.value}/most_recent?offset_weeks={files_count - 1 - i}",
            stage=stage,
            parse_response=False
        )

        assert response.status_code == 200

        server_seed = response.json()

        assert_deep_equals(posted_seed, server_seed)


def test_seeds_all_were_enhanced(stage: Stage, posted_seeds: List[RaidSeedDataRaw]):
    all_filenames = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.ENHANCED.value}",
        stage=stage,
    )

    files_count = len(all_filenames)

    for i, (_, posted_seed) in enumerate(posted_seeds):
        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_SEEDS}/{SeedType.ENHANCED.value}/most_recent?offset_weeks={files_count - 1 - i}",
            stage=stage,
            parse_response=False
        )

        assert response.status_code == 200

        server_seed = response.json()

        try:
            for raid_info in server_seed:
                RaidSeedDataEnhanced(**raid_info)
        except TypeError:
            raise AssertionError


# TEST RAID INFO


@pytest.mark.asyncio
async def test_raid_info_exists(stage: Stage, posted_seeds: List[RaidSeedDataRaw]):
    all_filenames = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
        stage=stage,
    )

    files_count = len(all_filenames)

    for i, (_, posted_seed) in enumerate(posted_seeds):

        paths = tuple(
            f"{BASE_PATH_RAID_INFO}/{SeedType.RAW.value}/{selectors.raid_tier(raid_info)}/{selectors.raid_level(raid_info)}?offset_weeks={files_count - 1 - i}"
            for raid_info in posted_seed
        )

        async with aiohttp.ClientSession() as session:
            raid_infos = await asyncio.gather(
                *map(lambda p: make_request_async(stage=stage, method=session.get, path=p, response_json=True), paths)
            )

        for posted_raid_info, server_raid_info in zip(posted_seed, raid_infos):
            assert_deep_equals(posted_raid_info, server_raid_info)


# TEST ADMIN DELETE FILES

def test_admin_delete_file(
        stage: Stage,
        posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
):
    for filename, posted_seed in posted_seeds:
        response = make_request_sync(
            method=requests.delete,
            path=f"{BASE_PATH_ADMIN}/raw_seed_file/{filename}",
            stage=stage,
            parse_response=False
        )

        assert response.status_code == 200


def test_admin_filenames_deleted(
        stage: Stage,
        posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_ADMIN}/all_seed_filenames/{SeedType.RAW.value}",
        stage=stage,
        parse_response=False
    )

    assert response.status_code == 200

    filenames = response.json()

    assert all(filename not in filenames for filename, _ in posted_seeds)
