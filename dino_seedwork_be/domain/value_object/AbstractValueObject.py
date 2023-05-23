from datetime import datetime

from returns.maybe import Maybe, Nothing

from dino_seedwork_be.utils.date import now_utc

from ..DomainAssertionConcern import DomainAssertionConcern

# __all__ = ["ValueObject"]


class ValueObject(DomainAssertionConcern):
    """
    Base class for value objects
    """

    _created_at: datetime

    def __init__(self, created_at: Maybe[datetime] = Nothing) -> None:
        self._created_at = created_at.value_or(now_utc())
        super().__init__()
