from datetime import datetime, timezone
from typing import Optional

__all__ = ["to_iso_format", "now_utc"]


def to_iso_format(aDateTime: Optional[datetime]):
    return aDateTime.isoformat() if aDateTime is not None else None


def now_utc():
    return datetime.now(timezone.utc)
