from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton
from .widget_search_generic import Widget_Search_Generic
from ..common.gui_functions import close_window, get_button
from ..common.gui_table import add_button_to_table, add_content_to_table, add_team_to_table
from ..tables.table_objects import Table_Objects
from ..windows.window_team_edit import Window_Team_Edit
from ...database.db_team import DB_TEAM, TEAM_ATTRIBUTE_LIST
from ...team.team import Team


class Widget_Menu_Teams(Widget_Search_Generic[Team]):
    def __init__(self) -> None:
        super().__init__(DB_TEAM)
        self.window_team_edit: Window_Team_Edit | None = None

    def get_table(self) -> Table_Objects[Team]:
        return Table_Objects[Team](
            4, 3.5, 55, [None, 5, 9, 3.5], TEAM_ATTRIBUTE_LIST + ["", ""],
            stretches=[0], translate=True, parent=self
        )

    def get_buttons(self) -> list[QPushButton]:
        return [
            get_button("large", (14, 5), "Add\nTeam", connect=self.add_new_row, translate=True),
            get_button("large", (14, 5), "Save", connect=self.update_database, translate=True)
        ]

    def get_object_from_values(self, values: tuple[str, str, str, str]) -> Team:
        return Team([], values[0], uuid_associate=self.get_associate_uuid())

    def edit_object_by_values(self, values: tuple[str, str, str, str], team: Team) -> None:
        team.set_name(values[0])
        team.set_uuid_associate(self.get_associate_uuid())

    def fill_in_row(self, row: int, team: Team | None = None) -> None:
        add_team_to_table(self.table, row, team, edit=True)
        if team is None:
            add_content_to_table(self.table, "", row, 2, edit=False, align=Qt.AlignmentFlag.AlignCenter)
        else:
            add_button_to_table(
                self.table, row, 2, "medium", None, "Edit", connect=self.edit_team, bold=True, translate=True
            )
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect=self.table.delete_current_row)

    def edit_team(self) -> None:
        row = self.table.currentRow()
        team = self.table.objects[row]
        assert(team is not None)

        close_window(self.window_team_edit)
        team = self.table.objects[row]
        assert(team is not None)
        self.window_team_edit = Window_Team_Edit(team, parent=self)
        self.window_team_edit.show()
