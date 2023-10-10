from json import loads
from .class_database_handler import DATABASE_HANDLER
from .class_ms_tournament import MS_Tournament
from .functions_player import load_players_all, add_players, remove_players_all
from .functions_team import load_teams_all, add_teams, remove_teams_all
from .functions_tournament import load_tournaments_shallow_all, add_tournaments_shallow, update_tournaments_shallow
from .functions_util import remove_uuid_duplicates

UUID_TUPLE = ("uuid", "uuid_associate")
MS_TOURNAMENT_ATTRIBUTE_STRING = ["Name", "Participants"]
MS_TOURNAMENT_COLUMNS = (
    "name", "participants", "stages_advance_lists", "draw_lots", "stage", "tournament_order", "uuid", "uuid_associate"
)


def get_table(table_root):
    return f"{table_root}ms_tournaments"


def json_loads_entry(entry):
    for i in (2, 5):
        entry[i] = loads(entry[i])


def add_ms_tournament_participants(table_root, ms_tournament):
    if ms_tournament.is_team_tournament():
        unique_members = remove_uuid_duplicates(
            [member for team in ms_tournament.get_participants() for member in team.get_members()]
        )
        add_players(get_table(table_root) + '_', unique_members)
        add_teams(get_table(table_root) + '_', ms_tournament.get_participants())
    else:
        add_players(get_table(table_root) + '_', ms_tournament.get_participants())


def add_ms_tournaments_participants(table_root, ms_tournaments):
    players = []
    teams = []
    for ms_tournament in ms_tournaments:
        if ms_tournament.is_team_tournament():
            players.extend([member for team in ms_tournament.get_participants() for member in team.get_members()])
            teams.extend(ms_tournament.get_participants())
        else:
            players.extend(ms_tournament.get_participants())
    add_players(get_table(table_root) + '_', players)
    add_teams(get_table(table_root) + '_', teams)


def load_ms_tournament_shallow(table_root, uuid, uuid_associate):
    entry = list(DATABASE_HANDLER.get_entries(get_table(table_root), UUID_TUPLE, (uuid, uuid_associate))[0])
    json_loads_entry(entry)
    return MS_Tournament([], *entry)


def load_ms_tournaments_shallow_all(table_root, uuid_associate):
    entries = [
        list(entry)
        for entry in DATABASE_HANDLER.get_entries(get_table(table_root), ("uuid_associate",), (uuid_associate,))
    ]
    for entry in entries:
        json_loads_entry(entry)
    return [MS_Tournament([], *entry) for entry in entries]


def load_ms_tournament(table_root, uuid, uuid_associate):
    entry = list(DATABASE_HANDLER.get_entries(get_table(table_root), UUID_TUPLE, (uuid, uuid_associate))[0])
    json_loads_entry(entry)
    tournaments = load_tournaments_shallow_all(get_table(table_root) + '_', uuid)
    if tournaments[0].is_team_tournament():
        participants = load_teams_all(get_table(table_root) + '_', uuid)
    else:
        participants = load_players_all(get_table(table_root) + '_', uuid)
    for tournament in tournaments:
        if tournament.get_participant_count():
            tournament.set_participants(participants)
    return MS_Tournament(tournaments, *entry)


def load_ms_tournaments_shallow_like(table_root, uuid_associate, name, limit):
    entries = [
        list(entry) for entry in DATABASE_HANDLER.get_entries_like(
            get_table(table_root), ("uuid_associate",), (uuid_associate,), ("name",), (name,), ("name",), (True,), limit
        )
    ]
    for entry in entries:
        json_loads_entry(entry)
    return [MS_Tournament([], *entry) for entry in entries]


def add_ms_tournament(table_root, ms_tournament):
    DATABASE_HANDLER.add_entry(get_table(table_root), MS_TOURNAMENT_COLUMNS, ms_tournament.get_data())
    add_tournaments_shallow(
        get_table(table_root) + '_',
        tuple(
            tournament
            for stage_tournaments in ms_tournament.get_stages_tournaments() for tournament in stage_tournaments
        )
    )
    add_ms_tournament_participants(table_root, ms_tournament)


def add_ms_tournaments(table_root, ms_tournaments):
    DATABASE_HANDLER.add_entries(
        get_table(table_root), MS_TOURNAMENT_COLUMNS,
        tuple(ms_tournament.get_data() for ms_tournament in ms_tournaments)
    )
    add_tournaments_shallow(
        get_table(table_root) + '_',
        [
            tournament for ms_tournament in ms_tournaments
            for stage_tournaments in ms_tournament.get_stages_tournaments() for tournament in stage_tournaments
        ]
    )
    add_ms_tournaments_participants(table_root, ms_tournaments)


def update_ms_tournament_shallow(table_root, ms_tournament):
    DATABASE_HANDLER.update_entry(
        get_table(table_root), UUID_TUPLE, ms_tournament.get_uuid_tuple(),
        MS_TOURNAMENT_COLUMNS, ms_tournament.get_data()
    )


def update_ms_tournaments_shallow(table_root, ms_tournaments):
    DATABASE_HANDLER.update_entries(
        get_table(table_root), UUID_TUPLE, tuple(ms_tournament.get_uuid_tuple() for ms_tournament in ms_tournaments),
        MS_TOURNAMENT_COLUMNS, tuple(ms_tournament.get_data() for ms_tournament in ms_tournaments)
    )


def update_ms_tournament(table_root, ms_tournament):
    ms_tournament.possess_participants_and_tournaments()
    update_ms_tournament_shallow(table_root, ms_tournament)
    update_tournaments_shallow(
        get_table(table_root) + '_',
        tuple(
            tournament
            for stage_tournaments in ms_tournament.get_stages_tournaments() for tournament in stage_tournaments
        )
    )
    if ms_tournament.is_team_tournament():
        remove_teams_all(get_table(table_root) + '_', ms_tournament.get_uuid())
    remove_players_all(get_table(table_root) + '_', ms_tournament.get_uuid())
    add_ms_tournament_participants(table_root, ms_tournament)


def remove_ms_tournament(table_root, ms_tournament):
    DATABASE_HANDLER.delete_entry(get_table(table_root), UUID_TUPLE, ms_tournament.get_uuid_tuple())


def remove_ms_tournaments(table_root, ms_tournaments):
    DATABASE_HANDLER.delete_entries(
        get_table(table_root), UUID_TUPLE, tuple(ms_tournament.get_uuid_tuple() for ms_tournament in ms_tournaments)
    )
