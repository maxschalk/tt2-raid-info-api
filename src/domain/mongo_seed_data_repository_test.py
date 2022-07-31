import uuid
from itertools import zip_longest
from test.mocks import (mock_raid_info_enhanced, mock_raid_info_raw,
                        mock_raid_seed_enhanced, mock_raid_seed_raw,
                        mock_seed_identifier)
from test.utils.assert_deep_equals import assert_deep_equals
from typing import Optional, Tuple

import pytest
from src.domain.mongo_seed_data_repository import (MongoSeedDataRepository,
                                                   temp_repo)
from src.domain.seed_data_repository import (SeedDuplicateError,
                                             SeedNotFoundError)
from src.model.raid_data import RaidSeed
from src.model.seed_type import SeedType
from src.utils.get_env import get_env
from src.utils.sort_order import SortOrder

# pylint: disable=redefined-outer-name,duplicate-code

_REPO_INIT_KWARGS = {
    "url": get_env(key="MONGO_URL"),
    "username": get_env(key="MONGO_USERNAME"),
    "password": get_env(key="MONGO_PASSWORD"),
    "db_name": str(uuid.uuid4()),
    "coll_name": "test",
}


class TestSaveSeed:

    @staticmethod
    @pytest.fixture(scope="module")
    def repo() -> MongoSeedDataRepository:
        with temp_repo(**_REPO_INIT_KWARGS) as repo:
            yield repo

    def test_one_success(self, repo: MongoSeedDataRepository):
        cases = (
            {
                "seed": mock_raid_seed_raw(),
                "seed_type": SeedType.RAW
            },
            {
                "seed": mock_raid_seed_enhanced(),
                "seed_type": SeedType.ENHANCED
            },
        )

        def base(seed: RaidSeed, seed_type: SeedType):
            id_kwargs = {
                "identifier": mock_seed_identifier(),
                "seed_type": seed_type
            }

            repo.save_seed(data=seed, **id_kwargs)

            saved_seed = repo.get_seed_by_identifier(**id_kwargs)

            assert_deep_equals(seed, saved_seed)

            repo.delete_seed(**id_kwargs)

        for case in cases:
            base(**case)

    def test_one_duplicate(self, repo: MongoSeedDataRepository):
        identifier = mock_seed_identifier()

        seed_raw = mock_raid_seed_raw()
        seed_enhanced = mock_raid_seed_enhanced()

        cases = (({
            "seed": seed_raw,
            "identifier": identifier,
            "seed_type": SeedType.RAW,
        }, {
            "seed": seed_raw,
            "identifier": str(uuid.uuid4()),
            "seed_type": SeedType.RAW
        }, {
            "seed": seed_enhanced,
            "identifier": identifier,
            "seed_type": SeedType.ENHANCED
        }), ({
            "seed": seed_enhanced,
            "identifier": identifier,
            "seed_type": SeedType.ENHANCED
        }, {
            "seed": seed_enhanced,
            "identifier": str(uuid.uuid4()),
            "seed_type": SeedType.ENHANCED
        }, {
            "seed": seed_raw,
            "identifier": identifier,
            "seed_type": SeedType.RAW
        }))

        for case in cases:
            initial, *others = case

            seed = initial.pop("seed")

            try:
                repo.save_seed(data=seed, **initial)

                full_id = f"{initial['identifier']}.{initial['seed_type'].value}"

                with pytest.raises(SeedDuplicateError, match=full_id):
                    repo.save_seed(data=seed, **initial)

                for other in others:
                    other_seed = other.pop("seed")

                    try:
                        repo.save_seed(data=other_seed, **other)
                    finally:
                        repo.delete_seed(**other)

            finally:
                repo.delete_seed(**initial)

    def test_one_invalid(self, repo: MongoSeedDataRepository):

        raid_info_raw = mock_raid_info_raw()
        raid_info_enhanced = mock_raid_info_enhanced()

        cases = (
            (SeedType.RAW, "invalid"),
            (SeedType.RAW, [raid_info_raw, "invalid"]),
            (SeedType.RAW, [raid_info_raw, raid_info_enhanced]),
            (SeedType.RAW, mock_raid_seed_enhanced()),
            (SeedType.ENHANCED, "invalid"),
            (SeedType.ENHANCED, [raid_info_enhanced, raid_info_raw]),
            (SeedType.ENHANCED, mock_raid_seed_raw()),
        )

        for seed_type, seed in cases:
            id_kwargs = {
                "identifier": mock_seed_identifier(),
                "seed_type": seed_type,
            }

            with pytest.raises(ValueError, match=seed_type.value):
                repo.save_seed(data=seed, **id_kwargs)

    def test_multiple_success(self, repo: MongoSeedDataRepository):

        cases = (
            {
                "seeds": tuple(mock_raid_seed_raw() for _ in range(3)),
                "ids": tuple(mock_seed_identifier() for _ in range(3)),
                "seed_types": tuple([SeedType.RAW] * 3)
            },
            {
                "seeds": tuple(mock_raid_seed_enhanced() for _ in range(3)),
                "ids": tuple(mock_seed_identifier() for _ in range(3)),
                "seed_types": tuple([SeedType.ENHANCED] * 3)
            },
        )

        def base(seeds: Tuple[RaidSeed], ids: Tuple[str],
                 seed_types: Tuple[SeedType]):
            items = zip(ids, seed_types, seeds)

            repo.save_seeds(items=items)

            for (identifier, seed_type, seed) in items:
                saved_seed = repo.get_seed_by_identifier(identifier=identifier,
                                                         seed_type=seed_type)

                assert_deep_equals(seed, saved_seed)

            repo.delete_seeds(items=zip(ids, seed_types))

        for case in cases:
            base(**case)

    def test_multiple_duplicate(self, repo: MongoSeedDataRepository):

        cases = (
            {
                "seeds":
                tuple(mock_raid_seed_raw() for _ in range(5)),
                "ids": ("duplicate", *(mock_seed_identifier()
                                       for _ in range(3)), "duplicate"),
                "seed_types": (SeedType.RAW, ) * 5
            },
            {
                "seeds":
                tuple(mock_raid_seed_enhanced() for _ in range(5)),
                "ids": ("duplicate", *(mock_seed_identifier()
                                       for _ in range(3)), "duplicate"),
                "seed_types": (SeedType.ENHANCED, ) * 5
            },
        )

        def base(seeds: Tuple[RaidSeed], ids: Tuple[str],
                 seed_types: Tuple[SeedType]):

            number_seeds_before = len(repo.list_seed_identifiers())

            items = zip(ids, seed_types, seeds)

            with pytest.raises(SeedDuplicateError, match="duplicate"):
                repo.save_seeds(items=items)

            number_seeds_after = len(repo.list_seed_identifiers())

            assert number_seeds_before == number_seeds_after

            for (identifier, seed_type, _) in items:
                saved_seed = repo.get_seed_by_identifier(identifier=identifier,
                                                         seed_type=seed_type)

                assert saved_seed is None

        for case in cases:
            base(**case)

    def test_multiple_invalid(self, repo: MongoSeedDataRepository):

        cases = (
            {
                "seeds": (mock_raid_seed_raw(), "invalid"),
                "ids": (mock_seed_identifier(), mock_seed_identifier()),
                "seed_types": (SeedType.RAW, ) * 2
            },
            {
                "seeds": (mock_raid_seed_enhanced(), "invalid"),
                "ids": (mock_seed_identifier(), mock_seed_identifier()),
                "seed_types": (SeedType.ENHANCED, ) * 2
            },
            {
                "seeds": (mock_raid_seed_raw(), mock_raid_seed_enhanced()),
                "ids": (mock_seed_identifier(), mock_seed_identifier()),
                "seed_types": (SeedType.RAW, ) * 2
            },
            {
                "seeds": (mock_raid_seed_enhanced(), mock_raid_seed_raw()),
                "ids": (mock_seed_identifier(), mock_seed_identifier()),
                "seed_types": (SeedType.ENHANCED, ) * 2
            },
        )

        def base(seeds: Tuple[RaidSeed], ids: Tuple[str],
                 seed_types: Tuple[SeedType]):

            number_seeds_before = len(repo.list_seed_identifiers())

            items = zip(ids, seed_types, seeds)

            with pytest.raises(ValueError):
                repo.save_seeds(items=items)

            number_seeds_after = len(repo.list_seed_identifiers())

            assert number_seeds_before == number_seeds_after

            for (identifier, seed_type, _) in items:
                saved_seed = repo.get_seed_by_identifier(identifier=identifier,
                                                         seed_type=seed_type)

                assert saved_seed is None

        for case in cases:
            base(**case)


