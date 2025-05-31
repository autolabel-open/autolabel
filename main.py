import os

os.system("sudo echo AutoLabel is Starting.")

import signal
import time

import click
import psutil
import typer
from loguru import logger
from rich import print

from analyze import analyze_logs
from parse import parse_config
from scene import start_scene, stop_scene
from utils import exec_command


def main(
    config_path: str = typer.Option(help="Path to the configuration folder"),
    output_path: str = typer.Option("results", help="Path to the output folder"),
):
    scene = parse_config(config_path)
    service_to_container_id, inv_dict = start_scene(scene)
    stop_all()

    print("Sleeping for 10 seconds to wait for the logs to be saved...")
    time.sleep(10)
    analyze_logs(scene, service_to_container_id, inv_dict, output_path)


def stop_all():
    stop_scene()

    parent = psutil.Process(os.getpid())
    children = parent.children(recursive=True)

    for child in children:
        print(f"Terminating child process {child.pid}...")
        try:
            exec_command(["sudo", "kill", str(child.pid)])
        except Exception as e:
            logger.warning(e)

    gone, still_alive = psutil.wait_procs(children, timeout=5)

    for child in still_alive:
        print(f"Child process {child.pid} did not terminate, killing it...")
        try:
            exec_command(["sudo", "kill", "-9", str(child.pid)])
        except Exception as e:
            logger.warning(e)


def stop_handler(signum, frame):
    print("AutoLabel is Stopping.")
    stop_all()
    exit(1)


def add_stop_handler():
    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)


if __name__ == "__main__":
    add_stop_handler()

    try:
        typer.run(main)
    except SystemExit as e:
        print(f"Exited with code {e.code}.")
    except BaseException as e:
        logger.exception(e)
    finally:
        stop_handler(None, None)
