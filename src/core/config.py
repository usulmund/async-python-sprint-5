"""
Модуль с описанием основных настроек.
"""
import os
import logging
from logging import config as logging_config
from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)
logger = logging.getLogger()

PROJECT_NAME = os.getenv('PROJECT_NAME', 'FileStorage')
PROJECT_HOST = os.getenv('PROJECT_HOST', 'localhost')
PROJECT_PORT = int(os.getenv('PROJECT_PORT', '8080'))


class AppSettings(BaseSettings):
    app_title: str
    bucket_name: str
    database_dsn: str
    aws_access_key_id: str
    aws_secret_access_key: str

    # openssl rand -hex 32
    # секретный ключ для подписи токенов JWS
    secret_key: str
    algorithm: str
    access_token_expire_days: int

    class Config:
        env_file = '.env'


app_settings = AppSettings()
