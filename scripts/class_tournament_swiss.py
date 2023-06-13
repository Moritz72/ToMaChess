from .class_tournament import Tournament
from .functions_swiss_bbp import get_pairings_bbp
from .class_tiebreak import Tiebreak, tiebreak_list
from .functions_tournament_util import get_score_dict_by_point_system, get_standings_with_tiebreaks


class Tournament_Swiss(Tournament):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Swiss"
        self.parameters = parameters or {
            "rounds": 4,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "Buchholz")}),
            "tiebreak_2": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "Buchholz Sum")}),
            "tiebreak_3": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "None")}),
            "tiebreak_4": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "None")})
        }
        self.parameter_display = {
            "rounds": "Rounds",
            "point_system": "Point System",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    def seat_participants(self):
        self.set_participants(sorted(
            self.get_participants(), key=lambda x: 0 if x.get_rating() is None else x.get_rating(), reverse=True
        ))

    @staticmethod
    def get_globals():
        return globals()

    def get_score_dict(self):
        return get_score_dict_by_point_system(self.get_parameter("point_system")[0])

    def is_valid_parameters(self):
        return self.get_parameter("rounds") > 0

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
        try:
            pairings = get_pairings_bbp(
                self.get_participants(), self.get_results(), self.get_parameter("rounds"), self.get_score_dict()
            )
        except:
            return
        self.set_pairings(pairings)
