import datetime
from typing import Generic, Optional, TypeVar, cast

from returns.result import Result, Success

from dino_seedwork_be.domain import IdentifiedDomainObject

from .value_objects import ID, UUID

RawAttributes = TypeVar("RawAttributes")


class Entity(Generic[RawAttributes], IdentifiedDomainObject):
    _created_at: Optional[datetime.datetime] = None
    _updated_at: Optional[datetime.datetime] = None

    _init_param_keys = []

    _concurrency_version: int = 0

    def __init__(self, id: Optional[ID] = None):
        self._concurrency_version = 0
        if id is not None:
            self.setId(id)
        super().__init__()

    @staticmethod
    def init_param_keys():
        return Entity._init_param_keys

    def updated_at(self):
        return self._updated_at

    def created_at(self):
        return self._created_at

    def set_update_at(self, a_date_time: datetime.datetime) -> Result:
        self._updated_at = a_date_time
        return Success("OK")

    def set_created_at(self, a_date_time: datetime.datetime) -> Result:
        self._created_at = a_date_time
        return Success("OK")

    def concurrency_version(self) -> int:
        return self._concurrency_version

    def increase_concurrency_version(self):
        self._concurrency_version += 1

    def __eq__(self, __o) -> bool:
        if __o is None:
            return False
        elif isinstance(__o, Entity):
            return False
        elif self == object:
            return True
        else:
            return self.identity() == cast(Entity, __o).identity()

    @staticmethod
    def create(raw_attributes: RawAttributes, id: UUID):
        print(
            "There is no default method for creation"
            "Please override this create method"
        )
