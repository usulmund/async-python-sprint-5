"""
Модуль с подключением роутеров.
"""
from fastapi import APIRouter

from .routers.user_router import user_router
from .routers.file_router import file_router
from .routers.service_router import service_router

router = APIRouter()
router.include_router(user_router, tags=['user'])
router.include_router(file_router, tags=['file'])
router.include_router(service_router, tags=['service'])
