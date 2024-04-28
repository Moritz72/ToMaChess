from typing import Any, cast
from .tournament import Participant, Tournament
from ..common.pairing import Pairing
from ..parameters.parameter_tiebreak import Parameter_Tiebreak, get_tiebreak_list
from ..utils.functions_tournament_util import get_score_dict_by_point_system


class Tournament_Custom(Tournament):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ) -> None:
        super().__init__(
            participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Custom"
        self.parameters = {
            "games_per_round": 4,
            "rounds": 7,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "half_bye": False,
            "tiebreak_1": Parameter_Tiebreak(get_tiebreak_list("Buchholz")),
            "tiebreak_2": Parameter_Tiebreak(get_tiebreak_list("Buchholz Sum")),
            "tiebreak_3": Parameter_Tiebreak(get_tiebreak_list("None")),
            "tiebreak_4": Parameter_Tiebreak(get_tiebreak_list("None"))
        } | self.parameters
        self.parameters_display |= {
            "games_per_round": "Games per Round",
            "rounds": "Rounds",
            "point_system": "Point System",
            "half_bye": "Half-Point Bye",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    def get_score_dict(self) -> dict[str, float]:
        return get_score_dict_by_point_system(self.get_point_system(), half_bye=self.get_half_bye())

    def get_games_per_round(self) -> int:
        return cast(int, self.get_parameter("games_per_round"))

    def get_rounds(self) -> int:
        return cast(int, self.get_parameter("rounds"))

    def get_point_system(self) -> str:
        return cast(str, self.get_parameter("point_system")[0])

    def get_half_bye(self) -> bool:
        return cast(bool, self.get_parameter("half_bye"))

    def get_tiebreaks(self) -> tuple[Parameter_Tiebreak, ...]:
        return (
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_1")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_2")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_3")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_4"))
        )

    def is_valid_parameters(self) -> bool:
        return self.get_rounds() >= max(1, self.get_round() - 1)

    def is_done(self) -> bool:
        return self.get_round() > self.get_rounds()

    def load_pairings(self) -> None:
        if bool(self.get_pairings()) or self.is_done():
            return
        uuids = self.get_participant_uuids(drop_outs=False, byes=False) + [""]
        games_per_round = self.get_games_per_round()
        pairings = [Pairing(uuids, uuids) for _ in range(games_per_round)]
        for uuid in self.get_byes():
            pairings.append(Pairing(uuid, "bye"))
        self.set_pairings(pairings)
