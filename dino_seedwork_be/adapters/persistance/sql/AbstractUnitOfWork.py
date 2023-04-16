from abc import ABC, abstractmethod
from contextlib import AsyncContextDecorator
from typing import Any, Callable, Generic, List

from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import (
    DBSessionUser, SessionType)


class AbstractUnitOfWork(ABC, Generic[SessionType], AsyncContextDecorator):
    _session_users: List[DBSessionUser[SessionType]]
    _session_factory: Callable[[], SessionType]

    def __init__(
        self,
        session_users: List[DBSessionUser[SessionType]],
        session_factory: Callable[[], SessionType],
    ):
        self._session_users = session_users
        self._session_factory = session_factory
        super().__init__()

    def session_users(self) -> List[DBSessionUser[SessionType]]:
        return self._session_users

    def session_factory(self) -> Callable[[], SessionType]:
        return self._session_factory

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
