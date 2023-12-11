from abc import abstractmethod
from typing import Any, TypeVar, Generic
from PySide6.QtWidgets import QMainWindow, QHeaderView, QPushButton, QWidget
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QCloseEvent
from .object import Object
from .player import Player
from .team import Team
from .table_objects import Table_Objects
from .widget_search_generic import Widget_Search_Generic
from .db_object import DB_Object
from .db_player import DB_PLAYER, PLAYER_ATTRIBUTE_LIST
from .db_team import DB_TEAM, TEAM_ATTRIBUTE_LIST
from .gui_functions import get_check_box, set_window_title, set_window_size
from .gui_table import add_player_to_table, add_team_to_table

T = TypeVar('T', bound=Object)


class Widget_Choice_Object(Widget_Search_Generic[T], Generic[T]):
    def __init__(
            self, db: DB_Object[T], excluded_uuids: set[tuple[str, str]], checked_uuids: set[tuple[str, str]],
            shallow_load: bool = False
    ) -> None:
        self.excluded_uuids: set[tuple[str, str]] = excluded_uuids
        self.checked_uuids: set[tuple[str, str]] = checked_uuids
        super().__init__(db, shallow_load=shallow_load)

    @staticmethod
    @abstractmethod
    def get_table() -> Table_Objects[T]:
        pass

    def get_buttons(self) -> list[QPushButton]:
        return []

    def search_objects(self) -> list[T]:
        return [obj for obj in super().search_objects() if obj.get_uuid_tuple() not in self.excluded_uuids]

    def get_object_from_values(self, values: tuple[Any, ...]) -> T:
        return NotImplemented

    def edit_object_by_values(self, values: tuple[Any, ...], obj: T) -> None:
        return

    def check_box_clicked(self, state: int) -> None:
        obj = self.table.objects[self.table.currentRow()]
        if obj is None:
            return
        if state == 2:
            self.checked_uuids.add(obj.get_uuid_tuple())
        else:
            self.checked_uuids.remove(obj.get_uuid_tuple())

    def get_checked_objects(self) -> list[T]:
        return self.db.load_list(
            "", [uuids[0] for uuids in self.checked_uuids], [uuids[1] for uuids in self.checked_uuids]
        )


class Widget_Choice_Players(Widget_Choice_Object[Player]):
    def __init__(self, excluded_uuids: set[tuple[str, str]], checked_uuids: set[tuple[str, str]]) -> None:
        super().__init__(DB_PLAYER, excluded_uuids, checked_uuids)

    @staticmethod
    def get_table() -> Table_Objects[Player]:
        table = Table_Objects[Player](
            7, 3.5, 55, [None, 3.5, 5, 4.5, 4, 5, 3.5], PLAYER_ATTRIBUTE_LIST + [""], translate=True
        )

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        return table

    def fill_in_row(self, row: int, player: Player | None = None) -> None:
        if player is None:
            return
        add_player_to_table(self.table, row, player)
        check_box = get_check_box(player.get_uuid_tuple() in self.checked_uuids, (3.5, 3.5))
        check_box.stateChanged.connect(self.check_box_clicked)
        self.table.setCellWidget(row, 6, check_box)


class Widget_Choice_Teams(Widget_Choice_Object[Team]):
    def __init__(self, excluded_uuids: set[tuple[str, str]], checked_uuids: set[tuple[str, str]]) -> None:
        super().__init__(DB_TEAM, excluded_uuids, checked_uuids, shallow_load=True)

    @staticmethod
    def get_table() -> Table_Objects[Team]:
        table = Table_Objects[Team](3, 3.5, 55, [None, 5, 3.5], TEAM_ATTRIBUTE_LIST + [""], translate=True)

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        return table

    def fill_in_row(self, row: int, team: Team | None = None) -> None:
        if team is None:
            return
        add_team_to_table(self.table, row, team)
        check_box = get_check_box(team.get_uuid_tuple() in self.checked_uuids, (3.5, 3.5))
        check_box.stateChanged.connect(self.check_box_clicked)
        self.table.setCellWidget(row, 2, check_box)


class Window_Choice_Objects(QMainWindow, Generic[T]):
    window_closed = Signal()

    def __init__(self, widget: Widget_Choice_Object[T], title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        set_window_title(self, title)

        self.widget: Widget_Choice_Object[T] = widget
        self.setCentralWidget(self.widget)
        self.size_window()

    def size_window(self) -> None:
        set_window_size(self, QSize(self.widget.table.maximumWidth() + 120, 0), factor_y=.8)

    def get_checked_uuids(self) -> set[tuple[str, str]]:
        return self.widget.checked_uuids

    def get_checked_objects(self) -> list[T]:
        return self.widget.get_checked_objects()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.window_closed.emit()
        super().closeEvent(event)


class Window_Choice_Players(Window_Choice_Objects[Player]):
    def __init__(
            self, title: str, excluded_uuids: set[tuple[str, str]] | None = None,
            checked_uuids: set[tuple[str, str]] | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(Widget_Choice_Players(excluded_uuids or set(), checked_uuids or set()), title, parent)


class Window_Choice_Teams(Window_Choice_Objects[Team]):
    def __init__(
            self, title: str, excluded_uuids: set[tuple[str, str]] | None = None,
            checked_uuids: set[tuple[str, str]] | None = None, parent: QWidget | None = None
    ) -> None:
        super().__init__(Widget_Choice_Teams(excluded_uuids or set(), checked_uuids or set()), title, parent)
