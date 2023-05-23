from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import \
    DBSessionUser

# __all__ = ["ApplicationLifeCycleUsecase"]

SessionType = TypeVar("SessionType")


class ApplicationLifeCycleUsecase(ABC, Generic[SessionType]):
    _session: SessionType

    def session(self):
        return self._session

    def set_session(self, a_session):
        self._session = a_session

    @abstractmethod
    def get_session_users(self) -> List[DBSessionUser[SessionType]]:
        ...
