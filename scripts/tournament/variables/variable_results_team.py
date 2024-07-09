from typing import Any
from .variable import Variable
from ..common.result import Result
from ..common.result_team import Result_Team
from ..registries.variable_registry import VARIABLE_REGISTRY


@VARIABLE_REGISTRY.register("Variable_Results_Team")
class Variable_Results_Team(list[list[Result_Team]], Variable):
    def __init__(self, results: list[list[list[list[list[str]]]]]) -> None:
        assert(all(
            len(result_individual) == 2 and all(len(item) == 2 for item in result_individual)
            for result_list in results for result in result_list for result_individual in result
        ))
        super().__init__([[Result_Team(
            [Result((item_1[0], item_1[1]), (item_2[0], item_2[1])) for item_1, item_2 in result]
        ) for result in result_list] for result_list in results])

    def get_class(self) -> str:
        return "Variable_Results_Team"

    def get_dict(self) -> dict[str, Any]:
        return {"results": [[[
            tuple(result_individual) for result_individual in result
        ] for result in result_list] for result_list in self]}
