from json import loads
from typing import Sequence, cast
from .db_object import DB_Object
from .db_player import DB_PLAYER
from .db_team import DB_TEAM
from .manager_database import MANAGER_DATABASE
from ..common.functions_util import remove_duplicates
from ..player.player import Player
from ..team.team import Team
from ..tournament.tournaments.tournament import Participant, Tournament, Tournament_Data, Tournament_Data_Loaded
from ..tournament.tournaments.tournament_custom import Tournament_Custom
from ..tournament.tournaments.tournament_keizer import Tournament_Keizer
from ..tournament.tournaments.tournament_knockout import Tournament_Knockout, Tournament_Knockout_Team
from ..tournament.tournaments.tournament_round_robin import Tournament_Round_Robin, Tournament_Round_Robin_Team
from ..tournament.tournaments.tournament_scheveningen import Tournament_Scheveningen
from ..tournament.tournaments.tournament_swiss import Tournament_Swiss, Tournament_Swiss_Team

UUID_TUPLE = ("uuid", "uuid_associate")
TOURNAMENT_ATTRIBUTE_LIST = ["Name", "Mode", "Participants"]
TOURNAMENT_COLUMNS = (
    "mode", "name", "participants", "parameters", "variables", "participant_order", "uuid", "uuid_associate"
)

MODES = {
    "Swiss": Tournament_Swiss,
    "Round Robin": Tournament_Round_Robin,
    "Knockout": Tournament_Knockout,
    "Keizer": Tournament_Keizer,
    "Scheveningen": Tournament_Scheveningen,
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


def get_tournament(participants: list[Participant], entry: Tournament_Data_Loaded) -> Tournament:
    return MODES_ALL[entry[0]](participants, entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7])


def get_blank_tournament(mode: str) -> Tournament:
    return MODES_ALL[mode]([], "")


def json_loads_entry(entry: Tournament_Data) -> Tournament_Data_Loaded:
    return entry[0], entry[1], entry[2], loads(entry[3]), loads(entry[4]), loads(entry[5]), entry[6], entry[7]


def add_tournaments_participants(table: str, tournaments: Sequence[Tournament]) -> None:
    players = []
    teams = []
    for tournament in tournaments:
        if tournament.is_team_tournament():
            participants = cast(list[Team], tournament.get_participants())
            players.extend([member for team in participants for member in team.get_members()])
            teams.extend(participants)
        else:
            players.extend(cast(list[Player], tournament.get_participants()))
    DB_PLAYER.add_list(table + '_', remove_duplicates(players))
    DB_TEAM.add_list(table + '_', teams)


class DB_Tournament(DB_Object[Tournament]):
    def __init__(self) -> None:
        super().__init__(obj_type="Tournament", table_name="tournaments")

    def load_all(self, table_root: str, uuid_associate: str, shallow: bool = False) -> list[Tournament]:
        if not shallow:
            return NotImplemented
        entries: list[Tournament_Data] = MANAGER_DATABASE.get_entries(
            self.table(table_root), ("uuid_associate",), (uuid_associate,)
        )
        return [get_tournament([], json_loads_entry(entry)) for entry in entries]

    def load_list(
            self, table_root: str, uuid_list: Sequence[str], uuid_associate_list: Sequence[str], shallow: bool = False
    ) -> list[Tournament]:
        if shallow:
            return NotImplemented
        tournaments = []
        for uuid, uuid_associate in zip(uuid_list, uuid_associate_list):
            entry: Tournament_Data = MANAGER_DATABASE.get_entries(
                self.table(table_root), UUID_TUPLE, (uuid, uuid_associate)
            )[0]
            if entry[0] in MODES:
                participants = cast(list[Participant], DB_PLAYER.load_all(self.table(table_root) + '_', uuid))
            else:
                participants = cast(list[Participant], DB_TEAM.load_all(self.table(table_root) + '_', uuid))
            tournaments.append(get_tournament(participants, json_loads_entry(entry)))
        return tournaments

    def load_like(
            self, table_root: str, uuid_associate: str, name: str, limit: int | None, shallow: bool = False
    ) -> list[Tournament]:
        if not shallow:
            return NotImplemented
        entries: list[Tournament_Data] = MANAGER_DATABASE.get_entries_like(
            self.table(table_root), ("uuid_associate",), (uuid_associate,),
            ("name",), (name,), ("mode", "name"), (True, True), limit
        )
        return [get_tournament([], json_loads_entry(entry)) for entry in entries]

    def add_list(self, table_root: str, tournaments: Sequence[Tournament], shallow: bool = False) -> None:
        MANAGER_DATABASE.add_entries(
            self.table(table_root), TOURNAMENT_COLUMNS, [tournament.get_data() for tournament in tournaments]
        )
        if not shallow:
            add_tournaments_participants(self.table(table_root), tournaments)

    def update_list(self, table_root: str, tournaments: Sequence[Tournament], shallow: bool = False) -> None:
        MANAGER_DATABASE.update_entries(
            self.table(table_root), UUID_TUPLE, [tournament.get_uuid_tuple() for tournament in tournaments],
            TOURNAMENT_COLUMNS, [tournament.get_data() for tournament in tournaments]
        )
        if shallow:
            return
        for tournament in tournaments:
            if tournament.is_team_tournament():
                DB_TEAM.remove_all(self.table(table_root) + '_', tournament.get_uuid())
            DB_PLAYER.remove_all(self.table(table_root) + '_', tournament.get_uuid())
        add_tournaments_participants(self.table(table_root), tournaments)

    def remove_all(self, table_root: str, uuid_associate: str) -> None:
        MANAGER_DATABASE.delete_entry(self.table(table_root), ("uuid_associate",), (uuid_associate,))

    def remove_list(self, table_root: str, tournaments: Sequence[Tournament]) -> None:
        MANAGER_DATABASE.delete_entries(
            self.table(table_root), UUID_TUPLE, [tournament.get_uuid_tuple() for tournament in tournaments]
        )


DB_TOURNAMENT = DB_Tournament()
