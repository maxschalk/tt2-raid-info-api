import operator

import requests

from src.models.SeedType import SeedType
from src.models.SortOrder import SortOrder
from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

BASE_PATH = "admin"


def get_all_filenames_base(stage: Stage,
                           seed_type: SeedType,
                           sort_order: SortOrder = None):
    qs = "" if sort_order is None else f"?sort_order={sort_order.value}"

    response = make_request_sync(
        method=requests.get,
        path=f"{BASE_PATH}/all_seed_filenames/{seed_type.value}{qs}",
        stage=stage,
        parse_response=False)

    assert response.status_code == 200

    filenames = response.json()

    assert all(type(filename) is str for filename in filenames)

    assert any(filename.endswith('test') for filename in filenames) is False

    if sort_order in {None, SortOrder.ASCENDING}:
        op = operator.le
    else:
        op = operator.ge

    assert all(op(a, b) for a, b in zip(filenames, filenames[1:]))


def test_get_all_filenames(stage: Stage):
    for seed_type in SeedType:
        for sort_order in (None, *SortOrder):
            get_all_filenames_base(stage, seed_type, sort_order)
