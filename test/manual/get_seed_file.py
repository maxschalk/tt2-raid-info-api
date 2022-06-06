import requests

from src.models.Stage import Stage
from test.manual.base import make_request

result = make_request(
    method=requests.get,
    path="admin/raw_seed_file/test_data_20220220.json",
    stage=Stage.DEV
)

print(result)
