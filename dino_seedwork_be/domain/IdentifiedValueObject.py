from dataclasses import dataclass, field
from uuid import uuid4

from dino_seedwork_be.domain import ID, IdentifiedDomainObject, ValueObject


@dataclass(frozen=True, kw_only=True)
class IdentifiedValueObject(IdentifiedDomainObject, ValueObject):
    id: ID = field(hash=True, default_factory=lambda: ID(uuid4()))
    """
    Base class for identified objects
    """
