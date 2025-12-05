from sys import stdout

from sqlalchemy import select, update, delete, func
from pydantic import BaseModel, ConfigDict
from typing import List

from db.models import async_session, User, Sign


class UserRepository:
    @classmethod
    async def add_user(cls, tg_id: int, sign: str = '') -> User:
        """
        Проверяет, существует ли пользователь. Если нет - создает запись в БД.
        Функция используется при /start и не только
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if user:
                return user

            zodiac_sign = await session.scalar(select(Sign).where(Sign.name == sign))
            new_user = User(tg_id=tg_id, zodiac_sign=zodiac_sign)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

            return new_user
    
    @classmethod
    async def update_paying_status(cls, tg_id: int, is_paying: bool):
        """
        Меняет поле is_paying на новое значение
        Функция используется при продлении подписки или при окончании ее срока действия
        """
        async with async_session() as session:
            user = await cls.add_user(tg_id=tg_id)
            if user.is_paying == is_paying:
                return "No changes"
            
            user.is_paying = is_paying
            res = await session.scalar(update(User).where(User.tg_id == tg_id).values(is_paying=is_paying))
            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def update_sign(cls, tg_id: int, sign: str):
        """
        Меняет поле zodiac_sign на новое значение
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            zodiac_sign = await SignRepository.get_sign(name=sign)
            if not user:
                stdout.write('ЮЗЕР НУЛЛ БЛЯЯЯЯЯТЬ\n')
            if user and zodiac_sign and user.zodiac_sign_id == zodiac_sign.id:
                return "No changes"
            
            if user and zodiac_sign:
                user.zodiac_sign = zodiac_sign

            await session.commit()
            await session.refresh(user)
    
    @classmethod
    async def get_sign(cls, tg_id: int):
        """
        Узнает знак зодиака пользователя
        """
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.id == tg_id))
            if user:
                sign = await session.scalar(select(Sign).where(Sign.id == user.zodiac_sign_id))
                if sign:
                    return sign.name
                
            return 'No sign'


class SignRepository:
    @classmethod
    async def get_sign(cls, name: str = 'none', runame: str = 'none'):
        """
        Возвращает знак зодиака по имени
        """
        async with async_session() as session:
            sign = None
            
            if name != 'none':
                sign = await session.scalar(select(Sign).where(Sign.name == name))
                return sign
            if runame != 'none':
                sign = await session.scalar(select(Sign).where(Sign.ru_name == runame))
                return sign
            
            return sign
                
    
    @classmethod
    async def add_sign(cls, name: str, runame: str):
        """
        Добавляет новый знак. Будет полезно, если появятся знаки помимо знаков зодиака
        """
        async with async_session() as session:
            sign = await session.scalar(select(Sign).where(Sign.name == name))
            if sign:
                return sign
            
            new_sign = Sign(name=name, ru_name=runame)
            session.add(new_sign)
            await session.commit()
            await session.refresh(new_sign)
            
            return new_sign
