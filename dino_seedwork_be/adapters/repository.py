import uuid
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, TypeVar

from returns.future import FutureResult

from dino_seedwork_be.domain.value_objects import ID
from dino_seedwork_be.exceptions import NotImplementError
from dino_seedwork_be.storage.uow import DBSessionUser

EntityType = TypeVar("EntityType")
DTOType = TypeVar("DTOType")


@dataclass
class PaginationResultDB(Generic[EntityType]):
    items: List[EntityType]
    limit: int
    size: int
    total: int


class Repository(DBSessionUser, Generic[EntityType]):
    async def get_next_id(self, simple: Optional[bool] = False) -> ID:
        next_id_candidate = uuid.uuid4()
        if simple:
            return ID(next_id_candidate)
        existIdentity = await self.get_by_id(ID(next_id_candidate))
        while existIdentity is not None:
            next_id_candidate = uuid.uuid4()
            existIdentity = await self.get_by_id(ID(next_id_candidate))
        return ID(next_id_candidate)

    @abstractmethod
    async def get_by_id(self, id: ID) -> EntityType:

        raise NotImplementError(
            "Repository does not support the default getById"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    async def add(self, entity: EntityType):

        raise NotImplementError(
            "Repository does not support the default insert"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    async def save(self, entity: EntityType):

        raise NotImplementError(
            "Repository does not support the default update"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    async def remove(self, id: ID):
        raise NotImplementError(
            "Repository does not support the default delete"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    async def count(self):
        raise NotImplementError(
            "Repository does not support the default count"
            "method, you need to give it the detail logic"
        )

    @abstractmethod
    async def get_list_pagination(
        self, filter: Any
    ) -> FutureResult[PaginationResultDB[EntityType], Any]:
        raise NotImplementError(
            "Repository does not support the default getListPagination"
            "method, you need to give it the detail logic"
        )
