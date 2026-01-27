from aiogram import Router, F
from aiogram.types import CallbackQuery


router = Router()


@router.callback_query(F.data == 'pay')
async def pay(callback: CallbackQuery):
    if callback.message:
        await callback.message.answer(text='Мне, конечно, приятно, но ЮКассу я еще не подключил, подожди немного')
        
    await callback.answer()