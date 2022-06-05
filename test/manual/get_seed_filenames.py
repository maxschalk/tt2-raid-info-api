import requests

from test.manual.base import make_request

result = make_request(requests.get, "admin/all_raw_seed_filenames")

print("RAW:", result)

result = make_request(requests.get, "admin/all_enhanced_seed_filenames")

print("ENHANCED:", result)
