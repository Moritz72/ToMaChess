from json import dumps
from uuid import uuid4
from copy import deepcopy
from .functions_util import shorten_float
from .functions_tournament_util import get_standings_with_tiebreaks, get_team_result, is_valid_team_seatings


class Tournament:
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        self.participants = []
        self.name = name
        self.shallow_participant_count = shallow_particpant_count
        self.parameters = parameters or dict()
        self.variables = variables or {"round": 1, "pairings": None, "results": []}
        self.order = order
        self.uuid = uuid or str(uuid4())
        self.uuid_associate = uuid_associate
        self.mode = None
        self.parameter_display = dict()
        self.convert_object_parameters()
        self.set_participants(participants)

    def __str__(self):
        return self.name

    def copy(self):
        return deepcopy(self)

    def is_team_tournament(self):
        return len(self.get_mode()) > 7 and self.get_mode()[-7:] == " (Team)"

    def convert_object_parameters(self):
        for parameter, value in self.get_parameters().items():
            if isinstance(value, dict) and set(value) == {"class", "dict"}:
                self.set_parameter(parameter, self.get_globals()[value["class"]](**value["dict"]))

    def set_participants(self, participants):
        self.participants = participants
        if self.order and participants:
            uuid_to_participant_dict = self.get_uuid_to_participant_dict()
            self.participants = [uuid_to_participant_dict[uuid] for uuid in self.order]
            self.order = None

    def possess_participants(self):
        for participant in self.get_participants():
            participant.set_uuid_associate(self.get_uuid())
            if self.is_team_tournament():
                for member in participant.get_members():
                    member.set_uuid_associate(self.get_uuid())

    @staticmethod
    def seat_participants():
        return

    @staticmethod
    def get_globals():
        return globals()

    def get_uuid(self):
        return self.uuid

    def get_uuid_associate(self):
        return self.uuid_associate

    def set_uuid_associate(self, uuid_associate):
        self.uuid_associate = uuid_associate

    def reload_uuid(self):
        self.uuid = str(uuid4())

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_mode(self):
        return self.mode

    def get_shallow_participant_count(self):
        return self.shallow_participant_count

    def get_participants(self):
        return self.participants

    def get_participant_count(self):
        return len(self.get_participants()) or self.get_shallow_participant_count() or len(self.get_participants())

    def get_participant_uuids(self):
        return [participant.get_uuid() for participant in self.get_participants()]

    def get_uuid_to_participant_dict(self):
        return {participant.get_uuid(): participant for participant in self.get_participants()}

    def get_uuid_to_individual_dict(self):
        if self.is_team_tournament():
            return {
                uuid: individual for participant in self.get_participants()
                for uuid, individual in participant.get_uuid_to_member_dict().items()
            }

    @staticmethod
    def get_score_dict():
        return {'1': 1, '½': .5, '0': 0, '+': 1, '-': 0}

    def get_score_dict_game(self):
        if self.is_team_tournament():
            return {'1': 1, '½': .5, '0': 0, '+': 1, '-': 0}

    @staticmethod
    def get_possible_scores():
        return [('1', '0'), ('½', '½'), ('0', '1'), ('+', '-'), ('-', '+'), ('-', '-')]

    def get_parameter_display(self):
        return self.parameter_display

    def get_parameters(self):
        return self.parameters

    def get_parameter(self, key):
        return self.parameters[key]

    def set_parameter(self, key, value):
        self.parameters[key] = value

    def get_variables(self):
        return self.variables

    def get_variable(self, key):
        return self.variables[key]

    def set_variable(self, key, value):
        self.variables[key] = value

    def get_data(self, include_order=True):
        parameters = self.get_parameters().copy()
        for parameter, value in parameters.items():
            if not isinstance(value, (bool, str, int, list, tuple, dict, type(None))):
                parameters[parameter] = {
                    "class": value.__class__.__name__,
                    "dict": value.__dict__,
                }
        if include_order:
            return self.get_mode(), self.get_name(), self.get_participant_count(), dumps(parameters), \
                   dumps(self.get_variables()), \
                   dumps([participant.get_uuid() for participant in self.get_participants()]), \
                   self.get_uuid(), self.get_uuid_associate()
        return self.get_mode(), self.get_name(), self.get_participant_count(), dumps(parameters), \
            dumps(self.get_variables()), self.get_uuid(), self.get_uuid_associate()

    def get_round(self):
        return self.get_variable("round")

    def set_round(self, roun):
        self.variables["round"] = roun

    def get_pairings(self):
        return self.get_variable("pairings")

    def set_pairings(self, pairings):
        self.set_variable("pairings", pairings)

    def get_results(self):
        return self.get_variable("results")

    def add_results(self, results):
        if self.is_team_tournament():
            self.variables["results_individual"].append(results)
            results = [
                tuple((uuid, score) for uuid, score in zip(pairing, get_team_result(result, self.get_score_dict())))
                for pairing, result in zip(self.get_pairings(), results)
            ]
        self.variables["results"].append(results)
        self.set_pairings(None)
        self.set_round(self.get_round() + 1)

    @staticmethod
    def get_round_name(r):
        return f"Round {r}"

    def get_simple_scores(self):
        score_dict = self.get_score_dict()
        scores = {player.get_uuid(): 0 for player in self.get_participants()}
        for roun in self.get_results():
            for (uuid_1, score_1), (uuid_2, score_2) in roun:
                if uuid_1 is not None:
                    scores[uuid_1] += score_dict[score_1]
                if uuid_2 is not None:
                    scores[uuid_2] += score_dict[score_2]
        return {uuid: shorten_float(score) for uuid, score in scores.items()}

    @staticmethod
    def is_valid_parameters():
        return True

    def is_valid(self):
        return self.is_valid_parameters() and self.get_name() and self.get_participant_count() > 1

    @staticmethod
    def is_valid_pairings(results):
        return all(uuid_1 != uuid_2 for (uuid_1, _), (uuid_2, _) in results if (uuid_1, uuid_2) != (None, None))

    def is_valid_pairings_match(self, team_uuids, results_match):
        if self.is_team_tournament():
            team_member_lists = tuple(
                None if uuid is None
                else list(self.get_uuid_to_participant_dict()[uuid].get_uuid_to_member_dict()) for uuid in team_uuids
            )
            return is_valid_team_seatings(team_uuids, team_member_lists, results_match)

    @staticmethod
    def is_done():
        return False

    def get_standings(self):
        return get_standings_with_tiebreaks(self, dict())

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
