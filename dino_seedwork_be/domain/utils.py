from src.seedwork.domain.entities import Entity
from src.seedwork.domain.value_objects import ID


def getIdentity(aEntity: Entity) -> ID:
    return aEntity.getIdentity()


def getRawIdentity(aEntity: Entity) -> str:
    return aEntity.getRawId()
