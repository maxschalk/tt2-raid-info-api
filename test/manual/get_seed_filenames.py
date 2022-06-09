import requests

from src.models.SeedType import SeedType
from src.models.Stage import Stage
from test.utils.make_request import make_request_sync

result = make_request_sync(
    method=requests.get,
    path="admin/all_seed_filenames/raw",
    stage=Stage.DEV
)

print("RAW:", result)

result = make_request_sync(
    method=requests.get,
    path=f"admin/all_seed_filenames/{SeedType.ENHANCED.value}",
    stage=Stage.DEV
)

print("ENHANCED:", result)
