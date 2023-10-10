"""
Модуль с pydantic-моделями
для валидации данных.
"""
from typing import Optional

from pydantic import BaseModel


class FilesInfo(BaseModel):
    account_id: Optional[str] = None
    files: list


class PingInfo(BaseModel):
    db: float
    bucket: float
    cache: float


class User(BaseModel):
    username: str
    password: str


class RegisterStatus(BaseModel):
    status: str
    username: str
    token: Optional[str] = None
