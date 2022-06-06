import requests

from src.models.Stage import Stage
from src.utils.make_request import make_request

result = make_request(
    method=requests.get,
    path="admin/all_seed_filenames/raw",
    stage=Stage.DEV
)

print("RAW:", result)

result = make_request(
    method=requests.get,
    path="admin/all_seed_filenames/enhanced",
    stage=Stage.DEV
)

print("ENHANCED:", result)
