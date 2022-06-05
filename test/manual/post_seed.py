import json

import requests

from test.manual.base import make_request

with open(f"./test_data_20220220.json", 'r') as file:
    seed_data = json.load(file)

file_data = {
    "data": seed_data
}

result = make_request(
    requests.post,
    "admin/add_raw_seed_file/test_data_20220220.json",
    data=json.dumps(file_data)
)

print(result)
