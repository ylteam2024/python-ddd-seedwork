from datetime import datetime

from returns.maybe import Maybe

from dino_seedwork_be.domain.value_object.AbstractValueObject import \
    ValueObject

from .IdentifiedDomainObject import IdentifiedDomainObject, IdentityType

__all__ = ["IdentifiedValueObject"]


class IdentifiedValueObject(ValueObject, IdentifiedDomainObject[IdentityType]):
    """
    Base class for identified objects
    """

    def __init__(self, an_id: IdentityType, created_at: Maybe[datetime]):
        self.set_id(an_id)
        super().__init__(created_at=created_at)
