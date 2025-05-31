from typing import Literal

from sysdig_rules.graph import ProvGraph, UnitNode
from sysdig_rules.java import JavaRunnableProcessor
from sysdig_rules.nodejs import NodeJSProcessor
from sysdig_rules.python_asyncio import FastAPIProcessor

ATK_FLAG_1 = "A#t#k#F#1#"
ATK_FLAG_2 = "A#t#k#F#2#"
ATK_FLAG_3 = "A#t#k#F#3#"


class SysdigProcessor:
    def __init__(self, inv_dict: dict[str, str]):
        self.graph = ProvGraph()
        self.temp_log: dict[tuple[str, str], dict] = {}
        self.reversed_inv_dict: dict[str, str] = {v: k for k, v in inv_dict.items()}

        self.processors = [
            FastAPIProcessor(self.graph),
            NodeJSProcessor(self.graph),
            JavaRunnableProcessor(self.graph),
        ]

    def handle_net(self, log: dict) -> bool:
        if (
            log["evt.type"] == "socket"
            or log["evt.type"] == "accept4"
            or log["evt.type"] == "accept"
        ):
            self.graph.add_net_node(
                log["container.id"],
                log["proc.vpid"],
                log["fd.num"],
                "null",
                0,
                "null",
                0,
                log["evt.datetime"],
            )

        if log["fd.cip"] in self.reversed_inv_dict:
            log["fd.cip"] = self.reversed_inv_dict[log["fd.cip"]]
        if log["fd.sip"] in self.reversed_inv_dict:
            log["fd.sip"] = self.reversed_inv_dict[log["fd.sip"]]

        client_ip = log["fd.cip"]
        client_port = log["fd.cport"]
        server_ip = log["fd.sip"]
        server_port = log["fd.sport"]
        fd = log["fd.num"]

        fd: int | Literal["null"]

        if (
            client_ip != "null"
            and client_port != "null"
            and server_ip != "null"
            and server_port != "null"
            and fd != "null"
        ):
            if (
                log["container.id"],
                log["proc.vpid"],
                fd,
            ) not in self.graph.node_by_cid_pid_fd:
                self.graph.add_net_node(
                    log["container.id"],
                    log["proc.vpid"],
                    fd,
                    client_ip,
                    client_port,
                    server_ip,
                    server_port,
                    log["evt.datetime"],
                )

            net_node = self.graph.get_by_cid_pid_fd(
                log["container.id"],
                log["proc.vpid"],
                fd,
            )
            net_node.client_ip = client_ip
            net_node.client_port = client_port
            net_node.server_ip = server_ip
            net_node.server_port = server_port

        if log["evt.type"] == "accept4" or log["evt.type"] == "accept":
            self.graph.add_process_node(
                log["container.id"], log["thread.vtid"], log["evt.datetime"]
            )
            self.graph.get_by_tid(log["container.id"], log["thread.vtid"]).is_accept = (
                True
            )

            if not (
                client_ip == "null"
                or client_port == "null"
                or server_ip == "null"
                or server_port == "null"
                or fd == "null"
            ):
                self.graph.add_edge(
                    self.graph.get_by_cid_pid_fd(
                        log["container.id"],
                        log["proc.vpid"],
                        fd,
                    ),
                    self.graph.get_by_tid(log["container.id"], log["thread.vtid"]),
                    log["evt.datetime"],
                    log,
                )

        if log["evt.is_io_read"] is True:
            if not (
                client_ip == "null"
                or client_port == "null"
                or server_ip == "null"
                or server_port == "null"
                or fd == "null"
            ):
                self.graph.add_edge(
                    self.graph.get_by_cid_pid_fd(
                        log["container.id"],
                        log["proc.vpid"],
                        fd,
                    ),
                    self.graph.get_by_tid(log["container.id"], log["thread.vtid"]),
                    log["evt.datetime"],
                    log,
                )

        if log["evt.is_io_write"] is True:
            if not (
                client_ip == "null"
                or client_port == "null"
                or server_ip == "null"
                or server_port == "null"
            ):
                self.graph.add_edge(
                    self.graph.get_by_tid(log["container.id"], log["thread.vtid"]),
                    self.graph.get_by_cid_pid_fd(
                        log["container.id"],
                        log["proc.vpid"],
                        fd,
                    ),
                    log["evt.datetime"],
                    log,
                )

        return True

    def handle_file(self, log: dict) -> bool:
        cur_fid = (log["container.id"], log["fd.ino"])

        for processor in self.processors:
            if processor.process(log):
                return False
                # return True

        if log["evt.type"] == "openat":
            if ATK_FLAG_2 in log["fd.name"]:
                log["malicious"] = True
                # breakpoint()

        if log["evt.type"] == "write":
            if log["evt.buffer"] == "malicious":
                log["malicious"] = True
                # breakpoint()

        if log["evt.is_io_read"] is True:
            if cur_fid not in self.graph.node_by_ino:
                self.graph.add_file_node(
                    log["container.id"], log["fd.ino"], log["evt.datetime"]
                )
            self.graph.add_edge(
                self.graph.get_by_ino(log["container.id"], log["fd.ino"]),
                self.graph.get_by_tid(log["container.id"], log["thread.vtid"]),
                log["evt.datetime"],
                log,
            )

        if log["evt.is_io_write"] is True:
            if cur_fid not in self.graph.node_by_ino:
                self.graph.add_file_node(
                    log["container.id"], log["fd.ino"], log["evt.datetime"]
                )
            self.graph.add_edge(
                self.graph.get_by_tid(log["container.id"], log["thread.vtid"]),
                self.graph.get_by_ino(log["container.id"], log["fd.ino"]),
                log["evt.datetime"],
                log,
            )

        return True

    def handle_process(self, log: dict) -> bool:
        if log["evt.type"] == "execve":
            if log["proc.env[malicious]"] == "true":
                log["malicious"] = True
                # breakpoint()

        if log["evt.type"] in ["clone", "fork", "vfork"]:
            parent_tid = log["thread.vtid"]
            child_tid = log["evt.rawres"]

            if child_tid == "0":
                return True

            self.graph.add_process_node(
                log["container.id"], child_tid, log["evt.datetime"]
            )

            self.graph.add_edge(
                self.graph.get_by_tid(log["container.id"], parent_tid),
                self.graph.get_by_tid(log["container.id"], child_tid),
                log["evt.datetime"],
                log,
            )

        return True

    def add_log_to_node(self, node: UnitNode, log: dict):
        del log["evt.buffer"]
        del log["proc.env[malicious]"]
        del log[">"]
        del log["evt.dir"]

        log_keys = list(log.keys())
        for key in log_keys:
            if isinstance(log[key], str):
                val = log[key]
                val = val.replace(ATK_FLAG_1, "")
                val = val.replace(ATK_FLAG_2, "")
                val = val.replace(ATK_FLAG_3, "")
                log[key] = val
            if log[key] == "null":
                log[key] = None

        if log["malicious"] is True:
            node.is_malicious = True
        node.logs.append(log)

    def process(self, log: dict):
        cur_tid = (log["container.id"], log["thread.vtid"])
        if log["evt.dir"] == ">":
            self.temp_log[cur_tid] = log
            return
        if cur_tid in self.temp_log:
            log[">"] = self.temp_log[cur_tid]
        else:
            log[">"] = {}

        log["malicious"] = False

        if cur_tid not in self.graph.node_by_tid:
            self.graph.add_process_node(
                log["container.id"], log["thread.vtid"], log["evt.datetime"]
            )

        cur_node = self.graph.get_by_tid(log["container.id"], log["thread.vtid"])

        if log["evt.category"] == "net":
            res = self.handle_net(log)
        elif log["evt.category"] == "file":
            res = self.handle_file(log)
        elif log["evt.category"] == "process":
            res = self.handle_process(log)
        else:
            return

        if (log["container.id"], log["thread.vtid"]) in self.graph.node_by_tid:
            cur_node = self.graph.get_by_tid(log["container.id"], log["thread.vtid"])

        if res:
            self.add_log_to_node(cur_node, log)
