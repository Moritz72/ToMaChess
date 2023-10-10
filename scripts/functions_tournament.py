from json import loads
from .class_database_handler import DATABASE_HANDLER
from .class_tournament_swiss import Tournament_Swiss
from .class_tournament_round_robin import Tournament_Round_Robin
from .class_tournament_knockout import Tournament_Knockout
from .class_tournament_custom import Tournament_Custom
from .class_tournament_swiss_team import Tournament_Swiss_Team
from .class_tournament_round_robin_team import Tournament_Round_Robin_Team
from .class_tournament_knockout_team import Tournament_Knockout_Team
from .functions_player import load_players_all, add_players, remove_players_all
from .functions_team import load_teams_all, add_teams, remove_teams_all

UUID_TUPLE = ("uuid", "uuid_associate")
TOURNAMENT_ATTRIBUTE_LIST = ["Name", "Mode", "Participants"]
TOURNAMENT_COLUMNS = (
    "mode", "name", "participants", "parameters", "variables", "participant_order", "uuid", "uuid_associate"
)

MODES = {
    "Swiss": Tournament_Swiss,
    "Round Robin": Tournament_Round_Robin,
    "Knockout": Tournament_Knockout,
    "Custom": Tournament_Custom
}
MODES_TEAM = {
    "Swiss (Team)": Tournament_Swiss_Team,
    "Round Robin (Team)": Tournament_Round_Robin_Team,
    "Knockout (Team)": Tournament_Knockout_Team
}
MODES_ALL = MODES | MODES_TEAM
MODE_DEFAULT = "Swiss"
MODE_DEFAULT_TEAM = "Swiss (Team)"


def get_table(table_root):
    return f"{table_root}tournaments"


def get_tournament(participants, entry):
    mode = entry.pop(0)
    return MODES_ALL[mode](participants, *entry)


def json_loads_entry(entry):
    for i in (3, 4, 5):
        entry[i] = loads(entry[i])


def add_tournament_participants(table_root, tournament):
    if tournament.is_team_tournament():
        unique_members = list({
            member.get_uuid(): member for member in
            [member for team in tournament.get_participants() for member in team.get_members()]
        }.values())
        add_players(get_table(table_root) + '_', unique_members)
        add_teams(get_table(table_root) + '_', tournament.get_participants())
    else:
        add_players(get_table(table_root) + '_', tournament.get_participants())


def add_tournaments_participants(table_root, tournaments):
    players = set()
    teams = []
    for tournament in tournaments:
        if tournament.is_team_tournament():
            players.add({
                member.get_uuid(): member for member in
                [member for team in tournament.get_participants() for member in team.get_members()]
            }.values())
            teams.extend(tournament.get_participants())
        else:
            players.add(tournament.get_participants())
    add_players(get_table(table_root) + '_', list(players))
    add_teams(get_table(table_root) + '_', teams)


def load_tournament_shallow(table_root, uuid, uuid_associate):
    entry = list(DATABASE_HANDLER.get_entries(get_table(table_root), UUID_TUPLE, (uuid, uuid_associate))[0])
    json_loads_entry(entry)
    return get_tournament([], entry)


def load_tournaments_shallow_all(table_root, uuid_associate):
    entries = [
        list(entry) for entry in DATABASE_HANDLER.get_entries(
            get_table(table_root), ("uuid_associate",), (uuid_associate,)
        )
    ]
    for entry in entries:
        json_loads_entry(entry)
    return [get_tournament([], entry) for entry in entries]


def load_tournament(table_root, uuid, uuid_associate):
    entry = list(DATABASE_HANDLER.get_entries(get_table(table_root), UUID_TUPLE, (uuid, uuid_associate))[0])
    json_loads_entry(entry)
    if entry[0] in MODES:
        participants = load_players_all(get_table(table_root) + '_', uuid)
    else:
        participants = load_teams_all(get_table(table_root) + '_', uuid)
    return get_tournament(participants, entry)


def load_tournaments_shallow_like(table_root, uuid_associate, name, limit):
    entries = [
        list(entry) for entry in DATABASE_HANDLER.get_entries_like(
            get_table(table_root), ("uuid_associate",), (uuid_associate,),
            ("name",), (name,), ("mode", "name"), (True, True), limit
        )
    ]
    for entry in entries:
        json_loads_entry(entry)
    return [get_tournament([], entry) for entry in entries]


def add_tournament_shallow(table_root, tournament):
    DATABASE_HANDLER.add_entry(get_table(table_root), TOURNAMENT_COLUMNS, tournament.get_data())


def add_tournament(table_root, tournament):
    add_tournament_shallow(table_root, tournament)
    add_tournament_participants(table_root, tournament)


def add_tournaments_shallow(table_root, tournaments):
    DATABASE_HANDLER.add_entries(
        get_table(table_root), TOURNAMENT_COLUMNS, tuple(tournament.get_data() for tournament in tournaments)
    )


def add_tournaments(table_root, tournaments):
    add_tournament_shallow(table_root, tournaments)
    add_tournaments_participants(table_root, tournaments)


def update_tournament(table_root, tournament):
    DATABASE_HANDLER.update_entry(
        get_table(table_root), UUID_TUPLE, tournament.get_uuid_tuple(), TOURNAMENT_COLUMNS, tournament.get_data()
    )
    if tournament.is_team_tournament():
        remove_teams_all(get_table(table_root) + '_', tournament.get_uuid())
    remove_players_all(get_table(table_root) + '_', tournament.get_uuid())
    add_tournament_participants(table_root, tournament)


def update_tournaments(table_root, tournaments):
    DATABASE_HANDLER.update_entries(
        get_table(table_root), UUID_TUPLE, tuple(tournament.get_uuid_tuple() for tournament in tournaments),
        TOURNAMENT_COLUMNS, tuple(tournament.get_data() for tournament in tournaments)
    )
    for tournament in tournaments:
        if tournament.is_team_tournament():
            remove_teams_all(get_table(table_root) + '_', tournament.get_uuid())
        remove_players_all(get_table(table_root) + '_', tournament.get_uuid())
    add_tournaments_participants(table_root, tournaments)


def update_tournament_shallow(table_root, tournament):
    DATABASE_HANDLER.update_entry(
        get_table(table_root), UUID_TUPLE, tournament.get_uuid_tuple(), TOURNAMENT_COLUMNS, tournament.get_data()
    )


def update_tournaments_shallow(table_root, tournaments):
    DATABASE_HANDLER.update_entries(
        get_table(table_root), UUID_TUPLE, tuple(tournament.get_uuid_tuple() for tournament in tournaments),
        TOURNAMENT_COLUMNS, tuple(tournament.get_data() for tournament in tournaments)
    )


def remove_tournament(table_root, tournament):
    DATABASE_HANDLER.delete_entry(get_table(table_root), UUID_TUPLE, tournament.get_uuid_tuple())


def remove_tournaments(table_root, tournaments):
    DATABASE_HANDLER.delete_entries(
        get_table(table_root), UUID_TUPLE, tuple(tournament.get_uuid_tuple() for tournament in tournaments)
    )
