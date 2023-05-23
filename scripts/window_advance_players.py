from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTableWidget, QApplication, QHeaderView, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_gui import get_button, add_button_to_table, add_combobox_to_table, make_headers_bold_horizontal,\
    make_headers_bold_vertical, size_table


class Window_Advance_Players(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, advance_list, tournaments, player_counts):
        super().__init__()
        self.setWindowTitle("Add Players")
        self.advance_list = advance_list
        self.tournaments = [
            tournament for tournament, player_count in zip(tournaments, player_counts) if player_count > 0
        ]
        self.player_counts = [player_count for player_count in player_counts if player_count > 0]

        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.table = QTableWidget()
        self.fill_in_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.table)
        self.layout.addLayout(layout)

        add_row_button = get_button("large", (8, 6), "Add\nPlayer", connect_function=lambda _: self.add_player_row())
        if len(self.tournaments) == 0:
            add_row_button.setVisible(False)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(add_row_button)
        self.layout.addLayout(layout)
        self.setFixedWidth(self.table.maximumWidth()+add_row_button.width())

    def set_window_height(self):
        self.setFixedHeight(
            min(
                max(self.table.maximumHeight(), int(QApplication.primaryScreen().size().height() * .3)),
                int(QApplication.primaryScreen().size().height() * .8)
            )
        )

    def resize_table(self):
        size_table(self.table, self.table.rowCount(), 3, 3.5, max_width=30, widths=[None, 8, 3.5])
        self.set_window_height()

    def get_seatings_choices(self, tournament):
        if tournament is None:
            return [str(i + 1) for i in range(self.player_counts[0])]
        return [str(i + 1) for i in range(self.player_counts[self.tournaments.index(tournament)])]

    def add_player_row(self, tournament=None, placement=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        add_combobox_to_table(self.table, self.tournaments, row, 0, "medium", None, current=tournament)
        self.table.cellWidget(row, 0).currentTextChanged.connect(self.update_placement_combobox)
        add_combobox_to_table(
            self.table, self.get_seatings_choices(tournament), row, 1, "medium", None,
            current=placement if placement is None else str(placement), item_limit=20
        )
        add_button_to_table(self.table, row, 2, "medium", None, '-', connect_function=self.remove_row)
        self.resize_table()

    def fill_in_table(self):
        self.resize_table()
        self.table.setHorizontalHeaderLabels(["Tournament", "Placement", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for tournament, placement in self.advance_list:
            self.add_player_row(tournament, placement)

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
