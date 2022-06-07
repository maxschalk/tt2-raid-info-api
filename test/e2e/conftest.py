import os

import pytest
from dotenv import load_dotenv

from src.models.Stage import Stage

load_dotenv()


@pytest.fixture(scope="module", autouse=True)
def stage() -> Stage:
    return Stage(os.getenv("STAGE"))


# @pytest.fixture(scope="module", autouse=True)
# def seeds(stage: Stage) -> List[RaidRawSeedData]:
#     mocked_seeds = [[mock_raid_raw_seed_data() for _ in range(140)] for _ in range(3)]
#
#     seeds = sorted(
#         (
#             (
#                 f"test_raid_seed_data_{mocked_seed[0].raid_info_valid_from.split('T')[0]}.json",
#                 list(map(BaseModel.dict, mocked_seed))
#             )
#             for mocked_seed in mocked_seeds
#         )
#         , key=lambda t: t[0]
#     )
#
#     for filename, seed in seeds:
#         response = make_request_sync(
#             method=requests.post,
#             path=f"admin/raw_seed_file/{filename}",
#             data=json.dumps(seed),
#             stage=stage
#         )
#
#     yield seeds
#
#     for filename, _ in seeds:
#         make_request_sync(
#             method=requests.delete,
#             path=f"admin/raw_seed_file/{filename}",
#             stage=stage
#         )
