import json

import requests

from src.models.Stage import Stage
from test.manual.base import make_request

result = make_request(
    method=requests.get,
    path="raid_info/4/10/enhanced",
    stage=Stage.DEV
)

print(json.dumps(result, indent=2))
