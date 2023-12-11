from typing import Sequence, Any
from .category_range import Category_Range
from .variable import Variable


class Variable_Category_Ranges(list[Category_Range], Variable):
    def __init__(self, category_ranges: Sequence[tuple[str, Any, Any]]):
        super().__init__([Category_Range(category, bottom, top) for category, bottom, top in category_ranges])

    def get_dict(self) -> dict[str, Any]:
        return {"category_ranges": [
            (category_range.category, category_range.bottom, category_range.top) for category_range in self
        ]}
