from .class_database_handler import DATABASE_HANDLER
from .class_player import Player


def load_player(table_root, uuid, uuid_associate):
    entry = DATABASE_HANDLER.get_entries(f"{table_root}players", ("uuid", "uuid_associate"), (uuid, uuid_associate))[0]
    return Player(*entry)


def load_players_all(table_root, uuid_associate):
    entries = DATABASE_HANDLER.get_entries(f"{table_root}players", ("uuid_associate",), (uuid_associate,))
    return [Player(*entry) for entry in entries]


def load_players_list(table_root, uuid_list, uuid_associate_list):
    entries = DATABASE_HANDLER.get_entries_list(
        f"{table_root}players", ("uuid", "uuid_associate"), (uuid_list, uuid_associate_list)
    )
    return [Player(*entry) for entry in entries]


def load_players_like(table_root, uuid_associate, name, limit):
    entries = DATABASE_HANDLER.get_entries_like(
        f"{table_root}players", ("uuid_associate",), (uuid_associate,),
        ("name",), (name,), ("rating", "name"), (False, True), limit
    )
    return [Player(*entry) for entry in entries]


def add_player(table_root, player):
    DATABASE_HANDLER.add_entry(
        f"{table_root}players",
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"), player.get_data()
    )


def add_players(table_root, players):
    players_data = (player.get_data() for player in players)
    DATABASE_HANDLER.add_entries(
        f"{table_root}players",
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        tuple(player.get_data() for player in players)
    )


def update_player(table_root, player):
    DATABASE_HANDLER.update_entry(
        f"{table_root}players", ("uuid", "uuid_associate"), (player.get_uuid(), player.get_uuid_associate()),
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        player.get_data()
    )


def update_players(table_root, players):
    DATABASE_HANDLER.update_entries(
        f"{table_root}players", ("uuid", "uuid_associate"),
        tuple((player.get_uuid(), player.get_uuid_associate()) for player in players),
        ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate"),
        tuple(player.get_data() for player in players)
    )


def remove_player(table_root, player):
    DATABASE_HANDLER.delete_entry(
        f"{table_root}players", ("uuid", "uuid_associate"), (player.get_uuid(), player.get_uuid_associate())
    )


def remove_players(table_root, players):
    DATABASE_HANDLER.delete_entries(
        f"{table_root}players", ("uuid", "uuid_associate"),
        tuple((player.get_uuid(), player.get_uuid_associate()) for player in players)
    )
