from datetime import datetime
from typing import Optional, Callable, Any


def _safe_parse_base(from_str: str, constructor: Callable, default: Any = None) -> Optional[Any]:
    return constructor(from_str) if from_str else default


def safe_parse_datetime(from_str: str) -> Optional[datetime]:
    return _safe_parse_base(from_str, datetime.fromisoformat)


def safe_parse_int(from_str: str) -> Optional[int]:
    return _safe_parse_base(from_str, int)


def safe_parse_float(from_str: str) -> Optional[float]:
    return _safe_parse_base(from_str, float)
