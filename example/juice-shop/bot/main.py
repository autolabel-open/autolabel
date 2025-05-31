import asyncio
import random
import time
from typing import NoReturn

import attacks_utils.payload_server
import attacks_utils.reverse_shell
import behaviors.attack
import behaviors.normal
from behaviors import States, choose_and_exec_behavior, special
from loguru import logger
from user import user_manager

from config import settings
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
        if settings.poison:
            await sleep(random.random())
        elif settings.attack:
            break
        else:
            await sleep(random.random() * 2)


if __name__ == "__main__":
    asyncio.run(main())
