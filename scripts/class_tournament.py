from json import dumps
from uuid import uuid4
from copy import deepcopy
from os import mkdir
from os.path import exists
from shutil import rmtree
from .functions_player import load_player
from .functions_util import shorten_float, get_root_directory, write_file


def get_directory(directory, uuid):
    return f"{get_root_directory()}/{directory}/{uuid}"


class Tournament:
    def __init__(self, name, pariticipants, uuid=None):
        if uuid is None:
            self.uuid = str(uuid4())
        else:
            self.uuid = uuid
        self.name = name
        self.participants = pariticipants
        self.mode = None
        self.parameters = {}
        self.parameter_display = {}
        self.variables = {
            "round": 1,
            "pairings": None,
            "results": []
        }

    def __str__(self):
        return self.name

    def dump_to_json(self):
        data = deepcopy(self.__dict__)
        data["participants"] = [participant.get_uuid() for participant in data["participants"]]
        for parameter, value in data["parameters"].items():
            if not isinstance(value, (bool, str, int, list, tuple, dict, type(None))):
                data["parameters"][parameter] = {
                    "class": value.__class__.__name__,
                    "dict": value.__dict__,
                }
        return dumps(data)

    def load_from_json(self, directory, json):
        players = [load_player(uuid, f"{directory}/{json['uuid']}/participants") for uuid in json["participants"]]
        self.set_participants(players)
        for parameter, value in json["parameters"].items():
            self.set_parameter(parameter, value)
        for variable, value in json["variables"].items():
            self.set_variable(variable, value)
        for parameter, value in self.get_parameters():
            if isinstance(value, dict) and set(value) == {"class", "dict"}:
                self.set_parameter(parameter, self.get_globals()[value["class"]](**value["dict"]))

    def save(self, directory="data/tournaments"):
        uuid = self.get_uuid()

        if not exists(get_directory(directory, uuid)):
            mkdir(get_directory(directory, uuid))
            mkdir(f"{get_directory(directory, uuid)}/participants")

        for participant in self.get_participants():
            participant.save(f"{directory}/{uuid}/participants")
        write_file(f"{get_directory(directory, uuid)}/tournament.json", self.dump_to_json())

    def remove(self, directory="data/tournaments"):
        rmtree(get_directory(directory, self.get_uuid()))

    def set_participants(self, participants):
        self.participants = participants

    @staticmethod
    def seat_participants():
        return

    @staticmethod
    def get_globals():
        return globals()

    def get_uuid(self):
        return self.uuid

    def reload_uuid(self):
        self.uuid = str(uuid4())

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_mode(self):
        return self.mode

    def get_participants(self):
        return self.participants

    def get_participants_uuids(self):
        return [participant.get_uuid() for participant in self.get_participants()]

    def get_uuid_to_participant_dict(self):
        return {participant.get_uuid(): participant for participant in self.get_participants()}

    @staticmethod
    def get_score_dict():
        return {'1': 1, '½': .5, '0': 0, '+': 1, '-': 0}

    @staticmethod
    def get_possible_scores():
        return [('1', '0'), ('½', '½'), ('0', '1'), ('+', '-'), ('-', '+'), ('-', '-')]

    def get_parameter_display(self):
        return self.parameter_display

    def get_parameters(self):
        return self.parameters.items()

    def get_parameter(self, key):
        return self.parameters[key]

    def set_parameter(self, key, value):
        self.parameters[key] = value

    def get_variable(self, key):
        return self.variables[key]

    def set_variable(self, key, value):
        self.variables[key] = value

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
        self.variables["results"].append([
            ((uuid_1, score_1), (uuid_2, score_2)) for (uuid_1, score_1), (uuid_2, score_2) in results
        ])
        self.set_pairings(None)
        self.set_round(self.get_round()+1)

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
        return self.is_valid_parameters() and self.get_name() and len(self.get_participants()) > 1

    @staticmethod
    def is_valid_pairings(results):
        return all(uuid_1 != uuid_2 for (uuid_1, _), (uuid_2, _) in results if (uuid_1, uuid_2) != (None, None))

    def is_done(self):
        return False

    @staticmethod
    def get_standings_header_vertical(table):
        header_vertical = []
        last_entry = None
        for i, entry in enumerate(table):
            if last_entry is None or entry[1:] != last_entry[1:]:
                header_vertical.append(str(i+1))
            else:
                header_vertical.append('')
            last_entry = entry
        return header_vertical

    def get_standings(self):
        results = self.get_results()
        header_horizontal = ["Name", "P"]
        points = self.get_simple_scores()
        table = sorted(
            ((participant, points[participant.get_uuid()]) for participant in self.get_participants()),
            key=lambda x: x[1], reverse=True
        )
        header_vertical = self.get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
