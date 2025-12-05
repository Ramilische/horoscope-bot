from os import getenv
import pathlib
from datetime import datetime

import dotenv
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import ForeignKey, String, Integer, ARRAY, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

BASE_URL = pathlib.Path(__file__).parent.parent


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(env_file=BASE_URL.joinpath('.env/db.env'))

    def get_db_url_pg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings() # type: ignore
print(settings.get_db_url_pg())
engine = create_async_engine(url=settings.get_db_url_pg(), echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    is_paying: Mapped[bool] = mapped_column(Boolean, default=False)
    
    zodiac_sign_id: Mapped[int] = mapped_column(ForeignKey('signs.id'))
    zodiac_sign: Mapped['Sign'] = relationship(back_populates='users')


class Sign(Base):
    __tablename__ = 'signs'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    ru_name: Mapped[str] = mapped_column(String)
    users: Mapped[List['User']] = relationship(back_populates='zodiac_sign')


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print('Finished DB init')