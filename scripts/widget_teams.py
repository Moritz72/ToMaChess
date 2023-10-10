from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt
from .class_team import Team
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_team import load_teams_shallow_like, update_teams, remove_teams, add_teams, load_team, \
    TEAM_ATTRIBUTE_LIST
from .functions_gui import add_content_to_table, add_button_to_table, get_button, add_team_to_table, close_window
from .window_team_edit import Window_Team_Edit


class Widget_Teams(Widget_Default_Generic):
    def __init__(self):
        super().__init__("Teams", load_teams_shallow_like, update_teams, remove_teams, add_teams)
        self.window_team_edit = None

    @staticmethod
    def get_table():
        table = Table_Widget_Search(4, 3.5, 55, [None, 5, 9, 3.5], TEAM_ATTRIBUTE_LIST + ["", ""], translate=True)

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        add_button = get_button("large", (14, 5), "Add\nTeam", connect_function=self.add_new_row, translate=True)
        save_button = get_button("large", (14, 5), "Save", connect_function=self.update_database, translate=True)
        return add_button, save_button

    def get_object_from_values(self, values):
        return Team([], values[0], uuid_associate=self.collection_current.get_uuid())

    def edit_object_by_values(self, values, obj):
        obj.set_name(values[0])
        obj.set_uuid_associate(self.collection_current.get_uuid())

    def fill_in_row(self, row, obj=None):
        add_team_to_table(self.table, row, obj, edit=True)
        if obj is None:
            add_content_to_table(self.table, "", row, 2, edit=False, align=Qt.AlignCenter)
        else:
            add_button_to_table(
                self.table, row, 2, "medium", None, "Edit", connect_function=self.edit_team, bold=True, translate=True
            )
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect_function=self.table.delete_current_row)

    def edit_team(self):
        row = self.table.currentRow()
        team = self.table.objects[row]
        if team.get_shallow_member_count() is not None:
            self.table.objects[row] = load_team("", team.get_uuid(), team.get_uuid_associate())
        self.table.mark_object_as_updated(row)

        close_window(self.window_team_edit)
        self.window_team_edit = Window_Team_Edit(self.table.objects[row], parent=self)
        self.window_team_edit.show()
