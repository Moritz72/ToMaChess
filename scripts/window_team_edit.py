from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from .window_choice_table import Window_Choice_Table
from .window_remove_table import Window_Remove_Table
from .window_team_line_up import Window_Line_Up
from .functions_player import load_players_list, sort_players_by_rating
from .functions_gui import get_button, set_window_title, set_window_size, close_window


class Window_Team_Edit(QMainWindow):
    window_closed = Signal()

    def __init__(self, team, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        set_window_title(self, "Edit Team")

        self.team = team
        self.child_window = None

        self.widget = QWidget()
        self.layout = QHBoxLayout(self.widget)
        self.setCentralWidget(self.widget)

        self.set_buttons()
        set_window_size(self, self.sizeHint())

    def set_buttons(self):
        self.layout.addWidget(get_button(
            "large", (12, 6), "Add\nMembers", connect_function=self.open_window_add_members, translate=True
        ))
        self.layout.addWidget(get_button(
            "large", (12, 6), "Remove\nMembers", connect_function=self.open_window_remove_members, translate=True
        ))
        self.layout.addWidget(get_button(
            "large", (12, 6), "Change\nLineup", connect_function=self.open_window_line_up, translate=True
        ))

    def set_child_window(self, window):
        self.child_window = window
        self.child_window.show()

    def open_window_add_members(self):
        close_window(self.child_window)
        self.set_child_window(Window_Choice_Table(
            "Add Members", "player", {member.get_uuid() for member in self.team.get_members()}, parent=self
        ))
        self.child_window.window_closed.connect(self.add_members)

    def open_window_remove_members(self):
        close_window(self.child_window)
        self.set_child_window(
            Window_Remove_Table("Remove Members", "player", self.team.get_members().copy(), parent=self)
        )
        self.child_window.window_closed.connect(self.remove_members)

    def open_window_line_up(self):
        close_window(self.child_window)
        self.set_child_window(Window_Line_Up(self.team, parent=self))
        self.child_window.window_closed.connect(self.line_up)

    def add_members(self):
        self.team.add_members(sort_players_by_rating(load_players_list("", self.child_window.get_checked_uuids())))

    def remove_members(self):
        removed_members = self.child_window.get_removed_objects()
        self.team.remove_members_by_uuid([member.get_uuid() for member in removed_members])
        if self.team.get_shallow_member_count() is not None:
            self.team.set_shallow_member_count(self.team.get_shallow_member_count() - len(removed_members))

    def line_up(self):
        members = self.team.get_members()
        self.team.set_members([members[i] for i in self.child_window.get_permutation()])

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
