import http.server
import multiprocessing
import os
import socketserver

from loguru import logger


def start_payload_server() -> None:
    os.makedirs("assets/tmp", exist_ok=True)
    os.chdir("assets")
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", 8000), handler) as httpd:
        logger.info(f"Serving payload server http://0.0.0.0:{8000}")
        httpd.serve_forever()


payload_server = multiprocessing.Process(target=start_payload_server)
payload_server.start()
