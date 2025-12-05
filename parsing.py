import asyncio
import time
import json

import requests_async
from bs4 import BeautifulSoup

signs = {
    "aries": 1,
    "taurus": 2,
    "gemini": 3,
    "cancer": 4,
    "leo": 5,
    "virgo": 6,
    "libra": 7,
    "scorpio": 8,
    "sagittarius": 9,
    "capricorn": 10,
    "aquarius": 11,
    "pisces": 12
}


async def parse_en_horoscope(day: str, sign: str):
    res = await requests_async.get(f'https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-{day}.aspx?sign={signs[sign.lower()]}')
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.find('div', attrs={'class': 'main-horoscope'})
    if data:
        data = data.find('p')
    else:
        return 'We could not get the horoscope you want, try later'
    if data:
        return data.text
    else:
        return 'We could not get the horoscope you want, try later'


async def parse_ru_horoscope(sign: str):
    res = await requests_async.get(f'https://1001goroskop.ru/?znak={sign.lower()}')
    soup = BeautifulSoup(res.content, 'html.parser')
    data = soup.find('div', attrs={'itemprop': 'description'})
    if data:
        data = data.find('p')
    else:
        return 'Не получилось достать нужный гороскоп, попробуйте позже'
    if data:
        return data.text
    else:
        return 'Не получилось достать нужный гороскоп, попробуйте позже'


async def update_en_horoscopes():
    en = dict()
    for sign in signs:
        res_en = await parse_en_horoscope('today', sign)
        en[sign] = res_en
        time.sleep(0.1)
    with open('en.json', 'w', encoding='utf-8') as file_en:
        json.dump(en, file_en, ensure_ascii=False, indent=4)


async def update_ru_horoscopes():
    ru = dict()
    for sign in signs:
        res_ru = await parse_ru_horoscope(sign)
        ru[sign] = res_ru
        time.sleep(0.1)
    with open('ru.json', 'w', encoding='utf-8') as file_ru:
        json.dump(ru, file_ru, ensure_ascii=False, indent=4)
    

async def get_ru_horoscope(sign: str):
    with open('ru.json', 'r', encoding='utf-8') as file_ru:
        if file_ru:
            res = json.load(file_ru)[sign.lower()]
        else:
            return 'File does not exist'
    return res


async def main():
    await update_ru_horoscopes()


if __name__ == '__main__':
    asyncio.run(main())
