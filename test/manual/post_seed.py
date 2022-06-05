import json

import requests

from test.manual.base import make_request

with open(f"./raid_seed_20220220.json", 'r') as file:
    seed_data = json.load(file)

file_data = {
    "file": {
        "filename": "raid_seed_20220220"
    },
    "data": seed_data
}

result = make_request(requests.post, "admin/add_seed", data=json.dumps(file_data))

print(result)
