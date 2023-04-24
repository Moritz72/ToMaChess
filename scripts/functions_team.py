from os import listdir
from json import loads
from .class_team import Team
from .functions_player import load_player
from .functions_util import get_root_directory, read_file


def get_directory(uuid):
    return f"{get_root_directory()}/data/teams/{uuid}"


def load_team_from_string(string):
    json = loads(string)
    team = Team(
        json["name"],
        [load_player(uuid, f"data/teams/{json['uuid']}/members") for uuid in json["members"]],
        json["uuid"]
    )
    return team


def load_team_from_file(uuid):
    string = read_file(f"{get_directory(uuid)}/team.json")
    return load_team_from_string(string)


def load_teams_all():
    return sorted([load_team_from_file(team) for team in listdir(get_directory(""))], key=lambda x: x.get_name())
