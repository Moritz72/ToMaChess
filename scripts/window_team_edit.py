from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from .window_add_players import Window_Add_Players
from .window_team_remove_members import Window_Team_Remove_Members
from .window_team_line_up import Window_Line_Up
from .functions_player import load_players_all
from .functions_gui import get_button, add_widgets_to_layout


class Window_Team_Edit(QMainWindow):
    window_closed = pyqtSignal()

    def __init__(self, team):
        super().__init__()
        self.setWindowTitle("Edit Team")
        self.team = team
        self.players = load_players_all()
        self.window_add_members = None
        self.window_remove_members = None
        self.window_line_up = None

        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.set_buttons()

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def set_buttons(self):
        button_add_members = get_button(
            "large", (12, 6), text="Add\nMembers", connect_function=self.open_window_add_members
        )
        button_remove_members = get_button(
            "large", (12, 6), text="Remove\nMembers", connect_function=self.open_window_remove_members
        )
        button_line_up = get_button(
            "large", (12, 6), text="Change\nLineup", connect_function=self.open_window_line_up
        )
        add_widgets_to_layout(self.layout, (button_add_members, button_remove_members, button_line_up))

    def close_windows(self):
        for window in (self.window_add_members, self.window_remove_members, self.window_line_up):
            if window is not None:
                window.close()

    def open_window_add_members(self):
        self.close_windows()
        self.window_add_members = Window_Add_Players(
            [player for player in self.players if player not in self.team.get_members()]
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
        self.team.add_members([
            self.players[row] for row in range(self.window_add_members.table.rowCount())
            if self.window_add_members.table.cellWidget(row, 3).checkState() == Qt.Checked
        ])
        self.window_add_members = None

    def remove_members(self):
        for member in self.window_remove_members.removed_members:
            self.team.remove_member(member)
        self.window_remove_members = None

    def line_up(self):
        members = self.team.get_members()
        self.team.set_members([members[i] for i in self.window_line_up.table.permutation])
        self.window_line_up = None

    def closeEvent(self, event):
        self.window_closed.emit()
        super().closeEvent(event)
