from __future__ import annotations
from random import shuffle
from typing import TYPE_CHECKING, Callable
from ...common.functions_util import shorten_float
if TYPE_CHECKING:
    from ..tournaments.tournament import Participant


def score_to_string(score: float) -> str:
    string = str(shorten_float(score))
    if '.' in string and len(string) > 6:
        string = string[:6]
    if string[-1] == '.':
        string = string[-1:]
    elif len(string) > 1 and string[-2:] == ".0":
        string = string[:-2]
    return string


class Standings_Table(list[list[float]]):
    def __init__(self, participants: list[Participant], table: list[list[float]], headers: list[str]) -> None:
        super().__init__(table)
        self.participants: list[Participant] = participants
        self.headers: list[str] = headers
        self.keys: list[Callable[[float], float]] = [lambda x: x for _ in range(len(self.headers) - 1)]
        self.sort_table()

    def __repr__(self) -> str:
        representation = f"Headers: {self.headers}\n"
        for participant, scores in zip(self.participants, self):
            representation += f"{participant.__repr__()}: {scores}\n"
        return representation[:-1]

    def set_key(self, i: int, key: Callable[[float], float]) -> None:
        self.keys[i] = key
        self.sort_table()

    def get_row_values(self, row: int) -> tuple[float, ...]:
        return tuple(key(value) for key, value in zip(self.keys, self[row]))

    def sort_table(self) -> None:
        index_switches = sorted(range(len(self)), key=lambda i: self.get_row_values(i), reverse=True)
        new_table = [self[i] for i in index_switches]
        self.participants = [self.participants[i] for i in index_switches]
        self.clear()
        self.extend(new_table)

    def get_placements(self, draw_lots: bool = False) -> list[list[Participant]]:
        if len(self) == 0:
            return []
        placements = [[self.participants[0]]]
        current_placement = 0

        for i in range(1, len(self)):
            assert(self.get_row_values(i) <= self.get_row_values(i - 1))
            if self.get_row_values(i) == self.get_row_values(i - 1):
                placements[current_placement].append(self.participants[i])
            else:
                while len(placements) < i:
                    placements.append([])
                placements.append([self.participants[i]])
                current_placement = i

        for placement in placements:
            shuffle(placement)
        if not draw_lots:
            return placements

        i = 0
        while i < len(placements):
            for j in range(i + 1, i + len(placements[i])):
                if j >= len(placements):
                    placements.append([placements[i].pop(0)])
                else:
                    placements[j] = [placements[i].pop(0)]
                i += 1
            i += 1
        return placements

    def get_header_vertical(self) -> list[str]:
        header_vertical = []
        placements = self.get_placements()
        for i, placement in enumerate(placements):
            if len(placement) > 0:
                header_vertical.extend([str(i + 1)] + (len(placement) - 1) * [''])
        return header_vertical

    def get_strings(self) -> list[list[str]]:
        return [
            [str(participant)] + [score_to_string(score) for score in scores]
            for participant, scores in zip(self.participants, self)
        ]
