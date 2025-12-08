from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def to_time(hour: int):
    if hour < 10:
        return f'0{hour}:00'
    return f'{hour}:00'


zodiac_keyboard = InlineKeyboardBuilder()
zodiac_keyboard.row(
    InlineKeyboardButton(text='Овен', callback_data='aries'), 
    InlineKeyboardButton(text='Телец', callback_data='taurus'),
    InlineKeyboardButton(text='Близнецы', callback_data='gemini'),
)
zodiac_keyboard.row(
    InlineKeyboardButton(text='Рак', callback_data='cancer'),
    InlineKeyboardButton(text='Лев', callback_data='leo'), 
    InlineKeyboardButton(text='Дева', callback_data='virgo'), 
)
zodiac_keyboard.row(
    InlineKeyboardButton(text='Весы', callback_data='libra'), 
    InlineKeyboardButton(text='Скорпион', callback_data='scorpio'), 
    InlineKeyboardButton(text='Стрелец', callback_data='sagittarius'), 
)
zodiac_keyboard.row(
    InlineKeyboardButton(text='Козерог', callback_data='capricorn'), 
    InlineKeyboardButton(text='Водолей', callback_data='aquarius'), 
    InlineKeyboardButton(text='Рыбы', callback_data='pisces')
)

hour_keyboard = InlineKeyboardBuilder()
hour_rows = 6
count = 0
i = 0
while count < 24:
    hour_keyboard.row(*[InlineKeyboardButton(text=to_time(count + j), callback_data='hour'+str(count + j)) for j in range(min(24 // hour_rows, 24 - count))])
    count += 24 // hour_rows
    i += 1