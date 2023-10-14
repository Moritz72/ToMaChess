from PySide6.QtWidgets import QMainWindow, QHeaderView
from PySide6.QtCore import Qt, Signal, QSize
from .table_widget_drag import Table_Widget_Drag
from .functions_player import PLAYER_ATTRIBUTE_LIST
from .functions_gui import set_up_table, size_table, set_window_title, set_window_size, add_player_to_table


class Window_Line_Up(QMainWindow):
    window_closed = Signal()

    def __init__(self, team, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, "Change Lineup")

        self.members = team.get_members()

        self.table = Table_Widget_Drag()
        self.fill_in_table()
        self.setCentralWidget(self.table)

        set_window_size(self, QSize(self.table.maximumWidth(), 0), factor_y=.8)

    def add_row(self, row, obj):
        add_player_to_table(self.table, row, obj)

    def fill_in_table(self):
        set_up_table(self.table, 0, 6, header_horizontal=PLAYER_ATTRIBUTE_LIST, translate=True)
        size_table(self.table, len(self.members), 3.5, max_width=55, widths=[None, 3.5, 5, 4.5, 4, 5, 3.5])

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, member in enumerate(self.members):
            self.add_row(i, member)

    def get_permutation(self):
        return self.table.permutation

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
