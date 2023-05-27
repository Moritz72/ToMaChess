from .class_tournament_knockout import Tournament_Knockout
from .class_armageddon import Armageddon
from .functions_util import shorten_float
from .functions_tournament_util import get_standings_header_vertical, get_team_result


def move_on(uuid_1, uuid_2, participant_standings):
    participant_standings[uuid_1]["level"] += 1
    participant_standings[uuid_1]["score"] = 0
    participant_standings[uuid_1]["board_points"] = 0
    participant_standings[uuid_1]["bewe"] = 0
    participant_standings[uuid_1]["seating"] = min(
        participant_standings[uuid_1]["seating"], participant_standings[uuid_2]["seating"]
    )
    participant_standings[uuid_2]["alive"] = False


def add_result_to_participant_standings(
        uuid_1, uuid_2, score_1, score_2, participant_standings, score_dict, individual):
    if score_1 == '-' == score_2:
        participant_standings[uuid_1]["score"] += .5
        participant_standings[uuid_2]["score"] += .5
    else:
        participant_standings[uuid_1]["score"] += score_dict[score_1]
        participant_standings[uuid_2]["score"] += score_dict[score_2]
    participant_standings[uuid_1]["board_points"] += sum(
        .5 if score_1 == '-' == score_2 else score_dict[score_1] for (_, score_1), (_, score_2) in individual
    )
    participant_standings[uuid_2]["board_points"] += sum(
        .5 if score_1 == '-' == score_2 else score_dict[score_2] for (_, score_1), (_, score_2) in individual
    )
    participant_standings[uuid_1]["bewe"] += sum(
        .5 * (len(individual) - i) if score_1 == '-' == score_2 else score_dict[score_1] * (len(individual) - i)
        for i, ((_, score_1), (_, score_2)) in enumerate(individual)
    )
    participant_standings[uuid_2]["bewe"] += sum(
        .5 * (len(individual) - i) if score_1 == '-' == score_2 else score_dict[score_2] * (len(individual) - i)
        for i, ((_, score_1), (_, score_2)) in enumerate(individual)
    )


def get_value_tuple(participant_standings, uuid):
    return participant_standings[uuid]["score"], participant_standings[uuid]["board_points"], \
           participant_standings[uuid]["bewe"]


def update_participant_standings(
        results, results_individual, participant_standings, score_dict, games, games_per_tiebreak
):
    for ((uuid_1, score_1), (uuid_2, score_2)), individual in zip(results, results_individual):
        add_result_to_participant_standings(
            uuid_1, uuid_2, score_1, score_2, participant_standings, score_dict, individual
        )
        score_sum = participant_standings[uuid_1]["score"] + participant_standings[uuid_2]["score"]
        if score_sum < games:
            if participant_standings[uuid_1]["score"] > games / 2:
                move_on(uuid_1, uuid_2, participant_standings)
            elif participant_standings[uuid_2]["score"] > games / 2:
                move_on(uuid_2, uuid_1, participant_standings)
        elif (score_sum - games) % games_per_tiebreak == 0:
            tuple_1 = get_value_tuple(participant_standings, uuid_1)
            tuple_2 = get_value_tuple(participant_standings, uuid_2)
            if tuple_1 > tuple_2:
                move_on(uuid_1, uuid_2, participant_standings)
            elif tuple_2 > tuple_1:
                move_on(uuid_2, uuid_1, participant_standings)


def get_end_rounds(participant_standings, games, games_per_tiebreak, boards):
    levels_max = dict()
    for standing in participant_standings.values():
        value_tuple = (standing["score"], standing["board_points"], standing["bewe"])
        if standing["level"] not in levels_max or levels_max[standing["level"]] < value_tuple:
            levels_max[standing["level"]] = value_tuple
    end_rounds = []
    for level, (max_score, max_board_points, max_bewe) in sorted(levels_max.items()):
        if max_score < games / 2:
            end_rounds.append(int(games / 2 + max_score + 1))
        else:
            div, mod = divmod(max_score - games / 2, games_per_tiebreak / 2)
            estimate = games + games_per_tiebreak * int(div)
            if (max_board_points, max_bewe) >= (estimate * boards / 2, estimate * boards * (boards + 1) / 4):
                estimate += int(games_per_tiebreak / 2 + mod + 1)
            end_rounds.append(estimate)
    return end_rounds


class Tournament_Knockout_Team(Tournament_Knockout):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Knockout (Team)"
        self.parameters = parameters or {
            "boards": 8,
            "games": 1,
            "games_per_tiebreak": 1,
            "armageddon": Armageddon()
        }
        self.parameter_display = {
            "boards": "Boards",
            "games": "Games per Match",
            "games_per_tiebreak": None,
            "armageddon": None
        }
        self.variables = variables or self.variables | {"results_individual": []}

    def set_participants(self, participants):
        super().set_participants(participants)
        if len(self.get_participant_uuids()) < 2 or self.get_round() > 1:
            return
        for dictionary in self.get_variable("participant_standings").values():
            dictionary["board_points"] = 0
            dictionary["bewe"] = 0

    def seat_participants(self):
        return

    def is_valid_parameters(self):
        return super().is_valid_parameters() and self.get_parameter("boards") > 0

    def add_results(self, results):
        self.variables["results_individual"].append(results)
        results_team = [
            tuple((uuid, score) for uuid, score in zip(pairing, get_team_result(result, self.get_score_dict())))
            for pairing, result in zip(self.get_pairings(), results)
        ]
        self.variables["results"].append(results_team)
        self.set_pairings(None)
        self.set_round(self.get_round() + 1)
        update_participant_standings(
            self.get_variable("results")[-1], self.get_variable("results_individual")[-1],
            self.get_variable("participant_standings"), self.get_score_dict(),
            self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        )

    def get_round_name(self, r):
        games = self.get_parameter("games")
        games_per_tiebreak = self.get_parameter("games_per_tiebreak")
        participant_standings = self.get_variable("participant_standings")
        boards = self.get_parameter("boards")
        end_rounds = get_end_rounds(participant_standings, games, games_per_tiebreak, boards)

        counter = 1
        while len(end_rounds) > 0 and r > end_rounds[0]:
            r -= end_rounds.pop(0)
            counter += 1

        if r <= games:
            if games == 1:
                return f"Round {counter}"
            return f"Round {counter}.{r}"
        return f"Round {counter}.T{r - games}"

    def get_standings(self):
        header_horizontal = ["Name", "M", "MaPo", "BoPo", "BeWe"]
        participant_standings = self.get_variable("participant_standings")

        table = sorted((
            (
                participant,
                participant_standings[participant.get_uuid()]["level"]-1,
                shorten_float(participant_standings[participant.get_uuid()]["score"]),
                shorten_float(participant_standings[participant.get_uuid()]["board_points"]),
                shorten_float(participant_standings[participant.get_uuid()]["bewe"])
            ) for participant in self.get_participants()
        ), key=lambda x: x[1:], reverse=True)

        header_vertical = get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table
