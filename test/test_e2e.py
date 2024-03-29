import asyncio
import contextlib
import json
import operator
import threading
import time
import uuid
from contextlib import suppress
from http.client import HTTPException
from test.mocks import mock_raid_seed_raw
from test.utils.assert_deep_equals import assert_deep_equals
from typing import List, Tuple

import aiohttp
import pytest
import requests
import uvicorn
from src.app.main import create_app
from src.domain.mongo_seed_data_repository import temp_repo
from src.model.raid_data import (RaidInfoRaw, RaidSeedRaw,
                                 map_to_native_object, map_to_raid_info,
                                 map_to_raid_seed)
from src.model.seed_type import SeedType
from src.stage import Stage
from src.utils import selectors
from src.utils.get_env import get_env
from src.utils.sort_order import SortOrder

# pylint: disable=redefined-outer-name

# UTILS

PORT = 6000

TT2_RAID_API_KEY = get_env(key='TT2_RAID_API_KEY')

BASE_URL = f"http://localhost:{PORT}/api/v0"

HEADERS = {'secret': TT2_RAID_API_KEY}


def make_request_sync(*,
                      method,
                      path,
                      data=None,
                      parse_response=True,
                      **kwargs):

    response = method(f"{BASE_URL}/{path}",
                      headers=HEADERS,
                      data=data,
                      **kwargs)

    if not parse_response:
        return response

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        return response.text


async def make_request_async(*, method, path, data=None, parse_response=False):

    async with method(url=f"{BASE_URL}/{path}", data=data) as response:
        if parse_response:
            return await response.json()

        return response


async def make_requests_async(paths):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*map(
            lambda p: make_request_async(
                method=session.get, path=p, parse_response=True), paths))


class Server(uvicorn.Server):

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


# SETUP

BASE_PATH_ADMIN = "admin"
BASE_PATH_SEEDS = "seeds"
BASE_PATH_RAID_INFO = "raid_info"


@pytest.fixture(scope="module", autouse=True)
def server():

    repo_init_kwargs = {
        "url": get_env(key="MONGO_URL"),
        "username": get_env(key="MONGO_USERNAME"),
        "password": get_env(key="MONGO_PASSWORD"),
        "db_name": str(uuid.uuid4()),
        "coll_name": "test",
    }

    with temp_repo(**repo_init_kwargs) as repo:

        app = create_app(stage=Stage.TEST, seed_data_repo=repo)

        config = uvicorn.Config(app=app, host="0.0.0.0", port=PORT)
        server = Server(config=config)

        with server.run_in_thread():
            yield


@pytest.fixture(scope="module")
def posted_seeds() -> List[Tuple[str, RaidSeedRaw]]:
    mocked_seeds = [mock_raid_seed_raw(length=3) for _ in range(3)]

    def identifier_from_seed(seed):
        valid_from = selectors.raid_valid_from(
            map_to_native_object(data=seed[0]))

        return f"raid_seed_{valid_from.strftime('%Y%m%d')}"

    seeds_posted = sorted(
        ((identifier_from_seed(seed), map_to_native_object(data=seed))
         for seed in mocked_seeds),
        key=lambda t: t[0])

    for identifier, seed in seeds_posted:
        response = make_request_sync(
            method=requests.post,
            path=f"{BASE_PATH_ADMIN}/save/{identifier}",
            data=json.dumps(seed),
            parse_response=False)

        assert response.status_code == 201

    yield seeds_posted

    for identifier, seed in seeds_posted:
        with suppress(HTTPException):
            response = make_request_sync(
                method=requests.delete,
                path=f"{BASE_PATH_ADMIN}/delete/{identifier}",
                parse_response=False)


# TEST ADMIN


def admin_get_all_identifiers_base(posted_seeds: List[Tuple[str, RaidSeedRaw]],
                                   seed_type: SeedType,
                                   sort_order: SortOrder = None):
    query = "" if sort_order is None else f"sort_order={sort_order.value}"

    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_ADMIN}/seed_identifiers/{seed_type.value}?{query}",
        parse_response=False)

    assert response.status_code == 200

    seed_identifiers = response.json()

    assert all(isinstance(identifier, str) for identifier in seed_identifiers)

    if sort_order in {None, SortOrder.ASCENDING}:
        comparison_op = operator.le
    else:
        comparison_op = operator.ge

    assert all(
        comparison_op(a, b)
        for a, b in zip(seed_identifiers, seed_identifiers[1:]))

    assert all(identifier in seed_identifiers
               for identifier, _ in posted_seeds)


def test_admin_get_all_identifiers(posted_seeds: List[Tuple[str,
                                                            RaidInfoRaw]]):
    for seed_type in SeedType:
        for sort_order in (None, *SortOrder):
            admin_get_all_identifiers_base(posted_seeds, seed_type, sort_order)


