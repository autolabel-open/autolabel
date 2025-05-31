import logging
import os
import re
import sys


from loguru import logger

from config import settings


def register() -> None:
    level = "INFO"
    # if settings.debug:
    #     level = "DEBUG"

    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": level},
        ]
    )

    logger.debug("IS_DEBUG: True")


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        if re.search(r"\d+ changes? detected:", record.getMessage()):
            return

        # Get corresponding Loguru level if it exists
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame = None
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
