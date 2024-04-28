from abc import abstractmethod
from typing import Any, Sequence


class Parameter:
    def __init__(self, **args: Any) -> None:
        self.window_update_necessary: bool = False

    @abstractmethod
    def get_dict(self) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_arg_list(self) -> list[Any]:
        pass

    @abstractmethod
    def get_arg_display_list(self) -> list[str]:
        pass

    @abstractmethod
    def update(self, arg_list: Sequence[Any]) -> None:
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    @abstractmethod
    def display_status(self) -> str:
        pass
