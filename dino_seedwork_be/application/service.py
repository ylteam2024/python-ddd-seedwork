from typing import Callable, List

from dino_seedwork_be.storage.uow import AbstractUnitOfWork, DBSessionUser

UowFactory = Callable[[List[DBSessionUser]], AbstractUnitOfWork]


class AbstractUOWApplicationService:

    _uow: UowFactory

    def uow(self, user_session: List[DBSessionUser]) -> AbstractUnitOfWork:
        return self._uow(user_session)

    def set_uow(self, uow: UowFactory):
        self._uow = uow
