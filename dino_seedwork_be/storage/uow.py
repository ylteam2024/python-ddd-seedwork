from abc import ABC, abstractmethod
from contextlib import AsyncContextDecorator
from typing import Any, Generic, List, TypeVar

from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.utils.functional import for_each

SessionType = TypeVar("SessionType")

__all__ = [
    "SessionUserAlreadyHaveSession",
    "DBSessionUser",
    "AsyncSessionUser",
    "SuperDBSessionUser",
    "AbstractUnitOfWork",
]


class SessionUserAlreadyHaveSession(Exception):
    ...


class DBSessionUser(Generic[SessionType]):
    _session: SessionType
    _session_preserved = False

    def session(self) -> SessionType:
        return self._session

    def set_session_preserved(self, aBool: bool):
        self._session_preserved = aBool

    def _set_ession(self, session: SessionType):
        self._session = session

    def set_session(self, session: SessionType):
        try:
            if self.session() is not None and not self.is_current_session_closed():
                if not self._session_preserved:
                    raise SessionUserAlreadyHaveSession(
                        f" {str(self)} already ocuppied by a session"
                    )
        except AttributeError:
            self._set_ession(session)
        self._set_ession(session)

    def is_current_session_closed(self) -> bool:
        session = self.session()
        return not (session.new or session.dirty or session.deleted)


class AsyncSessionUser(DBSessionUser[AsyncSession]):
    pass


class SuperDBSessionUser(DBSessionUser):
    _sessionUsers: List[DBSessionUser] = []
    _session: AsyncSession

    def set_session(self, session: AsyncSession):
        self._session = session
        if self.session_users() is not None:
            for_each(
                lambda sessionUser, _: sessionUser.set_session(session),
                self.session_users(),
            )

    def session(self):
        return self._session

    def session_users(self) -> List[DBSessionUser]:
        return self._sessionUsers

    def set_session_users(self, session_users: List[DBSessionUser]):
        self._sessionUsers = session_users


class AbstractUnitOfWork(ABC, AsyncContextDecorator):
    def __init__(
        self, session_users: List[DBSessionUser], session_factory: None | Any = None
    ):
        super().__init__()

    async def __aenter__(self):
        return self

    async def aenter(self):
        return self.__aenter__()

    async def __aexit__(self, *args):
        if args[0] is not None:
            await self.rollback()
        else:
            await self.commit()

    async def aexit(self, *args):
        return self.__aexit__(*args)

    @abstractmethod
    def session(self) -> Any:
        pass

    async def commit(self):
        await self._commit()

    @abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

    @abstractmethod
    def absord(self):
        raise NotImplementedError
