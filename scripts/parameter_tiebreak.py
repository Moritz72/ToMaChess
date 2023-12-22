from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, Any, Callable
from functools import partial
from .parameter import Parameter
from .functions_tiebreak import get_buchholz, get_buchholz_sum, get_sonneborn_berger, get_games, get_blacks, \
    get_number_of_wins, get_opponent_average_rating, get_progressive_score, get_number_of_black_wins, \
    get_direct_encounter, get_koya_system, get_board_points, get_berliner_wertung
if TYPE_CHECKING:
    from .tournament import Tournament

TIEBREAK_LIST = [
    "None", "Buchholz", "Buchholz Sum", "Sonneborn-Berger", "Games", "Games as Black", "Wins",
    "Wins as Black", "Average Rating", "Progressive Scores", "Koya System", "Direct Encounter"
]
TIEBREAK_LIST_TEAM = [
    "None", "Board Points", "Berliner Wertung", "Buchholz", "Buchholz Sum", "Sonneborn-Berger", "Games", "Wins",
    "Progressive Scores", "Koya System", "Direct Encounter"
]

TIEBREAKS: dict[str, Callable[..., dict[str, float]] | None] = {
    "None": None,
    "Buchholz": get_buchholz,
    "Buchholz Sum": get_buchholz_sum,
    "Sonneborn-Berger": get_sonneborn_berger,
    "Games": get_games,
    "Games as Black": get_blacks,
    "Wins": get_number_of_wins,
    "Wins as Black": get_number_of_black_wins,
    "Average Rating": get_opponent_average_rating,
    "Progressive Scores": get_progressive_score,
    "Koya System": get_koya_system,
    "Direct Encounter": get_direct_encounter,
    "Board Points": get_board_points,
    "Berliner Wertung": get_berliner_wertung
}
FUNC_ARGS: dict[str, dict[str, Any]] = {
    "None": {},
    "Buchholz": {"cut_down": 0, "cut_up": 0, "virtual": False},
    "Buchholz Sum": {"cut_down": 0, "cut_up": 0, "virtual": False},
    "Sonneborn-Berger": {"cut_down": 0, "cut_up": 0, "virtual": False},
    "Games": {},
    "Games as Black": {},
    "Wins": {"include_forfeits": False},
    "Wins as Black": {"include_forfeits": False},
    "Average Rating": {"cut_down": 0, "cut_up": 0, "include_forfeits": False},
    "Progressive Scores": {"cut_down": 0, "cut_up": 0},
    "Direct Encounter": {},
    "Koya System": {"threshold": 50},
    "Board Points": {},
    "Berliner Wertung": {}
}
FUNC_ARGS_DISPLAY: dict[str, dict[str, str]] = {
    "None": {},
    "Buchholz": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual Opponents"},
    "Buchholz Sum": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual Opponents"},
    "Sonneborn-Berger": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual Opponents"},
    "Games": {},
    "Games as Black": {},
    "Wins": {"include_forfeits": "Include Forfeits"},
    "Wins as Black": {},
    "Average Rating": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)"},
    "Progressive Scores": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)"},
    "Direct Encounter": {},
    "Koya System": {"threshold": "Threshold (%)"},
    "Board Points": {},
    "Berliner Wertung": {}
}


def get_tiebreak_list(default: str, team: bool = False) -> list[str]:
    if team:
        return sorted(TIEBREAK_LIST_TEAM, key=lambda x: x != default)
    return sorted(TIEBREAK_LIST, key=lambda x: x != default)


class Parameter_Tiebreak(Parameter):
    def __init__(self, criteria: list[str] | None = None, **specifications: Any):
        super().__init__()
        self.criteria: list[str] = criteria or TIEBREAK_LIST
        self.specifications: dict[str, Any] = specifications or FUNC_ARGS[self.criteria[0]]

    def __repr__(self) -> str:
        return f"{self.criteria[0]} ({self.specifications})"

    def get_dict(self) -> dict[str, Any]:
        return {"criteria": self.criteria} | self.specifications

    def get_arg_list(self) -> list[Any]:
        return [self.criteria] + list(self.specifications.values())

    def get_arg_display_list(self) -> list[str]:
        return ["Criterion"] + list(FUNC_ARGS_DISPLAY[self.criteria[0]].values())

    def is_valid(self) -> bool:
        return True

    def update(self, arg_list: Sequence[Any]) -> None:
        if arg_list[0][0] == self.criteria[0]:
            self.specifications = {key: value for key, value in zip(self.specifications, arg_list[1:])}
        else:
            self.window_update_necessary = True
            self.criteria = arg_list[0]
            self.specifications = FUNC_ARGS[self.criteria[0]]

    def get_evaluation_function(self, tournament: Tournament) -> Callable[[list[str]], dict[str, float]]:
        function = TIEBREAKS[self.criteria[0]]
        if function is None:
            return NotImplemented
        return partial(function, tournament=tournament, **self.specifications)

    def display_status(self) -> str:
        return self.criteria[0]
