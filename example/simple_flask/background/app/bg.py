import time

import requests
from loguru import logger
from rich import print

url = "http://192.168.123.4:5000"
urls = [f"{url}/a", f"{url}/b"]

while True:
    try:
        for url_ in urls:
            resp = requests.get(url_)
            print(resp.content.decode())
    except Exception as e:
        logger.exception(e)
    finally:
        time.sleep(1)
