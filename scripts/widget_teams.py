from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidget
from PyQt5.QtCore import Qt
from .class_team import Team
from .functions_team import load_teams_all
from .functions_gui import add_widgets_in_layout, add_content_to_table, add_button_to_table, clear_table,\
    make_headers_bold_horizontal, make_headers_bold_vertical, get_button, size_table
from .window_team_edit import Window_Team_Edit


class Widget_Teams(QWidget):
    def __init__(self):
        super().__init__()
        self.teams = load_teams_all()
        self.new_team_window = None
        self.window_team_edit = None
        self.deleted_teams = []

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QWidget())
        self.table = QTableWidget()
        self.fill_in_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        add_widgets_in_layout(self.layout, layout, (self.table,))
        self.set_buttons()

    def add_team_row(self, row, name, members):
        add_content_to_table(self.table, name, row, 0, bold=True)
        add_content_to_table(self.table, members, row, 1, edit=False, align=Qt.AlignCenter)
        add_button_to_table(self.table, row, 2, "medium", None, "Edit", connect_function=self.edit_team, bold=True)
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect_function=self.add_team_to_be_removed)

    def resize_table(self):
        size_table(self.table, len(self.teams), 4, 3.5, max_width=55, widths=[None, 5, 9, 3.5])

    def fill_in_table(self):
        self.resize_table()
        self.table.setHorizontalHeaderLabels(["Name", "Memb.", "", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header = self.table.verticalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

        for i, team in enumerate(self.teams):
            self.add_team_row(i, team.get_name(), len(team.get_members()))

    def set_buttons(self):
        add_button = get_button("large", (12, 5), "Add\nTeam", connect_function=self.add_new_team_row)
        save_button = get_button("large", (12, 5), "Save", connect_function=self.update_teams)
        layout_buttons = QVBoxLayout()
        layout_buttons.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        add_widgets_in_layout(self.layout, layout_buttons, (add_button, save_button))

    def add_new_team_row(self):
        self.teams.append(Team(""))
        self.fill_in_table()

    def add_team_to_be_removed(self):
        row = self.table.currentRow()
        if self.teams[row].is_valid():
            self.deleted_teams.append(self.teams[row])
        del self.teams[row]
        self.table.removeRow(row)
        self.resize_table()

    def remove_teams(self):
        while self.deleted_teams:
            self.deleted_teams.pop().remove()

    def get_table_text(self, row, column):
        if self.table.item(row, column) is None:
            return ""
        return self.table.item(row, column).text()

    def save_teams(self):
        for i, team in enumerate(self.teams):
            team.set_name(self.get_table_text(i, 0))

            if team.is_valid():
                team.save()

    def edit_team(self):
        row = self.table.currentRow()
        self.window_team_edit = Window_Team_Edit(self.teams[row])
        self.window_team_edit.window_closed.connect(self.update_teams_no_reload)
        self.window_team_edit.show()

    def update_teams_no_reload(self):
        clear_table(self.table)
        self.fill_in_table()

    def update_teams(self):
        self.save_teams()
        self.remove_teams()
        self.teams = load_teams_all()
        self.update_teams_no_reload()
