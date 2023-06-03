import logging
import uuid

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy_utils import create_database, drop_database

from app.db import db_config
from app.db.db_config import DbConfig, ProjectParams
from app.main import app

logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()


@pytest.fixture()
def setup_test_db():
    """Фикстура, подготавливающая тестовую базу:
    создает случайное название
    создает базу с этим названием
    После завершения стека вызова фикстур теста, удаляет её
    """
    params = ProjectParams()
    temp_name = ".".join([uuid.uuid4().hex, "test"])
    mylogger.info(temp_name)
    db_data = DbConfig(
        DATABASE_HOST=params.DATABASE_HOST,
        DATABASE_USERNAME=params.DATABASE_USERNAME,
        DATABASE_PASSWORD=params.DATABASE_PASSWORD,
        DATABASE_DB_NAME=temp_name,
    )
    mylogger.info("Создана тестовая база")
    create_database(db_data.get_sync_db_url())
    yield db_data
    mylogger.info("удаляю тестовую базу")
    drop_database(db_data.get_sync_db_url())


@pytest.fixture()
def patch_config(setup_test_db, monkeypatch):
    """Фикстура, которая заменять исходный конфиг базы, на тестовый конфиг"""
    mylogger.info("Патчу конфиг к базе")
    setup_test_db.engine = create_async_engine(
        setup_test_db.get_async_db_url(), poolclass=NullPool
    )  # тут прихоидтся инжектить poolclass
    # чтобы в рамках одного теста можно было делать запрос к серверу + делать запросы через алхимию к базе
    monkeypatch.setattr(db_config, "DB_DATA", setup_test_db)
    return setup_test_db


@pytest.fixture()
def apply_migration(patch_config):
    """Фикструа применяющая миграции к тестовой базе"""
    cfg = Config("./alembic.ini")
    mylogger.info("Накатили миграшки к бд")
    command.upgrade(cfg, "487b41c7d1aa")
    return patch_config


@pytest.fixture()
def get_session(apply_migration: DbConfig):
    """Фикстура, для получения сессии sqlalchemy, используется в тестах базы"""
    return apply_migration.session_factory()


@pytest.fixture()
def client(apply_migration) -> TestClient:
    """Фикстура, для получения тест клиента, для тестов api"""
    return TestClient(app)
