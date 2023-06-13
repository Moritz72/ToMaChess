from .class_tournament import Tournament
from .class_tournament_knockout import Tournament_Knockout
from .class_armageddon import Armageddon
from .functions_util import shorten_float
from .functions_tournament_knockout import get_end_rounds, update_participant_standings, reverse_participant_standings
from .functions_tournament_util import get_standings_header_vertical
from .functions_categories import filter_list_by_category_range


def get_totals(games, games_per_tiebreak, boards):
    return [games, games * boards, games * boards * (boards + 1) / 2], \
           [games_per_tiebreak, games_per_tiebreak * boards, games_per_tiebreak * boards * (boards + 1) / 2]


def get_scores_mini(score_1, score_2, score_dict, factor=1):
    if score_1 == '-' == score_2:
        return .5 * factor, .5 * factor
    return score_dict[score_1] * factor, score_dict[score_2] * factor


def get_scores(score_1, score_2, individual, score_dict, score_dict_game):
    team_points = get_scores_mini(score_1, score_2, score_dict)
    board_points = [get_scores_mini(score_1, score_2, score_dict_game) for (_, score_1), (_, score_2) in individual]
    berlins = [
        get_scores_mini(score_1, score_2, score_dict_game, factor=len(individual) - i)
        for i, ((_, score_1), (_, score_2)) in enumerate(individual)
    ]
    return [[team_points[i], sum(bo[i] for bo in board_points), sum(be[i] for be in berlins)] for i in range(2)]


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
            dictionary["score"] = [0, 0, 0]

    def seat_participants(self):
        return

    def is_valid_parameters(self):
        return super().is_valid_parameters() and self.get_parameter("boards") > 0

    def add_results(self, results):
        Tournament.add_results(self, results)
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        for ((uuid_1, score_1), (uuid_2, score_2)), individual \
                in zip(self.get_results()[-1], self.get_results_individual()[-1]):
            update_participant_standings(
                uuid_1, uuid_2,
                *get_scores(score_1, score_2, individual, self.get_score_dict(), self.get_score_dict_game()),
                self.get_variable("participant_standings"), games, games_per_tiebreak, self.get_parameter("armageddon"),
                *get_totals(games, games_per_tiebreak, self.get_parameter("boards"))
            )

    def remove_results(self):
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        for ((uuid_1, score_1), (uuid_2, score_2)), individual \
                in zip(self.get_results()[-1], self.get_results_individual()[-1]):
            reverse_participant_standings(
                uuid_1, uuid_2,
                *get_scores(score_1, score_2, individual, self.get_score_dict(), self.get_score_dict_game()),
                self.get_variable("participant_standings"), games, games_per_tiebreak, self.get_parameter("armageddon"),
                *get_totals(games, games_per_tiebreak, self.get_parameter("boards"))
            )
        Tournament.remove_results(self)

    def get_round_name(self, r):
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        armageddon = self.get_parameter("armageddon")
        end_rounds = get_end_rounds(
            self.get_variable("participant_standings"), games, games_per_tiebreak, armageddon,
            *get_totals(games, games_per_tiebreak, self.get_parameter("boards"))
        )

        counter = 1
        while len(end_rounds) > 0 and r > end_rounds[0]:
            r -= end_rounds.pop(0)
            counter += 1

        if armageddon.is_armageddon(games, games_per_tiebreak, r):
            return "Round", f" {counter}.A"
        if r <= games:
            if games == 1:
                return "Round", f" {counter}"
            return "Round", f" {counter}.{r}"
        return "Round", f" {counter}.T{r - games}"

    def get_standings(self, category_range=None):
        header_horizontal = ["Name", "Matches", "Match Points", "Board Points", "Berliner Wertung"]
        participant_standings = self.get_variable("participant_standings")
        participants = self.get_participants()
        if category_range is not None:
            participants = filter_list_by_category_range(participants, *category_range)

        table = sorted((
            (
                participant,
                participant_standings[participant.get_uuid()]["level"] - 1,
                shorten_float(participant_standings[participant.get_uuid()]["score"][0]),
                shorten_float(participant_standings[participant.get_uuid()]["score"][1]),
                shorten_float(participant_standings[participant.get_uuid()]["score"][2])
            ) for participant in participants
        ), key=lambda x: x[1:], reverse=True)

        header_vertical = get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table
