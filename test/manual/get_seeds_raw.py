import requests

from src.models.SeedType import SeedType
from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path=f"seeds/all/{SeedType.RAW.value}",
    stage=Stage.DEV
)

print(len(result))
