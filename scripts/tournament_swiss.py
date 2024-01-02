from typing import Sequence, Any, cast
from random import random
from .tournament import Tournament, Participant
from .player import Player
from .pairing import Pairing
from .parameter_tiebreak import Parameter_Tiebreak, get_tiebreak_list
from .functions_bbp import get_pairings_bbp
from .functions_pairing import PAIRING_FUNCTIONS
from .functions_util import has_duplicates
from .functions_tournament_util import get_score_dict_by_point_system
from .db_player import sort_players_swiss


class Tournament_Swiss(Tournament):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ) -> None:
        super().__init__(
            participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Swiss"
        self.parameters = {
            "rounds": 7,
            "pairing_method_first_round": ["Slide", "Fold", "Adjacent", "Random", "Custom"],
            "top_seed_color_first_round": ["Random", "White", "Black"],
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "half_bye": False,
            "baku_acceleration": False,
            "tiebreak_1": Parameter_Tiebreak(get_tiebreak_list("Buchholz")),
            "tiebreak_2": Parameter_Tiebreak(get_tiebreak_list("Buchholz Sum")),
            "tiebreak_3": Parameter_Tiebreak(get_tiebreak_list("None")),
            "tiebreak_4": Parameter_Tiebreak(get_tiebreak_list("None"))
        } | self.parameters
        self.parameters_display = {
            "rounds": "Rounds",
            "pairing_method_first_round": "Pairings (First Round)",
            "top_seed_color_first_round": "Top Seed (First Round)",
            "point_system": "Point System",
            "half_bye": "Half-Point Bye",
            "baku_acceleration": "Baku Acceleration",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    def get_score_dict(self) -> dict[str, float]:
        return get_score_dict_by_point_system(self.get_point_system(), half_bye=self.get_half_bye())

    def get_rounds(self) -> int:
        return cast(int, self.get_parameter("rounds"))

    def get_point_system(self) -> str:
        return cast(str, self.get_parameter("point_system")[0])

    def get_half_bye(self) -> bool:
        return cast(bool, self.get_parameter("half_bye"))

    def get_pairing_method_first_round(self) -> str:
        return cast(str, self.get_parameter("pairing_method_first_round")[0])

    def get_top_seed_color_first_round(self) -> str:
        return cast(str, self.get_parameter("top_seed_color_first_round")[0])

    def get_baku_acceleration(self) -> bool:
        return cast(bool, self.get_parameter("baku_acceleration"))

    def get_tiebreaks(self) -> tuple[Parameter_Tiebreak, ...]:
        return (
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_1")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_2")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_3")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_4"))
        )

    def is_valid_parameters(self) -> bool:
        return self.get_rounds() >= max(1, self.get_round() - 1)

    def is_valid_pairings(self, pairings: Sequence[Pairing]) -> bool:
        assert (all(pairing.is_fixed() for pairing in pairings))
        return not has_duplicates([item for item, _ in pairings] + [item for _, item in pairings])

    def is_done(self) -> bool:
        return self.get_round() > self.get_rounds()

    def seed_participants(self, seeds: list[int] | None = None) -> None:
        if seeds is None and not self.is_team_tournament():
            self.set_participants(sort_players_swiss(cast(list[Player], self.get_participants())))
        else:
            super().seed_participants(seeds)

    def load_pairings(self) -> None:
        if bool(self.get_pairings()) or self.is_done():
            return
        uuids = self.get_participant_uuids(drop_outs=False, byes=False)
        participant_number = len(uuids)
        first_round = self.get_round() == 1
        first_round_method = self.get_pairing_method_first_round()

        if first_round and first_round_method == "Custom":
            pairings = [Pairing(uuids, uuids) for _ in range(participant_number // 2)]
            if participant_number % 2:
                pairings.append(Pairing(uuids, ""))
        elif first_round:
            match self.get_top_seed_color_first_round():
                case "White":
                    first_seed_white = True
                case "Black":
                    first_seed_white = False
                case _:
                    first_seed_white = random() > .5
            if participant_number % 2:
                uuids.append("")
            if self.get_baku_acceleration():
                accelerated = (len(self.get_participants()) + 1) // 2
                accelerated += accelerated % 2
                accelerated = len([uuid for uuid in uuids if uuid in self.get_participant_uuids()[:accelerated]])
                accelerated -= accelerated % 2
                pairing_indices = PAIRING_FUNCTIONS[first_round_method](accelerated, first_seed_white)
                rest_indices = PAIRING_FUNCTIONS[first_round_method](participant_number - accelerated, first_seed_white)
                pairing_indices += [(i_1 + accelerated, i_2 + accelerated) for i_1, i_2 in rest_indices]
            else:
                pairing_indices = PAIRING_FUNCTIONS[first_round_method](participant_number, first_seed_white)
            pairings = [Pairing(uuids[i_1], uuids[i_2]) for i_1, i_2 in pairing_indices]
        else:
            pairings = get_pairings_bbp(self)
        for uuid in self.get_byes():
            pairings.append(Pairing(uuid, "bye"))
        self.set_pairings(pairings)

    def drop_in_participants(self, participants: Sequence[Participant]) -> None:
        if self.is_team_tournament():
            default_seeds = False
        else:
            default_seeds = self.get_participants() == sort_players_swiss(cast(list[Player], self.get_participants()))
        super().drop_in_participants(participants)
        if default_seeds:
            self.seed_participants()


class Tournament_Swiss_Team(Tournament_Swiss):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ):
        Tournament.__init__(
            self, participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Swiss (Team)"
        self.parameters = {
            "boards": 8,
            "enforce_lineups": True,
            "rounds": 7,
            "pairing_method_first_round": ["Slide", "Fold", "Adjacent", "Random"],
            "top_seed_color_first_round": ["Random", "White", "Black"],
            "point_system": ["2 - 1 - 0", "1 - ½ - 0", "3 - 1 - 0"],
            "point_system_game": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "half_bye": False,
            "tiebreak_1": Parameter_Tiebreak(get_tiebreak_list("Board Points", team=True)),
            "tiebreak_2": Parameter_Tiebreak(get_tiebreak_list("Buchholz", team=True)),
            "tiebreak_3": Parameter_Tiebreak(get_tiebreak_list("Buchholz Sum", team=True)),
            "tiebreak_4": Parameter_Tiebreak(get_tiebreak_list("None", team=True))
        } | self.parameters
        self.parameters_display = {
            "boards": "Boards",
            "enforce_lineups": "Enforce Lineups",
            "rounds": "Rounds",
            "pairing_method_first_round": "Pairings (First Round)",
            "top_seed_color_first_round": None,
            "point_system": "Point System (Match)",
            "point_system_game": "Point System (Game)",
            "half_bye": None,
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    def get_score_dict_game(self) -> dict[str, float]:
        return get_score_dict_by_point_system(self.get_point_system_game())

    def get_point_system_game(self) -> str:
        return cast(str, self.get_parameter("point_system_game")[0])
