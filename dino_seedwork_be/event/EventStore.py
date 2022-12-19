from abc import ABC, abstractmethod
from typing import Any, List

from returns.future import FutureResult

from dino_seedwork_be.domain.DomainEvent import DomainEvent
from dino_seedwork_be.event.StoredEvent import StoredEvent
from dino_seedwork_be.storage.uow import DBSessionUser


class EventStore(ABC, DBSessionUser):
    @abstractmethod
    def all_stored_events_since(
        self, a_stored_event_id: int
    ) -> FutureResult[List[StoredEvent], Exception]:
        ...

    @abstractmethod
    def all_stored_events_between(
        self, a_low_stored_event_id: int, a_high_stored_event_id: int
    ) -> FutureResult[List[StoredEvent], Any]:
        ...

    @abstractmethod
    def append(
        self, an_domain_event: DomainEvent
    ) -> FutureResult[StoredEvent, Exception]:
        ...

    @abstractmethod
    def close(self):
        ...

    @abstractmethod
    def count_events(self) -> FutureResult[int, Any]:
        ...
