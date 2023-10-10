"""
Модуль с описанием моделей БД.
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base


class UserPassword(Base):
    """
    Модель, хранящая данные о пользователях.
    """
    __tablename__ = 'user_password'
    id = Column(Integer, primary_key=True)
    username = Column(
        String(100),
        unique=True,
        nullable=False
    )
    password = Column(String(50), nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return "UserPassword(id='%s', username='%s', password='%s')" % (
            self.id,
            self.username,
            self.password,
        )


class AccountIdToken(Base):
    """
    Модель, хранящая связь ID пользователя и его авторизационный токен.
    """

    __tablename__ = 'account_id_token'
    account_id = Column(Integer, primary_key=True)
    token = Column(String(200), unique=True, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
    __mapper_args__ = {"eager_defaults": True}

    def __repr__(self):
        return "UserIdToken(account_id='%s', token='%s')" % (
            self.account_id,
            self.token,
        )
