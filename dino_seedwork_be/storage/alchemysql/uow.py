from collections.abc import Callable
from typing import List, TypeVar

from returns.future import FutureResult, future_safe
from returns.pipeline import flow
from returns.pointfree import bind, lash
from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.storage.uow import AbstractUnitOfWork, DBSessionUser
from dino_seedwork_be.utils.functional import pass_to

ResultType = TypeVar("ResultType")
ExceptionType = TypeVar("ExceptionType", bound=Exception)

__all__ = ["SqlAlchemyUnitOfWork"]


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    _session: AsyncSession

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        session_users: List[DBSessionUser],
    ):
        self.session_factory = session_factory
        self.session_users = session_users
        super().__init__(session_users)

    def session(self) -> AsyncSession:
        return self._session

    def set_session(self, session: AsyncSession):
        self._session = session

    async def __aenter__(
        self,
    ):
        self.set_session(self.session_factory())
        [session_user.set_session(self.session) for session_user in self.session_users]
        result = await super().__aenter__()
        return result

    @future_safe
    async def futureAEnter(self):
        r = await self.__aenter__()
        return r

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

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
        await self.session.commit()
        print("commit to db ", self.session_users)

    async def rollback(self):
        await self.session.rollback()
        print("rollback db ", self.session_users)

    def absord(self):
        def enter(_):
            return self.futureAEnter()

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
