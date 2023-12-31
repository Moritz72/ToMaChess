from PySide6.QtWidgets import QPushButton
from .player import Player
from .table_objects import Table_Objects
from .widget_search_generic import Widget_Search_Generic
from .db_player import DB_PLAYER, PLAYER_ATTRIBUTE_LIST
from .gui_functions import get_button
from .gui_table import add_button_to_table, add_player_to_table


class Widget_Menu_Players(Widget_Search_Generic[Player]):
    def __init__(self) -> None:
        super().__init__(DB_PLAYER)

    def get_table(self) -> Table_Objects[Player]:
        return Table_Objects[Player](
            7, 3.5, 55, [None, 3.5, 5, 4.5, 4, 5, 3.5], PLAYER_ATTRIBUTE_LIST + [""],
            stretches=[0], translate=True, parent=self
        )

    def get_buttons(self) -> list[QPushButton]:
        return [
            get_button("large", (14, 5), "Save", connect=self.update_database, translate=True),
            get_button("large", (14, 5), "Add\nPlayer", connect=self.add_new_row, translate=True)
        ]

    def get_object_from_values(self, values: tuple[str, str, str, str, str, str, str]) -> Player:
        return Player(*values[:6], uuid_associate=self.get_associate_uuid())

    def edit_object_by_values(self, values: tuple[str, str, str, str, str, str, str], player: Player) -> None:
        player.set_name(values[0])
        player.set_sex(values[1])
        player.set_birthday(values[2])
        player.set_country(values[3])
        player.set_title(values[4])
        player.set_rating(values[5])
        player.set_uuid_associate(self.get_associate_uuid())

    def fill_in_row(self, row: int, player: Player | None = None) -> None:
        add_player_to_table(self.table, row, player, edit=True)
        add_button_to_table(self.table, row, 6, "medium", None, '-', connect=self.table.delete_current_row)
