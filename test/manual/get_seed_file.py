import requests

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="admin/raw_seed_file/test_data_20220220.json",
    stage=Stage.DEV
)

print(result)
