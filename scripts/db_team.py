from typing import Sequence
from .manager_database import MANAGER_DATABASE
from .team import Team, Team_Data
from .player import Player
from .db_object import DB_Object

Player_Data_Ranked = tuple[str, str | None, int | None, str | None, str | None, int | None, str, str, int]
Player_Data_Keys = tuple[str, str | None, int | None, str | None, str | None, int | None, str, str, str, str, int]
UUID_TUPLE = ("uuid", "uuid_associate")
TEAM_ATTRIBUTE_LIST = ["Name", "Members"]
TEAM_COLUMNS = ("name", "members", "uuid", "uuid_associate")
TEAM_PLAYER_COLUMNS = ("uuid_player", "uuid_associate_player", "uuid_team", "uuid_associate_team", "member_order")


class DB_Team(DB_Object[Team]):
    def __init__(self) -> None:
        super().__init__(obj_type="Team", table_name="teams")

    def load_all(self, table_root: str, uuid_associate: str, shallow: bool = False) -> list[Team]:
        if shallow:
            entries: list[Team_Data] = MANAGER_DATABASE.get_entries(
                self.table(table_root), ("uuid_associate",), (uuid_associate,)
            )
            return [Team([], *entry) for entry in entries]
        entries_team: list[Team_Data] = MANAGER_DATABASE.get_entries(
            self.table(table_root), ("uuid_associate",), (uuid_associate,)
        )
        table_players = f"{table_root}players"
        table_junction = f"{table_root}players_to_teams"
        query = (
            f"SELECT {table_players}.*, "
            f"{table_junction}.uuid_team, {table_junction}.uuid_associate_team, {table_junction}.member_order "
            f"FROM {table_players} JOIN {table_junction} ON {table_junction}.uuid_player = {table_players}.uuid "
            f"AND {table_junction}.uuid_associate_player = {table_players}.uuid_associate "
            f"WHERE {table_junction}.uuid_associate_team = ?"
        )
        MANAGER_DATABASE.cursor.execute(query, (uuid_associate,))
        entries_players: list[Player_Data_Keys] = MANAGER_DATABASE.cursor.fetchall()
        players_and_keys = [
            (Player(*entry[:-3]), entry[-3:-1]) for entry in sorted(entries_players, key=lambda x: x[-1])
        ]
        team_dict = {entry[-2:]: Team([], *entry) for entry in entries_team}
        for player, key in players_and_keys:
            team_dict[key].add_members([player])
        return list(team_dict.values())

    def load_list(
            self, table_root: str, uuid_list: Sequence[str], uuid_associate_list: Sequence[str], shallow: bool = False
    ) -> list[Team]:
        if shallow:
            return NotImplemented
        entries_team: list[Team_Data] = MANAGER_DATABASE.get_entries_list(
            self.table(table_root), UUID_TUPLE, (uuid_list, uuid_associate_list)
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
        MANAGER_DATABASE.cursor.execute(
            query, [entry[-2] for entry in entries_team] + [entry[-1] for entry in entries_team]
        )
        entries_players: list[Player_Data_Keys] = MANAGER_DATABASE.cursor.fetchall()
        players_and_keys = [
            (Player(*entry[:-3]), entry[-3:-1]) for entry in sorted(entries_players, key=lambda x: x[-1])
        ]
        team_dict = {entry[-2:]: Team([], *entry) for entry in entries_team}
        for player, key in players_and_keys:
            team_dict[key].add_members([player])
        return list(team_dict.values())

    def load_like(
            self, table_root: str, uuid_associate: str, name: str, limit: int | None, shallow: bool = False
    ) -> list[Team]:
        if not shallow:
            return NotImplemented
        entries: list[Team_Data] = MANAGER_DATABASE.get_entries_like(
            self.table(table_root), ("uuid_associate",), (uuid_associate,),
            ("name",), (name,), ("name",), (True,), limit
        )
        return [Team([], *entry) for entry in entries]

    def add_list(self, table_root: str, teams: Sequence[Team], shallow: bool = False) -> None:
        if shallow:
            return
        MANAGER_DATABASE.add_entries(self.table(table_root), TEAM_COLUMNS, [team.get_data() for team in teams])
        junction_entries = [
            member.get_uuid_tuple() + team.get_uuid_tuple() + (i,)
            for team in teams for i, member in enumerate(team.get_members())
        ]
        MANAGER_DATABASE.add_entries(f"{table_root}players_to_teams", TEAM_PLAYER_COLUMNS, junction_entries)

    def update_list(self, table_root: str, teams: Sequence[Team], shallow: bool = False) -> None:
        MANAGER_DATABASE.update_entries(
            self.table(table_root), UUID_TUPLE, [team.get_uuid_tuple() for team in teams],
            TEAM_COLUMNS, [team.get_data() for team in teams]
        )
        if shallow:
            return
        MANAGER_DATABASE.delete_entries(
            f"{table_root}players_to_teams", ("uuid_team", "uuid_associate_team"),
            [team.get_uuid_tuple() for team in teams]
        )
        junction_entries = [
            member.get_uuid_tuple() + team.get_uuid_tuple() + (i,)
            for team in teams for i, member in enumerate(team.get_members())
        ]
        MANAGER_DATABASE.add_entries(f"{table_root}players_to_teams", TEAM_PLAYER_COLUMNS, junction_entries)

    def remove_all(self, table_root: str, uuid_associate: str) -> None:
        MANAGER_DATABASE.delete_entry(self.table(table_root), ("uuid_associate",), (uuid_associate,))

    def remove_list(self, table_root: str, teams: Sequence[Team]) -> None:
        MANAGER_DATABASE.delete_entries(self.table(table_root), UUID_TUPLE, [team.get_uuid_tuple() for team in teams])


DB_TEAM = DB_Team()
