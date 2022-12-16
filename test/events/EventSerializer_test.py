from src.seedwork.domain.DomainEvent import DomainEvent
from src.seedwork.event.EventSerializer import EventSerializer

from .TestableDomainEvent import TestableDomainEvent


class TestEventSerializer:
    def test_serialize(self):
        event_serializer = EventSerializer.instance()
        assert event_serializer is not None
        serialized_event = event_serializer.serialize(
            DomainEvent(name="TestDomainEvent", props={"name": "Nam nghien"})
        ).unwrap()
        assert "occurred_on" in serialized_event
        assert "Nam nghien" in serialized_event

    def test_deserialize(self):
        event_serializer = EventSerializer.instance()
        assert event_serializer is not None
        test_domain_event = TestableDomainEvent(name="HaiChan", props={"age": 12})
        serialized_event = event_serializer.serialize(test_domain_event).unwrap()
        deserialized_event = event_serializer.deserialize(serialized_event).unwrap()

        assert deserialized_event.name().value_or(None) == "HaiChan"
        assert deserialized_event.props
