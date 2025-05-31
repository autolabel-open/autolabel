import os
import subprocess
import time

from rich import print

from schema import Scene
from utils import client

CAPTURED_PATH = "/tmp/capture_dir"
CAPTURED_SYSDIG_PATH = CAPTURED_PATH + "/capture.scap"


if os.path.exists(CAPTURED_PATH):
    if os.environ.get("BATCH", "0") != "0":
        is_overwrite = "y"
    else:
        is_overwrite = input("The capture directory already exists, overwrite? (y/n)")
    if is_overwrite.lower() != "y":
        raise Exception("Capture directory already exists")
    os.system(f"sudo rm -rf {CAPTURED_PATH}")

os.makedirs(CAPTURED_PATH)
os.chmod(CAPTURED_PATH, 0o777)


def start_sysdig_log(container_ids: list[str]):
    assert len(container_ids) > 0

    print("[Starting Sysdig Logging]")

    container_id_rule = " or ".join(
        [f"container.id='{container_id[:12]}'" for container_id in container_ids]
    )

    filter_rule = "({})".format(
        " and ".join(
            [
                "(evt.category=net or evt.category=file or evt.category=process)",
                "container.id!='host'",
                "container.id!=''",
                f"({container_id_rule})",
            ]
        )
    )

    sysdig_command = [
        "sudo",
        "sysdig",
        filter_rule,
        "-w",
        CAPTURED_SYSDIG_PATH,
    ]

    print(sysdig_command)

    with open("/tmp/sysdig_output.log", "w") as outfile, open(
        "/tmp/sysdig_error.log", "w"
    ) as errfile:
        sysdig_process = subprocess.Popen(
            sysdig_command, stdin=subprocess.PIPE, stdout=outfile, stderr=errfile
        )
        time.sleep(2)
        if sysdig_process.poll() is not None:
            with open("/tmp/sysdig_error.log", "r") as errfile:
                error_message = errfile.read()
            raise RuntimeError(f"Sysdig failed to start: {error_message}")


def execute_nsenter_command(pid: int, command: str):
    nsenter_command = [
        "sudo",
        "nsenter",
        "--target",
        str(pid),
        "--net",
        "--",
        "sh",
        "-c",
        command,
    ]
    result = subprocess.run(nsenter_command, capture_output=True, text=True)
    return result.stdout


def list_network_devices(pid: int):
    command = "ip a"
    output = execute_nsenter_command(pid, command)
    return output


def capture_traffic(pid: int, container_id: str):
    devices_output = list_network_devices(pid)
    devices = []
    for line in devices_output.split("\n"):
        if "state UP" in line:
            device = line.split(":")[1].strip().split("@")[0]
            devices.append(device)

    for device in devices:
        pcap_file = f"{container_id}_{device}.pcap"
        tcpdump_command = f"tcpdump -i {device} -w {CAPTURED_PATH}/{pcap_file}"
        full_command = [
            "sudo",
            "nsenter",
            "--target",
            str(pid),
            "--net",
            "--",
            "sh",
            "-c",
            tcpdump_command,
        ]
        print(full_command)
        subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

    conntrack_command = [
        "/bin/bash",
        "./capture_conntrack.sh",
        f"{CAPTURED_PATH}/{container_id}_conntrack.txt",
        str(pid),
    ]
    print(conntrack_command)
    subprocess.Popen(
        conntrack_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    )


def start_traffic_log(container_ids: list[str]):
    print("[Starting Traffic Logging]")
    for container_id in container_ids:
        container = client.containers.get(container_id)
        pid: int = container.attrs["State"]["Pid"]
        capture_traffic(pid, container_id[:12])


def start_logging(service_to_container_id: dict[str, str]):
    start_sysdig_log(list(service_to_container_id.values()))
    start_traffic_log(list(service_to_container_id.values()))


def add_app_log(scene: Scene) -> Scene:
    print("[Add App Log]")
    for service_name, service in scene.services.items():
        app_log_path = service.get("x-app-log", None)
        if not app_log_path:
            continue
        service.setdefault("volumes", []).append(
            f"{CAPTURED_PATH}/app_log/{service_name}:{app_log_path}"
        )
    return scene
