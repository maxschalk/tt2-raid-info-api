import json

import requests

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

with open(f"./test_data_20220220.json", 'r') as file:
    seed_data = json.load(file)

result = make_request_sync(
    method=requests.post,
    path="admin/raw_seed_file/test_data_20220220.json",
    data=json.dumps(seed_data),
    stage=Stage.DEV
)

print(result)
