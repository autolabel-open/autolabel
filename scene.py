import subprocess
import sys
import tempfile
import time
from typing import Any

import yaml
from rich import print

from logs import start_logging
from modify import do_modify_after, do_modify_pre
from schema import Operation, Scene
from utils import client, exec_command, get_current_time

project: str | None = None


def modify_compose(scene: Scene) -> dict[str, Any]:
    compose = scene.model_dump(by_alias=True)

    compose["version"] = "3.9"

    return compose


def stop_scene():
    global project
    if project is not None:
        exec_command(["docker", "compose", "--file", project, "kill"])
        exec_command(["docker", "compose", "--file", project, "down", "-v"])
        project = None


def get_service_to_container_id_mapping(services: list[str], container_ids: list[str]):
    service_to_container_id: dict[str, str] = {}
    for container_id in container_ids:
        container_info = client.containers.get(container_id).attrs
        service_name = container_info["Config"]["Labels"].get(
            "com.docker.compose.service"
        )
        if service_name in services:
            service_to_container_id[service_name] = container_id[:12]
    return service_to_container_id


def run_base_scene(scene: Scene):
    global project

    print("[Running Base Scene]")
    compose = modify_compose(scene)
    print(compose)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", prefix=f"scene_{get_current_time()}_", delete=False
    ) as f:
        yaml.dump(compose, f)
        project = f.name
        print(project)

    exec_command(["docker", "compose", "--file", project, "up", "--build", "-d"])

    output = subprocess.check_output(
        ["docker", "compose", "--file", project, "ps", "-q"]
    )
    container_ids = output.decode().strip().split("\n")

    print("Services started, waiting for them to become healthy...")

    # 等待所有容器变为健康状态
    all_healthy = False
    while not all_healthy:
        all_healthy = True
        for container_id in container_ids:
            container = client.containers.get(container_id)
            container.reload()
            health_status = container.attrs["State"].get("Health", {}).get("Status")
            if health_status:
                if health_status != "healthy":
                    all_healthy = False
                    break
            else:
                # 如果没有定义健康检查，只检查容器是否在运行
                if container.status != "running":
                    all_healthy = False
                    break

        if not all_healthy:
            print("Not all services are healthy yet, waiting...")
            time.sleep(5)  # 等待5秒后再次检查

    print("All services are healthy!")
    return get_service_to_container_id_mapping(
        list(scene.services.keys()), container_ids
    )


def execute_steps(service_to_container_id: dict[str, str], steps: list[Operation]):

    for step in steps:
        print(f"[Executing Step] {step.name}")
        print(step.model_dump(by_alias=True))
        container_id = service_to_container_id[step.service]
        container = client.containers.get(container_id)
        env = {"LD_PRELOAD": "/hook_glibc_applog.so"}
        if step.is_attack:
            env["LD_PRELOAD"] += " /hook_glibc_attacker.so"
        if step.blocking:
            res = container.exec_run(step.command, environment=env, stream=True)
            for output in res.output:
                print(output.decode(), end="")
                sys.stdout.flush()
        else:
            container.exec_run(step.command, detach=True, environment=env)


def start_scene(scene: Scene) -> tuple[dict[str, str], dict[str, str]]:
    with do_modify_pre(scene) as pre_ret:
        scene, inv_dict, cur_path = pre_ret
        service_to_container_id = run_base_scene(scene)  # 运行基础场景
        with do_modify_after(
            scene, service_to_container_id, inv_dict, cur_path
        ):  # 执行后处理
            start_logging(service_to_container_id)  # 开始日志记录
            execute_steps(service_to_container_id, scene.steps)
            print("All steps executed, waiting for logs to be recorded...")
            time.sleep(5)  # 等待5秒，确保日志记录完毕

    return service_to_container_id, inv_dict
