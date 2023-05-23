from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar

from returns.future import FutureResult
from returns.maybe import Maybe

from dino_seedwork_be.domain.Entity import Entity
from dino_seedwork_be.domain.value_object.AbstractIdentity import \
    AbstractIdentity
from dino_seedwork_be.exceptions import NotImplementError

EntityType = TypeVar("EntityType", bound=Entity)
DTOType = TypeVar("DTOType")


@dataclass
class PaginationResultDB(Generic[EntityType]):
    items: List[EntityType]
    limit: int
    size: int
    total: int


class Repository(Generic[EntityType]):
    @abstractmethod
    def get_next_id(self, simple: bool = False) -> FutureResult[AbstractIdentity, Any]:
        pass

    @abstractmethod
    def get_by_id(self, id: AbstractIdentity) -> FutureResult[Maybe[EntityType], Any]:

        raise NotImplementError(
            "Repository does not support the default getById"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    def add(self, entity: EntityType) -> FutureResult:

        raise NotImplementError(
            "Repository does not support the default insert"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    def save(self, entity: EntityType) -> FutureResult:

        raise NotImplementError(
            "Repository does not support the default update"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    def remove(self, id: AbstractIdentity) -> FutureResult:
        raise NotImplementError(
            "Repository does not support the default delete"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    def count(self) -> FutureResult[int, Any]:
        raise NotImplementError(
            "Repository does not support the default count"
            "method, you need to give it the detail logic"
        )
