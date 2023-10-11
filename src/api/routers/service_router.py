"""
Модуль с описанием точек входа,
связанный с работой с сервисами.
Привязаны к объекту service_router.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.db import get_session
from services.logic import (

    get_access_time_to_db,
    get_access_time_to_bucket,
    get_access_time_to_cache
)

from schemas.response_models import PingInfo

service_router = APIRouter()


@service_router.get(
    '/ping',
    response_model=PingInfo,
    summary='Ping services',
    description='Use in to check access time to services.'
)
async def ping_services(
    session: AsyncSession = Depends(get_session),
):
    """
    Корутина для получения информации о скорости
    доступа к сервисам.
    """
    db_access_time = await get_access_time_to_db(session)
    bucket_access_time = await get_access_time_to_bucket()
    cache_access_time = await get_access_time_to_cache()

    return PingInfo(
        db=db_access_time,
        bucket=bucket_access_time,
        cache=cache_access_time
    )
