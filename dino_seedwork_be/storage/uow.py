from abc import ABC, abstractmethod
from contextlib import AsyncContextDecorator
from typing import Any, Generic, List, TypeVar

from sqlalchemy.ext.asyncio.session import AsyncSession

from src.seedwork.utils.functional import forEach

SessionType = TypeVar("SessionType")


class SessionUserAlreadyHaveSession(Exception):
    ...


class DBSessionUser(Generic[SessionType]):
    __session: SessionType
    __sessionClosed = False
    __sessionPreserved = False

    def getSession(self) -> SessionType:
        return self.__session

    def session(self) -> SessionType:
        return self.__session

    def setSessionPreserved(self, aBool: bool):
        self.__sessionPreserved = aBool

    def __setSession(self, session: SessionType):
        self.__session = session
        self.setSessionClosedStatus(False)

    def setSession(self, session: SessionType):
        try:
            if self.getSession() is not None and not self.isCurrentSessionClosed():
                if not self.__sessionPreserved:
                    raise SessionUserAlreadyHaveSession(
                        f" {str(self)} already ocuppied by a session"
                    )
        except AttributeError:
            self.__setSession(session)
        self.__setSession(session)

    def set_session(self, session: SessionType):
        self.setSession(session)

    def setSessionClosedStatus(self, closed: bool):
        self.__sessionClosed = closed

    def isCurrentSessionClosed(self) -> bool:
        session = self.getSession()
        return not (session.new or session.dirty or session.deleted)


class AsyncSessionUser(DBSessionUser[AsyncSession]):
    pass


class SuperDBSessionUser(DBSessionUser):
    __sessionUsers: List[DBSessionUser] = []
    __session: AsyncSession

    def setSessionClosedStatus(self, closed: bool):
        if self.getSessionUsers() is not None:
            forEach(
                lambda sessionUser, _: sessionUser.setSessionClosedStatus(closed),
                self.getSessionUsers(),
            )

    def setSession(self, session):
        if self.getSessionUsers() is not None:
            forEach(
                lambda sessionUser, _: sessionUser.setSession(session),
                self.getSessionUsers(),
            )

    def set_session(self, session):
        self.__session = session
        if self.get_session_users() is not None:
            forEach(
                lambda sessionUser, _: sessionUser.set_session(session),
                self.get_session_users(),
            )

    def session(self):
        return self.__session

    def getSessionUsers(self) -> List[DBSessionUser]:
        return self.__sessionUsers

    def get_session_users(self) -> List[DBSessionUser]:
        return self.__sessionUsers

    def setSessionUsers(self, sessionUsers: List[DBSessionUser]):
        self.__sessionUsers = sessionUsers

    def set_session_users(self, session_users: List[DBSessionUser]):
        self.__sessionUsers = session_users


class AbstractUnitOfWork(ABC, AsyncContextDecorator):
    def __init__(
        self, sessionUsers: List[DBSessionUser], session_factory: None | Any = None
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
        self.clearSession()

    async def aexit(self, *args):
        return self.__aexit__(*args)

    @abstractmethod
    def getSession(self) -> Any:
        pass

    @abstractmethod
    def clearSession(self):
        raise NotImplementedError

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
