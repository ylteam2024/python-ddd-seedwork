from abc import abstractmethod
from typing import Any, Generic, Set, TypeVar

from returns.functions import tap
from returns.future import FutureResult, FutureSuccess
from returns.maybe import Maybe

from dino_seedwork_be.domain.Entity import Entity
from dino_seedwork_be.domain.value_object.AbstractIdentity import \
    AbstractIdentity
from dino_seedwork_be.domain.value_object.NID import NID
from dino_seedwork_be.exceptions import MainException
from dino_seedwork_be.repository.IRepository import Repository
from dino_seedwork_be.utils.functional import maybe_to_future

EntityType = TypeVar("EntityType", bound=Entity)


class MockRepository(Generic[EntityType], Repository[EntityType]):
    _collection: Set[EntityType]

    def __init__(self) -> None:
        self.init_collection()
        super().__init__()

    @abstractmethod
    def init_collection(self):
        pass

    def get_by_id(self, id: NID) -> FutureResult[Maybe[EntityType], Any]:
        found_entity = next(
            (
                dataset
                for dataset in self._collection
                if dataset.identity().value_or(None) == id
            ),
            None,
        )
        # print(
        #     "found entity ",
        #     found_entity,
        #     id,
        #     list(self._collection)[4].identity().unwrap().get_raw(),
        # )
        return FutureSuccess(Maybe.from_optional(found_entity))

    def get_next_id(self, _: bool = False) -> FutureResult[AbstractIdentity, Any]:
        return FutureSuccess(NID(len(self._collection)))

    def add(self, entity: EntityType) -> FutureResult:
        self._collection.add(entity)
        return FutureSuccess(None)

    def save(self, entity: EntityType) -> FutureResult:
        return (
            self.get_by_id(entity.identity().unwrap())
            .bind(maybe_to_future(MainException(code="NOT_FOUND")))
            .map(tap(lambda old_entity: self._collection.remove(old_entity)))
            .map(tap(lambda _: self._collection.add(entity)))
        )

    def remove(self, id: AbstractIdentity) -> FutureResult:
        self._dataset = {
            entity for entity in self._collection if entity.identity() != id
        }
        return FutureSuccess(None)

    def count(self) -> FutureResult[int, Any]:
        return FutureSuccess(len(self._collection))
