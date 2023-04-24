from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHeaderView, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from .table_widget_drag import Table_Widget_Drag
from .functions_gui import add_content_to_table, make_headers_bold_horizontal, make_headers_bold_vertical, size_table


class Window_Line_Up(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, team):
        super().__init__()
        self.setWindowTitle("Change Lineup")

        self.team = team
        self.members = team.get_members()

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.table = Table_Widget_Drag()
        self.fill_in_table()
        self.layout.addWidget(self.table)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(layout)
        self.setFixedWidth(self.table.maximumWidth())
        self.setFixedHeight(min(self.table.maximumHeight(), int(QApplication.primaryScreen().size().height()*.8)))

    def add_member_row(self, row, first_name, last_name, rating):
        add_content_to_table(self.table, first_name, row, 0, edit=False)
        add_content_to_table(self.table, last_name, row, 1, edit=False, bold=True)
        add_content_to_table(self.table, rating, row, 2, edit=False, align=Qt.AlignCenter)

    def fill_in_table(self):
        size_table(self.table, len(self.members), 3, 3.5, max_width=55, widths=[None, None, 5])
        self.table.setHorizontalHeaderLabels(["First Name", "Last Name", "ELO"])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, member in enumerate(self.members):
            self.add_member_row(i, member.get_first_name(), member.get_last_name(), member.get_rating())

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