class TestSeedIdentifiers:

    @staticmethod
    @pytest.fixture(scope="module")
    def repo() -> MongoSeedDataRepository:
        with temp_repo(**_REPO_INIT_KWARGS) as repo:
            yield repo

    _seeds = (
        *(mock_raid_seed_raw() for _ in range(2)),
        *(mock_raid_seed_enhanced() for _ in range(2)),
    )

    _seed_types = (
        *(SeedType.RAW for _ in range(2)),
        *(SeedType.ENHANCED for _ in range(2)),
    )

    _ids = tuple(mock_seed_identifier() for _ in range(4))

    items = tuple(zip(_ids, _seed_types, _seeds))

    @pytest.fixture(autouse=True)
    def seeds(self, repo: MongoSeedDataRepository) -> Tuple[RaidSeed]:

        repo.save_seeds(items=self.items)

        try:
            yield
        finally:
            repo.delete_seeds(items=zip(self._ids, self._seed_types))

    def test_list_seed_identifiers(self, repo: MongoSeedDataRepository):

        def base(seed_type: SeedType):
            saved_ids = repo.list_seed_identifiers(seed_type=seed_type)

            items = self.items
            if seed_type is not None:
                items = filter(lambda i: i[1] == seed_type, self.items)

            ids = tuple(map(lambda i: i[0], items))

            assert len(saved_ids) == len(set(saved_ids))
            assert len(ids) == len(set(ids))

            assert set(saved_ids) == set(ids)

        for seed_type in (None, *SeedType):
            base(seed_type=seed_type)

    def test_list_seed_identifiers_sorted_default(
            self, repo: MongoSeedDataRepository):
        saved_ids = repo.list_seed_identifiers()

        assert all(a < b for a, b in zip(saved_ids, saved_ids[1:]))

    def test_list_seed_identifiers_sorted_ascending(
            self, repo: MongoSeedDataRepository):
        saved_ids = repo.list_seed_identifiers(sort_order=SortOrder.ASCENDING)

        assert all(a < b for a, b in zip(saved_ids, saved_ids[1:]))

    def test_list_seed_identifiers_sorted_descending(
            self, repo: MongoSeedDataRepository):
        saved_ids = repo.list_seed_identifiers(sort_order=SortOrder.DESCENDING)

        assert all(a > b for a, b in zip(saved_ids, saved_ids[1:]))

    def test_get_seed_identifier_by_week_offset(self,
                                                repo: MongoSeedDataRepository):

        def base(seed_type: SeedType):

            items = self.items
            if seed_type is not None:
                items = filter(lambda i: i[1] == seed_type, self.items)

            ids = map(lambda i: i[0], items)

            for i, sid in enumerate(ids):
                saved_id = repo.get_seed_identifier_by_week_offset(
                    seed_type=seed_type, offset_weeks=i)

                assert saved_id == sid

        for seed_type in (None, *SeedType):
            base(seed_type=seed_type)


