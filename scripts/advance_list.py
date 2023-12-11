from __future__ import annotations
from typing import Sequence
from .tournament import Tournament
from .functions_util import remove_duplicates


class Advance_List(list[tuple[Tournament, int]]):
    def __init__(self, tournament: Tournament) -> None:
        super().__init__()
        self.tournament: Tournament = tournament

    def __repr__(self) -> str:
        return f"Advance_List({self.tournament.__repr__()}, {super().__repr__()})"

    def fill(self, advance_list: list[tuple[Tournament, int]]) -> None:
        self.clear()
        self.extend(advance_list)

    def validate(self) -> None:
        new_list = remove_duplicates(self)
        self.clear()
        self.extend([
            (tournament, placement) for tournament, placement in new_list
            if placement <= tournament.get_participant_count()
        ])
        self.tournament.set_shallow_participant_count(len(self))

    def get_simplified(self, tournaments: Sequence[Tournament]) -> list[tuple[int, int]]:
        return [(tournaments.index(tournament), placement) for tournament, placement in self]
