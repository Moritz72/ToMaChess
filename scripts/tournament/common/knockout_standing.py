from typing import Any, Iterator, Sequence


class Knockout_Standing:
    def __init__(self, level: int, score: list[float], beaten_by_seed: int | None, seed: int) -> None:
        self.level: int = level
        self.score: list[float] = score
        self.beaten_by_seed: int | None = beaten_by_seed
        self.seed: int = seed

    def __getitem__(self, index: int) -> Any:
        return [self.level, self.score, self.beaten_by_seed, self.seed][index]

    def __iter__(self) -> Iterator[Any]:
        return iter([self.level, self.score, self.beaten_by_seed, self.seed])

    def __repr__(self) -> str:
        return f"Standing({self.level}, {self.score}, {self.beaten_by_seed}, {self.seed})"

    def was_beaten(self) -> bool:
        return bool(self.beaten_by_seed)

    def add_score(self, score: Sequence[float], reverse: bool = False) -> None:
        r = -1 if reverse else 1
        self.score = [sc_current + r * sc for sc_current, sc in zip(self.score, score)]
