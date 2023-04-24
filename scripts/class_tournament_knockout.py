from .class_tournament import Tournament
from .class_armageddon import Armageddon
from .functions_util import shorten_float


def move_on(uuid_1, uuid_2, participant_standings):
    participant_standings[uuid_1]["level"] += 1
    participant_standings[uuid_1]["score"] = 0
    participant_standings[uuid_1]["seating"] = min(
        participant_standings[uuid_1]["seating"], participant_standings[uuid_2]["seating"]
    )
    participant_standings[uuid_2]["alive"] = False


def update_participant_standings(results, participant_standings, score_dict, games, armageddon):
    for (uuid_1, score_1), (uuid_2, score_2) in results:
        if score_1 == '-' == score_2:
            participant_standings[uuid_1]["score"] += .5
            participant_standings[uuid_2]["score"] += .5
        else:
            participant_standings[uuid_1]["score"] += score_dict[score_1]
            participant_standings[uuid_2]["score"] += score_dict[score_2]

        score_sum = participant_standings[uuid_1]["score"] + participant_standings[uuid_2]["score"]
        if armageddon.is_armageddon(games, score_sum):
            if score_dict[score_1] > score_dict[score_2]:
                move_on(uuid_1, uuid_2, participant_standings)
            else:
                move_on(uuid_2, uuid_1, participant_standings)
        elif score_sum <= games:
            if participant_standings[uuid_1]["score"] > games / 2:
                move_on(uuid_1, uuid_2, participant_standings)
            elif participant_standings[uuid_2]["score"] > games / 2:
                move_on(uuid_2, uuid_1, participant_standings)
        elif (score_sum - games) % 2 == 0:
            if participant_standings[uuid_1]["score"] > participant_standings[uuid_2]["score"]:
                move_on(uuid_1, uuid_2, participant_standings)
            elif participant_standings[uuid_1]["score"] < participant_standings[uuid_2]["score"]:
                move_on(uuid_2, uuid_1, participant_standings)


def get_current_level(participant_standings):
    min_level = None
    for standing in participant_standings.values():
        if standing["alive"] and (min_level is None or standing["level"] < min_level):
            min_level = standing["level"]
    return min_level


def get_uuids_in_current_level(participant_standings):
    current_level = get_current_level(participant_standings)
    if current_level == 0:
        through = 2 * (1 << (len(participant_standings).bit_length() - 1)) - len(participant_standings)
        uuids = [uuid for uuid, standing in participant_standings.items() if standing["seating"] > through]
    else:
        uuids = [uuid for uuid, standing in participant_standings.items() if standing["level"] >= current_level]
    return [
        uuid for uuid in uuids
        if participant_standings[uuid]["alive"] and participant_standings[uuid]["level"] == current_level
    ]


def get_end_rounds(participant_standings, games, armageddon):
    levels_max = {}
    for standing in participant_standings.values():
        if standing["level"] not in levels_max or levels_max[standing["level"]] < standing["score"]:
            levels_max[standing["level"]] = standing["score"]
    end_rounds = [
        int(games / 2 + max_val + 1) if max_val < games / 2
        else games + 2 + 2 * int(max_val - games / 2)
        for level, max_val in sorted(levels_max.items())
    ]
    return [roun - armageddon.is_armageddon(games, roun) for roun in end_rounds]


class Tournament_Knockout(Tournament):
    def __init__(self, name, pariticipants, uuid=None):
        super().__init__(name, pariticipants, uuid)
        self.mode = "Knockout"
        self.parameters = {
            "games": 2,
            "armageddon": Armageddon()
        }
        self.parameter_display = {
            "games": "Games per Match",
            "armageddon": "Armageddon"
        }
        variables = {
            "participant_standings": None
        }
        self.variables = self.variables | variables

    def seat_participants(self):
        self.set_participants(sorted(self.get_participants(), key=lambda x: x.get_rating(), reverse=True))

    @staticmethod
    def get_globals():
        return globals()

    def set_participants(self, participants):
        super().set_participants(participants)
        if len(participants) < 2:
            return
        participant_uuids = self.get_participants_uuids()
        through = 2 * (1 << (len(participant_uuids).bit_length() - 1)) - len(participant_uuids)
        self.set_variable(
            "participant_standings",
            {uuid: {
                "level": 1 if i < through else 0, "score": 0, "alive": True, "seating": i+1
            } for i, uuid in enumerate(participant_uuids)}
        )

    def is_valid_parameters(self):
        return self.get_parameter("games") and not self.get_parameter("games") % 2

    def is_valid(self):
        return self.is_valid_parameters() and self.get_name() and len(self.get_participants()) > 1

    def is_done(self):
        return sum((standing["alive"] for standing in self.get_variable("participant_standings").values())) == 1

    def add_results(self, results):
        self.variables["results"].append([
            ((uuid_1, score_1), (uuid_2, score_2)) for (uuid_1, score_1), (uuid_2, score_2) in results
        ])

        update_participant_standings(
            self.variables.get("results")[-1], self.get_variable("participant_standings"),
            self.get_score_dict(), self.get_parameter("games"), self.get_parameter("armageddon")
        )

        self.set_pairings(None)
        self.set_round(self.get_round() + 1)
        return True

    def get_round_name(self, r):
        games = self.get_parameter("games")
        armageddon = self.get_parameter("armageddon")
        participant_standings = self.get_variable("participant_standings")
        end_rounds = get_end_rounds(participant_standings, games, armageddon)

        counter = 1
        while len(end_rounds) > 0 and r > end_rounds[0]:
            r -= end_rounds.pop(0)
            counter += 1

        if armageddon.is_armageddon(games, r):
            return f"Round {counter}.A"
        elif r <= games:
            return f"Round {counter}.{r}"
        else:
            return f"Round {counter}.T{r - games}"

    def get_standings(self):
        header_horizontal = ["Name", "M", "MP"]
        participant_standings = self.get_variable("participant_standings")

        table = sorted((
            (
                participant,
                participant_standings[participant.get_uuid()]["level"]-1,
                shorten_float(participant_standings[participant.get_uuid()]["score"])
            ) for participant in self.get_participants()
        ), key=lambda x: x[1:], reverse=True)

        header_vertical = self.get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
        participant_uuids = self.get_participants_uuids()
        games = self.get_parameter("games")
        armageddon = self.get_parameter("armageddon")
        participant_standings = self.get_variable("participant_standings")

        uuids = sorted(
            get_uuids_in_current_level(participant_standings), key=lambda x: participant_standings[x]["seating"]
        )
        pairings = [(uuids[i], uuids[i+int(len(uuids)/2)]) for i in range(int(len(uuids)/2))]
        score_sum = participant_standings[pairings[0][0]]["score"]+participant_standings[pairings[0][1]]["score"]

        if armageddon.is_armageddon(games, score_sum+1):
            self.set_pairings([armageddon.determine_color(uuid_1, uuid_2) for uuid_1, uuid_2 in pairings])
        elif score_sum % 2:
            self.set_pairings([(uuid_2, uuid_1) for uuid_1, uuid_2 in pairings])
        else:
            self.set_pairings(pairings)
