from datetime import datetime

import jsonpickle

from src.seedwork.domain.events import DomainEvent


class TestEvent:
    def test_EventSerializable(self):
        newEvent = DomainEvent(version=1, occurredOn=datetime.now())
        eventJson = jsonpickle.encode(newEvent, unpicklable=False)
        eventEncoded = jsonpickle.decode(eventJson)
        assert eventEncoded["version"] == newEvent.getVersion()
        assert (
            datetime.fromisoformat(eventEncoded["occurredOn"])
            == newEvent.getOccurredOn()
        )
