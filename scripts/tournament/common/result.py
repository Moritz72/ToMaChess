from typing import Iterator
from .pairing_item import Pairing_Item, get_item_from_string

Result_Item = tuple[Pairing_Item, str]


def get_item(item: tuple[str, str]) -> Result_Item:
    return get_item_from_string(item[0]), item[1]


class Result:
    def __init__(self, item_1: tuple[str, str], item_2: tuple[str, str]) -> None:
        self.items: tuple[Result_Item, Result_Item] = (get_item(item_1), get_item(item_2))

    def __getitem__(self, index: int) -> Result_Item:
        return self.items[index]

    def __iter__(self) -> Iterator[Result_Item]:
        return iter(self.items)

    def __repr__(self) -> str:
        return f"{self.items[0][0]} vs {self.items[1][0]} {self.items[0][1]}-{self.items[1][1]}"
