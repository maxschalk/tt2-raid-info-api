import json
from test.mocks.mocks import mock_raid_info_raw
from test.utils.make_request import make_request_sync
from typing import List, Tuple

import pytest
import requests
# pylint: disable=no-name-in-module
from pydantic import BaseModel
from src.model.raid_data import RaidInfoRaw
from src.stage import Stage
from src.utils import selectors


@pytest.fixture(scope="module", autouse=True)
def posted_seeds(stage: Stage) -> List[Tuple[str, RaidInfoRaw]]:
    mocked_seeds = [[mock_raid_info_raw() for _ in range(140)]
                    for _ in range(2)]

    def filename_from_seed(seed):
        valid_from = selectors.raid_valid_from(seed[0].dict())

        return f"raid_seed_{valid_from.strftime('%Y%m%d')}_test.json"

    def seed_to_dict(seed):
        return list(map(BaseModel.dict, seed))

    seeds_posted = sorted(((filename_from_seed(seed), seed_to_dict(seed))
                           for seed in mocked_seeds),
                          key=lambda t: t[0])

    for filename, seed in seeds_posted:
        response = make_request_sync(method=requests.post,
                                     path=f"admin/save/{filename}",
                                     data=json.dumps(seed),
                                     stage=stage,
                                     parse_response=False)

        assert response.status_code == 201

    yield seeds_posted

    for filename, _ in seeds_posted:
        response = make_request_sync(method=requests.delete,
                                     path=f"admin/delete/{filename}",
                                     stage=stage,
                                     parse_response=False)

        assert response.status_code == 200
