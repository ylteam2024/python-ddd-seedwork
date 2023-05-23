from typing import List

from returns.future import FutureResult

from ..DomainEvent import DomainEvent
from ..DomainEventSubscriber import DomainEventSubscriber
from .EventStore import EventStore


class EventStoreSubscriber(DomainEventSubscriber):
    _event_store: EventStore

    def __init__(self, event_store: EventStore) -> None:
        self._event_store = event_store
        super().__init__()

    def handle_event(
        self, an_event: DomainEvent
    ) -> FutureResult[DomainEvent, Exception]:
        return self._event_store.append(an_event)

    def event_type_subscribed(self) -> List[str] | str:
        return "*"
