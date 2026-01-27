from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from parsing import get_ru_horoscope
from db.requests import UserRepository
from utils.basiclogging import log_message


router = Router()


async def get_today_horo(tg_id: int):
    sign = await UserRepository.get_sign(tg_id=tg_id)
    horoscope = await get_ru_horoscope(sign=sign)
    return horoscope


@router.message(Command('today'))
async def today(message: Message) -> None:
    log_message(message=message)
    
    user = message.from_user
    if user:
        user_exists = await UserRepository.user_exists(tg_id=user.id)
        if not user_exists:
            await message.answer('Сначала выбери свой знак с помощью команды /pick')
        else:
            user = await UserRepository.get_user(tg_id=user.id)
            if user:
                await message.answer(await get_today_horo(user.tg_id))