import json


def temp_deepcopy(obj):
    return json.loads(json.dumps(obj))
