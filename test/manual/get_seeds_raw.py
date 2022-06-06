import requests

from src.models.Stage import Stage
from src.utils.make_request import make_request

result = make_request(
    method=requests.get,
    path="seeds/most_recent/raw",
    stage=Stage.DEV
)

print(result[0]["raid_info_valid_from"])