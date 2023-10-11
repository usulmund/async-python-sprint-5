"""
Модуль с функциями, выполняющими
основную бизнес-логику, не связанную
с пользователем и базой данных.
"""
from time import monotonic

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import UserPassword, AccountIdToken
from .db_logic import token_cache, get_bucket_session
from core.config import (
    logger,
    app_settings
)


BUCKET_NAME = app_settings.bucket_name


async def get_access_time_to_cache():
    """
    Корутина для подсчета времени доступа
    к кэшу.
    """
    start_time = monotonic()
    for _ in token_cache:
        pass
    access_time = monotonic() - start_time
    return access_time


async def get_access_time_to_db(session: AsyncSession) -> int:
    """
    Корутина для подсчета времени доступа
    к базе данных.
    """
    models_list = [
        UserPassword,
        AccountIdToken,
    ]
    start_time = monotonic()
    try:
        for model in models_list:
            check_table_query = (select(model))
            check_table = (
                await session.execute(check_table_query)
            ).all()
            if check_table:
                logger.info(f'{model} is done')
        access_time = monotonic() - start_time
    except Exception as e:
        logger.error(f'db is unavailable: {e}')
        access_time = -1
    return access_time


async def get_access_time_to_bucket():
    """
    Корутина для подсчета времени доступа
    к бакету.
    """
    start_time = monotonic()
    try:
        s3 = await get_bucket_session()
        for _ in s3.list_objects(Bucket=BUCKET_NAME)['Contents']:
            pass
        access_time = monotonic() - start_time

    except Exception as e:
        logger.error(f'bucket is unavailable: {e}')
        access_time = -1
    return access_time


async def find_path_by_id(file_id: str):
    """
    Корутина для поиска пути к файлу в бакете
    по его id.
    """
    s3 = await get_bucket_session()
    path = None
    for file in s3.list_objects(Bucket=BUCKET_NAME)['Contents']:
        if file['ETag'] == f'"{file_id}"':
            path = file['Key']
    return path


async def create_file_metadata(file):
    """
    Корутина для создания словаря
    с необходимой информацией о файле.
    """
    file_metadata = dict()

    file_metadata['id'] = file['ETag'].replace('"', '')
    file_metadata['name'] = file['Key'].split('/')[-1]
    format = "%Y-%m-%dT%H:%M:%SZ"
    file_metadata['created_at'] = file['LastModified'].strftime(format)
    file_metadata['path'] = file['Key']
    file_metadata['size'] = file['Size']
    file_metadata['is_downloadable'] = True

    return file_metadata


async def check_file_exists(
    path: str,
) -> bool:
    """
    Корутина для проверки существования файла
    по его пути.
    """
    s3 = await get_bucket_session()
    for key in s3.list_objects(Bucket=BUCKET_NAME)['Contents']:
        if key['Key'] == path:
            return True

    return False
