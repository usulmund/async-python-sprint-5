"""
Модуль с описанием точек входа,
связанный с работой с пользователями.
Привязаны к объекту user_router.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from db.db import get_session
from core.config import logger
from services.db_logic import get_account_token
from services.user_logic import (
    create_account,
    create_access_token,
    check_auth
)
from schemas.response_models import RegisterStatus

user_router = APIRouter()


@user_router.post(
    '/register',
    response_model=RegisterStatus,
    summary='Account registration',
    description='Enter username and password to register.'
)
async def register_user(
    response: Response,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(get_session)
):
    """
    Корутина для регистрации пользователя.
    При регистрации создается токен.
    Возвращается статут успешности регистрации.
    Неудача, если такой пользователь уже существует.
    """

    is_create_account_success = await create_account(
        username,
        password,
        session
    )
    if is_create_account_success:
        token = await create_access_token(username, password, session)
        return RegisterStatus(
            status='success',
            username=username,
            token=token
        )

    response.status_code = status.HTTP_401_UNAUTHORIZED

    return RegisterStatus(
        status='fail',
        username=username,
    )


@user_router.post(
    '/auth',
    summary='Account authorization',
    description='Enter username and password to authorize.'
)
async def auth_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
):
    """
    Корутина для авторизации пользователя.
    Если данные введены корректно,
    то получаем токен, который передается в заголовке респонса.
    """

    username = form_data.username
    password = form_data.password

    is_auth_success = await check_auth(
        username,
        password,
        session
    )
    logger.info(f'AUTH STATUS: {is_auth_success}')
    if is_auth_success:
        token = await get_account_token(username, session)
        return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )
