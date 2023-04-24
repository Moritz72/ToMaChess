from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_tournament import load_tournaments_all
from .functions_ms_tournament import load_ms_tournaments_all
from .functions_gui import add_widgets_in_layout, add_content_to_table, add_button_to_table, clear_table,\
    make_headers_bold_horizontal, make_headers_bold_vertical, get_button, size_table
from .window_tournament_new import Window_Tournament_New
from .window_ms_tournament_new import Window_MS_Tournament_New


class Widget_Tournaments(QWidget):
    selected_tournament = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.tournaments = sorted(load_tournaments_all()+load_ms_tournaments_all(), key=lambda x: x.get_name())
        self.new_tournament_window = None
        self.deleted_tournaments = []

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QWidget())
        self.table = QTableWidget()
        self.fill_in_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        add_widgets_in_layout(self.layout, layout, (self.table,))
        self.set_buttons()

    def add_tournament_row(self, row, name, mode, participants):
        add_content_to_table(self.table, name, row, 0, bold=True)
        add_content_to_table(self.table, mode, row, 1, edit=False)
        add_content_to_table(self.table, participants, row, 2, edit=False, align=Qt.AlignCenter)
        add_button_to_table(
            self.table, row, 3, "medium", None, "Open", connect_function=self.open_tournament, bold=True
        )
        add_button_to_table(self.table, row, 4, "medium", None, '-', connect_function=self.add_tournament_to_be_removed)

    def resize_table(self):
        size_table(self.table, len(self.tournaments), 5, 3.5, max_width=55, widths=[None, None, 5, 7, 3.5])

    def fill_in_table(self):
        self.resize_table()
        self.table.setHorizontalHeaderLabels(["Name", "Mode", "Part.", "", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, tournament in enumerate(self.tournaments):
            self.add_tournament_row(i, tournament.get_name(), tournament.get_mode(), len(tournament.get_participants()))

    def set_buttons(self):
        add_button = get_button("large", (10, 5), "Add\nTournament", connect_function=self.open_new_tournament_window)
        add_button_multi_stage = get_button(
            "large", (10, 7.5), "Add\nMulti Stage\nTournament",
            connect_function=self.open_new_tournament_window_multi_stage
        )
        save_button = get_button("large", (10, 5), "Save", connect_function=self.update_tournaments)
        layout_buttons = QVBoxLayout()
        layout_buttons.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        add_widgets_in_layout(self.layout, layout_buttons, (add_button, add_button_multi_stage, save_button))

    def add_tournament_to_be_removed(self):
        row = self.table.currentRow()
        if self.tournaments[row] is not None:
            self.deleted_tournaments.append(self.tournaments[row])
        del self.tournaments[row]
        self.table.removeRow(row)
        self.resize_table()

    def remove_tournaments(self):
        while self.deleted_tournaments:
            self.deleted_tournaments.pop().remove()

    def save_tournaments(self):
        for i, tournament in enumerate(self.tournaments):
            name = self.table.item(i, 0).text()
            if name == "":
                continue
            tournament.set_name(name)
            tournament.save()

    def open_tournament(self):
        self.selected_tournament.emit(self.table.currentRow())

    def open_new_tournament_window(self):
        if self.new_tournament_window is not None:
            self.new_tournament_window.close()
        self.new_tournament_window = Window_Tournament_New()
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def open_new_tournament_window_multi_stage(self):
        if self.new_tournament_window is not None:
            self.new_tournament_window.close()
        self.new_tournament_window = Window_MS_Tournament_New()
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def add_tournament(self):
        self.new_tournament_window.new_tournament.save()
        self.update_tournaments()

    def update_tournaments(self):
        self.save_tournaments()
        self.remove_tournaments()
        self.tournaments = sorted(load_tournaments_all()+load_ms_tournaments_all(), key=lambda x: x.get_name())
        clear_table(self.table)
        self.fill_in_table()
