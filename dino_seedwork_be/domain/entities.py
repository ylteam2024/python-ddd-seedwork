import datetime
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, cast

from returns.result import Result, Success

from dino_seedwork_be.domain.assertion_concern import AssertionConcern
from dino_seedwork_be.domain.IdentifiedDomainObject import \
    IdentifiedDomainObject

from .mixins import BusinessRuleValidationMixin
from .value_objects import ID, UUID

RawAttributes = TypeVar("RawAttributes")


class Entity(Generic[RawAttributes], IdentifiedDomainObject):
    __createdAt: Optional[datetime.datetime] = None
    __updatedAt: Optional[datetime.datetime] = None

    initParamKeys = []

    concurrencyVersion: int = 0

    def __init__(self, id: Optional[ID] = None):
        self.concurrencyVersion = 0
        if id is not None:
            self.setId(id)
        super().__init__()

    @staticmethod
    def getInitParamKeys():
        return Entity.initParamKeys

    def getUpdatedAt(self):
        return self.__updatedAt

    def getCreatedAt(self):
        return self.__createdAt

    def setUpdateAt(self, aDateTime: datetime.datetime) -> Result:
        self.__updatedAt = aDateTime
        return Success("OK")

    def setCreatedAt(self, aDateTime: datetime.datetime) -> Result:
        self.__createdAt = aDateTime
        return Success("OK")

    def getConcurrencyVersion(self) -> int:
        return self.concurrencyVersion

    def increaseConcurrencyVersion(self):
        self.concurrencyVersion += 1

    def __eq__(self, __o) -> bool:
        if __o is None:
            return False
        elif isinstance(__o, Entity):
            return False
        elif self == object:
            return True
        else:
            return self.getIdentity() == cast(Entity, __o).getIdentity()

    @staticmethod
    def create(rawAttributes: RawAttributes, id: UUID):
        print(
            "There is no default method for creation"
            "Please override this create method"
        )


@dataclass
class AggregateRoot(BusinessRuleValidationMixin, Entity, AssertionConcern):
    """Consits of 1+ entities. Spans transaction boundaries."""