def test_admin_download_seed(posted_seeds: List[Tuple[str, RaidSeedRaw]], ):
    for identifier, posted_seed in posted_seeds:
        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_ADMIN}/seed/{SeedType.RAW.value}/{identifier}",
            parse_response=False)

        assert response.status_code == 200

        data = response.json()

        try:
            map_to_raid_seed(data=data, seed_type=SeedType.RAW)
        except TypeError as err:
            raise AssertionError from err

        assert_deep_equals(posted_seed, data)


# TEST SEEDS


def test_seeds_all_raw_contains_posted_seeds(
    posted_seeds: List[Tuple[str, RaidSeedRaw]], ):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_SEEDS}/{SeedType.RAW.value}",
        parse_response=False)

    assert response.status_code == 200

    server_seeds = response.json()

    test_seeds = list(map(lambda t: t[1], posted_seeds))

    for posted_seed, server_seed in zip(test_seeds, server_seeds):
        try:
            map_to_raid_seed(data=server_seed, seed_type=SeedType.RAW)
        except TypeError as err:
            raise AssertionError from err

        assert_deep_equals(posted_seed, server_seed)


def test_seeds_recent_raw_contains_posted_seed(
        posted_seeds: List[Tuple[str, RaidSeedRaw]]):
    all_identifiers = make_request_sync(
        method=requests.get,
        path=f"admin/seed_identifiers/{SeedType.RAW.value}",
    )

    seeds_count = len(all_identifiers)

    for i, (_, posted_seed) in enumerate(posted_seeds):
        response = make_request_sync(
            method=requests.get,
            path=
            f"{BASE_PATH_SEEDS}/{SeedType.RAW.value}/recent?offset_weeks={seeds_count - 1 - i}",
            parse_response=False)

        assert response.status_code == 200

        server_seed = response.json()

        try:
            map_to_raid_seed(data=server_seed, seed_type=SeedType.RAW)
        except TypeError as err:
            raise AssertionError from err

        assert_deep_equals(posted_seed, server_seed)


def test_seeds_all_were_enhanced(posted_seeds: List[Tuple[str, RaidSeedRaw]]):
    all_identifiers = make_request_sync(
        method=requests.get,
        path=f"admin/seed_identifiers/{SeedType.ENHANCED.value}",
    )

    seeds_count = len(all_identifiers)

    for i, _ in enumerate(posted_seeds):
        query = f"offset_weeks={seeds_count - 1 - i}"

        response = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH_SEEDS}/{SeedType.ENHANCED.value}/recent?{query}",
            parse_response=False)

        assert response.status_code == 200

        server_seed = response.json()

        try:
            map_to_raid_seed(data=server_seed, seed_type=SeedType.ENHANCED)
        except TypeError as err:
            raise AssertionError from err


# TEST RAID INFO


@pytest.mark.asyncio
async def test_raid_info(posted_seeds: List[Tuple[str, RaidSeedRaw]]):
    all_identifiers = make_request_sync(
        method=requests.get,
        path=f"admin/seed_identifiers/{SeedType.RAW.value}",
    )

    seeds_count = len(all_identifiers)

    def build_path(raid_info, offset, seed_type=SeedType.RAW):
        tier = selectors.raid_tier(raid_info)
        level = selectors.raid_level(raid_info)
        query = f"offset_weeks={seeds_count - 1 - offset}"

        return f"{BASE_PATH_RAID_INFO}/{seed_type.value}/{tier}/{level}?{query}"

    for i, (_, posted_seed) in enumerate(posted_seeds):

        paths_raw = tuple(
            build_path(raid_info, i) for raid_info in posted_seed)

        raid_infos = await make_requests_async(paths_raw)

        for posted_raid_info, server_raid_info in zip(posted_seed, raid_infos):
            try:
                map_to_raid_info(data=server_raid_info, seed_type=SeedType.RAW)
            except TypeError as err:
                raise AssertionError from err

            assert_deep_equals(posted_raid_info, server_raid_info)

        paths_enhanced = tuple(
            build_path(raid_info, i, SeedType.ENHANCED)
            for raid_info in posted_seed)

        raid_infos_enhanced = await make_requests_async(paths_enhanced)

        for server_raid_info in raid_infos_enhanced:
            try:
                map_to_raid_info(data=server_raid_info,
                                 seed_type=SeedType.ENHANCED)
            except TypeError as err:
                raise AssertionError from err


# TEST ADMIN DELETE FILES


def test_admin_delete_seed(posted_seeds: List[Tuple[str, RaidSeedRaw]], ):
    for identifier, _ in posted_seeds:
        response = make_request_sync(
            method=requests.delete,
            path=f"{BASE_PATH_ADMIN}/delete/{identifier}",
            parse_response=False)

        assert response.status_code == 200


def test_admin_identifiers_deleted(posted_seeds: List[Tuple[str,
                                                            RaidInfoRaw]], ):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH_ADMIN}/seed_identifiers/{SeedType.RAW.value}",
        parse_response=False)

    assert response.status_code == 200

    identifiers = response.json()

    assert all(identifier not in identifiers for identifier, _ in posted_seeds)
