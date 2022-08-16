import contextlib
import re
from datetime import datetime, timedelta
from typing import (Callable, Generator, Iterable, Literal, Optional, Tuple,
                    Union)

import pymongo
from cachetools import TTLCache, cached
from pymongo import MongoClient
from pymongo.collection import Collection
from src.domain.seed_data_repository import (SeedDataRepository,
                                             SeedDuplicateError,
                                             SeedNotFoundError)
from src.model.raid_data import (RaidSeed, is_of_seed_type,
                                 map_to_native_object, map_to_raid_seed)
from src.model.seed_type import SeedType
from src.utils.sort_order import SortOrder

_CACHE = TTLCache(maxsize=32, ttl=600)


def _map_pymongo_sort_order(
        *, sort_order: SortOrder) -> Optional[Union[Literal[1], Literal[-1]]]:
    if sort_order == SortOrder.ASCENDING:
        return pymongo.ASCENDING

    if sort_order == SortOrder.DESCENDING:
        return pymongo.DESCENDING

    return None


def filter_by_key(predicate: Callable, iterable: Iterable,
                  key_func: Callable) -> Generator:
    for value in iterable:
        if predicate(key_func(value)):
            yield value


def get_ids_older_than(ids: Iterable[str], days: int) -> Tuple[str]:

    def key_func(seed_id: str) -> datetime.date:
        date_str = re.search(r"\d+", seed_id).group()
        date = datetime.strptime(date_str, "%Y%m%d").date()

        return date

    cutoff = (datetime.now() - timedelta(days=days)).date()

    ids_older = filter_by_key(predicate=lambda d: d < cutoff,
                              iterable=ids,
                              key_func=key_func)

    return tuple(ids_older)


