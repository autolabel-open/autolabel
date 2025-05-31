import datetime
import os
import re
from queue import Queue

import msgpack
from dateutil import tz
from loguru import logger
from tqdm import tqdm

from load_logs import load_sysdig, load_tshark
from logs import CAPTURED_PATH
from net_trace import ConnInfo, NatInfo, parse_log_file, query_net
from schema import Scene
from sysdig_rules import SysdigProcessor
from sysdig_rules.graph import NetworkNode, Node, ProvGraph, UnitNode
from utils import IS_DEBUG

CAPTURED_PATH = "/tmp/capture_dir"

is_sysdig_loaded = False
is_tshark_loaded = False


def get_rawtime(time_str: str) -> int:
    # input: datetime string 2024-09-26 00:24:36.129186487
    # output: timestamp in nanoseconds 1727281568219457129

    seconds_str, nanoseconds_str = time_str.split(".")
    dt = datetime.datetime.strptime(seconds_str, "%Y-%m-%d %H:%M:%S")
    timestamp = dt.timestamp()
    total_nanoseconds = int(timestamp * 1e9) + int(nanoseconds_str)
    return total_nanoseconds


def build_provenance_graph(inv_dict: dict[str, str]) -> ProvGraph:
    """
    syscalls: dict[str, dict[str, list[dict]]] = {}
    for event in load_sysdig():
        category = event["evt.category"]
        type = event["evt.type"]
        syscalls.setdefault(category, {})
        syscalls[category].setdefault(type, [])
        syscalls[category][type].append(event)

    breakpoint()
    return ProvGraph()
    """

    sysdig_processor = SysdigProcessor(inv_dict)

    for event in load_sysdig():
        sysdig_processor.process(event)

    graph = sysdig_processor.graph
    return graph


local_tz = tz.tzlocal()


def parse_app_log_line(log_line: str):
    pattern = r"^\[AutoLabel (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2})\.(\d{9}) (\d+)\] "
    match = re.search(pattern, log_line)
    if match:
        date_str, time_str, nanoseconds, integer = match.groups()
        datetime_str = f"{date_str} {time_str}"
        datetime_obj = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        datetime_obj = datetime_obj.replace(tzinfo=datetime.timezone.utc)
        datetime_obj = datetime_obj.astimezone(local_tz)
        tst_seconds = datetime_obj.timestamp()
        tst_nanoseconds = int(tst_seconds * 1_000_000_000) + int(nanoseconds)
        integer_value = int(integer)
        return datetime_obj, tst_nanoseconds, integer_value
    else:
        raise ValueError("Log format does not match expected pattern")


def parse_app_log(container_id: str, log_path: str):
    print(f"Relating File: {log_path}")

    print("Pre Scan...")
    need_to_be_mapped = False
    with open(log_path, "r") as f:
        for li, line in tqdm(enumerate(f)):
            try:
                _, __, ___ = parse_app_log_line(line)
            except ValueError:
                continue
            need_to_be_mapped = True
            break

    if not need_to_be_mapped:
        return {}

    app_log_matches = {}

    """
    logs_by_tid = {}

    for event in load_sysdig():
        event_container_id = event["container.id"]
        event_tst = get_rawtime(event["evt.datetime"])
        event_tid = int(event["thread.vtid"])
        event_type = event["evt.type"]
        event_dir = event["evt.dir"]
        fd_name = event["fd.name"]

        if (
            event_container_id != container_id
            or event_type != "write"
            or fd_name == "/dev/null"
        ):
            continue

        logs_by_tid.setdefault(event_tid, [])
        logs_by_tid[event_tid].append(event)

    iters_by_tid = {}
    for key in logs_by_tid:
        try:
            iterator = iter(logs_by_tid[key])
            iters_by_tid[key] = iterator
        except Exception as msg:
            logger.warning(msg)
    """

    iters_by_tid = {}
    fd_by_tid = {}

    with open(log_path, "r") as f:

        previous_val: dict[int, dict | None] = {}

        for li, line in tqdm(enumerate(f)):
            try:
                occur_time, tst, tid = parse_app_log_line(line)
            except ValueError:
                continue

            while True:
                try:
                    if (tid in previous_val) and (previous_val[tid] is not None):
                        event = previous_val[tid]
                        assert event is not None
                    else:
                        try:
                            # event = next(iters_by_tid[tid])
                            if tid not in fd_by_tid:
                                if not os.path.exists(
                                    f"{CAPTURED_PATH}/divided/{container_id}_{tid}.pk"
                                ):
                                    break
                                fd_by_tid[tid] = open(
                                    f"{CAPTURED_PATH}/divided/{container_id}_{tid}.pk",
                                    "rb",
                                )
                                iters_by_tid[tid] = msgpack.Unpacker(
                                    fd_by_tid[tid], raw=False
                                )
                            event: dict = next(iters_by_tid[tid])
                        except Exception as msg:
                            logger.warning(msg)
                            break

                    event_container_id = event["container.id"]
                    event_tst = get_rawtime(event["evt.datetime"])
                    event_tid = int(event["thread.vtid"])
                    event_type = event["evt.type"]
                    event_dir = event["evt.dir"]

                    # breakpoint()

                    if event_tst < tst:
                        previous_val[tid] = None
                        continue

                    # if current event_tst >= tst and event_dir == '>'
                    # there is no write include this event_tst

                    if event_dir == ">":
                        previous_val[tid] = event
                        break

                    # breakpoint()

                    app_log_matches[event["evt.num"]] = (log_path, li)
                    break

                except StopIteration:
                    break

    for key in fd_by_tid:
        fd_by_tid[key].close()

    return app_log_matches


