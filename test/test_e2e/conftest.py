import json
from test.mocks.mocks import mock_raid_raw_seed_data
from test.utils.make_request import make_request_sync
from typing import List, Tuple

import pytest
import requests
from pydantic import BaseModel
from src.models.raid_data import RaidSeedDataRaw
from src.models.Stage import Stage
from src.utils import selectors


@pytest.fixture(scope="module", autouse=True)
def posted_seeds(stage: Stage) -> List[Tuple[str, RaidSeedDataRaw]]:
    mocked_seeds = [[mock_raid_raw_seed_data() for _ in range(140)]
                    for _ in range(2)]

    posted_seeds = sorted(((
        f"raid_seed_{selectors.raid_valid_from(mocked_seed[0].dict()).strftime('%Y%m%d')}_test.json",
        list(map(BaseModel.dict, mocked_seed)))
                           for mocked_seed in mocked_seeds),
                          key=lambda t: t[0])

    for filename, seed in posted_seeds:
        response = make_request_sync(method=requests.post,
                                     path=f"admin/raw_seed_file/{filename}",
                                     data=json.dumps(seed),
                                     stage=stage,
                                     parse_response=False)

        assert response.status_code == 201

    yield posted_seeds

    for filename, _ in posted_seeds:
        response = make_request_sync(method=requests.delete,
                                     path=f"admin/raw_seed_file/{filename}",
                                     stage=stage,
                                     parse_response=False)

        assert response.status_code == 200
