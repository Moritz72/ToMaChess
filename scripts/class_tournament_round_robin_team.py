from .class_tournament_round_robin import Tournament_Round_Robin
from .class_tiebreak import Tiebreak, tiebreak_list_team
from .functions_team import load_team_from_file
from .functions_tournament_2 import get_standings_with_tiebreaks, get_team_result, is_valid_team_seatings,\
    get_score_dict_by_point_system


class Tournament_Round_Robin_Team(Tournament_Round_Robin):
    def __init__(self, name, participants, uuid=None):
        super().__init__(name, participants, uuid)
        self.mode = "Round Robin (Team)"
        self.parameters = {
            "boards": 8,
            "cycles": 1,
            "choose_seating": False,
            "point_system": ["2 - 1 - 0", "1 - ½ - 0", "3 - 1 - 0"],
            "point_system_game": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak 1": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "Board Points")}
            ),
            "tiebreak 2": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "Direct Encounter")}
            ),
            "tiebreak 3": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "Sonneborn-Berger")}
            ),
            "tiebreak 4": Tiebreak(
                args={"functions": sorted(tiebreak_list_team, key=lambda x: x != "None")}
            )
        }
        self.parameter_display = {
            "boards": "Boards",
            "cycles": "Cycles",
            "choose_seating": None,
            "point_system_match": "Point System (Match)",
            "point_system": "Point System (Game)",
            "tiebreak 1": "Tiebreak (1)",
            "tiebreak 2": "Tiebreak (2)",
            "tiebreak 3": "Tiebreak (3)",
            "tiebreak 4": "Tiebreak (4)"
        }
        self.variables = self.variables | {"results_individual": []}

    def load_from_json(self, directory, json, load_participants_function=load_team_from_file):
        super().load_from_json(directory, json, load_participants_function)

    def get_score_dict_game(self):
        return get_score_dict_by_point_system(self.get_parameter("point_system_game")[0])

    def get_uuid_to_individual_dict(self):
        return {
            uuid: individual for participant in self.get_participants()
            for uuid, individual in participant.get_uuid_to_member_dict().items()
        }

    def add_results(self, results):
        self.variables["results_individual"].append(results)
        results_team = [
            tuple((uuid, score) for uuid, score in zip(pairing, get_team_result(result, self.get_score_dict())))
            for pairing, result in zip(self.get_pairings(), results)
        ]
        super().add_results(results_team)

    def is_valid_parameters(self):
        return super().is_valid_parameters() and self.get_parameter("boards") > 0

    def is_valid_pairings_match(self, team_uuids, results_match):
        team_member_lists = tuple(
            None if uuid is None
            else list(self.get_uuid_to_participant_dict()[uuid].get_uuid_to_member_dict()) for uuid in team_uuids
        )
        return is_valid_team_seatings(team_uuids, team_member_lists, results_match)

    def get_standings(self):
        return get_standings_with_tiebreaks(self, {
            "results": self.get_results(), "score_dict": self.get_score_dict(),
            "score_dict_game": self.get_score_dict_game(), "all_participants": self.get_participants(),
            "results_individual": self.get_variable("results_individual")
        })
