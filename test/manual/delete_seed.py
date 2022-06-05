import json

import requests

from test.manual.base import make_request

file_data = {
    "filename": "test_data"
}

result = make_request(requests.delete, "admin/delete_seed", data=json.dumps(file_data))

print(result)
