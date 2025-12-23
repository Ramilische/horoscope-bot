from os import getenv
import pathlib

import dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from db.models import Base


BASE_URL = pathlib.Path(__file__).parent.parent
dotenv.load_dotenv('.env/config.env')
IS_TEST = getenv('IS_TEST')


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    TEST_USER: str
    TEST_PASSWORD: str
    TEST_HOST: str
    TEST_PORT: int
    TEST_NAME: str

    model_config = SettingsConfigDict(env_file=BASE_URL.joinpath('.env/db.env'))

    def get_db_url_pg(self):
        if IS_TEST == 'True':
            return f"postgresql+asyncpg://{self.TEST_USER}:{self.TEST_PASSWORD}@{self.TEST_HOST}:{self.TEST_PORT}/{self.TEST_NAME}"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        



settings = Settings() # type: ignore
engine = create_async_engine(url=settings.get_db_url_pg(), echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print('Finished DB init')
        return 0