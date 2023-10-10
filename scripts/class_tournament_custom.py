from .class_tournament import Tournament
from .class_tiebreak import Tiebreak, get_tiebreak_list
from .functions_tournament_util import get_score_dict_by_point_system, get_standings_with_tiebreaks


class Tournament_Custom(Tournament):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Custom"
        self.parameters = {
            "games_per_round": 5,
            "rounds": 4,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Tiebreak(args={"functions": get_tiebreak_list("Buchholz")}),
            "tiebreak_2": Tiebreak(args={"functions": get_tiebreak_list("Buchholz Sum")}),
            "tiebreak_3": Tiebreak(args={"functions": get_tiebreak_list("None")}),
            "tiebreak_4": Tiebreak(args={"functions": get_tiebreak_list("None")})
        } | self.parameters
        self.parameter_display = {
            "games_per_round": "Games per Round",
            "rounds": "Rounds",
            "point_system": "Point System",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    @staticmethod
    def get_globals():
        return globals()

    def get_score_dict(self):
        return get_score_dict_by_point_system(self.get_parameter("point_system")[0])

    def is_valid_parameters(self):
        return self.get_parameter("rounds") >= max(1, self.get_round() - 1)

    def is_done(self):
        return self.get_round() > self.get_parameter("rounds")

    def get_standings(self, category_range=None):
        return get_standings_with_tiebreaks(self, {
            "results": self.get_results(), "score_dict": self.get_score_dict(),
            "all_participants": self.get_participants()
        }, category_range)

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
        participant_uuids = self.get_participant_uuids(drop_outs=False) + [None]
        self.set_pairings(self.get_parameter("games_per_round") * [(participant_uuids, participant_uuids)])
