from datetime import datetime, timezone
from typing import Optional


def to_iso_format(aDateTime: Optional[datetime]):
    return aDateTime.isoformat() if aDateTime is not None else None


def now_utc():
    return datetime.now(timezone.utc)
