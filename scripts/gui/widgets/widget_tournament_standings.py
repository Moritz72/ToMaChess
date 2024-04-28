from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QVBoxLayout
from .widget_tournament_info import Widget_Tournament_Info
from ..common.gui_table import add_content_to_table, clear_table, set_up_table, size_table
from ...tournament.common.category_range import Category_Range
from ...tournament.tournaments.tournament import Tournament


class Widget_Tournament_Standings(Widget_Tournament_Info):
    def __init__(self, tournament: Tournament, category_range: Category_Range | None = None) -> None:
        super().__init__("Standings", tournament)
        self.category_range = category_range

        self.layout_main: QVBoxLayout = QVBoxLayout(self)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout_main.addWidget(self.table)

    def fill_in_table(self) -> None:
        table = self.tournament.get_standings(self.category_range)
        h_vertical = table.get_header_vertical()
        if self.category_range is not None:
            table.headers[0] = self.category_range.get_title()
        set_up_table(
            self.table, len(h_vertical), len(table.headers),
            header_horizontal=table.headers, header_vertical=h_vertical, translate=True
        )
        size_table(
            self.table, rows=len(h_vertical), row_height=3.5, max_width=55, widths=len(table.headers) * [5.],
            stretches_h=[0]
        )
        margins = self.layout_main.contentsMargins().top() + self.layout_main.contentsMargins().bottom()
        self.setMaximumHeight(self.table.maximumHeight() + margins)
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        for i, strings in enumerate(table.get_strings()):
            add_content_to_table(self.table, strings[0], i, 0, edit=False, bold=True)
            for j, string in enumerate(strings[1:]):
                add_content_to_table(self.table, string, i, j + 1, edit=False, align=Qt.AlignmentFlag.AlignCenter)

    def refresh(self) -> None:
        clear_table(self.table)
        self.fill_in_table()
