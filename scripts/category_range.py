from typing import Sequence, Any, TypeVar
from math import inf
from .manager_translation import MANAGER_TRANSLATION

T = TypeVar('T')
INTEGER_CATEGORIES = ["Rating", "Birth"]
CATEGORIES_PLAYER = ["Rating", "Birth", "Sex", "Federation"]
CATEGORIES_TEAM: list[str] = []
CATEGORY_TO_METHOD = {"Rating": "get_rating", "Birth": "get_birthday", "Sex": "get_sex", "Federation": "get_country"}


def get_range_string(bottom: Any, top: Any) -> str:
    if bottom == top:
        return f"{bottom}"
    if bottom in (-inf, ""):
        return f"≤ {top}"
    if top in (inf, ""):
        return f"≥ {bottom}"
    return f"{bottom} - {top}"


class Category_Range:
    def __init__(self, category: str, bottom: Any, top: Any) -> None:
        self.category: str = category
        self.bottom: Any = bottom
        self.top: Any = top

    def __repr__(self) -> str:
        return self.get_title(translate=False)

    def get_title(self, translate: bool = True) -> str:
        if translate:
            return f"{MANAGER_TRANSLATION.tl(self.category)} {get_range_string(self.bottom, self.top)}"
        return f"{self.category} {get_range_string(self.bottom, self.top)}"

    def contains(self, obj: Any) -> bool:
        method_string = CATEGORY_TO_METHOD[self.category]
        if hasattr(obj, method_string):
            method = getattr(obj, method_string)
            if callable(method):
                value: Any = method()
                if value is None:
                    return False
                return bool(self.bottom <= value <= self.top)
        return False

    def filter_list(self, obj_list: Sequence[T]) -> list[T]:
        return [obj for obj in obj_list if self.contains(obj)]
