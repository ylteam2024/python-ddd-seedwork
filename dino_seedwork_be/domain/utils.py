from dino_seedwork_be.domain import ID, Entity

__all__ = ["get_identity", "get_raw_identity"]


def get_identity(aEntity: Entity) -> ID:
    return aEntity.identity()


def get_raw_identity(aEntity: Entity) -> str:
    return aEntity.raw_id()
