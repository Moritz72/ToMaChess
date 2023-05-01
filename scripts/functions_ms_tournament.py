from json import loads
from os import listdir
from .class_ms_tournament import MS_Tournament
from .functions_util import read_file
from .functions_util import get_directory_by_uuid


def load_ms_tournament_from_string(string):
    json = loads(string)
    tournament = MS_Tournament(
        json["name"], [], json["stages_advance_lists"], json["draw_lots"], json["stage"], json["uuid"]
    )
    tournament.load_from_json(json)
    return tournament


def load_ms_tournament_from_file(uuid, directory="data/ms_tournaments"):
    string = read_file(f"{get_directory_by_uuid(directory, uuid)}/ms_tournament.json")
    return load_ms_tournament_from_string(string)


def load_ms_tournaments_all(directory="data/ms_tournaments"):
    return sorted((
        load_ms_tournament_from_file(ms_tournament)
        for ms_tournament in listdir(get_directory_by_uuid(directory, ""))
    ), key=lambda x: x.get_name())
