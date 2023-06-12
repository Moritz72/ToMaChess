from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_ms_tournament import load_ms_tournaments_shallow_like, update_ms_tournaments_shallow,\
    remove_ms_tournaments, add_ms_tournament, load_ms_tournament
from .functions_gui import add_content_to_table, add_button_to_table, get_button
from .window_ms_tournament_new import Window_MS_Tournament_New


class Widget_MS_Tournaments(Widget_Default_Generic):
    selected_tournament = pyqtSignal()

    def __init__(self):
        super().__init__(
            "Multi-Stage Tournaments",
            load_ms_tournaments_shallow_like, update_ms_tournaments_shallow, remove_ms_tournaments, None
        )
        self.new_tournament_window = None

    @staticmethod
    def get_table():
        table = Table_Widget_Search(4, 3.5, 55, [None, 5, 7, 3.5])
        table.setHorizontalHeaderLabels(["Name", "Part.", "", ""])

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)
        return table

    def get_buttons(self):
        add_button = get_button(
            "large", (12, 5), "Add\nTournament", connect_function=lambda: self.open_new_tournament_window({})
        )
        add_button_team = get_button(
            "large", (12, 5), "Add Team\nTournament",
            connect_function=lambda: self.open_new_tournament_window({"participant_type": "team"})
        )
        save_button = get_button("large", (12, 5), "Save", connect_function=self.update_database)
        return add_button, add_button_team, save_button

    def get_object_from_values(self, values):
        pass

    def edit_object_by_values(self, values, obj):
        obj.set_name(values[0])
        obj.set_uuid_associate(self.collection_current.get_uuid())

    def fill_in_row(self, row, obj=None):
        add_content_to_table(self.table, obj.get_name(), row, 0, bold=True)
        add_content_to_table(self.table, obj.get_participant_count(), row, 1, edit=False, align=Qt.AlignCenter)
        add_button_to_table(
            self.table, row, 2, "medium", None, "Open", connect_function=self.open_tournament, bold=True
        )
        add_button_to_table(self.table, row, 3, "medium", None, '-', connect_function=self.table.delete_current_row)

    def open_tournament(self):
        self.selected_tournament.emit()

    def open_new_tournament_window(self, args):
        if self.new_tournament_window is not None:
            self.new_tournament_window.close()
        self.new_tournament_window = Window_MS_Tournament_New(**args)
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def add_tournament(self):
        tournament = self.new_tournament_window.new_tournament
        tournament.set_uuid_associate(self.collection_current.get_uuid())
        add_ms_tournament("", tournament)
        self.fill_in_table()

    def get_current_tournament_loaded(self):
        tournament = self.table.objects[self.table.currentRow()]
        return load_ms_tournament("", tournament.get_uuid(), tournament.get_uuid_associate())
