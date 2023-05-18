from abc import ABC, abstractmethod
from typing import Any, List

from returns.future import FutureResult

from dino_seedwork_be.domain.DomainEvent import DomainEvent

__all__ = ["EventStore"]


class EventStore(ABC):
    @abstractmethod
    def all_stored_events_since(
        self, a_stored_event_id: int
    ) -> FutureResult[List[DomainEvent], Exception]:
        ...

    @abstractmethod
    def all_stored_events_between(
        self, a_low_stored_event_id: int, a_high_stored_event_id: int
    ) -> FutureResult[List[DomainEvent], Any]:
        ...

    @abstractmethod
    def append(
        self, an_domain_event: DomainEvent
    ) -> FutureResult[DomainEvent, Exception]:
        ...

    @abstractmethod
    def close(self):
        ...

    @abstractmethod
    def count_events(self) -> FutureResult[int, Any]:
        ...
