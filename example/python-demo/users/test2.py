import asyncio
import random
import string

import aiohttp

host = "192.168.123.2"
prefix = f"http://{host}:8000"


async def get_raw(session: aiohttp.ClientSession, url: str):
    response = await session.get(url)
    await response.read()


async def main():
    while True:
        try:
            username = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(10)
            )
            password = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(10)
            )
            async with aiohttp.ClientSession(
                cookie_jar=aiohttp.CookieJar(unsafe=True)
            ) as session:
                await session.post(
                    f"{prefix}/register",
                    json={"username": username, "password": password},
                )
                await asyncio.sleep(1)
                res = await session.post(
                    f"{prefix}/login", json={"username": username, "password": password}
                )
                await asyncio.sleep(1)
                while True:
                    try:
                        async with session.get(f"{prefix}/items") as res:
                            items = await res.json()
                        await asyncio.sleep(random.choice([0, 1]))

                        item = random.choice(items)
                        print(item)
                        price = item["price"]
                        async with session.get(f"{prefix}/balance") as res:
                            balance = float(await res.text())
                        await asyncio.sleep(random.choice([0, 1]))

                        if balance < price:
                            res = await session.get(f"{prefix}/charge/10000")
                            await res.json()
                        await session.get(f"{prefix}/buy/{item['name']}")
                        await asyncio.sleep(random.choice([random.randint(1, 2), 0]))
                    except Exception as e:
                        print(e)
        except aiohttp.ClientError as e:
            print(e)


asyncio.run(main())
# processes = []
# for i in range(16):
#     p = Process(target=lambda: )
#     p.start()
#     processes.append(p)
#     sleep(1)
# for p in processes:
#     p.join()
