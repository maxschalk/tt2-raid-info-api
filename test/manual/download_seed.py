import json

import requests
from requests import Response

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="admin/seed_file/raid_seed_20220626.json",
    stage=Stage.DEV,
)

print(result)
