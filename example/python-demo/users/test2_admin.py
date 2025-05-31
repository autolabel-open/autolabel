import asyncio
import random
import string
from multiprocessing import Process
from time import sleep

import aiohttp
from yarl import URL

host = "192.168.123.2"
prefix = f"http://{host}:8000"


def randstr(length: int) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


async def get_raw(session: aiohttp.ClientSession, url: str):
    response = await session.get(url)
    await response.read()


async def main():

    while True:
        async with aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True)
        ) as session:
            try:
                res = await session.post(
                    f"{prefix}/admin/login",
                    json={"username": "admin", "password": "123456"},
                )
                await res.json()
                # await asyncio.sleep(random.choice([0, 30]))
                items = [
                    {"name": randstr(10), "price": random.random() * 10000}
                    for _ in range(random.randint(2, 10))
                ]
                res = await session.post(f"{prefix}/admin/edit", json=items)
                print(await res.json())

                from urllib.parse import quote

                expr = f"{random.randint(10, 100)} + {random.randint(10, 100)}"
                encoded_expr = quote(expr, safe="")

                res = await session.get(f"{prefix}/solve/{encoded_expr}")
                print(await res.text())

                await asyncio.sleep(random.randint(1, 2))
            except Exception as e:
                print(e)


asyncio.run(main())