def log_relating(
    graph: ProvGraph, scene: Scene, service_to_container_id: dict[str, str]
) -> ProvGraph:

    # Relating App Logs

    pre_scan_fds = {}
    for event in load_sysdig():
        event_container_id = event["container.id"]
        event_tid = int(event["thread.vtid"])
        event_type = event["evt.type"]
        fd_name = event["fd.name"]

        if event_type != "write" or fd_name == "/dev/null":
            continue

        if (event_container_id, event_tid) not in pre_scan_fds:
            pre_scan_fds[(event_container_id, event_tid)] = open(
                f"{CAPTURED_PATH}/divided/{event_container_id}_{event_tid}.pk", "wb"
            )

        pre_scan_fds[(event_container_id, event_tid)].write(msgpack.packb(event))

    for key in pre_scan_fds:
        pre_scan_fds[key].close()

    # evt.num -> (log_path, line)
    graph.app_log_matches = {}

    for service_name, service in scene.services.items():
        app_log_path = service.get("x-app-log", None)
        if not app_log_path:
            continue
        directory = f"{CAPTURED_PATH}/app_log/{service_name}"
        for root, _, files in os.walk(directory):
            for file in files:
                path = os.path.join(root, file)
                try:
                    graph.app_log_files.add(path)
                    graph.app_log_matches.update(
                        parse_app_log(service_to_container_id[service_name], path)
                    )
                except Exception as e:
                    logger.exception(e)
                    continue

    # Relating Traffic Logs

    all_nat_info: dict[
        tuple[bool, ConnInfo], list[tuple[NatInfo, datetime.datetime]]
    ] = {}
    for service_name in scene.services.keys():
        container_id = service_to_container_id[service_name]
        nat_info = parse_log_file(container_id)
        for key in nat_info:
            all_nat_info.setdefault(key, [])
            all_nat_info[key] += nat_info[key]

    for key in all_nat_info.keys():
        all_nat_info[key] = sorted(all_nat_info[key], key=lambda x: x[0].timestamp)

    for node in graph.nodes:
        if not isinstance(node, NetworkNode):
            continue
        if (
            node.client_ip == "null"
            or node.client_port == 0
            or node.server_ip == "null"
            or node.server_port == 0
        ):
            continue
        conn = ConnInfo(
            src=node.client_ip,
            sport=node.client_port,
            dst=node.server_ip,
            dport=node.server_port,
        )
        conns_server = query_net(
            conn,
            False,
            datetime.datetime.strptime(
                node.create_time.partition(".")[0], "%Y-%m-%d %H:%M:%S"
            ),
            all_nat_info,
        )
        conns_client = query_net(
            conn,
            True,
            datetime.datetime.strptime(
                node.create_time.partition(".")[0], "%Y-%m-%d %H:%M:%S"
            ),
            all_nat_info,
        )

        """
        FIRST_OUT_NODE = Node.ID_MAP[list(Node.ID_MAP[1].out_edges.keys())[0]]
        if isinstance(FIRST_OUT_NODE, NetworkNode) and (
            node.client_port == FIRST_OUT_NODE.client_port
        ):
            breakpoint()
        """
        conns = conns_server.union(conns_client)
        graph.join(node.ID, conns)

    # breakpoint()
    return graph


def get_(x: dict, keys: str):
    for key in keys.split("/"):
        if not key in x:
            return None
        x = x[key]
    return x


def anchor_point_locating(graph: ProvGraph) -> ProvGraph:
    # Traffic Anchor Points
    for pcap_json_file, packet in load_tshark():
        try:

            if (IP := get_(packet, "_source/layers/ip")) is None:
                continue

            srcip = IP["ip.src"]
            dstip = IP["ip.dst"]

            if (
                timestamp := get_(packet, "_source/layers/frame/frame.time_epoch")
            ) is None:
                continue

            timestamp = datetime.datetime.fromtimestamp(float(str(timestamp)))

            if (TCP := get_(packet, "_source/layers/tcp")) is not None:
                srcport = TCP["tcp.srcport"]
                dstport = TCP["tcp.dstport"]

            elif (UDP := get_(packet, "_source/layers/udp")) is not None:
                srcport = UDP["udp.srcport"]
                dstport = UDP["udp.dstport"]

            else:
                continue

            flag_str = get_(packet, "_source/layers/ip/ip.flags")
            flag = str((int(flag_str, base=16) & 0x80) >> 7)
            recorded_packet = packet
            recorded_packet["pcap_file"] = pcap_json_file

            conn = ConnInfo(
                src=srcip, sport=int(srcport), dst=dstip, dport=int(dstport)
            )
            node = graph.query_by_time(conn, timestamp)
            if node is not None:
                node.logs.append(recorded_packet)
                if flag == "1":
                    node.is_malicious = True
                continue

            # Reverse client and server and search again

            conn = ConnInfo(src=dstip, sport=dstport, dst=srcip, dport=srcport)
            node = graph.query_by_time(conn, timestamp)
            if node is not None:
                node.logs.append(recorded_packet)
                if flag == "1":
                    node.is_malicious = True
                continue

        except Exception as e:
            logger.exception(e)
            raise

    return graph


