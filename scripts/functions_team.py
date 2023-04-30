from os import listdir
from json import loads
from .class_team import Team
from .functions_player import load_player
from .functions_util import get_directory_by_uuid, read_file


def load_team_from_string(string, directory="data/teams"):
    json = loads(string)
    team = Team(
        json["name"],
        [load_player(uuid, f"{directory}/{json['uuid']}/members") for uuid in json["members"]],
        json["uuid"]
    )
    return team


def load_team_from_file(uuid, directory="data/teams"):
    string = read_file(f"{get_directory_by_uuid(directory, uuid)}/team.json")
    return load_team_from_string(string)


def load_teams_all(directory="data/teams"):
    return sorted(
        (load_team_from_file(team) for team in listdir(get_directory_by_uuid(directory, ""))),
        key=lambda x: x.get_name()
    )
