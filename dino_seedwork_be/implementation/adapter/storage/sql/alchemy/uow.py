from typing import Callable, List, TypeVar

from returns.future import FutureResult, future_safe
from returns.pipeline import flow
from returns.pointfree import bind, lash
from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.adapters.persistance.sql.AbstractUnitOfWork import \
    AbstractUnitOfWork
from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import \
    DBSessionUser
from dino_seedwork_be.utils.functional import pass_to

ResultType = TypeVar("ResultType")
ExceptionType = TypeVar("ExceptionType", bound=Exception)

__all__ = ["SqlAlchemyUnitOfWork"]


class SqlAlchemyUnitOfWork(AbstractUnitOfWork[AsyncSession]):

    _session: AsyncSession

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        session_users: List[DBSessionUser[AsyncSession]],
    ):
        super().__init__(session_users, session_factory)

    def session(self) -> AsyncSession:
        return self._session

    def set_session(self, session: AsyncSession):
        self._session = session

    async def __aenter__(
        self,
    ):
        self.set_session(self.session_factory()())
        [
            session_user.set_session(self._session)
            for session_user in self.session_users()
        ]
        result = await super().__aenter__()
        return result

    @future_safe
    async def future_Enter(self):
        r = await self.__aenter__()
        return r

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self._session.close()

    @future_safe
    async def future__aexit_with_failure(self, result: ExceptionType) -> ExceptionType:
        await self.__aexit__(result)
        print("result failure", result)
        raise result

    @future_safe
    async def future__aexit__with_success(self, result: ResultType) -> ResultType:
        await self.__aexit__(None)
        return result

    async def _commit(self):
        await self._session.commit()
        print("commit to db ", self.session_users)

    async def rollback(self):
        await self._session.rollback()
        print("rollback db ", self.session_users)

    def absord(self):
        def enter(_):
            return self.future_Enter()

        def catch_future_result(
            result: FutureResult[ResultType, ExceptionType]
        ) -> FutureResult[ResultType, ExceptionType]:
            return flow(
                True,
                enter,
                bind(pass_to(result)),
                bind(self.future__aexit__with_success),
                lash(self.future__aexit_with_failure),
            )

        return catch_future_result

    @classmethod
    def factory(
        cls,
        session_factory: Callable[[], AsyncSession],
        session_users: List[DBSessionUser],
    ):
        return SqlAlchemyUnitOfWork(session_factory, session_users)
