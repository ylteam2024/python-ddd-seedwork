from typing import Generic

from dino_seedwork_be.domain.IdentifiedDomainObject import IdentityType

from .Entity import Entity, RawAttributes

# __all__ = ["AggregateRoot"]


class AggregateRoot(
    Generic[RawAttributes, IdentityType], Entity[RawAttributes, IdentityType]
):
    """Consits of 1+ entities. Spans transaction boundaries."""

    ...
