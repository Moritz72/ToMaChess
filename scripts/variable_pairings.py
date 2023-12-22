from typing import Any
from .pairing import Str_s, Pairing
from .variable import Variable


class Variable_Pairings(list[Pairing], Variable):
    def __init__(self, pairings: list[list[Str_s]]) -> None:
        assert(all(len(pairing) == 2 for pairing in pairings))
        super().__init__([Pairing(pairing[0], pairing[1]) for pairing in pairings])

    def get_dict(self) -> dict[str, Any]:
        return {"pairings": [tuple(pairing) for pairing in self]}

    def is_fixed(self) -> bool:
        return all(pairing.is_fixed() for pairing in self)
