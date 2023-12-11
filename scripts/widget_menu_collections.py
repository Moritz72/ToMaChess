from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QHeaderView, QPushButton
from PySide6.QtCore import Qt
from .collection import Collection
from .table_objects import Table_Objects
from .widget_search_generic import Widget_Search_Generic
from .db_collection import DB_COLLECTION, COLLECTION_ATTRIBUTE_LIST
from .gui_functions import get_button
from .gui_table import add_button_to_table, add_combobox_to_table, add_collection_to_table
if TYPE_CHECKING:
    from .window_main import Window_Main


class Widget_Menu_Collections(Widget_Search_Generic[Collection]):
    def __init__(self, window_main: Window_Main) -> None:
        self.window_main: Window_Main = window_main
        super().__init__(DB_COLLECTION)

    @staticmethod
    def get_table() -> Table_Objects[Collection]:
        table = Table_Objects[Collection](
            3, 3.5, 55, [None, None, 3.5], COLLECTION_ATTRIBUTE_LIST + [""], translate=True
        )
        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        return table

    def get_buttons(self) -> list[QPushButton]:
        return [
            get_button("large", (14, 5), "Add\nCollection", connect=self.add_new_row, translate=True),
            get_button("large", (14, 5), "Save", connect=self.update_database, translate=True)
        ]

    def update_database(self) -> None:
        super().update_database()
        self.window_main.reload()

    def get_object_from_values(self, values: tuple[str, list[str], str]) -> Collection:
        return Collection(values[0], values[1][0])

    def edit_object_by_values(self, values: tuple[str, list[str], str], collection: Collection) -> None:
        if collection.get_name() == "Default":
            return
        collection.set_name(values[0])

    def fill_in_row(self, row: int, collection: Collection | None = None) -> None:
        add_collection_to_table(self.table, row, collection, edit=True)
        items = ["Players", "Tournaments", "Teams", "Multi-Stage Tournaments"]
        if collection is None:
            add_combobox_to_table(self.table, items, row, 1, "medium", None, translate=True)
        add_button_to_table(self.table, row, 2, "medium", None, '-', connect=self.table.delete_current_row)
