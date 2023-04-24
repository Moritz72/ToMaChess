from .class_tournament import Tournament
from .functions_swiss_bbp import get_pairings_bbp
from .class_tiebreak import Tiebreak, tiebreaks
from .functions_util import recursive_buckets


class Tournament_Swiss(Tournament):
    def __init__(self, name, pariticipants, uuid=None):
        super().__init__(name, pariticipants, uuid)
        self.mode = "Swiss"
        self.parameters = {
            "rounds": 4,
            "point_system": ["1 - ½ - 0", "3 - 1 - 0"],
            "tiebreak 1": Tiebreak(
                args={"functions": sorted(list(tiebreaks.keys()), key=lambda x: x != "Buchholz")}
            ),
            "tiebreak 2": Tiebreak(
                args={"functions": sorted(list(tiebreaks.keys()), key=lambda x: x != "Buchholz Sum")}
            ),
            "tiebreak 3": Tiebreak(
                args={"functions": sorted(list(tiebreaks.keys()), key=lambda x: x != "None")}
            ),
            "tiebreak 4": Tiebreak(
                args={"functions": sorted(list(tiebreaks.keys()), key=lambda x: x != "None")}
            )
        }
        self.parameter_display = {
            "rounds": "Rounds",
            "point_system": "Point System",
            "tiebreak 1": "Tiebreak (1)",
            "tiebreak 2": "Tiebreak (2)",
            "tiebreak 3": "Tiebreak (3)",
            "tiebreak 4": "Tiebreak (4)"
        }

    def seat_participants(self):
        self.set_participants(sorted(self.get_participants(), key=lambda x: x.get_rating(), reverse=True))

    @staticmethod
    def get_globals():
        return globals()

    def get_score_dict(self):
        if self.get_parameter("point_system")[0] == "1 - ½ - 0":
            return super().get_score_dict()
        return {'1': 3, '½': 1, '0': 0, '+': 3, '-': 0}

    def is_valid_parameters(self):
        return self.get_parameter("rounds") > 0

    def is_valid(self):
        return self.is_valid_parameters() and self.get_name() and len(self.get_participants()) > 1

    def is_done(self):
        return self.get_round() > self.get_parameter("rounds")

    def get_standings(self):
        participants = self.get_participants()
        results = self.get_results()
        rounds = self.get_parameter("rounds")
        score_dict = self.get_score_dict()
        uuid_to_participant_dict = self.get_uuid_to_participant_dict()
        tiebreaks = [
            self.get_parameter("tiebreak 1"),
            self.get_parameter("tiebreak 2"),
            self.get_parameter("tiebreak 3"),
            self.get_parameter("tiebreak 4")
        ]

        header_horizontal = ["Name", "P"]
        rank_functions = [lambda x: self.get_simple_scores()]
        for tb in tiebreaks:
            if tb.get_abbreviation() is None:
                continue
            header_horizontal.append(tb.get_abbreviation())
            rank_functions.append(lambda x, tiebreak=tb: tiebreak.evaluate(x, results, score_dict, participants))

        table = [
            [uuid_to_participant_dict[e[0]]]+e[1:]
            for e in recursive_buckets([[e] for e in uuid_to_participant_dict], rank_functions)
        ]
        header_vertical = self.get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
        try:
            pairings = get_pairings_bbp(
                self.get_participants(),
                self.get_results(),
                self.get_parameter("rounds"),
                self.get_score_dict()
            )
        except:
            return
        self.set_pairings(pairings)
