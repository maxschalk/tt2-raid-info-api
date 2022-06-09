import json

import requests
from requests import Response

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="admin/raw_seed_file/raid_seed_20220522.json",
    stage=Stage.DEV,
)

print(result)
