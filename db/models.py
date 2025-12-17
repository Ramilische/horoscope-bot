from typing import List
from sqlalchemy import ForeignKey, String, Integer, ARRAY, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    hour: Mapped[int] = mapped_column(Integer, default=7)
    is_paying: Mapped[bool] = mapped_column(Boolean, default=False)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    zodiac_sign_id: Mapped[int] = mapped_column(ForeignKey('signs.id'))
    zodiac_sign: Mapped['Sign'] = relationship(back_populates='users')


class Sign(Base):
    __tablename__ = 'signs'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    ru_name: Mapped[str] = mapped_column(String)
    users: Mapped[List['User']] = relationship(back_populates='zodiac_sign')
