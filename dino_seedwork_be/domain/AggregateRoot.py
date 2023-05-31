from typing import Generic

from returns.maybe import Some
from returns.result import Result
from typing_extensions import Self

from dino_seedwork_be.domain.exceptions import DomainException
from dino_seedwork_be.domain.IdentifiedDomainObject import IdentityType

from .Entity import Entity, OutsideParams

# __all__ = ["AggregateRoot"]


class AggregateRoot(
    Generic[OutsideParams, IdentityType], Entity[OutsideParams, IdentityType]
):
    """Consits of 1+ entities. Spans transaction boundaries."""

    def from_repository(
        self, outside_params: OutsideParams, id: IdentityType
    ) -> Result[Self, DomainException]:
        return self.init(outside_params, Some(id))
