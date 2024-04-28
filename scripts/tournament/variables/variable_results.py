from typing import Any
from .variable import Variable
from ..common.result import Result


class Variable_Results(list[list[Result]], Variable):
    def __init__(self, results: list[list[list[list[str]]]]) -> None:
        assert(all(
            len(result) == 2 and all(len(item) == 2 for item in result)
            for result_list in results for result in result_list
        ))
        super().__init__([[
            Result((item_1[0], item_1[1]), (item_2[0], item_2[1])) for item_1, item_2 in result_list
        ] for result_list in results])

    def get_dict(self) -> dict[str, Any]:
        return {"results": [[tuple(result) for result in result_list] for result_list in self]}

    def get_white_black_stats(self) -> tuple[dict[str, int], dict[str, int]]:
        white_dict: dict[str, int] = dict()
        black_dict: dict[str, int] = dict()
        for round_results in self:
            for result in round_results:
                for i, (item, score) in enumerate(result):
                    if item.is_bye():
                        continue
                    if item not in white_dict:
                        white_dict[item], black_dict[item] = 0, 0
                    if score in "+-b":
                        continue
                    if i == 0:
                        white_dict[item] += 1
                    else:
                        black_dict[item] += 1
        return white_dict, black_dict
