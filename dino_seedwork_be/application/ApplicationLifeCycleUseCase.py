from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.storage.uow import DBSessionUser


class ApplicationLifeCycleUsecase(ABC):
    _session: AsyncSession

    def session(self):
        return self._session

    def set_session(self, a_session):
        self._session = a_session

    @abstractmethod
    def get_session_users(self) -> List[DBSessionUser]:
        ...
