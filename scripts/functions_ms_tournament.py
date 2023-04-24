from json import loads
from os import listdir
from .class_ms_tournament import MS_Tournament
from .functions_util import read_file
from .functions_util import get_root_directory


def get_directory(uuid):
    return f"{get_root_directory()}/data/ms_tournaments/{uuid}"


def load_ms_tournament_from_string(string):
    json = loads(string)
    tournament = MS_Tournament(json["name"], [], json["stages_advance_lists"], json["stage"], json["uuid"])
    tournament.load_from_json(json)
    return tournament


def load_ms_tournament_from_file(uuid):
    string = read_file(f"{get_directory(uuid)}/ms_tournament.json")
    return load_ms_tournament_from_string(string)


def load_ms_tournaments_all():
    return sorted((
        load_ms_tournament_from_file(ms_tournament)
        for ms_tournament in listdir(get_directory(""))
    ), key=lambda x: x.get_name())
