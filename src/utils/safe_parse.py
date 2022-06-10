from datetime import datetime
from typing import Optional, Callable, Any


def _safe_parse_base(from_str: str, constructor: Callable, default: Any = None) -> Optional[Any]:
    if type(from_str) is not str:
        return default

    try:
        return constructor(from_str)
    except (ValueError, TypeError):
        return default


def safe_parse_datetime(from_str: str, default: datetime = None) -> Optional[datetime]:
    if type(from_str) == datetime:
        return from_str

    return _safe_parse_base(from_str, datetime.fromisoformat, default)


def safe_parse_int(from_str: str, default: int = None) -> Optional[int]:
    if type(from_str) == int:
        return from_str

    return _safe_parse_base(from_str, int, default)


def safe_parse_float(from_str: str, default: float = None) -> Optional[float]:
    if type(from_str) == float:
        return from_str

    return _safe_parse_base(from_str, float, default)
