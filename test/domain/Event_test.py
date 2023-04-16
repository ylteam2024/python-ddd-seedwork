from datetime import datetime

from dino_seedwork_be.domain.DomainEvent import DomainEvent


class TestEvent:
    def test_EventSerializable(self):
        new_event = DomainEvent(
            version=1,
            occurred_on=datetime.now(),
            name="domain name",
            id=1,
            props={},
        )
        event_json = new_event.as_dict()
        event_encoded = DomainEvent.restore(event_json)
        assert type(event_encoded) == DomainEvent
        assert event_encoded.version() == new_event.version()
        assert event_encoded.occurred_on() == new_event.occurred_on()
