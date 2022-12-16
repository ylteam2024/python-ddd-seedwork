from sqlalchemy.ext.asyncio.session import AsyncSession

from src.seedwork.storage.uow import DBSessionUser


class AlchemyRepository(DBSessionUser[AsyncSession]):
    pass
