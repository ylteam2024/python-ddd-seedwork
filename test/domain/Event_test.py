from datetime import datetime

import jsonpickle

from dino_seedwork_be.domain import DomainEvent


class TestEvent:
    def test_EventSerializable(self):
        new_event = DomainEvent(
            version=1,
            occurred_on=datetime.now(),
            name="domain name",
            id=1,
            props={},
        )
        event_json = jsonpickle.encode(new_event, unpicklable=False)
        event_encoded = jsonpickle.decode(event_json)
        assert type(event_encoded) == DomainEvent
        assert event_encoded.version() == new_event.version()
        assert (
            datetime.fromisoformat(event_encoded.occurred_on())
            == new_event.occurred_on()
        )
