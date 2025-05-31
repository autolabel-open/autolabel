import tempfile
from contextlib import contextmanager
from typing import Generator

from logs import add_app_log
from loguru import logger
from rich import print
from schema import Scene
from utils import exec_command, invert_ip


def hook_glibc_applog_trace(scene: Scene, cur_path: str) -> Scene:
    print("[Hook Glibc Applog & Trace]")
    exec_command(["/bin/bash", f"{cur_path}/hook_glibc_applog/build.sh"])
    exec_command(["/bin/bash", f"{cur_path}/hook_glibc_trace/build.sh"])
    for service in scene.services.values():
        service.setdefault("volumes", []).append(
            f"{cur_path}/hook_glibc_applog/hook_glibc_applog.so:/hook_glibc_applog.so"
        )
        service.setdefault("volumes", []).append(
            f"{cur_path}/hook_glibc_trace/hook_glibc_trace.so:/hook_glibc_trace.so"
        )
        envs: dict | list = service.get("environment", {})
        if isinstance(envs, list):
            envs.append({"LD_PRELOAD": "/hook_glibc_applog.so /hook_glibc_trace.so"})
            envs.append({"malicious": "false"})
        elif isinstance(envs, dict):
            envs["LD_PRELOAD"] = "/hook_glibc_applog.so /hook_glibc_trace.so"
            envs["malicious"] = "false"
        service["environment"] = envs
    return scene


def get_inv_dict(scene: Scene) -> dict[str, str]:
    print("[Get Inv Dict]")
    inv_dict: dict[str, str] = {}
    for service in scene.services.values():
        for _, network in service["networks"].items():
            original_ip = network["ipv4_address"]
            inv_ip = invert_ip(original_ip)
            inv_dict[original_ip] = inv_ip
    print(inv_dict)
    return inv_dict


def hook_glibc_attacker(scene: Scene, inv_dict: dict[str, str], cur_path: str) -> Scene:
    print("[Hook Glibc Attacker]")

    inv_dict_reverse = {v: k for k, v in inv_dict.items()}
    config_attack = f"ip_list = {inv_dict_reverse}\n"
    print(config_attack)

    with open(f"{cur_path}/hook_glibc_attacker/config_attack.py", "w") as f:
        f.write(config_attack)

    exec_command(["/bin/bash", f"{cur_path}/hook_glibc_attacker/build.sh"])
    for service in scene.services.values():
        service.setdefault("volumes", []).append(
            f"{cur_path}/hook_glibc_attacker/hook_glibc_attacker.so:/hook_glibc_attacker.so"
        )
    return scene


@contextmanager
def hook_kernel(scene: Scene, service_to_container_id: dict[str, str], cur_path: str):
    print("[Hook Kernel]")

    containers_have_applog = set()
    for service_name, cid in service_to_container_id.items():
        if "x-app-log" in scene.services[service_name]:
            containers_have_applog.add(cid)

    config_applog = f"container_names = {str(set(containers_have_applog))}\n\n"

    applog_path = {
        cid: scene.services[service_name]["x-app-log"]
        for service_name, cid in service_to_container_id.items()
        if "x-app-log" in scene.services[service_name]
    }
    config_applog += f"applog_path_prefixes = {applog_path}\n"

    print(config_applog)

    with open(f"{cur_path}/hook_kernel/config_applog.py", "w") as f:
        f.write(config_applog)

    exec_command(
        [
            "/bin/bash",
            "-c",
            f"cd {cur_path}/hook_kernel && (make INSTANCE=test clean || true)",
        ]
    )
    exec_command(
        ["/bin/bash", "-c", f"cd {cur_path}/hook_kernel && make INSTANCE=test"]
    )
    exec_command(["sudo", "insmod", f"{cur_path}/hook_kernel/write_uuid_test.ko"])

    try:
        yield
    except BaseException as e:
        logger.exception(e)
    finally:
        exec_command(["sudo", "rmmod", "write_uuid_test.ko"])


@contextmanager
def hook_netlog(
    service_to_container_id: dict[str, str],
    inv_dict: dict[str, str],
    cur_path: str,
):
    print("[Hook Netlog]")

    inv_dict_reverse = {v: k for k, v in inv_dict.items()}
    config_filter = f"hack_ips_orig = {inv_dict_reverse}\n\n"

    config_filter += (
        f"container_names = {str(set(service_to_container_id.values()))}\n\n"
    )

    print(config_filter)

    with open(f"{cur_path}/hook_netlog/config_filter.py", "w") as f:
        f.write(config_filter)

    exec_command(
        [
            "/bin/bash",
            "-c",
            f"cd {cur_path}/hook_netlog && (python_executable=$(which python) make INSTANCE=test clean || true)",
        ]
    )
    exec_command(
        [
            "/bin/bash",
            "-c",
            f"cd {cur_path}/hook_netlog && python_executable=$(which python) make INSTANCE=test",
        ]
    )
    exec_command(["sudo", "insmod", f"{cur_path}/hook_netlog/filter_test.ko"])

    try:
        yield
    except BaseException as e:
        logger.exception(e)
    finally:
        exec_command(["sudo", "rmmod", "filter_test.ko"])


@contextmanager
def do_modify_pre(
    scene: Scene,
) -> Generator[tuple[Scene, dict[str, str], str], None, None]:
    print("[Do Modify Pre]")
    inv_dict = get_inv_dict(scene)
    with tempfile.TemporaryDirectory() as tmpdir:
        exec_command(["cp", "-r", "./modify", f"{tmpdir}/modify"])
        cur_path = f"{tmpdir}/modify"
        try:
            scene = hook_glibc_attacker(scene, inv_dict, cur_path)
            scene = hook_glibc_applog_trace(scene, cur_path)
            scene = add_app_log(scene)
            print(scene)
            # breakpoint()
        except BaseException as e:
            breakpoint()
            raise

        try:
            yield scene, inv_dict, cur_path
        except BaseException as e:
            logger.exception(e)


@contextmanager
def do_modify_after(
    scene: Scene,
    service_to_container_id: dict[str, str],
    inv_dict: dict[str, str],
    cur_path: str,
):
    print("[Do Modify After]")
    with hook_kernel(scene, service_to_container_id, cur_path):
        with hook_netlog(service_to_container_id, inv_dict, cur_path):
            try:
                yield
            except BaseException as e:
                logger.exception(e)
