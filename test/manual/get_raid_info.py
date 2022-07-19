import json

import requests

from src.models.SeedType import SeedType
from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(method=requests.get,
                           path=f"raid_info/{SeedType.ENHANCED.value}/4/10",
                           stage=Stage.DEV)

print(json.dumps(result, indent=2))
