from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QComboBox, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_gui import add_content_to_table, add_button_to_table, add_combobox_to_table, clear_table,\
    make_headers_bold_horizontal, size_table


class Widget_Tournament_Round(QWidget):
    confirmed_round = pyqtSignal()

    def __init__(self, tournament, round_number):
        super().__init__()
        self.tournament = tournament
        self.round_number = round_number
        self.participants = self.tournament.get_participants()
        self.uuid_to_participant_dict = self.tournament.get_uuid_to_participant_dict() | {None: None}
        self.current = self.is_current()
        self.results = self.get_results()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout.addWidget(self.table)

    def is_current(self):
        return self.round_number == self.tournament.get_round()

    def get_results(self):
        if self.current:
            return [((uuid_1, None), (uuid_2, None)) for uuid_1, uuid_2 in self.tournament.get_pairings()]
        return self.tournament.get_results()[self.round_number-1]

    def add_pairing_row_participant(self, row, column, participant):
        if len(participant) == 1:
            add_content_to_table(
                self.table, participant[0], row, column, edit=False, align=Qt.AlignVCenter | Qt.AlignLeft
            )
        else:
            add_combobox_to_table(self.table, ["Choose..."] + list(participant), row, column, "medium", None)

    def add_pairing_row_result(self, row, column, score_1, score_2, choose_pairing):
        if score_1 is not None and score_2 is not None:
            add_content_to_table(
                self.table, f"{score_1}:{score_2}", row, column, edit=False, align=Qt.AlignCenter, bold=True
            )
        elif choose_pairing:
            add_content_to_table(self.table, f":", row, column, edit=False, align=Qt.AlignCenter, bold=True)
        else:
            add_combobox_to_table(
                self.table, [" : "] + [":".join(score) for score in self.tournament.get_possible_scores()],
                row, column, "medium", None
            )

    def add_pairing_row(self, row, participant_1, participant_2, score_1=None, score_2=None):
        add_content_to_table(self.table, row+1, row, 0, edit=False, bold=True, align=Qt.AlignCenter)
        self.add_pairing_row_participant(row, 1, participant_1)
        self.add_pairing_row_result(row, 2, score_1, score_2, len(participant_1+participant_2) > 2)
        self.add_pairing_row_participant(row, 3, participant_2)

    def add_last_row(self, choose_players):
        row = self.table.rowCount()-1
        add_content_to_table(self.table, '', row, 0, edit=False, color_bg=(200, 200, 200))
        add_content_to_table(self.table, '', row, 1, edit=False, color_bg=(200, 200, 200))
        add_content_to_table(self.table, '', row, 2, edit=False, color_bg=(200, 200, 200))
        if choose_players:
            add_button_to_table(
                self.table, row, 3, "medium", None, "Confirm Pairings", connect_function=self.confirm_pairings
            )
        else:
            add_button_to_table(
                self.table, row, 3, "medium", None, "Confirm Results", connect_function=self.confirm_results
            )

    def fill_in_table(self):
        size_table(self.table, len(self.results)+self.current, 4, 3.5, max_width=55, widths=[3.5, None, 7, None])
        self.table.setHorizontalHeaderLabels(["", "White", "", "Black"])
        make_headers_bold_horizontal(self.table)
        self.table.verticalHeader().setVisible(False)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(3, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        choose_pairing = self.fill_in_pairings()
        if self.current:
            self.add_last_row(choose_pairing)

    def fill_in_pairings(self):
        choose_pairing = False
        for i, ((uuid_1, score_1), (uuid_2, score_2)) in enumerate(self.results):
            if not isinstance(uuid_1, (list, tuple)):
                uuid_1 = [uuid_1]
            if not isinstance(uuid_2, (list, tuple)):
                uuid_2 = [uuid_2]
            participant_1 = [self.uuid_to_participant_dict[uuid] for uuid in uuid_1]
            participant_2 = [self.uuid_to_participant_dict[uuid] for uuid in uuid_2]
            if len(participant_1+participant_2) > 2:
                choose_pairing = True
            if participant_1 == [None] and participant_2 == [None]:
                score_1, score_2 = '-', '-'
            elif participant_1 == [None]:
                score_1, score_2 = '-', '+'
            elif participant_2 == [None]:
                score_1, score_2 = '+', '-'
            self.add_pairing_row(i, participant_1, participant_2, score_1, score_2)
        return choose_pairing

    def enter_participant_in_results(self, row, column):
        widget = self.table.cellWidget(row, column)
        if not isinstance(widget, QComboBox):
            return True
        if widget.currentText() == "Choose...":
            return False
        participant = widget.currentData()
        if column == 1:
            self.results[row] = (
                (None if participant is None else participant.get_uuid(), self.results[row][0][1]), self.results[row][1]
            )
            return True
        if column == 3:
            self.results[row] = (
                self.results[row][0], (None if participant is None else participant.get_uuid(), self.results[row][1][1])
            )
            return True

    def confirm_pairings(self):
        all_pairings_confirmed = all(
            self.enter_participant_in_results(row, column)
            for row in range(self.table.rowCount()-1) for column in (1, 3)
        )
        if all_pairings_confirmed and self.tournament.is_valid_pairings(self.results):
            self.update_table()

    def enter_score_in_results(self, row):
        if self.table.cellWidget(row, 2) is None:
            score_1, score_2 = self.table.item(row, 2).text().split(':')
        else:
            score_1, score_2 = self.table.cellWidget(row, 2).currentText().split(':')
        if score_1 == " " or score_2 == " ":
            return False
        self.results[row] = ((self.results[row][0][0], score_1), (self.results[row][1][0], score_2))
        return True

    def confirm_results(self):
        all_results_confirmed = all(self.enter_score_in_results(row) for row in range(self.table.rowCount()-1))
        if all_results_confirmed:
            self.tournament.add_results(self.results)
            self.confirmed_round.emit()
            self.current = self.is_current()
            self.results = self.get_results()
            self.update_table()

    def update_table(self):
        clear_table(self.table)
        self.fill_in_table()
