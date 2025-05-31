from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import ControledNode, LocalNode


id_ = 0


class Exploiter(ABC):
    # Target is fixed

    def __init__(self, ip: str):
        self.ip = ip
        self.is_rce = False
        self.is_endpoint = False
        self.prefix = f"http://{self.ip}:8000"

    @abstractmethod
    def exploit_rce_init(self, proxier: "ControledNode | LocalNode"):
        pass

    @abstractmethod
    def exploit_rce(self, proxier: "ControledNode | LocalNode", cmd: str) -> str:
        pass

    @abstractmethod
    def exploit_no_rce(self, proxier: "ControledNode | LocalNode"):
        pass
