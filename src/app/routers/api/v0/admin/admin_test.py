from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from src.domain.seed_data_repository import (SeedDuplicateError,
                                             SeedNotFoundError)
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder

from .admin import (TT2_RAID_API_KEY, _factory_delete_seed,
                    _factory_download_seed_file, _factory_enhance_seed,
                    _factory_list_seed_identifiers, _factory_save_seed,
                    _verify_authorization)

# pylint: disable = protected-access

repo_mock = Mock()

create_stream_response_mock = Mock()
enhance_seed_data_mock = Mock()
map_to_native_object_mock = Mock()


def test_verify_authorization():

    _verify_authorization(secret=TT2_RAID_API_KEY)

    with pytest.raises(HTTPException):
        _verify_authorization(secret="invalid")


class TestListSeedIdentifiers:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_list_seed_identifiers(repo=repo_mock)

    @pytest.mark.asyncio
    async def test_success(self, handler):

        data = object()

        async def base(**kwargs):
            repo_mock.list_seed_identifiers = Mock()
            repo_mock.list_seed_identifiers.return_value = data

            result = await handler(**kwargs)

            kwargs["sort_order"] = kwargs.get("sort_order",
                                              SortOrder.ASCENDING)

            repo_mock.list_seed_identifiers.assert_called_once_with(**kwargs)

            assert result == data

        for seed_type in SeedType:
            for sort_order in (None, *SortOrder):

                kwargs = {"seed_type": seed_type}

                if sort_order:
                    kwargs["sort_order"] = sort_order

                await base(**kwargs)


class TestDownloadSeedFile:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_download_seed_file(
            repo=repo_mock,
            create_stream_response_func=create_stream_response_mock)

    @pytest.mark.asyncio
    async def test_success(self, handler):

        data = object()
        stream_response = object()

        async def base(**kwargs):
            repo_mock.get_seed_by_identifier = Mock()
            repo_mock.get_seed_by_identifier.return_value = data

            create_stream_response_mock.return_value = stream_response

            result = await handler(**kwargs)

            repo_mock.get_seed_by_identifier.assert_called_once_with(**kwargs)
            create_stream_response_mock.assert_called_with(
                **{
                    "data": data,
                    "filename": "testid.json"
                })

            assert result == stream_response

            # assert isinstance(result, StreamingResponse)
            # assert result.media_type == "application/json"
            # assert result.status_code == 200
            # assert result.headers.get("content-disposition") == "attachment; filename=testid.json"

            # data, *_ = [item async for item in result.body_iterator]
            # assert json.loads(data) == return_value

        for seed_type in SeedType:
            await base(seed_type=seed_type, identifier="testid")

    @pytest.mark.asyncio
    async def test_throws_noseed(self, handler):
        repo_mock.get_seed_by_identifier.return_value = None

        with pytest.raises(HTTPException):
            await handler(seed_type=SeedType.RAW, identifier="testid")


class TestEnhanceSeedFile:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_enhance_seed(
            enhance_seed_data_func=enhance_seed_data_mock,
            create_stream_response_func=create_stream_response_mock)

    @pytest.mark.asyncio
    async def test_success_data(self, handler):

        data = object()
        enhanced_data = object()

        enhance_seed_data_mock.return_value = enhanced_data

        result = await handler(data=data)

        enhance_seed_data_mock.assert_called_with(**{"data": data})

        assert result == enhanced_data

    @pytest.mark.asyncio
    async def test_success_downloadfalse(self, handler):
        data = object()
        enhanced_data = object()

        enhance_seed_data_mock.return_value = enhanced_data

        result = await handler(data=data, download=False)

        enhance_seed_data_mock.assert_called_with(**{"data": data})

        assert result == enhanced_data

    @pytest.mark.asyncio
    async def test_success_download(self, handler):
        data = object()
        enhanced_data = object()
        stream_response = object()

        enhance_seed_data_mock.return_value = enhanced_data
        create_stream_response_mock.return_value = stream_response

        result = await handler(data=data, download=True)

        enhance_seed_data_mock.assert_called_with(**{"data": data})
        create_stream_response_mock.assert_called_with(
            **{
                "data": enhanced_data,
                "filename": "enhanced_custom_seed.json"
            })

        assert result == stream_response


class TestSaveSeed:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_save_seed(
            repo=repo_mock, enhance_seed_data_func=enhance_seed_data_mock)

    @pytest.mark.asyncio
    async def test_success(self, handler):

        data = object()
        enhanced_data = object()

        save_data = (
            ("testid", SeedType.RAW, data),
            ("testid", SeedType.ENHANCED, enhanced_data),
        )

        enhance_seed_data_mock.return_value = enhanced_data
        repo_mock.save_seeds = Mock()

        result = await handler(identifier="testid",
                               data=data,
                               secret=TT2_RAID_API_KEY)

        enhance_seed_data_mock.assert_called_with(**{"data": data})
        repo_mock.save_seeds.assert_called_once_with(**{"items": save_data})

        assert f"testid.{SeedType.RAW.value}" in result["detail"]
        assert f"testid.{SeedType.ENHANCED.value}" in result["detail"]
        assert result["identifier"] == "testid"

    @pytest.mark.asyncio
    async def test_throw_noauth(self, handler):

        data = object()

        with pytest.raises(HTTPException):
            await handler(identifier="testid", data=data)

    @pytest.mark.asyncio
    async def test_throw_duplicate(self, handler):

        data = object()

        repo_mock.save_seeds = Mock()
        repo_mock.save_seeds.side_effect = SeedDuplicateError

        with pytest.raises(HTTPException):
            await handler(identifier="testid",
                          data=data,
                          secret=TT2_RAID_API_KEY)


class TestDeleteSeed:

    @staticmethod
    @pytest.fixture
    def handler():
        return _factory_delete_seed(repo=repo_mock)

    @pytest.mark.asyncio
    async def test_success(self, handler):

        delete_data = (
            ("testid", SeedType.RAW),
            ("testid", SeedType.ENHANCED),
        )

        repo_mock.delete_seeds = Mock()

        result = await handler(identifier="testid", secret=TT2_RAID_API_KEY)

        repo_mock.delete_seeds.assert_called_once_with(
            **{"items": delete_data})

        assert f"testid.{SeedType.RAW.value}" in result["detail"]
        assert f"testid.{SeedType.ENHANCED.value}" in result["detail"]
        assert result["identifier"] == "testid"

    @pytest.mark.asyncio
    async def test_throw_noauth(self, handler):
        with pytest.raises(HTTPException):
            await handler(identifier="testid")

    @pytest.mark.asyncio
    async def test_throw_notfound(self, handler):

        repo_mock.delete_seeds = Mock()
        repo_mock.delete_seeds.side_effect = SeedNotFoundError

        with pytest.raises(HTTPException):
            await handler(identifier="testid", secret=TT2_RAID_API_KEY)
