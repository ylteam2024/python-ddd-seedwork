from sqlalchemy.ext.asyncio.session import AsyncSession

from dino_seedwork_be.adapters.IRepository import IRepository
from dino_seedwork_be.adapters.persistance.sql.DBSessionUser import \
    DBSessionUser

__all__ = ["AlchemyRepository"]


class AlchemyRepository(DBSessionUser[AsyncSession], IRepository):
    pass
