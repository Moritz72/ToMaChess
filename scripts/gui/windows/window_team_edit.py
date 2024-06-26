from dataclasses import dataclass, fields
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QWidget
from .window_choice_objects import Window_Choice_Players
from .window_drag_objects import Window_Drag_Players
from .window_remove_objects import Window_Remove_Players
from ..common.gui_functions import close_window, get_button, set_window_size, set_window_title
from ...database.db_player import sort_players_swiss
from ...team.team import Team


@dataclass
class Windows:
    add: Window_Choice_Players | None = None
    remove: Window_Remove_Players | None = None
    lineup: Window_Drag_Players | None = None


class Window_Team_Edit(QMainWindow):
    window_closed = Signal()

    def __init__(self, team: Team, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        set_window_title(self, "Edit Team")

        self.team: Team = team
        self.windows: Windows = Windows()

        self.widget = QWidget()
        self.layout_main: QHBoxLayout = QHBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.set_buttons()
        set_window_size(self, self.sizeHint())

    def set_buttons(self) -> None:
        self.layout_main.addWidget(get_button(
            "large", (12, 6), "Add\nMembers", connect=self.open_window_add_members, translate=True
        ))
        self.layout_main.addWidget(get_button(
            "large", (12, 6), "Remove\nMembers", connect=self.open_window_remove_members, translate=True
        ))
        self.layout_main.addWidget(get_button(
            "large", (12, 6), "Change\nLineup", connect=self.open_window_line_up, translate=True
        ))

    def close_windows(self) -> None:
        for field in fields(self.windows):
            close_window(getattr(self.windows, field.name))
        self.windows = Windows()

    def open_window_add_members(self) -> None:
        self.close_windows()
        tuples = {member.get_uuid_tuple() for member in self.team.get_members()}
        self.windows.add = Window_Choice_Players("Add Members", tuples, parent=self)
        self.windows.add.window_closed.connect(self.add_members)
        self.windows.add.show()

    def open_window_remove_members(self) -> None:
        self.close_windows()
        self.windows.remove = Window_Remove_Players("Remove Members", self.team.get_members().copy(), parent=self)
        self.windows.remove.window_closed.connect(self.remove_members)
        self.windows.remove.show()

    def open_window_line_up(self) -> None:
        self.close_windows()
        self.windows.lineup = Window_Drag_Players(self.team.get_members(), "Change Lineup", parent=self)
        self.windows.lineup.window_closed.connect(self.line_up)
        self.windows.lineup.show()

    def add_members(self) -> None:
        assert(self.windows.add is not None)
        self.team.add_members(sort_players_swiss(self.windows.add.get_checked_objects()))

    def remove_members(self) -> None:
        assert(self.windows.remove is not None)
        removed_members = self.windows.remove.get_removed_objects()
        self.team.remove_members_by_uuid([member.get_uuid() for member in removed_members])

    def line_up(self) -> None:
        assert(self.windows.lineup is not None)
        self.team.set_members(self.windows.lineup.get_objects())

    def closeEvent(self, event: QCloseEvent) -> None:
        self.window_closed.emit()
        super().closeEvent(event)
