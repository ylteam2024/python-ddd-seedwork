from abc import abstractmethod
from typing import Any, Generic, TypeVar
from uuid import uuid4

from returns.future import FutureResult, FutureSuccess, future_safe
from returns.maybe import Maybe
from returns.pipeline import pipe
from returns.result import safe
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.functions import count

from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import \
    DBSessionUser
from dino_seedwork_be.domain.value_object.AbstractIdentity import \
    AbstractIdentity
from dino_seedwork_be.domain.value_object.UUID import UUID
from dino_seedwork_be.repository.IRepository import EntityType, Repository
from dino_seedwork_be.repository.Mapper import Mapper, RepositoryModel

from .BaseModel import UUIDBaseModel

__all__ = ["StandardAlchemyRepository"]


AlchemyModel = TypeVar("AlchemyModel", bound=UUIDBaseModel)


class StandardAlchemyRepository(
    Generic[EntityType, AlchemyModel],
    Repository[EntityType],
    DBSessionUser[AsyncSession],
):
    model: AlchemyModel
    mapper: Mapper[EntityType, AlchemyModel]

    def get_next_id(self, _: bool = True) -> FutureResult[AbstractIdentity, Any]:
        return FutureSuccess(UUID(uuid4()))

    def get_by_id(self, id: AbstractIdentity) -> FutureResult[Maybe[EntityType], Any]:
        stmt = select(RepositoryModel).where(self.model.id == id.get_raw())
        return (
            future_safe(self.session().execute)(stmt)
            .map(lambda result: result.scalars().first())
            .bind(pipe(self.mapper.to_aggregate, FutureResult.from_result))
        )

    def add(self, entity: EntityType):
        return self.mapper.to_db(entity).map(
            pipe(safe(self.session().add), FutureResult.from_result)
        )

    @future_safe
    async def save(self, entity: EntityType):
        stmt = select(self.model).where(
            self.model.id
            == entity.identity().map(lambda id: id.get_raw()).value_or(None)
        )

        def update(session: Session):
            db_ins = session.execute(stmt).scalars().first()
            self.save_update(db_ins)

        await self.session().run_sync(update)

    @safe
    @abstractmethod
    def save_update(self, db_ins: AlchemyModel):
        pass

    @future_safe
    async def remove(self, id: AbstractIdentity):
        stmt = delete(self.model).where(self.model.id == id.get_raw())
        await self.session().execute(stmt)

    @future_safe
    async def count(self):
        stmt = select(count(self.model.id))

        return (await self.session().execute(stmt)).scalars().first() or 0
