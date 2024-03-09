from abc import abstractmethod
from typing import TypeVar, Generic, cast
from functools import partial
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QTableWidget, QVBoxLayout
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QCloseEvent
from .object import Object
from .player import Player
from .team import Team
from .db_object import DB_Object
from .gui_functions import get_button, set_window_title, set_window_size
from .gui_table import add_button_to_table, set_up_table, size_table
from .window_choice_objects import Window_Choice_Objects, Window_Choice_Players, Window_Choice_Teams

T = TypeVar('T', bound=Object)


class Window_Forbidden_Pairings_Objects(QMainWindow, Generic[T]):
    window_closed = Signal()

    def __init__(
            self, uuid_tuples: list[list[tuple[str, str]]], names: list[list[str]], parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        set_window_title(self, "Add Forbidden Pairings")

        self.uuid_tuples: list[list[tuple[str, str] | None]] = cast(list[list[tuple[str, str] | None]], uuid_tuples)
        self.names: list[list[str | None]] = cast(list[list[str | None]], names)
        self.choice_window: Window_Choice_Objects[T] | None = None
        self.choice_window_position: tuple[int, int] = (-1, 0)

        self.widget: QWidget = QWidget()
        self.layout_main: QHBoxLayout = QHBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.table: QTableWidget = QTableWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.table)
        self.layout_main.addLayout(layout)

        self.fill_in_table()
        self.add_row_button = get_button("large", (3, 3), '+', connect=self.add_new_row, translate=True)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.add_row_button)
        self.layout_main.addLayout(layout)
        set_window_size(self, QSize(self.table.maximumWidth() + self.add_row_button.width(), 0), factor_y=.4)

    def get_pairings(self) -> list[tuple[str, str]]:
        return [
            (tuples[0][0], tuples[1][0]) for tuples in self.uuid_tuples
            if tuples[0] is not None and tuples[1] is not None and tuples[0] != tuples[1]
        ]

    def resize_table(self) -> None:
        size_table(
            self.table, rows=len(self.uuid_tuples), row_height=3.5, max_width=37.5, widths=[17, 17, 3.5],
            header_width=0, stretches_h=[0, 1]
        )

    def add_pairing_row(self, row: int) -> None:
        name_1, name_2 = self.names[row][0] or "", self.names[row][1] or ""
        add_button_to_table(
            self.table, row, 0, "medium", None, name_1, connect=partial(self.open_choice_window, 0), align="left"
        )
        add_button_to_table(
            self.table, row, 1, "medium", None, name_2, connect=partial(self.open_choice_window, 1), align="left"
        )
        add_button_to_table(self.table, row, 2, "medium", None, '-', connect=self.remove_row)
        self.resize_table()

    def fill_in_table(self) -> None:
        set_up_table(self.table, 0, 3, header_horizontal=["Participant", "Participant", ""], translate=True)
        self.resize_table()
        for row in range(len(self.uuid_tuples)):
            self.add_pairing_row(row)

    def add_new_row(self) -> None:
        row = self.table.rowCount()
        self.uuid_tuples.append([None, None])
        self.names.append([None, None])
        self.table.insertRow(row)
        self.add_pairing_row(row)

    def open_choice_window(self, i: int) -> None:
        row = self.table.currentRow()
        if self.choice_window is not None:
            self.choice_window.close()
        self.choice_window = self.get_choice_window(row, i)
        self.choice_window_position = (row, i)
        self.choice_window.window_closed.connect(self.edit_pairings)
        self.choice_window.show()

    def edit_pairings(self) -> None:
        assert(self.choice_window is not None)
        objs = self.choice_window.get_checked_objects()
        row, i = self.choice_window_position
        if len(objs) == 0:
            self.uuid_tuples[row][i] = None
            self.names[row][i] = None
        else:
            self.uuid_tuples[row][i] = objs[0].get_uuid_tuple()
            self.names[row][i] = objs[0].get_name()
        self.add_pairing_row(row)
        self.choice_window_position = (-1, 0)

    def remove_row(self) -> None:
        row = self.table.currentRow()
        if row == self.choice_window_position[0]:
            return
        if row < self.choice_window_position[0]:
            self.choice_window_position = (self.choice_window_position[0] - 1, self.choice_window_position[1])
        self.uuid_tuples.pop(row)
        self.names.pop(row)
        self.table.removeRow(row)
        self.resize_table()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.window_closed.emit()
        super().closeEvent(event)

    @abstractmethod
    def get_choice_window(self, row: int, i: int) -> Window_Choice_Objects[T]:
        pass


class Window_Forbidden_Pairings_Players(Window_Forbidden_Pairings_Objects[Player]):
    def __init__(
            self, uuid_tuples: list[list[tuple[str, str]]], names: list[list[str]], db: DB_Object[Player],
            table_root: str = "", associates: list[tuple[str, str]] | None = None, parent: QWidget | None = None
    ) -> None:
        self.table_root: str = table_root
        self.associates: list[tuple[str, str]] | None = associates
        self.db: DB_Object[Player] = db
        super().__init__(uuid_tuples, names, parent=parent)

    def get_choice_window(self, row: int, i: int) -> Window_Choice_Objects[Player]:
        uuid_tuple = self.uuid_tuples[row][i]
        return Window_Choice_Players(
            "Choose Participant", checked_uuids=set() if uuid_tuple is None else {uuid_tuple},
            table_root=self.table_root, associates=self.associates, db=self.db, only_one=True, parent=self
        )


class Window_Forbidden_Pairings_Teams(Window_Forbidden_Pairings_Objects[Team]):
    def __init__(
            self, uuid_tuples: list[list[tuple[str, str]]], names: list[list[str]], db: DB_Object[Team],
            table_root: str = "", associates: list[tuple[str, str]] | None = None, parent: QWidget | None = None
    ) -> None:
        self.table_root: str = table_root
        self.associates: list[tuple[str, str]] | None = associates
        self.db: DB_Object[Team] = db
        super().__init__(uuid_tuples, names, parent=parent)

    def get_choice_window(self, row: int, i: int) -> Window_Choice_Objects[Team]:
        uuid_tuple = self.uuid_tuples[row][i]
        return Window_Choice_Teams(
            "Choose Participant", checked_uuids=set() if uuid_tuple is None else {uuid_tuple},
            table_root=self.table_root, associates=self.associates, db=self.db, only_one=True, parent=self
        )
