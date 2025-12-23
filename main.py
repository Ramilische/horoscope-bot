import asyncio
from os import getenv
import sys
import time

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods import send_message
import dotenv
import apscheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from parsing import get_ru_horoscope, update_ru_horoscopes
from db.requests import UserRepository, SignRepository
from db.session import init_db, IS_TEST
from utils.collections import zodiac_en_to_ru, signs_en
from utils.keyboards import to_time, hour_keyboard, zodiac_keyboard

dotenv.load_dotenv('.env/creds.env')
TOKEN = getenv("BOT_TOKEN")

start_message = """Привет, я бот, отправляющий гороскопы
Напиши /today чтобы получить гороскоп на сегодня
Напиши /daily чтобы включить (или отключить) ежедневную отправку гороскопов"""

if IS_TEST:
    start_message += '\n\nРаботаю в тестовом режиме'

if TOKEN is None:
    print('Файл с токеном не прочитался')
    sys.exit()

dp = Dispatcher()
bot = Bot(token=str(TOKEN))


# Command handler
@dp.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    user = message.from_user
    if user:
        if not await UserRepository.user_exists(tg_id=user.id):
            await pick_a_sign(message)
            
    if message.chat.type == 'private':
        # Рекламировать свою подписку в групповом чате неприлично, поэтому логика такая
        just_payment = InlineKeyboardBuilder()
        just_payment.row(InlineKeyboardButton(text='💳 Какая-нибудь функция скоро будет за пэйволлом', callback_data='pay'))
        await message.answer(start_message, reply_markup=just_payment.as_markup())
    else:
        await message.answer(start_message)


@dp.callback_query(F.data == 'pay')
async def pay(callback: CallbackQuery):
    if callback.message:
        await callback.message.answer(text='Мне, конечно, приятно, но ЮКассу я еще не подключил, подожди немного')
        
    await callback.answer()


@dp.message(Command('today'))
async def today(message: Message) -> None:
    user = message.from_user
    if user:
        user_exists = await UserRepository.user_exists(tg_id=user.id)
        if not user_exists:
            await message.answer('Сначала выбери свой знак с помощью команды /pick')
        else:
            user = await UserRepository.get_user(tg_id=user.id)
            if user:
                await message.answer(await get_today_horo(user.tg_id))


async def get_today_horo(tg_id: int):
    sign = await UserRepository.get_sign(tg_id=tg_id)
    horoscope = await get_ru_horoscope(sign=sign)
    return horoscope


@dp.message(Command('pick'))
async def pick_a_sign(message: Message):
    user = message.from_user
    if user:
        user_exists = await UserRepository.user_exists(tg_id=user.id)
        if not user_exists:
            await UserRepository.add_user(tg_id=user.id)
    
        await message.answer('Выберите свой знак зодиака', reply_markup=zodiac_keyboard.as_markup())


@dp.callback_query(F.data.in_(signs_en))
async def sign_callback(callback: CallbackQuery):
    user = callback.from_user
    if callback.message and callback.data and user:
        await UserRepository.update_sign(tg_id=user.id, sign=callback.data)
        await callback.message.answer(text=f'Теперь ваш знак - {zodiac_en_to_ru[callback.data]}')
    await callback.answer()


@dp.message(Command('time'))
async def pick_a_time(message: Message):
    user = message.from_user
    if user:
        await message.answer(text='Выберите время по МСК для отправки ежедневного гороскопа', reply_markup=hour_keyboard.as_markup())


@dp.callback_query(F.data.in_(['hour' + str(i) for i in range(24)]))
async def time_callback(callback: CallbackQuery):
    user = callback.from_user
    if user:
        hour = int(callback.data[-1]) if len(callback.data) == 5 else int(callback.data[-2:]) # type: ignore
        await UserRepository.update_time(tg_id=user.id, hour=hour)
        if callback.message:
            await callback.message.answer(text=f'Теперь ежедневный гороскоп будет приходить в {to_time(hour=hour)} по МСК')
        await callback.answer()


@dp.message(Command(commands=['subscribe', 'daily', 'morning']))
async def daily_switch(message: Message):
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


@dp.callback_query(F.data == 'sub')
@dp.callback_query(F.data == 'unsub')
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


# Run the bot
async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_ru_horoscopes, 'interval', hours=1, id='update_horoscopes')
    scheduler.add_job(daily_horo_send, 'cron', hour='0-23', minute=0)
    scheduler.start()

    await init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
          