from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QTableWidget
from PyQt5.QtCore import Qt
from .functions_categories import get_category_range_string
from .functions_gui import add_content_to_table, size_table, clear_table


class Widget_Tournament_Standings(QWidget):
    def __init__(self, tournament, category_range=None):
        super().__init__()
        self.tournament = tournament
        self.category_range = category_range

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout.addWidget(self.table)

        self.setMaximumHeight(
            self.table.maximumHeight() + self.layout.contentsMargins().top() + self.layout.contentsMargins().bottom()
        )

    def fill_in_table(self):
        header_horizontal, header_vertical, table = self.tournament.get_standings(self.category_range)
        if self.category_range is not None:
            header_horizontal[0] = get_category_range_string(*self.category_range)
        size_table(
            self.table, len(header_vertical), len(header_horizontal), 3.5,
            max_width=55, widths=len(header_horizontal) * [5]
        )
        self.table.setHorizontalHeaderLabels(header_horizontal)
        self.table.setVerticalHeaderLabels(header_vertical)

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, row in enumerate(table):
            for j, field in enumerate(row):
                add_content_to_table(
                    self.table, field, i, j, edit=False, align=Qt.AlignCenter if j else None, bold=(j == 1)
                )

    def update(self):
        clear_table(self.table)
        self.fill_in_table()
