from math import inf
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTableWidget, QApplication, QHeaderView, QVBoxLayout
from PyQt5.QtCore import Qt
from .functions_categories import integer_categories
from .functions_gui import get_button, add_button_to_table, add_combobox_to_table, make_headers_bold_horizontal,\
    size_table, add_content_to_table, get_table_value


class Window_Add_Categories(QMainWindow):

    def __init__(self, categories):
        super().__init__()
        self.setWindowTitle("Add Categories")

        self.categories = categories

        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.table = QTableWidget()
        self.make_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.table)
        self.layout.addLayout(layout)

        add_row_button = get_button("large", (8, 6), "Add\nCategory", connect_function=self.add_category_row)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(add_row_button)
        self.layout.addLayout(layout)

        self.setFixedWidth(self.table.maximumWidth() + add_row_button.width())
        self.setFixedHeight(int(QApplication.primaryScreen().size().height() * .3))

    def resize_table(self):
        size_table(self.table, self.table.rowCount(), 4, 3.5, max_width=29.5, widths=[12, 7, 7, 3.5])

    def add_category_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        add_combobox_to_table(self.table, self.categories, row, 0, "medium", None)
        add_content_to_table(self.table, "", row, 1, align=Qt.AlignCenter)
        add_content_to_table(self.table, "", row, 2, align=Qt.AlignCenter)
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect_function=self.remove_row)
        self.resize_table()

    def make_table(self):
        self.resize_table()
        self.table.setHorizontalHeaderLabels(["Category", "From", "Up To", ""])
        make_headers_bold_horizontal(self.table)

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setVisible(False)

    def remove_row(self):
        row = self.table.currentRow()
        self.table.removeRow(row)
        self.resize_table()

    def get_row_values(self, row):
        return get_table_value(self.table, row, 0)[0], get_table_value(self.table, row, 1),\
               get_table_value(self.table, row, 2)

    def remove_invalid_rows(self):
        for row in range(self.table.rowCount() - 1, -1, -1):
            category, bottom, top = self.get_row_values(row)
            invalid = bottom == "" == top or (category in integer_categories and (
                    (bottom != "" and not bottom.isdigit()) or (top != "" and not top.isdigit())
            ))
            if invalid:
                self.table.removeRow(row)
        self.resize_table()

    def get_entries(self):
        self.remove_invalid_rows()
        entries = []
        for row in range(self.table.rowCount()):
            category, bottom, top = self.get_row_values(row)
            if category in integer_categories:
                bottom = -inf if bottom == "" else int(bottom)
                top = inf if top == "" else int(top)
            entries.append((category, bottom, top))
        return entries

    def closeEvent(self, event):
        self.remove_invalid_rows()
        super().closeEvent(event)
