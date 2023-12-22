from typing import Sequence, Any, Iterator


class Knockout_Standing:
    def __init__(self, level: int, score: list[float], beaten_by_seat: int | None, seating: int) -> None:
        self.level: int = level
        self.score: list[float] = score
        self.beaten_by_seat: int | None = beaten_by_seat
        self.seating: int = seating

    def __getitem__(self, index: int) -> Any:
        return [self.level, self.score, self.beaten_by_seat, self.seating][index]

    def __iter__(self) -> Iterator[Any]:
        return iter([self.level, self.score, self.beaten_by_seat, self.seating])

    def __repr__(self) -> str:
        return f"Standing({self.level}, {self.score}, {self.beaten_by_seat}, {self.seating})"

    def was_beaten(self) -> bool:
        return bool(self.beaten_by_seat)

    def add_score(self, score: Sequence[float], reverse: bool = False) -> None:
        r = -1 if reverse else 1
        self.score = [sc_current + r * sc for sc_current, sc in zip(self.score, score)]
