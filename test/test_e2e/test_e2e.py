import operator
from test.utils.assert_deep_equals import assert_deep_equals
from test.utils.make_request import make_request_sync, make_requests_async
from typing import List, Tuple

import pytest
import requests
from dotenv import load_dotenv
from src.model.raid_data import RaidSeedDataEnhanced, RaidSeedDataRaw
from src.model.seed_type import SeedType
from src.stage import Stage
from src.utils import selectors
from src.utils.sort_order import SortOrder

load_dotenv()

BASE_PATH_ADMIN = "admin"
BASE_PATH_SEEDS = "seeds"
BASE_PATH_RAID_INFO = "raid_info"


def test_validate_stage(stage: Stage):
    if stage == Stage.PRODUCTION:
        pytest.skip(allow_module_level=True)


# TEST ADMIN


def admin_get_all_filenames_base(stage: Stage,
                                 posted_seeds: List[Tuple[str,
                                                          RaidSeedDataRaw]],
                                 seed_type: SeedType,
                                 sort_order: SortOrder = None):
    query = "" if sort_order is None else f"?sort_order={sort_order.value}"

    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_ADMIN}/all_seed_filenames/{seed_type.value}{query}",
        stage=stage,
        parse_response=False)

    assert response.status_code == 200

    filenames = response.json()

    assert all(isinstance(filename, str) for filename in filenames)

    if sort_order in {None, SortOrder.ASCENDING}:
        comparison_op = operator.le
    else:
        comparison_op = operator.ge

    assert all(comparison_op(a, b) for a, b in zip(filenames, filenames[1:]))

    assert all(filename in filenames for filename, _ in posted_seeds)


def test_admin_get_all_filenames(stage: Stage,
                                 posted_seeds: List[Tuple[str,
                                                          RaidSeedDataRaw]]):
    for seed_type in SeedType:
        for sort_order in (None, *SortOrder):
            admin_get_all_filenames_base(stage, posted_seeds, seed_type,
                                         sort_order)


def test_admin_download_file(
    stage: Stage,
    posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
):
    for filename, posted_seed in posted_seeds:
        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_ADMIN}/seed_file/{SeedType.RAW.value}/{filename}",
            stage=stage,
            parse_response=False)

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
        parse_response=False)

    assert response.status_code == 200

    server_seeds = response.json()

    test_seeds = list(map(lambda t: t[1], posted_seeds))

    for posted_seed, server_seed in zip(test_seeds, server_seeds):
        assert_deep_equals(posted_seed, server_seed)


def test_seeds_recent_raw_contains_posted_seed(
        stage: Stage, posted_seeds: List[RaidSeedDataRaw]):
    all_filenames = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
        stage=stage,
    )

    files_count = len(all_filenames)

    for i, (_, posted_seed) in enumerate(posted_seeds):
        response = make_request_sync(
            method=requests.get,
            path=
            f"{BASE_PATH_SEEDS}/{SeedType.RAW.value}/recent?offset_weeks={files_count - 1 - i}",
            stage=stage,
            parse_response=False)

        assert response.status_code == 200

        server_seed = response.json()

        assert_deep_equals(posted_seed, server_seed)


def test_seeds_all_were_enhanced(stage: Stage,
                                 posted_seeds: List[RaidSeedDataRaw]):
    all_filenames = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.ENHANCED.value}",
        stage=stage,
    )

    files_count = len(all_filenames)

    for i, _ in enumerate(posted_seeds):
        query = f"offset_weeks={files_count - 1 - i}"

        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_SEEDS}/{SeedType.ENHANCED.value}/recent?{query}",
            stage=stage,
            parse_response=False)

        assert response.status_code == 200

        server_seed = response.json()

        try:
            for raid_info in server_seed:
                RaidSeedDataEnhanced(**raid_info)
        except TypeError as exc:
            raise AssertionError from exc


# TEST RAID INFO


@pytest.mark.asyncio
async def test_raid_info_exists(stage: Stage,
                                posted_seeds: List[RaidSeedDataRaw]):
    all_filenames = make_request_sync(
        method=requests.get,
        path=f"admin/all_seed_filenames/{SeedType.RAW.value}",
        stage=stage,
    )

    files_count = len(all_filenames)

    def build_path(raid_info, offset):
        seed_type = SeedType.RAW.value
        tier = selectors.raid_tier(raid_info)
        level = selectors.raid_level(raid_info)
        query = f"offset_weeks={files_count - 1 - offset}"

        return f"{BASE_PATH_RAID_INFO}/{seed_type}/{tier}/{level}?{query}"

    for i, (_, posted_seed) in enumerate(posted_seeds):

        paths = tuple(build_path(raid_info, i) for raid_info in posted_seed)

        raid_infos = await make_requests_async(paths, stage)

        for posted_raid_info, server_raid_info in zip(posted_seed, raid_infos):
            assert_deep_equals(posted_raid_info, server_raid_info)


# TEST ADMIN DELETE FILES


def test_admin_delete_file(
    stage: Stage,
    posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
):
    for filename, _ in posted_seeds:
        response = make_request_sync(
            method=requests.delete,
            path=f"{BASE_PATH_ADMIN}/raw_seed_file/{filename}",
            stage=stage,
            parse_response=False)

        assert response.status_code == 200


def test_admin_filenames_deleted(
    stage: Stage,
    posted_seeds: List[Tuple[str, RaidSeedDataRaw]],
):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_ADMIN}/all_seed_filenames/{SeedType.RAW.value}",
        stage=stage,
        parse_response=False)

    assert response.status_code == 200

    filenames = response.json()

    assert all(filename not in filenames for filename, _ in posted_seeds)
