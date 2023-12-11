from typing import Any, cast
from .pairing import Pairing, Pairing_Item
from .variable import Variable


class Variable_Pairings(list[Pairing], Variable):
    def __init__(self, pairings: list[Pairing] | list[tuple[Pairing_Item, Pairing_Item]]) -> None:
        if all(isinstance(pairing, Pairing) for pairing in pairings):
            super().__init__(cast(list[Pairing], pairings))
        else:
            super().__init__([Pairing(item_1, item_2) for item_1, item_2 in pairings])

    def get_dict(self) -> dict[str, Any]:
        return {"pairings": [tuple(pairing) for pairing in self]}

    def is_fixed(self) -> bool:
        return all(pairing.is_fixed() for pairing in self)
