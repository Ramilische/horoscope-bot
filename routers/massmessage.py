from os import getenv

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import dotenv
from db.requests import UserRepository
from utils.basiclogging import log_message
from bot import bot


dotenv.load_dotenv('.env/creds.env')
ADMIN_ID = getenv('ADMIN_ID')
router = Router()


class MassMessageStates(StatesGroup):
    getmessage = State()


@router.message(Command(commands=['massmessage', 'rassylka']))
async def make_mass_message(message: Message, state: FSMContext):
    log_message(message=message)
    
    user = message.from_user
    if user and str(user.id) == ADMIN_ID:
        await state.set_state(MassMessageStates.getmessage)
        await message.answer('Введите сообщение, которое нужно разослать')


@router.message(MassMessageStates.getmessage)
async def send_mass_message(message: Message, state: FSMContext):
    users = await UserRepository.get_all_users()
    if message.text:
        for user in users:
            await bot.send_message(chat_id=user.tg_id, text=message.text)
    await state.clear()