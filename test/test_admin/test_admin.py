import operator
from test.utils.make_request import make_request_sync

import requests
from src.model.seed_type import SeedType
from src.stage import Stage
from src.utils.sort_order import SortOrder

# pylint: disable=duplicate-code

BASE_PATH = "admin"


def get_all_filenames_base(stage: Stage,
                           seed_type: SeedType,
                           sort_order: SortOrder = None):

    query = "" if sort_order is None else f"sort_order={sort_order.value}"

    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH}/seed_identifiers/{seed_type.value}?{query}",
        stage=stage,
        parse_response=False)

    assert response.status_code == 200

    filenames = response.json()

    assert all(isinstance(filename, str) for filename in filenames)

    assert any(filename.endswith('test') for filename in filenames) is False

    if sort_order in {None, SortOrder.ASCENDING}:
        comparison_op = operator.le
    else:
        comparison_op = operator.ge

    assert all(comparison_op(a, b) for a, b in zip(filenames, filenames[1:]))


def test_get_all_filenames(stage: Stage):
    for seed_type in SeedType:
        for sort_order in (None, *SortOrder):
            get_all_filenames_base(stage, seed_type, sort_order)
