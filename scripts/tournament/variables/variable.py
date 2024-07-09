from abc import abstractmethod
from typing import Any


class Variable:
    @abstractmethod
    def __init__(self, **args: Any) -> None:
        pass

    @abstractmethod
    def get_class(self) -> str:
        pass

    @abstractmethod
    def get_dict(self) -> dict[str, Any]:
        pass
