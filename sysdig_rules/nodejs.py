from sysdig_rules.graph import ProvGraph


class NodeJSProcessor:
    def __init__(self, graph: ProvGraph):
        self.graph: ProvGraph = graph
        self.unit_id: int = 0
        self.nodeid_to_unit: dict[int, int] = dict()
        self.handler_to_unit: dict[str, int] = dict()
        self.handler_to_parent_node: dict[str, int] = dict()

        self.handler_stacks: dict[tuple[str, str], list[int]] = dict()

    def new_unit_id(self) -> int:
        self.unit_id += 1
        return self.unit_id

    def process(self, log: dict) -> bool:
        if log["evt.type"] == "write" and log["evt.arg.data"].startswith(
            "furina-node-ins"
        ):
            handler_id = str(log["evt.arg.data"].rpartition(" ")[-1])

            if "work_" in log["evt.arg.data"]:
                handler_id = "work_" + handler_id

            if (
                "handler_end" in log["evt.arg.data"]
                or "work_end" in log["evt.arg.data"]
            ):
                # del self.graph.node_by_tid[(log["container.id"], log["thread.vtid"])]

                if (
                    log["container.id"],
                    log["thread.vtid"],
                ) not in self.handler_stacks or len(
                    self.handler_stacks[(log["container.id"], log["thread.vtid"])]
                ) < 1:
                    del self.graph.node_by_tid[
                        (log["container.id"], log["thread.vtid"])
                    ]
                    self.handler_stacks[(log["container.id"], log["thread.vtid"])] = []
                else:
                    unit_id = self.handler_stacks[
                        (log["container.id"], log["thread.vtid"])
                    ].pop()
                    # unit_id = self.handler_stacks[
                    #     (log["container.id"], log["thread.vtid"])
                    # ][-1]
                    self.graph.switch_unit(
                        log["container.id"],
                        log["thread.vtid"],
                        unit_id,
                        log["evt.datetime"],
                    )

                # if handler_id in self.handler_to_unit:
                #     del self.handler_to_unit[handler_id]
                # if handler_id in self.handler_to_parent_node:
                #     del self.handler_to_parent_node[handler_id]

            else:
                if (
                    "uvio_init" in log["evt.arg.data"]
                    or "work_init" in log["evt.arg.data"]
                    or "handler_init" in log["evt.arg.data"]
                ):
                    # new handler id
                    # current unit id -> handler id

                    cur_node = self.graph.get_by_tid(
                        log["container.id"], log["thread.vtid"]
                    )
                    self.nodeid_to_unit.setdefault(cur_node.ID, self.new_unit_id())
                    cur_unit_id = self.nodeid_to_unit[cur_node.ID]

                    self.handler_to_unit[handler_id] = cur_unit_id

                    if (
                        log["container.id"],
                        log["thread.vtid"],
                        cur_unit_id,
                    ) not in self.graph.node_by_tid_unit:
                        self.graph.node_by_tid_unit[
                            (log["container.id"], log["thread.vtid"], cur_unit_id)
                        ] = cur_node

                if "work_init" in log["evt.arg.data"]:
                    # store the parent node id
                    self.handler_to_parent_node[handler_id] = cur_node.ID

                if (
                    "handler_begin" in log["evt.arg.data"]
                    or "work_begin" in log["evt.arg.data"]
                ):
                    # add edge from the parent node id
                    # switch unit

                    cur_node = self.graph.get_by_tid(
                        log["container.id"], log["thread.vtid"]
                    )
                    self.nodeid_to_unit.setdefault(cur_node.ID, self.new_unit_id())
                    cur_unit_id = self.nodeid_to_unit[cur_node.ID]

                    self.handler_stacks.setdefault(
                        (log["container.id"], log["thread.vtid"]), []
                    ).append(cur_unit_id)

                    if handler_id in self.handler_to_unit:
                        unit_id = self.handler_to_unit[handler_id]
                    else:
                        unit_id = self.new_unit_id()
                        self.handler_to_unit[handler_id] = unit_id
                        self.handler_to_parent_node[handler_id] = -1

                    # self.handler_stacks.setdefault(
                    #     (log["container.id"], log["thread.vtid"]), []
                    # ).append(unit_id)

                    self.graph.switch_unit(
                        log["container.id"],
                        log["thread.vtid"],
                        self.handler_to_unit[handler_id],
                        log["evt.datetime"],
                    )

                if "work_begin" in log["evt.arg.data"]:
                    cur_node = self.graph.get_by_tid(
                        log["container.id"], log["thread.vtid"]
                    )

                    if self.handler_to_parent_node[handler_id] != -1:
                        parent_node = self.graph.nodes[
                            self.handler_to_parent_node[handler_id]
                        ]
                        self.graph.add_edge(
                            parent_node,
                            cur_node,
                            log["evt.datetime"],
                            log,
                        )
                        self.graph.add_edge(
                            cur_node,
                            parent_node,
                            log["evt.datetime"],
                            log,
                        )

            return True

        else:
            return False
