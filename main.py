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
from db.models import init_db
from utils.collections import zodiac_en_to_ru

dotenv.load_dotenv('.env/creds.env')
TOKEN = getenv("BOT_TOKEN")

start_message = """Привет, я бот, отправляющий гороскопы
Напиши /today чтобы получить гороскоп на сегодня"""

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
            
    if message.chat.is_direct_messages:
        # Рекламировать свою подписку в групповом чате неприлично, поэтому логика такая
        just_payment = InlineKeyboardBuilder()
        just_payment.row(InlineKeyboardButton(text='💳 Утренний гороскоп всего за 100 рублей в месяц', callback_data='pay'))
        await message.answer(start_message, reply_markup=just_payment.as_markup())
    else:
        await message.answer(start_message)


@dp.callback_query(F.data == 'pay')
async def pay(callback: CallbackQuery):
    if callback.message:
        await callback.message.answer(text='Здесь должна быть оплата')
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
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='Овен', callback_data='aries'), 
        InlineKeyboardButton(text='Телец', callback_data='taurus'),
        InlineKeyboardButton(text='Близнецы', callback_data='gemini'),
    )
    builder.row(
        InlineKeyboardButton(text='Рак', callback_data='cancer'),
        InlineKeyboardButton(text='Лев', callback_data='leo'), 
        InlineKeyboardButton(text='Дева', callback_data='virgo'), 
    )
    builder.row(
        InlineKeyboardButton(text='Весы', callback_data='libra'), 
        InlineKeyboardButton(text='Скорпион', callback_data='scorpio'), 
        InlineKeyboardButton(text='Стрелец', callback_data='sagittarius'), 
    )
    builder.row(
        InlineKeyboardButton(text='Козерог', callback_data='capricorn'), 
        InlineKeyboardButton(text='Водолей', callback_data='aquarius'), 
        InlineKeyboardButton(text='Рыбы', callback_data='pisces')
    )
    user = message.from_user
    if user:
        user_exists = await UserRepository.user_exists(tg_id=user.id)
        if not user_exists:
            await UserRepository.add_user(tg_id=user.id)
    
        await message.answer('Выберите свой знак зодиака', reply_markup=builder.as_markup())


@dp.callback_query(F.data == 'aries')
@dp.callback_query(F.data == 'taurus')
@dp.callback_query(F.data == 'gemini')
@dp.callback_query(F.data == 'cancer')
@dp.callback_query(F.data == 'leo')
@dp.callback_query(F.data == 'virgo')
@dp.callback_query(F.data == 'libra')
@dp.callback_query(F.data == 'scorpio' )
@dp.callback_query(F.data == 'sagittarius')
@dp.callback_query(F.data == 'capricorn')
@dp.callback_query(F.data == 'aquarius')
@dp.callback_query(F.data == 'pisces')
async def sign_callback(callback: CallbackQuery):
    user = callback.from_user
    if callback.message and callback.data and user:
        await UserRepository.update_sign(tg_id=user.id, sign=callback.data)
        await callback.message.answer(text=f'Теперь ваш знак - {zodiac_en_to_ru[callback.data]}')
    await callback.answer()


@dp.message(Command(commands=['subscribe', 'daily', 'morning']))
async def daily_switch(message: Message):
    user = message.from_user
    if user:
        # is_paying = UserRepository.get_paying_status(tg_id=user.id)
        is_subscribed = UserRepository.get_subscription_status(tg_id=user.id)
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
        await bot.send_message(chat_id=user.tg_id, text=await get_today_horo(user.tg_id))


# Run the bot
async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_ru_horoscopes, 'interval', hours=1, id='update_horoscopes')
    scheduler.add_job(daily_horo_send, 'cron', hour='0-23', minute=32)
    scheduler.start()

    await init_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
          