import os

import yaml
from loguru import logger
from pydantic import ValidationError
from rich import print

from schema import Scene
from utils import set_current_workpath


def parse_config(path: str):
    print(f"[Parsing Config]: {path}")

    set_current_workpath(path)
    compose_path = os.path.join(path, "scene.yml")

    with open(compose_path, "r") as file:
        content = yaml.safe_load(file)

    try:
        scene = Scene.model_validate(content)
    except ValidationError:
        raise

    return scene


if __name__ == "__main__":
    res = parse_config("./example/simple_flask")
    breakpoint()
