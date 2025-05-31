import bisect
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

from loguru import logger

CAPTURED_PATH = "/tmp/capture_dir"


@dataclass(frozen=True)
class ConnInfo:
    src: str
    sport: int
    dst: str
    dport: int


@dataclass(frozen=True)
class NatInfo:
    orig_conn: ConnInfo
    repl_conn: ConnInfo

    timestamp: datetime


def parse_log_entry(log_entry: str) -> NatInfo | None:
    """
    Example:
    [1728015478.556410] [UPDATE] tcp 6 120 FIN_WAIT src=192.168.123.3 dst=192.168.123.4 sport=55384 dport=5000 src=192.168.123.4 dst=192.168.123.3 sport=5000 dport=55384 [ASSURED]
    """

    try:
        timestamp_match = re.search(r"\[(\d+\.\d+)\]", log_entry)
        if not timestamp_match:
            return None
        if "udp" in log_entry:
            return None

        timestamp = datetime.fromtimestamp(float(timestamp_match.group(1)))

        pattern = (
            r"src=(?P<orig_src>[\d\.]+).*?"
            r"dst=(?P<orig_dst>[\d\.]+).*?"
            r"sport=(?P<orig_sport>\d+).*?"
            r"dport=(?P<orig_dport>\d+).*?"
            r"src=(?P<repl_src>[\d\.]+).*?"
            r"dst=(?P<repl_dst>[\d\.]+).*?"
            r"sport=(?P<repl_sport>\d+).*?"
            r"dport=(?P<repl_dport>\d+)"
        )
        match = re.search(pattern, log_entry)
        if not match:
            return None

        ret = NatInfo(
            orig_conn=ConnInfo(
                src=match.group("orig_src"),
                sport=int(match.group("orig_sport")),
                dst=match.group("orig_dst"),
                dport=int(match.group("orig_dport")),
            ),
            # reply_conn need to be reversed
            repl_conn=ConnInfo(
                src=match.group("repl_dst"),
                sport=int(match.group("repl_dport")),
                dst=match.group("repl_src"),
                dport=int(match.group("repl_sport")),
            ),
            timestamp=timestamp,
        )
        return ret

    except Exception as e:
        logger.error(e)
        return None


def parse_log_file(
    container_id: str,
) -> dict[tuple[bool, ConnInfo], list[tuple[NatInfo, datetime]]]:
    """
    (is_server?, ConnInfo) -> [(NatInfo, create_time)]
    - if is_server is True, check the reply conn
    - if is_server is False, check the original conn
    """

    ret = {}
    with open(f"{CAPTURED_PATH}/{container_id}_conntrack.txt", "r") as f:
        get_created_time = {}
        for line in f:
            nat_info = parse_log_entry(line)

            if nat_info is None:
                continue

            if "NEW" in line:
                get_created_time[(False, nat_info.orig_conn)] = nat_info.timestamp

            try:
                create_time = get_created_time[(False, nat_info.orig_conn)]
            except Exception:
                continue

            ret.setdefault((False, nat_info.orig_conn), [])
            ret[(False, nat_info.orig_conn)].append((nat_info, create_time))
            ret.setdefault((True, nat_info.repl_conn), [])
            ret[(True, nat_info.repl_conn)].append((nat_info, create_time))

    return ret


def query_net(
    conn: ConnInfo,
    is_server: bool,
    timestamp: datetime,
    all_nat_info: dict[tuple[bool, ConnInfo], list[tuple[NatInfo, datetime]]],
) -> set[tuple[ConnInfo, datetime]]:
    ret = {(conn, timestamp)}
    if (is_server, conn) not in all_nat_info:
        return ret

    found_nat_info = all_nat_info[(is_server, conn)]

    # found closest timestamp
    pos = bisect.bisect_left(found_nat_info, timestamp, key=lambda x: x[0].timestamp)
    if pos == 0:
        pass
    elif pos == len(found_nat_info):
        pos -= 1
    elif (
        found_nat_info[pos][0].timestamp - timestamp
        > timestamp - found_nat_info[pos - 1][0].timestamp
    ):
        pos -= 1

    if timestamp > found_nat_info[pos][0].timestamp:
        delta = timestamp - found_nat_info[pos][0].timestamp
    else:
        delta = found_nat_info[pos][0].timestamp - timestamp

    # greater than 1 minute is not the same connection.
    if delta > timedelta(minutes=1):
        return ret

    if not is_server:
        # client
        if found_nat_info[pos][0].repl_conn != conn:
            ret = ret.union(
                query_net(
                    found_nat_info[pos][0].repl_conn,
                    False,
                    found_nat_info[pos][1],
                    all_nat_info,
                )
            )
    else:
        # server
        if found_nat_info[pos][0].orig_conn != conn:
            ret = ret.union(
                query_net(
                    found_nat_info[pos][0].orig_conn,
                    True,
                    found_nat_info[pos][1],
                    all_nat_info,
                )
            )

    return ret
