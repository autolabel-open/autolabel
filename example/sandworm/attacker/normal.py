import os
import random
import time

cmds = [
    "ping",
    "ping -c 3 127.0.0.1",
    "nslookup",
    "pwd",
    "ls",
    "ls -alh .",
    "dig",
    "netstat",
    "netstat -tunlp",
    "ss",
    "ip",
    "ip a",
    "uptime",
    "free -h",
    "vmstat",
    "ps",
    "ps -ef",
    "curl",
]

ip = "192.168.0.5"

while True:
    cmd = random.choice(cmds)
    if cmd == "curl":
        cmd = f"curl -k https://{ip}"
    else:
        cmd = f"sshpass -p 'MYPASSWORD' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null myuser@{ip} {cmd}"
    os.system(cmd)
    time.sleep(10)
