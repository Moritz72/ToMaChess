from json import loads
from typing import Sequence, cast
from .db_object import DB_Object
from .db_player import DB_PLAYER
from .db_team import DB_TEAM
from .db_tournament import DB_TOURNAMENT
from .manager_database import MANAGER_DATABASE
from ..ms_tournament.type_declerations import MS_Tournament_Data, MS_Tournament_Data_Loaded
from ..player.player import Player
from ..team.team import Team
from ..tournament.common.type_declarations import Participant
from ..ms_tournament.ms_tournament import MS_Tournament
from ..common.functions_util import remove_duplicates

UUID_TUPLE = ("uuid", "uuid_associate")
MS_TOURNAMENT_ATTRIBUTE_STRING = ["Name", "Participants"]
MS_TOURNAMENT_COLUMNS = (
    "name", "participants", "stages_advance_lists", "draw_lots", "stage", "tournament_order", "uuid", "uuid_associate"
)


def json_loads_entry(entry: MS_Tournament_Data) -> MS_Tournament_Data_Loaded:
    return entry[0], entry[1], loads(entry[2]), entry[3], entry[4], loads(entry[5]), entry[6], entry[7]


def add_ms_tournaments_participants(table: str, ms_tournaments: Sequence[MS_Tournament]) -> None:
    players = []
    teams = []
    for ms_tournament in ms_tournaments:
        if ms_tournament.is_team_tournament():
            participants = cast(list[Team], ms_tournament.get_participants())
            players.extend([member for team in participants for member in team.get_members()])
            teams.extend(participants)
        else:
            players.extend(cast(list[Player], ms_tournament.get_participants()))
    DB_PLAYER.add_list(table + '_', remove_duplicates(players))
    DB_TEAM.add_list(table + '_', remove_duplicates(teams))


class DB_MS_Tournament(DB_Object[MS_Tournament]):
    def __init__(self) -> None:
        super().__init__(obj_type="Multi-Stage Tournament", table_name="ms_tournaments")

    def load_all(self, table_root: str, uuid_associate: str, shallow: bool = False) -> list[MS_Tournament]:
        if not shallow:
            return NotImplemented
        entries: list[MS_Tournament_Data] = MANAGER_DATABASE.get_entries(
            self.table(table_root), ("uuid_associate",), (uuid_associate,)
        )
        return [MS_Tournament([], *json_loads_entry(entry)) for entry in entries]

    def load_list(
            self, table_root: str, uuid_list: Sequence[str], uuid_associate_list: Sequence[str], shallow: bool = False
    ) -> list[MS_Tournament]:
        if shallow:
            return NotImplemented
        ms_tournaments = []
        for uuid, uuid_associate in zip(uuid_list, uuid_associate_list):
            entry: MS_Tournament_Data = MANAGER_DATABASE.get_entries(
                self.table(table_root), UUID_TUPLE, (uuid, uuid_associate)
            )[0]
            tournaments = DB_TOURNAMENT.load_all(self.table(table_root) + '_', uuid, shallow=True)
            if tournaments[0].is_team_tournament():
                participants = cast(list[Participant], DB_TEAM.load_all(self.table(table_root) + '_', uuid))
            else:
                participants = cast(list[Participant], DB_PLAYER.load_all(self.table(table_root) + '_', uuid))
            for tournament in tournaments:
                if tournament.get_order() is not None:
                    tournament.set_participants(participants, from_order=True)
            ms_tournaments.append(MS_Tournament(tournaments, *json_loads_entry(entry)))
        return ms_tournaments

    def load_like(
            self, table_root: str, uuid_associate: str, name: str, limit: int | None, shallow: bool = False
    ) -> list[MS_Tournament]:
        if not shallow:
            return NotImplemented
        entries: list[MS_Tournament_Data] = MANAGER_DATABASE.get_entries_like(
            self.table(table_root), ("uuid_associate",), (uuid_associate,),
            ("name",), (name,), ("name",), (True,), limit
        )
        return [MS_Tournament([], *json_loads_entry(entry)) for entry in entries]

    def add_list(self, table_root: str, ms_tournaments: Sequence[MS_Tournament], shallow: bool = False) -> None:
        if shallow:
            return
        MANAGER_DATABASE.add_entries(
            self.table(table_root), MS_TOURNAMENT_COLUMNS,
            [ms_tournament.get_data() for ms_tournament in ms_tournaments]
        )
        tournaments = [tournament for ms_tournament in ms_tournaments for tournament in ms_tournament.get_tournaments()]
        DB_TOURNAMENT.add_list(self.table(table_root) + '_', tournaments, shallow=True)
        add_ms_tournaments_participants(self.table(table_root), ms_tournaments)

    def update_list(self, table_root: str, ms_tournaments: Sequence[MS_Tournament], shallow: bool = False) -> None:
        MANAGER_DATABASE.update_entries(
            self.table(table_root), UUID_TUPLE, [ms_tournament.get_uuid_tuple() for ms_tournament in ms_tournaments],
            MS_TOURNAMENT_COLUMNS, [ms_tournament.get_data() for ms_tournament in ms_tournaments]
        )
        if shallow:
            return
        for ms_tournament in ms_tournaments:
            ms_tournament.possess_participants_and_tournaments()
            DB_TOURNAMENT.update_list(self.table(table_root) + '_', ms_tournament.get_tournaments(), shallow=True)
            if ms_tournament.is_team_tournament():
                DB_TEAM.remove_all(self.table(table_root) + '_', ms_tournament.get_uuid())
            DB_PLAYER.remove_all(self.table(table_root) + '_', ms_tournament.get_uuid())
        add_ms_tournaments_participants(self.table(table_root), ms_tournaments)

    def remove_all(self, table_root: str, uuid_associate: str) -> None:
        MANAGER_DATABASE.delete_entry(self.table(table_root), ("uuid_associate",), (uuid_associate,))

    def remove_list(self, table_root: str, ms_tournaments: Sequence[MS_Tournament]) -> None:
        MANAGER_DATABASE.delete_entries(
            self.table(table_root), UUID_TUPLE, [ms_tournament.get_uuid_tuple() for ms_tournament in ms_tournaments]
        )


DB_MS_TOURNAMENT = DB_MS_Tournament()
