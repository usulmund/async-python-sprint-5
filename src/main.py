"""
Модуль с запуском сервиса.
"""
import sys
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from alembic import command
from alembic.config import Config

from core.config import app_settings
from api.base_router import router


app = FastAPI(
    title=app_settings.app_title,
    default_response_class=ORJSONResponse,
)

app.include_router(router)


async def apply_migration():
    """
    Корутина для применения миграций с помощью alembic.
    """
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', app_settings.database_dsn)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, 'head')


if __name__ == "__main__":

    if sys.argv[-1] == '--migration-on':
        asyncio.run(apply_migration())

    uvicorn.run(
        'main:app',
        host=app_settings.project_host,
        port=app_settings.project_port,
    )
