from dino_seedwork_be.domain.entities import Entity
from dino_seedwork_be.domain.value_objects import ID


def getIdentity(aEntity: Entity) -> ID:
    return aEntity.getIdentity()


def getRawIdentity(aEntity: Entity) -> str:
    return aEntity.getRawId()
