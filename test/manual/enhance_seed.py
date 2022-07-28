import json
from test.utils.make_request import make_request_sync

import requests
from src.stage import Stage

with open("./test/manual/test_data_20220220.json", mode='r',
          encoding='utf-8') as file:
    seed_data = json.load(file)

result = make_request_sync(method=requests.post,
                           path="admin/enhance_seed?download=true",
                           data=json.dumps(seed_data),
                           stage=Stage.DEV)

print(result)
