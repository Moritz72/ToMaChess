from typing import cast
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal
from .tournament import Tournament
from .table_objects import Table_Objects
from .widget_search_generic import Widget_Search_Generic
from .window_tournament_new import Window_Tournament_New_Player, Window_Tournament_New_Team
from .db_tournament import DB_TOURNAMENT, TOURNAMENT_ATTRIBUTE_LIST
from .gui_functions import get_button, close_window
from .gui_table import add_button_to_table, add_tournament_to_table


class Widget_Menu_Tournaments(Widget_Search_Generic[Tournament]):
    selected_tournament = Signal()

    def __init__(self) -> None:
        super().__init__(DB_TOURNAMENT, shallow_load=True, shallow_update=True)
        self.new_tournament_window: Window_Tournament_New_Player | Window_Tournament_New_Team | None = None

    def get_table(self) -> Table_Objects[Tournament]:
        return Table_Objects[Tournament](
            5, 3.5, 55, [None, None, 5, 7, 3.5], TOURNAMENT_ATTRIBUTE_LIST + ["", ""],
            stretches=[0, 1], translate=True, parent=self
        )

    def get_buttons(self) -> list[QPushButton]:
        return [
            get_button("large", (14, 5), "Add\nTournament", connect=self.open_new_tournament, translate=True),
            get_button("large", (14, 5), "Add Team\nTournament", connect=self.open_new_tournament_team, translate=True),
            get_button("large", (14, 5), "Save", connect=self.update_database, translate=True)
        ]

    def get_object_from_values(self, values: tuple[str, str, str, str, str]) -> Tournament:
        return NotImplemented

    def edit_object_by_values(self, values: tuple[str, str, str, str, str], tournament: Tournament) -> None:
        tournament.set_name(values[0])
        tournament.set_uuid_associate(self.get_associate_uuid())

    def fill_in_row(self, row: int, tournament: Tournament | None = None) -> None:
        add_tournament_to_table(self.table, row, tournament, edit=True)
        add_button_to_table(
            self.table, row, 3, "medium", None, "Open", connect=self.open_tournament, bold=True, translate=True
        )
        add_button_to_table(self.table, row, 4, "medium", None, '-', connect=self.table.delete_current_row)

    def open_tournament(self) -> None:
        self.selected_tournament.emit()

    def open_new_tournament(self) -> None:
        self.open_window(Window_Tournament_New_Player)

    def open_new_tournament_team(self) -> None:
        self.open_window(Window_Tournament_New_Team)

    def open_window(self, window_type: type[Window_Tournament_New_Player | Window_Tournament_New_Team]) -> None:
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

    def get_current_tournament_loaded(self) -> Tournament:
        tournament = cast(Tournament, self.table.objects[self.table.currentRow()])
        return self.db.load_list("", [tournament.get_uuid()], [tournament.get_uuid_associate()])[0]
