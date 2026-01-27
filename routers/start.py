from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db.requests import UserRepository
from db.session import IS_TEST
from utils.keyboards import just_payment
from utils.basiclogging import log_message
from routers.sign import pick_a_sign


start_message = """Привет, я бот, отправляющий гороскопы
Напиши /today чтобы получить гороскоп на сегодня
Напиши /daily чтобы включить (или отключить) ежедневную отправку гороскопов"""

if IS_TEST:
    start_message += '\n\nРаботаю в тестовом режиме'

router = Router()


# Command handler
@router.message(Command('start'))
async def command_start_handler(message: Message) -> None:
    log_message(message=message)
    
    user = message.from_user
    if user:
        if not await UserRepository.user_exists(tg_id=user.id):
            await pick_a_sign(message)
            
    if message.chat.type == 'private':
        # Рекламировать свою подписку в групповом чате неприлично, поэтому логика такая
        await message.answer(start_message, reply_markup=just_payment.as_markup())
    else:
        await message.answer(start_message)