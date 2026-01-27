import sys
from os import getenv

import dotenv
from aiogram import Bot


dotenv.load_dotenv('.env/creds.env')
TOKEN = getenv('BOT_TOKEN')
ADMIN_ID = getenv('ADMIN_ID')
if TOKEN is None:
    print('Файл с токеном не прочитался')
    sys.exit()

bot = Bot(token=str(TOKEN))
