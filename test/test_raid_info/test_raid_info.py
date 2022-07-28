import asyncio
from test.utils.make_request import make_request_async, make_requests_async

import aiohttp
import pytest
from src.domain.raid_data import RaidSeedDataEnhanced, RaidSeedDataRaw
from src.domain.seed_type import SeedType
from src.domain.stage import Stage

BASE_PATH = "raid_info"


@pytest.mark.asyncio
async def test_raid_info_valid_model(stage: Stage):
    cases = ((SeedType.RAW, RaidSeedDataRaw), (SeedType.ENHANCED,
                                               RaidSeedDataEnhanced))

    for seed_type, data_type in cases:
        paths = tuple(f"{BASE_PATH}/{seed_type.value}/{tier}/1"
                      for tier in range(1, 5))

        raid_infos = await make_requests_async(paths, stage)

        for raid_info in raid_infos:
            data_type(**raid_info)


@pytest.mark.asyncio
async def test_raid_info_invalid_tier_level(stage: Stage):
    cases = (
        (-1, 1),
        (-1, 0),
        (-1, -1),
        (0, 1),
        (0, 0),
        (0, -1),
        (5, 1),
        (5, 0),
        (5, -1),
        (1, 90),
        (2, 90),
        (3, 90),
        (4, 90),
    )

    paths = tuple(f"{BASE_PATH}/{seed_type.value}/{tier}/{level}"
                  for (tier, level) in cases for seed_type in SeedType)

    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*map(
            lambda p: make_request_async(
                stage=stage, method=session.get, path=p), paths))

        for response in responses:
            assert response.status == 400
