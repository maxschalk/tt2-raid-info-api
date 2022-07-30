from typing import List, Literal, Optional, Tuple, Union

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
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


class SeedDuplicateError(Exception):
    pass


class SeedNotFoundError(Exception):
    pass


class MongoSeedDataRepository(SeedDataRepository):

    _connection_string_template = ("mongodb+srv://"
                                   "{username}:{password}"
                                   "@{url}?retryWrites=true&w=majority")

    def __init__(self, *, url: str, username: str, password: str, db_name: str,
                 collection_name: str) -> None:
        super().__init__()

        self._connection_string = self._connection_string_template.format(
            username=username, password=password, url=url)

        self._client = self._connect()

        self._db_name = db_name
        self._database = self._client[db_name]

        self._collection_name = collection_name
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
        except (KeyError, TypeError):
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

    def _save_seed(self,
                   *,
                   collection: Collection,
                   identifier: str,
                   seed_type: SeedType,
                   data: List[RaidSeedData],
                   session=None) -> bool:

        if collection.count_documents(
            {
                "identifier": identifier,
                "seed_type": seed_type.value
            },
                session=session) > 0:
            return False

        collection.insert_one(
            {
                "identifier": identifier,
                "seed_type": seed_type.value,
                "data": list(map(lambda elem: elem.dict(), data))
            },
            session=session)

        return True

    def save_seed(self, *, identifier: str, seed_type: SeedType,
                  data: List[RaidSeedData]) -> bool:

        return self._save_seed(collection=self._collection,
                               identifier=identifier,
                               seed_type=seed_type,
                               data=data)

    def save_seeds(
            self, *, items: Tuple[Tuple[str, SeedType,
                                        List[RaidSeedData]]]) -> bool:

        def callback(session) -> None:
            collection = session.client[self._db_name][self._collection_name]

            for item in items:
                identifier, seed_type, data = item

                success = self._save_seed(collection=collection,
                                          identifier=identifier,
                                          seed_type=seed_type,
                                          data=data,
                                          session=session)

                if success is False:
                    raise Exception(
                        f"Failed to save seed {identifier}.{seed_type}")

        with self._client.start_session() as session:
            try:
                session.with_transaction(callback=callback)
            except Exception:
                return False

        return True

    def _delete_seed(self,
                     *,
                     collection: Collection,
                     identifier: str,
                     seed_type: SeedType,
                     session=None) -> bool:

        result = collection.delete_one(
            {
                "identifier": identifier,
                "seed_type": seed_type.value,
            },
            session=session)

        return result.deleted_count > 0

    def delete_seed(self, *, identifier: str, seed_type: SeedType) -> bool:

        return self._delete_seed(collection=self._collection,
                                 identifier=identifier,
                                 seed_type=seed_type)

    def delete_seeds(self, *, items: Tuple[Tuple[str, SeedType]]) -> bool:

        def callback(session) -> None:
            collection = session.client[self._db_name][self._collection_name]

            for item in items:
                identifier, seed_type = item

                success = self._delete_seed(collection=collection,
                                            identifier=identifier,
                                            seed_type=seed_type,
                                            session=session)

                if success is False:
                    raise Exception

        with self._client.start_session() as session:
            try:
                session.with_transaction(callback=callback)
            except Exception:
                return False

        return True
