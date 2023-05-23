from .class_tournament_round_robin import Tournament_Round_Robin
from .class_tiebreak import Tiebreak, tiebreak_list_team
from .functions_tournament_util import get_standings_with_tiebreaks, get_score_dict_by_point_system


class Tournament_Round_Robin_Team(Tournament_Round_Robin):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Round Robin (Team)"
        self.parameters = parameters or {
            "boards": 8,
            "cycles": 1,
            "choose_seating": False,
            "point_system": ["2 - 1 - 0", "1 - ½ - 0", "3 - 1 - 0"],
            "point_system_game": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "Board Points")}
            ),
            "tiebreak_2": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "Direct Encounter")}
            ),
            "tiebreak_3": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "Sonneborn-Berger")}
            ),
            "tiebreak_4": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "None")}
            )
        }
        self.parameter_display = {
            "boards": "Boards",
            "cycles": "Cycles",
            "choose_seating": None,
            "point_system": "Point System (Match)",
            "point_system_game": "Point System (Game)",
            "tiebreak_1": "Tiebreak (1)",
            "tiebreak_2": "Tiebreak (2)",
            "tiebreak_3": "Tiebreak (3)",
            "tiebreak_4": "Tiebreak (4)"
        }
        self.variables = variables or self.variables | {"results_individual": []}

    def get_score_dict_game(self):
        return get_score_dict_by_point_system(self.get_parameter("point_system_game")[0])

    def is_valid_parameters(self):
        return super().is_valid_parameters() and self.get_parameter("boards") > 0

    def get_standings(self):
        return get_standings_with_tiebreaks(self, {
            "results": self.get_results(), "score_dict": self.get_score_dict(),
            "score_dict_game": self.get_score_dict_game(), "all_participants": self.get_participants(),
            "results_individual": self.get_variable("results_individual")
        })
