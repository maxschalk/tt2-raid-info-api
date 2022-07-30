from test.mocks import mock_raid_raw_seed_data

import pytest
from src.domain.mongo_seed_data_repository import MongoSeedDataRepository
from src.model.seed_type import SeedType
from src.utils.get_env import get_env

# pylint: disable=redefined-outer-name,protected-access


@pytest.fixture()
def repo() -> MongoSeedDataRepository:
    repo = MongoSeedDataRepository(
        url=get_env(key="MONGO_URL"),
        username=get_env(key="MONGO_USERNAME"),
        password=get_env(key="MONGO_PASSWORD"),
        db_name="test",
        collection_name=get_env(key="MONGO_COLLECTION_NAME"),
    )

    yield repo

    repo._teardown_db()


def test_save_seed(repo: MongoSeedDataRepository):
    repo.save_seed(identifier="test",
                   seed_type=SeedType.RAW,
                   data=[mock_raid_raw_seed_data()])

    assert "test" in repo.list_seed_identifiers()
