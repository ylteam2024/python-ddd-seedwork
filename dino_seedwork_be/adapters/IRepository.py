import uuid
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, List, Optional, TypeVar

from returns.future import FutureResult, FutureSuccess
from returns.maybe import Maybe
from returns.pipeline import flow, pipe
from returns.pointfree import bind, lash

from dino_seedwork_be.domain.value_objects import ID
from dino_seedwork_be.exceptions import NotImplementError
from dino_seedwork_be.storage.uow import DBSessionUser
from dino_seedwork_be.utils.functional import return_v

EntityType = TypeVar("EntityType")
DTOType = TypeVar("DTOType")


@dataclass
class PaginationResultDB(Generic[EntityType]):
    items: List[EntityType]
    limit: int
    size: int
    total: int


class IRepository(DBSessionUser, Generic[EntityType]):
    def get_next_id(self, simple: Optional[bool] = False) -> FutureResult[ID, Any]:
        def check_exist_and_gen() -> FutureResult:
            next_id_candidate = ID(uuid.uuid4())
            return flow(
                next_id_candidate,
                self.get_by_id,
                bind(
                    pipe(
                        bind(return_v(FutureSuccess(next_id_candidate))),
                        lash(lambda _: check_exist_and_gen()),
                    )
                ),
            )

        next_id_candidate = uuid.uuid4()
        match simple:
            case True:
                return FutureSuccess(ID(next_id_candidate))
            case False:
                return check_exist_and_gen()

        return FutureSuccess(ID(next_id_candidate))

    @abstractmethod
    def get_by_id(self, id: ID) -> FutureResult[Maybe[EntityType], Any]:

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
    def remove(self, id: ID) -> FutureResult:
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

    @abstractmethod
    def get_list_pagination(
        self, filter: Any
    ) -> FutureResult[PaginationResultDB[EntityType], Any]:
        raise NotImplementError(
            "Repository does not support the default getListPagination"
            "method, you need to give it the detail logic"
        )
