from dino_seedwork_be.domain.assertion_concern import DomainAssertionConcern
from dino_seedwork_be.domain.entities import Entity


class Aggregate(Entity, DomainAssertionConcern):
    ...
