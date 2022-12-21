from datetime import datetime
from typing import Any, Generic, TypeVar

from returns.pipeline import flow
from returns.pointfree import bind
from returns.result import Failure, Result, Success, safe

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.logic.assertion_concern import AssertionConcern
from dino_seedwork_be.serializer.Serializable import JSONSerializable
from dino_seedwork_be.utils.functional import return_v


class DomainEventSerializable(DomainEvent, JSONSerializable):
    pass


DomainEventT = TypeVar("DomainEventT", bound=DomainEvent)


class Notification(Generic[DomainEventT], JSONSerializable, AssertionConcern):
    _event: DomainEventT
    _id: int
    _occurred_on: datetime
    _type_name: str
    _version: int = 0

    def __init__(self, a_num_id: int, event: DomainEventT):
        self.set_id(a_num_id)
        self.set_domain_event(event)
        self.set_occurred_on(event.occurred_on())
        self.set_type_name(event.type())
        self.set_version(event.version())

    @safe
    @staticmethod
    def factory(a_num_id: int, event: DomainEventT):
        return Notification(a_num_id, event)

    def set_domain_event(self, event: DomainEventT):
        self.assert_argument_not_null(event, a_message="Event must be specified")
        self._event = event

    def set_id(self, a_num_id: int):
        self.assert_argument_not_null(
            a_num_id, a_message="Notification id cannot be null"
        )
        self._id = a_num_id

    def set_version(self, a_version: int):
        self._version = a_version

    def set_type_name(self, a_type_name: str) -> Result[None, Any]:
        assert_result = flow(
            self.assert_argument_not_empty(
                a_type_name, a_message="The type name cannot be empty"
            ),
            bind(
                return_v(
                    self.assert_argument_length(
                        a_type_name,
                        a_maximum=100,
                        a_minimum=0,
                        a_message="The type name must be 100 characters or less",
                    )
                )
            ),
        )
        match assert_result:
            case Failure(_):
                return assert_result
            case _:
                self._type_name = a_type_name
                return Success(None)

    def set_occurred_on(self, anOccurredOn: datetime):
        self._occurred_on = anOccurredOn

    def type_name(self) -> str:
        return self._type_name

    def version(self) -> int:
        return self._version

    def occurred_on(self) -> datetime:
        return self._occurred_on

    def id(self) -> int:
        return self._id

    def event(self) -> DomainEvent:
        return self._event

    @staticmethod
    def restore(a_dict: dict) -> "Notification":
        event = a_dict["event"]
        return Notification(a_num_id=a_dict["id"], event=DomainEvent.restore(event))

    def as_dict(self) -> dict:
        return {"id": self.id(), "event": self.event().as_dict()}
