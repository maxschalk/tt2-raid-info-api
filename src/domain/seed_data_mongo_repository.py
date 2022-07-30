from typing import List, Literal, Optional, Tuple, Union

import pymongo
from pymongo import MongoClient
from src.domain.seed_data_repository import SeedDataRepository
from src.model.raid_data import RaidSeedData
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder


def _get_pymongo_sort_order(
        *, sort_order: SortOrder) -> Optional[Union[Literal[1], Literal[-1]]]:
    if sort_order == SortOrder.ASCENDING:
        return pymongo.ASCENDING

    if sort_order == SortOrder.DESCENDING:
        return pymongo.DESCENDING

    return None


class SeedDataMongoRepository(SeedDataRepository):

    _connection_string_template = ("mongodb+srv://"
                                   "{username}:{password}"
                                   "@{url}?retryWrites=true&w=majority")

    def __init__(self, *, url: str, username: str, password: str, db_name: str,
                 collection_name: str) -> None:
        super().__init__()

        self._connection_string = self._connection_string_template.format(
            username=username, password=password, url=url)

        self._client = self._connect()

        self._database = self._client[db_name]
        self._collection = self._database[collection_name]

    def _connect(self) -> MongoClient:
        return MongoClient(self._connection_string)

    def _disconnect(self) -> None:
        if self._client:
            self._client.close()

    def list_seed_identifiers(
            self,
            *,
            seed_type: SeedType = SeedType.RAW,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:

        db_sort_order = _get_pymongo_sort_order(sort_order=sort_order)

        records = self._collection.find({
            "seed_type": seed_type.value
        }).sort("identifier", db_sort_order)

        return tuple(map(lambda r: r['identifier'], records))

    def get_seed_identifier_by_week_offset(
            self,
            *,
            seed_type: SeedType = SeedType.RAW,
            offset_weeks: int = 0) -> Optional[str]:

        offset_weeks = abs(offset_weeks)

        records = self._collection.find({
            "seed_type": seed_type.value
        }).sort("identifier", pymongo.DESCENDING)

        try:
            return records[offset_weeks]["identifier"]
        except IndexError:
            return None

    def get_seed_by_identifier(self,
                               *,
                               identifier: str,
                               seed_type: SeedType = SeedType.RAW
                               ) -> Optional[List[RaidSeedData]]:

        record = self._collection.find_one({
            "identifier": identifier,
            "seed_type": seed_type.value
        })

        try:
            return record["data"]
        except KeyError:
            return None

    def get_seed_by_week_offset(
        self,
        *,
        seed_type: SeedType = SeedType.RAW,
        offset_weeks: int = 0,
    ) -> Optional[List[RaidSeedData]]:

        seed_id = self.get_seed_identifier_by_week_offset(
            seed_type=seed_type, offset_weeks=offset_weeks)

        if seed_id is None:
            return None

        return self.get_seed_by_identifier(identifier=seed_id,
                                           seed_type=seed_type)

    def list_seeds(
        self,
        *,
        seed_type: SeedType = SeedType.RAW,
        sort_order: SortOrder = SortOrder.ASCENDING
    ) -> Tuple[List[RaidSeedData]]:

        db_sort_order = _get_pymongo_sort_order(sort_order=sort_order)

        records = self._collection.find({
            "seed_type": seed_type.value
        }).sort("identifier", db_sort_order)

        return tuple(map(lambda r: r["data"], records))

    def save_seed(self, *, identifier: str, data: List[RaidSeedData],
                  seed_type: SeedType) -> bool:

        if self._collection.count_documents({
                "identifier": identifier,
                "seed_type": seed_type.value
        }) > 0:
            return False

        self._collection.insert_one({
            "identifier":
            identifier,
            "seed_type":
            seed_type.value,
            "data":
            list(map(lambda elem: elem.dict(), data))
        })

        return True

    def delete_seed(self, *, identifier: str, seed_type: SeedType) -> bool:

        result = self._collection.delete_one({
            "identifier": identifier,
            "seed_type": seed_type.value,
        })

        return result.deleted_count > 0
