from __future__ import annotations


class UUID(str):
    def __new__(cls, uuid: str) -> UUID:
        return super().__new__(cls, uuid)

    @staticmethod
    def is_bye() -> bool:
        return False


class Bye(str):
    def __new__(cls, o: object = "bye") -> Bye:
        return super().__new__(cls, o)

    @staticmethod
    def is_bye() -> bool:
        return True


class Bye_PA(str):
    def __new__(cls, o: object = "") -> Bye_PA:
        return super().__new__(cls, o)

    @staticmethod
    def is_bye() -> bool:
        return True


Pairing_Item = UUID | Bye | Bye_PA


def get_item_from_string(string: str) -> Pairing_Item:
    match string:
        case "":
            return Bye_PA()
        case "bye":
            return Bye()
        case _:
            return UUID(string)


def get_tentative_results(item_1: Pairing_Item, item_2: Pairing_Item) -> tuple[str, str] | None:
    if item_1.is_bye() and item_2.is_bye():
        return '-', '-'
    if item_1.is_bye():
        return '-', 'b' if isinstance(item_1, Bye) else '+'
    if item_2.is_bye():
        return 'b' if isinstance(item_2, Bye) else '+', '-'
    return None
