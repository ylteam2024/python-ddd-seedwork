import datetime
from abc import abstractmethod
from typing import Any, Generic, Optional, TypedDict, TypeVar, cast

from returns.result import Result, Success, safe
from typing_extensions import Self

from dino_seedwork_be.utils.date import now_utc

from .IdentifiedDomainObject import IdentifiedDomainObject, IdentityType


class BaseRawAttributes(TypedDict):
    created_at: datetime.datetime | None
    updated_at: datetime.datetime | None


RawAttributes = TypeVar("RawAttributes", bound=BaseRawAttributes)


__all__ = ["Entity"]


class Entity(
    Generic[RawAttributes, IdentityType], IdentifiedDomainObject[IdentityType]
):
    _created_at: Optional[datetime.datetime] = None
    _updated_at: Optional[datetime.datetime] = None

    _concurrency_version: int = 0

    def __init__(self, id: Optional[IdentityType] = None):
        self._concurrency_version = 0
        if id is not None:
            self.set_id(id)
        super().__init__()

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

    @classmethod
    @safe
    def create(cls, raw_attributes: RawAttributes, id: IdentityType) -> Self:
        entity = cls()
        match raw_attributes["created_at"]:
            case datetime.datetime(created_at):
                entity.set_created_at(created_at).unwrap()
            case None:
                entity.set_created_at(now_utc()).unwrap()

        match raw_attributes["updated_at"]:
            case datetime.datetime(updated_at):
                entity.set_update_at(updated_at).unwrap()
        entity.set_id(id).unwrap()
        entity.from_atributes(raw_attributes).unwrap()
        return entity

    @abstractmethod
    def from_atributes(self, raw_attributes: RawAttributes) -> Result:
        pass
