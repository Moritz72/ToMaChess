from PyQt5.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from .table_widget_drag import Table_Widget_Drag_Light
from .window_tournament_new import Window_Tournament_New
from .window_choice_table import Window_Choice_Table
from .window_advance_players import Window_Advance_Players
from .functions_player import load_players_list
from .functions_gui import add_content_to_table, add_button_to_table, size_table, make_headers_bold_vertical,\
    make_headers_bold_horizontal, get_button, add_widgets_in_layout


class Widget_MS_Tournament_Stage_New(QWidget):
    update_necessary = pyqtSignal()

    def __init__(self, stage, parent_window):
        super().__init__()
        self.stage = stage
        self.parent_window = parent_window

        self.tournaments = []
        self.advance_lists = []
        self.new_tournament_window = None
        self.add_players_window = None
        self.add_players_tournament = None
        self.advance_players_window = None
        self.advance_players_tournament = None

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QWidget())
        self.table = Table_Widget_Drag_Light(self.swap_table)
        self.fill_in_table()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.table)
        self.layout.addLayout(layout)
        self.set_buttons()

    def add_tournament_row(self, row, name, mode, participants):
        add_content_to_table(self.table, name, row, 0, bold=True)
        add_content_to_table(self.table, mode, row, 1, edit=False)
        add_content_to_table(self.table, participants, row, 2, edit=False, align=Qt.AlignCenter)
        add_button_to_table(
            self.table, row, 3, "medium", None, "Part.",
            connect_function=self.open_add_players if self.stage == 0 else self.open_advance_players
        )
        add_button_to_table(self.table, row, 4, "medium", None, "Copy", connect_function=self.copy_tournament)
        add_button_to_table(self.table, row, 5, "medium", None, '-', connect_function=self.remove_tournament)

    def fill_in_table(self):
        size_table(self.table, len(self.tournaments), 6, 3.5, max_width=55, widths=[None, None, 5, 4, 4, 3.5])
        self.table.setHorizontalHeaderLabels(["Name", "Mode", "Part.", "", "", ""])
        make_headers_bold_horizontal(self.table)
        make_headers_bold_vertical(self.table)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, tournament in enumerate(self.tournaments):
            self.add_tournament_row(
                i, tournament.get_name(), tournament.get_mode(),
                len(tournament.get_participants()) if self.stage == 0 else len(self.advance_lists[i])
            )

        self.table.itemChanged.connect(self.change_names)

    def set_buttons(self):
        add_button = get_button("large", (10, 5), "Add\nTournament", connect_function=self.open_new_tournament_window)
        layout_buttons = QVBoxLayout()
        layout_buttons.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        add_widgets_in_layout(self.layout, layout_buttons, (add_button,))

    def get_lower_tournaments(self):
        return self.parent_window.get_stage_widget(self.stage - 1).tournaments

    def get_lower_player_counts(self):
        return [len(advance_list) for advance_list in self.parent_window.get_stage_widget(self.stage - 1).advance_lists]

    def update_tournament_order(self):
        self.tournaments = [self.tournaments[i] for i in self.table.permutation]
        self.advance_lists = [self.advance_lists[i] for i in self.table.permutation]

    def change_names(self, item):
        column = item.column()
        if column == 0 and item.text():
            self.tournaments[item.row()].set_name(item.text())

    def swap_table(self):
        self.update_tournament_order()
        self.fill_in_table()

    def remove_tournament(self):
        row = self.table.currentRow()
        self.update_tournament_order()
        del self.tournaments[row]
        del self.advance_lists[row]
        self.update_necessary.emit()
        self.fill_in_table()

    def open_new_tournament_window(self):
        self.new_tournament_window = Window_Tournament_New(add_participants=False)
        self.new_tournament_window.added_tournament.connect(self.add_tournament)
        self.new_tournament_window.show()

    def copy_tournament(self):
        row = self.table.currentRow()
        self.update_tournament_order()
        new_tournament = self.tournaments[row].copy()
        new_tournament.reload_uuid()
        self.tournaments.insert(row + 1, new_tournament)
        self.advance_lists.insert(row + 1, self.advance_lists[row])
        self.fill_in_table()

    def add_tournament(self):
        row = self.table.rowCount()
        self.update_tournament_order()
        self.tournaments.append(self.new_tournament_window.new_tournament)
        self.advance_lists.append([])
        self.fill_in_table()

    def validate_advance_lists(self):
        lower_tournaments = self.get_lower_tournaments()
        lower_player_counts = self.get_lower_player_counts()
        unique_elements = []

        for i in range(len(self.advance_lists)):
            self.advance_lists[i] = [
                (tournament, placement) for tournament, placement in self.advance_lists[i]
                if tournament in lower_tournaments
                and placement <= lower_player_counts[lower_tournaments.index(tournament)]
            ]
            delete_later = []
            for j, (tournament, placement) in enumerate(self.advance_lists[i]):
                if (id(tournament), placement) in unique_elements:
                    delete_later.append(j)
                else:
                    unique_elements.append((id(tournament), placement))
            for index in delete_later[::-1]:
                self.advance_lists[i].pop(index)

        self.fill_in_table()

    def update_added_players(self):
        players = load_players_list("", *self.add_players_window.get_checked_uuids())
        self.add_players_tournament.set_participants(players)
        index = self.tournaments.index(self.add_players_tournament)
        self.advance_lists[index] = [(None, i + 1) for i in range(len(self.tournaments[index].get_participants()))]
        self.add_players_window = None
        self.add_players_tournament = None
        self.fill_in_table()
        self.update_necessary.emit()

    def open_add_players(self):
        row = self.table.currentRow()
        if self.add_players_window is not None:
            self.add_players_window.close()
        self.add_players_tournament = self.tournaments[row]
        self.add_players_window = Window_Choice_Table(
            "Add Players", "Players",
            checked_uuids=[
                (participant.get_uuid(), participant.get_uuid_associate())
                for participant in self.add_players_tournament.get_participants()
            ]
        )
        self.add_players_window.window_closed.connect(self.update_added_players)
        self.add_players_window.show()

    def update_advance_players(self):
        list_entries = [
            (
                self.advance_players_window.table.cellWidget(row, 0).currentData(),
                int(self.advance_players_window.table.cellWidget(row, 1).currentText())
            )
            for row in range(self.advance_players_window.table.rowCount())
        ]
        index = self.tournaments.index(self.advance_players_tournament)
        self.advance_lists[index] = list_entries
        self.advance_players_window = None
        self.advance_players_tournament = None
        self.fill_in_table()
        self.update_necessary.emit()

    def open_advance_players(self):
        row = self.table.currentRow()
        if self.advance_players_window is not None:
            self.advance_players_window.close()
        self.advance_players_tournament = self.tournaments[row]
        self.advance_players_window = Window_Advance_Players(
            self.advance_lists[row], self.get_lower_tournaments(), self.get_lower_player_counts()
        )
        self.advance_players_window.window_closed.connect(self.update_advance_players)
        self.advance_players_window.show()
