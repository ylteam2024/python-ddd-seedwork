from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


def engine_factory(uri: str, pool_size: int = 20, max_overflow: int = 20):
    engine = create_async_engine(
        uri,
        isolation_level="READ COMMITTED",
        echo=True,
        future=True,
        # pool_size=pool_size,
        # max_overflow=max_overflow,
        poolclass=NullPool,
    )
    return engine


def alchemy_session_factory(engine: AsyncEngine):
    return sessionmaker(bind=engine, class_=AsyncSession)()
