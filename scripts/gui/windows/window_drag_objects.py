from typing import Generic, TypeVar, cast
from PySide6.QtCore import Signal, QSize
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QWidget
from ..common.gui_functions import set_window_size, set_window_title
from ..common.gui_table import add_player_to_table, add_team_to_table
from ..tables.table_objects import Table_Objects_Drag
from ...common.object import Object
from ...database.db_player import PLAYER_ATTRIBUTE_LIST
from ...database.db_team import TEAM_ATTRIBUTE_LIST
from ...player.player import Player
from ...team.team import Team


T = TypeVar("T", bound=Object)


class Widget_Drag_Players(Table_Objects_Drag[Player]):
    def __init__(self, players: list[Player], parent: QWidget | None = None) -> None:
        super().__init__(
            6, 3.5, 55, [None, 3.5, 5, 4.5, 4, 5, 3.5], PLAYER_ATTRIBUTE_LIST,
            stretches=[0], translate=True, parent=parent
        )
        self.set_objects(players)

        for i, player in enumerate(self.objects):
            assert(player is not None)
            add_player_to_table(self, i, player)


class Widget_Drag_Teams(Table_Objects_Drag[Team]):
    def __init__(self, teams: list[Team], parent: QWidget | None = None) -> None:
        super().__init__(
            2, 3.5, 55, [None, 5.], TEAM_ATTRIBUTE_LIST, stretches=[0], translate=True, parent=parent
        )
        self.set_objects(teams)

        for i, team in enumerate(self.objects):
            assert(team is not None)
            add_team_to_table(self, i, team)


class Window_Drag_Objects(QMainWindow, Generic[T]):
    window_closed = Signal()

    def __init__(self, widget: Table_Objects_Drag[T], title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        set_window_title(self, title)

        self.widget: Table_Objects_Drag[T] = widget
        self.setCentralWidget(self.widget)
        self.size_window()

    def size_window(self) -> None:
        set_window_size(self, QSize(self.widget.maximumWidth(), 0), factor_y=.8)

    def get_objects(self) -> list[T]:
        return cast(list[T], self.widget.objects)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.window_closed.emit()
        super().closeEvent(event)


class Window_Drag_Players(Window_Drag_Objects[Player]):
    def __init__(self, players: list[Player], title: str, parent: QWidget | None = None) -> None:
        super().__init__(Widget_Drag_Players(players), title, parent=parent)


class Window_Drag_Teams(Window_Drag_Objects[Team]):
    def __init__(self, teams: list[Team], title: str, parent: QWidget | None = None) -> None:
        super().__init__(Widget_Drag_Teams(teams), title, parent=parent)
