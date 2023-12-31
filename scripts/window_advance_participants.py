from typing import cast
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTableWidget, QVBoxLayout, QComboBox
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QCloseEvent
from .advance_list import Advance_List
from .tournament import Tournament
from .gui_functions import get_button, set_window_title, set_window_size
from .gui_table import add_button_to_table, add_combobox_to_table, set_up_table, size_table


class Window_Advance_Participants(QMainWindow):
    window_closed = Signal()

    def __init__(
            self, advance_list: Advance_List, tournaments: list[Tournament], parent: QWidget | None = None
    ) -> None:
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, "Add Participants")

        self.advance_list: Advance_List = advance_list
        self.participant_counts = [tournament.get_participant_count() for tournament in tournaments]
        self.tournaments: list[Tournament] = [
            tournament for (tournament, count) in zip(tournaments, self.participant_counts) if count > 0
        ]

        self.widget: QWidget = QWidget()
        self.layout_main: QHBoxLayout = QHBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.table = QTableWidget()
        self.fill_in_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.table)
        self.layout_main.addLayout(layout)

        add_row_button = get_button("large", (10, 6), "Add\nParticipant", connect=self.add_new_row, translate=True)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(add_row_button)
        self.layout_main.addLayout(layout)

        set_window_size(self, QSize(self.table.maximumWidth() + add_row_button.width(), 0), factor_y=.5)
        if len(self.tournaments) == 0:
            self.close()

    def resize_table(self) -> None:
        size_table(
            self.table, rows=self.table.rowCount(), row_height=3.5, max_width=30, widths=[None, 8, 3.5], stretches_h=[0]
        )

    def get_seeding_choices(self, tournament: Tournament | None) -> list[int]:
        if tournament is None:
            return [i + 1 for i in range(self.participant_counts[0])]
        return [i + 1 for i in range(self.participant_counts[self.tournaments.index(tournament)])]

    def get_combo_box(self, row: int, column: int) -> QComboBox:
        return cast(QComboBox, self.table.cellWidget(row, column))

    def get_tournament(self, row: int) -> Tournament:
        return cast(Tournament, self.get_combo_box(row, 0).currentData())

    def get_placement(self, row: int) -> int:
        return cast(int, self.get_combo_box(row, 1).currentData())

    def add_row(self, tournament: Tournament | None = None, placement: int | None = None) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        add_combobox_to_table(self.table, self.tournaments, row, 0, "medium", None, current=tournament)
        add_combobox_to_table(
            self.table, self.get_seeding_choices(tournament), row, 1, "medium", None, current=placement
        )
        add_button_to_table(self.table, row, 2, "medium", None, '-', connect=self.remove_row)

        self.get_combo_box(row, 0).currentTextChanged.connect(self.update_placement_combobox)
        self.resize_table()

    def add_new_row(self) -> None:
        self.add_row()

    def fill_in_table(self) -> None:
        set_up_table(self.table, 0, 3, header_horizontal=["Tournament", "Placement", ""], translate=True)
        self.resize_table()
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        for tournament, placement in self.advance_list:
            self.add_row(tournament, placement)

    def update_placement_combobox(self) -> None:
        row = self.table.currentRow()
        placement_box = self.get_combo_box(row, 1)
        placement_box.clear()
        for placement in self.get_seeding_choices(self.get_tournament(row)):
            placement_box.addItem(str(placement), placement)

    def remove_row(self) -> None:
        self.table.removeRow(self.table.currentRow())
        self.resize_table()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.advance_list.fill([
            (self.get_tournament(row), self.get_placement(row)) for row in range(self.table.rowCount())
        ])
        self.window_closed.emit()
        super().closeEvent(event)
