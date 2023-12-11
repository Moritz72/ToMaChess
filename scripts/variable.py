from typing import Any
from abc import abstractmethod


class Variable:
    @abstractmethod
    def __init__(self, **args: Any) -> None:
        pass

    @abstractmethod
    def get_dict(self) -> dict[str, Any]:
        pass
