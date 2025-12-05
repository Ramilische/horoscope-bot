import asyncio
from os import getenv
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
import dotenv

from parsing import get_ru_horoscope
from db.requests import UserRepository, SignRepository
from db.models import init_db
from utils.collections import zodiac_en_to_ru

dotenv.load_dotenv('.env/creds.env')
TOKEN = getenv("BOT_TOKEN")

start_message = """Привет, я бот, отправляющий гороскопы
Для начала работы напиши /pick чтобы выбрать свой знак зодиака
Напиши /today чтобы получить гороскоп на сегодня"""

if TOKEN is None:
    print('Файл с токеном не прочитался')
    sys.exit()

dp = Dispatcher()


# Command handler
@dp.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    just_payment = InlineKeyboardBuilder()
    just_payment.row(InlineKeyboardButton(text='💳 Утренний гороскоп всего за 100 рублей в месяц', callback_data='pay'))
    await message.answer(start_message, reply_markup=just_payment.as_markup())


@dp.callback_query(F.data == 'pay')
async def pay(callback: CallbackQuery):
    if callback.message:
        await callback.message.answer(text='Здесь должна быть оплата')
    await callback.answer()


@dp.message(Command('today'))
async def today(message: Message) -> None:
    tg_user = message.from_user
    if tg_user:
        user = await UserRepository.add_user(tg_id=tg_user.id, sign='aries')
        if user:
            sign = await UserRepository.get_sign(tg_id=user.id)
    horoscope = await get_ru_horoscope(sign=sign)
    await message.answer(horoscope)


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


# Run the bot
async def main() -> None:
    await init_db()
    bot = Bot(token=str(TOKEN))
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
          