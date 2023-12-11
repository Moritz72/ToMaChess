from typing import Sequence, cast
from .manager_database import MANAGER_DATABASE
from .player import Player, Player_Data, TITLES
from .db_object import DB_Object

UUID_TUPLE = ("uuid", "uuid_associate")
PLAYER_ATTRIBUTE_LIST = ["Name", "Sex", "Birth", "Federation", "Title", "Rating"]
PLAYER_COLUMNS = ("name", "sex", "birthday", "country", "title", "rating", "uuid", "uuid_associate")


def sort_players_by_rating(players: Sequence[Player]) -> list[Player]:
    if not players or not isinstance(players[0], Player):
        return list(players)
    return sorted(players, key=lambda x: (
        0 if x.get_rating() is None else -cast(int, x.get_rating()),
        len(TITLES) if x.get_title() is None else TITLES.index(x.get_title()),
        x.get_name()
    ))


class DB_Player(DB_Object[Player]):
    def __init__(self) -> None:
        super().__init__(obj_type="Player", table_name="players")

    def load_all(self, table_root: str, uuid_associate: str, shallow: bool = False) -> list[Player]:
        entries: list[Player_Data] = MANAGER_DATABASE.get_entries(
            self.table(table_root), ("uuid_associate",), (uuid_associate,)
        )
        return [Player(*entry) for entry in entries]

    def load_list(
            self, table_root: str, uuid_list: Sequence[str], uuid_associate_list: Sequence[str], shallow: bool = False
    ) -> list[Player]:
        entries: list[Player_Data] = MANAGER_DATABASE.get_entries_list(
            self.table(table_root), UUID_TUPLE, (uuid_list, uuid_associate_list)
        )
        return [Player(*entry) for entry in entries]

    def load_like(
            self, table_root: str, uuid_associate: str, name: str, limit: int | None, shallow: bool = False
    ) -> list[Player]:
        entries: list[Player_Data] = MANAGER_DATABASE.get_entries_like(
            self.table(table_root), ("uuid_associate",), (uuid_associate,),
            ("name",), (name,), ("rating", "name"), (False, True), limit
        )
        return [Player(*entry) for entry in entries]

    def add_list(self, table_root: str, players: Sequence[Player], shallow: bool = False) -> None:
        MANAGER_DATABASE.add_entries(self.table(table_root), PLAYER_COLUMNS, [player.get_data() for player in players])

    def update_list(self, table_root: str, players: Sequence[Player], shallow: bool = False) -> None:
        MANAGER_DATABASE.update_entries(
            self.table(table_root), UUID_TUPLE, [player.get_uuid_tuple() for player in players],
            PLAYER_COLUMNS, [player.get_data() for player in players]
        )

    def remove_all(self, table_root: str, uuid_associate: str) -> None:
        MANAGER_DATABASE.delete_entry(self.table(table_root), ("uuid_associate",), (uuid_associate,))

    def remove_list(self, table_root: str, players: Sequence[Player]) -> None:
        MANAGER_DATABASE.delete_entries(
            self.table(table_root), UUID_TUPLE, [player.get_uuid_tuple() for player in players]
        )


DB_PLAYER = DB_Player()
