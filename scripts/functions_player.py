from .class_database_handler import database_handler
from .class_player import Player


def load_player(table_root, uuid, uuid_associate):
    entry = database_handler.get_entries(f"{table_root}players", ("uuid", "uuid_associate"), (uuid, uuid_associate))[0]
    return Player(*entry)


def load_players_all(table_root, uuid_associate):
    entries = database_handler.get_entries(f"{table_root}players", ("uuid_associate",), (uuid_associate,))
    return [Player(*entry) for entry in entries]


def load_players_list(table_root, uuid_list, uuid_associate_list):
    entries = database_handler.get_entries_list(
        f"{table_root}players", ("uuid", "uuid_associate"), (uuid_list, uuid_associate_list)
    )
    return [Player(*entry) for entry in entries]


def load_players_like(table_root, uuid_associate, name, limit):
    entries = database_handler.get_entries_like(
        f"{table_root}players", ("uuid_associate",), (uuid_associate,),
        ("name",), (name,), ("rating", "name"), (False, True), limit
    )
    return [Player(*entry) for entry in entries]


def add_player(table_root, player):
    database_handler.add_entry(
        f"{table_root}players",
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"), player.get_data()
    )


def add_players(table_root, players):
    players_data = (player.get_data() for player in players)
    database_handler.add_entries(
        f"{table_root}players",
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        tuple(player.get_data() for player in players)
    )


def update_player(table_root, player):
    database_handler.update_entry(
        f"{table_root}players", ("uuid", "uuid_associate"), (player.get_uuid(), player.get_uuid_associate()),
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        player.get_data()
    )


def update_players(table_root, players):
    database_handler.update_entries(
        f"{table_root}players", ("uuid", "uuid_associate"),
        tuple((player.get_uuid(), player.get_uuid_associate()) for player in players),
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        tuple(player.get_data() for player in players)
    )


def remove_player(table_root, player):
    database_handler.delete_entry(
        f"{table_root}players", ("uuid", "uuid_associate"), (player.get_uuid(), player.get_uuid_associate())
    )


def remove_players(table_root, players):
    database_handler.delete_entries(
        f"{table_root}players", ("uuid", "uuid_associate"),
        tuple((player.get_uuid(), player.get_uuid_associate()) for player in players)
    )
