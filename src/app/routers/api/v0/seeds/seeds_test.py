from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder

from .seeds import _factory_get_all_seeds, _factory_get_seed_by_recency

# pylint: disable = duplicate-code

repo_mock = Mock()


class TestListSeeds:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_get_all_seeds(repo=repo_mock)

    @pytest.mark.asyncio
    async def test_success(self, handler):

        data = object()

        async def base(**kwargs):
            repo_mock.list_seeds = Mock()
            repo_mock.list_seeds.return_value = data

            result = await handler(**kwargs)

            kwargs["sort_order"] = kwargs.get("sort_order",
                                              SortOrder.ASCENDING)

            repo_mock.list_seeds.assert_called_once_with(**kwargs)

            assert result == data

        for seed_type in SeedType:
            for sort_order in (None, *SortOrder):

                kwargs = {"seed_type": seed_type}

                if sort_order:
                    kwargs["sort_order"] = sort_order

                await base(**kwargs)


class TestGetSeed:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_get_seed_by_recency(repo=repo_mock)

    @pytest.mark.asyncio
    async def test_success_data(self, handler):

        async def base(**kwargs):
            data = object()

            repo_mock.get_seed_by_week_offset = Mock()
            repo_mock.get_seed_by_week_offset.return_value = data

            result = await handler(**kwargs)

            kwargs["offset_weeks"] = kwargs.get("offset_weeks", 0)

            repo_mock.get_seed_by_week_offset.assert_called_once_with(**kwargs)

            assert result == data

        for seed_type in SeedType:
            for offset_weeks in (None, *range(-5, 6)):
                for download in (None, False):

                    kwargs = {"seed_type": seed_type}

                    if offset_weeks:
                        kwargs["offset_weeks"] = offset_weeks

                    if download:
                        kwargs["download"] = download

                    await base(**kwargs)

    @pytest.mark.asyncio
    async def test_success_download(self, handler):

        async def base(**kwargs):
            repo_mock.get_seed_identifier_by_week_offset = Mock()
            repo_mock.get_seed_identifier_by_week_offset.return_value = "testid"

            result = await handler(**kwargs)

            repo_mock.get_seed_identifier_by_week_offset.assert_called_once_with(
                offset_weeks=kwargs.get("offset_weeks", 0))

            assert isinstance(result, RedirectResponse)

            assert result.headers.get(
                "location"
            ) == f"/api/v0/admin/seed/{kwargs['seed_type'].value}/testid"

        for seed_type in SeedType:
            for offset_weeks in (None, *range(-5, 6)):

                kwargs = {"seed_type": seed_type, "download": True}

                if offset_weeks:
                    kwargs["offset_weeks"] = offset_weeks

                await base(**kwargs)

    @pytest.mark.asyncio
    async def test_throws_noseed(self, handler):

        repo_mock.get_seed_by_week_offset = Mock()
        repo_mock.get_seed_by_week_offset.return_value = None

        with pytest.raises(HTTPException):
            await handler(seed_type=SeedType.RAW)
