from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QApplication, QTableWidget, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_gui import size_table, make_headers_bold_vertical, make_headers_bold_horizontal, add_content_to_table,\
    add_button_to_table


class Window_Team_Remove_Members(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, members):
        super().__init__()
        self.setWindowTitle("Remove Members")
        self.members = members
        self.removed_members = []

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget()
        self.fill_in_table()

        self.layout.addWidget(self.table)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.setFixedWidth(self.table.maximumWidth())

    def add_member_row(self, row, first_name, last_name, rating):
        add_content_to_table(self.table, first_name, row, 0, edit=False)
        add_content_to_table(self.table, last_name, row, 1, bold=True, edit=False)
        add_content_to_table(self.table, rating, row, 2, align=Qt.AlignCenter, edit=False)
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect_function=self.add_member_to_be_removed)

    def resize_table(self):
        size_table(self.table, len(self.members), 4, 3.5, max_width=55, widths=[None, None, 4.5, 3.5])
        self.setFixedHeight(min(self.table.maximumHeight(), int(QApplication.primaryScreen().size().height() * .8)))

    def fill_in_table(self):
        self.resize_table()
        self.table.setHorizontalHeaderLabels(["First Name", "Last Name", "ELO", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, member in enumerate(self.members):
            self.add_member_row(i, member.get_first_name(), member.get_last_name(), member.get_rating())

    def add_member_to_be_removed(self):
        row = self.table.currentRow()
        self.removed_members.append(self.members[row])
        del self.members[row]
        self.table.removeRow(row)
        self.resize_table()

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
