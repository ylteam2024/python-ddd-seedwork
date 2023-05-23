from datetime import datetime
from typing import Any, Optional

from returns.maybe import Maybe, Nothing, Some
from returns.result import Result

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.logic.assertion_concern import AssertionConcern

from .EventSerializer import EventSerializer

# __all__ = ["StoredEvent"]


class StoredEvent(AssertionConcern):
    _body: str
    _id: Maybe[int]
    _occurred_on: datetime
    _type_name: str

    def __init__(
        self,
        body: str,
        occurred_on: datetime,
        type_name: str,
        id: Maybe[int] = Nothing,
    ) -> None:
        self.set_body(body)
        match id:
            case int():
                self.set_id(id)
        self.set_occurred_on(occurred_on)
        self.set_type_name(type_name)

    @staticmethod
    def factory(
        body: str, occurred_on: datetime, type_name: str, id: Maybe[int] = Nothing
    ):
        return StoredEvent(body, occurred_on, type_name, id)

    def set_body(self, an_event_body: str):
        self.assert_argument_not_null(
            an_event_body, a_message=Some("Event body cannot be empty")
        )
        self.assert_argument_range(
            len(an_event_body),
            a_minium=1,
            a_maximum=65000,
            a_message=Some("The event body must be 65000 character or less"),
        )
        self._body = an_event_body

    def set_id(self, an_id: int):
        self._id = Some(an_id)

    def set_occurred_on(self, a_datetime: datetime):
        self._occurred_on = a_datetime

    def set_type_name(self, a_type_name: str):
        self.assert_argument_not_empty(
            Some(a_type_name), Some("The event type name is required")
        )
        self.assert_argument_length(
            a_type_name,
            a_minimum=1,
            a_maximum=100,
            a_message=Some("The event type name must be 100 characters or less"),
        )
        self._type_name = a_type_name

    def id(self) -> Maybe[int]:
        return self._id

    def body(self) -> str:
        return self._body

    def type_name(self) -> str:
        return self._type_name

    def occurred_on(self) -> datetime:
        return self._occurred_on

    def to_domain_event(self) -> Result[DomainEvent, Any]:
        return EventSerializer.instance().deserialize(self.body())
