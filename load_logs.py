import gzip
import json
import multiprocessing
import os

import msgpack
from loguru import logger
from tqdm import tqdm

from utils import exec_command, fields

CAPTURED_PATH = "/tmp/capture_dir"
CAPTURED_DIVIDED_PATH = f"{CAPTURED_PATH}/divided"

is_sysdig_loaded = False
is_tshark_loaded = False

cpu_count_ = os.cpu_count()
if cpu_count_ is None:
    raise ValueError
cpu_count = int(cpu_count_)


def process_scap(idx: int):
    path = f"{CAPTURED_DIVIDED_PATH}/capture.scap{idx}"
    os.system(
        f"sysdig -r {path} -c ./print_fields_new.lua | gzip > {CAPTURED_DIVIDED_PATH}/capture{idx}.gz"
    )
    os.system(f"rm -f {path}")


def load_gz(idx: int):
    path = f"{CAPTURED_DIVIDED_PATH}/capture{idx}.gz"
    with gzip.open(path, "rb") as f:
        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
        while True:
            data = f.read(50 * 1024 * 1024)
            if not data:
                break
            unpacker.feed(data)
            for obj in unpacker:
                yield obj


def load_objs():
    idx = -1
    while True:
        idx += 1
        if not os.path.exists(f"{CAPTURED_DIVIDED_PATH}/capture{idx}.gz"):
            break

    evt_num = 0
    for idx_ in range(idx):
        gen = load_gz(idx_)
        field_names = next(gen)
        for obj_ in gen:
            if isinstance(obj_, list):
                obj = {field_names[i - 1]: obj_[i] for i in range(len(obj_))}
            else:
                obj = {field_names[i - 1]: obj_[i] for i in obj_.keys()}
                obj.update(
                    {key: "null" for key in field_names if key not in obj.keys()}
                )
            obj["evt.num"] = evt_num
            evt_num += 1
            yield obj


def load_sysdig():
    global is_sysdig_loaded

    if not is_sysdig_loaded:
        is_sysdig_loaded = True

        exec_command(["mkdir", "-p", CAPTURED_DIVIDED_PATH])

        exec_command(
            [
                "sysdig",
                "-r",
                f"{CAPTURED_PATH}/capture.scap",
                "-P",
                "-C",
                "100MB",
                "-w",
                f"{CAPTURED_DIVIDED_PATH}/capture.scap",
            ]
        )

        idx = -1
        while True:
            idx += 1
            if not os.path.exists(f"{CAPTURED_DIVIDED_PATH}/capture.scap{idx}"):
                break

        for batch in tqdm(range(0, idx, cpu_count)):
            cur_batch = (batch, min(batch + cpu_count, idx))
            cur_processors: list[multiprocessing.Process] = []

            for i in range(*cur_batch):
                p = multiprocessing.Process(target=process_scap, args=(i,))
                cur_processors.append(p)
                p.start()

            for p in cur_processors:
                p.join()

    for obj in tqdm(load_objs()):
        try:
            yield obj
        except Exception as e:
            logger.exception(e)
            raise


def load_tshark():
    global is_tshark_loaded

    if not is_tshark_loaded:
        is_tshark_loaded = True

        pcap_files = [f for f in os.listdir(CAPTURED_PATH) if f.endswith(".pcap")]
        logger.info(pcap_files)

        for pcap_file in tqdm(pcap_files):
            exec_command(
                [
                    "/bin/bash",
                    "-c",
                    " ".join(
                        [
                            "tshark",
                            "-r",
                            f"{CAPTURED_PATH}/{pcap_file}",
                            "-T",
                            "json",
                            ">",
                            f"{CAPTURED_PATH}/{pcap_file}.json",
                        ]
                    ),
                ],
                check=False,
            )

    pcap_json_files = [f for f in os.listdir(CAPTURED_PATH) if f.endswith(".pcap.json")]
    logger.info(pcap_json_files)

    for pcap_json_file in pcap_json_files:
        with open(f"{CAPTURED_PATH}/{pcap_json_file}", "r", errors="ignore") as f:
            content = json.loads(f.read())
            for packet in content:
                yield (pcap_json_file, packet)


if __name__ == "__main__":
    with open("/tmp/one.txt", "w") as out:
        for line in load_sysdig():
            out.write(str(line) + "\n")

    with open("/tmp/two.txt", "w") as out:
        for line in load_sysdig():
            out.write(str(line) + "\n")
