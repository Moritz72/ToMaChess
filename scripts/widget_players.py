from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from .class_player import Player
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_player import load_players_like, update_players, add_players, remove_players
from .functions_gui import add_content_to_table, add_button_to_table, make_headers_bold_horizontal, \
    make_headers_bold_vertical, get_button


class Widget_Players(Widget_Default_Generic):
    def __init__(self):
        super().__init__("Players", load_players_like, update_players, remove_players, add_players)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(7, 3.5, 55, [None, 3.5, 5, 4.5, 4, 5, 3.5])
        table.setHorizontalHeaderLabels(["Name", "Sex", "Birth", "Fed.", "Title", "Rating", ""])
        make_headers_bold_horizontal(table)
        make_headers_bold_vertical(table)

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        add_button = get_button("large", (12, 5), "Add\nPlayer", connect_function=self.add_new_row)
        save_button = get_button("large", (12, 5), "Save", connect_function=self.update_database)
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
        if obj is None:
            name = sex = birthday = country = title = rating = ""
        else:
            name, sex, birthday, country, title, rating = obj.get_data()[:6]
        add_content_to_table(self.table, name, row, 0, bold=True)
        add_content_to_table(self.table, sex, row, 1, align=Qt.AlignCenter)
        add_content_to_table(self.table, birthday, row, 2, align=Qt.AlignCenter)
        add_content_to_table(self.table, country, row, 3, align=Qt.AlignCenter)
        add_content_to_table(self.table, title, row, 4, align=Qt.AlignCenter)
        add_content_to_table(self.table, rating, row, 5, align=Qt.AlignCenter)
        add_button_to_table(self.table, row, 6, "medium", None, '-', connect_function=self.table.delete_current_row)
