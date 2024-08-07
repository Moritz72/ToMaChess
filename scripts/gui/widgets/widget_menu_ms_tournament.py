from typing import Type, cast
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton
from .widget_search_generic import Widget_Search_Generic
from ..common.gui_functions import close_window, get_button
from ..common.gui_table import add_button_to_table, add_ms_tournament_to_table
from ..tables.table_objects import Table_Objects
from ..windows.window_ms_tournament_new import Window_MS_Tournament_New_Player, Window_MS_Tournament_New_Team
from ...database.db_ms_tournament import DB_MS_TOURNAMENT, MS_TOURNAMENT_ATTRIBUTE_STRING
from ...ms_tournament.ms_tournament import MS_Tournament


class Widget_Menu_MS_Tournament(Widget_Search_Generic[MS_Tournament]):
    selected_tournament = Signal()

    def __init__(self) -> None:
        super().__init__(DB_MS_TOURNAMENT, shallow_load=True, shallow_update=True)
        self.new_tournament_window: Window_MS_Tournament_New_Player | Window_MS_Tournament_New_Team | None = None

    def get_table(self) -> Table_Objects[MS_Tournament]:
        return Table_Objects[MS_Tournament](
            4, 3.5, 55, [None, 5, 7, 3.5], MS_TOURNAMENT_ATTRIBUTE_STRING + ["", ""],
            stretches=[0], translate=True, parent=self
        )

    def get_buttons(self) -> list[QPushButton]:
        return [
            get_button("large", (14, 5), "Add\nTournament", connect=self.open_new_tournament, translate=True),
            get_button("large", (14, 5), "Add Team\nTournament", connect=self.open_new_tournament_team, translate=True),
            get_button("large", (14, 5), "Save", connect=self.update_database, translate=True)
        ]

    def get_object_from_values(self, values: tuple[str, str, str, str]) -> MS_Tournament:
        return NotImplemented

    def edit_object_by_values(self, values: tuple[str, str, str, str], ms_tournament: MS_Tournament) -> None:
        ms_tournament.set_name(values[0])
        ms_tournament.set_uuid_associate(self.get_associate_uuid())

    def fill_in_row(self, row: int, ms_tournament: MS_Tournament | None = None) -> None:
        add_ms_tournament_to_table(self.table, row, ms_tournament, edit=True)
        add_button_to_table(
            self.table, row, 2, "medium", None, "Open", connect=self.open_tournament, bold=True, translate=True
        )
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect=self.table.delete_current_row)

    def open_tournament(self) -> None:
        self.selected_tournament.emit()

    def open_new_tournament(self) -> None:
        self.open_window(Window_MS_Tournament_New_Player)

    def open_new_tournament_team(self) -> None:
        self.open_window(Window_MS_Tournament_New_Team)

    def open_window(self, window_type: Type[Window_MS_Tournament_New_Player | Window_MS_Tournament_New_Team]) -> None:
        close_window(self.new_tournament_window)
        self.new_tournament_window = window_type(parent=self)
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def add_tournament(self) -> None:
        if self.new_tournament_window is None or self.new_tournament_window.new_tournament is None:
            return
        tournament = self.new_tournament_window.new_tournament
        tournament.set_uuid_associate(self.get_associate_uuid())
        self.db.add_list("", [tournament])
        self.fill_in_table()

    def get_current_tournament_loaded(self) -> MS_Tournament:
        tournament = cast(MS_Tournament, self.table.objects[self.table.currentRow()])
        return self.db.load_list("", [tournament.get_uuid()], [tournament.get_uuid_associate()])[0]
