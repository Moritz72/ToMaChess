from PySide6.QtWidgets import QVBoxLayout, QTableWidget
from PySide6.QtCore import Qt
from .tournament import Tournament
from .widget_tournament_info import Widget_Tournament_Info
from .gui_functions import get_label
from .gui_table import size_table, add_content_to_table


class Widget_Tournament_Details(Widget_Tournament_Info):
    def __init__(self, tournament: Tournament):
        super().__init__("Details", tournament)
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        header = get_label(
            self.tournament.get_name(), "extra_large",
            widget_size=(None, 5), bold=True, align=Qt.AlignmentFlag.AlignCenter
        )
        self.layout_main.addWidget(header)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout_main.addWidget(self.table)

    def fill_in_table(self) -> None:
        description = self.tournament.get_details()
        size_table(
            self.table, rows=len(description), columns=2, row_height=4, max_width=55, header_width=3, stretches_h=[0, 1]
        )
        self.table.setHorizontalHeaderLabels(2 * [""])
        self.table.setVerticalHeaderLabels(self.table.rowCount() * [""])
        for i, (key, value) in enumerate(description.items()):
            add_content_to_table(self.table, key, i, 0, size="large", edit=False, bold=True, translate=True)
            add_content_to_table(self.table, value, i, 1, size="large", edit=False, translate=True)

    def refresh(self) -> None:
        self.fill_in_table()
