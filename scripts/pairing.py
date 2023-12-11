from typing import Iterator

Pairing_Item = (str | None) | list[str] | list[None] | list[str | None]


class Pairing:
    def __init__(self, item_1: Pairing_Item, item_2: Pairing_Item) -> None:
        self.item_1: Pairing_Item = item_1
        self.item_2: Pairing_Item = item_2

    def __getitem__(self, index: int) -> Pairing_Item:
        return (self.item_1, self.item_2)[index]

    def __iter__(self) -> Iterator[Pairing_Item]:
        return iter((self.item_1, self.item_2))

    def __repr__(self) -> str:
        return f"{self.item_1} vs {self.item_2}"

    def is_fixed(self) -> bool:
        return isinstance(self.item_1, str | None) and isinstance(self.item_2, str | None)

    def fix(self, index: int, uuid: str | None) -> None:
        if index == 0 and isinstance(self.item_1, list) and uuid in self.item_1:
            self.item_1 = uuid
        elif index == 1 and isinstance(self.item_2, list) and uuid in self.item_2:
            self.item_2 = uuid
