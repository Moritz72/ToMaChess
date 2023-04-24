from json import loads
from os import listdir
from .functions_util import read_file, get_root_directory
from .class_tournament_swiss import Tournament_Swiss
from .class_tournament_round_robin import Tournament_Round_Robin
from .class_tournament_knockout import Tournament_Knockout
from .class_tournament_custom import Tournament_Custom

modes = {
    "Swiss": Tournament_Swiss,
    "Round Robin": Tournament_Round_Robin,
    "Knockout": Tournament_Knockout,
    "Custom": Tournament_Custom
}
mode_default = "Swiss"


def get_directory(directory, uuid):
    return f"{get_root_directory()}/{directory}/{uuid}"


def load_tournament_from_string(string, directory="data/tournaments"):
    json = loads(string)
    tournament = modes[json["mode"]](json["name"], [], json["uuid"])
    tournament.load_from_json(directory, json)
    return tournament


def load_tournament_from_file(uuid, directory="data/tournaments"):
    string = read_file(f"{get_directory(directory, uuid)}/tournament.json")
    return load_tournament_from_string(string, directory)


def load_tournaments_all(directory="data/tournaments"):
    return sorted((
        load_tournament_from_file(tournament, directory)
        for tournament in listdir(get_directory(directory, ""))
    ), key=lambda x: x.get_name())
