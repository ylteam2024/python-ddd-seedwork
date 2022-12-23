from abc import ABC, abstractmethod
from typing import Any

from returns.future import FutureResult

from dino_seedwork_be.domain import DomainEvent

__all__ = ["DomainEventSubscriber"]


class DomainEventSubscriber(ABC):
    @abstractmethod
    def handle_event(self, an_event: DomainEvent) -> FutureResult[Any, Exception]:
        ...

    @abstractmethod
    def event_type_subscribed(self) -> str:
        ...