class MongoSeedDataRepository(SeedDataRepository):

    _connection_string_template = ("mongodb+srv://"
                                   "{username}:{password}"
                                   "@{url}?retryWrites=true&w=majority")

    def __init__(self, *, url: str, username: str, password: str, db_name: str,
                 coll_name: str) -> None:
        super().__init__()

        self._connection_string = self._connection_string_template.format(
            username=username, password=password, url=url)

        self._client = self._connect()

        self._database_name = db_name
        self._database = self._client[db_name]

        self._collection_name = coll_name
        self._collection = self._database[coll_name]

    def _connect(self) -> MongoClient:
        return MongoClient(self._connection_string)

    def _disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def _teardown_db(self) -> None:
        self._client.drop_database(self._database)

        self._disconnect()

    def list_seed_identifiers(
            self,
            *,
            seed_type: Optional[SeedType] = None,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[str]:

        db_sort_order = _map_pymongo_sort_order(sort_order=sort_order)

        query = {} if seed_type is None else {"seed_type": seed_type.value}

        records = self._collection.find(query).sort("identifier",
                                                    db_sort_order)

        return tuple(map(lambda r: r['identifier'], records))

    def get_seed_identifier_by_week_offset(
            self,
            *,
            seed_type: Optional[SeedType] = None,
            offset_weeks: int = 0) -> Optional[str]:

        offset_weeks = abs(offset_weeks)

        query = {} if seed_type is None else {"seed_type": seed_type.value}

        records = self._collection.find(query).sort("identifier",
                                                    pymongo.DESCENDING)

        try:
            return records[offset_weeks]["identifier"]
        except IndexError:
            return None

    @cached(_CACHE)
    def list_seeds(
            self,
            *,
            seed_type: Optional[SeedType] = None,
            sort_order: SortOrder = SortOrder.ASCENDING) -> Tuple[RaidSeed]:

        db_sort_order = _map_pymongo_sort_order(sort_order=sort_order)

        query = {} if seed_type is None else {"seed_type": seed_type.value}

        records = self._collection.find(query).sort("identifier",
                                                    db_sort_order)

        return tuple(
            map(
                lambda r: map_to_raid_seed(data=r["data"], seed_type=seed_type
                                           ), records))

    @cached(_CACHE)
    def get_seed_by_identifier(
            self,
            *,
            identifier: str,
            seed_type: Optional[SeedType] = None) -> Optional[RaidSeed]:

        query = {
            "identifier": identifier,
        }

        if seed_type is not None:
            query["seed_type"] = seed_type.value

        record = self._collection.find_one(query)

        if record is None:
            return None

        return map_to_raid_seed(data=record["data"], seed_type=seed_type)

    def get_seed_by_week_offset(
        self,
        *,
        seed_type: Optional[SeedType] = None,
        offset_weeks: int = 0,
    ) -> Optional[RaidSeed]:

        seed_id = self.get_seed_identifier_by_week_offset(
            seed_type=seed_type, offset_weeks=offset_weeks)

        if seed_id is None:
            return None

        return self.get_seed_by_identifier(identifier=seed_id,
                                           seed_type=seed_type)

    def _save_seed(self,
                   *,
                   collection: Collection,
                   identifier: str,
                   seed_type: SeedType,
                   data: RaidSeed,
                   session=None,
                   _duplicate_ok: bool = False) -> None:

        if not is_of_seed_type(data=data, seed_type=seed_type):
            raise ValueError(f"Not a valid {seed_type.value} raid seed")

        if collection.count_documents(
            {
                "identifier": identifier,
                "seed_type": seed_type.value
            },
                session=session) > 0:

            if not _duplicate_ok:
                raise SeedDuplicateError(
                    f"Seed {identifier}.{seed_type.value} already exists")

            return

        collection.insert_one(
            {
                "identifier": identifier,
                "seed_type": seed_type.value,
                "data": map_to_native_object(data=data)
            },
            session=session)

    def save_seed(self,
                  *,
                  identifier: str,
                  seed_type: SeedType,
                  data: RaidSeed,
                  _duplicate_ok: bool = False) -> None:

        self._save_seed(collection=self._collection,
                        identifier=identifier,
                        seed_type=seed_type,
                        data=data,
                        _duplicate_ok=_duplicate_ok)

        _CACHE.clear()

    def save_seeds(self,
                   *,
                   items: Tuple[Tuple[str, SeedType, RaidSeed]],
                   _duplicate_ok: bool = False) -> None:

        def callback(session) -> None:
            collection = session.client[self._database_name][
                self._collection_name]

            for (identifier, seed_type, data) in items:
                self._save_seed(collection=collection,
                                identifier=identifier,
                                seed_type=seed_type,
                                data=data,
                                session=session,
                                _duplicate_ok=_duplicate_ok)

        with self._client.start_session() as session:
            session.with_transaction(callback=callback)

        _CACHE.clear()

    def _delete_seed(self,
                     *,
                     collection: Collection,
                     identifier: str,
                     seed_type: SeedType,
                     session=None,
                     _notfound_ok: bool = False) -> None:

        record = collection.find_one_and_delete(
            {
                "identifier": identifier,
                "seed_type": seed_type.value
            },
            session=session)

        if not _notfound_ok and record is None:
            raise SeedNotFoundError(
                f"Seed {identifier}.{seed_type.value} not found")

    def delete_seed(self,
                    *,
                    identifier: str,
                    seed_type: SeedType,
                    _notfound_ok: bool = False) -> None:

        self._delete_seed(collection=self._collection,
                          identifier=identifier,
                          seed_type=seed_type,
                          _notfound_ok=_notfound_ok)

        _CACHE.clear()

    def delete_seeds(self,
                     *,
                     items: Tuple[Tuple[str, SeedType]],
                     _notfound_ok: bool = False) -> None:

        def callback(session) -> None:
            collection = session.client[self._database_name][
                self._collection_name]

            for (identifier, seed_type) in items:
                self._delete_seed(collection=collection,
                                  identifier=identifier,
                                  seed_type=seed_type,
                                  session=session,
                                  _notfound_ok=_notfound_ok)

        with self._client.start_session() as session:
            session.with_transaction(callback=callback)

        _CACHE.clear()

    def delete_seeds_older_than(self, *, days: int) -> None:

        ids = set(self.list_seed_identifiers())
        to_delete = get_ids_older_than(ids, days)

        items = (*((seed_id, SeedType.RAW) for seed_id in to_delete),
                 *((seed_id, SeedType.ENHANCED) for seed_id in to_delete))

        self.delete_seeds(items=items)


@contextlib.contextmanager
def temp_repo(**kwargs) -> MongoSeedDataRepository:

    repo = MongoSeedDataRepository(**kwargs)

    # pylint: disable=protected-access

    try:
        yield repo
    finally:
        repo._teardown_db()
