from json import loads
from os import listdir
from .functions_util import read_file, get_root_directory
from .class_player import Player


def get_directory(directory, uuid):
    return f"{get_root_directory()}/{directory}/{uuid}"


def load_player(uuid, directory="data/players"):
    return Player(**loads(read_file(f"{get_directory(directory, uuid)}.json")))


def load_players_all(directory="data/players"):
    return sorted((
        load_player(player[:-5], directory) for player in listdir(get_directory(directory, ""))
    ), key=lambda x: (x.get_last_name(), x.get_first_name()))
