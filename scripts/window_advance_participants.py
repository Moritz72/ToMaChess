from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTableWidget, QApplication, QHeaderView, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QSize
from .functions_gui import get_button, add_button_to_table, add_combobox_to_table, set_up_table, size_table,\
    set_window_title, set_window_size


class Window_Advance_Participants(QMainWindow):
    window_closed = Signal()

    def __init__(self, advance_list, tournaments, participant_counts, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, "Add Participants")

        self.advance_list = advance_list
        self.tournaments = [tournament for tournament, count in zip(tournaments, participant_counts) if count > 0]
        self.participant_counts = [count for count in participant_counts if count > 0]
        if len(self.tournaments) == 0:
            self.close()

        self.widget = QWidget()
        self.layout = QHBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.table = QTableWidget()
        self.fill_in_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.table)
        self.layout.addLayout(layout)

        add_row_button = get_button(
            "large", (10, 6), "Add\nParticipant", connect_function=self.add_new_row, translate=True
        )
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(add_row_button)
        self.layout.addLayout(layout)

        set_window_size(self, QSize(
            self.table.maximumWidth() + add_row_button.width(), int(QApplication.primaryScreen().size().height() * .5)
        ))

    def resize_table(self):
        size_table(self.table, self.table.rowCount(), 3.5, max_width=30, widths=[None, 8, 3.5])

    def get_seatings_choices(self, tournament):
        if tournament is None:
            return [str(i + 1) for i in range(self.participant_counts[0])]
        return [str(i + 1) for i in range(self.participant_counts[self.tournaments.index(tournament)])]

    def add_row(self, tournament=None, placement=None):
        row = self.table.rowCount()
        self.table.insertRow(row)

        add_combobox_to_table(self.table, self.tournaments, row, 0, "medium", None, current=tournament)
        add_combobox_to_table(
            self.table, self.get_seatings_choices(tournament), row, 1, "medium", None,
            current=placement if placement is None else str(placement)
        )
        add_button_to_table(self.table, row, 2, "medium", None, '-', connect_function=self.remove_row)

        self.table.cellWidget(row, 0).currentTextChanged.connect(self.update_placement_combobox)
        self.resize_table()

    def add_new_row(self):
        self.add_row()

    def fill_in_table(self):
        set_up_table(self.table, 0, 3, header_horizontal=["Tournament", "Placement", ""], translate=True)
        self.resize_table()

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for tournament, placement in self.advance_list:
            self.add_row(tournament, placement)

    def update_placement_combobox(self):
        row = self.table.currentRow()
        tournament = self.table.cellWidget(row, 0).currentData()
        self.table.cellWidget(row, 1).clear()
        self.table.cellWidget(row, 1).addItems(self.get_seatings_choices(tournament))

    def remove_row(self):
        row = self.table.currentRow()
        self.table.removeRow(row)
        self.resize_table()

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
