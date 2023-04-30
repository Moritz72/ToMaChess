from .class_tournament import Tournament
from .class_tiebreak import Tiebreak, tiebreak_list
from .functions_tournament_2 import get_score_dict_by_point_system, get_standings_with_tiebreaks


class Tournament_Custom(Tournament):
    def __init__(self, name, pariticipants, uuid=None):
        super().__init__(name, pariticipants, uuid)
        self.mode = "Custom"
        self.parameters = {
            "games_per_round": 5,
            "rounds": 4,
            "point_system": ["1 - ½ - 0", "2 - 1- 0", "3 - 1 - 0"],
            "tiebreak 1": Tiebreak(
                args={"functions": sorted(tiebreak_list, key=lambda x: x != "Buchholz")}
            ),
            "tiebreak 2": Tiebreak(
                args={"functions": sorted(tiebreak_list, key=lambda x: x != "Buchholz Sum")}
            ),
            "tiebreak 3": Tiebreak(
                args={"functions": sorted(tiebreak_list, key=lambda x: x != "None")}
            ),
            "tiebreak 4": Tiebreak(
                args={"functions": sorted(tiebreak_list, key=lambda x: x != "None")}
            )
        }
        self.parameter_display = {
            "games_per_round": "Games per Round",
            "rounds": "Rounds",
            "point_system": "Point System",
            "tiebreak 1": "Tiebreak (1)",
            "tiebreak 2": "Tiebreak (2)",
            "tiebreak 3": "Tiebreak (3)",
            "tiebreak 4": "Tiebreak (4)"
        }

    @staticmethod
    def get_globals():
        return globals()

    def get_score_dict(self):
        return get_score_dict_by_point_system(self.get_parameter("point_system")[0])

    def is_valid_parameters(self):
        return self.get_parameter("rounds") > 0

    def is_valid(self):
        return self.is_valid_parameters() and self.get_name() and len(self.get_participants()) > 1

    def is_done(self):
        return self.get_round() > self.get_parameter("rounds")

    def get_standings(self):
        return get_standings_with_tiebreaks(self, {
            "results": self.get_results(), "score_dict": self.get_score_dict(),
            "all_participants": self.get_participants()
        })

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
        participant_uuids = self.get_participants_uuids() + [None]
        self.set_pairings(
            [(participant_uuids, participant_uuids) for _ in range(self.get_parameter("games_per_round"))]
        )
