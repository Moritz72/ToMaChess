from __future__ import annotations
from functools import partial
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QAbstractItemView, QMainWindow, QTableWidget, QWidget
from ..common.gui_functions import set_window_title, set_window_size
from ..common.gui_table import add_blank_to_table, add_button_threaded_to_table, add_content_to_table, set_up_table, \
    size_table
from ...common.functions_util import get_uuid_from_numbers
from ...database.db_collection import collection_exists
from ...database.manager_database import MANAGER_DATABASE
from ...player.functions_rating_lists import COUNTRIES, FEDERATIONS, INDICES, NAMES_DICT, update_list
if TYPE_CHECKING:
    from .window_main import Window_Main


class Window_Rating_Lists(QMainWindow):
    def __init__(self, window_main: Window_Main, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        set_window_title(self, "Rating Lists")
        self.window_main: Window_Main = window_main
        self.updating: int | None = None

        self.table: QTableWidget = QTableWidget()
        self.setCentralWidget(self.table)

        set_up_table(
            self.table, len(INDICES), 6, header_horizontal=["Rating List", "Chess Federation", "Country", "", "", ""],
            header_vertical=len(INDICES) * [""], translate=True
        )
        size_table(
            self.table, row_height=3.5, max_width=85, widths=[None, 25, 10, 10, 10, 10], header_width=3, stretches_h=[0]
        )
        set_window_size(self, self.table.maximumSize(), factor_y=.8, center=True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        for row in range(len(INDICES)):
            self.add_row(row)

    def add_row(self, row: int) -> None:
        add_content_to_table(self.table, NAMES_DICT[INDICES[row]], row, 0, edit=False)
        add_content_to_table(self.table, FEDERATIONS[INDICES[row][0]], row, 1, edit=False)
        add_content_to_table(self.table, COUNTRIES[INDICES[row][0]], row, 2, edit=False)
        if collection_exists("", get_uuid_from_numbers(0, *INDICES[row])):
            add_blank_to_table(self.table, row, 3)
            add_button_threaded_to_table(
                self.table, row, 4, self.window_main, "medium", None, "Update", "Updating...",
                connect=partial(self.update_list, row), on_finish=partial(self.set_updating, row), translate=True
            )
            add_button_threaded_to_table(
                self.table, row, 5, self.window_main, "medium", None, "Delete", "Deleting...",
                connect=partial(self.remove_list, row), on_finish=partial(self.set_updating, row), translate=True
            )
        else:
            add_button_threaded_to_table(
                self.table, row, 3, self.window_main, "medium", None, "Create", "Creating...",
                connect=partial(self.update_list, row), on_finish=partial(self.set_updating, row), translate=True
            )
            add_blank_to_table(self.table, row, 4)
            add_blank_to_table(self.table, row, 5)

    def update_list(self, row: int) -> None:
        if self.updating is None:
            self.updating = row
            update_list(*INDICES[row])

    def remove_list(self, row: int) -> None:
        if self.updating is None:
            self.updating = row
            MANAGER_DATABASE.delete_entry("collections", ("uuid",), (get_uuid_from_numbers(0, *INDICES[row]),))
            MANAGER_DATABASE.cursor.execute("VACUUM")

    def set_updating(self, row: int) -> None:
        if self.updating == row:
            self.add_row(row)
            self.updating = None
