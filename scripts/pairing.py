from typing import Iterator
from .pairing_item import Pairing_Item, get_item_from_string

Str_s = str | list[str]
Pairing_Item_s = Pairing_Item | list[Pairing_Item]


def get_item_s_from_string_s(str_s: str | Str_s) -> Pairing_Item_s:
    if isinstance(str_s, str):
        return get_item_from_string(str_s)
    return [get_item_from_string(string) for string in str_s]


class Pairing:
    def __init__(self, str_s_1: Str_s, str_s_2: Str_s) -> None:
        self.item_s_1: Pairing_Item_s = get_item_s_from_string_s(str_s_1)
        self.item_s_2: Pairing_Item_s = get_item_s_from_string_s(str_s_2)

    def __getitem__(self, index: int) -> Pairing_Item_s:
        return (self.item_s_1, self.item_s_2)[index]

    def __iter__(self) -> Iterator[Pairing_Item_s]:
        return iter((self.item_s_1, self.item_s_2))

    def __repr__(self) -> str:
        return f"{self.item_s_1} vs {self.item_s_2}"

    def is_fixed(self) -> bool:
        return isinstance(self.item_s_1, str) and isinstance(self.item_s_2, str)

    def fix(self, index: int, item: Pairing_Item) -> None:
        if index == 0 and isinstance(self.item_s_1, list) and item in self.item_s_1:
            self.item_s_1 = item
        elif index == 1 and isinstance(self.item_s_2, list) and item in self.item_s_2:
            self.item_s_2 = item
