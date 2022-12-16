from typing import Callable, List

from src.seedwork.storage.uow import AbstractUnitOfWork, DBSessionUser

UowFactory = Callable[[List[DBSessionUser]], AbstractUnitOfWork]


class AbstractUOWApplicationService:
    __uow: UowFactory

    def uow(self, userSession: List[DBSessionUser]) -> AbstractUnitOfWork:
        return self.__uow(userSession)

    def setUow(self, uow: UowFactory):
        self.__uow = uow
