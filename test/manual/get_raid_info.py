import json

import requests

from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="raid_info/4/10/enhanced",
    stage=Stage.DEV
)

print(json.dumps(result, indent=2))
