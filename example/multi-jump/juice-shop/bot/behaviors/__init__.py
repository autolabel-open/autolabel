import random
from collections.abc import Coroutine
from dataclasses import dataclass
from enum import auto
from typing import Callable

from loguru import logger

from utils import AutoStrEnum


class Behaviors(AutoStrEnum):
    login = auto()
    logout = auto()
    add_address = auto()
    add_card = auto()
    charge = auto()
    check_review = auto()
    write_review = auto()
    add_to_basket = auto()
    checkout = auto()
    track_order = auto()
    complain = auto()

    # attacks
    get_ftp_file = auto()
    get_prometheus = auto()
    file_read = auto()
    dirsearch = auto()
    js_code_exec = auto()


class States(AutoStrEnum):
    logged_out = auto()
    logged_in = auto()


@dataclass
class BehaviorInfo:
    is_attack: bool
    avaliable_states: list[States]
    weight: float


behavior_infos: dict[Behaviors, BehaviorInfo] = {}


type BehaviorHandler = Callable[[], Coroutine[None, None, States | None]]


behavior_handlers: dict[Behaviors, BehaviorHandler] = {}


def define_behavior(
    name: Behaviors,
    *,
    weight: float,
    is_attack: bool = False,
    avaliable_states: list[States] = [s for s in States],
) -> Callable[[BehaviorHandler], BehaviorHandler]:
    behavior_infos[name] = BehaviorInfo(is_attack, avaliable_states, weight)

    def decorator(func: BehaviorHandler) -> BehaviorHandler:
        behavior_handlers[name] = func
        return func

    return decorator


async def choose_and_exec_behavior(
    current_state: States, include_attack: bool = False
) -> States:
    avaliable_behaviors = {
        b: info.weight
        for b, info in behavior_infos.items()
        if (not info.is_attack or include_attack)
        and current_state in info.avaliable_states
    }
    behavior = random.choices(
        list(avaliable_behaviors.keys()), list(avaliable_behaviors.values()), k=1
    )[0]
    if behavior_infos[behavior].is_attack:
        logger.warning(f"Choosen behavior: {behavior}")
    else:
        logger.info(f"Choosen behavior: {behavior}")
    return await behavior_handlers[behavior]() or current_state
