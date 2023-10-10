from random import random
from .class_tournament import Tournament
from .functions_swiss_bbp import get_pairings_bbp
from .class_tiebreak import Tiebreak, get_tiebreak_list
from .functions_pairing import PAIRING_FUNCTIONS
from .functions_tournament_util import get_score_dict_by_point_system, get_standings_with_tiebreaks
from .functions_player import sort_players_by_rating


class Tournament_Swiss(Tournament):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Swiss"
        self.parameters = {
            "rounds": 5,
            "pairing_method_first_round": ["Slide", "Fold", "Adjacent", "Random", "Custom"],
            "top_seed_color_first_round": ["White", "Black", "Random"],
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Tiebreak(args={"functions": get_tiebreak_list("Buchholz")}),
            "tiebreak_2": Tiebreak(args={"functions": get_tiebreak_list("Buchholz Sum")}),
            "tiebreak_3": Tiebreak(args={"functions": get_tiebreak_list("None")}),
            "tiebreak_4": Tiebreak(args={"functions": get_tiebreak_list("None")})
        } | self.parameters
        self.parameter_display = {
            "rounds": "Rounds",
            "pairing_method_first_round": "Pairings (First Round)",
            "top_seed_color_first_round": "Top Seed (First Round)",
            "point_system": "Point System",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    def seat_participants(self):
        self.set_participants(sort_players_by_rating(self.get_participants()))

    @staticmethod
    def get_globals():
        return globals()

    def get_score_dict(self):
        return get_score_dict_by_point_system(self.get_parameter("point_system")[0])

    def is_valid_parameters(self):
        return self.get_parameter("rounds") >= max(1, self.get_round() - 1)

    def is_valid_pairings(self, results):
        uuids = [uuid_1 for (uuid_1, _), (_, _) in results] + [uuid_2 for (_, _), (uuid_2, _) in results]
        return len(uuids) == len(set(uuids))

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
        uuids = self.get_participant_uuids(drop_outs=False)
        participant_number = len(uuids)
        first_round = self.get_variable("round") == 1
        first_round_method = self.get_parameter("pairing_method_first_round")[0]

        if first_round and first_round_method == "Custom":
            pairings = int(participant_number / 2) * [(uuids, uuids)]
            if participant_number % 2:
                pairings.append((uuids, None))
        elif first_round:
            match self.get_parameter("top_seed_color_first_round")[0]:
                case "White":
                    first_seed_white = True
                case "Black":
                    first_seed_white = False
                case _:
                    first_seed_white = random() > .5
            if participant_number % 2:
                uuids.append(None)
            pairing_indices = PAIRING_FUNCTIONS[first_round_method](participant_number, first_seed_white)
            pairings = [(uuids[i_1], uuids[i_2]) for i_1, i_2 in pairing_indices]
        else:
            pairings = get_pairings_bbp(
                self.get_participants(), self.get_results(), self.get_parameter("rounds"), self.get_score_dict(),
                self.get_variable("drop_outs")
            )
        self.set_pairings(pairings)
