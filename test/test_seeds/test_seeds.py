import asyncio
import operator
import unittest
from test.utils.make_request import make_request_async, make_request_sync
from typing import Type

import aiohttp
import pytest
import requests
from src.models.raid_data import RaidEnhancedSeedData, RaidRawSeedData
from src.models.SeedType import SeedType
from src.models.SortOrder import SortOrder
from src.models.Stage import Stage

BASE_PATH = "seeds"


def seeds_all_valid_model_base(
        stage: Stage,
        seed_type: SeedType,
        data_type: Type[RaidRawSeedData | RaidEnhancedSeedData]
):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH}/{seed_type.value}/all",
        stage=stage,
        parse_response=False
    )

    assert response.status_code == 200

    server_seeds = response.json()

    for server_seed in server_seeds:
        for raid_info in server_seed:
            data_type(**raid_info)


def test_seeds_all_raw_valid_model(stage: Stage):
    seeds_all_valid_model_base(stage, SeedType.RAW, RaidRawSeedData)


def test_seeds_all_enhanced_valid_model(stage: Stage):
    seeds_all_valid_model_base(stage, SeedType.ENHANCED, RaidEnhancedSeedData)


def seeds_all_sort_order_base(stage: Stage, seed_type: SeedType, sort_order: SortOrder = None):
    qs = "" if sort_order is None else f"?sort_order={sort_order.value}"

    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH}/{seed_type.value}/all{qs}",
        stage=stage,
        parse_response=False
    )

    assert response.status_code == 200

    server_seeds = response.json()

    server_seeds_valid_from_dates = list(
        map(lambda seed: seed[0]["raid_info_valid_from"], server_seeds))

    if sort_order in {None, SortOrder.ASCENDING}:
        op = operator.le
    else:
        op = operator.ge

    assert all(op(a, b) for a, b in zip(
        server_seeds_valid_from_dates, server_seeds_valid_from_dates[1:]))


def test_seeds_all_raw_default_is_ascending(stage: Stage):
    seeds_all_sort_order_base(stage, SeedType.RAW)


def test_seeds_all_raw_ascending(stage: Stage):
    seeds_all_sort_order_base(stage, SeedType.RAW, SortOrder.ASCENDING)


def test_seeds_all_raw_descending(stage: Stage):
    seeds_all_sort_order_base(stage, SeedType.RAW, SortOrder.DESCENDING)


def test_seeds_all_enhanced_default_is_ascending(stage: Stage):
    seeds_all_sort_order_base(stage, SeedType.ENHANCED)


def test_seeds_all_enhanced_ascending(stage: Stage):
    seeds_all_sort_order_base(stage, SeedType.ENHANCED, SortOrder.ASCENDING)


def test_seeds_all_enhanced_descending(stage: Stage):
    seeds_all_sort_order_base(stage, SeedType.ENHANCED, SortOrder.DESCENDING)


def seeds_most_recent_valid_model_base(
        stage: Stage,
        seed_type: SeedType,
        data_type: Type[RaidRawSeedData | RaidEnhancedSeedData]
):
    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH}/{seed_type.value}/most_recent",
        stage=stage,
        parse_response=False
    )

    assert response.status_code == 200

    server_seed = response.json()

    for raid_info in server_seed:
        data_type(**raid_info)


def test_seeds_most_recent_raw_valid_model(stage: Stage):
    seeds_most_recent_valid_model_base(stage, SeedType.RAW, RaidRawSeedData)


def test_seeds_most_recent_enhanced_valid_model(stage: Stage):
    seeds_most_recent_valid_model_base(
        stage, SeedType.ENHANCED, RaidEnhancedSeedData)


@pytest.mark.asyncio
async def test_seeds_most_recent_get_descending_seeds(stage: Stage):
    for seed_type in SeedType:
        all_server_seeds = make_request_sync(
            method=requests.get,
            path=f"{BASE_PATH}/{seed_type.value}/all?sort_order={SortOrder.DESCENDING.value}",
            stage=stage,
            parse_response=False
        ).json()

        paths = tuple(
            f"{BASE_PATH}/{seed_type.value}/most_recent?offset_weeks={i}"
            for i, _ in enumerate(all_server_seeds)
        )

        async with aiohttp.ClientSession() as session:
            individual_seeds = await asyncio.gather(
                *map(lambda p: make_request_async(stage=stage, method=session.get, path=p, response_json=True), paths)
            )

        for a, b in zip(all_server_seeds, individual_seeds):
            unittest.TestCase().assertListEqual(a, b)
