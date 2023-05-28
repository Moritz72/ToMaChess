from random import shuffle
from .class_tournament import Tournament
from .class_tiebreak import Tiebreak, tiebreak_list
from .functions_tournament_util import get_score_dict_by_point_system, get_standings_with_tiebreaks


def get_seating_from_pairings(uuid_to_participant_dict, results):
    participants_and_uuids = [(participant, uuid) for uuid, participant in uuid_to_participant_dict.items()]
    if len(participants_and_uuids) % 2:
        results = [results[-1]] + results[:-1]
        results[0] = (results[0][1], results[0][0])
    order = [uuid_2 if i % 2 else uuid_1 for i, ((uuid_1, _), (uuid_2, _)) in enumerate(results)] + \
            [uuid_1 if i % 2 else uuid_2 for i, ((uuid_1, _), (uuid_2, _)) in enumerate(results)][::-1]
    participants_and_uuids = sorted(participants_and_uuids, key=lambda x: order.index(x[1]))
    return [participant for participant, _ in participants_and_uuids]


def get_round_robin_pairings(uuids, participant_number, roun):
    if participant_number % 2:
        uuids = [None] + uuids
        participant_number += 1
    cycle, modulo_round = divmod(roun - 1, participant_number - 1)

    uuids_rotated = [uuids[0]] + (participant_number - 1) * [None]
    for i in range(1, participant_number):
        if modulo_round >= i:
            uuids_rotated[i] = uuids[(i - 1 - modulo_round) % participant_number]
        else:
            uuids_rotated[i] = uuids[(i - modulo_round) % participant_number]

    if modulo_round % 2 or uuids_rotated[0] is None:
        uuids_rotated[0], uuids_rotated[-1] = uuids_rotated[-1], uuids_rotated[0]

    pairings = [
        (uuids_rotated[-1 - i], uuids_rotated[i]) if i % 2 else (uuids_rotated[i], uuids_rotated[-1 - i])
        for i in range(int(participant_number / 2))
    ]

    if None in uuids_rotated:
        pairings = pairings[1:] + [pairings[0]]

    if cycle % 2:
        for i, (uuid_1, uuid_2) in enumerate(pairings):
            pairings[i] = (uuid_2, uuid_1)
    return pairings


class Tournament_Round_Robin(Tournament):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Round Robin"
        self.parameters = parameters or {
            "cycles": 1,
            "choose_seating": False,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "Direct Encounter")}),
            "tiebreak_2": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "Sonneborn-Berger")}),
            "tiebreak_3": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "None")}),
            "tiebreak_4": Tiebreak(args={"functions": sorted(tiebreak_list, key=lambda x: x != "None")})
        }
        self.parameter_display = {
            "cycles": "Cycles",
            "choose_seating": "Choose Seating",
            "point_system": "Point System",
            "tiebreak_1": "Tiebreak (1)",
            "tiebreak_2": "Tiebreak (2)",
            "tiebreak_3": "Tiebreak (3)",
            "tiebreak_4": "Tiebreak (4)",
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
        if self.get_round() == 2 and self.get_parameter("choose_seating"):
            self.set_participants(get_seating_from_pairings(self.get_uuid_to_participant_dict(), results))

    def get_round_name(self, r):
        if self.get_parameter("cycles") == 1:
            return super().get_round_name(r)
        participant_number = len(self.get_participants())
        if participant_number % 2:
            participant_number += 1
        cycle, modulo_round = divmod(r - 1, participant_number - 1)
        return f"Round {cycle + 1}.{modulo_round + 1}"

    def get_standings(self, category_range=None):
        return get_standings_with_tiebreaks(self, {
            "results": self.get_results(), "score_dict": self.get_score_dict(),
            "all_participants": self.get_participants()
        }, category_range)

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
        uuids = self.get_participant_uuids()
        participant_number = len(uuids)
        roun = self.get_round()

        if roun == 1:
            if self.get_parameter("choose_seating"):
                pairings = int(participant_number / 2) * [(uuids, uuids)]
                if participant_number % 2:
                    pairings.append((uuids, None))
                self.set_pairings(pairings)
                return
            shuffle(self.get_participants())

        self.set_pairings(get_round_robin_pairings(self.get_participant_uuids(), participant_number, roun))
