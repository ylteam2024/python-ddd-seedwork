from collections.abc import Callable
from typing import List, TypeVar

from returns.future import FutureResult, future_safe
from returns.pipeline import flow
from returns.pointfree import bind, lash
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.seedwork.storage.uow import AbstractUnitOfWork, DBSessionUser
from src.seedwork.utils.functional import passTo

ResultType = TypeVar("ResultType")
ExceptionType = TypeVar("ExceptionType", bound=Exception)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        session_factory: Callable[[], AsyncSession],
        session_users: List[DBSessionUser],
    ):
        self.session_factory = session_factory
        self.session_users = session_users
        super().__init__(session_users)

    def getSession(self) -> AsyncSession:
        return self.session

    async def __aenter__(
        self,
    ):
        self.session = self.session_factory()
        [session_user.setSession(self.session) for session_user in self.session_users]
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
    async def futureAExitWithFailure(self, result: ExceptionType) -> ExceptionType:
        await self.__aexit__(result)
        print("result failure", result)
        raise result

    @future_safe
    async def futureAExitWithSuccess(self, result: ResultType) -> ResultType:
        await self.__aexit__(None)
        return result

    def clearSession(self):
        [
            session_user.setSessionClosedStatus(True)
            for session_user in self.session_users
        ]

    async def _commit(self):
        await self.session.commit()
        print("commit to db ", self.session_users)

    async def rollback(self):
        await self.session.rollback()
        print("rollback db ", self.session_users)

    def absord(self):
        def enter(_):
            return self.futureAEnter()

        def catchFutureResult(
            result: FutureResult[ResultType, ExceptionType]
        ) -> FutureResult[ResultType, ExceptionType]:
            return flow(
                True,
                enter,
                bind(passTo(result)),
                bind(self.futureAExitWithSuccess),
                lash(self.futureAExitWithFailure),
            )

        return catchFutureResult
