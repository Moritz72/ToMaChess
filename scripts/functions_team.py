from .class_database_handler import DATABASE_HANDLER
from .class_team import Team
from .class_player import Player

UUID_TUPLE = ("uuid", "uuid_associate")
TEAM_ATTRIBUTE_LIST = ["Name", "Members"]
TEAM_COLUMNS = ("name", "members", "uuid", "uuid_associate")
TEAM_PLAYER_COLUMNS = ("uuid_player", "uuid_associate_player", "uuid_team", "uuid_associate_team", "member_order")


def get_table(table_root):
    return f"{table_root}teams"


def load_team_shallow(table_root, uuid, uuid_associate):
    entry = DATABASE_HANDLER.get_entries(get_table(table_root), UUID_TUPLE, (uuid, uuid_associate))[0]
    return Team([], *entry)


def load_teams_shallow_all(table_root, uuid_associate):
    entries = DATABASE_HANDLER.get_entries(get_table(table_root), ("uuid_associate",), (uuid_associate,))
    return [Team([], *entry) for entry in entries]


def load_team(table_root, uuid, uuid_associate):
    entry_team = DATABASE_HANDLER.get_entries(get_table(table_root), UUID_TUPLE, (uuid, uuid_associate))[0]
    table_players = f"{table_root}players"
    table_junction = f"{table_root}players_to_teams"
    query = (
        f"SELECT {table_players}.*, {table_junction}.member_order FROM {table_players} JOIN {table_junction} "
        f"ON {table_junction}.uuid_player = {table_players}.uuid "
        f"AND {table_junction}.uuid_associate_player = {table_players}.uuid_associate "
        f"WHERE {table_junction}.uuid_team = ? AND {table_junction}.uuid_associate_team = ?"
    )
    DATABASE_HANDLER.cursor.execute(query, (uuid, uuid_associate))
    entry_players = DATABASE_HANDLER.cursor.fetchall()
    players = [Player(*entry[:-1]) for entry in sorted(entry_players, key=lambda x: x[-1])]
    return Team(players, *entry_team)


def load_teams_all(table_root, uuid_associate):
    entries_team = DATABASE_HANDLER.get_entries(get_table(table_root), ("uuid_associate",), (uuid_associate,))
    table_players = f"{table_root}players"
    table_junction = f"{table_root}players_to_teams"
    query = (
        f"SELECT {table_players}.*, "
        f"{table_junction}.uuid_team, {table_junction}.uuid_associate_team, {table_junction}.member_order "
        f"FROM {table_players} JOIN {table_junction} ON {table_junction}.uuid_player = {table_players}.uuid "
        f"AND {table_junction}.uuid_associate_player = {table_players}.uuid_associate "
        f"WHERE {table_junction}.uuid_associate_team = ?"
    )
    DATABASE_HANDLER.cursor.execute(query, (uuid_associate,))
    entries_players = DATABASE_HANDLER.cursor.fetchall()
    players_and_keys = [(Player(*entry[:-3]), entry[-3:-1]) for entry in sorted(entries_players, key=lambda x: x[-1])]
    team_dict = {tuple(entry[-2:]): Team([], *entry) for entry in entries_team}
    for player, key in players_and_keys:
        team_dict[key].add_members([player])
    return list(team_dict.values())


def load_teams_list(table_root, uuid_list, uuid_associate_list=None):
    if uuid_associate_list is None:
        entries_team = DATABASE_HANDLER.get_entries_list(get_table(table_root), ("uuid",), (uuid_list,))
    else:
        entries_team = DATABASE_HANDLER.get_entries_list(
            get_table(table_root), UUID_TUPLE, (uuid_list, uuid_associate_list)
        )
    table_players = f"{table_root}players"
    table_junction = f"{table_root}players_to_teams"
    query = (
        f"SELECT {table_players}.*, "
        f"{table_junction}.uuid_team, {table_junction}.uuid_associate_team, {table_junction}.member_order "
        f"FROM {table_players} JOIN {table_junction} ON {table_junction}.uuid_player = {table_players}.uuid "
        f"AND {table_junction}.uuid_associate_player = {table_players}.uuid_associate "
        f"WHERE {table_junction}.uuid_team IN ({', '.join('?' * len(entries_team))}) "
        f"AND {table_junction}.uuid_associate_team IN ({', '.join('?' * len(entries_team))})"
    )
    DATABASE_HANDLER.cursor.execute(
        query, [entry[-2] for entry in entries_team] + [entry[-1] for entry in entries_team]
    )
    entries_players = DATABASE_HANDLER.cursor.fetchall()
    players_and_keys = [(Player(*entry[:-3]), entry[-3:-1]) for entry in sorted(entries_players, key=lambda x: x[-1])]
    team_dict = {tuple(entry[-2:]): Team([], *entry) for entry in entries_team}
    for player, key in players_and_keys:
        team_dict[key].add_members([player])
    return list(team_dict.values())


