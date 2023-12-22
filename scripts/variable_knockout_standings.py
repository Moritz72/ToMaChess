from typing import Sequence, Any, cast
from .knockout_standing import Knockout_Standing
from .variable import Variable


class Variable_Knockout_Standings(dict[str, Knockout_Standing], Variable):
    def __init__(self, standings: dict[str, list[list[float] | int | None]]) -> None:
        assert(all(
            len(value) == 4 and isinstance(value[0], int) and isinstance(value[1], list)
            and isinstance(value[2], int | None) and isinstance(value[3], int)
            and all(isinstance(score, float) for score in value[1])
            for value in standings.values()
        ))
        super().__init__({key: Knockout_Standing(
            cast(int, value[0]), cast(list[float], value[1]), cast(int | None, value[2]), cast(int, value[3])
        ) for key, value in standings.items()})

    def get_dict(self) -> dict[str, Any]:
        return {"standings": {key: tuple(value) for key, value in self.items()}}

    def get_current_level(self) -> int:
        min_level: int | None = None
        for standing in self.values():
            if standing.beaten_by_seat is None and (min_level is None or standing.level < min_level):
                min_level = standing.level
        return min_level or 0

    def get_uuids(self, level: int | None = None) -> list[str]:
        level = level or self.get_current_level()
        return sorted(
            [uuid for uuid, standing in self.items() if standing.beaten_by_seat is None and standing.level == level],
            key=lambda x: self[x].seating
        )

    def add(self, uuid: str, level: int, score: Sequence[float]) -> None:
        self[uuid] = Knockout_Standing(level, list(score), None, len(self) + 1)
