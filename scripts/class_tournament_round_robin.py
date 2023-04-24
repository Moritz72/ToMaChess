from random import shuffle
from .class_tournament import Tournament
from .class_tiebreak import Tiebreak, tiebreaks
from .functions_util import recursive_buckets


def get_seating_from_pairings(participants, results):
    participants_and_uuids = [(participant, participant.get_uuid()) for participant in participants]
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
        participant_number = participant_number + 1
    cycle, modulo_round = divmod(roun - 1, participant_number - 1)

    uuids_rotated = [uuids[0]] + [None for _ in range(participant_number - 1)]
    for i in range(1, participant_number):
        if modulo_round >= i:
            uuids_rotated[i] = uuids[(i - 1 - modulo_round) % participant_number]
        else:
            uuids_rotated[i] = uuids[(i - modulo_round) % participant_number]

    if modulo_round % 2 or uuids_rotated[0] is None:
        uuids_rotated[0], uuids_rotated[-1] = uuids_rotated[-1], uuids_rotated[0]

    pairings = [
        (uuids_rotated[-1 - i], uuids_rotated[i])
        if i % 2 else
        (uuids_rotated[i], uuids_rotated[-1 - i])
        for i in range(int(participant_number / 2))
    ]

    if None in uuids_rotated:
        pairings = pairings[1:] + [pairings[0]]

    if cycle % 2:
        for i, (uuid_1, uuid_2) in enumerate(pairings):
            pairings[i] = (uuid_2, uuid_1)
    return pairings


class Tournament_Round_Robin(Tournament):
    def __init__(self, name, pariticipants, uuid=None):
        super().__init__(name, pariticipants, uuid)
        self.mode = "Round Robin"
        self.parameters = {
            "cycles": 1,
            "choose_seating": False,
            "point_system": ["1 - ½ - 0", "3 - 1 - 0"],
            "tiebreak 1": Tiebreak(
                args={"functions": sorted(tiebreaks.keys(), key=lambda x: x != "Direct Encounter")}
            ),
            "tiebreak 2": Tiebreak(
                args={"functions": sorted(tiebreaks.keys(), key=lambda x: x != "Sonneborn-Berger")}
            ),
            "tiebreak 3": Tiebreak(
                args={"functions": sorted(tiebreaks.keys(), key=lambda x: x != "None")}
            ),
            "tiebreak 4": Tiebreak(
                args={"functions": sorted(tiebreaks.keys(), key=lambda x: x != "None")}
            )
        }
        self.parameter_display = {
            "cycles": "Cycles",
            "choose_seating": "Choose Seating",
            "point_system": "Point System",
            "tiebreak 1": "Tiebreak (1)",
            "tiebreak 2": "Tiebreak (2)",
            "tiebreak 3": "Tiebreak (3)",
            "tiebreak 4": "Tiebreak (4)",
        }

    @staticmethod
    def get_globals():
        return globals()

    def get_score_dict(self):
        if self.get_parameter("point_system")[0] == "1 - ½ - 0":
            return super().get_score_dict()
        return {'1': 3, '½': 1, '0': 0, '+': 3, '-': 0}

    def is_valid_parameters(self):
        return self.get_parameter("cycles") > 0

    def is_valid(self):
        return self.is_valid_parameters() and self.get_name() and len(self.get_participants()) > 1

    def is_valid_pairings(self, results):
        uuids = [uuid_1 for (uuid_1, _), (_, _) in results] + [uuid_2 for (_, _), (uuid_2, _) in results]
        return len(uuids) == len(set(uuids))

    def is_done(self):
        participant_number = len(self.get_participants())
        if participant_number % 2:
            return self.get_round() > self.get_parameter("cycles") * participant_number
        else:
            return self.get_round() > self.get_parameter("cycles") * (participant_number - 1)

    def add_results(self, results):
        self.variables["results"].append([
            ((uuid_1, score_1), (uuid_2, score_2)) for (uuid_1, score_1), (uuid_2, score_2) in results
        ])

        if self.get_round() == 1 and self.get_parameter("choose_seating"):
            self.set_participants(get_seating_from_pairings(self.get_participants(), results))

        self.set_pairings(None)
        self.set_round(self.get_round() + 1)
        return True

    def get_round_name(self, r):
        if self.get_parameter("cycles") == 1:
            return super().get_round_name(r)
        participant_number = len(self.get_participants())
        if participant_number % 2:
            participant_number += 1
        cycle, modulo_round = divmod(r - 1, participant_number - 1)
        return f"Round {cycle + 1}.{modulo_round + 1}"

    def get_standings(self):
        participants = self.get_participants()
        results = self.get_results()
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
            [uuid_to_participant_dict[e[0]]] + e[1:]
            for e in recursive_buckets([[f] for f in uuid_to_participant_dict], rank_functions)
        ]
        header_vertical = self.get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
        uuids = self.get_participants_uuids()
        participant_number = len(uuids)
        roun = self.get_round()

        if roun == 1:
            if self.get_parameter("choose_seating"):
                pairings = [(uuids, uuids) for _ in range(int(participant_number / 2))]
                if participant_number % 2:
                    pairings.append((uuids, None))
                self.set_pairings(pairings)
                return
            shuffle(self.get_participants())

        uuids = self.get_participants_uuids()
        self.set_pairings(get_round_robin_pairings(uuids, participant_number, roun))
