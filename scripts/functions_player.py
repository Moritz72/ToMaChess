from json import loads
from os import listdir
from .functions_util import read_file, get_directory_by_uuid
from .class_player import Player


def load_player(uuid, directory="data/players"):
    return Player(**loads(read_file(f"{get_directory_by_uuid(directory, uuid)}.json")))


def load_players_all(directory="data/players"):
    return sorted((
        load_player(player[:-5], directory) for player in listdir(get_directory_by_uuid(directory, ""))
    ), key=lambda x: (x.get_last_name(), x.get_first_name()))
