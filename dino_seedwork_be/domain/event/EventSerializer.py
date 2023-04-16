import json
from typing import Optional

from returns.maybe import Maybe, Some
from returns.pipeline import pipe
from returns.result import safe

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.serializer.AbstractSerializer import AbstractSerializer

__all__ = ["EventSerializer"]


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
