from test.utils.make_request import make_request_sync

import requests
from src.stage import Stage

result = make_request_sync(method=requests.delete,
                           path="admin/raw_seed_file/test_data_20220220.json",
                           stage=Stage.STAGING)

print(result)
