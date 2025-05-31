import sys
from scapy.route import conf
from settings import settings

if len(sys.argv) != 3:
    print(f"{settings.python_executable} ns_route.py {key} {val}")
    exit(1)

if __name__ == "__main__":
    key = sys.argv[1]
    val = sys.argv[2]
    print(conf.route.route(val)[1], conf.route.route(key)[1])
