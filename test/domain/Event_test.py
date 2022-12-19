from datetime import datetime

import jsonpickle

from dino_seedwork_be.domain.DomainEvent import DomainEvent


class TestEvent:
    def test_EventSerializable(self):
        newEvent = DomainEvent(
            version=1, occurred_on=datetime.now(), name="domain name"
        )
        eventJson = jsonpickle.encode(newEvent, unpicklable=False)
        eventEncoded = jsonpickle.decode(eventJson)
        assert eventEncoded["version"] == newEvent.version()
        assert (
            datetime.fromisoformat(eventEncoded["occurred_on"])
            == newEvent.occurred_on()
        )
