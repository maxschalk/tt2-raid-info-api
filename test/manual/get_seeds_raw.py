import requests

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="seeds/all/raw",
    stage=Stage.DEV
)

print(len(result))
