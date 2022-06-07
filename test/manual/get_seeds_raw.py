import requests

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="seeds/most_recent/raw",
    stage=Stage.DEV
)

print(result[0]["raid_info_valid_from"])
