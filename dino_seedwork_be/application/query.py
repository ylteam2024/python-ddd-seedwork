from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar

from returns.future import FutureResult

ItemType = TypeVar("ItemType")

# __all__ = ["PaginationResult", "BaseQuerier"]

InputType = TypeVar("InputType")
ReturnType = TypeVar("ReturnType")


@dataclass
class PaginationResult(Generic[ItemType]):
    items: List[ItemType]
    total: int
    offset: int
    limit: int


class BaseQuerier:
    pass


class BusBaseQuerier(Generic[InputType, ReturnType], BaseQuerier):
    @abstractmethod
    def handle(self, query: InputType) -> FutureResult[ReturnType, Any]:
        pass

    def execute(self, query: InputType) -> FutureResult[ReturnType, Any]:
        return self.handle(query)
