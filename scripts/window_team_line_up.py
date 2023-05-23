from PyQt5.QtWidgets import QMainWindow, QWidget, QHeaderView, QHBoxLayout, QApplication
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
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
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
        self.setFixedHeight(int(QApplication.primaryScreen().size().height() * .8))

    def add_member_row(self, row, obj):
        add_content_to_table(self.table, obj.get_name(), row, 0, edit=False, bold=True)
        add_content_to_table(self.table, obj.get_sex(), row, 1, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_birthday(), row, 2, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_country(), row, 3, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_title(), row, 4, edit=False, align=Qt.AlignCenter)
        add_content_to_table(self.table, obj.get_rating(), row, 5, edit=False, align=Qt.AlignCenter)

    def fill_in_table(self):
        size_table(self.table, len(self.members), 6, 3.5, max_width=55, widths=[None, 3.5, 5, 4.5, 4, 5, 3.5])
        self.table.setHorizontalHeaderLabels(["Name", "Sex", "Birth", "Fed.", "Title", "Rating"])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, member in enumerate(self.members):
            self.add_member_row(i, member)

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
