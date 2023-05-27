from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from .table_widget_search import Table_Widget_Search
from .widget_default_generic import Widget_Default_Generic
from .functions_tournament import load_tournaments_like_shallow, update_tournaments_shallow, remove_tournaments,\
    add_tournament, load_tournament
from .functions_gui import add_content_to_table, add_button_to_table, make_headers_bold_horizontal,\
    make_headers_bold_vertical, get_button
from .window_tournament_new import Window_Tournament_New


class Widget_Tournaments(Widget_Default_Generic):
    selected_tournament = pyqtSignal()

    def __init__(self):
        super().__init__(
            "Tournaments",
            load_tournaments_like_shallow, update_tournaments_shallow, remove_tournaments, None
        )
        self.new_tournament_window = None

    @staticmethod
    def get_table():
        table = Table_Widget_Search(5, 3.5, 55, [None, None, 5, 7, 3.5])
        table.setHorizontalHeaderLabels(["Name", "Mode", "Part.", "", ""])
        make_headers_bold_horizontal(table)
        make_headers_bold_vertical(table)

        header_horizontal, header_vertical = table.horizontalHeader(), table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
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
        add_content_to_table(self.table, obj.get_mode(), row, 1, edit=False)
        add_content_to_table(self.table, obj.get_participant_count(), row, 2, edit=False, align=Qt.AlignCenter)
        add_button_to_table(
            self.table, row, 3, "medium", None, "Open", connect_function=self.open_tournament, bold=True
        )
        add_button_to_table(self.table, row, 4, "medium", None, '-', connect_function=self.table.delete_current_row)

    def open_tournament(self):
        self.selected_tournament.emit()

    def open_new_tournament_window(self, args):
        if self.new_tournament_window is not None:
            self.new_tournament_window.close()
        self.new_tournament_window = Window_Tournament_New(**args)
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def add_tournament(self):
        tournament = self.new_tournament_window.new_tournament
        tournament.set_uuid_associate(self.collection_current.get_uuid())
        add_tournament("", tournament)
        self.fill_in_table()

    def get_current_tournament_loaded(self):
        tournament = self.table.objects[self.table.currentRow()]
        return load_tournament("", tournament.get_uuid(), tournament.get_uuid_associate())
