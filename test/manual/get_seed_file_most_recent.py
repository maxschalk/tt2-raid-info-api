import requests

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="seeds/raw/recent",
    stage=Stage.PRODUCTION
)

print(result[0])
