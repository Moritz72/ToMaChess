from typing import Any
from math import inf
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTableWidget, QVBoxLayout
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCloseEvent
from .category_range import INTEGER_CATEGORIES, Category_Range
from .gui_functions import get_button, set_window_title, set_window_size
from .gui_table import add_button_to_table, add_combobox_to_table, set_up_table, size_table, \
    add_content_to_table, get_table_value


class Window_Add_Categories(QMainWindow):
    def __init__(self, categories: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        set_window_title(self, "Add Categories")

        self.categories: list[str] = categories

        self.widget: QWidget = QWidget()
        self.layout_main: QHBoxLayout = QHBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.table = QTableWidget()
        set_up_table(self.table, 0, 4, header_horizontal=["Category", "From", "Up To", ""], translate=True)
        self.resize_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.table)
        self.layout_main.addLayout(layout)

        self.add_row_button = get_button("large", (3, 3), '+', connect=self.add_category_row, translate=True)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.add_row_button)
        self.layout_main.addLayout(layout)
        self.size_window()

    def size_window(self) -> None:
        set_window_size(self, QSize(self.table.maximumWidth() + self.add_row_button.width(), 0), factor_y=.4)

    def resize_table(self) -> None:
        size_table(
            self.table, rows=self.table.rowCount(), row_height=3.5, max_width=29.5, widths=[12, 7, 7, 3.5],
            header_width=0, stretches_h=[0]
        )

    def add_category_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        add_combobox_to_table(self.table, self.categories, row, 0, "medium", None, translate=True)
        add_content_to_table(self.table, "", row, 1, align=Qt.AlignmentFlag.AlignCenter)
        add_content_to_table(self.table, "", row, 2, align=Qt.AlignmentFlag.AlignCenter)
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect=self.remove_row)
        self.resize_table()

    def remove_row(self) -> None:
        row = self.table.currentRow()
        self.table.removeRow(row)
        self.resize_table()

    def get_row_values(self, row: int) -> tuple[str, Any, Any]:
        return get_table_value(self.table, row, 0)[0], get_table_value(self.table, row, 1),\
               get_table_value(self.table, row, 2)

    def remove_invalid_rows(self) -> None:
        for row in range(self.table.rowCount() - 1, -1, -1):
            category, bottom, top = self.get_row_values(row)
            invalid_part = (bottom != "" and not bottom.isdigit()) or (top != "" and not top.isdigit())
            invalid = bottom == "" == top or (category in INTEGER_CATEGORIES and invalid_part)
            if invalid:
                self.table.removeRow(row)
        self.resize_table()

    def get_category_ranges(self) -> list[Category_Range]:
        self.remove_invalid_rows()
        entries = []
        for row in range(self.table.rowCount()):
            category, bottom, top = self.get_row_values(row)
            if category in INTEGER_CATEGORIES:
                bottom = -inf if bottom == "" else int(bottom)
                top = inf if top == "" else int(top)
            entries.append((category, bottom, top))
        return [Category_Range(*entry) for entry in entries]

    def closeEvent(self, event: QCloseEvent) -> None:
        self.remove_invalid_rows()
        super().closeEvent(event)
