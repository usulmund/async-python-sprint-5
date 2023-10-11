"""
Модуль с описанием точек входа,
связанный с работой с файлами.
Привязаны к объекту file_router.
"""

from typing import Optional
from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import RedirectResponse, ORJSONResponse
import botocore.client

from services.logic import get_bucket_session
from core.config import (
    app_settings
)

from services.logic import (
    get_bucket_session,
    find_path_by_id,
    create_file_metadata,
    check_file_exists
)

from services.user_logic import (
    get_current_user
)

from schemas.response_models import FilesInfo


file_router = APIRouter()

BUCKET_NAME = app_settings.bucket_name


@file_router.get(
    '/files/',
    response_model=FilesInfo,
    summary='Show info',
    description='Use it to show all info about files in storage.'
)
async def get_info_about_files(
    current_user: Annotated[int, Depends(get_current_user)],
    s3: botocore.client = Depends(get_bucket_session),
):
    """
    Корутина, возвращающая статистику по всем файлам в бакете.
    Доступна только авторизованному пользователю.
    """
    files: list[dict] = list()
    account_id = None
    try:
        file_objects = s3.list_objects(Bucket=BUCKET_NAME)['Contents']
    except KeyError:
        return FilesInfo(files=[])

    for file in file_objects:
        account_id = file['Owner']['ID']
        file_metadata = await create_file_metadata(file)
        files.append(file_metadata)
    return FilesInfo(
        account_id=account_id,
        files=files
    )


@file_router.post(
    '/files/upload',
    summary='Upload file to storage',
    description='Choose a file to upload it to storage.'
)
async def upload_file_to_storage(
    current_user: Annotated[int, Depends(get_current_user)],
    file: UploadFile,
    path_to_storage: Optional[str] = None,
    s3: botocore.client = Depends(get_bucket_session),
) -> None:
    """
    Корутина для загрузки файлов в бакет.
    Опционально принимает новый путь до файла в бакете.
    Можно указывать промежуточные директории.
    Данные о новом файле заносятся в базу данных.
    Доступна только авторизованному пользователю.
    """

    if not path_to_storage:
        path_to_storage = file.filename
    elif path_to_storage[-1] == '/':
        path_to_storage += file.filename

    s3.upload_fileobj(file.file, BUCKET_NAME, path_to_storage)


@file_router.get(
    '/files/download',
    summary='Download file from storage',
    description='Enter path or file-id to download it.'
)
async def download_file(
    current_user: Annotated[int, Depends(get_current_user)],
    path: Optional[str] = '',
):
    """
    Корутина для скачивания файла из бакета.
    Принимает параметром либо путь до файла, либо
    id файла.
    Перенаправляет на nginx для скачивания.
    """

    is_file_exist = await check_file_exists(path)

    if not is_file_exist:
        path = await find_path_by_id(path)

    if path is None:

        return ORJSONResponse(
            {'error': 'file not exists'},
            status_code=status.HTTP_404_NOT_FOUND
        )
    nginx_host = app_settings.nginx_host
    nginx_port = app_settings.nginx_port
    return RedirectResponse(f'http://{nginx_host}:{nginx_port}/{path}')
