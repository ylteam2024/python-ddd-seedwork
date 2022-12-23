from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.storage.uow import DBSessionUser

__all__ = ["AlchemyRepository"]


class AlchemyRepository(DBSessionUser[AsyncSession]):
    pass
