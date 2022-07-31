from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from src.model.seed_type import SeedType

from .raid_info import _factory_raid_info_by_tier_level

repo_mock = Mock()
selectors_utils_mock = Mock()
map_to_native_object_mock = Mock()

# pylint: disable = fixme


class TestGetRaidInfo:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_raid_info_by_tier_level(
            repo=repo_mock,
            selectors_utils=selectors_utils_mock,
            map_to_native_object_func=map_to_native_object_mock)

    @pytest.mark.asyncio
    async def test_success(self, handler):

        async def base(**kwargs):
            data = object()
            mapped_data = object()
            selected_data = object()

            repo_mock.get_seed_by_week_offset = Mock()
            repo_mock.get_seed_by_week_offset.return_value = data

            map_to_native_object_mock.return_value = mapped_data

            selectors_utils_mock.select_first_by = Mock()
            selectors_utils_mock.select_first_by.return_value = selected_data

            result = await handler(**kwargs)

            repo_mock.get_seed_by_week_offset.assert_called_once_with(
                **{
                    "seed_type": kwargs.get("seed_type"),
                    "offset_weeks": kwargs.get("offset_weeks", 0)
                })

            # TODO: test passes validators are selecting correctly
            selectors_utils_mock.select_first_by.assert_called_once()

            assert result == selected_data

        for seed_type in SeedType:
            for offset_weeks in (None, *range(-5, 6)):
                for tier in range(-2, 3):
                    for level in range(-2, 3):

                        kwargs = {
                            "seed_type": seed_type,
                            "tier": tier,
                            "level": level
                        }

                        if offset_weeks:
                            kwargs["offset_weeks"] = offset_weeks

                        await base(**kwargs)

    @pytest.mark.asyncio
    async def test_throws_nodata(self, handler):

        repo_mock.get_seed_by_week_offset = Mock()
        repo_mock.get_seed_by_week_offset.return_value = None

        with pytest.raises(HTTPException):
            await handler(seed_type=SeedType.RAW, tier=1, level=1)

    @pytest.mark.asyncio
    async def test_throws_noselection(self, handler):

        repo_mock.get_seed_by_week_offset = Mock()
        repo_mock.get_seed_by_week_offset.return_value = object()

        selectors_utils_mock.select_first_by = Mock()
        selectors_utils_mock.select_first_by.return_value = None

        with pytest.raises(HTTPException):
            await handler(seed_type=SeedType.RAW, tier=1, level=1)
