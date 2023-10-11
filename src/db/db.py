"""
Модуль с подключением к базе данных
и описанием корутины-фабрики сессий.
"""
from core.config import app_settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool


engine = create_async_engine(
    app_settings.database_dsn,
    echo=True,
    future=True,
    poolclass=NullPool
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
