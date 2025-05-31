IS_DEBUG = True

import os
import socket
import struct
import subprocess
from datetime import datetime

import docker
from loguru import logger
from rich import print

client = docker.from_env()

fields = {
    "proc.name",
    "evt.num",
    "container.id",
    "proc.vpid",
    "thread.vtid",
    "evt.dir",
    "evt.type",
    "fd.name",
    "fd.num",
    "evt.category",
    "fd.cip",
    "fd.cport",
    "fd.sip",
    "fd.sport",
    "fd.is_server",
    "fd.ino",
    "evt.is_io_read",
    "evt.is_io_write",
    "evt.datetime",
    "evt.rawres",
    "proc.cmdline",
    "evt.buffer",
    "proc.env[malicious]",
}


def set_current_workpath(path: str):
    os.environ["CONTEXT_PATH"] = os.path.abspath(path)


def exec_command(command: list[str], check=True):
    print(f"executing command: {command}")
    try:
        subprocess.run(command, check=check)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error: {e.stderr}")
        raise


def get_current_time() -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    return timestamp


def ip_to_int(ip: str) -> int:
    """Convert an IPv4 address to a 32-bit integer."""
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def int_to_ip(ip_int: int) -> str:
    """Convert a 32-bit integer to an IPv4 address."""
    return socket.inet_ntoa(struct.pack("!I", ip_int))


def invert_ip(ip: str) -> str:
    """Invert an IPv4 address."""
    ip_int = ip_to_int(ip)
    inverted_ip_int = ~ip_int & 0xFFFFFFFF  # Invert bits and ensure it's within 32 bits
    return int_to_ip(inverted_ip_int)
