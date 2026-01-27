from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from db.requests import UserRepository
from utils.collections import zodiac_en_to_ru, signs_en
from utils.keyboards import zodiac_keyboard
from utils.basiclogging import log_message


router = Router()


@router.message(Command('pick'))
async def pick_a_sign(message: Message):
    log_message(message=message)
    
    user = message.from_user
    if user:
        user_exists = await UserRepository.user_exists(tg_id=user.id)
        if not user_exists:
            await UserRepository.add_user(tg_id=user.id)
    
        await message.answer('Выберите свой знак зодиака', reply_markup=zodiac_keyboard.as_markup())


@router.callback_query(F.data.in_(signs_en))
async def sign_callback(callback: CallbackQuery):
    user = callback.from_user
    if callback.message and callback.data and user:
        await UserRepository.update_sign(tg_id=user.id, sign=callback.data)
        await callback.message.answer(text=f'Теперь ваш знак - {zodiac_en_to_ru[callback.data]}')
    await callback.answer()