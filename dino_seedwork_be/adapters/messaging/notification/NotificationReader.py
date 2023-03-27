import json
from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from returns.maybe import Maybe

from dino_seedwork_be.media.AbstractJsonMediaReader import \
    AbstractJSONMediaReader

ValueType = TypeVar("ValueType")
DomainEventT = TypeVar("DomainEventT")
"""
    Reader for Message-Based Context Mapping 
"""

__all__ = ["NotificationReader"]


class NotificationReader(Generic[DomainEventT], AbstractJSONMediaReader):
    _event: dict

    def __init__(self, a_json_notification: str):
        notification_dict = json.loads(a_json_notification)

        self.set_event(notification_dict["event"])

    def event(self):
        return self._event

    def set_event(self, event: dict):
        self._event = event

    def event_string_value(self, path: str):
        return Maybe.from_optional(self.string_value(a_dict=self.event(), path=path))

    def event_big_decimal_value(self, path: str):
        str_val = self.string_value(a_dict=self.event(), path=path)
        return Maybe.from_optional(Decimal(str_val) if str_val is not None else None)

    def event_boolean_value(self, path: str) -> Maybe[bool]:
        return Maybe.from_optional(self.boolean_value(a_dict=self.event(), path=path))

    def event_datetime_value(self, path: str) -> Maybe[datetime]:
        return Maybe.from_optional(self.datetime_value(a_dict=self.event(), path=path))

    def event_float_value(self, path: str) -> Maybe[float]:
        return Maybe.from_optional(self.float_value(a_dict=self.event(), path=path))

    def event_int_value(self, path: str) -> Maybe[int]:
        return Maybe.from_optional(self.int_value(a_dict=self.event(), path=path))
