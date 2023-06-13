from PyQt5.QtWidgets import QMainWindow, QWidget, QHeaderView, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
from .table_widget_drag import Table_Widget_Drag
from .functions_gui import add_content_to_table, set_up_table, size_table, set_window_title


class Window_Line_Up(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, team):
        super().__init__()
        set_window_title(self, "Change Lineup")

        self.team = team
        self.members = team.get_members()

        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.table = Table_Widget_Drag()
        self.fill_in_table()
        self.layout.addWidget(self.table)

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
        set_up_table(
            self.table, 0, 6, header_horizontal=["Name", "Sex", "Birth", "Fed.", "Title", "Rating"], translate=True
        )
        size_table(self.table, len(self.members), 3.5, max_width=55, widths=[None, 3.5, 5, 4.5, 4, 5, 3.5])

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, member in enumerate(self.members):
            self.add_member_row(i, member)

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
