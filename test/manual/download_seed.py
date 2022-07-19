from test.utils.make_request import make_request_sync

import requests
from src.domain.stage import Stage

result = make_request_sync(
    method=requests.get,
    path="admin/seed_file/raid_seed_20220626.json",
    stage=Stage.DEV,
)

print(result)
