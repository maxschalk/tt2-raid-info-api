import json
from test.utils.make_request import make_request_sync

import requests
from src.model.seed_type import SeedType
from src.stage import Stage

result = make_request_sync(method=requests.get,
                           path=f"raid_info/{SeedType.ENHANCED.value}/4/10",
                           stage=Stage.DEV)

print(json.dumps(result, indent=2))
