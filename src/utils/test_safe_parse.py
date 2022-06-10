from src.utils.safe_parse import *
from datetime import datetime

dt_default = datetime(1970, 1, 1, 0, 0, 0)
dt_str_default = dt_default.isoformat()

dt_valid = datetime(2022, 1, 1, 12, 42, 30)
dt_str_valid = dt_valid.isoformat()

CASES_DATETIME = (
    ({"from_str": dt_str_valid}, dt_valid),

    ({"from_str": dt_str_valid, "default": dt_default}, dt_valid),

    ({"from_str": "2022-13-01T12:42:30"}, None),
    ({"from_str": "2022-01-40T12:42:30"}, None),
    ({"from_str": "2022-01-0112:42:30"}, None),
    ({"from_str": "2022-01-01T25:42:30"}, None),
    ({"from_str": "2022-01-01T12:70:30"}, None),
    ({"from_str": True}, None),
    ({"from_str": 420}, None),
    ({"from_str": "some string"}, None),
    ({"from_str": [1, 2, 3]}, None),

    ({"from_str": "2022-13-01T12:42:30", "default": dt_default}, dt_default),
    ({"from_str": "2022-01-40T12:42:30", "default": dt_default}, dt_default),
    ({"from_str": "2022-01-0112:42:30", "default": dt_default}, dt_default),
    ({"from_str": "2022-01-01T25:42:30", "default": dt_default}, dt_default),
    ({"from_str": "2022-01-01T12:70:30", "default": dt_default}, dt_default),
    ({"from_str": "2022-01-01T12:42:70", "default": dt_default}, dt_default),
    ({"from_str": True, "default": dt_default}, dt_default),
    ({"from_str": 420, "default": dt_default}, dt_default),
    ({"from_str": "some string", "default": dt_default}, dt_default),
    ({"from_str": [1, 2, 3], "default": dt_default}, dt_default),
)


def test_safe_parse_datetime():
    for case in CASES_DATETIME:
        args, output = case

        assert safe_parse_datetime(**args) == output


CASES_INT = (
    ({"from_str": "42"}, 42),

    ({"from_str": "42", "default": 10}, 42),

    ({"from_str": "42.10"}, None),
    ({"from_str": "42,510"}, None),
    ({"from_str": True}, None),
    ({"from_str": 420}, 420),
    ({"from_str": "some string"}, None),
    ({"from_str": [1, 2, 3]}, None),

    ({"from_str": "42,510", "default": 10}, 10),
    ({"from_str": True, "default": 10}, 10),
    ({"from_str": "some string", "default": 10}, 10),
    ({"from_str": [1, 2, 3], "default": 10}, 10),
)


def test_safe_parse_int():
    for case in CASES_INT:
        args, output = case

        assert safe_parse_int(**args) == output


CASES_FLOAT = (
    ({"from_str": "0"}, 0.0),
    ({"from_str": "42"}, 42.0),
    ({"from_str": "42.10"}, 42.1),

    ({"from_str": "0", "default": 10.0}, 0.0),
    ({"from_str": "42", "default": 10.0}, 42.0),
    ({"from_str": "42.10", "default": 10.0}, 42.1),

    ({"from_str": "42,510"}, None),
    ({"from_str": True}, None),
    ({"from_str": 420}, None),
    ({"from_str": "some string"}, None),
    ({"from_str": [1, 2, 3]}, None),

    ({"from_str": "42,10", "default": 10.0}, 10.0),
    ({"from_str": True, "default": 10.0}, 10.0),
    ({"from_str": 420, "default": 10.0}, 10.0),
    ({"from_str": "some string", "default": 10.0}, 10.0),
    ({"from_str": [1, 2, 3], "default": 10.0}, 10.0),
)


def test_safe_parse_float():
    for case in CASES_FLOAT:
        args, output = case

        assert safe_parse_float(**args) == output
