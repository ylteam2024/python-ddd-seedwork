from dataclasses import dataclass, field
from uuid import uuid4

from src.seedwork.domain.IdentifiedDomainObject import IdentifiedDomainObject
from src.seedwork.domain.value_objects import ID, UUID_v4, ValueObject


@dataclass(frozen=True, kw_only=True)
class IdentifiedValueObject(IdentifiedDomainObject, ValueObject):
    id: ID = field(hash=True, default_factory=lambda: ID(uuid4()))
    """
    Base class for identified objects
    """
