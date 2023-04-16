from dataclasses import dataclass

from dino_seedwork_be.domain.value_objects import ValueObject

from .IdentifiedDomainObject import IdentifiedDomainObject, IdentityType

__all__ = ["IdentifiedValueObject"]


@dataclass(frozen=True, kw_only=True)
class IdentifiedValueObject(IdentifiedDomainObject[IdentityType], ValueObject):
    id: IdentityType
    """
    Base class for identified objects
    """
