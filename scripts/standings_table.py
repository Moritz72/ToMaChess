from __future__ import annotations
from typing import TYPE_CHECKING
from random import shuffle
from .functions_util import shorten_float
if TYPE_CHECKING:
    from .tournament import Participant


def score_to_string(score: float) -> str:
    string = str(shorten_float(score))
    if '.' in string and len(string) > 6:
        string = string[:6]
    if string[-1] == '.':
        string = string[-1:]
    return string


class Standings_Table(list[list[float]]):
    def __init__(self, participants: list[Participant], table: list[list[float]], headers: list[str]):
        super().__init__(table)
        self.participants: list[Participant] = participants
        self.headers: list[str] = headers
        self.sort_table()

    def __repr__(self) -> str:
        representation = f"Headers: {self.headers}\n"
        for participant, scores in zip(self.participants, self):
            representation += f"{participant.__repr__()}: {scores}\n"
        return representation[:-1]

    def sort_table(self) -> None:
        index_switches = sorted(range(len(self)), key=lambda i: self[i], reverse=True)
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
            assert(self[i] <= self[i - 1])
            if self[i] == self[i - 1]:
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
