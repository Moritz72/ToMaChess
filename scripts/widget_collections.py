from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt
from .class_collection import Collection
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_collection import load_collections_like, update_collections, remove_collections, add_collections, \
    COLLECTION_ATTRIBUTE_LIST
from .functions_gui import add_button_to_table, get_button, add_combobox_to_table, add_collection_to_table


class Widget_Collections(Widget_Default_Generic):
    def __init__(self, window_main):
        self.window_main = window_main
        super().__init__(None, load_collections_like, update_collections, remove_collections, add_collections)

    @staticmethod
    def get_table():
        table = Table_Widget_Search(3, 3.5, 55, [None, None, 3.5], COLLECTION_ATTRIBUTE_LIST + [""], translate=True)

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        add_button = get_button("large", (14, 5), "Add\nCollection", connect_function=self.add_new_row, translate=True)
        save_button = get_button("large", (14, 5), "Save", connect_function=self.update_database, translate=True)
        return add_button, save_button

    def update_database(self):
        super().update_database()
        self.window_main.reload()

    def get_object_from_values(self, values):
        return Collection(values[0], values[1][0])

    def edit_object_by_values(self, values, obj):
        if obj.get_name() == "Default":
            return
        obj.set_name(values[0])

    def fill_in_row(self, row, obj=None):
        add_collection_to_table(self.table, row, obj, edit=True)
        if obj is None:
            add_combobox_to_table(
                self.table, ["Players", "Tournaments", "Teams", "Multi-Stage Tournaments"], row, 1, "medium", None,
                translate=True
            )
        add_button_to_table(self.table, row, 2, "medium", None, '-', connect_function=self.table.delete_current_row)
