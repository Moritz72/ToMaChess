from typing import Sequence, cast
from .db_object import DB_Object
from .db_player import DB_PLAYER
from .db_team import DB_TEAM
from .manager_database import MANAGER_DATABASE
from ..common.functions_util import remove_duplicates
from ..player.player import Player
from ..team.team import Team
from ..tournament.registries.tournament_registry import TOURNAMENT_REGISTRY
from ..tournament.tournaments.tournament import Participant, Tournament, Tournament_Data
from ..tournament.utils.functions_tournament_get import get_tournament

UUID_TUPLE = ("uuid", "uuid_associate")
TOURNAMENT_ATTRIBUTE_LIST = ["Name", "Mode", "Participants"]
TOURNAMENT_COLUMNS = (
    "mode", "name", "participants", "parameters", "variables", "participant_order", "uuid", "uuid_associate"
)


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
        return [get_tournament([], entry) for entry in entries]

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
            if entry[0] in TOURNAMENT_REGISTRY.get_modes():
                participants = cast(list[Participant], DB_PLAYER.load_all(self.table(table_root) + '_', uuid))
            else:
                participants = cast(list[Participant], DB_TEAM.load_all(self.table(table_root) + '_', uuid))
            tournaments.append(get_tournament(participants, entry))
        return tournaments

    def load_like(
            self, table_root: str, uuid_associate: str, name: str, limit: int | None, shallow: bool = False
    ) -> list[Tournament]:
        if not shallow:
            return NotImplemented
        entries: list[Tournament_Data] = MANAGER_DATABASE.get_entries_like(
            self.table(table_root), ("uuid_associate",), (uuid_associate,),
            ("name",), (name,), ("name", "mode"), (True, True), limit
        )
        return [get_tournament([], entry) for entry in entries]

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
