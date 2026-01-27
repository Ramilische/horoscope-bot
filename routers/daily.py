import time

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.requests import UserRepository
from utils.keyboards import to_time, hour_keyboard
from utils.basiclogging import log_message
from routers.horo import get_today_horo
from bot import bot


router = Router(name='daily')


@router.message(Command('time'))
async def pick_a_time(message: Message):
    log_message(message=message)
    
    user = message.from_user
    if user:
        await message.answer(text='Выберите время по МСК для отправки ежедневного гороскопа', reply_markup=hour_keyboard.as_markup())


@router.callback_query(F.data.in_(['hour' + str(i) for i in range(24)]))
async def time_callback(callback: CallbackQuery):
    user = callback.from_user
    if user:
        hour = int(callback.data[-1]) if len(callback.data) == 5 else int(callback.data[-2:]) # type: ignore
        await UserRepository.update_time(tg_id=user.id, hour=hour)
        if callback.message:
            await callback.message.answer(text=f'Теперь ежедневный гороскоп будет приходить в {to_time(hour=hour)} по МСК')
        await callback.answer()


@router.message(Command(commands=['subscribe', 'daily', 'morning']))
async def daily_switch(message: Message):
    log_message(message=message)
    
    user = message.from_user
    if user:
        # is_paying = UserRepository.get_paying_status(tg_id=user.id)
        is_subscribed = await UserRepository.get_subscription_status(tg_id=user.id)
        builder = InlineKeyboardBuilder()
        
        if is_subscribed:
            message_text = 'Вы хотите отписаться от ежедневных гороскопов?'
            builder.add(InlineKeyboardButton(text='Да', callback_data='unsub'))
        else:
            message_text = 'Вы хотите подписаться на ежедневные гороскопы?'
            builder.add(InlineKeyboardButton(text='Да', callback_data='sub'))
        await message.answer(message_text, reply_markup=builder.as_markup())


@router.callback_query(F.data == 'sub')
@router.callback_query(F.data == 'unsub')
async def daily_horo_callback(callback: CallbackQuery):
    user = callback.from_user
    if callback.message and callback.data and user:
        is_subscribed = True if callback.data == 'sub' else False
        message_text = 'Вы подписались на ежедневные гороскопы' if callback.data == 'sub' else 'Вы отписались от ежедневных гороскопов'
        await UserRepository.update_subscription_status(tg_id=user.id, is_subscribed=is_subscribed)
        await callback.answer(message_text)


async def daily_horo_send():
    hour = time.localtime(time.time()).tm_hour
    users = await UserRepository.get_all_users_for_hour(hour=hour)
    for user in users:
        if user.is_subscribed:
            await bot.send_message(chat_id=user.tg_id, text=await get_today_horo(user.tg_id))
