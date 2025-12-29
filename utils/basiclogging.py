import time
from aiogram.types import Message


def timenow():
    currtime = time.localtime()
    
    year = currtime.tm_year
    mon = '0' + str(currtime.tm_mon) if currtime.tm_mon < 10 else str(currtime.tm_mon)
    day = '0' + str(currtime.tm_mday) if currtime.tm_mday < 10 else str(currtime.tm_mday)
    hour = '0' + str(currtime.tm_hour) if currtime.tm_hour < 10 else str(currtime.tm_hour)
    minute = '0' + str(currtime.tm_min) if currtime.tm_min < 10 else str(currtime.tm_min)
    sec = '0' + str(currtime.tm_sec) if currtime.tm_sec < 10 else str(currtime.tm_sec)
    
    return year, mon, day, hour, minute, sec


def log_message(message: Message):
    user = message.from_user
    year, mon, day, hour, minute, sec = timenow()
    filename = f'logs/log-{year}-{mon}-{day}.txt'
    if user:
        text = f'{hour}:{minute}:{sec} [{user.username}] - {message.text}' + '\n'
        with open(filename, mode='a', encoding='utf-8') as file:
            file.write(text)
