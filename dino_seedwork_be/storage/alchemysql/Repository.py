from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.storage.uow import DBSessionUser


class AlchemyRepository(DBSessionUser[AsyncSession]):
    pass
