import os

from pydantic import BaseSettings


class ProjectParams(BaseSettings):
    """Класс, который читает секреты из .env файла"""

    DATABASE_HOST: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_DB_NAME: str

    class Config:
        env_file = os.path.abspath(r"./.env")
