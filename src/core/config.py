"""
Модуль с описанием основных настроек.
"""
import logging
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING


logging_config.dictConfig(LOGGING)
logger = logging.getLogger()


class AppSettings(BaseSettings):
    project_host = Field('0.0.0.0', env='PROJECT_HOST')
    project_port = Field(8080, env='PROJECT_PORT')

    nginx_host = Field('nginx', env='NGINX_HOST')
    nginx_port = Field(80, env='NGINX_PORT')

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
