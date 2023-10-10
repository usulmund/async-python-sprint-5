"""
Модуль с функциями, содержащими логику работы
с базой данных.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from cachetools import LRUCache
import boto3

from models import UserPassword, AccountIdToken
from core.config import logger, app_settings

BUCKET_NAME = app_settings.bucket_name
token_cache = LRUCache(maxsize=100)


async def get_account_id(
    username: str,
    session: AsyncSession
) -> str:
    """
    Корутина для получения имени
    пользователя по его id.
    """
    get_account_id_query = (
        select(UserPassword.id).
        where(UserPassword.username == username)
    )
    account_id = (
        await session.execute(get_account_id_query)
    ).scalar()

    return account_id


async def add_account_token_record(
    account_id: int,
    token: str,
    session: AsyncSession
) -> None:
    """
    Корутина для добавления записи
    аккаунт_id - токен в таблицу.
    """
    new_token_record = AccountIdToken(
        account_id=account_id,
        token=token
    )
    session.add(new_token_record)
    try:
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.info(f'Not first enter: {e}')


async def get_account_token(
    username: str,
    session: AsyncSession
) -> str:
    """
    Корутина для получения токена, соответствующего юзернейму, из базы данных.
    Информация ищется в кэше, и если в нем отстуствует запись,
    обращаемся к базе данных.
    """
    if username in token_cache:
        logger.info('GET TOKEN FROM CACHE')
        return token_cache[username]

    account_id = await get_account_id(username, session)
    get_account_token_query = (
        select(AccountIdToken.token).
        where(AccountIdToken.account_id == account_id)
    )
    account_token = (
        await session.execute(get_account_token_query)
    ).scalar()

    token_cache[username] = account_token
    return account_token


async def get_account_id_by_token(
    token: str,
    session: AsyncSession
) -> str:
    """
    Корутина для получения id аккаунта
    по токену.
    """
    get_account_id_query = (
        select(AccountIdToken.account_id).
        where(AccountIdToken.token == token)
    )
    account_id = (
        await session.execute(get_account_id_query)
    ).scalar()

    return account_id


async def check_file_exists(
    path: str,
    session: AsyncSession
) -> str:
    """
    Корутина для проверки существования файла
    по его пути.
    """
    s3 = await get_bucket_session()
    for key in s3.list_objects(Bucket=BUCKET_NAME)['Contents']:
        if key['Key'] == path:
            return True
    return False


async def get_bucket_session():
    session = boto3.session.Session()
    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        aws_access_key_id=app_settings.aws_access_key_id,
        aws_secret_access_key=app_settings.aws_secret_access_key,
    )
    return s3