class TestSeeds:

    @staticmethod
    @pytest.fixture(scope="module")
    def repo() -> MongoSeedDataRepository:
        with temp_repo(**_REPO_INIT_KWARGS) as repo:
            yield repo

    _ids = tuple(mock_seed_identifier() for _ in range(4))

    _seeds = (
        *(mock_raid_seed_raw() for _ in range(2)),
        *(mock_raid_seed_enhanced() for _ in range(2)),
    )

    _seed_types = (
        *(SeedType.RAW for _ in range(2)),
        *(SeedType.ENHANCED for _ in range(2)),
    )

    items = tuple(zip(_ids, _seed_types, _seeds))

    @pytest.fixture(autouse=True)
    def seeds(self, repo: MongoSeedDataRepository) -> Tuple[RaidSeed]:

        repo.save_seeds(items=self.items)

        try:
            yield
        finally:
            repo.delete_seeds(items=zip(self._ids, self._seed_types))

    def test_list_seeds(self, repo: MongoSeedDataRepository):

        def base(seed_type: Optional[SeedType],
                 sort_order: Optional[SortOrder]):
            kwargs = {}

            if seed_type:
                kwargs["seed_type"] = seed_type

            if sort_order:
                kwargs["sort_order"] = sort_order

            items = self.items
            if seed_type is not None:
                items = filter(lambda i: i[1] == seed_type, self.items)

            seeds = tuple(map(lambda i: i[2], items))

            saved_seeds = repo.list_seeds(**kwargs)

            test_sort = tuple(
                map(lambda s: s[0].raid_info_valid_from, saved_seeds))
            if sort_order in {None, SortOrder.ASCENDING}:
                assert all(a < b for a, b in zip(test_sort, test_sort[1:]))
            else:
                assert all(a > b for a, b in zip(test_sort, test_sort[1:]))

            seeds = sorted(seeds, key=lambda s: s[0].raid_info_valid_from)
            saved_seeds = sorted(saved_seeds,
                                 key=lambda s: s[0].raid_info_valid_from)

            for seed1, seed2 in zip_longest(seeds, saved_seeds):
                assert seed1 == seed2

        for seed_type in (None, *SeedType):
            for sort_order in (None, *SortOrder):
                base(seed_type=seed_type, sort_order=sort_order)

    def test_get_seed_by_identifier_nonexistent(self,
                                                repo: MongoSeedDataRepository):
        result = repo.get_seed_by_identifier(identifier="doesnotexist",
                                             seed_type=SeedType.RAW)

        assert result is None

        result = repo.get_seed_by_identifier(identifier="doesnotexist",
                                             seed_type=SeedType.ENHANCED)

        assert result is None

    def test_get_seed_by_identifier(self, repo: MongoSeedDataRepository):
        for (seed_id, seed_type, seed) in self.items:
            saved_seed = repo.get_seed_by_identifier(identifier=seed_id,
                                                     seed_type=seed_type)

            assert saved_seed == seed

    def test_get_seed_by_week_offset_nonexistent(
            self, repo: MongoSeedDataRepository):

        result = repo.get_seed_by_week_offset(offset_weeks=len(self.items))
        assert result is None

        result = repo.get_seed_by_week_offset(seed_type=SeedType.RAW,
                                              offset_weeks=len(self.items) //
                                              2)
        assert result is None

        result = repo.get_seed_by_week_offset(seed_type=SeedType.ENHANCED,
                                              offset_weeks=len(self.items))
        assert result is None

    def test_get_seed_by_week_offset(self, repo: MongoSeedDataRepository):

        def base(seed_type: SeedType):

            items = self.items
            if seed_type is not None:
                items = filter(lambda i: i[1] == seed_type, self.items)

            seeds = map(lambda i: i[2], items)

            for i, seed in enumerate(seeds):
                saved_seed = repo.get_seed_by_week_offset(seed_type=seed_type,
                                                          offset_weeks=i)

                assert saved_seed == seed

        for seed_type in (None, *SeedType):
            base(seed_type=seed_type)


