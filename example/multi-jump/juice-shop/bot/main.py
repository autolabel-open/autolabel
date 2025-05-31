import asyncio
import random
import time
from typing import NoReturn

from loguru import logger

import behaviors.attack
import behaviors.normal
from attacks_utils.payload_server import payload_server
from attacks_utils.reverse_shell import reverse_shell
from behaviors import States, choose_and_exec_behavior, special
from config import settings
from user import user_manager
from utils import sleep


async def main() -> NoReturn:
    await sleep(20)
    await special.init_app()
    await user_manager.register()
    logger.info("Finished init")

    current_state = next(s for s in States)

    if settings.attack:
        END_TIME = 30
    else:
        END_TIME = 10000

    for _ in range(END_TIME):
        logger.info(f"{_} / {END_TIME}")
        try:
            current_state = await choose_and_exec_behavior(
                current_state, settings.attack
            )
        except Exception as e:
            logger.exception(e)
        await sleep(random.randint(5, 10))

    payload_server.kill()
    reverse_shell.kill()


if __name__ == "__main__":
    asyncio.run(main())
