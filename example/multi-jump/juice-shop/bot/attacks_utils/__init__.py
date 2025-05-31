import socket
import struct

from attacks_utils import payload_server


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
