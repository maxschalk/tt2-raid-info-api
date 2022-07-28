from test.utils.make_request import make_request_sync

import requests
from src.domain.stage import Stage

result = make_request_sync(method=requests.get,
                           path="seeds/raw/recent",
                           stage=Stage.PRODUCTION)

print(result[0])
