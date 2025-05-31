import bisect
from datetime import datetime, timedelta

from net_trace import ConnInfo


class MergeSet:
    def __init__(self, ID_MAP):
        self.fa: dict[
            int | tuple[ConnInfo, datetime], int | tuple[ConnInfo, datetime]
        ] = {}
        self.ID_MAP = ID_MAP
        self.all_conn_info: dict[ConnInfo, list[datetime]] = {}

    def query_by_id(self, node_id: int) -> int:
        if node_id not in self.fa:
            return node_id
        root_node_id = self.find(node_id)
        assert isinstance(root_node_id, int)
        return root_node_id

    def query_by_time(self, conn: ConnInfo, timestamp: datetime):
        if conn not in self.all_conn_info:
            return None

        ret = set()
        pos = bisect.bisect_left(self.all_conn_info[conn], timestamp)

        if pos == 0:
            return None
        if timestamp - self.all_conn_info[conn][pos - 1] > timedelta(minutes=1):
            return None

        root_node_id = self.find((conn, self.all_conn_info[conn][pos - 1]))
        assert isinstance(root_node_id, int)

        return self.ID_MAP[root_node_id]

    def find(self, x: int | tuple[ConnInfo, datetime]):
        tmp = x
        while self.fa[tmp] != tmp:
            tmp = self.fa[tmp]
        while x != tmp:
            x, self.fa[x] = self.fa[x], tmp
        return tmp

    def merge(
        self, x: int | tuple[ConnInfo, datetime], y: int | tuple[ConnInfo, datetime]
    ):
        x = self.find(x)
        y = self.find(y)
        if not isinstance(x, int):
            x, y = y, x

        if x == y:
            return

        self.fa[y] = x

        if isinstance(y, int) and isinstance(x, int):
            node_x = self.ID_MAP[x]
            node_y = self.ID_MAP[y]

            # y.edge move to x.edge
            # (z -> y) -> (z -> x)
            for z in node_y.in_edges:
                node_z = self.ID_MAP[z]
                node_x.in_edges.setdefault(z, [])
                node_z.out_edges.setdefault(x, [])
                for z_out_edge in node_z.out_edges[y]:
                    z_out_edge.target = node_x
                    node_z.out_edges[x].append(z_out_edge)
                    node_x.in_edges[z].append(z_out_edge)
                del node_z.out_edges[y]

            # (y -> z) -> (x -> z)
            for z in node_y.out_edges:
                node_z = self.ID_MAP[z]
                node_x.out_edges.setdefault(z, [])
                node_z.in_edges.setdefault(x, [])
                for z_in_edge in node_z.in_edges[y]:
                    z_in_edge.source = node_x
                    node_z.in_edges[x].append(z_in_edge)
                    node_x.out_edges[z].append(z_in_edge)
                del node_z.in_edges[y]

    def join(self, node_id: int, conns: set[tuple[ConnInfo, datetime]]):
        if node_id not in self.fa:
            try:
                cur_node = self.ID_MAP[node_id]
            except Exception:
                breakpoint()
            self.fa[node_id] = node_id

        for conn, timestamp in conns:
            if (conn, timestamp) not in self.fa:
                self.fa[(conn, timestamp)] = (conn, timestamp)
                self.all_conn_info.setdefault(conn, []).append(timestamp)
            self.merge(node_id, (conn, timestamp))
