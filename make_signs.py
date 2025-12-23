from db.session import init_db
from db.requests import UserRepository, SignRepository
from utils.collections import signs
import asyncio


async def main():
    await init_db()
    for sign in signs:
        await SignRepository.add_sign(sign[0], sign[1])
    


if __name__ == '__main__':
    asyncio.run(main())
    