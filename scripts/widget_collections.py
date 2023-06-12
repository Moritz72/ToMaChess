from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from .class_collection import Collection
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_collection import load_collections_like, update_collections, remove_collections, add_collections
from .functions_gui import add_content_to_table, add_button_to_table, get_button, add_combobox_to_table


class Widget_Collections(Widget_Default_Generic):
    def __init__(self, window_main):
        self.window_main = window_main
        super().__init__(None, load_collections_like, update_collections, remove_collections, add_collections)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(3, 3.5, 55, [None, None, 3.5])
        table.setHorizontalHeaderLabels(["Name", "Type", ""])

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        add_button = get_button("large", (12, 5), "Add\nCollection", connect_function=self.add_new_row)
        save_button = get_button("large", (12, 5), "Save", connect_function=self.update_database)
        return add_button, save_button

    def update_database(self):
        super().update_database()
        self.window_main.load(4)

    def get_object_from_values(self, values):
        return Collection(values[0], values[1][0])

    def edit_object_by_values(self, values, obj):
        if obj.get_name() == "Default":
            return
        obj.set_name(values[0])

    def fill_in_row(self, row, obj=None):
        if obj is None:
            name = ""
            object_type = ""
        else:
            name = obj.get_name()
            object_type = obj.get_object_type()
        add_content_to_table(self.table, name, row, 0, bold=True)
        if name == "":
            add_combobox_to_table(
                self.table, ["Players", "Tournaments", "Teams", "Multi-Stage Tournaments"], row, 1, "medium", None
            )
        else:
            add_content_to_table(self.table, object_type, row, 1, edit=False)
        add_button_to_table(self.table, row, 2, "medium", None, '-', connect_function=self.table.delete_current_row)
