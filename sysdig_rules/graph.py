import json
import os
import re
from datetime import datetime
from io import TextIOWrapper

from logs import CAPTURED_PATH
from merge_set import MergeSet
from net_trace import ConnInfo

from utils import exec_command


class Node:
    GLOBAL_ID = 0
    ID_MAP: dict[int, "Node"] = {}

    def __init__(self, container_id: str, create_time: str):
        self.ID = Node.GLOBAL_ID
        Node.ID_MAP[self.ID] = self
        Node.GLOBAL_ID += 1
        self.container_id = container_id
        self.create_time = create_time
        self.out_edges: dict[int, list["Edge"]] = {}
        self.in_edges: dict[int, list["Edge"]] = {}


class UnitNode(Node):
    def __init__(self, container_id: str, tid: str, create_time: str):
        Node.__init__(self, container_id, create_time)
        self.is_malicious = False
        self.tid = tid
        self.logs: list[dict] = []
        self.is_accept = False
        self.unit_id: str = "null"


class FileNode(Node):
    def __init__(self, container_id: str, ino: str, create_time: str):
        Node.__init__(self, container_id, create_time)
        self.ino = ino


class NetworkNode(Node):
    def __init__(
        self,
        container_id: str,
        pid: int,
        fd: int,
        client_ip: str,
        client_port: int,
        server_ip: str,
        server_port: int,
        create_time: str,
    ):
        Node.__init__(self, container_id, create_time)
        self.pid = pid
        self.fd = fd
        self.client_ip = client_ip
        self.client_port = client_port
        self.server_ip = server_ip
        self.server_port = server_port
        self.is_malicious: Literal[True, False, "Suspicious"] = False
        self.logs: list[dict] = []


class Edge:
    def __init__(self, source: Node, target: Node, time: str, log: dict):
        self.source = source
        self.target = target
        self.time = time
        self.log = log


