"""
Модуль с тестами.
"""
import os

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool
import pytest

from db.db import get_session
from models.base import Base
from main import app


DSN = os.getenv(
    'DATABASE_DSN',
    default='postgresql+asyncpg://postgres:postgres@localhost:1234/postgres'
)

test_engine = create_async_engine(
    DSN,
    echo=True,
    future=True,
    poolclass=NullPool
)

test_async_session = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.mark.asyncio
async def test_create_database():
    """
    Корутина для создания тестовой БД.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def override_get_session():
    async with test_async_session() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session
client = TestClient(app)


@pytest.mark.asyncio
async def test_ping():
    ping_point = app.url_path_for('ping_services')
    response = client.get(ping_point)
    assert response.status_code == 200
    assert response.json()['db'] > 0
    assert response.json()['bucket'] > 0
    assert response.json()['cache'] > 0


@pytest.mark.asyncio
async def test_register():
    register_point = app.url_path_for('register_user')
    response = client.post(
        register_point,
        headers={
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="username=a&password=a",
    )
    assert response.json()['status'] == 'success'


@pytest.mark.asyncio
async def test_files_info():
    files_info_point = app.url_path_for('get_info_about_files')
    response = client.get(
        files_info_point,
        headers={
            "accept": "application/json",
            "Authorization": "Bearer test",
        },
    )

    assert response.json()['files'] != []
    assert response.status_code == 200
