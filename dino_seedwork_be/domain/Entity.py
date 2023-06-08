import datetime
from abc import ABC, abstractmethod
from typing import Generic, TypedDict, TypeVar

from returns.maybe import Maybe, Nothing, Some
from returns.result import Result, Success
from typing_extensions import Self

from dino_seedwork_be.fp.domain_safe import domain_safe
from dino_seedwork_be.utils.date import now_utc
from dino_seedwork_be.utils.functional import unwrap

from .IdentifiedDomainObject import IdentifiedDomainObject, IdentityType


class BaseOutsideParams(TypedDict):
    created_at: Maybe[datetime.datetime]
    updated_at: Maybe[datetime.datetime]


OutsideParams = TypeVar("OutsideParams", bound=BaseOutsideParams)


# __all__ = ["Entity", "BaseRawAttributes"]


class Entity(
    ABC, Generic[OutsideParams, IdentityType], IdentifiedDomainObject[IdentityType]
):
    _created_at: Maybe[datetime.datetime] = Nothing
    _updated_at: Maybe[datetime.datetime] = Nothing

    _concurrency_version: int = 0

    def __init__(self, id: Maybe[IdentityType] = Nothing):
        self._concurrency_version = 0
        super().__init__(id)

    def updated_at(self) -> Maybe:
        return self._updated_at

    def created_at(self) -> Maybe:
        return self._created_at

    def set_update_at(self, a_date_time: datetime.datetime) -> Result:
        self._updated_at = Some(a_date_time)
        return Success("OK")

    def set_created_at(self, a_date_time: datetime.datetime) -> Result:
        self._created_at = Some(a_date_time)
        return Success("OK")

    def concurrency_version(self) -> int:
        return self._concurrency_version

    def increase_concurrency_version(self):
        self._concurrency_version += 1

    @classmethod
    @domain_safe
    def init(cls, outside_params: OutsideParams, id: Maybe[IdentityType]) -> Self:
        entity = cls(id)
        entity._created_at = outside_params["created_at"]
        entity._updated_at = outside_params["updated_at"]
        unwrap(entity.from_outside_params(outside_params))
        return entity

    @classmethod
    @domain_safe
    def factory(cls, id: Maybe[IdentityType], *args, **kwargs) -> Self:
        entity = cls(id)
        entity._created_at = Some(now_utc())
        entity._updated_at = Nothing
        entity.create_with_params(*args, **kwargs)
        return entity

    @abstractmethod
    def from_outside_params(self, outside_params: OutsideParams) -> Result:
        pass

    @abstractmethod
    def create_with_params(self, *args, **kwargs) -> Result:
        pass
