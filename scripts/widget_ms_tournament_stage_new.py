from PyQt5.QtWidgets import QWidget, QHBoxLayout, QHeaderView, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from .table_widget_drag import Table_Widget_Drag_Light
from .window_tournament_new import Window_Tournament_New
from .window_choice_table import Window_Choice_Table
from .window_advance_participants import Window_Advance_Participants
from .functions_type import type_to_add_participant_window_args, get_function
from .functions_gui import add_content_to_table, add_button_to_table, set_up_table, size_table, get_button,\
    add_widgets_in_layout


class Widget_MS_Tournament_Stage_New(QWidget):
    update_necessary = pyqtSignal()

    def __init__(self, stage, parent_window, participant_type="player"):
        super().__init__()
        self.stage = stage
        self.parent_window = parent_window
        self.participant_type = participant_type

        self.load_function = get_function(participant_type, "load", multiple=True, specification="list")
        self.tournaments = []
        self.advance_lists = []
        self.new_tournament_window = None
        self.add_participants_window, self.add_particiapants_tournament = None, None
        self.advance_participants_window, self.advance_participants_tournament = None, None

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
            self.table, row, 3, "medium", None, "Participants",
            connect_function=self.open_add_participants if self.stage == 0 else self.open_advance_participants,
            translate=True
        )
        add_button_to_table(
            self.table, row, 4, "medium", None, "Copy", connect_function=self.copy_tournament, translate=True
        )
        add_button_to_table(
            self.table, row, 5, "medium", None, '-', connect_function=self.remove_tournament, translate=True
        )

    def fill_in_table(self):
        set_up_table(self.table, 0, 6, header_horizontal=["Name", "Mode", "Participants", "", "", ""], translate=True)
        size_table(self.table, len(self.tournaments), 3.5, max_width=55, widths=[None, None, 5, 8, 8, 3.5])

        header_horizontal, header_vertical = self.table.horizontalHeader(), self.table.verticalHeader()
        header_horizontal.setSectionResizeMode(0, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, tournament in enumerate(self.tournaments):
            self.add_tournament_row(
                i, tournament.get_name(), tournament.get_mode(),
                len(tournament.get_participants()) if self.stage == 0 else len(self.advance_lists[i])
            )

        self.table.itemChanged.connect(self.change_names)

    def set_buttons(self):
        add_button = get_button(
            "large", (10, 5), "Add\nTournament", connect_function=self.open_new_tournament_window, translate=True
        )
        layout_buttons = QVBoxLayout()
        layout_buttons.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        add_widgets_in_layout(self.layout, layout_buttons, (add_button,))

    def get_lower_tournaments(self):
        return self.parent_window.get_stage_widget(self.stage - 1).tournaments

    def get_lower_participant_counts(self):
        return [len(advance_list) for advance_list in self.parent_window.get_stage_widget(self.stage - 1).advance_lists]

    def update_tournament_order(self):
        self.tournaments = [self.tournaments[i] for i in self.table.permutation]
        self.advance_lists = [self.advance_lists[i] for i in self.table.permutation]

    def change_names(self, item):
        if item.column() == 0 and item.text():
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
        self.new_tournament_window = Window_Tournament_New(
            participant_type=self.participant_type, add_participants=False
        )
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
        lower_participant_counts = self.get_lower_participant_counts()

        for i in range(len(self.advance_lists)):
            self.advance_lists[i] = [
                (tournament, placement) for tournament, placement in self.advance_lists[i]
                if tournament in lower_tournaments
                and placement <= lower_participant_counts[lower_tournaments.index(tournament)]
            ]
            self.advance_lists[i] = list({entry: None for entry in self.advance_lists[i]}.keys())

        self.fill_in_table()

    def update_added_participants(self):
        participants = self.load_function("", *self.add_participants_window.get_checked_uuids())
        self.add_particiapants_tournament.set_participants(participants)
        index = self.tournaments.index(self.add_particiapants_tournament)
        self.advance_lists[index] = [(None, i + 1) for i in range(len(self.tournaments[index].get_participants()))]

        self.add_participants_window, self.add_particiapants_tournament = None, None
        self.fill_in_table()
        self.update_necessary.emit()

    def open_add_participants(self):
        row = self.table.currentRow()
        if self.add_participants_window is not None:
            self.add_participants_window.close()
        self.add_particiapants_tournament = self.tournaments[row]
        checked_uuids = [
            (participant.get_uuid(), participant.get_uuid_associate())
            for participant in self.add_particiapants_tournament.get_participants()
        ]
        self.add_participants_window = Window_Choice_Table(
            *type_to_add_participant_window_args[self.participant_type], checked_uuids=checked_uuids
        )
        self.add_participants_window.window_closed.connect(self.update_added_participants)
        self.add_participants_window.show()

    def update_advance_participants(self):
        list_entries = [
            (
                self.advance_participants_window.table.cellWidget(row, 0).currentData(),
                int(self.advance_participants_window.table.cellWidget(row, 1).currentText())
            )
            for row in range(self.advance_participants_window.table.rowCount())
        ]
        index = self.tournaments.index(self.advance_participants_tournament)
        self.advance_lists[index] = list_entries

        self.advance_participants_window, self.advance_participants_tournament = None, None
        self.fill_in_table()
        self.update_necessary.emit()

    def open_advance_participants(self):
        row = self.table.currentRow()
        if self.advance_participants_window is not None:
            self.advance_participants_window.close()
        self.advance_participants_tournament = self.tournaments[row]
        self.advance_participants_window = Window_Advance_Participants(
            self.advance_lists[row], self.get_lower_tournaments(), self.get_lower_participant_counts()
        )
        self.advance_participants_window.window_closed.connect(self.update_advance_participants)
        self.advance_participants_window.show()
