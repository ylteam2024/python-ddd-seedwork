import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, TypeVar

from returns.future import FutureResult

from src.seedwork.application.query import PaginationResult
from src.seedwork.domain.entities import UUID
from src.seedwork.domain.value_objects import ID
from src.seedwork.exceptions import NotImplementError
from src.seedwork.storage.uow import DBSessionUser

EntityType = TypeVar("EntityType")
DTOType = TypeVar("DTOType")


@dataclass
class PaginationResultDB(Generic[EntityType]):
    items: List[EntityType]
    limit: int
    size: int
    total: int


class Repository(DBSessionUser, Generic[EntityType]):
    async def getNextId(self, simple: Optional[bool] = False) -> ID:
        nextIdCandidate = uuid.uuid4()
        if simple:
            return ID(nextIdCandidate)
        existIdentity = await self.getById(ID(nextIdCandidate))
        while existIdentity is not None:
            nextIdCandidate = uuid.uuid4()
            existIdentity = await self.getById(ID(nextIdCandidate))
        return ID(nextIdCandidate)

    @abstractmethod
    async def getById(self, id: ID) -> EntityType:

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
    async def getListPagination(
        self, filter: Any
    ) -> FutureResult[PaginationResultDB[EntityType], Any]:
        raise NotImplementError(
            "Repository does not support the default getListPagination"
            "method, you need to give it the detail logic"
        )