def load_teams_shallow_like(table_root, uuid_associate, name, limit):
    entries = DATABASE_HANDLER.get_entries_like(
        get_table(table_root), ("uuid_associate",), (uuid_associate,), ("name",), (name,), ("name",), (True,), limit
    )
    return [Team([], *entry) for entry in entries]


def add_team(table_root, team):
    DATABASE_HANDLER.add_entry(get_table(table_root), TEAM_COLUMNS, team.get_data())
    DATABASE_HANDLER.add_entries(
        f"{table_root}players_to_teams", TEAM_PLAYER_COLUMNS,
        tuple(member.get_uuid_tuple() + team.get_uuid_tuple() + (i,) for i, member in enumerate(team.get_members()))
    )


def add_teams(table_root, teams):
    DATABASE_HANDLER.add_entries(get_table(table_root), TEAM_COLUMNS, tuple(team.get_data() for team in teams))
    DATABASE_HANDLER.add_entries(
        f"{table_root}players_to_teams", TEAM_PLAYER_COLUMNS,
        tuple(
            member.get_uuid_tuple() + team.get_uuid_tuple() + (i,)
            for team in teams for i, member in enumerate(team.get_members())
        )
    )


def update_team_shallow(table_root, team):
    DATABASE_HANDLER.update_entry(
        get_table(table_root), UUID_TUPLE, team.get_uuid_tuple(), TEAM_COLUMNS, team.get_data()
    )


def update_teams_shallow(table_root, teams):
    DATABASE_HANDLER.update_entries(
        get_table(table_root), UUID_TUPLE, tuple(team.get_uuid_tuple() for team in teams),
        TEAM_COLUMNS, tuple(team.get_data() for team in teams)
    )


def update_team(table_root, team):
    update_team_shallow(table_root, team)
    DATABASE_HANDLER.delete_entries(
        f"{table_root}players_to_teams", ("uuid_team", "uuid_associate_team"), team.get_uuid_tuple()
    )
    DATABASE_HANDLER.add_entries(
        f"{table_root}players_to_teams", TEAM_PLAYER_COLUMNS,
        tuple(member.get_uuid_tuple() + team.get_uuid_tuple() + (i,) for i, member in enumerate(team.get_members()))
    )


def update_teams(table_root, teams):
    update_teams_shallow(table_root, teams)
    DATABASE_HANDLER.delete_entries(
        f"{table_root}players_to_teams", ("uuid_team", "uuid_associate_team"),
        tuple(team.get_uuid_tuple() for team in teams)
    )
    DATABASE_HANDLER.add_entries(
        f"{table_root}players_to_teams", TEAM_PLAYER_COLUMNS,
        tuple(
            member.get_uuid_tuple() + team.get_uuid_tuple() + (i,)
            for team in teams for i, member in enumerate(team.get_members())
        )
    )


def remove_team(table_root, team):
    DATABASE_HANDLER.delete_entry(get_table(table_root), UUID_TUPLE, team.get_uuid_tuple())


def remove_teams(table_root, teams):
    DATABASE_HANDLER.delete_entries(get_table(table_root), UUID_TUPLE, tuple(team.get_uuid_tuple() for team in teams))


def remove_teams_all(table_root, uuid_associate):
    DATABASE_HANDLER.delete_entry(get_table(table_root), ("uuid_associate",), (uuid_associate,))
