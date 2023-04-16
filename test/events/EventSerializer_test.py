from uuid import uuid4

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.domain.event.EventSerializer import EventSerializer
from dino_seedwork_be.domain.value_object.UUID import UUID

from .TestableDomainEvent import TestableDomainEvent


class TestEventSerializer:
    def test_serialize(self):
        event_serializer = EventSerializer.instance()
        assert event_serializer is not None
        serialized_event = event_serializer.serialize(
            DomainEvent(
                name="TestDomainEvent",
                props={"name": "Nam nghien", "id": UUID(uuid4())},
                id=10,
            )
        ).unwrap()
        assert "occurred_on" in serialized_event
        assert "Nam nghien" in serialized_event

    def test_deserialize(self):
        event_serializer = EventSerializer.instance()
        assert event_serializer is not None
        test_domain_event = TestableDomainEvent(
            name="HaiChan", props={"age": 12}, id=10
        )
        serialized_event = event_serializer.serialize(test_domain_event).unwrap()
        deserialized_event = event_serializer.deserialize(serialized_event).unwrap()

        assert deserialized_event.name() == "HaiChan"
        assert deserialized_event.props()["age"] == 12
