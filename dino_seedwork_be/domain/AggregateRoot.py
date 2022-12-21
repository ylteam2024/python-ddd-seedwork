from dino_seedwork_be.domain import Entity
from dino_seedwork_be.logic import DomainAssertionConcern


class AggregateRoot(Entity, DomainAssertionConcern):
    """Consits of 1+ entities. Spans transaction boundaries."""

    ...
