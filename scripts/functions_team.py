from .class_database_handler import database_handler
from .class_team import Team
from .class_player import Player


def load_team_shallow(table_root, uuid, uuid_associate):
    entry = database_handler.get_entries(f"{table_root}teams", ("uuid", "uuid_associate"), (uuid, uuid_associate))[0]
    return Team([], *entry)


def load_teams_shallow_all(table_root, uuid_associate):
    entries = database_handler.get_entries(f"{table_root}teams", ("uuid_associate",), (uuid_associate,))
    return [Team([], *entry) for entry in entries]


def load_team(table_root, uuid, uuid_associate):
    entry_team = database_handler.get_entries(
        f"{table_root}teams", ("uuid", "uuid_associate"), (uuid, uuid_associate)
    )[0]
    table_players = f"{table_root}players"
    table_junction = f"{table_root}players_to_teams"
    query = (
        f"SELECT {table_players}.*, {table_junction}.member_order FROM {table_players} JOIN {table_junction} "
        f"ON {table_junction}.uuid_player = {table_players}.uuid "
        f"AND {table_junction}.uuid_associate_player = {table_players}.uuid_associate "
        f"WHERE {table_junction}.uuid_team = ? AND {table_junction}.uuid_associate_team = ?"
    )
    database_handler.cursor.execute(query, (uuid, uuid_associate))
    entry_players = database_handler.cursor.fetchall()
    players = [Player(*entry[:-1]) for entry in sorted(entry_players, key=lambda x: x[-1])]
    return Team(players, *entry_team)


def load_teams_all(table_root, uuid_associate):
    entries_team = database_handler.get_entries(f"{table_root}teams", ("uuid_associate",), (uuid_associate,))
    table_players = f"{table_root}players"
    table_junction = f"{table_root}players_to_teams"
    query = (
        f"SELECT {table_players}.*, "
        f"{table_junction}.uuid_team, {table_junction}.uuid_associate_team, {table_junction}.member_order "
        f"FROM {table_players} JOIN {table_junction} ON {table_junction}.uuid_player = {table_players}.uuid "
        f"AND {table_junction}.uuid_associate_player = {table_players}.uuid_associate "
        f"WHERE {table_junction}.uuid_associate_team = ?"
    )
    database_handler.cursor.execute(query, (uuid_associate,))
    entries_players = database_handler.cursor.fetchall()
    players_and_keys = [(Player(*entry[:-3]), entry[-3:-1]) for entry in sorted(entries_players, key=lambda x: x[-1])]
    team_dict = {tuple(entry[-2:]): Team([], *entry) for entry in entries_team}
    for player, key in players_and_keys:
        team_dict[key].add_members([player])
    return list(team_dict.values())


def load_teams_list(table_root, uuid_list, uuid_associate_list):
    entries_team = database_handler.get_entries_list(
        f"{table_root}teams", ("uuid", "uuid_associate"), (uuid_list, uuid_associate_list)
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
    database_handler.cursor.execute(
        query, [entry[-2] for entry in entries_team] + [entry[-1] for entry in entries_team]
    )
    entries_players = database_handler.cursor.fetchall()
    players_and_keys = [(Player(*entry[:-3]), entry[-3:-1]) for entry in sorted(entries_players, key=lambda x: x[-1])]
    team_dict = {tuple(entry[-2:]): Team([], *entry) for entry in entries_team}
    for player, key in players_and_keys:
        team_dict[key].add_members([player])
    return list(team_dict.values())


def load_teams_like_shallow(table_root, uuid_associate, name, limit):
    entries = database_handler.get_entries_like(
        f"{table_root}teams", ("uuid_associate",), (uuid_associate,), ("name",), (name,), ("name",), (True,), limit
    )
    return [Team([], *entry) for entry in entries]


def add_team(table_root, team):
    database_handler.add_entry(f"{table_root}teams", ("name", "members", "uuid", "uuid_associate"), team.get_data())
    database_handler.add_entries(
        f"{table_root}players_to_teams",
        ("uuid_player", "uuid_associate_player", "uuid_team", "uuid_associate_team", "member_order"),
        tuple(
            (member.get_uuid(), member.get_uuid_associate(), team.get_uuid(), team.get_uuid_associate(), i)
            for i, member in enumerate(team.get_members())
        )
    )


def add_teams(table_root, teams):
    database_handler.add_entries(
        f"{table_root}teams", ("name", "members", "uuid", "uuid_associate"), tuple(team.get_data() for team in teams)
    )
    database_handler.add_entries(
        f"{table_root}players_to_teams",
        ("uuid_player", "uuid_associate_player", "uuid_team", "uuid_associate_team", "member_order"),
        tuple(
            (member.get_uuid(), member.get_uuid_associate(), team.get_uuid(), team.get_uuid_associate(), i)
            for team in teams for i, member in enumerate(team.get_members())
        )
    )


def update_team_shallow(table_root, team):
    database_handler.update_entry(
        f"{table_root}teams", ("uuid", "uuid_associate"), (team.get_uuid(), team.get_uuid_associate()),
        ("name", "members", "uuid", "uuid_associate"), team.get_data()
    )


def update_teams_shallow(table_root, teams):
    database_handler.update_entries(
        f"{table_root}teams", ("uuid", "uuid_associate"),
        tuple((team.get_uuid(), team.get_uuid_associate()) for team in teams),
        ("name", "members", "uuid", "uuid_associate"), tuple(team.get_data() for team in teams)
    )


def update_team(database_handler, table_root, team):
    update_team_shallow(table_root, team)
    database_handler.delete_entries(
        f"{table_root}players_to_teams",
        ("uuid_team", "uuid_associate_team"), (team.get_uuid(), team.get_uuid_associate())
    )
    database_handler.add_entries(
        f"{table_root}players_to_teams",
        ("uuid_player", "uuid_associate_player", "uuid_team", "uuid_associate_team", "member_order"),
        tuple(
            (member.get_uuid(), member.get_uuid_associate(), team.get_uuid(), team.get_uuid_associate(), i)
            for i, member in enumerate(team.get_members())
        )
    )


def update_teams(table_root, teams):
    update_teams_shallow(table_root, teams)
    database_handler.delete_entries(
        f"{table_root}players_to_teams", ("uuid_team", "uuid_associate_team"),
        tuple((team.get_uuid(), team.get_uuid_associate()) for team in teams)
    )
    database_handler.add_entries(
        f"{table_root}players_to_teams",
        ("uuid_player", "uuid_associate_player", "uuid_team", "uuid_associate_team", "member_order"),
        tuple(
            (member.get_uuid(), member.get_uuid_associate(), team.get_uuid(), team.get_uuid_associate(), i)
            for team in teams for i, member in enumerate(team.get_members())
        )
    )


def remove_team(table_root, team):
    database_handler.delete_entry(
        f"{table_root}teams", ("uuid", "uuid_associate"), (team.get_uuid(), team.get_uuid_associate())
    )


def remove_teams(table_root, teams):
    database_handler.delete_entries(
        f"{table_root}teams", ("uuid", "uuid_associate"),
        tuple((team.get_uuid(), team.get_uuid_associate()) for team in teams)
    )
