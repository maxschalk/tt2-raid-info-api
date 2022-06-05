import requests

from test.manual.base import make_request

result = make_request(
    requests.get,
    "admin/download_raw_seed_file/test_data_20220220.json"
)

print(result)
