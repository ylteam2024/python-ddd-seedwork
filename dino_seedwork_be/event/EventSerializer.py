import json
from typing import Generic, Optional, Type, TypeVar

from returns.maybe import Maybe, Some
from returns.pipeline import pipe
from returns.result import safe

from src.seedwork.domain.DomainEvent import DomainEvent
from src.seedwork.serializer.AbstractSerializer import AbstractSerializer


class EventSerializer(AbstractSerializer):
    ins: Optional["EventSerializer"] = None

    @classmethod
    def instance(cls) -> "EventSerializer":
        return (
            Maybe.from_optional(EventSerializer.ins)
            .lash(pipe(lambda _: cls.init_instance(), Some))
            .unwrap()
        )

    @classmethod
    def init_instance(cls):
        cls.ins = EventSerializer()
        return cls.ins

    @safe
    def serialize(self, an_event: DomainEvent) -> str:
        return str(self.json_marshaller().encode(an_event, unpicklable=False))

    @safe
    def deserialize(self, an_json: str) -> DomainEvent:
        return DomainEvent.restore(json.loads(an_json))
