from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt
from .class_player import Player
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_player import load_players_like, update_players, add_players, remove_players, PLAYER_ATTRIBUTE_LIST
from .functions_gui import add_button_to_table, get_button, add_player_to_table


class Widget_Players(Widget_Default_Generic):
    def __init__(self):
        super().__init__("Players", load_players_like, update_players, remove_players, add_players)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(
            7, 3.5, 55, [None, 3.5, 5, 4.5, 4, 5, 3.5], PLAYER_ATTRIBUTE_LIST + [""], translate=True
        )

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        add_button = get_button("large", (14, 5), "Add\nPlayer", connect_function=self.add_new_row, translate=True)
        save_button = get_button("large", (14, 5), "Save", connect_function=self.update_database, translate=True)
        return add_button, save_button

    def get_object_from_values(self, values):
        return Player(*values[:6], uuid_associate=self.collection_current.get_uuid())

    def edit_object_by_values(self, values, obj):
        obj.set_name(values[0])
        obj.set_sex(values[1])
        obj.set_birthday(values[2])
        obj.set_country(values[3])
        obj.set_title(values[4])
        obj.set_rating(values[5])
        obj.set_uuid_associate(self.collection_current.get_uuid())

    def fill_in_row(self, row, obj=None):
        add_player_to_table(self.table, row, obj, edit=True)
        add_button_to_table(self.table, row, 6, "medium", None, '-', connect_function=self.table.delete_current_row)
