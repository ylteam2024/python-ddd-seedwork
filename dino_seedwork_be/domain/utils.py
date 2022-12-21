from dino_seedwork_be.domain import ID, Entity


def get_identity(aEntity: Entity) -> ID:
    return aEntity.identity()


def get_raw_identity(aEntity: Entity) -> str:
    return aEntity.raw_id()
