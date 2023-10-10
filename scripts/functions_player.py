from .class_database_handler import DATABASE_HANDLER
from .class_player import Player, TITLES

UUID_TUPLE = ("uuid", "uuid_associate")
PLAYER_ATTRIBUTE_LIST = ["Name", "Sex", "Birth", "Federation", "Title", "Rating"]
PLAYER_COLUMNS = ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate")


def get_table(table_root):
    return f"{table_root}players"


def sort_players_by_rating(players):
    if not players or not isinstance(players[0], Player):
        return players
    return sorted(players, key=lambda x: (
        0 if x.get_rating() is None else -x.get_rating(),
        len(TITLES) if x.get_title() is None else TITLES.index(x.get_title()),
        x.get_name()
    ))


def load_player(table_root, uuid, uuid_associate=None):
    if uuid_associate is None:
        entry = DATABASE_HANDLER.get_entries(get_table(table_root), ("uuid",), (uuid,))[0]
    else:
        entry = DATABASE_HANDLER.get_entries(get_table(table_root), UUID_TUPLE, (uuid, uuid_associate))[0]
    return Player(*entry)


def load_players_all(table_root, uuid_associate):
    entries = DATABASE_HANDLER.get_entries(get_table(table_root), ("uuid_associate",), (uuid_associate,))
    return [Player(*entry) for entry in entries]


def load_players_list(table_root, uuid_list, uuid_associate_list=None):
    if uuid_associate_list is None:
        entries = DATABASE_HANDLER.get_entries_list(get_table(table_root), ("uuid",), (uuid_list,))
    else:
        entries = DATABASE_HANDLER.get_entries_list(get_table(table_root), UUID_TUPLE, (uuid_list, uuid_associate_list))
    return [Player(*entry) for entry in entries]


def load_players_like(table_root, uuid_associate, name, limit):
    entries = DATABASE_HANDLER.get_entries_like(
        get_table(table_root), ("uuid_associate",), (uuid_associate,),
        ("name",), (name,), ("rating", "name"), (False, True), limit
    )
    return [Player(*entry) for entry in entries]


def add_player(table_root, player):
    DATABASE_HANDLER.add_entry(get_table(table_root), PLAYER_COLUMNS, player.get_data())


def add_players(table_root, players):
    players_data = (player.get_data() for player in players)
    DATABASE_HANDLER.add_entries(get_table(table_root), PLAYER_COLUMNS, tuple(player.get_data() for player in players))


def update_player(table_root, player):
    DATABASE_HANDLER.update_entry(
        get_table(table_root), UUID_TUPLE, player.get_uuid_tuple(), PLAYER_COLUMNS, player.get_data()
    )


def update_players(table_root, players):
    DATABASE_HANDLER.update_entries(
        get_table(table_root), UUID_TUPLE, tuple(player.get_uuid_tuple() for player in players),
        PLAYER_COLUMNS, tuple(player.get_data() for player in players)
    )


def remove_player(table_root, player):
    DATABASE_HANDLER.delete_entry(get_table(table_root), UUID_TUPLE, player.get_uuid_tuple())


def remove_players(table_root, players):
    DATABASE_HANDLER.delete_entries(
        get_table(table_root), UUID_TUPLE, tuple(player.get_uuid_tuple() for player in players)
    )


def remove_players_all(table_root, uuid_associate):
    DATABASE_HANDLER.delete_entry(get_table(table_root), ("uuid_associate",), (uuid_associate,))
