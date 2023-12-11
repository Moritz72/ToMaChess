from abc import abstractmethod
from typing import TypeVar, Generic
from PySide6.QtWidgets import QMainWindow, QTableWidget, QHeaderView, QWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QCloseEvent
from .object import Object
from .player import Player
from .team import Team
from .db_player import PLAYER_ATTRIBUTE_LIST
from .db_team import TEAM_ATTRIBUTE_LIST
from .gui_functions import set_window_title, set_window_size
from .gui_table import set_up_table, size_table, add_button_to_table, add_player_to_table, add_team_to_table

T = TypeVar('T', bound=Object)


class Table_Remove_Objects(QTableWidget, Generic[T]):
    def __init__(self, objects: list[T]) -> None:
        super().__init__()
        self.objects: list[T] = objects
        self.removed_objects: list[T] = []
        self.fill_in_table()

    @abstractmethod
    def add_row(self, row: int, obj: T) -> None:
        pass

    @abstractmethod
    def resize_table(self) -> None:
        pass

    def fill_in_table(self) -> None:
        for i, obj in enumerate(self.objects):
            self.add_row(i, obj)

    def add_object_to_be_removed(self) -> None:
        row = self.currentRow()
        self.removed_objects.append(self.objects[row])
        del self.objects[row]
        self.removeRow(row)
        self.resize_table()


class Table_Remove_Players(Table_Remove_Objects[Player]):
    def __init__(self, players: list[Player]) -> None:
        super().__init__(players)

    def add_row(self, row: int, player: Player) -> None:
        add_player_to_table(self, row, player)
        add_button_to_table(self, row, 6, "medium", None, '-', connect=self.add_object_to_be_removed)

    def resize_table(self) -> None:
        size_table(self, len(self.objects), 3.5, max_width=55, widths=[None, 3.5, 5, 4.5, 4, 5, 3.5])

    def fill_in_table(self) -> None:
        set_up_table(self, 0, 7, header_horizontal=PLAYER_ATTRIBUTE_LIST + [""], translate=True)
        self.resize_table()

        header_horizontal, header_vertical = self.horizontalHeader(), self.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        super().fill_in_table()


class Table_Remove_Teams(Table_Remove_Objects[Team]):
    def __init__(self, teams: list[Team]) -> None:
        super().__init__(teams)

    def add_row(self, row: int, team: Team) -> None:
        add_team_to_table(self, row, team)
        add_button_to_table(self, row, 2, "medium", None, '-', connect=self.add_object_to_be_removed)

    def resize_table(self) -> None:
        size_table(self, len(self.objects), 3.5, max_width=55, widths=[None, 5, 3.5])

    def fill_in_table(self) -> None:
        set_up_table(self, 0, 3, header_horizontal=TEAM_ATTRIBUTE_LIST + [""], translate=True)
        self.resize_table()

        header_horizontal, header_vertical = self.horizontalHeader(), self.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        super().fill_in_table()


class Window_Remove_Objects(QMainWindow, Generic[T]):
    window_closed = Signal()

    def __init__(self, table: Table_Remove_Objects[T], title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, title)

        self.table: Table_Remove_Objects[T] = table
        self.setCentralWidget(self.table)

        set_window_size(self, QSize(self.table.maximumWidth(), 0), factor_y=.8)

    def get_removed_objects(self) -> list[T]:
        return self.table.removed_objects

    def closeEvent(self, event: QCloseEvent) -> None:
        self.window_closed.emit()
        super().closeEvent(event)


class Window_Remove_Players(Window_Remove_Objects[Player]):
    def __init__(self, title: str, players: list[Player], parent: QWidget | None = None) -> None:
        super().__init__(Table_Remove_Players(players), title, parent)


class Window_Remove_Teams(Window_Remove_Objects[Team]):
    def __init__(self, title: str, teams: list[Team], parent: QWidget | None = None) -> None:
        super().__init__(Table_Remove_Teams(teams), title, parent)
