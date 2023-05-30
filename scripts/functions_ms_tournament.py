from json import loads
from .class_database_handler import database_handler
from .class_ms_tournament import MS_Tournament
from .functions_player import load_players_all, add_players
from .functions_team import load_teams_all, add_teams
from .functions_tournament import load_tournaments_shallow_all, add_tournaments_shallow, update_tournaments


def json_loads_entry(entry):
    for i in (2, 5):
        entry[i] = loads(entry[i])


def load_ms_tournament_shallow(table_root, uuid, uuid_associate):
    entry = list(database_handler.get_entries(
        f"{table_root}ms_tournaments", ("uuid", "uuid_associate"), (uuid, uuid_associate)
    )[0])
    json_loads_entry(entry)
    return MS_Tournament([], [], *entry)


def load_ms_tournaments_shallow_all(table_root, uuid_associate):
    entries = [
        list(entry) for entry
        in database_handler.get_entries(f"{table_root}ms_tournaments", ("uuid_associate",), (uuid_associate,))
    ]
    for entry in entries:
        json_loads_entry(entry)
    return [MS_Tournament([], [], *entry) for entry in entries]


def load_ms_tournament(table_root, uuid, uuid_associate):
    entry = list(database_handler.get_entries(
        f"{table_root}ms_tournaments", ("uuid", "uuid_associate"), (uuid, uuid_associate)
    )[0])
    json_loads_entry(entry)
    tournaments = load_tournaments_shallow_all(f"{table_root}ms_tournaments_", uuid)
    if tournaments[0].is_team_tournament():
        participants = load_teams_all(f"{table_root}ms_tournaments_", uuid)
    else:
        participants = load_players_all(f"{table_root}ms_tournaments_", uuid)
    for tournament in tournaments:
        tournament.set_participants(participants)
    return MS_Tournament(participants, tournaments, *entry)


def load_ms_tournaments_shallow_like(table_root, uuid_associate, name, limit):
    entries = [
        list(entry) for entry in database_handler.get_entries_like(
            f"{table_root}ms_tournaments", ("uuid_associate",), (uuid_associate,),
            ("name",), (name,), ("name",), (True,), limit
        )
    ]
    for entry in entries:
        json_loads_entry(entry)
    return [MS_Tournament([], [], *entry) for entry in entries]


def add_ms_tournament(table_root, ms_tournament):
    database_handler.add_entry(
        f"{table_root}ms_tournaments",
        (
            "name", "participants", "stages_advance_lists", "draw_lots", "stage", "tournament_order", "uuid",
            "uuid_associate"
        ),
        ms_tournament.get_data()
    )
    add_tournaments_shallow(
        f"{table_root}ms_tournaments_",
        tuple(
            tournament
            for stage_tournaments in ms_tournament.get_stages_tournaments() for tournament in stage_tournaments
        )
    )
    if ms_tournament.is_team_tournament():
        unique_members = list({
            member.get_uuid(): member for member in
            [member for team in ms_tournament.get_participants() for member in team.get_members()]
        }.values())
        add_players(f"{table_root}ms_tournaments_", unique_members)
        add_teams(f"{table_root}ms_tournaments_", ms_tournament.get_participants())
    else:
        add_players(f"{table_root}ms_tournaments_", ms_tournament.get_participants())


def add_ms_tournaments(table_root, ms_tournaments):
    database_handler.add_entries(
        f"{table_root}ms_tournaments",
        (
            "name", "participants", "stages_advance_lists", "draw_lots", "stage", "tournament_order", "uuid",
            "uuid_associate"
        ),
        tuple(ms_tournament.get_data() for ms_tournament in ms_tournaments)
    )
    add_tournaments_shallow(
        f"{table_root}ms_tournaments_",
        [
            tournament for ms_tournament in ms_tournaments
            for stage_tournaments in ms_tournament.get_stages_tournaments() for tournament in stage_tournaments
        ]
    )
    players = []
    teams = []
    for ms_tournament in ms_tournaments:
        if ms_tournament.is_team_tournament():
            players.extend([member for team in ms_tournament.get_participants() for member in team.get_members()])
            teams.extend(ms_tournament.get_participants())
        else:
            players.extend(ms_tournament.get_participants())
    add_players(f"{table_root}ms_tournaments_", players)
    add_teams(f"{table_root}ms_tournaments_", teams)


def update_ms_tournament_shallow(table_root, ms_tournament):
    database_handler.update_entry(
        f"{table_root}ms_tournaments",
        ("uuid", "uuid_associate"), (ms_tournament.get_uuid(), ms_tournament.get_uuid_associate()),
        (
            "name", "participants", "stages_advance_lists", "draw_lots", "stage", "tournament_order", "uuid",
            "uuid_associate"
        ),
        ms_tournament.get_data()
    )


def update_ms_tournaments_shallow(table_root, ms_tournaments):
    database_handler.update_entries(
        f"{table_root}ms_tournaments", ("uuid", "uuid_associate"),
        tuple((ms_tournament.get_uuid(), ms_tournament.get_uuid_associate()) for ms_tournament in ms_tournaments),
        (
            "name", "participants", "stages_advance_lists", "draw_lots", "stage", "tournament_order", "uuid",
            "uuid_associate"
        ),
        tuple(ms_tournament.get_data() for ms_tournament in ms_tournaments)
    )


def update_ms_tournament(table_root, ms_tournament):
    update_ms_tournament_shallow(table_root, ms_tournament)
    update_tournaments(
        f"{table_root}ms_tournaments_",
        tuple(
            tournament
            for stage_tournaments in ms_tournament.get_stages_tournaments() for tournament in stage_tournaments
        )
    )


def remove_ms_tournament(table_root, ms_tournament):
    database_handler.delete_entry(
        f"{table_root}ms_tournaments",
        ("uuid", "uuid_associate"), (ms_tournament.get_uuid(), ms_tournament.get_uuid_associate())
    )


def remove_ms_tournaments(table_root, ms_tournaments):
    database_handler.delete_entries(
        f"{table_root}ms_tournaments", ("uuid", "uuid_associate"),
        tuple((ms_tournament.get_uuid(), ms_tournament.get_uuid_associate()) for ms_tournament in ms_tournaments)
    )
