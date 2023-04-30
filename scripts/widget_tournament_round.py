from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QComboBox, QTableWidget
from PyQt5.QtCore import Qt, pyqtSignal
from .functions_gui import add_content_to_table, add_button_to_table, add_combobox_to_table, clear_table,\
    make_headers_bold_horizontal, size_table


class Widget_Tournament_Round(QWidget):
    confirmed_round = pyqtSignal()

    def __init__(self, results, uuid_to_participant_dict, possible_scores, is_valid_pairings,
                 headers=("White", "Black")):
        super().__init__()
        self.results = results
        self.uuid_to_participant_dict = uuid_to_participant_dict | {None: None}
        self.possible_scores = possible_scores
        self.is_valid_pairings = is_valid_pairings
        self.headers = headers

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout.addWidget(self.table)

    def is_current(self):
        return any(score_1 is None or score_2 is None for (_, score_1), (_, score_2) in self.results)

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
                self.table, [" : "] + [":".join(score) for score in self.possible_scores],
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
        size_table(self.table, len(self.results)+self.is_current(), 4, 3.5, max_width=55, widths=[3.5, None, 7, None])
        self.table.setHorizontalHeaderLabels(["", self.headers[0], "", self.headers[1]])
        make_headers_bold_horizontal(self.table)
        self.table.verticalHeader().setVisible(False)

        header_horizontal = self.table.horizontalHeader()
        header_horizontal.setSectionResizeMode(1, QHeaderView.Stretch)
        header_horizontal.setSectionResizeMode(3, QHeaderView.Stretch)
        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        choose_pairing, choose_result = self.fill_in_pairings()
        if self.is_current():
            if choose_result or choose_pairing:
                self.add_last_row(choose_pairing)
            else:
                self.confirm_results()

    def fill_in_pairings(self):
        choose_pairing = False
        choose_result = False
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
            else:
                choose_result = True
            self.add_pairing_row(i, participant_1, participant_2, score_1, score_2)
        return choose_pairing, choose_result

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
        if all_pairings_confirmed and self.is_valid_pairings(self.results):
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
            self.confirmed_round.emit()
            self.update_table()

    def update_table(self):
        clear_table(self.table)
        self.fill_in_table()
