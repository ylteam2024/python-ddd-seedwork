from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar

ItemType = TypeVar("ItemType")


@dataclass
class PaginationResult(Generic[ItemType]):
    items: List[ItemType]
    total: int
    offset: int
    limit: int


class BaseQuerier:
    pass
