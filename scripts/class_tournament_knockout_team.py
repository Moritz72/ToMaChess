from .class_tournament import Tournament
from .class_tournament_knockout import Tournament_Knockout
from .class_armageddon import Armageddon
from .functions_util import shorten_float
from .functions_tournament_util import get_standings_header_vertical
from .functions_categories import filter_list_by_category_range


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
        Tournament.__init__(
            self, participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Knockout (Team)"
        self.parameters = {
            "boards": 8,
            "enforce_lineups": True,
            "games": 1,
            "games_per_tiebreak": 1,
            "pairing_method": ["Slide", "Fold", "Adjacent", "Random"],
            "armageddon": Armageddon()
        } | self.parameters
        self.parameter_display = {
            "boards": "Boards",
            "enforce_lineups": "Enforce Lineups",
            "games": "Games per Match",
            "games_per_tiebreak": None,
            "pairing_method": "Pairing Method",
            "armageddon": None
        }
        self.variables = {"participant_standings": dict(), "results_individual": []} | self.variables

    def is_valid_parameters(self):
        return super().is_valid_parameters() and self.get_parameter("boards") > 0

    @staticmethod
    def get_initial_score():
        return [0, 0, 0]

    def get_totals(self):
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        boards = self.get_parameter("boards")
        return [games, games * boards, games * boards * (boards + 1) / 2], \
               [games_per_tiebreak, games_per_tiebreak * boards, games_per_tiebreak * boards * (boards + 1) / 2]

    def get_latest_scores(self):
        return [
            get_scores(score_1, score_2, individual, self.get_score_dict(), self.get_score_dict_game())
            for ((uuid_1, score_1), (uuid_2, score_2)), individual
            in zip(self.get_results()[-1], self.get_results_individual()[-1])
        ]

    def get_standings(self, category_range=None):
        header_horizontal = ["Name", "Matches", "Match Points", "Board Points", "Berliner Wertung"]
        participant_standings = self.get_variable("participant_standings")
        participants = self.get_participants()
        if category_range is not None:
            participants = filter_list_by_category_range(participants, *category_range)

        table = sorted((
            (
                participant,
                participant_standings[participant.get_uuid()]["level"],
                shorten_float(participant_standings[participant.get_uuid()]["score"][0]),
                shorten_float(participant_standings[participant.get_uuid()]["score"][1]),
                shorten_float(participant_standings[participant.get_uuid()]["score"][2])
            ) for participant in participants
        ), key=lambda x: x[1:], reverse=True)

        header_vertical = get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table
