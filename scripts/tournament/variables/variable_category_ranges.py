from typing import Any, cast
from .variable import Variable
from ..common.category_range import Category_Range
from ..registries.variable_registry import VARIABLE_REGISTRY


@VARIABLE_REGISTRY.register("Variable_Category_Ranges")
class Variable_Category_Ranges(list[Category_Range], Variable):
    def __init__(self, category_ranges: list[list[Any]]):
        assert(all(
            len(category_range) == 3 and isinstance(category_range[0], str) for category_range in category_ranges
        ))
        super().__init__([
            Category_Range(cast(str, category_range[0]), category_range[1], category_range[2])
            for category_range in category_ranges
        ])

    def get_class(self) -> str:
        return "Variable_Category_Ranges"

    def get_dict(self) -> dict[str, Any]:
        return {"category_ranges": [
            (category_range.category, category_range.bottom, category_range.top) for category_range in self
        ]}
