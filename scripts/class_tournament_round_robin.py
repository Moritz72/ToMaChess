from random import shuffle
from .class_tournament import Tournament
from .class_tiebreak import Tiebreak, get_tiebreak_list
from .functions_pairing import PAIRING_FUNCTIONS
from .functions_tournament_util import get_score_dict_by_point_system, get_standings_with_tiebreaks


class Tournament_Round_Robin(Tournament):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Round Robin"
        self.parameters = {
            "cycles": 1,
            "pairing_method": ["Cycle", "Berger"],
            "choose_seating": False,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Tiebreak(args={"functions": get_tiebreak_list("Direct Encounter")}),
            "tiebreak_2": Tiebreak(args={"functions": get_tiebreak_list("Sonneborn-Berger")}),
            "tiebreak_3": Tiebreak(args={"functions": get_tiebreak_list("None")}),
            "tiebreak_4": Tiebreak(args={"functions": get_tiebreak_list("None")})
        } | self.parameters
        self.parameter_display = {
            "cycles": "Cycles",
            "pairing_method": "Pairing Method",
            "choose_seating": "Choose Seating",
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
        return self.get_parameter("cycles") > 0

    def is_valid_pairings(self, results):
        uuids = [uuid_1 for (uuid_1, _), (_, _) in results] + [uuid_2 for (_, _), (uuid_2, _) in results]
        return len(uuids) == len(set(uuids))

    def is_done(self):
        participant_number = len(self.get_participants())
        if participant_number % 2:
            return self.get_round() > self.get_parameter("cycles") * participant_number
        return self.get_round() > self.get_parameter("cycles") * (participant_number - 1)

    def add_results(self, results):
        super().add_results(results)
        if self.get_round() != 2 or not self.get_parameter("choose_seating"):
            return

        uuid_to_seat = dict()
        pairings = PAIRING_FUNCTIONS[self.get_parameter("pairing_method")[0]](len(self.get_participants()), 1)
        for ((uuid_1, _), (uuid_2, _)), (p_1, p_2) in zip(results, pairings):
            uuid_to_seat[uuid_1], uuid_to_seat[uuid_2] = p_1, p_2
        self.set_participants(sorted(self.get_participants(), key=lambda x: uuid_to_seat[x.get_uuid()]))

    def get_round_name(self, r):
        if self.get_parameter("cycles") == 1:
            return super().get_round_name(r)
        participant_number = len(self.get_participants())
        if participant_number % 2:
            participant_number += 1
        div, mod = divmod(r - 1, participant_number - 1)
        return "Round", f" {div + 1}.{mod + 1}"

    def get_standings(self, category_range=None):
        return get_standings_with_tiebreaks(self, {
            "results": self.get_results(), "score_dict": self.get_score_dict(),
            "all_participants": self.get_participants()
        }, category_range)

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return

        participant_number = len(self.get_participants())
        roun = self.get_round()

        if roun == 1 and self.get_parameter("choose_seating"):
            pairings = int(participant_number / 2) * [(self.get_participant_uuids(), self.get_participant_uuids())]
            if participant_number % 2:
                pairings.append((self.get_participant_uuids(), None))
            self.set_pairings(pairings)
            return

        if roun == 1:
            shuffle(self.get_participants())

        uuids = self.get_participant_uuids()
        if participant_number % 2:
            uuids = uuids + [None]
        pairing_indices = PAIRING_FUNCTIONS[self.get_parameter("pairing_method")[0]](participant_number, roun)
        pairings = [(uuids[i_1], uuids[i_2]) for i_1, i_2 in pairing_indices]
        self.set_pairings(pairings)
