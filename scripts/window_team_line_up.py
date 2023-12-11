from PySide6.QtWidgets import QMainWindow, QHeaderView, QWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QCloseEvent
from .player import Player
from .team import Team
from .table_drag import Table_Drag
from .db_player import PLAYER_ATTRIBUTE_LIST
from .gui_functions import set_window_title, set_window_size
from .gui_table import set_up_table, size_table, add_player_to_table


class Window_Line_Up(QMainWindow):
    window_closed = Signal()

    def __init__(self, team: Team, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, "Change Lineup")

        self.members: list[Player] = team.get_members()
        self.table: Table_Drag = Table_Drag()

        self.fill_in_table()
        self.setCentralWidget(self.table)

        set_window_size(self, QSize(self.table.maximumWidth(), 0), factor_y=.8)

    def add_row(self, row: int, player: Player) -> None:
        add_player_to_table(self.table, row, player)

    def fill_in_table(self) -> None:
        set_up_table(self.table, 0, 6, header_horizontal=PLAYER_ATTRIBUTE_LIST, translate=True)
        size_table(self.table, len(self.members), 3.5, max_width=55, widths=[None, 3.5, 5, 4.5, 4, 5, 3.5])

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        for i, member in enumerate(self.members):
            self.add_row(i, member)

    def get_permutation(self) -> list[int]:
        return self.table.permutation

    def closeEvent(self, event: QCloseEvent) -> None:
        self.window_closed.emit()
        super().closeEvent(event)