def attack_subgraph_extraction(scene: Scene, graph: ProvGraph) -> ProvGraph:
    """
    out_degree: dict[Node, int] = {}
    departure_paths: dict[Node, set[Node]] = {}
    topo_queue: Queue[Node] = Queue()

    def is_network_or_unit(node: Node) -> NetworkNode | UnitNode | None:
        if isinstance(node, NetworkNode) or isinstance(node, UnitNode):
            return node
        return None

    for node in graph.nodes:
        out_degree[node] = len(node.out_edges)
        departure_paths[node] = set()

        if (
            isinstance(node, NetworkNode)
            and graph.merge_set.fa.get(node.ID, None) != node.ID
        ):
            continue

        if out_degree[node] == 0:
            topo_queue.put(node)

    while not topo_queue.empty():
        node = topo_queue.get()

        if (node_ := is_network_or_unit(node)) is not None:
            if not node_.is_malicious:
                continue

            for unique_path_node in departure_paths[node]:
                if (node_ := is_network_or_unit(unique_path_node)) is not None:
                    node_.is_malicious = True

            departure_paths[node] = {node}

        for source_id, edge_list in node.in_edges.items():
            src_node = Node.ID_MAP[source_id]
            out_degree[src_node] -= len(edge_list)
            departure_paths[src_node].update(departure_paths[node])
            if out_degree[src_node] == 0:
                topo_queue.put(src_node)

        if not IS_DEBUG:
            del departure_paths[node]

    return graph
    """

    long_conns: set[tuple[str, int]] = set()
    for node in graph.nodes:
        if isinstance(node, NetworkNode):
            in_edge_set = set(node.in_edges.keys())
            out_edge_set = set(node.out_edges.keys())
            all_edge_set = set()

            for to_node in in_edge_set:
                if graph.nodes[to_node].is_accept:
                    all_edge_set.add(to_node)

            for to_node in out_edge_set:
                if graph.nodes[to_node].is_accept:
                    all_edge_set.add(to_node)

            if (
                len(all_edge_set) > 2
                and f"{node.server_ip}:{node.server_port}" not in scene.attack_conns
            ):
                long_conns.add((node.server_ip, node.server_port))
                # breakpoint()

    if len(long_conns) != 0:
        logger.warning("Long Connections:")
        for conn in long_conns:
            logger.warning(conn)

    visited: set[Node] = set()

    def is_network_or_unit(node: Node) -> NetworkNode | UnitNode | None:
        if isinstance(node, NetworkNode) or isinstance(node, UnitNode):
            return node
        return None

    def dfs(node: NetworkNode | UnitNode, visited: set[Node]):
        visited.add(node)
        if (
            isinstance(node, NetworkNode)
            and (node.server_ip, node.server_port) in long_conns
        ):
            node.is_malicious = "Suspicious"
            return

        for dst_id, _ in node.out_edges.items():
            dst_node = Node.ID_MAP[dst_id]
            if (
                isinstance(node, NetworkNode)
                and isinstance(dst_node, UnitNode)
                and not dst_node.is_accept
            ):
                continue
            if (
                dst_node not in visited
                and (node_ := is_network_or_unit(dst_node)) is not None
            ):
                if (
                    isinstance(node_, NetworkNode)
                    and (node_.server_ip, node_.server_port) in long_conns
                ):
                    node_.is_malicious = "Suspicious"
                else:
                    node_.is_malicious = True
                    dfs(node_, visited)

    for node in graph.nodes:
        if (node_ := is_network_or_unit(node)) is not None:
            if node_ not in visited and node_.is_malicious is True:
                dfs(node_, visited)

    return graph


def analyze_logs(
    scene: Scene,
    service_to_container_id: dict[str, str],
    inv_dict: dict[str, str],
    output_path: str,
):
    graph = build_provenance_graph(inv_dict)
    graph = log_relating(graph, scene, service_to_container_id)
    graph = anchor_point_locating(graph)
    graph = attack_subgraph_extraction(scene, graph)

    graph.output(service_to_container_id, output_path)


if __name__ == "__main__":
    # analyze_logs()
    pass
