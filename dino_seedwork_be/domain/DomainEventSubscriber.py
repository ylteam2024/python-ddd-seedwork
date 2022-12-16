from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from returns.future import FutureResult

from src.seedwork.domain.DomainEvent import DomainEvent


class DomainEventSubscriber(ABC):
    @abstractmethod
    def handle_event(self, an_event: DomainEvent) -> FutureResult[Any, Exception]:
        ...

    @abstractmethod
    def event_type_subscribed(self) -> str:
        ...
