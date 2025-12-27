import time
from aiogram.types import Message


def log_tg_message(message: Message):
    pass


def log_message(command: str = '', message: str = '', username: str = '', first_name: str = '', last_name: str = ''):
    currtime = time.localtime()
    hour = '0' + str(currtime.tm_hour) if currtime.tm_hour < 10 else str(currtime.tm_hour)
    minute = '0' + str(currtime.tm_min) if currtime.tm_min < 10 else str(currtime.tm_min)
    sec = '0' + str(currtime.tm_sec) if currtime.tm_sec < 10 else str(currtime.tm_sec)
    mon = '0' + str(currtime.tm_mon) if currtime.tm_mon < 10 else str(currtime.tm_mon)
    day = '0' + str(currtime.tm_mday) if currtime.tm_mday < 10 else str(currtime.tm_mday)
    filename = f'logs/log-{currtime.tm_year}-{mon}-{day}.txt'
    text = f'{hour}:{minute}:{sec} [{username}] - {message}' + '\n'
    with open(filename, mode='a', encoding='utf-8') as file:
        file.write(text)