class TestDeleteSeed:

    @staticmethod
    @pytest.fixture(scope="module")
    def repo() -> MongoSeedDataRepository:
        with temp_repo(**_REPO_INIT_KWARGS) as repo:
            yield repo

    _ids = tuple(mock_seed_identifier() for _ in range(4))

    _seeds = (
        *(mock_raid_seed_raw() for _ in range(2)),
        *(mock_raid_seed_enhanced() for _ in range(2)),
    )

    _seed_types = (
        *(SeedType.RAW for _ in range(2)),
        *(SeedType.ENHANCED for _ in range(2)),
    )

    items = tuple(zip(_ids, _seed_types, _seeds))

    @pytest.fixture(autouse=True)
    def seeds(self, repo: MongoSeedDataRepository) -> Tuple[RaidSeed]:

        repo.save_seeds(items=self.items, _duplicate_ok=True)

        try:
            yield
        finally:
            items = zip(self._ids, self._seed_types)
            repo.delete_seeds(items=items, _notfound_ok=True)

    def test_one_success(self, repo: MongoSeedDataRepository):

        def base(identifier: str, seed_type: SeedType):
            id_kwargs = {"identifier": identifier, "seed_type": seed_type}

            repo.delete_seed(**id_kwargs)

            saved_seed = repo.get_seed_by_identifier(**id_kwargs)

            assert saved_seed is None

        for (seed_id, seed_type, _) in self.items:
            base(identifier=seed_id, seed_type=seed_type)

    def test_one_notfound(self, repo: MongoSeedDataRepository):
        (seed_id, seed_type, _) = self.items[0]

        id_kwargs = {"identifier": seed_id, "seed_type": seed_type}

        repo.delete_seed(**id_kwargs)

        full_id = f"{seed_id}.{seed_type.value}"
        with pytest.raises(SeedNotFoundError, match=full_id):
            repo.delete_seed(**id_kwargs)

    def test_one_invalid(self, repo: MongoSeedDataRepository):

        full_id = f"doesnotexist.{SeedType.RAW.value}"

        with pytest.raises(SeedNotFoundError, match=full_id):
            repo.delete_seed(identifier="doesnotexist", seed_type=SeedType.RAW)

    def test_multiple_success(self, repo: MongoSeedDataRepository):
        repo.delete_seeds(items=zip(self._ids, self._seed_types))

        for (seed_id, seed_type, _) in self.items:

            saved_seed = repo.get_seed_by_identifier(identifier=seed_id,
                                                     seed_type=seed_type)

            assert saved_seed is None

    def test_multiple_duplicate(self, repo: MongoSeedDataRepository):

        _ids = (*self._ids, self._ids[0])
        _seed_types = (*self._seed_types, self._seed_types[0])

        full_id = f"{_ids[-1]}.{_seed_types[-1].value}"
        with pytest.raises(SeedNotFoundError, match=full_id):
            repo.delete_seeds(items=zip(_ids, _seed_types))

        for (seed_id, seed_type, _) in self.items:

            saved_seed = repo.get_seed_by_identifier(identifier=seed_id,
                                                     seed_type=seed_type)

            assert saved_seed is not None

    def test_multiple_notfound(self, repo: MongoSeedDataRepository):

        _ids = (*self._ids, "doesnotexist")
        _seed_types = (*self._seed_types, SeedType.RAW)

        full_id = f"doesnotexist.{SeedType.RAW.value}"
        with pytest.raises(SeedNotFoundError, match=full_id):
            repo.delete_seeds(items=zip(_ids, _seed_types))

        for (seed_id, seed_type, _) in self.items:

            saved_seed = repo.get_seed_by_identifier(identifier=seed_id,
                                                     seed_type=seed_type)

            assert saved_seed is not None
