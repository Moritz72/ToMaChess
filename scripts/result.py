from typing import Iterator

Result_Item = tuple[str | None, str]


class Result:
    def __init__(self, item_1: Result_Item, item_2: Result_Item) -> None:
        self.items: tuple[Result_Item, Result_Item] = (item_1, item_2)

    def __getitem__(self, index: int) -> Result_Item:
        return self.items[index]

    def __iter__(self) -> Iterator[Result_Item]:
        return iter(self.items)

    def __repr__(self) -> str:
        return f"{self.items[0][0]} vs {self.items[1][0]} {self.items[0][1]}-{self.items[1][1]}"
