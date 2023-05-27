from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QTableWidget, QHeaderView
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
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.table = QTableWidget()
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
        add_button_to_table(self.table, row, 6, "medium", None, '-', connect_function=self.add_member_to_be_removed)

    def resize_table(self):
        size_table(self.table, len(self.members), 7, 3.5, max_width=55, widths=[None, 3.5, 5, 4.5, 4, 5, 3.5])

    def fill_in_table(self):
        self.resize_table()
        self.table.setHorizontalHeaderLabels(["Name", "Sex", "Birth", "Fed.", "Title", "Rating", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, member in enumerate(self.members):
            self.add_member_row(i, member)

    def add_member_to_be_removed(self):
        row = self.table.currentRow()
        self.removed_members.append(self.members[row])
        del self.members[row]
        self.table.removeRow(row)
        self.resize_table()

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