class ProvGraph:
    def __init__(self):
        self.type: str = "process"
        self.node_by_tid: dict[tuple[str, str], UnitNode] = {}
        self.node_by_ino: dict[tuple[str, str], FileNode] = {}
        self.node_by_cid_pid_fd: dict[tuple[str, int, int], NetworkNode] = {}
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self.merge_set = MergeSet(Node.ID_MAP)

        self.node_by_tid_unit: dict[tuple[str, str, int], UnitNode] = {}

        self.app_log_files: set[str] = set()
        self.app_log_matches: dict[int, tuple[str, int]] = {}

    def output(self, service_to_container_id: dict[str, str], output_path: str):
        cur_time = datetime.now()
        sysdig_prefix = f"{output_path}/{cur_time}/sysdig"
        tshark_prefix = f"{output_path}/{cur_time}/tshark"
        applog_prefix = f"{output_path}/{cur_time}/applog"
        os.makedirs(sysdig_prefix, exist_ok=True)
        os.makedirs(tshark_prefix, exist_ok=True)
        os.makedirs(applog_prefix, exist_ok=True)

        malicious_applogs: dict[str, set[int]] = {}

        inv_dict = {v: k for k, v in service_to_container_id.items()}

        fds: dict[str, tuple[TextIOWrapper, list[tuple[int, dict]]]] = {}
        for node in self.nodes:
            if isinstance(node, UnitNode):
                for log in node.logs:
                    log["malicious"] = node.is_malicious
                    # log["unit_id"] = node.unit_id

                    if (
                        log["evt.num"] in self.app_log_matches
                        and node.is_malicious is True
                    ):
                        log_path, li = self.app_log_matches[log["evt.num"]]
                        malicious_applogs.setdefault(log_path, set()).add(li)

                    if log["container.id"] in fds:
                        fd = fds[log["container.id"]]
                    else:
                        fd = (
                            open(
                                f"{sysdig_prefix}/{inv_dict[log['container.id']]}.log",
                                "w",
                            ),
                            [],
                        )
                        fds[log["container.id"]] = fd
                    # fd.write(json.dumps(log) + "\n")
                    fd[1].append((int(log["evt.num"]), log))
            elif (
                isinstance(node, NetworkNode)
                and self.merge_set.fa.get(node.ID, None) == node.ID
            ):
                for log in node.logs:
                    log["malicious"] = node.is_malicious
                    if log["pcap_file"] in fds:
                        fd = fds[log["pcap_file"]]
                    else:
                        cid, interface = (
                            log["pcap_file"].partition(".json")[0].split("_")
                        )
                        cid = inv_dict[cid]
                        fd = (
                            open(f"{tshark_prefix}/{cid}_{interface}.log", "w"),
                            [],
                        )
                        fds[log["pcap_file"]] = fd
                    # fd.write(json.dumps(log) + "\n")
                    fd[1].append(
                        (int(log["_source"]["layers"]["frame"]["frame.number"]), log)
                    )

        for fd, logs in fds.values():
            logs.sort(key=lambda x: x[0])
            for log in logs:
                fd.write(json.dumps(log[1]) + "\n")

        for app_log_file in self.app_log_files:
            relative_path = app_log_file.partition(f"{CAPTURED_PATH}/app_log/")[
                2
            ].replace("/", "#")
            with open(app_log_file, "r") as f:
                with open(f"{applog_prefix}/{relative_path}", "w") as copied_fd:
                    for li, line in enumerate(f):
                        pattern = r"^\[AutoLabel (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})\.(\d{9}) (\d+)\] "
                        if match := re.search(pattern, line):
                            line = line[match.end() :]
                        if (
                            app_log_file in malicious_applogs
                            and li in malicious_applogs[app_log_file]
                        ):
                            copied_fd.write(f"[*MALICIOUS*] {line}")
                        else:
                            copied_fd.write(line)

        exec_command(
            [
                "tar",
                "czvf",
                f"{output_path}/{cur_time}.tar.gz",
                "-C",
                f"{output_path}/{cur_time}",
                ".",
            ]
        )

        exec_command(["rm", "-rf", f"{output_path}/{cur_time}"])

    def query_by_id(self, node_id: int) -> int:
        return self.merge_set.query_by_id(node_id)

    def query_by_time(self, conn: ConnInfo, timestamp: datetime) -> NetworkNode | None:
        return self.merge_set.query_by_time(conn, timestamp)

    def join(self, node_id: int, conns: set[tuple[ConnInfo, datetime]]):
        self.merge_set.join(node_id, conns)

    def add_net_node(
        self,
        container_id: str,
        pid: int,
        fd: int,
        client_ip: str,
        client_port: int,
        server_ip: str,
        server_port: int,
        create_time: str,
    ):
        new_node = NetworkNode(
            container_id,
            pid,
            fd,
            client_ip,
            client_port,
            server_ip,
            server_port,
            create_time,
        )
        self.nodes.append(new_node)
        self.node_by_cid_pid_fd[(container_id, pid, fd)] = new_node

    def add_file_node(self, container_id: str, ino: str, create_time: str):
        new_node = FileNode(container_id, ino, create_time)
        self.nodes.append(new_node)
        self.node_by_ino[(container_id, ino)] = new_node

    def add_process_node(self, container_id: str, tid: str, create_time: str):
        new_node = UnitNode(container_id, tid, create_time)
        self.nodes.append(new_node)
        self.node_by_tid[(container_id, tid)] = new_node

    def switch_unit(self, container_id: str, tid: str, unit_id: int, create_time: str):
        if (container_id, tid, unit_id) in self.node_by_tid_unit:
            cur_node = self.node_by_tid_unit[(container_id, tid, unit_id)]
            self.node_by_tid[(container_id, tid)] = cur_node
            cur_node.unit_id = str(unit_id)
        else:
            self.add_process_node(
                container_id,
                tid,
                create_time,
            )
            cur_node = self.node_by_tid[(container_id, tid)]
            cur_node.unit_id = str(unit_id)
            self.node_by_tid_unit[(container_id, tid, unit_id)] = cur_node

    def get_by_cid_pid_fd(self, container_id: str, pid: int, fd: int) -> NetworkNode:
        return self.node_by_cid_pid_fd[(container_id, pid, fd)]

    def get_by_tid(self, container_id: str, tid: str) -> UnitNode:
        return self.node_by_tid[(container_id, tid)]

    def get_by_ino(self, container_id: str, ino: str) -> FileNode:
        return self.node_by_ino[(container_id, ino)]

    def add_edge(self, source: Node, target: Node, time: str, log: dict):
        new_edge = Edge(source, target, time, log)
        self.edges.append(new_edge)
        source.out_edges.setdefault(target.ID, [])
        source.out_edges[target.ID].append(new_edge)

        target.in_edges.setdefault(source.ID, [])
        target.in_edges[source.ID].append(new_edge)
