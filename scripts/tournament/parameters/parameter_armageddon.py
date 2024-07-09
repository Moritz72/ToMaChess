from random import random
from typing import Any, Sequence
from .parameter import Parameter
from ..common.pairing import Pairing
from ..registries.parameter_registry import PARAMETER_REGISTRY


def determine_color_default(uuid_1: str, uuid_2: str) -> Pairing:
    return Pairing(uuid_1, uuid_2)


def determine_color_random(uuid_1: str, uuid_2: str) -> Pairing:
    if random() < .5:
        return Pairing(uuid_1, uuid_2)
    return Pairing(uuid_2, uuid_1)


def determine_color_choice(uuid_1: str, uuid_2: str) -> Pairing:
    return Pairing([uuid_1, uuid_2], [uuid_1, uuid_2])


@PARAMETER_REGISTRY.register("Parameter_Armageddon")
class Parameter_Armageddon(Parameter):
    def __init__(self, enabled: bool = False, after_rounds: int = 1, color_methods: list[str] | None = None) -> None:
        super().__init__()
        self.enabled: bool = enabled
        self.after_rounds: int = after_rounds
        self.color_methods: list[str] = color_methods or ["Choice", "Random", "In Order"]

    def __repr__(self) -> str:
        return f"Armageddon({self.enabled}, {self.after_rounds}, {self.color_methods[0]})"

    def get_class(self) -> str:
        return "Parameter_Armageddon"

    def get_dict(self) -> dict[str, Any]:
        return {"enabled": self.enabled, "after_rounds": self.after_rounds, "color_methods": self.color_methods}

    def get_arg_list(self) -> list[Any]:
        if self.enabled:
            return [self.enabled, self.after_rounds, self.color_methods]
        return [self.enabled]

    def get_arg_display_list(self) -> list[str]:
        if self.enabled:
            return ["With Armageddon", "After Tiebreak", "Color Determination"]
        return ["With Armageddon"]

    def is_valid(self) -> bool:
        return True

    def update(self, arg_list: Sequence[Any]) -> None:
        self.window_update_necessary = arg_list[0] != self.enabled
        if len(arg_list) == 3:
            self.enabled, self.after_rounds, self.color_methods = tuple(arg_list)
        else:
            self.enabled = arg_list[0]

    def display_status(self) -> str:
        return "Yes" if self.enabled else "No"

    def is_armageddon(self, games: int, games_per_tiebreak: int, roun: int) -> bool:
        return self.enabled and roun - games - games_per_tiebreak * self.after_rounds >= 1

    def determine_color(self, uuid_1: str, uuid_2: str) -> Pairing:
        match self.color_methods[0]:
            case "In Order":
                return determine_color_default(uuid_1, uuid_2)
            case "Random":
                return determine_color_random(uuid_1, uuid_2)
            case "Choice":
                return determine_color_choice(uuid_1, uuid_2)
        return NotImplemented
