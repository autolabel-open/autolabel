from sysdig_rules.graph import ProvGraph


class FastAPIProcessor:
    def __init__(self, graph: ProvGraph):
        self.graph = graph

    def process(self, log: dict) -> bool:
        if log["evt.type"] == "write" and log["evt.arg.data"].startswith(
            "python conn_"
        ):
            unit_id = int(log["evt.arg.data"].rpartition(" ")[-1])
            if "conn_end" in log["evt.arg.data"]:
                del self.graph.node_by_tid[(log["container.id"], log["thread.vtid"])]
            else:
                if "conn_init" in log["evt.arg.data"]:
                    cur_node = self.graph.get_by_tid(
                        log["container.id"], log["thread.vtid"]
                    )
                    self.graph.node_by_tid_unit[
                        (log["container.id"], log["thread.vtid"], unit_id)
                    ] = cur_node

                if "conn_start" in log["evt.arg.data"]:
                    self.graph.switch_unit(
                        log["container.id"],
                        log["thread.vtid"],
                        unit_id,
                        log["evt.datetime"],
                    )
            return True

        else:
            return False
