from dataclasses import dataclass
from typing import Generic, List, TypeVar

ItemType = TypeVar("ItemType")

__all__ = ["PaginationResult", "BaseQuerier"]


@dataclass
class PaginationResult(Generic[ItemType]):
    items: List[ItemType]
    total: int
    offset: int
    limit: int


class BaseQuerier:
    pass
