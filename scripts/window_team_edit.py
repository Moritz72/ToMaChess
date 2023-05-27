from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSignal
from .window_choice_table import Window_Choice_Table
from .window_team_remove_members import Window_Team_Remove_Members
from .window_team_line_up import Window_Line_Up
from .functions_player import load_players_list
from .functions_gui import get_button, add_widgets_to_layout


class Window_Team_Edit(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, team):
        super().__init__()
        self.setWindowTitle("Edit Team")
        self.team = team
        self.window_add_members, self.window_remove_members, self.window_line_up = None, None, None

        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.set_buttons()

    def set_buttons(self):
        add_widgets_to_layout(
            self.layout, (
                get_button("large", (12, 6), text="Add\nMembers", connect_function=self.open_window_add_members),
                get_button("large", (12, 6), text="Remove\nMembers", connect_function=self.open_window_remove_members),
                get_button("large", (12, 6), text="Change\nLineup", connect_function=self.open_window_line_up)
            )
        )

    def close_windows(self):
        for window in (self.window_add_members, self.window_remove_members, self.window_line_up):
            if window is not None:
                window.close()

    def open_window_add_members(self):
        self.close_windows()
        self.window_add_members = Window_Choice_Table(
            "Add Members", "Players",
            [(member.get_uuid(), member.get_uuid_associate()) for member in self.team.get_members()]
        )
        self.window_add_members.window_closed.connect(self.add_members)
        self.window_add_members.show()

    def open_window_remove_members(self):
        self.close_windows()
        self.window_remove_members = Window_Team_Remove_Members(self.team.get_members().copy())
        self.window_remove_members.window_closed.connect(self.remove_members)
        self.window_remove_members.show()

    def open_window_line_up(self):
        self.close_windows()
        self.window_line_up = Window_Line_Up(self.team)
        self.window_line_up.window_closed.connect(self.line_up)
        self.window_line_up.show()

    def add_members(self):
        self.team.add_members(sorted(
            load_players_list("", *self.window_add_members.get_checked_uuids()),
            key=lambda x: 0 if x.get_rating() is None else x.get_rating(), reverse=True
        ))
        self.window_add_members = None

    def remove_members(self):
        for member in self.window_remove_members.removed_members:
            self.team.remove_member(member)
            self.team.set_shallow_member_count(self.team.get_shallow_member_count() - 1)
        self.window_remove_members = None

    def line_up(self):
        members = self.team.get_members()
        self.team.set_members([members[i] for i in self.window_line_up.table.permutation])
        self.window_line_up = None

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
