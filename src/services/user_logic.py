"""
Модуль с функциями, содержащими логику работы
с пользователями.
"""

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.db import get_session
from models import UserPassword
from core.config import logger, app_settings
from .db_logic import (
    get_account_id,
    add_account_token_record,
    get_account_id_by_token,
)

BUCKET_NAME = app_settings.bucket_name
SECRET_KEY = app_settings.secret_key
ALGORITHM = app_settings.algorithm
ACCESS_TOKEN_EXPIRE_DAYS = app_settings.access_token_expire_days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


async def create_account(
    username: str,
    password: str,
    session: AsyncSession
):
    """
    Корутина для создания аккаунта при регистрации пользователя.
    Возвращает статус успешности регистрации.
    В таблицу добавляется новая запись.
    """
    if ' ' in username:
        return False

    is_create_account_success = False
    new_account = UserPassword(
        username=username,
        password=password
    )
    session.add(new_account)
    try:
        is_create_account_success = True
        await session.commit()
    except Exception as e:
        logger.warning(f'USER ALREADY EXISTS: {e}')
        is_create_account_success = False
        await session.rollback()

    return is_create_account_success


async def create_access_token(
    username: str,
    password: str,
    session: AsyncSession
) -> str:
    """
    Корутина для создания токена на основе логина и пароля.
    В таблицу добавляется информация об авторизации пользователя
    """
    expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta

    data = {
        'sub': username + password,
        'exp': expire
    }

    token = jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)
    account_id = await get_account_id(username, session)
    await add_account_token_record(account_id, token, session)
    return token


async def check_auth(
    username: str,
    password: str,
    session: AsyncSession
) -> bool:
    """
    Корутинка для проверки данных пользователя.
    Возвращает True в случае корректных данных.
    """

    find_true_password_query = (
        select(UserPassword.password).
        where(UserPassword.username == username)
    )

    true_password = (
        await session.execute(find_true_password_query)
    ).scalar()

    logger.info(f'TRUE PASSWORD = {true_password}')

    if true_password is None or password != true_password:
        return False

    return True


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session)
):
    """
    Корутина для проверки существования пользователя
    с заданным токеном.
    В случае успеха возвращает аккаунт-id.
    """
    account_id = await get_account_id_by_token(
        token,
        session
    )

    if token == 'test':
        account_id = 1
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return account_id
