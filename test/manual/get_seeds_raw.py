from test.utils.make_request import make_request_sync

import requests
from src.domain.seed_type import SeedType
from src.domain.stage import Stage

result = make_request_sync(method=requests.get,
                           path=f"seeds/all/{SeedType.RAW.value}",
                           stage=Stage.DEV)

print(len(result))
