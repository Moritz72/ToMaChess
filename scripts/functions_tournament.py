from json import loads
from os import listdir
from .functions_util import read_file, get_directory_by_uuid
from .class_tournament_swiss import Tournament_Swiss
from .class_tournament_round_robin import Tournament_Round_Robin
from .class_tournament_knockout import Tournament_Knockout
from .class_tournament_custom import Tournament_Custom
from .class_tournament_swiss_team import Tournament_Swiss_Team
from .class_tournament_round_robin_team import Tournament_Round_Robin_Team
from .class_tournament_knockout_team import Tournament_Knockout_Team

modes = {
    "Swiss": Tournament_Swiss,
    "Round Robin": Tournament_Round_Robin,
    "Knockout": Tournament_Knockout,
    "Custom": Tournament_Custom
}
modes_team = {
    "Swiss (Team)": Tournament_Swiss_Team,
    "Round Robin (Team)": Tournament_Round_Robin_Team,
    "Knockout (Team)": Tournament_Knockout_Team
}
mode_default = "Swiss"
mode_default_team = "Swiss (Team)"


def load_tournament_from_string(string, directory="data/tournaments"):
    json = loads(string)
    if json["mode"] in modes:
        tournament = modes[json["mode"]](json["name"], [], json["uuid"])
    else:
        tournament = modes_team[json["mode"]](json["name"], [], json["uuid"])
    tournament.load_from_json(directory, json)
    return tournament


def load_tournament_from_file(uuid, directory="data/tournaments"):
    string = read_file(f"{get_directory_by_uuid(directory, uuid)}/tournament.json")
    return load_tournament_from_string(string, directory)


def load_tournaments_all(directory="data/tournaments"):
    return sorted((
        load_tournament_from_file(tournament, directory)
        for tournament in listdir(get_directory_by_uuid(directory, ""))
    ), key=lambda x: x.get_name())
