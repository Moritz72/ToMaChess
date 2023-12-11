from .result import Result


class Result_Team(list[Result]):
    def __init__(self, results: list[Result]) -> None:
        super().__init__(results)
