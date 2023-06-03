from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from utils.secrets_reader import ProjectParams

DATABASE_URL_CONST = "postgresql+asyncpg://%s:%s@%s/%s"
SYNC_DATABASE_URL_CONST = "postgresql://%s:%s@%s/%s"


class DbConfig:
    """Класс конфиг бд, где храню всю необходимую информацию про неё"""

    _self = None

    def __new__(cls, *args, **kwargs) -> DbConfig:  # noqa:ANN002,ANN003
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self, DATABASE_HOST: str, DATABASE_USERNAME: str, DATABASE_PASSWORD: str, DATABASE_DB_NAME: str) -> None:
        self.host = DATABASE_HOST
        self.username = DATABASE_USERNAME
        self.password = DATABASE_PASSWORD
        self.db_name = DATABASE_DB_NAME
        self.engine = None

    def get_async_db_url(self) -> str:
        """Используется для установки рабочего пула с базой"""
        return DATABASE_URL_CONST % (self.username, self.password, self.host, self.db_name)

    def get_sync_db_url(self) -> str:
        """Синхронный движок используется при работе с миграциями"""
        return SYNC_DATABASE_URL_CONST % (self.username, self.password, self.host, self.db_name)

    def get_engine(self) -> AsyncEngine:
        """Получаю engine к текущей базе"""
        if not self.engine:
            url = self.get_async_db_url()
            self.engine = create_async_engine(url, echo=False)
        return self.engine

    def session_factory(self) -> Session:
        engine = self.get_engine()
        return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


params = ProjectParams()  # Загружаю параметры из .env файла

DB_DATA = DbConfig(
    DATABASE_HOST=params.DATABASE_HOST,
    DATABASE_USERNAME=params.DATABASE_USERNAME,
    DATABASE_PASSWORD=params.DATABASE_PASSWORD,
    DATABASE_DB_NAME=params.DATABASE_DB_NAME,
)
