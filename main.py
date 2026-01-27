import asyncio
from os import getenv
import sys
import time

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from parsing import get_ru_horoscope, update_ru_horoscopes
from db.requests import UserRepository, SignRepository
from db.session import init_db, IS_TEST
from utils.collections import zodiac_en_to_ru, signs_en
from utils.keyboards import to_time, hour_keyboard, zodiac_keyboard
from utils.basiclogging import log_message
from routers import daily, payment, sign, start, horo, massmessage
from bot import bot


dp = Dispatcher()
dp.include_routers(start.router, daily.router, horo.router, sign.router, payment.router, massmessage.router)


# Run the bot
async def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_ru_horoscopes, 'interval', hours=1, id='update_horoscopes')
    scheduler.add_job(daily.daily_horo_send, 'cron', hour='0-23', minute=0)
    scheduler.start()

    await init_db()
    if IS_TEST:
        print('************************\nРаботаю в тестовом режиме\n************************')
    await update_ru_horoscopes()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
