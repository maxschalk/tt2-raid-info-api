import requests

from src.models.Stage import Stage
from src.utils.make_request import make_request

result = make_request(
    method=requests.delete,
    path="admin/raw_seed_file/test_data_20220220.json",
    stage=Stage.DEV
)

print(result)
