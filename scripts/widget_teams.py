from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from .class_team import Team
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_team import load_teams_like_shallow, update_teams, remove_teams, add_teams, load_team
from .functions_gui import add_content_to_table, add_button_to_table, make_headers_bold_horizontal,\
    make_headers_bold_vertical, get_button
from .window_team_edit import Window_Team_Edit


class Widget_Teams(Widget_Default_Generic):
    def __init__(self):
        super().__init__("Teams", load_teams_like_shallow, update_teams, remove_teams, add_teams)
        self.window_team_edit = None

    @staticmethod
    def get_table():
        table = Table_Widget_Search(4, 3.5, 55, [None, 5, 9, 3.5])
        table.setHorizontalHeaderLabels(["Name", "Memb.", "", ""])
        make_headers_bold_horizontal(table)
        make_headers_bold_vertical(table)

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        add_button = get_button("large", (12, 5), "Add\nTeam", connect_function=self.add_new_row)
        save_button = get_button("large", (12, 5), "Save", connect_function=self.update_database)
        return add_button, save_button

    def get_object_from_values(self, values):
        return Team([], values[0], uuid_associate=self.collection_current.get_uuid())

    def edit_object_by_values(self, values, obj):
        obj.set_name(values[0])
        obj.set_uuid_associate(self.collection_current.get_uuid())

    def fill_in_row(self, row, obj=None):
        if obj is None:
            name = ""
            members = 0
        else:
            name = obj.get_name()
            members = obj.get_member_count()
        add_content_to_table(self.table, name, row, 0, bold=True)
        add_content_to_table(self.table, members, row, 1, edit=False, align=Qt.AlignCenter)
        if name:
            add_button_to_table(self.table, row, 2, "medium", None, "Edit", connect_function=self.edit_team, bold=True)
        else:
            add_content_to_table(self.table, "", row, 2, edit=False, align=Qt.AlignCenter)
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect_function=self.table.delete_current_row)

    def edit_team(self):
        row = self.table.currentRow()
        team = self.table.objects[row]
        if team.get_shallow_member_count() is not None:
            self.table.objects[row] = load_team("", team.get_uuid(), team.get_uuid_associate())
        self.table.mark_object_as_updated(row)
        self.window_team_edit = Window_Team_Edit(self.table.objects[row])
        self.window_team_edit.show()
