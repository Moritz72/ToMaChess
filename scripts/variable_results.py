from typing import Sequence, Any, cast
from .result import Result
from .variable import Variable


class Variable_Results(list[list[Result]], Variable):
    def __init__(self, results: Sequence[Sequence[Sequence[Sequence[str | None]]]]) -> None:
        valid = all(
            len(result) == 2 and all(len(item) == 2 and item[1] is not None for item in result)
            for result_list in results for result in result_list
        )
        if not valid:
            return
        super().__init__([[
            Result((uuid_1, cast(str, score_1)), (uuid_2, cast(str, score_2)))
            for (uuid_1, score_1), (uuid_2, score_2) in result_list
        ] for result_list in results])

    def get_dict(self) -> dict[str, Any]:
        return {"results": [[tuple(result) for result in result_list] for result_list in self]}
