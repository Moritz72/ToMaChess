from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHeaderView, QTableWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_gui import add_content_to_table, make_headers_bold_horizontal, make_headers_bold_vertical,\
    get_check_box, size_table


class Window_Add_Teams(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, teams, checked_player_uuids=[]):
        super().__init__()
        self.setWindowTitle("Add Teams")

        self.teams = teams
        self.checked_player_uuids = checked_player_uuids

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout.addWidget(self.table)
        self.setFixedWidth(self.table.maximumWidth())
        self.setFixedHeight(min(self.table.maximumHeight(), int(QApplication.primaryScreen().size().height()*.8)))

    def add_player_row(self, row, name, members, check_state):
        add_content_to_table(self.table, name, row, 0, edit=False, bold=True)
        add_content_to_table(self.table, members, row, 1, edit=False, align=Qt.AlignCenter)
        check_box = get_check_box(check_state, (3.5, 3.5))
        self.table.setCellWidget(row, 2, check_box)

    def fill_in_table(self):
        size_table(self.table, len(self.teams), 3, 3.5, max_width=55, widths=[None, 7, 3.5])
        self.table.setHorizontalHeaderLabels(["Name", "Members", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, team in enumerate(self.teams):
            self.add_player_row(
                i, team.get_name(), len(team.get_members()), team.get_uuid() in self.checked_player_uuids
            )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            current_row = self.table.currentRow()
            checkbox = self.table.cellWidget(current_row, 2)
            checkbox.setChecked(not checkbox.isChecked())
            self.table.selectRow(current_row+1)
        elif event.key() == Qt.Key_Backspace:
            current_row = self.table.currentRow()
            checkbox = self.table.cellWidget(current_row, 2)
            checkbox.setChecked(not checkbox.isChecked())
            self.table.selectRow(current_row-1)

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
