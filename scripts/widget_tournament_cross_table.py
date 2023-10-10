from math import ceil, sqrt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget
from PySide6.QtCore import Qt
from .functions_gui import add_content_to_table, set_up_table, size_table, clear_table, add_blank_to_table


def get_line_breaked_entry(entry):
    if len(entry) == 0:
        return ""
    interval = ceil(sqrt(len(entry)))
    return '\n'.join([entry[i:i + interval] for i in range(0, len(entry), interval)])


def get_results_matrix(results, participant_number, id_to_index):
    results_matrix = [["" for _ in range(participant_number)] for _ in range(participant_number)]
    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 is not None and uuid_2 is not None:
                results_matrix[id_to_index[uuid_1]][id_to_index[uuid_2]] += score_1
                results_matrix[id_to_index[uuid_2]][id_to_index[uuid_1]] += score_2
    return [[get_line_breaked_entry(entry) for entry in row] for row in results_matrix]


def get_appropriate_width_for_matrix(results_matrix):
    entry_widths = [entry.index('\n') if '\n' in entry else len(entry) for row in results_matrix for entry in row]
    return 2 * max([1.5] + entry_widths)


class Widget_Tournament_Cross_Table(QWidget):
    def __init__(self, tournament):
        super().__init__()
        self.tournament = tournament

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        self.table = QTableWidget()
        self.fill_in_table()
        self.layout.addWidget(self.table)

    def fill_in_table(self):
        participants = [entry[0] for entry in self.tournament.get_standings()[2]]
        results = self.tournament.get_results()
        id_to_index = {participant.get_uuid(): i for i, participant in enumerate(participants)}
        participant_number = len(participants)
        results_matrix = get_results_matrix(results, participant_number, id_to_index)
        width = get_appropriate_width_for_matrix(results_matrix)
        header_horizontal = ["Name"] + [str(i) for i in range(1, participant_number + 1)]

        set_up_table(self.table, 0, participant_number + 1, header_horizontal=header_horizontal, translate=True)
        size_table(
            self.table, participant_number, width, header_width=3.5, max_width=3.5 + width * participant_number + 17,
            widths=[17] + participant_number * [width]
        )

        header_vertical = self.table.verticalHeader()
        header_vertical.setDefaultAlignment(Qt.AlignCenter)

        for i, participant in enumerate(participants):
            add_content_to_table(self.table, participant, i, 0, edit=False)

        for i in range(participant_number):
            for j in range(participant_number):
                if i == j:
                    add_blank_to_table(self.table, i, j + 1)
                else:
                    add_content_to_table(
                        self.table, results_matrix[i][j], i, j + 1, edit=False, align=Qt.AlignCenter, bold=True
                    )

    def update(self):
        clear_table(self.table)
        self.fill_in_table()
